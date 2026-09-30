# Acceptance Criteria (STAGE 3 SPEC — PROPOSED)

Phase-exit gates (each must hold before the next phase starts; verified by the
suites in TESTING_STRATEGY.md):

- **Foundation**: strict validation rejects the adversarial-input suite with
  typed errors; API tiers documented + snapshot-tested; determinism suite
  green incl. permutation cases; v0.1.0 goldens green; LICENCE + SPDX present;
  zero new runtime deps.
- **Dutch conformance**: named-ruleset calls; BBP differential on seeded
  corpus with zero *unexplained* mismatches (each mismatch triaged
  rule-gap/oracle-bug/spec-gap); checker-mode agreement with BBP `-c` on
  shared TRFs; 2026-delta fixtures green; performance smoke at 100 players.
- **Integration**: chess-manager seam contracts tested both sides; replay
  envelopes round-trip; error→UX mapping reviewed by manager owner.
- **New systems (each)**: ruleset slice spec + oracle/goldens + capability
  declaration; no regression in prior systems' corpora.
- **Round robin**: Handbook-table equality 3–16 + double-cycle rule tests.
- **Team**: spec unblocked (C.04.6 retrieved) + domain review + goldens.
- **Knockout/match**: generator determinism + Double match-result model tests.
- **Scale**: budgets published from measurement; pathological cases bounded
  (typed failure, no hang) at 500/1000 scenarios.
- **Maturity**: OSS checklist (Stage 4 §4.9) complete; API stability declared.
- **Endorsement prep**: FPC/RTG-equivalent artefacts runnable by third parties;
  self-VCL green; candidacy dossier reviewed (still no public claim).
