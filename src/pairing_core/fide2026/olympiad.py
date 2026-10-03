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
    """Art.4.1/4.2: bye to the eligible team with the LOWEST ranking in 3.2
    order (lowest matchpoints; ties: largest initial number). 4.2.1–4.2.3
    map to got_pab / forfeit_win / late_entry."""
    cands = [p for p in teams if not p.got_pab and not p.forfeit_win
              and not p.late_entry]
    if not cands:
        raise ImpossiblePairingError("no eligible Olympiad bye team (Art.4).")
    return min(cands, key=lambda p: (p.score, -p.tpn))


def seed_initial_numbers(entries: Sequence[Tuple[int, Sequence[int], str]]
                         ) -> Dict[int, int]:
    """Art.3.1 initial pairing numbers: avg of four highest ratings desc,
    then fifth-player rating desc, then alphabetical, then id asc
    (deterministic final tiebreak). Unrated/missing board ratings count 0.0;
    a missing fifth rating sorts after any present one. Caller duty to feed
    board ratings; pairing uses the resulting numbers as TPNs."""
    keyed = []
    for pid, ratings, name in entries:
        r = sorted((x if x is not None else 0 for x in ratings),
                   reverse=True)
        avg4 = sum(r[:4]) / 4.0 if r[:4] else 0.0
        fifth = r[4] if len(r) >= 5 else None
        keyed.append((pid, avg4, fifth, name))
    keyed.sort(key=lambda e: (-e[1], -(e[2] if e[2] is not None else -1),
                              e[3], e[0]))
    return {pid: i + 1 for i, (pid, _, _, _) in enumerate(keyed)}


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
    """Art.9.1–9.3: top-half vs bottom-half; subgroup-relative search (the
    same procedure applied to each subgroup: its first team tries N+1, N+2,
    … 2N, then N−1 …). Scrutiny 9.2: top-down (median and above) or
    bottom-up (below median), i.e. the subgroup is ordered accordingly.
    Colour bans 7.3 enforced unless ignore_colour_bans (7.4 override tried
    by the caller second)."""
    order = _rank(group)
    n = len(order)
    if n % 2:
        return None
    if reverse_scrutiny:
        order = list(reversed(order))
    assigned: Dict[int, int] = {}

    def backtrack() -> bool:
        stepper.tick()
        # subgroup = still-unassigned, in scrutiny order; its first team
        # tries positions N'+1 .. 2N', then N'−1 .. 1 (9.3).
        sub = [p for p in order if p.id not in assigned]
        if not sub:
            return True
        m = sub[0]
        half = len(sub) // 2
        for j in (list(range(half, len(sub)))
                  + list(range(half - 1, -1, -1))):
            q = sub[j]
            if q.id in assigned or q.id == m.id:
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
    for p in _rank(group):
        if p.id in seen:
            continue
        o = assigned[p.id]
        out.append((p.id, o))
        seen.add(p.id)
        seen.add(o)
    return out


def pair_olympiad(req: P26Request) -> P26Pairing:
    """Olympiad round pairing (median routing 6.4 + 8.x/9.4 floaters + 9.x).

    Worklist over the 6.4 processing order: floaters always route toward the
    median, except median 9.4-floaters (down to adjacent-below, reprocessed).
    Reprocessing is deterministically capped (typed error on ping-pong).
    Publication order follows 11.1 (MP, sum, average rating)."""
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
    scores = [s for s, _ in order]
    members_of = {s: list(m) for s, m in order}
    paired: Set[int] = set()
    result: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    queue: Dict[float, List[int]] = {s: [] for s in scores}
    odd_ids: Set[int] = set()  # 8.x odd-floaters (designated partners)
    up_ids: Set[int] = set()  # arrivals floated UP (8.2.x; rest are DOWN)
    group_pairs: Dict[float, List[Tuple[int, int]]] = {}
    counts: Dict[int, int] = {}
    pending = list(range(len(order)))
    while pending:
        gi = pending.pop(0)
        counts[gi] = counts.get(gi, 0) + 1
        if counts[gi] > 3:
            raise ImpossiblePairingError(
                "Olympiad group reprocessing did not converge (8.x/9.4).")
        if gi in group_pairs:
            _unpair_group(order[gi][0], group_pairs, result, paired)
        routed = _process_group(
            gi, order, scores, members_of, med, by_id, stepper, req,
            paired, result, floats, queue, odd_ids, up_ids, group_pairs)
        for dest_gi in routed:
            if dest_gi != gi and dest_gi not in pending:
                pending.append(dest_gi)
        # keep 6.4 order among newly scheduled (stable, deterministic)
        pending.sort()
    unplaced = [p.id for p in remaining if p.id not in paired]
    if unplaced:
        raise ImpossiblePairingError(f"Olympiad left {unplaced} unpaired.")
    ordered = _olympiad_board_order(result, by_id)
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset="olympiad-2022",
        notes=())


