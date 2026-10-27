# Pairing-Core completion and readiness standard

- **Version:** 1.0
- **Applies to:** the pairing-only Pairing-Core library and its supported entry points.
- **Owner of current evidence:** [`GAP_REGISTER.md`](GAP_REGISTER.md).

A single green test suite is not a universal readiness verdict. The following five assessments are independent and must be reported separately.

## 1. Engineering quality

**Ready when every applicable gate below passes on the named source revision.**

| Gate | Measurable acceptance |
|---|---|
| Automated behavior | Full `pytest` suite passes on every supported CPython minor in CI. Any skipped test is enumerated with its environmental reason; no unexpected skips, xfails, or swallowed failures. |
| Compatibility | Frozen `v0.1.0` behavioral corpus and public legacy API tests remain byte/behavior-identical unless an explicitly approved migration changes the affected API. `v0.4.1` tag/artifacts remain untouched. |
| Input boundary | Hostile/malformed tests prove finite numeric validation, boolean-vs-integer distinction, unique player/TPN/history data, typed failures, and no raw `AttributeError`/`TypeError` leakage for public requests. |
| Output boundary | Every successful facade result covers exactly the eligible input roster once, has a parity-correct and eligible bye, contains no unknown player, repeat opponent, invalid float reference, or partial result; engine invariant failures return a typed internal failure. |
| Determinism/replay | Repeated calls, input reorder where semantically irrelevant, and at least two `PYTHONHASHSEED` values produce identical pairing and canonical result bytes. Versioned 2026 results include input/result SHA-256 digests and producer/ruleset provenance. |
| Bounds/security | Pathological search returns within the declared deterministic step ceiling or a typed timeout. Adapter output is capped during collection; timeout, output overflow, and cleanup terminate the spawned process tree on platforms where process-group control is claimed. |
| Packaging | Wheel and sdist build from a clean checkout; artifact metadata, `Requires-Python`, MIT text, source inclusion, and imports are checked in an isolated environment. A plain install has no runtime dependency unless a future change justifies and documents one. No v0.4.1 artifact is rebuilt or republished. |
| Static/source checks | Offline FIDE registry validation passes: source/supersession/rights metadata, available artifact checksums, real implementation symbols and tests, example-fixture provenance, internal links/anchors, generated-view row counts and registry hashes are checked by `tools/fide_evidence.py`. `compileall` and targeted undefined-name lint also pass. Broad style modernization is not a release gate until repository-wide baseline debt is triaged. |
| Documentation | Public docs match package version, actual API fields, supported systems, product boundary, runtime dependencies, security posture, source effective dates, and limitations. Historical reports are visibly historical. |

