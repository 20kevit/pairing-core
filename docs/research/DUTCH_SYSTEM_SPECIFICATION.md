# Dutch System Technical Specification (STAGE 2 RESEARCH)

Covers mission §2.2 (deep dive), §2.3 (native-vs-FIDE matrix), §2.4
(adversarial cases, research only — NOT implemented as tests).
Source grades per claim. "FIDE rule" vs "implementation strategy" separated
throughout. Effective-date discipline: pre-2026 (till 31 Jan 2026) vs 2026
(from 1 Feb 2026) texts differ; both covered.

## 1. Which "Dutch" — versions (VERIFIED PRIMARY)

| Text | Reference | Bye value | Coding | pairing-core claim |
|---|---|---|---|---|
| C.04.3 till 31 Jan 2026 | handbook `C0403Till2026`; NewDutch2022.pdf (Chennai 2022) | draw (win unless regs state otherwise — C.04.1.c old) | A/B/C/D/E articles, MDP/BSN/Limbo/P0 | closest to native engine |
| C.04.3 from 1 Feb 2026 | handbook `C0403202602`; Council 28/10/2025; FIDE news 2026-02-01 | **win** unless regs state otherwise (C.04.1 art. 3) | unified C1–C21 optimisation criteria | NOT implemented natively |
| Repo claim "effective 1 July 2025" | `__fide_reference__` | FIDE news "Updated FIDE (Dutch) System Effective from July 1, 2025" (fide.com) | — | PARTIALLY VERIFIED: matches a real FIDE update announcement (simplification drawing on Dutch+Dubov insights); article-level mapping of that update vs the kernel still open |

## 2. Deep dive (FIDE rules; grades inline)

### 2.1 Pairing numbers & ranking

FIDE RULE (PRIMARY: JaVaFo AUM "Ranking id" + C.04.2 A.2.b reference):
pairings use **pairing numbers**, not ratings. Numbers are typically assigned by
rating/title/alphabet before round 1 and frozen. Initial colour by drawing of
lots (E-rules; pre-2026 E.5: odd pairing number gets initial colour).
IMPLEMENTATION STRATEGY (adopted by JaVaFo/BBP, PRIMARY: AUM): caller assigns
numbers; optional positional-id (`XXC rank`) override. Native engine: same
strategy (caller-owned `pairing_no`; rating inert) — consistent.

### 2.2 Score groups, brackets, homogeneous vs heterogeneous

FIDE RULE (PRIMARY: C0403Till2026 excerpts + 2024 TEC Dubov/Dutch drafts):
scoregroup = equal scores; bracket = residents + incoming floaters;
homogeneous = no incoming floaters; heterogeneous = with incoming floaters.
Top-down processing; collapsed last bracket (CLB) if tail cannot pair.
IMPLEMENTATION STRATEGY: native `build_brackets` + floaters-first merge
matches the heterogeneous definition (PARTIAL match — see §3).

### 2.3 S1/S2, P0, MDP, BSN, Limbo (pre-2026 formulation, PRIMARY excerpts)

S1 = top half by pairing number, S2 = bottom half; S1[i]↔S2[i] tentatively.
P0 = the pairing itself (S1/S2 configuration under test). Heterogeneous
brackets pair M1 MDPs (most-desirable-products: S1 vs resident-S2 pairs) while
remaining residents form the remainder; unpaired MDPs sit in **Limbo** and all
Limbo players are bound downfloaters. **BSN** (bracket sequence number) orders
players for exchange comparison. Native engine models NONE of MDP/BSN/Limbo/P0
explicitly (NOT IMPLEMENTED as concepts; behaviour approximated via S1/S2 +
downfloater flags) — see §3.

### 2.4 Colour preferences (absolute / strong / mild)

FIDE RULE:
- Pre-2026 A.6.a (PRIMARY: JaVaFo AUM checklist table): double-absolute
  (WWW/BBB: twice-same-colour AND |difference|>1), absolute-by-difference
  (WW/BB), absolute-by-repetition (W1/B1, W/B); A.6.b strong `(W)/(B)`;
  A.6.c mild `(w)/(b)`; A.6.d none `A`.
- 2026 (SECONDARY, consistent): absolute = twice-same-colour OR |diff|>2;
  topscorer/non-topscorer split in C3/C10–C13; **only games actually played on
  the board enter colour history** (unplayed rounds generate no preference).
