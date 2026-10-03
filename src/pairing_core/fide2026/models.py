"""2026 value model + ruleset identities (FIDE articles only).

P26Player carries everything the 2026 texts require:
- TPN (all systems), rating (Dubov-mandatory, Lim Maxi-guard, Olympiad seeding),
- score (primary), secondary (team game points / colour tiebreak input),
- colors: per-round 'W'/'B'/'u' (unplayed) history in round order,
- opponents: played opponent ids (unplayed pairings excluded per C.04.2 3.5),
- unplayed: count of unplayed games (Dutch C9; PAB preferences),
- last_float / prev_float: 'D'/'U'/'' for previous / two-ago rounds (C14-C21,
  Dubov C8-C10, Double/Team C7/C8/C10),
- got_pab / forfeit_win: C2 blockers; played: games/matches actually played
  (PAB "most games" tiebreaks).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple

from pairing_core.controls import CancelToken
from pairing_core.errors import InvalidPlayerError, UnsupportedRulesetError

DUTCH_2026 = "dutch-2026"
DUBOV_2026 = "dubov-2026"
BURSTEIN_2026 = "burstein-2026"
LIM_2026 = "lim-2026"
DOUBLE_2026 = "double-2026"
TEAM_2026 = "team-2026"
OLYMPIAD_2022 = "olympiad-2022"


@dataclass(frozen=True)
class P26RulesetId:
    """Dated 2026 ruleset identity: system + effective date (+ options)."""

    system: str
    effective_date: str
    acceleration: Optional[str] = None
    team_colour_type: Optional[str] = None  # team-2026: "A" (default), "B", "none"

    def to_dict(self) -> Dict[str, object]:
        return {"system": self.system, "effective_date": self.effective_date,
                "acceleration": self.acceleration,
                "team_colour_type": self.team_colour_type}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "P26RulesetId":
        try:
            system = data["system"]
            date = data["effective_date"]
            if not isinstance(system, str) or not isinstance(date, str):
                raise KeyError("types")
            return P26RulesetId(
                system=system, effective_date=date,
                acceleration=data.get("acceleration"),
                team_colour_type=data.get("team_colour_type"))
        except (KeyError, TypeError, AttributeError) as exc:
            raise InvalidPlayerError(
                f"malformed P26RulesetId dict: {exc}") from exc


#: Exact-match table of implemented 2026 rulesets (separate from the frozen
#: v0.1.0 KNOWN_RULESETS — that table stays len==1 per regression pin).
SYSTEM_RULESETS: Dict[P26RulesetId, Dict[str, str]] = {
    P26RulesetId(system="dutch", effective_date="2026-02-01"): {
        "label": DUTCH_2026, "source": "F-0105", "engine": "fide2026.dutch",
        "note": "C.04.3 full C1-C21 search; evidence DUTCH_2026_EVIDENCE.md"},
    P26RulesetId(system="dubov", effective_date="2026-02-01"): {
        "label": DUBOV_2026, "source": "F-0108", "engine": "fide2026.dubov",
        "note": "C.04.4.1 ARO engine; evidence DUBOV_2026_EVIDENCE.md"},
    P26RulesetId(system="burstein", effective_date="2026-02-01"): {
        "label": BURSTEIN_2026, "source": "F-0110", "engine": "fide2026.burstein",
        "note": "C.04.4.2 Index engine; evidence BURSTEIN_2026_EVIDENCE.md"},
    P26RulesetId(system="lim", effective_date="2026-02-01"): {
        "label": LIM_2026, "source": "F-0112", "engine": "fide2026.lim",
        "note": "C.04.4.3 procedural engine; evidence LIM_2026_EVIDENCE.md"},
    P26RulesetId(system="double", effective_date="2026-02-01"): {
        "label": DOUBLE_2026, "source": "F-0114", "engine": "fide2026.double_team",
        "note": "C.04.5 match engine; evidence DOUBLE_SWISS_2026_EVIDENCE.md"},
    P26RulesetId(system="team", effective_date="2026-02-01"): {
        "label": TEAM_2026, "source": "F-0115", "engine": "fide2026.double_team",
        "note": "C.04.6 team engine; evidence TEAM_SWISS_2026_EVIDENCE.md"},
    P26RulesetId(system="olympiad", effective_date="2022-01-01"): {
        "label": OLYMPIAD_2022, "source": "F-0601", "engine": "fide2026.olympiad",
        "note": "Olympiad Pairing Rules; evidence OLYMPIAD_EVIDENCE.md"},
}

ALIASES_2026: Dict[str, P26RulesetId] = {
    DUTCH_2026: P26RulesetId(system="dutch", effective_date="2026-02-01"),
    DUBOV_2026: P26RulesetId(system="dubov", effective_date="2026-02-01"),
    BURSTEIN_2026: P26RulesetId(system="burstein", effective_date="2026-02-01"),
    LIM_2026: P26RulesetId(system="lim", effective_date="2026-02-01"),
    DOUBLE_2026: P26RulesetId(system="double", effective_date="2026-02-01"),
    TEAM_2026: P26RulesetId(system="team", effective_date="2026-02-01"),
    OLYMPIAD_2022: P26RulesetId(system="olympiad", effective_date="2022-01-01"),
}


def resolve_2026_ruleset(ruleset: object) -> P26RulesetId:
    """Exact-match resolver for 2026 rulesets (no fallback, typed errors).

    Team-2026 colour-type options (Art.1.7: "A" default, "B", "none") are
    facets of the same dated ruleset, not distinct rulesets: any of the
    three (or unset) resolves.
    """
    candidate = None
    if isinstance(ruleset, P26RulesetId):
        candidate = ruleset
    elif isinstance(ruleset, str) and ruleset in ALIASES_2026:
        return ALIASES_2026[ruleset]
    if candidate is not None:
        if candidate in SYSTEM_RULESETS:
            return candidate
        if (candidate.system, candidate.effective_date,
                candidate.acceleration) == ("team", "2026-02-01", None) \
                and candidate.team_colour_type in ("A", "B", "none"):
            return candidate
    known = sorted(ALIASES_2026)
    raise UnsupportedRulesetError(
        f"Unsupported 2026 ruleset {ruleset!r}. Known: {', '.join(known)}.")


@dataclass(frozen=True)
class P26Player:
    """One entrant's pairing-relevant state for one 2026 round."""

    id: int
    tpn: int
    score: float = 0.0
    rating: Optional[int] = None
    secondary: float = 0.0
    colors: str = ""
    opponents: Tuple[int, ...] = ()
    unplayed: int = 0
    last_float: str = ""
    prev_float: str = ""
    got_pab: bool = False
    forfeit_win: bool = False
    played: int = 0
    late_entry: bool = False  # joined after round-1 publication
    # (Olympiad Art.4.2.3 bye ineligibility; management-side fact)

    def __post_init__(self) -> None:
        object.__setattr__(self, "opponents", tuple(sorted(self.opponents)))
        _validate_player(self)

    def to_dict(self) -> Dict[str, object]:
        return {"id": self.id, "tpn": self.tpn, "score": self.score,
                "rating": self.rating, "secondary": self.secondary,
                "colors": self.colors, "opponents": list(self.opponents),
                "unplayed": self.unplayed, "last_float": self.last_float,
                "prev_float": self.prev_float, "got_pab": self.got_pab,
                "forfeit_win": self.forfeit_win, "played": self.played,
                "late_entry": self.late_entry}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "P26Player":
        try:
            return P26Player(
                id=data["id"], tpn=data["tpn"],
                score=float(data.get("score", 0.0)),
                rating=data.get("rating"),
                secondary=float(data.get("secondary", 0.0)),
                colors=data.get("colors", ""),
                opponents=tuple(data.get("opponents", [])),
                unplayed=int(data.get("unplayed", 0)),
                last_float=data.get("last_float", ""),
                prev_float=data.get("prev_float", ""),
                got_pab=bool(data.get("got_pab", False)),
                forfeit_win=bool(data.get("forfeit_win", False)),
                played=int(data.get("played", 0)),
                late_entry=bool(data.get("late_entry", False)))
        except (KeyError, TypeError, AttributeError, ValueError) as exc:
            raise InvalidPlayerError(
                f"malformed P26Player dict: {exc}") from exc


