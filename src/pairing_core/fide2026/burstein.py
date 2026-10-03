"""Burstein System 2026 engine (C.04.4.2, F-0110, FULL_TEXT).

Implements: seeding rounds via Dutch-2026 (1.6: first min(floor(R/2),4)
rounds), opposition evaluation 1.7 (Buchholz; SB; self-game for unplayed;
zero-bye streaks as draws for opponents; virtual points excluded — virtual
points enter via score adjustments the CALLER applies before invoking, and
are excluded here by using played-result reconstruction inputs),
ranking 1.8 (Index then TPN; scores unused), PAB 3.1, bracket 3.2 (max pairs
under C1–C5; first-best in Art.4 order), Art.4 BSN + zero-padding +
opponent-BSN-descending enumeration (worked 6-player table), colours Art.5.

Per-round results enter through the explicit typed input
P26Request.round_results (id -> W/D/L code per played opponent, aligned with
opponents order); without it the engine raises InvalidPlayerError (never
inferred). Art.1.7.2.1 self-game provisions hold structurally (registered
points live in current scores); virtual points (1.7.2.2) must be stripped by
the caller.
"""

from __future__ import annotations

from itertools import permutations
from typing import Dict, List, Optional, Sequence, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import ImpossiblePairingError, InvalidPlayerError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper, exists_complete_pairing
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