- Allocation pre-2026 E.1–E.5 (PRIMARY excerpt): grant both → grant stronger
  (both-absolute topscorers: wider difference wins) → alternate by most recent
  opposite-colour round (with C.04.2.D.5) → higher-ranked preference → initial
  colour by pairing-number parity.
IMPLEMENTATION STRATEGY (native): balance/last-two model reproduces the
absolute triggers VERIFIED for standard histories; strong/mild chain is the
engine's own priority ladder (E.3-alternation and E.5-parity NOT modelled —
native uses due-colour + higher-ranked-white default). Difference, not
necessarily defect, pending article-level check.

### 2.5 Floaters (up/down), repetition bars

FIDE RULE: after cross-score play, higher-ranked gets downfloat, lower gets
upfloat; non-players get downfloat (PRIMARY: NewDutch2022 A-definitions).
2026 C14–C17 minimise float repetition (consecutive / within two rounds);
C18–C21 minimise float score gaps. Pre-2026: two consecutive same-direction
floats strongly avoided; three effectively barred via completion criteria.
IMPLEMENTATION STRATEGY (native): 3-level model (soft/strong/absolute) +
strict→relaxed passes — a reasonable strategy mapping, but C6–C9/C14–C21
**optimisation framing is absent** (native floats by parity + preference order,
not by minimising counts/scores). Difference recorded in §3.

### 2.6 Rematches, exchanges, transpositions

FIDE RULE (PRIMARY excerpts): transpositions reorder S2 (D.1); when exhausted,
**resident-only** exchanges between original S1/S2 (D.2) ordered by comparison
rules on post-exchange S1 (priority to specific S1 shapes); heterogeneous
remainder re-paired with homogeneous rules (B.7). C1 (no rematch) is the top
criterion in both formulations.
IMPLEMENTATION STRATEGY (native): transpositions-then-exchanges order matches;
exchange *enumeration detail* vs D.2 comparison rules UNVERIFIED (native has no
BSN concept; order described as "FIDE convention" without article cite).

### 2.7 Pairing criteria & optimisation (2026 C1–C21; SECONDARY source, consistent)

C1 no-rematch (mandatory); C2 no second PAB/unplayed full point (mandatory);
C3 same-absolute-colour non-topscorers shall not meet; C4 completion; C5 PAB to
lowest score; C6 minimise downfloater count; C7 minimise downfloater scores
descending; C8 downfloater suitability for next bracket; C9 minimise PAB
recipient's unplayed games; C10–C13 colour controls (topsccorer ±2, 3×colour,
preferences, strong preferences); C14–C17 float repetition; C18–C21 float score
gaps. Native engine is a **satisficing first-legal search**, not a criteria
optimiser — architectural difference (Stage 3 consequence).

### 2.8 Tie-breaking within rules

Pairing numbers break all ranking ties (FIDE RULE, PRIMARY). Native: pno then
id — the id final tiebreak is an implementation choice beyond FIDE (two players
never share a pairing number in a conformant tournament).

### 2.9 Byes (FIDE RULE, PRIMARY: C.04.1 art. 3 + C.2 + C5)

Odd field → one unpaired player: no opponent, no colour, win-points (2026;
draw pre-2026) unless regs say otherwise; already-bye'd / forfeit-win players
excluded (C.2/C.04.1.d); minimise recipient score (C5); minimise recipient's
unplayed games (C9); PAB assignment is part of last-bracket pairing; a bye
counts as a downfloat (SECONDARY manual; consistent). Impossible completion →
"arbiter shall decide" (PRIMARY: C0403Till2026) — i.e. FIDE explicitly leaves
total failure to human judgment; a library MUST surface structured impossibility.

## 3. Native engine vs FIDE matrix (§2.3 requirement)

