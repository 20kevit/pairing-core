# FIDE Conformance Final Report (hostile audit wave, 2026-10-03)

## 1. Baseline

- Commit `b418bbe` (`main`, clean tree), package `0.3.0`, previous release `v0.3.0`.
- Suite: **310 passed / 10 skipped**; source validator green; wheel/sdist build
  green; determinism suite green (4).
- Full details: `docs/audit/FIDE_CONFORMANCE_AUDIT_BASELINE.md` (recorded
  before any code change).

## 2. Audit scope

All 10 implemented systems, rule-by-rule against CM3-202517 FULL_TEXT
(Dutch C.04.3, Dubov C.04.4.1, Burstein C.04.4.2, Lim C.04.4.3, Double C.04.5,
Team C.04.6, Baku C.04.7 — 1871 lines re-read) + Annotated Dutch V2026
(4.4.1/4.4.2 validity + ordering) + Mastering/Terms Dutch + prior evidence
records. Olympiad F-0601 primary PDF unobtainable this wave (handbook
bot-wall); audited against the 2026-10-03 FULL_TEXT evidence record instead.
Berger audited against C.05 Annex 1 construction + pinned tables. Legacy
`dutch-till2026-compat` audited for behavioral invariance only (never "fixed").

## 3. Systems audited

Dutch 2026, Dubov 2026, Burstein 2026, Lim 2026, Double Swiss 2026,
Team Swiss 2026, Baku/Accelerated, Olympiad 2022, Berger, frozen legacy Dutch.

## 4. Rules audited

Complete article-level pass; the rule→code→test chain for every material rule
is tabulated in `docs/audit/FIDE_CONFORMANCE_MATRIX.md` (~150 rows).

## 5. Bugs found (every one fixed, regression-pinned, old behavior verified)

| ID | Source article | Incorrect behavior | Exact cause | Fix | Regression test |
|---|---|---|---|---|---|
| B1 | Dutch 4.1.1 | BSN 1 = weakest (hetero brackets misordered) | `_bsn` sorted score-ascending | 1.2 order (-score, tpn) | H-BSN |
| B2 | Dutch 4.4.2 | MDP sets complement-lex ({3,4} first) | ordering on Limbo, not kept sets | kept-lex + larger-first | H-MDP |
| B3 | Dutch 3.x | M1/mdps in raw TPN order | `sorted(key=tpn)` | 1.2 order | (covered by H hetero golden) |
| B4 | Burstein 2.3.2 | C6 maximised outgoing (strongest floats) | negated comparison key | unnegated min | H-C6 |
| B5 | Burstein 2.3.3 | C7 probe ignored outgoing floaters | scope = rest_after only | determined next-bracket scope | H-C7 |
| B-loop | Burstein 1.2.2 | incoming floaters dropped; rounds stranded | join-filter vs consumed `remaining` | score-ordered loop, persistent incoming | H-loop |
| B6 | Burstein Art.4 | duplicate pairings (identical zeroes); no 0-0 skip | missing dedup in rec() | per-level value dedup + prune | H-table (count 45) |
| B7 | Dubov 3.2.3 | TPN-half G1 for all-seeker brackets | wrong condition | all-unplayed-only condition | H-G1 (+ impossibility guard test) |
| B8 | Dubov 3.2.4.1 | phase-1 shift never fired (dead code) | greedy probe needs equal sizes | search over 4.3 sets w/ actual-pairing C7 | H-phase1 |
| B9 | Dubov 3.2.2 | C7 on greedy estimate; C1-only viability | best-effort pairing | real S1×T2 scoring; C1+C3 legality | H-C7 |
| B10 | Double/Team 3.5.2 | (clarified) C5-best profile w/o legal pairing now raises (3.3.3) instead of silent fallback | profile loop fell through | constructional profile + typed error | H-C5 ×2 |
| B-ids | Double/Team 3.6 | id/TPN space confusion (KeyError/mis-pair) | rec carried ids, caller read TPNs | TPN identifiers end-to-end | H-idspace |
| B11 | Team 4.3.7 | step missing (wrong colour on walkback ties) | chain skipped 4.3.7 | grant first-team pref after walkback | H-437 |
| B12 | Team 4.2.2 | secondary dropped for kind 'none' | kind↔secondary coupling | always rank secondary (caller passes 0) | H-kindnone |
| B13 | Olympiad 8.x | NameError + vanishing floaters on odd groups | undefined vars; no queue routing | processing-order queues | H-odd |
| B14 | Lim 4.1.1 | scrutiny highest-TPN-first downward | phrase misread vs 4.2 table | #1-first; upward mirrored | H-scrutiny |
| B15 | Lim 4.2 | same-half opponents ascending | list order | descending (table columns) | H-columns |
| B16 | Lim 3.2.2 | even-maker from minority due side | inverted majority test | majority + 3.2.4 tiebreak | H-even |
| B17 | Lim 4.4 | extra due-colour float + retry | wrong recovery | 4.4.1 swap / 4.4.2 culprit+lowest | H-44 |
| B18 | Lim 2.6 | median self-priority instead of adjacent cracking | wrong mechanism | crack adjacent by floater counts | H-26 |
| B19 | Lim 3.3–3.9 | 3.9 absent ("folded" claim false); no 3.6/3.7/3.8/3.5 | missing | explicit 3.9/3.6/3.7/3.8/3.5 | H-priority, H-even |
| B-L54 | Lim 5.4 | identical-histories always higher-ranked | missing side rule | below-median → lower-ranked | H-54 |
| B-L6 | Lim Art.6 | colour bans enforced in last round | no relaxation | compatible(last_round) lift | H-Art6 |
| B-WB | all walkbacks | played-sequence zip misaligns across 'u' | index vs round confusion | round-aligned last_differing_round | H-walkback |
| B-perf | budgets | R1-20 Dutch 7s (upfront exchange sort); big brackets hang unticked | eager materialization; unticked loops | deferred alterations; ticks + count guards; exact lex-first fast paths (Double/Burstein); every-tick wall checks | benchmarks_2026 |

