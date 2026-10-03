# FIDE Conformance Matrix (hostile audit wave, 2026-10-03)

Source of truth: Council bundle CM3-202517 (FULL_TEXT, 1871 lines) + Annotated
Dutch V2026 + Mastering Dutch 2026 + Terms 2026 (all read in full; nothing
vendored). Olympiad F-0601 primary PDF unavailable to this wave (handbook
bot-wall); Olympiad rows rest on OLYMPIAD_EVIDENCE.md (FULL_TEXT retrieval
record 2026-10-03) and are marked accordingly.

Statuses: VERIFIED | VERIFIED_BY_OFFICIAL_EXAMPLE | VERIFIED_BY_DERIVED_CASE
| DIFFERENTIAL_ONLY | INTERPRETATION | UNRESOLVED.

Code refs are `src/pairing_core/fide2026/*`; tests are `tests/test_hostile_audit.py`
(H-*), `tests/test_fide2026.py`, `tests/test_properties_2026.py`,
`tests/corpus/fide_official/*`.

## Dutch 2026 (C.04.3)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 1.1–1.2 ranking/scoregroups/brackets | 1.1–1.3 | dutch.pair_dutch | H-dutch-heterogeneous | VERIFIED | score desc, TPN asc |
| 1.4 floats/MDP/Limbo | 1.4.1–1.4.4 | dutch | H goldens | VERIFIED | |
| 1.5 PAB | C.04.1 Art.3 (via 1.5) | common.pab_eligible | suite | VERIFIED | |
| 1.6 colour difference | 1.6 | common.colour_difference | suite | VERIFIED | |
| 1.7 preferences | 1.7.1–1.7.4 | common.preference | H-guard | VERIFIED | zero-game = none |
| 1.8 topscorers | 1.8 | dutch (is_last_round) | suite | VERIFIED | score > 50% max |
| 1.9 outlook | 1.9.1–1.9.3 | pair_dutch top-down + typed error | H | VERIFIED | |
| 5.1–5.2.5 colours | 5.1–5.2.5 | allocate_colour | suite | VERIFIED | chain incl. 5.2.5 parity |
| 5.2.3 alternation alignment | C.04.2 Art.3.4 (note under 5.2.3) | _alternate_from_encounter (round-aligned) | H-walkback | VERIFIED | played-only per round |
| C1–C3 absolute | 2.1.1–2.1.3 | _abs_ok | H-C1/C3 | VERIFIED | topscorer carve-out in C3 |
| C4 completion | 2.2.1 | _rest_pairable/_even_pairable | H/PAB tests | VERIFIED_BY_DERIVED_CASE | existence probe, budget-guarded |
| C5 PAB score | 2.3.1 | _vector c5 + PAB options | H-PAB | VERIFIED | |
| C5 post-(score,unplayed) tie | — (C.04.3 silent) | PAB order (-tpn) | H-PAB-largest-TPN | INTERPRETATION | I-D-PAB: family convention (Dubov 3.1.5 etc. explicit) |
| C6/C7 downfloaters | 2.4.1–2.4.2 | _vector c6/c7 | H | VERIFIED | |
| C8 look-ahead | 2.4.3 | _c8_next_vector (hetero machinery, C1–C7, one bracket) | H/properties | VERIFIED_BY_DERIVED_CASE | approx: no RSL pre-sizing; C5-in-probe excluded; (0,()) early-exit exact |
| C9 unplayed | 2.4.4 + note | _vector c9 | H-PAB | VERIFIED | single-PAB-bracket scope per note |
| C10–C21 | 2.4.5–2.4.16 | _vector c10–c21 | suite | VERIFIED_BY_DERIVED_CASE | topscorer-pool, gaps desc |
| 3.1 M0/M1/MaxPairs | 3.1–3.2 | _iter_hetero/max_pairs | H | VERIFIED | M1 ≤ residents, ≤ MaxPairs |
| 3.3 candidates | 3.3.1–3.3.3 | pair construction | H | VERIFIED | M1=0 direct remainder |
| 3.4 perfect | 3.4.1 | _quality_zero + short-circuit | perf (R1) | VERIFIED | C5 handled separately |
| 3.5/3.6 alterations | 3.5–3.6.1 | deferred exchanges + transpositions | H | VERIFIED | exchange order computed only when needed |
| 3.7 hetero alterations | 3.7.1–3.7.3 | _iter_heterogeneous (S1R/S2R frozen, S2 restored) | H | VERIFIED | |
| 3.8 best + earlier | 3.8.1 | min-vector + stable generation order | H | VERIFIED | |
| 4.1 BSN | 4.1.1 | _bsn (-score, tpn) | H-BSN (B1) | VERIFIED | was inverted; fixed + pinned |
| 4.2 transpositions | 4.2.1–4.2.2 + 11-pl/2-MDP counts | _s2_transpositions | suite | VERIFIED | 720 / 72 counts match; ticks added |
| 4.3 exchanges | 4.3.1–4.3.2 + worked rules | _resident_exchanges | suite | VERIFIED_BY_OFFICIAL_EXAMPLE | 6↔4>8↔5, 5>4, 6>7 patterns hold |
| 4.4 MDP sets | 4.4.1–4.4.2 + annotated {1,3}<{1,4}<{3,4} | _mdp_sets (kept-lex, larger-first) | H-MDP (B2) | VERIFIED_BY_OFFICIAL_EXAMPLE | validity pre-filter (C7+C4) approximated by global-min selection: INTERPRETATION I-D-MDPVALID |
| 4.5 next element | 4.5.1 | generator order | H | VERIFIED | |

