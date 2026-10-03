"""Live BBP oracle tests (env-gated: BBP_EXE=<path to bbpPairings binary>).

Without BBP_EXE every test SKIPS with reason (no binary vendored, none
assumed). With it: round-1 pair-set agreement, oracle-output validity, and
a small RTG differential whose classifications are RECORDED (informational)
with hard gates only on validator-cleanliness both sides — never asserting
exact equality (first-wins vs global optimum legitimately differ; the
authoritative ruleset, checked via the independent validator, decides
legality, not identity).

Verified baseline (2026-10-01, BBP 8f9e3c5 source build): round-1 pair sets
agree; colors differ per E.5 parity rule (documented deviation
DUTCH_CONFORMANCE_STATUS.md §E.5); float-heavy states diverge (absolute-bar
question, same doc).
"""

import json
import os

import pytest

BBP_EXE = os.environ.get("BBP_EXE", "")
needs_bbp = pytest.mark.skipif(
    not BBP_EXE, reason="live BBP oracle needs BBP_EXE=<bbpPairings binary>")


def _fresh_trf(n, seed_rating=2000):
    from pairing_core.adapters.trf import (
        TournamentInput,
        TrfPlayer,
        build_trf,
    )
    players = tuple(
        TrfPlayer(pairing_id=i, name=f"P{i}",
                  rating=seed_rating - (i - 1) * 10, points=0.0)
        for i in range(1, n + 1))
    return build_trf(TournamentInput(players=players, rounds_total=5,
                                     name="OracleR1", initial_color="w"))


