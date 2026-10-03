# Evidence — Burstein 2026 (C.04.4.2)

1. Source ID: F-0110. Handbook: https://handbook.fide.com/chapter/C040402202602.
2. Approval 28/10/2025 (CM3-202517); effective 01/02/2026. Supersedes F-0111.
3. Sections (all read in full): Preface (Index equalisation; Dutch seeding);
   1.1 TPN; 1.2 brackets (residents + incoming floaters); 1.3 PAB; 1.4/1.5 colours
   (zero-game = no preference); 1.6 seeding rounds = Dutch for first
   min(floor(R/2),4) rounds; 1.7 opposition evaluation (Buchholz = current
   opponent scores; SB = points × opponent current score; unplayed = self-game
   with registered result; zero-bye streaks = draws for opponents; virtual
   points excluded); 1.8 ranking = Index (Buchholz, then SB), then ascending TPN
   (scores NOT used); 1.9 outlook; Art.2 criteria C1–C8 (C5 max pairs; C6 minimise
   outgoing-floater scores descending; C7 next-bracket C1–C6; C8 colours);
   3.1 PAB (eligible → completion → lowest score → most games → lowest Art.1.8 rank);
   3.2 bracket (max pairs under C1–C5; first-best pairing in Art.4 order);
   Art.4 BSN + virtual zero-BSN padding + opponent-BSN-descending enumeration
   with worked 6-player/2-pair table; Art.5 colours (mirrors Dubov with Art.1.8 rank).
4. Retrieval: Council PDF (curl+pdftotext). Evidence: FULL_TEXT.
5. Extracted: `../extracted/BURSTEIN_2026_RULES.md`. Unresolved: none.
6. Cross-checks: pre-2026 Burstein full text in interim-refs PDF; spp snippets
   consistent. BBP Burstein self-declared flawed/non-endorsed — NEVER an oracle
   (recorded discrepancy: implementation defect, not ruleset difference).
7. Implementation: new `burstein-2026` ruleset (Index computation incl. self-game
   rule; seeding-round delegation to Dutch; BSN enumeration). No "median cracking"
   in 2026 text — that mechanism belongs to Lim 2.6 (prior misattribution corrected).
