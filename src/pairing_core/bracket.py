"""
Score bracket construction and management — FIDE C.04.3.

This module handles:
    - Building score brackets from the player list
    - Merging incoming downfloaters into brackets
    - S1/S2 splitting within a bracket
    - Remainder candidate selection
    - Bracket state for backtracking

FIDE C.04.3 Bracket Rules:
    1. Players are grouped into score brackets by their current score.
       All players with the same score are in the same bracket.

    2. Brackets are processed from top (highest score) to bottom.

    3. Within each bracket, players are ordered by their pairing number
       (lower = higher ranked).

    4. The bracket is split into two halves:
       - S1: top half (higher ranked players)
       - S2: bottom half (lower ranked players)
       S1[i] is ideally paired with S2[i].

    5. If the bracket has an odd number of players, the lowest-ranked
       player becomes a REMAINDER candidate and may float down.

    6. Incoming downfloaters from the bracket above are merged into
       the bracket BEFORE splitting. They are sorted by pairing number
       together with the residents.

    7. The TOP bracket has special handling:
       - It may be a Homogeneous bracket (all players have same score
         AND came from the same previous bracket) or a Heterogeneous
         bracket (contains incoming floaters).
       - In a heterogeneous top bracket, the incoming floaters are
         placed at the TOP of the bracket (before residents) in S1,
         because they have higher scores.

    8. When backtracking, a bracket can be asked to produce a different
       remainder candidate, leading to a different S1/S2 configuration.

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Dict, List, Optional, Set, Tuple

from pairing_core.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Bracket Data Structure
# ═══════════════════════════════════════════════════════════════════

class Bracket:
    """
    A score bracket containing players with the same score.

    This class is the central data structure for the Dutch algorithm.
    It manages the bracket's player list, splitting, and remainder
    selection for the recursive pairing search.
    """
    __slots__ = (
        "score", "residents", "downfloaters",
        "is_top", "is_bottom", "index",
    )

    def __init__(
        self,
        score: float,
        residents: List[EnginePlayer],
        downfloaters: Optional[List[EnginePlayer]] = None,
        is_top: bool = False,
        is_bottom: bool = False,
        index: int = 0,
    ):
        self.score = score
        self.residents = list(residents)
        self.downfloaters = list(downfloaters) if downfloaters else []
        self.is_top = is_top
        self.is_bottom = is_bottom
        self.index = index

    # ── Player access ────────────────────────────────────────────

    @property
    def all_players(self) -> List[EnginePlayer]:
        """
        All players in bracket, sorted by pairing number.
        
        FIDE C.04.3 Rule 7:
            In a heterogeneous bracket, the incoming downfloaters are
            placed at the TOP of the bracket (before residents) in S1,
            because they have higher scores.
        """
        # FIXED: Any bracket with downfloaters is heterogeneous.
        # Floaters must come first, sorted by pno, then residents.
        if self.downfloaters:
            return (
                sorted(self.downfloaters, key=lambda p: p.pno) +
                sorted(self.residents, key=lambda p: p.pno)
            )
        
        # Homogeneous bracket: all sorted by pno
        return sorted(self.residents, key=lambda p: p.pno)

    @property
    def resident_ids(self) -> Set[int]:
        return {p.id for p in self.residents}

    @property
    def downfloater_ids(self) -> Set[int]:
        return {p.id for p in self.downfloaters}

    # ── Counts ───────────────────────────────────────────────────

    @property
    def count(self) -> int:
        return len(self.residents) + len(self.downfloaters)

    @property
    def is_odd(self) -> bool:
        return self.count % 2 == 1

    @property
    def max_pairs(self) -> int:
        return self.count // 2

    @property
    def is_empty(self) -> bool:
        return self.count == 0

    # ── S1/S2 Splitting ──────────────────────────────────────────

    def split(
        self,
        exclude_id: Optional[int] = None,
    ) -> Tuple[List[EnginePlayer], List[EnginePlayer]]:
        """
        Split bracket into S1 (top half) and S2 (bottom half).

        If exclude_id is given, that player is removed before splitting.
        This is used when a remainder candidate has been selected.

        FIDE C.04.3:
            S1 contains the higher-ranked half.
            S2 contains the lower-ranked half.
            S1[0] is ideally paired with S2[0], S1[1] with S2[1], etc.

        Args:
            exclude_id: Player ID to exclude (the remainder/downfloater).

        Returns:
            (s1, s2) tuple. Both are sorted by pairing number.

        Raises:
            ValueError: If the resulting player count is odd
                       (caller must ensure even count).
        """
        players = self.all_players
        if exclude_id is not None:
            players = [p for p in players if p.id != exclude_id]

        n = len(players)
        if n == 0:
            return [], []
        if n % 2 != 0:
            raise ValueError(
                f"Cannot split odd-count bracket ({n} players) "
                f"into S1/S2. Remove a remainder first."
            )

        half = n // 2
        return players[:half], players[half:]

    def split_for_pairing(
        self,
        remainder_id: Optional[int] = None,
    ) -> Tuple[List[EnginePlayer], List[EnginePlayer], Optional[EnginePlayer]]:
        """
        Prepare bracket for pairing by splitting into S1, S2,
        and optionally selecting a remainder.

        If the bracket is odd and no remainder_id is provided,
        the default remainder (lowest-ranked) is used.

        Returns:
            (s1, s2, remainder_player)
            remainder_player is None if the bracket has even count.
        """
        players = self.all_players

        if not players:
            return [], [], None

        remainder = None

        if len(players) % 2 == 1:
            if remainder_id is not None:
                remainder = next(
                    (p for p in players if p.id == remainder_id),
                    None,
                )
            if remainder is None:
                # Default: lowest-ranked player
                remainder = players[-1]

        exclude = remainder.id if remainder else None
        s1, s2 = self.split(exclude_id=exclude)
        return s1, s2, remainder

    # ── Remainder Candidates ─────────────────────────────────────

    def remainder_candidates(
        self,
        incoming_ids: Optional[Set[int]] = None,
    ) -> List[EnginePlayer]:
        """
        Return ordered list of remainder/downfloater candidates.

        These are the players who could be removed from this bracket
        and sent to the next bracket as downfloaters.

        Order (FIDE C.04.3):
            1. Prefer residents over incoming floaters
            2. Prefer players NOT floated in the previous round
            3. Prefer fewer consecutive same-direction floats
            4. Prefer lowest-ranked (highest pairing number)

        Args:
            incoming_ids: Set of IDs of incoming downfloaters.
                         If None, uses self.downfloater_ids.

        Returns:
            Ordered list (best candidate first).
        """
        if incoming_ids is None:
            incoming_ids = self.downfloater_ids

        players = self.all_players

        if not players:
            return []

        candidates = sorted(
            players,
            key=lambda p: (
                # Prefer residents over incoming
                0 if p.id not in incoming_ids else 1,
                # Prefer not recently floated
                1 if p.floats.last_was_down else 0,
                # Fewer consecutive floats
                p.floats.consecutive_downs,
                # Lowest ranked first (highest pno)
                -p.pno,
                # Stable tiebreak
                p.id,
            ),
        )

        return candidates

    # ── Bracket Manipulation ─────────────────────────────────────

    def with_downfloaters(
        self,
        new_floaters: List[EnginePlayer],
    ) -> "Bracket":
        """
        Return a new bracket with additional downfloaters merged in.
        """
        # Mark players as downfloaters
        marked = []
        for p in new_floaters:
            p.is_downfloater = True
            marked.append(p)

        return Bracket(
            score=self.score,
            residents=list(self.residents),
            downfloaters=list(self.downfloaters) + marked,
            is_top=self.is_top,
            is_bottom=self.is_bottom,
            index=self.index,
        )

    def without_player(self, player_id: int) -> "Bracket":
        """
        Return a new bracket with one player removed.
        """
        return Bracket(
            score=self.score,
            residents=[p for p in self.residents if p.id != player_id],
            downfloaters=[p for p in self.downfloaters if p.id != player_id],
            is_top=self.is_top,
            is_bottom=self.is_bottom,
            index=self.index,
        )

    # ── Representation ───────────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"Bracket(score={self.score}, "
            f"residents={len(self.residents)}, "
            f"floaters={len(self.downfloaters)}, "
            f"top={self.is_top}, bottom={self.is_bottom})"
        )


# ═══════════════════════════════════════════════════════════════════
#  Bracket Construction
# ═══════════════════════════════════════════════════════════════════

def build_brackets(players: List[EnginePlayer]) -> List[Bracket]:
    """
    Build score brackets from a list of engine players.

    Players are grouped by their current score. Brackets are
    returned in descending score order (highest first).

    Each player's bracket_idx is set to their bracket position.

    Args:
        players: List of EnginePlayer, already sorted by pairing number.

    Returns:
        List of Bracket objects, highest score first.
    """
    if not players:
        return []

    # Group by score
    groups: Dict[float, List[EnginePlayer]] = {}
    for p in players:
        groups.setdefault(p.points, []).append(p)

    # Sort scores descending
    scores = sorted(groups.keys(), reverse=True)

    brackets: List[Bracket] = []
    for idx, score in enumerate(scores):
        bracket_players = sorted(groups[score], key=lambda p: p.pno)

        # Set bracket index on each player
        for p in bracket_players:
            p.bracket_idx = idx

        bracket = Bracket(
            score=score,
            residents=bracket_players,
            is_top=(idx == 0),
            is_bottom=(idx == len(scores) - 1),
            index=idx,
        )
        brackets.append(bracket)

    return brackets


def get_bracket_summary(brackets: List[Bracket]) -> str:
    """
    Return a human-readable summary of bracket structure.
    Useful for debugging and logging.
    """
    lines = []
    for b in brackets:
        players = b.all_players
        pnos = [str(p.pno) for p in players]
        lines.append(
            f"  [{b.score:.1f}] "
            f"{b.count} players "
            f"(pno: {', '.join(pnos)})"
            f"{' [TOP]' if b.is_top else ''}"
            f"{' [BOT]' if b.is_bottom else ''}"
        )
    return "Brackets:\n" + "\n".join(lines)