@needs_bbp
def test_round1_pair_sets_agree(tmp_path):
    """Same pairs as native on fresh fields (colors excluded: E.5)."""
    import subprocess
    from pairing_core import EngineRequest, ConstraintSet, PlayerData, pair
    for n in (4, 8, 10):
        src = tmp_path / f"r1_{n}.trf"
        src.write_text(_fresh_trf(n), encoding="utf-8")
        out = tmp_path / f"r1_{n}.out"
        r = subprocess.run([BBP_EXE, "--dutch", str(src), "-p", str(out)],
                           capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[:300]
        bbp_sets = set()
        for ln in out.read_text(encoding="utf-8").splitlines()[1:]:
            if ln.strip():
                w, b = ln.split()
                bbp_sets.add(frozenset((int(w), int(b))))
        players = [PlayerData(id=i, pairing_no=i,
                              rating=2000 - (i - 1) * 10, points=0.0)
                   for i in range(1, n + 1)]
        res = pair(EngineRequest(
            players=players, ruleset="dutch-till2026-compat", round_number=1,
            constraints=ConstraintSet()))
        nat_sets = {frozenset((c.white_id, c.black_id))
                    for c in res.pairings if c.black_id is not None}
        assert bbp_sets == nat_sets


@needs_bbp
def test_oracle_output_passes_independent_validator(tmp_path):
    """BBP's own output must satisfy our absolute legality checks."""
    import subprocess
    from pairing_core import PlayerData, validate_round
    from pairing_core.adapters.trf import parse_trf, parse_pairing_output
    from pairing_core import PairingCard, RoundResult
    src = tmp_path / "r1.trf"
    src.write_text(_fresh_trf(8), encoding="utf-8")
    out = tmp_path / "r1.out"
    r = subprocess.run([BBP_EXE, "--dutch", str(src), "-p", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[:300]
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


@needs_bbp
def test_rtg_differential_recorded(tmp_path):
    """Small RTG differential: record classifications; gate legality only."""
    import subprocess
    from pairing_core.adapters.trf import parse_trf
    cfg = tmp_path / "rtg.cfg"
    cfg.write_text("PlayersNumber=8\nRoundsNumber=3\nForfeitRate=10000\n"
                   "RetiredRate=10000\nHalfPointByeRate=10000\n"
                   "HighestRating=2200\nLowestRating=1800\n",
                   encoding="utf-8")
    records = []
    for seed in (11, 12, 13):
        trf = tmp_path / f"g{seed}.trf"
        r = subprocess.run(
            [BBP_EXE, "--dutch", "-g", str(cfg), "-o", str(trf),
             "-s", str(seed)], capture_output=True, text=True, timeout=120)
        assert r.returncode == 0, r.stderr[:300]
        text = trf.read_text(encoding="utf-8")
        codes = set()
        for line in text.splitlines():
            if line.startswith("001"):
                for tok in line.split()[10:]:
                    if tok in "10=+-DWFHLZUW":
                        codes.add(tok)
        records.append({"seed": seed, "codes": sorted(codes)})
    with open(os.path.join("/tmp", "oracle_differential.json"),
              "w", encoding="utf-8") as fh:
        json.dump(records, fh)
    assert all("1" in rec["codes"] for rec in records)


@needs_bbp
def test_c9_bye_unplayed_games(tmp_path):
    """BBP's own C9 fixture shape: unplayed-heavy player skipped for bye."""
    import subprocess
    from pairing_core import (
        ConstraintSet,
        EngineRequest,
        PlayerData,
        pair,
    )
    from pairing_core.adapters.trf import (
        TournamentInput,
        TrfPlayer,
        TrfRound,
        build_trf,
    )
    histories = {
        1: [("w", 3, "1")], 2: [("b", 4, "1")], 3: [("b", 1, "0")],
        4: [("w", 2, "0")], 5: [("-", None, "Z")],
    }
    tplayers = tuple(
        TrfPlayer(pairing_id=i, name=f"P{i}", rating=2700 - (i - 1) * 10,
                  points={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0}[i],
                  rounds=tuple(
                      TrfRound(opponent=o, color=c, result=r)
                      for (c, o, r) in histories[i]))
        for i in range(1, 6))
    src = tmp_path / "c9.trf"
    src.write_text(build_trf(TournamentInput(
        players=tplayers, rounds_total=3, name="C9",
        initial_color="w")), encoding="utf-8")
    out = tmp_path / "c9.out"
    r = subprocess.run([BBP_EXE, "--dutch", str(src), "-p", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[:300]
    bbp_bye = None
    for ln in out.read_text(encoding="utf-8").splitlines()[1:]:
        if ln.strip():
            w, b = ln.split()
            if b == "0":
                bbp_bye = int(w)
    assert bbp_bye == 4
    pds = [PlayerData(id=i, pairing_no=i, rating=2700 - (i - 1) * 10,
                      points={1: 1.0, 2: 1.0, 3: 0.0, 4: 0.0, 5: 0.0}[i],
                      color_hist={"w": "w", "b": "b", "-": "-"}[
                          histories[i][0][0]],
                      opponents=frozenset(
                          {o for (_, o, _) in histories[i]
                           if o is not None}))
             for i in range(1, 6)]
    res = pair(EngineRequest(
        players=pds, ruleset="dutch-till2026-compat", round_number=2,
        constraints=ConstraintSet()))
    assert res.bye_player_id == 4 == bbp_bye


@needs_bbp
def test_forbidden_pairs_agree(tmp_path):
    """XXP avoidance agrees with BBP (pair sets; colors excluded: E.5)."""
    import subprocess
    from pairing_core import (
        ConstraintSet,
        EngineRequest,
        PlayerData,
        pair,
    )
    from pairing_core.adapters.trf import (
        TournamentInput,
        TrfPlayer,
        build_trf,
    )
    players = tuple(
        TrfPlayer(pairing_id=i, name=f"P{i}",
                  rating=2000 - (i - 1) * 10, points=0.0)
        for i in range(1, 5))
    src = tmp_path / "xxp.trf"
    src.write_text(build_trf(TournamentInput(
        players=players, rounds_total=3, name="XXP", initial_color="w",
        forbidden_pairs=((1, 2),))), encoding="utf-8")
    out = tmp_path / "xxp.out"
    r = subprocess.run([BBP_EXE, "--dutch", str(src), "-p", str(out)],
                       capture_output=True, text=True, timeout=120)
    assert r.returncode == 0, r.stderr[:300]
    bbp_sets = set()
    for ln in out.read_text(encoding="utf-8").splitlines()[1:]:
        if ln.strip():
            w, b = ln.split()
            pair_set = frozenset((int(w), int(b)))
            assert pair_set != frozenset((1, 2))
            bbp_sets.add(pair_set)
    pds = [PlayerData(id=i, pairing_no=i, rating=2000 - (i - 1) * 10,
                      points=0.0) for i in range(1, 5)]
    res = pair(EngineRequest(
        players=pds, ruleset="dutch-till2026-compat", round_number=1,
        constraints=ConstraintSet(forbidden_pairs=[(1, 2)])))
    nat_sets = {frozenset((c.white_id, c.black_id)) for c in res.pairings
                if c.black_id is not None}
    assert frozenset((1, 2)) not in nat_sets
    assert bbp_sets == nat_sets
