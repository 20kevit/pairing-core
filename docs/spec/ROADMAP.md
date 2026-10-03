# Roadmap (OWNER DECISION O07 — FINAL, authorisation of phases still required)

Ordered by chess-manager value → FIDE importance → dependencies → risk →
ecosystem value. Phase exit = acceptance criteria (ACCEPTANCE_CRITERIA.md).
STATUS markers record actual completion as of v0.4.0 (2026-10-03);
the capability-wave notes below are preserved as history.

1. **Foundation** — DONE: typed errors, validation boundary, API tiers,
   versioning policy, licence file, determinism suite, v0.1.0 harness,
   timeout/cancellation, explicit engine configuration, harness skeleton.
   (Seam design with chess-manager still pending integration phase.)
2. **Dutch production/conformance** — DONE (v0.3.x–0.4.0): `dutch-2026`
   criteria engine (C1–C21) implemented from FULL_TEXT evidence, hostile-audit
   defects fixed, closure interpretations pinned; `dutch-till2026-compat`
   stays pinned + hardened (C9 bye ordering, forbidden pairs, budgets,
   bounded search); BBP/JaVaFo oracle differentials live; TRF interchange;
   validator as checker-mode.
   **Guard holds: non-conformant Dutch is NEVER promoted to production
   to satisfy schedule.** (Pre-0.3.0 note, preserved: this phase was once
   PARTIAL, blocked on PRIMARY article text — resolved by the Council-bundle
   retrieval.)
3. **chess-manager integration** — NOT STARTED (explicitly out of scope).
4. **Additional Swiss** — DONE (v0.3.x–0.4.0): Dubov, Burstein, Lim
   implemented from FULL_TEXT evidence with audit + closure fixes
   (known limitations L3/L4/I-L-412 disclosed).
   Double Swiss RESEARCHED+ note (pre-0.3.0, preserved): was closest
   candidate — now implemented as `double-2026`.
5. **Round robin** — DONE (Berger single/double, validated vs C.05 Annex 1).
6. **Team systems** — DONE (v0.3.x–0.4.0): `team-2026` + `olympiad-2022`
   implemented (Olympiad rewritten from retrieved chapter text in 0.4.0;
   limitation L5 disclosed). (Pre-0.3.0 note, preserved: Olympiad-rules path
   was RESEARCHED+, C.04.6 TPS excerpt-only.)
7. **Knockout/match/playoffs** — RESEARCHED only (no single authoritative
   pairing text; no requesting use case). NOT implemented.
8. **Scale/performance** — DONE (baselines 50–1000 + pathological; two
   measured bounding fixes; budgets explicit).
9. **Open-source maturity** — PARTIAL (LICENSE, CHANGELOG, API stability via
   harness; templates/docs-site/SBOM still open).
10. **Endorsement preparation** — NOT STARTED (correctly late; readiness
    sheet maintained).