Old behavior for the discriminating cases was verified by executing the same
probes against stashed pre-fix code (NameError / ImpossiblePairingError /
KeyError / wrong outputs — recorded in wave notes).

## 6. Official examples

Re-executed, all pass: Dutch 11-player/2-MDP transposition counts (720/72);
Art.4.3 comparison patterns (6↔4 > 8↔5; 5 > 4; 6 > 7); annotated MDP order
{1,3} < {1,4} < {3,4}; Dubov A–G middle-outward (D,C,E,…) + ABC transposition
order; Burstein 6-player table head (1-6,2-5,3-0,4-0); Double sets
{2,6,1} < {2,6,3} < … + identifier `4 6 9 11 8 16 10 24`; Lim R1 40-player
tables (lot W/B mirror) + 4.2 exchange columns (1v4,1v5,1v6,1v3,1v2); Olympiad
6-team 15-combination table (corpus); Baku 161→82, 9R 1.0×3+0.5×2, 11R team
2×3+1×3; Berger even 4–12 rows. NOT re-executed (source unavailable):
Olympiad 88-team example (U-O-88).

## 7. Differential results

| Pair | Versions | Result |
|---|---|---|
| BBP vs `dutch-till2026-compat` R1 + validator | BBP 2025-era vs legacy | agree (12 pass) — same-era, meaningful |
| JaVaFo vs legacy | legacy scope | pass/skip (env-gated) |
| BBP-Dutch-2025 vs `dutch-2026` | cross-version | NOT compared (meaningless per §18) |
| BBP-Burstein (known-flawed, per its README) vs `burstein-2026` | cross-version + flawed | NOT compared |
| Dubov/Lim/Double/Team/Olympiad/Baku 2026 vs externals | — | no external 2026 implementations exist → N/A |

No difference was called a bug without an applicable FIDE rule; the only
same-era differentials pass.

## 8. Remaining interpretations

I-D-PAB, I-D-MDPVALID, I-T-C7, I-T-MATCH, I-T-C1FB, I-T-C3, I-L-334, I-L-38,
I-L-412, I-L-44, I-L-55, I-O-RANK — each defined in the matrix §Interpretation
register with the exact FIDE silence + adopted reading + divergence case.
None is eliminable from the official text as retrieved.

## 9. Remaining evidence gaps

- U-O-823 (Olympiad 8.x.3 played-all preference), U-O-88 (88-team example):
  blocked on F-0601 primary PDF (handbook bot-wall; queued manual retrieval).
- Dutch RSL pre-sizing for MDP validity (approximation documented).
- Double/Team full-completion (C3) lookahead beyond next bracket.
- Lim 4.3 #2-row interleaving exactness (approximation documented).

