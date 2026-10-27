# pairing-core

Deterministic chess pairing library: one round at a time, who-plays-whom —
with boards, colours, bye/float metadata, validation, and reproducibility
envelopes, under explicitly named, dated rulesets.

[![CI](https://github.com/20kevit/pairing-core/actions/workflows/ci.yml/badge.svg)](https://github.com/20kevit/pairing-core/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Status:** the published `v0.4.1` release is immutable and available on PyPI.
> This checkout contains unreleased audit work versioned `0.4.2.dev0`; it has
> not been released, formally evaluated by FIDE, or endorsed. The CI workflow
> is configured for CPython 3.10–3.15; results are revision-specific. Python
> 3.10 reached upstream end-of-life on 2026-10-01 and remains in the matrix
> only to preserve the declared compatibility floor. See
> [`docs/audit/GAP_REGISTER.md`](docs/audit/GAP_REGISTER.md)
> and [`docs/audit/COMPLETION_STANDARD.md`](docs/audit/COMPLETION_STANDARD.md)
> for the current evidence and separate readiness verdicts.

## Why pairing-core?

Running a chess tournament requires deciding, every round, who plays whom
under intricate pairing rules. pairing-core is an independent library for
one-round pairing decisions: your application owns tournament lifecycle,
players, results and standings; pairing-core validates pairing requests and
returns deterministic results with explicit ruleset and provenance metadata.
Those engineering checks are not a proof of full FIDE-system conformance.

- **Library-first.** No server, no database, no UI. Pure Python, zero
  runtime dependencies, importable anywhere.
- **Deterministic by design.** Same request → byte-identical result,
  independent of hash seed, locale, or machine.
- **Explicit rulesets.** Every call names a dated ruleset
  (e.g. `dutch-2026`); unknown rulesets are rejected, never guessed.
- **Provider-oriented.** Native kernels and external engines (BBP, JaVaFo)
  are selected explicitly through a registry — no silent fallback.
- **Honest about FIDE.** Evidence-backed implementations with disclosed
  limitations and registered interpretations. No FIDE endorsement claimed,
  no blanket conformance claimed — ever.

## What it is / what it is not

**It is:** pairing algorithms, pairing constraints, ruleset logic, pairing
validation, deterministic pairing output, provider abstraction, execution
controls (budgets/cancellation), deterministic serialization, and
bring-your-own-binary external-engine adapters.

**It is not:** tournament management. Tournament lifecycle, player
accounts, results/standings persistence, ratings, tie-break calculation,
payments, notifications, UI, or web APIs belong to the consuming
application (e.g. `chess-manager`). See
[`docs/spec/TOURNAMENT_BOUNDARIES.md`](docs/spec/TOURNAMENT_BOUNDARIES.md).

## Key features

- Seven explicitly named Swiss rulesets (including the frozen compatibility
  ruleset), a separately dated Olympiad team-pairing ruleset, and Berger
  round robin (see table below).
- Canonical consumer API (`pair_canonical`) plus a frozen legacy API
  (v0.1.0 behavior permanently pinned by golden tests).
- Typed errors for every failure mode (`PairingError` hierarchy).
- Step budgets, wall-clock limits, and cooperative cancellation —
  pathological brackets fail with typed errors, never hangs or partials.
- Reproducibility envelopes: input digests, engine/ruleset versions,
  canonical JSON, digest-verified round-trips.
- TRF interchange subset (BBP-verified) and supervised BBP/JaVaFo
  adapters with bounded output capture and roster validation.
- Automated tests covering goldens, source-linked and adversarial cases,
  property behavior, determinism, security, performance and packaging. Test
  success is engineering evidence only; it is not external FIDE evaluation.

## Pairing systems in the current source

The ruleset identifiers below select code paths; they are not certification
or blanket conformance claims. Engineering status and system-specific
evidence are reported separately in the [gap register](docs/audit/GAP_REGISTER.md)
and [completion standard](docs/audit/COMPLETION_STANDARD.md).

| Ruleset id | System | Entry point | Scope / limitation |
|---|---|---|---|
| `dutch-till2026-compat` | Dutch, pre-2026 formulation (frozen kernel) | `pair` / `pair_canonical` | Compatibility behavior is golden-pinned; it is not the current 2026 formulation and retains documented deviations. |
| `dutch-2026` | Dutch 2026 | `pairing_core.fide2026.pair_2026` | Implementation exists; exact-search ceilings and documented rule readings remain. |
| `dubov-2026` | Dubov 2026 | `pair_2026` | Implementation exists; caller-owned ratings/history and per-system evidence limits remain. |
| `burstein-2026` | Burstein 2026 | `pair_2026` | Requires a complete externally supplied C.04 Burstein Index set and provenance after seeding; Pairing-Core does not calculate Buchholz or SB. |
| `lim-2026` | Lim 2026 | `pair_2026` | Implementation exists; documented scrutiny/ordering approximations remain. |
| `double-2026` | Double Swiss 2026 (match play) | `pair_2026` | Implementation exists; bounded next-bracket lookahead is a strategy/limitation, not proof of full conformance. |
| `team-2026` | Team Swiss 2026 | `pair_2026` | Pairing mechanics exist; event composition, lineup and score valuation are caller-owned. |
| `olympiad-2022` | Olympiad Pairing Rules | `pair_2026` | Separate dated team system; source/procedure evidence qualifications and caller-owned event facts remain. |
| `baku` helper | Accelerated Baku method | `pairing_core.fide2026.baku` | Helper only; application of acceleration and standings data remain caller responsibilities. |
| Berger round robin | Berger tables, single/double | `round_robin` | Table generation is implemented; official-example evidence is limited to the documented tests. |

Pairing-Core's tests and rule-source maps are engineering evidence, not a
FIDE checker certificate. Formal evaluation applies to a Tournament Handler
Program, a broader product than this library; Pairing-Core is not shown on
the official endorsed-program list retrieved for this audit. No endorsement
or full-system conformance is claimed.

General tie-break calculation is outside this library. `tiebreak-core` is a
separate project with a separate API; Pairing-Core has no dependency on it and
does not treat C.07 values as C.04 Burstein Index values. See the explicit
[Burstein integration boundary](docs/spec/TIEBREAK_ARCHITECTURE.md#2-current-burstein-input-contract).
Other out-of-scope capabilities include KO/playoff orchestration, ratings,
tournament management, standings and results persistence, UI, and web APIs.

## Installation

Requires Python `>=3.10`. The CI workflow matrix covers CPython 3.10–3.15;
3.10 remains for compatibility despite upstream end-of-life. Zero runtime
dependencies — a plain install pulls nothing but the library.

```bash
# Installs the latest published release (v0.4.1 at the time of writing):
pip install pairing-core
```

The `0.4.2.dev0` source in this checkout is unreleased; use an explicit
source checkout only when you intentionally want the audit branch's changes.

From source (works today):

```bash
git clone https://github.com/20kevit/pairing-core.git
cd pairing-core
pip install .
```

Development install with test tooling (pytest is an opt-in extra;
runtime stays dependency-free):

```bash
pip install -e ".[test]"
python3 -m pytest tests/ -q
```

External engines (BBP, JaVaFo) are strictly bring-your-own binaries —
never bundled, never downloaded, never auto-discovered. Their absence is
a typed error, never a silent fallback.

## Quick start

Complete runnable usage — pair round 1 of a 6-player club tournament
with the canonical API:

```python
from pairing_core import (
    CanonicalPlayer, CanonicalRequest, pair_canonical,
    DUTCH_TILL2026_COMPAT,
)

players = tuple(
    CanonicalPlayer(id=i, pairing_no=i, rating=2000 - i * 10, points=0.0)
    for i in range(1, 7)
)
request = CanonicalRequest(
    players=players, ruleset=DUTCH_TILL2026_COMPAT, round_number=1)
result = pair_canonical(request)  # RoundPairing envelope

for board in result.pairings:
    if board.is_bye:
        print(f"board {board.board}: player {board.white_id} has the bye")
    else:
        print(f"board {board.board}: {board.white_id} (white)"
              f" vs {board.black_id} (black)")
print("digest:", result.input_digest)
```

Expected output (deterministic — same input always gives this):

```text
board 1: 1 (white) vs 4 (black)
board 2: 2 (white) vs 5 (black)
board 3: 3 (white) vs 6 (black)
digest: b40a00dde2fdb…
```

The 2026 family uses its own entry point with the same shape:

```python
from pairing_core.fide2026 import (
    P26Player, P26Request, pair_2026, DUTCH_2026,
)

players = tuple(P26Player(id=i, tpn=i, rating=2000 - i * 10)
                for i in range(1, 5))
result = pair_2026(P26Request(players=players, ruleset=DUTCH_2026,
                             round_number=1))
for pair in result.pairs:
    print(pair.white_id, "vs", pair.black_id)
```

A realistic two-round example with roll-forward and error handling:
[`examples/basic_swiss.py`](examples/basic_swiss.py). A custom-provider
example: [`examples/custom_provider.py`](examples/custom_provider.py).

## Canonical API (preferred)

New integrations should use the canonical consumer contract — stable and
implementation-independent:

| Name | Kind | Purpose |
|---|---|---|
| `CanonicalPlayer` | value object | One entrant's state for one round (id, pairing number, rating, points, histories) |
| `CanonicalRequest` | value object | Players + mandatory ruleset + round number (+ optional constraints, budgets, provider hint) |
| `pair_canonical(request)` | function | Pair one round → `RoundPairing` envelope |
| `RoundPairing` | result | Boards + bye + engine/ruleset/version metadata + input digest + warnings |
| `canonical_json` | function | Canonical (key-sorted) JSON serialization |
| `explain(result, players)` | function | Structured per-board/bye explanation (preferences, score groups, validity) |
| `describe_systems()` / `KNOWN_SYSTEMS` | discovery | Supported system names and serving paths |
| `versions()` | discovery | Library/engine/ruleset/adapter/format status report |

Rulesets are mandatory and exact: a request carries a `RulesetId` or an
alias string such as `DUTCH_TILL2026_COMPAT`, resolved by
`resolve_ruleset()` — unknown identities raise `UnsupportedRulesetError`.
Caller constraints (forced/forbidden pairs) travel in a `ConstraintSet`;
anything a provider cannot honor is refused, never ignored. There is no
default ruleset to drift on.

Legacy paths (`EngineRequest` + `pair` / `pair_detailed`, `pair_round` /
`SwissEngine` / `NativeDutchEngine`) remain fully supported under the
two-minor deprecation window (O08); new code should prefer canonical.
Migration guide:
[`docs/MIGRATION_V010_TO_CANONICAL.md`](docs/MIGRATION_V010_TO_CANONICAL.md).
API tiers: [`docs/spec/API_TIERS.md`](docs/spec/API_TIERS.md).

## Providers and registry

Engines are selected explicitly — never by silent fallback:

```python
from pairing_core import EngineRequest, pair_via, create_default_registry
# ... build a validated EngineRequest ...
result = pair_via("native-dutch", request, create_default_registry())
```

- `EngineProvider`: `metadata` (`EngineMetadata`: id + version) +
  `capabilities` (rulesets, constraint flags, determinism) +
  `supports()` predicate + `pair()`.
- `Registry`: explicit registration and lookup (`create_default_registry()`
  ships the `NativeDutchProvider`). Unknown id, unsupported
  ruleset, or unhonorable constraints → typed errors, never substitution.
- **Provenance rule:** the envelope's `engine_id` names the *effective*
  engine that computed the pairing, not necessarily the selecting
  provider — a delegating provider truthfully reports what ran.
  `pair_via()` never rewrites provenance. (Spec:
  [`docs/spec/ENGINE_ABSTRACTION.md`](docs/spec/ENGINE_ABSTRACTION.md).)
- Third parties add engines without touching the core: implement
  `EngineProvider`, declare an honest `Capability`, register, select.
  Worked guide: [`examples/custom_provider.py`](examples/custom_provider.py).

## Determinism and reproducibility

Same request → byte-identical result: no RNG anywhere, sorted collection
handling, canonical JSON, input digest on every envelope. Verified by
hash-seed sweeps (`PYTHONHASHSEED` varied) and dedicated determinism
suites. To reproduce a pairing, keep the request plus the envelope's
`input_digest`, `ruleset`, and engine versions; `RoundPairing.to_dict()`
/ `from_dict()` round-trip with digest verification
(`VersionMismatchError` on corruption or schema drift).

External-engine *byte output* is outside this guarantee (their binaries,
their versions) — but the envelope records exactly which binary/version
produced a result, so provenance is never ambiguous. Contract:
[`docs/spec/DETERMINISM_CONTRACT.md`](docs/spec/DETERMINISM_CONTRACT.md).

## Execution controls

Every pairing run is bounded:

```python
from pairing_core import ExecutionBudgets, CancelToken, EngineRequest, pair

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
- A bounded run NEVER returns a partial pairing as success: success is
  complete and valid; failure is typed plus diagnostics.
- Exact-search ceilings (large dense brackets) are a documented policy,
  not a bug: [`docs/audit/SEARCH_CEILING_POLICY.md`](docs/audit/SEARCH_CEILING_POLICY.md).

## Error handling

All failures are typed `PairingError` subclasses (also `ValueError`
compatible for legacy callers):

| Error | Meaning |
|---|---|
| `InvalidRequestError` | Malformed request (bad round, bad histories, bad serialization) |
| `InvalidPlayerError` | Invalid player data |
| `DuplicatePlayerIdError` | Two players share an id |
| `ImpossiblePairingError` | No legal pairing exists (incl. external engine exit 1) |
| `EngineTimeoutError` | Step budget or wall-clock budget exhausted |
| `CancelledError` | Run cancelled via `CancelToken` |
| `EngineUnavailableError` | Missing/unusable external binary, failed version probe |
| `UnsupportedRulesetError` | Unknown ruleset or engine that lacks it |
| `UnsupportedCapabilityError` | Honest refusal of unhonorable constraints |
| `VersionMismatchError` | Schema/digest mismatch on deserialization |
| `InternalError` | Engine-output faults, cap violations, unexpected states |

`validate_request()` rejects malformed input at the boundary;
`validate_round()` independently checks any result.

## External engines (BBP / JaVaFo)

Bring-your-own binaries at the adapter edge (`pairing_core.adapters`):
supervised subprocess (argv only, no shell), required timeouts,
10 MiB per-stream output caps enforced *during* collection, strict UTF-8,
TRF interchange (BBP-verified subset), and roster validation of every
external result. On POSIX each run is isolated and timeout/output-overflow
cleanup terminates its process group; on Windows the standard-library
fallback guarantees direct-child cleanup only. Nothing is vendored,
downloaded, or PATH-searched.

`versions()` reports adapters truthfully as `adapter-edge` (code exists
with BYO/limit qualifications) rather than `implemented` or
`not-implemented`.

## Evidence, conformance and limitations

The official sources and effective dates, direct source retrieval, known
interpretations, implementation strategies and unresolved system limitations
are tracked in the current [audit gap register](docs/audit/GAP_REGISTER.md).
Older conformance matrices and closure reports are historical project
records, not independent or current certification evidence. The gap register
and [completion standard](docs/audit/COMPLETION_STANDARD.md) govern the
current readiness statements.

> Pairing-Core does not claim FIDE endorsement, certification, approval,
> blanket conformance, or formal FIDE evaluation.

The official FIDE Endorsed Programs PDF retrieved for this audit does not
list Pairing-Core. No later decision naming this product was found in the
sources searched; this is not an exhaustive proof that no later decision
exists. A successful local test suite is not a FIDE checker certificate.

Known, material limits include:

- **Burstein integration:** after Dutch seeding rounds, `pair_2026` requires
  a complete per-player `BursteinIndexSet` with source provenance. Pairing-Core
  does not calculate Buchholz or Sonneborn–Berger. The separate
  `tiebreak-core` library exposes C.07 values, which are not treated as C.04
  values without separately verified semantic equivalence.
- **Exact-search ceilings:** dense Dutch/Burstein brackets may terminate with
  a typed timeout rather than a pairing; no heuristic result is substituted.
- **Double/Team:** next-bracket lookahead is a documented implementation
  strategy/limitation and not proof of full criterion conformance.
- **Lim:** documented scrutiny/order approximations and unresolved readings
  remain; see the gap register.
- **Olympiad:** distinct 2022 source/evidence posture and caller-owned event
  facts remain; see the gap register.
- **Frozen compatibility ruleset:** it preserves historic behavior and
  documented deviations; it is not the current 2026 FIDE formulation.

## Architecture

```mermaid
flowchart TD
    App[Application: players, results, rounds] --> CA[Canonical API: pair_canonical]
    CA --> REQ[Request + dated Ruleset]
    REQ --> REG[Provider Registry: explicit selection]
    REG --> NAT[Native providers]
    REG --> EXT[External adapters: BBP / JaVaFo BYO]
    NAT --> ENV[Validated RoundPairing envelope]
    EXT --> ENV
    ENV --> OUT[Deterministic result + canonical JSON]
```

- **Core/domain** (`engine`, `bracket`, `pairer`, `color`, `floats`,
  `exchange`, `bye`, `validator`): pairing search and legality. Internal.
- **Ruleset data** (`rulesets`, `fide2026/models`): dated identities,
  constraints, value models.
- **Provider layer** (`api`, `provider`, `registry`, `canonical`): the
  stable consumer contract; explicit routing, no fallback.
- **Adapters** (`adapters/`): TRF interchange + supervised subprocess
  execution. Never imported by core (import-lint enforced).
- **Reproducibility** (`envelope`): digests, versions, canonical
  serialization with digest verification.
- **I/O boundary:** callers pass data in, get values out. The only
  processes ever spawned are caller-nominated external-engine binaries.

## Testing and quality

Published v0.4.1 audit baseline: **527 passed, 16 skipped** on Python 3.11.
That is not the test result for this unreleased `0.4.2.dev0` source checkout;
current verification results are reported separately. Coverage is described
by behavior, not percentage:

- Frozen v0.1.0 goldens (41) + contract tests — behavior can never
  silently drift.
- Official-example corpus + rule-traceability tests.
- Hostile/adversarial suites (conformance attacks, output flooding,
  malicious engine output, malformed TRF).
- Seeded property tests across the seven `fide2026` entry-point systems:
  six 2026 C.04 systems and the separately dated `olympiad-2022` ruleset.
- Hash-seed determinism sweeps.
- Env-gated BBP/JaVaFo live differentials.
- Performance gates (ordinary + pathological sizes, bounded-failure
  assertions, no hard timing asserts).
- Release gates (product files, metadata/catalog consistency, examples,
  zero-dependency contract, clean-tree).

CI is configured to run this suite on CPython 3.10–3.15, then builds,
inspects, and smoke-tests install artifacts. The exact revision's CI result,
not the matrix declaration, is the evidence of a passing interpreter.

## Security

- External binaries: argv-only, no shell, explicit paths, required
  timeouts, POSIX process-group cleanup with TERM grace then KILL,
  10 MiB/stream caps enforced during collection, strict UTF-8, temp-dir
  cleanup. Windows currently guarantees direct-child cleanup only.
- External results: syntax-checked *and* roster-validated (unknown,
  duplicate, self-paired, multi-bye, incomplete → `InternalError`).
- Exact search: step budgets + wall-clock limits; ceilings raise typed
  errors; partials never escape as success.
- Inputs: strict validation boundaries with typed errors; linear TRF
  grammar; no network, no persistence, no secrets, no unsafe
  deserialization.
- Zero runtime dependencies — minimal supply-chain surface.

Full policy and reporting:
[`SECURITY.md`](SECURITY.md).

## Documentation map

- Start: this README, [`docs/INDEX.md`](docs/INDEX.md),
  [`examples/`](examples/) (`basic_swiss.py`, `custom_provider.py`).
- Product: [`docs/CAPABILITY.md`](docs/CAPABILITY.md),
  [`docs/audit/GAP_REGISTER.md`](docs/audit/GAP_REGISTER.md) (current audit
  authority), [`docs/audit/COMPLETION_STANDARD.md`](docs/audit/COMPLETION_STANDARD.md),
  [`CHANGELOG.md`](CHANGELOG.md),
  [`docs/spec/TOURNAMENT_BOUNDARIES.md`](docs/spec/TOURNAMENT_BOUNDARIES.md).
- Contracts: [`docs/spec/API_TIERS.md`](docs/spec/API_TIERS.md),
  [`docs/spec/ENGINE_ABSTRACTION.md`](docs/spec/ENGINE_ABSTRACTION.md),
  [`docs/spec/DETERMINISM_CONTRACT.md`](docs/spec/DETERMINISM_CONTRACT.md),
  [`docs/audit/SEARCH_CEILING_POLICY.md`](docs/audit/SEARCH_CEILING_POLICY.md).
- Evidence: [`docs/audit/FIDE_CONFORMANCE_MATRIX.md`](docs/audit/FIDE_CONFORMANCE_MATRIX.md),
  [`docs/audit/FIDE_CONFORMANCE_CLOSURE_REPORT.md`](docs/audit/FIDE_CONFORMANCE_CLOSURE_REPORT.md),
  [`docs/rules/fide/RULE_SOURCE_MATRIX.md`](docs/rules/fide/RULE_SOURCE_MATRIX.md).
- Process: [`CONTRIBUTING.md`](CONTRIBUTING.md),
  [`docs/spec/VERSIONING.md`](docs/spec/VERSIONING.md),
  [`docs/RELEASING.md`](docs/RELEASING.md),
  [`docs/spec/TESTING_STRATEGY.md`](docs/spec/TESTING_STRATEGY.md).

## Development

```bash
pip install -e ".[test]"    # editable install + test tooling
python3 -m pytest tests/ -q # full suite; oracles skip without BYO
                            # binaries (BBP_EXE / JAVAFO_JAR)
PAIRING_UPDATE_BASELINES=1 python3 -m pytest tests/test_benchmarks.py -q
```

Benchmark refresh is opt-in so plain runs never dirty the tree. See
[`CONTRIBUTING.md`](CONTRIBUTING.md) (evidence-first workflow, regression
test per bug, linear history on `main`).

## Contributing

Contributions welcome within the product boundary (pairing decisions,
not tournament management). Read [`CONTRIBUTING.md`](CONTRIBUTING.md)
first: scope rules, O08 compatibility policy, no-endorsement rule.
Security issues: [`SECURITY.md`](SECURITY.md) (private advisory, no
public issue for live vulnerabilities).

## Versioning and release policy

Semver library version plus four independent axes (engine, ruleset,
external-engine, input format) —
see [`docs/spec/VERSIONING.md`](docs/spec/VERSIONING.md). The v0.1.0
kernel behavior is a permanent golden reference. Public API follows a
two-minor deprecation window (O08). Releases are cut manually from a
clean `main` per [`docs/RELEASING.md`](docs/RELEASING.md);
`CHANGELOG.md` records every version.

## License

MIT — see [`LICENSE`](LICENSE). External engine binaries stay
bring-your-own under their own licenses; nothing GPL is vendored.