## Dubov 2026 (C.04.4.1)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 1.1 ratings mandatory | 1.1.1–1.1.2 | _check_ratings (typed) | suite | VERIFIED | caller duty, never inferred |
| 1.6 prefs + 1.6.4 zero-game | 1.6.1–1.6.4 | preference(dubov_zero_game) | suite | VERIFIED | mild Black |
| 1.7 ARO half-up, played-only | 1.7.1–1.7.3 | aro() Fractions | suite | VERIFIED_BY_DERIVED_CASE | |
| 1.8 MaxT | 1.8.1–1.8.2 | max_t() | suite | VERIFIED | 2 + floor(R/5) |
| C1–C4 | 2.1–2.2 | _bracket_ok/completion | H | VERIFIED | legal = C1+C3+C4 (3.2.1 note) |
| C5/C6 count+gaps | 2.3.1–2.3.2 + "i.e." clause | key (k, -scores) | H-C5 | VERIFIED | maximise-scores-asc == minimise-gaps |
| C7 colours | 2.3.3 | real S1×T2 misses (B9 fix) | H-C7 | VERIFIED_BY_DERIVED_CASE | was greedy estimate |
| C8–C10 guards | 2.3.4–2.3.6 | up_count/last_float, last-round off | suite | VERIFIED | |
| 3.1 PAB 3.1.1–3.1.5 | 3.1.1–3.1.5 | _select_pab (score,-played,-tpn) | suite | VERIFIED | largest TPN explicit in FIDE |
| 3.2.1/3.2.2 upfloaters | 3.2.1–3.2.2 + 4.2.3 | _select_upfloaters (min-k, seq order, full-legality via real pairing) | H | VERIFIED | C1+C3 (not rematch-only) |
| 3.2.3 G1/G2 | 3.2.3 | _pair_bracket | H-G1 (B7) | VERIFIED | TPN-half ONLY if all unplayed |
| 3.2.4 shifts | 3.2.4.1–3.2.4.2 + note | _rebalance/_phase1_search/_best_shift (actual-pairing C7) | H-phase1 (B8) | VERIFIED_BY_DERIVED_CASE | phase-1 was dead; greedy removed |
| 3.2.5 S1 | 3.2.5 | ARO/TPN sort | suite | VERIFIED | |
| 3.2.6 first T2 | 3.2.6 + 4.4.2 worked ABC | _find_transposition | suite | VERIFIED_BY_OFFICIAL_EXAMPLE | ABCACB… order; empty-S1 guard added |
| 4.1–4.2 pools/sets | 4.1.1–4.2.3 | lexicographic_sets + seq ranks | H | VERIFIED | |
| 4.3 shifters + A–G example | 4.3.1–4.3.3 + worked D,C,E,… | _shifter_order | suite (middle-outward) | VERIFIED_BY_OFFICIAL_EXAMPLE | |
| Art.5 colours | 5.2.1–5.2.5 | dubov_colour (round-aligned 5.2.4) | H-walkback | VERIFIED | post-5.2.5 fallthrough documented |

