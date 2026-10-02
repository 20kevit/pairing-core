"""Property/randomized tests (seeded, stdlib-only, no new dependencies).

For each generated state, EXACTLY ONE of the following must hold:
  (a) success with a validator-clean, order-stable, conserved output; or
  (b) typed ImpossiblePairingError / InvalidRequestError.
Anything else (unexpected exception type, validator errors on success,
player loss/duplication, nondeterminism) fails. Seeds fixed: deterministic.
"""

import random

import pytest

from pairing_core import (
    ConstraintSet,
    EngineRequest,
    PlayerData,
    RoundPairing,
    pair_via,
    validate_round,
)
from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidRequestError,
    PairingError,
)

COMPAT = "dutch-till2026-compat"


def _gen_state(rng):
    n = rng.randint(2, 10)
    played_rounds = rng.randint(0, 4)
    players = []
    opps = {i: set() for i in range(1, n + 1)}
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            if rng.random() < played_rounds / max(n - 1, 1) * 0.8:
                opps[i].add(j)
                opps[j].add(i)
    for i in range(1, n + 1):
        colors = "".join(rng.choice("wbb-w-") for _ in range(played_rounds))
        floats = "".join(rng.choice("DU---") for _ in range(played_rounds))
        points = round(rng.choice([0, 0.5, 1, 1.5, 2, 2.5, 3, 3.5, 4])
                       if played_rounds else 0.0, 1)
        players.append(PlayerData(
            id=i, pairing_no=i, rating=rng.randint(1200, 2400),
            points=points, color_hist=colors,
            opponents=frozenset(opps[i]),
            received_bye=rng.random() < 0.1, float_hist=floats))
    return players, played_rounds + 1


def _check_invariants(result, players):
    ids = [p.id for p in players]
    seen = []
    for c in result.pairings:
        seen.append(c.white_id)
        if c.black_id is not None:
            seen.append(c.black_id)
    assert sorted(seen) == sorted(ids), "player conservation"
    assert [c.board for c in result.pairings] == \
        list(range(1, len(result.pairings) + 1)), "board order"
    assert sum(1 for c in result.pairings if c.is_bye) <= 1, "bye count"
    rep = validate_round(result, players)
    assert not rep.has_errors, rep.error_summary
    # serialization/replay equivalence of the envelope
    from pairing_core import pair_detailed
    req = EngineRequest(players=players, ruleset=COMPAT,
                        round_number=result.round_number,
                        constraints=ConstraintSet())
    detailed = pair_detailed(req)
    assert isinstance(detailed, RoundPairing)
    assert [(c.board, c.white_id, c.black_id) for c in detailed.pairings] == \
           [(c.board, c.white_id, c.black_id) for c in result.pairings]


@pytest.mark.parametrize("seed", range(30))
def test_generated_states_totality(seed):
    rng = random.Random(9000 + seed)
    players, rnd = _gen_state(rng)
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=rnd,
                        constraints=ConstraintSet())
    try:
        first = pair_via("native-dutch", req)
    except (ImpossiblePairingError, InvalidRequestError):
        return
    except PairingError as exc:
        pytest.fail(f"unexpected error category: {type(exc).__name__}: {exc}")
    _check_invariants(first, players)
    # determinism: repeat + reversal identical
    again = pair_via("native-dutch", req)
    assert [(c.board, c.white_id, c.black_id, c.white_float,
             c.black_float) for c in again.pairings] == \
           [(c.board, c.white_id, c.black_id, c.white_float,
             c.black_float) for c in first.pairings]
    rev = EngineRequest(players=list(reversed(players)), ruleset=COMPAT,
                        round_number=rnd, constraints=ConstraintSet())
    swapped = pair_via("native-dutch", rev)
    assert {frozenset((c.white_id, c.black_id)) for c in swapped.pairings
            if c.black_id is not None} == \
           {frozenset((c.white_id, c.black_id)) for c in first.pairings
            if c.black_id is not None}
