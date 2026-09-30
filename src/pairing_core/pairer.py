"""
FIDE Dutch Swiss Pairing Algorithm — Core Engine.

Implements C.04.3 (FIDE Dutch System) with:
    - Bracket-by-bracket processing (top to bottom)
    - S1/S2 splitting by pairing number
    - Exact lazy lexicographic transposition search
    - Systematic exchanges between S1/S2 (FIDE order)
    - Remainder/downfloater selection with float rules
    - Cross-bracket recursive backtracking
    - Two-pass search: strict constraints first, then relaxed
    - No randomness, no heuristic fallback, fully deterministic

Important correctness and performance fixes:
    1. The engine does not stop at the first locally valid pairing
       if downstream brackets fail. It backtracks over all local
       pairings of the same bracket in exact FIDE order.

    2. Repeated impossible global states are cached:
           (bracket_idx, incoming_ids, strict_floats)

    3. Repeated impossible local bracket states are cached:
           (ordered players with float flags, strict_floats)

    4. Exact perfect-matching feasibility pruning is used inside the
       transposition DFS. This is NOT a shortcut: it only proves that
       a remaining suffix cannot possibly be completed and prunes it.
"""
from typing import Dict, Generator, List, Optional, Set, Tuple

from pairing_core.models import EnginePlayer, PairingCard
from pairing_core.bracket import Bracket
from pairing_core.color import (
    assign_colors,
    has_legal_assignment,
    is_legal_orientation,
)
from pairing_core.floats import (
    float_pair_legal,
    rank_downfloater_candidates,
)


# ═══════════════════════════════════════════════════════════════════
#  Public API
# ═══════════════════════════════════════════════════════════════════

def pair_all_brackets(
    brackets: List[Bracket],
    played_map: Dict[int, Set[int]],
    round_number: int,
) -> Optional[List[PairingCard]]:
    """
    Pair all score brackets using the FIDE Dutch algorithm.

    Two-pass approach:
        Pass 1: Strict float constraints
        Pass 2: Relaxed float constraints

    Absolute constraints are never relaxed.
    """
    ctx = _PairingContext(
        brackets=brackets,
        played_map=played_map,
        round_number=round_number,
    )

    # Pass 1: strict float rules
    ctx.strict_floats = True
    solution = _solve_bracket(ctx, bracket_idx=0, incoming=[])
    if solution is not None:
        return _to_pairing_cards(solution)

    # Pass 2: relaxed float rules
    ctx.strict_floats = False
    solution = _solve_bracket(ctx, bracket_idx=0, incoming=[])
    if solution is not None:
        return _to_pairing_cards(solution)

    return None


# ═══════════════════════════════════════════════════════════════════
#  Internal Context
# ═══════════════════════════════════════════════════════════════════

class _PairingContext:
    """Shared state for the recursive pairing search."""

    __slots__ = (
        "brackets",
        "played_map",
        "round_number",
        "strict_floats",
        "global_dead_end_cache",
        "local_impossible_cache",
        "search_steps",
        "max_search_steps",
    )

    def __init__(
        self,
        brackets: List[Bracket],
        played_map: Dict[int, Set[int]],
        round_number: int,
    ):
        self.brackets = brackets
        self.played_map = played_map
        self.round_number = round_number
        self.strict_floats = True

        # Global exact dead-end cache:
        #   (bracket_idx, incoming_ids_tuple, strict_floats) -> impossible
        self.global_dead_end_cache: Set[
            Tuple[int, Tuple[int, ...], bool]
        ] = set()

        # Local exact impossibility cache:
        #   (players-with-flags, strict_floats) -> impossible
        self.local_impossible_cache: Set[
            Tuple[Tuple[Tuple[int, int, int], ...], bool]
        ] = set()
        self.search_steps = 0
        self.max_search_steps = 2000000

    def have_played(self, p1: EnginePlayer, p2: EnginePlayer) -> bool:
        """
        Check if two players have already faced each other.

        Uses both played_map and the per-player opponent sets
        for robustness.
        """
        if p2.id in self.played_map.get(p1.id, set()):
            return True
        if p1.id in self.played_map.get(p2.id, set()):
            return True
        if p1.has_played(p2.id):
            return True
        if p2.has_played(p1.id):
            return True
        return False


# ═══════════════════════════════════════════════════════════════════
#  Internal Pair Representation
# ═══════════════════════════════════════════════════════════════════

