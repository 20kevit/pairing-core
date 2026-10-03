"""FIDE 2026 engines: unit + official-corpus + property tests.

Provenance discipline: every corpus case records official-example | derived |
differential. Nothing derived is presented as official.
"""

import json
from pathlib import Path

import pytest

from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidPlayerError,
    UnsupportedRulesetError,
)
from pairing_core.fide2026 import baku
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.api import pair_2026
from pairing_core.fide2026.double_team import (
    _inner_key,
    double_colour,
    enumerate_pairings,
    team_colour,
)
from pairing_core.fide2026.dubov import aro, dubov_colour, max_t, _shifter_order
from pairing_core.fide2026.burstein import (
    buchholz_sb,
    enumerate_burstein_pairings,
    rank_key,
    seeding_rounds,
)
from pairing_core.fide2026.dutch import allocate_colour
from pairing_core.fide2026.lim import compatible, due_colour
from pairing_core.fide2026.models import (
    BURSTEIN_2026,
    DOUBLE_2026,
    DUBOV_2026,
    DUTCH_2026,
    LIM_2026,
    OLYMPIAD_2022,
    TEAM_2026,
    P26Player,
    P26Request,
    P26RulesetId,
    SYSTEM_RULESETS,
    resolve_2026_ruleset,
)
from pairing_core.fide2026.olympiad import (
    median_score_group,
    pair_9x,
    select_olympiad_bye,
)

CORPUS = Path(__file__).parent / "corpus" / "fide_official"


def P(pid, tpn=None, **kw):
    return P26Player(id=pid, tpn=tpn or pid, **kw)


def fresh(n, **kw):
    return [P(i, rating=2000 - 50 * i, score=0.0, colors="",
              played=0, **kw) for i in range(1, n + 1)]


# ------------------------------------------------------------- resolution

def test_resolve_aliases_and_exact():
    assert resolve_2026_ruleset(DUTCH_2026).system == "dutch"
    assert resolve_2026_ruleset(
        P26RulesetId("dubov", "2026-02-01")).system == "dubov"
    assert len(SYSTEM_RULESETS) == 7


def test_resolve_unknown_typed():
    with pytest.raises(UnsupportedRulesetError):
        resolve_2026_ruleset("dubov")
    with pytest.raises(UnsupportedRulesetError):
        pair_2026(P26Request(players=(), ruleset="dutch",
                             round_number=1))


def test_team_colour_type_option():
    rid = P26RulesetId("team", "2026-02-01", team_colour_type="B")
    assert resolve_2026_ruleset(rid).team_colour_type == "B"
    with pytest.raises(UnsupportedRulesetError):
        resolve_2026_ruleset(P26RulesetId("team", "2026-02-01",
                                          team_colour_type="C"))


# ------------------------------------------------------------------- baku

def test_baku_split_official():
    g = baku.split_groups(list(range(1, 162)))
    assert len(g.ga) == 82 and g.ga[-1] == 82  # official 161->82 note
    g8 = baku.split_groups(list(range(1, 9)))
    assert len(g8.ga) == 4  # 2*ceil(8/4)


def test_baku_virtual_schedules_official():
    assert [baku.virtual_points(True, r, 9) for r in (1, 2, 3)] == [1.0] * 3
    assert [baku.virtual_points(True, r, 9) for r in (4, 5)] == [0.5] * 2
    assert baku.virtual_points(True, 6, 9) == 0.0
    assert baku.virtual_points(False, 1, 9) == 0.0
    mp = [baku.virtual_points(True, r, 11, win_value=2.0) for r in range(1, 7)]
    assert mp == [2.0, 2.0, 2.0, 1.0, 1.0, 1.0]


def test_baku_pairing_scores():
    g = baku.split_groups([1, 2, 3, 4])
    out = baku.pairing_scores({1: 2.0, 2: 1.5, 3: 2.0, 4: 0.5}, g, 1, 9)
    assert out[1] == 3.0 and out[3] == 2.0  # GA 1,2 gain; GB untouched


# ------------------------------------------------------------ board order

