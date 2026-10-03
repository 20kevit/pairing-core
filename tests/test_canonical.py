"""Canonical contract tests (master wave, Phase B).

- Converters legacy<->canonical round-trip.
- pair_canonical agrees with pair_detailed on the same logical input.
- Serialization round-trips; schema/version errors typed.
- Module isolation: canonical.py must not (even lazily) depend on engine
  internals — verified in a fresh subprocess.
"""
import subprocess
import sys
from pathlib import Path

import pytest

from pairing_core.api import EngineRequest, pair_detailed
from pairing_core.canonical import (
    CanonicalPlayer,
    CanonicalRequest,
    canonical_json,
    describe_systems,
    pair_canonical,
)
from pairing_core.controls import ExecutionBudgets
from pairing_core.envelope import RoundPairing
from pairing_core.errors import (
    InvalidRequestError,
    UnsupportedCapabilityError,
    VersionMismatchError,
)
from pairing_core.models import PlayerData
from pairing_core.rulesets import ConstraintSet, DUTCH_TILL2026_COMPAT


def _pd(i, pts=0.0, color_hist="", opponents=()):
    return PlayerData(id=i, pairing_no=i, rating=1500 + i, points=pts,
                      color_hist=color_hist, opponents=frozenset(opponents))


def _canon_req(n=4, **kw):
    players = tuple(
        CanonicalPlayer.from_legacy(_pd(i)) for i in range(1, n + 1))
    base = dict(players=players, ruleset=DUTCH_TILL2026_COMPAT,
                round_number=1)
    base.update(kw)
    return CanonicalRequest(**base)


def test_legacy_round_trip():
    p = _pd(3, pts=1.5, color_hist="wb", opponents={1, 2})
    c = CanonicalPlayer.from_legacy(p)
    assert c.opponents == (1, 2)
    back = c.to_legacy()
    assert back == p


def test_pair_canonical_agrees_with_pair_detailed():
    req = _canon_req(n=6)
    got = pair_canonical(req)
    assert isinstance(got, RoundPairing)
    ereq = EngineRequest(players=[_pd(i) for i in range(1, 7)],
                         ruleset=DUTCH_TILL2026_COMPAT, round_number=1)
    expected = pair_detailed(ereq)
    assert got.to_dict() == expected.to_dict()


def test_pair_canonical_via_provider():
    req = _canon_req(n=4, provider_id="native-dutch")
    got = pair_canonical(req)
    assert got.engine_id == "native-dutch"


def test_unsupported_system_refused():
    req = _canon_req(n=4, system="berger-rr")
    with pytest.raises(UnsupportedCapabilityError):
        pair_canonical(req)
    with pytest.raises(UnsupportedCapabilityError):
        pair_canonical(_canon_req(n=4, system="knockout"))


def test_nondeterministic_mode_refused():
    with pytest.raises(UnsupportedCapabilityError):
        pair_canonical(_canon_req(n=4, deterministic=False))


def test_missing_ruleset_refused():
    players = tuple(
        CanonicalPlayer.from_legacy(_pd(i)) for i in range(1, 5))
    with pytest.raises(InvalidRequestError):
        pair_canonical(CanonicalRequest(players=players, ruleset=None))


def test_serialization_round_trip():
    req = _canon_req(n=4, constraints=ConstraintSet(
        forbidden_pairs=((1, 2),)),
        budgets=ExecutionBudgets(max_steps=100))
    data = req.to_dict()
    assert canonical_json(data) == canonical_json(req.to_dict())
    back = CanonicalRequest.from_dict(data)
    assert back.to_dict() == data
    got = pair_canonical(back)
    assert isinstance(got, RoundPairing)


def test_unknown_schema_rejected():
    data = _canon_req(n=4).to_dict()
    data["schema"] = 999
    with pytest.raises(VersionMismatchError):
        CanonicalRequest.from_dict(data)


def test_malformed_dicts_rejected():
    with pytest.raises(InvalidRequestError):
        CanonicalRequest.from_dict({"bogus": True})
    with pytest.raises(InvalidRequestError):
        CanonicalPlayer.from_dict({"id": 1})


def test_describe_systems():
    systems = describe_systems()
    assert {s["system"] for s in systems} == {"dutch", "berger-rr"}


def test_canonical_module_isolation():
    # Load canonical.py standalone WITHOUT executing pairing_core/__init__
    # (which legitimately wires the whole package): true unit isolation.
    # Paths resolve from this file's location — no checkout-location
    # assumptions (the suite must pass from any clone path).
    repo_root = Path(__file__).resolve().parents[1]
    canonical_src = repo_root / "src" / "pairing_core" / "canonical.py"
    code = (
        "import sys, importlib.util; "
        "spec = importlib.util.spec_from_file_location("
        f"'canonical_standalone', {str(canonical_src)!r}); "
        "mod = importlib.util.module_from_spec(spec); "
        "sys.modules['canonical_standalone'] = mod; "
        "spec.loader.exec_module(mod); "
        "leak = sorted(m for m in sys.modules "
        "if m.split('.')[0] == 'pairing_core'); "
        "print('LEAK:' + ','.join(leak));"
    )
    out = subprocess.run([sys.executable, "-c", code], capture_output=True,
                         text=True, cwd=str(repo_root))
    assert out.returncode == 0, out.stderr
    assert out.stdout.strip() == "LEAK:", out.stdout
    # Static check: module-level imports must be stdlib-only (every
    # pairing_core coupling is a function-local compat seam, never an
    # import-time dependency). pairing_core.errors is taxonomy, allowed
    # if ever hoisted; engine-ish modules are banned at any depth of
    # a top-level import statement.
    import ast
    src = canonical_src.read_text(encoding="utf-8")
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            else:
                names = [node.module or ""]
            for name in names:
                assert not name.startswith("pairing_core.engine"), name
                assert not name.startswith("pairing_core.pairer"), name
                assert not name.startswith("pairing_core.bracket"), name
                assert name != "pairing_core.provider", name
                assert not name.startswith("pairing_core.adapters"), name
    # And no code reference to concrete engine classes anywhere: the
    # canonical layer routes through EngineRequest/providers, never
    # naming implementations. (Docstrings may NAME them to document the
    # non-dependency, so scan AST identifiers, not raw text.)
    refs = {n.id for n in ast.walk(tree)
            if isinstance(n, ast.Name)}
    refs |= {n.attr for n in ast.walk(tree)
             if isinstance(n, ast.Attribute)}
    for banned in ("SwissEngine", "NativeDutchEngine", "EnginePlayer"):
        assert banned not in refs, banned
