# Foundation Implementation Blueprint (FINAL — awaiting implementation approval)

Phase: Foundation (Roadmap Phase 1, O07). Scope: everything needed before any
Dutch-conformance work. Nothing here is implemented; file names are PROPOSED
additions grounded in the VERIFIED current tree.

## A. Current state (v0.1.0, SHA 2cb570b + docs commit)

- API: `pair_round`, `SwissEngine`, `NativeDutchEngine`, `PairingRequest`,
  `PlayerData/PairingCard/RoundResult`, `validate_round`, `ValidationReport/
  Finding` (`src/pairing_core/__init__.py` `__all__`, 14 names).
- Modules: `api, models, engine, bracket, pairer, color, floats, exchange,
  bye, validator` (10); tests: `tests/test_contract.py` (15 tests, green).
- Known limitations (binding): silent input absorption, ValueError-only errors,
  inert rating, silent `status` filter, id-equality hazard, greedy bye, no TRF/
  CLI/benchmarks, pre-2026 formulation (see `docs/audit/`).
- Compatibility constraints: 14-name surface + observable behaviours (round-1
  shapes, bye-last boards, fresh-first bye, determinism, ValueError signals)
  frozen by the permanent golden harness (O08).

## B. Target architecture (dependency graph)

```
pairing_core.errors        (NEW, leaf: no intra-package imports)
pairing_core.rulesets      (NEW: RulesetId, ConstraintSet, default table; imports errors)
pairing_core.envelope      (NEW: digests, replay/verify; imports errors[, rulesets])
pairing_core.provider      (NEW: EngineProvider/Metadata/Capabilities/modes; imports errors,rulesets,envelope)
pairing_core.registry      (NEW: lookup, defaults, fallback resolution; imports provider)
pairing_core.api           (MODIFY additive: new request/result re-exports; old names kept)
pairing_core.{models,engine,bracket,pairer,color,floats,exchange,bye,validator}
                           (FROZEN in Foundation: behaviour-identical; engine.py gets
                            additive budget-checkpoint plumbing only, defaults = current 2M cap)
pairing_core.adapters.*    (NOT in Foundation — Dutch phase; contract specified in §H)
tests/test_contract.py     (UNTOUCHED — must stay green)
tests/test_v010_*.py etc.  (NEW harness — §F)
```

Rules: core imports stdlib only (adapters later live in opt-in extras);
registry never imports adapters (entry-point/lazy mapping); tests never import
chess-manager (synthetic fixtures only); TRF types never cross into core
(import-lint test).

## C. File-level plan

| File | Action | Why |
|---|---|---|
| `src/pairing_core/errors.py` | CREATE | typed taxonomy ends ValueError-only (R-ERR-01/O02/O10) |
| `src/pairing_core/rulesets.py` | CREATE | dated RulesetIds + ConstraintSet + default table (O03/D13) |
| `src/pairing_core/envelope.py` | CREATE | replay envelopes + digests + verify (C-REP-01) |
| `src/pairing_core/provider.py` | CREATE | EngineProvider/Metadata/Capabilities + 3 request modes (O01/O03) |
| `src/pairing_core/registry.py` | CREATE | lookup, capability filter, explicit-fallback resolution + metadata (O03) |
| `src/pairing_core/api.py` | MODIFY additive | new request/result/registry re-exports; zero removals/renames |
| `src/pairing_core/__init__.py` | MODIFY additive | export new names; keep all 14 v0.1.0 names |
| `src/pairing_core/engine.py` | MODIFY additive | step-budget + wall-clock checkpoints (defaults preserve behaviour) |
| `models/bracket/pairer/color/floats/exchange/bye/validator.py` | UNTOUCHED | kernel frozen under harness until Dutch phase |
| `tests/test_contract.py` | UNTOUCHED | v0.1.0 contract witness |
| `tests/test_v010_behavioral.py` etc. | CREATE (§F) | harness before changes (Stage-1 lesson) |
| `pyproject.toml`, packaging, deps | UNTOUCHED | out of scope for Foundation code (release policy doc-level) |

## D. Public API (proposed; status-marked)

- `EngineRequest(players, round, ruleset, constraints, seed, budgets, cancel,
  mode, diagnostics)` — PUBLIC (new; `PairingRequest` kept + wrapped).
- `RoundPairing(pairings, bye, envelope, warnings)` + `Pairing` — PUBLIC.
- `EngineProvider.pair / capabilities / versions` + `EngineMetadata` — PUBLIC.
- `Capability` model (system/ruleset/bye/seed/constraints/TRF/team/RR flags) —
  PUBLIC (queryable), INTERNAL (matching internals).
