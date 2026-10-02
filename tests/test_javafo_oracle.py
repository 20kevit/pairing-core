"""Live JaVaFo oracle tests (env-gated: JAVAFO_JAR=<jar> [, JAVA_EXE=<java>]).

Without them every test SKIPS with reason (BYO model; nothing vendored or
assumed). With them: version identity, round-1 pair-set agreement with
native (colors excluded — E.5 parity, JaVaFo agrees with BBP here), and
oracle-output validity through the independent validator.

Verified baseline (2026-10-02, JaVaFo Rel. 2.2 Build 3223, OpenJDK 21):
092 line identifies its rules as "Swiss Dutch 2017" — an older vintage than
BBP's 2025 Dutch. Oracle disagreements must therefore be read as
reference-vs-kernel differences across rule vintages, never as FIDE verdicts.
"""

import os
import shutil

import pytest

JAVA_EXE = os.environ.get("JAVA_EXE", shutil.which("java") or "")
JAVAFO_JAR = os.environ.get("JAVAFO_JAR", "")
needs_javafo = pytest.mark.skipif(
    not (JAVA_EXE and JAVAFO_JAR),
    reason="live JaVaFo oracle needs JAVAFO_JAR=<jar> (JAVA_EXE optional)")


def _fresh_trf(n):
    from pairing_core.adapters.trf import (
        TournamentInput,
        TrfPlayer,
        build_trf,
    )
    players = tuple(
        TrfPlayer(pairing_id=i, name=f"P{i}",
                  rating=2000 - (i - 1) * 10, points=0.0)
        for i in range(1, n + 1))
    return build_trf(TournamentInput(players=players, rounds_total=5,
                                     name="OracleR1", initial_color="w"))


@needs_javafo
def test_version_identity():
    from pairing_core.adapters.javafo import JaVaFoConfig, probe_version
    cfg = JaVaFoConfig(java_executable=JAVA_EXE, jar_path=JAVAFO_JAR,
                       timeout_seconds=60.0)
    version = probe_version(cfg)
    assert "JaVaFo" in version and "Rel." in version


@needs_javafo
def test_round1_pair_sets_agree(tmp_path):
    """Same pairs as native on fresh fields (E.5 colors excluded)."""
    import subprocess
    from pairing_core import EngineRequest, ConstraintSet, PlayerData, pair
    for n in (4, 8):
        src = tmp_path / f"r1_{n}.trf"
        src.write_text(_fresh_trf(n), encoding="utf-8")
        out = tmp_path / f"r1_{n}.out"
        r = subprocess.run(
            [JAVA_EXE, "-jar", JAVAFO_JAR, str(src), "-p", str(out)],
            capture_output=True, text=True, timeout=180)
        assert r.returncode == 0, (r.stdout + r.stderr)[:300]
        assert out.is_file(), "JaVaFo produced no output (engine failure)"
        jsets = set()
        for ln in out.read_text(encoding="utf-8").splitlines()[1:]:
            if ln.strip():
                w, b = ln.split()
                jsets.add(frozenset((int(w), int(b))))
        players = [PlayerData(id=i, pairing_no=i,
                              rating=2000 - (i - 1) * 10, points=0.0)
                   for i in range(1, n + 1)]
        res = pair(EngineRequest(
            players=players, ruleset="dutch-till2026-compat", round_number=1,
            constraints=ConstraintSet()))
        nat_sets = {frozenset((c.white_id, c.black_id))
                    for c in res.pairings if c.black_id is not None}
        assert jsets == nat_sets


@needs_javafo
def test_oracle_output_passes_independent_validator(tmp_path):
    """JaVaFo's output must satisfy our absolute legality checks."""
    import subprocess
    from pairing_core import PlayerData, validate_round
    from pairing_core.adapters.trf import parse_trf, parse_pairing_output
    from pairing_core import PairingCard, RoundResult
    src = tmp_path / "r1.trf"
    src.write_text(_fresh_trf(8), encoding="utf-8")
    out = tmp_path / "r1.out"
    r = subprocess.run(
        [JAVA_EXE, "-jar", JAVAFO_JAR, str(src), "-p", str(out)],
        capture_output=True, text=True, timeout=180)
    assert r.returncode == 0, (r.stdout + r.stderr)[:300]
    t = parse_trf(src.read_text(encoding="utf-8"))
    pds = [PlayerData(id=p.pairing_id, pairing_no=p.pairing_id,
                      rating=p.rating, points=p.points)
           for p in t.players]
    cards = [PairingCard(board=i + 1, white_id=w, black_id=b,
                         is_bye=(b is None))
             for i, (w, b) in
             enumerate(parse_pairing_output(out.read_text(encoding="utf-8")))]
    rep = validate_round(RoundResult(round_number=1, pairings=cards), pds)
    assert not rep.has_errors, rep.error_summary