| Native code | FIDE concept | Source | Match? | Difference | Risk |
|---|---|---|---|---|---|
| `make_engine_players` sort (-pts,pno) | A.2 ranking by pairing no | AUM Ranking-id (P) | YES | rating field inert (by FIDE design) | none |
| `build_brackets` exact-score groups | scoregroup/bracket, homo/hetero | C.04.3 (P) | PARTIAL | no MDP/BSN/Limbo/P0; floaters-first merge approximates hetero | medium — order fidelity UNVERIFIED |
| S1/S2 split + remainder | S1/S2/P0 | C.04.3 (P) | PARTIAL | no MDP-pairing vs remainder split; remainder = lowest-ranked default | medium |
| transposition DFS then exchanges | D.1 then D.2 resident exchanges | C.04.3 (P) | PARTIAL | D.2 comparison-rule order vs "FIDE convention" order UNVERIFIED; completeness VERIFIED (Stage 1.6) | medium |
| `compute_color` + priority chain | A.6 / C10–C13 + E allocation | AUM checklist (P) + 2026 (S) | PARTIAL | absolute triggers match; E.3/E.5, topscorer split, played-only history NOT modelled | medium-high |
| 3-level float + 2 passes | C6–C9/C14–C21 + repetition bars | 2026 (S) + A-defs (P) | WEAK | parity-driven floating, no count/score optimisation; inference-based upfloat | high for 2026 conformance |
| rematch bidirectional block | C1 | C.04.1 (P) | YES | — | none |
| bye bottom-up fresh-first | C.2/C5/C9 + C.04.1 | (P) | PARTIAL | greedy first-wins; C9 (unplayed games) absent; value (draw vs win) is caller-side | medium |
| `ValueError` on impossible | "arbiter shall decide" | C.04.3 (P) | WEAK | unstructured error, no diagnostics/partial-result policy | medium (Stage 3 fixes shape) |
| first-legal-wins search | C1–C21 optimisation | 2026 (S) | NO | satisficing vs minimisation across C6–C9/C12–C21 | high for 2026 conformance |
| locked_pairs | XXP forbidden pairs / manual pairing | AUM XXP (P) | PARTIAL | inverted polarity (forced vs forbidden); manual pairing exists in all managers | low (both needed long-term) |

Overall: native ≈ pre-2026 Dutch **legality kernel** (rematch + absolute colour
+ absolute float + bye basics) with an independent search strategy; NOT a
demonstrated implementation of either dated text, and architecturally distant
from the 2026 optimisation formulation. No compliance claimed.

## 4. Adversarial research cases (§2.4 — fixtures only, NOT tests)

Notation: `Pn(rating/pts|colours|floats|vs{opp})`. All PROPOSED.

**Bracket/backtracking (B1–B5):** B1 top-bracket triple at equal score with
cross-rematches forcing cascade depth 2; B2 three consecutive odd brackets
(float chain length 3); B3 single-leader bracket (1-player top group) with
colour-blocked S1/S2 below; B4 heterogeneous bracket where first-ranked
remainder poisons completion but second-ranked succeeds (order-fidelity probe);
B5 collapsed-last-bracket with 3 players (CLB handling probe).

**Floats (F1–F5):** F1 player with `DD` history requiring third downfloat
(absolute-bar probe); F2 `D-` vs `-D` streak-break semantics (validator WARNING
vs ERROR boundary); F3 two downfloaters meeting (D/D tag case from Stage 1.6
differential — observed real instance); F4 upfloat-after-double-upfloat
(`UU` + opponent-down inference); F5 strict-vs-relaxed pass divergence (pairing
exists only with 2nd-consecutive float).

**Colour (C1–C5):** C1 `ww` vs `ww` (both-absolute conflict, rank resolution);
C2 balance +2 vs -2 cross (both absolute opposite — grant-both); C3 strong vs
strong same direction; C4 mild vs none (alternation probe); C5 unplayed-round
colours (`-` must not create preference — 2026 played-only rule).

**Rematch (R1–R5):** R1 4-player round-robin-exhausted field (impossible-state
probe); R2 one-sided opponent memory (asymmetric sets); R3 locked-pair rematch
(rejection probe); R4 rematch-density forcing maximum floats; R5 self-pair
attempt via locked pair (rejection probe).

**Bye (Y1–Y5):** Y1 all-fresh odd field (lowest-score-lowest-rank wins); Y2 one
fresh left among bye'd (fresh priority); Y3 all-bye'd (repeat allowed, INFO
level); Y4 odd field where lowest candidate's remainder is unpairable but a
higher candidate works (greedy-order probe); Y5 single-player tournament.

**Impossible (I1–I5):** I1 fully-played small field (no legal pairing —
`ValueError` shape probe); I2 colour-locked field (all absolute same side);
I3 float-locked field (all at consecutive-downs cap); I4 odd field, every bye
candidate's remainder unpairable; I5 100-player single-score bracket (step-cap
behaviour probe — expects bounded failure, not hang).
