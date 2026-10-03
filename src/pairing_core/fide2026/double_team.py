"""Double Swiss 2026 (C.04.5) + Team Swiss 2026 (C.04.6) engines.

Shared machinery (PAB Art.3.4, upfloater sets Art.3.5 with worked lexicographic
example, bracket identifiers Art.3.6 with worked example). Differences: colour
model (Double Art.4 HRP chain vs Team Art.4 first-team chain), preferences
(Double: none; Team: Type A/B/none), quality sets (Team C8/C9/C10; Double C7/C8;
Team C7/C10 skip the last TWO rounds, Double C7/C8 only the last).

Selection semantics (documented reading, applied uniformly): generation order
(Art.3.5.4 / Art.3.6.3) defines priority; among generated candidates the one
with the minimal quality-violation vector wins; ties break to the earlier
generated candidate. This generalises Dutch Art.3.8 ("better ... or generated
earlier") to the Double/Team "first ... that complies" phrasing, and coincides
with it whenever a zero-violation candidate exists. C6 (next-bracket
compliance) is a hard filter on upfloater sets, per Art.3.5.5.

All section refs verified FULL_TEXT from the Council bundle.
"""

from __future__ import annotations

from itertools import combinations
from typing import Dict, List, Sequence, Tuple

from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import ImpossiblePairingError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.common import Stepper, exists_complete_pairing
from pairing_core.fide2026.models import P26Pair, P26Pairing, P26Player, P26Request


# ---------------------------------------------------------------- PAB

def select_pab(players: Sequence[P26Player], blocked: Sequence[Tuple[int, int]],
               stepper: Stepper) -> P26Player:
    """Art.3.4 (both): completion-leaving (legal = C1+C2, Art.3.1.1) ->
    lowest score -> most matches played -> largest TPN."""
    cands = sorted([p for p in players if C.pab_eligible(p)],
                   key=lambda p: (p.score, -p.played, -p.tpn))
    for cand in cands:
        rest = [p for p in players if p.id != cand.id]
        if len(rest) % 2:
            continue
        if exists_complete_pairing(rest, blocked, stepper):
            return cand
    raise ImpossiblePairingError(
        "no PAB assignee leaves a legal pairing (Art.3.4.1).")


# ------------------------------------------------------- upfloater sets

def _inner_key(ids: Tuple[int, ...], by_id: Dict[int, P26Player]) -> Tuple[int, ...]:
    """Art.3.5.3: members sorted by descending score, then ascending TPN."""
    members = sorted((by_id[i] for i in ids),
                     key=lambda p: (-p.score, p.tpn))
    return tuple(p.tpn for p in members)


def _score_profile(ids: Tuple[int, ...],
                   by_id: Dict[int, P26Player]) -> Tuple[float, ...]:
    return tuple(sorted((by_id[i].score for i in ids), reverse=True))


def _rest_next_bracket_ok(remaining: Sequence[P26Player],
                          used_ids: Sequence[int],
                          by_id: Dict[int, P26Player],
                          blocked: Sequence[Tuple[int, int]],
                          stepper: Stepper) -> bool:
    """C6-class probe: after removing the bracket, the next top-scoregroup
    admits at least one legal bracket (Art.3.5.5 / 2.3.3)."""
    rest = [p for p in remaining if p.id not in set(used_ids)]
    if not rest:
        return True
    top = max(p.score for p in rest)
    residents = [p for p in rest if p.score == top]
    lower = [p for p in rest if p.score < top]
    for k in range(0, len(lower) + 1):
        if (len(residents) + k) % 2:
            continue
        for combo in combinations([p.id for p in lower], k):
            cand = residents + [by_id[i] for i in combo]
            if exists_complete_pairing(cand, blocked, stepper):
                return True
    return False


