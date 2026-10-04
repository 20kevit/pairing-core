# pairing-core documentation index

Start at the [`README`](../README.md). This page maps everything else.
Entries marked **authority** are the current source of truth for their
topic; entries marked **historical** are preserved evidence — do not cite
them for current behavior.

## Start here

- [`README`](../README.md) — project homepage, quick start, positioning.
- [`examples/basic_swiss.py`](../examples/basic_swiss.py) — two-round
  Swiss fragment on the canonical API (runnable).
- [`examples/custom_provider.py`](../examples/custom_provider.py) —
  third-party provider guide (runnable).
- [`CHANGELOG.md`](../CHANGELOG.md) — **authority** for what changed,
  per version. `0.4.1` is an untagged release candidate.

## Users

- `docs/CAPABILITY.md` — **authority** for current supported systems
  and maturity.
- `docs/spec/API_TIERS.md` — **authority** for public vs internal API.
- `docs/MIGRATION_V010_TO_CANONICAL.md` — legacy → canonical migration.
- `docs/spec/CANONICAL_CONTRACT.md` — canonical request/result contract.
- `docs/spec/ENGINE_ABSTRACTION.md` — provider/registry/provenance rules
  (incl. provider-vs-effective-engine identity, §1b).
- `docs/spec/DETERMINISM_CONTRACT.md` — determinism and replay rules.
- `docs/PERFORMANCE.md` — measured baseline + exact-search ceiling policy
  in practice.
- `docs/audit/SEARCH_CEILING_POLICY.md` — **authority** for bounded
  exact search (ceilings, budgets, cancellation, no partials).

## Developers

- [`CONTRIBUTING.md`](../CONTRIBUTING.md) — scope, evidence-first
  workflow, test policy, commit style.
- `docs/spec/ARCHITECTURE.md` — module layout and layering.
- `docs/spec/TESTING_STRATEGY.md` — adopted test policy + per-suite
  implementation status.
- `docs/spec/VERSIONING.md` — **authority** for versioning (five axes,
  O08 deprecation window).
- `docs/spec/TOURNAMENT_BOUNDARIES.md` — **authority** for the product
  boundary (what pairing-core owns vs the caller).
- `docs/RELEASING.md` — **authority** for the release procedure
  (manual; owner-only actions listed).

## FIDE evidence and status

- `docs/audit/FIDE_CONFORMANCE_MATRIX.md` — **authority** for
  rule-by-rule conformance standing + interpretation register.
- `docs/audit/FIDE_CONFORMANCE_CLOSURE_REPORT.md` — **authority** for
  closure resolutions and the limitation register (L1/L3/L4/L5, I-L-412).
- `docs/audit/FIDE_CONFORMANCE_FINAL_REPORT.md` — hostile-audit wave
  report (**historical** record of that wave; conclusions carry forward).
- `docs/rules/fide/RULE_SOURCE_MATRIX.md` — rule → source → code → test
  traceability.
- `docs/rules/fide/SOURCE_MANIFEST.md` + `evidence/` — retrieved sources.
- `docs/rules/fide/CURRENT_SYSTEM_CATALOG.md` — retrieved-system catalog.
- `docs/DECISIONS.md` — O01–O10 final owner decisions.
- `docs/OPEN_QUESTIONS.md` — genuinely unresolved items only.
- `docs/spec/ROADMAP.md` — phase completion + future scope.

## Operations

- [`SECURITY.md`](../SECURITY.md) — security posture and reporting.
- `docs/RELEASING.md` — release steps, artifact policy, owner actions.
- `.github/workflows/ci.yml` — release gate (tests, seeds, build,
  artifact inspection, install smoke, tree-clean).

## Historical (preserved, not authoritative)

Stage-1 snapshots and superseded work lists — kept as evidence, each with
a banner pointing at its current authority:

- `docs/audit/CURRENT_CAPABILITIES.md`, `CURRENT_LIMITATIONS.md`
- `docs/rules/fide/CURRENT_STATUS.md`, `SYSTEM_COVERAGE.md`
- `docs/audit/FIDE_REMAINING_ITEMS.md`
- `docs/FINAL_CAPABILITY_AND_PROFESSIONALIZATION_REPORT.md`,
  `docs/FINAL_MASTER_WAVE_REPORT.md` (wave reports)
- `docs/research/`, `docs/rules/fide/extracted/`,
  `docs/rules/fide/historical/` (research-phase material)
- `CHANGELOG.md` archived post-0.1.0 section
