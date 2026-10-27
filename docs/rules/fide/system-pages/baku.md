# Baku Acceleration helper, 2026 edition

**System ID:** `baku`<br>
**System status:** `partial_helper_only`<br>
**Sources:** [F-0103](../source-pages/F-0103.md), [F-0117](../source-pages/F-0117.md)

## Scope and limitations

Pure helper functions for GA/GB and virtual-point inputs. Pairing-Core does not select an acceleration policy, manage late entries, verify scoring premises, or manage tournament standings.

**Inspected entry points:** [`src/pairing_core/fide2026/baku.py::split_groups`](../../../../src/pairing_core/fide2026/baku.py#L21), [`src/pairing_core/fide2026/baku.py::virtual_points`](../../../../src/pairing_core/fide2026/baku.py#L38), [`src/pairing_core/fide2026/baku.py::pairing_scores`](../../../../src/pairing_core/fide2026/baku.py#L56)

Limitations:
- Caller is responsible for correct event eligibility, late-entry history and applying the helper to the intended Swiss system.
- Only the source's worked examples and selected helper behavior have regression fixtures.

## Clause-level view

The rows below state project implementation and independent verification separately. They are not a conformity result.

| Clause ID | Source clause | Project paraphrase | Implementation | Verification | Code/tests | Closure |
|---|---|---|---|---|---|---|
| [F-0117:0](../source-pages/F-0117.md#f-0117-0) | 0 | Acceleration rearranges early Swiss brackets; Baku is one method and its event premise remains caller-owned. | `unmapped` | `none` | none mapped | Inspect this exact official clause against the selected engine; add a named code mapping and clause-specific test, or record why it is caller-owned/out of scope. |
| [F-0117:1.1](../source-pages/F-0117.md#f-0117-1-1) | 1.1 | Method applies only when a win is worth two draws and a loss is zero. | `caller supplied` | `none` | [`src/pairing_core/fide2026/baku.py::virtual_points`](../../../../src/pairing_core/fide2026/baku.py#L38), [`tests/test_fide2026.py::test_baku_virtual_schedules_official`](../../../../tests/test_fide2026.py#L104) | Keep the caller-owned input/provenance obligation explicit and validate it in the consuming application. |
| [F-0117:1.2](../source-pages/F-0117.md#f-0117-1-2) | 1.2 | Split sorted entrants into GA, first half rounded up to even, and remaining GB. | `implemented` | `official_worked_example_only` | [`src/pairing_core/fide2026/baku.py::split_groups`](../../../../src/pairing_core/fide2026/baku.py#L21), [`tests/test_fide2026.py::test_baku_split_official`](../../../../tests/test_fide2026.py#L97) | Keep the mapping current; add independent per-system evidence before any conformity statement. |
| [F-0117:1.3.1-1.3.2](../source-pages/F-0117.md#f-0117-1-3-1-1-3-2) | 1.3.1-1.3.2 | Admit late entrants under C.04.2 and preserve the last GA participant across rounds. | `caller supplied` | `none` | [`src/pairing_core/fide2026/models.py::P26Player`](../../../../src/pairing_core/fide2026/models.py#L156) | Keep the caller-owned input/provenance obligation explicit and validate it in the consuming application. |
| [F-0117:1.4.1-1.4.4](../source-pages/F-0117.md#f-0117-1-4-1-1-4-4) | 1.4.1-1.4.4 | Assign, halve and stop virtual points over the specified accelerated rounds; includes examples. | `implemented` | `official_worked_example_only` | [`src/pairing_core/fide2026/baku.py::accelerated_rounds`](../../../../src/pairing_core/fide2026/baku.py#L33), [`src/pairing_core/fide2026/baku.py::virtual_points`](../../../../src/pairing_core/fide2026/baku.py#L38), [`tests/test_fide2026.py::test_baku_virtual_schedules_official`](../../../../tests/test_fide2026.py#L104) | Keep the mapping current; add independent per-system evidence before any conformity statement. |
| [F-0117:1.5](../source-pages/F-0117.md#f-0117-1-5) | 1.5 | Pairing score is real standings score plus virtual points. | `implemented` | `none` | [`src/pairing_core/fide2026/baku.py::pairing_scores`](../../../../src/pairing_core/fide2026/baku.py#L56), [`tests/test_fide2026.py::test_baku_pairing_scores`](../../../../tests/test_fide2026.py#L113) | Keep the mapping current; add independent per-system evidence before any conformity statement. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
