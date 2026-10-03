"""Structured pairing explanations (capability wave, additive).

PUBLIC. explain() derives a human- and machine-readable account of a
completed pairing from the OUTPUT plus the input players — it replays no
search and exposes no search internals (cheap, deterministic, stable):

- per board: score groups, float tags with meanings, colour preferences
  with satisfaction, bye handling;
- bye: recipient score/unplayed-games/freshness (the documented C5/C9 +
  fresh-first policy inputs);
- everything plain data (to_dict-serializable); versioned schema.

It explains WHAT was decided and WHICH inputs determined it, never the
search path that found it (that is deliberately not a contract).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pairing_core.errors import InvalidRequestError
from pairing_core.models import compute_color


@dataclass(frozen=True)
class BoardExplanation:
    """PUBLIC. One board, explained."""
    board: int
    white_id: int
    black_id: Optional[int] = None
    is_bye: bool = False
    white_points: float = 0.0
    black_points: float = 0.0
    same_score_group: bool = True
    white_float: str = ""
    black_float: str = ""
    white_preference: str = "NONE"
    black_preference: str = "NONE"
    white_preference_satisfied: bool = True
    black_preference_satisfied: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {k: getattr(self, k) for k in (
            "board", "white_id", "black_id", "is_bye", "white_points",
            "black_points", "same_score_group", "white_float",
            "black_float", "white_preference", "black_preference",
            "white_preference_satisfied", "black_preference_satisfied")}


@dataclass(frozen=True)
class ByeExplanation:
    """PUBLIC. Why this player sits out (policy inputs, not proof)."""
    player_id: int
    score: float = 0.0
    unplayed_rounds: int = 0
    had_prior_bye: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {"player_id": self.player_id, "score": self.score,
                "unplayed_rounds": self.unplayed_rounds,
                "had_prior_bye": self.had_prior_bye}


@dataclass(frozen=True)
class Explanation:
    """PUBLIC. Complete structured explanation of one pairing result."""
    round_number: int = 1
    boards: Tuple[BoardExplanation, ...] = ()
    bye: Optional[ByeExplanation] = None
    ruleset: str = ""
    valid: bool = True
    errors: Tuple[str, ...] = ()
    warnings: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, Any]:
        return {"schema": 1, "round_number": self.round_number,
                "boards": [b.to_dict() for b in self.boards],
                "bye": self.bye.to_dict() if self.bye else None,
                "ruleset": self.ruleset, "valid": self.valid,
                "errors": list(self.errors),
                "warnings": list(self.warnings)}


def _pref_name(player) -> str:
    return player.color.preference.name


def _satisfied(player, got_white: bool) -> bool:
    pref = player.color.preference
    if pref.name == "NONE":
        return True
    if got_white:
        return not pref.wants_black
    return not pref.wants_white


def explain(result, players, *, ruleset: str = "") -> Explanation:
    """PUBLIC. Explain a RoundResult (or RoundPairing) against players.

    Runs the independent validator for the valid/errors/warnings section;
    derives per-board facts from inputs + outputs only. Raises
    InvalidRequestError for unknown player ids (cannot explain).
    """
    from pairing_core.models import make_engine_players
    from pairing_core.validator import validate_round

    engine_players = make_engine_players(list(players))
    by_id = {p.id: p for p in engine_players}
    for card in result.pairings:
        if card.white_id not in by_id or (
                card.black_id is not None and card.black_id not in by_id):
            raise InvalidRequestError(
                "cannot explain pairings with unknown player ids.")
    rep = validate_round(result, list(players))
    boards = []
    bye = None
    for card in result.pairings:
        white = by_id[card.white_id]
        if card.is_bye or card.black_id is None:
            bye = ByeExplanation(
                player_id=card.white_id, score=white.points,
                unplayed_rounds=white.data.color_hist.count("-"),
                had_prior_bye=white.data.received_bye)
            boards.append(BoardExplanation(
                board=card.board, white_id=card.white_id, is_bye=True,
                white_points=white.points,
                white_preference=_pref_name(white)))
            continue
        black = by_id[card.black_id]
        boards.append(BoardExplanation(
            board=card.board, white_id=card.white_id,
            black_id=card.black_id,
            white_points=white.points, black_points=black.points,
            same_score_group=(white.points == black.points),
            white_float=card.white_float, black_float=card.black_float,
            white_preference=_pref_name(white),
            black_preference=_pref_name(black),
            white_preference_satisfied=_satisfied(white, True),
            black_preference_satisfied=_satisfied(black, False)))
    return Explanation(
        round_number=result.round_number, boards=tuple(boards), bye=bye,
        ruleset=ruleset, valid=rep.is_valid,
        errors=tuple(sorted(f.rule for f in rep.errors)),
        warnings=tuple(sorted(f.rule for f in rep.warnings)))