def select_upfloaters(residents: Sequence[P26Player],
                      lower: Sequence[P26Player],
                      remaining: Sequence[P26Player],
                      by_id: Dict[int, P26Player],
                      blocked: Sequence[Tuple[int, int]],
                      stepper: Stepper, *,
                      count_repeat: bool) -> List[P26Player]:
    """Art.3.5: minimum-k sets with C5-maximal score profile first; within a
    profile, lexicographic TPN order (worked example); C6 hard filter; C7
    (previous-round floaters among upfloaters) minimised, ties -> earlier set.
    count_repeat=False skips C7 (last round(s))."""
    pool_ids = [p.id for p in lower]
    best: Optional[Tuple[int, Tuple[int, ...], List[P26Player]]] = None
    for k in range(0, len(pool_ids) + 1):
        if (len(residents) + k) % 2:
            continue
        combos = list(combinations(pool_ids, k))
        # C5: highest score profile first
        profiles: Dict[Tuple[float, ...], List[Tuple[int, ...]]] = {}
        for combo in combos:
            profiles.setdefault(_score_profile(combo, by_id), []).append(combo)
        for profile in sorted(profiles, reverse=True):
            ordered = sorted(profiles[profile],
                             key=lambda c: _inner_key(c, by_id))
            for combo in ordered:
                stepper.tick()
                ups = [by_id[i] for i in combo]
                bracket = list(residents) + ups
                if not exists_complete_pairing(bracket, blocked, stepper):
                    continue
                used = [p.id for p in bracket]
                if not _rest_next_bracket_ok(remaining, used, by_id,
                                             blocked, stepper):
                    continue  # C6 filter
                rep = sum(1 for u in ups if u.last_float in ("D", "U"))
                key = (k, (rep if count_repeat else 0),
                       _inner_key(combo, by_id))
                if best is None or key < best[0]:
                    best = (key, _inner_key(combo, by_id), ups)
            if best is not None and best[0][0] == k:
                break
        if best is not None:
            break
    if best is None:
        raise ImpossiblePairingError(
            "no upfloater set yields a C6-compliant bracket (Art.3.5).")
    return best[2]


# ---------------------------------------------------------- identifiers

def enumerate_pairings(bracket: Sequence[P26Player]) -> List[List[Tuple[int, int]]]:
    """Art.3.6.1-3.6.3: (smaller-TPN top, larger-TPN bottom); identifier =
    top TPNs ascending + corresponding bottom TPNs; lexicographic
    (worked `4 6 9 11 8 16 10 24` example)."""
    order = sorted(bracket, key=lambda p: p.tpn)
    out: List[List[Tuple[int, int]]] = []

    def rec(remaining: Tuple[P26Player, ...],
            acc: List[Tuple[int, int]]) -> None:
        if not remaining:
            out.append(sorted(acc, key=lambda pr: pr[0]))
            return
        first = remaining[0]
        for i in range(1, len(remaining)):
            other = remaining[i]
            top, bottom = (first.tpn, other.tpn) \
                if first.tpn < other.tpn else (other.tpn, first.tpn)
            rec(remaining[1:i] + remaining[i + 1:], acc + [(top, bottom)])

    rec(tuple(order), [])
    out.sort(key=lambda pairs: (tuple(t for t, _ in pairs),
                                tuple(b for _, b in pairs)))
    return out


# --------------------------------------------------------------- colours

def double_colour(a: P26Player, b: P26Player, *,
                  initial_colour: str) -> Tuple[int, int]:
    """C.04.5 Art.4: HRP = higher score else smaller TPN. Returns (white, black)."""
    hrp, opp = (a, b) if (a.score, -a.tpn) >= (b.score, -b.tpn) else (b, a)
    sa, sb = C.played_colors(hrp), C.played_colors(opp)
    if not sa and not sb:  # 4.3.1 odd-HRP initial-colour else opposite
        odd_initial = (hrp.tpn % 2 == 1) == (initial_colour == "W")
        w = hrp.id if odd_initial else opp.id
        return (w, opp.id if w == hrp.id else hrp.id)
    na, nb = sa.count("W"), sb.count("W")
    if na != nb:  # 4.3.2 fewer Whites gets White
        w = hrp.id if na < nb else opp.id
        return (w, opp.id if w == hrp.id else hrp.id)
    for ca, cb in zip(reversed(sa), reversed(sb)):  # 4.3.3
        if ca != cb:
            w = hrp.id if ca == "B" else opp.id
            return (w, opp.id if w == hrp.id else hrp.id)
    if sa:  # 4.3.4 alternate HRP
        w = hrp.id if sa[-1] == "B" else opp.id
        return (w, opp.id if w == hrp.id else hrp.id)
    if sb:  # 4.3.5 alternate opponent
        w = opp.id if sb[-1] == "B" else hrp.id
        return (w, opp.id if w == hrp.id else hrp.id)
    w = hrp.id if initial_colour == "W" else opp.id
    return (w, opp.id if w == hrp.id else hrp.id)


