"""Dutch System 2026 engine (C.04.3, F-0105, FULL_TEXT).

Full C1–C21 criteria-vector search with the specified sequential generation
(Art.4: BSNs, lexicographic S2 transpositions, resident-exchange comparison
rules, pairable-MDP sets, next-element) and Art.5 colour allocation.

Structure per bracket (Art.3):
- homogeneous: for each S1 composition (original, then resident exchanges in
  4.3 order, S1/S2 re-sorted per 1.2): for each S2 transposition in 4.2 order:
  build candidate (pairs + downfloaters), evaluate; perfect (3.4.1) accepted
  immediately; else track best per 3.8.1 (higher-priority criterion first,
  ties -> earlier generation).
- heterogeneous: 3.7.1 remainder moves first (S1R/S2R frozen post-MDP-pairing),
  then 3.7.2 new S2 transposition -> new MDP-pairing + remainder, then 3.7.3
  next pairable-MDP set from Limbo with S2 restored.
- C8 look-ahead: exactly one bracket deep (computed via restricted C1–C7
  optimisation of the next bracket, no deeper recursion).
- PAB: no separate formula exists in C.04.3 (unlike Double/Team 3.4); the bye
  emerges from last-bracket pairing via C5 (minimise assignee score) + C9
  (minimise assignee unplayed) + C2. The last bracket enumerates leave-one-
  unpaired (PAB) options for C2-eligible players alongside full pairing.
- Budgets: Stepper guards every enumeration; exhaustion -> EngineTimeoutError.

Documented approximation: C8 evaluates the next bracket's optimal (C6, C7)
over the same candidate machinery restricted to C1–C7 (colours excluded);
deeper chains are not searched (matches "just in the following bracket").
"""

from __future__ import annotations

from itertools import combinations, permutations
from typing import Dict, List, Optional, Sequence, Set, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import ImpossiblePairingError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper, exists_complete_pairing
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


# ================================================================ colours

def allocate_colour(a: P26Player, b: P26Player, *,
                    initial_colour: str) -> Tuple[int, int]:
    """Art.5 colour allocation. Higher-ranked (1.2) = higher score else
    smaller TPN. Returns (white_id, black_id)."""
    hi, lo = (a, b) if (a.score, -a.tpn) >= (b.score, -b.tpn) else (b, a)
    pa, pb = C.preference(hi), C.preference(lo)
    if pa[0] is not None and pb[0] is not None and pa[0] != pb[0]:
        # 5.2.1 grant both (possible exactly when preferences differ)
        w = hi.id if pa[0] == "W" else lo.id
        return (w, lo.id if w == hi.id else hi.id)
    if pa[1] > pb[1] and pa[0] is not None:  # 5.2.2 stronger
        return (hi.id, lo.id) if pa[0] == "W" else (lo.id, hi.id)
    if pb[1] > pa[1] and pb[0] is not None:
        return (lo.id, hi.id) if pb[0] == "W" else (hi.id, lo.id)
    if pa[1] == 3 and pb[1] == 3 and pa[0] is not None and pa[0] == pb[0]:
        # both absolute, same side: topscorer rule widens the difference.
        # (Non-topscorer same-absolute pairs are barred by C3; topscorers
        # may be forced together — wider CD granted.)
        cda, cdb = C.colour_difference(hi), C.colour_difference(lo)
        if pa[0] == "W":
            w = hi.id if cda <= cdb else lo.id
        else:
            w = lo.id if cda <= cdb else hi.id
        return (w, lo.id if w == hi.id else hi.id)
    alt = _alternate_from_encounter(hi, lo)  # 5.2.3
    if alt is not None:
        return alt
    if pa[0] is not None:  # 5.2.4 higher-ranked preference
        return (hi.id, lo.id) if pa[0] == "W" else (lo.id, hi.id)
    # 5.2.5 odd-TPN higher-ranked gets initial-colour, else opposite.
    hi_white = (hi.tpn % 2 == 1) == (initial_colour == "W")
    return (hi.id, lo.id) if hi_white else (lo.id, hi.id)