## Burstein 2026 (C.04.4.2)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 1.2 brackets/incoming | 1.2.1–1.2.2 | pair_burstein loop (score-ordered, incoming joins) | H-loop | VERIFIED | loop was broken (floaters dropped); fixed |
| 1.6 seeding | 1.6.1–1.6.2 | seeding_rounds + Dutch delegation | suite | VERIFIED | min(floor(R/2),4) |
| 1.7 opposition | 1.7–1.7.2 | buchholz_sb + round_results typed input | suite | VERIFIED_BY_DERIVED_CASE | virtual-points stripping is caller duty (contract) |
| 1.8 ranking | 1.8.1 | rank_key (Index, TPN; scores unused) | H | VERIFIED | |
| C1–C4 | 2.1–2.2 | _c1c3_ok + probes | H | VERIFIED | no topscorer carve-out (unlike Dutch) |
| C5 max pairs | 2.3.1 | _max_pairs | H | VERIFIED | |
| C6 min outgoing scores | 2.3.2 | _choose_pairing (unnegated) | H-C6 (B4) | VERIFIED | was inverted; fixed + pinned |
| C7 next bracket | 2.3.3 | _next_bracket_ok (determined scope) | H-C7 (B5) | VERIFIED_BY_DERIVED_CASE | was scope-blind; fixed |
| C8 colours | 2.3.4 | _colour_misses | suite | VERIFIED | |
| 3.1 PAB (lowest ranking) | 3.1.1–3.1.5 | _select_pab (_Rev rank) | suite | VERIFIED | |
| 3.2.1 preparation | 3.2.1.1–3.2.1.3 | _max_pairs + virtual count | H | VERIFIED | |
| 3.2.2 first+best | 3.2.2.1–3.2.2.2 | min-vector + Art.4 tiebreak + C7 filter | H | VERIFIED | + exact lex-first fast path (zero case) |
| Art.4 + 6-player table | 4.1–4.3 + worked table | enumerate (deduped, guarded) | H-table (B6) + corpus | VERIFIED_BY_OFFICIAL_EXAMPLE | head 1-6,2-5,3-0,4-0; count 45 |
| Art.5 colours | 5.2.1–5.2.5 | burstein_colour (round-aligned 5.2.4) | H-walkback | VERIFIED | 5.2.1 first (unlike Dutch) |

## Lim 2026 (C.04.4.3)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| Art.1 PAB | 1.1 | lowest-TPN... (max tpn = lowest rank) in lowest group | suite | VERIFIED | |
| 2.1 compatible | 2.1 | compatible() | H-Art6 | VERIFIED | + Art.6 last-round lift (B-L6) |
| 2.2 routing/median | 2.2 | order above→below→median; median=rounds/2 | suite/H-26 | VERIFIED | |
| 2.3 triggers | 2.3.1–2.3.4 | _needs_floater + even-making | H-even | VERIFIED | |
| 2.4 proposed | 2.4 | top-vs-bottom 1v(n/2+1) | H-columns | VERIFIED | |
| 2.5 exchanges | 2.5 | Art.4 machinery | H | VERIFIED | |
| 2.6 cracking | 2.6.1–2.6.2 | _pair_median (adjacent-group crack, side by counts) | H-26 (B18) | VERIFIED_BY_DERIVED_CASE | was median-self priority; fixed |
| 3.1–3.2.1 | 3.1–3.2.1 | _float_one direction | H | VERIFIED | |
| 3.2.2 majority | 3.2.2 | majority side (B16 fix) | H-even | VERIFIED | was minority; fixed |
| 3.2.3 maxi | 3.2.3 | 100pt guard + 3.8 proviso | suite | VERIFIED | |
| 3.2.4 number | 3.2.4 | min/max TPN | H-even | VERIFIED | |
| 3.3/3.4 + 3.9 | 3.3/3.4/3.9.1–3.9.2 | 3.9-type in selection; compat pools | H | VERIFIED_BY_DERIVED_CASE | opponent-exclusion approximated: I-L-334 |
| 3.5 exchange/further | 3.5 | _float_one | H (via 44) | VERIFIED_BY_DERIVED_CASE | |
| 3.6/3.7 priority | 3.6–3.7.3 | _scrutiny_order | H-priority | VERIFIED_BY_DERIVED_CASE | |
| 3.8 opponent pref | 3.8 | 3.8-target tried first | H | VERIFIED_BY_DERIVED_CASE | "alternate colour" reading: I-L-38 |
| 3.10 refloat | 3.10–3.10.2 | _refloat_allowed (remainder-pairs) | suite | VERIFIED_BY_DERIVED_CASE | a/b/c-conditions approximated |
| 4.1 scrutiny | 4.1.1–4.1.2 vs 4.2 example | downward #1-first; upward mirror | H-scrutiny (B14) | VERIFIED_BY_OFFICIAL_EXAMPLE + INTERPRETATION | 4.1.1 phrasing contradicts 4.2 table; table wins; upward mirror I-L-412 |
| 4.2 columns | 4.2 table (1v4,1v5,1v6,1v3,1v2) | opponents_of (opp asc, same desc) | H-columns (B15) | VERIFIED_BY_OFFICIAL_EXAMPLE | #2-row interleaving approximated |
| 4.3 backtrack | 4.3–4.4 | backtracking + 4.4 recovery | H-44 (B17) | VERIFIED_BY_DERIVED_CASE | culprit generalisation I-L-44 |
| Art.5 colours | 5.1–5.7 | _lim_colour (round-aligned 5.4) | H-54 (B-L54) | VERIFIED_BY_DERIVED_CASE | 5.4 below-median flip fixed; 5.5/5.6 round-parity via CD heuristic: I-L-55 |
| Art.6 last round | 6 | compatible(last_round) lift | H-Art6 (B-L6) | VERIFIED | |
| Art.7 R1 | 7.1–7.3 + 40-player tables | _round_one | corpus lim_round_one | VERIFIED_BY_OFFICIAL_EXAMPLE | lowest-rated PAB; lot mirror |
| Art.8 R2 | 8.1–8.3 | routing | H-26 | VERIFIED | |

