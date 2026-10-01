# Open Questions (FINAL — only genuinely unresolved items)

O01–O10 are DECIDED (see `docs/DECISIONS.md`). Remaining items need retrieval,
measurement, or later-phase decisions — none blocks Foundation.

- **FIDE/algorithm retrieval**: repeat-bye semantics across rulesets (GEN-03 vs
  C2 tension); full 2026-Dutch article text; C.04.6 team text; Lim detail;
  FIDE-order fidelity among multiple legal pairings (needs BBP differential).
- **Engine**: BBP version pin for oracle baseline; JaVaFo clearance IF bundling
  ever reconsidered (BYO-binary is the decided posture).
- **API/compatibility**: `SwissEngine` public-vs-internal tiering (detail under
  decided O08 policy); diagnostics verbosity contract.
- **Testing**: oracle-mass storage (repo corpora vs external downloads);
  property-test dev-dependency choice.
- **Performance**: benchmark budgets (measure-first); native wall-clock default
  budget value (measure-first; step budget primary).
