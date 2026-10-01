"""Determinism snapshot (F1 checkpoint, O08).

Methodology: every engine golden case is re-run repeatedly and under input
permutation (reversed + fixed-seed shuffles). Full outputs (boards, colours,
float tags, bye) must be byte-identical — no normalization of differences.

CI note: also run this module under varying PYTHONHASHSEED
(e.g. 0/42); the kernel must not depend on hash order. Verified manually
during F1 (see F1 report); enforced in CI from Foundation F6 onward.
"""

import json
import os
import random

from pairing_core import (
    NativeDutchEngine,
    PairingRequest,
    PlayerData,
    SwissEngine,
    pair_round,
)

from tests.test_v010_behavioral import _engine_cases, _player

REPEATS = 25


def _fingerprint(result):
    return [(c.board, c.white_id, c.black_id, c.is_bye,
             c.white_float, c.black_float) for c in result.pairings]


def _run(case, players):
    return pair_round(players, round_number=case["round"],
                      locked_pairs=[tuple(x) for x in case["locked"]]
                      if case["locked"] else None)


def test_repeat_runs_identical():
    for case in _engine_cases():
        if not case["players"]:
            continue
        players = [_player(p) for p in case["players"]]
        first = _fingerprint(_run(case, players))
        for _ in range(REPEATS):
            assert _fingerprint(_run(case, players)) == first


def test_input_order_irrelevant():
    rng = random.Random(20261001)
    for case in _engine_cases():
        if len(case["players"]) < 2:
            continue
        base = [_player(p) for p in case["players"]]
        want = (_fingerprint(_run(case, base)),
                _run(case, base).bye_player_id)
        rev = list(reversed(base))
        assert _fingerprint(_run(case, rev)) == want[0]
        assert _run(case, rev).bye_player_id == want[1]
        for _ in range(5):
            shuf = list(base)
            rng.shuffle(shuf)
            assert _fingerprint(_run(case, shuf)) == want[0]
            assert _run(case, shuf).bye_player_id == want[1]


def test_interfaces_agree_exactly():
    for case in _engine_cases():
        players = [_player(p) for p in case["players"]]
        req = PairingRequest(players=list(players),
                             round_number=case["round"],
                             locked_pairs=[tuple(x) for x in case["locked"]]
                             if case["locked"] else [])
        a = _run(case, players)
        b = NativeDutchEngine().pair(req)
        c = SwissEngine(list(players), round_number=case["round"],
                        locked_pairs=list(req.locked_pairs)).generate()
        assert _fingerprint(b) == _fingerprint(a)
        assert _fingerprint(c) == _fingerprint(a)
        assert b.bye_player_id == a.bye_player_id
        assert c.bye_player_id == a.bye_player_id


def test_error_paths_deterministic():
    from tests.test_v010_behavioral import _error_cases
    for case in _error_cases():
        players = [_player(p) for p in case["players"]]
        msgs = set()
        for _ in range(5):
            try:
                _run(case, players)
            except ValueError as exc:
                msgs.add(str(exc))
            else:
                raise AssertionError(f"{case['id']} unexpectedly succeeded")
        assert len(msgs) == 1
