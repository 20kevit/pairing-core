"""Dubov System 2026 engine (C.04.4.1, F-0108, FULL_TEXT).

Implements: ratings-mandatory (1.1; missing -> InvalidPlayerError, since the
caller (Chief Arbiter duty 1.1.2) must supply provisional ratings), ARO (1.7),
MaxT (1.8), PAB order 3.1, bracket 3.2 (min upfloaters; best set; G1/G2;
shifters; ARO sort; first legal T2), sorting Art.4 (middle-outward shifters
with worked A–G example), colours Art.5.
"""

from __future__ import annotations

from itertools import permutations
from typing import Dict, List, Optional, Sequence, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidPlayerError,
)
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper, exists_complete_pairing
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


def aro(p: P26Player, by_id: Dict[int, P26Player]) -> int:
    """Art.1.7: mean of PLAYED opponents' ratings, round half-up; zero if none."""
    ratings = [by_id[o].rating for o in p.opponents
               if o in by_id and by_id[o].rating is not None]
    if not ratings:
        return 0
    from fractions import Fraction

    mean = Fraction(sum(ratings), len(ratings))
    base = mean.numerator // mean.denominator
    if (mean - base) >= Fraction(1, 2):
        base += 1
    return base


def max_t(total_rounds: int) -> int:
    """Art.1.8.2: MaxT = 2 + floor(Rnds/5)."""
    return 2 + total_rounds // 5


def _check_ratings(players: Sequence[P26Player]) -> None:
    missing = [p.id for p in players if p.rating is None]
    if missing:
        raise InvalidPlayerError(
            f"dubov-2026 requires ratings (Art.1.1.1); missing for ids {missing}. "
            "Chief Arbiter must assign provisional ratings (Art.1.1.2).")


def _bracket_ok(pairs: Sequence[Tuple[int, int]], by_id: Dict[int, P26Player],
                *, skip_c3: bool = False) -> bool:
    """Legal = C1 + C3 (+C4 handled by construction/selection)."""
    for xa, xb in pairs:
        a, b = by_id[xa], by_id[xb]
        if C.rematch(a, b):
            return False
        if not skip_c3:
            pa = C.preference(a, dubov_zero_game=True)
            pb = C.preference(b, dubov_zero_game=True)
            if pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0]:
                return False
    return True


def _colour_misses(pairs: Sequence[Tuple[int, int]],
                   by_id: Dict[int, P26Player], *,
                   initial_colour: str) -> int:
    """C7: players not getting their colour preference under Art.5 allocation."""
    misses = 0
    for xa, xb in pairs:
        a, b = by_id[xa], by_id[xb]
        w, _ = dubov_colour(a, b, initial_colour=initial_colour)
        for p in (a, b):
            pref = C.preference(p, dubov_zero_game=True)[0]
            if pref is None:
                continue
            has = "W" if w == p.id else "B"
            if has != pref:
                misses += 1
    return misses


def dubov_colour(a: P26Player, b: P26Player, *,
                 initial_colour: str) -> Tuple[int, int]:
    """Art.5. Higher-ranked = more points else smaller TPN (5.2.1)."""
    hr = a if (a.score, -a.tpn) >= (b.score, -b.tpn) else b
    opp = b if hr is a else a
    sa, sb = C.played_colors(hr), C.played_colors(opp)
    if not sa and not sb:  # 5.2.1
        odd_initial = (hr.tpn % 2 == 1) == (initial_colour == "W")
        w = hr.id if odd_initial else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    pa = C.preference(hr, dubov_zero_game=True)
    pb = C.preference(opp, dubov_zero_game=True)
    if pa[0] is not None and pb[0] is not None and pa[0] != pb[0]:
        # 5.2.2 grant both (possible exactly when preferences differ).
        w = hr.id if pa[0] == "W" else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    if pa[1] > pb[1] and pa[0] is not None:
        # 5.2.3 grant the stronger preference (higher-ranked side).
        return (hr.id, opp.id) if pa[0] == "W" else (opp.id, hr.id)
    if pb[1] > pa[1] and pb[0] is not None:
        return (opp.id, hr.id) if pb[0] == "W" else (hr.id, opp.id)
    for ca, cb in zip(reversed(sa), reversed(sb)):  # 5.2.4
        if ca != cb:
            w = hr.id if ca == "B" else opp.id
            return (w, opp.id if w == hr.id else hr.id)
    # 5.2.5 higher-ranked preference (already unequal handled above; fallthrough
    # = equal/no preferences): grant higher-ranked if it has one, else alternate.
    if pa[0] == "W":
        return (hr.id, opp.id)
    if pa[0] == "B":
        return (opp.id, hr.id)
    if sa:
        w = hr.id if sa[-1] == "B" else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    w = hr.id if initial_colour == "W" else opp.id
    return (w, opp.id if w == hr.id else hr.id)


