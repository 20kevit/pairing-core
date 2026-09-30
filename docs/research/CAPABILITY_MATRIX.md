# Capability Matrix — Engines & Systems (STAGE 2)

Legend: YES / PARTIAL / NO / UNKNOWN. pairing-core column = Stage 1 evidence;
others = Stage 2 research (grades in SOURCES.md).

| Capability | pairing-core native (v0.1.0) | BBP | JaVaFo 2.2 | Vega | Swiss-Manager | py4swiss | echecs/swiss | gnutterts/chesspairing |
|---|---|---|---|---|---|---|---|---|
| Dutch (which rules) | PARTIAL (pre-2026 kernel) | YES (2025) | YES (Dutch) | YES | YES | YES (≈BBP) | YES (claim) | YES (claim) |
| Dubov | NO | NO | NO | YES | UNKNOWN | PARTIAL (immature) | YES (claim) | YES (claim) |
| Burstein | NO | PARTIAL (self-decl. flawed) | NO | YES | UNKNOWN | PARTIAL (immature) | YES (claim) | YES (claim) |
| Lim | NO | NO | NO | YES | UNKNOWN | NO | YES (claim) | YES (claim) |
| Double Swiss | NO | NO | NO | UNKNOWN | UNKNOWN | NO | YES (claim) | YES (claim) |
| Team Swiss | NO | NO | NO | YES (Orion) | YES | NO | YES (claim) | YES (claim) |
| Round robin | NO | NO | NO | YES (≤24) | YES (≤150 rds) | NO | NO | YES (claim) |
| Determinism | YES | YES | YES (hash-seeded R1 colour) | YES | YES | YES | UNKNOWN | UNKNOWN |
| Seeded RTG/corpus | NO | YES (-s) | YES (seed/`012`) | UNKNOWN | UNKNOWN | via BBP | UNKNOWN | fuzz (claimed) |
| Checker mode (FPC-like) | PARTIAL (validator, no TRF) | YES (-c, checklist) | YES (-c, checklist) | via JaVaFo | via JaVaFo | via BBP | UNKNOWN | validate cmd (claimed) |
| TRF I/O | NO | YES (TRF-2026+bx) | YES (TRF(x)) | YES | YES | YES | YES (TRF16/26) | YES (TRF16/26) |
| Library API | YES (Python) | NO (CLI) | PARTIAL (exper. Java) | NO | NO | PARTIAL (CLI+bindings) | YES (TS) | YES (Go) |
| Error taxonomy | NO (ValueError-only) | YES (codes 0–5) | PARTIAL (stderr) | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN | UNKNOWN |
| Forbidden/manual pairs | PARTIAL (forced locks) | UNKNOWN | YES (XXP) | YES (manual) | YES (manual+bye) | UNKNOWN | UNKNOWN | UNKNOWN |
| Scale evidence | NO | O(n³s²log n) analysis | big-group fixes (changelog) | 1200 pl/23 rds (vendor) | 2000 pl/23 rds (vendor) | UNKNOWN | UNKNOWN | UNKNOWN |
| Licence reuse posture | MIT (declared) | Apache-2.0 (vendoring OK w/ NOTICE; subprocess clean) | custom free+attr; bundling UNKNOWN | proprietary | commercial | MIT/Apache mix | MIT | UNKNOWN licence |

Reading: no engine does everything; the library-API + multi-system + testable
combination is the open niche. BBP+JaVaFo are oracles/adapters, not competitors.
