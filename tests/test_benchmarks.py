"""W7 performance baselines: realistic spreads + pathological brackets.

Method (evidence-first, no optimization): a seeded self-play simulator builds
REALISTIC multi-round histories (colors/opponents/floats/points all derived
from kernel outputs + deterministic rating-based results). Each scenario
records wall time + outcome. Assertions: realistic spreads must SUCCEED;
pathological brackets must end in typed EngineTimeoutError (bounded failure,
never hang) under an explicit wall-clock budget. No hard timing asserts
(machine-dependent); durations print to stdout and are refreshed on disk
only with PAIRING_UPDATE_BASELINES=1 (tests/data/benchmarks/).

Run: pytest tests/test_benchmarks.py -q -s (table prints with -s).
"""

import json
import os
import random
import time

import pytest

from pairing_core import (
    ConstraintSet,
    EngineRequest,
    PlayerData,
    pair,
    validate_round,
)
from pairing_core.controls import ExecutionBudgets
from pairing_core.errors import EngineTimeoutError

COMPAT = "dutch-till2026-compat"
BENCH_DIR = os.path.join(os.path.dirname(__file__), "data", "benchmarks")
RECORD = {}


def _simulate(n_players, rounds, seed, rating_spread=400):
    """Deterministic self-play: returns final-round EngineRequest."""
    rng = random.Random(seed)
    ratings = [2200 - i * rating_spread // max(n_players - 1, 1)
               for i in range(n_players)]
    ids = list(range(1, n_players + 1))
    pnos = list(ids)
    points = {i: 0.0 for i in ids}
    colors = {i: "" for i in ids}
    floats = {i: "" for i in ids}
    opps = {i: set() for i in ids}
    for rnd in range(1, rounds + 1):
        players = [PlayerData(id=i, pairing_no=pnos[i - 1],
                              rating=ratings[i - 1], points=points[i],
                              color_hist=colors[i],
                              opponents=frozenset(opps[i]),
                              float_hist=floats[i]) for i in ids]
        req = EngineRequest(players=players, ruleset=COMPAT,
                            round_number=rnd,
                            constraints=ConstraintSet())
        t0 = time.perf_counter()
        result = pair(req)
        dt = time.perf_counter() - t0
        RECORD.setdefault(f"sim_n{n_players}_r{rounds}", []).append(dt)
        rep = validate_round(result, players)
        assert not rep.has_errors
        by_id = {p.id: p for p in players}
        for card in result.pairings:
            if card.is_bye:
                points[card.white_id] += 1.0
                floats[card.white_id] += "D"
                continue
            w, b = card.white_id, card.black_id
            opps[w].add(b)
            opps[b].add(w)
            colors[w] += "w"
            colors[b] += "b"
            if card.white_float == "D":
                floats[w] += "D"
            elif card.white_float == "U":
                floats[w] += "U"
            else:
                floats[w] += "-"
            if card.black_float == "D":
                floats[b] += "D"
            elif card.black_float == "U":
                floats[b] += "U"
            else:
                floats[b] += "-"
            # deterministic rating-based result, 15% draws
            diff = by_id[w].rating - by_id[b].rating
            roll = rng.random()
            exp = 1.0 / (1.0 + 10.0 ** (-diff / 400.0))
            if roll < 0.15:
                points[w] += 0.5
                points[b] += 0.5
            elif roll < exp:
                points[w] += 1.0
            else:
                points[b] += 1.0
    return EngineRequest(
        players=[PlayerData(id=i, pairing_no=pnos[i - 1],
                            rating=ratings[i - 1], points=points[i],
                            color_hist=colors[i],
                            opponents=frozenset(opps[i]),
                            float_hist=floats[i]) for i in ids],
        ruleset=COMPAT, round_number=rounds + 1,
        constraints=ConstraintSet())


def _time_request(req, budgets=None, label=""):
    req2 = EngineRequest(players=req.players, ruleset=COMPAT,
                         round_number=req.round_number,
                         constraints=req.constraints, budgets=budgets)
    t0 = time.perf_counter()
    try:
        result = pair(req2)
        dt = time.perf_counter() - t0
        RECORD[label] = {"seconds": dt, "outcome": "success",
                         "boards": len(result.pairings)}
        return result
    except EngineTimeoutError:
        dt = time.perf_counter() - t0
        RECORD[label] = {"seconds": dt, "outcome": "timeout-bounded"}
        raise


@pytest.mark.parametrize("n", [50, 100, 250])
def test_realistic_spread(n):
    req = _simulate(n, 4, seed=1000 + n)
    result = _time_request(req, label=f"realistic_n{n}_round5")
    assert len(result.pairings) == n // 2