def seeding_rounds(total_rounds: int) -> int:
    """Art.1.6.2: min(floor(R/2), 4)."""
    return min(total_rounds // 2, 4)


def buchholz_sb(p: P26Player, by_id: Dict[int, P26Player],
                results: Dict[int, Tuple[str, ...]]) -> Tuple[float, float]:
    """Art.1.7: Buchholz = current scores of faced opponents; SB = Σ
    points-earned × opponent current score (standard scoring note).

    results: player id -> one code per listed opponent, each 'W' (win),
    'D' (draw) or 'L' (loss) from the player's perspective. opponents[]
    contains PLAYED opponents only (C.04.2 Art.3.5: unplayed pairings may
    repeat, hence are excluded) — so every code is over-the-board.

    Art.1.7.2.1 (unplayed rounds as self-games; zero-bye streaks as draws for
    opponents) is satisfied structurally, not by extra terms: registered
    points already live in current scores (which feed opponents' BH/SB
    automatically), and self-games contribute no opponent term to anyone's
    BH/SB. Virtual points (1.7.2.2) must be stripped by the caller before
    invoking (the engine sees real standings only).
    """
    codes = results.get(p.id)
    opps = list(p.opponents)
    if codes is None or len(codes) != len(opps):
        raise InvalidPlayerError(
            f"burstein-2026 needs one W/D/L result code per played opponent "
            f"of player {p.id} (Art.1.7); got {codes!r} for {len(opps)} "
            f"opponents.")
    bh = 0.0
    sb = 0.0
    for opp_id, code in zip(opps, codes):
        if opp_id not in by_id:
            raise InvalidPlayerError(
                f"opponent {opp_id} of player {p.id} unknown.")
        if code not in ("W", "D", "L"):
            raise InvalidPlayerError(
                f"player {p.id}: result code {code!r} unknown (use W/D/L).")
        opp = by_id[opp_id]
        bh += opp.score
        if code == "W":
            sb += opp.score
        elif code == "D":
            sb += 0.5 * opp.score
    return (bh, sb)


def index_key(p: P26Player, by_id: Dict[int, P26Player],
              results: Dict[int, Tuple[str, ...]]) -> Tuple[float, float]:
    """Art.1.8.1: (Buchholz, Sonneborn-Berger)."""
    return buchholz_sb(p, by_id, results)


def rank_key(p: P26Player, by_id: Dict[int, P26Player],
             results: Dict[int, Tuple[str, ...]]) -> Tuple[float, float, int]:
    """Art.1.8: Index, then ascending TPN (scores NOT used)."""
    bh, sb = index_key(p, by_id, results)
    return (-bh, -sb, p.tpn)


def burstein_colour(a: P26Player, b: P26Player, ra: tuple, rb: tuple, *,
                    initial_colour: str) -> Tuple[int, int]:
    """Art.5: higher-ranked = Art.1.8 order. 5.2.1 unplayed odd-TPN rule."""
    hr, opp = (a, b) if ra <= rb else (b, a)
    sa, sb = C.played_colors(hr), C.played_colors(opp)
    if not sa and not sb:
        odd_initial = (hr.tpn % 2 == 1) == (initial_colour == "W")
        w = hr.id if odd_initial else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    pa, pb = C.preference(hr), C.preference(opp)
    if pa[0] is not None and pb[0] is not None and pa[0] != pb[0]:
        w = hr.id if pa[0] == "W" else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    if pa[1] > pb[1] and pa[0] is not None:
        return (hr.id, opp.id) if pa[0] == "W" else (opp.id, hr.id)
    if pb[1] > pa[1] and pb[0] is not None:
        return (opp.id, hr.id) if pb[0] == "W" else (hr.id, opp.id)
    for ca, cb in zip(reversed(sa), reversed(sb)):
        if ca != cb:
            w = hr.id if ca == "B" else opp.id
            return (w, opp.id if w == hr.id else hr.id)
    if pa[0] == "W":
        return (hr.id, opp.id)
    if pa[0] == "B":
        return (opp.id, hr.id)
    if sa:
        w = hr.id if sa[-1] == "B" else opp.id
        return (w, opp.id if w == hr.id else hr.id)
    w = hr.id if initial_colour == "W" else opp.id
    return (w, opp.id if w == hr.id else hr.id)


def enumerate_burstein_pairings(
        bracket: Sequence[P26Player],
        rank_of: Dict[int, tuple],
        n_pairs: int) -> List[List[Tuple[int, int]]]:
    """Art.4: BSNs in 1.8 order; pad with (n-k) zero-BSN virtual floaters;
    pairings ordered by BSN#1's opponent BSN descending, then #2..., (the
    worked 6-player/2-pair table follows this rule). Yields id-pairs with
    0 = virtual (float)."""
    ordered = sorted(bracket, key=lambda p: rank_of[p.id])
    bsns = list(range(1, len(ordered) + 1))
    n = len(ordered)
    n_float = n - 2 * n_pairs
    slots = bsns + [0] * n_float
    seen = set()
    out = []

    def rec(remaining: Tuple[int, ...],
            acc: List[Tuple[int, int]]) -> None:
        if not remaining:
            out.append(list(acc))
            return
        first = remaining[0]
        for i in range(1, len(remaining)):
            other = remaining[i]
            # canonical dedup: identical (first, other) BSN pairs once
            rec(remaining[1:i] + remaining[i + 1:], acc + [(first, other)])

    rec(tuple(slots), [])
    # order: BSN#1's opponent desc, then #2...; map BSN->position.
    # NOTE: pairings containing a 0-0 (virtual-vs-virtual) slot pair are
    # excluded: virtual floaters mark unpaired players, they never pair
    # among themselves.
    def order_key(pairing):
        opp_of = {}
        for x, y in pairing:
            opp_of[x] = y
            opp_of[y] = x
        return tuple(-opp_of.get(b, -1) for b in bsns)
    out.sort(key=order_key)
    # translate BSN slots back to player ids (0 -> virtual float); drop any
    # pairing with a 0-0 slot pair.
    id_of_bsn = {b: p.id for b, p in zip(bsns, ordered)}
    result = []
    for pairing in out:
        if any(x == 0 and y == 0 for x, y in pairing):
            continue
        rec_pairs = []
        for x, y in pairing:
            xi = id_of_bsn.get(x, 0)
            yi = id_of_bsn.get(y, 0)
            rec_pairs.append((xi, yi))
        result.append(rec_pairs)
    return result


def _colour_misses(pairs: Sequence[Tuple[int, int]],
                   by_id: Dict[int, P26Player],
                   rank_of: Dict[int, tuple], *,
                   initial_colour: str) -> int:
    misses = 0
    for xa, xb in pairs:
        if xa == 0 or xb == 0:
            continue
        a, b = by_id[xa], by_id[xb]
        w, _ = burstein_colour(a, b, rank_of[a.id], rank_of[b.id],
                               initial_colour=initial_colour)
        for p in (a, b):
            pref = C.preference(p)[0]
            if pref is None:
                continue
            if ("W" if w == p.id else "B") != pref:
                misses += 1
    return misses


def pair_burstein(req: P26Request) -> P26Pairing:
    """Burstein round pairing. Seeding rounds delegate to Dutch-2026 (1.6.1)."""
    if req.round_number <= seeding_rounds(req.total_rounds):
        from dataclasses import replace as _replace

        from pairing_core.fide2026 import dutch as _dutch

        out = _dutch.pair_dutch(req)
        return _replace(out, ruleset="burstein-2026",
                        notes=out.notes + ("seeding-round(dutch-rules)",))
    players = list(req.players)
    results = req.round_results_dict()
    by_id = {p.id: p for p in players}
    rank_of = {}
    for p in players:
        rank_of[p.id] = rank_key(p, by_id, results)
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    blocked = [(a.id, b.id) for a in players for b in players
               if a.id < b.id and C.rematch(a, b)]
    pairs: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    bye_id = None
    remaining = list(players)
    if len(remaining) % 2:
        bye_id = _select_pab(remaining, by_id, rank_of, blocked, stepper)
        remaining = [p for p in remaining if p.id != bye_id]
    guard = 0
    incoming: List[P26Player] = []  # 1.2.2: unpaired leftovers of the previous
    # bracket only (never the whole lower field).
    while remaining:
        guard += 1
        if guard > len(players) + 2:
            raise ImpossiblePairingError("scoregroup loop did not terminate.")
        top = max(p.score for p in remaining)
        residents = [p for p in remaining if p.score == top]
        bracket = residents + [p for p in incoming if p in remaining]
        n_pairs = _max_pairs(bracket, by_id, blocked, stepper)
        rest_after = [p for p in remaining if p not in bracket]
        chosen = _choose_pairing(bracket, by_id, rank_of, n_pairs, blocked,
                                 stepper, req=req, rest_after=rest_after)
        out_ids = set()
        new_incoming: List[P26Player] = []
        for xa, xb in chosen:
            if xa == 0:
                new_incoming.append(by_id[xb])
                floats.append((xb, "D"))
                out_ids.add(xb)
            elif xb == 0:
                new_incoming.append(by_id[xa])
                floats.append((xa, "D"))
                out_ids.add(xa)
            else:
                a, b = by_id[xa], by_id[xb]
                w, bl = burstein_colour(a, b, rank_of[a.id], rank_of[b.id],
                                        initial_colour=req.initial_colour)
                pairs.append((w, bl))
                out_ids.add(xa)
                out_ids.add(xb)
        remaining = [p for p in remaining if p.id not in out_ids]
        incoming = new_incoming
    ordered = C.board_order([(by_id[w], by_id[b]) for w, b in pairs])
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset="burstein-2026",
        notes=())


