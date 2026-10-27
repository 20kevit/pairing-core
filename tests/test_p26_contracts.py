"""Boundary tests for the public dated 2026 request/result contract."""

import math

import pytest

from pairing_core.errors import (
    InternalError,
    InvalidPlayerError,
    InvalidRequestError,
    VersionMismatchError,
)
from pairing_core.fide2026 import DUTCH_2026, pair_2026
from pairing_core.fide2026.models import (
    BursteinIndexProvenance,
    BursteinIndexSet,
    BursteinIndexValue,
    P26Pair,
    P26Pairing,
    P26Player,
    P26Request,
)


def _players():
    return (P26Player(id=1, tpn=1), P26Player(id=2, tpn=2))


@pytest.mark.parametrize("score", [float("nan"), float("inf"), float("-inf"), -0.5])
def test_player_score_must_be_finite_and_nonnegative(score):
    with pytest.raises(InvalidPlayerError):
        P26Player(id=1, tpn=1, score=score)


def test_player_numeric_and_history_validation():
    with pytest.raises(InvalidPlayerError, match="rating"):
        P26Player(id=1, tpn=1, rating=-1)
    with pytest.raises(InvalidPlayerError, match="played"):
        P26Player(id=1, tpn=1, played=True)
    with pytest.raises(InvalidPlayerError, match="opponents"):
        P26Player(id=1, tpn=1, opponents=(2, 2))
    with pytest.raises(InvalidPlayerError, match="opponent ids"):
        P26Player(id=1, tpn=1, opponents=(True,))


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"round_number": True}, "round_number"),
        ({"total_rounds": -1}, "total_rounds"),
        ({"max_steps": True}, "max_steps"),
        ({"wall_clock_seconds": math.nan}, "wall_clock_seconds"),
        ({"wall_clock_seconds": math.inf}, "wall_clock_seconds"),
    ],
)
def test_request_rejects_invalid_numeric_controls(kwargs, message):
    with pytest.raises(InvalidRequestError, match=message):
        P26Request(players=_players(), ruleset=DUTCH_2026, **kwargs)


def test_request_validates_round_results_and_last_round_flag():
    with pytest.raises(InvalidRequestError, match="duplicate player ids"):
        P26Request(players=_players(), ruleset=DUTCH_2026,
                   round_results=((1, ()), (1, ())))
    with pytest.raises(InvalidRequestError, match="align with its opponents"):
        P26Request(players=_players(), ruleset=DUTCH_2026,
                   round_results=((1, ("W",)),))
    final = P26Request(players=_players(), ruleset=DUTCH_2026,
                       round_number=9, total_rounds=9)
    assert final.is_last_round is True
    with pytest.raises(InvalidRequestError, match="agree"):
        P26Request(players=_players(), ruleset=DUTCH_2026,
                   round_number=9, total_rounds=9, is_last_round=False)


def test_legacy_round_results_are_ignored_outside_burstein_and_rejected_for_it():
    players = _players()
    legacy = ((1, ()),)
    # Previously accepted legacy payloads remain inert for non-Burstein systems.
    request = P26Request(players=players, ruleset=DUTCH_2026,
                         round_results=legacy)
    old_payload = request.to_dict()
    old_payload.pop("schema")
    assert P26Request.from_dict(old_payload) == request
    assert len(pair_2026(request).pairs) == 1
    # They cannot be mistaken for a C.04 Index calculator input.
    burstein = P26Request(players=players, ruleset="burstein-2026",
                          round_results=legacy)
    with pytest.raises(InvalidRequestError, match="not a Burstein Index"):
        pair_2026(burstein)


def test_burstein_index_set_requires_unique_finite_values_and_provenance():
    source = BursteinIndexProvenance(source="caller-supplied")
    with pytest.raises(InvalidRequestError, match="duplicate"):
        BursteinIndexSet(
            values=(BursteinIndexValue(1, 1, 0), BursteinIndexValue(1, 2, 1)),
            provenance=source)
    with pytest.raises(InvalidRequestError, match="finite non-negative"):
        BursteinIndexValue(1, math.nan, 0)
    with pytest.raises(InvalidRequestError, match="requires producer"):
        BursteinIndexProvenance(source="library-calculated")


