# FIDE documentation and evidence coverage dashboard

**Registry snapshot:** 2026-10-27 · **Generated from:** `registry/sources.json`, `registry/systems.json`, `registry/clauses.json`

> [!WARNING]
> These counts measure source/rule indexing and project evidence pointers only. They do **not** measure FIDE compliance, approval, certification, independent evaluation, or production readiness.

## Source inventory

- Source records: **40**; all source IDs referenced by the clause registry are validated against this list.
- Status counts: `current` 20; `current_list_as_retrieved` 1; `historical` 6; `historical_snapshot` 2; `superseded` 9; `unknown` 2
- Current parsed Handbook pages retrieved in this review expose no original bytes; those entries have no claimed raw-source checksum. No local FIDE originals or bulk texts are committed.
- Redistribution permission/open licence: **not established**. No source originals/full texts are committed; a small set of clearly labeled test fixtures contains structured transcriptions or derived values from named official numerical examples, and rights for those example-data transcriptions are also not established.

## Clause/evidence inventory

- Clause records: **262** across **20** cited sources and **13** system/boundary views.
- Records with at least one inspected implementation symbol: **98**.
- Records with at least one named repository test: **96**.
- Implementation-status counts: `caller_supplied` 10; `disputed` 1; `historical_compat` 2; `implemented` 45; `out_of_scope` 30; `partial` 41; `unmapped` 132; `withdrawn` 1
- Independent-verification-status counts: `none` 240; `official_worked_example_only` 22
- External independent oracle/evaluation records in this registry: **0**. Official worked-example regressions are separately identified and do not establish full-system behavior.
- A large unmapped count is intentional: clauses are not marked supported just because a nearby implementation or generic test exists.

## Per-system counts

| System | Clauses | Impl refs | Test refs | Unmapped/disputed | Out of scope | Independent status |
|---|---:|---:|---:|---:|---:|---|
| [baku](system-pages/baku.md) | 6 | 5 | 4 | 1 | 0 | none: 4, official_worked_example_only: 2 |
| [berger](system-pages/berger.md) | 21 | 15 | 15 | 1 | 5 | none: 7, official_worked_example_only: 14 |
| [burstein-2026](system-pages/burstein-2026.md) | 54 | 22 | 22 | 26 | 6 | none: 53, official_worked_example_only: 1 |
| [c07-tiebreak-boundary](system-pages/c07-tiebreak-boundary.md) | 4 | 0 | 0 | 0 | 4 | none: 4 |
| [double-2026](system-pages/double-2026.md) | 49 | 18 | 18 | 25 | 6 | none: 46, official_worked_example_only: 3 |
| [dubov-2026](system-pages/dubov-2026.md) | 62 | 24 | 23 | 32 | 6 | none: 62 |
| [dutch-2026](system-pages/dutch-2026.md) | 90 | 9 | 9 | 74 | 6 | none: 90 |
| [dutch-till2026-compat](system-pages/dutch-till2026-compat.md) | 3 | 1 | 1 | 1 | 0 | none: 3 |
| [knockout-boundary](system-pages/knockout-boundary.md) | 0 | 0 | 0 | 0 | 0 |  |
| [lim-2026](system-pages/lim-2026.md) | 52 | 19 | 19 | 28 | 6 | none: 51, official_worked_example_only: 1 |
| [olympiad-2022](system-pages/olympiad-2022.md) | 17 | 11 | 11 | 1 | 5 | none: 16, official_worked_example_only: 1 |
| [team-2026](system-pages/team-2026.md) | 54 | 19 | 19 | 29 | 6 | none: 54 |
| [thp-product-boundary](system-pages/thp-product-boundary.md) | 10 | 0 | 0 | 0 | 10 | none: 10 |

## Known evidence gaps that remain visible

- Superseded source editions are indexed; apart from explicit grouped historical records, they are not exhaustively clause-mapped and do not establish prior-edition coverage.
- Historical `dutch-till2026-compat` is represented by a grouped behavioral record, not a clause-complete current-rule map.
- C.04.4.2 Burstein Index calculation remains absent; callers must provide complete values and provenance. C.07 values are not presumed equivalent.
- Dutch C8 and Double/Team look-ahead are partial implementation strategies; Lim scrutiny/order includes a disputed record.
- The parent C.05 general-regulations page remains an unresolved source pointer because the fetch exposed no article text; current Annex 2 Varma draw procedures are inventoried as out of scope.
- Olympiad clauses and independent per-system evidence remain incomplete; event-management rules are caller-owned/out of scope.
- All unmapped records include a closure action on their source/system view.

## Navigation

[clause index](CLAUSE_INDEX.md) · [source index](SOURCE_INDEX.md) · [rule/source/code/test matrix](RULE_SOURCE_MATRIX.md) · [system views](SYSTEM_COVERAGE.md)

Current readiness and audit findings remain authoritative in [GAP_REGISTER.md](../../audit/GAP_REGISTER.md); the separate acceptance gates are in [COMPLETION_STANDARD.md](../../audit/COMPLETION_STANDARD.md).
