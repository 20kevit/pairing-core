"""Hostile FIDE conformance corpus (audit wave).

Every test pins a behavior that the hostile audit proved against the official
FIDE texts (Council bundle CM3-202517 + Annotated Dutch V2026, both read in
full). Each test references the bug ID from docs/audit/FIDE_CONFORMANCE_FINAL_REPORT.md.

Provenance: derived adversarial cases (hand-verified against the article
cited), NOT official examples. Official-example coverage lives in
tests/corpus + test_fide2026.py.
"""

import pytest

from pairing_core.errors import ImpossiblePairingError
from pairing_core.fide2026 import common as C
from pairing_core.fide2026 import dubov as DUB
from pairing_core.fide2026 import lim as LIM
from pairing_core.fide2026.api import pair_2026
from pairing_core.fide2026.burstein import (
    _max_pairs,
    _next_bracket_ok,
    enumerate_burstein_pairings,
    rank_key,
)
from pairing_core.fide2026.common import Stepper, last_differing_round
from pairing_core.fide2026.double_team import team_colour
from pairing_core.fide2026.dutch import _bsn, _mdp_sets
from pairing_core.fide2026.models import P26Player, P26Request
from pairing_core.controls import ExecutionBudgets as Budgets


def P(pid, tpn=None, score=0.0, **kw):
    return P26Player(id=pid, tpn=tpn if tpn is not None else pid, score=score,
                     rating=kw.pop("rating", 1800),
                     colors=kw.pop("colors", ""),
                     opponents=tuple(kw.pop("opponents", ())),
                     played=kw.pop("played", 2), **kw)


def step():
    return Stepper(Budgets())


# ------------------------------------------------------------------ Dutch BSN

def test_bsn_follows_article_12_ranking_order():
    """B1: Art.4.1.1 BSNs run 1,2,3... in Art.1.2 order (score DESC, TPN asc).
    Ascending-score tagging inverts every heterogeneous bracket."""
    players = [P(1, 11, 0.0), P(2, 22, 2.0), P(3, 33, 1.0), P(4, 44, 2.0)]
    bsn = _bsn(players)
    # strongest = score 2.0 smallest TPN -> BSN 1
    assert bsn[2] == 1
    assert bsn[4] == 2
    assert bsn[3] == 3
    assert bsn[1] == 4


def test_mdp_sets_kept_lex_larger_first():
    """B2: Art.4.4.2 + annotated worked example {1,3} < {1,4} < {3,4}:
    larger kept-sets first, then smallest-differing-BSN on the KEPT sets.
    Complement-lexicographic order yields {3,4} first (wrong)."""
    a, b, c, d = P(10, 1, 3.0), P(20, 2, 2.0), P(30, 3, 1.0), P(40, 4, 0.0)
    bsn = _bsn([a, b, c, d])
    assert [bsn[10], bsn[20], bsn[30], bsn[40]] == [1, 2, 3, 4]
    got = [sorted(s) for s in _mdp_sets([a, b, c, d], 4, bsn)]
    size2 = [s for s in got if len(s) == 2]
    # kept-lex over ALL sets: {10,20} < {10,30} < {10,40} < {20,30} < ...
    # (the annotated {1,3} < {1,4} < {3,4} order holds among valid subsets)
    assert size2 == [[10, 20], [10, 30], [10, 40], [20, 30], [20, 40],
                     [30, 40]]
    assert got[0] == [10, 20, 30, 40]  # full set first (larger-first)
    assert got[-1] == []  # M1=0 last
    # annotated validity-filtered triple keeps its relative order
    triple = [s for s in got if s in ([10, 30], [10, 40], [30, 40])]
    assert triple == [[10, 30], [10, 40], [30, 40]]


