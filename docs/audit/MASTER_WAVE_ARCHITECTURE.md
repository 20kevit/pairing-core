# Architecture Review (master wave, Phase AA)

Hostile review against the mission checklist. Verdict: PASS on all items
within implemented scope; out-of-scope items remain explicitly BLOCKED
(see `docs/CAPABILITY.md`), not silently absorbed.

- Consumer without engine knowledge? YES — `pair_canonical` names no engine
  class (AST + subprocess enforced). Provider/metadata internals stay behind
  `pair_via`/registry.
- Native replaceable without consumer changes? YES — `EngineProvider`
  interface + explicit registry; canonical request carries only a
  `provider_id` hint with no fallback/substitution.
- BBP/JaVaFo replaceable? YES — adapters sit at the TRF edge, never imported
  by core domain (import-lint rule retained).
- Rulesets/versions explicit? YES — mandatory `ruleset`, exact-match
  resolution, `dutch-till2026-compat` frozen (E.5/float-bar deviations
  documented, untouched per O08).
- Determinism testable? YES — `DETERMINISM_CONTRACT.md` scope + sweeps +
  canonical byte-equality.
- Impossible states diagnosable? YES — typed taxonomy + validator codes +
  `explain()` (output-derived, no search internals).
- Hard constraints vs preferences separated? YES — `ConstraintSet`
  (forced/forbidden hard; bye directives refused, never softened);
  colour/float preferences remain ordering criteria inside the frozen kernel,
  documented as compat behavior.
- Public/internal separated? YES — `API_TIERS.md` + `__all__` boundary tests.
- Independently installable? YES — wheel built and inspected this wave
  (33 files, no tests/binaries/secrets; zero runtime deps).
- Tournament management absent? YES — no standings/scheduling/persistence;
  `round_robin()` is a fixed Berger table, not event management.
- tiebreak-core separate? YES — untouched; no tiebreak code added.
- External boundaries clean? YES — explicit BYO configs, version probes,
  typed failures, no silent fallback.
- Compatibility explicit? YES — migration guide + O08 window + permanent
  v0.1.0 suites (41 goldens + 15 contract green).
