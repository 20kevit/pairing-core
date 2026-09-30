# pairing-core

Standalone FIDE Dutch Swiss pairing engine, extracted behavior-preserving
from `20kevit/chess-manager` (`domain/pairing/`).

- No Flask, no SQLAlchemy, no persistence, no network.
- Deterministic: same input -> same output.
- Reference: FIDE C.04.2 + C.04.3 (effective 1 July 2025).

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
