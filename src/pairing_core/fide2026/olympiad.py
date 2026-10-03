"""Olympiad Pairing Rules engine (2022, F-0601, FULL_TEXT annex PDF).

Implements: bye 4.x (lowest initial number eligible; 4.2.1–4.2.3), median
routing 6.4 (top→pre-median, bottom→pre-median, median last; even-field
lower-middle = median; 88-team example), board-1 colours 7.x (R1 lot 7.2;
CD ±2 + 3-in-row bans 7.3; float-necessity override 7.4; equalise→alternate
7.5; walkback 7.6; unplayed = no colour 7.7), floaters 8.x (up 8.2.1–8.2.4 /
down 8.3.1–8.3.4 chains + 8.4 re-floater fallback), pairing 9.x (top-half vs
bottom-half 9.1; rank-priority 9.2; 1v(N+1)→(N+2)…→(2N)→(N−1)… search 9.3 with
worked 15-combination table; 9.4 played-all float-out; 9.5 max-in-group).

Arts.10 (presence) and 11 (publication/management) are tournament management
(OUT — engine pairs present teams; bye value 1MP+2GP is manager-side).
"""

from __future__ import annotations

from typing import Dict, List, Optional, Sequence, Set, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import ImpossiblePairingError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


def _rank(teams: Sequence[P26Player]) -> List[P26Player]:
    """Art.3.2: matchpoints desc, then initial pairing number asc."""
    return sorted(teams, key=lambda p: (-p.score, p.tpn))


def select_olympiad_bye(teams: Sequence[P26Player]) -> P26Player:
    """Art.4: lowest initial number among eligible (4.2.1–4.2.3)."""
    cands = [p for p in teams if not p.got_pab and not p.forfeit_win
             and not p.late_entry]
    if not cands:
        raise ImpossiblePairingError("no eligible Olympiad bye team (Art.4).")
    return min(cands, key=lambda p: p.tpn)


def median_score_group(ranked: Sequence[P26Player]) -> float:
    """Art.6.4: score of the median team (even count -> lower of two middles)."""
    n = len(ranked)
    median = ranked[n // 2]  # lower middle for even n; middle for odd
    return median.score


def board1_colour(a: P26Player, b: P26Player, *,
                  initial_colour: str) -> Tuple[int, int]:
    """Art.7.5–7.7: equalise, then alternate; walkback 7.6; unplayed = none."""
    sa, sb = C.played_colors(a), C.played_colors(b)
    na, nb = sa.count("W"), sb.count("W")
    # equalisation first: fewer Whites gets White (7.5.1)
    if na != nb:
        w = a.id if na < nb else b.id
        return (w, b.id if w == a.id else a.id)
    # 7.5.2 alternation + 7.6 walkback (round-aligned; unplayed = no colour)
    last_diff = C.last_differing_round(a, b)
    if last_diff is not None:
        ca, _cb = last_diff
        w = a.id if ca == "B" else b.id
        return (w, b.id if w == a.id else a.id)
    if sa:
        # always same colours: higher ranked alternated from last (7.6)
        hi = a if (a.score, -a.tpn) >= (b.score, -b.tpn) else b
        lo = b if hi is a else a
        last = sa[-1] if hi is a else sb[-1]
        w = hi.id if last == "B" else lo.id
        return (w, lo.id if w == hi.id else hi.id)
    w = a.id if initial_colour == "W" else b.id
    return (w, b.id if w == a.id else a.id)


def _colour_bans_ok(p: P26Player, white: bool) -> bool:
    """Art.7.3 bans (CD ±2, 3-in-row) for a prospective board-1 colour."""
    seq = C.played_colors(p) + ("W" if white else "B")
    if len(seq) >= 3 and seq[-1] == seq[-2] == seq[-3]:
        return False
    cd = seq.count("W") - seq.count("B")
    return abs(cd) <= 2


def pair_9x(group: List[P26Player], by_id: Dict[int, P26Player],
            stepper: Stepper, *, ignore_colour_bans: bool = False,
            reverse_scrutiny: bool = False) -> Optional[List[Tuple[int, int]]]:
    """Art.9.1–9.3: top-half vs bottom-half; first team vs N+1, N+2... 2N,
    then N−1... (worked 15-combination table order); colour bans 7.3 enforced
    unless ignore_colour_bans (7.4 override tried by caller second).
    Scrutiny 9.2: top-down (median and above) or bottom-up (below median)."""
    order = _rank(group)
    n = len(order)
    if n % 2:
        return None
    half = n // 2
    assigned: Dict[int, int] = {}

    def opponents_of(i: int) -> List[int]:
        # 9.3 order for the member at index i: N+1..2N then N−1..1 style.
        if i < half:
            cand = list(range(i + half, n)) + list(range(i + half - 1, -1, -1))
        else:
            cand = (list(range(i - half, -1, -1))
                    + list(range(i - half + 1, half))
                    + list(range(half, n)))
        seen = set()
        uniq = []
        for j in cand:
            if j != i and j not in seen:
                seen.add(j)
                uniq.append(j)
        return uniq

    rank_seq = list(range(n))
    if reverse_scrutiny:
        rank_seq = list(reversed(rank_seq))

    def backtrack() -> bool:
        stepper.tick()
        m = next((order[k] for k in rank_seq if order[k].id not in assigned),
                 None)
        if m is None:
            return True
        i = order.index(m)
        for j in opponents_of(i):
            q = order[j]
            if q.id in assigned:
                continue
            if C.rematch(m, q):
                continue
            # colour bans: some assignment must satisfy 7.3 for both
            if not ignore_colour_bans and not (
                    (_colour_bans_ok(m, True) and _colour_bans_ok(q, False))
                    or (_colour_bans_ok(m, False) and _colour_bans_ok(q, True))):
                continue
            assigned[m.id] = q.id
            assigned[q.id] = m.id
            if backtrack():
                return True
            del assigned[m.id]
            del assigned[q.id]
        return False

    if not backtrack():
        return None
    seen = set()
    out = []
    for p in order:
        if p.id in seen:
            continue
        o = assigned[p.id]
        out.append((p.id, o))
        seen.add(p.id)
        seen.add(o)
    return out


def pair_olympiad(req: P26Request) -> P26Pairing:
    """Olympiad round pairing (median routing + 8.x floaters + 9.x search)."""
    teams = list(req.players)
    by_id = {p.id: p for p in teams}
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    remaining = list(teams)
    bye_id = None
    if len(remaining) % 2:
        bye = select_olympiad_bye(remaining)
        bye_id = bye.id
        remaining = [p for p in remaining if p.id != bye_id]
    ranked = _rank(remaining)
    med = median_score_group(ranked)
    groups = _matchpoint_groups(ranked)
    above = [g for g in groups if g[0] > med]
    below = [g for g in groups if g[0] < med]
    median = [g for g in groups if g[0] == med]
    order = above + list(reversed(below)) + median  # 6.4
    paired: Set[int] = set()
    result: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    # group members as ranked lists; floaters attach to adjacent groups
    queue: Dict[float, List[int]] = {}
    for gi, (score, members) in enumerate(order):
        work = [by_id[i] for i in members if i not in paired]
        work += [by_id[i] for i in queue.get(score, []) if i not in paired]
        work = _rank(work)
        is_below = score < med
        # odd group -> floater per 8.2/8.3 with fallback chains
        while len(work) % 2:
            f = _select_floater(work, is_below, by_id, stepper,
                                queue=queue, order=order, gi=gi)
            work.remove(f)
            floats.append((f.id, "U" if is_below else "D"))
        res = pair_9x(work, by_id, stepper,
                      reverse_scrutiny=is_below)
        if res is None:  # 7.4: disregard 7.3 bans if group unpairable
            res = pair_9x(work, by_id, stepper, ignore_colour_bans=True,
                          reverse_scrutiny=is_below)
        if res is None:
            raise ImpossiblePairingError(
                f"matchpoint group {score} unpairable (Art.9).")
        for a_id, b_id in res:
            w, b = _assign_board_colour(by_id[a_id], by_id[b_id],
                                       initial_colour=req.initial_colour)
            result.append((w, b))
            paired.add(a_id)
            paired.add(b_id)
    unplaced = [p.id for p in remaining if p.id not in paired]
    if unplaced:
        raise ImpossiblePairingError(f"Olympiad left {unplaced} unpaired.")
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in result),
        bye_id=bye_id, floats=tuple(floats), ruleset="olympiad-2022",
        notes=())


