# SYSTEM COVERAGE MATRIX

No cell populated by inference; gaps say so. As of 2026-10-03.

| System | Latest source | Effective date | Full algorithm? | Official examples? | Implementation possible? | pairing-core status |
|---|---|---|---|---|---|---|
| Dutch | F-0105 (C.04.3 2026) | 01-02-2026 | PARTIAL (frame; bodies G-01) | TBD (in full text) | PARTIAL (architecture set) | frozen `dutch-till2026-compat`; `dutch-2026` rejected |
| Dutch till-2026 | F-0107 | till 31-01-2026 | YES (A–E excerpts + structure) | via TEC/AUM | YES (kernel = compat spec) | F1 goldens = executable spec |
| Dubov | F-0108 (C.04.4.1) | 01-02-2026 | PARTIAL | TBD | PARTIAL | NO engine; RESEARCH CONTINUES |
| Burstein | F-0110 (C.04.4.2) | 01-02-2026 | PARTIAL | TBD | PARTIAL | NO engine; RESEARCH CONTINUES |
| Lim | F-0112 (C.04.4.3) | 01-02-2026 | PARTIAL (thinnest) | TBD | NO (article text needed) | NO engine; RESEARCH CONTINUES |
| Double Swiss | F-0114 (C.04.5) | 01-02-2026 | PARTIAL | TBD | PARTIAL (needs match model) | NO engine; RESEARCH CONTINUES |
| Team Swiss | F-0115 (C.04.6) | 01-02-2026 | PARTIAL | TBD | PARTIAL (needs team layer) | NO engine; RESEARCH CONTINUES |
| Olympiad | F-0601 (2022 Rules) | 01-01-2022 | PARTIAL | TBD | PARTIAL (needs team layer) | NO engine; RESEARCH CONTINUES |
| Baku accel. | F-0117 (C.04.7) | 01-02-2026 | PARTIAL | TBD | PARTIAL (needs virtual-pt model) | NO model; RESEARCH CONTINUES |
| Berger RR | F-0501 (C.05 Ann.1) | current | YES | tables = examples | YES | IMPLEMENTED + validated |
| KO/match/playoff | Hbk 07 art.3 + F-0114 | current | boundary YES | n/a | n/a (management) | OUT (boundary set) |

## Coverage rule
A system leaves RESEARCH CONTINUES only with full article text in hand
(machine- or manually-retrieved) mapped Rule ID → section. Berger is the only
FULLY SPECIFIED system; KO/match is fully specified *as a boundary*.

## Completion-wave implementation (2026-10-03)

| System | Engine | Evidence | Conformance status |
|---|---|---|---|
| Dutch-2026 | `fide2026/dutch.py` (`dutch-2026`) | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (PAB-TPN tiebreak reading) |
| Dubov-2026 | `fide2026/dubov.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (ratings + prior_upfloats caller duties) |
| Burstein-2026 | `fide2026/burstein.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (round_results + virtual-strip duties) |
| Lim-2026 | `fide2026/lim.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (3.9-folding reading) |
| Double-2026 | `fide2026/double_team.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (min-vector reading; valuation OUT) |
| Team-2026 | `fide2026/double_team.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (min-vector reading; line-ups OUT) |
| Baku-2026 | `fide2026/baku.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (list-management caller-side) |
| Olympiad-2022 | `fide2026/olympiad.py` | FULL_TEXT | IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (Arts.10–11 + valuation OUT) |
| Berger | `roundrobin.py` (pre-existing) | FULL_TEXT | FULLY_IMPLEMENTED_AND_EVIDENCED |
| KO/match | boundary only | CONTEXT | OUT_OF_SCOPE_WITH_REASON |

## Audit-wave amendments (2026-10-03)

Per-system status is UNCHANGED in kind (no 2026 system reaches
FULLY_IMPLEMENTED_AND_EVIDENCED — each retains explicit interpretations /
gaps, now precisely itemised in docs/audit/FIDE_CONFORMANCE_MATRIX.md), but
20 conformance defects were fixed and the evidence basis strengthened
(30-test adversarial corpus, 2026 property suite, 2026 perf gates,
version-scoped differential oracles). Amendments:

- Dutch-2026: BSN/MDP/exchange-ordering defects fixed; PAB tiebreak
  reclassified INTERPRETATION (I-D-PAB); C8 probe hetero-exact.
- Dubov-2026: G1 extremes, 3.2.4.1 shift, real-pairing C7 fixed.
- Burstein-2026: C6 sign, C7 scope, incoming loop, enumeration fixed.
- Lim-2026: scrutiny/columns/even-making/2.6/3.x/4.4/5.4/Art.6 fixed;
  upward-mirror + 4.4-culprit + 5.5/5.6-heuristic interpretations recorded.
- Double/Team-2026: C5 construction, id/TPN spaces, Team 4.3.7 + secondary
  fixed; first-vs-min fork recorded (I-T-C7); match/C1FB/C3 limits recorded.
- Baku-2026: unchanged (pure functions, official numbers pinned).
- Olympiad-2022: floater routing fixed; 8.x.3 + 88-team example unresolved
  (no primary PDF this wave).
- Berger: unchanged (even 4–12 pinned; odd/double structural).
