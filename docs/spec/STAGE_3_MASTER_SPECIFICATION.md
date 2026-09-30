# Stage 3 Master Specification (STAGE 3 gate document — PROPOSED)

## What is specified

A versioned Python pairing library evolving v0.1.0's Dutch kernel into a
multi-system, oracle-tested, reproducible engine family with external adapters
(BBP first, JaVaFo second, both bring-your-own-binary), serving chess-manager
first and the open-source ecosystem second, with endorsement preparation as a
late phase and NEVER a premature claim.

## Document map (all under `docs/spec/`, all PROPOSED)

PRODUCT_VISION → why/two goals/scale; PRODUCT_REQUIREMENTS (ID catalog) +
NON_FUNCTIONAL_REQUIREMENTS; DOMAIN_MODEL (entities/invariants/roll-forward);
ARCHITECTURE (adopted-with-modifications layout + dependency/test rules);
ENGINE_ABSTRACTION (identity/call/registry/conformance); RESULT_MODEL
(core/envelope/diagnostics + failure policy); TOURNAMENT_BOUNDARIES (seams);
TOURNAMENT_SYSTEMS (family taxonomy); TESTING_STRATEGY (12 suites);
REPRODUCIBILITY (envelope + replay); VERSIONING (5 versions); LICENSE_STRATEGY
(MIT + BYO-binary + NOTICE hygiene); ROADMAP (10 phases); ACCEPTANCE_CRITERIA
(phase gates).

## Internal consistency claim (audited in Stage 4)

Single-round scope everywhere; no HTTP/DB/UI; core stdlib-only; TRF at
adapter edge; rulesets dated; errors typed; every requirement traces to
evidence or an explicit product decision (traceability matrix in Stage 4).
Contradictions found later go to the decision register, never silent.
