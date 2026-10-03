# FIDE Conformance Closure Report (closure wave, 2026-10-03)

## A. Starting state

- Commit `973d5d2` (`main`, clean), version `0.3.1`; baseline recorded in
  `FIDE_CLOSURE_BASELINE.md` before any change: 477 passed / 16 skipped,
  validator green, build green, determinism green.
- 12 interpretations + 4 evidence gaps + 4 owner decisions enumerated in
  `FIDE_REMAINING_ITEMS.md` (no miscellaneous category).

## B. All 12 interpretations

| ID | Original issue | Evidence | Final resolution | Implementation | Test |
|---|---|---|---|---|---|
| I-D-PAB | PAB tiebreak past (score, unplayed) | C.04.3 C5/C9 + 3.8.1 + Mastering 15-6/PAB-#13 example | RESOLVED_BY_FIDE_TEXT: no assignment step exists; assignee emerges from generation order. Invented enumeration + largest-TPN removed. | unified last-bracket evaluation | H-PAB ×2 (old/new diverge) |
| I-D-MDPVALID | MDP validity pre-filter vs global-min | Annotated 4.4.1/4.4.2 + worked {1,3}<{1,4}<{3,4} | RESOLVED_BY_OFFICIAL_TECHNICAL_GUIDANCE: validity vacuous over constructible sets ⇒ global-min faithful (matrix DERIVED) | unchanged (documented) | H-MDP |
| I-T-C7 | "first complies" vs min-vector | Art.2.3 "as much as possible" + Team-C10 routine-repeat absurdity | RESOLVED_BY_FIDE_TEXT: min + generation tiebreak; no strategy parameter | unchanged (docstring derivation added) | H-graceful |
| I-T-MATCH | match↔game placement | Preface + 1.4 + 1.6 | RESOLVED_BY_FIDE_TEXT: caller contract, no new input type | RESULT_CONTRACTS.md | properties |
| I-T-C1FB | forfeit-both repeat | Preface + C.04.2 Art.3.5 | RESOLVED_BY_FIDE_TEXT: exclusion convention, no flag | rematch docstring | H-forfeit-both |
| I-T-C3 | completion scope | 2.2.1/3.1.2 + 2.3.3 scope note | DERIVED policy (next-bracket probe; limitation L) | unchanged (documented) | properties |
| I-L-334 | 3.3/3.4 exclusion exactness | 3.3/3.4 + 3.9 + 3.2 order | RESOLVED_BY_FIDE_TEXT: claimed-partner operationalization | exclusion tier in selection | H-33 (old/new diverge) |
| I-L-38 | 3.8 "alternate colour" + force | 3.8 + due-colour def | RESOLVED_BY_FIDE_TEXT: opposite-due partner, mandatory | forced single-option | H-38 (old/new diverge) |
| I-L-412 | upward search shape | 4.1.2 + 4.2 table (downward only) | GENUINE_AMBIGUITY: mirror by symmetry, deterministic default, no flag | documented | H-scrutiny |
| I-L-44 | 4.4 culprit identity | 4.4–4.4.2 + worked #2 | RESOLVED_BY_FIDE_TEXT: sequential-scrutiny mirror + literal companion | _culprit | H-44 (old/new diverge) |
| I-L-55 | 5.5/5.6 round parity | 5.1–5.6 + Art.6 | RESOLVED_BY_FIDE_TEXT: parity-explicit tail + 5.4 even clause | _lim_colour rewrite | H-55 (old/new diverge) |
| I-O-RANK | seeding placement | F-0601 3.1 (chapter retrieved) | RESOLVED_BY_FIDE_TEXT: helper + caller contract | seed_initial_numbers | H-331 |

No item remains bare INTERPRETATION.

## C. All 4 evidence gaps

- G1 (U-O-823): CLOSED — Handbook chapter retrieved (archive URL + SHAs in
  SOURCE_MANIFEST.md); 8.x.3 is the moved-back/next-candidate chain
  (implemented); 8.2.4 skip-loop + 8.4 re-floater implemented.
- G2 (U-O-88): CLOSED — 88-team median example present in retrieved text and
  re-executed in miniature (H-88-team).
- G3 (RSL): CLOSED as DERIVED (merged into I-D-MDPVALID; no normative rule).
- G4 (full-C3): retained approximation as derived execution policy
  (limitation L, not missing evidence).
- Retrieval attempts logged: live handbook (bot-wall), doc.fide Annex (404),
  Olympiad2026MainCompetition.pdf (inaccessible), archive-2024 (empty),
  archive-2023 chapter HTML (SUCCESS, complete §§1–11). F-0601 PDF per se
  unobtained; nothing verder vendored (metadata only).

## D. Four owner decisions

