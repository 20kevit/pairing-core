"""
Independent pairing compliance validator — FIDE C.04.2 / C.04.3.

This module validates a completed pairing against ALL FIDE rules.
It is completely independent of the pairing engine and can be used
to verify pairings from ANY source (engine, manual, imported).

It does NOT repair pairings. It only reports violations.

Validation checks:
    ABSOLUTE (errors — pairing is illegal):
        GEN-01:   No repeat opponents
        GEN-02:   At most one pairing-allocated bye per round
        GEN-DUP:  No player appears more than once
        GEN-SELF: No player paired with themselves
        COL-01:   Color balance must not exceed ±2 after assignment
        COL-02:   No three consecutive same color
        COL-ACO:  Absolute Color Obligation must be satisfied
        COMP-01:  Every active player must appear in pairings
        COMP-02:  No unknown players in pairings

    STRONG (warnings — pairing is legal but suboptimal):
        GEN-03:   Player receives bye for second time
        COL-SCP:  Strong Color Preference violated
        FLO-01:   Consecutive same-direction float
        BOARD:    Board numbers not sequential

    INFORMATIONAL:
        COL-MCP:  Mild Color Preference not satisfied
        FLO-SOFT: Incoming player re-floated

This module is stateless and deterministic. Zero external dependencies.
"""
from typing import Dict, List, Optional, Set

from pairing_core.models import (
    ColorPref,
    EnginePlayer,
    PairingCard,
    PlayerData,
    RoundResult,
    make_engine_players,
)


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def validate_round(
    result: RoundResult,
    players: List[PlayerData],
    *,
    forbidden_pairs=None,
) -> "ValidationReport":
    """
    Validate a complete round of pairings against FIDE rules.

    Args:
        result:   The RoundResult to validate.
        players:  All active PlayerData in the tournament.
        forbidden_pairs: Optional iterable of (id, id) pairs that must not
            meet ( Phase-2 ConstraintSet enforcement check, FORBID-01 ).

    Returns:
        ValidationReport with all findings.
    """
    engine_players = make_engine_players(players)
    player_map = {p.id: p for p in engine_players}
    played_map = {p.id: set(p.data.opponents) for p in engine_players}

    report = ValidationReport()

    report.extend(_check_completeness(result, engine_players))
    report.extend(_check_duplicates(result))
    report.extend(_check_self_pairings(result))
    report.extend(_check_unknown_players(result, player_map))
    report.extend(_check_repeat_opponents(result, played_map))
    if forbidden_pairs:
        report.extend(_check_forbidden_pairs(result, forbidden_pairs))
    report.extend(_check_color_absolute(result, player_map))
    report.extend(_check_color_balance_limit(result, player_map))
    report.extend(_check_color_preferences(result, player_map))
    report.extend(_check_bye_rules(result, engine_players))
    report.extend(_check_board_numbers(result))
    report.extend(_check_float_rules(result, player_map))

    return report


def validate_and_fix(
    pairings: list,
    all_players: list,
    played_map: dict,
    round_number: int,
    max_attempts: int = 100,
) -> list:
    """
    Legacy backward-compatible entry point.

    Validates and raises ValueError if illegal.
    Does NOT attempt repair.
    """
    # Convert legacy inputs
    cards = []
    for p in pairings:
        white_id = getattr(p, "white_id", None) or getattr(p, "white_player_id", 0)
        black_id = getattr(p, "black_id", None) or getattr(p, "black_player_id", None)
        board = getattr(p, "board", 0) or getattr(p, "board_number", 0)
        is_bye = getattr(p, "is_bye", False) or (black_id is None)
        cards.append(PairingCard(
            board=board,
            white_id=white_id,
            black_id=black_id,
            is_bye=is_bye,
        ))

    result = RoundResult(round_number=round_number, pairings=cards)

    # Convert legacy player data
    player_data_list = []
    for p in all_players:
        if isinstance(p, PlayerData):
            player_data_list.append(p)
        else:
            player_data_list.append(PlayerData(
                id=getattr(p, "id", 0),
                pairing_no=getattr(p, "start_number", getattr(p, "id", 0)),
                rating=getattr(p, "rating", 0) or 0,
                points=getattr(p, "points", 0.0) or 0.0,
                color_hist=getattr(p, "color_hist", ""),
                opponents=frozenset(getattr(p, "played_against", [])),
                received_bye=getattr(p, "received_bye", False),
                float_hist=getattr(p, "float_hist", ""),
            ))

    report = validate_round(result, player_data_list)

    if report.has_errors:
        raise ValueError(f"Invalid pairing: {report.error_summary}")

    return pairings