def _alternate_from_encounter(a: P26Player, b: P26Player):
    """5.2.3: most recent round where one had White and the other Black
    (played-only per C.04.2 Art.3.4) -> swap those colours."""
    sa = [(i, c) for i, c in enumerate(a.colors) if c in ("W", "B")]
    sb = {i: c for i, c in enumerate(b.colors) if c in ("W", "B")}
    for i, ca in reversed(sa):
        cb = sb.get(i)
        if cb is not None and cb != ca:
            # a had ca, b had cb: alternate -> a gets cb, b gets ca.
            w = a.id if cb == "W" else b.id
            return (w, b.id if w == a.id else a.id)
    return None


# ============================================================ generation

def _bsn(players: Sequence[P26Player]) -> Dict[int, int]:
    """Art.4.1.1: BSNs 1,2,3... in Article 1.2 ranking order (score desc,
    TPN asc) before any shuffle. (Ascending-score tagging inverts every
    heterogeneous-bracket BSN and corrupts 4.2/4.3/4.4 orderings.)"""
    order = sorted(players, key=lambda p: (-p.score, p.tpn))
    return {p.id: i + 1 for i, p in enumerate(order)}


def _s2_transpositions(s2: List[P26Player], n1: int, bsn: Dict[int, int],
                       stepper=None):
    """Art.4.2: S2 orders sorted lexicographically by first N1 BSNs
    (trailing downfloater/remainder BSNs ignored). Lazy generator.
    Factorial-scale: ticks per permutation (typed timeout, never hang)."""
    ids = [p.id for p in s2]
    seen = set()
    for perm in permutations(ids):
        if stepper is not None:
            stepper.tick()
        key = tuple(bsn[i] for i in perm[:n1])
        if key in seen:
            continue
        seen.add(key)
        yield [next(p for p in s2 if p.id == i) for i in perm]


def _resident_exchanges(s1: List[P26Player], s2: List[P26Player],
                         bsn: Dict[int, int], stepper) -> object:
    """Art.4.3: equal-size original-S1<->S2 BSN swaps in comparison-rule
    order: (1) fewest moved; (2) smallest |sum-in - sum-out|; (3) largest
    differing BSN leaving S1; (4) smallest differing BSN entering S1.
    Lazy: the original composition is always generated first by the caller;
    this order is computed only when alterations are actually needed, and
    pre-guarded by count (factorial-scale sets raise typed timeouts)."""
    from math import comb as _comb
    b1 = sorted(bsn[p.id] for p in s1)
    b2 = sorted(bsn[p.id] for p in s2)
    total = sum(_comb(len(b1), k) * _comb(len(b2), k)
                for k in range(1, min(len(b1), len(b2)) + 1))
    stepper.check_count(total, "resident exchanges")
    cands = []
    for k in range(1, min(len(b1), len(b2)) + 1):
        for out in combinations(b1, k):
            for inn in combinations(b2, k):
                stepper.tick()
                set_out, set_in = set(out), set(inn)
                diff_out = sorted(set_out - set_in, reverse=True)
                diff_in = sorted(set_in - set_out)
                key = (k, abs(sum(set_in) - sum(set_out)),
                       tuple(-x for x in diff_out),
                       tuple(diff_in), tuple(sorted(set_out)),
                       tuple(sorted(set_in)))
                cands.append((key, set_out, set_in))
    cands.sort(key=lambda c: c[0])
    for _, set_out, set_in in cands:
        new_s1_bsns = (set(b1) - set_out) | set_in
        new_s2_bsns = (set(b2) - set_in) | set_out
        yield new_s1_bsns, new_s2_bsns


