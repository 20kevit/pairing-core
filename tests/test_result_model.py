"""F3 result-model tests: detailed seam, metadata, O02, determinism."""

import random

import pytest

from pairing_core import (
    ConstraintSet,
    DUTCH_TILL2026_COMPAT,
    EngineRequest,
    RoundPairing,
    __version__,
    pair_detailed,
)
from pairing_core.envelope import input_digest
from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidRequestError,
    PairingError,
)
from pairing_core.rulesets import RulesetId
from tests.test_v010_behavioral import _engine_cases, _player

COMPAT = DUTCH_TILL2026_COMPAT


def _req(case):
    return EngineRequest(
        players=[_player(p) for p in case["players"]],
        ruleset=COMPAT, round_number=case["round"],
        constraints=ConstraintSet(
            forced_pairs=[tuple(x) for x in case["locked"]]
            if case["locked"] else []))


def test_detailed_matches_goldens_and_carries_metadata():
    for case in _engine_cases():
        rp = pair_detailed(_req(case))
        assert isinstance(rp, RoundPairing)
        exp = case["expected"]
        assert [(c.board, c.white_id, c.black_id, c.is_bye,
                 c.white_float, c.black_float) for c in rp.pairings] == \
               [(p["board"], p["white"], p["black"], p["bye"],
                 p["white_float"], p["black_float"])
                for p in exp["pairings"]]
        assert rp.bye_player_id == exp["bye_player_id"]
        assert rp.engine_id == "native-dutch"
        assert rp.engine_version == __version__
        assert rp.ruleset == RulesetId(system="dutch",
                                       effective_date="2026-01-31")
        assert rp.library_version == __version__
        assert rp.input_digest == input_digest(
            [_player(p) for p in case["players"]], case["round"], rp.ruleset)
        want_warn = tuple(sorted(
            exp["validation"]["warnings"] + exp["validation"]["infos"]))
        assert rp.warnings == want_warn
        # envelope round-trips losslessly, digest intact
        assert RoundPairing.from_dict(rp.to_dict()) == rp


def test_impossible_propagates_typed_not_partial():
    from tests.test_v010_behavioral import _error_cases
    imp = [c for c in _error_cases() if c["id"] == "X-impossible"][0]
    with pytest.raises(ImpossiblePairingError):
        pair_detailed(_req(imp))


def test_invalid_request_propagates_unwrapped():
    from pairing_core import PlayerData
    bad = EngineRequest(
        players=[PlayerData(id=1, pairing_no=1, rating=1500, points=0.0),
                 PlayerData(id=1, pairing_no=2, rating=1400, points=0.0)],
        ruleset=COMPAT, round_number=1,
        constraints=ConstraintSet())
    with pytest.raises(InvalidRequestError):
        pair_detailed(bad)


def test_detailed_deterministic_under_permutation():
    rng = random.Random(20261002)
    cases = [c for c in _engine_cases() if len(c["players"]) >= 2][:8]
    for case in cases:
        first = pair_detailed(_req(case))
        for _ in range(5):
            players = [_player(p) for p in case["players"]]
            rng.shuffle(players)
            again = pair_detailed(EngineRequest(
                players=players, ruleset=COMPAT,
                round_number=case["round"],
                constraints=ConstraintSet(
                    forced_pairs=[tuple(x) for x in case["locked"]]
                    if case["locked"] else [])))
            assert again == first


def test_no_partial_on_error_paths():
    # Every error case raises PairingError; RoundPairing is never produced.
    from tests.test_v010_behavioral import _error_cases
    for case in _error_cases():
        with pytest.raises(PairingError):
            pair_detailed(_req(case))


def test_detailed_records_budgets():
    from pairing_core.controls import ExecutionBudgets
    case = [c for c in _engine_cases() if c["id"] == "E-r1-4"][0]
    players = [_player(p) for p in case["players"]]
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=1,
                        constraints=ConstraintSet(),
                        budgets=ExecutionBudgets(max_steps=2000000))
    rp = pair_detailed(req)
    assert rp.budgets == {"max_steps": 2000000, "wall_clock_seconds": None}
    assert RoundPairing.from_dict(rp.to_dict()) == rp
    plain = pair_detailed(_req(case))
    assert plain.budgets is None
