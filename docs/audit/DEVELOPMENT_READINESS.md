# Development Readiness Gate (STAGE 4, §4.17 + §§4.1–4.12, 4.16)

## 1. Hostile consistency audit (§4.1) — contradictions found

- **C-A (repeat-bye tension)**: Stage-1 validator treats repeat PAB as
  WARNING/INFO (GEN-03) while 2026 C2 makes a second PAB mandatory-forbidden.
  Disposition: ruleset-dated resolution required (till-2026 vs 2026 semantics +
  all-bye'd-field exception); recorded in OPEN_QUESTIONS, validator severity
  must become ruleset-dependent. Genuine catch — blocking for Dutch-2026 work,
  not for foundation.
- **C-B (first-wins vs optimisation)**: Stage-1 completeness proof (first-legal
  is solution-complete) coexists with Stage-3's criteria-optimisation goal.
  Disposition: no contradiction — completeness ≠ optimality; both documented.
- **C-C (compat harness vs 2026 rewrite)**: pinning v0.1.0 behaviour while
  pursuing 2026 conformance. Disposition: resolved by dated rulesets
  (`dutch-till2026` compat id vs `dutch-2026` target) — by design, not conflict.
- **C-D (rating kept but inert)**: retained as manager-owned metadata with
  documented inertness + ranking-fingerprint in envelope. No conflict.
- No other terminology/requirement/architecture/licence/roadmap contradictions
  found across the 44 documents.

## 2. Traceability matrix (§4.2; Requirement → Source → Decision → Future Test)

| Requirement | Source | Design decision | Future test |
|---|---|---|---|
| F-DUTCH-01/02 | C.04.3-2026 (S) + engine audit | D16 criteria engine; D13 RulesetId | conformance fixtures + BBP differential |
| F-LOCK-01 | v0.1.0 locks + JaVaFo XXP (P) | D11 scope; ConstraintSet | lock/forbid e2e suite |
| F-RR-01 | C.05 Berger (P) | taxonomy separate module | Handbook-table equality |
| F-SWISS-01 | C.04.4.x (P) | D10 strategy D; per-system modules | per-system oracle suites |
| C-ABS-01/C-DET-01/C-REP-01 | Stage-1 probes + JaVaFo repro model (P) | envelope + replay | property + determinism + replay suites |
| A-API-01/A-SEM-01/A-COMP-01 | v0.1.0 compat analysis | tiers + 5 versions + goldens | API-compat + golden suites |
| R-ERR-01/R-EXT-01 | BBP codes 0–5 (P) + engine audit | D14 taxonomy; supervised adapters | failure-test suite |
| P-SCALE-01 | vendor scale claims (P) + complexity notes | measure-first budgets | benchmark suite |
| S-IN-01/O-DIAG-01 | silent-absorption findings | D15 strict boundary; diagnostics | adversarial-input + diagnostics suites |
| T-STRAT-01/D-SPEC-01 | mission + VCL model (P) | 12 suites; living spec | CI + release audit |
| L-MIT-01 | licence research + JaVaFo terms (P) | O06 proposal; D17/D18 rejections | licence CI check |
| R-CAP-01 (Stage-4-derived) | missing-hunt §4.3: no cancellation path | native timeout/step budget, typed | timeout/cancel tests |

## 3. Missing-hunt, impossible states, external failures, capability, determinism (§§4.3–4.7)

- Player states (newcomer/provisional/missing/withdrawn/late/unavailable):
  covered by eligibility flags + manager seam; pairing-number policy stays
  manager-owned (documented).
- Data integrity: covered by S-IN-01 suite (duplicates, dup numbering, bad
  scores/colours/histories, asymmetry with warning+rule).
- Impossible states: typed error + blocking evidence + tried-scope record;
  default NO partials (O02). FIDE "arbiter decides" → report, human decides.
- External failures: unavailable/crash/timeout/non-zero-exit/malformed/
  unsupported-capability/version-mismatch → typed errors with raw capture.
- Capability model: registry answers system/ruleset/version/bye/colour-via-
  ruleset/constraints/seed/team/RR/TRF — complete per ENGINE_ABSTRACTION.
- Determinism months-later: envelope + pins; caveat recorded (float-equality
  caller hygiene; build-coupled external seeds disclosed).

## 4. OSS / performance readiness (§§4.9–4.10)

OSS checklist (LICENSE/CONTRIBUTING/CoC/SECURITY/templates/testing/release/
changelog/semver/dep-policy/attribution): all NOT SATISFIED — correctly
scheduled in roadmap phases 1+9, not pretended. Performance: scenarios defined
(10/20/50/100/250/500/1000 + pathological), no optimisation now, budgets TBD.

## 5. Anti-overengineering (§4.11)

Required now: errors, validation, tiers, versioning, harness (foundation).
Clearly later: registry/adapters/TRF (strategy D needs them), criteria engine
(2026 needs it). Speculative, cut/deferred: team domain, KO orchestration,
tie-break engine, match model beyond Double. Verdict: no unnecessary complexity
adopted; deferrals explicit.

## 6. Why-not-just-BBP/JaVaFo (§4.12)

Reuse as oracles/adapters (BBP: licence-clean, CLI-stable; JaVaFo: reference,
BYO-binary). Don't rebuild on them: language/toolchain barriers, no library
API, BBP Burstein flawed, JaVaFo licence/JVM/build-coupling, TRF-only
constraints, no custom-constraint embedding. Native justified for control,
portability, chess-manager embedding; oracles justify confidence. No
implementation either way.

## 7. Completeness matrix (§4.16)

| Area | Complete? | Evidence | Missing | Blocking? |
|---|---|---|---|---|
| Repository | YES | Stage-1 audit + gate | — | no |
| Public API | YES | mapped + tiered (proposal) | owner tiering O08 | no |
| Domain | YES | audit + spec model | — | no |
| Native engine | YES | trace + 1.6 proofs | FIDE-order fidelity | no (foundation can start) |
| FIDE | PARTIAL | chapters + deltas; full 2026-Dutch text pending | article-level retrieval | for Dutch-2026 phase only |
| Dutch | PARTIAL | spec + 30 cases; order-fidelity open | BBP differential run | for conformance phase only |
| Other Swiss | SURVEYED | mechanics + status | Lim/C.04.6 detail | deferred phases |
| RR/Team/Other | SURVEYED/SPEC-SLICED | Berger tables; taxonomy | C.04.6 text | deferred phases |
| BBP/JaVaFo | YES | full README/AUM retrieval | JaVaFo redistribution terms | adapter bundling only |
| Ecosystem | YES | 8-candidate table | minor licence gaps | no |
| Architecture | YES (proposed) | evaluated hypothesis | owner adoption O01 | yes — decision before design |
| Testing | YES (strategy) | 12 suites + gates | implementation | phased |
| Reproducibility | YES (spec) | envelope + replay | implementation | phased |
| Compatibility | YES (policy) | tiers + versions + harness | owner windows O08 | no |
| Licensing | YES (strategy) | MIT + constraints | owner adoption O06 | before distribution changes |
| Security | YES (posture) | audit + boundary | TRF fuzz (phased) | no |
| Performance | SCENARIOS ONLY | no invented numbers | measurements | phased |
| Open source | CHECKLISTED | gaps scheduled | implementation | phased |
| FIDE endorsement | CLASSIFIED | readiness sheet | everything (late phase) | no (explicitly late) |

## 8. Gate verdict (§4.17): **READY FOR OWNER REVIEW**

Documentation is complete, internally consistent (one genuine tension found and
parked with a resolution path), requirements carry acceptance criteria,
compatibility/licensing/FIDE positions are understood — but owner decisions
O01–O08 remain. NOT "ready for development" (architecture unadopted by owner);
NOT "not ready" (no blocking information gap for review). No development starts.

## 9. Addendum — final architectural decisions recorded (no code changed)

O01–O10 are now FINAL owner direction (`docs/DECISIONS.md`): Strategy D,
no-partial-results, explicit fallback with metadata, JaVaFo BYO-binary,
tie-break boundary + tiebreak-core contract, MIT retention, refined 10-phase
roadmap (seam-in-Foundation, non-conformant-Dutch guard), permanent golden
harness + two-minor deprecation, timeout/cancellation bounds. Verification
against all prior docs found NO contradictions (refinements only: O03 envelope
fields, O07/O08 exactness). New requirements R-TIME-01/R-CANCEL-01/
R-FALLBACK-01/TB-IF-01 extend the traceability matrix above. Remaining opens
are retrieval debts + measurement-first values, none blocking Foundation.
**Recommended posture: READY FOR DEVELOPMENT OF FOUNDATION PHASE ONLY, subject
to explicit owner implementation approval** — Dutch-conformance and later
phases retain their own retrieval/measurement gates. Implementation has NOT started.
