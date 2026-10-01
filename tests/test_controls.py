"""F5 execution-control tests: budgets, cancellation, determinism of bounds."""

import pytest

from pairing_core import (
    ConstraintSet,
    EngineRequest,
    pair,
    pair_detailed,
)
from pairing_core.controls import CancelToken, ExecutionBudgets
from pairing_core.errors import (
    CancelledError,
    EngineTimeoutError,
    InvalidRequestError,
    PairingError,
)
from pairing_core.rulesets import ConstraintSet
from tests.test_v010_behavioral import _engine_cases, _player

COMPAT = "dutch-till2026-compat"


def _req(cid, **kw):
    case = [c for c in _engine_cases() if c["id"] == cid][0]
    return EngineRequest(
        players=[_player(p) for p in case["players"]],
        ruleset=COMPAT, round_number=case["round"],
        constraints=ConstraintSet(
            forced_pairs=[tuple(x) for x in case["locked"]]
            if case["locked"] else []),
        **kw)


def _fp(result):
    return ([(c.board, c.white_id, c.black_id, c.is_bye,
              c.white_float, c.black_float) for c in result.pairings],
            result.bye_player_id)


def test_budgets_validation():
    assert ExecutionBudgets().max_steps is None
    with pytest.raises(InvalidRequestError):
        ExecutionBudgets(max_steps=0)
    with pytest.raises(InvalidRequestError):
        ExecutionBudgets(max_steps=True)
    with pytest.raises(InvalidRequestError):
        ExecutionBudgets(wall_clock_seconds=0)
    with pytest.raises(InvalidRequestError):
        ExecutionBudgets(wall_clock_seconds="fast")


def test_cancel_token():
    tok = CancelToken()
    assert tok.cancelled is False
    tok.cancel()
    assert tok.cancelled is True
    tok.cancel()
    assert tok.cancelled is True


def test_explicit_legacy_cap_behaves_identically():
    req = _req("E-r1-8", budgets=ExecutionBudgets(max_steps=2000000))
    assert _fp(pair(req)) == _fp(pair(_req("E-r1-8")))


def test_generous_wall_clock_never_perturbs():
    req = _req("E-r3-mixed",
               budgets=ExecutionBudgets(wall_clock_seconds=3600))
    assert _fp(pair(req)) == _fp(pair(_req("E-r3-mixed")))


def test_tiny_step_budget_fails_deterministically():
    msgs = set()
    for _ in range(3):
        with pytest.raises(EngineTimeoutError) as exc:
            pair(_req("E-r1-8", budgets=ExecutionBudgets(max_steps=1)))
        msgs.add(str(exc.value))
    assert len(msgs) == 1
    assert "1 nodes" in next(iter(msgs))


def test_step_budget_success_path_unaffected():
    # Generous-but-finite budget: identical output to unbounded.
    req = _req("E-r2-draw", budgets=ExecutionBudgets(max_steps=1000000))
    assert _fp(pair(req)) == _fp(pair(_req("E-r2-draw")))


def test_precancelled_token_raises_before_search():
    tok = CancelToken()
    tok.cancel()
    with pytest.raises(CancelledError):
        pair(_req("E-r1-8", cancel_token=tok))
    with pytest.raises(CancelledError):
        pair_detailed(_req("E-r1-8", cancel_token=tok))


def test_past_deadline_at_pairer_level():
    from pairing_core.bracket import build_brackets
    from pairing_core.controls import now_monotonic
    from pairing_core.models import make_engine_players
    from pairing_core.pairer import pair_all_brackets
    from pairing_core import PlayerData
    players = [PlayerData(id=i, pairing_no=i, rating=1500, points=0.0)
               for i in range(1, 9)]
    eps = make_engine_players(players)
    brackets = build_brackets(eps)
    played = {e.id: set() for e in eps}
    with pytest.raises(EngineTimeoutError):
        pair_all_brackets(brackets, played, 1,
                          deadline=now_monotonic() - 1.0)


def test_bad_budget_shapes_rejected_at_boundary():
    req = _req("E-r1-2")
    req_bad = EngineRequest(players=req.players, ruleset=COMPAT,
                            round_number=1,
                            constraints=ConstraintSet(),
                            budgets="unlimited")
    with pytest.raises(InvalidRequestError):
        pair(req_bad)
    req_bad2 = EngineRequest(players=req.players, ruleset=COMPAT,
                             round_number=1, constraints=ConstraintSet(),
                             cancel_token="nope")
    with pytest.raises(InvalidRequestError):
        pair(req_bad2)


def test_timeout_is_pairing_error_and_value_error():
    assert issubclass(EngineTimeoutError, PairingError)
    assert issubclass(CancelledError, PairingError)