## Double Swiss 2026 (C.04.5)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| match model (2-game) | Preface + 1.6 | score/first-game-colour inputs (caller maps match↔games) | properties | INTERPRETATION | I-T-MATCH: game-level decomposition + PAB valuation applied caller-side |
| 1.2 order | 1.2 | (-score, tpn) keys | H-idspace | VERIFIED | |
| 1.3 brackets | 1.3 | top+upfloaters loop | H/properties | VERIFIED | |
| C1 repeat (+forfeit-both) | 2.1.1 | C.rematch (all repeats barred) | properties | INTERPRETATION | I-T-C1FB: model has no forfeit-both flag; exception unrepresentable |
| C2 PAB block | 2.1.2 | got_pab/forfeit_win | suite | VERIFIED | FPB deprecated: out of scope |
| C3 completion | 2.2.1 | next-bracket probe (C6) + existence | properties | INTERPRETATION | I-T-C3: next-bracket only, not full lookahead |
| C4/C5 count+gaps | 2.3.1–2.3.2 + example | construction (min-k legality-aware; max profile) | H-C5 (B10) + corpus | VERIFIED | k* legality-aware ("needed", 3.3.2): documented |
| C6 next bracket | 2.3.3 + note | _rest_next_bracket_ok (hard filter) | H | VERIFIED | "only mentioned scoregroup" per note |
| C7/C8 repeat guards | 2.3.4–2.3.5 | minimise + order tiebreak; last-round off | H-graceful | INTERPRETATION | I-T-C7: coincides with first-complying iff zero exists |
| 3.1 legal | 3.1.1–3.1.2 | C1/C2 + probes | H | VERIFIED | |
| 3.3 steps | 3.3.1–3.3.3 | PAB→brackets→colours; typed Arbiter error | H | VERIFIED | |
| 3.4 PAB | 3.4.1–3.4.4 | select_pab | suite | VERIFIED | largest TPN explicit |
| 3.5 sets | 3.5.1–3.5.5 + worked sets | select_upfloaters; 3.5.3/3.5.4 order | corpus double_upfloater_sets | VERIFIED_BY_OFFICIAL_EXAMPLE | |
| 3.6 identifiers | 3.6.1–3.6.3 + `4 6 9 11…` | enumerate_pairings + lex_first | corpus double_pairing_identifier + H-lexfirst | VERIFIED_BY_OFFICIAL_EXAMPLE | TPN/id spaces separated (B-ids) |
| 3.6.4 first+C1/C8 | 3.6.4 | min-vector + identifier tiebreak; lex-first zero fast path (exact) | H-graceful | INTERPRETATION | I-T-C7 (same fork as 3.5.5) |
| Art.4 colours | 4.2–4.4 | double_colour (round-aligned 4.3.3) | H-walkback | VERIFIED | White-holder opens White = output convention |