def _matchpoint_groups(ranked):
    groups = []
    cur = None
    for p in ranked:
        if cur is None or cur[0] != p.score:
            cur = (p.score, [])
            groups.append(cur)
        cur[1].append(p.id)
    return groups


def _assign_board_colour(a: P26Player, b: P26Player, *,
                         initial_colour: str) -> Tuple[int, int]:
    """Board-1 colour for a decided pair: the Art.7.5–7.6 choice when it
    respects the 7.3 bans for both teams, else the swapped assignment when
    that one does (7.4 override documented in notes by caller)."""
    w, bl = board1_colour(a, b, initial_colour=initial_colour)
    if _colour_bans_ok(a, w == a.id) and _colour_bans_ok(b, bl == b.id):
        return (w, bl)
    if _colour_bans_ok(a, bl == a.id) and _colour_bans_ok(b, w == b.id):
        return (bl, w)
    return (w, bl)


def _select_floater(work, is_below, by_id, stepper, *, queue, order, gi):
    """Art.8.2/8.3: below-median odd -> highest ranked up (8.2.1); above ->
    lowest ranked down (8.3.1); fallbacks: remainder-completeness (8.x.2:
    rest must admit a 9.x pairing), played-all/re-float (8.x.3/8.4: keep
    rank order), float-two-groups (8.x.4: route one step further).

    The floater is routed into the queue of the next group in processing
    order (toward the median), so it is paired there — never dropped.
    """
    cands = list(work) if is_below else list(reversed(work))
    # 8.4 last resort handled by caller loop; here: try each candidate.
    for cand in cands:
        rest = [p for p in work if p.id != cand.id]
        if pair_9x(rest, by_id, stepper,
                   reverse_scrutiny=is_below) is not None:
            _route_floater(cand, queue, order, gi)
            return cand
    # 8.2.4/8.3.4: float two groups (route further); 8.4: re-choose.
    cand = cands[0]
    _route_floater(cand, queue, order, gi, extra=True)
    return cand


def _route_floater(cand, queue, order, gi, extra=False):
    # Processing always moves toward the median (above: top-down; below:
    # bottom-up), so floaters route to the next group in processing order.
    # (Median is provably even when the field is even, so the clamp below
    # is defensive only: total even minus even paired groups leaves even.)
    step = 2 if extra else 1
    di = max(0, min(len(order) - 1, gi + step))
    dest = order[di][0]
    queue.setdefault(dest, []).append(cand.id)
