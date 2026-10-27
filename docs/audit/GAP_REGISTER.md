# Pairing-Core authoritative audit gap register

- **Audit date:** 2026-10-27
- **Scope:** Pairing-Core as a pairing-only Python library; the published `v0.4.1` release is immutable.
- **Authority:** This file is the single current register of findings, their evidence, owners/boundaries, and closure status. Older audit reports, capability tables, changelog entries, and implementation comments are historical evidence, not current status unless this register explicitly adopts them.

## 1. Audit baseline and evidence discipline

| Item | Verified baseline |
|---|---|
| Checkout | `20kevit/pairing-core`, branch `arena/69b8f781-pairing-core`, baseline commit `8c5c1d233187ea90ed51585fdf733157d713cf38` |
| Release tag | Annotated tag object `ad9af7a2e13b75b9e2d8a4087809b83afadd595b`; peeled target is the baseline commit above. The local and remote tag targets agree. Do not move, recreate, or overwrite this tag or release. |
| Published artifacts | Wheel SHA-256 `9dec79c657357bef820ddd959541320e9d337b2ee32308411b004d75d4c6aa1a`; sdist SHA-256 `96ca52e1c41993c924ec842d86d6ecc99b5417d2bbdcb32a91ccd670dbf03dbe`. Both match the GitHub release API asset digests. |
| Baseline tests | `527 passed, 16 skipped` with Python 3.11.2 and pytest in an isolated `/tmp` virtual environment; skips are environment-gated. The first attempt with system Python was inconclusive because pytest was absent. |
| Latest listed CI | GitHub Actions run `37192287120` succeeded; the published workflow covered Python 3.10–3.12. |
| License / dependencies | Root `LICENSE` is MIT. The package declares no runtime dependencies; pytest is an optional test extra. A prior dependency audit incorrectly said there was no license file and described old packaging metadata. |
| Repository changes at audit start | None. The checkout was clean. |

Evidence grades used here:

- **PRIMARY-TEXT:** current FIDE Handbook or FIDE decision text fetched directly from the official FIDE host.
- **PRIMARY-LIST:** official FIDE endorsed-program list; absence from a dated list is not proof that no later decision exists.
- **REPOSITORY-CLAIM:** existing documentation, source, or tests; useful for locating claims but not independent proof.
- **DIRECT-PROBE:** executable behavior observed against the checkout or a pinned external-library source.
- **DERIVED:** a conclusion from stated primary text and inspected behavior. Interpretations and strategies are labelled separately; they are not FIDE rules.

### Current audit-branch verification (2026-10-27)

| Gate | Result / scope |
|---|---|
| Full test suite | CPython 3.11.2: **564 passed, 16 skipped**. Skips are explained: 5 BBP live-oracle tests (no `BBP_EXE`), 3 JaVaFo live-oracle tests (no `JAVAFO_JAR`), 2 opt-in heavy benchmarks, and 6 team-kind parameter cases. |
| Determinism | `PYTHONHASHSEED=12345`: **56 passed** across determinism, canonical, and frozen-v0.1.0 suites. |
| Official Berger fixtures | `tests/test_roundrobin.py`: **41 passed**; exact C.05 Annex 1 comparisons for N=3–16. |
| Static/source | `compileall` passed; Ruff `F821` passed across `src` and `tests`; modified Python files passed targeted `F821,F401,E722`; source registry validator passed (**41 sources, 74 rules, 8 full-text evidence files**); `git diff --check` passed. Repo-wide unused-import debt is not a gate (40 `F401` findings remain). |
| Packaging | Wheel and sdist for `0.4.2.dev0` built successfully; metadata/license/archive checks passed; isolated wheel install and public API/example smoke passed. Build outputs were removed. No v0.4.1 artifact was rebuilt. |
| Interpreter matrix | Workflow is configured for CPython 3.10–3.15, but this branch has not yet completed hosted CI across that matrix. Only Python 3.11.2 has been verified locally; G-09 remains open. |

These are exact-revision local results, not FIDE conformance evidence. The
remaining open engineering gate and per-system evidence limitations are kept
open below rather than inferred from successful local tests.

## 2. Confirmed findings and required dispositions

