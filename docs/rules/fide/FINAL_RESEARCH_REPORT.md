# FINAL RESEARCH REPORT — FIDE Authoritative Documentation Master Wave

Baseline `bf77d7f` / release `v0.2.0`. Retrieval wave 2026-10-03. No pairing
behavior changed (frozen `dutch-till2026-compat`; `dutch-2026` still rejected).

## A. Source inventory (30 F-entries + 8 S-entries)

- Handbook C.04: F-0100 family + F-0101…F-0119 (C.04.1/2/3, Dubov/Burstein/Lim,
  Double, Team, Baku, Appendix A) — full URLs + dates + supersession in SOURCE_INDEX.md.
- Council: F-0201 CM3-202517 (28/10/2025 → applied 01/02/2026).
- Announcements: F-0301 (reminder, fetched full), F-0302 (July-2025 interim, fetched
  full), F-0303 (C.04.1 2024 update).
- TEC/SPP/TRF: F-0401 (endorsement, fetched full), F-0402, F-0403 (TRF-2026), F-0404.
- Berger: F-0501 (tables retrieved in full). Olympiad: F-0601 (2022 Rules, current).
- Historical: F-0701 (1987 GA), F-0702 (NewDutch2022), F-0703 (prior excerpts).
- Secondary S-0101…S-0108: BBP, JaVaFo, py4swiss, echecs, Vega/Swiss-Manager,
  TEC tutorials, papers, table explainers.

## B. Current effective rules (per system)

| System | Document | Version | Effective | Sections |
|---|---|---|---|---|
| Dutch | C.04.3 [F-0105] | 2026 (Council 28/10/2025) | 01-02-2026 | [C1]–[C21] |
| Dubov | C.04.4.1 [F-0108] | 2026 | 01-02-2026 | two-step; C4–C7 |
| Burstein | C.04.4.2 [F-0110] | 2026 recodified | 01-02-2026 | Buchholz order; §2.6 cracking |
| Lim | C.04.4.3 [F-0112] | 2026 | 01-02-2026 | median bi-directional |
| Double | C.04.5 [F-0114] | 2026 new chapter | 01-02-2026 | 2-game matches; PAB 1.5 |
| Team | C.04.6 [F-0115] | 2026 | 01-02-2026 | TPN/brackets; PAB draw |
| Baku | C.04.7 [F-0117] | 2026 generalised | 01-02-2026 | GA/GB + virtual pts |
| Berger | C.05 Ann.1 [F-0501] | current | current | tables 3–16 |
| Olympiad | Rules 2022 [F-0601] | Council 27/10/2021 | 01-01-2022 | 11-rd matchpoints |

## C. Historical timeline
See VERSION_TIMELINE.md: 1987 GA → 2016/2017 Dutch extras → 2021 Olympiad →
2022 snapshot → 2025 interim (eff. 01-07-2025) → TRF-2026 → Council 28/10/2025 →
in-force 01-02-2026 → reminder 24/03/2026. Supersession graph included.

## D. System research status
- FULLY SPECIFIED: Berger; KO/match (as boundary).
- RESEARCH CONTINUES: Dutch-2026 (frame set, bodies G-01), Dubov, Burstein, Lim
  (thinnest), Double, Team/Olympiad, Baku.
- BLOCKED — NO AUTHORITATIVE SPECIFICATION: none. Every system has a located
  current chapter; gaps are article-body depth with a defined manual path.

## E. Current implementation gap (FIDE requirement vs pairing-core)
- Dutch till-2026 kernel ≈ pre-2026 legality kernel; deviations frozen + pinned:
  E.5 parity (live-confirmed), absolute float-bar over-strictness (live-confirmed,
  dissolves in 2026-criteria engine), D.2 order fidelity open, C9 implemented.
- 2026 Dutch needs a criteria-optimiser architecture (BBP-weighted-matching class),
  not kernel tuning. Dubov/Burstein/Lim/Double/Team/Baku each need distinct
  bracket/result models (Stage 3 taxonomy). Berger implemented + validated.
- Full gap detail: docs/research/DUTCH_CONFORMANCE_STATUS.md (unchanged) +
  CURRENT_STATUS.md + per-system notes.

