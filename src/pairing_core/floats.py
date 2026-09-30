"""
Float restriction engine — FIDE C.04.2 / C.04.3.

This module handles all float-related logic:
    - Determining if a player CAN be floated (down or up)
    - Selecting the best downfloater candidate from a bracket
    - Tracking float status for output recording

FIDE Float Rules Summary (C.04.2):
    1. A downfloat means a player is paired in a lower score bracket
       than their own. An upfloat means paired in a higher bracket.

    2. A player should not downfloat (or upfloat) in two consecutive
       rounds. This is a STRONG constraint (avoid if possible).

    3. A player MUST NOT downfloat (or upfloat) in three or more
       consecutive rounds. This is an ABSOLUTE constraint.

    4. When selecting which player to float down from a bracket,
       prefer (in order):
         a) A player who was NOT floated in the previous round
         b) A player with fewer consecutive same-direction floats
         c) The lowest-ranked player in the bracket (highest pairing number)

    5. An incoming downfloater should not be re-floated down again
       if other candidates exist (avoid double-floating).

    6. These constraints may be relaxed (in order) when no legal
       pairing can be found:
         - First relax the "no consecutive same-direction" soft rule
         - Then relax the "no re-float incoming" preference
         - NEVER relax the 3-consecutive absolute limit (hard ceiling)

Constraint levels:
    ABSOLUTE:  3+ consecutive same direction → always illegal
    STRONG:    2 consecutive same direction → avoid, but allow if necessary
    SOFT:      re-floating an incoming player → avoid, but allow if necessary

This module is stateless and deterministic. Zero external dependencies.
"""
from enum import Enum, auto
from typing import List, Optional, Tuple

from pairing_core.models import EnginePlayer, FloatStatus


# ═══════════════════════════════════════════════════════════════════
#  Float Constraint Level
# ═══════════════════════════════════════════════════════════════════