def _unpair_group(score, group_pairs, result, paired):
    """Withdraw a group's recorded pairs (reprocessing after new arrivals)."""
    for a_id, b_id in group_pairs.pop(score, []):
        for k in range(len(result) - 1, -1, -1):
            w, b = result[k]
            if {w, b} == {a_id, b_id}:
                del result[k]
                break
        paired.discard(a_id)
        paired.discard(b_id)


def _process_group(gi, order, scores, members_of, med, by_id, stepper,
                   req, paired, result, floats, queue, odd_ids, up_ids,
                   group_pairs) -> List[int]:
    """Pair one matchpoint group. Returns destination group indices that
    received floaters (for reprocessing). Steps: 9.4 played-all floaters,
    8.x odd-floater, designated 8.2.1/8.3.1 pairing, 9.x rest (7.4-aware),
    8.4 re-floater fallback."""
    score, members = order[gi]
    work = [by_id[i] for i in members if i not in paired]
    work += [by_id[i] for i in queue.get(score, []) if i not in paired]
    work = _rank(work)
    is_below = score < med
    is_median = score == med
    routed: List[int] = []

    def dest_gi(from_gi, steps=1):
        di = from_gi + steps
        if 0 <= di < len(order):
            return di
        return None

    def send(pid, to_gi, tag):
        dest = order[to_gi][0]
        queue.setdefault(dest, []).append(pid)
        floats.append((pid, tag))
        if tag == "U":
            up_ids.add(pid)
        else:
            up_ids.discard(pid)
        if to_gi not in routed:
            routed.append(to_gi)

    # 9.4: teams that played all other group members must float (down if
    # above/median, up if below; median-down is the documented default).
    for p in list(work):
        mates = [q for q in work if q.id != p.id]
        if mates and all(q.id in p.opponents for q in mates):
            work.remove(p)
            if is_below:
                di = dest_gi(gi, 1)
                if di is None:
                    raise ImpossiblePairingError(
                        f"9.4-floater {p.id} has no higher group.")
                send(p.id, di, "U")
            else:
                di = dest_gi(gi, 1) if not is_median else _down_gi(
                    gi, order, scores)
                if di is None:
                    raise ImpossiblePairingError(
                        f"9.4-floater {p.id} has no lower group.")
                send(p.id, di, "D")
    # 8.x odd-floater (median-odd falls back to lowest-ranked down).
    while len(work) % 2:
        f, to_gi, tag = _select_floater(
            work, is_below, is_median, by_id, stepper, order, scores, gi,
            queue)
        work.remove(f)
        odd_ids.add(f.id)
        send(f.id, to_gi, tag)
    # designated 8.2.1/8.3.1 pairing for arrived odd-floaters: the
    # up-floater meets the lowest-ranked unplayed team, the down-floater
    # the highest-ranked unplayed team (rank = score desc, number asc).
    taken: Set[int] = set()
    forced: List[Tuple[int, int]] = []
    for pid in list(queue.get(score, [])):
        if pid not in odd_ids or pid not in {p.id for p in work}:
            continue
        f = by_id[pid]
        pool = [p for p in work if p.id not in taken and p.id != pid
                and p.id not in f.opponents]
        if pid in up_ids:
            pool.sort(key=lambda p: (p.score, -p.tpn))
        else:
            pool.sort(key=lambda p: (-p.score, p.tpn))
        if not pool:
            continue  # dest changed since floating: join the 9.x pool
        partner = pool[0]
        taken.add(pid)
        taken.add(partner.id)
        forced.append((pid, partner.id))
    rest = [p for p in work if p.id not in taken]
    res = pair_9x(rest, by_id, stepper, reverse_scrutiny=is_below)
    if res is None:  # 7.4: disregard 7.3 bans if group unpairable
        res = pair_9x(rest, by_id, stepper, ignore_colour_bans=True,
                      reverse_scrutiny=is_below)
    if res is None:  # 8.4: choose another floater and retry once
        extra = _refloater(rest, is_below, by_id, stepper)
        if extra is None:
            raise ImpossiblePairingError(
                f"matchpoint group {score} unpairable (Art.9).")
        rest.remove(extra)
        di = dest_gi(gi, 1)
        if di is None:
            di = _down_gi(gi, order, scores)
        if di is None:
            raise ImpossiblePairingError(
                f"8.4-floater {extra.id} has nowhere to go.")
        send(extra.id, di, "U" if is_below or is_median else "D")
        res = pair_9x(rest, by_id, stepper, reverse_scrutiny=is_below)
        if res is None:
            res = pair_9x(rest, by_id, stepper, ignore_colour_bans=True,
                          reverse_scrutiny=is_below)
        if res is None:
            raise ImpossiblePairingError(
                f"matchpoint group {score} unpairable (Art.9).")
    n_teams = len(by_id)
    for a_id, b_id in forced + res:
        w, b = _assign_board_colour(by_id[a_id], by_id[b_id], req=req,
                                    n_teams=n_teams)
        result.append((w, b))
        paired.add(a_id)
        paired.add(b_id)
    group_pairs[score] = list(forced) + list(res)
    return routed


