# pairing-core

Deterministic tournament-pairing library for chess: one round at a time,
who-plays-whom, with boards, colours, bye/float metadata, validation, and
reproducibility envelopes — under explicitly named, dated rulesets.

- Zero runtime dependencies; pure Python, `>=3.10`.
- Deterministic: same input → same output (hash-seed independent).
- No FIDE endorsement claimed; no blanket conformance claimed. Explicit
  interpretations are registered in
  `docs/audit/FIDE_CONFORMANCE_MATRIX.md`.
- Current version `0.4.1` is a release candidate (committed on `main`,
  not yet tagged or published — see `docs/RELEASING.md`).

## Scope

pairing-core owns **pairing decisions**: pairing algorithms, pairing
constraints, ruleset logic, pairing validation, deterministic pairing
output, the provider abstraction, execution controls, and external-engine
adapters.

It does **not** own tournament management: tournament lifecycle, players,
results/standings, rounds persistence, permissions, UI, payments,
notifications, ratings, or general tie-break calculation. Those belong to
the caller (e.g. `chess-manager`). See
`docs/spec/TOURNAMENT_BOUNDARIES.md`.

## Supported pairing systems (v0.4.1)

| Ruleset id | System | Entry point |
|---|---|---|
| `dutch-till2026-compat` | Dutch, pre-2026 formulation (frozen kernel; behavior pinned by 41 goldens) | `pair` / `pair_canonical` |
| `dutch-2026` | Dutch 2026 (C1–C21 criteria search) | `pairing_core.fide2026.pair_2026` |
| `dubov-2026` | Dubov 2026 | `pair_2026` |
| `burstein-2026` | Burstein 2026 | `pair_2026` |
| `lim-2026` | Lim 2026 | `pair_2026` |
| `double-2026` | Double Swiss 2026 (match play) | `pair_2026` |
| `team-2026` | Team Swiss 2026 | `pair_2026` |
| `olympiad-2022` | Olympiad Pairing Rules | `pair_2026` |
| `baku` modifier | Accelerated Baku method | `pair_2026` (modifier) |
| Berger round robin | C.05 Annex 1 tables, single/double | `round_robin` |

Not supported (out of scope with reason): KO/match/playoff orchestration,
tiebreak-core, tournament-core, ratings, REST API, frontend, database.
Current capability authority: `docs/CAPABILITY.md`. Known limitations
(L1/L3/L4/L5, I-L-412) are disclosed in
`docs/audit/FIDE_CONFORMANCE_CLOSURE_REPORT.md` §L.

## Installation

```bash
pip install pairing-core   # once published (0.4.1 is not on PyPI yet)
```

From source (works today):

```bash
pip install .
```

Requires Python `>=3.10`. No runtime dependencies. External engines
(BBP, JaVaFo) are strictly bring-your-own binaries — never bundled, never
auto-discovered; their absence is a typed error, never a silent fallback.

## Minimal usage

```python
from pairing_core import (
    CanonicalPlayer, CanonicalRequest, pair_canonical,
    DUTCH_TILL2026_COMPAT,
)

players = (
    CanonicalPlayer(id=1, pairing_no=1, rating=2000, points=0.0),
    CanonicalPlayer(id=2, pairing_no=2, rating=1900, points=0.0),
    CanonicalPlayer(id=3, pairing_no=3, rating=1800, points=0.0),
    CanonicalPlayer(id=4, pairing_no=4, rating=1700, points=0.0),
)
request = CanonicalRequest(
    players=players, ruleset=DUTCH_TILL2026_COMPAT, round_number=1)
result = pair_canonical(request)  # RoundPairing envelope
for board in result.pairings:
    print(board.board, board.white_id, board.black_id, board.bye_id)
```

The 2026 family uses its own entry point:

```python
from pairing_core.fide2026 import (
    P26Player, P26Request, pair_2026, DUTCH_2026,
)

players = tuple(P26Player(id=i, tpn=i, rating=2000 - i * 10) for i in range(1, 5))
result = pair_2026(P26Request(players=players, ruleset=DUTCH_2026, round_number=1))
```

A realistic multi-step example lives in `examples/basic_swiss.py`.

## Canonical API

New integrations should use the canonical consumer contract, which is
stable and implementation-independent:

- `CanonicalPlayer` / `CanonicalRequest` — value objects (ruleset mandatory,
  never defaulted).
- `pair_canonical(request)` — pair one round, return a `RoundPairing`
  envelope (pairings + engine/ruleset/version metadata + input digest).
- `canonical_json` — canonical (key-sorted) JSON serialization.
- `describe_systems()` / `KNOWN_SYSTEMS` — supported system names.
- Migration from the legacy API:
  `docs/MIGRATION_V010_TO_CANONICAL.md`.

Lower-level paths (`EngineRequest` + `pair` / `pair_detailed`, legacy
`pair_round` / `SwissEngine`) remain supported under the O08 compatibility
policy (two-minor deprecation window). API tiers:
`docs/spec/API_TIERS.md`.

## Providers and registry