def _mdp_sets(m0: List[P26Player], max_m1: int, bsn: Dict[int, int],
               stepper=None):
    """Art.4.4.2: larger kept-sets first (annotated: "the larger is the number
    of MDPs in the set, the better is the set"); within a size, kept sets in
    smallest-differing-BSN order (annotated worked example {1,3} < {1,4} <
    {3,4}: compare first BSNs, then second). Yields frozensets of kept
    (paired) MDP ids. (Complement-lexicographic order is NOT equivalent:
    it yields {3,4} first in the example.)"""
    from itertools import combinations as _cb
    if stepper is not None:
        stepper.check_count(2 ** len(m0), "pairable MDP sets")
    order = sorted((p.id for p in m0), key=lambda i: bsn[i])
    all_sets = []
    for k in range(min(max_m1, len(order)), -1, -1):
        for combo in _cb(order, k):
            if stepper is not None:
                stepper.tick()
            kept_bsns = tuple(sorted(bsn[i] for i in combo))
            all_sets.append(((-k, kept_bsns), combo))
    all_sets.sort(key=lambda s: s[0])
    for _, s in all_sets:
        yield frozenset(s)


# ============================================================= evaluation

class _Ctx:
    def __init__(self, req: P26Request, by_id: Dict[int, P26Player],
                 blocked, stepper: Stepper, topscorers: Set[int]):
        self.req = req
        self.by_id = by_id
        self.blocked = blocked
        self.stepper = stepper
        self.topscorers = topscorers


def _abs_ok(pairs: Sequence[Tuple[int, int]], ctx: _Ctx,
            extra_bye: Optional[int] = None) -> bool:
    """C1–C3 (+C2 for the bye taker)."""
    for xa, xb in pairs:
        a, b = ctx.by_id[xa], ctx.by_id[xb]
        if C.rematch(a, b):
            return False
        pa, pb = C.preference(a), C.preference(b)
        if pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0]:
            # C3: same-absolute non-topscorers shall not meet.
            if not (a.id in ctx.topscorers or b.id in ctx.topscorers):
                return False
    if extra_bye is not None:
        p = ctx.by_id[extra_bye]
        if not C.pab_eligible(p):
            return False
    return True


def _rest_pairable(paired_ids: Set[int], all_ids: Set[int],
                   ctx: _Ctx) -> bool:
    """C4: an absolute-compliant continuation exists for the not-yet-paired
    (C1–C3 backtracking existence probe; PAB slot reserved if odd)."""
    rest = [ctx.by_id[i] for i in all_ids - paired_ids]
    if len(rest) % 2:
        # one may take the PAB below: existence needs an eligible taker whose
        # removal leaves an even pairable rest.
        found = False
        for cand in sorted(rest, key=lambda p: (p.score, p.tpn)):
            if not C.pab_eligible(cand):
                continue
            sub = [p for p in rest if p.id != cand.id]
            if _even_pairable(sub, ctx):
                found = True
                break
        return found
    return _even_pairable(rest, ctx)


def _even_pairable(players: Sequence[P26Player], ctx: _Ctx) -> bool:
    ids = tuple(sorted(p.id for p in players))
    bset = ctx.blocked

    def bt(rem):
        ctx.stepper.tick()
        if not rem:
            return True
        f = rem[0]
        for i, o in enumerate(rem[1:]):
            if (f, o) in bset or (o, f) in bset:
                continue
            a, b = ctx.by_id[f], ctx.by_id[o]
            pa, pb = C.preference(a), C.preference(b)
            if pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0]:
                if not (f in ctx.topscorers or o in ctx.topscorers):
                    continue
            if bt(rem[1:i + 1] + rem[i + 2:]):
                return True
        return False

    return bt(ids)