The current CI target is CPython 3.10–3.15. Python 3.10 is retained in
`Requires-Python` and the CI matrix for compatibility, although upstream
end-of-life was 2026-10-01; the library cannot provide interpreter security
fixes. The configured matrix is not itself a pass: report only exact-revision
runs that completed successfully. Previously recorded GitHub Actions run
[40504177884](https://github.com/20kevit/pairing-core/actions/runs/40504177884)
passed all six CPython 3.10–3.15 jobs on commit
`d311cf3e75843eec2e72862d3f3f162d59d9bc02`; this is evidence only for that
exact commit, not later PR-head commits. Check [PR #1](https://github.com/20kevit/pairing-core/pull/1)
for the branch-head result. This is engineering-matrix evidence only, not FIDE
conformance. GitHub emitted non-blocking Node 20 and `ubuntu-latest` migration
warnings for the historical run.

A passing engineering gate says that the library behaves as its documented contract says. It does not prove that the contract or every algorithm matches FIDE.

## 2. Production use

**Default verdict for the whole library: LIMITED, not blanket production-ready.**

A consuming application may use a particular engine in production only when all of these are true:

1. The exact system, effective-date ruleset, engine version, input assumptions, and limitations are explicitly selected and recorded.
2. The caller supplies complete, current tournament state required by that system; no rule-sensitive values are fabricated or inferred.
3. The system-specific evidence threshold in §3 is met for the intended operating subset, and a tournament-data owner validates state roll-forward and output before publication.
4. Resource limits and adapter prerequisites are set appropriately; all failures are surfaced as errors, not substituted results.
5. For Burstein after seeding, a complete C.04.4.2 Index set is supplied with source provenance. Pairing-Core does not compute that Index. If no semantically suitable calculator/value source exists, Burstein is unavailable for that request.
6. Any integration that requires FIDE use has its own authorization/evaluation status and does not treat Pairing-Core's test suite as a FIDE checker certificate.

`dutch-till2026-compat` is a frozen compatibility ruleset, not the current 2026 Dutch rule set. FIDE-system names in the API identify the intended ruleset and do not constitute certification.

## 3. Per-system evidence threshold

A system can be called **evidence-supported for a stated subset** only when its record contains:

- the exact authoritative source URL, source type, approval/adoption date, effective date, supersession status, and retrieved-text hash or a transparent reason a hash cannot be retained;
- a clause-level map from every applicable absolute, completion, quality, bye, colour, ordering, and boundary rule to code and named tests;
- official worked examples reproduced exactly where available, plus independent adversarial/property fixtures for unillustrated rules;
- any differential oracle identified by exact version/ruleset, with every mismatch explained and retained as regression evidence;
- every interpretation, implementation strategy, caller-owned fact, and unresolved issue distinguished from normative rules;
- deterministic/performance/security evidence for the actual input-size envelope; and
- a current limitation list that is reflected in runtime capability metadata and user documentation.

The current project-maintained source/edition and clause-level inventory is navigable from [`docs/rules/fide/README.md`](../rules/fide/README.md); all 262 clause records are accounted for and no record is currently `unmapped`. Partial, disputed, caller-supplied, out-of-scope, historical, and explicitly not-implemented records remain open or bounded; grouped ranges and incomplete historical mapping still limit completeness. A source that is complete does not imply implementation completeness. A test corpus derived from the implementation is not an independent oracle. “Evidence-supported” does not mean FIDE-approved or endorsed.

## 4. Formal FIDE evaluation

**For Pairing-Core as a library: NOT APPLICABLE / NOT READY.**

FIDE Handbook C.02.03 Article 7 defines a Tournament Handler Program (THP) as an application managing player data, pairings, and results. Its listed requirements include rating-list import; declared FIDE Swiss and acceleration support; mandatory tie-break standings; FIDE mode, English interface/help; current TRF import/export with backward compatibility; free pairing/tie-break checker and random tournament generator unless TEC-exempted; and a controlled test environment. Pairing-Core intentionally does not provide most of this product surface.

A future integrating THP may include Pairing-Core as one component and seek evaluation for its own declared products/systems. No wording may imply that Pairing-Core alone has passed or is eligible for the THP evaluation process.

## 5. Actual FIDE endorsement

**Current verdict: NO ENDORSEMENT EVIDENCE FOUND; NO CLAIM.**

Only a current, official FIDE record or written FIDE decision naming the exact product, version, and pairing system can change this verdict. An old endorsed pairing engine, the use of a named FIDE system, source citations, conformance tests, an application author's claim, or a successful local audit is not endorsement evidence.

The retrieved 2022 FIDE Endorsed Programs PDF and the current C.02.04 THP table retrieved for this audit (effective 2026-03-01) do not list Pairing-Core. That supports “not listed in the retrieved lists”; it is not proof that no separate or later decision exists. See the source pages and bounded status notes in [`docs/rules/fide/SOURCE_INDEX.md`](../rules/fide/SOURCE_INDEX.md).

## 6. Release/revision reporting template

Every audit or release report must state, separately:

- **Engineering quality:** READY / NOT READY, exact revision, gates and exceptions.
- **Production use:** READY / LIMITED / NOT READY, exact engine and operating subset.
- **Per-system evidence:** one verdict per ruleset, source/effective date and open limitations.
- **Formal FIDE evaluation:** NOT APPLICABLE TO LIBRARY / PENDING / PASSED, with exact product evidence.
- **Actual endorsement:** NO EVIDENCE FOUND / VERIFIED, with exact official record.

Never combine these into one “FIDE-compliant” badge or a single green status.
