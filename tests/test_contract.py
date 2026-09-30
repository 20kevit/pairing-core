"""Conformance tests for pairing-core public contract.

Ported from chess-manager tests/domain/test_pairing_engine.py +
test_pairing_validator.py (behavior-preserving subset). No Flask/SQLAlchemy.
"""
from pairing_core import (
    PlayerData, PairingCard, RoundResult, PairingRequest,
    NativeDutchEngine, SwissEngine, pair_round, validate_round,
)


def pd(pid, pno, rating, points=0.0, color_hist="", opponents=None,
       received_bye=False, float_hist=""):
    opp = frozenset(opponents) if opponents else frozenset()
    return PlayerData(id=pid, pairing_no=pno, rating=rating, points=points,
                      color_hist=color_hist, opponents=opp,
                      received_bye=received_bye, float_hist=float_hist)


def make_players(n, start_rating=2000, step=10, points_map=None, **kw):
    out = []
    for i in range(1, n + 1):
        pts = points_map.get(i, 0.0) if points_map else 0.0
        out.append(pd(i, i, start_rating - (i - 1) * step, points=pts, **kw))
    return out


def paired_ids(r):
    s = set()
    for c in r.pairings:
        s.add(c.white_id)
        if c.black_id is not None:
            s.add(c.black_id)
    return s


def pair_set(r):
    return {frozenset((c.white_id, c.black_id)) for c in r.pairings if not c.is_bye}


class TestBasic:
    def test_zero_players(self):
        r = pair_round([], round_number=1)
        assert r.pairings == [] and r.bye_player_id is None

    def test_single_player_bye(self):
        r = pair_round([pd(1, 1, 2000)], round_number=1)
        assert len(r.pairings) == 1 and r.pairings[0].is_bye
        assert r.bye_player_id == 1

    def test_two_players(self):
        r = pair_round(make_players(2), round_number=1)
        assert pair_set(r) == {frozenset((1, 2))}

    def test_four_round1(self):
        r = pair_round(make_players(4), round_number=1)
        assert pair_set(r) == {frozenset((1, 3)), frozenset((2, 4))}

    def test_eight_round1(self):
        r = pair_round(make_players(8), round_number=1)
        assert pair_set(r) == {frozenset((1, 5)), frozenset((2, 6)),
                               frozenset((3, 7)), frozenset((4, 8))}

    def test_odd_five(self):
        r = pair_round(make_players(5), round_number=1)
        assert len([c for c in r.pairings if c.is_bye]) == 1
        assert paired_ids(r) == {1, 2, 3, 4, 5}


class TestConstraints:
    def test_no_rematch(self):
        ps = [pd(1, 1, 2000, points=1.0, opponents={2}),
              pd(2, 2, 1900, points=1.0, opponents={1}),
              pd(3, 3, 1800, points=0.0),
              pd(4, 4, 1700, points=0.0)]
        r = pair_round(ps, round_number=2)
        for c in r.pairings:
            if c.is_bye:
                continue
            assert c.black_id not in {1: {2}, 2: {1}}.get(c.white_id, set())

    def test_bye_fresh_first(self):
        ps = [pd(1, 1, 2000, received_bye=True),
              pd(2, 2, 1900), pd(3, 3, 1800)]
        r = pair_round(ps, round_number=2)
        assert r.bye_player_id != 1

    def test_locked_pairs(self):
        ps = make_players(4)
        r = pair_round(ps, round_number=1, locked_pairs=[(1, 2)])
        assert frozenset((1, 2)) in pair_set(r)

    def test_locked_repeat_raises(self):
        import pytest
        ps = [pd(1, 1, 2000, opponents={2}), pd(2, 2, 1900, opponents={1})]
        with pytest.raises(ValueError):
            pair_round(ps, round_number=2, locked_pairs=[(1, 2)])

    def test_color_absolute(self):
        # player 1 has ww -> must get black; pair with fresh player
        ps = [pd(1, 1, 2000, color_hist="ww"), pd(2, 2, 1900)]
        r = pair_round(ps, round_number=3)
        card = r.pairings[0]
        assert card.black_id == 1 or card.white_id == 1
        # 1 must not be white
        assert card.white_id != 1

    def test_validation_clean(self):
        ps = make_players(4)
        r = pair_round(ps, round_number=1)
        rep = validate_round(r, ps)
        assert rep.is_valid


class TestDeterminism:
    def test_repeat_and_reorder(self):
        ps = make_players(8)
        r1 = pair_round(ps, round_number=1)
        r2 = pair_round(ps, round_number=1)
        assert [(c.white_id, c.black_id) for c in r1.pairings] == \
               [(c.white_id, c.black_id) for c in r2.pairings]
        rev = list(reversed(ps))
        r3 = pair_round(rev, round_number=1)
        assert pair_set(r3) == pair_set(r1)

    def test_engine_interface_equivalence(self):
        ps = make_players(6)
        a = pair_round(ps, round_number=2)
        eng = NativeDutchEngine()
        b = eng.pair(PairingRequest(players=ps, round_number=2))
        assert pair_set(a) == pair_set(b)
        assert (a.bye_player_id == b.bye_player_id)
        # class API compat
        c = SwissEngine(ps, round_number=2).generate()
        assert pair_set(c) == pair_set(a)

    def test_golden_round1_8players(self):
        # snapshot from current engine behavior — do not change lightly
        ps = make_players(8)
        r = pair_round(ps, round_number=1)
        assert pair_set(r) == {frozenset((1, 5)), frozenset((2, 6)),
                               frozenset((3, 7)), frozenset((4, 8))}