def test_board_order_c0402():
    a = P(1, score=2.0)
    b = P(2, score=1.0)
    c = P(3, score=2.0)
    d = P(4, score=2.0)
    out = C.board_order([(a, b), (c, d)])
    assert out[0] == (3, 4)  # higher pair sum first (4.0 > 3.0)


# -------------------------------------------------------------- preferences

def test_dutch_preference_triggers():
    assert C.preference(P(1, colors="WW")) == ("B", 3)  # repetition absolute
    assert C.preference(P(1, colors="WBW")) == ("B", 2)  # CD +1 strong
    assert C.preference(P(1, colors="BB")) == ("W", 3)  # repetition absolute
    assert C.preference(P(1, colors="")) == (None, 0)


def test_dutch_preference_strong_mild():
    assert C.preference(P(1, colors="W")) == ("B", 2)
    assert C.preference(P(1, colors="B")) == ("W", 2)
    assert C.preference(P(1, colors="WB")) == ("W", 1)  # CD 0, last B -> W
    assert C.preference(P(1, colors="BW")) == ("B", 1)  # CD 0, last W -> B


def test_dubov_zero_game_mild_black():
    assert C.preference(P(1, colors=""), dubov_zero_game=True) == ("B", 1)


def test_team_preferences():
    assert C.team_preference(P(1, colors="WW"), kind="A") == ("B", 1)
    assert C.team_preference(P(1, colors=""), kind="A") == (None, 0)
    # single W: CD +1 without two-game history -> mild, not strong (1.7.2.3)
    assert C.team_preference(P(1, colors="W"), kind="B") == ("B", 1)
    # CD +1 WITH last-two White -> strong (1.7.2.2)
    assert C.team_preference(P(1, colors="BWW"), kind="B") == ("B", 2)
    # CD 0 non-last-round with last same-side game -> mild (1.7.2.3/4)
    assert C.team_preference(P(1, colors="WB"), kind="B",
                             is_last_round=True) == (None, 0)
    assert C.team_preference(P(1, colors="BW"), kind="B") == ("B", 1)
    assert C.team_preference(P(1, colors="WB"), kind="B") == ("W", 1)
    assert C.team_preference(P(1, colors="W"), kind="none") == (None, 0)


# ------------------------------------------------------------------ dutch

def test_dutch_r1_parity():
    from pairing_core.fide2026 import dutch as D
    req = P26Request(players=tuple(fresh(8)), ruleset=DUTCH_2026,
                     round_number=1, total_rounds=9)
    out = D.pair_dutch(req)
    got = {(p.white_id, p.black_id) for p in out.pairs}
    assert got == {(1, 5), (6, 2), (3, 7), (8, 4)}  # 5.2.5 parity


def test_dutch_c1_rematch_refusal():
    from pairing_core.fide2026 import dutch as D
    ps = [P(1, colors="W", opponents=(2,), played=1, score=1.0),
          P(2, colors="B", opponents=(1,), played=1, score=1.0)]
    req = P26Request(players=tuple(ps), ruleset=DUTCH_2026, round_number=2,
                     total_rounds=2, max_steps=5000)
    with pytest.raises(ImpossiblePairingError):
        D.pair_dutch(req)


def test_dutch_c3_same_absolute_non_topscorers():
    from pairing_core.fide2026 import dutch as D
    # four players, all WW (absolute Black), same score, all互 unplayed
    # vs each other except cross pairs free; C3 bars same-absolute meetings
    # for non-topscorers -> impossible here.
    ps = [P(i, colors="WW", played=2, score=1.0) for i in range(1, 5)]
    req = P26Request(players=tuple(ps), ruleset=DUTCH_2026, round_number=3,
                     total_rounds=9, max_steps=20000)
    with pytest.raises(ImpossiblePairingError):
        D.pair_dutch(req)


def test_dutch_odd_field_pab_lowest_score():
    from pairing_core.fide2026 import dutch as D
    ps = fresh(7)
    req = P26Request(players=tuple(ps), ruleset=DUTCH_2026, round_number=1,
                     total_rounds=9)
    out = D.pair_dutch(req)
    assert out.bye_id == 7  # lowest score group, largest TPN
    assert len(out.pairs) == 3


