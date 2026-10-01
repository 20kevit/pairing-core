# Roadmap (OWNER DECISION O07 — FINAL, authorisation of phases still required)

Ordered by chess-manager value → FIDE importance → dependencies → risk →
ecosystem value. Phase exit = acceptance criteria (ACCEPTANCE_CRITERIA.md).

1. **Foundation**: typed errors, input-validation boundary, explicit API tiers,
   versioning/changelog/release policy, licence hygiene, determinism suite,
   v0.1.0 compat harness, **integration-seam design + seam tests with
   chess-manager** (so architectural mismatches surface early, not in Phase 3),
   timeout/cancellation + explicit engine configuration + harness skeleton.
   (Unblocks everything; de-risks silently-absorbed input.)
2. **Dutch production/conformance**: dated rulesets (`dutch-till2026` pinned to
   current behaviour + `dutch-2026` criteria work), played-only colours,
   win-PAB config, C2-forfeit exclusion, topscorer handling, TRF-2026 subset,
   BBP oracle differential + first adapter (BYO binary), validator as
   checker-mode. (chess-manager integration target.) **Guard: non-conformant
   Dutch is NEVER promoted to production to satisfy schedule.**
3. **chess-manager integration**: seam contracts, roll-forward helper, error→UX
   mapping, replay envelopes, migration off embedded pairing.
4. **Additional Swiss**: Dubov → Burstein → Lim (each: spec slice, oracle,
   goldens). Blocked on Lim/C.04.6 retrieval where noted.
5. **Round robin**: Berger single/double (cheap, high club value).
6. **Team systems**: domain layer + Team Swiss (blocked on C.04.6 text).
7. **Knockout/match/playoffs**: bracket generator + Double-Swiss match results.
8. **Scale/performance**: benchmark budgets, pathological-case hardening,
   cap tuning with evidence.
9. **Open-source maturity**: contributing/security/issue templates, docs site,
   SBOM, API stability declaration.
10. **Endorsement preparation**: FPC/RTG-equivalent artefacts, VCL-style
    self-checklist, version-pinned candidacy (FIDE_ENDORSEMENT_READINESS.md).
    No claim before certificate.