- `RulesetId(system, effective_date, acceleration, point_profile)` — PUBLIC;
  default table — PUBLIC data, versioned.
- `PairingError` hierarchy (`ImpossiblePairing, InvalidInput(+subclasses),
  EngineUnavailable, EngineTimeout, Cancelled, UnsupportedCapability,
  VersionMismatch, InternalError`) — PUBLIC.
- `Registry lookup/select/defaults` — PUBLIC; standby-fallback resolution —
  PUBLIC with mandatory metadata.
- Reproducibility envelope + `replay/verify/envelope_diff` — PUBLIC.
- Timeout/cancel (`budgets{wall_clock, steps}`, cancel token) — PUBLIC.
- Diagnostics schema (criteria costs, provenance, frontier summaries) —
  EXPERIMENTAL (non-contractual detail).
- Checker-mode/TRF/adapters/tiebreak-consumption — DEFERRED (Dutch phase+).

## E. v0.1.0 migration map (no accidental breakage)

`pair_round` → preserved (delegates to default-mode provider call; identical
output); `SwissEngine` → preserved class, additive budget params;
`NativeDutchEngine` → preserved, registered as `native-dutch` provider;
`PlayerData/PairingCard/RoundResult` → preserved (new `Pairing/RoundPairing`
are siblings, not renames); `validate_round` → preserved; `ValueError`
raise-sites → preserved in compat path, new paths raise typed errors;
`PlayerSnapshot` → preserved alias (tier decision: keep, document);
`validate_and_fix` → preserved, documented legacy (misnomer noted, not renamed
in Foundation). Changed/removed: NOTHING in Foundation.

## F. Test plan (Foundation-mandatory)

v0.1.0 compatibility goldens (shapes, boards, colours, byes, float tags,
validator verdicts, determinism incl. input permutation + hash-seed variation);
API snapshot; input-validation adversarial suite; impossible-state suite
(typed, with diagnostics assertions); timeout (step-budget deterministic +
wall-clock bounded) + cancellation tests; registry/capability/selection/
fallback tests incl. no-standby-asserts-failure; error-mapping tests;
envelope replay/verify tests; diagnostics-content tests; import-lint tests
(stdlib-only core, no TRF/manager imports); 5-line simplicity test (native path
stays one call). LATER (Dutch phase): criteria fixtures, BBP differential,
checker-mode, TRF matrix, benchmarks-as-gates.

## G. Conformance/differential harness plan (skeleton in Foundation)

Corpus format: versioned JSON cases (input state, ruleset, seed, engine pins,
expected class); metadata per case (provenance, FIDE article refs where
applicable); comparison profiles with fixed normalization (board-order-
insensitive, colour-aware) and the 7-class taxonomy; failure records storing
corpus + both outputs + pins + triage label. BBP as first oracle in Dutch
phase (BYO binary, pinned version, TRF-2026); JaVaFo second (attribution,
BYO); native-vs-native determinism differential runs in Foundation CI.
Oracle disagreement opens investigation records — never auto-baselined.

## H. External adapter contract (specified, not built)

Lifecycle: resolve → verify version → convert (native state→TRF) → spawn with
timeout → capture stdout/stderr → parse → normalize → envelope.
Discovery: explicit path/config only (no PATH sniffing surprises; documented
search order). Version: `-r`-equivalent probe, recorded, mismatch = typed
error. Exits: BBP 0–5 mapped; unknown codes = InternalError with capture.
Malformed output: typed error + raw excerpt (bounded length). Termination:
grace period then kill; zombie-reaping documented per platform. Reproducibility:
binary identity + TRF echo + seed recorded. Licence: BYO-binary + attribution
file shipped with adapter docs; bundling forbidden (O04/O06).

## I. Tiebreak-core interface (contract only, per O09)

Narrow versioned input contract (precomputed vectors, system+version ids);
stub provider for tests; Burstein path calls it or raises typed
unsupported-capability; no calculation code in pairing-core; single-source
rule enforced by shared goldens later. No project created.

## J. Performance (Foundation)

No optimisation; harness asserts: 10/20 players instant (smoke budgets TBD by
measurement), 50/100 bounded, 250/500/1000 scenarios recorded (no pass/fail
budgets yet — measure-first), pathological single-bracket + dense-rematch end
in typed timeout (never hang), step-budget determinism test. Budgets published
from data in Dutch phase.

## K. Security/robustness (Foundation)

