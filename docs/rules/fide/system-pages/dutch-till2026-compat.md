# Dutch pre-2026 compatibility ruleset

**System ID:** `dutch-till2026-compat`<br>
**System status:** `frozen_compatibility_not_current_rules`<br>
**Sources:** [F-0102](../source-pages/F-0102.md), [F-0107](../source-pages/F-0107.md)

## Scope and limitations

Retained for behavioral compatibility; its output is not a claim of current 2026 Dutch-system behavior. Read the archival behavior corpus and limitations before use.

**Inspected entry points:** [`src/pairing_core/api.py::pair`](../../../../src/pairing_core/api.py#L276)

Limitations:
- Historical source mapping is not yet clause-complete in the new registry.
- Known legacy deviations remain; the v0.1.0 golden corpus is a compatibility oracle, not an independent FIDE oracle.

## Clause-level view

The rows below state project implementation and independent verification separately. They are not a conformity result.

| Clause ID | Source clause | Project paraphrase | Implementation | Verification | Code/tests | Closure |
|---|---|---|---|---|---|---|
| [F-0102:3](../source-pages/F-0102.md#f-0102-3) | 3 | The superseded basic rules assigned a historical pairing-bye value; retained only for compatibility context. | `unmapped` | `none` | none mapped | Recheck the exact superseded source clause and verify whether any compatibility behavior is intentionally retained; do not infer support from current PAB tests. |
| [F-0106:interim-PAB](../source-pages/F-0106.md#f-0106-interim-pab) | interim-PAB | The interim 2025 Dutch edition is historical; its old matrix claim is not adopted as current evidence. | `historical compat` | `none` | none mapped | Keep this interim edition historical; re-verify its exact archived text before making any edition-specific claim. |
| [F-0107:A.1-E.5](../source-pages/F-0107.md#f-0107-a-1-e-5) | A.1-E.5 | The frozen compatibility engine is associated with the superseded Dutch formulation: ranking/brackets, absolute/completion criteria, transpositions/exchanges and colour allocation. This grouped index is intentionally marked incomplete. | `historical compat` | `none` | [`src/pairing_core/engine.py::pair_round`](../../../../src/pairing_core/engine.py#L35), [`tests/test_v010_behavioral.py::test_engine_golden`](../../../../tests/test_v010_behavioral.py#L71), [`tests/test_v010_behavioral.py::test_validator_golden`](../../../../tests/test_v010_behavioral.py#L90), [`tests/test_v010_behavioral.py::test_error_golden`](../../../../tests/test_v010_behavioral.py#L104) | Keep the frozen v0.1 behavioral harness as compatibility evidence only; split exact historical clause mapping only after rechecking the cited superseded edition. Do not count it as current-system or FIDE-conformance evidence. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
