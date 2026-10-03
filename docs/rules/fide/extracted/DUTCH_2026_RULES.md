# Dutch 2026 — Extracted Rules (C.04.3, effective 01/02/2026, F-0105)

Source: Council bundle CM3-202517 (FULL_TEXT, verified by direct reading).
Paraphrased in our own words; article refs exact. Statement classes inline [...].

## Ranking / scoregroups / brackets
- R-D23 [DEFINITION, 1.1–1.2]: TPN per C.04.2 Art.2; pairing order = score, then TPN ascending.
- [DEFINITION, 1.3]: scoregroup = same score; bracket = non-empty scoregroup residents +
  unpaired leftovers from previous bracket; homogeneous vs heterogeneous; remainder =
  resident-only sub-bracket (Art.3.3).
- [DEFINITION, 1.4]: downfloater = unpaired-in-bracket, moved down, becomes MDP below;
  cross-score play: higher-ranked (1.2) downfloat, lower upfloat; PAB or unplayed
  above-loss score also downfloat; nothing else floats (1.4.4 closed list).
- [DEFINITION, 1.5]: PAB = C.04.1 Art.3 (no opponent/colour, win-value unless regs differ).
- [DEFINITION, 1.9]: round complete iff all but ≤1 PAB-downfloat paired under C1–C3;
  top-down processing; else Chief Arbiter decides (MANDATORY RULE 1.9.3).

## Colour preferences (1.7) + allocation (Art.5)
- [DEFINITION, 1.7.1 absolute]: |CD|>1, or same colour in last two played rounds
  (White if CD<−1 or last-two Black; Black if CD>+1 or last-two White).
- [DEFINITION, 1.7.2 strong]: CD=+1 → Black; CD=−1 → White.
- [DEFINITION, 1.7.3 mild]: CD=0 → alternate last played.
- [DEFINITION, 1.7.4]: zero games → no preference (opponent's granted).
- [DEFINITION, 1.8]: topscorer = score >50% of maximum possible at final-round pairing.
- [ALGORITHM STEP, 5.1]: initial-colour by lots before round 1.
- [ALGORITHM STEP, 5.2]: grant both (5.2.1) → stronger (5.2.2; both-absolute topscorers →
  wider CD) → alternate vs most recent White-vs-Black encounter + C.04.2 Art.3.4 played-only
  (5.2.3) → higher-ranked preference (5.2.4) → odd-TPN higher-ranked gets initial-colour
  else opposite (5.2.5). NOTE: 5.2.5 is the E.5-successor (parity rule survives in 2026).

## Criteria C1–C21 (Art.2)
- [MANDATORY, C1–C3]: no repeat (C.04.1 Art.2); no second PAB/unplayed win (C.04.1 Art.4);
  same-absolute non-topscorers shall not meet (C.04.1 Arts.6–7).
- [MANDATORY C4 completion]: an absolute-compliant continuation must always exist for
  the not-yet-paired (precedes even C5: completion can force PAB out of lowest group).
- [C5 PAB]: minimise assignee score. [C6]: minimise downfloater count (= max pairs).
- [C7]: minimise downfloater scores descending. [C8 look-ahead]: choose downfloaters so
  the NEXT bracket satisfies C1–C7 (one bracket deep only).
- [C9]: (brackets downfloating exactly one eventual PAB taker) minimise assignee's
  unplayed games. [C10]: minimise topscorer/opponent CD beyond ±2.
- [C11]: minimise topscorer/opponent 3× same colour. [C12]: minimise ungranted
  preferences. [C13]: minimise ungranted strong preferences.
- [C14]: minimise resident downfloaters floated last round. [C15]: minimise MDP
  opponents upfloated last round. [C16]/[C17]: same for two rounds ago.
- [C18]: minimise score gaps (desc) of MDPs downfloated last round. [C19]: same for MDP
  opponents upfloated last round. [C20]/[C21]: same pair for two rounds ago.

## Bracket process (Art.3)
- [DEFINITION, 3.1]: M0 = incoming MDPs (may be 0); MaxPairs = max producible pairs
  (usually floor(N/2); ≤ residents if M0 > residents); M1 = MDPs paired here
  (usually M0; ≤ residents; ≤ MaxPairs).
- [STEP, 3.2]: S1 = first MaxPairs residents (TPN asc) if homogeneous, else first
  pairable-MDP set (4.4.2); S2 = remaining residents; M0−M1 MDPs in Limbo → double-float.
- [STEP, 3.3]: S1[i]↔S2[i] tentative; homogeneous candidate = pairs + unpaired
  (downfloaters); heterogeneous = MDP-pairing + remainder paired homogeneously
  (M1=0 → straight to remainder); candidate = MDP-pairing + remainder candidate.
- [STEP, 3.4 perfect]: C1–C5 complied + C6–C21 all fulfilled → accept immediately;
  else 3.5, or 3.8 if none exists.
- [STEP, 3.6 homogeneous/remainder]: exhaust S2 transpositions (4.2), then resident
  S1↔S2 exchanges (4.3) with re-sort per 1.2.
- [STEP, 3.7 heterogeneous]: exhaust remainder moves (S1R/S2R frozen post-MDP-pairing),
  then new S2 transposition → new MDP-pairing + remainder, then next pairable-MDP set
  from Limbo (4.4.2) with S2 restored.
- [STEP, 3.8 best-available]: better = better satisfies higher-priority PAB/quality
  criterion; ties → earlier generation order.

## Sequential generation (Art.4)
- [STEP, 4.1 BSN]: tag all bracket/remainder players 1,2,3… in 1.2 order before shuffles.
- [STEP, 4.2 transpositions]: all S2 orders, sorted lexicographically by first N1 BSNs
  (N1=|S1|; trailing downfloater/remainder BSNs ignored; 11-player → 720; 2-MDP → 72).
- [STEP, 4.3 resident exchanges]: equal-size original-S1↔S2 BSN swaps; comparison rules:
  (1) fewest BSNs moved; (2) smallest |Σ(S2→S1) − Σ(S1→S2)|; (3) largest differing BSN
  leaving S1; (4) smallest differing BSN entering S1.
- [STEP, 4.4 MDP sets]: valid iff Limbo satisfies C7; sorted by smallest differing BSN.
- [STEP, 4.5]: each application picks the next element in the established order.

## Special cases / failure
- M1=0 → empty S1, all MDPs Limbo, direct remainder (3.3.3 note).
- Total failure → Chief Arbiter decides (1.9.3); library maps to typed impossibility
  [IMPLEMENTATION GUIDANCE].
- "Test pairing" (completion probe) need not equal final pairing [NOTE, Annotated].
- PPB/CLB machinery: REMOVED 2024 [HISTORICAL RULE]; Requirement Zero/C4 replaces it.

## Rule IDs covered
R-D01…R-D24 (matrix) + R-D25 (5.2.5 parity), R-D26 (C8 one-bracket look-ahead),
R-D27 (M0/M1/MaxPairs/Limbo machinery), R-D28 (4.2/4.3/4.4 generation order).
