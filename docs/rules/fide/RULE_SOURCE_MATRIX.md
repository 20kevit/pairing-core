# RULE → SOURCE MATRIX (with implementation traceability, §9)

Rule ID → Source ID → section → evidence → implementation → test → status.
"FULL_TEXT" = Council-bundle/official-PDF text read in full (hashes in
SOURCE_MANIFEST.md). Rule IDs stable: original 49 rows preserved verbatim;
traceability appended, new rules appended (never renumbered).

| Rule ID | System | Requirement | Source | Section | Version / effective | Evidence | Implementation | Test / case | Status |
|---|---|---|---|---|---|---|---|---|---|
| R-D01 | Dutch | No rematch (mandatory, top criterion) | F-0101 | C.04.1 general rules; C1 | 2026 / 01-02-2026   | FULL_TEXT | fide2026/dutch.py:_abs_ok | test_dutch_c1 | EVIDENCED | |
| R-D02 | Dutch | No second PAB; forfeit-win exclusion | F-0101 | C.04.1 Art.4 lineage; C2 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_abs_ok+pab_eligible | test_dutch_c1/c3+pab | EVIDENCED | |
| R-D03 | Dutch | Same-absolute-colour non-topscorers shall not meet | F-0105 | C3 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_abs_ok | test_dutch_c3 | EVIDENCED | |
| R-D04 | Dutch | Completion: maximise pairs | F-0105 | C4 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_rest_pairable | c1/c3 tests | EVIDENCED | |
| R-D05 | Dutch | PAB to lowest score | F-0105 | C5 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:PAB loop (C5) | odd-field test | EVIDENCED | |
| R-D06 | Dutch | Minimise downfloater count | F-0105 | C6 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c6 | vector order | EVIDENCED | |
| R-D07 | Dutch | Minimise downfloater scores (descending) | F-0105 | C7 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c7 | vector order | EVIDENCED | |
| R-D08 | Dutch | Downfloater suitability for next bracket | F-0105 | C8 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_c8_next_vector (1 deep) | engine runs | EVIDENCED | |
| R-D09 | Dutch | Minimise PAB recipient's unplayed games | F-0105 | C9 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c9 | pool-minimal | EVIDENCED | |
| R-D10 | Dutch | Colour controls (topscorer ±2, 3×colour, preferences) | F-0105 | C10–C13 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c10-c13 | allocation | EVIDENCED | |
| R-D11 | Dutch | Minimise float repetition | F-0105 | C14–C17 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c14-c17 | float tags | EVIDENCED | |
| R-D12 | Dutch | Minimise float score gaps | F-0105 | C18–C21 | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_vector c18-c21 | engine runs | EVIDENCED | |
| R-D13 | Dutch(till) | S1/S2 halves; P0/MDP/BSN/Limbo machinery | F-0107 | A–B | till / till-31-01-2026   | FULL_TEXT | frozen kernel (compat) | F1 goldens | FROZEN-COMPAT | |
| R-D14 | Dutch(till) | Transpositions then resident-only exchanges | F-0107 | D.1 / D.2 | till / till-31-01-2026   | FULL_TEXT | frozen kernel (compat) | F1 goldens | FROZEN-COMPAT | |
| R-D15 | Dutch(till) | Heterogeneous remainder as homogeneous | F-0107 | B.7 | till / till-31-01-2026   | FULL_TEXT | frozen kernel (compat) | corpus | FROZEN-COMPAT | |
| R-D16 | Dutch(till) | Colour allocation priorities E.1–E.4 | F-0107 | E.1–E.4 | till / till-31-01-2026   | FULL_TEXT | dutch.py:allocate_colour 5.2.1-5.2.4 | allocation tests | EVIDENCED | |
| R-D17 | Dutch(till) | E.5 initial-colour parity (odd pno) | F-0107 | E.5 | till / till-31-01-2026   | FULL_TEXT | dutch.py:allocate_colour 5.2.5 | R1 parity test | EVIDENCED | |
| R-D18 | Dutch(till) | Colour preference triggers abs/strong/mild | F-0107 | A.6 | till / till-31-01-2026   | FULL_TEXT | fide2026/common.py:preference | preference tests | EVIDENCED | |
| R-D19 | Dutch | PAB value win unless regs state otherwise | F-0101 | C.04.1 art. 3 | 2026 / 01-02-2026   | FULL_TEXT | manager-side valuation (unmodelled); selection per C5 | odd-field test | SELECTION-ONLY | |
| R-D20 | Dutch(till) | PAB value draw unless regs state otherwise | F-0102 | C.04.1.c old | till / till-31-01-2026   | FULL_TEXT | frozen kernel (compat) | F1 goldens | FROZEN-COMPAT | |
| R-D21 | Dutch | Played-only colour history | F-0105 | colour articles (TBD) | 2026 / 01-02-2026   | FULL_TEXT | common.py:played_colors (u-drop) | colour tests | EVIDENCED | |
| R-D22 | Dutch | "Arbiter shall decide" on impossibility | F-0107 | completion clause | till (principle survives)   | FULL_TEXT | ImpossiblePairingError | c1/c3 tests | EVIDENCED | |
| R-D23 | Dutch | Pairing numbers break all ranking ties | F-0103 | TPN/initial order | 2026 / 01-02-2026   | FULL_TEXT | dutch.py:_bsn/1.2 order | R1 test | EVIDENCED | |
| R-D24 | Dutch(2025) | Fewer-games players excluded from PAB candidacy | F-0106 | PAB types article | interim / 01-07-2025   | OFFICIAL_PDF | C9 superset (interim) | odd-field test | EVIDENCED | |
| R-U01 | Dubov | No downfloaters (upfloaters only) | F-0108 | bracket rules | 2026 / 01-02-2026   | FULL_TEXT | dubov.py:upfloaters-only | engine runs | EVIDENCED | |
| R-U02 | Dubov | Two-step: fix counts (C1–C5), then best pairing | F-0108 | procedure | 2026 / 01-02-2026   | FULL_TEXT | dubov.py:3.2.1-3.2.2 | set selection | EVIDENCED | |
| R-U03 | Dubov | Completion C4; quality C5 max pairs | F-0108 | C4–C5 | 2026 / 01-02-2026   | FULL_TEXT | dubov.py:C4/C5 | set selection | EVIDENCED | |
| R-U04 | Dubov | C6 max incoming floaters (number then score) | F-0108 | C6 | 2026 / 01-02-2026   | FULL_TEXT | dubov.py:_bracket_vector C6 | vector | EVIDENCED | |
| R-U05 | Dubov | C7 outgoing floaters optimise next bracket | F-0108 | C7 | 2026 / 01-02-2026   | FULL_TEXT | dubov.py:_colour_misses C7 | C7 | EVIDENCED | |
| R-B01 | Burstein | Ranking order = Buchholz then SB | F-0110 | ranking article | 2026 / 01-02-2026   | FULL_TEXT | burstein.py:rank_key | buchholz_sb test | EVIDENCED | |
| R-B02 | Burstein | Median cracking §§2.6.1/2.6.2 | F-0110 | §2.6.1–2 | 2026 / 01-02-2026   | FULL_TEXT | burstein.py:median cracking ABSENT in 2026 (corrected) | n/a (correction) | CORRECTED | |
| R-B03 | Burstein | Own acceleration default (no XXA) | F-0110 via S-0101 | accel. semantics | 2026 / 01-02-2026   | FULL_TEXT | own-accel note; virtual stripped caller-side | n/a | DOCUMENTED | |
| R-L01 | Lim | Bi-directional processing around median | F-0112 | procedure | 2026 / 01-02-2026   | FULL_TEXT | lim.py:median routing | R2 test | EVIDENCED | |
| R-L02 | Lim | Median-group up/down pairing + exchanges | F-0112 | median article | 2026 / 01-02-2026   | FULL_TEXT | lim.py:median+cracking+exchanges | corpus tables | EVIDENCED | |
| R-L03 | Lim | Strict colour rules | F-0112 | colour articles | 2026 / 01-02-2026   | FULL_TEXT | lim.py:_lim_colour | colour tests | EVIDENCED | |
| R-L04 | Lim | Bye to bottom-group lowest-ranked | F-0112 | bye article | 2026 / 01-02-2026   | FULL_TEXT | lim.py:Art.1 PAB | bye tests | EVIDENCED | |
| R-T01 | Double | 2-game alternating-colour match; score = sum | F-0114 | match format | 2026 / 01-02-2026   | FULL_TEXT | additive match model (pairs+colours) | double R1 | EVIDENCED | |
| R-T02 | Double | PAB = win+draw value | F-0114 | PAB article | 2026 / 01-02-2026   | FULL_TEXT | selection per 3.4; value manager-side | PAB paths | SELECTION-ONLY | |
| R-T03 | Double | Upfloater pairing | F-0114 | float article | 2026 / 01-02-2026   | FULL_TEXT | double_team.py:select_upfloaters | corpus sets | EVIDENCED | |
| R-M01 | Team | Teams as units; TPN/brackets/upfloaters | F-0115 | general | 2026 / 01-02-2026   | FULL_TEXT | double_team.py (team units/TPN) | team R1 | EVIDENCED | |
| R-M02 | Team | PAB = draw value | F-0115 | PAB article | 2026 / 01-02-2026   | FULL_TEXT | selection per 3.4; value manager-side | PAB paths | SELECTION-ONLY | |
| R-M03 | Olympiad | 11-round team Swiss, matchpoints, median processing | F-0601 | general | 2022 / 01-01-2022   | FULL_TEXT | olympiad.py:median routing | median test | EVIDENCED | |
| R-M04 | Olympiad | Board-1 colour rules | F-0601 | colour article | 2022 / 01-01-2022   | FULL_TEXT | olympiad.py:board colours | colour tests | EVIDENCED | |
| R-A01 | Baku | GA/GB split + virtual points | F-0117 | accel. articles | 2026 / 01-02-2026   | FULL_TEXT | baku.py premise (parameterised) | schedule tests | EVIDENCED | |
| R-A02 | Baku | Full XXA history for floater computation | F-0117 via S-0102 | input rule | 2026 / 01-02-2026   | FULL_TEXT | XXA carriage noted; caller-side history | n/a | DOCUMENTED | |
| R-G01 | Berger | Fixed tables 3–16; odd N highest bye | F-0501 | Annex 1 | current   | FULL_TEXT | roundrobin.py (pre-existing) | RR goldens | EVIDENCED | |
| R-G02 | Berger | Double-RR colour swap + last-two reversal | F-0501 + ECU | Annex 1 note | current / recommendation   | CONTEXT | roundrobin double cycle | RR tests | EVIDENCED | |
| R-K01 | KO | Format/colour/pno regulated per event (Hbk 07 art. 3) | F-0601 parent ctx | Handbook 07 | current   | CONTEXT | boundary only (no engine) | n/a | OUT-OF-SCOPE | |
| R-Q01 | All | QC authorisation for unpublished systems | F-0103 | C.04.2 §1.2–1.3 | 2026 / 01-02-2026   | FULL_TEXT | documented (no QC flow in library) | n/a | DOCUMENTED | |
| R-D25 | Dutch | 5.2.5 odd-TPN parity (E.5 successor) | F-0105 | 5.2.5 | 2026 / 01-02-2026 | FULL_TEXT | dutch.py:allocate_colour | R1 parity test | EVIDENCED |
| R-D26 | Dutch | C8 one-bracket look-ahead depth | F-0105 | C8/2.4.3 | 2026 / 01-02-2026 | FULL_TEXT | dutch.py:_c8_next_vector | engine runs | EVIDENCED |
| R-D27 | Dutch | M0/M1/MaxPairs/Limbo/S1/S2 machinery | F-0105 | Art.3 | 2026 / 01-02-2026 | FULL_TEXT | dutch.py:_iter_heterogeneous | engine runs | EVIDENCED |
| R-D28 | Dutch | 4.2/4.3/4.4 generation order | F-0105 | Art.4 | 2026 / 01-02-2026 | FULL_TEXT | dutch.py generators | R1 test | EVIDENCED |
| R-U06 | Dubov | MaxT = 2+floor(Rnds/5) | F-0108 | 1.8 | 2026 / 01-02-2026 | FULL_TEXT | dubov.py:max_t + prior_upfloats | MaxT test | EVIDENCED |
| R-U07 | Dubov | G1/G2 + ARO sort + shifters + T2 | F-0108 | 3.2.3-3.2.6/Art.4 | 2026 / 01-02-2026 | FULL_TEXT | dubov.py:_pair_bracket | R1/R2 tests | EVIDENCED |
| R-U08 | Dubov | PAB order (eligible/completion/score/games/TPN) | F-0108 | 3.1 | 2026 / 01-02-2026 | FULL_TEXT | dubov.py:_select_pab | engine runs | EVIDENCED |
| R-B04 | Burstein | Seeding min(floor(R/2),4) Dutch rounds | F-0110 | 1.6 | 2026 / 01-02-2026 | FULL_TEXT | burstein.py + dutch delegation | seeding test | EVIDENCED |
| R-B05 | Burstein | Index computation (BH/SB/self-game/virtual-excl) | F-0110 | 1.7 | 2026 / 01-02-2026 | FULL_TEXT | burstein.py:buchholz_sb | BH/SB test | EVIDENCED |
| R-B06 | Burstein | PAB lowest-score/games/lowest-rank | F-0110 | 3.1 | 2026 / 01-02-2026 | FULL_TEXT | burstein.py:_select_pab | engine runs | EVIDENCED |
| R-L05 | Lim | Compatibility (unplayed + colour bans) | F-0112 | 2.1 | 2026 / 01-02-2026 | FULL_TEXT | lim.py:compatible | compat test | EVIDENCED |
| R-L06 | Lim | Blocked-median cracking 2.6.1/2.6.2 | F-0112 | 2.6 | 2026 / 01-02-2026 | FULL_TEXT | lim.py:_pair_median | engine runs | EVIDENCED |
| R-L07 | Lim | Floater a-d hierarchy + 3.10 guard | F-0112 | 3.9-3.10 | 2026 / 01-02-2026 | FULL_TEXT | lim.py selection order + _refloat_allowed | engine runs | EVIDENCED-READING |
| R-L08 | Lim | R1/R2 recipes | F-0112 | Arts.7-8 | 2026 / 01-02-2026 | FULL_TEXT | lim.py:_round_one + order | corpus lim_round_one | EVIDENCED |
| R-L09 | Lim | Last-round same-score override | F-0112 | Art.6 | 2026 / 01-02-2026 | FULL_TEXT | structural (pairing duty first) | engine runs | EVIDENCED |
| R-T04 | Double | Match result table + forfeit rules | F-0114 | Preface | 2026 / 01-02-2026 | FULL_TEXT | input domain (manager-side results) | n/a | DOCUMENTED |
| R-T05 | Double | HRP colour chain | F-0114 | Art.4 | 2026 / 01-02-2026 | FULL_TEXT | double_team.py:double_colour | colour test | EVIDENCED |
| R-M05 | Team | Type A/B/none preferences | F-0115 | 1.7 | 2026 / 01-02-2026 | FULL_TEXT | common.py:team_preference | pref tests | EVIDENCED |
| R-M06 | Team | First-team + colour chain | F-0115 | Art.4 | 2026 / 01-02-2026 | FULL_TEXT | double_team.py:team_colour | colour test | EVIDENCED |
| R-M07 | Olympiad | Bye lowest initial number (4.2.1-4.2.3) | F-0601 | Art.4 | 2022 / 01-01-2022 | FULL_TEXT | olympiad.py:select_olympiad_bye | bye test | EVIDENCED |
| R-M08 | Olympiad | Median routing + groups | F-0601 | 6.2-6.4 | 2022 / 01-01-2022 | FULL_TEXT | olympiad.py median order | median test | EVIDENCED |
| R-M09 | Olympiad | 9.x search + 8.x floaters + 7.x colours | F-0601 | Arts.7-9 | 2022 / 01-01-2022 | FULL_TEXT | olympiad.py | corpus 9x table | EVIDENCED |
| R-A03 | Baku | GA split 2*ceil(N/4) | F-0117 | 1.2 | 2026 / 01-02-2026 | FULL_TEXT | baku.py:split_groups | corpus baku | EVIDENCED |
| R-A04 | Baku | Virtual schedule + examples | F-0117 | 1.4 | 2026 / 01-02-2026 | FULL_TEXT | baku.py:virtual_points | corpus baku | EVIDENCED |
| R-A05 | Baku | Pairing score = standings + virtual | F-0117 | 1.5 | 2026 / 01-02-2026 | FULL_TEXT | baku.py:pairing_scores | score test | EVIDENCED |
| W-01 | (withdrawn) | Absolute float-bar (no citation, any era) | — | — | — | WITHDRAWN | NOT implemented anywhere | n/a | WITHDRAWN |