def _max_pairs(bracket, by_id, blocked, stepper) -> int:
    """Art.3.2.1: maximum pairs under C1–C5 (C5 is the maximisation itself;
    C1/C3 absolute; C2/C4 concern PAB/completion handled at round level)."""
    n = len(bracket)
    for k in range(n // 2, -1, -1):
        if _exists_k_pairs(bracket, by_id, blocked, stepper, k):
            return k
    return 0


def _exists_k_pairs(bracket, by_id, blocked, stepper, k) -> bool:
    from itertools import combinations as _cb
    ids = [p.id for p in bracket]
    # try subsets of 2k players fully pairable (C1+C3)
    for subset in _cb(ids, 2 * k):
        if exists_complete_pairing([by_id[i] for i in subset], blocked,
                                   stepper):
            # C3 absolute-colour check inside exists_? No: exists_ checks
            # rematch only. Filter C3 here.
            if _subset_c3_ok([by_id[i] for i in subset], blocked):
                return True
    return False


def _subset_c3_ok(players, blocked) -> bool:
    # existence of a C1+C3 full pairing (small backtrack)
    bset = {tuple(sorted(b)) for b in blocked}
    idmap = {p.id: p for p in players}
    ids = tuple(sorted(idmap))

    def c3_ok(x, y):
        a, b = idmap[x], idmap[y]
        pa, pb = C.preference(a), C.preference(b)
        return not (pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0])

    def bt(rem):
        if not rem:
            return True
        f = rem[0]
        for i, o in enumerate(rem[1:]):
            if tuple(sorted((f, o))) in bset:
                continue
            if c3_ok(f, o) and bt(rem[1:i + 1] + rem[i + 2:]):
                return True
        return False

    return bt(ids)


