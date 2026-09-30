# Pairing Engine Audit — pairing-core v0.1.0 (STAGE 1)

Scope: `engine.py` (orchestration), `pairer.py` (search), `bracket.py`,
`color.py`, `floats.py`, `exchange.py`, `bye.py`, `api.py`. All section
verdicts are code-evidence verdicts, not compliance certificates.

## 1. What is implemented — VERIFIED

A **score-bracket Dutch-system search** with this pipeline
(`SwissEngine.generate`, `engine.py:69-112`):

```
normalize input (_normalize_input, legacy-tolerant)
  → make_engine_players (sort by -points, pno, id)
  → validate locked_pairs → PairingCards (board assigned later)
  → pairable subset:
      0 players → return locked only
      1 player  → bye card
      even      → build_brackets → pair_all_brackets
      odd       → try bye candidates in order; first candidate whose
                  remainder pairs successfully wins (bye card appended last)
  → board numbers: normal cards in order, bye last (_assign_board_numbers)
```

`pair_all_brackets` (`pairer.py:48-80`) runs **two passes**: strict floats,
then relaxed floats; absolute constraints never relaxed. Recursion
(`_solve_bracket`, `pairer.py:169-228`) processes brackets top→bottom with
cross-bracket backtracking over downfloater choices; within a bracket,
`_iter_bracket_pairings` yields transpositions of the original S2 first, then
systematic S1↔S2 exchanges (`exchange.py`) each with all S2 transpositions.
Pair legality = no-rematch AND color-legal AND float-legal AND legal color
orientation (`_build_pair_if_legal`, `pairer.py:566-591`). Transposition DFS
(`pairer.py:377-474`) uses exact bipartite perfect-matching pruning
(`_perfect_completion_possible`, `pairer.py:477-563`) plus global/local
dead-end caches and a 2,000,000-step cap (`_PairingContext`, `pairer.py:87-124`).

## 2. FIDE ruleset correspondence — assessment (NOT a compliance claim)

- Claimed reference: "FIDE C.04.2 + C.04.3 (effective 1 July 2025)"
  (`README.md:8`, `__init__.py:31`, `engine.py:1-3`). The date/version string
  is a **claim in text**, VERIFIED present but **UNVERIFIED against the actual
  FIDE handbook** (no handbook copy in repo, no rule-by-rule traceability
  matrix, no external reference tests).
- Explicitly implemented with code evidence: score brackets desc; pno-ordered
  S1/S2 split; heterogeneous-bracket floaters-first ordering (`bracket.py:95-104`);
  transposition-then-exchange search order; absolute color bars (3× repeat,
  balance ±2); strong/mild color priority chain; bye bottom-up fresh-first;
  downfloat ranking (resident > non-recent > fewer-consecutive > lowest-ranked);
  3-consecutive float absolute bar with strict/relaxed two-pass.
- Inferred (structure suggests FIDE intent, no citation in code): the exact
  exchange enumeration order (`exchange.py:13-27` says "FIDE convention" without
  a handbook article number); mild-preference handling as INFO-only.
- Missing/simplified/suspect — see §§4–5 and CURRENT_LIMITATIONS.md. In
  particular this audit does **NOT** certify FIDE compliance; the engine is
  "Dutch-family" by construction, "FIDE-compliant" only where individually
  evidenced. Verdict on the name `NativeDutchEngine`: the name asserts
  lineage, not verified compliance — PARTIALLY VERIFIED (algorithm family),
  compliance UNVERIFIED.

## 3. Determinism / randomness / seeds — VERIFIED

- No `random`, `shuffle`, `seed`, `os.urandom`, time, thread, or iteration over
  unordered sets anywhere in `src/pairing_core/*.py` (grep VERIFIED; only hit
  is the word "randomness" in a `pairer.py` docstring).
- All orderings derive from sorted keys (`sort_key`, pno, id, points, float
  counters). Dict iteration is insertion-ordered and deterministic for a given
  input. `EnginePlayer.sort_key` makes input-list order irrelevant to ranking.
- Tests confirm: `test_repeat_and_reorder` pairs twice + reversed input and
  expects identical pair sets (passes — 15/15 suite green at audit time).