_RUN_HEAVY = os.environ.get("RUN_HEAVY_BENCH") == "1"
needs_heavy = pytest.mark.skipif(
    not _RUN_HEAVY, reason="heavy benchmark: RUN_HEAVY_BENCH=1 to run")


@needs_heavy
@pytest.mark.parametrize("n", [500, 1000])
def test_realistic_spread_heavy(n):
    req = _simulate(n, 4, seed=1000 + n)
    result = _time_request(req, label=f"realistic_n{n}_round5")
    assert len(result.pairings) == n // 2


def test_pathological_single_bracket_bounded():
    # 80 players, one score group, dense histories: must end typed, not hang.
    rng = random.Random(77)
    players = []
    for i in range(1, 81):
        opps = set(rng.sample([j for j in range(1, 81) if j != i], 6))
        players.append(PlayerData(
            id=i, pairing_no=i, rating=2000 - i, points=3.0,
            color_hist="".join(rng.choice("wb") for _ in range(6)),
            opponents=frozenset(opps), float_hist="------"))
    # symmetrize for plausibility (still adversarially dense)
    by_id = {p.id: p for p in players}
    fixed = []
    for p in players:
        extra = {o for o in by_id if p.id in by_id[o].opponents}
        fixed.append(PlayerData(
            id=p.id, pairing_no=p.pairing_no, rating=p.rating,
            points=p.points, color_hist=p.color_hist,
            opponents=p.opponents | extra, float_hist=p.float_hist))
    req = EngineRequest(players=fixed, ruleset=COMPAT, round_number=7,
                        constraints=ConstraintSet(),
                        budgets=ExecutionBudgets(wall_clock_seconds=120))
    try:
        result = _time_request(req, label="pathological_single80")
        assert len(result.pairings) == 40
    except EngineTimeoutError:
        pass  # bounded typed failure is the requirement


def test_dense_rematch_bounded():
    raw = [PlayerData(id=i, pairing_no=i, rating=2000 - i, points=2.0,
                      opponents=frozenset(
                          {j for j in range(1, 21) if j != i}
                          - ({i + 1} if i < 20 else {1})))
           for i in range(1, 21)]
    by_id = {p.id: p for p in raw}
    players = [PlayerData(
        id=p.id, pairing_no=p.pairing_no, rating=p.rating,
        points=p.points, color_hist=p.color_hist,
        opponents=p.opponents | {o for o in by_id
                                 if p.id in by_id[o].opponents},
        float_hist=p.float_hist) for p in raw]
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=6,
                        constraints=ConstraintSet(),
                        budgets=ExecutionBudgets(wall_clock_seconds=120))
    # Near-complete histories explode combinatorially: the requirement is a
    # TYPED bounded outcome (success or step-cap timeout), never a hang.
    try:
        result = _time_request(req, label="dense_rematch20")
        assert len(result.pairings) == 10
    except EngineTimeoutError:
        RECORD["dense_rematch20"] = {"outcome": "timeout-bounded"}


def test_write_baseline_record():
    # Record-only: file refresh is opt-in (PAIRING_UPDATE_BASELINES=1) so a
    # plain suite run never dirties the working tree. Gates live in the
    # scenario tests above; this test only pins that scenarios ran.
    if os.environ.get("PAIRING_UPDATE_BASELINES") != "1":
        print("\nBENCHMARK " + json.dumps(RECORD, indent=1))
        assert RECORD
        return
    if not RECORD:
        pytest.skip("no scenarios ran in this session; nothing to refresh")
    os.makedirs(BENCH_DIR, exist_ok=True)
    import subprocess
    try:
        sha = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"], capture_output=True,
            text=True, check=True).stdout.strip()
    except Exception:
        sha = "UNKNOWN"
    path = os.path.join(BENCH_DIR, "baseline.json")
    previous = {}
    if os.path.isfile(path):
        try:
            previous = json.load(open(path, encoding="utf-8")
                                 ).get("scenarios", {})
        except (ValueError, OSError):
            previous = {}
    # Merge: refresh measured scenarios, keep heavy ones from earlier runs.
    previous.update(RECORD)
    record = {"git_sha": sha, "tool": "tests/test_benchmarks.py",
              "note": "machine-dependent durations; outcomes are the gates",
              "scenarios": previous}
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(record, fh, indent=1)
    print("\nBENCHMARK " + json.dumps(RECORD, indent=1))
    assert RECORD