def test_dutch_allocate_chain():
    a = P(1, colors="WW")  # absolute Black
    b = P(2, colors="BB")  # absolute White
    w, _ = allocate_colour(a, b, initial_colour="W")
    assert w == 2  # grant both


# ------------------------------------------------------------------ dubov

def test_dubov_missing_rating():
    from pairing_core.fide2026 import dubov as D
    ps = [P(1, tpn=1, rating=None), P(2, tpn=2, rating=1800)]
    with pytest.raises(InvalidPlayerError):
        D.pair_dubov(P26Request(players=tuple(ps), ruleset=DUBOV_2026,
                                round_number=1, total_rounds=9))


def test_aro_math():
    by_id = {1: P(1, tpn=1, rating=2000, opponents=(2, 3)),
             2: P(2, tpn=2, rating=1800), 3: P(3, tpn=3, rating=1801)}
    assert aro(by_id[1], by_id) == 1801  # (1800+1801)/2 = 1800.5 -> half-up
    assert aro(by_id[2], by_id) == 0
    assert max_t(9) == 3 and max_t(11) == 4 and max_t(4) == 2


def test_shifter_middle_outward():
    seek = [P(i, tpn=i, rating=2000 - 100 * i) for i in range(1, 8)]
    by_id = {p.id: p for p in seek}
    assert _shifter_order(seek, white=False, by_id=by_id) == [4, 3, 5, 2, 6, 1, 7]


def test_dubov_r1_and_determinism():
    from pairing_core.fide2026 import dubov as D
    req = P26Request(players=tuple(fresh(8)), ruleset=DUBOV_2026,
                     round_number=1, total_rounds=9)
    r1 = D.pair_dubov(req)
    r2 = D.pair_dubov(req)
    assert r1.to_dict() == r2.to_dict()
    got = {(p.white_id, p.black_id) for p in r1.pairs}
    assert got == {(1, 5), (6, 2), (3, 7), (8, 4)}


def test_dubov_colour_unplayed_even_hrp():
    a = P(1, tpn=2, rating=2000)
    b = P(2, tpn=6, rating=1900)
    w, _ = dubov_colour(a, b, initial_colour="W")
    assert w == 2  # even-TPN higher-ranked gets opposite


# --------------------------------------------------------------- burstein

def test_seeding_rounds():
    assert seeding_rounds(9) == 4 and seeding_rounds(5) == 2
    assert seeding_rounds(11) == 4


def test_buchholz_sb():
    by_id = {1: P(1, tpn=1, score=1.0, opponents=(2,)),
             2: P(2, tpn=2, score=0.5, opponents=(1,))}
    bh, sb = buchholz_sb(by_id[1], by_id, {1: ("W",), 2: ("L",)})
    assert (bh, sb) == (0.5, 0.5)
    assert rank_key(by_id[1], by_id, {1: ("W",), 2: ("L",)})[2] == 1


def test_burstein_enumeration_first():
    ps = [P(i, tpn=i) for i in range(1, 7)]
    rank_of = {p.id: (0, 0, p.tpn) for p in ps}
    out = enumerate_burstein_pairings(ps, rank_of, 2)
    first = [(x, y) for x, y in out[0] if x != 0 and y != 0]
    assert (1, 6) in first and (2, 5) in first  # official table head


def test_burstein_seeding_delegates():
    from pairing_core.fide2026 import burstein as B
    req = P26Request(players=tuple(fresh(6)), ruleset=BURSTEIN_2026,
                     round_number=2, total_rounds=9)
    out = B.pair_burstein(req)
    assert out.ruleset == "burstein-2026"
    assert any("seeding-round" in n for n in out.notes)


def test_burstein_needs_results():
    from pairing_core.fide2026 import burstein as B
    ps = [P(i, tpn=i, score=1.0 if i <= 3 else 0.0, rating=1900,
            colors="W" if i <= 3 else "B", opponents=(),
            played=1) for i in range(1, 7)]
    with pytest.raises(InvalidPlayerError):
        B.pair_burstein(P26Request(
            players=tuple(ps), ruleset=BURSTEIN_2026, round_number=5,
            total_rounds=9))