Engines are selected explicitly — never by silent fallback:

```python
from pairing_core import EngineRequest, pair_via, create_default_registry
# ... build request ...
result = pair_via("native-dutch", request, create_default_registry())
```

Unknown provider id, ruleset, or capability raises a typed error
(`EngineUnavailableError`, `UnsupportedRulesetError`,
`UnsupportedCapabilityError`). Result metadata records requested engine,
actual engine, reason, versions, and ruleset. To add your own engine
without touching the core, see `examples/custom_provider.py`.

## Determinism

Same request → byte-identical result: no RNG, sorted collection handling,
canonical JSON, input digests on every envelope. Verified by hash-seed
sweeps and determinism suites. External-engine byte output is outside this
guarantee (their binaries, their versions); the envelope records exactly
which binary/version produced a result. Contract:
`docs/spec/DETERMINISM_CONTRACT.md`.

## Execution controls

Every pairing run is bounded:

```python
from pairing_core import ExecutionBudgets, CancelToken
from pairing_core import EngineRequest, pair

budgets = ExecutionBudgets(max_steps=200_000, wall_clock_seconds=30.0)
token = CancelToken()  # any thread may call token.cancel()
request = EngineRequest(players=..., ruleset=..., round_number=...,
                        constraints=..., budgets=budgets,
                        cancel_token=token)
```

- Step budget (primary, deterministic): exhaustion → `EngineTimeoutError`.
- Wall-clock budget (secondary, polled at deterministic checkpoints):
  expiry → `EngineTimeoutError` (environment-dependent, not replayable).
- Cancellation → `CancelledError`.
- A bounded run NEVER returns a partial pairing as success (O02):
  success is complete and valid, failure is typed + diagnostics.
- Exact-search ceilings (large dense brackets) are a documented policy,
  not a bug: `docs/audit/SEARCH_CEILING_POLICY.md`.

## Error handling

All failures are typed `PairingError` subclasses (also `ValueError`
compatible for legacy callers): `InvalidRequestError`,
`InvalidPlayerError`, `DuplicatePlayerIdError`, `ImpossiblePairingError`,
`EngineTimeoutError`, `CancelledError`, `EngineUnavailableError`,
`UnsupportedCapabilityError`, `UnsupportedRulesetError`,
`VersionMismatchError`, `InternalError`. `validate_request()` rejects
malformed input at the boundary; `validate_round()` independently checks
any result.

## External engines (BBP / JaVaFo)

Bring-your-own binaries at the adapter edge (`pairing_core.adapters`):
supervised subprocess (argv only, no shell), required timeouts,
kill-after-grace, 10 MiB output caps, strict UTF-8, TRF interchange
(BBP-verified subset). Nothing is vendored, downloaded, or PATH-searched.

## Development and testing

```bash
pip install -e ".[test]"    # editable install + test tooling (pytest is an
                            # opt-in extra; runtime stays dependency-free)
python3 -m pytest tests/ -q # full suite (~500 tests; oracle tests skip
                            # without BYO binaries: BBP_EXE / JAVAFO_JAR)
PAIRING_UPDATE_BASELINES=1 python3 -m pytest tests/test_benchmarks.py -q
```

Benchmark baseline refresh is opt-in so plain runs never dirty the tree.
Release gate (CI): tests + build + artifact inspection + import smoke +
determinism checks. Release process: `docs/RELEASING.md`.

## Versioning

Semver library version plus four independent axes (engine, ruleset,
external-engine, input format) — see `docs/spec/VERSIONING.md`. The v0.1.0
kernel behavior is a permanent golden reference (41 goldens + contract
tests must stay green). Changelog: `CHANGELOG.md`.

## Known limitations (v0.4.1)

- **L1** — exact-search factorial ceilings (Dutch/Burstein big brackets):
  typed timeouts, no heuristic pruning.
- **L3** — Double/Team full-C3 lookahead beyond the next bracket is a
  documented policy approximation.
- **L4** — Lim 4.2 #2-row interleaving exactness is a documented
  approximation.
- **L5** — Olympiad source PDF per se unobtained; retrieved chapter text
  (§§1–11) is complete and sufficient.
- **I-L-412** — Lim upward-search shape is a genuine ambiguity; exact
  mirror adopted as the deterministic default.
- Frozen compat deviations (E.5 round-1 parity colours, absolute 3rd-float
  bar): confirmed, intentionally frozen per O08.

## What "FIDE" means here

Rulesets are named after the FIDE Handbook articles they implement, with
effective dates, and every rule maps to source → code → test
(`docs/rules/fide/RULE_SOURCE_MATRIX.md`). This project is an independent
implementation with disclosed interpretations and limitations — it is not
FIDE-endorsed, FIDE-certified, or guaranteed fully conformant anywhere an
interpretation is registered.

## Contributing / security / license

- Contributing: `CONTRIBUTING.md`
- Security policy: `SECURITY.md`
- Code of conduct: `CODE_OF_CONDUCT.md`
- License: MIT (`LICENSE`)
