# Changelog

All notable changes to this project are recorded here. Versioning follows
the five-axis model in `docs/spec/VERSIONING.md`; the library version below
is the `pyproject.toml` version. Dates are commit dates (UTC).

## [0.3.1] — 2026-10-03

Hostile FIDE conformance audit of the 0.3.0 2026 engines (authoritative
reference: Council bundle CM3-202517 FULL_TEXT + Annotated Dutch V2026).
No public API change; frozen v0.1.0/v0.2.0 behavior byte-identical:

- 20 conformance defects fixed across Dutch (BSN order, MDP-set order,
  M1/MDP ordering), Dubov (G1 extremes, 3.2.4.1 shift, real-pairing C7),
  Burstein (C6 sign, C7 scope, incoming loop, enumeration), Double/Team
  (C5 construction, TPN identifier space, Team 4.3.7 + secondary),
  Olympiad (floater routing), Lim (scrutiny, columns, even-making, 2.6,
  3.x, 4.4, 5.4, Art.6), and all colour walkbacks (round-aligned).
- Budgets made effective (ticks + count guards + every-tick wall checks;
  deferred Dutch alterations; exact lex-first fast paths); 2026 performance
  gates measured (R1 + realistic sizes succeed; factorial ceilings terminate
  typed — no heuristic pruning).
- 30-test adversarial corpus, 2026 randomized property suite (7 rulesets),
  2026 benchmark record; version-scoped differential oracles pass
  (BBP 2025-era vs legacy; no meaningless cross-version comparisons).
- Rule-level conformance matrix (`docs/audit/FIDE_CONFORMANCE_MATRIX.md`)
  with explicit interpretation register; final report
  (`docs/audit/FIDE_CONFORMANCE_FINAL_REPORT.md`). No FIDE endorsement
  claimed; full conformance claimed nowhere interpretations remain.

## [0.3.0] — 2026-10-03

New additive `pairing_core.fide2026` namespace (no v0.1.0/v0.2.0 behavior
change — frozen kernel, KNOWN_RULESETS, KNOWN_SYSTEMS, resolve_ruleset all
untouched and pinned):

- Seven new rulesets from FULL_TEXT Council-bundle evidence (CM3-202517):
  `dutch-2026` (C1–C21 search), `dubov-2026` (ARO/MaxT/G1–G2), `burstein-2026`
  (Index/BSN enumeration), `lim-2026` (median routing), `double-2026`,
  `team-2026` (lexicographic machinery), `olympiad-2022` (median + 9.x),
  plus the `baku` accelerated modifier and C.04.2 board-order sorting.
- Entry point `pair_2026()` with exact-match `P26RulesetId` resolution (no
  fallback); typed errors; budget/cancel/step discipline throughout.
- Evidence package (`docs/rules/fide/evidence/`), extracted rules
  (`docs/rules/fide/extracted/`), official corpus
  (`tests/corpus/fide_official/`, provenance-labelled), rule→source→code→test
  traceability (`RULE_SOURCE_MATRIX.md`), upgraded source validator (wired
  into the suite).
- Conformance: Berger FULLY_IMPLEMENTED_AND_EVIDENCED (unchanged); six 2026
  systems + Olympiad IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (documented
  readings listed in the matrix; no silent guessing); KO/match
  OUT_OF_SCOPE_WITH_REASON. No FIDE endorsement claimed.
- v0.1.0/v0.2.0 compatibility: 41/41 goldens + full legacy suite green,
  kernel outputs byte-identical.

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