## Team Swiss 2026 (C.04.6)

As Double, plus:

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 1.2 primary/secondary | 1.2.1–1.2.2 | score/secondary fields; first-team always primary→secondary→TPN | H-kindnone (B12) | VERIFIED | secondary dropped only via caller passing 0 |
| 1.7 Type A/B/none | 1.7–1.7.2 | team_preference | suite (Type A/B) | VERIFIED | last-round CD-0 rule; unplayed = none |
| C8/C9/C10 | 2.3.5–2.3.7 | _violation_vector (priority order); last-TWO off | H | VERIFIED | |
| 3.6.4 first+C1/C8/C9/C10 | 3.6.4 | min-vector + tiebreak | H | INTERPRETATION | I-T-C7 |
| Art.4 first-team | 4.2.1–4.2.3 | team_colour ka/kb | H (B12) | VERIFIED | |
| Art.4 chain | 4.3.1–4.3.9 | team_colour incl. 4.3.7 (B11 fix) | H-437 (B11) | VERIFIED | 4.3.5 algebraic lower-CD; 4.3.6 round-aligned |

## Baku 2026 (C.04.7)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 1.1 premise | 1.1 | win_value params (no 1-½-0 hardcode) | suite | VERIFIED | |
| 1.2 GA split | 1.2 (161→82) | split_groups 2·ceil(N/4) | suite | VERIFIED_BY_OFFICIAL_EXAMPLE | |
| 1.3 late entries | 1.3 | documented caller-side | — | INTERPRETATION | boundary freeze not modelled |
| 1.4 schedule | 1.4.1–1.4.3 (9R + 11R team) | accelerated_rounds/virtual_points | suite | VERIFIED_BY_OFFICIAL_EXAMPLE | 1.0×3+0.5×2; 2×3+1×3 |
| 1.5 pairing score | 1.5 | pairing_scores | suite | VERIFIED | |

## Olympiad 2022 (F-0601; primary PDF unavailable — evidence-record basis)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| 3.x rank | 3.1–3.2 (evidence) | _rank (MP desc, number asc); initial number = caller TPN | suite | INTERPRETATION | I-O-RANK: avg-top-4 seeding is caller-side |
| 4.x bye | 4 (evidence) | select_olympiad_bye + late_entry | suite | VERIFIED_BY_DERIVED_CASE | |
| 5 unfinished | 5 (evidence) | caller scores | — | INTERPRETATION | draws-for-pairing caller-side |
| 6.x groups/median | 6–6.4 (evidence, 88-team ex.) | routing + lower-middle | H + suite | VERIFIED_BY_DERIVED_CASE | 88-team example not re-executed (no PDF): U-O-88 |
| 7.x board colours | 7.1–7.7 (evidence) | board1_colour + bans + 7.4 override | H-walkback | VERIFIED_BY_DERIVED_CASE | |
| 8.x floaters | 8.1–8.4 (evidence) | _select_floater (rank + completion) + routing | H-odd (B13) | VERIFIED_BY_DERIVED_CASE | 8.x.3 played-all preference: UNRESOLVED U-O-823 |
| 9.x search + 15-table | 9.1–9.3 + 6-team table | pair_9x | corpus olympiad_9x_table | VERIFIED_BY_OFFICIAL_EXAMPLE | table order pinned |
| 9.2/9.4/9.5 | 9.2/9.4/9.5 (evidence) | scrutiny direction; complete = maximal | suite | VERIFIED_BY_DERIVED_CASE | |
| 10/11 management | 10–11.3 | OUT | — | OUT_OF_SCOPE_WITH_REASON | presence/publication are management |

## Berger (C.05 Annex 1)

| Rule | FIDE source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| even tables 4–12 | Handbook rows (retrieved note) | roundrobin._berger_single | test_roundrobin exact | VERIFIED_BY_OFFICIAL_EXAMPLE | |
| odd fields/bye rotation | "highest number bye" | ghost slot | properties | VERIFIED_BY_DERIVED_CASE | |
| double cycle + reversal | FIDE recommendation | double= + reverse_last_two | suite | VERIFIED_BY_DERIVED_CASE | reversal default-off (recommendation ≠ rule) |

