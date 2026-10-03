# Evidence — Dutch 2026 (C.04.3)

1. Source ID: F-0105. Official document: FIDE Handbook C.04.3 FIDE (Dutch) System.
2. Official URL: https://handbook.fide.com/chapter/C0403202602 (body bot-protected;
   same normative text verified in F-0201 below).
3. Approval date: 28/10/2025 (3rd FIDE Council, CM3-202517). Effective: 01/02/2026.
4. Superseded: F-0107 (till-2026 A–E text) and F-0106 (interim 2025 text).
5. Exact sections: Art.1 (1.1 TPN, 1.2 order score→TPN, 1.3 scoregroups/brackets/
   remainder, 1.4 floats, 1.5 PAB, 1.6 colour difference, 1.7 preferences,
   1.8 topscorers >50% max at final pairing, 1.9 outlook); Art.2 criteria
   [C1]–[C21] (2.1 absolute, 2.2 completion C4, 2.3 PAB C5, 2.4 quality C6–C21);
   Art.3 bracket process (M0/MaxPairs/M1, S1/S2/Limbo, candidate, perfect,
   alterations 3.6/3.7, best-available 3.8); Art.4 sequential generation
   (BSN, S2 transpositions lexicographic, resident-exchange comparison rules,
   pairable-MDP sets, next-element); Art.5 colour allocation (5.1 lots,
   5.2.1–5.2.5 incl. E.5-successor parity rule at 5.2.5).
6. Retrieval: official Council PDF via curl + pdftotext (`cm3-202517.pdf`,
   SHA-256 `6b12df0e…4c94`, /tmp only, not vendored). Handbook HTML fetch fails
   (bot-protection); fide.com reminder F-0301 fetched full-page.
7. Evidence type: FULL_TEXT (normative Council bundle) + OFFICIAL_PDF.
8. Extracted rules: see `../extracted/DUTCH_2026_RULES.md` (C1–C21 verbatim-verified).
9. Unresolved: none at rule-text level. All articles read in full by the researcher.
10. Cross-checks: TEC Annotated Dutch V2026 (Rev. 2512151400, SHA `c0515191…`;
    2,184 lines) + Terms PDF + Mastering (72 pp) corroborate structure
    ([C1]–[C21], PPB/CLB removal, PAB-min-score, x/z colour math, C14–C21
    resident-vs-MDP split); handbook search-index excerpts match bundle text.
11. Conflicts: none. BBP implements 2025 Dutch (BBP README) — ruleset/version
    difference vs 2026 text; FIDE text wins where they differ.
12. Implementation consequences: new `dutch-2026` ruleset required (criteria-vector
    search + specified generation order); frozen `dutch-till2026-compat` untouched.
