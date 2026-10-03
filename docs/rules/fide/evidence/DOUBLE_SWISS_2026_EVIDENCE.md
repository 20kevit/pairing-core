# Evidence — Double Swiss 2026 (C.04.5)

1. Source ID: F-0114. Handbook: https://handbook.fide.com/chapter/DoubleSwissSystem202602.
2. Approval 28/10/2025 (CM3-202517); effective 01/02/2026. New standalone chapter
   (pre-2026 C.04.5 was Accelerated — renumbered to C.04.7).
3. Sections (all read in full): Preface (2-game alternating-colour matches;
   per-game points; full result table incl. ½-0/0-½/0-0 derivatives; forfeit-both
   rule with repeat-pairing exception; single-game forfeit = played for
   standings/tie-breaks, not rating; byes apply to matches only); 1.1 TPN;
   1.2 order score→TPN; 1.3 brackets (even, residents + lower upfloaters);
   1.4 PAB = win+draw match value, uniform; 1.5 floater = cross-score;
   1.6 match colour = first-game scheduled colour if ≥1 game played;
   Art.2 criteria C1–C8 (C1 no repeat modulo forfeit-both; C2 PAB block incl.
   forfeit-match-win + deprecated FPB; C3 completion; C4 minimise upfloaters;
   C5 upfloater gaps; C6 next-bracket C1/C3/C4; C7/C8 non-last-round float-repeat
   guards); 3.1 legal pairing (C1+C2; +C3 during pairing); 3.2 top-scoregroup;
   3.3 outlook + 4-step process + colours Art.4; 3.4 PAB (completion → lowest
   score → most matches → largest TPN); 3.5 upfloater sets (C4/C5 filter,
   score-desc/TPN-asc inner sort, lexicographic set order, worked {2,6,1}…
   example; first set satisfying C6/C7); 3.6 bracket pairing identifiers
   (top-member-TPNs asc + bottom TPNs; worked `4 6 9 11 8 16 10 24`; lexicographic;
   first satisfying C1/C8); Art.4 colours (HRP = higher score else smaller TPN;
   unplayed-odd-HRP initial-colour; fewer-Whites → alternate → HRP alternation →
   opponent alternation; White-holder opens match White).
4. Retrieval: Council PDF. Evidence: FULL_TEXT. Extracted: `../extracted/DOUBLE_2026_RULES.md`.
5. Unresolved: none. Cross-checks: handbook snippets match preface/headers.
6. Implementation: new `double-2026` ruleset + additive match-score domain model
   (does NOT disturb single-game Swiss model). Needs match-result inputs
   (per-game points) — new explicit input type.
