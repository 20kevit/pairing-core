"""
Swiss Pairing Engine — FIDE Dutch System (C.04.2 + C.04.3).
Effective from 1 July 2025.
This is the sole public entry point for the pairing engine.
Public API:
    pair_round(players, round_number, locked_pairs=None) -> RoundResult
    SwissEngine(players, round_number, locked_pairs=None).generate() -> RoundResult
locked_pairs:
    Optional list of (white_id, black_id) tuples. These pairs are
    excluded from automatic pairing and placed directly into the output.
    The engine validates that locked players exist, haven't played each
    other, and the color orientation is legal.
"""
from typing import Dict, List, Optional, Set, Tuple
from pairing_core.models import (
    EnginePlayer,
    PairingCard,
    PlayerData,
    RoundResult,
    make_engine_players,
)
from pairing_core.bracket import build_brackets, get_bracket_summary
from pairing_core.bye import (
    create_bye_card,
    is_bye_needed,
    _ordered_bye_candidates,
)
from pairing_core.pairer import pair_all_brackets
from pairing_core.color import is_legal_orientation


# ═══════════════════════════════════════════════════════════════
#  Public API — Functional
# ═══════════════════════════════════════════════════════════════
def pair_round(
    players: List[PlayerData],
    round_number: int,
    locked_pairs: Optional[List[Tuple[int, int]]] = None,
) -> RoundResult:
    """
    Generate pairings for a round using the FIDE Dutch system.
    Args:
        players:       List of PlayerData for all active players.
        round_number:  The round being paired.
        locked_pairs:  Optional list of (white_id, black_id) tuples
                       that must appear in the output as-is. These
                       players are excluded from automatic pairing.
    """
    engine = SwissEngine(players, round_number, locked_pairs=locked_pairs)
    return engine.generate()


