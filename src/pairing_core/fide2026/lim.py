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
    paired: Set[int] = set()
    pending: Set[int] = {p.id for p in remaining}
    result_pairs: List[Tuple[int, int]] = []
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
        if is_median:
            ok = _pair_median(work, pending, paired, result_pairs, queue,
                              req, stepper, by_id, median_score)
            if not ok:
                raise ImpossiblePairingError(
                    "median scoregroup unpairable even after cracking (2.6).")
        else:
            _pair_group(work, dest, downward, pending, paired, result_pairs,
                        queue, req, stepper, by_id)
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


def _select_floater(work: List[P26Player], *, downward: bool,
                    maxi: bool) -> P26Player:
    """Art.3.2.2-3.2.4 even-making choice."""
    whites = sum(1 for p in work if due_colour(p) == "W")
    cands = [p for p in work if due_colour(p) == ("W" if whites < len(work) - whites else "B")]
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
        return min(cands, key=lambda p: p.tpn)
    return max(cands, key=lambda p: p.tpn)


def _pair_group(work: List[P26Player], dest: Optional[float], downward: bool,
                pending: Set[int], paired: Set[int],
                result_pairs: List[Tuple[int, int]],
                queue: Dict[float, List[int]], req: P26Request,
                stepper: Stepper, by_id: Dict[int, P26Player]) -> None:
    """Pair one non-median scoregroup (2.3-2.5, Art.3, Art.4)."""
    work = list(work)
    for p in list(work):
        if _needs_floater(p, work):
            work.remove(p)
            _send_floater(p, dest, queue)
    while len(work) % 2:
        cand = _select_floater(work, downward=downward,
                               maxi=req.maxi_tournament)
        if cand.last_float in ("D", "U") and not _refloat_allowed(
                cand, work, by_id):
            alt = next((q for q in work
                        if q.id != cand.id and (
                            q.last_float not in ("D", "U") or
                            _refloat_allowed(q, work, by_id))), cand)
            cand = alt
        work.remove(cand)
        _send_floater(cand, dest, queue)
    res = _exchange_pair(work, by_id, downward=downward, priority=set(),
                         stepper=stepper)
    if res is None:
        # 4.4: float the lowest-numbered remainder member along, retry once
        # with even-making choice; else fail.
        extra = _select_floater(work, downward=downward,
                                maxi=req.maxi_tournament)
        work.remove(extra)
        _send_floater(extra, dest, queue)
        res = _exchange_pair(work, by_id, downward=downward, priority=set(),
                             stepper=stepper)
        if res is None:
            raise ImpossiblePairingError(
                "scoregroup unpairable after 4.4 float (Art.4.4).")
    for a_id, b_id in res:
        w, b = _lim_colour(by_id[a_id], by_id[b_id], req=req)
        result_pairs.append((w, b))
        paired.add(a_id)
        paired.add(b_id)
        pending.discard(a_id)
        pending.discard(b_id)


def _send_floater(p: P26Player, dest: Optional[float],
                  queue: Dict[float, List[int]]) -> None:
    if dest is None:
        raise ImpossiblePairingError(
            f"floater {p.id} has no adjacent scoregroup (Art.3.5).")
    queue.setdefault(dest, []).append(p.id)


def _refloat_allowed(cand: P26Player, work: List[P26Player],
                     by_id: Dict[int, P26Player]) -> bool:
    """Art.3.10: allowed unless it produces a/b/c floaters or shrinks pairs.
    Approximated: the remainder must still pair fully (no stranded member)."""
    rest = [p for p in work if p.id != cand.id]
    if len(rest) % 2:
        return False
    return _exchange_pair(rest, by_id, downward=True, priority=set(),
                          stepper=None) is not None


def _exchange_pair(work: List[P26Player], by_id: Dict[int, P26Player], *,
                   downward: bool, priority: Set[int], stepper) -> Optional[List[Tuple[int, int]]]:
    """Art.4: proposed 1v(n/2+1)...; scrutiny in compatibility order
    (downward: highest number first per 4.1.1; upward: lowest first per 4.1.2);
    opponents tried in Art.4.2 column order (proposed, rest of opposite half
    in order, then same-half others); 4.3 compatibility preserved by
    backtracking; failure (4.4) -> None.

    priority: floater ids paired first (2.6 cracked pairs re-enter as
    additional floaters and restart the median pairing).
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
        rest = []
        for q in ordered:
            if q.id == m.id or q.id == first:
                continue
            # opposite half first (in TPN order), then same half (4.2 tables)
            rest.append(q)
        opp_half = [q for q in rest if (q.id in top_ids) != (m.id in top_ids)]
        same_half = [q for q in rest if (q.id in top_ids) == (m.id in top_ids)]
        return [by_id[first]] + opp_half + same_half

    if downward:
        scrutiny = sorted(work, key=lambda p: -p.tpn)  # 4.1.1 highest first
    else:
        scrutiny = sorted(work, key=lambda p: p.tpn)  # 4.1.2 lowest first
    scrutiny = sorted(scrutiny,
                      key=lambda p: 0 if p.id in priority else 1)
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


def _pair_median(work: List[P26Player], pending: Set[int], paired: Set[int],
                 result_pairs: List[Tuple[int, int]],
                 queue: Dict[float, List[int]], req: P26Request,
                 stepper: Stepper, by_id: Dict[int, P26Player],
                 median_score: float) -> bool:
    """Median group paired downward (2.2) with 2.6 cracking retries: crack the
    next pairing (first proposed pair), treat its players as additional
    floaters (priority pairing), restart."""
    ordered = sorted(work, key=lambda p: p.tpn)
    half = len(ordered) // 2
    cracked: Set[int] = set()
    for _ in range(1 + len(ordered)):
        res = _exchange_pair(ordered, by_id, downward=True, priority=cracked,
                             stepper=stepper)
        if res is not None:
            for a_id, b_id in res:
                w, b = _lim_colour(by_id[a_id], by_id[b_id], req=req)
                result_pairs.append((w, b))
                paired.add(a_id)
                paired.add(b_id)
                pending.discard(a_id)
                pending.discard(b_id)
            return True
        # 2.6: crack the next (first proposed) pairing still uncracked.
        pair = None
        for i in range(half):
            a, b = ordered[i].id, ordered[i + half].id
            if a not in cracked and b not in cracked:
                pair = (a, b)
                break
        if pair is None:
            return False
        cracked.add(pair[0])
        cracked.add(pair[1])
    return False


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
    for ca, cb in zip(reversed(sa), reversed(sb)):  # 5.4 walkback
        if ca != cb:
            # most recent difference decides: alternate from it.
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
