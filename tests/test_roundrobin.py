"""Round-robin tests: official Handbook tables + structural properties."""

import json
from pathlib import Path

import pytest

from pairing_core.errors import InvalidRequestError
from pairing_core.roundrobin import round_robin


BERGER_FIXTURE = Path(__file__).parent / "corpus" / "fide_official" / \
    "berger_tables_c05.json"
BERGER_DATA = json.loads(BERGER_FIXTURE.read_text(encoding="utf-8"))


def _flat(schedule):
    return [[(w, b) for (w, b) in rnd] for rnd in schedule]


def test_4_players_exact():
    assert _flat(round_robin(4)) == [
        [(1, 4), (2, 3)],
        [(4, 3), (1, 2)],
        [(2, 4), (3, 1)],
    ]


def test_6_players_exact():
    assert _flat(round_robin(6)) == [
        [(1, 6), (2, 5), (3, 4)],
        [(6, 4), (5, 3), (1, 2)],
        [(2, 6), (3, 1), (4, 5)],
        [(6, 5), (1, 4), (2, 3)],
        [(3, 6), (4, 2), (5, 1)],
    ]


def test_8_players_exact():
    assert _flat(round_robin(8)) == [
        [(1, 8), (2, 7), (3, 6), (4, 5)],
        [(8, 5), (6, 4), (7, 3), (1, 2)],
        [(2, 8), (3, 1), (4, 7), (5, 6)],
        [(8, 6), (7, 5), (1, 4), (2, 3)],
        [(3, 8), (4, 2), (5, 1), (6, 7)],
        [(8, 7), (1, 6), (2, 5), (3, 4)],
        [(4, 8), (5, 3), (6, 2), (7, 1)],
    ]


def test_10_players_exact():
    sched = _flat(round_robin(10))
    assert sched[0] == [(1, 10), (2, 9), (3, 8), (4, 7), (5, 6)]
    assert sched[1] == [(10, 6), (7, 5), (8, 4), (9, 3), (1, 2)]
    assert sched[8] == [(5, 10), (6, 4), (7, 3), (8, 2), (9, 1)]
    assert len(sched) == 9


def test_12_players_exact():
    sched = _flat(round_robin(12))
    assert sched[0] == [(1, 12), (2, 11), (3, 10), (4, 9), (5, 8), (6, 7)]
    assert sched[5] == [(12, 9), (10, 8), (11, 7), (1, 6), (2, 5), (3, 4)]
    assert sched[10] == [(6, 12), (7, 5), (8, 4), (9, 3), (10, 2), (11, 1)]
    assert len(sched) == 11


@pytest.mark.parametrize("n", range(3, 17))
def test_all_published_berger_tables_exact(n):
    """Compare every FIDE Annex 1 table from 3 through 16 players."""
    assert BERGER_DATA["provenance"] == "official-example"
    slots = n + (n % 2)
    official = BERGER_DATA["tables"][str(slots)]
    expected = []
    for round_pairs in official:
        expected_round = []
        for white, black in round_pairs:
            if n % 2 and slots in (white, black):
                expected_round.append((black if white == slots else white, None))
            else:
                expected_round.append((white, black))
        expected.append(expected_round)
    assert _flat(round_robin(n)) == expected


def _pairs(n, double=False, **kw):
    return round_robin(n, double=double, **kw)


@pytest.mark.parametrize("n", [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14])
def test_completeness_and_bye_rotation(n):
    sched = _pairs(n)
    owe = n if n % 2 == 1 else n - 1
    assert len(sched) == owe
    seen = set()
    byes = []
    for rnd in sched:
        boards = [b for b in rnd if b[1] is not None]
        assert len(rnd) == (n + 1) // 2
        for (w, b) in boards:
            key = frozenset((w, b))
            assert key not in seen, f"duplicate pairing {key}"
            seen.add(key)
        byes += [w for (w, b) in rnd if b is None]
    expect = n * (n - 1) // 2
    assert len(seen) == expect, "every pair meets exactly once"
    if n % 2 == 1:
        assert sorted(byes) == list(range(1, n + 1)), "each sits out once"
    else:
        assert byes == []


@pytest.mark.parametrize("n", [4, 6, 8, 10, 12])
def test_color_balance_bounded(n):
    sched = _pairs(n)
    whites = {i: 0 for i in range(1, n + 1)}
    blacks = {i: 0 for i in range(1, n + 1)}
    for rnd in sched:
        for (w, b) in rnd:
            whites[w] += 1
            blacks[b] += 1
    for i in range(1, n + 1):
        assert abs(whites[i] - blacks[i]) <= 2, i


def test_double_swaps_colors():
    single = _pairs(6)
    double = _pairs(6, double=True)
    assert len(double) == 10
    for a, b in zip(single, double[5:]):
        assert sorted([tuple(sorted(p)) for p in a]) == \
            sorted([tuple(sorted(p)) for p in b])
        for (w1, b1), (w2, b2) in zip(a, b):
            assert {w1, b1} == {w2, b2} and (w1, b1) == (b2, w2)


@pytest.mark.parametrize("n", [3, 4, 6, 8, 10])
def test_double_reversal_option_reverses_only_first_cycle_final_two(n):
    plain = _pairs(n, double=True)
    reversed_schedule = _pairs(n, double=True, reverse_last_two=True)
    rounds_per_cycle = len(plain) // 2

    assert reversed_schedule[:rounds_per_cycle - 2] == \
        plain[:rounds_per_cycle - 2]
    assert reversed_schedule[rounds_per_cycle - 2:rounds_per_cycle] == \
        plain[rounds_per_cycle - 2:rounds_per_cycle][::-1]
    assert reversed_schedule[rounds_per_cycle:] == plain[rounds_per_cycle:]


def test_double_reversal_reduces_four_player_colour_streak():
    def longest_streak(schedule, player):
        sequence = []
        for rnd in schedule:
            for white, black in rnd:
                if player == white:
                    sequence.append("W")
                elif player == black:
                    sequence.append("B")
        longest = current = 0
        last = None
        for colour in sequence:
            current = current + 1 if colour == last else 1
            longest = max(longest, current)
            last = colour
        return longest

    plain = _pairs(4, double=True)
    reversed_schedule = _pairs(4, double=True, reverse_last_two=True)
    assert max(longest_streak(plain, p) for p in range(1, 5)) == 3
    assert max(longest_streak(reversed_schedule, p) for p in range(1, 5)) == 2


def test_two_players_and_errors():
    assert _flat(round_robin(2)) == [[(1, 2)]]
    with pytest.raises(InvalidRequestError):
        round_robin(1)
    with pytest.raises(InvalidRequestError):
        round_robin(0)
    with pytest.raises(InvalidRequestError):
        round_robin("8")


def test_deterministic():
    assert round_robin(9) == round_robin(9)
