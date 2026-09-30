# Decision Register (STAGE 4, §4.13)

Status scale: DECIDED (mission/process fact) / PROPOSED (recommendation) /
OWNER DECISION REQUIRED / DEFERRED / REJECTED. Proposals never silently decided.

## Process (DECIDED by mission)

- D01 DECIDED: read/research/document only; implementation forbidden until
  explicit owner approval.
- D02 DECIDED: English documentation; exact identifiers; evidence labels.
- D03 DECIDED: no endorsement claim before a certificate exists.

## Architecture & scope (PROPOSED unless noted)

- D10 PROPOSED: adopt Engine Strategy D (native + BYO-binary adapters + standing
  conformance harness); BBP first oracle/adapter, JaVaFo second.
- D11 PROPOSED: single-round scope; tournament management stays OUT
  (TOURNAMENT_BOUNDARIES.md).
- D12 PROPOSED: core stdlib-only; adapters in opt-in extras; TRF at adapter edge.
- D13 PROPOSED: RulesetId (system + effective date) mandatory on every call.
- D14 PROPOSED: typed error taxonomy replacing ValueError-only.
- D15 PROPOSED: strict input validation (no silent absorption).
- D16 PROPOSED: native criteria-optimisation engine for Dutch-2026 (rewrite-scale;
  current kernel pinned under a compat ruleset).
- D17 REJECTED: in-process GPL-family dependencies (copyleft containment).
- D18 REJECTED: bundling javafo.jar (redistribution UNKNOWN).
- D19 REJECTED: forcing all systems into one abstraction (family taxonomy kept).
- D20 DEFERRED: team systems, knockout orchestration, tie-break engine.

## Owner decisions (OWNER DECISION REQUIRED)

- O01: adopt/reject Strategy D (options A–D in ENGINE_STRATEGY_OPTIONS.md).
- O02: failure-result policy (no partials vs flagged best-effort).
- O03: default engine per ruleset + fallback policy.
- O04: JaVaFo clearance pursuit (bundling vs perpetual BYO-binary).
- O05: tie-break adjacency (Burstein inputs-as-data vs out-of-scope purity).
- O06: licence adoption (MIT retention + NOTICE hygiene as specified).
- O07: roadmap phase order and chess-manager integration timing.
- O08: deprecation windows and v0.1.0 compat-harness permanence.
