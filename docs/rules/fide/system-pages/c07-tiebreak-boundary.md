# C.07 tie-break calculation boundary

**System ID:** `c07-tiebreak-boundary`<br>
**System status:** `outside_pairing_core_product_scope`<br>
**Sources:** [F-0704](../source-pages/F-0704.md), [F-0110](../source-pages/F-0110.md)

## Scope and limitations

Tie-break calculations belong to a separate library/application. C.07 results are not silently substituted for the C.04.4.2 Burstein Index.

Limitations:
- No C.07 calculator is implemented in Pairing-Core.
- No semantic equivalence between C.07 and C.04 Burstein calculations has been verified.

## Clause-level view

The rows below state project implementation and independent verification separately. They are not a conformity result.

| Clause ID | Source clause | Project paraphrase | Implementation | Verification | Code/tests | Closure |
|---|---|---|---|---|---|---|
| [F-0704:16.1-16.6](../source-pages/F-0704.md#f-0704-16-1-16-6) | 16.1-16.6 | C.07 Article 16 treatment is not substituted for C.04 Burstein Index handling. | `out of scope` | `none` | none mapped | Keep tie-break calculation separate. Do not equate C.07 values or unplayed-round semantics with C.04.4.2 without independently verified equivalence. |
| [F-0704:4.3](../source-pages/F-0704.md#f-0704-4-3) | 4.3 | C.07 tie-break types describe their own participant/opponent data; they do not establish C.04 Burstein Index equivalence. | `out of scope` | `none` | none mapped | Keep tie-break calculation separate. Do not equate C.07 values or unplayed-round semantics with C.04.4.2 without independently verified equivalence. |
| [F-0704:8.1](../source-pages/F-0704.md#f-0704-8-1) | 8.1 | C.07 Buchholz is a standings tie-break and is not a C.04.4.2 calculator input by presumed equivalence. | `out of scope` | `none` | none mapped | Keep tie-break calculation separate. Do not equate C.07 values or unplayed-round semantics with C.04.4.2 without independently verified equivalence. |
| [F-0704:9.1](../source-pages/F-0704.md#f-0704-9-1) | 9.1 | C.07 SB is a standings tie-break; C.04.4.2 semantics are distinct unless verified. | `out of scope` | `none` | none mapped | Keep tie-break calculation separate. Do not equate C.07 values or unplayed-round semantics with C.04.4.2 without independently verified equivalence. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