def _shifter_order(seekers: List[P26Player], *, white: bool,
                   by_id: Dict[int, P26Player]) -> List[int]:
    """Art.4.3: White seekers by ARO asc else TPN; Black seekers TPN asc;
    middle-outward numbering (worked A–G example: D,C,E,B,F,A,G)."""
    if white:
        ordered = sorted(seekers,
                         key=lambda p: (aro(p, by_id), p.tpn))
    else:
        ordered = sorted(seekers, key=lambda p: p.tpn)
    # middle-outward: repeatedly take middle (higher of two middles).
    result: List[P26Player] = []
    work = list(ordered)
    while work:
        mid = (len(work) - 1) // 2
        result.append(work.pop(mid))
    return [p.id for p in result]


def pair_dubov(req: P26Request) -> P26Pairing:
    """Dubov round pairing (1.9.2: PAB first, then top-down scoregroups)."""
    players = list(req.players)
    _check_ratings(players)
    by_id = {p.id: p for p in players}
    mt = max_t(req.total_rounds)
    up_count = dict(req.prior_upfloats)
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    blocked = [(a.id, b.id) for a in players for b in players
               if a.id < b.id and C.rematch(a, b)]
    pairs: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    bye_id = None
    remaining = list(players)
    if len(remaining) % 2:
        bye_id = _select_pab(remaining, by_id, blocked, stepper)
        remaining = [p for p in remaining if p.id != bye_id]
    guard = 0
    while remaining:
        guard += 1
        if guard > len(players) + 2:
            raise ImpossiblePairingError("scoregroup loop did not terminate.")
        top = max(p.score for p in remaining)
        residents = [p for p in remaining if p.score == top]
        lower = sorted([p for p in remaining if p.score < top],
                       key=lambda p: (-p.score, p.tpn))
        ups = _select_upfloaters(residents, lower, by_id, blocked, stepper,
                                 req=req, mt=mt, up_count=up_count)
        bracket = residents + ups
        for u in ups:
            floats.append((u.id, "U"))
        chosen = _pair_bracket(bracket, by_id, blocked, stepper, req=req)
        for wa, bl in chosen:
            a, b = by_id[wa], by_id[bl]
            w, bb = dubov_colour(a, b, initial_colour=req.initial_colour)
            pairs.append((w, bb))
        used = {i for pr in chosen for i in pr}
        remaining = [p for p in remaining if p.id not in used]
    ordered = C.board_order([(by_id[w], by_id[b]) for w, b in pairs])
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset="dubov-2026", notes=())


def _select_pab(remaining: Sequence[P26Player], by_id: Dict[int, P26Player],
                blocked: Sequence[Tuple[int, int]],
                stepper: Stepper) -> int:
    """Art.3.1: eligible -> completion -> lowest score -> most games ->
    largest TPN."""
    cands = sorted([p for p in remaining if C.pab_eligible(p)],
                   key=lambda p: (p.score, -p.played, -p.tpn))
    for cand in cands:
        rest = [p for p in remaining if p.id != cand.id]
        if len(rest) % 2:
            continue
        if exists_complete_pairing(rest, blocked, stepper):
            return cand.id
    raise ImpossiblePairingError("no Dubov PAB assignee (Art.3.1).")


def _select_upfloaters(residents: Sequence[P26Player],
                       lower: Sequence[P26Player],
                       by_id: Dict[int, P26Player],
                       blocked: Sequence[Tuple[int, int]],
                       stepper: Stepper, *, req: P26Request,
                       mt: int, up_count: Dict[int, int]) -> List[P26Player]:
    """Art.3.2.1-3.2.2 + 4.2: minimum-k sets; K-sets by smallest differing
    sequence number (score-desc/TPN-asc keying); best = higher-priority
    quality first (C5 count, C6 scores, C7 colours, C8-C10 max-upfloat guards
    unless last round)."""
    pool = [p.id for p in lower]
    seq = {pid: i for i, pid in
           enumerate(sorted(pool, key=lambda pid: (-by_id[pid].score,
                                                   by_id[pid].tpn)))}
    best = None
    best_k = None
    for k in range(0, len(pool) + 1):
        if (len(residents) + k) % 2:
            continue
        sets = sorted(C.lexicographic_sets(pool, k),
                      key=lambda s: tuple(sorted(seq[i] for i in s)))
        for combo in sets:
            stepper.tick()
            ups = [by_id[i] for i in combo]
            bracket = list(residents) + ups
            if not exists_complete_pairing(bracket, blocked, stepper):
                continue
            vec = _bracket_vector(bracket, ups, by_id, req=req, mt=mt,
                                  up_count=up_count)
            key = ((k,) + vec, tuple(sorted(seq[i] for i in combo)))
            if best is None or key < best[0]:
                best = (key, ups)
                best_k = k
        if best_k == k:
            # C5 fixes the count at the minimum feasible k; stop deepening.
            break
    if best is None:
        raise ImpossiblePairingError("no Dubov upfloater set (Art.3.2).")
    return best[1]