| ID | Priority | Baseline finding and evidence | Required disposition | Current status |
|---|---|---|---|---|
| G-01 | P0 | At the audit baseline, the 2026 `pair_2026()` dispatcher returned engine output without a request-relative completeness postcondition. `P26Pairing` could be constructed empty; the value object could not know the roster. Several engines had internal checks, but the public facade was the correct common safety boundary. **DIRECT-PROBE / SOURCE.** | Reject empty rosters as requests; after dispatch verify exact roster coverage, no unknown/duplicate players, the parity-correct bye, eligible bye, valid float references, no rematch, and matching ruleset. A failed engine postcondition is `InternalError`, never a successful partial result. | CLOSED — facade postconditions; contract tests and full suite pass |
| G-02 | P0 | At the audit baseline, 2026 input value objects did not validate all types/ranges/finiteness. Direct probes confirmed acceptance of `score=NaN`, negative rating, duplicate opponents, negative `total_rounds`, and `round_number=True`; further source inspection found boolean/non-integer counters, untyped request members, non-finite secondary scores/budgets, and duplicate `round_results` player IDs. **DIRECT-PROBE / SOURCE.** | Validate at the value-object/facade boundary with typed pairing errors; reject booleans where integers are required; reject non-finite numbers, negative ratings/counters, duplicate histories, malformed maps, and inconsistent request dates. Preserve accepted valid inputs and document any intentional caller-owned facts. | CLOSED — validation and boundary tests; full suite passes |
| G-03 | P0 | At the audit baseline, `fide2026/burstein.py:buchholz_sb()` reimplemented tie-break calculations inside Pairing-Core. It used W/D/L as fixed `1/.5/0`, summed only listed opponents, and did not implement C.04.4.2 Art.1.7.2's self-game treatment for unplayed rounds or the consecutive-zero-bye exception. **PRIMARY-TEXT / DIRECT-PROBE / SOURCE.** | Remove the local calculator. Make the narrow integration contract explicit: post-seeding Burstein requests require a complete, finite per-player `(Buchholz, Sonneborn–Berger)` Index set plus source metadata. Pairing-Core consumes only those pairing-order values; it does not calculate or silently substitute a different ordering. Missing or roster-mismatched values fail with a typed request error. | CLOSED — local formula removed; external Index boundary covered by tests; C.04 calculator remains an explicit system limitation |
| G-04 | P0 | The separate `tiebreak-core` v1.2.0 API was inspected at commit `61491321d7886ab4abe1b7c64686dfce48d2c3dd`; its suite passed `656 passed, 69 skipped`. It implements C.07 `fide-2026` BH/SB and Article 16 dummy/adjusted-score handling, but has no C.04.4.2 Burstein Index API. C.07 unplayed-round treatment is not interchangeable with C.04.4.2 self-game/zero-bye-streak treatment. The pinned library README marks C.04 pairing-time evaluation consumer-owned/out of scope, and its integration note treats Burstein ordering numbers as inputs rather than a calculator feature. **PRIMARY-TEXT / DIRECT-PROBE.** | Keep a versioned caller-supplied/library-calculated input seam and record the claimed producer, producer version, and producer ruleset. Do not add a C.07-to-C.04 equivalence claim. No C.07/C.04 semantic equivalence has been independently established in this audit; callers must verify it for their data before using such values. Otherwise the precise C.04 calculation gap remains, and Pairing-Core refuses to invent a value. No Pairing-Core dependency on or copy of tiebreak-core is required by this contract. | CLOSED — provenance boundary implemented and documented; no C.04 calculator/equivalence is claimed |
| G-05 | P0 | At the audit baseline, 2026 `P26Pairing` output carried pairs/byes/floats/ruleset/notes only; it omitted round number, engine/package version, normalized input digest, result digest, and Burstein Index source. **SOURCE.** | Add additive, versioned 2026 output provenance and canonical digests. Record engine identity/version, dated ruleset, input digest, round, and any Burstein Index producer metadata. Preserve parsing of the old unversioned dictionary shape. | CLOSED — versioned envelope, digest verification, and legacy-shape parsing tested |
| G-06 | P1 | At the audit baseline, Berger tests pinned official tables only for even fields 4–12, while C.05 Annex 1 publishes schedules for 3–16. **PRIMARY-TEXT / SOURCE.** | Add exact official-table comparisons for every listed field size 3–16, including odd-field bye placement, and retain structural checks outside the published range. Label the double-cycle last-two-round reversal as the text's recommendation/implementation strategy, not a mandatory rule. | CLOSED — exact official comparisons for N=3–16; `tests/test_roundrobin.py` 41 passed |
| G-07 | P1 | At the audit baseline, `_process.py` terminated only the direct child; descendants could outlive the adapter call or retain pipes. **SOURCE / SECURITY REVIEW.** | On POSIX, isolate each adapter run in its own process group and terminate/reap the group on timeout, output overflow, and cleanup; test a spawned descendant. Keep the non-POSIX limitation explicit unless equivalent process-tree control is implemented and verified there. Validate finite positive timeout values. | CLOSED — POSIX group cleanup and descendant test; Windows direct-child limitation documented |
| G-08 | P1 | At the audit baseline, documentation contradicted current package metadata, release status, tiebreak-core availability, and implementation scope. **DIRECT-PROBE / SOURCE.** | Establish this register as the current authority; reconcile README, capability, acceptance, dependency, security, and integration docs. Keep historical reports labelled historical. State the pairing-only boundary and FIDE endorsement/evaluation limits consistently. | CLOSED — current product/source/dependency docs reconciled; prior reports visibly historical; release tests pass |
| G-09 | P1 | At the audit baseline, declared `Python >=3.10` outpaced the workflow matrix of 3.10–3.12; CPython 3.13–3.15 had no workflow evidence. Python 3.10 reached upstream end-of-life on 2026-10-01. **SOURCE / DIRECT-PROBE.** | Keep the compatibility floor deliberately documented, expand the CI matrix to maintained/current minors plus the retained floor, and state only versions that pass CI as verified. Do not infer support from `requires-python` alone. | OPEN — matrix configured for 3.10–3.15; local run is CPython 3.11.2 only; hosted full-matrix result pending |
| G-10 | P2 | At the audit baseline, `ruff` was not a project gate. The prior broad default scan reported 1,057 legacy style/modernization findings, mostly UP rules; targeted checks found unused imports and undefined/dead code. A current repo-wide `F401` probe still reports 40 existing unused-import findings outside the selected gate. **DIRECT-PROBE.** | Fix confirmed undefined/dead code and add a narrowly scoped undefined-name gate. Do not mass-reformat the compatibility-sensitive repository as part of this audit. Track broad lint modernization separately. | CLOSED — F821 fixes, CI gate, full-source F821 pass; changed files F821/F401/E722 clean; broad F401 debt remains non-gating |
| G-11 | P1 | The 2026 rule engines have a large existing rule→source→code→test corpus, but existing “validated” labels and historical reports are project claims. This audit has not independently re-proved every search order, interpretation, or generated pairing for every system. Known unresolved/strategy items include the Dutch exact-search ceiling; Lim upward-scrutiny mirror/ordering approximations; Double/Team next-bracket lookahead; Olympiad source/procedure evidence qualifications; and caller-owned event data. **PRIMARY-TEXT / REPOSITORY-CLAIM.** | Keep each system's precise source and known limitation visible. No global “FIDE-compliant”, “fully conformant”, or “production-ready” assertion. Close each remaining per-system item only with a clause-level source, independent test/oracle, reproducible run, and an explicit interpretation/strategy decision. | OPEN — per-system conformance not independently re-proved; limitations remain documented |
| G-12 | P0 | FIDE C.02.03 effective 2026-03-01 defines a Tournament Handler Program (THP) as software managing player data, pairings, and results. Article 7 requires, among other things, rating-list import, declared FIDE Swiss systems and acceleration support, correct mandatory tie-break standings, English FIDE mode/help, current TRF import/export, free PTC and RTG unless exempt, and a controlled test environment. Pairing-Core is a pairing library and does not provide this product surface. C.04.2 Art.1.4 also deprecates use of Swiss systems unless an approved THP with free checker is available. **PRIMARY-TEXT.** | Formal THP evaluation is not an acceptance criterion Pairing-Core can meet alone. State that an integrating product may pursue evaluation; do not represent the library as FIDE-evaluable, certified, approved, or endorsed. | CLOSED — product boundary |
| G-13 | P1 | The official C.04 Annex 3 FIDE Endorsed Programs list retrieved (`C04Annex3_FEP22.pdf`, 2022 vintage) does not list Pairing-Core. No later FIDE decision naming Pairing-Core was found in the sources searched. This is not evidence that an unobserved later decision cannot exist. **PRIMARY-LIST / SEARCH.** | Make no endorsement claim. Report “no endorsement evidence found; not listed in the retrieved official list” rather than asserting an exhaustive negative. Recheck an authoritative current list before any future endorsement statement. | CLOSED — no claim |
| G-14 | P1 | Continuation review found that the 2026 Burstein and Dubov PAB completion probes used the shared rematch-only helper, although C.04.4.1/4.2 C4 requires a completion satisfying all absolute criteria, including C3's same-absolute-colour prohibition. A lower-score bye could therefore be selected despite leaving no C1+C3-compliant completion, even when a later eligible candidate did. **PRIMARY-TEXT / DIRECT-PROBE / SOURCE.** | Make PAB completion probes system-aware: include C3 colour conflicts for Burstein/Dubov while retaining their system-specific colour-preference semantics. Pin a regression where the first candidate is infeasible under C3 but the next is feasible. | CLOSED — C3-aware probes and regression; full suite passes (564 passed, 16 skipped) |

