"""Basic Swiss pairing example (public API only).

Runs a two-round club tournament fragment with the frozen
`dutch-till2026-compat` kernel through the canonical consumer contract:
construct players -> build request -> pair -> inspect -> roll forward ->
handle errors.

Usage: python3 examples/basic_swiss.py
"""

from pairing_core import (
    CanonicalPlayer,
    CanonicalRequest,
    ConstraintSet,
    DUTCH_TILL2026_COMPAT,
    EngineRequest,
    ExecutionBudgets,
    ImpossiblePairingError,
    InvalidRequestError,
    describe_systems,
    pair,
    pair_canonical,
    pair_via,
    create_default_registry,
)


def make_players(round_state):
    """Build canonical players from (id, pairing_no, rating, points)."""
    return tuple(
        CanonicalPlayer(id=pid, pairing_no=pno, rating=rating, points=points)
        for pid, pno, rating, points in round_state
    )


def show(result, title):
    print(f"--- {title} ---")
    for board in result.pairings:
        if board.is_bye:
            print(f"board {board.board}: player {board.white_id} has the bye")
        else:
            print(f"board {board.board}: {board.white_id} (white)"
                  f" vs {board.black_id} (black)")


def main():
    print("supported systems:", describe_systems())

    # Round 1: six players, all on zero.
    players = make_players([
        (1, 1, 2000, 0.0), (2, 2, 1900, 0.0), (3, 3, 1800, 0.0),
        (4, 4, 1700, 0.0), (5, 5, 1600, 0.0), (6, 6, 1500, 0.0),
    ])
    request = CanonicalRequest(
        players=players, ruleset=DUTCH_TILL2026_COMPAT, round_number=1)
    round1 = pair_canonical(request)
    show(round1, "round 1 (canonical API)")

    # Same round via the explicit provider path (no silent fallback).
    from pairing_core import PlayerData
    engine_request = EngineRequest(
        players=[PlayerData(id=p.id, pairing_no=p.pairing_no,
                            rating=p.rating, points=p.points)
                 for p in players],
        ruleset=DUTCH_TILL2026_COMPAT,
        round_number=1,
        constraints=ConstraintSet(),
        budgets=ExecutionBudgets(max_steps=2_000_000,
                                 wall_clock_seconds=30.0),
    )
    round1_via = pair_via("native-dutch", engine_request,
                          create_default_registry())
    show(round1_via, "round 1 (provider path)")

    # Round 2: feed results back (winners get 1.0, color history recorded).
    # Board winners: white on boards 1-2, black on board 3 (arbitrary demo).
    round2_state = [
        (1, 1, 2000, 1.0), (4, 4, 1700, 0.0),
        (2, 2, 1900, 1.0), (5, 5, 1600, 0.0),
        (6, 6, 1500, 1.0), (3, 3, 1800, 0.0),
    ]
    histories = {1: "w", 4: "b", 2: "w", 5: "b", 6: "b", 3: "w"}
    opponents = {1: (4,), 4: (1,), 2: (5,), 5: (2,), 6: (3,), 3: (6,)}
    players2 = tuple(
        CanonicalPlayer(id=pid, pairing_no=pno, rating=rating, points=pts,
                        color_hist=histories[pid],
                        opponents=opponents[pid])
        for pid, pno, rating, pts in round2_state
    )
    request2 = CanonicalRequest(
        players=players2, ruleset=DUTCH_TILL2026_COMPAT, round_number=2)
    show(pair_canonical(request2), "round 2 (rolled forward)")

    # Errors are typed: an unknown ruleset fails loudly (never a silent
    # fallback), and an impossible tournament fails loudly (never a
    # partial pairing).
    from pairing_core import UnsupportedRulesetError
    try:
        bad = EngineRequest(
            players=[PlayerData(id=1, pairing_no=1, rating=2000,
                                points=0.0)],
            ruleset="no-such-ruleset", round_number=1,
            constraints=ConstraintSet())
        pair(bad)
    except (InvalidRequestError, UnsupportedRulesetError,
            ImpossiblePairingError) as exc:
        print(f"typed error (expected): {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    main()
