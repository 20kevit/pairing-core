# Capability & Maturity Matrix (product authority — v0.4.1, 2026-10-04)

Maturity scale: RESEARCHED (studied, not built) / EXPERIMENTAL (built,
provisional) / VALIDATED (spec-anchored tests green) / PRODUCTION_READY
(evidence across spec/coverage/edge-cases/determinism/performance/docs) /
DEPRECATED / UNSUPPORTED / BLOCKED (with reason). Promotion requires the
listed evidence — tests alone never suffice.

Supersedes the pre-0.3.0 matrix (which listed the 2026 systems as
BLOCKED/RESEARCHED for lack of primary text). That assessment was retired
when the Council-bundle FULL_TEXT evidence package arrived
(`docs/rules/fide/evidence/`, `RULE_SOURCE_MATRIX.md`) and the seven 2026
rulesets were implemented, audited, and closed (0.3.0 → 0.3.1 → 0.4.0;
see `docs/audit/FIDE_CONFORMANCE_MATRIX.md` and
`docs/audit/FIDE_CONFORMANCE_CLOSURE_REPORT.md`). No FIDE endorsement is
claimed for any system; explicit interpretations are registered in the
conformance matrix.

## Pairing systems

| System | Maturity | Evidence |
|---|---|---|
| Dutch, `dutch-till2026-compat` (frozen kernel) | PRODUCTION_READY (compat scope) | F1 goldens (41), corpus (22), 42 live oracle runs, benchmarks, hash sweeps; deviations E.5/float-bar documented + frozen per O08 |
| Dutch-2026 (`dutch-2026`, C1–C21 criteria engine) | VALIDATED | FULL_TEXT evidence, 47-suite + PAB/C12 vectors, hostile audit + closure fixes, property fuzzing; limitation L1 (exact-search ceilings) applies |
| Dubov-2026 (`dubov-2026`, ARO engine) | VALIDATED | FULL_TEXT evidence, official-example tests, hostile audit fixes (G1 extremes, 3.2.4.1 shift, C7 real-pairing) |
| Burstein-2026 (`burstein-2026`, Index engine) | VALIDATED | FULL_TEXT evidence, hostile audit fixes (C6 sign, C7 scope, enumeration); limitation L1 applies |
| Lim-2026 (`lim-2026`, procedural engine) | VALIDATED | FULL_TEXT evidence, hostile audit + closure fixes (scrutiny, 3.3/3.8/4.4/5.5); limitations L4 (4.2 interleaving approx) and I-L-412 (upward-search mirror, genuine ambiguity, deterministic default) |
| Double Swiss-2026 (`double-2026`, match engine) | VALIDATED | FULL_TEXT evidence, hostile audit fixes (C5 construction, TPN space); limitation L3 (full-C3 lookahead policy approx) |
| Team Swiss-2026 (`team-2026`, lexicographic machinery) | VALIDATED | FULL_TEXT evidence, hostile audit fixes (4.3.7 + secondary); limitation L3 applies |
| Olympiad team Swiss (`olympiad-2022`, median + 9.x) | VALIDATED | Retrieved chapter text (§§1–11), 0.4.0 rewrite (bye rank, 7.2 lot, 8.x chains, 9.x floaters, 11.1 order); limitation L5 (source PDF per se unobtained; chapter text complete and sufficient) |
| Baku accelerated modifier (`baku`) | VALIDATED | FULL_TEXT evidence (C.04.7 GA/GB split + virtual points); caller-side duties documented |
| Berger Round Robin, `berger-rr` (single/double) | VALIDATED | Handbook C.05 Annex 1 goldens (even 4–12), structural odds, balance bounds |
| Knockout/Match/Playoff | OUT_OF_SCOPE_WITH_REASON | No single authoritative pairing text; bracket generation is tournament management, outside the pairing-core boundary (`docs/spec/TOURNAMENT_BOUNDARIES.md`) |

## Cross-cutting capabilities

| Capability | Maturity | Evidence |
|---|---|---|
| Forced / forbidden pairs | PRODUCTION_READY | e2e + validator FORBID-01 + BBP-XXP agreement |
| Bye selection (fresh-first + C5 + C9) | PRODUCTION_READY (compat scope) | goldens + corpus Y1–Y5 + BBP C9 agreement |
| Colour allocation (compat model) | PRODUCTION_READY (compat scope) | goldens; E.5 deviation documented + frozen |
| Float model (compat 3-level) | PRODUCTION_READY (compat scope) | goldens; absolute-bar question documented + frozen |
| Typed errors / budgets / cancellation | PRODUCTION_READY | suites + pathological bounds; 2026 `cancel_token` wired (0.4.0); ceilings per `docs/audit/SEARCH_CEILING_POLICY.md` |
| Envelopes / digests / replay metadata | PRODUCTION_READY | round-trip + determinism suites |
| Explainability (`explain`) | VALIDATED | unit + integration tests (no search-path exposure by design) |
| Request serialization | VALIDATED | round-trip + malformed rejection |
| TRF interchange (subset) | VALIDATED | round-trips + live BBP acceptance; PAB-U verified; absentee/accel limits documented |
| BBP adapter | VALIDATED | stub failure-paths + live runs (BYO binary, never bundled) |
| JaVaFo adapter | VALIDATED | stub failure-paths + live runs (BYO JVM + jar, never bundled) |
| Canonical consumer contract (`CanonicalPlayer`/`CanonicalRequest`/`pair_canonical`) | VALIDATED | isolation tests (subprocess + AST), pair-equivalence, serialization round-trips |
| Migration guide v0.1.0 → canonical | VALIDATED | O08 window restated; compat suites green |
| Differential harness | VALIDATED | taxonomy + corpus + native self-differential |
| Benchmarks | VALIDATED | 50–1000 + pathological, baselines recorded (`tests/data/benchmarks/`); refresh is opt-in (`PAIRING_UPDATE_BASELINES=1`) |

## Explicitly out of scope (product boundary)

Tournament lifecycle, standings/results management, ratings, general
tie-break calculation (future independent tiebreak-core per O09),
persistence, permissions, UI, payments, notifications, REST API, database.
pairing-core owns one-round pairing decisions + validation +
reproducibility; chess-manager owns everything else
(see `docs/spec/TOURNAMENT_BOUNDARIES.md`).

Promotion rule: any maturity upgrade needs a dated entry here with its
evidence. Downgrades on contradictory evidence immediately.
