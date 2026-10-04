# Open Questions (v0.4.1 — only genuinely unresolved items)

O01–O10 are DECIDED (see `docs/DECISIONS.md`). The 2026 retrieval questions
from earlier revisions are RESOLVED (FULL_TEXT Council bundle retrieved,
extracted, implemented, audited — see `docs/rules/fide/SOURCE_MANIFEST.md`
and `docs/audit/FIDE_CONFORMANCE_MATRIX.md`). Remaining items need
measurement or later-phase decisions — none blocks the current product.

- **Frozen compat deviations**: E.5 round-1 parity colours vs pinned S1-white,
  and the absolute 3rd-float bar (live BBP + source evidence against the bar;
  see `docs/research/DUTCH_CONFORMANCE_STATUS.md`). Both CONFIRMED, both
  FROZEN per O08 — any alignment belongs to a new dated ruleset with golden
  migration, by owner decision. Open only in the sense of "not yet decided".
- **I-L-412 genuine ambiguity**: Lim upward-search shape (mirror adopted by
  symmetry, deterministic default, no caller flag). Documented in the
  conformance matrix; removable only by future FIDE text or owner ruling.
- **L1/L3/L4 execution-vs-exactness boundary**: exact-search ceilings (L1),
  Double/Team full-C3 lookahead policy (L3), Lim 4.2 interleaving exactness
  (L4). Current policy (typed errors, no heuristic pruning) is DERIVED and
  documented (`docs/audit/SEARCH_CEILING_POLICY.md`); lifting any of them is
  future owner-funded work, not a defect.
- **Bye policy variant**: repeat-PAB resolved analytically (disruptions-only);
  strict-FIDE vs completion-tolerant variant naming deferred to future
  ruleset work.
- **Engine**: JaVaFo clearance IF bundling ever reconsidered (BYO-binary is
  the decided posture). JaVaFo LIVE-VERIFIED (Rel. 2.2 Build 3223, Dutch-2017
  vintage per 092 tag; JVM + jar BYO in test env only, never vendored).
  BBP oracle pin DONE (8f9e3c5 source build; live runs via BBP_EXE).
- **Testing**: oracle-mass storage (repo corpora vs external downloads);
  property-test dev-dependency choice (currently stdlib-only, no dependency).
- **Performance**: native wall-clock default budget value (measure-first;
  step budget primary; baselines recorded in `tests/data/benchmarks/`).
