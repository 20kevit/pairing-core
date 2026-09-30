"""
Color assignment engine — FIDE C.04.2.

This module determines the color (white/black) assignment for any
pair of players. It implements the full FIDE priority chain:

    Priority 1 (Absolute):
        A player who has had the same color in the last two rounds
        MUST receive the opposite color. A player whose color balance
        is at ±2 MUST receive the equalizing color.
        Violation of this rule makes a pairing ILLEGAL.

    Priority 2 (Strong):
        A player whose color balance is not zero SHOULD receive
        the equalizing color.

    Priority 3 (Mild):
        A player whose color balance is zero but has played at least
        one game SHOULD alternate from their last color.

    Priority 4 (Default):
        The higher-ranked player (lower pairing number) receives
        their due color. If neither player has a due color, the
        higher-ranked player gets white.

When two players have conflicting preferences of the SAME strength,
the higher-ranked player's preference takes priority (C.04.3).

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Optional, Tuple

from pairing_core.models import ColorPref, ColorState, EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def assign_colors(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Determine (white_player, black_player) for a legal pairing.
    
    Applies FIDE C.04.2 color rules in strict priority order:
    
    Priority 1 (Absolute - C.04.2.a):
        - 3 consecutive same color → MUST receive opposite
        - Color balance ±2 → MUST receive equalizing color
    
    Priority 2 (Strong - C.04.2.b):
        - Color balance ≠ 0 → SHOULD receive equalizing color
    
    Priority 3 (Mild - C.04.2.c):
        - Color balance = 0, games played → SHOULD alternate
    
    Priority 4 (Default - C.04.2.d):
        - Higher-ranked player receives due color
        - If no due color, higher-ranked gets white
    
    Conflict resolution (C.04.3):
        When two players have conflicting preferences of SAME strength,
        the higher-ranked player's preference takes priority.
    
    Args:
        p1: First player.
        p2: Second player.
    
    Returns:
        (white, black) tuple of EnginePlayer.
    
    Note:
        If no legal orientation exists (both have same absolute
        obligation), this function still returns the least-bad
        orientation. The caller should check legality separately
        using `is_legal_orientation()`.
    """
    # ── Priority 1: Absolute Color Obligations ─────────────────────
    # If exactly one player has an absolute need, satisfy it.
    if p1.must_white() and not p2.must_white():
        return p1, p2
    if p2.must_white() and not p1.must_white():
        return p2, p1
    if p1.must_black() and not p2.must_black():
        return p2, p1
    if p2.must_black() and not p1.must_black():
        return p1, p2

    # Both have absolute same direction: conflict.
    # Higher-ranked player wins (lower pairing number).
    if p1.must_white() and p2.must_white():
        return _higher_ranked_gets(p1, p2, "w")
    if p1.must_black() and p2.must_black():
        return _higher_ranked_gets(p1, p2, "b")

    # ── Priority 2: Strong Color Preference ────────────────────────
    c1 = p1.color
    c2 = p2.color
    s1 = p1.pref_strength()
    s2 = p2.pref_strength()

    # One has strong/absolute, the other doesn't
    if s1 > s2 and s1 >= 2:
        return _give_preferred(p1, p2)
    if s2 > s1 and s2 >= 2:
        return _give_preferred(p2, p1)

    # Both have strong preference
    if s1 >= 2 and s2 >= 2:
        # Opposite directions: both satisfied
        if c1.preference.direction != c2.preference.direction:
            return _give_preferred(p1, p2)
        # Same direction: higher ranked wins
        return _higher_ranked_gets_pref(p1, p2)

    # ── Priority 3: Mild Color Preference ──────────────────────────
    if s1 == 1 and s2 == 0:
        return _give_preferred(p1, p2)
    if s2 == 1 and s1 == 0:
        return _give_preferred(p2, p1)

    if s1 == 1 and s2 == 1:
        # Both mild: opposite directions → both satisfied
        if c1.preference.direction != c2.preference.direction:
            return _give_preferred(p1, p2)
        # Same direction: higher ranked wins
        return _higher_ranked_gets_pref(p1, p2)

    # ── Priority 4: Default ────────────────────────────────────────
    return _default_assignment(p1, p2)


def is_legal_orientation(
    white: EnginePlayer,
    black: EnginePlayer,
) -> bool:
    """
    Check if assigning white/black in this orientation is legal.

    A color assignment is ILLEGAL if:
        - White player would get 3 consecutive whites
        - Black player would get 3 consecutive blacks
        - White player's color balance would exceed +2
        - Black player's color balance would go below -2
        - White player has ABSOLUTE_BLACK obligation
        - Black player has ABSOLUTE_WHITE obligation

    Returns:
        True if the orientation is legal.
    """
    wc = white.color
    bc = black.color

    # Three consecutive same color
    if wc.last_two == "ww":
        return False
    if bc.last_two == "bb":
        return False

    # Balance limit: after this game, white gets +1, black gets -1
    if wc.balance >= 2:
        return False
    if bc.balance <= -2:
        return False

    # Absolute obligations
    if wc.must_black:
        return False
    if bc.must_white:
        return False

    return True


def has_legal_assignment(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> bool:
    """
    Check if ANY legal color assignment exists for this pair.

    Returns True if at least one of (p1=W, p2=B) or (p1=B, p2=W)
    is legal.
    """
    return is_legal_orientation(p1, p2) or is_legal_orientation(p2, p1)


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _give_preferred(
    preferred: EnginePlayer,
    other: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """Give `preferred` the color they want."""
    if preferred.color.preference.wants_white:
        return preferred, other
    if preferred.color.preference.wants_black:
        return other, preferred
    # No direction (shouldn't happen if strength > 0)
    return _default_assignment(preferred, other)


def _higher_ranked_gets(
    p1: EnginePlayer,
    p2: EnginePlayer,
    color: str,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """Give the higher-ranked player the specified color."""
    higher = p1 if p1.pno < p2.pno else p2
    lower = p2 if higher is p1 else p1

    if color == "w":
        return higher, lower
    return lower, higher


def _higher_ranked_gets_pref(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Both players have same-direction preference.
    Higher-ranked player gets their preference.
    """
    higher = p1 if p1.pno < p2.pno else p2
    return _give_preferred(higher, p2 if higher is p1 else p1)


def _default_assignment(
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Tuple[EnginePlayer, EnginePlayer]:
    """
    Default color assignment when no preferences apply.

    FIDE: Higher-ranked player receives their due color.
    If no due color, higher-ranked gets white.
    """
    higher = p1 if p1.pno < p2.pno else p2
    lower = p2 if higher is p1 else p1

    if higher.color.due_color == "b":
        return lower, higher
    # Due white, or no due color → higher ranked gets white
    return higher, lower