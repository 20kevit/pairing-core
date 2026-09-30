# Validation Audit — pairing-core v0.1.0 (STAGE 1)

Source: `src/pairing_core/validator.py` (635 lines) + engine-side checks in
`engine.py` + `bye.py`. All VERIFIED by source inspection.

## 1. What is validated, when, by whom

| Check | Rule code | Severity | When | Evidence |
|---|---|---|---|---|
| Active player missing from pairings | COMP-01 | ERROR | post-hoc, caller-invoked | `validator.py:239-257` |
| Paired id not in active list | COMP-02 / GEN-UNK | ERROR | post-hoc | `validator.py:259-265`, `315-335` |
| Player twice on boards | GEN-DUP | ERROR | post-hoc | `validator.py:273-290` |
| Self-pairing | GEN-SELF | ERROR | post-hoc (+ pre-engine for locked) | `validator.py:297-308`; `engine.py:148-153` |
| Repeat opponents | GEN-01 | ERROR | post-hoc (+ pre/in-search for engine) | `validator.py:342-359`; engine via `have_played` |
| 3rd consecutive same color | COL-02 | ERROR | post-hoc (+ in-search gate) | `validator.py:381-393`; `color.py:157-160` |
| Absolute color obligation violated | COL-ACO | ERROR | post-hoc (+ in-search gate) | `validator.py:395-407`; `color.py:169-173` |
| Balance would exceed ±2 | COL-01 | ERROR | post-hoc (+ in-search gate) | `validator.py:416-449`; `color.py:163-166` |
| Repeated pairing bye | GEN-03 | WARNING (if fresh alt exists) / INFO | post-hoc | `validator.py:506-541` |
| Multiple byes | GEN-02 | ERROR | post-hoc | `validator.py:514-518` |
| Strong color preference missed | COL-SCP | WARNING | post-hoc | `validator.py:472-497` |
| Mild color preference missed | COL-MCP | INFO | post-hoc | `validator.py:478-497` |
| 3rd consecutive float | FLO-01 | ERROR | post-hoc (+ in-search absolute bar) | `validator.py:607-635`; `floats.py` |
| 2nd consecutive float | FLO-01 | WARNING | post-hoc | `validator.py:615-634` |
| Board numbers non-sequential | BOARD | WARNING | post-hoc | `validator.py:548-563` |
| Locked-pair existence/repeat/dup/color | (messages, no codes) | `ValueError` raised | pre-engine | `engine.py:136-182` |
| Search step cap exceeded | (message) | `ValueError` raised | in-search | `pairer.py:368`, `418` |
| No legal pairing exists | (message + bracket summary) | `ValueError` raised | terminal | `engine.py:239-248`, `293-297` |

## 2. Timing: pre-engine, in-search, post-engine

- **Pre-engine** (fail-fast `ValueError`): locked-pair checks only. General
  input hygiene (duplicate ids, bad `pairing_no`, malformed histories,
  unknown locked ids aside) is NOT pre-validated — VERIFIED absent.
- **In-search** (absolute legality gates): rematch, color-absolute/balance,
  float absolute (+strong in strict pass). Strong/mild color and soft float
  preferences guide ordering but do not gate (except strong-float in pass 1).
- **Post-engine** (`validate_round`, fully independent recompute via
  `make_engine_players`): the 16-check table above. **Never invoked by the
  engine itself** — VERIFIED (no `validate_round` import/call in `engine.py`
  or `pairer.py`). The caller must remember to call it.

## 3. Invalid input / output behavior

- Invalid **input** (duplicates, `pairing_no=0`, garbage histories, `None`
  opponents for legacy objects): silently absorbed (defaults, ignores, or
  last-wins dict collapse). Only locked-pair violations raise. No
  `TypeError`/`KeyError` hardening; e.g. `None` points on legacy objects is
  coerced (`or 0.0`), but a non-numeric `points` string would raise an
  undocumented `TypeError` from sorting. VERIFIED by code paths.
- Invalid **output** (hand-built illegal `RoundResult`): `validate_round`
  reports findings; never raises, never repairs. `validate_and_fix` wrapper
  raises `ValueError` on errors — and despite its name performs zero repair
  (VERIFIED `validator.py:85-136`).
- Error messages: human-readable with board/player context (`Finding.__repr__`),
  but rule codes are ad-hoc strings (`GEN-01`, `COL-02`, …) with no published
  codebook and no stable-code guarantee.

## 4. Completeness assessment

- Structural validation (completeness/duplicates/self/unknown): **complete** —
  VERIFIED all four checks present.
- Absolute FIDE legality (rematch/color/float/bye-count): **complete at the
  level the engine models** — VERIFIED.
- Rule-aware quality validation (was the *best* FIDE pairing chosen, correct
  downfloater choice, correct S1/S2 handling, correct bye choice): **NOT
  validated** — the checker verifies legality + reports soft preferences, but
  cannot tell whether search-order shortcuts (cf. PAIRING_ENGINE.md §5.1) picked
  a suboptimal legal pairing. Structural, not optimality-aware — VERIFIED by
  absence of any search-order/first-vs-best check in `validator.py`.
- Result/consistency validation (standings arithmetic, history roll-forward,
  score plausibility): NOT IMPLEMENTED (no such inputs exist).
- Coverage gaps (VERIFIED absent): no check that `bye_player_id` matches an
  `is_bye` card; no check that exactly one bye exists when player count is odd
  (only that ≤1 exists); no check on float-tag correctness against bracket
  movement (tags trusted as emitted); no duplicate-`pairing_no` check; no
  `board` uniqueness check beyond sequentiality.

## 5. Taxonomy applied to this repo

- Input validation: WEAK (locked pairs only; otherwise trusting).
- Pairing legality validation: STRONG (absolute bars, both engine + checker).
- FIDE rule validation: PARTIAL (legality yes, optimality/conformance no).
- Result validation: NOT IMPLEMENTED (no results modeled).
- Consistency validation: PARTIAL (completeness/duplicates yes; id-uniqueness,
  history-plausibility no).