## 10. Performance (Gate G — measured, budgets derived)

`tests/test_benchmarks_2026.py` + `tests/data/benchmarks/benchmarks_2026.json`
(machine timings recorded; outcomes are the gates):

- R1 fresh 20/50, ALL systems: ≤ 0.01s — succeed (Dutch R1-50 fixed 7s→0.003s
  by deferred alterations; Double R1-50 by lex-first fast path).
- Mid-tournament n=20, ALL systems: succeed (Dutch 0.16s worst).
- Fragmented n=50, ALL systems: succeed (Dutch 3.5s worst).
- Big-bracket n=50 (two ~25-groups): Double succeeds (0.004s, fast path);
  Dutch → EngineTimeoutError at wall (45s); Burstein → EngineTimeoutError via
  count guard (0.001s). Both TYPED, never hang.
- Pathological (dense rematch): typed timeout-bounded (1.3s).
- Derived budgets: default 2M steps + caller wall-clock carry realistic play
  through ~30-player dense brackets; full-field 50+ exact Dutch/Burstein
  search is factorial and intentionally bounded by typed budgets, not by
  heuristic pruning (conformance risk — owner decision §16).

## 11. Determinism (Gate D)

Hash-seed sweeps (0/1/42/123456) green; fresh-process determinism pinned by
property tests (pair twice → byte-identical dicts); canonical JSON
round-trips; no set/dict-order dependence in any pairing decision
(audit grep + `lexicographic_sets`/`sorted` discipline; dedup sets are
membership-only).

## 12. Security (Gate H)

2026 engines are pure (no I/O, subprocess, temp files, pickle, eval).
External engines exist only in env-gated tests (no shell=True).
TRF parsing rejects malformed input (suite); core never imports adapters
(pinned). Fuzzing via 2026 property suite (105+ states/ruleset incl.
malformed-adjacent histories) yields only typed errors or valid outputs.
No regressions.

## 13. API compatibility (Gates C/I)

Top-level `__all__` unchanged (legacy names intact); 2026 namespace isolated
(`pairing_core.fide2026`, own `__all__`, no internal helpers exported);
exact-match resolution (no fallback/drift); v0.1/v0.2 goldens byte-identical
(41/41 + conformance json); fresh-process imports green.

## 14. Final conformance status by system

- Dutch 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (I-D-PAB, I-D-MDPVALID)
- Dubov 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (none structural; C7
  scoring now exact — gaps: none beyond routine derived-case coverage)
- Burstein 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (caller round_results
  contract by design)
- Lim 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (I-L-334/38/412/44/55)
- Double Swiss 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (I-T-C7/MATCH/C1FB/C3)
- Team Swiss 2026: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (same + colour types)
- Baku / Accelerated: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (1.3 boundary
  caller-side; list management out)
- Olympiad 2022: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (I-O-RANK, U-O-823, U-O-88)
- Berger: IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS (even 4–12 Handbook-exact;
  odd/double-cycle structural only)
- Frozen legacy Dutch: behaviorally invariant (not a FIDE claim; compatibility VERIFIED)

No system is marked RESEARCH_COMPLETE_IMPLEMENTATION_PENDING or
PARTIALLY_SPECIFIED: all retrieved rules are implemented; what remains is
interpretation-resolution (later FIDE clarifications) and the Olympiad PDF.

## 15. Release decision

PATCH release **0.3.1**: the 2026 engines (new in 0.3.0, hours old) had 20
conformance defects changing pairing outputs; all fixed with regression pins;
public API unchanged (additive tests only); legacy behavior byte-identical.
Gates A–J all green (see §§6–13 + matrix). No "FIDE compliant/endorsed" claim
is made: conformance = rule-level evidence in the matrix, with explicit
interpretations where FIDE is silent.

## 16. Remaining owner decisions

1. Exact-search ceilings (§10): accept typed timeouts beyond ~30-player dense
   brackets, or fund bounded pruning heuristics (conformance risk).
2. I-T-C7 strict-filter alternative (fail ordinary forced-repeat rounds) —
   rejected by this wave (fragility); revisit only on FIDE clarification.
3. Olympic F-0601 manual PDF retrieval (U-O-823, U-O-88).
4. Double C3 full-completion lookahead + forfeit-both model extension
   (needs new input fields = public API addition → minor release).
