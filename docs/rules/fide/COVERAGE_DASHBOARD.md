# FIDE documentation and evidence coverage dashboard

**Registry snapshot:** 2026-10-27 · **Generated from:** `registry/sources.json`, `registry/systems.json`, `registry/clauses.json`

> [!WARNING]
> These counts measure source/rule indexing and project evidence pointers only. They do **not** measure FIDE compliance, approval, certification, independent evaluation, or production readiness.

## Source inventory

- Source records: **40**; all source IDs referenced by the clause registry are validated against this list.
- Status counts: `current` 15; `current_list_as_retrieved` 1; `historical` 6; `historical_snapshot` 3; `superseded` 9; `unknown` 6
- Current parsed Handbook pages retrieved in this review expose no original bytes; those entries have no claimed raw-source checksum. No local FIDE originals or bulk texts are committed.
- Redistribution permission/open licence: **not established**. No source originals/full texts are committed; a small set of clearly labeled test fixtures contains structured transcriptions or derived values from named official numerical examples, and rights for those example-data transcriptions are also not established.

## Clause/evidence inventory

- Clause records: **262** across **20** cited sources and **14** system/boundary views.
- Records with at least one inspected implementation symbol: **220**.
- Records with at least one named repository test: **215**.
- Implementation-status counts: `caller_supplied` 23; `disputed` 1; `historical_compat` 1; `implemented` 57; `not_implemented` 1; `out_of_scope` 40; `partial` 138; `withdrawn` 1
- Source-reading evidence counts: `interpretation_required` 3; `interpretation_resolved` 3; `not_reverified` 2; `textual_cue_recorded` 254
- Independent-verification-status counts: `none` 240; `official_worked_example_only` 22
- External independent oracle/evaluation records in this registry: **0**. Official worked-example regressions are separately identified and do not establish full-system behavior.
- `unmapped` items and all other non-implemented statuses remain visible with per-clause actions in [CLAUSE_CLOSURE_QUEUE.md](CLAUSE_CLOSURE_QUEUE.md). A mapped code/test link is not a conformity finding.

## Per-system counts

| System | Clauses | Impl refs | Test refs | Unmapped/disputed | Out of scope | Independent status |
|---|---:|---:|---:|---:|---:|---|
| [baku](system-pages/baku.md) | 6 | 6 | 5 | 0 | 0 | none: 4, official_worked_example_only: 2 |
| [berger](system-pages/berger.md) | 21 | 16 | 16 | 0 | 5 | none: 7, official_worked_example_only: 14 |
| [burstein-2026](system-pages/burstein-2026.md) | 54 | 44 | 41 | 0 | 10 | none: 53, official_worked_example_only: 1 |
| [c07-tiebreak-boundary](system-pages/c07-tiebreak-boundary.md) | 4 | 0 | 0 | 0 | 4 | none: 4 |
| [double-2026](system-pages/double-2026.md) | 49 | 39 | 36 | 0 | 10 | none: 46, official_worked_example_only: 3 |
| [dubov-2026](system-pages/dubov-2026.md) | 62 | 52 | 48 | 0 | 10 | none: 62 |
| [dutch-2026](system-pages/dutch-2026.md) | 90 | 78 | 76 | 0 | 11 | none: 90 |
| [dutch-interim-2025-source](system-pages/dutch-interim-2025-source.md) | 1 | 0 | 0 | 0 | 0 | none: 1 |
| [dutch-till2026-compat](system-pages/dutch-till2026-compat.md) | 2 | 1 | 1 | 0 | 1 | none: 2 |
| [knockout-boundary](system-pages/knockout-boundary.md) | 0 | 0 | 0 | 0 | 0 |  |
| [lim-2026](system-pages/lim-2026.md) | 52 | 43 | 40 | 1 | 9 | none: 51, official_worked_example_only: 1 |
| [olympiad-2022](system-pages/olympiad-2022.md) | 19 | 14 | 14 | 0 | 5 | none: 18, official_worked_example_only: 1 |
| [team-2026](system-pages/team-2026.md) | 52 | 42 | 38 | 0 | 10 | none: 52 |
| [thp-product-boundary](system-pages/thp-product-boundary.md) | 10 | 0 | 0 | 0 | 10 | none: 10 |

## Known evidence gaps that remain visible

- Superseded source editions are indexed; the frozen legacy Dutch record remains grouped and is not a clause-complete map. F-0106 interim Dutch text is now recovered from the official Council-PDF URL as parsed content; its Handbook URL returned generic navigation and a reconstruction of the prior abbreviated PDF URL without `/DOC/` returned 404, though the prior record does not preserve the exact URL used. The PDF approval field is `dd/mm/yyyy`, source bytes/checksums are not retained, and no distinct F-0106 implementation is claimed.
- F-0106 C5/C9 minimize the PAB assignee's score and unplayed games; the Table of Changes states C9's purpose but does not state categorical fewer-games exclusion. The prior R-D24 categorical-exclusion claim is withdrawn; see the source-only historical record.
- Historical `dutch-till2026-compat` stays distinct from current Dutch-2026; its v0.1 golden tests are compatibility evidence, not a source oracle.
- C.04.4.2 Burstein Index calculation remains absent; callers must provide complete values and provenance. C.07 values are not presumed equivalent.
- Dutch C8 and Lim 3.10 remain partial; Lim scrutiny wording and its worked example conflict and remain disputed. Double/Team look-ahead remains only repository-tested.
- The correct C.05 parent page and linked Competition_Rules.pdf were inspected as parsed content. The PDF has approval/amendment history but no stated effective date; source status remains unknown. Varma restricted draws remain caller/arbiter scope.
- Olympiad 2022 content was retrieved, but currentness is bounded to the recorded search and does not prove no later rules exist; event-management rules remain caller-owned/out of scope.
- Fixture redistribution rights remain unresolved; see the [rights and fixture inventory](RIGHTS_AND_FIXTURE_INVENTORY.md).
- The closure queue keeps caller-owned, out-of-scope, disputed, partial, historical, and unmapped records visible.

## Navigation

[clause index](CLAUSE_INDEX.md) · [closure/boundary queue](CLAUSE_CLOSURE_QUEUE.md) · [source index](SOURCE_INDEX.md) · [rule/source/code/test matrix](RULE_SOURCE_MATRIX.md) · [rights/fixture inventory](RIGHTS_AND_FIXTURE_INVENTORY.md) · [system views](SYSTEM_COVERAGE.md)

Current readiness and audit findings remain authoritative in [GAP_REGISTER.md](../../audit/GAP_REGISTER.md); the separate acceptance gates are in [COMPLETION_STANDARD.md](../../audit/COMPLETION_STANDARD.md).