def team_colour(a: P26Player, b: P26Player, *, initial_colour: str,
                kind: str, is_last_round: bool) -> Tuple[int, int]:
    """C.04.6 Art.4. first-team = higher primary -> secondary (unless kind
    'none', when secondary is dropped entirely) -> smaller TPN."""
    if kind == "none":
        ka = (a.score, -a.tpn)
        kb = (b.score, -b.tpn)
    else:
        ka = (a.score, a.secondary, -a.tpn)
        kb = (b.score, b.secondary, -b.tpn)
    first, other = (a, b) if ka >= kb else (b, a)
    sf, so = C.played_colors(first), C.played_colors(other)
    if not sf and not so:  # 4.3.1
        odd_initial = (first.tpn % 2 == 1) == (initial_colour == "W")
        w = first.id if odd_initial else other.id
        return (w, other.id if w == first.id else first.id)

    def pref(p: P26Player):
        return C.team_preference(p, kind=kind, is_last_round=is_last_round)

    if kind != "none":
        pf, po = pref(first)[0], pref(other)[0]
        if (pf is not None) != (po is not None):  # 4.3.2 sole preference
            holder = first if pf is not None else other
            hcol = pf if holder is first else po
            w = holder.id if hcol == "W" else (
                other.id if holder is first else first.id)
            return (w, other.id if w == first.id else first.id)
        if pf is not None and po is not None and pf != po:  # 4.3.3 opposite
            w = first.id if pf == "W" else other.id
            return (w, other.id if w == first.id else first.id)
        if kind == "B":  # 4.3.4 sole strong
            sf_s, so_s = pref(first), pref(other)
            if (sf_s[1] == 2) != (so_s[1] == 2):
                holder = first if sf_s[1] == 2 else other
                hcol = sf_s[0] if holder is first else so_s[0]
                w = holder.id if hcol == "W" else (
                    other.id if holder is first else first.id)
                return (w, other.id if w == first.id else first.id)
    cdf, cdo = C.colour_difference(first), C.colour_difference(other)
    if cdf != cdo:  # 4.3.5 lower CD gets White
        w = first.id if cdf < cdo else other.id
        return (w, other.id if w == first.id else first.id)
    for cf, co in zip(reversed(sf), reversed(so)):  # 4.3.6
        if cf != co:
            w = first.id if cf == "B" else other.id
            return (w, other.id if w == first.id else first.id)
    if sf:  # 4.3.8 first-team alternation
        w = first.id if sf[-1] == "B" else other.id
        return (w, other.id if w == first.id else first.id)
    if so:  # 4.3.9 other-team alternation
        w = other.id if so[-1] == "B" else first.id
        return (w, other.id if w == first.id else first.id)
    w = first.id if initial_colour == "W" else other.id
    return (w, other.id if w == first.id else first.id)


# ----------------------------------------------------------------- engine

def _granted_colour(a: P26Player, b: P26Player, *, system: str, kind: str,
                    initial_colour: str,
                    is_last_round: bool) -> Tuple[int, int]:
    if system == "team":
        return team_colour(a, b, initial_colour=initial_colour, kind=kind,
                           is_last_round=is_last_round)
    return double_colour(a, b, initial_colour=initial_colour)


def _violation_vector(rec: Sequence[Tuple[int, int]], by_id: Dict[int, P26Player],
                      *, system: str, kind: str, initial_colour: str,
                      is_last_round: bool, up_ids: frozenset,
                      count_opp_repeat: bool) -> Tuple[int, ...]:
    """Quality-violation vector (lower wins): team -> (ungranted prefs,
    ungranted strong [B only], upfloat-opponents floated); double ->
    (upfloat-opponents floated,). up_ids = chosen upfloaters of this bracket.
    """
    ungranted = 0
    strong = 0
    opp_float = 0
    for xa, xb in rec:
        a, b = by_id[xa], by_id[xb]
        w, _ = _granted_colour(a, b, system=system, kind=kind,
                               initial_colour=initial_colour,
                               is_last_round=is_last_round)
        if system == "team" and kind != "none":
            for p, _ in ((a, b), (b, a)):
                pr = C.team_preference(p, kind=kind,
                                       is_last_round=is_last_round)
                if pr[0] is None:
                    continue
                has = "W" if w == p.id else "B"
                if has != pr[0]:
                    ungranted += 1
                    if pr[1] == 2:
                        strong += 1
        # C8/C10-class: the upfloater's opponent floated previous round.
        u, o = (a, b) if a.id in up_ids else ((b, a) if b.id in up_ids else (None, None))
        if count_opp_repeat and u is not None and o.last_float in ("D", "U"):
            opp_float += 1
    if system == "team":
        return (ungranted, strong if kind == "B" else 0, opp_float)
    return (opp_float,)


