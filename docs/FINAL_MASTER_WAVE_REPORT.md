# Final Engineering Report — Master Development Wave (2026-10-03)

## Repository

- Starting commit: `ff50dac` (verified: branch `main`, clean tree, remote
  `git@github.com:20kevit/pairing-core.git`, tag `v0.1.0` = `2cb570b`).
- Final commit: see log (linear, no rewrite, no force-push).
- This wave: 5 commits (baseline → canonical → migration/tiers →
  release-prep → this report). Tags created: `v0.2.0`.
- End state: clean tree, all pushed to `origin/main` + tag.

## API

- Canonical (new, preferred): `CanonicalPlayer`, `CanonicalRequest`,
  `pair_canonical()`, `canonical_json()`, `describe_systems()` +
  `SYSTEM_DUTCH`/`SYSTEM_ROUND_ROBIN`/`KNOWN_SYSTEMS`/
  `CANONICAL_REQUEST_SCHEMA`. Zero import-time coupling to engine
  internals (subprocess + AST enforced). Spec:
  `docs/spec/CANONICAL_CONTRACT.md`.
- Legacy stable (unchanged behavior): `SwissEngine`, `PlayerData`,
  `pair_round`, `PairingRequest`/`NativeDutchEngine`, `EngineRequest`,
  `pair`/`pair_detailed`/`pair_via`. Nothing deprecated yet.
- Internal: bracket/pairer/search structures, adapter process internals.
  Supported submodule surfaces: `adapters.{trf,bbp,javafo}`,
  `harness.{compare,corpus}`. Tiers: `docs/spec/API_TIERS.md`.
- Migration: `docs/MIGRATION_V010_TO_CANONICAL.md` (O08 two-minor window).

## Pairing systems

| System | Status | Ruleset | Evidence | Limitations |
|---|---|---|---|---|
| Dutch (frozen kernel) | IMPLEMENTED | `dutch-till2026-compat` | 41 goldens, 15 contract, corpus, 42 live oracle runs, benchmarks | E.5 parity + float-bar deviations frozen per O08 |
| Berger RR single/double | IMPLEMENTED | C.05 Annex 1 construction | Handbook goldens even 4–12, structural odds | Generated beyond 12, marked as such |
| Dutch-2026 | BLOCKED | — | no PRIMARY article text | secondary sources only |
| Dubov / Burstein / Lim | BLOCKED | — | no PRIMARY text / no oracle; BBP self-declares Burstein flawed | — |
| Team (C.04.6 / Olympiad) | BLOCKED / RESEARCHED+ | — | excerpts only | full articles missing |
| KO/match/playoff | RESEARCHED | — | no single authoritative pairing text | outside pairing scope until specified |

## Rulesets

| Ruleset | Version | Status | Conformance |
|---|---|---|---|
| `dutch-till2026-compat` (`dutch@2026-01-31`) | frozen v0.1.0 kernel | IMPLEMENTED | pinned by goldens; 2 confirmed deviations documented, frozen |

## Determinism

Guarantee + scope: `docs/spec/DETERMINISM_CONTRACT.md`. Evidence this
wave: full suite green under `PYTHONHASHSEED` 0/1/42; fresh-process
canonical byte-equality verified; 262 passed / 10 skipped (env-gated
oracle/heavy suites with recorded reasons).

## Constraints

Hard: forced pairs (kernel locks), forbidden pairs (rematch-equivalent,
`FORBID-01`, BBP-XXP agreement). Soft: none (no silent hard→soft
conversion anywhere). Bye directives: explicitly refused.

## External engines

BBP (BYO source build 8f9e3c5): adapter VALIDATED, 42-tournament
differential on record. JaVaFo 2.2 b3223 (BYO JVM+jar, Dutch-2017 vintage):
adapter VALIDATED. Nothing vendored; licenses respected (Apache-2.0 use-only;
JaVaFo BYO + attribution).

## Testing

Unit ✓, contract ✓ (15/15), golden ✓ (41/41), property ✓ (seeded),
differential ✓ (taxonomy + corpus + live-gated), regression ✓ (goldens),
determinism ✓ (sweeps + fresh-process), fuzz/seeded-random ✓,
adversarial/pathological ✓ (bounded, measured), performance ✓
(50–1000 + pathological baselines), security ✓ (boundary tests + re-audit),
serialization ✓ (round-trips + digest + schema rejection), import-API ✓
(new). Result: 262 passed, 10 skipped, 0 failed.

## Performance

Measured only (no claims invented): suite completes ~21s; single-1000
round-1 ≈97s bounded (prior baseline); pathological single-80 hang
eliminated (>400s → ~8.5s typed timeout). Benchmark baselines in-repo.

## Compatibility

v0.1.0 behavior preserved (goldens/contract green, kernel byte-identical).
No breaking changes. No deprecation warnings issued. Migration path
documented. `src/*.egg-info` untracked (was committed by accident; repo
policy says generated artifacts are never committed) + `.gitignore`
hardened.

## Release

- Latest official release: `v0.1.0` (= `2cb570b`, 2026-09-30).
- New release created: **`v0.2.0`** (annotated tag) — additive canonical
  contract, all gates satisfied (tests, determinism evidence, changelog,
  migration notes, version consistency, capability matrix, clean tree,
  inspected wheel: 33 files, no tests/binaries/secrets, zero deps).

## Remaining work

- READY: Dutch-2026 criteria engine IF primary text obtained; oracle-mass
  storage decision; wall-clock default budget value (measure-first).
- BLOCKED: Dubov/Burstein/Lim/C.04.6-full/KO (exact reasons in
  `docs/CAPABILITY.md` + table above).
- OWNER DECISION REQUIRED: dated-ruleset migration vehicle for E.5/float-bar
  corrections (frozen per O08 until approved); oracle-mass storage.
- No IN PROGRESS items left dangling; nothing hidden.