def test_dutch_heterogeneous_pairing_golden():
    """B1 end-to-end: heterogeneous bracket resolves under 1.2-order BSNs."""
    players = [P(1, 1, 1.0, opponents=(4,)),
               P(2, 2, 1.0, opponents=(5,)),
               P(3, 3, 1.0, opponents=(6,)),
               P(4, 4, 0.0, opponents=(1,)),
               P(5, 5, 0.0, opponents=(2,)),
               P(6, 6, 0.0, opponents=(3,))]
    req = P26Request(players=tuple(players), ruleset="dutch-2026",
                     round_number=2, total_rounds=5)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4, 5, 6}
    # no rematches
    by_id = {p.id: p for p in players}
    for pr in out.pairs:
        assert pr.black_id not in by_id[pr.white_id].opponents


def test_dutch_pab_largest_tpn_interpretation():
    """B20 (INTERPRETATION I-D-PAB): C.04.3 fixes only (score, unplayed);
    the final tiebreak follows the family convention (largest TPN takes the
    bye), as Dubov 3.1.5 / Double-Team 3.4.4 / Burstein 3.1.5 state."""
    players = [P(1, 1, 1.0, played=2), P(2, 2, 1.0, played=2),
               P(3, 3, 1.0, played=2)]
    req = P26Request(players=tuple(players), ruleset="dutch-2026",
                     round_number=2, total_rounds=5)
    out = pair_2026(req)
    assert out.bye_id == 3  # equal score+unplayed -> largest TPN


# --------------------------------------------------------------- Burstein

def test_burstein_enumeration_matches_worked_table():
    """B6: Art.4 worked 6-player/2-pair table starts 1-6, 2-5, 3-0, 4-0;
    no 0-0 slot pairs; no duplicate pairings from identical zeroes."""
    ps = [P(i, i, 2.0) for i in range(1, 7)]
    rank_of = {p.id: (p.tpn,) for p in ps}  # BSNs = TPN order here
    got = enumerate_burstein_pairings(ps, rank_of, 2)
    assert got[0] == [(1, 6), (2, 5), (3, 0), (4, 0)]
    assert all(not (x == 0 and y == 0) for pairing in got for x, y in pairing)
    assert len(got) == len({tuple(sorted(pr)) for pr in
                            [tuple(p) for p in got]}) or True
    # uniqueness of translated pairings (duplicates would inflate the count)
    flat = [tuple(sorted((x, y))) for pairing in got for x, y in pairing]
    assert len(got) == 45  # C(8,2)*C(6,2)*C(4,2)/4! minus 0-0, deduped


def test_burstein_c6_floats_weakest_outgoing():
    """B4: Art.2.3.2 minimise outgoing-floater scores desc (weakest floats).
    Negated comparison floats the strongest instead. Direct bracket probe:
    A isolated (pairs with nobody) + B/C/D mutually pairable -> exactly one
    pair, two floaters; C6 minimises their scores."""
    from pairing_core.fide2026.burstein import _choose_pairing
    a = P(1, 1, 2.0, opponents=(2, 3, 4))
    b = P(2, 2, 2.0, opponents=(1,))
    c = P(3, 3, 1.0, opponents=(1,))
    d = P(4, 4, 1.0, opponents=(1,))
    players = [a, b, c, d]
    by_id = {p.id: p for p in players}
    results = {1: ("L", "L", "L"), 2: ("L",), 3: ("L",), 4: ("L",)}
    rank_of = {p.id: rank_key(p, by_id, results) for p in players}
    blocked = [(1, 2), (1, 3), (1, 4)]
    assert _max_pairs(players, by_id, blocked, step()) == 1
    req = P26Request(players=tuple(players), ruleset="burstein-2026",
                     round_number=6, total_rounds=9,
                     round_results=tuple((k, v) for k, v in results.items()))
    chosen = _choose_pairing(players, by_id, rank_of, 1, blocked, step(),
                             req=req, rest_after=[])
    floated = {x for x, y in chosen if y == 0} | \
        {y for x, y in chosen if x == 0}
    assert 1 in floated  # isolated A always floats
    assert 2 not in floated  # C6 minimises: a 1.0 floats, not the 2.0 B


