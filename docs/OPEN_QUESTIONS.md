# Open Questions (FINAL — only genuinely unresolved items)

O01–O10 are DECIDED (see `docs/DECISIONS.md`). Remaining items need retrieval,
measurement, or later-phase decisions — none blocks Foundation.

- **FIDE/algorithm retrieval**: repeat-bye semantics across rulesets (GEN-03 vs
  C2 tension); E.5 round-1 parity colours vs pinned S1-white (W6 finding —
  needs full article text, kernel unchanged); full 2026-Dutch article text;
  C.04.6 team text; Lim detail;
  FIDE-order fidelity among multiple legal pairings (needs BBP differential).
- **Engine**: BBP version pin for oracle baseline; JaVaFo clearance IF bundling
  ever reconsidered (BYO-binary is the decided posture).
- **API/compatibility**: `SwissEngine` public-vs-internal tiering (detail under
  decided O08 policy); diagnostics verbosity contract.
- **Testing**: oracle-mass storage (repo corpora vs external downloads);
  property-test dev-dependency choice.
- **Performance**: first baselines recorded (W7: 50–1000 realistic spreads +
  pathological brackets, see tests/data/benchmarks/baseline.json; round-1
  single-1000 bracket ≈97s — worst case, bounded); budget publication +
  native wall-clock default value still measure-first/open.