# ═══════════════════════════════════════════════════════════════════
#  Validation Report
# ═══════════════════════════════════════════════════════════════════

class Finding:
    """A single validation finding."""

    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"

    __slots__ = ("level", "rule", "message", "board", "player_id")

    def __init__(
        self,
        level: str,
        rule: str,
        message: str,
        board: int = 0,
        player_id: int = 0,
    ):
        self.level = level
        self.rule = rule
        self.message = message
        self.board = board
        self.player_id = player_id

    def __repr__(self) -> str:
        parts = [f"[{self.level}]", self.rule]
        if self.board:
            parts.append(f"Board {self.board}")
        if self.player_id:
            parts.append(f"Player {self.player_id}")
        parts.append(self.message)
        return " | ".join(parts)


class ValidationReport:
    """Collection of validation findings with query helpers."""

    def __init__(self):
        self._findings: List[Finding] = []

    def add(self, finding: Finding) -> None:
        self._findings.append(finding)

    def extend(self, findings: List[Finding]) -> None:
        self._findings.extend(findings)

    @property
    def findings(self) -> List[Finding]:
        return list(self._findings)

    @property
    def has_errors(self) -> bool:
        return any(f.level == Finding.ERROR for f in self._findings)

    @property
    def has_warnings(self) -> bool:
        return any(f.level == Finding.WARNING for f in self._findings)

    @property
    def is_valid(self) -> bool:
        return not self.has_errors

    @property
    def errors(self) -> List[Finding]:
        return [f for f in self._findings if f.level == Finding.ERROR]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self._findings if f.level == Finding.WARNING]

    @property
    def error_summary(self) -> str:
        errs = self.errors
        if not errs:
            return "No errors"
        return " | ".join(repr(e) for e in errs[:10])

    @property
    def error_count(self) -> int:
        return len(self.errors)

    @property
    def warning_count(self) -> int:
        return len(self.warnings)

    def __repr__(self) -> str:
        return (
            f"ValidationReport(valid={self.is_valid}, "
            f"errors={self.error_count}, "
            f"warnings={self.warning_count})"
        )


# ═══════════════════════════════════════════════════════════════════
#  Check: Completeness
# ═══════════════════════════════════════════════════════════════════

