# Dutch interim 2025 edition — source-only historical record

**System ID:** `dutch-interim-2025-source`<br>
**System status:** `source_recovered_not_implemented`<br>
**Sources:** [F-0106](../source-pages/F-0106.md)

## Scope and limitations

Historical C.04.3 source edition only; no runnable ruleset or implementation is claimed. The official Council PDF states application from 2025-07-01, but its approval-date field is the placeholder dd/mm/yyyy. The F-0107 frozen compatibility system and current F-0105 Dutch-2026 system remain separate.

Limitations:
- The Table of Changes describes C9 as intended to prevent missed-game players from receiving a PAB; the operative C5/C9 text is a minimization criterion, not a categorical fewer-games exclusion.
- No Pairing-Core implementation or named repository test maps specifically to this interim edition; any owner request for it requires a distinct versioned ruleset and tests.

## Clause-level view

The rows below preserve source wording cues and project readings separately from implementation and repository tests. They are not a conformity result.

| Clause ID | Section | Source cue / reading status | Project paraphrase | Implementation | Verification | Code/tests | Test scope | Closure |
|---|---|---|---|---|---|---|---|---|
| [F-0106:interim-PAB](../source-pages/F-0106.md#f-0106-interim-pab) | 2.8.1; 3.3.1 (C5); 3.4.4 (C9) | Minimise the score of the assignee of the pairing-allocated-bye. / textual_cue_recorded | The interim Dutch text says to minimise the PAB assignee’s score (C5) and the assignee’s unplayed games (C9). Its Table of Changes describes C9 as intended to prevent participants who missed a game from receiving a PAB; the source does not state a categorical fewer-games exclusion. | `not implemented` | `none` | none mapped | No test is linked as evidence for F-0106. tests/test_hostile_audit.py::test_dutch_pab_emerges_from_generation_order and ::test_dutch_pab_global_best_beats_per_taker_first exercise the F-0105 Dutch-2026 path; tests/test_v010_behavioral.py::test_engine_golden pins frozen F-0107-era behavior. Neither establishes F-0106 behavior. | Retain this recovered interim text as a source-only historical record; do not map it to the F-0107 frozen compatibility kernel or F-0105 Dutch-2026 implementation. The prior “fewer-games players excluded” claim is not supported as a categorical rule: C9 minimizes unplayed games and C2 separately blocks the specified prior PAB/win-value cases. If the project owner requires exact interim-2025 support, make a separate versioned-ruleset decision and add source-specific implementation and adversarial tests. |

For all systems and aggregate counts, see [coverage dashboard](../COVERAGE_DASHBOARD.md) and [complete clause index](../CLAUSE_INDEX.md).