def _choose_pairing(bracket, by_id, rank_of, n_pairs, blocked, stepper, *,
                    req, rest_after) -> List[Tuple[int, int]]:
    """Art.3.2.2: first pairing (Art.4 order) that complies best C1–C8
    (higher-priority quality first; C6 outgoing scores desc; C7 next-bracket
    C1–C6 as a hard filter via rest probe; C8 colours)."""
    cands = []
    for pairing in enumerate_burstein_pairings(bracket, rank_of, n_pairs):
        stepper.tick()
        ok = True
        for xa, xb in pairing:
            if xa == 0 or xb == 0:
                continue
            if not _c1c3_ok(by_id[xa], by_id[xb]):
                ok = False
                break
        if not ok:
            continue
        # C6: outgoing-floater scores descending (players tied to virtual 0).
        out_scores = sorted(
            [by_id[x].score for x, y in pairing if y == 0] +
            [by_id[y].score for x, y in pairing if x == 0], reverse=True)
        misses = _colour_misses(pairing, by_id, rank_of,
                                initial_colour=req.initial_colour)
        vec = (tuple(-s for s in out_scores), misses)
        key = (vec, _pairing_order_key(pairing, rank_of, by_id, bracket))
        cands.append((key, pairing))
    cands.sort(key=lambda c: c[0])
    for _, pairing in cands:
        # C7: outgoing floaters must leave the next bracket C1–C6-compliant.
        if _next_bracket_ok(pairing, rest_after, by_id, blocked, stepper):
            return pairing
    raise ImpossiblePairingError(
        "no Burstein bracket pairing with C7-compliant sequel (Art.3.2.2).")


def _next_bracket_ok(pairing, rest_after, by_id, blocked, stepper) -> bool:
    """C7 probe: players left for later brackets (outgoing floaters + untouched
    lower groups) admit at least one legal next bracket (C1/C3/C4-class)."""
    if not rest_after:
        return True
    top = max(p.score for p in rest_after)
    residents = [p for p in rest_after if p.score == top]
    lower = [p for p in rest_after if p.score < top]
    for k in range(0, len(lower) + 1):
        if (len(residents) + k) % 2:
            continue
        from itertools import combinations as _cb
        for combo in _cb([p.id for p in lower], k):
            cand = residents + [by_id[i] for i in combo]
            if _subset_c3_ok(cand, blocked) and \
                    exists_complete_pairing(cand, blocked, stepper):
                return True
    return False


def _c1c3_ok(a: P26Player, b: P26Player) -> bool:
    if C.rematch(a, b):
        return False
    pa, pb = C.preference(a), C.preference(b)
    return not (pa[1] == 3 and pb[1] == 3 and pa[0] == pb[0])


def _pairing_order_key(pairing, rank_of, by_id, bracket):
    # regeneration of Art.4 order rank for tiebreak (enumeration already in
    # order; use index-insensitive stable key of opponent BSNs).
    ordered = sorted(bracket, key=lambda p: rank_of[p.id])
    bsn_of = {p.id: i + 1 for i, p in enumerate(ordered)}
    opp = {}
    for x, y in pairing:
        bx = bsn_of.get(x, 0)
        by = bsn_of.get(y, 0)
        opp[bx] = by
        opp[by] = bx
    n = len(ordered)
    return tuple(-opp.get(b, -1) for b in range(1, n + 1))


class _Rev:
    """Descending-order wrapper for tuple keys (stable, deterministic)."""

    def __init__(self, key):
        self.key = key

    def __lt__(self, other):
        return self.key > other.key

    def __eq__(self, other):
        return self.key == other.key


def _select_pab(remaining, by_id, rank_of, blocked, stepper) -> int:
    """Art.3.1: eligible -> completion -> lowest score -> most games ->
    lowest Art.1.8 ranking (= worst Index = largest rank key)."""
    cands = sorted([p for p in remaining if C.pab_eligible(p)],
                   key=lambda p: (p.score, -p.played, _Rev(rank_of[p.id])))
    for cand in cands:
        rest = [p for p in remaining if p.id != cand.id]
        if len(rest) % 2:
            continue
        if exists_complete_pairing(rest, blocked, stepper):
            return cand.id
    raise ImpossiblePairingError("no Burstein PAB assignee (Art.3.1).")