# -------------------------------------------------------------------- lim

def test_lim_compatibility():
    assert compatible(P(1), P(2))
    assert not compatible(P(1, opponents=(2,)), P(2, opponents=(1,)))
    assert due_colour(P(1, colors="WB")) == "W"


def test_lim_r1_official_table():
    from pairing_core.fide2026 import lim as L
    req = P26Request(players=tuple(fresh(8)), ruleset=LIM_2026,
                     round_number=1, total_rounds=5)
    out = L.pair_lim(req)
    got = [(p.white_id, p.black_id) for p in out.pairs]
    # board-ordered; membership: 1v5, 6v2, 3v7, 8v4 (official 40pl pattern)
    assert {frozenset(g) for g in got} == {frozenset(g) for g in
                                          [(1, 5), (6, 2), (3, 7), (8, 4)]}
    whites = {w for w, _ in got}
    assert whites == {1, 6, 3, 8}


def test_lim_r1_lot_black_mirror():
    from pairing_core.fide2026 import lim as L
    req = P26Request(players=tuple(fresh(8)), ruleset=LIM_2026,
                     round_number=1, total_rounds=5, initial_colour="B")
    out = L.pair_lim(req)
    whites = {p.white_id for p in out.pairs}
    assert whites == {5, 2, 7, 4}  # mirrored colours


# ------------------------------------------------------------ double/team

def test_double_identifier_official():
    ps = [P(t, tpn=t) for t in (4, 6, 8, 9, 10, 11, 16, 24)]
    found = None
    for pairing in enumerate_pairings(ps):
        tops = sorted(t for t, _ in pairing)
        if tops == [4, 6, 9, 11]:
            ident = tuple(tops) + tuple(
                b for t in tops
                for (tt, b) in pairing if tt == t)
            if ident == (4, 6, 9, 11, 8, 16, 10, 24):
                found = pairing
    assert found is not None


def test_double_upfloater_example_order():
    from pairing_core.fide2026.double_team import _inner_key
    by_id = {i: P(i, tpn=i, score={2: 3.0, 6: 3.0, 8: 3.0, 1: 2.5,
                                   3: 2.5, 5: 2.5}[i]) for i in (1, 2, 3, 5, 6, 8)}
    assert _inner_key((2, 6, 1), by_id) < _inner_key((2, 6, 3), by_id)
    assert _inner_key((2, 8, 5), by_id) < _inner_key((6, 8, 1), by_id)


def test_double_r1_identifier_first():
    from pairing_core.fide2026 import double_team as DT
    req = P26Request(players=tuple(fresh(8)),
                     ruleset=P26RulesetId("double", "2026-02-01"),
                     round_number=1, total_rounds=7)
    out = DT.pair_double_or_team(req, system="double")
    got = {frozenset((p.white_id, p.black_id)) for p in out.pairs}
    assert got == {frozenset(g) for g in [(1, 5), (2, 6), (3, 7), (4, 8)]}


def test_double_colour_hrp_chain():
    a = P(1, tpn=1, score=2.0, colors="WW")  # 2 whites
    b = P(2, tpn=2, score=2.0, colors="BB")  # 0 whites
    w, _ = double_colour(a, b, initial_colour="W")
    assert w == 2  # fewer Whites gets White


def test_team_first_team_and_types():
    a = P(1, tpn=1, score=2.0, secondary=3.0)
    b = P(2, tpn=2, score=2.0, secondary=4.0)
    # kind A: secondary counts -> first-team is 2 (even TPN) -> opposite of
    # initial W -> 2 gets Black, white is 1.
    w, _ = team_colour(a, b, initial_colour="W", kind="A",
                       is_last_round=False)
    assert w == 1
    # kind none: secondary dropped -> first-team is 1 (smaller TPN, odd) ->
    # initial W -> white is 1 (same colour, different first-team).
    w2, _ = team_colour(a, b, initial_colour="W", kind="none",
                        is_last_round=False)
    assert w2 == 1