## 3. Authoritative rules reviewed in this audit

These official texts were fetched directly from `handbook.fide.com`; the named approval/effective dates are part of the source, not inferred from the retrieval date. Complete parsed page content was read from the returned chunks for the current C.04/C.05/C.07/C.02.03 and Olympiad texts listed here, including all chunks of C.04.6. The fetch interface did not expose raw response bytes, so no new source-text hashes are claimed; the retrieval limitation is recorded in [`../rules/fide/SOURCE_MANIFEST.md`](../rules/fide/SOURCE_MANIFEST.md).

| Source | Official URL | Verified identity/date | Relevant pairing scope |
|---|---|---|---|
| C.04.1 Basic Swiss Rules | <https://handbook.fide.com/chapter/C0401202507> | Council approved 2025-10-28; applied 2026-02-01 | No-repeat, PAB, PAB ineligibility, score grouping, general colour limits/preferences, transparency. |
| C.04.2 General Handling Rules | <https://handbook.fide.com/chapter/GeneralHandlingRulesForSwissTournaments202602> | Council approved 2025-10-28; applied 2026-02-01 | Swiss-system authorization, TPN/late-entry procedure, played-only colour histories (3.4), future re-pairing after an unplayed encounter (3.5), publication ordering. |
| C.04.3 Dutch | <https://handbook.fide.com/chapter/C0403202602> | Council approved 2025-10-28; applied 2026-02-01 | Pairing rank is score then ascending TPN; C1–C21 criteria, sequential generation and colour allocation. |
| C.04.4.1 Dubov | <https://handbook.fide.com/chapter/C040401202602> | Council approved 2025-10-28; applied 2026-02-01 | Rating/ARO definitions, upfloater/colour criteria, sequential procedure. |
| C.04.4.2 Burstein | <https://handbook.fide.com/chapter/C040402202602> | Council approved 2025-10-28; applied 2026-02-01 | Index = Buchholz then SB then ascending TPN; Art.1.7.2 self-game/unplayed rules and exclusion of acceleration virtual points. |
| C.04.4.3 Lim | <https://handbook.fide.com/chapter/C040403202602> | Council approved 2025-10-28; applied 2026-02-01 | Median routing, compatibility, floater/exchange/colour procedure. |
| C.04.5 Double Swiss | <https://handbook.fide.com/chapter/DoubleSwissSystem202602> | Council approved 2025-10-28; applied 2026-02-01 | Two-game matches, match scoring, PAB, pairing and colour rules. |
| C.04.6 Swiss Team | <https://handbook.fide.com/chapter/SwissTeamPairingSystem202602> | Council approved 2025-10-28; applied 2026-02-01 | Team primary/secondary score, PAB, no absolute colour preferences, pairing criteria. |
| C.04.7 Accelerated Systems | <https://handbook.fide.com/chapter/C0407202602> | Council approved 2025-10-28; applied 2026-02-01 | Baku GA/GB split, virtual points and pairing score; virtual points must not be confused with real standings for Burstein Index. |
| C.05 Annex 1 Berger Tables | <https://handbook.fide.com/chapter/C05Annex1> | Current Handbook Annex at retrieval; no separate approval/effective date stated on the page | Published schedules for 3–16; odd field highest pairing number is the bye; last-two-round reversal is recommended for double round robin. |
| C.07 Play-Off and Tie-Break Regulations | <https://handbook.fide.com/chapter/TieBreakRegulations032026> | Council approved 2026-02-02; applied 2026-03-01 | C.07 BH/SB definitions and Article 16 unplayed-round management; this is not itself a C.04.4.2 specification. |
| C.02.03 Chess Equipment with Electronic Components | <https://handbook.fide.com/chapter/ChessEquipmentWithElectronicComponenets032026> | Effective 2026-03-01 | Article 7 THP definition and conditions of compliance. |
| FIDE Endorsed Programs list | <https://handbook.fide.com/files/handbook/C04Annex3_FEP22.pdf> | Official Annex 3 list retrieved; list vintage 2022 | Lists named endorsed THPs/pairing engines; Pairing-Core is absent from this retrieved list. |

