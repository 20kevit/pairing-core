# Exact-search ceiling policy (derived execution policy, closure wave)

FIDE semantics are never approximated: a ceiling never returns a partial or
best-effort pairing. Reaching any ceiling raises a typed error
(`EngineTimeoutError` for budgets, `CancelledError` for cancellation,
`ImpossiblePairingError` for provable impossibility); callers (Chief Arbiter
duty, cf. Dutch 1.9.3 / Dubov 1.9.3 / Double 3.3.3) decide. This follows from
already-decided project requirements (deterministic step budgets, wall-clock
secondary protection, typed errors, no partial results, reproducibility,
bounded execution) — no new product decision was needed.

## What constitutes a search step

One `Stepper.tick()`: a candidate-generation or candidate-evaluation node
(transposition, exchange, MDP set, upfloater set, bracket pairing, backtrack
node, enumeration node). Every factorial-scale generator ticks per node, and
every materialization is pre-guarded by exact combinatorial count
(`check_count`), so exhaustion is deterministic and OOM-safe.

## Determinism

- Step budgets are logic-clock: same input + same `max_steps` → same outcome
  (pairing or typed error) on every machine. Recorded step counts in error
  messages make cutoffs replayable.
- Wall-clock is SECONDARY protection only: it may fire earlier on slower
  machines (same input can therefore time out on one machine and succeed on
  another). Wall-clock never changes WHICH pairing a successful run returns.
- Cancellation is immediate and typed; it never yields partial output.

## Scaling

Budgets are caller-set per tournament size. Measured guidance (2026-10-03,
`tests/data/benchmarks/benchmarks_2026.json`): default 2M steps carry R1 and
realistic mid-tournament fields through ~30-player dense brackets; full-field
50+ exact Dutch/Burstein search is factorial and terminates typed. Callers
running large events raise `max_steps` and/or set `wall_clock_seconds`
explicitly; the engines never silently degrade.

## No partial results

`P26Pairing` values are constructed only on full success (partials are
unrepresentable: paired-sets cover all non-bye players or the call raises).
Timeout/cancel paths raise before any pairing object exists.