def _c8_next_vector(downfloater_ids: Sequence[int],
                    next_residents: Sequence[P26Player], ctx: _Ctx,
                    paired_after: Set[int], all_ids: Set[int]):
    """C8: optimal (C6 count, C7 scores-desc) achievable in the next bracket
    (residents + these downfloaters as MDPs), restricted to C1–C7 (colours
    excluded), with C4 continuation probe. Heterogeneous machinery when the
    next bracket has MDPs (MDPs pair with residents only — a homogeneous
    probe would over-pair via MDP-MDP pairs and understate C6)."""
    mdps = [ctx.by_id[i] for i in downfloater_ids]
    residents = list(next_residents)
    if not residents and not mdps:
        return (0, ())
    iters = (_iter_heterogeneous(residents, mdps, ctx) if mdps
             else _iter_homogeneous(residents, ctx))
    best = None
    for cand_pairs, cand_down, _ in iters:
        if not _abs_ok(cand_pairs, ctx):
            continue
        if not _rest_pairable(paired_after | {i for pr in cand_pairs
                                              for i in pr},
                              all_ids, ctx):
            continue  # C4 within C1–C7 compliance
        c6 = len(cand_down)
        c7 = tuple(sorted((ctx.by_id[i].score for i in cand_down),
                          reverse=True))
        key = (c6, c7)
        if best is None or key < best:
            best = key
            if best == (0, ()):
                break  # global minimum: no downfloaters (exact short-cut)
    if best is None:
        return (10 ** 9, ())
    return best


def _vector(pairs: Sequence[Tuple[int, int]], down: Sequence[int],
            mdp_pairs: Sequence[Tuple[int, int]],
            mdp_ids: Set[int], bye: Optional[int],
            next_residents: Sequence[P26Player], ctx: _Ctx,
            paired_now: Set[int], all_ids: Set[int],
            *, is_last: bool, c1c7_only: bool = False):
    """Full criterion vector (lower wins lexicographically).
    C5: 0 in non-last brackets (vacuous — no PAB decided there); in the last
    bracket the assignee score (PAB options) or 0 (even close, no PAB)."""
    by_id = ctx.by_id
    if bye is not None:
        c5 = by_id[bye].score
    else:
        c5 = 0.0
    c6 = len(down)
    c7 = tuple(sorted((by_id[i].score for i in down), reverse=True))
    if next_residents:
        c8 = _c8_next_vector(down, next_residents, ctx, paired_now, all_ids)
    else:
        c8 = (0, ())
    c9 = by_id[bye].unplayed if bye is not None else 0
    if c1c7_only:
        return (c5, c6, c7, c8, c9)
    # colours under Art.5 allocation
    alloc = {}
    for xa, xb in pairs:
        w, _ = allocate_colour(by_id[xa], by_id[xb],
                               initial_colour=ctx.req.initial_colour)
        alloc[xa], alloc[xb] = w, (xb if w == xa else xa)
    tops = ctx.topscorers
    c10 = c11 = c12 = c13 = 0
    for xa, xb in pairs:
        for xid in (xa, xb):
            p = by_id[xid]
            seq = C.played_colors(p)
            got_w = alloc[xid] == xid
            new_seq = seq + ("W" if got_w else "B")
            in_pool = xid in tops or (
                by_id[xa].id in tops or by_id[xb].id in tops)
            # C10: topscorer-or-opponent CD beyond ±2
            if in_pool:
                cd = new_seq.count("W") - new_seq.count("B")
                if abs(cd) > 2:
                    c10 += 1
                # C11: 3× same colour
                if len(new_seq) >= 3 and \
                        new_seq[-1] == new_seq[-2] == new_seq[-3]:
                    c11 += 1
            pref, strength = C.preference(p)
            if pref is not None:
                has = "W" if got_w else "B"
                if has != pref:
                    c12 += 1
                    if strength == 2:
                        c13 += 1
    # C14–C21: residents vs MDP-opponents, last vs two-ago, counts vs gaps.
    c14 = c15 = c16 = c17 = 0
    c18: List[float] = []
    c19: List[float] = []
    c20: List[float] = []
    c21: List[float] = []
    down_set = set(down)
    for xa, xb in mdp_pairs:
        a, b = by_id[xa], by_id[xb]
        mdp, opp = (a, b) if a.id in mdp_ids else (b, a)
        gap = abs(mdp.score - opp.score)
        if mdp.last_float == "D":
            c18.append(gap)
        if opp.last_float == "U":
            c15 += 1
            c19.append(gap)
        if mdp.prev_float == "D":
            c20.append(gap)
        if opp.prev_float == "U":
            c17 += 1
            c21.append(gap)
    for xid in down:
        p = by_id[xid]
        if xid not in mdp_ids:  # resident downfloaters (C14/C16)
            if p.last_float == "D":
                c14 += 1
            if p.prev_float == "D":
                c16 += 1
    return (c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17,
            tuple(sorted(c18, reverse=True)), tuple(sorted(c19, reverse=True)),
            tuple(sorted(c20, reverse=True)), tuple(sorted(c21, reverse=True)))