def _matchpoint_groups(ranked):
    groups = []
    cur = None
    for p in ranked:
        if cur is None or cur[0] != p.score:
            cur = (p.score, [])
            groups.append(cur)
        cur[1].append(p.id)
    return groups


def _down_gi(gi, order, scores):
    """Nearest group index below in score (for median-down floaters)."""
    me = order[gi][0]
    best = None
    for i, (s, _) in enumerate(order):
        if s < me and (best is None or s > order[best][0]):
            best = i
    return best


def _refloater(rest, is_below, by_id, stepper):
    """Art.8.4: another floater whose removal leaves a pairable rest (rank
    order: lowest above, highest below)."""
    cands = list(rest) if is_below else list(reversed(rest))
    for cand in cands:
        sub = [p for p in rest if p.id != cand.id]
        if pair_9x(sub, by_id, stepper,
                   reverse_scrutiny=is_below) is not None:
            return cand
    return None
    groups = []
    cur = None
    for p in ranked:
        if cur is None or cur[0] != p.score:
            cur = (p.score, [])
            groups.append(cur)
        cur[1].append(p.id)
    return groups


def _assign_board_colour(a: P26Player, b: P26Player, *, req: P26Request,
                         n_teams: int) -> Tuple[int, int]:
    """Board-1 colour for a decided pair: Art.7.2 R1 lot pattern when both
    are unplayed in round 1 (#1's lot = initial_colour; odd top-half with
    #1, even against; partner takes the other colour); otherwise the
    Art.7.5–7.6 choice when it respects the 7.3 bans for both teams, else
    the swapped assignment when that one does (7.4 override documented in
    notes by caller)."""
    if req.round_number == 1 and not C.played_colors(a) \
            and not C.played_colors(b):
        half = n_teams // 2
        top = a if a.tpn <= half else (b if b.tpn <= half else None)
        if top is not None:
            other = b if top is a else a
            top_white = (req.initial_colour == "W") == (top.tpn % 2 == 1)
            return (top.id, other.id) if top_white else (other.id, top.id)
    w, bl = board1_colour(a, b, initial_colour=req.initial_colour)
    if _colour_bans_ok(a, w == a.id) and _colour_bans_ok(b, bl == b.id):
        return (w, bl)
    if _colour_bans_ok(a, bl == a.id) and _colour_bans_ok(b, w == b.id):
        return (bl, w)
    return (w, bl)


