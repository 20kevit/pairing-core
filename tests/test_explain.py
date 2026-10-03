"""Explainability + request-serialization tests (capability wave)."""

import pytest

from pairing_core import (
    ConstraintSet,
    EngineRequest,
    PlayerData,
    RulesetId,
    explain,
    pair,
    pair_detailed,
    validate_round,
)
from pairing_core.errors import InvalidRequestError
from pairing_core.explain import (
    BoardExplanation,
    ByeExplanation,
    Explanation,
)

COMPAT = "dutch-till2026-compat"


def _players():
    return [PlayerData(id=1, pairing_no=1, rating=2000, points=1.0,
                       color_hist="w", opponents=frozenset({5})),
            PlayerData(id=2, pairing_no=2, rating=1900, points=1.0,
                       color_hist="w", opponents=frozenset({6})),
            PlayerData(id=3, pairing_no=3, rating=1800, points=1.0,
                       color_hist="w", opponents=frozenset({7})),
            PlayerData(id=4, pairing_no=4, rating=1700, points=1.0,
                       color_hist="w", opponents=frozenset({8})),
            PlayerData(id=5, pairing_no=5, rating=1600, points=0.0,
                       color_hist="b", opponents=frozenset({1})),
            PlayerData(id=6, pairing_no=6, rating=1500, points=0.0,
                       color_hist="b", opponents=frozenset({2})),
            PlayerData(id=7, pairing_no=7, rating=1400, points=0.0,
                       color_hist="b", opponents=frozenset({3})),
            PlayerData(id=8, pairing_no=8, rating=1300, points=0.0,
                       color_hist="b", opponents=frozenset({4}))]


def test_explain_boards_and_preferences():
    players = _players()
    result = pair(EngineRequest(players=players, ruleset=COMPAT,
                                round_number=2,
                                constraints=ConstraintSet()))
    exp = explain(result, players, ruleset=COMPAT)
    assert isinstance(exp, Explanation)
    assert exp.round_number == 2 and exp.ruleset == COMPAT and exp.valid
    assert exp.errors == () and len(exp.boards) == 4 and exp.bye is None
    first = exp.boards[0]
    assert isinstance(first, BoardExplanation)
    assert first.same_score_group is True
    # winners played white -> strong black preference, unsatisfied here
    assert first.white_preference == "STRONG_BLACK"
    d = exp.to_dict()
    assert d["schema"] == 1 and len(d["boards"]) == 4


def test_explain_bye():
    players = [PlayerData(id=1, pairing_no=1, rating=2000, points=0.0),
               PlayerData(id=2, pairing_no=2, rating=1900, points=0.0),
               PlayerData(id=3, pairing_no=3, rating=1800, points=0.0)]
    result = pair(EngineRequest(players=players, ruleset=COMPAT,
                                round_number=1,
                                constraints=ConstraintSet()))
    exp = explain(result, players)
    assert isinstance(exp.bye, ByeExplanation)
    assert exp.bye.player_id == 3 and exp.bye.score == 0.0
    assert exp.bye.had_prior_bye is False
    assert sum(1 for b in exp.boards if b.is_bye) == 1


def test_explain_rejects_unknown_ids():
    from pairing_core import PairingCard, RoundResult
    players = _players()
    bad = RoundResult(round_number=2, pairings=[
        PairingCard(board=1, white_id=1, black_id=999)])
    with pytest.raises(InvalidRequestError):
        explain(bad, players)


def test_request_serialization_round_trip():
    from pairing_core.controls import ExecutionBudgets
    req = EngineRequest(
        players=_players()[:2], ruleset=RulesetId(system="dutch",
                                                  effective_date="2026-01-31"),
        round_number=2,
        constraints=ConstraintSet(forced_pairs=[(1, 2)]),
        budgets=ExecutionBudgets(max_steps=1000))
    d = req.to_dict()
    back = EngineRequest.from_dict(d)
    assert back == req
    assert EngineRequest.from_dict(
        EngineRequest(players=_players()[:2], ruleset=COMPAT,
                      round_number=1,
                      constraints=ConstraintSet()).to_dict()).ruleset == COMPAT
    with pytest.raises(InvalidRequestError):
        EngineRequest.from_dict({"nope": True})
    with pytest.raises(InvalidRequestError):
        RulesetId.from_dict({"system": 1, "effective_date": "x"})
    assert ConstraintSet.from_dict(
        ConstraintSet(forbidden_pairs=[(1, 2)]).to_dict()
    ).forbidden_pairs == ((1, 2),)


def test_explained_result_matches_detailed():
    players = _players()
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=2,
                        constraints=ConstraintSet())
    detailed = pair_detailed(req)
    exp = explain(detailed, players, ruleset=COMPAT)
    assert [(b.board, b.white_id, b.black_id) for b in exp.boards] == \
           [(c.board, c.white_id, c.black_id) for c in detailed.pairings]
