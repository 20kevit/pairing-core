# Dutch Conformance Status (W6 analysis + live-BBP evidence)

Method: re-retrieval attempted 2026-10-01 (handbook fetch: timed out again;
targeted search: no article text). LIVE evidence added 2026-10-02: BBP built
from source (commit 8f9e3c5, 2026-07-30, g++ O3, non-release build; Apache-2.0,
/tmp-only, never vendored) and used as execution oracle. Rule: no
implementation without PRIMARY article text; oracle behavior is evidence,
not truth.

## 0. Live-verified adapter facts (BBP binary, recorded)

- TRF writer ACCEPTED by BBP (exit 0 on fresh and realistic files).
- PAB encoding VERIFIED two ways: BBP source (U ⇒ win + pairing
  participation, eligibleForBye) AND live acceptance of U-coded histories
  with matching points. Earlier F-for-PAB assumption was WRONG, corrected.
- BBP score cross-check confirmed (rejects inconsistent points, exit 3).
- BBP requires XXR > 0 and explicit initial colour for colour-less fields.
- Round-1 pair SETS agree with native on fresh 4/8/10-player fields
  (oracle test, gated in CI when BBP_EXE set).
- BBP pin recorded above; live runs reproducible via tests/test_bbp_oracle.py.
- C9 bye ordering IMPLEMENTED (capability wave): among equal-score fresh
  bye candidates, fewer unplayed (`-`) rounds first — evidenced by BBP's own
  dutch_2025_C9 fixture (reproduced exactly), BBP source "C9" minimization
  weights, and the 2026 C9 criterion. Zero pinned behavior changed
  (no golden/corpus case has unplayed rounds except Y4, where fresh-first
  dominates): additive refinement in previously-untested territory, with new
  goldens (unit + corpus Y5 + live oracle). O08 compat contract holds.

## 1. Target rulesets (unchanged)

- Implemented + pinned: `dutch-till2026-compat` (pre-2026 formulation as
  realized by the frozen kernel; F1 goldens are its executable spec).
- NOT implemented: `dutch-2026` (C1–C21 optimisation rewrite). No code
  claims it; no code path selects it (resolve rejects it explicitly).

## 2. Article-by-article map (till-2026 text)

| Article (till-2026) | Native behavior | Grade | Verdict |
|---|---|---|---|
| A.2 ranking by pairing number | sort_key (-pts, pno, id); rating inert | PRIMARY (AUM) | CONFORMANT |
| A.3/A.4 brackets, S1/S2, floaters-first hetero | build_brackets + merge order | PRIMARY-excerpt | CONFORMANT (order fidelity: validator-anchored, exact D.2 order UNVERIFIED) |
| A.5/PAB assignment (odd field, no colour, draw-valued pre-2026) | bottom-up fresh-first; value unmodelled (manager-side) | PRIMARY-excerpt | CONFORMANT (selection); value OUT of pairing scope |
| A.6 colour preferences (absolute/strong/mild triggers) | compute_color triggers | PRIMARY (AUM table) | CONFORMANT (triggers) |
| A-float definitions (higher-ranked=D, non-player=D) | _Pair tags from cascade flags | PRIMARY-excerpt | CONFORMANT |
| B transpositions-then-exchanges, resident-only | pairer + exchange order | PRIMARY-excerpt | CONFORMANT (D.2 comparison-rule exactness UNVERIFIED) |
| B.7 heterogeneous remainder as homogeneous | single S1/S2 machinery for merged brackets | PRIMARY-excerpt | DEVIATION-FORM (no MDP/remainder split) — behaviorally valid per corpus, FIDE-order fidelity open |
| C1 no rematch | bidirectional absolute gate | PRIMARY | CONFORMANT |
| C2 no second PAB / forfeit handling | fresh-first; repeat allowed iff all-bye'd; forfeit concept absent (input modeling) | PRIMARY-excerpt | OPEN (repeat-bye semantics + GEN-03 severity need article text) |
| C3 same-absolute-colour non-topscorers | absolute gate + rank conflict resolution | PRIMARY-excerpt | CONFORMANT (conflict resolution uncited, behavior pinned) |
| E.1–E.4 allocation priorities | 4-level chain approximates | PRIMARY-excerpt | PARTIAL (E.3 alternation-history, E.5 parity not modelled) |
| E.5 initial-colour by pairing-number parity (round 1) | S1-white round 1 (F1-pinned) | PRIMARY-excerpt + LIVE BBP demo | CONFIRMED DEVIATION, see §3 (frozen per O08) |
| Odd-tail / CLB handling | backtrack-to-even via upstream floats | PRIMARY-excerpt | CONFORMANT in outcome space (all subsets explored; Stage-1.6 proof) |
| "Arbiter shall decide" impossibility | typed ImpossiblePairingError + diagnostics | PRIMARY-excerpt | CONFORMANT (library mapping of human-judgment clause) |

## 3. E.5 round-1 parity — CONFIRMED deviation (live demo + excerpt agree)

Pre-2026 E.5 (excerpt): with initial colour by lot, the higher-ranked player
of each pair gets the initial colour iff their pairing number is odd, else
the opposite. LIVE CONFIRMATION (BBP 8f9e3c5): round-1 8-fresh with XXC
white1 → `1v5, 6v2, 3v7, 8v4` (even-pno 2,4 take BLACK); black1 → exact
mirror. Native gives S1 (1–4) white — DEVIATES on boards 2 and 4. Severity:
colour allocation is output, so this is conformance-relevant, not cosmetic.
Disposition: kernel FROZEN per O08 (F1 goldens pin S1-white); correction
requires a dated-ruleset migration + golden migration under owner decision.
Tracked for Dutch-2026 scope (pending whether 2026 E-rules retain parity).

