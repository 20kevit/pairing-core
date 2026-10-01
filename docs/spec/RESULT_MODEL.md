# Result Model Specification (STAGE 3 SPEC — PROPOSED)

## 1. Domain result vs diagnostics (decision PROPOSED)

**Core result** (stable, versioned, minimal): pairings (board, white, black),
bye holder + bye kind/value, float tags (closed enum), round number.
**Envelope** (versioned, additive): engine id+version, ruleset id,
constraint-set digest, seed, input digest, warnings list, criteria-cost
summary (native), external raw-output reference (adapters).
**Diagnostics** (best-effort, non-contractual detail): per-pairing provenance,
blocking-constraint traces on failure, bracket summaries. Core result fields
are covered by compatibility guarantees; diagnostics are informative only.

## 2. Failure results (O02 FINAL — no partials as success)

Impossible pairing → typed `ImpossiblePairingError` carrying: ruleset,
blocking evidence (first failing bracket + criteria), attempted scope
(strict/relaxed, bye candidates tried), timeout/cancel context where
applicable. Timeout → typed `TimeoutError` (budget, elapsed, frontier
summary). Success payloads NEVER contain partial pairings. A future
analysis/feasibility API (e.g. completability queries) is
DEFERRED — documented here as possible future capability, not current scope.

## 3. Reproducibility binding

Result envelope contains everything REPRODUCIBILITY.md requires; a `replay()`
helper regenerates the result from (input, envelope) and asserts equality.
External results additionally pin binary identity (path/version/build + TRF
echo) to the extent the engine reports it.