# ======================================================= bracket search

def _iter_homogeneous(residents: List[P26Player], ctx: _Ctx,
                      _c1c7_only: bool = False):
    """Yield (pairs, downfloaters, mdp_pairs=()) in Art.3.6 generation order:
    S1 compositions (original then resident exchanges, 4.3) × S2
    transpositions (4.2). S1 = first MaxPairs by TPN (3.2.2)."""
    n = len(residents)
    max_pairs = n // 2
    if max_pairs == 0:
        yield (), tuple(p.id for p in residents), ()
        return
    bsn = _bsn(residents)
    # All compositions live in BSN space (Art.4.1); map back via inverse.
    # (BSNs are unique within the bracket: 1.2 order has no ties.)
    player_of_bsn = {bsn[p.id]: p for p in residents}
    # S1 = first MaxPairs in Article 1.2 order (3.2.2).
    first = sorted(residents, key=lambda p: (-p.score, p.tpn))[:max_pairs]
    rest = [p for p in residents if p not in set(first)]
    # Original composition first (always). Resident-exchange alterations
    # (4.3) are computed ONLY if the original pass finds no perfect
    # candidate: their count is factorial-scale and pre-guarded.
    compositions = [(frozenset(bsn[p.id] for p in first),
                     frozenset(bsn[p.id] for p in rest))]

    def _emit(comp_s1, comp_s2):
        # 3.6.1: re-sort the newly formed S1/S2 according to Article 1.2.
        s1 = sorted((player_of_bsn[b] for b in comp_s1),
                    key=lambda p: (-p.score, p.tpn))
        # S2 pool in BSN order so permutations() yields Art.4.2
        # lexicographic order (never raw set order — undetermined).
        s2pool = sorted((player_of_bsn[b] for b in comp_s2),
                        key=lambda p: bsn[p.id])
        for s2order in _s2_transpositions(s2pool, len(s1), bsn,
                                            ctx.stepper):
            ctx.stepper.tick()
            pairs = [(s1[i].id, s2order[i].id) for i in range(len(s1))]
            paired = {i for pr in pairs for i in pr}
            down = tuple(sorted(
                (p.id for p in residents if p.id not in paired),
                key=lambda i: ctx.by_id[i].tpn))
            yield pairs, down, ()

    for comp_s1, comp_s2 in compositions:
        yield from _emit(comp_s1, comp_s2)
    for ns1, ns2 in _resident_exchanges(first, rest, bsn, ctx.stepper):
        yield from _emit(frozenset(ns1), frozenset(ns2))


def _iter_heterogeneous(residents: List[P26Player], mdps: List[P26Player],
                        ctx: _Ctx):
    """Yield (pairs, downfloaters, mdp_pairs) in Art.3.7 order: remainder
    moves (3.7.1) -> new S2 transposition + remainder (3.7.2) -> next MDP set
    from Limbo (3.7.3, 4.4.2 order)."""
    max_pairs = (len(residents) + len(mdps)) // 2
    max_m1 = min(len(mdps), len(residents), max_pairs)
    bsn = _bsn(residents + mdps)
    for kept in _mdp_sets(mdps, max_m1, bsn, ctx.stepper):
        # M1 in Article 1.2 order (score desc, TPN asc): positional S1[i]<->S2[i]
        # pairing follows ranking, not raw TPN.
        m1 = sorted(kept,
                    key=lambda i: (-ctx.by_id[i].score, ctx.by_id[i].tpn))
        limbo = [p for p in mdps if p.id not in kept]
        s2pool = sorted(residents, key=lambda p: bsn[p.id])
        n1 = len(m1)
        for s2order in _s2_transpositions(s2pool, n1, bsn, ctx.stepper):
            ctx.stepper.tick()
            mdp_pairs = [(m1[i], s2order[i].id) for i in range(n1)]
            used = {s2order[i].id for i in range(n1)}
            remainder = [p for p in residents if p.id not in used]
            # 3.7.1: remainder moves first (S1R/S2R frozen for this MDP-pairing)
            for rem_pairs, rem_down, _ in _iter_homogeneous(remainder, ctx):
                pairs = list(mdp_pairs) + list(rem_pairs)
                down = tuple(sorted(
                    [p.id for p in limbo] + list(rem_down),
                    key=lambda i: ctx.by_id[i].tpn))
                yield pairs, down, list(mdp_pairs)


