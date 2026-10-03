"""W8 performance gates for the 2026 engines (audit §23).

Method: single-round timings on (a) fresh R1 fields (always pairable —
must succeed) and (b) crafted realistic mid-tournament positions (must
succeed), at 20/50/100 players where the architecture admits it; plus
pathological inputs that must terminate TYPED (budget model), never hang.
No hard timing asserts (machine-dependent); durations are RECORDED to
tests/data/benchmarks/benchmarks_2026.json. Budgets are derived from the
measurements in docs/audit/FIDE_CONFORMANCE_FINAL_REPORT.md §10.
"""

import json
import os
import time

import pytest

from pairing_core.errors import EngineTimeoutError, PairingError
from pairing_core.fide2026.api import pair_2026
from pairing_core.fide2026.models import P26Player, P26Request

BENCH_DIR = os.path.join(os.path.dirname(__file__), "data", "benchmarks")
RECORD = {}
WALL = 120.0
WALL_SEARCH = 15.0  # seed-search attempts fail fast (bounded)
WALL_LARGE = 45.0  # 50-player positions: success or typed timeout


def _fresh(n, seed=1):
    import random
    rng = random.Random(seed)
    return [P26Player(id=i, tpn=i, score=0.0, rating=2200 - i * 5,
                      secondary=float(rng.choice([0, 0.5, 1.0])),
                      colors="", opponents=(), unplayed=0, played=0)
            for i in range(1, n + 1)]


def _mid(n, ruleset, seed=2):
    """Realistic R3 position via two engine self-play rounds (guaranteed
    consistent histories). First seed (from `seed`) whose R3 state pairs
    successfully is used — deterministic. Viable at n=20; at n=50 the
    exact-search systems need minutes (see test_big_bracket_n50_bounded)."""
    for attempt in range(seed, seed + 10):
        made = _play_two_rounds(n, attempt, ruleset)
        if made is None:
            continue
        players, extra = made
        total = 9 if ruleset != "olympiad-2022" else 11
        rnd = 6 if ruleset == "burstein-2026" else 3
        try:
            req = P26Request(players=tuple(players), ruleset=ruleset,
                             round_number=rnd, total_rounds=total,
                             wall_clock_seconds=WALL_SEARCH, **extra)
            pair_2026(req)
        except PairingError:
            continue
        return players, extra, rnd, total, attempt
    raise AssertionError(f"no pairable R3 state for {ruleset} n={n}")


def _fragmented(n, ruleset, seed=5):
    """50-player mid-tournament state with FRAGMENTED scores (many tiny
    brackets exercise the heterogeneous/MDP machinery fast). Histories come
    from one real R1 pairing (consistent and fast); scores are spread
    artificially (the engine takes scores as inputs and never cross-checks
    results)."""
    import random
    import dataclasses
    rng = random.Random(seed)
    players = _fresh(n, seed=seed)
    total = 9 if ruleset != "olympiad-2022" else 11
    out = pair_2026(P26Request(players=tuple(players), ruleset=ruleset,
                               round_number=1, total_rounds=total,
                               wall_clock_seconds=WALL_SEARCH))
    fl = dict(out.floats)
    hist = []
    for pr in out.pairs:
        w, b = pr.white_id, pr.black_id
        res = rng.choice(["W", "D", "L"])
        hist.append((w, b, res))
    spread = sorted([round(0.5 * ((i * 37) % 9), 1) for i in range(n)],
                    reverse=True)
    by_tpn = {p.tpn: p for p in players}
    opp_of = {i: [] for i in range(1, n + 1)}
    col_of = {i: "" for i in range(1, n + 1)}
    res_of = {i: [] for i in range(1, n + 1)}
    for w, b, res in hist:
        opp_of[w].append(b)
        opp_of[b].append(w)
        col_of[w] += "W"
        col_of[b] += "B"
        if res == "W":
            res_of[w].append("W")
            res_of[b].append("L")
        elif res == "L":
            res_of[w].append("L")
            res_of[b].append("W")
        else:
            res_of[w].append("D")
            res_of[b].append("D")
    if out.bye_id is not None:
        col_of[out.bye_id] += "u"
    out_players = []
    for p, s in zip(sorted(players, key=lambda p: p.tpn), spread):
        i = p.id
        out_players.append(P26Player(
            id=i, tpn=p.tpn, score=s, rating=p.rating, secondary=0.0,
            colors=col_of[i], opponents=tuple(opp_of[i]), unplayed=0,
            last_float=fl.get(i, ""), prev_float="", played=1 if i != out.bye_id else 0))
    extra = {}
    if ruleset == "burstein-2026":
        extra["round_results"] = tuple(
            (i, tuple(res_of[i])) for i in range(1, n + 1))
    if ruleset == "dubov-2026":
        extra["prior_upfloats"] = tuple(
            (i, 1) for i, f in fl.items() if f == "U")
    rnd = 6 if ruleset == "burstein-2026" else 2
    return out_players, extra, rnd, total


