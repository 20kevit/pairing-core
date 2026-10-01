# Decision Register — FINAL ARCHITECTURAL DECISIONS (owner direction recorded)

Status scale: DECIDED / OWNER DECISION (final, owner-directed) / PROPOSED /
DEFERRED / REJECTED. Verification note: O01–O08 were checked against all
existing docs (audit/research/spec); NO contradictions found — only refinements
adopted (O03 envelope fields, O07 seam-in-Foundation + non-conformant guard,
O08 exact two-minor window superseding the earlier "≥1 minor" draft).

## Process (DECIDED by mission)

- D01 DECIDED: read/research/document only; implementation forbidden until
  explicit owner approval (still in force after this task).
- D02 DECIDED: English documentation; exact identifiers; evidence labels.
- D03 DECIDED: no endorsement claim before a certificate exists.

## Final architecture (OWNER DECISION — O01–O09 + timeout)

- O01 OWNER DECISION: **Strategy D** — native engine + external adapters
  (BBP, JaVaFo) + permanent conformance/differential harness. Externals are
  optional providers/oracles, NOT the architecture; no dual-engine runtime
  requirement; differential runs serve validation/regression/release/investigation;
  native must become independently conformant per supported ruleset.
- O02 OWNER DECISION: **no partial pairings as success** — success = complete,
  valid, internally consistent, reproducible; failure = typed failure +
  structured diagnostics (+ optional internal search diagnostics); feasibility
  API is DEFERRED future capability, not current scope.
- O03 OWNER DECISION: **ruleset-dependent defaults, explicit configuration,
  never-silent fallback**. Defaults exist only for demonstrated-conformant
  (engine, ruleset) pairs; unsupported systems have no default. Fallback only
  when explicitly configured; result metadata records requested engine, actual
  engine, reason, versions, ruleset, reproducibility info. Version mismatch =
  typed error, never substitution.
- O04 OWNER DECISION: **JaVaFo = reference/oracle + BYO-binary adapter target**;
  no bundling without explicit licence/redistribution clearance. Adapter
  isolates process lifecycle, discovery, version detection, timeout, exits,
  malformed output, TRF conversion, stdio capture, attribution metadata.
- O05 OWNER DECISION: **tie-break computation is an independent capability**;
  pairing-core consumes narrowly defined ranking/index inputs where formal
  rules require (Burstein); no general tie-break duplication. Correct formula:
  "general tournament tie-break calculation is outside pairing-core, while
  pairing systems may consume narrowly defined ranking/index data when their
  formal rules require it."
- O06 OWNER DECISION: **MIT retained** (no blocking contradiction found);
  external licences stay separate; no GPL vendored; JaVaFo BYO + attribution;
  BBP Apache-2.0 respected, NOTICE review before any vendoring.
- O07 OWNER DECISION: **10-phase roadmap** (Foundation → Dutch conformance →
  integration → additional Swiss → RR → Team → KO/Match → scale → OSS maturity
  → endorsement prep) WITH: integration seam designed/tested during Foundation;
  non-conformant Dutch NEVER shipped to production for roadmap reasons.
- O08 OWNER DECISION: **v0.1.0 behavioural golden harness, permanent** —
  covering ordering, colours, byes, floats, validation, determinism, error
  semantics; **two-minor-release deprecation window** (security/critical
  exceptions only, documented); testable compatibility policy.
- O09 OWNER DECISION: **tiebreak-core = future independent library**
  (spec: `docs/spec/TIEBREAK_ARCHITECTURE.md`); independent of chess-manager;
  serves pairing-core/chess-manager/future managers; NO implementation now;
  NO premature tournament-core.
- O10 OWNER DECISION (timeout/cancellation): **both native and external
  execution are bounded** — wall-clock timeout AND deterministic step budget;
  typed timeout error with diagnostics; reproducibility rules for timeouts
  specified (budgets recorded; timeout outcomes are environment-dependent and
  NOT replayable to success); external termination after grace; native
  interruption at bracket-boundary checkpoints with step-budget primacy.

## Rejected / deferred (unchanged, re-confirmed)

- D17 REJECTED: in-process GPL-family dependencies. D18 REJECTED: bundling
  javafo.jar. D19 REJECTED: one-abstraction-for-all-systems.
- D20 DEFERRED (refined by O09): team systems, KO orchestration as features;
  tie-break engine → specified as tiebreak-core, implementation deferred.
- D10–D16 (Stage-4 proposals) are SUPERSEDED by O01–O08/O10 finals above.