### External compatibility source

| Source | URL | Retrieved | Finding |
|---|---|---|---|
| Python Developer's Guide — Status of Python versions | <https://devguide.python.org/versions/> | 2026-10-27 | CPython 3.10 reached upstream end-of-life on 2026-10-01; 3.11–3.15 are listed as maintained. The package keeps its `>=3.10` compatibility floor and tests 3.10 in CI; this does not imply upstream security support for 3.10. |

### Rule / interpretation / strategy / policy distinctions

- **Rule:** text directly required by the cited FIDE article.
- **Interpretation:** a deterministic reading where the cited text leaves more than one reasonable choice; it must be named and tested.
- **Implementation strategy:** a computational method or bounded search used to realize a rule; it is not itself a FIDE rule.
- **Policy:** a Pairing-Core boundary decision (for example, refusing a result when required caller data is absent).
- **Unresolved:** evidence or semantics are insufficient to claim a specific result; it must remain a limitation or trigger refusal.

The source pages prove what the rules say and when they apply. They do **not**, by themselves, prove that a particular engine implementation conforms.

## 4. Per-system evidence posture

The authoritative evidence record is deliberately conservative. “Implemented” means code exists, not that a FIDE evaluation has occurred.

| System | Source/date | Current scope statement |
|---|---|---|
| `dutch-till2026-compat` | Pre-2026 Dutch text; frozen v0.1.0 kernel | Compatibility behavior is golden-pinned; documented E.5/float-bar deviations remain. It is not the current 2026 Dutch ruleset. |
| `dutch-2026` | C.04.3, 2026-02-01 | Implemented search with existing adversarial/property tests. Exact-search ceilings and documented rule readings remain; no external FIDE evaluation. |
| `dubov-2026` | C.04.4.1, 2026-02-01 | Implemented search with source-linked tests. Required ratings and history remain caller-owned; no external FIDE evaluation. |
| `burstein-2026` | C.04.4.2, 2026-02-01 | Post-seeding pairing requires a complete externally supplied Index set. Pairing-Core does not calculate or independently verify C.04 Index values. The caller must provide a semantically suitable value source; without it, this request is unavailable and the system is not a turnkey pairing path. |
| `lim-2026` | C.04.4.3, 2026-02-01 | Implemented procedural engine with documented scrutiny/ordering approximations and ambiguities. Must not be described as fully conformant. |
| `double-2026` | C.04.5, 2026-02-01 | Implemented match-pairing engine; completion lookahead is an explicit bounded strategy/limitation, not proof of full C3 conformance. |
| `team-2026` | C.04.6, 2026-02-01 | Implemented team-pairing mechanics; team composition, lineup and score valuation are caller-owned. Existing lookahead limitations remain. |
| `olympiad-2022` | FIDE Olympiad Pairing Rules, effective 2022-01-01 | Separate team system; initial team ordering and event facts are caller-owned. Its source/evidence grade differs from the 2026 C.04 Handbook pages. |
| `baku` helper | C.04.7, 2026-02-01 | Acceleration helper only; participant group membership, standings, and application to an engine are caller responsibilities. |
| Berger round robin | C.05 Annex 1 | Exact test comparisons cover every published size N=3–16, including odd-field bye placement. Double-cycle reversal of the last two rounds is a recommendation, not a mandatory rule. Exact table fixtures establish those table outputs, not universal C.05 conformance. |

