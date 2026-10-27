# Dutch pre-2026 compatibility ruleset

**System ID:** `dutch-till2026-compat`<br>
**System status:** `frozen_compatibility_not_current_rules`<br>
**Sources:** [F-0102](../source-pages/F-0102.md), [F-0107](../source-pages/F-0107.md)

## Scope and limitations

Frozen compatibility entry point for the older pre-2026 F-0107 Dutch formulation as realized by the v0.1.0 kernel; it is not the interim 2025 F-0106 source and is not current Dutch-2026 behavior. The F-0106 source is indexed separately as source-only because no distinct implementation is claimed. The v0.1.0 golden corpus pins historical repository outputs, not FIDE conformity.

**Inspected entry points:** [`src/pairing_core/api.py::pair`](../../../../src/pairing_core/api.py#L276)

Limitations:
- Historical source mapping is not clause-complete; F-0106 interim-2025 is a separate recovered source-only record, not a claimed compatibility target.
- Known legacy deviations remain; the v0.1.0 golden corpus is a repository compatibility oracle, not an independent FIDE oracle.

## Clause-level view

The rows below preserve source wording cues and project readings separately from implementation and repository tests. They are not a conformity result.

| Clause ID | Section | Source cue / reading status | Project paraphrase | Implementation | Verification | Code/tests | Test scope | Closure |
|---|---|---|---|---|---|---|---|---|
| [F-0102:3](../source-pages/F-0102.md#f-0102-3) | 3 | as many points as are rewarded for a win / textual_cue_recorded | The superseded basic-rules text assigned pairing-bye points as a win-value default subject to tournament rules; the library does not award standings points. | `out of scope` | `none` | [`src/pairing_core/bye.py::create_bye_card`](../../../../src/pairing_core/bye.py#L109), [`src/pairing_core/models.py::PairingCard`](../../../../src/pairing_core/models.py#L76) | The legacy engine creates a bye card and golden tests pin compatibility output; neither awards nor validates tournament standings points. | Keep historical bye scoring in the event/standings caller. Do not infer PAB score calculation from a selected bye or a current-rule pairing test. |
| [F-0107:A.1-E.5](../source-pages/F-0107.md#f-0107-a-1-e-5) | A.1-E.5 | Version approved at the 87th FIDE Congress in Baku 2016 / textual_cue_recorded | The frozen compatibility engine is associated with the superseded Dutch formulation: ranking/brackets, absolute/completion criteria, transpositions/exchanges and colour allocation. This grouped index is intentionally marked incomplete. | `historical compat` | `none` | [`src/pairing_core/engine.py::pair_round`](../../../../src/pairing_core/engine.py#L35), [`tests/test_v010_behavioral.py::test_engine_golden`](../../../../tests/test_v010_behavioral.py#L71), [`tests/test_v010_behavioral.py::test_validator_golden`](../../../../tests/test_v010_behavioral.py#L90), [`tests/test_v010_behavioral.py::test_error_golden`](../../../../tests/test_v010_behavioral.py#L104) | Named repository tests exercise the linked behavior only; they do not establish independent evaluation, all source branches, or full-system conformity. | Keep the frozen v0.1 behavioral harness as compatibility evidence only; split exact historical clause mapping only after rechecking the cited superseded edition. Do not count it as current-system or FIDE-conformance evidence. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