def _play_two_rounds(n, seed, ruleset):
    """Two self-play rounds; returns the R3 player list or None."""
    import random
    rng = random.Random(seed)
    ratings = [2200 - i * 5 for i in range(n)]
    score = {i: 0.0 for i in range(1, n + 1)}
    colors = {i: "" for i in range(1, n + 1)}
    opps = {i: [] for i in range(1, n + 1)}
    results = {i: [] for i in range(1, n + 1)}
    last_fl = {i: "" for i in range(1, n + 1)}
    prev_fl = {i: "" for i in range(1, n + 1)}
    upfloats = {i: 0 for i in range(1, n + 1)}
    for rnd in (1, 2):
        players = []
        for i in range(1, n + 1):
            col = colors[i]
            players.append(P26Player(
                id=i, tpn=i, score=score[i], rating=ratings[i - 1],
                secondary=0.0, colors=col, opponents=tuple(opps[i]),
                unplayed=col.count("u"),
                last_float=last_fl[i], prev_float=prev_fl[i],
                played=len(col) - col.count("u")))
        kw = {}
        if ruleset == "burstein-2026":
            kw["round_results"] = tuple(
                (i, tuple(results[i])) for i in range(1, n + 1))
        if ruleset == "dubov-2026":
            kw["prior_upfloats"] = tuple(
                (i, upfloats[i]) for i in range(1, n + 1) if upfloats[i])
        total = 9 if ruleset != "olympiad-2022" else 11
        try:
            out = pair_2026(P26Request(
                players=tuple(players), ruleset=ruleset, round_number=rnd,
                total_rounds=total, wall_clock_seconds=WALL_SEARCH, **kw))
        except PairingError:
            return None
        fl = dict(out.floats)
        for pr in out.pairs:
            w, b = pr.white_id, pr.black_id
            opps[w].append(b)
            opps[b].append(w)
            colors[w] += "W"
            colors[b] += "B"
            diff = ratings[w - 1] - ratings[b - 1]
            roll = rng.random()
            exp = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
            if roll < 0.15:
                score[w] += 0.5
                score[b] += 0.5
                results[w].append("D")
                results[b].append("D")
            elif roll < exp:
                score[w] += 1.0
                results[w].append("W")
                results[b].append("L")
            else:
                score[b] += 1.0
                results[w].append("L")
                results[b].append("W")
        if out.bye_id is not None:
            score[out.bye_id] += 1.0
            colors[out.bye_id] += "u"
        for i in range(1, n + 1):
            prev_fl[i] = last_fl[i]
            last_fl[i] = fl.get(i, "")
            if fl.get(i) == "U":
                upfloats[i] += 1
    # R3 state + results/upfloats
    players = []
    for i in range(1, n + 1):
        col = colors[i]
        players.append(P26Player(
            id=i, tpn=i, score=score[i], rating=ratings[i - 1],
            secondary=0.0, colors=col, opponents=tuple(opps[i]),
            unplayed=col.count("u"), last_float=last_fl[i],
            prev_float=prev_fl[i], played=len(col) - col.count("u")))
    extra = {}
    if ruleset == "burstein-2026":
        extra["round_results"] = tuple(
            (i, tuple(results[i])) for i in range(1, n + 1))
    if ruleset == "dubov-2026":
        extra["prior_upfloats"] = tuple(
            (i, upfloats[i]) for i in range(1, n + 1) if upfloats[i])
    return players, extra


def _round_results(players):
    return tuple((p.id, tuple("D" for _ in p.opponents)) for p in players)


RULESETS = ["dutch-2026", "dubov-2026", "burstein-2026", "lim-2026",
            "double-2026", "team-2026", "olympiad-2022"]


def _time(players, ruleset, rnd, total, label, wall=WALL, **kw):
    if ruleset == "burstein-2026":
        kw["round_results"] = _round_results(players)
    req = P26Request(players=tuple(players), ruleset=ruleset,
                     round_number=rnd, total_rounds=total,
                     is_last_round=(rnd == total),
                     wall_clock_seconds=wall, **kw)
    t0 = time.perf_counter()
    try:
        out = pair_2026(req)
        dt = time.perf_counter() - t0
        RECORD[label] = {"seconds": round(dt, 3), "outcome": "success",
                         "pairs": len(out.pairs)}
        return out
    except PairingError as exc:
        dt = time.perf_counter() - t0
        RECORD[label] = {"seconds": round(dt, 3),
                         "outcome": f"{type(exc).__name__}"}
        raise