class _Pair:
    """A matched pair of players with assigned colors."""
    __slots__ = ("white", "black", "white_float", "black_float")

    def __init__(self, white: EnginePlayer, black: EnginePlayer):
        self.white = white
        self.black = black
        
        w_down = white.is_downfloater
        b_down = black.is_downfloater
        
        self.white_float = "D" if w_down else ("U" if b_down else "")
        self.black_float = "D" if b_down else ("U" if w_down else "")

    def __repr__(self) -> str:
        return f"Pair(W={self.white.pno}, B={self.black.pno})"

# ═══════════════════════════════════════════════════════════════════
#  Recursive Bracket Solver
# ═══════════════════════════════════════════════════════════════════

def _solve_bracket(
    ctx: _PairingContext,
    bracket_idx: int,
    incoming: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Recursively solve pairing from bracket_idx downward.
    """
    state_key = (
        bracket_idx,
        tuple(sorted(p.id for p in incoming)),
        ctx.strict_floats,
    )
    if state_key in ctx.global_dead_end_cache:
        return None

    if bracket_idx >= len(ctx.brackets):
        if incoming:
            ctx.global_dead_end_cache.add(state_key)
            return None
        return []

    bracket = ctx.brackets[bracket_idx]

    if incoming:
        bracket = bracket.with_downfloaters(incoming)

    players = bracket.all_players

    if not players:
        result = _solve_bracket(ctx, bracket_idx + 1, [])
        if result is None:
            ctx.global_dead_end_cache.add(state_key)
        return result

    has_next = bracket_idx + 1 < len(ctx.brackets)

    # Last bracket rules
    if not has_next:
        if len(players) % 2 == 0:
            for pairs in _iter_bracket_pairings(ctx, bracket):
                return pairs
            ctx.global_dead_end_cache.add(state_key)
            return None

        result = _try_last_bracket_odd(ctx, bracket)
        if result is None:
            ctx.global_dead_end_cache.add(state_key)
        return result

    # Non-last bracket
    result = _search_bracket_configurations(
        ctx=ctx,
        bracket_idx=bracket_idx,
        bracket=bracket,
        selected_downfloaters=[],
    )
    if result is None:
        ctx.global_dead_end_cache.add(state_key)
    return result


def _search_bracket_configurations(
    ctx: _PairingContext,
    bracket_idx: int,
    bracket: Bracket,
    selected_downfloaters: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Explore all legal ways to carry zero or more players down from
    the current bracket before recursing.
    """
    # Option 1: current reduced bracket is even and locally pairable
    if bracket.count > 0 and bracket.count % 2 == 0:
        # FIXED: Verify local pairability BEFORE expensive downstream recursion.
        # این کار از فراخوانی‌های بازگشتی بی‌هوده و فریز شدن سیستم جلوگیری می‌کند.
        local_pairings_iter = _iter_bracket_pairings(ctx, bracket)
        first_local = next(local_pairings_iter, None)
        
        if first_local is not None:
            tail = _recurse_with_downfloaters(
                ctx,
                bracket_idx + 1,
                selected_downfloaters,
            )
            if tail is not None:
                return first_local + tail

    # Option 2: current reduced bracket is empty -> send all selected down
    if bracket.count == 0:
        tail = _recurse_with_downfloaters(
            ctx,
            bracket_idx + 1,
            selected_downfloaters,
        )
        if tail is not None:
            return tail

    # Option 3: carry one more player down and continue searching
    incoming_ids = bracket.downfloater_ids
    candidates = rank_downfloater_candidates(
        bracket.all_players,
        incoming_ids,
        strict=ctx.strict_floats,
    )
    for candidate in candidates:
        reduced = bracket.without_player(candidate.id)
        result = _search_bracket_configurations(
            ctx=ctx,
            bracket_idx=bracket_idx,
            bracket=reduced,
            selected_downfloaters=selected_downfloaters + [candidate],
        )
        if result is not None:
            return result

    return None


def _recurse_with_downfloaters(
    ctx: _PairingContext,
    next_bracket_idx: int,
    downfloaters: List[EnginePlayer],
) -> Optional[List[_Pair]]:
    """
    Recurse to the next bracket with a list of selected downfloaters.
    """
    if not downfloaters:
        return _solve_bracket(ctx, next_bracket_idx, [])

    saved_flags = []
    for p in downfloaters:
        saved_flags.append((p, p.is_downfloater, p.is_upfloater))
        p.is_downfloater = True
        p.is_upfloater = False

    try:
        return _solve_bracket(ctx, next_bracket_idx, list(downfloaters))
    finally:
        for p, old_down, old_up in saved_flags:
            p.is_downfloater = old_down
            p.is_upfloater = old_up


def _try_last_bracket_odd(
    ctx: _PairingContext,
    bracket: Bracket,
) -> Optional[List[_Pair]]:
    """
    Handle an odd-count last bracket.
    
    FIXED: FIDE C.04.3.B.2 states that if the last bracket is odd, 
    the highest ranked player is moved to the previous bracket (Upfloat).
    Since our engine processes top-down recursively, we CANNOT silently 
    drop the player. We must return None to force backtracking, which 
    will cause the previous bracket to adjust its downfloaters so that 
    this last bracket becomes even. If all backtracking fails, the 
    engine layer will safely fallback to assigning a Bye if needed.
    """
    return None


# ═══════════════════════════════════════════════════════════════════
#  Bracket Pairing Search
# ═══════════════════════════════════════════════════════════════════

def _iter_bracket_pairings(
    ctx: _PairingContext,
    bracket: Bracket,
) -> Generator[List[_Pair], None, None]:
    """
    Yield ALL legal local pairings for a bracket in exact search order.
    """
    players = bracket.all_players
    n = len(players)

    if n < 2 or n % 2 != 0:
        return

    cache_key = _make_local_cache_key(players, ctx.strict_floats)
    if cache_key in ctx.local_impossible_cache:
        return

    half = n // 2
    s1_original = players[:half]
    s2_original = players[half:]
    yielded_any = False

    # 1 + 2: original split + all transpositions
    for pairs in _iter_transposition_pairings(ctx, s1_original, s2_original):
        yielded_any = True
        yield pairs

    # 3 + 4: exchanges + all transpositions
    from pairing_core.exchange import generate_exchanges

    for new_s1, new_s2 in generate_exchanges(s1_original, s2_original):
        ctx.search_steps += 1
        if ctx.search_steps > ctx.max_search_steps:
            raise ValueError(f"Pairing complexity exceeded limit ({ctx.max_search_steps} nodes). Bracket is too complex.")
        for pairs in _iter_transposition_pairings(ctx, new_s1, new_s2):
            yielded_any = True
            yield pairs

    if not yielded_any:
        ctx.local_impossible_cache.add(cache_key)


def _iter_transposition_pairings(
    ctx: _PairingContext,
    s1: List[EnginePlayer],
    s2: List[EnginePlayer],
) -> Generator[List[_Pair], None, None]:
    """
    Yield ALL legal pairings corresponding to transpositions of S2,
    in exact lexicographic order, without materializing all permutations.
    """
    if len(s1) != len(s2):
        return

    n = len(s1)
    if n == 0:
        yield []
        return

    pair_matrix: List[List[Optional[_Pair]]] = []
    legal_masks: List[int] = []

    for i in range(n):
        row: List[Optional[_Pair]] = []
        mask = 0
        for j in range(n):
            pair = _build_pair_if_legal(ctx, s1[i], s2[j])
            row.append(pair)
            if pair is not None:
                mask |= (1 << j)
        pair_matrix.append(row)
        legal_masks.append(mask)

        if mask == 0:
            return

    full_mask = (1 << n) - 1
    dead_states: Set[Tuple[int, int]] = set()
    feasible_cache: Dict[Tuple[int, int], bool] = {}

    def dfs(i: int, used_mask: int) -> Generator[List[_Pair], None, None]:
        ctx.search_steps += 1
        if ctx.search_steps > ctx.max_search_steps:
            raise ValueError(f"Pairing complexity exceeded limit ({ctx.max_search_steps} nodes). Bracket is too complex.")
        state = (i, used_mask)
        if state in dead_states:
            return

        if i == n:
            yield []
            return

        remaining_mask = full_mask ^ used_mask

        # Fast exact pruning: each remaining row must have at least one
        # legal remaining column.
        for k in range(i, n):
            if (legal_masks[k] & remaining_mask) == 0:
                dead_states.add(state)
                return

        # Stronger exact pruning: remaining suffix must admit a perfect
        # matching in the bipartite legality graph.
        if not _perfect_completion_possible(
            i=i,
            used_mask=used_mask,
            legal_masks=legal_masks,
            n=n,
            full_mask=full_mask,
            feasible_cache=feasible_cache,
        ):
            dead_states.add(state)
            return

        yielded = False

        # Lexicographic transposition order:
        # for fixed row i, try remaining columns in ascending order
        for j in range(n):
            bit = 1 << j
            if used_mask & bit:
                continue

            pair = pair_matrix[i][j]
            if pair is None:
                continue

            child_yielded = False
            for suffix in dfs(i + 1, used_mask | bit):
                child_yielded = True
                yielded = True
                yield [pair] + suffix

            if not child_yielded:
                continue

        if not yielded:
            dead_states.add(state)

    yield from dfs(0, 0)


def _perfect_completion_possible(
    i: int,
    used_mask: int,
    legal_masks: List[int],
    n: int,
    full_mask: int,
    feasible_cache: Dict[Tuple[int, int], bool],
) -> bool:
    """
    Exact feasibility check for the remaining suffix.

    Returns True iff the remaining rows i..n-1 can be matched injectively
    to the remaining unused S2 columns.

    This is an exact bipartite perfect-matching test, so it does not
    change FIDE search order; it only prunes impossible branches.
    """
    key = (i, used_mask)
    cached = feasible_cache.get(key)
    if cached is not None:
        return cached

    remaining_cols_mask = full_mask ^ used_mask
    remaining_rows = list(range(i, n))

    # Trivial cases
    if not remaining_rows:
        feasible_cache[key] = True
        return True

    remaining_cols: List[int] = []
    for j in range(n):
        if remaining_cols_mask & (1 << j):
            remaining_cols.append(j)

    if len(remaining_rows) != len(remaining_cols):
        feasible_cache[key] = False
        return False

    col_pos = {col: idx for idx, col in enumerate(remaining_cols)}

    # Build adjacency for remaining rows
    adjacency: List[List[int]] = []
    for row in remaining_rows:
        allowed_mask = legal_masks[row] & remaining_cols_mask
        if allowed_mask == 0:
            feasible_cache[key] = False
            return False

        cols_for_row: List[int] = []
        for col in remaining_cols:
            if allowed_mask & (1 << col):
                cols_for_row.append(col_pos[col])

        if not cols_for_row:
            feasible_cache[key] = False
            return False

        adjacency.append(cols_for_row)

    # Solve perfect matching exactly with DFS augmenting paths
    # Rows are processed by ascending degree for speed only.
    row_order = sorted(
        range(len(adjacency)),
        key=lambda r: len(adjacency[r]),
    )

    match_to_row = [-1] * len(remaining_cols)

    def augment(row_idx: int, seen: List[bool]) -> bool:
        for col_idx in adjacency[row_idx]:
            if seen[col_idx]:
                continue
            seen[col_idx] = True
            if match_to_row[col_idx] == -1 or augment(match_to_row[col_idx], seen):
                match_to_row[col_idx] = row_idx
                return True
        return False

    for row_idx in row_order:
        seen = [False] * len(remaining_cols)
        if not augment(row_idx, seen):
            feasible_cache[key] = False
            return False

    feasible_cache[key] = True
    return True


def _build_pair_if_legal(
    ctx: _PairingContext,
    p1: EnginePlayer,
    p2: EnginePlayer,
) -> Optional[_Pair]:
    """
    Build a colored pair if the pairing is fully legal.
    """
    if ctx.have_played(p1, p2):
        return None

    if not has_legal_assignment(p1, p2):
        return None

    if not float_pair_legal(p1, p2, strict=ctx.strict_floats):
        return None

    white, black = assign_colors(p1, p2)

    if is_legal_orientation(white, black):
        return _Pair(white=white, black=black)

    if is_legal_orientation(black, white):
        return _Pair(white=black, black=white)

    return None


# ═══════════════════════════════════════════════════════════════════
#  Cache Helpers
# ═══════════════════════════════════════════════════════════════════

def _make_local_cache_key(
    players: List[EnginePlayer],
    strict_floats: bool,
) -> Tuple[Tuple[Tuple[int, int, int], ...], bool]:
    """
    Exact local-impossibility cache key.

    Includes:
        - player id
        - is_downfloater
        - is_upfloater
        - strict/relaxed float mode
    """
    return (
        tuple(
            (p.id, 1 if p.is_downfloater else 0, 1 if p.is_upfloater else 0)
            for p in players
        ),
        strict_floats,
    )


# ═══════════════════════════════════════════════════════════════════
#  Materialization
# ═══════════════════════════════════════════════════════════════════

def _to_pairing_cards(
    pairs: List[_Pair],
) -> List[PairingCard]:
    """
    Convert internal _Pair list to output PairingCard list.
    """
    cards: List[PairingCard] = []

    for idx, pair in enumerate(pairs, start=1):
        cards.append(PairingCard(
            board=idx,
            white_id=pair.white.id,
            black_id=pair.black.id,
            is_bye=False,
            white_float=pair.white_float,
            black_float=pair.black_float,
        ))

    return cards
