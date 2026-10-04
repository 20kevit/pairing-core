# pairing-core — Master Specification (product entry map; v0.4.1)

> Authority note: this document maps the product and points to authorities;
> it is not itself the conformance record. Current capability authority is
> `docs/CAPABILITY.md`; conformance authority is
> `docs/audit/FIDE_CONFORMANCE_MATRIX.md` (+ closure report); ruleset
> catalog is `docs/rules/fide/CURRENT_SYSTEM_CATALOG.md`. Stage-1/2/3
> historical detail lives in `docs/audit/`, `docs/research/`, `docs/spec/`.

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

## 4. Current state (v0.4.1; unchanged behaviorally since v0.4.0)

Deterministic, zero-runtime-dependency pairing library: frozen
`dutch-till2026-compat` Dutch kernel (41 goldens pin behavior) + seven
implemented 2026-family rulesets (`dutch-2026`, `dubov-2026`,
`burstein-2026`, `lim-2026`, `double-2026`, `team-2026`, `olympiad-2022`,
`baku` modifier, all from FULL_TEXT evidence) + validated Berger
round-robin + TRF interchange + BYO BBP/JaVaFo adapters + typed errors,
validation boundary, budgets/cancellation, envelopes, provider/registry,
canonical consumer contract. Full audit trail: `docs/audit/`. Known
limitations L1/L3/L4/L5 + I-L-412 disclosed in the closure report §L.

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

Frozen `dutch-till2026-compat` kernel + the seven 2026-family rulesets
(Dutch criteria C1–C21, Dubov, Burstein, Lim, Double, Team, Olympiad) +
Baku modifier + Berger round robin (validated, standalone module).
Explicitly OUT of scope: KO/match/playoff orchestration, tiebreak-core,
tournament-core, ratings, REST API, UI, persistence (see
`docs/spec/TOURNAMENT_BOUNDARIES.md`). Per-system evidence:
`docs/rules/fide/CURRENT_SYSTEM_CATALOG.md`; conformance standing + explicit
interpretations: `docs/audit/FIDE_CONFORMANCE_MATRIX.md` (no FIDE
endorsement claimed).

## 11. Future systems

None currently scoped: the C.04 family sweep is complete (see the catalog
above). Any future system (e.g. new FIDE text ⇒ new dated ruleset id) is
gated by spec slice + oracle + goldens per ACCEPTANCE_CRITERIA.md and the
O08 compat policy — never a silent kernel change.

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
implementation-specific / unsupported / oracle-disagreement). LIVE STATUS:
BBP 8f9e3c5 source build runs green in-harness (round-1 pair-sets agree;
systematic valid-alternative divergence characterized; E.5 + float-bar
deviations confirmed with evidence, frozen per O08 pending dated-ruleset
migration).

## 15. Reproducibility

Replay envelope (input digest, ruleset, engine versions, constraints, seed,
numbering fingerprint) + `replay()` equality.

## 16. Compatibility

v0.1.0 permanent behavioural goldens; semver + 5 independent versions;
two-minor deprecation window (O08); API tiers; no partial results (O02).

## 17. Performance

Measure-first; scenarios 10→1000 + pathological; bounded typed failure, no
hangs; first baselines recorded in tests/data/benchmarks/baseline.json
(W7); budgets published from data, none invented.

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
