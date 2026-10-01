# pairing-core — Master Specification (STAGE 4, §4.15; single entry point)

## 1. Vision

Two goals: (1) solve chess-manager's pairing needs with a versioned,
deterministic Python library; (2) grow into a professional open-source pairing
library — FIDE-rule-correct, reproducible, highly tested, endorsement-capable.
Never claim endorsement before a certificate exists.

## 2. Scope

One round/match at a time: who-plays-whom, boards, colours, bye/float metadata,
validation, diagnostics, reproducibility — under a named, dated ruleset.
Dutch first (2026 alignment), then Dubov/Burstein/Lim, RR, Double, Team.

## 3. Non-goals

Tournament management (registration, money, accounts, notifications, UI,
publishing, admin), REST APIs, databases, ratings, tie-break engines,
scheduling, arbiter judgment. See `docs/spec/TOURNAMENT_BOUNDARIES.md`.

## 4. Current state (v0.1.0, SHA 2cb570b)

Zero-dependency Dutch-kernel library: deterministic bracket search with
rematch/absolute-colour/absolute-float legality, fresh-first byes, locked
pairs, independent validator. Gaps: no input validation, ValueError-only
errors, rating inert, silent legacy filtering, 15 basic tests, no TRF/CLI/
benchmarks, pre-2026 formulation. Full audit: `docs/audit/`.

## 5. Target state

Multi-system engine family behind one provider interface, native kernels +
bring-your-own-binary BBP/JaVaFo adapters, TRF interchange, standing
conformance harness, typed errors, replay envelopes. Spec: `docs/spec/`.

## 6. Requirements

ID catalog in `docs/spec/PRODUCT_REQUIREMENTS.md` (+ non-functionals);
traceability matrix in `docs/audit/DEVELOPMENT_READINESS.md`.

## 7. Domain

PlayerState (histories as played-only lists, bye/float ledgers, eligibility),
Pairing/RoundPairing (+ envelope/diagnostics split), RulesetId, ConstraintSet,
pure roll-forward helper. See `docs/spec/DOMAIN_MODEL.md`.

## 8. Architecture

Domain → provider interface + registry → native / external adapters; validation
sidecar; reproducibility envelope; core stdlib-only; bounded execution
(step budget + wall-clock timeout, O10); explicit engine configuration, never
silent fallback (O03). See `docs/spec/ARCHITECTURE.md`.

## 9. Engine abstraction

Identity/versions/capabilities, `pair(request)`, determinism contract,
supervised-subprocess failure mapping, conformance obligations per engine.

## 10. Supported systems

Dutch (target: 2026 criteria; compat: pre-2026 kernel pinned). Explicitly NOT
yet: Dubov, Burstein, Lim, Double, Team, RR (roadmap phases with gates).

## 11. Future systems

Dubov → Burstein → Lim → RR → Team → KO/match per `docs/spec/ROADMAP.md`;
each gated by spec slice + oracle + goldens (ACCEPTANCE_CRITERIA.md).

## 12. FIDE requirements

System + effective date on every call; C1/C2 absolutes; 2026 deltas
(played-only colours, win-PAB, forfeit exclusion, topscorers, C1–C21 framing);
research: `docs/research/` (sources register included).

## 13. Testing

12 suites: unit → goldens → conformance → cross-engine differential (seeded
corpora) → property/randomized → regression → performance → failure → TRF →
API-compat. Every bug becomes a regression test.

## 14. Conformance

BBP first oracle (Dutch-2025 scope), JaVaFo second; checker-mode agreement;
mismatch triage discipline (rule-gap/oracle-bug/spec-gap); 7-class comparison
taxonomy (exact / reordered-equivalent / valid-alternative / violation /
implementation-specific / unsupported / oracle-disagreement).

## 15. Reproducibility

Replay envelope (input digest, ruleset, engine versions, constraints, seed,
numbering fingerprint) + `replay()` equality.

## 16. Compatibility

v0.1.0 permanent behavioural goldens; semver + 5 independent versions;
two-minor deprecation window (O08); API tiers; no partial results (O02).

## 17. Performance

Measure-first; scenarios 10→1000 + pathological; bounded typed failure, no
hangs; budgets published from data, none invented.

## 18. Security

Pure-library posture; strict input boundary; isolated adapters; linear TRF
grammar + fuzz; bounded execution; no secrets/surface by design.

## 18b. Tie-break architecture (O05/O09)

General tie-break calculation is OUT (future independent tiebreak-core:
`docs/spec/TIEBREAK_ARCHITECTURE.md`); pairing consumes only narrow
ranking/index inputs where formal rules require (Burstein); one-way
dependency; no tournament-core.

## 19. Licensing

MIT retained (PROPOSED); Apache-2.0 NOTICE hygiene if vendored; no in-process
GPL; JaVaFo bring-your-own-binary + attribution, no bundling.

## 20. Roadmap

10 phases, foundation → Dutch conformance → integration → systems → maturity →
endorsement prep. Proposal, not authorisation.

## 21. Decisions

`docs/DECISIONS.md` — O01–O10 FINAL owner direction (strategy D, no partials,
explicit fallback, JaVaFo BYO, tie-break boundary, MIT, roadmap, compat,
tiebreak-core, timeout); D17–D19 rejections stand.

## 22. Open questions

`docs/OPEN_QUESTIONS.md` — only genuinely unresolved items (retrieval debts,
oracle pin, tiering detail, budgets); O01–O10 decided.

## 23. Documentation map

`docs/audit/` (Stage 1 + readiness + final report), `docs/research/`
(Stage 2, 13 docs), `docs/spec/` (19 docs: Stage 3 suite + endorsement readiness + tiebreak
architecture + foundation blueprint),
root: MASTER_SPECIFICATION, DECISIONS, OPEN_QUESTIONS.
