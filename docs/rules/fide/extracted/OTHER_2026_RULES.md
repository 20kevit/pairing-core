# Double / Team / Baku / Olympiad — Extracted Rules

## Double Swiss 2026 (C.04.5, F-0114)
- Preface: 2-game alternating matches, per-game points; full result table (2-0 …
  0-2 + ½-0/0-½/0-0 derivatives); forfeit-both → match forfeited + repeat allowed;
  single-game forfeit = played for standings/tie-breaks (NOT rating); byes = matches only.
- 1.2 order score→TPN. 1.3 even brackets (residents + lower upfloaters).
  1.4 PAB = win+draw value, uniform. 1.5 floater = cross-score.
  1.6 match colour = first-game scheduled colour if ≥1 game played.
- C1 no repeat (forfeit-both exception); C2 PAB block (PAB/forfeit-match-win/deprecated FPB);
  C3 completion; C4 minimise upfloaters; C5 upfloater gaps; C6 next-bracket C1/C3/C4;
  C7/C8 non-last-round float-repeat guards (upfloaters / their opponents).
- 3.1 legal = C1+C2 (+C3 during pairing). 3.3 four-step process (PAB → top+upfloaters →
  repeat → colours Art.4); else Arbiter.
- 3.4 PAB: completion-leaving → lowest score → most matches → largest TPN.
- 3.5 upfloater sets: C4/C5 filter; inner sort score-desc/TPN-asc; lexicographic set order
  (worked {2,6,1}<{2,6,3}<… example); first set also satisfying C6/C7.
- 3.6 identifiers: top-member TPNs asc + bottom TPNs (worked `4 6 9 11 8 16 10 24`);
  lexicographic; first satisfying C1/C8.
- Art.4: HRP = higher score else smaller TPN; unplayed odd-HRP initial-colour;
  fewer-Whites → alternate (C.04.2 3.4) → HRP alternation → opponent alternation;
  White-holder opens White.
- Rule IDs: R-T01…R-T03 + R-T04 (match result table), R-T05 (colour rules).

## Team Swiss 2026 (C.04.6, F-0115)
- Preface: C.04.1 + C.04.2 Arts.1/2.4/2.5/3/4 mutatis mutandis EXCEPT C.04.1 Arts.6–7
  NEVER apply (no absolute colours). Type A default / Type B optional / none.
  TPN assignment = competition rules (Chief Arbiter fallback).
- 1.2 primary/secondary score (default MP / GP-for-colours). 1.3 even brackets.
  1.4 PAB = draw-value MP+GP, uniform. 1.6 match colour = board-1 scheduled colour
  if played; CD = W−B. 1.7 Type A simple (±1 thresholds + last-two-same at CD 0/∓1)
  / Type B strong+ mild (CD ∓1; CD-0 non-last-round last-game; none if unplayed or
  CD-0 last round).
- C1/C2 absolute; C3 completion; C4 minimise upfloaters; C5 gaps; C6 next-bracket;
  C7 non-last-TWO float-repeat; C8 ungranted prefs; C9 Type-B strong; C10 non-last-two
  opponents' float-repeat.
- 3.4 PAB: completion → lowest score → most matches → largest TPN.
  3.5/3.6 same lexicographic machinery + worked examples as Double.
- Art.4: first-team (primary → secondary unless dropped → smaller TPN);
  unplayed-odd initial-colour; sole → opposite → Type-B-strong → lower CD
  (−2<−1<+1<+2) → alternate → first-team pref/alternation → other alternation.
- Rule IDs: R-M01…R-M04 + R-M05 (Type A/B), R-M06 (first-team + colour chain).

## Baku 2026 (C.04.7, F-0117)
- Preface: bracket rearrangement via virtual points; statistical-proof admission; any
  Swiss system unless stated. 1.1 premise win = 2 draws, loss = 0.
- 1.2 GA = first half rounded UP to even (161→82; formula 2·ceil(N/4) = last GA TPN).
- 1.3 late entries per C.04.2 Art.2; GA-boundary player frozen (TPN may shift; GA may go odd).
- 1.4 accelerated rounds = first ceil(half) of tournament; GA gets win-value for first
  half of those (rounded up), halved after; GB/post = none. Worked: 9R individual →
  1.0×3 + 0.5×2; 11R team MP → 2×3 + 1×3; gamepoint-primary excluded.
- 1.5 pairing score = standings + virtual (also board order per C.04.2 3.6).
- Rule IDs: R-A01…R-A02 + R-A03 (GA split), R-A04 (virtual schedule), R-A05 (pairing score).

## Olympiad 2022 (F-0601)
- 3.1 initial rank: avg top-4 rating → 5th rating → alpha. 3.2 per-round: MP → initial number.
- 4. bye: lowest-initial-number ELIGIBLE (ineligible: bye/default-win/joined-after-R1);
  1 MP + 2 GP. 5. unfinished = draws for pairing. 6.1 no repeat; 6.2 score-gap minimised;
  6.4 median routing + even-field lower-middle rule + 88-team example.
- 7. board-1 colours (board-not-player; R1 lot; CD ±2 + 3-in-row bans; float-necessity
  override; equalise→alternate; walkback; unplayed = no colour).
- 8. floaters: up (highest→lowest-unplayed + completion fallback chain 8.2.1–8.2.4);
  down mirror 8.3; 8.4 re-floater fallback.
- 9. top-half-vs-bottom-half with 1v(N+1)→(N+2)…→(N−1)… search + 15-combination table;
  9.2 rank-priority (above-median top-down, below-median bottom-up); 9.4/9.5
  max-in-group-pairings. 10. presence rules (management OUT). 11. board-order
  publication + 11.3 frozen unless 6.1/7.3 breach.
- Rule IDs: R-M03…R-M04 + R-M07 (bye), R-M08 (median routing), R-M09 (9.x search order).
