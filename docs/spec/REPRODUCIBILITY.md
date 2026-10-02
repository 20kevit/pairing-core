# Reproducibility Specification (STAGE 3 SPEC — PROPOSED)

## 1. Replay envelope (required on every result)

Input digest (canonical serialisation hash) + full input reference; round;
RulesetId (system + effective date + acceleration + point values incl. PAB
value); engine id + version (+ binary build where external); ConstraintSet
digest (forced/forbidden/bye directives); seed (or explicit `none`);
pairing-number assignment fingerprint (order + numbers, since ranking is
caller-owned); software version pins (library, adapter, TRF dialect);
timestamp (informational only, never an input); request mode
(default/explicit/fallback) + requested vs actual engine + fallback reason;
timeout budgets (wall-clock + step) applying to the run.

## 2. Guarantees

`replay(envelope) == result` byte-identical (C-REP-01). External engines:
replay valid to the extent the engine self-identifies (JaVaFo build-coupled
seeds documented as a caveat). Initial-colour lots: only via declared seed;
hash-seeded defaults (JaVaFo-style) are allowed ONLY if disclosed in the
envelope.

## 3. Timeout, fallback, and replay limits (O03/O10 FINAL)

Step-budget exhaustion replays deterministically (same budget → same
`TimeoutError` frontier, VERIFIED by construction once implemented — gate it
with a test). Wall-clock timeouts do NOT replay to success: the envelope
records budget + outcome so a timeout is *explainable*, and re-running with a
larger budget is an explicit new request, not a replay. Fallback runs replay
against the ACTUAL engine recorded, with the original request mode preserved
for audit.

## 4. Budget policy (Phase 1B decision, evidence-backed)

- Native step budget: default 2,000,000 nodes (legacy cap, retained for
  compatibility); configurable per request via ExecutionBudgets. Deterministic.
- Native wall-clock: NO default (deterministic-by-default principle; a
  machine-dependent default would make default behavior unreproducible).
  Callers set explicit wall-clock budgets where needed (measured reference:
  single-1000 round-1 ≈97s; pathological single-80 → step-cap at ≈8.5s;
  realistic ≤250-player rounds in milliseconds — see
  tests/data/benchmarks/baseline.json). Step budget remains the primary bound.
- Cancellation: cooperative token, checked per search node + bracket entry;
  no default cancellation (explicit token only).
- Adapter timeouts (BBP/JaVaFo configs): REQUIRED explicit parameters with
  conservative operational defaults (60s pairing / 30s probe), documented in
  adapter modules; these bound external processes, not pairing semantics.
- Timeout vs cancellation stay distinct typed errors with budget context in
  the envelope (budgets field); replay-limit semantics per §3 unchanged.

## 5. Retention & audit

Envelopes stored alongside results by the manager; core provides
verify/envelope-diff helpers. Audit trail = envelopes + diagnostics, no
logging framework inside core.