## 4. 2026 deltas (all DEFERRED, none implementable from excerpts alone)

Played-only colour history (already holds by construction); win-valued PAB
(unmodelled — manager-side); C2 forfeit-win exclusion (no forfeit concept —
input modeling); topscorer split (needs article text); C1–C21 optimisation
framing (rewrite-scale; needs article text + oracle). None attempted.

## 5. Firmly-mappable kernel changes in this wave: NONE

Every candidate required either article text not in hand or input concepts
the core must not own (forfeits, PAB valuation, lots). The kernel is
therefore UNCHANGED in W6. Conformance deliverables stand as: F1 goldens
(executable compat spec) + W4 rule-anchored corpus (18 cases, validator as
independent anchor) + BBP/JaVaFo oracle adapters (live-binary runs pending).

## 5. Firmly-mappable kernel changes: NONE (W6 outcome, superseded by §7–§9)

## 6. Asymmetric-history strictness (standing instruction outcome)

chess-manager data/contracts are NOT in this repository (verified: no
manager sources present). Per instructions: behavior UNCHANGED, documented
here. The new-path boundary keeps rejecting asymmetric memory with
InvalidPlayerError; the legacy path keeps its defensive tolerance. Phase-3
(manager evidence) owns the final call.

## 7. Float-bar oracle divergence (LIVE differential, 12 RTG tournaments)

Method: BBP RTG (seeded, forfeit-minimized) → our TRF → BBP `-p` vs native
`pair_via`, classified by the harness taxonomy (BBP outputs additionally
screened by our independent validator). Result: 7 valid-alternative (both
sides validator-clean, different legal pairings — expected first-wins vs
global-optimum divergence), 5 native-Impossible where BBP pairs legally.
Root cause (seed-101 autopsy + BBP source): our ABSOLUTE bar
(consecutive_downs ≥ 2 ⇒ can never downfloat again) blocks singleton-top
players with `--DD` histories; BBP has NO absolute float bar — repetition
enters only as weighted-minimization criteria (dutch.cpp: "Minimize
down/upfloaters repeated from the previous/two-rounds-before", score-ordered
variants), and its absolute gate (`compatible()`) covers rematch + absolute
colour + completeness only. The bar is donor lore with zero FIDE citations
in-repo; against it stand BBP's strict implementation + 2026 C14–C17
minimization framing. Classification: suspected over-strictness, ruleset
distinction pending article text. NO kernel change (would alter observable
behavior under O08; the 2026-criteria engine dissolves the bar naturally).
Pinned: corpus X101 (native failure) + X100 (valid-alternative) with BBP
provenance; live re-verifiable via tests/test_bbp_oracle.py (BBP_EXE).

## 8. Repeat-bye: resolved analytically (no kernel change)

Live probes: fresh-first agreement (allpab4: both bye the never-bye'd
player); all-used + rematch-blocked → BOTH refuse (BBP exit 1, native
Impossible). Combinatorics proof: in a clean odd-P event, all-P-used
(P ≤ R rounds) and pairs-remaining (R < P) are jointly impossible
(P rounds × (P−1)/2 slots = C(P,2)). Hence repeat-PAB only matters with
disruptions (withdrawals/re-entries/absences) — native's allow-if-all-used
is a completion-tolerant application behavior for exactly those states,
BBP's refusal is FIDE-pure. A ruleset variant (strict vs tolerant) can be
decided for future ids; current behavior documented, corpus Y1–Y4 covers it.

## 10. Live-differential summary (42 oracle tournaments, 2026-10-02)

BBP 8f9e3c5 (Dutch 2025) RTG-seeded fields + JaVaFo 2.2 b3223 (Dutch
**2017** per its own 092 tag — older vintage, read disagreements
accordingly) RTG/model fields; native inputs derived with documented
FIDE-A-def float reconstruction; BBP outputs screened by our validator.

| Outcome | BBP (32) | JaVaFo (10) | Meaning |
|---|---|---|---|
| Pair-compatible, both validator-clean | 18 (8 effectively exact modulo unknown BBP tags; 10 pair-divergent-but-legal) | 6 (incl. 2 colour-dimension) | first-wins vs global-optimum choice divergence |
| Native Impossible, oracle legal+clean | 14 | 4 | float-bar over-strictness (§7); zero illegal outputs anywhere |

Methodology lessons recorded: oracle files need XXR + truncation with
recomputed points (both engines otherwise repair the last round — a
misleading "rematch" artifact, not an engine finding); BBP float tags are
unknown to the comparison, so tag-only "float" flags mean effectively-exact.
Live re-verification: tests/test_bbp_oracle.py (BBP_EXE),
tests/test_javafo_oracle.py (JAVAFO_JAR).

## 9. Valid-alternative characterization (seed-100 autopsy)

BBP {7v1, 9v2, 3v5, 4v6, 10v8} vs native {1v5, 2v9, 3v7, 4v10, 6v8}: disjoint
pair SETS, both validator-clean. Systematic pattern TBD across more seeds;
working hypothesis: global float/colour minimization (BBP weights) vs
bracket-order first-wins (native). This is the FIDE-order-fidelity question
in the flesh — resolvable only by the 2026-criteria engine + bigger oracle
mass, NOT by tuning the frozen kernel.