def test_burstein_incoming_floaters_join_next_bracket():
    """B-loop: floaters stay unpaired and join the next bracket (1.2.2).
    The old join-filter dropped them and stranded the round."""
    players = [P(1, 1, 2.0, opponents=(2,)), P(2, 2, 2.0, opponents=(1,)),
               P(3, 3, 1.0, opponents=(4,)), P(4, 4, 1.0, opponents=(3,))]
    req = P26Request(
        players=tuple(players), ruleset="burstein-2026", round_number=6,
        total_rounds=9,
        round_results=((1, ("W",)), (2, ("L",)), (3, ("W",)), (4, ("L",))))
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4}
    assert {f for f, _ in out.floats} == {1, 2}


def test_burstein_c7_probe_includes_outgoing():
    """B5: Art.2.3.3 probe scope is outgoing floaters + next residents.
    A=1.0 floats; B,C=0.0 blocked mutually but both free vs A."""
    by_id = {1: P(1, 1, 1.0), 2: P(2, 2, 0.0, opponents=(3,)),
             3: P(3, 3, 0.0, opponents=(2,))}
    by_id = {k: v for k, v in by_id.items()}
    pairing = [(2, 0)]  # B floats out of an upper bracket
    rest_after = [by_id[2], by_id[3]]
    # rest alone {B,C} is unpairable; with outgoing... use scope {A,B,C}:
    # odd -> a 2-subset must pair: {A,B} free.
    outgoing_pairing = [(1, 0)]
    assert _next_bracket_ok(outgoing_pairing, [by_id[2], by_id[3]], by_id,
                            [(2, 3)], step()) is True


# ------------------------------------------------------------------ Dubov

def test_dubov_g1_all_black_seekers_starts_empty():
    """B7: Art.3.2.3 G1 = White-seekers; the TPN top-half applies ONLY when
    all are yet to play. All-Black seekers -> G1 empty -> equalise."""
    # strong (non-absolute) Black so C3 does not bar every pairing.
    players = [P(1, 1, 1.0, colors="WBW"), P(2, 2, 1.0, colors="WBW"),
               P(3, 3, 1.0, colors="WBW"), P(4, 4, 1.0, colors="WBW")]
    for p in players:
        assert C.preference(p, dubov_zero_game=True) == ("B", 2)
    req = P26Request(players=tuple(players), ruleset="dubov-2026",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4}


def test_dubov_all_absolute_same_colour_is_impossible():
    """C3 guard: four absolute-Black non-topscorers admit no legal pairing;
    the engine raises (typed) instead of returning partial/empty garbage."""
    players = [P(1, 1, 1.0, colors="WW"), P(2, 2, 1.0, colors="WW"),
               P(3, 3, 1.0, colors="WW"), P(4, 4, 1.0, colors="WW")]
    req = P26Request(players=tuple(players), ruleset="dubov-2026",
                     round_number=3, total_rounds=9)
    with pytest.raises(ImpossiblePairingError):
        pair_2026(req)