def _best_in_bracket(residents: List[P26Player], mdps: List[P26Player],
                     all_ids: Set[int], paired_so_far: Set[int],
                     next_residents: Sequence[P26Player], ctx: _Ctx,
                     is_last: bool, c1c7_only: bool = False):
    """Evaluate all generated candidates; perfect (3.4.1) short-circuits;
    else best per 3.8.1. In the last bracket, plain candidates are valid only
    with no leftover (even close); odd leftovers go through leave-one-unpaired
    PAB options (C5/C9/C2)."""
    cands = []
    iters = (_iter_heterogeneous(residents, mdps, ctx) if mdps
             else _iter_homogeneous(residents, ctx))
    for pairs, down, mdp_pairs in iters:
        if not _abs_ok(pairs, ctx):
            continue
        if is_last and not c1c7_only and down:
            continue  # last bracket: leftovers must be the PAB (see below)
        now_paired = paired_so_far | {i for pr in pairs for i in pr}
        if not _rest_pairable(now_paired, all_ids, ctx):
            continue  # C4
        mdp_ids = {p.id for p in mdps}
        vec = _vector(pairs, down, mdp_pairs, mdp_ids, None,
                      next_residents, ctx, now_paired, all_ids,
                      is_last=is_last, c1c7_only=c1c7_only)
        if not c1c7_only and _quality_zero(vec):
            return (pairs, down, mdp_pairs, None, vec, True)
        cands.append((vec, pairs, down, mdp_pairs, None))
    # last-bracket PAB options (C5/C9/C2): leave one eligible player unpaired.
    # INTERPRETATION (conformance matrix I-D-PAB): C.04.3 Art.2.3.1/2.4.4 fix
    # only (score, unplayed) minimisation and state no further rule, so the
    # final tiebreak follows the family convention used explicitly by Dubov
    # 3.1.5, Double/Team 3.4.4 and Burstein 3.1.5 (largest TPN = lowest rank
    # takes the bye). Deterministic; revisited if FIDE clarifies C.04.3.
    if is_last and not c1c7_only:
        pool = residents + mdps
        for cand in sorted(pool, key=lambda p: (p.score, p.unplayed,
                                                -p.tpn)):
            if not C.pab_eligible(cand):
                continue
            sub_res = [p for p in residents if p.id != cand.id]
            sub_mdp = [p for p in mdps if p.id != cand.id]
            sub_iter = (_iter_heterogeneous(sub_res, sub_mdp, ctx) if sub_mdp
                        else _iter_homogeneous(sub_res, ctx))
            for pairs, down, mdp_pairs in sub_iter:
                if down:
                    continue
                if not _abs_ok(pairs, ctx, extra_bye=cand.id):
                    continue
                mdp_ids = {p.id for p in sub_mdp}
                now_paired = (paired_so_far
                              | {i for pr in pairs for i in pr} | {cand.id})
                vec = _vector(pairs, down, mdp_pairs, mdp_ids, cand.id, (),
                              ctx, now_paired, all_ids, is_last=True)
                cands.append((vec, pairs, down, mdp_pairs, cand.id))
                break  # first (generation-order) pairing per PAB taker
    if not cands:
        return None
    cands.sort(key=lambda c: c[0])
    vec, pairs, down, mdp_pairs, bye = cands[0]
    perfect = _quality_zero(vec) and (
        bye is None or _pab_pool_minimal(bye, residents + mdps, ctx))
    return (pairs, down, mdp_pairs, bye, vec, perfect)


