"""Round-robin schedules via Berger tables (Phase 3, standalone module).

Deliberately NOT forced into the Swiss provider abstraction (O-decision:
no inappropriate unification): a round robin is a fixed schedule computed
from pairing numbers, not a searched pairing. No histories, no constraints,
no budgets needed (O(n^2) table construction, instant and total).

Method (FIDE Handbook C.05 Annex 1 construction, as documented in the
retrieved Berger-Explained note whose worked 10-player example reproduces
the Handbook tables exactly):
- Round 1, board b (1-based): pairing number b (white) vs N-b+1 (black).
- Later rounds: sort players 1..N-1 by previous-round board order, white
  before black on each board; player N meets the LAST of the list (removed
  first); N alternates colour; that opponent is white iff their number is
  in 1..B else black. Then repeatedly from the END of the list: white =
  penultimate, black = last, removing both.
- Odd N: add ghost slot N+1 (even); whoever meets the ghost sits out
  (bye, represented as (player, None)). Highest number = bye holder
  consistent with "highest number counts as a bye".
- Double round robin: second cycle swaps colours; optional
  reverse_last_two (FIDE-recommended for >4 players to avoid 3× colour;
  default False — recommendation, not rule).

Maturity: VALIDATED for even N = 4..12 (outputs pinned against retrieved
Handbook rows); GENERATED (same construction) beyond, marked as such.
Odd fields covered structurally (bye rotation, completeness, balance).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from pairing_core.errors import InvalidRequestError

Board = Tuple[int, Optional[int]]  # (white, black or None for bye)


def round_robin(n_players: int, *, double: bool = False,
                reverse_last_two: bool = False,
                ) -> Tuple[Tuple[Board, ...], ...]:
    """PUBLIC. Deterministic Berger schedule for pairing numbers 1..N.

    Returns one tuple per round; each round lists boards in order as
    (white, black) with bye as (player, None). Raises InvalidRequestError
    for n < 2 or non-int input. Pure function: same N -> same schedule.
    """
    if not isinstance(n_players, int) or isinstance(n_players, bool) \
            or n_players < 2:
        raise InvalidRequestError(
            f"round robin needs int n_players >= 2, got {n_players!r}.")
    n_slots = n_players if n_players % 2 == 0 else n_players + 1
    ghost = n_slots if n_players % 2 == 1 else None
    first = _berger_single(n_slots, ghost)
    if not double:
        return first
    second = tuple(
        tuple((b, w) if w is not None and b is not None else (w, b)
              for (w, b) in rnd)
        for rnd in first)
    if reverse_last_two and len(first) > 2 and n_slots != 4:
        first = first[:-2] + first[-2:][::-1]
        second = second[:-2] + second[-2:][::-1]
    return first + second


def _berger_single(n_slots: int, ghost: Optional[int],
                   ) -> Tuple[Tuple[Board, ...], ...]:
    boards = _round_one(n_slots)
    rounds = [_boards_to_public(boards, ghost)]
    count = n_slots - 1
    for _ in range(1, count):
        boards = _next_round(boards, n_slots)
        rounds.append(_boards_to_public(boards, ghost))
    return tuple(rounds)


def _round_one(n_slots: int) -> List[Tuple[int, int]]:
    half = n_slots // 2
    return [(m, n_slots - m + 1) for m in range(1, half + 1)]


def _next_round(prev: List[Tuple[int, int]], n_slots: int) -> List[Tuple[int, int]]:
    # Players 1..N-1 in previous board order, white before black on each
    # board; N meets the LAST of that list (N itself excluded from it).
    ordered: List[int] = []
    for (white, black) in prev:
        if white != n_slots:
            ordered.append(white)
        if black != n_slots:
            ordered.append(black)
    tail = ordered[-1]
    rest = ordered[:-1]
    # Partner white iff their number is in 1..half, else black
    # (N takes the other colour; alternation follows — asserted in tests).
    pair_n = (tail, n_slots) if tail <= n_slots // 2 else (n_slots, tail)
    boards = [pair_n]
    # From the end: white = penultimate, black = last.
    while rest:
        black = rest.pop()
        white = rest.pop()
        boards.append((white, black))
    return boards


def _boards_to_public(boards: List[Tuple[int, int]],
                      ghost: Optional[int]) -> Tuple[Board, ...]:
    out = []
    for (white, black) in boards:
        if ghost is not None and (white == ghost or black == ghost):
            holder = black if white == ghost else white
            out.append((holder, None))
        else:
            out.append((white, black))
    return tuple(out)
