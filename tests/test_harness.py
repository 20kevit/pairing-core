"""W4 harness tests: taxonomy, corpus runner, native self-differential."""

import os

import pytest

from pairing_core import EngineRequest, pair_via
from pairing_core.harness.compare import (
    ComparisonOutcome,
    Fingerprint,
    check_constraints,
    compare,
    fingerprint_of,
)
from pairing_core.harness.corpus import run_corpus

CORPUS = os.path.join(os.path.dirname(__file__), "data", "conformance",
                      "dutch_till2026.json")


def _fp(pairs, bye=None):
    return Fingerprint(pairs=tuple(pairs), bye=bye)


A = _fp([(1, 3, "", ""), (2, 4, "", "")])
A_REORDERED = _fp([(2, 4, "", ""), (1, 3, "", "")])
A_SWAPPED_COLOR = _fp([(3, 1, "", ""), (2, 4, "", "")])
B = _fp([(1, 4, "", ""), (2, 3, "", "")])
A_BYE = _fp([(1, 3, "", "")], bye=5)
A_BYE_OTHER = _fp([(1, 3, "", "")], bye=4)
A_FLOAT = _fp([(1, 3, "D", "U"), (2, 4, "", "")])


def test_exact_and_reordered():
    out = compare(A, A, native_valid=True, ref_valid=True)
    assert out.kind == "exact-equivalent"
    out = compare(A, A_REORDERED, native_valid=True, ref_valid=True)
    assert out.kind == "reordered-equivalent"


def test_valid_alternative_dimensions():
    out = compare(A, B, native_valid=True, ref_valid=True)
    assert out.kind == "valid-alternative" and "pairing" in out.dimensions
    out = compare(A, A_SWAPPED_COLOR, native_valid=True, ref_valid=True)
    assert out.kind == "valid-alternative" and "colour" in out.dimensions
    out = compare(A_BYE, A_BYE_OTHER, native_valid=True, ref_valid=True)
    assert out.kind == "valid-alternative" and "bye" in out.dimensions
    out = compare(A, A_FLOAT, native_valid=True, ref_valid=True)
    assert out.kind == "valid-alternative" and "float" in out.dimensions


def test_violations_sided():
    out = compare(A, B, native_valid=False, ref_valid=True)
    assert out.kind == "native-violation"
    out = compare(A, B, native_valid=True, ref_valid=False)
    assert out.kind == "reference-violation"
    out = compare(A, B, native_valid=False, ref_valid=False)
    assert out.kind == "engine-limitation"


def test_errors_ruleset_and_nondeterminism():
    out = compare(A, B, native_valid=True, ref_valid=True,
                  native_error="ImpossiblePairingError")
    assert out.kind == "engine-limitation"
    out = compare(A, B, native_valid=True, ref_valid=True,
                  same_ruleset=False)
    assert out.kind == "ruleset-mismatch"
    out = compare(A, B, native_valid=True, ref_valid=True,
                  same_engine_run=True)
    assert out.kind == "nondeterminism"


def test_check_constraints():
    assert check_constraints(A, ((1, 3),), ((1, 4),)) == ()
    assert check_constraints(A, ((1, 4),), ()) == ("forced-missing:1-4",)
    assert check_constraints(A, (), ((1, 3),)) == ("forbidden-present:1-3",)


def test_corpus_passes_with_independent_anchor():
    import json
    doc = json.load(open(CORPUS, encoding="utf-8"))
    assert len(doc["cases"]) == 22
    failures = run_corpus(CORPUS)
    assert failures == [], [f.detail for f in failures]


def test_native_self_differential_exact():
    from pairing_core import ConstraintSet
    from pairing_core.rulesets import ConstraintSet as CS
    from tests.test_v010_behavioral import _engine_cases, _player
    for case in _engine_cases()[:6]:
        players = [_player(p) for p in case["players"]]
        req = EngineRequest(
            players=players, ruleset="dutch-till2026-compat",
            round_number=case["round"],
            constraints=CS(forced_pairs=[
                tuple(x) for x in case["locked"]] if case["locked"] else []))
        from pairing_core import validate_round
        r1, r2 = pair_via("native-dutch", req), pair_via("native-dutch", req)
        f1, f2 = fingerprint_of(r1), fingerprint_of(r2)
        assert f1 == f2
        out = compare(f1, f2, native_valid=True, ref_valid=True,
                      same_engine_run=True)
        assert out.kind == "exact-equivalent"
        assert validate_round(r1, players).is_valid


def test_core_does_not_import_harness():
    import sys
    for mod in ("pairing_core.api", "pairing_core.engine",
                "pairing_core.envelope", "pairing_core.provider",
                "pairing_core.registry", "pairing_core.rulesets",
                "pairing_core.models", "pairing_core.validator"):
        with open(sys.modules[mod].__file__, encoding="utf-8") as fh:
            imports = [ln for ln in fh
                       if ln.lstrip().startswith(("import ", "from "))]
        assert not any("pairing_core.harness" in ln for ln in imports), mod
