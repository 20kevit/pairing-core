# Tournament Handler Program (THP) product boundary

**System ID:** `thp-product-boundary`<br>
**System status:** `outside_pairing_core_product_scope`<br>
**Sources:** [F-0405](../source-pages/F-0405.md), [F-0406](../source-pages/F-0406.md), [F-0407](../source-pages/F-0407.md)

## Scope and limitations

FIDE C.02.03 defines a THP as an application managing player data, pairings and results and requires product features beyond this pairing-only library. FIDE list evidence is bounded to the retrieved C.02.04 page.

Limitations:
- Pairing-Core has no THP evaluation, TAPC, FIDE approval or endorsement claim.
- Absence from a retrieved list does not rule out an unobserved later written decision.

## Clause-level view

The rows below state project implementation and independent verification separately. They are not a conformity result.

| Clause ID | Source clause | Project paraphrase | Implementation | Verification | Code/tests | Closure |
|---|---|---|---|---|---|---|
| [F-0405:7.1.1.a](../source-pages/F-0405.md#f-0405-7-1-1-a) | 7.1.1.a | THPs import current FIDE rating lists; Pairing-Core does not manage rating-list import. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.1.1.b](../source-pages/F-0405.md#f-0405-7-1-1-b) | 7.1.1.b | THPs support declared FIDE Swiss systems and acceleration methods. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.1.1.c](../source-pages/F-0405.md#f-0405-7-1-1-c) | 7.1.1.c | THPs generate final standings using mandatory tie-breaks; calculation is outside Pairing-Core. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.1.2-7.1.4](../source-pages/F-0405.md#f-0405-7-1-2-7-1-4) | 7.1.2-7.1.4 | THP compliance is per system and requires FIDE mode, English help, data exchange, free checker/generator unless exempt and controlled testing. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.2.1-7.2.2](../source-pages/F-0405.md#f-0405-7-2-1-7-2-2) | 7.2.1-7.2.2 | THPs use TRF26 with backward compatibility; Pairing-Core TRF support is a subset and not a THP evaluation. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.2.3](../source-pages/F-0405.md#f-0405-7-2-3) | 7.2.3 | PTC is a free THP checker; Pairing-Core’s tests are not a checker certificate. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.2.4](../source-pages/F-0405.md#f-0405-7-2-4) | 7.2.4 | RTG is a THP product feature; it is not implemented by this library. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0405:7.3.1-7.3.7](../source-pages/F-0405.md#f-0405-7-3-1-7-3-7) | 7.3.1-7.3.7 | NRD, acceptance-cycle, TAPC and transition rules describe external FIDE evaluation, not library behavior. | `out of scope` | `none` | none mapped | No Pairing-Core implementation action. An integrating THP must provide and independently evidence this product capability. |
| [F-0406:THP-list](../source-pages/F-0406.md#f-0406-thp-list) | THP-list | The retrieved C.02.04 table lists named products/versions and expiry dates; Pairing-Core does not appear. This is bounded list evidence, not proof that no separate decision exists. | `out of scope` | `none` | none mapped | Make no endorsement claim. Recheck an official current record or obtain written FIDE decision before changing the verdict. |
| [F-0407:2022-list](../source-pages/F-0407.md#f-0407-2022-list) | 2022-list | Pairing-Core does not appear in the retrieved 2022 FIDE Endorsed Programs PDF. This is evidence about that list only, not proof that no later or separate decision exists. | `out of scope` | `none` | none mapped | Keep this conclusion bounded to the retrieved 2022 list; use the separately indexed current C.02.04 list and do not make an exhaustive negative or endorsement claim. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
