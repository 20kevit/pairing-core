"""Clause-focused regression probes for the 2026 audit closure wave.

These are repository tests of implementation details, not independent FIDE
validation. They use hand-built inputs; source-derived official examples stay
in the separately rights-unresolved fixture corpus.
"""

from pairing_core.fide2026 import common as C
from pairing_core.fide2026.burstein import (
    _choose_pairing as choose_burstein_pairing,
    _colour_misses as burstein_colour_misses,
)
from pairing_core.fide2026.dubov import (
    _bracket_vector as dubov_bracket_vector,
    _colour_misses as dubov_colour_misses,
    _find_transposition,
)
from pairing_core.fide2026.double_team import (
    _violation_vector,
    enumerate_pairings as enumerate_team_pairings,
    lex_first_pairing,
)
from pairing_core.fide2026.dutch import (
    _Ctx as DutchContext,
    _abs_ok as dutch_abs_ok,
    _c8_next_vector,
    _vector as dutch_vector,
)
from pairing_core.fide2026.lim import (
    _exchange_pair as lim_exchange_pair,
    _needs_floater as lim_needs_floater,
    _refloat_allowed as lim_refloat_allowed,
    compatible as lim_compatible,
    pair_lim,
)
from pairing_core.fide2026.models import (
    BURSTEIN_2026,
    DUBOV_2026,
    DUTCH_2026,
    OLYMPIAD_2022,
    P26Player,
    P26Request,
    TEAM_2026,
)
from pairing_core.fide2026.olympiad import (
    _colour_bans_ok as olympiad_colour_bans_ok,
    board1_colour,
    pair_olympiad,
)


def player(pid, *, tpn=None, **fields):
    return P26Player(id=pid, tpn=tpn if tpn is not None else pid, **fields)


def request(players, ruleset, *, round_number=2, total_rounds=9, **fields):
    return P26Request(players=tuple(players), ruleset=ruleset,
                      round_number=round_number, total_rounds=total_rounds,
                      **fields)


def test_dubov_c6_uses_ascending_upfloater_score_sequence():
    """C6 maximises the ascending upfloater scores, not the descending list."""
    req = request((player(1), player(2)), DUBOV_2026)

    def c6(scores):
        ups = [player(i + 1, score=score) for i, score in enumerate(scores)]
        by_id = {p.id: p for p in ups}
        return dubov_bracket_vector(ups, ups, (), by_id, req=req, mt=3,
                                    up_count={})[0]

    # Ascending [2, 2] outranks ascending [1, 3] at the first differing value.
    assert c6([2.0, 2.0]) < c6([1.0, 3.0])


def test_dubov_maximum_upfloater_vector_counts_current_use_and_last_round_exception():
    u = player(1, score=0.5, last_float="U")
    by_id = {u.id: u}
    ordinary = request((u,), DUBOV_2026, round_number=8, total_rounds=9)
    vector = dubov_bracket_vector([u], [u], (), by_id, req=ordinary, mt=3,
                                  up_count={u.id: 3})
    assert vector[2:] == (1, 4, 1)  # C8 count, C9 prior + this upfloat, C10 repeat

    last = request((u,), DUBOV_2026, round_number=9, total_rounds=9)
    final_vector = dubov_bracket_vector(
        [u], [u], (), by_id, req=last, mt=3, up_count={u.id: 3})
    assert final_vector[2:] == (0, 0, 0)


def test_dubov_set_order_uses_smallest_differing_sequence_number():
    ordered = list(C.lexicographic_sets([4, 2, 1, 3], 2))
    assert ordered == [(1, 2), (1, 3), (1, 4),
                       (2, 3), (2, 4), (3, 4)]


def test_dubov_g2_transposition_is_first_legal_tpn_permutation():
    s1 = [player(1), player(2), player(3)]
    g2 = [player(4), player(5), player(6)]
    # Both permutations beginning with TPN 4 fail; [5, 4, 6] is first legal.
    s1[0] = player(1, opponents=(4,))
    by_id = {p.id: p for p in s1 + g2}
    assert _find_transposition(s1, g2, by_id, C.Stepper()) == [5, 4, 6]


def test_dubov_c7_counts_preference_miss_from_real_pairing():
    a = player(1, colors="B")
    b = player(2, colors="B")
    assert dubov_colour_misses([(a.id, b.id)], {a.id: a, b.id: b},
                               initial_colour="W") == 1