def pair_double_or_team(req: P26Request, *, system: str) -> P26Pairing:
    """Shared top-down engine (Double/Team Art.3.3): PAB, then top-scoregroup
    + upfloaters, repeat; colours Art.4 (step 4)."""
    is_team = system == "team"
    kind = "A"
    if is_team and req.ruleset.team_colour_type in ("A", "B", "none"):
        kind = req.ruleset.team_colour_type
    count_repeat = not req.is_last_round and not (
        is_team and req.round_number >= req.total_rounds - 1)
    stepper = Stepper(ExecutionBudgets(max_steps=req.max_steps,
                                      wall_clock_seconds=req.wall_clock_seconds))
    players = list(req.players)
    by_id = {p.id: p for p in players}
    by_tpn = {p.tpn: p for p in players}
    blocked = [(a.id, b.id) for a in players for b in players
               if a.id < b.id and C.rematch(a, b)]
    pairs: List[Tuple[int, int]] = []
    floats: List[Tuple[int, str]] = []
    bye_id = None
    remaining = list(players)
    if len(remaining) % 2:
        pab = select_pab(remaining, blocked, stepper)
        bye_id = pab.id
        floats.append((pab.id, "D"))
        remaining = [p for p in remaining if p.id != pab.id]
    guard = 0
    while remaining:
        guard += 1
        if guard > len(players) + 2:
            raise ImpossiblePairingError("bracket loop did not terminate.")
        top_score = max(p.score for p in remaining)
        residents = sorted([p for p in remaining if p.score == top_score],
                           key=lambda p: p.tpn)
        lower = sorted([p for p in remaining if p.score < top_score],
                       key=lambda p: (-p.score, p.tpn))
        ups = select_upfloaters(residents, lower, remaining, by_id, blocked,
                                stepper, count_repeat=count_repeat)
        bracket = residents + ups
        for u in ups:
            floats.append((u.id, "U"))
        chosen = _choose_bracket_pairing(
            bracket, by_id, by_tpn, blocked, stepper, system=system, kind=kind,
            initial_colour=req.initial_colour,
            is_last_round=req.is_last_round, up_ids=frozenset(u.id for u in ups),
            count_opp_repeat=count_repeat)
        for ta, tb in chosen:
            a, b = by_tpn[ta], by_tpn[tb]
            w, bl = _granted_colour(a, b, system=system, kind=kind,
                                    initial_colour=req.initial_colour,
                                    is_last_round=req.is_last_round)
            pairs.append((by_id[w].id, by_id[bl].id))
        used_tpns = {t for pr in chosen for t in pr}
        remaining = [p for p in remaining if p.tpn not in used_tpns]
    ordered = C.board_order([(by_id[w], by_id[b]) for w, b in pairs])
    label = "team-2026" if is_team else "double-2026"
    notes = (("team-colour-type:" + kind,) if is_team else ())
    return P26Pairing(
        pairs=tuple(P26Pair(white_id=w, black_id=b) for w, b in ordered),
        bye_id=bye_id, floats=tuple(floats), ruleset=label, notes=notes)


def _choose_bracket_pairing(bracket, by_id, by_tpn, blocked, stepper, *,
                            system, kind, initial_colour, is_last_round,
                            up_ids, count_opp_repeat):
    """Art.3.6.4: minimal violation vector; ties -> earlier identifier
    (enumeration is already in identifier order: strictly-smaller wins)."""
    best_vec = None
    best_rec = None
    for ident_pairs in enumerate_pairings(bracket):
        stepper.tick()
        rec = []
        ok = True
        for t_top, t_bot in ident_pairs:
            a, b = by_tpn[t_top], by_tpn[t_bot]
            if C.rematch(a, b):
                ok = False
                break
            rec.append((a.id, b.id))
        if not ok:
            continue
        vec = _violation_vector(rec, by_id, system=system, kind=kind,
                                initial_colour=initial_colour,
                                is_last_round=is_last_round, up_ids=up_ids,
                                count_opp_repeat=count_opp_repeat)
        if best_vec is None or vec < best_vec:
            best_vec, best_rec = vec, rec
    if best_rec is None:
        raise ImpossiblePairingError(
            "no legal bracket pairing in identifier order (Art.3.6.4).")
    return best_rec
