# Evidence — Dubov 2026 (C.04.4.1)

1. Source ID: F-0108. Handbook: https://handbook.fide.com/chapter/C040401202602.
2. Approval 28/10/2025 (CM3-202517); effective 01/02/2026. Supersedes F-0109.
3. Sections (all read in full, Council bundle): Preface (ARO equalisation goal);
   1.1 ratings mandatory (provisional by Chief Arbiter); 1.2 TPN + pre-round-4
   recalculation; 1.3 brackets = residents + lower upfloaters (NO downfloaters);
   1.4 PAB; 1.5 colour difference; 1.6 preferences (zero-game = mild Black);
   1.7 ARO (played games only, mean, round half-up, zero if unplayed);
   1.8 maximum upfloater MaxT = 2 + floor(Rnds/5); 1.9 outlook (PAB first, then
   top-down; C1–C3 absolute); Art.2 criteria C1–C10 (C5 minimise upfloaters;
   C6 upfloater score gaps; C7 colours; C8–C10 non-last-round max-upfloat guards);
   3.1 PAB order (eligible → completion → lowest score → most games → largest TPN);
   3.2 bracket (min upfloaters; best set; G1 White-seekers/top-half; shifters;
   ARO-then-TPN S1; first legal T2 pairing); Art.4 sorting (sequence numbers,
   upfloater/shifter/G2 orders; middle-outward shifter example A–G);
   Art.5 colours (unplayed-odd-HRP initial-colour; both → stronger → alternate →
   higher-ranked). Nota bene: Art.4.4.1 cites "Article 2.2.4" (official-text
   cross-reference slip; clearly means 3.2.4).
4. Retrieval: same Council PDF as Dutch (curl+pdftotext). Evidence: FULL_TEXT.
5. Extracted: `../extracted/DUBOV_2026_RULES.md`. Unresolved: none.
6. Cross-checks: pre-2026 Dubov full text in interim-refs PDF (2024_1FC,
   "no downfloaters" note already present); spp mirror search-cache consistent.
7. Conflicts: none. BBP has no Dubov (not applicable).
8. Implementation: new `dubov-2026` ruleset (rating input required; MaxT;
   ARO ordering; G1/G2 machinery). Ratings mandatory per 1.1.1 — typed input gap
   if missing (Chief Arbiter assigns provisional: caller-side duty).
