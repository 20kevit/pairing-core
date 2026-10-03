# Evidence — Team Swiss 2026 (C.04.6)

1. Source ID: F-0115. Handbook: https://handbook.fide.com/chapter/SwissTeamPairingSystem202602.
2. Approval 28/10/2025 (CM3-202517); effective 01/02/2026. Supersedes F-0116.
3. Sections (all read in full): Preface (C.04.1 + C.04.2 Arts.1/2.4/2.5/3/4 apply
   mutatis mutandis EXCEPT C.04.1 Arts.6–7 never apply — no absolute colour
   preferences; Type A default / Type B optional / none allowed; TPN assignment
   left to competition); 1.1 TPN 1…N + competition assignment + freeze;
   1.2 primary/secondary score (default match points / game points for colours);
   1.3 brackets (even, residents + lower upfloaters); 1.4 PAB = draw-value
   match+game points, uniform; 1.5 floater; 1.6 match colour (board-1 scheduled;
   CD = White-matches − Black-matches); 1.7 Type A (simple: CD beyond ±1 or
   CD 0/∓1 with last-two same → preference; else none) and Type B (strong on same
   triggers; mild on CD ∓1 or CD-0 non-last-round last-game same-side; none if
   unplayed or CD-0 last round); Art.2 criteria C1–C10 (C1/C2 absolute; C3
   completion; C4 minimise upfloaters; C5 gaps; C6 next-bracket; C7 non-last-two
   float-repeat; C8 ungranted preferences; C9 Type-B strong; C10 non-last-two
   opponents' float-repeat); 3.1 legal; 3.2 top-scoregroup; 3.3 4-step process;
   3.4 PAB (completion → lowest score → most matches → largest TPN);
   3.5 upfloater sets (same lexicographic machinery + worked example as Double);
   3.6 pairing identifiers (same scheme + worked example); Art.4 colours
   (first-team = higher primary → secondary unless dropped → smaller TPN;
   unplayed-odd initial-colour; sole → opposite → Type-B-strong → lower CD →
   alternate → first-team preference/alternation → other alternation).
4. Retrieval: Council PDF. Evidence: FULL_TEXT. Extracted: `../extracted/TEAM_2026_RULES.md`.
5. Unresolved: none. Cross-checks: Mastering TPS 2026 (TEC) explains same C4–C10.
6. Implementation: new `team-2026` ruleset + additive team domain model
   (team entity, match/game points, board-1 colours). Line-ups/board orders are
   management-side (OUT — engine pairs teams, assigns match colours only).