> Berger overall: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (even 4–12 rows
> Handbook-exact; odd-field tables + double-cycle colour nuances rest on
> construction + properties, not row-by-row Handbook pins).

## Frozen legacy (v0.1/v0.2)

| Rule | Source | Code | Test | Status | Notes |
|---|---|---|---|---|---|
| SwissEngine/PlayerData/EngineRequest/pair_round/dutch-till2026-compat | v0.1/v0.2 goldens | untouched kernel | test_v010_behavioral + conformance json + BBP oracle (12 pass) | VERIFIED | byte-identical outputs; no 2026 concept leaks |

## Interpretation register (carry to final report)

- I-D-PAB: Dutch PAB post-(score,unplayed) largest-TPN (C.04.3 silent).
- I-D-MDPVALID: Dutch MDP-set C7+C4 validity pre-filter ≈ global-min selection.
- I-T-C7: Double/Team "first complies" = min-vector + generation tiebreak (coincides iff zero exists; graceful else).
- I-T-MATCH: match↔game decomposition + PAB valuation caller-side.
- I-T-C1FB: forfeit-both repeat exception unrepresentable in model.
- I-T-C3: Double/Team completion = next-bracket probe (not full lookahead).
- I-L-334: Lim 3.3/3.4 other-floaters'-opponents exclusion approximated.
- I-L-38: Lim 3.8 "alternate colour" = opposite of floater's due.
- I-L-412: Lim upward search = exact mirror of 4.2 columns.
- I-L-44: Lim 4.4 culprit = lowest-TPN unpaired ("#2"-analogue).
- I-L-55: Lim 5.5/5.6 round parity via CD-balance heuristic.
- I-O-RANK: Olympiad initial seeding caller-side (TPN = initial number).
- U-O-823: Olympiad 8.x.3 played-all preference unresolved (no PDF).
- U-O-88: Olympiad 88-team example not re-executed (no PDF).

## Closure resolutions (2026-10-03; §13 final statuses)

Previous INTERPRETATION → final resolution. Statuses: VERIFIED |
VERIFIED_OFFICIAL_EXAMPLE | DERIVED | EXPLICIT_ALTERNATIVE |
GENUINE_AMBIGUITY | EVIDENCE_GAP. No item remains bare INTERPRETATION.

