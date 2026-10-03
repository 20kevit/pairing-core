# Evidence — Olympiad Pairing Rules (2022, current)

1. Source ID: F-0601. Handbook: https://handbook.fide.com/chapter/OlympiadPairingRules2022;
   diff: …/OlympiadPairingRules2021Changes; live pointer Olympiad2026MainCompetition.pdf §4.1.
2. Approval: Council 27/10/2021 (annex doc `3FC2021 Annex 3.2.3 2021-1015`);
   effective 01/01/2022. No newer Olympiad pairing text found (2026-10-03).
3. Sections (full annex PDF retrieved via curl + pdftotext, SHA `e7c995b9…`,
   210 lines, /tmp only): 1. Swiss system; 2. B/C teams for odd fields;
   3.1 initial rank (avg top-4 rating → 5th rating → alpha); 3.2 per-round rank
   (matchpoints → initial number); 4. bye (lowest initial number eligible;
   ineligible if bye/default-win/joined-after-R1-published; 1 MP + 2 GP);
   5. unfinished games = draws for pairing; 6. no repeat; score-gap minimisation;
   groups = matchpoint sets; 6.4 median-group routing (top→pre-median,
   bottom→pre-median, median last; even-field lower-middle = median; 88-team
   worked example); 7. board-1 colours (7.1 board-not-player; 7.2 R1 lot;
   7.3 CD ±2 / 3-in-row bans; 7.4 float-necessity override; 7.5 equalise→alternate;
   7.6 history walkback; 7.7 unplayed = no colour); 8. floaters (8.1 definition;
   8.2 up: highest→lowest-unplayed with remainder-completion fallback chain;
   8.3 down mirror; 8.4 re-floater fallback); 9. S1/S2-style top-half-vs-bottom-half
   with 1v(N+1)→(N+2)…→(N−1)… search order + worked 6-team 15-combination table;
   9.2/9.4/9.5 rank-priority + max-in-group-pairings; 10. presence/team-size
   management rules; 11. board-order publication + 11.3 frozen-pairings rule
   (change only on 6.1/7.3 breach).
4. Evidence: FULL_TEXT (official Council annex PDF). Extracted: `../extracted/OLYMPIAD_RULES.md`.
5. Unresolved: none at text level. Olympiad ≠ C.04.6 Team Swiss (distinct system:
   median routing, initial-number bye, board-1 colours) — modelled as specialised
   ruleset `olympiad-2022` at application layer (team engine reuse where exact).
6. Implementation: new `olympiad-2022` ruleset (bye rule, median routing, 9.x
   search order, board-1 colours). Arts.10–11.3 presence/publication = management OUT.
