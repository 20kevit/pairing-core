# Dutch Conformance Status (W6 — article map, no kernel changes)

Method: re-retrieval attempted 2026-10-01 (handbook fetch: timed out again;
targeted search: no article text). Grades: PRIMARY-excerpt (handbook/AUM/BBP
manual excerpts retrieved earlier), SECONDARY (guides), UNKNOWN (not
retrieved). Rule: no implementation without PRIMARY article text.

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
| E.5 initial-colour by pairing-number parity (round 1) | S1-white round 1 (F1-pinned) | UNKNOWN (excerpt ambiguous) | OPEN — possible deviation, see §3 |
| Odd-tail / CLB handling | backtrack-to-even via upstream floats | PRIMARY-excerpt | CONFORMANT in outcome space (all subsets explored; Stage-1.6 proof) |
| "Arbiter shall decide" impossibility | typed ImpossiblePairingError + diagnostics | PRIMARY-excerpt | CONFORMANT (library mapping of human-judgment clause) |

## 3. E.5 round-1 question (NEW open item, do not act on)

Pre-2026 E.5 (excerpt): with initial colour by lot, the higher-ranked player
of each pair gets the initial colour iff their pairing number is odd, else
the opposite. Naively applied with initial=white, even-pno top-half players
(pno 2, 4, …) would get BLACK in round 1 — contradicting the F1-pinned
S1-white behavior and universal top-half-white practice. Possible readings:
(a) excerpt is from a superseded draft; (b) "initial-colour" determination
differs (JaVaFo hash-seeded default + XXC overrides suggest managers control
this); (c) E.5 truly mandates parity-based round-1 colours. WITHOUT the full
article text this cannot be resolved — changing round-1 colours now would
break the compat contract on a guess. Recorded in OPEN_QUESTIONS; kernel
UNCHANGED.

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

## 6. Asymmetric-history strictness (standing instruction outcome)

chess-manager data/contracts are NOT in this repository (verified: no
manager sources present). Per instructions: behavior UNCHANGED, documented
here. The new-path boundary keeps rejecting asymmetric memory with
InvalidPlayerError; the legacy path keeps its defensive tolerance. Phase-3
(manager evidence) owns the final call.