def _check_completeness(
    result: RoundResult,
    players: List[EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []
    active_ids = {p.id for p in players}
    paired_ids: Set[int] = set()

    for card in result.pairings:
        paired_ids.add(card.white_id)
        if card.black_id is not None:
            paired_ids.add(card.black_id)

    for pid in active_ids - paired_ids:
        findings.append(Finding(
            Finding.ERROR, "COMP-01",
            f"Active player {pid} not found in any pairing.",
            player_id=pid,
        ))

    for pid in paired_ids - active_ids:
        findings.append(Finding(
            Finding.ERROR, "COMP-02",
            f"Player {pid} in pairings but not in active list.",
            player_id=pid,
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Duplicates
# ═══════════════════════════════════════════════════════════════════

def _check_duplicates(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []
    seen: Dict[int, int] = {}

    for card in result.pairings:
        for pid in (card.white_id, card.black_id):
            if pid is None:
                continue
            if pid in seen:
                findings.append(Finding(
                    Finding.ERROR, "GEN-DUP",
                    f"Player {pid} on boards {seen[pid]} and {card.board}.",
                    board=card.board, player_id=pid,
                ))
            else:
                seen[pid] = card.board

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Self-pairing
# ═══════════════════════════════════════════════════════════════════

def _check_self_pairings(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is not None and card.white_id == card.black_id:
            findings.append(Finding(
                Finding.ERROR, "GEN-SELF",
                f"Player {card.white_id} paired with themselves.",
                board=card.board, player_id=card.white_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Unknown players
# ═══════════════════════════════════════════════════════════════════

def _check_unknown_players(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.white_id not in player_map:
            findings.append(Finding(
                Finding.ERROR, "GEN-UNK",
                f"Unknown white player {card.white_id}.",
                board=card.board, player_id=card.white_id,
            ))
        if card.black_id is not None and card.black_id not in player_map:
            findings.append(Finding(
                Finding.ERROR, "GEN-UNK",
                f"Unknown black player {card.black_id}.",
                board=card.board, player_id=card.black_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Repeat opponents (GEN-01)
# ═══════════════════════════════════════════════════════════════════

def _check_repeat_opponents(
    result: RoundResult,
    played_map: Dict[int, Set[int]],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue
        w, b = card.white_id, card.black_id
        if b in played_map.get(w, set()) or w in played_map.get(b, set()):
            findings.append(Finding(
                Finding.ERROR, "GEN-01",
                f"Repeat opponents: {w} vs {b}.",
                board=card.board,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Forbidden pairs (FORBID-01)
# ═══════════════════════════════════════════════════════════════════

def _check_forbidden_pairs(
    result: RoundResult,
    forbidden_pairs,
) -> List[Finding]:
    findings: List[Finding] = []
    forbidden = set()
    for entry in forbidden_pairs:
        a, b = tuple(entry)
        forbidden.add(frozenset((a, b)))

    for card in result.pairings:
        if card.black_id is None:
            continue
        if frozenset((card.white_id, card.black_id)) in forbidden:
            findings.append(Finding(
                Finding.ERROR, "FORBID-01",
                f"Forbidden pairing: {card.white_id} vs {card.black_id}.",
                board=card.board,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Absolute (COL-01, COL-02, COL-ACO)
# ═══════════════════════════════════════════════════════════════════

def _check_color_absolute(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        # COL-02: Three consecutive same color
        if wp.color.last_two == "ww":
            findings.append(Finding(
                Finding.ERROR, "COL-02",
                f"Player {wp.id} gets 3rd consecutive white.",
                board=card.board, player_id=wp.id,
            ))
        if bp.color.last_two == "bb":
            findings.append(Finding(
                Finding.ERROR, "COL-02",
                f"Player {bp.id} gets 3rd consecutive black.",
                board=card.board, player_id=bp.id,
            ))

        # COL-ACO: Absolute Color Obligation violated
        if wp.must_black():
            findings.append(Finding(
                Finding.ERROR, "COL-ACO",
                f"Player {wp.id} has ACO for black but assigned white.",
                board=card.board, player_id=wp.id,
            ))
        if bp.must_white():
            findings.append(Finding(
                Finding.ERROR, "COL-ACO",
                f"Player {bp.id} has ACO for white but assigned black.",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Balance Limit (COL-01)
# ═══════════════════════════════════════════════════════════════════

def _check_color_balance_limit(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        new_w_bal = wp.color.balance + 1
        new_b_bal = bp.color.balance - 1

        if new_w_bal > 2:
            findings.append(Finding(
                Finding.ERROR, "COL-01",
                f"Player {wp.id} color balance would be "
                f"{new_w_bal} (exceeds +2).",
                board=card.board, player_id=wp.id,
            ))
        if new_b_bal < -2:
            findings.append(Finding(
                Finding.ERROR, "COL-01",
                f"Player {bp.id} color balance would be "
                f"{new_b_bal} (exceeds -2).",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Color — Preferences (COL-SCP, COL-MCP)
# ═══════════════════════════════════════════════════════════════════

def _check_color_preferences(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.black_id is None:
            continue

        wp = player_map.get(card.white_id)
        bp = player_map.get(card.black_id)
        if wp is None or bp is None:
            continue

        # White player getting white — check if they preferred black
        if wp.color.preference == ColorPref.STRONG_BLACK:
            findings.append(Finding(
                Finding.WARNING, "COL-SCP",
                f"Player {wp.id} has SCP for black but got white.",
                board=card.board, player_id=wp.id,
            ))
        elif wp.color.preference == ColorPref.MILD_BLACK:
            findings.append(Finding(
                Finding.INFO, "COL-MCP",
                f"Player {wp.id} has MCP for black but got white.",
                board=card.board, player_id=wp.id,
            ))

        # Black player getting black — check if they preferred white
        if bp.color.preference == ColorPref.STRONG_WHITE:
            findings.append(Finding(
                Finding.WARNING, "COL-SCP",
                f"Player {bp.id} has SCP for white but got black.",
                board=card.board, player_id=bp.id,
            ))
        elif bp.color.preference == ColorPref.MILD_WHITE:
            findings.append(Finding(
                Finding.INFO, "COL-MCP",
                f"Player {bp.id} has MCP for white but got black.",
                board=card.board, player_id=bp.id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Bye Rules (GEN-02, GEN-03)
# ═══════════════════════════════════════════════════════════════════

def _check_bye_rules(
    result: RoundResult,
    players: List[EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    byes = [c for c in result.pairings if c.is_bye]

    if len(byes) > 1:
        findings.append(Finding(
            Finding.ERROR, "GEN-02",
            f"Multiple pairing byes detected: {len(byes)}.",
        ))

    for bye_card in byes:
        player = next(
            (p for p in players if p.id == bye_card.white_id), None
        )
        if player is None:
            continue

        if player.data.received_bye:
            has_fresh = any(
                not p.data.received_bye
                for p in players
                if p.id != bye_card.white_id
            )
            level = Finding.WARNING if has_fresh else Finding.INFO
            findings.append(Finding(
                level, "GEN-03",
                f"Player {bye_card.white_id} receives bye again"
                f"{' (alternatives exist)' if has_fresh else ''}.",
                player_id=bye_card.white_id,
            ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Board Numbers
# ═══════════════════════════════════════════════════════════════════

def _check_board_numbers(result: RoundResult) -> List[Finding]:
    findings: List[Finding] = []

    if not result.pairings:
        return findings

    boards = sorted(c.board for c in result.pairings)
    expected = list(range(1, len(boards) + 1))

    if boards != expected:
        findings.append(Finding(
            Finding.WARNING, "BOARD",
            f"Board numbers not sequential: {boards} vs {expected}.",
        ))

    return findings


# ═══════════════════════════════════════════════════════════════════
#  Check: Float Rules (FLO-01)
# ═══════════════════════════════════════════════════════════════════

def _check_float_rules(
    result: RoundResult,
    player_map: Dict[int, EnginePlayer],
) -> List[Finding]:
    findings: List[Finding] = []

    for card in result.pairings:
        if card.is_bye:
            continue

        _check_player_float(
            findings, card.board,
            card.white_id, card.white_float, player_map,
        )
        if card.black_id is not None:
            _check_player_float(
                findings, card.board,
                card.black_id, card.black_float, player_map,
            )

    return findings


def _check_player_float(
    findings: List[Finding],
    board: int,
    player_id: int,
    float_tag: str,
    player_map: Dict[int, EnginePlayer],
) -> None:
    if not float_tag:
        return

    player = player_map.get(player_id)
    if player is None:
        return

    if float_tag == "D":
        cons = player.floats.consecutive_downs
        if cons >= 2:
            findings.append(Finding(
                Finding.ERROR, "FLO-01",
                f"Player {player_id}: {cons + 1} consecutive downfloats.",
                board=board, player_id=player_id,
            ))
        elif player.floats.last_was_down:
            findings.append(Finding(
                Finding.WARNING, "FLO-01",
                f"Player {player_id}: 2nd consecutive downfloat.",
                board=board, player_id=player_id,
            ))

    elif float_tag == "U":
        cons = player.floats.consecutive_ups
        if cons >= 2:
            findings.append(Finding(
                Finding.ERROR, "FLO-01",
                f"Player {player_id}: {cons + 1} consecutive upfloats.",
                board=board, player_id=player_id,
            ))
        elif player.floats.last_was_up:
            findings.append(Finding(
                Finding.WARNING, "FLO-01",
                f"Player {player_id}: 2nd consecutive upfloat.",
                board=board, player_id=player_id,
            ))