## 5. Non-negotiable completion standard

The measurable gates are in [`COMPLETION_STANDARD.md`](COMPLETION_STANDARD.md). Code/test/package readiness, system-specific evidence, FIDE formal evaluation, and actual endorsement are separate verdicts. Passing Pairing-Core's own tests cannot satisfy the latter two.

### Current separate verdicts (2026-10-27)

| Assessment | Current verdict | Basis / condition to change |
|---|---|---|
| Engineering quality | **NOT READY for release sign-off** | Local gates pass on CPython 3.11.2, but G-09 remains open until the exact revision passes the configured CPython 3.10–3.15 hosted matrix. |
| Production use | **LIMITED** | Only a named ruleset/subset with caller-owned facts, known engine limits, resource controls, and human/data-owner review is supportable. Burstein after seeding needs a semantically suitable external C.04 Index source. |
| Per-system evidence | **MIXED; no system-wide conformance verdict** | See §4 per-system posture. Exact Berger tables are tested for 3–16; every Swiss/team engine still has independent verification gaps, interpretations/strategies, or caller-owned facts. |
| Formal FIDE evaluation | **NOT APPLICABLE / NOT READY for Pairing-Core alone** | The library is not a Tournament Handler Program; an integrating product would be evaluated separately. |
| Actual FIDE endorsement | **NO ENDORSEMENT EVIDENCE FOUND; NO CLAIM** | Pairing-Core is absent from the retrieved 2022 FEP list; no later naming decision was found in searched sources. Recheck a current official record before any future claim. |