def test_dutch_topscorer_exception_uses_strict_half_score_threshold():
    top = player(1, score=3.0, colors="BB")
    other = player(2, score=2.0, colors="BB")
    req = request((top, other), DUTCH_2026, round_number=5, total_rounds=5)
    ctx = DutchContext(req, {1: top, 2: other}, (), C.Stepper(), {1})
    assert dutch_abs_ok([(1, 2)], ctx)

    tied = (player(1, score=2.5, colors="BB"),
            player(2, score=2.5, colors="BB"))
    tied_req = request(tied, DUTCH_2026, round_number=5, total_rounds=5)
    tied_ctx = DutchContext(tied_req, {p.id: p for p in tied}, (),
                            C.Stepper(), set())
    assert not dutch_abs_ok([(1, 2)], tied_ctx)


def test_dutch_c8_probe_is_one_next_bracket_deep():
    residents = [player(1, score=1.0), player(2, score=1.0)]
    mdp = player(3, score=0.5)
    all_players = residents + [mdp, player(4, score=0.0)]
    by_id = {p.id: p for p in all_players}
    req = request(all_players, DUTCH_2026)
    ctx = DutchContext(req, by_id, (), C.Stepper(), set())
    assert _c8_next_vector([mdp.id], residents, ctx, set(), set(by_id)) == \
        (1, (0.5,))


def test_dutch_vector_keeps_pab_colour_and_float_criteria_separate():
    a = player(1, score=3.0, colors="BB", last_float="D", prev_float="D")
    b = player(2, score=2.0, colors="BB", last_float="U", prev_float="U")
    bye = player(3, score=1.0, last_float="D", prev_float="D", unplayed=2)
    by_id = {p.id: p for p in (a, b, bye)}
    req = request((a, b, bye), DUTCH_2026, round_number=5, total_rounds=5)
    ctx = DutchContext(req, by_id, (), C.Stepper(), {a.id})
    vector = dutch_vector(
        [(a.id, b.id)], [bye.id], [(a.id, b.id)], {a.id}, bye.id, (), ctx,
        {a.id, b.id, bye.id}, set(by_id), is_last=True)
    assert vector == (
        1.0, 1, (1.0,), (0, ()), 2,
        1, 1, 1, 0,
        1, 1, 1, 1,
        (1.0,), (1.0,), (1.0,), (1.0,),
    )


def test_burstein_colour_quality_selects_pairing_with_fewer_misses():
    players = [
        player(1, colors="WW"), player(2, colors="BB"),
        player(3, colors="BB"), player(4, colors="WW"),
    ]
    by_id = {p.id: p for p in players}
    rank_of = {p.id: (0, 0, p.tpn) for p in players}
    req = request(players, BURSTEIN_2026, round_number=5)
    chosen = choose_burstein_pairing(
        players, by_id, rank_of, 2, (), C.Stepper(), req=req, rest_after=[])
    assert {frozenset(pair) for pair in chosen} == {
        frozenset((1, 3)), frozenset((2, 4))}
    assert burstein_colour_misses(chosen, by_id, rank_of,
                                  initial_colour="W") == 0


def test_lim_compatibility_triggers_floater_for_rematch_or_no_colour_option():
    a = player(1, colors="WW")
    b = player(2, colors="WW")
    assert not lim_compatible(a, b)
    assert lim_needs_floater(a, [a, b])

    fresh_a, fresh_b = player(3), player(4)
    assert lim_compatible(fresh_a, fresh_b)
    assert not lim_needs_floater(fresh_a, [fresh_a, fresh_b])


def test_lim_proposed_pairing_exchanges_around_rematch_in_column_order():
    work = [player(i) for i in range(1, 5)]
    # Proposed 1v3 is a rematch; scrutiny backtracks to 1v4, 2v3.
    work[0] = player(1, opponents=(3,))
    work[2] = player(3, opponents=(1,))
    by_id = {p.id: p for p in work}
    pairs = lim_exchange_pair(
        work, by_id, downward=True, upper=True, floater_of={},
        group_score=1.0, stepper=C.Stepper(), maxi=False)
    assert pairs == [(1, 4), (2, 3)]


def test_lim_refloat_guard_is_only_a_remainder_pairability_probe():
    cand, a, b = player(1), player(2), player(3)
    by_id = {p.id: p for p in (cand, a, b)}
    assert lim_refloat_allowed(
        cand, [cand, a, b], by_id, True, True, {}, False)
    assert not lim_refloat_allowed(
        cand, [cand, a], by_id, True, True, {}, False)


