# Evidence — Lim 2026 (C.04.4.3)

1. Source ID: F-0112. Handbook: https://handbook.fide.com/chapter/C040403202602.
2. Headers: GA 1987 approval + 1988/1989/1997/1998 amendments + 1999 EB;
   Council 28/10/2025; effective 01/02/2026. Supersedes F-0113.
3. Sections (all read in full): 1. PAB = lowest rank in lowest scoregroup;
   2.1 compatibility (unplayed + no 3-in-row + no ±3 imbalance); 2.2 median
   scoregroup (score = half rounds played); top-down to pre-median, bottom-up to
   median, median last (paired downward); 2.3 floater triggers (exhausted / ±2
   colour no-fix / 2× colour no-alternate / odd numbers); 2.4 top-half vs
   bottom-half proposed pairings 1v(n/2+1)…; 2.5 exchanges; 2.6 blocked-median
   cracking (float-heavier side decides which neighbour pairing cracks);
   Art.3 floater selection (direction, even-making colour balance, Maxi-100pt
   guard, 3.2.4 number rule, 3.3/3.4 compatible-opponent choice with rival-opponent
   exclusion, 3.5 swap-or-float-further, 3.6/3.7 pairing order DF-first above /
   UF-first below, 3.8 alternate-colour partner + Maxi guard, 3.9 a–d hierarchy,
   3.10 no re-float for even-making); Art.4 exchanges (scrutiny order, worked
   6-player tables, 4.4 float-on-failure incl. #7-swap rule); Art.5 colours
   (alternate/equalise, hard bans 5.1.1/5.1.2, double scrutiny, 5.3 2× rule,
   5.4 history walkback + median-split rank rule, 5.5/5.6 odd/even rounds,
   Maxi guard); Art.6 last-round same-score priority over colours (even at 3×/±3
   cost); Art.7 round-1 recipe (lowest-rated PAB; lot colour; 40-player tables);
   Art.8 round-2 (1pt → 0pt → 0.5pt median order).
4. Retrieval: Council PDF (curl+pdftotext). Evidence: FULL_TEXT.
5. Extracted: `../extracted/LIM_2026_RULES.md`. Unresolved: none at text level.
   (Prior "thinnest area" assessment retired — full text recovered.)
6. Cross-checks: spp mirror + old.fide.com?id=168 search-cache match bundle text
   essentially verbatim (G-04 closed for Lim).
7. Implementation: new `lim-2026` ruleset (procedural engine; Maxi-100pt guard =
   optional tournament parameter, default off; standard 1/½/0 assumed per 7.3).
