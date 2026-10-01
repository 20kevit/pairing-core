# Testing Strategy (STAGE 3 SPEC — PROPOSED)

Rule: every discovered bug becomes a regression test; every FIDE claim gets an
oracle anchor. Suites (all PROPOSED, phased by ROADMAP.md):

1. **Unit**: colour/float derivation tables (incl. `-` streak-breaks, UU/DD
   edges), bracket splits, exchange enumeration order, bye ordering, error
   constructors. Fast, no I/O.
2. **Integration**: engine+validator agreement on every output (validator runs
   in-test, not in-engine); locks/forbidden pairs end-to-end; roll-forward
   round-trips.
3. **Golden**: v0.1.0 behaviour snapshots (round-1 shapes, bye-last boards)
   frozen as the compatibility harness; JaVaFo/BBP sample TRFs (AUM/TRFX
   samples, BBP test dir) as external goldens with pinned versions.
4. **FIDE conformance**: criteria-level fixtures (Stage-2 adversarial B/F/C/R/Y
   sets encoded as data); checker-mode cross-validation (our validator vs
   JaVaFo `-c`/BBP `-c` on shared TRFs).
5. **Cross-engine differential**: seeded corpora (RTG-style generator owned by
   repo; BBP `-s`/JaVaFo seed for external mass) comparing native vs BBP
   (Dutch-2025 scope) then native vs JaVaFo; mismatches triaged as
   rule-gap/oracle-bug/spec-gap with labels. Engines are NEVER assumed
   byte-identical: every comparison is classified into exactly one of —
   exact-equivalent / rule-equivalent-but-reordered / valid-alternative /
   genuine-rule-violation / implementation-specific / unsupported-feature /
   oracle-disagreement-requiring-investigation — with normalization rules
   (board-order-insensitive, colour-orientation-aware) fixed per comparison
   profile. Disagreements open investigation records; regression storage keeps
   corpus + both outputs + engine pins + triage label.
6. **Property-based**: absolute bars hold over generated tournaments
   (no-rematch, colour limits, float caps, exactly-≤1-bye, completeness);
   determinism over input permutation; id-typed (hypothesis-style; library TBD
   without adding hard deps — PROPOSED dev-dependency).
7. **Randomized deterministic**: fixed-seed fuzz of states incl. pathological
   densities (Stage-1 differential shape promoted to CI).
8. **Regression**: one test per bug + per endorsement-style discrepancy.
9. **Performance**: 10/20/50/100/250/500/1000 scenarios + pathological
   single-bracket + dense-rematch states; budgets recorded, never invented;
   step/time caps asserted (bounded failure, no hangs).
10. **Failure tests**: impossible states (I-set), malformed TRF, missing
    binary, timeout, crash, version mismatch — each mapped to its typed error.
11. **Serialization**: TRF round-trip + version-dialect matrix (TRF16/26/x).
12. **API compatibility**: public-surface snapshot + behavioural goldens per
    release; deprecation-window enforcement tests.
