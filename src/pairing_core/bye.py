"""
Pairing-allocated bye selection — FIDE C.04.2.

This module selects which player receives the pairing-allocated bye
when the number of active players is odd.

FIDE interpretation implemented here:
    1. The bye is a full-point pairing-allocated bye.
    2. Candidate order is determined globally from the bottom of the
       standings upward:
           - lower score first
           - within same score: lower-ranked player first
             (= higher pairing number)
    3. Any player who has already received a pairing-allocated bye
       is skipped as long as there exists at least one player anywhere
       in the field who has not yet received such a bye.
    4. Only when ALL active players already received a pairing bye
       may a repeated bye be assigned.
    5. Requested half-/zero-byes do not count as pairing-allocated byes.

This module is stateless and deterministic.
"""
from typing import List, Optional, Tuple

from pairing_core.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def is_bye_needed(players: List[EnginePlayer]) -> bool:
    """
    Return True if an odd number of active players requires a bye.
    """
    return len(players) % 2 == 1


def select_bye_player(
    players: List[EnginePlayer],
) -> Optional[EnginePlayer]:
    """
    Select the player who receives the pairing-allocated bye.

    Global deterministic order:
        1. Lowest score first
        2. Within equal score: lowest-ranked first
           (= highest pairing number)

    Repetition rule:
        - If at least one player has NOT yet received a pairing bye,
          only those players are eligible.
        - A player who already received a pairing bye becomes eligible
          only if ALL active players already received one.

    Args:
        players: Active EnginePlayer list.

    Returns:
        Selected EnginePlayer or None if list is empty.
    """
    if not players:
        return None

    ordered = _ordered_bye_candidates(players)

    fresh = [p for p in ordered if not p.data.received_bye]
    if fresh:
        return fresh[0]

    return ordered[0]


def validate_bye_selection(
    selected: EnginePlayer,
    all_players: List[EnginePlayer],
) -> List[str]:
    """
    Validate the bye selection and return warning strings.

    Returns:
        List[str]
    """
    warnings: List[str] = []

    if not selected:
        return ["No bye player selected"]

    if selected.id not in {p.id for p in all_players}:
        warnings.append(f"Selected bye player {selected.id} is not active.")

    fresh_exists = any(not p.data.received_bye for p in all_players)
    if selected.data.received_bye and fresh_exists:
        warnings.append(
            f"Player {selected.id} received a repeated pairing bye "
            f"while other players without bye still exist."
        )

    preferred = select_bye_player(all_players)
    if preferred is not None and preferred.id != selected.id:
        warnings.append(
            f"Selected bye player {selected.id} is not the preferred "
            f"candidate; expected {preferred.id}."
        )

    return warnings


def create_bye_card(
    player: EnginePlayer,
    board_number: int,
) -> Tuple[EnginePlayer, "PairingCard"]:
    """
    Create a bye pairing card for the selected player.

    The engine output card marks this as a pairing-allocated bye.
    """
    from pairing_core.models import PairingCard

    # We keep the returned EnginePlayer for compatibility with the
    # existing call site; no runtime mutation is required here.
    card = PairingCard(
        board=board_number,
        white_id=player.id,
        black_id=None,
        is_bye=True,
        white_float="",
        black_float="",
    )
    return player, card


# ═══════════════════════════════════════════════════════════════════
#  Internal Helpers
# ═══════════════════════════════════════════════════════════════════

def _unplayed_count(player: EnginePlayer) -> int:
    """Rounds with no game (colorless '-'): requested byes, absences,
    forfeits-without-colour. PAB rounds are also colorless but their
    holders are excluded earlier via received_bye (C2-compatible)."""
    return player.data.color_hist.count("-")


def _ordered_bye_candidates(
    players: List[EnginePlayer],
) -> List[EnginePlayer]:
    """
    Global FIDE-style bye ordering (C5 then C9):
        - lower score first (C5: minimize recipient score)
        - within same score: fewer unplayed games first (C9: minimize
          recipient's unplayed games; BBP dutch_2025_C9 test + C.04.3
          C9 criterion + BBP dutch.cpp "C9" minimization weights)
        - within same score: lower-ranked first (= higher pno)
        - stable final tie-break by id
    """
    return sorted(
        players,
        key=lambda p: (
            p.points,
            _unplayed_count(p),
            -p.pno,
            p.id,
        ),
    )