## F. Dutch 2026 evidence
E.5 = till-2026 parity article (no 2026 E.5 exists). 2026 float control = C14–C21
minimisation; absolute-bar claim WITHDRAWN (W-01) against BBP source evidence.
[C1]–[C21] frame, PAB-min-score, topscorer split, 2024 PPB/CLB removal verified.

## G. Team/Olympiad evidence
C.04.6 2026 chapter located (TPN/brackets/upfloaters, PAB draw) + Olympiad 2022
Rules (matchpoints, median processing, board-1 colours, §4.1 live pointer).
Bodies pending; team layer PROPOSED outside core v1.

## H. Secondary references
S-0101…S-0108 + BBP/JaVaFo→FIDE mapping table in SECONDARY_SOURCES.md.
BBP Burstein never an oracle (self-declared flawed).

## I. Remaining research debt (genuine gaps only)
- G-01: full article bodies (manual browser path; Q-01/Q-02 queued).
- G-02: F-0106 direct chapter re-verification. G-04: pre-2026 Dubov/Burstein/Lim
  individual archive URLs. Lim depth (thinnest file).
- No invented content anywhere: every gap is labelled, every claim has a Source ID.

## Quality gate (§30) — self-check
Source completeness ✓ (all C.04/C.05/D.02 searched; dates + supersession set).
System coverage ✓ (10 systems incl. variants + KO boundary; §32 — did not stop
at Dutch). Evidence ✓ (50 Rule IDs → Source → section/version).
Repository ✓ (registry + notes + matrices + timeline + manifest committed;
validator green; no secrets; no vendored copyrighted bulk; links verified
2026-10-03; behavior diff zero).

## Z. Hostile conformance audit addendum (2026-10-03; supersedes conflicting
##    implementation claims above — research conclusions stand, corrected
##    where the audit disproved an implementation reading)

Method: every 2026 engine re-read against CM3-202517 FULL_TEXT (+ Annotated
Dutch V2026); 20 implementation defects fixed (docs/audit/
FIDE_CONFORMANCE_FINAL_REPORT.md §5); 30-test adversarial corpus +
2026 property suite + 2026 performance gates added (474 passed / 16 skipped).

Corrections to prior implementation claims:

1. "Lim 3.9 folded into selection order" — INACCURATE. No 3.9 evaluation
   existed (selection was due-colour + number only). 3.9 a–d is now explicit
   in floater selection; 3.3/3.4/3.5/3.6/3.7/3.8 implemented alongside.
2. "Dutch PAB past-(score,unplayed) uses largest-TPN family convention" —
   reclassified INTERPRETATION I-D-PAB (C.04.3 silent; convention borrowed
   from Dubov 3.1.5 / Double-Team 3.4.4 / Burstein 3.1.5 where explicit).
3. "Double/Team min-vector + generation tiebreak" — retained with narrowed
   justification I-T-C7 (coincides with "first complying" iff a zero exists;
   graceful otherwise; strict zero-filter would fail ordinary rounds).
4. "BSN/id-space confusion after exchanges" (Burstein, fixed deffe5d) —
   re-verified fixed; the SAME bug class was found and fixed in Double/Team
   3.6 identifier handling (id≠TPN KeyError/mis-pairing).
5. Dutch C8 "restricted look-ahead" — probe now uses the heterogeneous
   machinery (MDPs pair residents-only); RSL pre-sizing still absent
   (documented approximation).
6. Olympiad evidence: F-0601 primary PDF not re-retrievable this wave
   (handbook bot-wall); Olympiad rows rest on the 2026-10-03 FULL_TEXT
   evidence record; 8.x.3 and the 88-team example stay unresolved.
7. BBP differential scope: BBP implements 2025 Dutch + a flawed previous
   Burstein (per its README) — cross-version comparison is meaningless and
   was not performed; version-scoped legacy oracles pass (12 BBP + JaVaFo).
8. Performance: exact-search architecture ceilings measured (Dutch/Burstein
   big brackets → typed budget timeouts; R1 + realistic sizes succeed).
   No pruning heuristics introduced (conformance risk); budgets derived from
   measurements (test_benchmarks_2026 + benchmarks_2026.json).
