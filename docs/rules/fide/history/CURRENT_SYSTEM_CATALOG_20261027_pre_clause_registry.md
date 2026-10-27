> **Historical snapshot — preserved before the clause-registry migration (2026-10-27).** This file records the earlier research wave and is not the current source, coverage, or readiness authority. Use the current [source index](../SOURCE_INDEX.md), [source manifest](../SOURCE_MANIFEST.md), [rule/source matrix](../RULE_SOURCE_MATRIX.md), [system catalog](../CURRENT_SYSTEM_CATALOG.md), and [coverage dashboard](../COVERAGE_DASHBOARD.md); current audit findings are in [`GAP_REGISTER.md`](../../../audit/GAP_REGISTER.md). The original findings below are retained rather than silently rewritten.

# FIDE system source catalog (reviewed 2026-10-27)

This catalog records system identifiers and the source/effective-date context.
It does not certify code. Source availability, implementation, independent
evidence, production suitability, formal evaluation, and endorsement are
separate questions. Current implementation findings and readiness status are
authoritatively recorded in [`../../../audit/GAP_REGISTER.md`](../../../audit/GAP_REGISTER.md)
and [`../../../audit/COMPLETION_STANDARD.md`](../../../audit/COMPLETION_STANDARD.md).

| Pairing identifier | Source | Approval/effective date | Current Pairing-Core note |
|---|---|---|---|
| `dutch-till2026-compat` | Historical pre-2026 Dutch formulation | Superseded for current Swiss rules | Frozen compatibility behavior; documented deviations remain. |
| `dutch-2026` | C.04.3 | Council approved 2025-10-28; effective 2026-02-01 | Code exists; exact-search ceiling and documented interpretations remain. |
| `dubov-2026` | C.04.4.1 | Council approved 2025-10-28; effective 2026-02-01 | Code exists; rating/history inputs are caller-owned. |
| `burstein-2026` | C.04.4.2 | Council approved 2025-10-28; effective 2026-02-01 | Pairing code requires complete external C.04 Index values after Dutch seeding; no local Index calculation. |
| `lim-2026` | C.04.4.3 | Council approved 2025-10-28; effective 2026-02-01 | Code exists; documented scrutiny/order readings remain. |
| `double-2026` | C.04.5 | Council approved 2025-10-28; effective 2026-02-01 | Code exists; event match facts are caller-owned; bounded lookahead is a strategy. |
| `team-2026` | C.04.6 | Council approved 2025-10-28; effective 2026-02-01 | Code exists; team composition, lineup and score valuation are caller-owned. |
| `baku` helper | C.04.7 | Council approved 2025-10-28; effective 2026-02-01 | Helper functions only; event integration is caller-owned. |
| `olympiad-2022` | Olympiad Pairing Rules | Council approved 2021-10-27; effective 2022-01-01 | Separate dated team system; evidence and event assumptions differ from C.04. |
| Berger round robin | C.05 Annex 1 | Handbook annex; no separate effective date identified on page | Official schedules for 3–16 players are pinned by exact tests; double-cycle reversal is recommended, not mandatory. |
| KO/match/playoff orchestration | General competition context | Event-dependent | Tournament-management and bracket orchestration remain outside the library boundary. |

For C.07 tie-break regulations and C.02.03 THP requirements, see the audit
register. The separate `tiebreak-core` v1.2.0 library was inspected; its C.07
calculations are not assumed equivalent to C.04.4.2 Burstein Index values.
