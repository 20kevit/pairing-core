# pairing-core

Standalone FIDE Dutch Swiss pairing engine, extracted behavior-preserving
from `20kevit/chess-manager` (`domain/pairing/`).

- No Flask, no SQLAlchemy, no persistence, no network.
- Deterministic: same input -> same output.
- Ruleset: `dutch-till2026-compat` (pre-2026 Dutch formulation as realized
  by the frozen kernel; see `docs/research/DUTCH_CONFORMANCE_STATUS.md`
  for the exact conformance standing, including confirmed deviations under
  investigation — no FIDE endorsement claimed).

## Install

```bash
pip install -e .
```

## Use

```python
from pairing_core import PlayerData, PairingRequest, NativeDutchEngine, pair_round

players = [PlayerData(id=1, pairing_no=1, rating=2000, points=0.0)]
result = pair_round(players, round_number=1)

engine = NativeDutchEngine()
result = engine.pair(PairingRequest(players=players, round_number=1))
```

## Layout

- `src/pairing_core/` — engine (models, engine, pairer, bracket, color, floats, exchange, bye, validator, api)
- `tests/` — contract/conformance tests (no Flask/SQLAlchemy)
