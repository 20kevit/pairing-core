# Open Questions (FINAL — only genuinely unresolved items)

O01–O10 are DECIDED (see `docs/DECISIONS.md`). Remaining items need retrieval,
measurement, or later-phase decisions — none blocks Foundation.

- **FIDE/algorithm retrieval**: E.5 round-1 parity colours vs pinned S1-white
  (CONFIRMED deviation via live BBP + excerpt; correction needs dated-ruleset
  migration decision); full 2026-Dutch article text; C.04.6 team text; Lim
  detail; FIDE-order fidelity (live differential shows systematic
  valid-alternative divergence; needs 2026-criteria engine + oracle mass).
- **Float-bar alignment**: BBP-source + differential evidence against the
  absolute 3rd-float bar (see DUTCH_CONFORMANCE_STATUS.md §7); behavior
  frozen per O08 — alignment (if ever) belongs to a dated ruleset with
  golden migration, owner decision.
- **Bye policy variant**: repeat-PAB resolved analytically (disruptions-only;
  see §8); strict-FIDE vs completion-tolerant variant naming deferred to
  future ruleset work.
- **Engine**: JaVaFo clearance IF bundling ever reconsidered (BYO-binary is
  the decided posture). JaVaFo LIVE-VERIFIED (Rel. 2.2 Build 3223, Dutch-2017
  vintage per 092 tag; JVM + jar BYO in test env only, never vendored).
  BBP oracle pin DONE (8f9e3c5 source build; live runs via BBP_EXE).
- **API/compatibility**: `SwissEngine` public-vs-internal tiering (detail under
  decided O08 policy); diagnostics verbosity contract.
- **Testing**: oracle-mass storage (repo corpora vs external downloads);
  property-test dev-dependency choice.
- **Performance**: native wall-clock default budget value (measure-first;
  step budget primary; first baselines recorded).