def _bracket_vector(bracket, ups, by_id, *, req, mt, up_count):
    """(C6 score-multiset desc [higher wins -> negate], C7 colour misses,
    C8 max-upfloaters used, C9 repeat-max usage, C10 previous-round reuse)."""
    up_scores = tuple(sorted((u.score for u in ups), reverse=True))
    # colour misses need a pairing; use best-effort pairing for scoring:
    trial = _pair_bracket_best_effort(bracket, by_id, req=req)
    misses = _colour_misses(trial, by_id,
                            initial_colour=req.initial_colour)
    maxed = [u.id for u in ups if up_count.get(u.id, 0) >= mt]
    rep_max = sum(up_count.get(u.id, 0) for u in ups
                  if up_count.get(u.id, 0) >= mt)
    prev_reuse = sum(1 for u in ups if u.last_float == "U")
    guard_on = 0 if req.is_last_round else 1
    return (tuple(-s for s in up_scores), misses,
            guard_on * len(maxed), guard_on * rep_max,
            guard_on * prev_reuse)


def _pair_bracket_best_effort(bracket, by_id, *, req) -> List[Tuple[int, int]]:
    """First identifier-order legal pairing (for C7 vector scoring)."""
    order = sorted(bracket, key=lambda p: p.tpn)
    ids = [p.tpn for p in order]
    by_tpn = {p.tpn: p for p in order}

    def rec(rem: Tuple[int, ...]) -> Optional[List[Tuple[int, int]]]:
        if not rem:
            return []
        first = rem[0]
        for i in range(1, len(rem)):
            a, b = by_tpn[first], by_tpn[rem[i]]
            if C.rematch(a, b):
                continue
            pa = C.preference(a, dubov_zero_game=True)
            pb = C.preference(b, dubov_zero_game=True)
            if pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0]:
                continue
            sub = rec(rem[1:i] + rem[i + 1:])
            if sub is not None:
                return [(a.id, b.id)] + sub
        return None

    return rec(tuple(ids)) or []


def _pair_bracket(bracket: Sequence[P26Player], by_id: Dict[int, P26Player],
                  blocked: Sequence[Tuple[int, int]], stepper: Stepper,
                  *, req: P26Request) -> List[Tuple[int, int]]:
    """Art.3.2.3-3.2.6: G1 (White-seekers, else TPN top-half) / G2; shift
    unavoidable same-subgroup pairs + equalise (best = first 4.3-order set
    with best C7-legal pairing); S1 = ARO-asc/TPN-asc; first legal T2."""
    whites = [p for p in bracket
              if C.preference(p, dubov_zero_game=True)[0] == "W"]
    if whites and len(whites) != len(bracket):
        g1, g2 = list(whites), [p for p in bracket if p not in whites]
    else:
        half = (len(bracket) + 1) // 2
        topo = sorted(bracket, key=lambda p: p.tpn)
        g1, g2 = topo[:half], topo[half:]
    g1, g2 = _rebalance(g1, g2, by_id, blocked, stepper,
                        initial_colour=req.initial_colour)
    s1 = sorted(g1, key=lambda p: (aro(p, by_id), p.tpn))
    t2 = _first_legal_transposition(s1, g2, by_id, stepper)
    return [(a.id, by_id[t].id) for a, t in zip(s1, t2)]


def _rebalance(g1: List[P26Player], g2: List[P26Player],
               by_id: Dict[int, P26Player],
               blocked: Sequence[Tuple[int, int]],
               stepper: Stepper, *, initial_colour: str) -> Tuple[List[P26Player], List[P26Player]]:
    """Art.3.2.4: shift unavoidable same-subgroup pairs, then equalise sizes;
    best = first 4.3-order set yielding best C7-legal pairing."""
    for _ in range(3):
        stepper.tick()
        small, large = (g1, g2) if len(g1) <= len(g2) else (g2, g1)
        need_shift = _forced_same(small, large)
        moved = False
        if need_shift:
            cand = _best_shift_set(small, large, by_id, need_shift,
                                   initial_colour=initial_colour)
            if cand:
                for p in cand:
                    small.remove(p)
                    large.append(p)
                moved = True
        if len(g1) != len(g2):
            big, sml = (g1, g2) if len(g1) > len(g2) else (g2, g1)
            k = (len(big) - len(sml)) // 2  # bracket size is even: exact half
            cand = _best_shift_set(big, sml, by_id, k,
                                   initial_colour=initial_colour)
            if cand:
                for p in cand:
                    big.remove(p)
                    sml.append(p)
                moved = True
        if not moved:
            break
    return g1, g2