Untrusted-input suite (duplicates, garbage, asymmetry, huge fields);
bounded CPU/memory (budgets; no unbounded caches across calls);
adapter isolation design (separate process, bounded stdio, no shell, explicit
paths); TRF grammar kept out of core; diagnostics redaction rule (no raw
memory dumps, bounded excerpts); determinism under adversarial input.

## L. Acceptance gates (all testable; zero vagueness)

1. `tests/test_contract.py` + all v0.1.0 goldens green. 2. Determinism suite
   green incl. PYTHONHASHSEED sweep. 3. Adversarial-input suite: 100% typed
   errors, zero silent absorptions (enumerated case list). 4. Impossible suite:
   typed + diagnostics assertions green. 5. Timeout/cancel suite green with
   recorded budgets. 6. Registry suite: defaults/explicit/fallback + metadata
   assertions green; no-standby ⇒ typed failure (substitution-impossible test).
   7. Envelope replay suite green. 8. Import-lint + simplicity tests green.
   9. Seam schema + synthetic chess-manager-side tests green (joint review).
   10. Docs: DECISIONS/ARCHITECTURE/API/VERSIONING/ROADMAP updated in the same
   change as the code (doc-code same-PR rule). Phase exits only when 1–10 hold.

## M. Implementation order (evidence-adjusted)

F1 compat harness + determinism snapshot (safety net FIRST — Stage-1 lesson:
untested machinery everywhere). F2 errors + input validation + API tiers
(kills silent absorption). F3 provider + registry + explicit config + fallback
metadata. F4 envelope + replay + diagnostics. F5 timeout/cancel (+ budgets).
F6 differential-harness skeleton (native-vs-native + stubs) + seeded corpus
generator. F7 integration seam + synthetic manager-side tests. F8 API cleanup,
versioning/changelog/release policy, licence hygiene. (Differs from the example
only by putting the harness first — justified above.)

## N. Hostile architectural review (pre-finalization; classifications)

- **CRITICAL**: hidden breaking renames (PairingCard→Pairing etc.) — RULE: no
  renames/removals in Foundation; migration map §E enforced by API-snapshot
  tests. Controlled.
- **HIGH**: nondeterminism via wall-clock polling inside search loops —
  RULE: step budget primary (per-node counter), wall-clock only at bracket
  boundaries; PYTHONHASHSEED-sweep test. Controlled by gates L2/L5.
- **HIGH**: overengineering (registry/envelope/harness for a small lib) —
  JUSTIFIED by O01/O03 multi-engine + conformance requirements; guarded by the
  §F simplicity test (native one-call path stays). Accepted with guard.
- **MEDIUM**: circular deps (registry→adapters→core) — RULE: registry maps
  names to lazy entry points; import-lint test. Controlled.
- **MEDIUM**: duplicate truth (RulesetId vs kernel behaviour; envelope vs
  result) — RULE: dated rulesets + compat harness pins kernel; envelope
  derived, never hand-written. Controlled.
- **MEDIUM**: engine metadata loss on external paths — RULE: raw capture +
  version probe mandatory (§H). Controlled.
- **MEDIUM**: TRF leakage into core — RULE + import-lint test. Controlled.
- **MEDIUM**: chess-manager coupling via seam — RULE: data-schema seam,
  synthetic fixtures, joint-review gate L9. Controlled.
- **MEDIUM**: timeout gap in single transposition DFS — RULE: per-node step
  check (O(1) counter) + boundary wall-clock. Controlled.
- **MEDIUM**: licence contamination via BBP-vendoring temptation — RULE:
  NOTICE-review gate + dependency-closure CI (L-MIT-01). Controlled.
- **MEDIUM**: FIDE/date ambiguity in new APIs — RULE: RulesetId mandatory,
  undated claims rejected in review. Controlled.
- **MEDIUM**: unprovable tests ("validator catches everything") — RULE:
  property suites state their generated scope honestly. Controlled.
- **LOW**: fallback ambiguity — eliminated by design (no unconfigured path) +
  test. Tie-break leakage — narrow contract + stub tests. Unknown-failure
  silence — exhaustive `InternalError` mapping. Tournament-core creep —
  explicitly rejected (O09 §9).
- **DEFERRED**: full 2026-Dutch article retrieval; C.04.6 text; oracle-mass
  storage decision; wall-clock default value (measure-first).

Review verdict: no blocking architectural flaw; all items have a control or an
explicit gate. Exact implementation starting point: **F1 — write
`tests/test_v010_behavioral.py` goldens + determinism snapshot against the
UNMODIFIED kernel; nothing else changes until L1 holds.**