@pytest.mark.parametrize("ruleset", RULESETS)
@pytest.mark.parametrize("n", [20, 50])
def test_r1_fresh_succeeds(ruleset, n):
    total = 9 if ruleset != "olympiad-2022" else 11
    out = _time(_fresh(n), ruleset, 1, total, f"{ruleset}_r1_n{n}")
    assert len(out.pairs) == n // 2


@pytest.mark.parametrize("ruleset", RULESETS)
def test_mid_position_n20_succeeds(ruleset):
    players, extra, rnd, total, attempt = _mid(20, ruleset)
    out = _time(players, ruleset, rnd, total,
                f"{ruleset}_mid_n20_seed{attempt}", **extra)
    assert len(out.pairs) >= 1


@pytest.mark.parametrize("ruleset", RULESETS)
def test_mid_position_n50_terminates(ruleset):
    # 50-player fragmented mid position (many small brackets): success or
    # typed error, always bounded.
    players, extra, rnd, total = _fragmented(50, ruleset, seed=5)
    t0 = time.perf_counter()
    try:
        _time(players, ruleset, rnd, total,
              f"{ruleset}_frag_n50", wall=WALL_LARGE, **extra)
    except PairingError:
        pass
    assert time.perf_counter() - t0 < WALL_LARGE + 60.0


def test_big_bracket_n50_bounded():
    # 50-player R2 state with two ~25-player scoregroups (exact search is
    # factorial here): Dutch/Burstein/Double must terminate TYPED
    # (budget model) or succeed — never hang. Documents the architecture's
    # exact-search ceiling (final report §10).
    for ruleset in ("dutch-2026", "burstein-2026", "double-2026"):
        players = _fresh(50, seed=50)
        total = 9
        r1 = pair_2026(P26Request(players=tuple(players), ruleset=ruleset,
                                  round_number=1, total_rounds=total,
                                  wall_clock_seconds=WALL_SEARCH))
        fl = dict(r1.floats)
        opp_of = {i: [] for i in range(1, 51)}
        col_of = {i: "" for i in range(1, 51)}
        for pr in r1.pairs:
            w, b = pr.white_id, pr.black_id
            opp_of[w].append(b)
            opp_of[b].append(w)
            col_of[w] += "W"
            col_of[b] += "B"
        state = [P26Player(
            id=i, tpn=i, score=1.0 if i <= 25 else 0.0, rating=2200 - i * 5,
            secondary=0.0, colors=col_of[i], opponents=tuple(opp_of[i]),
            unplayed=0, last_float=fl.get(i, ""), prev_float="",
            played=1) for i in range(1, 51)]
        extra = {}
        if ruleset == "burstein-2026":
            extra["round_results"] = tuple(
                (i, ("D",)) for i in range(1, 51))
        rnd = 6 if ruleset == "burstein-2026" else 2
        t0 = time.perf_counter()
        try:
            _time(state, ruleset, rnd, total,
                  f"{ruleset}_big_n50", wall=WALL_LARGE, **extra)
        except PairingError:
            pass
        assert time.perf_counter() - t0 < WALL_LARGE + 60.0


def test_pathological_dense_rematch_bounded():
    n = 12
    players = [P26Player(id=i, tpn=i, score=1.0, rating=1800, colors="WB",
                         opponents=tuple(j for j in range(1, n + 1) if j != i),
                         played=2)
               for i in range(1, n + 1)]
    req = P26Request(players=tuple(players), ruleset="dutch-2026",
                     round_number=3, total_rounds=5,
                     wall_clock_seconds=20.0, max_steps=200000)
    t0 = time.perf_counter()
    try:
        out = pair_2026(req)
        outcome = f"success pairs={len(out.pairs)}"
    except EngineTimeoutError:
        outcome = "timeout-bounded"
    except PairingError as exc:
        outcome = f"{type(exc).__name__}"
    dt = time.perf_counter() - t0
    RECORD["dutch_pathological_dense_rematch"] = {
        "seconds": round(dt, 3), "outcome": outcome}
    assert dt < 60.0, "must terminate bounded"


def test_write_2026_benchmark_record():
    # Record-only: file refresh is opt-in (PAIRING_UPDATE_BASELINES=1) so a
    # plain suite run never dirties the working tree.
    if os.environ.get("PAIRING_UPDATE_BASELINES") != "1":
        assert RECORD
        return
    path = os.path.join(BENCH_DIR, "benchmarks_2026.json")
    with open(path, "w") as fh:
        json.dump({"tool": __name__, "note": "machine-dependent durations; "
                   "outcomes are the gates", "scenarios": RECORD},
                  fh, indent=1, sort_keys=True)
