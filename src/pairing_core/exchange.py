"""
Systematic exchange generator — FIDE C.04.3.

This module generates all legal exchange patterns between S1 and S2
in the exact order required by the FIDE Dutch system.

FIDE C.04.3 Exchange Rules:
    1. An exchange is a swap of one or more players between S1 and S2.
       After an exchange, S1 and S2 are re-sorted by pairing number.

    2. Exchanges are tried AFTER all transpositions of the original S2
       have been exhausted.

    3. Exchange order (FIDE convention):
        a) Single exchanges first:
           - Start with swapping the LOWEST-RANKED player in S1
             (highest pairing number) with the HIGHEST-RANKED
             player in S2 (lowest pairing number).
           - Then try the same lowest-ranked S1 with the next
             highest-ranked S2, and so on.
           - Then move to the next lowest-ranked S1 and repeat.
        b) Double exchanges next:
           - Swap two players from S1 with two from S2.
           - Ordered similarly: start with lowest two S1 and
             highest two S2, then permutations.
        c) Continue with triple, quadruple, etc. up to min(|S1|, |S2|)

    4. After each exchange, the new S1 and S2 are re-sorted by pairing
       number, and then all transpositions of the new S2 are tried.

    5. The exchange process continues until a legal pairing is found
       or all possibilities are exhausted.

Example with S1 = [pno=1, pno=3, pno=5], S2 = [pno=7, pno=9, pno=11]:

    Single exchanges (order):
        (S1[2]=5 ↔ S2[0]=7)  → new S1=[1,3,7], S2=[5,9,11]
        (S1[2]=5 ↔ S2[1]=9)  → new S1=[1,3,9], S2=[5,7,11]
        (S1[2]=5 ↔ S2[2]=11) → new S1=[1,3,11], S2=[5,7,9]
        (S1[1]=3 ↔ S2[0]=7)  → new S1=[1,5,7], S2=[3,9,11]
        (S1[1]=3 ↔ S2[1]=9)  → new S1=[1,5,9], S2=[3,7,11]
        ... and so on

Performance note:
    For S1 of size n and S2 of size m:
        Single exchanges:    n * m
        Double exchanges:    C(n,2) * C(m,2)
        Triple exchanges:    C(n,3) * C(m,3)
        ...

    For n=m=10:
        Single:     100
        Double:     45 * 45 = 2,025
        Triple:     120 * 120 = 14,400
        Total:     ~16,525 exchange patterns

    The engine splits brackets so S1/S2 never grow that large.

This module is stateless and deterministic. Zero external dependencies.
"""
from itertools import combinations
from typing import Generator, List, Tuple

from pairing_core.models import EnginePlayer


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def generate_exchanges(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    max_exchange_size: int = None,
) -> Generator[Tuple[List[EnginePlayer], List[EnginePlayer]], None, None]:
    """
    Generate all exchange patterns between S1 and S2 in FIDE order.

    Each exchange pattern yields a new (S1_new, S2_new) pair where:
        - Some players have been swapped between S1 and S2
        - Both halves have been re-sorted by pairing number
        - The yield order follows FIDE convention exactly

    Args:
        s1: The original S1 half, sorted by pairing number (ascending).
        s2: The original S2 half, sorted by pairing number (ascending).
        max_exchange_size: Maximum number of players to swap at once.
                         If None, uses min(len(s1), len(s2)).

    Yields:
        (new_s1, new_s2) tuples after each exchange.

    Note:
        The identity (no exchange) is NOT yielded. The caller should
        try the original S1/S2 before calling this generator.
    """
    n = len(s1)
    m = len(s2)

    if max_exchange_size is None:
        max_exchange_size = min(n, m)

    # Generate exchanges in order: single, double, triple, ...
    for k in range(1, max_exchange_size + 1):
        yield from _generate_k_exchanges(s1, s2, k)

    return


# ═══════════════════════════════════════════════════════════════════
#  Exchange Generation
# ═══════════════════════════════════════════════════════════════════

def _generate_k_exchanges(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    k: int,
) -> Generator[Tuple[List[EnginePlayer], List[EnginePlayer]], None, None]:
    """
    Generate all k-size exchange patterns in FIDE order.

    FIDE order for k-size exchanges:
        1. Generate all combinations of k players from S1 (lowest-ranked first)
        2. Generate all combinations of k players from S2 (highest-ranked first)
        3. For each S1 combination (from lowest to highest ranked):
             a. For each S2 combination (from highest to lowest ranked):
                  - Swap the two groups
                  - Re-sort both halves
                  - Yield the result

    This ensures that we try the "least disruptive" exchanges first.

    Args:
        s1: Original S1 half.
        s2: Original S2 half.
        k: Number of players to exchange.

    Yields:
        (new_s1, new_s2) after each k-size exchange.
    """
    n = len(s1)
    m = len(s2)

    if k == 0:
        yield list(s1), list(s2)
        return

    if k > n or k > m:
        return

    # Generate S1 combinations: lowest-ranked first
    # S1 is sorted ascending (pno 1, 3, 5, ...)
    # Lowest-ranked in S1 = highest pno = last in list.
    # LAZY: never materialize combination lists (C(n,k) explodes for large
    # brackets and defeated the search step budget with unbounded memory
    # growth). The inner S2 combinations are re-generated per S1 group in
    # the same order as before.
    s1_combinations = _reverse_combinations(s1, k)

    # Yield in FIDE order: for each S1 combo, all S2 combos
    for s1_group in s1_combinations:
        # Generate S2 combinations: highest-ranked first
        # S2 is sorted ascending (pno 7, 9, 11, ...)
        # Highest-ranked in S2 = lowest pno = first in list
        for s2_group in combinations(s2, k):
            new_s1, new_s2 = _swap_groups(s1, s2, s1_group, s2_group)
            yield new_s1, new_s2


def _reverse_combinations(
    items: List[EnginePlayer],
    r: int,
) -> Generator[Tuple[EnginePlayer, ...], None, None]:
    """
    Generate combinations in REVERSE order (lowest-ranked players first).
    
    FIDE C.04.3 Exchange order:
        Start with swapping the lowest-ranked player in S1 
        (highest pairing number = highest index in list).
    """
    n = len(items)
    if r > n:
        return

    # FIXED: Generate combinations of indices in reverse order
    # by using a descending range. This naturally yields highest
    # indices (lowest-ranked players) first.
    # Example for n=4, r=2: (3,2), (3,1), (3,0), (2,1), (2,0), (1,0)
    for combo in combinations(range(n - 1, -1, -1), r):
        yield tuple(items[i] for i in combo)

def _swap_groups(
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
    s1_group: Tuple[EnginePlayer, ...],
    s2_group: Tuple[EnginePlayer, ...],
) -> Tuple[List[EnginePlayer], List[EnginePlayer]]:
    """
    Swap two groups of players between S1 and S2.

    Args:
        s1: Original S1 half.
        s2: Original S2 half.
        s1_group: Players to move from S1 to S2.
        s2_group: Players to move from S2 to S1.

    Returns:
        (new_s1, new_s2) with groups swapped and both halves re-sorted.
    """
    new_s1 = [p for p in s1 if p not in s1_group] + list(s2_group)
    new_s2 = [p for p in s2 if p not in s2_group] + list(s1_group)

    # Re-sort by pairing number
    new_s1.sort(key=lambda p: p.pno)
    new_s2.sort(key=lambda p: p.pno)

    return new_s1, new_s2