# Open-Source Ecosystem Research (STAGE 2, §2.8)

Suitability scale: DIRECT (dependable library) / ADAPTER (wrap as engine) /
REFERENCE (read + test against) / ORACLE (differential-test target) /
INSPIRATION (ideas only) / UNSUITABLE. Evidence: repo pages retrieved or
search excerpts (grades inline).

## 1. Candidates

| Project | Lang | Licence (evidence) | Maturity | Algorithms | API | Tests | FIDE claim | Verdict |
|---|---|---|---|---|---|---|---|---|
| bbpPairings | C++ | Apache-2.0 (PRIMARY: repo files) | med-high (endorsed-via-SwissSys; 128 commits) | Dutch-2025, Burstein-flawed | CLI/TRF only | test/ + external diff-tests | via SwissSys | ORACLE + ADAPTER (subprocess); REFERENCE (matching approach) |
| JaVaFo | Java | custom free+attribution (PRIMARY: project page); redistribution UNKNOWN | high (reference role; Rel 2.2 b3222) | Dutch | CLI/TRF + exper. Java API | FPC/RTG self-tools | reference pairer | ORACLE + ADAPTER (subprocess); NOT direct (licence/JVM) |
| py4swiss (Moritz72) | Python+C++(BBP blossom) | MIT own / Apache-2.0 `cpp/` (PRIMARY: repo LICENSE) | low (27 commits, 6 stars, young) | Dutch≈BBP-identical, Dubov≈CPPDubovSystem, Burstein-immature | CLI/TRF; PyPI wheels | pytest vs bbpPairings.exe + CPPDubovSystem | tested-identical to BBP (Dutch) | REFERENCE + INSPIRATION (API shape, TRF handling); NOT direct (immature, binary wheels) |
| gnutterts/chesspairing | Go | ? (UNVERIFIED — licence not retrieved) | med (1325 tests/19 pkgs claimed) | Dutch/Burstein/Dubov/Lim/Double/Team/K eizer/RR + 25 tiebreaks | Go lib + CLI (TRF16/26, JSON/XML) | goldens vs BBP+JaVaFo + fuzz | handbook-referenced | REFERENCE (goldens, architecture) + ORACLE; NOT direct (Go, licence unknown) |
| echecs/swiss + echecs/trf | TypeScript | MIT (PRIMARY: registry pages) | low-med (v5/v4, spec-linked) | Dutch/Dubov/Burstein/Lim/Double/Team subpaths | TS lib, typed | coverage badges (unverified depth) | spec-linked claims | REFERENCE + INSPIRATION (modular per-system subpaths — closest to target architecture); NOT direct (TS) |
| JavaPairing | Java | open/SourceForge (SECONDARY) | med (endorsed 2013 v2.7) | Dutch + others | jar CLI | — | endorsed v2.7 (old rules) | INSPIRATION only (outdated ruleset) |
| markjenkins/chesspairings | Python scripts | ? (UNVERIFIED) | low (front-end only) | via JaVaFo | CSV→JaVaFo pipeline | — | via JaVaFo | INSPIRATION (integration pattern) |
| python-chess | Python | GPL-3.0 (well-known; SECONDARY here) | high (not pairing-focused) | board/moves, NO Swiss pairing (to our knowledge — UNVERIFIED absence) | lib | extensive | n/a | UNSUITABLE for pairing; note GPL-3.0 copyleft boundary respected (no dependency) |

## 2. Direct-dependency suitability (library use inside pairing-core)

NONE of the above qualifies as a direct Python dependency today: C++/Java/Go/TS
language barriers, binary-distribution needs (BBP exe, JVM), immature APIs
(py4swiss), or unknown licences. VERIFIED conclusion from the table. The viable
integration patterns are ADAPTER (subprocess over TRF) and ORACLE (golden/
differential testing) — decided in ENGINE_STRATEGY_OPTIONS.md (PROPOSED).

## 3. What to reuse vs reimplement (research guidance)

- REUSE patterns: BBP error codes 0–5; JaVaFo CLI/TRF(x) conventions (de-facto
  standard); echecs per-system module split; gnutterts golden-vs-BBP/JaVaFo
  harness shape; py4swiss strict/lenient TRF parsing.
- REIMPLEMENT natively: Dutch kernel (already exists; needs 2026 alignment),
  Berger schedules (trivial), domain/result models (absent everywhere as a lib).
- DO NOT reuse: BBP Burstein (self-declared flawed), JaVaFo versioning
  (build-coupled seeds), any GPL code paths inside the library.
