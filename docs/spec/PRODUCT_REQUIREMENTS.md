# Product Requirements Catalog (STAGE 3 SPEC — PROPOSED)

Every requirement: ID, category, description, rationale, priority (P0/P1/P2),
source, dependencies, acceptance criteria, status (PROPOSED).

## Functional

- **F-DUTCH-01** (functional/algorithmic/FIDE, P0, source: C.04.3-2026 +
  Stage 1 engine): Dutch pairing for a single round given per-player state.
  Accept: C1/C2 absolute + completion on oracle corpus; named ruleset per call.
- **F-DUTCH-02** (P0, source: 2026 deltas): honour played-only colour history,
  win-valued PAB (configurable), C2 forfeit-win exclusion, topscorer split.
  Accept: targeted fixtures (adversarial C/Y sets) + BBP differential.
- **F-LOCK-01** (P0, source: v0.1.0 `locked_pairs` + JaVaFo XXP): forced pairs
  (keep) AND forbidden pairs (add; XXP-equivalent). Accept: validation errors
  + search honours both.
- **F-RR-01** (P1, source: C.05 Berger): single/double round-robin schedules
  with colour-correct tables + rotating bye. Accept: table-equality to Handbook
  Annex 1 for 3–16 players + reversal rule for double.
- **F-SWISS-01** (P1, source: C.04.4.x): Dubov, then Burstein, then Lim engines
  behind the same abstraction. Accept: per-system oracle/golden suites.
- **F-DOUBLE-01** (P2, source: C.04.5): two-game match pairings + match result
  model. Depends on RESULT_MODEL match extension.
- **F-TEAM-01** (P2, source: C.04.6 — text TBD): team Swiss. Depends on team
  domain retrieval. Status: PROPOSED/DEFERRED.

## Correctness / determinism / reproducibility

- **C-ABS-01** (P0): absolute bars (rematch, colour, float, bye-count) never
  violable via any public path. Accept: property tests + oracle corpus zero
  violations.
- **C-DET-01** (P0): same logical input → byte-identical output (incl. colours,
  boards, tags) across runs/platforms/versions-pinned. Accept: determinism
  suite incl. input-permutation cases.
- **C-REP-01** (P0): every result carries reproducibility metadata
  (REPRODUCIBILITY.md). Accept: replay script regenerates result from metadata.

## API / compatibility / reliability

- **A-API-01** (P0): versioned explicit public API (ENGINE_ABSTRACTION.md);
  implicit surfaces tiered or removed with deprecation. Accept: API-compat tests.
- **A-SEM-01** (P0): semantic versioning + separate engine/ruleset/input-format
  versions (VERSIONING.md). Accept: policy doc + changelog enforcement.
- **A-COMP-01** (P0): v0.1.0 behavioural compatibility harness (goldens of
  current engine) before any kernel change. Accept: harness green on refactors.
- **R-ERR-01** (P0): typed error taxonomy (impossible, invalid-input,
  engine-unavailable, timeout, version-mismatch…) replacing ValueError-only.
  Accept: callers can branch programmatically (tests per category).
- **R-EXT-01** (P1): external-engine failure model (timeout/crash/malformed
  output/version mismatch → typed errors + diagnostics). Depends on adapters.

## Performance / security / observability

- **P-SCALE-01** (P1): benchmark suite 10→1000 + pathological brackets; publish
  budgets (no invented numbers now). Accept: suite exists, runs in CI.
- **S-IN-01** (P0): strict input validation boundary (typed errors, no silent
  absorption). Accept: adversarial-input suite (duplicates, garbage, asymmetry).
- **O-DIAG-01** (P1): diagnostics on failure (bracket summary, blocking
  constraint, partial-result policy) + opt-in audit trail. Accept: fixture
  assertions on diagnostics content.

## Testing / docs / licensing / release

- **T-STRAT-01** (P0): TESTING_STRATEGY.md suites implemented per roadmap phase.
- **D-SPEC-01** (P0): this spec suite stays consistent (Stage 4 audit repeats
  per release).
- **L-MIT-01** (P0): MIT retained; NOTICE hygiene if BBP-derived code vendored;
  no GPL in-process; JaVaFo BYO-binary. Accept: licence CI check.
- **E-REL-01** (P1): release engineering (changelog, tags, wheels, version
  pins) per VERSIONING.md.
