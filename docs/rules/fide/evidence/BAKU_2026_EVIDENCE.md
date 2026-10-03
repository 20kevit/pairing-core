# Evidence — Baku / Accelerated 2026 (C.04.7)

1. Source ID: F-0117. Handbook: https://handbook.fide.com/chapter/C0407202602.
2. Approval 28/10/2025 (CM3-202517); effective 01/02/2026. Supersedes F-0118.
3. Sections (all read in full): Preface (acceleration = score-bracket
   rearrangement via virtual points; statistical-proof admission standard; Baku
   first; applicable to any Swiss system unless stated); 1.1 premise (win = two
   draws, loss = zero — generalised beyond 1-½-0); 1.2 GA/GB split (GA = first
   half rounded up to even; 161→82 worked note; 2·ceil(N/4) formula);
   1.3 late entries (C.04.2 Art.2 slotting; GA-boundary player frozen; GA may go
   odd); 1.4 virtual points (accelerated rounds = first ceil(half) of tournament;
   GA gets win-value for first half of those (rounded up), halved after; GB and
   post-acceleration get none; worked 9-round individual + 11-round team MP
   examples; gamepoint-primary exclusion note); 1.5 pairing score = standings +
   virtual (also drives board order per C.04.2 Art.3.6).
4. Retrieval: Council PDF. Evidence: FULL_TEXT. Extracted: `../extracted/BAKU_2026_RULES.md`.
5. Unresolved: none. Cross-checks: SPP Baku page snippets match; Milvang
   acceleration analysis (S-0107) is context only.
6. Implementation: pure additive `baku` modifier (GA/GB split + virtual-point
   schedule → pairing-score mapping). No 1-½-0 hardcoding (premise is the
   win=2·draw relation). Other accelerated methods: none admitted in 2026 text —
   UNKNOWN, not invented.
