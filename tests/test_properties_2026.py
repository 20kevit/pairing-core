"""Randomized property tests for every 2026 ruleset (audit §27).

Seeded stdlib-only. For each generated state, EXACTLY ONE of:
  (a) success satisfying all structural invariants below; or
  (b) typed ImpossiblePairingError / InvalidPlayerError / UnsupportedRulesetError.
Anything else (wrong exception, lost/duplicated players, self-pair, repeat
opponent, ineligible bye, nondeterminism, non-reproducible serialization)
fails. Seeds fixed: deterministic.
"""

import json
import random

import pytest

from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidPlayerError,
    UnsupportedRulesetError,
)
from pairing_core.fide2026 import common as C
from pairing_core.fide2026.api import pair_2026
from pairing_core.fide2026.models import P26Player, P26Request, P26RulesetId

TYPED = (ImpossiblePairingError, InvalidPlayerError, UnsupportedRulesetError)

RULESETS = [
    "dutch-2026",
    "dubov-2026",
    "burstein-2026",
    "lim-2026",
    "double-2026",
    "team-2026",
    "olympiad-2022",
]


def _gen_state(rng):
    n = rng.randint(2, 10)
    total_rounds = rng.randint(1, 9)
    round_number = rng.randint(1, total_rounds)
    played_rounds = round_number - 1
    # symmetric played history via random matchings per past round
    opps = {i: [] for i in range(1, n + 1)}
    colors = {i: [] for i in range(1, n + 1)}
    for _ in range(played_rounds):
        order = list(range(1, n + 1))
        rng.shuffle(order)
        for k in range(0, len(order) - 1, 2):
            a, b = order[k], order[k + 1]
            if rng.random() < 0.12:
                colors[a].append("u")
                colors[b].append(rng.choice("WB"))
            elif rng.random() < 0.12:
                colors[a].append(rng.choice("WB"))
                colors[b].append("u")
            else:
                ca = rng.choice("WB")
                colors[a].append(ca)
                colors[b].append("B" if ca == "W" else "W")
                opps[a].append(b)
                opps[b].append(a)
        if len(order) % 2:
            colors[order[-1]].append(rng.choice("WBu"))
    players = []
    for i in range(1, n + 1):
        col = "".join(colors[i])
        unplayed = col.count("u")
        played = played_rounds - unplayed
        score = round(sum(rng.choice([0.0, 0.5, 1.0])
                          for _ in range(played)), 1)
        players.append(P26Player(
            id=i, tpn=i, score=score, rating=rng.randint(1200, 2400),
            secondary=float(rng.choice([0, 0.5, 1.0, 1.5, 2.0])),
            colors=col, opponents=tuple(opps[i]), unplayed=unplayed,
            last_float=rng.choice(["", "", "", "D", "U"]),
            prev_float=rng.choice(["", "", "", "D", "U"]),
            got_pab=rng.random() < 0.05,
            forfeit_win=rng.random() < 0.03,
            played=played))
    return players, round_number, total_rounds


def _results_for(players, rng):
    out = []
    for p in players:
        out.append((p.id, tuple(rng.choice("WDL") for _ in p.opponents)))
    return tuple(out)


def _check_invariants(out, players, ruleset):
    by_id = {p.id: p for p in players}
    seen = []
    for pr in out.pairs:
        assert pr.white_id != pr.black_id, "no self-pair"
        seen.extend([pr.white_id, pr.black_id])
    if out.bye_id is not None:
        seen.append(out.bye_id)
        me = by_id[out.bye_id]
        assert C.pab_eligible(me), "bye taker eligible"
    assert sorted(seen) == sorted(by_id), "player conservation"
    for pr in out.pairs:
        a, b = by_id[pr.white_id], by_id[pr.black_id]
        assert b.id not in a.opponents, "no repeated opponent"
    for fid, _ in out.floats:
        assert fid in by_id, "float tags reference players"
    # deterministic serialization round-trip
    d1 = out.to_dict()
    assert json.loads(json.dumps(d1)) == d1
    assert d1["ruleset"] == ruleset


@pytest.mark.parametrize("ruleset", RULESETS)
@pytest.mark.parametrize("seed", range(15))
def test_property_2026(ruleset, seed):
    rng = random.Random(6000 + seed * 131 + len(ruleset))
    players, rnd, total = _gen_state(rng)
    kw = dict(round_number=rnd, total_rounds=total,
              is_last_round=(rnd == total),
              initial_colour=rng.choice("WB"))
    if ruleset == "burstein-2026":
        kw["round_results"] = _results_for(players, rng)
    if ruleset == "lim-2026":
        kw["maxi_tournament"] = bool(rng.getrandbits(1))
    req = P26Request(players=tuple(players), ruleset=ruleset, **kw)
    try:
        out = pair_2026(req)
    except TYPED:
        return
    _check_invariants(out, players, out.ruleset)
    out2 = pair_2026(req)
    assert out2.to_dict() == out.to_dict(), "deterministic result"


@pytest.mark.parametrize("ruleset", RULESETS)
def test_property_2026_team_kinds(ruleset):
    if ruleset != "team-2026":
        pytest.skip("team kinds only")
    rng = random.Random(777)
    players, rnd, total = _gen_state(rng)
    for kind in ("A", "B", "none"):
        rs = P26RulesetId(system="team", effective_date="2026-02-01",
                          team_colour_type=kind)
        req = P26Request(players=tuple(players), ruleset=rs,
                         round_number=rnd, total_rounds=total)
        try:
            out = pair_2026(req)
        except TYPED:
            continue
        _check_invariants(out, players, out.ruleset)
