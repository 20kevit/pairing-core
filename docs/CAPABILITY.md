# Capability & Maturity Matrix (product authority)

Maturity scale: RESEARCHED (studied, not built) / EXPERIMENTAL (built,
provisional) / VALIDATED (spec-anchored tests green) / PRODUCTION_READY
(evidence across spec/coverage/edge-cases/determinism/performance/docs) /
DEPRECATED / UNSUPPORTED / BLOCKED (with reason). Promotion requires the
listed evidence — tests alone never suffice.

## Pairing systems

| System | Maturity | Evidence |
|---|---|---|
| Dutch, `dutch-till2026-compat` (frozen kernel) | PRODUCTION_READY (compat scope) | F1 goldens (41), corpus (22), 42 live oracle runs, benchmarks, hash sweeps; deviations E.5/float-bar documented+ frozen |
| Dutch-2026 (C1–C21 criteria engine) | BLOCKED (no PRIMARY article text; secondary only) | research/DUTCH_SYSTEM_SPECIFICATION.md |
| Dubov | BLOCKED (no PRIMARY text in hand; no oracle) | research/FIDE_SYSTEMS.md |
| Burstein | BLOCKED (BBP self-declares its impl flawed; no PRIMARY text) | research/PAIRING_ENGINES.md |
| Lim | BLOCKED (thin spec retrieval; no oracle) | research/FIDE_SYSTEMS.md |
| Double Swiss | RESEARCHED+ (C.04.5 skeleton retrieved: TPN order, even brackets + upfloaters, C1/C2/C4/C5, PAB=win+draw, arbiter-decides; pairing procedures 3.4–3.6 and colours art. 4 still missing) | Closest future system: mirrors Dutch machinery with upfloat direction |
| Berger Round Robin (single/double) | VALIDATED | Handbook C.05 Annex 1 goldens (even 4–12), structural odds, balance bounds |
| Team Swiss (Olympiad rules) | RESEARCHED+ (Olympiad Pairing Rules 2022 excerpts: controlled Swiss on match points, median groups, float procedures with priority tables, board-1 colours ±2/3× with floater exception, B/C-team odd handling; full articles 3–6 + ranking still missing; ECU confirms Olympiad rules as team standard) | Next team candidate if full text retrieved |
| Team Swiss (C.04.6 TPS) | BLOCKED (only excerpts: brackets + upfloaters C4–C7, PAB, Type-A colours) | research/TEAM_SYSTEMS.md |
| Knockout/Match/Playoff | RESEARCHED (no single authoritative pairing text; no requesting use case) | research/OTHER_FORMATS.md |

## Cross-cutting capabilities

| Capability | Maturity | Evidence |
|---|---|---|
| Forced / forbidden pairs | PRODUCTION_READY | e2e + validator FORBID-01 + BBP-XXP agreement |
| Bye selection (fresh-first + C5 + C9) | PRODUCTION_READY (compat scope) | goldens + corpus Y1–Y5 + BBP C9 agreement |
| Colour allocation (compat model) | PRODUCTION_READY (compat scope) | goldens; E.5 deviation documented |
| Float model (compat 3-level) | PRODUCTION_READY (compat scope) | goldens; absolute-bar question documented |
| Typed errors / budgets / cancellation | PRODUCTION_READY | suites + pathological bounds |
| Envelopes / digests / replay metadata | PRODUCTION_READY | round-trip + determinism suites |
| Explainability (`explain`) | VALIDATED | unit + integration tests (no search-path exposure by design) |
| Request serialization | VALIDATED | round-trip + malformed rejection |
| TRF interchange (subset) | VALIDATED | round-trips + live BBP acceptance; PAB-U verified; absentee/accel limits documented |
| BBP adapter | VALIDATED | stub failure-paths + live runs (BYO) |
| JaVaFo adapter | VALIDATED | stub failure-paths + live runs (BYO JVM+jar) |
| Canonical consumer contract (`CanonicalPlayer`/`CanonicalRequest`/`pair_canonical`) | VALIDATED | isolation tests (subprocess + AST), pair-equivalence, serialization round-trips; 2026-10-03 |
| Migration guide v0.1.0 → canonical | VALIDATED | O08 window restated; compat suites green; 2026-10-03 |
| Differential harness | VALIDATED | taxonomy + corpus + native self-differential |
| Benchmarks | VALIDATED | 50–1000 + pathological, baselines recorded |

Promotion rule: any maturity upgrade needs a dated entry here with its
evidence. Downgrades on contradictory evidence immediately.
