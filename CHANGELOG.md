# Changelog

All notable changes to this project are recorded here. Versioning follows
the five-axis model in `docs/spec/VERSIONING.md`; the library version below
is the `pyproject.toml` version. Dates are commit dates (UTC).

## [0.2.0] — 2026-10-03

Additive canonical consumer contract (no v0.1.0 behavior change):

- `CanonicalPlayer` / `CanonicalRequest` / `pair_canonical()` — stable,
  implementation-independent pairing contract (system + mandatory ruleset +
  schema version + provider hint + deterministic flag), with legacy
  converters, canonical JSON serialization, and module-isolation tests.
- Migration guide `v0.1.0 → canonical`
  (`docs/MIGRATION_V010_TO_CANONICAL.md`); O08 two-minor support window
  restated, nothing deprecated yet.
- Determinism contract (`docs/spec/DETERMINISM_CONTRACT.md`), API tiers
  (`docs/spec/API_TIERS.md`), canonical contract spec, forensic baseline.
- Import-boundary tests (`__all__` allow-list, version consistency).
- Version-reporting tests now track the package version instead of pinning
  `0.1.0` (historical goldens/records unchanged).
- v0.1.0 compatibility: 41/41 goldens + 15/15 contract tests green,
  kernel outputs byte-identical.

## [Unreleased] (main branch, post-0.1.0 development)

### Added (all additive; v0.1.0 behavior preserved)

- Typed error taxonomy (`PairingError` family, `ValueError`-compatible).
- Dated rulesets (`RulesetId`, `ConstraintSet`, `dutch-till2026-compat`).
- Strict validation boundary + validated compat wrapper (`EngineRequest`,
  `pair`, `validate_request`, `versions()`).
- Reproducibility envelope (`Pairing`, `RoundPairing`, digests, budgets).
- Engine provider abstraction + native provider + explicit registry
  (`pair_via`; no silent fallback by construction).
- Execution budgets (step primary, wall-clock secondary) + cancellation.
- Forbidden-pair enforcement (rematch-equivalent) + `FORBID-01` check.
- C9 bye ordering (fewer unplayed games first; BBP-verified).
- Berger round-robin schedules incl. double cycle.
- Structured explanations (`explain`) + request serialization.
- TRF interchange subset (fixed-width, BBP-verified) + BBP/JaVaFo adapters
  (bring-your-own binaries, stub-tested failure paths).
- Differential/conformance harness (11-class taxonomy, 23-case corpus).
- Env-gated live oracle suites (BBP_EXE, JAVAFO_JAR).
- Seeded property tests, hash-seed sweeps, benchmark suite + baselines.
- `LICENSE` (MIT, per O06), capability maturity model (`docs/CAPABILITY.md`).

### Fixed (measured, behavior-preserving except where noted)

- Lazy exchange enumeration (unbounded memory growth on huge brackets).
- Step-counted legality-matrix work (pathological single-80: >400s hang →
  ~8.5s typed timeout). Small-case outputs byte-identical (goldens green).

### Known deviations under investigation (frozen per O08)

- E.5 round-1 parity colours (live BBP + JaVaFo agreement vs S1-white).
- Absolute 3rd-float bar (live oracle divergence; BBP minimizes only).
- See `docs/research/DUTCH_CONFORMANCE_STATUS.md`.

## [0.1.0] — 2026-09-30

- Initial extraction: standalone FIDE Dutch Swiss engine from
  `20kevit/chess-manager` (`domain/pairing/`), behavior-preserving.
- 15 contract tests; zero runtime dependencies.