def _olympiad_board_order(result: List[Tuple[int, int]],
                          by_id: Dict[int, P26Player]) -> List[Tuple[int, int]]:
    """Art.11.1 publication order: matchpoints of the higher-ranked team,
    pair score sum, average rating (Art.3) of the higher-ranked team.
    Unrated teams sort after rated ones; TPN breaks residual ties."""
    def higher(t):
        a, b = by_id[t[0]], by_id[t[1]]
        return (a, b) if (-a.score, a.tpn) <= (-b.score, b.tpn) else (b, a)

    def key(t):
        h, o = higher(t)
        hr = h.rating if h.rating is not None else -1
        return (-h.score, -(h.score + o.score), -hr, h.tpn)

    return sorted(result, key=key)


def _find_dest(cand, order, scores, gi, queue, by_id, is_below, is_median,
               force=False):
    """Destination group index for a floater: adjacent in processing
    direction first (8.2.1/8.3.1), then further groups (8.2.4/8.3.4 repeat);
    reachable = contains a team the candidate has not played (8.2.3/8.3.3).
    Median-odd floats down to the nearest lower score (documented default).
    With force=True the nearest group is returned regardless (caller fails
    typed if pairing proves impossible)."""
    if is_median:
        seq = _down_steps(gi, order)
    else:
        # processing always moves toward the median: gi+1, gi+2, ...
        seq = list(range(gi + 1, len(order)))
    for di in seq:
        pool = _group_teams(di, order, _members_map(order), queue, by_id,
                            set())
        if force or any(p.id not in cand.opponents for p in pool
                        if p.id != cand.id):
            return di
    if force and seq:
        return seq[0]
    return None


def _select_floater(work, is_below, is_median, by_id, stepper, order,
                    scores, gi, queue):
    """Art.8.2/8.3 odd-floater chain. Below-median: highest ranked up
    (8.2.1); above/median: lowest ranked down (8.3.1 + median-down default).
    8.x.2: rest must admit a 9.x pairing (7.4-aware: bans-disregarded also
    counts). 8.x.3: the floater must have an unplayed team in the
    destination group (else moved back, next candidate). 8.x.4: if no
    candidate can play into the adjacent group, skip to further groups
    (repeat until one can). Returns (floater, dest_gi, tag)."""
    cands = list(work) if is_below else list(reversed(work))
    for cand in cands:
        rest = [p for p in work if p.id != cand.id]
        if pair_9x(rest, by_id, stepper,
                   reverse_scrutiny=is_below) is None and pair_9x(
                       rest, by_id, stepper, ignore_colour_bans=True,
                       reverse_scrutiny=is_below) is None:
            continue  # 8.x.2: rest must pair completely
        dest_gi = _find_dest(cand, order, scores, gi, queue, by_id,
                             is_below, is_median)
        if dest_gi is None:
            continue  # 8.x.3: no playable adjacent group for this candidate
        return cand, dest_gi, ("U" if dest_gi < gi else "D")
    # 8.x.4 fallback: no candidate can play adjacent — take the rank-default
    # candidate and skip groups until a playable one (loops inside _find).
    cand = cands[0]
    dest_gi = _find_dest(cand, order, scores, gi, queue, by_id, is_below,
                         is_median, force=True)
    if dest_gi is None:
        raise ImpossiblePairingError(
            "odd Olympiad group has no reachable destination (Art.8).")
    return cand, dest_gi, ("U" if dest_gi < gi else "D")


def _group_teams(dest_gi, order, members_of, queue, by_id, paired):
    """All teams presently attached to a destination group."""
    if dest_gi is None or not 0 <= dest_gi < len(order):
        return []
    score = order[dest_gi][0]
    ids = ([i for i in members_of.get(score, []) if i not in paired]
           + [i for i in queue.get(score, []) if i not in paired])
    seen = set()
    out = []
    for i in sorted(set(ids), key=lambda i: by_id[i].tpn):
        if i not in seen:
            seen.add(i)
            out.append(by_id[i])
    return out


def _members_map(order):
    return {s: list(m) for s, m in order}


def _down_steps(gi, order):
    """Group indices below gi in score (for median-down floaters)."""
    me = order[gi][0]
    cands = [i for i, (s, _) in enumerate(order) if s < me]
    cands.sort(key=lambda i: -order[i][0])
    return cands
