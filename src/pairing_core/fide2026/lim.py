"""Lim System 2026 engine (C.04.4.3, F-0112, FULL_TEXT).

Procedural implementation: median routing (2.2), floater triggers (2.3),
proposed pairings 1v(n/2+1) (2.4), exchanges with worked tables (Art.4),
floater selection incl. a–d hierarchy (Art.3), colours with double scrutiny
(Art.5), last-round override (Art.6), R1/R2 recipes (Arts.7–8).

Processing order (2.2) aligns with float directions: groups above the median
are handled top-down (floats go downward = later), groups below bottom-up
(floats go upward = later), median last (paired downward; unpairable median
is extended by cracking per 2.6, never floated out).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import ImpossiblePairingError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


def compatible(a: P26Player, b: P26Player) -> bool:
    """Art.2.1: unplayed + no 3-in-row + no ±3 imbalance for either side.

    A pairing is compatible iff SOME colour assignment avoids the hard bans
    (5.1.1/5.1.2) for both players.
    """
    if C.rematch(a, b):
        return False
    for wa in (True, False):
        if _colour_ok(a, wa) and _colour_ok(b, not wa):
            return True
    return False


def _colour_ok(p: P26Player, white: bool) -> bool:
    """Would giving `white` to p violate 5.1.1 (3-in-row) or 5.1.2 (±3)?"""
    seq = C.played_colors(p) + ("W" if white else "B")
    if len(seq) >= 3 and seq[-1] == seq[-2] == seq[-3]:
        return False
    return abs(seq.count("W") - seq.count("B")) < 3


def due_colour(p: P26Player) -> str:
    """Alternate of last played colour ('due' side for even-making, 3.2.2)."""
    seq = C.played_colors(p)
    if not seq:
        return "W"
    return "B" if seq[-1] == "W" else "W"


def pair_lim(req: P26Request) -> P26Pairing:
    """Lim round pairing with median routing (2.2)."""
    players = list(req.players)
    by_id = {p.id: p for p in players}
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    if req.round_number == 1:
        return _round_one(players, by_id, req)
    remaining = list(players)
    bye_id = None
    if len(remaining) % 2:
        # Art.1: lowest rank (= highest TPN here) in lowest scoregroup.
        low = min(p.score for p in remaining)
        cands = [p for p in remaining
                 if p.score == low and C.pab_eligible(p)]
        if not cands:
            raise ImpossiblePairingError("no eligible Lim PAB taker (Art.1).")
        bye = max(cands, key=lambda p: p.tpn)
        bye_id = bye.id
        remaining = [p for p in remaining if p.id != bye_id]
    rounds_played = req.round_number - 1
    median_score = rounds_played / 2.0
    scores_desc = sorted({p.score for p in remaining}, reverse=True)
    scores_asc = sorted({p.score for p in remaining})
    above = [s for s in scores_desc if s > median_score]
    below = [s for s in scores_asc if s < median_score]
    order = [(s, 1) for s in above] + [(s, -1) for s in below]
    has_median = any(p.score == median_score for p in remaining)
    if has_median:
        order.append((median_score, 1))  # median last, paired downward (2.2)
    members_of = {}
    for p in remaining:
        members_of.setdefault(p.score, []).append(p.id)
    for s in members_of:
        members_of[s].sort(key=lambda i: by_id[i].tpn)
    # destination queues: score -> [player ids] transferred there
    queue: Dict[float, List[int]] = {s: [] for s in members_of}
    # floater origin: player id -> (source group score, 'D' from higher / 'U'
    # from lower). Drives 3.6/3.7 scrutiny priority and 2.6 side counts.
    floater_of: Dict[int, Tuple[float, str]] = {}
    paired: Set[int] = set()
    pending: Set[int] = {p.id for p in remaining}
    result_pairs: List[Tuple[int, int]] = []
    group_pairs: Dict[float, List[Tuple[int, int]]] = {}
    scores_in_order = [s for s, _ in order]
    for idx, (score, direction) in enumerate(order):
        downward = direction == 1
        work_ids = ([i for i in members_of.get(score, []) if i in pending]
                    + [i for i in queue.get(score, []) if i in pending])
        # dedupe, TPN order
        seen = set()
        work = []
        for i in sorted(set(work_ids), key=lambda i: by_id[i].tpn):
            if i in pending and i not in seen:
                seen.add(i)
                work.append(by_id[i])
        if not work:
            continue
        is_median = (score == median_score)
        dest = _dest_score(score, scores_in_order, idx, downward, is_median)
        rest = scores_in_order[idx + 1:]
        further = rest[1] if len(rest) > 1 else None
        upper = score >= median_score
        if is_median:
            ok = _pair_median(work, pending, paired, result_pairs, queue,
                              req, stepper, by_id, median_score, floater_of,
                              group_pairs, members_of, order)
            if not ok:
                raise ImpossiblePairingError(
                    "median scoregroup unpairable even after cracking (2.6).")
        else:
            _pair_group(work, dest, downward, pending, paired, result_pairs,
                        queue, req, stepper, by_id, floater_of, group_pairs,
                        score, upper, members_of, further)
    unplaced = [i for i in pending if i not in paired]
    if unplaced:
        raise ImpossiblePairingError(
            f"Lim left {len(unplaced)} players unpairable.")
    ordered = C.board_order([(by_id[w], by_id[b]) for w, b in result_pairs])
    floats = _float_tags(result_pairs, by_id)
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset="lim-2026", notes=())


def _dest_score(score: float, scores_in_order: List[float], idx: int,
                downward: bool, is_median: bool) -> Optional[float]:
    """Next group in the processing direction (float destination)."""
    if is_median:
        return None
    rest = scores_in_order[idx + 1:]
    return rest[0] if rest else None


def _needs_floater(p: P26Player, work: List[P26Player]) -> bool:
    """Art.2.3.1-2.3.3: no suitable (compatible) opponent in the group."""
    mates = [q for q in work if q.id != p.id]
    if not mates:
        return True
    return all(not compatible(p, q) for q in mates)


def _dest_pool(dest: Optional[float], by_id: Dict[int, P26Player],
               members_of: Dict[float, List[int]],
               queue: Dict[float, List[int]],
               pending: Set[int], paired: Set[int]) -> List[P26Player]:
    """Players known to belong to the adjacent (destination) scoregroup:
    its own members plus already-queued arrivals (3.3/3.4/3.9 reference)."""
    if dest is None:
        return []
    ids = ([i for i in members_of.get(dest, []) if i in pending]
           + [i for i in queue.get(dest, []) if i in pending])
    seen = set()
    out = []
    for i in sorted(set(ids), key=lambda i: by_id[i].tpn):
        if i not in seen:
            seen.add(i)
            out.append(by_id[i])
    return out


def _floater_type(p: P26Player, arrived: Set[int],
                  dest_pool: List[P26Player]) -> int:
    """Art.3.9 disadvantage rank (lower better): d=0 compatible newcomer,
    c=1 incompatible newcomer, b=2 compatible re-floater, a=3 incompatible
    re-floater. ('Re-floater' = already floated into the group just handled.)"""
    was_here = p.id in arrived
    compat = any(compatible(p, q) for q in dest_pool if q.id != p.id)
    if not was_here and compat:
        return 0  # d
    if not was_here:
        return 1  # c
    if compat:
        return 2  # b
    return 3  # a


def _select_floater(work: List[P26Player], dest_pool: List[P26Player],
                    arrived: Set[int], *, downward: bool,
                    maxi: bool) -> P26Player:
    """Art.3.2.2-3.2.4 even-making choice with 3.9 minimisation folded in:
    majority due-colour side (3.2.2) -> least-disadvantaged 3.9 type ->
    3.2.4 number (lowest TPN downward, highest upward). Maxi 100pt guard
    (3.2.3) applies to the due-colour shortlist."""
    whites = sum(1 for p in work if due_colour(p) == "W")
    blacks = len(work) - whites
    if whites == blacks:
        cands = list(work)
    else:
        majority = "W" if whites > blacks else "B"
        cands = [p for p in work if due_colour(p) == majority]
    if not cands:
        cands = list(work)
    if maxi and cands:
        ref = min(work, key=lambda p: p.tpn) if downward else max(
            work, key=lambda p: p.tpn)
        guarded = [p for p in cands
                   if abs((p.rating or 0) - (ref.rating or 0)) <= 100]
        if guarded:
            cands = guarded
    if downward:
        return min(cands,
                   key=lambda p: (_floater_type(p, arrived, dest_pool), p.tpn))
    # upward 3.2.4: highest numbered -> max TPN; 3.9 type still minimised.
    return min(cands,
               key=lambda p: (_floater_type(p, arrived, dest_pool), -p.tpn))


def _pair_group(work: List[P26Player], dest: Optional[float], downward: bool,
                pending: Set[int], paired: Set[int],
                result_pairs: List[Tuple[int, int]],
                queue: Dict[float, List[int]], req: P26Request,
                stepper: Stepper, by_id: Dict[int, P26Player],
                floater_of: Dict[int, Tuple[float, str]],
                group_pairs: Dict[float, List[Tuple[int, int]]],
                group_score: float, upper: bool,
                members_of: Dict[float, List[int]],
                further: Optional[float]) -> None:
    """Pair one non-median scoregroup (2.3-2.5, Art.3, Art.4)."""
    work = list(work)
    arrived = {p.id for p in work if p.id in floater_of}
    dest_pool = _dest_pool(dest, by_id, members_of, queue, pending, paired)
    further_pool = _dest_pool(further, by_id, members_of, queue, pending,
                              paired)
    even_floated = None
    for p in list(work):
        if _needs_floater(p, work):
            work.remove(p)
            _float_one(p, work, dest, further, queue, floater_of,
                       group_score, downward, by_id, dest_pool, further_pool)
    if len(work) % 2:
        even_maker = _select_floater(work, dest_pool, arrived,
                                     downward=downward,
                                     maxi=req.maxi_tournament)
        if even_maker.last_float in ("D", "U") and not _refloat_allowed(
                even_maker, work, by_id, downward, upper, floater_of):
            alt = next((q for q in work
                        if q.id != even_maker.id and (
                            q.last_float not in ("D", "U") or
                            _refloat_allowed(q, work, by_id, downward,
                                             upper, floater_of))),
                       even_maker)
            even_maker = alt
        work.remove(even_maker)
        before = {(d, i) for d in queue for i in queue[d]}
        _float_one(even_maker, work, dest, further, queue, floater_of,
                   group_score, downward, by_id, dest_pool, further_pool)
        after = {(d, i) for d in queue for i in queue[d]}
        floated_now = [i for d, i in after - before]
        even_floated = floated_now[0] if floated_now else None
    res = _exchange_pair(work, by_id, downward=downward, upper=upper,
                         floater_of=floater_of, group_score=group_score,
                         stepper=stepper, maxi=req.maxi_tournament)
    if res is None:
        # Art.4.4: originally odd -> exchange the culprit with the
        # even-maker (4.4.1); originally even -> float the culprit together
        # with the lowest numbered remaining player (4.4.2); retry once.
        res = _apply_44(work, even_floated, dest, further, downward, queue,
                        req, stepper, by_id, floater_of, dest_pool,
                        further_pool, upper, group_score)
        if res is None:
            raise ImpossiblePairingError(
                "scoregroup unpairable after Art.4.4 float.")
    group_pairs[group_score] = list(res)
    for a_id, b_id in res:
        w, b = _lim_colour(by_id[a_id], by_id[b_id], req=req)
        result_pairs.append((w, b))
        paired.add(a_id)
        paired.add(b_id)
        pending.discard(a_id)
        pending.discard(b_id)


def _compat_in_dest(p: P26Player,
                    dest_pool: List[P26Player]) -> bool:
    """Whether p has a compatible opponent in the adjacent group (3.3-3.5)."""
    return any(q.id != p.id and compatible(p, q) for q in dest_pool)


def _float_one(p: P26Player, work: List[P26Player], dest: Optional[float],
               further: Optional[float],
               queue: Dict[float, List[int]],
               floater_of: Dict[int, Tuple[float, str]],
               src_score: float, downward: bool,
               by_id: Dict[int, P26Player],
               dest_pool: List[P26Player],
               further_pool: List[P26Player]) -> int:
    """Float p out of `work` (3.2.1), applying 3.5: a proposed floater with
    no compatible opponent adjacent is exchanged for another group member
    who has one (3.2.4 number order: lowest TPN downward, highest upward;
    the proposed floater rejoins `work`); otherwise floated further. `work`
    is updated in place. Returns the id that actually floated."""
    if dest is None:
        raise ImpossiblePairingError(
            f"floater {p.id} has no adjacent scoregroup (Art.3.5).")
    if _compat_in_dest(p, dest_pool):
        queue.setdefault(dest, []).append(p.id)
        floater_of[p.id] = (src_score, "D" if downward else "U")
        return p.id
    # 3.5 exchange: another member with an adjacent compatible opponent
    # floats instead; p rejoins the group for pairing.
    ordered = sorted((q for q in work if q.id != p.id),
                     key=lambda q: q.tpn if downward else -q.tpn)
    for q in ordered:
        if _compat_in_dest(q, dest_pool):
            work.remove(q)
            work.append(p)
            queue.setdefault(dest, []).append(q.id)
            floater_of[q.id] = (src_score, "D" if downward else "U")
            return q.id
    # otherwise: float to a further scoregroup.
    if further is None:
        raise ImpossiblePairingError(
            f"floater {p.id} incompatible adjacent with no further group.")
    queue.setdefault(further, []).append(p.id)
    floater_of[p.id] = (src_score, "D" if downward else "U")
    return p.id


def _refloat_allowed(cand: P26Player, work: List[P26Player],
                      by_id: Dict[int, P26Player], downward: bool,
                      upper: bool,
                      floater_of: Dict[int, Tuple[float, str]]) -> bool:
    """Art.3.10: allowed unless it produces a/b/c floaters or shrinks pairs.
    Approximated: the remainder must still pair fully (no stranded member)."""
    rest = [p for p in work if p.id != cand.id]
    if len(rest) % 2:
        return False
    sub = {i: floater_of[i] for i in floater_of
           if i in {p.id for p in rest}}
    group_score = cand.score
    return _exchange_pair(rest, by_id, downward=downward, upper=upper,
                          floater_of=sub, group_score=group_score,
                          stepper=None, maxi=False) is not None


def _apply_44(work: List[P26Player], even_floated: Optional[int],
              dest: Optional[float], further: Optional[float],
              downward: bool, queue: Dict[float, List[int]],
              req: P26Request, stepper: Stepper,
              by_id: Dict[int, P26Player],
              floater_of: Dict[int, Tuple[float, str]],
              dest_pool: List[P26Player], further_pool: List[P26Player],
              upper: bool, group_score: float) -> Optional[List[Tuple[int, int]]]:
    """Art.4.4 recovery after a failed exchange search. Culprit generalised
    as the lowest numbered (TPN) unpaired player ("#2"-analogue):
    originally-odd groups exchange the culprit with the even-maker (4.4.1);
    originally-even groups float the culprit together with the lowest
    numbered remaining player (4.4.2). Single retry."""
    if not work:
        return []
    culprit = min(work, key=lambda p: p.tpn)
    if even_floated is not None:
        # 4.4.1: return the even-maker to the group...
        back = by_id[even_floated]
        for q in list(queue.get(dest, [])):
            if q == even_floated:
                queue[dest].remove(q)
        if further is not None:
            for q in list(queue.get(further, [])):
                if q == even_floated:
                    queue[further].remove(q)
        floater_of.pop(even_floated, None)
        if even_floated not in {p.id for p in work}:
            work.append(back)
        # ...and float the culprit instead.
        culprit = min(work, key=lambda p: p.tpn)
        work.remove(culprit)
        _float_one(culprit, work, dest, further, queue, floater_of,
                   group_score, downward, by_id, dest_pool, further_pool)
    else:
        # 4.4.2: float the culprit in company with the lowest numbered
        # remaining player.
        work.remove(culprit)
        _float_one(culprit, work, dest, further, queue, floater_of,
                   group_score, downward, by_id, dest_pool, further_pool)
        if not work:
            return []
        companion = min(work, key=lambda p: p.tpn)
        work.remove(companion)
        _float_one(companion, work, dest, further, queue, floater_of,
                   group_score, downward, by_id, dest_pool, further_pool)
    return _exchange_pair(work, by_id, downward=downward, upper=upper,
                          floater_of=floater_of, group_score=group_score,
                          stepper=stepper, maxi=req.maxi_tournament)


def _exchange_pair(work: List[P26Player], by_id: Dict[int, P26Player], *,
                   downward: bool, upper: bool,
                   floater_of: Dict[int, Tuple[float, str]],
                   group_score: float, stepper, maxi: bool = False,
                   ) -> Optional[List[Tuple[int, int]]]:
    """Art.4 exchanges with Art.3 scrutiny priorities.

    Proposed 1v(n/2+1)... (2.4); scrutiny in compatibility order: floaters
    first per 3.6/3.7 (upper/median groups: DF by higher source score then
    higher TPN, then UF by lower source score then lower TPN, then rest per
    3.6.1-3.6.3; lower groups: UF, DF, rest per 3.7.1-3.7.3), remaining
    players 4.1-direction (downward: #1/lowest-TPN first per the worked 4.2
    table; upward mirrored). Opponents tried in Art.4.2 column order
    (downward: proposed, rest of opposite half in order, then same-half
    others descending — exactly 1v4,1v5,1v6,1v3,1v2; upward mirrored by
    symmetry), with the 3.8 floater-opponent preference tried first; 4.3
    compatibility preserved by backtracking; failure (4.4) -> None.
    """
    n = len(work)
    if n == 0:
        return []
    if n % 2:
        return None
    ordered = sorted(work, key=lambda p: p.tpn)
    half = n // 2
    top, bottom = ordered[:half], ordered[half:]
    proposed = {top[i].id: bottom[i].id for i in range(half)}
    proposed.update({bottom[i].id: top[i].id for i in range(half)})
    top_ids = {p.id for p in top}

    def opponents_of(m: P26Player) -> List[P26Player]:
        first = proposed[m.id]
        rest = [q for q in ordered
                if q.id != m.id and q.id != first]
        in_top = m.id in top_ids
        if downward:
            opp_half = [q for q in rest
                        if (q.id in top_ids) != in_top]
            same_half = [q for q in rest
                         if (q.id in top_ids) == in_top]
            same_half.reverse()  # descending (4.2 table)
            base = [by_id[first]] + opp_half + same_half
        else:
            # upward mirror of the downward column order.
            opp_half = [q for q in reversed(rest)
                        if (q.id in top_ids) != in_top]
            same_half = [q for q in rest
                         if (q.id in top_ids) == in_top]
            base = [by_id[first]] + opp_half + same_half
        if m.id in floater_of:
            # 3.8: floater meets the highest (downward) / lowest (upward)
            # numbered available player due the opposite colour; tried first.
            due_m = due_colour(m)
            want = "B" if due_m == "W" else "W"
            cands = [q for q in base if due_colour(q) == want]
            if maxi and cands:
                ref_rating = by_id[first].rating or 0
                guarded = [q for q in cands
                           if abs((q.rating or 0) - ref_rating) <= 100]
                if guarded:
                    cands = guarded
            if cands:
                pick = max(cands, key=lambda q: q.tpn) if downward else \
                    min(cands, key=lambda q: q.tpn)
                base = [pick] + [q for q in base if q.id != pick.id]
        return base

    scrutiny = _scrutiny_order(work, downward, upper, floater_of)
    assigned: Dict[int, int] = {}

    def backtrack(k: int) -> bool:
        if stepper is not None:
            stepper.tick()
        if k == len(scrutiny):
            return True
        m = scrutiny[k]
        if m.id in assigned:
            return backtrack(k + 1)
        for q in opponents_of(m):
            if q.id in assigned or q.id == m.id:
                continue
            if not compatible(m, q):
                continue
            assigned[m.id] = q.id
            assigned[q.id] = m.id
            if backtrack(k + 1):
                return True
            del assigned[m.id]
            del assigned[q.id]
        return False

    if not backtrack(0):
        return None
    seen = set()
    out = []
    for m in ordered:
        if m.id in seen:
            continue
        o = assigned[m.id]
        out.append((m.id, o))
        seen.add(m.id)
        seen.add(o)
    return out


def _scrutiny_order(work: List[P26Player], downward: bool, upper: bool,
                    floater_of: Dict[int, Tuple[float, str]]
                    ) -> List[P26Player]:
    """Scrutiny order: 3.6/3.7 floater classes first, then 4.1 direction."""
    df = [p for p in work if floater_of.get(p.id, (None, ""))[1] == "D"]
    uf = [p for p in work if floater_of.get(p.id, (None, ""))[1] == "U"]
    rest = [p for p in work if p.id not in {q.id for q in df + uf}]
    # 3.6/3.6.1/3.6.2: higher source score, then higher pairing number.
    df.sort(key=lambda p: (-floater_of[p.id][0], -p.tpn))
    # 3.7/3.7.1/3.7.2: lower source score, then lower pairing number.
    uf.sort(key=lambda p: (floater_of[p.id][0], p.tpn))
    if downward:
        tail = sorted(rest, key=lambda p: p.tpn)  # 4.1.1/#1 first (4.2)
    else:
        tail = sorted(rest, key=lambda p: -p.tpn)  # 4.1.2 mirror
    if upper:
        return df + uf + tail  # 3.6.3
    return uf + df + tail  # 3.7.3


def _adjacent_group(median_score: float, side: str,
                    members_of: Dict[float, List[int]]) -> Optional[float]:
    """Scoregroup adjacent to the median on the given side (nearest score)."""
    if side == "higher":
        above = [s for s in members_of if s > median_score]
        return min(above) if above else None
    below = [s for s in members_of if s < median_score]
    return max(below) if below else None


def _pair_median(work: List[P26Player], pending: Set[int], paired: Set[int],
                 result_pairs: List[Tuple[int, int]],
                 queue: Dict[float, List[int]], req: P26Request,
                 stepper: Stepper, by_id: Dict[int, P26Player],
                 median_score: float,
                 floater_of: Dict[int, Tuple[float, str]],
                 group_pairs: Dict[float, List[Tuple[int, int]]],
                 members_of: Dict[float, List[int]],
                 order) -> bool:
    """Median group paired downward (2.2) with Art.2.6 cracking: on failure,
    crack the next pairing of the adjacent scoregroup on the mandated side
    (2.6.1: the lower scoregroup when more median floaters came from higher
    groups; 2.6.2: the higher scoregroup otherwise), un-pair it, treat its
    players as additional floaters (3.6/3.7 ordering applies), and restart."""
    base_ids = [p.id for p in work]
    extra: List[P26Player] = []
    cracked: Set[Tuple[float, int]] = set()
    while True:
        cur = [by_id[i] for i in base_ids] + extra
        res = _exchange_pair(cur, by_id, downward=True, upper=True,
                             floater_of=floater_of, group_score=median_score,
                             stepper=stepper, maxi=req.maxi_tournament)
        if res is not None:
            for a_id, b_id in res:
                w, b = _lim_colour(by_id[a_id], by_id[b_id], req=req)
                result_pairs.append((w, b))
                paired.add(a_id)
                paired.add(b_id)
                pending.discard(a_id)
                pending.discard(b_id)
            group_pairs[median_score] = list(res)
            return True
        # Art.2.6: side by floater counts in the current median work.
        n_hi = sum(1 for p in cur
                   if floater_of.get(p.id, (None, ""))[0] is not None
                   and floater_of[p.id][0] > median_score)
        n_lo = sum(1 for p in cur
                   if floater_of.get(p.id, (None, ""))[0] is not None
                   and floater_of[p.id][0] < median_score)
        side = "lower" if n_hi > n_lo else "higher"
        target = _adjacent_group(median_score, side, members_of)
        if target is None or target not in group_pairs:
            return False
        pairs = group_pairs[target]
        idx = next((i for i in range(len(pairs))
                    if (target, i) not in cracked), None)
        if idx is None:
            return False
        cracked.add((target, idx))
        a_id, b_id = pairs[idx]
        # un-pair: drop the coloured record, release both players.
        for k in range(len(result_pairs) - 1, -1, -1):
            w, b = result_pairs[k]
            if {w, b} == {a_id, b_id}:
                del result_pairs[k]
                break
        paired.discard(a_id)
        paired.discard(b_id)
        pending.add(a_id)
        pending.add(b_id)
        # treat as additional floaters from the cracked side.
        for pid in (a_id, b_id):
            extra.append(by_id[pid])
            floater_of[pid] = (target, "U" if side == "lower" else "D")


def _lim_colour(a: P26Player, b: P26Player, *, req: P26Request) -> Tuple[int, int]:
    """Art.5 colour allocation with double scrutiny; Art.6 last-round override
    lives in the pairing (colours may then violate 5.1)."""
    sa, sb = C.played_colors(a), C.played_colors(b)
    a_alt = len(sa) >= 2 and sa[-1] == sa[-2]
    b_alt = len(sb) >= 2 and sb[-1] == sb[-2]
    if a_alt and not b_alt:  # 5.3: 2× player must alternate
        return (b.id, a.id) if sa[-1] == "W" else (a.id, b.id)
    if b_alt and not a_alt:
        return (a.id, b.id) if sb[-1] == "W" else (b.id, a.id)
    last_diff = C.last_differing_round(a, b)  # 5.4 walkback (round-aligned)
    if last_diff is not None:
        # most recent difference decides: alternate from it.
        ca, _cb = last_diff
        return (b.id, a.id) if ca == "W" else (a.id, b.id)
    if sa and sb and sa == sb:
        # identical histories: higher-ranked (smaller TPN) gets the alternate.
        hi = a if a.tpn <= b.tpn else b
        lo = b if hi is a else a
        if sa[-1] == "W":
            return (lo.id, hi.id)
        return (hi.id, lo.id)
    cda, cdb = C.colour_difference(a), C.colour_difference(b)
    if cda != cdb:  # 5.5/5.6 balance: more-negative CD gets White
        w = a.id if cda < cdb else b.id
        return (w, b.id if w == a.id else a.id)
    if sa and sa[-1] == "W":  # default alternation
        return (b.id, a.id)
    return (a.id, b.id)


def _round_one(players: List[P26Player], by_id: Dict[int, P26Player],
               req: P26Request) -> P26Pairing:
    """Art.7: odd -> lowest-rated PAB; #1 colour by lot; odd upper-half follow
    #1, evens oppose; worked 40-player tables
    (lot W: 1v21, 22v2, 3v23, 24v4...; lot B mirrored)."""
    remaining = list(players)
    bye_id = None
    if len(remaining) % 2:
        pab = min(remaining, key=lambda p: ((p.rating or 0), p.tpn))
        bye_id = pab.id
        remaining = [p for p in remaining if p.id != bye_id]
    ordered = sorted(remaining, key=lambda p: p.tpn)
    half = len(ordered) // 2
    upper, lower = ordered[:half], ordered[half:]
    one_white = req.initial_colour == "W"
    pairs = []
    for u, l in zip(upper, lower):
        # Odd upper-half follows #1's colour, even upper-half opposes (7.2);
        # White is always mentioned first (worked 40-player tables).
        u_white = one_white if (u.tpn % 2 == 1) else (not one_white)
        pairs.append((u.id, l.id) if u_white else (l.id, u.id))
    ordered_out = C.board_order([(by_id[w], by_id[b]) for w, b in pairs])
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered_out),
        bye_id=bye_id, floats=(), ruleset="lim-2026",
        notes=("round-one-recipe",))


def _float_tags(result_pairs, by_id):
    tags = []
    seen = set()
    for w, b in result_pairs:
        a, bb = by_id[w], by_id[b]
        if a.score != bb.score:
            hi, lo = (a, bb) if a.score > bb.score else (bb, a)
            if hi.id not in seen:
                tags.append((hi.id, "D"))
                seen.add(hi.id)
            if lo.id not in seen:
                tags.append((lo.id, "U"))
                seen.add(lo.id)
    return tags