1. **Exact-search ceilings** — DERIVED (no owner choice needed):
   `SEARCH_CEILING_POLICY.md`. Steps = ticks; ceilings raise typed errors
   (never partials); step budgets deterministic, wall-clock secondary,
   cancellation immediate; budgets caller-scaled with measured guidance.
2. **I-T-C7 alternative** — RESOLVED, not a choice: single FIDE-mandated
   reading adopted (see B); no strategy parameter (documented why).
3. **Olympiad PDF retrieval** — executed above (chapter text retrieved;
   PDF attempts exhausted and logged).
4. **Double C3 / forfeit-both** — DERIVED: forfeit convention formalized
   (no model change); C3 lookahead retained as policy (limitation L).

## E. Defects found during closure

- B-C12: Dutch C12/C13 white-holder map inverted for Black recipients
  (all colour-criterion decisions corrupt) — fixed, pinned by PAB vectors.
- B-O-BYE: Olympiad bye = lowest initial number (should be lowest 3.2 rank).
- B-O-72: Olympiad R1 colours ignored 7.2 lot pattern.
- B-O-94: Olympiad lacked 9.4 played-all floaters.
- B-O-821: Olympiad ignored 8.2.1/8.3.1 designated partners.
- B-O-93: Olympiad 9.x used global offsets, not subgroup-relative order.
- B-O-111: Olympiad publication ignored 11.1 rating key.
- B-LIM-44-test: _culprit crashed on odd work (KeyError) — fixed with
  scrutiny-order fallback (caught by property fuzzer).
- Cancellation unwired in 2026 API (Stepper supported it; nothing passed it;
  fast paths bypassed checks) — `cancel_token` added (additive) + entry check.

## F. Tests added

14 hostile-corpus additions (all discriminating old/new where applicable:
PAB emergence + global-best, 33-exclusion, 38-force, 44-culprit, 55-even,
forfeit convention, seeding helper, bye rank, 88-team, cutoff determinism,
team id-space, cancel, huge-values, duty omissions), Olympiad bye test
rewritten to 4.1, lex-first construction test. Full adversarial re-run green.

## G. Differential results

| Engine | Version | Ruleset | Applicable | Result |
|---|---|---|---|---|
| BBP | 2025-era build | dutch-till2026-compat | yes | 12 pass, agree |
| JaVaFo | distro jar | legacy scope | yes | pass/skip (env-gated) |
| BBP | 2025 Dutch | dutch-2026 | NO (version mismatch) | not compared |
| BBP | flawed previous Burstein (per its README) | burstein-2026 | NO | not compared |
| — | — | Dubov/Lim/Double/Team/Olympiad/Baku 2026 | NO (no external 2026 engine) | N/A |

No implementation changed to match an engine.

## H. Performance

benchmarks_2026 re-run green (31): R1-20/50 all ≤0.01s; mid-20 all succeed;
frag-50 all succeed; big-50: Double succeeds, Dutch/Burstein typed timeouts
(bounded); pathological typed. Deterministic cutoff re-pinned (same
input+budget → same typed error, twice).

## I. Determinism

Hash-seed sweeps (0/1/42/123456) green; pair-twice identical; canonical
round-trips; no pairing decision depends on iteration order.

## J. Compatibility

v0.1.0 goldens (41/41) + conformance json + BBP oracles green;
byte-identical legacy outputs; `__all__` stable; fresh-process imports green.
One ADDITIVE API item: `P26Request.cancel_token` (optional, default None).

## K. Security

Huge-value termination verified (typed/paired, 0.01s); duty omissions typed;
TRF malformed suite green; no subprocess/shell in library; core↔adapter
isolation pinned; property fuzzing (105+ states × 7 rulesets) clean.

## L. Remaining genuine limitations

- L1: exact-search factorial ceilings (Dutch/Burstein big brackets) — typed
  budgets, no heuristic pruning (conformance risk; future owner-funded work).
- L2: I-L-412 upward mirror (genuine ambiguity, deterministic default).
- L3: Double/Team full-C3 lookahead beyond next bracket (policy approx).
- L4: Lim 4.2 #2-row interleaving exactness (approximation documented).
- L5: F-0601 PDF per se unobtained (chapter text complete and sufficient).

## M. Final release decision

**0.4.0 (minor)**: additive `cancel_token` API per repo versioning spec
(additive = minor); conformance behavior corrections (PAB unification, C12,
Olympiad rewrite, Lim refinements); ruleset identities unchanged (same FIDE
effective dates); no deprecations, no breaks, legacy byte-identical. Gates
A–J green. No FIDE endorsement claimed; no blanket conformance claimed
(I-L-412 ambiguity + L1/L3/L4 limitations stand disclosed).