# ═══════════════════════════════════════════════════════════════
#  Public API — Class-based
# ═══════════════════════════════════════════════════════════════
class SwissEngine:
    """FIDE Dutch Swiss Pairing Engine."""

    def __init__(
        self,
        players: List[PlayerData],
        round_number: int,
        locked_pairs: Optional[List[Tuple[int, int]]] = None,
    ):
        self.round_number = round_number
        self.locked_pairs: List[Tuple[int, int]] = list(locked_pairs or [])
        self._raw_players = self._normalize_input(players)

    def generate(self) -> RoundResult:
        """
        Generate pairings for the current round.
        1. Validate and extract locked pairs as PairingCards.
        2. Pair the remaining (pairable) players automatically.
        3. Combine locked + automatic pairings.
        4. Assign sequential board numbers.
        """
        # ── Edge case: no players ─────────────────────────────
        if not self._raw_players:
            return RoundResult(round_number=self.round_number)

        # ── Build engine state ────────────────────────────────
        engine_players = make_engine_players(self._raw_players)
        played_map = self._build_played_map(engine_players)

        # ── Process locked pairs ──────────────────────────────
        locked_player_ids, locked_cards = self._process_locked_pairs(
            engine_players, played_map
        )

        # ── Remaining (pairable) players ──────────────────────
        pairable = [p for p in engine_players if p.id not in locked_player_ids]

        # If all players are locked, just return locked cards
        if not pairable:
            self._assign_board_numbers(locked_cards)
            return RoundResult(
                round_number=self.round_number,
                pairings=locked_cards,
            )

        # ── Pair remaining players automatically ──────────────
        auto_result = self._pair_subset(pairable, played_map)

        # ── Combine locked + automatic ────────────────────────
        all_pairings = locked_cards + auto_result.pairings
        self._assign_board_numbers(all_pairings)

        return RoundResult(
            round_number=self.round_number,
            pairings=all_pairings,
            bye_player_id=auto_result.bye_player_id,
        )

    # ═════════════════════════════════════════════════════════
    #  Locked Pairs Processing
    # ═════════════════════════════════════════════════════════
    def _process_locked_pairs(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> Tuple[Set[int], List[PairingCard]]:
        """
        Validate locked_pairs and convert them to PairingCards.
        Returns:
            (locked_player_ids, locked_cards)
        Raises:
            ValueError if any locked pair is invalid.
        """
        if not self.locked_pairs:
            return set(), []

        player_map: Dict[int, EnginePlayer] = {p.id: p for p in engine_players}
        locked_ids: Set[int] = set()
        locked_cards: List[PairingCard] = []

        for idx, (w_id, b_id) in enumerate(self.locked_pairs):
            # Players must exist
            if w_id not in player_map:
                raise ValueError(
                    f"Locked pair #{idx + 1}: white player {w_id} "
                    f"is not in the active player list."
                )
            if b_id not in player_map:
                raise ValueError(
                    f"Locked pair #{idx + 1}: black player {b_id} "
                    f"is not in the active player list."
                )
            # No self-pairing
            if w_id == b_id:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {w_id} "
                    f"cannot be paired with themselves."
                )
            # No repeat opponents
            if b_id in played_map.get(w_id, set()) or w_id in played_map.get(b_id, set()):
                raise ValueError(
                    f"Locked pair #{idx + 1}: players {w_id} and {b_id} "
                    f"have already played each other."
                )
            # Each player appears at most once
            if w_id in locked_ids:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {w_id} "
                    f"appears in multiple locked pairs."
                )
            if b_id in locked_ids:
                raise ValueError(
                    f"Locked pair #{idx + 1}: player {b_id} "
                    f"appears in multiple locked pairs."
                )
            locked_ids.add(w_id)
            locked_ids.add(b_id)

            # Color orientation must be legal
            w_player = player_map[w_id]
            b_player = player_map[b_id]
            if not is_legal_orientation(w_player, b_player):
                raise ValueError(
                    f"Locked pair #{idx + 1}: assigning white to {w_id} "
                    f"and black to {b_id} violates FIDE color rules "
                    f"(3-consecutive or balance limit)."
                )

            locked_cards.append(PairingCard(
                board=0,  # assigned later
                white_id=w_id,
                black_id=b_id,
                is_bye=False,
            ))

        return locked_ids, locked_cards

    # ═════════════════════════════════════════════════════════
    #  Subset Pairing (for remaining players after locks)
    # ═════════════════════════════════════════════════════════
    def _pair_subset(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """
        Pair a subset of players (those not in locked_pairs).
        Handles bye selection if the subset has odd count.
        """
        if not engine_players:
            return RoundResult(round_number=self.round_number, pairings=[])

        if len(engine_players) == 1:
            # Single player left -> must receive the pairing bye
            player = engine_players[0]
            _, bye_card = create_bye_card(player, board_number=0)
            return RoundResult(
                round_number=self.round_number,
                pairings=[bye_card],
                bye_player_id=player.id,
            )

        if not is_bye_needed(engine_players):
            return self._pair_without_bye(engine_players, played_map)
        else:
            return self._pair_with_bye(engine_players, played_map)

    # ═════════════════════════════════════════════════════════
    #  Internal Pairing Helpers
    # ═════════════════════════════════════════════════════════
    def _pair_without_bye(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """Pair all players (even count, no bye)."""
        brackets = build_brackets(engine_players)
        pairing_cards = pair_all_brackets(
            brackets=brackets,
            played_map=played_map,
            round_number=self.round_number,
        )
        if pairing_cards is None:
            raise ValueError(
                f"Round {self.round_number}: "
                f"No legal FIDE Dutch pairing exists for "
                f"{len(engine_players)} players. "
                f"Possible causes:\n"
                f"  - All players have played each other\n"
                f"  - Color constraints are too restrictive\n"
                f"  - Float constraints prevent valid pairing\n"
                f"Bracket structure:\n{get_bracket_summary(brackets)}"
            )
        return RoundResult(
            round_number=self.round_number,
            pairings=pairing_cards,
        )

    def _pair_with_bye(
        self,
        engine_players: List[EnginePlayer],
        played_map: Dict[int, Set[int]],
    ) -> RoundResult:
        """
        Pair with bye.
        Candidate policy:
            1. If any player has not yet received a pairing bye,
               ONLY those players are considered.
            2. Repeated byes are considered only if all active players
               already received a pairing-allocated bye.
        """
        bye_candidates = self._get_bye_candidates(engine_players)
        for bye_player in bye_candidates:
            pairing_players = [
                p for p in engine_players if p.id != bye_player.id
            ]
            if len(pairing_players) < 2:
                _, bye_card = create_bye_card(bye_player, board_number=0)
                return RoundResult(
                    round_number=self.round_number,
                    pairings=[bye_card],
                    bye_player_id=bye_player.id,
                )
            brackets = build_brackets(pairing_players)
            pairing_cards = pair_all_brackets(
                brackets=brackets,
                played_map=played_map,
                round_number=self.round_number,
            )
            if pairing_cards is not None:
                _, bye_card = create_bye_card(bye_player, board_number=0)
                pairing_cards.append(bye_card)
                return RoundResult(
                    round_number=self.round_number,
                    pairings=pairing_cards,
                    bye_player_id=bye_player.id,
                )
        raise ValueError(
            f"Round {self.round_number}: "
            f"No legal FIDE Dutch pairing exists for "
            f"{len(engine_players)} players under current bye constraints."
        )

    def _get_bye_candidates(
        self,
        players: List[EnginePlayer],
    ) -> List[EnginePlayer]:
        # Ordering is delegated to the canonical FIDE implementation in
        # bye.py so the engine and the standalone module cannot drift.
        ordered = _ordered_bye_candidates(players)
        # Prefer players who have NOT yet received a pairing-allocated bye;
        # only when everyone has one does the raw order apply.
        fresh = [p for p in ordered if not p.data.received_bye]
        return fresh if fresh else ordered

    # ═════════════════════════════════════════════════════════
    #  Input Normalization
    # ═════════════════════════════════════════════════════════
    @staticmethod
    def _normalize_input(players: list) -> List[PlayerData]:
        """
        Accept both PlayerData and legacy PlayerSnapshot objects.
        """
        normalized: List[PlayerData] = []
        for p in players:
            status = getattr(p, "status", "active")
            if status != "active":
                continue
            if isinstance(p, PlayerData):
                normalized.append(p)
                continue
            player_id = getattr(p, "id", 0)
            pairing_no = getattr(p, "pairing_no", 0)
            if pairing_no == 0:
                pairing_no = getattr(p, "start_number", player_id)
            rating = getattr(p, "rating", 0) or 0
            points = getattr(p, "points", 0.0) or 0.0
            color_hist = getattr(p, "color_hist", "")
            if not color_hist:
                color_hist = getattr(p, "color_history", "")
            if not color_hist:
                color_hist = _build_legacy_color_hist(p)
            opponents_raw = getattr(p, "opponents", None)
            if opponents_raw is None:
                played_list = getattr(p, "played_against", [])
                played_set = getattr(p, "played_ids", None)
                if played_set is not None:
                    opponents_raw = frozenset(played_set)
                elif played_list:
                    opponents_raw = frozenset(played_list)
                else:
                    opponents_raw = frozenset()
            elif not isinstance(opponents_raw, frozenset):
                opponents_raw = frozenset(opponents_raw)
            received_bye = getattr(p, "received_bye", False)
            float_hist = getattr(p, "float_hist", "")
            if not float_hist:
                float_hist = getattr(p, "float_history", "")
            normalized.append(PlayerData(
                id=player_id,
                pairing_no=pairing_no,
                rating=rating,
                points=points,
                color_hist=color_hist,
                opponents=opponents_raw,
                received_bye=received_bye,
                float_hist=float_hist,
            ))
        return normalized

    # ═════════════════════════════════════════════════════════
    #  Internal Helpers
    # ═════════════════════════════════════════════════════════
    @staticmethod
    def _build_played_map(
        players: List[EnginePlayer],
    ) -> Dict[int, Set[int]]:
        played: Dict[int, Set[int]] = {}
        for p in players:
            played[p.id] = set(p.data.opponents)
        return played

    @staticmethod
    def _assign_board_numbers(pairings: List[PairingCard]) -> None:
        """
        Final board numbering:
            - normal pairings first (in input order)
            - bye last
        """
        normal = [p for p in pairings if not p.is_bye]
        byes = [p for p in pairings if p.is_bye]
        ordered = normal + byes
        for idx, card in enumerate(ordered, start=1):
            card.board = idx
        pairings[:] = ordered


# ═══════════════════════════════════════════════════════════════
#  Legacy Color History Builder
# ═══════════════════════════════════════════════════════════════
def _build_legacy_color_hist(player) -> str:
    """
    Build a minimal color history string from legacy fields
    (color_balance, last_color).
    This is only a best-effort fallback.
    """
    balance = getattr(player, "color_balance", 0) or 0
    last_color = getattr(player, "last_color", "") or ""
    if balance == 0 and not last_color:
        return ""
    history = []
    whites = max(0, balance)
    blacks = max(0, -balance)
    total = whites + blacks
    if total == 0 and last_color:
        return last_color[0]
    for _ in range(total):
        if whites > blacks:
            history.append("w")
            whites -= 1
        elif blacks > whites:
            history.append("b")
            blacks -= 1
        else:
            if history and history[-1] == "w":
                history.append("b")
            else:
                history.append("w")
    if last_color and history:
        expected_last = last_color[0]
        if history[-1] != expected_last:
            if len(history) >= 2:
                history[-1], history[-2] = history[-2], history[-1]
            else:
                history[-1] = expected_last
    return "".join(history)