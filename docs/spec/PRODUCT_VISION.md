# Product Vision (STAGE 3 SPEC — PROPOSED)

## 1. Two-goal structure (from mission §3.1)

**Goal 1 (near): solve chess-manager's pairing needs.** Deterministic Dutch
pairing + validation as a dependency-free Python library call, with TRF-based
cross-checking against BBP during integration. Success = chess-manager drops
its embedded domain pairing for versioned pairing-core calls with identical or
better-verified behaviour.

**Goal 2 (far): professional reusable open-source pairing library.**
Production-grade, competition-grade, FIDE-rule-correct, reproducible, highly
tested; multi-system (Dutch → Dubov/Burstein/Lim → RR → Double → Team);
adapter surface for reference engines; conformance harness; eventual FIDE
endorsement candidacy.

## 2. Long-term target properties (all PROPOSED requirements pointers)

production-grade (SPEC: reliability, errors, versioning), competition-grade
(performance scale table + pathological cases), FIDE-rule-correct (named
system + dated ruleset per call, oracle-tested), reproducible (REPRODUCIBILITY.md
metadata), highly tested (TESTING_STRATEGY.md), endorsement-capable
(FIDE_ENDORSEMENT_READINESS.md). Non-goal: claiming endorsement before a
certificate exists (explicit prohibition carried from mission).

## 3. What the product is NOT (scope guardrails)

Not a tournament manager (TOURNAMENT_BOUNDARIES.md), not a REST service (no
public HTTP API required), not a database, not a UI, not a ratings system, not
a tie-break engine (tie-breaks live in Handbook 07 — adjacent, OUT unless
Burstein-style ranking needs them; OWNER DECISION REQUIRED).

## 4. Scale doctrine (mission §3.2)

Initial correctness target <100 players (chess-manager reality); design must
not preclude 100/250/500/1000. Correctness before optimisation; optimisation
only against the benchmark scenarios (Stage 4 performance readiness), never
speculative.
