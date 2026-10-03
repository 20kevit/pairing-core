"""Shared 2026 primitives (FIDE articles only; no vendor concepts).

- Colour histories: played-only semantics per C.04.2 Art.3.4 (unplayed 'u'
  rounds do not enter colour sequences; histories behave as if 'u' shifted
  to the front, i.e. they are dropped for colour computation).
- Preferences: Dutch 1.7 family (Dutch/Burstein zero-game = none; Dubov
  zero-game = mild Black per C.04.4.1 Art.1.6.4), Team Type A/B (C.04.6 1.7).
- PAB eligibility: C.04.1 Art.4 (got_pab or forfeit_win blocks).
- Stepper: deterministic budget/cancel checkpoints (EngineTimeoutError /
  CancelledError); wall-clock checked every 1024 steps (deterministic cadence).
- Board order: C.04.2 Art.3.6 recommended sort (score of higher-ranked, pair
  score sum, smaller TPN of higher-ranked).
"""

from __future__ import annotations

import time
from itertools import combinations
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from pairing_core.controls import CancelToken, ExecutionBudgets
from pairing_core.errors import (
    CancelledError,
    EngineTimeoutError,
    ImpossiblePairingError,
)
from pairing_core.fide2026.models import P26Player

DEFAULT_STEP_CAP = 2_000_000


def played_colors(p: P26Player) -> str:
    """Colour sequence with unplayed rounds removed (C.04.2 Art.3.4)."""
    return "".join(c for c in p.colors if c in ("W", "B"))


def last_differing_round(a: P26Player, b: P26Player):
    """Most recent round where both played AND had opposite colours.

    Returns (colour_of_a, colour_of_b) or None. Round-index aligned (unplayed
    'u' rounds keep their slots): C.04.2 Art.3.4 played-only semantics applied
    per-round, NOT by zipping played-only sequences (which misaligns whenever
    either side has unplayed rounds). Used by every Art.5/4.3/5.4/7.6
    alternation walkback (Dutch 5.2.3, Dubov 5.2.4, Burstein 5.2.4,
    Double 4.3.3, Team 4.3.6, Lim 5.4, Olympiad 7.6).
    """
    ca = a.colors
    cb = b.colors
    for i in range(min(len(ca), len(cb)) - 1, -1, -1):
        xa, xb = ca[i], cb[i]
        if xa in ("W", "B") and xb in ("W", "B") and xa != xb:
            return (xa, xb)
    return None


def colour_difference(p: P26Player) -> int:
    """White games minus Black games over played games (Dutch 1.6)."""
    seq = played_colors(p)
    return seq.count("W") - seq.count("B")


def preference(p: P26Player, *, dubov_zero_game: bool = False) -> Tuple[Optional[str], int]:
    """(colour, strength): strength 3 absolute / 2 strong / 1 mild / 0 none.

    Dutch Art.1.7 (Burstein 1.5 identical). Dubov 1.6.4 differs only for
    zero-game players (mild Black); pass dubov_zero_game=True there.
    """
    seq = played_colors(p)
    if not seq:
        if dubov_zero_game:
            return ("B", 1)
        return (None, 0)
    cd = seq.count("W") - seq.count("B")
    last2 = seq[-2:]
    if cd > 1 or last2 == "WW":
        return ("B", 3)
    if cd < -1 or last2 == "BB":
        return ("W", 3)
    if cd == 1:
        return ("B", 2)
    if cd == -1:
        return ("W", 2)
    # mild: alternate last played
    return ("B" if seq[-1] == "W" else "W", 1)