| ID | Previous | Final | Evidence / derivation | Test |
|---|---|---|---|---|
| I-D-PAB | INTERPRETATION (largest-TPN) | VERIFIED | RESOLVED_BY_FIDE_TEXT: C.04.3 has no PAB-assignment step; Mastering worked example (15-6 + PAB #13) follows 4.4.2/4.2 generation + 3.8.1, matching the unified last-bracket evaluation. Invented enumeration + tiebreak removed. | H-PAB-emergence + H-PAB-global-best (old code picks taker id3; new id5) |
| B-C12 (new) | — (undetected miscount) | VERIFIED | White-holder map inverted for Black recipients (found via hand-trace of unified PAB vectors). Fixed to white-holder id. | H-PAB-global-best vectors |
| I-D-MDPVALID | INTERPRETATION | DERIVED | RESOLVED_BY_OFFICIAL_TECHNICAL_GUIDANCE: annotated 4.4.1/4.4.2 admits all sizes as valid + larger-first ordering ⇒ validity filter vacuous over constructible sets ⇒ global-min selection faithful. RSL is a facilitator, not normative (G3 merged here). | H-MDP + annotated triple order |
| I-T-C7 | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: Art.2.3 "comply as much as possible" makes C6/C7/C8/C10 optimisation criteria; "first" (3.5.5/3.6.4) is the generation-order tiebreak. Strict zero-filter rejected: it would fail ordinary rounds (Team C10 repeats are routine), contradicting Art.2.3. No strategy parameter (single adopted reading). | H-graceful (min succeeds where filter would raise) |
| I-T-MATCH | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: Preface (2-game matches, per-game points) + 1.4 (PAB value) + 1.6 (first-game colour) place game accounting caller-side; pairing uses match score/colours only. Contract: RESULT_CONTRACTS.md. No new input type. | properties (match-score pairing) |
| I-T-C1FB | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: Preface ("same pairing may be repeated" after forfeit-ended match) + C.04.2 Art.3.5 played-only opponents ⇒ forfeit-both matches excluded from `opponents` structurally; single-forfeits stay listed. Contract + rematch docstring. | H-forfeit-both (excluded re-pairs; listed bars) |
| I-T-C3 | INTERPRETATION | DERIVED | Next-bracket probe retained as the feasible operationalization (Double 2.3.3/Team 2.3.3 explicitly scope C6 to the mentioned scoregroup); full recursive lookahead intractable — permanent limitation L (not FIDE ambiguity). | properties (105 states × 7 rulesets, no stranding) |
| I-L-334 | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: 3.3/3.4 exclusion operationalized as claimed-partner sets per destination (3.2 due-class → 3.9 type → exclusion → 3.2.4 number). | H-33-exclusion (old took TPN1; new TPN2) |
| I-L-38 | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: "is paired with" (3.8) is mandatory (reading (a): partner due the opposite colour); global failure routes to 4.4, not to alternatives. | H-38-force (old succeeds alternatively; new None→4.4) |
| I-L-412 | INTERPRETATION | GENUINE_AMBIGUITY | 4.1.2 fixes scrutiny start (lowest = highest TPN, consistent with 4.2's "#1 = highest") but no upward column table exists; mirror adopted by symmetry. Effect confined to below-median incompatibility repairs; deterministic default, no caller flag. | H-scrutiny (direction pinned; mirror documented) |
| I-L-44 | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: culprit mirrors sequential scrutiny (column-order greedy; first stuck player — matches the worked #2); companion stays literal lowest-numbered (4.4.2). | H-44-culprit (upward: 4 not 1; downward: 2) |
| I-L-55 | INTERPRETATION | VERIFIED | RESOLVED_BY_FIDE_TEXT: residual colours chosen by round parity (5.5 both ≤1; 5.6 both =0) over ban-free options, minmax then designate-alternation tiebreaks; 5.4 even-round equalising clause implemented. | H-55-even (old alternated; new equalises) |
| I-O-RANK | INTERPRETATION | VERIFIED | Helper `seed_initial_numbers` implements 3.1 exactly (avg-top-4 → 5th → alpha → id); TPN assignment stays caller-side. Evidence upgraded: Handbook chapter text retrieved (archive). | H-seeding-331 |
| G1 U-O-823 | EVIDENCE_GAP | VERIFIED | Chapter retrieved: 8.x.3 IS the moved-back/next-candidate chain (implemented); 8.2.4 skip-loop; 8.4 re-floater. | H-odd + properties |
| G2 U-O-88 | EVIDENCE_GAP | VERIFIED_OFFICIAL_EXAMPLE | 88-team median example re-executed in miniature (#45 lower-middle → 10pt group). | H-88-team |
| G3 RSL | EVIDENCE_GAP | DERIVED | Merged into I-D-MDPVALID (no normative RSL rule in C.04.3). | — |
| G4 full-C3 | EVIDENCE_GAP | DERIVED | Retained approximation as derived execution policy (§6 ceilings); limitation L. | — |
| B-O (new) | — | VERIFIED | Retrieved chapter forced fixes: 4.1 bye = lowest rank (was lowest number); 7.2 R1 lot pattern; 9.4 played-all floats; 8.2.1/8.3.1 designated partners; 9.3 subgroup-relative search; 11.1 rating-key order. | H-bye-rank, H-R1 (probes), H-94 (probe), corpus 15-table |
| Ceilings | owner decision | VERIFIED (policy) | Derived execution policy: SEARCH_CEILING_POLICY.md (ticks + count guards + every-tick wall + entry cancel check + no partials). Deterministic cutoff pinned. | H-cutoff, H-cancel, benchmarks |
| cancel_token | — (unwired) | VERIFIED (new API) | P26Request.cancel_token (optional, additive) threaded to all six Steppers + dispatcher entry check. | H-cancel |

Olympiad evidence basis upgraded from record-only to retrieved Handbook
chapter text (archive URL + SHAs in SOURCE_MANIFEST.md); F-0601 PDF itself
remains unobtained (direct PDF attempts logged) but the chapter HTML is the
complete normative text (§§1–11 + tables + examples present).