def test_lim_round_two_routes_top_then_bottom_then_median(monkeypatch):
    import pairing_core.fide2026.lim as lim

    players = [player(1, score=1.0), player(2, score=1.0),
               player(3, score=0.5), player(4, score=0.5),
               player(5, score=0.0), player(6, score=0.0)]
    visited = []
    original = lim._exchange_pair

    def observe(work, *args, **kwargs):
        visited.append(tuple(p.id for p in work))
        return original(work, *args, **kwargs)

    monkeypatch.setattr(lim, "_exchange_pair", observe)
    out = pair_lim(request(players, "lim-2026", round_number=2,
                           total_rounds=9))
    assert set(visited) == {(1, 2), (5, 6), (3, 4)}
    assert visited.index((1, 2)) < visited.index((5, 6)) < visited.index((3, 4))
    assert len(out.pairs) == 3


def test_olympiad_board1_walkback_aligns_unplayed_rounds_and_initial_lot():
    a = player(1, colors="BWu")
    b = player(2, colors="WBB")
    # The latest jointly played opposite-colour round is round 2, not the
    # misaligned last played-only colour after deleting the unplayed slot.
    assert board1_colour(a, b, initial_colour="W")[0] == b.id

    first, second = player(3), player(4)
    assert board1_colour(first, second, initial_colour="B")[0] == second.id


def test_olympiad_colour_ban_is_ignored_only_after_no_banned_pairing_exists():
    a = player(1, score=1.0, colors="WW")
    b = player(2, score=1.0, colors="WW")
    out = pair_olympiad(request((a, b), OLYMPIAD_2022,
                                round_number=3, total_rounds=11))
    assert len(out.pairs) == 1
    pair = out.pairs[0]
    assert pair.white_id == b.id  # equalise CD, then the 7.4 override is needed
    assert not olympiad_colour_bans_ok(b, True)


def test_team_quality_vector_distinguishes_strong_misses_and_repeat_opponents():
    a = player(1, score=1.0, colors="WW")
    b = player(2, score=1.0, colors="WW")
    by_id = {a.id: a, b.id: b}
    by_tpn = {a.tpn: a, b.tpn: b}
    strong = _violation_vector(
        [(1, 2)], by_id, by_tpn, system="team", kind="B",
        initial_colour="W", is_last_round=False, up_ids=frozenset(),
        count_opp_repeat=True)
    assert strong[:2] == (1, 1)

    opponent = player(2, score=1.0, last_float="D")
    by_id = {a.id: a, opponent.id: opponent}
    by_tpn = {a.tpn: a, opponent.tpn: opponent}
    repeated = _violation_vector(
        [(1, 2)], by_id, by_tpn, system="team", kind="none",
        initial_colour="W", is_last_round=False, up_ids=frozenset({1}),
        count_opp_repeat=True)
    omitted_last_round = _violation_vector(
        [(1, 2)], by_id, by_tpn, system="team", kind="none",
        initial_colour="W", is_last_round=True, up_ids=frozenset({1}),
        count_opp_repeat=False)
    assert repeated[-1] == 1
    assert omitted_last_round[-1] == 0


def test_double_quality_vector_counts_opponent_float_reuse():
    up = player(1, score=1.0)
    opponent = player(2, score=1.0, last_float="D")
    by_id = {up.id: up, opponent.id: opponent}
    by_tpn = {up.tpn: up, opponent.tpn: opponent}
    ordinary = _violation_vector(
        [(1, 2)], by_id, by_tpn, system="double", kind="none",
        initial_colour="W", is_last_round=False, up_ids=frozenset({1}),
        count_opp_repeat=True)
    last_round = _violation_vector(
        [(1, 2)], by_id, by_tpn, system="double", kind="none",
        initial_colour="W", is_last_round=True, up_ids=frozenset({1}),
        count_opp_repeat=False)
    assert ordinary == (1,)
    assert last_round == (0,)


def test_team_pairing_identifiers_use_tpn_space_and_lexicographic_order():
    players = [player(101, tpn=10), player(102, tpn=20),
               player(103, tpn=30), player(104, tpn=40)]
    expected = [(10, 30), (20, 40)]
    assert lex_first_pairing(players) == expected
    assert enumerate_team_pairings(players)[0] == expected
