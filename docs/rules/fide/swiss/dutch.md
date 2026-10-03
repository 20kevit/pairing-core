# Dutch System — Structured Research Note

## Identity
- System name: FIDE (Dutch) System. FIDE terminology: "FIDE (Dutch) System", C.04.3.
- Rulesets: till-2026 [F-0107] (effective till 31/01/2026) → interim 2025 [F-0106]
  (effective 01/07/2025) → 2026 [F-0105] (effective 01/02/2026, Council 28/10/2025).
- pairing-core纪律: frozen kernel = `dutch-till2026-compat` (pre-2026 formulation
  as realized; behavior FROZEN, O08 compat contract). `dutch-2026` explicitly rejected.

## Authoritative sources
- [F-0105] C0403202602 — exact sections: criteria [C1]–[C21]; PAB provisions; topscorer split.
- [F-0107] C0403Till2026 — exact sections: A (A.2 ranking, A.3/A.4 brackets S1/S2,
  A.5 PAB, A.6 colour preferences, float definitions), B (transpositions D.1,
  exchanges D.2 resident-only, B.7 heterogeneous remainder), C1–C3 completion gates,
  E.1–E.5 colour allocation (E.5 = initial-colour parity by pairing number).
- [F-0101] C.04.1 — rematch ban, PAB value (draw pre-2026 / win 2026), colour limits.
- [F-0103] C.04.2 — authorised systems, TPN/initial order, QC authorisation (§1.2–1.3).
- [F-0201] CM3-202517 — enacting instrument. [F-0301]/[F-0302] — applicability evidence.

## Inputs (MANDATORY RULE where marked)
- Pairing numbers (TPN), frozen before round 1 [F-0103] — DEFINITION.
- Scores incl. virtual PAB points (2026 PAB types: half/virtual/zero/full [F-0106]).
- Colour histories — only games actually played on the board enter colour history
  (2026; MANDATORY RULE, secondary-consistent, article TBD).
- Opponent histories (rematch ban C1 — MANDATORY RULE, both formulations).
- Float histories (direction + recency; 2026 C14–C17 repetition bars — MANDATORY RULE frame).
- Forfeit/win flags (C2: no second PAB / forfeit-win exclusion — MANDATORY RULE frame).
- Initial colours by lot incl. E.5 parity (till-2026 — MANDATORY RULE): higher-ranked
  gets initial colour iff pairing number odd, else opposite.

## Definitions
- Scoregroup = equal scores; bracket = residents + incoming floaters; homogeneous
  (no incoming) vs heterogeneous (with incoming) [F-0107] — DEFINITIONS.
- S1/S2 = top/bottom halves by pairing number; P0 = pairing under test;
  MDP = most-desirable-products; BSN = bracket sequence number; Limbo = unpaired MDP
  players (bound downfloaters) [F-0107] — DEFINITIONS (till-2026; none modelled natively).
- PPB/CLB = special end brackets — HISTORICAL RULE (removed 2024 per S-0106).
- PAB = pairing-allocated bye; value draw (till) / win unless regs state otherwise
  (2026) [F-0101] — DEFINITION + MANDATORY RULE.
- Topscorer vs non-topscorer (2026 colour split, C3/C10–C13) — DEFINITION (frame only).
- Colour preferences: absolute (double WWW/BBB; by-difference; by-repetition),
  strong, mild, none [F-0107 A.6] — DEFINITIONS.

## Pairing process (ALGORITHM STEPs; 2026 framing)
1. Order brackets top-down by score [F-0105] (STEP).
2. Assign PAB within last-bracket pairing: lowest score (C5), minimise recipient's
   unplayed games (C9), exclude already-bye'd/forfeit-win (C2) [F-0105] (STEPs).
3. For each bracket: maximise pairs (C4/C5-class completion), minimise downfloater
   count (C6), then scores descending (C7), then next-bracket suitability (C8) (STEPs, frame).
4. Satisfy colour controls C10–C13 (STEPs, frame; topscorer ±2, 3×colour, preferences).
5. Minimise float repetition C14–C17 + score gaps C18–C21 (STEPs, frame).
6. Till-2026 mechanics: S1/S2 tentative pairing → transpositions (D.1) → resident-only
   exchanges ordered by D.2 comparison rules on post-exchange S1 → heterogeneous
   remainder re-paired with homogeneous rules (B.7) (STEPs).
7. Total failure → "arbiter shall decide" [F-0107] (MANDATORY RULE → library maps to
   typed impossibility; IMPLEMENTATION GUIDANCE).

## Ordering / Constraints / Preferences
- MANDATORY: C1 no rematch (both formulations); C2 no second PAB; C3 same-absolute
  non-topscorers shall not meet (2026); completion C4.
- Ordering: pairing numbers break all ranking ties (MANDATORY RULE [F-0103/AUM]).
- Till-2026 exchange order: D.2 comparison rules (exact fidelity UNVERIFIED in native).

## Colour allocation
- E.1–E.4 priorities (till-2026, MANDATORY RULE frame): grant both → stronger →
  alternation history → higher-ranked preference → E.5 parity.
- 2026: topscorer split; played-only history (MANDATORY RULE frames).
- Native gaps (NOTE, not defect claim): E.3 alternation, E.5 parity, topscorer split
  unmodelled; E.5 deviation CONFIRMED by live BBP demo (round-1 boards 2/4) — frozen.

## Float handling
- Tags: higher-ranked cross-score player = downfloat; lower = upfloat; non-player =
  downfloat [F-0107 A-defs] (MANDATORY RULE).
- Till-2026: two consecutive same-direction floats strongly avoided; three effectively
  barred via completion (HISTORICAL RULE frame).
- 2026: minimisation criteria C6–C9/C14–C21 — MANDATORY RULE frame; there is NO
  verified absolute "float-bar" in 2026 (BBP source has weighted minimisation only;
  see DUTCH_CONFORMANCE_STATUS §7). Any absolute-bar claim = WITHDRAWN pending citation.

## Bye handling
- Odd field → one unpaired: no opponent, no colour; value draw (till) / win (2026)
  unless regs state otherwise (MANDATORY RULE [F-0101]).
- Selection: lowest score (C5) + fewest unplayed games (C9) + fresh-first (C2)
  (MANDATORY RULE frames). Bye counts as downfloat (NOTE, secondary-consistent).

## Exchange / transposition — see process step 6.

## Special cases
- Collapsed-last-bracket tail handling (till-2026; outcome-conformant natively) (NOTE).
- Single-leader top bracket; odd-tail backtracking (NOTES).

## Failure / impossible conditions
- "Arbiter shall decide" on impossible completion [F-0107] (MANDATORY RULE);
  native `ImpossiblePairingError` + diagnostics = conformant library mapping (NOTE).

## Examples
- Official 2026 examples: in full text (G-01). TEC tutorials S-0106 (secondary walkthrough).
- Executable compat spec: F1 goldens pin `dutch-till2026-compat` (repository evidence).

## Ambiguities (evidence-backed only)
- A-01: D.2 exchange comparison-rule exactness vs native order (UNVERIFIED).
- A-02: 2026 criterion-level optimisation semantics (article bodies pending).
- A-03: topscorer threshold definition (article pending).
- A-04: C9 "unplayed games" counting rule detail (implemented from BBP C9 fixture;
  article pending).
