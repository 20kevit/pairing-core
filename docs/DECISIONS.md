# Decision Register — original owner decisions with current audit addendum

> This register preserves the pre-audit decisions. Some process and delivery
> statuses have since been superseded; the 2026-10-27 addendum at the end
> records the current task authorization and library boundary. Current audit
> authority is [`audit/GAP_REGISTER.md`](audit/GAP_REGISTER.md).

Status scale: DECIDED / OWNER DECISION (final, owner-directed) / PROPOSED /
DEFERRED / REJECTED. The original verification note below is historical: it
records an earlier consistency review and is not a claim that these decisions
were independently revalidated by the current audit.

## Process (DECIDED by mission)

- D01 DECIDED (historical process gate): read/research/document only before
  owner authorization. It was superseded for this audit by the explicit request
  to audit, fix confirmed in-scope defects, and verify the checkout; it is not a
  current prohibition on the authorized 2026-10-27 work.
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
- O09 OWNER DECISION (original): **tie-break calculation belongs in a
  separate independent library**, not Pairing-Core; no shared tournament-core.
  The separate `20kevit/tiebreak-core` project now exists (v1.2.0 was inspected
  at commit `61491321d7886ab4abe1b7c64686dfce48d2c3dd`). It remains independent,
  has no Pairing-Core runtime dependency, and does not provide the required
  C.04.4.2 Burstein Index calculation. Current integration limits are in
  `docs/spec/TIEBREAK_ARCHITECTURE.md`.
- O10 OWNER DECISION (timeout/cancellation): **both native and external
  execution are bounded** — wall-clock timeout AND deterministic step budget;
  typed timeout error with diagnostics; reproducibility rules for timeouts
  specified (budgets recorded; timeout outcomes are environment-dependent and
  NOT replayable to success); external termination after grace; native
  interruption at bracket-boundary checkpoints with step-budget primacy.

## Rejected / deferred (unchanged, re-confirmed)

- D17 REJECTED: in-process GPL-family dependencies. D18 REJECTED: bundling
  javafo.jar. D19 REJECTED: one-abstraction-for-all-systems.
- D20 DEFERRED (historical roadmap status; refined by O09): KO orchestration
  remains outside current product scope. The separate tie-break library is no
  longer merely deferred; `tiebreak-core` is a published independent project.
  Pairing-Core still does not absorb its algorithms or provide general
  standings/tie-break calculation.
- D10–D16 (Stage-4 proposals) are SUPERSEDED by O01–O08/O10 finals above.

## Validation-wave confirmations (evidence-backed, no architecture change)

- O03/O08 CONFIRMED (live-oracle + differential evidence, 42 tournaments):
  `dutch-till2026-compat` stays FROZEN. Confirmed deviations (E.5 round-1
  parity colours; absolute 3rd-float bar) are NOT corrected in place;
  correction, if ever approved, requires a new dated ruleset id with its
  own golden migration — never a silent compat change.
- O10 CONFIRMED: budget policy explicit (see REPRODUCIBILITY.md §4); no
  default wall-clock for native; adapter timeouts are required explicit
  parameters with conservative operational defaults.
- BBP oracle pin: source build 8f9e3c5 (2026-07-30); live runs via BBP_EXE.
  JaVaFo live-verified: Rel. 2.2 Build 3223 (Dutch-2017 vintage per 092
  tag); BYO-only posture unchanged, nothing vendored.

## Current audit addendum (2026-10-27)

- The current authorized work is an independent audit and repair of the
  pairing-only library; fixes are permitted for confirmed in-scope defects.
- Published `v0.4.1` remains immutable. The working source version is
  `0.4.2.dev0` and is not a release or FIDE evaluation.
- Pairing-Core produces and validates pairings only. General tournament
  management, standings, ratings, and tie-break calculations remain outside
  the product boundary. A Burstein Index input is caller-supplied or declared
  externally calculated, with provenance; Pairing-Core neither computes nor
  independently certifies that value.
- FIDE rule text, implementation interpretation, computational strategy,
  caller policy, and unresolved limitations are separate evidence categories.
  Engineering readiness, production suitability, formal evaluation, and
  endorsement are separate verdicts in `docs/audit/COMPLETION_STANDARD.md`.