# --------------------------------------------------------------- olympiad

def test_olympiad_bye_lowest_number():
    ps = [P(i, tpn=i, score=float(i)) for i in range(1, 8)]
    ps[0] = P26Player(id=1, tpn=1, score=1.0, got_pab=True)
    assert select_olympiad_bye(ps).id == 2


def test_olympiad_9x_first_combination():
    from pairing_core.fide2026 import olympiad as O
    ps = [P(i, tpn=i) for i in range(1, 7)]
    by_id = {p.id: p for p in ps}
    out = pair_9x(ps, by_id, C.Stepper())
    got = {frozenset(g) for g in out}
    assert got == {frozenset(g) for g in [(1, 4), (2, 5), (3, 6)]}


def test_median_group_even_field():
    ps = [P(i, tpn=i, score=2.0 if i <= 44 else 1.0) for i in range(1, 89)]
    ranked = sorted(ps, key=lambda p: (-p.score, p.tpn))
    assert median_score_group(ranked) == 1.0  # 45th team has 1.0 (lower middle)


# ----------------------------------------------------------- corpus files

def test_corpus_provenance_schema():
    for path in sorted(CORPUS.glob("*.json")):
        data = json.loads(path.read_text())
        assert data["provenance"] in ("official-example",
                                      "official-example-with-derived-truncation",
                                      "derived", "differential"), path
        assert "source" in data and "article" in data, path


def test_corpus_burstein_enumeration():
    data = json.loads((CORPUS / "burstein_art4_enumeration.json").read_text())
    ps = [P(i, tpn=i) for i in range(1, 7)]
    rank_of = {p.id: (0, 0, p.tpn) for p in ps}
    out = enumerate_burstein_pairings(ps, rank_of, 2)
    first = sorted([tuple(sorted((x, y))) for x, y in out[0]
                    if x != 0 and y != 0])
    assert first == [(1, 6), (2, 5)]


def test_corpus_double_upfloater_order():
    data = json.loads((CORPUS / "double_upfloater_sets.json").read_text())
    scores = {int(k): v for k, v in data["scores"].items()}
    by_id = {i: P(i, tpn=i, score=s) for i, s in scores.items()}
    assert _inner_key((2, 6, 1), by_id) == tuple(
        _inner_key(data["expected_first_set"], by_id))
    assert _inner_key(tuple(data["expected_first_set"]), by_id) < \
        _inner_key((2, 6, 3), by_id)


def test_corpus_olympiad_table():
    data = json.loads((CORPUS / "olympiad_9x_table.json").read_text())
    ps = [P(i, tpn=i) for i in range(1, 7)]
    out = pair_9x(ps, {p.id: p for p in ps}, C.Stepper())
    assert {frozenset(g) for g in out} == \
        {frozenset(g) for g in data["expected_first"]}


def test_corpus_baku():
    data = json.loads((CORPUS / "baku_split_schedule.json").read_text())
    for case in data["cases"]:
        g = baku.split_groups(list(range(1, case["n"] + 1)))
        assert len(g.ga) == case["expected_ga"]
    v9 = data["virtual"]["9R-individual"]
    assert [baku.virtual_points(True, r, 9) for r in v9["rounds"]] == v9["expected"]


def test_corpus_lim_tables():
    exch = json.loads((CORPUS / "lim_exchange_table.json").read_text())
    assert exch["expected_columns_for_1"] == ["4", "5", "6", "3", "2"]
    r1 = json.loads((CORPUS / "lim_round_one.json").read_text())
    assert r1["official_40player_lotW_head"] == [[1, 21], [22, 2], [3, 23],
                                                [24, 4]]
    # derived 8-player expectation verified by test_lim_r1_official_table
    assert {frozenset(g) for g in r1["expected_pairs_white_first_8"]} == \
        {frozenset(g) for g in [(1, 5), (6, 2), (3, 7), (8, 4)]}


# ------------------------------------------------------- property tests

