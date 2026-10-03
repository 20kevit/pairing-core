# Migration Guide: v0.1.0 → Canonical API

Deprecation policy (per O08): the v0.1.0 surface stays supported for a
minimum of two minor releases. Nothing below is removed or changed; the
canonical API is purely additive. Compatibility tests (`test_v010_behavioral`,
goldens) remain permanent.

## Old imports → new imports

```python
# v0.1.0 (still supported)
from pairing_core import PlayerData, SwissEngine, pair_round

# Canonical (new)
from pairing_core import (
    CanonicalPlayer, CanonicalRequest, pair_canonical,
    DUTCH_TILL2026_COMPAT, ConstraintSet,
)
```

## Old request → new request

```python
# v0.1.0
players = [PlayerData(id=1, pairing_no=1, rating=2000, points=0.0)]
engine = SwissEngine(players, round_number=1)
result = engine.generate()          # RoundResult
# or: result = pair_round(players, round_number=1)

# Canonical
players = [CanonicalPlayer(id=1, pairing_no=1, rating=2000, points=0.0)]
request = CanonicalRequest(players=tuple(players),
                           ruleset=DUTCH_TILL2026_COMPAT,
                           round_number=1)
result = pair_canonical(request)    # RoundPairing (envelope)
```

For existing `PlayerData` lists, adapt without rebuilding by hand:

```python
players = tuple(CanonicalPlayer.from_legacy(p) for p in legacy_players)
```

## Old result handling → new result handling

- `RoundResult.pairings` (`PairingCard`: `board/white_id/black_id/is_bye/...`)
  maps 1:1 onto `RoundPairing.pairings` (`Pairing`: same fields).
- New envelope adds: `engine_id/engine_version`, `ruleset`, `library_version`,
  `input_digest`, `warnings`, `budgets`, `digest`. Verify with
  `RoundPairing.from_dict(d)` / `to_dict()`.
- Failures: the frozen kernel raises plain `ValueError`; the canonical path
  raises the typed taxonomy (`InvalidRequestError`, `ImpossiblePairingError`,
  `EngineTimeoutError`, …) which subclasses `ValueError` — existing
  `except ValueError` handlers keep working, and callers can now branch on
  precise types.

## Semantic differences

1. `ruleset` is mandatory (was implicit). Pass `DUTCH_TILL2026_COMPAT`.
2. Locked pairs are expressed as `ConstraintSet(forced_pairs=...)`.
3. Forbidden pairs are enforced (rematch-equivalent); bye directives are
   refused, not ignored.
4. `pair_canonical` never returns partial pairings (O02); impossible states
   raise `ImpossiblePairingError`.
5. Deterministic output is contractually guaranteed (see
   `docs/spec/DETERMINISM_CONTRACT.md`).

## Deprecation timeline

- `v0.1.0` (`2cb570b`): baseline. Supported indefinitely per O08 window.
- Current development: canonical API additive; no deprecation warnings
  emitted (nothing is deprecated yet — the legacy surface is *stable*, the
  canonical surface is *preferred*).
- Earliest any legacy removal could be proposed: two minor releases after
  a deprecation notice is issued. No notice is issued in this wave.