- Seeded randomness: NOT IMPLEMENTED (no seed parameter exists anywhere).
- Tie-breaking: fully deterministic (pno, then id). VERIFIED.
- Caveat: determinism of *pair sets* is tested; determinism of *color
  orientation* under input reorder is NOT asserted by tests (only pair sets
  compared). Minor gap, see TESTING_CURRENT_STATE.md.

## 4. What is explicitly implemented vs missing/simplified

| Area | Implemented (evidence) | Missing / simplified / suspect |
|---|---|---|
| Brackets | exact-score groups, desc, pno-sorted; floaters-first merge | no accelerated/round-1 special seeding beyond S1/S2; rating unused |
| S1/S2 | half-split, remainder-exclusion (`bracket.py:134-209`) | — |
| Transpositions | lazy lexicographic DFS, exact pruning | bitmask `1 << j` caps S2 width at word size in practice (see §6) |
| Exchanges | single→double→…→k, lowest-S1 × highest-S2 first | combinatorial blowup; only step-cap as guard |
| Colors | 4-priority chain + absolute legality gate | Priority-1 docstring wording imprecise ("3 consecutive" vs 2-history trigger); conflict both-absolute resolved by rank (code choice, uncited) |
| Floats | 3-level model, strict→relaxed passes, absolute never relaxed | `is_upfloater` confirmed permanently `False` (dead flag, harmless: upfloat enforcement via opponent-down inference `floats.py:240-241` covers all in-bracket upfloats — VERIFIED Stage 1.6); inference-vs-FIDE fidelity UNVERIFIED |
| Rematch | bidirectional, both maps | no forbidden-pair API beyond played set + locked pairs |
| Bye | bottom-up, fresh-first, repeat-if-all-used | bye candidate loop tries candidates in order and takes first pairable remainder (greedy over bye choice, not globally optimal — VERIFIED `engine.py:267-297`) |
| Last-bracket-odd | `_try_last_bracket_odd` returns None → forces backtrack | Deliberate incompleteness: odd tail only solvable via upstream float adjustment; total-odd handled by bye layer, but mid-search odd tails can only resolve by backtracking (VERIFIED `pairer.py:313-328`) |
| Locked pairs | validated preassignments, color-gated | locked cards get NO float tags; locked players excluded from float/color global optimisation |
| Failure mode | `ValueError` with bracket summary; step-cap `ValueError` | no structured error taxonomy (see ARCHITECTURE_AUDIT.md) |

## 5. Potentially incorrect / risky spots (flagged, not fixed — Stage 1 only)