def _check_invariants(out, players, *, my_floats=()):
    ids = {p.id for p in players}
    seen = []
    for pr in out.pairs:
        seen += [pr.white_id, pr.black_id]
    if out.bye_id is not None:
        seen.append(out.bye_id)
    assert sorted(seen) == sorted(ids)  # player preservation, bye uniqueness
    assert len(set(seen)) == len(seen)  # no duplicates
    by_id = {p.id: p for p in players}
    for pr in out.pairs:  # no rematch
        assert pr.black_id not in by_id[pr.white_id].opponents
    for fid, _ in out.floats:
        assert fid in ids


def test_property_dutch_r1():
    from pairing_core.fide2026 import dutch as D
    req = P26Request(players=tuple(fresh(9)), ruleset=DUTCH_2026,
                     round_number=1, total_rounds=9)
    out = D.pair_dutch(req)
    assert out.bye_id == 9  # C5 lowest score, family tiebreak largest TPN
    _check_invariants(out, req.players)


def test_property_all_systems_deterministic():
    from pairing_core.fide2026 import dutch as D
    from pairing_core.fide2026 import dubov as DU
    from pairing_core.fide2026 import lim as L
    from pairing_core.fide2026 import double_team as DT
    from pairing_core.fide2026 import olympiad as O
    req_d = P26Request(players=tuple(fresh(6)), ruleset=DUTCH_2026,
                       round_number=1, total_rounds=7)
    assert D.pair_dutch(req_d).to_dict() == D.pair_dutch(req_d).to_dict()
    req_u = P26Request(players=tuple(fresh(6)), ruleset=DUBOV_2026,
                       round_number=1, total_rounds=7)
    assert DU.pair_dubov(req_u).to_dict() == DU.pair_dubov(req_u).to_dict()
    req_l = P26Request(players=tuple(fresh(6)), ruleset=LIM_2026,
                       round_number=1, total_rounds=5)
    assert L.pair_lim(req_l).to_dict() == L.pair_lim(req_l).to_dict()
    req_dd = P26Request(players=tuple(fresh(6)),
                        ruleset=P26RulesetId("double", "2026-02-01"),
                        round_number=1, total_rounds=7)
    assert DT.pair_double_or_team(req_dd, system="double").to_dict() == \
        DT.pair_double_or_team(req_dd, system="double").to_dict()
    req_t = P26Request(players=tuple(fresh(6)),
                       ruleset=P26RulesetId("team", "2026-02-01"),
                       round_number=1, total_rounds=7)
    assert DT.pair_double_or_team(req_t, system="team").to_dict() == \
        DT.pair_double_or_team(req_t, system="team").to_dict()
    req_o = P26Request(players=tuple(fresh(6)), ruleset=OLYMPIAD_2022,
                       round_number=1, total_rounds=11)
    assert O.pair_olympiad(req_o).to_dict() == O.pair_olympiad(req_o).to_dict()
    _check_invariants(D.pair_dutch(req_d), req_d.players)


def test_property_double_r2_no_rematch():
    from pairing_core.fide2026 import double_team as DT
    # R1 was 1v5, 2v6, 3v7, 4v8 with 1,6,3,8 White.
    opp = {1: (5,), 5: (1,), 2: (6,), 6: (2,), 3: (7,), 7: (3,), 4: (8,),
           8: (4,)}
    ps = [P(i, score=1.0 if i <= 4 else 0.0,
            colors="W" if i in (1, 6, 3, 8) else "B", opponents=opp[i],
            played=1) for i in range(1, 9)]
    req = P26Request(players=tuple(ps),
                     ruleset=P26RulesetId("double", "2026-02-01"),
                     round_number=2, total_rounds=7)
    out = DT.pair_double_or_team(req, system="double")
    _check_invariants(out, req.players)


def test_budgets_exhaust_typed():
    from pairing_core.errors import EngineTimeoutError
    from pairing_core.fide2026 import dutch as D
    req = P26Request(players=tuple(fresh(8)), ruleset=DUTCH_2026,
                     round_number=1, total_rounds=9, max_steps=1)
    with pytest.raises(EngineTimeoutError):
        D.pair_dutch(req)