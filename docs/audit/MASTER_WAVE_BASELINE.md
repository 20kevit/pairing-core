# Master Wave — Forensic Baseline (Phase A)

Starting commit: `ff50dac` (`docs: finalize capability wave with roadmap and report`).
Branch: `main`. Working tree: clean (one test-run artifact in
`tests/data/benchmarks/baseline.json` observed and reverted — benchmark
durations are machine-dependent, not a source change). Remote:
`git@github.com:20kevit/pairing-core.git`. Tag: `v0.1.0` (= `2cb570b`).
History: linear, no rewrite, no force-push. Verified 2026-10-03.

Test baseline at `ff50dac`: **247 passed, 10 skipped, 0 failed**
(`python3 -m pytest tests -x -q`; skips are env-gated heavy/oracle suites
with recorded reasons).

## 1. Source tree (`src/pairing_core/`)

| Module | Role |
|---|---|
| `models.py` | Domain I/O (`PlayerData`/`PlayerSnapshot`, `PairingCard`, `RoundResult`) + internal `EnginePlayer`/`ColorPref`/`ColorState`/`FloatStatus` |
| `engine.py` | `SwissEngine` (frozen v0.1.0 kernel) + `pair_round()`; accepts legacy donor objects via `_normalize_input` |
| `api.py` | `PairingRequest`, `PairingEngine` ABC, `NativeDutchEngine`; F2 `EngineRequest`, `pair`, `pair_detailed`, `pair_via`, `validate_request`, `versions` |
| `rulesets.py` | `RulesetId`, `ConstraintSet`, `DUTCH_TILL2026_COMPAT`, `resolve_ruleset` (exact-match only) |
| `errors.py` | 11-class typed taxonomy, `PairingError(ValueError)` base, `translate_kernel_error` |
| `envelope.py` | `Pairing`, `RoundPairing` success-only values, canonical JSON + sha256, `from_kernel` O02 guard |
| `controls.py` | `ExecutionBudgets` (step primary, wall-clock secondary), `CancelToken` |
| `provider.py` | `EngineProvider` ABC, `Capability`, `EngineMetadata`, `NativeDutchProvider` (thin wrapper, no second implementation) |
| `registry.py` | `Registry` (explicit, no fallback/discovery) + `create_default_registry()` |
| `roundrobin.py` | Standalone Berger schedules (NOT a provider — fixed table, no search) |
| `explain.py` | `explain()` output-derived explanations, no search internals |
| `validator.py` | Independent legality checker (error/warning/info codes) |
| `bye.py`, `bracket.py`, `pairer.py`, `color.py`, `floats.py`, `exchange.py` | Internal Dutch machinery (not consumer contracts) |
| `adapters/trf.py` | TRF(x) subset at adapter edge (BBP-shape verified); never imported by core domain |
| `adapters/bbp.py`, `adapters/javafo.py`, `adapters/_process.py` | BYO-binary execution + conversion layers; explicit configs, no discovery |
| `harness/compare.py`, `harness/corpus.py` | 11-class differential taxonomy + 23-case corpus |

## 2. Public surfaces (from `__init__.py`, 51 `__all__` entries + submodules)

- Domain I/O: `PlayerData` (= `PlayerSnapshot`), `PairingCard`, `RoundResult`.
- Legacy engine: `pair_round`, `SwissEngine`, `validate_round`, `ValidationReport`, `Finding`.
- Abstraction: `PairingRequest`, `PairingEngine`, `NativeDutchEngine`.
- Validated path: `EngineRequest`, `pair`, `pair_detailed`, `pair_via`, `validate_request`, `versions`.
- Rulesets: `RulesetId`, `ConstraintSet`, `resolve_ruleset`, `DUTCH_TILL2026_COMPAT`.
- Envelope: `Pairing`, `RoundPairing`.
- Controls: `ExecutionBudgets`, `CancelToken`.
- Provider/registry: `EngineProvider`, `NativeDutchProvider`, `Capability`, `EngineMetadata`, `Registry`, `create_default_registry`.
- Round robin: `round_robin`. Explain: `explain`, `Explanation`, `BoardExplanation`, `ByeExplanation`.
- Errors: all 11 taxonomy classes. Versions: `__version__ = "0.1.0"`.
- Submodule surfaces (importable, not top-level): `adapters.{trf,bbp,javafo}`, `harness.{compare,corpus}`.

## 3. Key findings for this wave

1. **No canonical contract exists yet.** `EngineRequest` still carries
   `PlayerData` (a v0.1.0 domain record) and has no pairing-system field, no
   request schema version, and no provider-selection hint. The mission
   requires the canonical API to be independent of `SwissEngine` /
   `PlayerData` / `NativeDutchEngine` — so Phase B must add an
   implementation-independent request/player model with converters, keeping
   `EngineRequest` as a supported (legacy-stable) path.
2. **Legacy compatibility is already structurally sound**: frozen kernel,
   41 goldens + 15 contract tests pin v0.1.0 behavior; `translate_kernel_error`
   preserves messages. Phase C work is documentation + adapter framing, not
   rescue.
3. **Determinism is implemented but not contracted in one place**: sorted
   canonical paths, seeded property tests, hash-seed sweeps exist; the exact
   guarantee scope needs a single contract document (Phase D).
4. **API tiers are recorded** (`docs/audit/PUBLIC_API.md` §4) but there is no
   import-boundary test enforcing public/internal separation (Phase F).
5. **Packaging**: `pyproject.toml` version `0.1.0`, setuptools, no runtime
   dependencies, `requires-python >=3.10`. Version source of truth is split
   between `pyproject.toml` and `__init__.__version__` (both `0.1.0` today —
   consistent but unchecked by any test).
6. **Blocked systems** (Dutch-2026, Dubov, Burstein, Lim, C.04.6 TPS, KO/match)
   remain blocked for the documented reasons in `docs/CAPABILITY.md` — no new
   authoritative text is available in this environment (no network retrieval
   attempted beyond what prior waves recorded; nothing in-repo changes that
   standing). They stay BLOCKED and must not gate this wave.
