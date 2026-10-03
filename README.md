# pairing-core

Standalone FIDE Dutch Swiss pairing engine, extracted behavior-preserving
from `20kevit/chess-manager` (`domain/pairing/`).

- No Flask, no SQLAlchemy, no persistence, no network.
- Deterministic: same input -> same output.
- Ruleset: `dutch-till2026-compat` (pre-2026 Dutch formulation as realized
  by the frozen kernel; see `docs/research/DUTCH_CONFORMANCE_STATUS.md`
  for the exact conformance standing, including confirmed deviations under
  investigation — no FIDE endorsement claimed).
- Also: Berger round-robin schedules (`round_robin`, validated against
  FIDE C.05 Annex 1), typed errors, dated rulesets, execution budgets,
  BBP/JaVaFo adapter edge (bring-your-own binaries), TRF interchange.
- 2026 family (`pairing_core.fide2026`, v0.3.0+): `dutch-2026`, `dubov-2026`,
  `burstein-2026`, `lim-2026`, `double-2026`, `team-2026`, `olympiad-2022`,
  Baku modifier — implemented from FULL_TEXT Council-bundle evidence
  (see `docs/rules/fide/evidence/`); frozen `dutch-till2026-compat` untouched.

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

Preferred canonical API (implementation-independent; see
`docs/MIGRATION_V010_TO_CANONICAL.md`):

```python
from pairing_core import (
    CanonicalPlayer, CanonicalRequest, pair_canonical,
    DUTCH_TILL2026_COMPAT,
)

players = (CanonicalPlayer(id=1, pairing_no=1, rating=2000, points=0.0),)
request = CanonicalRequest(players=players,
                           ruleset=DUTCH_TILL2026_COMPAT,
                           round_number=1)
result = pair_canonical(request)  # RoundPairing envelope
```

## Layout

- `src/pairing_core/` — engine (models, engine, pairer, bracket, color, floats, exchange, bye, validator, api)
- `tests/` — contract/conformance tests (no Flask/SQLAlchemy)