## 6. Closure log

This section is updated in the same change that closes an item; closure requires a test or verifiable artifact named here. No finding is considered closed because code merely changed.

| ID | Closure evidence | Closed on |
|---|---|---|
| G-01 | `pair_2026` rejects empty rosters and validates roster conservation, bye parity/eligibility, rematches, float IDs, and ruleset; `tests/test_p26_contracts.py` and the full suite pass. | 2026-10-27 |
| G-02 | `P26Player`/`P26Request` validation covers finite/range/type/history/date controls; boundary tests and full suite pass. | 2026-10-27 |
| G-03 | Removed local `buchholz_sb`; `BursteinIndexSet` requires complete finite per-player values at post-seeding and carries declared provenance; tests pass. The missing C.04 calculator remains a stated product limitation. | 2026-10-27 |
| G-04 | Inspected `tiebreak-core` v1.2.0 source/tests; added caller/library provenance seam and explicit no-equivalence rule. No C.04 calculator or C.07 equivalence claim was added. | 2026-10-27 |
| G-05 | Versioned P26 request/result schema, input/result digests, ruleset/engine/version/round provenance, Burstein producer metadata, tamper detection, and old unversioned result parsing are tested. | 2026-10-27 |
| G-06 | Official C.05 Annex 1 tables transcribed and compared exactly for N=3–16; `tests/test_roundrobin.py`: 41 passed. | 2026-10-27 |
| G-07 | POSIX isolated process groups, TERM/KILL cleanup and descendant regression verified; Windows direct-child limitation is stated in code/docs. | 2026-10-27 |
| G-08 | Current README, capability, packaging, tie-break/product-boundary, source, and readiness docs reconciled; superseded reports visibly historical; release/docs tests pass. | 2026-10-27 |
| G-10 | Ruff undefined-name gate (`F821`) added and passed; confirmed undefined/dead code removed; compile/source checks passed. Broad style/unused-import cleanup remains explicitly non-gating. | 2026-10-27 |
| G-12 | Product boundary recorded; no THP or certification claim is made. | 2026-10-27 |
| G-13 | Official C04Annex3 FEP22 PDF retrieved and checked; Pairing-Core is not listed; wording is bounded to the retrieved list. | 2026-10-27 |
| G-14 | Burstein uses `_subset_c3_ok` and Dubov adds C3 conflicts to the PAB completion probe; a five-player regression proves the first candidate is skipped and the next feasible candidate selected. Full suite: 564 passed, 16 skipped. | 2026-10-27 |