def team_preference(p: P26Player, *, kind: str = "A",
                    is_last_round: bool = False) -> Tuple[Optional[str], int]:
    """Team colour preference (C.04.6 Art.1.7). kind: 'A', 'B', or 'none'.

    Strength: Type A simple = 1; Type B strong = 2 / mild = 1. Unplayed
    matches count as no colour (board-1 scheduled colour only when played).
    """
    if kind == "none":
        return (None, 0)
    seq = played_colors(p)
    cd = seq.count("W") - seq.count("B")
    last2 = seq[-2:] if len(seq) >= 2 else ""
    last1 = seq[-1:] if seq else ""
    if kind == "A":
        if cd < -1 or ((cd == 0 or cd == -1) and last2 == "BB"):
            return ("W", 1)
        if cd > 1 or ((cd == 0 or cd == 1) and last2 == "WW"):
            return ("B", 1)
        return (None, 0)
    # Type B
    if cd < -1 or ((cd == 0 or cd == -1) and last2 == "BB"):
        return ("W", 2)
    if cd > 1 or ((cd == 0 or cd == 1) and last2 == "WW"):
        return ("B", 2)
    if cd == -1 or (cd == 0 and not is_last_round and last1 == "B"):
        return ("W", 1)
    if cd == 1 or (cd == 0 and not is_last_round and last1 == "W"):
        return ("B", 1)
    return (None, 0)


def pab_eligible(p: P26Player) -> bool:
    """C.04.1 Art.4: no PAB and no unplayed win-value score since."""
    return not p.got_pab and not p.forfeit_win


def rematch(a: P26Player, b: P26Player) -> bool:
    """C.04.1 Art.2: opponents who met (played) may not meet again."""
    return b.id in a.opponents or a.id in b.opponents


class Stepper:
    """Deterministic step budget + cancellation + wall-clock boundary."""

    def __init__(self, budgets: Optional[ExecutionBudgets] = None,
                 cancel_token: Optional[CancelToken] = None) -> None:
        cap = DEFAULT_STEP_CAP
        clock = None
        if budgets is not None:
            if budgets.max_steps is not None:
                cap = budgets.max_steps
            clock = budgets.wall_clock_seconds
        self._cap = cap
        self._cancel = cancel_token
        self._deadline = (time.monotonic() + clock) if clock else None
        self.steps = 0

    def tick(self) -> None:
        self.steps += 1
        if self.steps > self._cap:
            raise EngineTimeoutError(
                f"step budget exhausted ({self._cap} steps).")
        if self._cancel is not None and self._cancel.cancelled:
            raise CancelledError("pairing run cancelled.")
        if self._deadline is not None and self.steps % 1024 == 0 \
                and time.monotonic() > self._deadline:
            raise EngineTimeoutError("wall-clock budget exhausted.")


def lexicographic_sets(pool: Sequence[int], k: int) -> Iterable[Tuple[int, ...]]:
    """K-subsets in smallest-differing-element order (Dubov 4.1.3 pattern)."""
    items = sorted(pool)
    # combinations() already yields lexicographic order on sorted input,
    # which matches "smallest differing sequence number" ordering.
    return combinations(items, k)


def board_order(pairs: Sequence[Tuple[P26Player, P26Player]]) -> List[Tuple[int, int]]:
    """C.04.2 Art.3.6 recommended publication sort: higher-ranked score desc,
    pair score-sum desc, smaller TPN of higher-ranked first. Returns id pairs."""
    def higher(pair: Tuple[P26Player, P26Player]) -> P26Player:
        a, b = pair
        if (a.score, -a.tpn) >= (b.score, -b.tpn):
            return a
        return b

    def key(pair: Tuple[P26Player, P26Player]):
        h = higher(pair)
        other = pair[1] if pair[0] is h else pair[0]
        return (-h.score, -(h.score + other.score), h.tpn)

    return [(a.id, b.id) for a, b in sorted(pairs, key=key)]


def exists_complete_pairing(players: Sequence[P26Player],
                            blocked: Sequence[Tuple[int, int]],
                            stepper: Stepper) -> bool:
    """Existence probe: can `players` (even count) be fully paired avoiding
    `blocked` unordered id-pairs? Plain backtracking; budget-guarded."""
    ids = sorted(p.id for p in players)
    if len(ids) % 2:
        return False
    blocked_set = {tuple(sorted(b)) for b in blocked}

    def rec(remaining: Tuple[int, ...]) -> bool:
        stepper.tick()
        if not remaining:
            return True
        first = remaining[0]
        rest = remaining[1:]
        for i, other in enumerate(rest):
            if (first, other) in blocked_set or (other, first) in blocked_set:
                continue
            if rec(rest[:i] + rest[i + 1:]):
                return True
        return False

    return rec(tuple(ids))