class FloatConstraint(Enum):
    """Level of float restriction."""
    LEGAL = auto()          # No restriction violated
    SOFT_VIOLATION = auto() # Re-floating incoming player
    STRONG_VIOLATION = auto()  # 2nd consecutive same-direction float
    ABSOLUTE_VIOLATION = auto() # 3+ consecutive — always illegal


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def can_downfloat(
    player: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a player can legally be sent as a downfloater.

    Args:
        player: The candidate downfloater.
        strict: If True, enforce both absolute AND strong constraints.
                If False, only enforce absolute constraint (3+ consecutive).

    Returns:
        True if the player can be downfloated at the given strictness level.
    """
    level = downfloat_violation_level(player)

    if level == FloatConstraint.ABSOLUTE_VIOLATION:
        return False

    if strict and level == FloatConstraint.STRONG_VIOLATION:
        return False

    return True


def can_upfloat(
    player: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a player can legally be sent as an upfloater.

    Args:
        player: The candidate upfloater.
        strict: If True, enforce both absolute AND strong constraints.
                If False, only enforce absolute constraint (3+ consecutive).

    Returns:
        True if the player can be upfloated at the given strictness level.
    """
    level = upfloat_violation_level(player)

    if level == FloatConstraint.ABSOLUTE_VIOLATION:
        return False

    if strict and level == FloatConstraint.STRONG_VIOLATION:
        return False

    return True


def downfloat_violation_level(player: EnginePlayer) -> FloatConstraint:
    """
    Determine the violation level if this player were to downfloat.

    Returns:
        FloatConstraint indicating the severity of violation (if any).
    """
    fs = player.floats

    # Absolute: already 2+ consecutive downs → this would be 3+
    if fs.consecutive_downs >= 2:
        return FloatConstraint.ABSOLUTE_VIOLATION

    # Strong: already 1 consecutive down → this would be 2
    if fs.last_was_down:
        return FloatConstraint.STRONG_VIOLATION

    # Soft: incoming downfloater being re-floated down
    if player.is_downfloater:
        return FloatConstraint.SOFT_VIOLATION

    return FloatConstraint.LEGAL


def upfloat_violation_level(player: EnginePlayer) -> FloatConstraint:
    """
    Determine the violation level if this player were to upfloat.

    Returns:
        FloatConstraint indicating the severity of violation (if any).
    """
    fs = player.floats

    # Absolute: already 2+ consecutive ups → this would be 3+
    if fs.consecutive_ups >= 2:
        return FloatConstraint.ABSOLUTE_VIOLATION

    # Strong: already 1 consecutive up → this would be 2
    if fs.last_was_up:
        return FloatConstraint.STRONG_VIOLATION

    # Soft: incoming upfloater being re-floated up
    if player.is_upfloater:
        return FloatConstraint.SOFT_VIOLATION

    return FloatConstraint.LEGAL


def select_downfloater(
    candidates: List[EnginePlayer],
    incoming_ids: set,
    strict: bool = True,
) -> Optional[EnginePlayer]:
    """
    Select the best downfloater candidate from a list of players.

    Selection criteria (FIDE C.04.3, applied in order):
        1. Must not violate absolute float limit (3+ consecutive)
        2. If strict: must not violate strong limit (2 consecutive)
        3. Prefer a resident over an incoming floater
        4. Prefer someone NOT floated last round
        5. Prefer fewer consecutive same-direction floats
        6. Prefer lowest-ranked (highest pairing_no)

    Args:
        candidates:   Players eligible for downfloating.
        incoming_ids: Set of player IDs who are incoming floaters.
        strict:       Whether to enforce strong constraints.

    Returns:
        The best candidate, or None if no legal candidate exists.
    """
    eligible = [
        p for p in candidates
        if can_downfloat(p, strict=strict)
    ]

    if not eligible:
        return None

    eligible.sort(key=lambda p: _downfloat_sort_key(p, incoming_ids))

    return eligible[0]


def rank_downfloater_candidates(
    candidates: List[EnginePlayer],
    incoming_ids: set,
    strict: bool = True,
) -> List[EnginePlayer]:
    """
    Return all legal downfloater candidates in FIDE priority order.

    Same criteria as select_downfloater but returns the full
    ordered list for use in backtracking search.

    Args:
        candidates:   Players eligible for downfloating.
        incoming_ids: Set of player IDs who are incoming floaters.
        strict:       Whether to enforce strong constraints.

    Returns:
        Ordered list (best candidate first). May be empty.
    """
    eligible = [
        p for p in candidates
        if can_downfloat(p, strict=strict)
    ]

    eligible.sort(key=lambda p: _downfloat_sort_key(p, incoming_ids))

    return eligible


def float_pair_legal(
    p1: EnginePlayer,
    p2: EnginePlayer,
    strict: bool = True,
) -> bool:
    """
    Check if a pairing between two players violates float rules.
    """
    w_down = p1.is_downfloater
    b_down = p2.is_downfloater
    
    p1_is_up = p1.is_upfloater or (b_down and not w_down)
    p2_is_up = p2.is_upfloater or (w_down and not b_down)

    if w_down:
        if not can_downfloat(p1, strict=strict):
            return False
    if b_down:
        if not can_downfloat(p2, strict=strict):
            return False

    if p1_is_up:
        if not can_upfloat(p1, strict=strict):
            return False
    if p2_is_up:
        if not can_upfloat(p2, strict=strict):
            return False

    return True


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _downfloat_sort_key(
    player: EnginePlayer,
    incoming_ids: set,
) -> Tuple[int, int, int, int, int]:
    """
    Sort key for downfloater candidate selection.

    Tuple ordering (all ascending = lower is better):
        0: Is incoming floater? (0=resident, 1=incoming → prefer resident)
        1: Was floated last round? (0=no, 1=yes → prefer not floated)
        2: Consecutive same-direction floats (fewer = better)
        3: Negative pairing number (more negative = higher pno = lower ranked → prefer)
        4: Player ID (stable tiebreak)
    """
    return (
        1 if player.id in incoming_ids else 0,
        1 if player.floats.last_was_down else 0,
        player.floats.consecutive_downs,
        -player.pno,
        player.id,
    )