def _quality_zero(vec) -> bool:
    """C6–C21 all fulfilled (zero counts/gaps). C5 handled separately."""
    return all(v == 0 or v == () or v == (0, ()) for v in vec[1:])


def _pab_pool_minimal(bye: int, pool: Sequence[P26Player], ctx: _Ctx) -> bool:
    """C5+C9 minimality within the eligible pool (score, unplayed, -TPN)."""
    me = ctx.by_id[bye]
    for p in pool:
        if p.id != bye and C.pab_eligible(p):
            if (p.score, p.unplayed, -p.tpn) < (me.score, me.unplayed,
                                               -me.tpn):
                return False
    return True


# ================================================================== driver

def pair_dutch(req: P26Request) -> P26Pairing:
    """Dutch-2026 round pairing (1.9.2 top-down; 1.9.3 else Arbiter->typed)."""
    players = list(req.players)
    by_id = {p.id: p for p in players}
    blocked = {(a.id, b.id) for a in players for b in players
               if a.id < b.id and C.rematch(a, b)}
    blocked |= {(b, a) for a, b in list(blocked)}
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    topscorers: Set[int] = set()
    if req.is_last_round:
        limit = req.total_rounds / 2.0
        topscorers = {p.id for p in players if p.score > limit}
    ctx = _Ctx(req, by_id, blocked, stepper, topscorers)
    all_ids = {p.id for p in players}
    scores = sorted({p.score for p in players}, reverse=True)
    pairs: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    bye_id = None
    paired_so_far: Set[int] = set()
    mdps: List[P26Player] = []
    for si, score in enumerate(scores):
        residents = sorted([p for p in players
                            if p.score == score and p.id not in paired_so_far],
                           key=lambda p: p.tpn)
        if not residents and not mdps:
            continue
        is_last = si == len(scores) - 1
        next_res = [] if is_last else sorted(
            [p for p in players if p.score == scores[si + 1]
             and p.id not in paired_so_far], key=lambda p: p.tpn)
        res = _best_in_bracket(residents, mdps, all_ids, paired_so_far,
                               next_res, ctx, is_last)
        if res is None:
            raise ImpossiblePairingError(
                f"bracket at score {score} has no C4-compliant candidate "
                "(Art.1.9.3: Chief Arbiter decides).")
        bpairs, bdown, bmdp_pairs, bbye, _vec, _perfect = res
        if bbye is not None:
            bye_id = bbye
            floats.append((bbye, "D"))
        # colours for the bracket's pairs
        for xa, xb in bpairs:
            w, _ = allocate_colour(by_id[xa], by_id[xb],
                                   initial_colour=req.initial_colour)
            pairs.append((w, xb if w == xa else xa))
        down_set = set(bdown)
        mdp_ids = {p.id for p in mdps}
        for xid in bdown:
            if xid not in mdp_ids:
                floats.append((xid, "D"))
            # Limbo doublers already carry 'D' from above; keep single tag.
        for xa, xb in bmdp_pairs:
            a, b = by_id[xa], by_id[xb]
            mdp, opp = (a, b) if a.id in mdp_ids else (b, a)
            if opp.id not in down_set:
                floats.append((opp.id, "U"))
        paired_so_far |= {i for pr in bpairs for i in pr}
        if bye_id is not None:
            paired_so_far.add(bye_id)
        mdps = [by_id[i] for i in
                sorted(bdown, key=lambda i: (-by_id[i].score, by_id[i].tpn))]
    if len(paired_so_far) != len(players):
        raise ImpossiblePairingError(
            "round pairing incomplete (Art.1.9.3: Chief Arbiter decides).")
    ordered = C.board_order([(by_id[w], by_id[b]) for w, b in pairs])
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset="dutch-2026", notes=())
