"""
FIDE Dutch Swiss Pairing Engine — Data Models.

This module defines all data structures used by the pairing engine.
It has zero external dependencies (pure Python stdlib + dataclasses).

Public contracts:
    PlayerData      — Input: one player's tournament state
    PairingCard     — Output: one board assignment
    RoundResult     — Output: complete round result

Internal models:
    EnginePlayer    — Runtime player state during computation
    ColorPref       — Color preference classification (enum)
    ColorState      — Computed color state from history
    FloatStatus     — Computed float state from history
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, FrozenSet, List, Optional, Set, Tuple


# ═══════════════════════════════════════════════════════════════════
#  PUBLIC — Input Contract
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class PlayerData:
    """
    Input data for one player. Provided by the caller (tournament system).

    All fields required for FIDE Dutch pairing are included.
    The caller is responsible for computing these from tournament history.

    Attributes:
        id:              Unique player identifier.
        pairing_no:      Official tournament pairing number.
                         Assigned once at tournament start, never changes.
                         Determines initial ranking and all tiebreaks within
                         the Dutch algorithm. Lower number = higher ranked.
                         Typically assigned by: rating desc, then title,
                         then alphabetical.
        rating:          Player rating (standard/rapid/blitz per tournament type).
        points:          Current cumulative score (e.g., 3.5 after 5 rounds).
        color_hist:      Chronological color history as a string.
                         'w' = white, 'b' = black, '-' = no game (bye/forfeit).
                         Example: "wb-bw" (5 rounds: W, B, bye, B, W).
                         Empty string if no rounds played.
        opponents:       Frozenset of opponent IDs already faced.
        received_bye:    True if player already received a pairing-allocated bye.
                         Requested byes (half/zero) do NOT count.
        float_hist:      Chronological float history as a string.
                         'D' = downfloat, 'U' = upfloat, '-' = no float.
                         Example: "--D-U" (5 rounds).
                         Empty string if no rounds played.
    """
    id: int
    pairing_no: int
    rating: int
    points: float
    color_hist: str = ""
    opponents: FrozenSet[int] = field(default_factory=frozenset)
    received_bye: bool = False
    float_hist: str = ""


# Legacy alias
PlayerSnapshot = PlayerData


# ═══════════════════════════════════════════════════════════════════
#  PUBLIC — Output Contract
# ═══════════════════════════════════════════════════════════════════

@dataclass
class PairingCard:
    """
    Output: one board's pairing assignment.

    Attributes:
        board:        Board number (1-based).
        white_id:     Player ID assigned white.
        black_id:     Player ID assigned black. None if bye.
        is_bye:       True if this is the pairing-allocated bye.
        white_float:  'D' (down), 'U' (up), or '' (none).
        black_float:  'D', 'U', or ''.
    """
    board: int
    white_id: int
    black_id: Optional[int] = None
    is_bye: bool = False
    white_float: str = ""
    black_float: str = ""


@dataclass
class RoundResult:
    """
    Output: complete pairing result for one round.

    Attributes:
        round_number:   Round these pairings are for.
        pairings:       Ordered list of board pairings.
        bye_player_id:  ID of the player who got the pairing bye (or None).
    """
    round_number: int
    pairings: List[PairingCard] = field(default_factory=list)
    bye_player_id: Optional[int] = None


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Color Preference
# ═══════════════════════════════════════════════════════════════════

class ColorPref(Enum):
    """
    Color preference classification per FIDE C.04.2.

    Ordered from strongest to weakest:
        ABSOLUTE_WHITE / ABSOLUTE_BLACK
            Player MUST receive this color. Violation is illegal.

        STRONG_WHITE / STRONG_BLACK
            Player SHOULD receive this color. Violation is undesirable.

        MILD_WHITE / MILD_BLACK
            Player PREFERS this color. Violation is acceptable.

        NONE
            No preference. Player has not played any games yet.
    """
    ABSOLUTE_WHITE = auto()
    ABSOLUTE_BLACK = auto()
    STRONG_WHITE = auto()
    STRONG_BLACK = auto()
    MILD_WHITE = auto()
    MILD_BLACK = auto()
    NONE = auto()

    @property
    def wants_white(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_WHITE,
            ColorPref.STRONG_WHITE,
            ColorPref.MILD_WHITE,
        )

    @property
    def wants_black(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_BLACK,
            ColorPref.STRONG_BLACK,
            ColorPref.MILD_BLACK,
        )

    @property
    def is_absolute(self) -> bool:
        return self in (
            ColorPref.ABSOLUTE_WHITE,
            ColorPref.ABSOLUTE_BLACK,
        )

    @property
    def is_strong(self) -> bool:
        return self in (
            ColorPref.STRONG_WHITE,
            ColorPref.STRONG_BLACK,
        )

    @property
    def is_mild(self) -> bool:
        return self in (
            ColorPref.MILD_WHITE,
            ColorPref.MILD_BLACK,
        )

    @property
    def strength(self) -> int:
        """Numeric strength: 3=absolute, 2=strong, 1=mild, 0=none."""
        if self.is_absolute:
            return 3
        if self.is_strong:
            return 2
        if self.is_mild:
            return 1
        return 0

    @property
    def direction(self) -> str:
        """'w', 'b', or '' for none."""
        if self.wants_white:
            return "w"
        if self.wants_black:
            return "b"
        return ""


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Color State
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class ColorState:
    """
    Fully computed color state for one player.
    Derived from PlayerData.color_hist at engine startup.
    Immutable.
    """
    balance: int = 0
    last: str = ""
    last_two: str = ""
    games_played: int = 0
    preference: ColorPref = field(default=ColorPref.NONE)
    due_color: str = ""

    @property
    def must_white(self) -> bool:
        return self.preference == ColorPref.ABSOLUTE_WHITE

    @property
    def must_black(self) -> bool:
        return self.preference == ColorPref.ABSOLUTE_BLACK


def compute_color(hist: str) -> ColorState:
    """Compute ColorState from a color history string."""
    played = [c for c in hist if c in ("w", "b")]
    whites = played.count("w")
    blacks = played.count("b")
    balance = whites - blacks
    games = len(played)

    last = played[-1] if played else ""
    last_two = "".join(played[-2:]) if len(played) >= 2 else (
        played[-1] if played else ""
    )

    if balance < 0:
        due = "w"
    elif balance > 0:
        due = "b"
    elif last == "w":
        due = "b"
    elif last == "b":
        due = "w"
    else:
        due = ""

    pref = _classify_preference(balance, last_two, last)

    return ColorState(
        balance=balance,
        last=last,
        last_two=last_two,
        games_played=games,
        preference=pref,
        due_color=due,
    )


def _classify_preference(
    balance: int,
    last_two: str,
    last: str,
) -> ColorPref:
    if last_two == "ww":
        return ColorPref.ABSOLUTE_BLACK
    if last_two == "bb":
        return ColorPref.ABSOLUTE_WHITE
    if balance >= 2:
        return ColorPref.ABSOLUTE_BLACK
    if balance <= -2:
        return ColorPref.ABSOLUTE_WHITE
    if balance > 0:
        return ColorPref.STRONG_BLACK
    if balance < 0:
        return ColorPref.STRONG_WHITE
    if last == "w":
        return ColorPref.MILD_BLACK
    if last == "b":
        return ColorPref.MILD_WHITE
    return ColorPref.NONE


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Float Status
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class FloatStatus:
    """
    Fully computed float state for one player.
    Derived from PlayerData.float_hist at engine startup.
    Immutable.
    """
    last_dir: str = ""
    last_was_down: bool = False
    last_was_up: bool = False
    consecutive_downs: int = 0
    consecutive_ups: int = 0
    total_downs: int = 0
    total_ups: int = 0

    @property
    def would_violate_down(self) -> bool:
        return self.consecutive_downs >= 2

    @property
    def would_violate_up(self) -> bool:
        return self.consecutive_ups >= 2

    @property
    def had_recent_down(self) -> bool:
        return self.last_was_down

    @property
    def had_recent_up(self) -> bool:
        return self.last_was_up


def compute_floats(hist: str) -> FloatStatus:
    """
    Compute FloatStatus from a float history string.
    FIXED: A '-' (no float) ALWAYS breaks the consecutive streak.
    """
    if not hist:
        return FloatStatus()

    total_d = hist.count("D")
    total_u = hist.count("U")

    # Find last actual float direction
    last_dir = ""
    for ch in reversed(hist):
        if ch in ("D", "U"):
            last_dir = ch
            break

    # Count consecutive same-direction from the END backward.
    # A '-' (no float) ALWAYS breaks the streak.
    cons_d = 0
    cons_u = 0
    found_direction = False

    for ch in reversed(hist):
        if ch == "-":
            # Any no-float marker breaks the consecutive streak
            break
        elif ch == "D":
            if not found_direction:
                found_direction = True
            if cons_u > 0:
                break  # Direction changed
            cons_d += 1
        elif ch == "U":
            if not found_direction:
                found_direction = True
            if cons_d > 0:
                break  # Direction changed
            cons_u += 1

    return FloatStatus(
        last_dir=last_dir,
        last_was_down=(last_dir == "D"),
        last_was_up=(last_dir == "U"),
        consecutive_downs=cons_d,
        consecutive_ups=cons_u,
        total_downs=total_d,
        total_ups=total_u,
    )


# ═══════════════════════════════════════════════════════════════════
#  INTERNAL — Engine Player
# ═══════════════════════════════════════════════════════════════════

class EnginePlayer:
    """
    Runtime representation of a player during pairing computation.
    Created once per player at engine startup from PlayerData.
    """
    __slots__ = (
        "data", "pno", "color", "floats",
        "_opponents", "bracket_idx",
        "is_downfloater", "is_upfloater",
    )

    def __init__(self, data: PlayerData):
        self.data = data
        self.pno: int = data.pairing_no
        self.color: ColorState = compute_color(data.color_hist)
        self.floats: FloatStatus = compute_floats(data.float_hist)
        self._opponents: FrozenSet[int] = data.opponents
        self.bracket_idx: int = -1
        self.is_downfloater: bool = False
        self.is_upfloater: bool = False

    @property
    def id(self) -> int:
        return self.data.id

    @property
    def rating(self) -> int:
        return self.data.rating

    @property
    def points(self) -> float:
        return self.data.points

    @property
    def played_ids(self) -> FrozenSet[int]:
        return self._opponents

    def has_played(self, other_id: int) -> bool:
        return other_id in self._opponents

    def can_meet(self, other: "EnginePlayer") -> bool:
        return (
            other.id not in self._opponents
            and self.id not in other._opponents
        )

    def must_white(self) -> bool:
        return self.color.must_white

    def must_black(self) -> bool:
        return self.color.must_black

    def pref_strength(self) -> int:
        return self.color.preference.strength

    @property
    def sort_key(self) -> Tuple[float, int, int]:
        return (-self.points, self.pno, self.id)

    def __repr__(self) -> str:
        return (
            f"EP(id={self.id}, pno={self.pno}, "
            f"pts={self.points}, r={self.rating})"
        )

    def __eq__(self, other) -> bool:
        if not isinstance(other, EnginePlayer):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


def make_engine_players(players: List[PlayerData]) -> List[EnginePlayer]:
    """
    Convert PlayerData list into EnginePlayer list sorted by
    FIDE ranking (pairing number order).
    """
    engine = [EnginePlayer(p) for p in players]
    engine.sort(key=lambda ep: ep.sort_key)
    return engine