1. `_search_bracket_configurations` (`pairer.py:231-285`) takes only the
   **first** local pairing (`first_local = next(iter, None)`) before recursing
   downstream; if downstream fails it does NOT try the next local pairing of
   the same bracket — it moves to carrying another player down. The module
   docstring (§1: "does not stop at the first locally valid pairing… backtracks
   over all local pairings") **contradicts the code**, which advances the
   generator only once per configuration — VERIFIED contradiction in wording.
   **Completeness verdict: FALSE POSITIVE as a completeness bug** (Stage 1.6
   deep probe, 2026-09-30): downstream feasibility depends only on the
   downfloater *set* (`_recurse_with_downfloaters` forwards players, not pairs;
   no pairing step mutates shared player state; the dead-end cache key
   `(bracket_idx, incoming_ids, strict)` captures exactly this), so any legal
   local pairing of the same configuration shares the same downstream — the
   first-legal shortcut cannot miss a solution, and all downfloater subsets are
   explored via the Option-3 recursion (each loop level branches over every
   remaining candidate). Corroboration: a read-only differential probe
   (`/tmp/stage16_diff.py`, NOT in repo: 4000 randomized 4–8 player tournaments
   vs an independent exhaustive absolute-legality checker reusing the engine's
   own predicates) found **0 cases** of engine-failure-with-solution-present.
   What REMAINS open is (a) the docstring overclaim (says exhaustive local
   backtracking; code does first-wins) and (b) whether first-wins-in-search-order
   matches FIDE's choice among multiple legal pairings — UNVERIFIED, Stage 2
   FIDE comparison. The last bracket
   (`pairer.py:209-211`) does return the first pairing directly, which is
   correct for a terminal bracket.
2. `_ordered_bye_candidates` (`bye.py:137-152`) sorts by
   `(points, -pno, id)` — ascending `-pno` puts the *highest* pno first, matching
   the documented "lowest-ranked first". VERIFIED consistent (audit probe: 3-player
   same-score field gave the bye to pno 3). No issue; recorded because the
   double negation is easy to misread.
3. Non-English comment at `pairer.py:244` (Persian). Harmless functionally;
   hygiene finding (see CURRENT_LIMITATIONS.md §A).
4. `float_pair_legal` upfloat inference (`floats.py:240-241`): any player paired
   against a downfloater is treated as an upfloater and subjected to
   `can_upfloat` — including strict-pass rejection for `last_was_up`. This is
   stricter than the "incoming re-float" soft concept; whether it matches FIDE
   is UNVERIFIED.

## 6. Complexity / performance characteristics (theoretical — NOT measured)

- Bracket build/sort: O(n log n). Color/float derivation: O(history length).
- Transposition DFS per bracket: worst-case O((n/2)!) leaf paths before pruning;
  perfect-matching pruning + caches cut dead branches exactly (no order change).
- Exchanges: Σ_k C(n/2,k)² patterns (docstring's own n=m=10 estimate ≈ 16.5k
  patterns, each × transpositions). Only the 2M-step cap bounds this.
- Bitmask limit: `legal_masks`/`used_mask` use `1 << j` Python ints (unbounded,
  so no overflow) but DFS state space is exponential regardless; realistic
  brackets (≤ ~30 players per score group) are fine; a single 100+-player
  bracket with dense legality would hit the step cap → `ValueError`.
- Scale estimates (theoretical, clearly labeled): 10 players trivial (<ms);
  50–100 typical Swiss spread → small brackets, fast; 250–500 → still small
  brackets normally, but pathological single-score-group late-tournament states
  could explode; 1000 → same bracket-size argument, engine has no chunking or
  parallelism. No benchmarks exist (NOT IMPLEMENTED). See OPEN_QUESTIONS.md Q9.

## 7. Algorithm trace (input → output with file/function map)

1. Input normalization — `engine.py:314-364` (`_normalize_input`): legacy-tolerant,
   silent `status` filter; O(n).
2. Ranking — `models.py:451-458` (`make_engine_players`): sort by
   (-points, pno, id); rating ignored.
3. played_map — `engine.py:369-376`: dict of opponent sets.
4. Locked pairs — `engine.py:117-191`: 6 checks, `ValueError`s; color gate via
   `color.is_legal_orientation`.
5. Bye handling — `engine.py:196-309` + `bye.py`: even → direct; odd → ordered
   candidates, first-successful-wins; single-player → bye.
6. Score grouping — `bracket.py:314-357` (`build_brackets`): exact float equality.
7. Bracket recursion — `pairer.py:169-228` with downfloater accumulation
   (`_search_bracket_configurations`, `_recurse_with_downfloaters`).
8. Candidate generation — transpositions (`pairer.py:377-474`) then exchanges
   (`exchange.py:71-107`).
9. Color allocation — `color.py:40-132` (`assign_colors`), gated by
   `is_legal_orientation` (`color.py:135-174`).
10. Float handling — `floats.py` gates inside `_build_pair_if_legal`.
11. Rematch gate — `have_played` both-directions check.
12. Optimization/search — first-legal-in-FIDE-order wins (satisficing, not
    optimizing); strict pass then relaxed pass.
13. Fallback — none that relaxes absolute rules; terminal failure = `ValueError`
    (even) or bye-exhausted `ValueError` (odd). No heuristic fallback (claimed
    and VERIFIED absent).
14. Validation — none post-generation inside engine (validator is separate,
    caller-invoked).
15. Output — `_to_pairing_cards` + `_assign_board_numbers` (normal first, bye last).
16. Error handling — `ValueError` only (see ARCHITECTURE_AUDIT.md §6).