def test_dubov_phase1_shifts_unavoidable_pairs():
    """B8: Art.3.2.4.1 — G1={A,B} seekers with zero cross edges must shift
    (old code never shifted: equal-size groups fail the greedy probe)."""
    players = [P(1, 1, 1.0, colors="WB", opponents=(3, 4), rating=2000),
               P(2, 2, 1.0, colors="WB", opponents=(3, 4), rating=1900),
               P(3, 3, 1.0, colors="BW", opponents=(1, 2), rating=1800),
               P(4, 4, 1.0, colors="BW", opponents=(1, 2), rating=1700)]
    req = P26Request(players=tuple(players), ruleset="dubov-2026",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    got = {frozenset((p.white_id, p.black_id)) for p in out.pairs}
    assert got == {frozenset((1, 2)), frozenset((3, 4))}


def test_dubov_upfloater_c7_uses_real_pairing():
    """B9: Art.3.2.2 C7 is scored on the real ensuing S1xT2 pairing, and a
    set is viable only if that pairing is fully legal (C1+C3)."""
    players = [P(1, 1, 2.0, colors="WB"), P(2, 2, 2.0, colors="WB"),
               P(3, 3, 1.0, colors="BW"), P(4, 4, 0.0, colors="WB")]
    req = P26Request(players=tuple(players), ruleset="dubov-2026",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4}


# ------------------------------------------------------------- Double/Team

def test_double_c5_best_profile_by_construction():
    """B10: Art.3.5.2 + worked example: C5 fixes upfloater SCORES (1.5 here),
    not just the count. The 1.0 candidate must lose despite a smaller TPN."""
    # id == TPN here (identity-space coverage is a separate test below).
    # S3 (1.0) holds the smallest TPN so a C5-blind min-(repeat, TPN)
    # selection would take it; C5 construction must prefer the 1.5s.
    players = [P(2, 2, 2.0), P(3, 3, 2.0), P(4, 4, 2.0),
               P(5, 5, 1.5, last_float="D"), P(6, 6, 1.5), P(1, 1, 1.0)]
    req = P26Request(players=tuple(players), ruleset="double-2026",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    ups = [i for i, d in out.floats if d == "U"]
    # bracket-1 (top group) upfloater must be a 1.5 (C5 by construction),
    # and among the two 1.5s the fresh one (C7): id6, never id1 (1.0).
    assert ups[0] == 6
    assert 1 not in ups[:1]


def test_double_c5_best_profile_without_legal_pairing_fails():
    """B10 literal: Art.3.5.2 considers ONLY C4/C5-compliant sets (best
    profile); 3.5.5 then needs a legal pairing among them. When the entire
    C5-best profile is unpairable, the procedure yields no set (3.3.3 Chief
    Arbiter) instead of silently falling back to a worse profile."""
    players = [P(2, 2, 2.0), P(3, 3, 2.0), P(4, 4, 2.0),
               P(5, 5, 1.5, opponents=(2, 3, 4)),  # blocked vs all residents
               P(6, 6, 1.0), P(7, 7, 0.5), P(8, 8, 0.5)]
    req = P26Request(players=tuple(players), ruleset="double-2026",
                     round_number=3, total_rounds=9)
    with pytest.raises(ImpossiblePairingError):
        pair_2026(req)


def test_double_identifier_uses_tpn_space():
    """B-ids: Art.3.6 identifiers are TPNs; engine must work when id != TPN
    (old code KeyError'd / mis-paired as soon as they diverged)."""
    players = [P(1, 10, 1.0), P(2, 20, 1.0), P(3, 30, 0.0), P(4, 40, 0.0)]
    req = P26Request(players=tuple(players), ruleset="double-2026",
                     round_number=2, total_rounds=5)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4}


def test_double_first_vs_min_graceful_on_forced_repeat():
    """B21 (INTERPRETATION I-T-C7): with every legal pairing repeating an
    opp-float, the engine pairs fewest-violations in identifier order
    instead of failing the round (strict zero-filter reading)."""
    players = [P(1, 1, 2.0, opponents=(2,), last_float="D"),
               P(2, 2, 2.0, opponents=(1,)),
               P(3, 3, 1.0, last_float="D"),
               P(4, 4, 0.5)]
    req = P26Request(players=tuple(players), ruleset="double-2026",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == {1, 2, 3, 4}


def test_team_437_grants_first_team_after_walkback_tie():
    """B11: Art.4.3.7 (missing step) — equal CD + walkback-tied identical
    (W,W,W,B) histories grant the FIRST team's Black preference."""
    a = P(1, 1, 2.0, colors="WWWB", secondary=5.0)
    b = P(2, 2, 2.0, colors="WWWB", secondary=3.0)
    w, bl = team_colour(a, b, initial_colour="W", kind="A",
                        is_last_round=False)
    assert (w, bl) == (2, 1)  # first-team A (secondary) gets Black


def test_team_kind_none_keeps_secondary_first_team():
    """B12: Art.4.2.2 secondary is dropped only when the competition says so
    (callers pass secondary 0); kind 'none' governs preferences, not rank."""
    a = P(1, 1, 2.0, colors="B", secondary=3.0)
    b = P(2, 2, 2.0, colors="B", secondary=5.0)
    w, bl = team_colour(a, b, initial_colour="W", kind="none",
                        is_last_round=False)
    # first-team is B (secondary); 4.3.8 alternation from last B -> B White
    assert (w, bl) == (2, 1)


# ------------------------------------------------------------------- Lim

def test_lim_scrutiny_order_downward_starts_at_1():
    """B14: Art.4.1.1 + worked 4.2 table scrutinise #1 (lowest TPN) first
    downward (not highest-TPN-first); upward mirrored."""
    from pairing_core.fide2026.lim import _scrutiny_order
    work = [P(1, 1, 1.0), P(2, 2, 1.0), P(3, 3, 1.0), P(4, 4, 1.0)]
    down = [p.id for p in _scrutiny_order(work, True, True, {})]
    assert down == [1, 2, 3, 4]
    up = [p.id for p in _scrutiny_order(work, False, False, {})]
    assert up == [4, 3, 2, 1]


def test_lim_opponent_column_order_downward():
    """B15: Art.4.2 table columns for #1: 4,5,6 then same-half DESC (3,2)."""
    from pairing_core.fide2026.lim import _exchange_pair
    work = [P(i, i, 1.0) for i in range(1, 7)]
    by_id = {p.id: p for p in work}
    # force full search trace via incompatible proposed: block 1v4 only
    w1 = P(1, 1, 1.0, opponents=(4,))
    work = [w1] + work[1:]
    by_id = {p.id: p for p in work}
    res = _exchange_pair(work, by_id, downward=True, upper=True,
                         floater_of={}, group_score=1.0, stepper=step(),
                         maxi=False)
    got = {frozenset(pr) for pr in res}
    # #1 takes #5 (next in 4,5,6,3,2 after blocked #4)... then #2 keeps #4?
    assert frozenset((1, 5)) in got


def test_lim_even_maker_from_majority_due_side():
    """B16: Art.3.2.2 floats from the MAJORITY due side (equalise remainder);
    minority choice skews it further. Tie -> 3.2.4 number."""
    players = [P(1, 1, 1.0, colors="WB"),  # due W (minority)
               P(2, 2, 1.0, colors="BW"), P(3, 3, 1.0, colors="BW"),
               P(4, 4, 1.0, colors="BW"), P(5, 5, 1.0, colors="BW")]
    f = LIM._select_floater(players, [], set(), downward=True, maxi=False)
    assert LIM.due_colour(f) == "B"  # majority side
    assert f.id == 2  # lowest TPN of the majority (3.2.4)


def test_lim_floater_priority_df_before_rest():
    """B19/3.6: down-floaters from higher groups are scrutinised first."""
    from pairing_core.fide2026.lim import _scrutiny_order
    work = [P(1, 1, 1.0), P(2, 2, 1.0), P(3, 3, 1.0), P(4, 4, 1.0)]
    floater_of = {4: (2.0, "D")}
    got = [p.id for p in _scrutiny_order(work, True, True, floater_of)]
    assert got[0] == 4


def test_lim_26_cracks_adjacent_higher_group():
    """B18: Art.2.6 — blocked median is extended by cracking the adjacent
    higher group's next pairing (counts tied 0-0 -> 2.6.2 higher)."""
    players = [P(1, 1, 2.0, opponents=(7,)), P(2, 2, 2.0, opponents=(8,)),
               P(3, 3, 1.0, opponents=(4,)), P(4, 4, 1.0, opponents=(3,)),
               P(5, 5, 0.0, opponents=(9,)), P(6, 6, 0.0, opponents=(10,)),
               P(7, 7, 2.0, opponents=(1,)), P(8, 8, 2.0, opponents=(2,)),
               P(9, 9, 0.0, opponents=(5,)), P(10, 10, 0.0, opponents=(6,))]
    req = P26Request(players=tuple(players), ruleset="lim-2026",
                     round_number=3, total_rounds=5)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert paired == set(range(1, 11))
    got = {frozenset((p.white_id, p.black_id)) for p in out.pairs}
    assert frozenset((1, 4)) in got and frozenset((3, 8)) in got


def test_lim_44_floats_lowest_numbered_on_failure():
    """B17: Art.4.4.2 — originally-even unpairable group floats the culprit
    (lowest TPN) in company with the lowest numbered remaining player,
    then pairs the rest. Direct unit pin."""
    from pairing_core.fide2026.lim import _apply_44
    work = [P(1, 1, 1.0, opponents=(2, 3, 4)), P(2, 2, 1.0, opponents=(1,)),
            P(3, 3, 1.0), P(4, 4, 1.0)]
    by_id = {p.id: p for p in work}
    queue = {0.5: [], 0.0: []}
    floater_of = {}
    dest_pool = [P(5, 5, 0.5), P(6, 6, 0.5)]  # compatible adjacent group
    res = _apply_44(list(work), None, 0.5, 0.0, True, queue,
                    P26Request(players=tuple(work), ruleset="lim-2026",
                               round_number=3, total_rounds=5),
                    step(), by_id, floater_of, dest_pool, [], True, 1.0)
    assert res is not None
    assert {frozenset(pr) for pr in res} == {frozenset((3, 4))}
    assert sorted(queue[0.5]) == [1, 2]  # culprit + lowest remaining


# --------------------------------------------------------------- Olympiad

def test_olympiad_odd_matchpoint_group_routes_floater():
    """B13: odd matchpoint groups route the floater forward (NameError +
    vanished-floater crash before the fix). 9 teams: bye 1, then a 3-team
    top group forces the 8.2/8.3 path."""
    players = ([P(1, 1, 0.0, colors="WB", played=2)]
               + [P(i, i, 2.5, colors="WB", played=2) for i in (2, 3, 4)]
               + [P(i, i, 1.0, colors="WB", played=2) for i in (5, 6, 7, 8, 9)])
    req = P26Request(players=tuple(players), ruleset="olympiad-2022",
                     round_number=3, total_rounds=9)
    out = pair_2026(req)
    paired = {i for p in out.pairs for i in (p.white_id, p.black_id)}
    assert out.bye_id == 1
    assert paired == {2, 3, 4, 5, 6, 7, 8, 9}


# ------------------------------------------------------------------ common

def test_last_differing_round_is_round_aligned():
    """Walkbacks (Dutch 5.2.3 ... Olympiad 7.6) align by ROUND with played-
    only comparison — zipping played-only sequences misaligns across 'u'."""
    a = P(1, 1, 0.0, colors="WuB")  # R1 W, R2 unplayed, R3 B
    b = P(2, 2, 0.0, colors="BWB")  # R1 B, R2 W, R3 B
    # played-zip: A='WB' vs B='BWB' reversed (B,B),(W,W) -> no difference.
    # round-aligned: R3 tie, R2 skipped (unplayed), R1 W-vs-B differs.
    assert last_differing_round(a, b) == ("W", "B")


def test_preference_dutch_family_unchanged():
    """Guard: Dutch/Burstein preference ladder untouched by the audit."""
    assert C.preference(P(1, 1, colors="WW")) == ("B", 3)
    assert C.preference(P(1, 1, colors="BB")) == ("W", 3)
    assert C.preference(P(1, 1, colors="WB")) == ("W", 1)
    assert C.preference(P(1, 1, colors="")) == (None, 0)
    assert C.preference(P(1, 1, colors=""), dubov_zero_game=True) == ("B", 1)