def _legal_edge(a: P26Player, b: P26Player) -> bool:
    """C1 + C3 legality of a prospective pair (Dubov: no topscorer carve-out)."""
    if C.rematch(a, b):
        return False
    pa = C.preference(a, dubov_zero_game=True)
    pb = C.preference(b, dubov_zero_game=True)
    return not (pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0])


def _max_cross_matching(left: List[P26Player],
                        right: List[P26Player]) -> Dict[int, int]:
    """Deterministic Kuhn matching left->right over legal edges (TPN order)."""
    adj = {p.id: sorted([q.id for q in right if _legal_edge(p, q)])
           for p in sorted(left, key=lambda p: p.tpn)}
    match_r: Dict[int, int] = {}

    def visit(u: int, seen: set) -> bool:
        for v in adj[u]:
            if v in seen:
                continue
            seen.add(v)
            if v not in match_r or visit(match_r[v], seen):
                match_r[v] = u
                return True
        return False

    for u in sorted(adj):
        visit(u, set())
    return match_r


def _forced_same(group: List[P26Player], other: List[P26Player]) -> int:
    """Unavoidable same-subgroup pairs for `group`: members that cannot all
    be matched across (deficit of max cross-matching). Art.3.2.4.1."""
    if not group or not other:
        return 0
    matched = _max_cross_matching(group, other)
    return len(group) - len(matched)


def _greedy_cross_misses(g1: List[P26Player], g2: List[P26Player],
                         by_id: Dict[int, P26Player], *,
                         initial_colour: str) -> Optional[int]:
    """Colour misses of the greedy first-legal cross pairing (C7 estimate);
    None if no full legal cross pairing exists."""
    if len(g1) != len(g2):
        return None
    used = set()
    misses = 0
    for a in sorted(g1, key=lambda p: p.tpn):
        found = None
        for b in sorted(g2, key=lambda p: p.tpn):
            if b.id in used or not _legal_edge(a, b):
                continue
            found = b
            break
        if found is None:
            return None
        used.add(found.id)
        w, _ = dubov_colour(a, found, initial_colour=initial_colour)
        for p in (a, found):
            pref = C.preference(p, dubov_zero_game=True)[0]
            if pref is None:
                continue
            if ("W" if w == p.id else "B") != pref:
                misses += 1
    return misses


def _best_shift_set(src: List[P26Player], dst: List[P26Player],
                    by_id: Dict[int, P26Player], k: int, *,
                    initial_colour: str) -> List[P26Player]:
    """First 4.3-order k-set that can yield a legal pairing, best C7 first:
    min colour-miss estimate, ties -> earlier 4.3 order (Art.3.2.4 note)."""
    if k <= 0:
        return []
    is_white_group = any(C.preference(p, dubov_zero_game=True)[0] == "W"
                         for p in src)
    order = _shifter_order(src, white=is_white_group, by_id=by_id)
    ranked = {pid: i for i, pid in enumerate(order)}
    cands = sorted(C.lexicographic_sets([p.id for p in src], k),
                   key=lambda s: tuple(sorted(ranked[i] for i in s)))
    best = None
    for combo in cands:
        combo_set = set(combo)
        new_src = [p for p in src if p.id not in combo_set]
        new_dst = list(dst) + [by_id[i] for i in combo]
        est = _greedy_cross_misses(new_src, new_dst, by_id,
                                   initial_colour=initial_colour)
        if est is None:
            continue
        key = (est, tuple(sorted(ranked[i] for i in combo)))
        if best is None or key < best[0]:
            best = (key, [by_id[i] for i in combo])
    return best[1] if best else []


def _first_legal_transposition(s1: List[P26Player], g2: List[P26Player],
                               by_id: Dict[int, P26Player],
                               stepper: Stepper) -> List[int]:
    """Art.3.2.6 + 4.4: G2 transpositions in TPN-asc sequence order; first
    yielding a legal pairing (1-1, 2-2, ...)."""
    base = sorted([p.tpn for p in g2])
    id_of_tpn = {p.tpn: p.id for p in g2}
    # permutations() of sorted input yields lexicographic order, matching the
    # Art.4.4.2 worked example ({A,B,C} {A,C,B} {B,A,C} {B,C,A} {C,A,B} {C,B,A}).
    for perm in permutations(base):
        stepper.tick()
        ok = True
        for a, t in zip(s1, perm):
            b = by_id[id_of_tpn[t]]
            if C.rematch(a, b):
                ok = False
                break
            pa = C.preference(a, dubov_zero_game=True)
            pb = C.preference(b, dubov_zero_game=True)
            if pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0]:
                ok = False
                break
        if ok:
            return [id_of_tpn[t] for t in perm]
    raise ImpossiblePairingError("no legal Dubov G2 transposition (Art.3.2.6).")