@pytest.mark.parametrize("system", ["burstein", "dubov"])
def test_pab_completion_respects_absolute_colour_conflicts(system):
    """A low-score bye candidate can leave an unpairable C3 remainder."""
    from pairing_core.controls import ExecutionBudgets
    from pairing_core.fide2026.common import Stepper

    players = (
        P26Player(id=1, tpn=1, score=0, colors="WW", played=2),  # absolute B
        P26Player(id=2, tpn=2, score=0.5, colors="BB", played=2),  # absolute W
        P26Player(id=3, tpn=3, score=1, colors="BB", played=2),  # absolute W
        P26Player(id=4, tpn=4, score=1, colors="BB", played=2),  # absolute W
        P26Player(id=5, tpn=5, score=1, colors="WW", played=2),  # absolute B
    )
    by_id = {player.id: player for player in players}
    stepper = Stepper(ExecutionBudgets(max_steps=1000))
    if system == "burstein":
        from pairing_core.fide2026.burstein import _select_pab
        rank_of = {player.id: (0.0, 0.0, player.tpn) for player in players}
        selected = _select_pab(players, by_id, rank_of, [], stepper)
    else:
        from pairing_core.fide2026.dubov import _select_pab
        selected = _select_pab(players, by_id, [], stepper)
    # Removing player 1 leaves three absolute-White seekers and one
    # absolute-Black seeker, which cannot be paired without violating C3.
    assert selected == 2


def test_request_order_normalizes_and_provenance_digest_is_stable():
    players = _players()
    first = P26Request(players=players, ruleset=DUTCH_2026)
    reordered = P26Request(players=tuple(reversed(players)), ruleset=DUTCH_2026)
    assert first == reordered
    assert first.to_dict() == reordered.to_dict()
    assert pair_2026(first).to_dict() == pair_2026(reordered).to_dict()


def test_public_dispatcher_rejects_partial_engine_output(monkeypatch):
    from pairing_core.fide2026 import dutch

    incomplete = P26Pairing(pairs=(), bye_id=None, floats=(),
                            ruleset=DUTCH_2026)
    monkeypatch.setattr(dutch, "pair_dutch", lambda _request: incomplete)
    with pytest.raises(InternalError, match="does not cover the roster exactly"):
        pair_2026(P26Request(players=_players(), ruleset=DUTCH_2026))


def test_public_dispatcher_rejects_rematches_and_unknown_float_ids(monkeypatch):
    from pairing_core.fide2026 import dutch

    players = (P26Player(id=1, tpn=1, opponents=(2,)),
               P26Player(id=2, tpn=2))
    rematch = P26Pairing(pairs=(P26Pair(1, 2),), bye_id=None,
                         floats=(), ruleset=DUTCH_2026)
    monkeypatch.setattr(dutch, "pair_dutch", lambda _request: rematch)
    with pytest.raises(InternalError, match="rematch"):
        pair_2026(P26Request(players=players, ruleset=DUTCH_2026))

    legal = P26Pairing(pairs=(P26Pair(1, 2),), bye_id=None,
                       floats=((99, "D"),), ruleset=DUTCH_2026)
    monkeypatch.setattr(dutch, "pair_dutch", lambda _request: legal)
    with pytest.raises(InternalError, match="unknown player"):
        pair_2026(P26Request(players=_players(), ruleset=DUTCH_2026))


def test_result_envelope_detects_digest_tampering():
    result = pair_2026(P26Request(players=_players(), ruleset=DUTCH_2026))
    payload = result.to_dict()
    payload["pairs"][0]["white"] = 2
    with pytest.raises(VersionMismatchError, match="digest mismatch"):
        P26Pairing.from_dict(payload)


def test_legacy_unversioned_result_shape_remains_parseable():
    result = pair_2026(P26Request(players=_players(), ruleset=DUTCH_2026))
    current = result.to_dict()
    legacy = {key: current[key]
              for key in ("pairs", "bye_id", "floats", "ruleset", "notes")}
    parsed = P26Pairing.from_dict(legacy)
    assert parsed.provenance is None
    assert parsed.round_number is None
    assert parsed.pairs == result.pairs


def test_result_constructor_keeps_positive_player_id_invariants():
    with pytest.raises(InvalidRequestError, match="positive integer"):
        P26Pair(0, 1)