def _validate_player(p: "P26Player") -> None:
    if not isinstance(p.id, int) or isinstance(p.id, bool):
        raise InvalidPlayerError(f"player id must be int, got {p.id!r}.")
    if not isinstance(p.tpn, int) or isinstance(p.tpn, bool) or p.tpn < 1:
        raise InvalidPlayerError(f"tpn must be int >= 1, got {p.tpn!r}.")
    if p.rating is not None and (not isinstance(p.rating, int)
                                 or isinstance(p.rating, bool)):
        raise InvalidPlayerError(f"rating must be int or None, got {p.rating!r}.")
    for ch in p.colors:
        if ch not in ("W", "B", "u"):
            raise InvalidPlayerError(
                f"colors must use W/B/u only, got {p.colors!r}.")
    if p.last_float not in ("", "D", "U") or p.prev_float not in ("", "D", "U"):
        raise InvalidPlayerError(
            f"float tags must be ''/D/U, got {p.last_float!r}/{p.prev_float!r}.")
    if p.unplayed < 0 or p.played < 0:
        raise InvalidPlayerError("unplayed/played must be >= 0.")
    if p.id in p.opponents:
        raise InvalidPlayerError(f"player {p.id} lists self as opponent.")


@dataclass(frozen=True)
class P26Request:
    """Single-round 2026 pairing request (ruleset mandatory, never defaulted)."""

    players: Tuple[P26Player, ...] = ()
    ruleset: object = None
    round_number: int = 1
    total_rounds: int = 9
    is_last_round: bool = False
    initial_colour: str = "W"
    maxi_tournament: bool = False  # Lim 100pt guard (Art.3.2.3/3.8/5.7)
    prior_upfloats: Tuple[Tuple[int, int], ...] = ()  # id -> cumulative
    # upfloats before this round (Dubov C8-C10 maximum-upfloat guards)
    round_results: Tuple[Tuple[int, Tuple[str, ...]], ...] = ()  # id ->
    # one W/D/L code per played opponent, aligned with opponents order
    # (Burstein Art.1.7 opposition evaluation; never inferred)
    max_steps: Optional[int] = None
    wall_clock_seconds: Optional[float] = None
    cancel_token: Optional[CancelToken] = None  # cooperative cancellation;
    # pre-cancelled (or cancelled mid-run) -> typed CancelledError, never
    # partial output (see SEARCH_CEILING_POLICY.md).

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", tuple(self.players))
        if self.ruleset is None:
            raise InvalidPlayerError("ruleset is mandatory (no default drift).")
        if not isinstance(self.round_number, int) or self.round_number < 1:
            raise InvalidPlayerError("round_number must be int >= 1.")
        if self.initial_colour not in ("W", "B"):
            raise InvalidPlayerError("initial_colour must be W or B.")
        for code_set in self.round_results:
            try:
                _pid, codes = code_set
            except (TypeError, ValueError) as exc:
                raise InvalidPlayerError(
                    f"malformed round_results entry: {exc}") from exc
            if any(c not in ("W", "D", "L") for c in codes):
                raise InvalidPlayerError(
                    "round_results codes must be W/D/L only.")
        ids = [p.id for p in self.players]
        if len(set(ids)) != len(ids):
            raise InvalidPlayerError("duplicate player ids.")
        tpns = [p.tpn for p in self.players]
        if len(set(tpns)) != len(tpns):
            raise InvalidPlayerError("duplicate tpns (TPN must be unique).")
        for p in self.players:
            for opp in p.opponents:
                if opp not in ids:
                    raise InvalidPlayerError(
                        f"player {p.id} lists unknown opponent {opp}.")

    def round_results_dict(self) -> Dict[int, Tuple[str, ...]]:
        """round_results as id -> codes mapping."""
        return {pid: tuple(codes) for pid, codes in self.round_results}


@dataclass(frozen=True)
class P26Pair:
    white_id: int
    black_id: int


@dataclass(frozen=True)
class P26Pairing:
    """Complete 2026 round pairing (partials unrepresentable)."""

    pairs: Tuple[P26Pair, ...]
    bye_id: Optional[int]
    floats: Tuple[Tuple[int, str], ...]  # (player id, 'D'/'U')
    ruleset: str
    notes: Tuple[str, ...] = ()

    def to_dict(self) -> Dict[str, object]:
        return {"pairs": [{"white": p.white_id, "black": p.black_id}
                          for p in self.pairs],
                "bye_id": self.bye_id,
                "floats": [list(f) for f in self.floats],
                "ruleset": self.ruleset, "notes": list(self.notes)}
