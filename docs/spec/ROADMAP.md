# Roadmap (OWNER DECISION O07 — FINAL, authorisation of phases still required)

Ordered by chess-manager value → FIDE importance → dependencies → risk →
ecosystem value. Phase exit = acceptance criteria (ACCEPTANCE_CRITERIA.md).
STATUS markers record actual completion as of the capability wave
(main @ capability-wave HEAD; see FINAL_CAPABILITY_AND_PROFESSIONALIZATION_REPORT.md).

1. **Foundation** — DONE: typed errors, validation boundary, API tiers,
   versioning policy, licence file, determinism suite, v0.1.0 harness,
   timeout/cancellation, explicit engine configuration, harness skeleton.
   (Seam design with chess-manager still pending integration phase.)
2. **Dutch production/conformance** — PARTIAL: `dutch-till2026-compat` pinned
   + hardened (C9 bye ordering, forbidden pairs, budgets, bounded search);
   BBP/JaVaFo oracle differentials live; TRF interchange; validator as
   checker-mode. NOT DONE: `dutch-2026` criteria engine (blocked: no PRIMARY
   article text), played-only/win-PAB/C2/topscorer deltas (need same text).
   **Guard holds: non-conformant Dutch is NEVER promoted to production
   to satisfy schedule.**
3. **chess-manager integration** — NOT STARTED (explicitly out of scope).
4. **Additional Swiss** — Dubov/Burstein/Lim BLOCKED (insufficient PRIMARY
   text, no oracles); Double Swiss RESEARCHED+ (closest candidate).
5. **Round robin** — DONE (Berger single/double, validated vs C.05 Annex 1).
6. **Team systems** — Olympiad-rules path RESEARCHED+ (needs full articles
   3–6); C.04.6 TPS still excerpt-only. NOT implemented.
7. **Knockout/match/playoffs** — RESEARCHED only (no single authoritative
   pairing text; no requesting use case). NOT implemented.
8. **Scale/performance** — DONE (baselines 50–1000 + pathological; two
   measured bounding fixes; budgets explicit).
9. **Open-source maturity** — PARTIAL (LICENSE, CHANGELOG, API stability via
   harness; templates/docs-site/SBOM still open).
10. **Endorsement preparation** — NOT STARTED (correctly late; readiness
    sheet maintained).
