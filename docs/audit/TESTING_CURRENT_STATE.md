# Testing Current State — pairing-core v0.1.0 (STAGE 1)

Suite: `tests/test_contract.py` (142 lines) + empty `tests/__init__.py`.
Runner config: `[tool.pytest.ini_options] testpaths = ["tests"]`
(`pyproject.toml:20-21`). Result at audit time: **15 passed** (read-only run,
nothing installed or changed). No coverage config, no markers, no fixtures.

## 1. Test inventory (all 15, VERIFIED by source)

| # | Test | Location | Class (per file) |
|---|---|---|---|
| 1 | `test_zero_players` — empty input → empty result, bye None | :42-44 | unit (edge) |
| 2 | `test_single_player_bye` — 1 player → 1 bye card, `bye_player_id==1` | :46-49 | unit (edge) |
| 3 | `test_two_players` — pair set {(1,2)} | :51-53 | unit |
| 4 | `test_four_round1` — {(1,3),(2,4)} | :55-57 | unit/golden-ish |
| 5 | `test_eight_round1` — {(1,5),(2,6),(3,7),(4,8)} | :59-62 | unit/golden-ish |
| 6 | `test_odd_five` — exactly 1 bye, all 5 appear | :64-67 | unit (edge) |
| 7 | `test_no_rematch` — 1v2 history respected | :71-80 | constraint |
| 8 | `test_bye_fresh_first` — repeat-bye player avoided | :82-86 | constraint |
| 9 | `test_locked_pairs` — preassigned (1,2) present | :88-91 | integration (locked path) |
| 10 | `test_locked_repeat_raises` — rematch lock → `ValueError` | :93-97 | failure-case |
| 11 | `test_color_absolute` — `ww` player never white | :99-106 | constraint |
| 12 | `test_validation_clean` — round-1 result `is_valid` | :108-112 | validator smoke |
| 13 | `test_repeat_and_reorder` — repeat identical + reversed input same pair set | :116-124 | determinism |
| 14 | `test_engine_interface_equivalence` — `pair_round` ≡ `NativeDutchEngine` ≡ `SwissEngine` | :126-135 | API-compat |
| 15 | `test_golden_round1_8players` — snapshot {(1,5),(2,6),(3,7),(4,8)} "do not change lightly" | :137-142 | golden/reference |

Helpers: `pd()` factory (:12-17), `make_players()` (:20-25),
`paired_ids()` (:28-34), `pair_set()` (:37-38, color-blind by design).

## 2. Classification

- Unit: 1–6, 11 — small direct engine calls. VERIFIED.
- Integration: 7–10, 12, 14 — engine+validator / engine+locked-path. VERIFIED.
- Golden/reference: 4, 5, 15 — hard-coded S1-vs-S2 round-1 expectations. **Weak
  goldens**: they assert the trivially-correct round-1 shape, not a complex
  mid-tournament snapshot. PARTIALLY VERIFIED value.
- Determinism: 13 (pair-set level only — color orientation not compared). VERIFIED gap.
- End-to-end / regression / property-based / randomized / conformance /
  performance / serialization / API-compat (beyond 14): NOT IMPLEMENTED —
  VERIFIED absent (no hypothesis, no fuzz, no benchmark, no external reference
  data, no multi-round tournament simulation).

## 3. Edge-case coverage matrix (required checklist)

| Case | Covered? | Evidence / gap |
|---|---|---|
| Odd player counts | Partial (5 players, 1 player, 0 players) | No 3/7/9-player or all-received-bye repeat-bye test |
| Byes | Partial (fresh-first, count==1) | No repeat-bye-allowed path, no bye color/float follow-up, no `validate_bye_selection` test |
| Repeated opponents | Yes (basic 4-player) | No dense-history / near-impossible-state test |
| Color balance / preferences | Partial (`ww` absolute only) | No balance-±2, `bb`, strong/mild, due-color, or conflict tests |
| Score brackets / floaters | **No** — zero bracket/float tests | No multi-score-group, downfloat ranking, 3×-float-bar, strict→relaxed pass tests |
| Tied scores / equal ratings | Implicit (all round-1 tests tie at 0.0) | No mid-tournament ties; rating unused and untested |
| Missing/zero ratings | No | `rating=0` path untested |
| Newcomers / withdrawn / late entries / unavailable | No | Silent `status` filter entirely untested |
| Preassigned pairings | Yes (happy + repeat-raises) | No color-illegal lock, duplicate-player lock, unknown-player lock tests |
| Forbidden/impossible pairings | Partial (one raises case) | No all-played-each-other, no step-cap, no odd-tail tests |
| Deterministic output | Partial (pair sets) | Colors, boards, float tags not asserted deterministic |
| Multiple valid pairings | No | First-wins choice never characterized |
| Pathological states | No | No large-bracket, no 100-player, no adversarial-history test |
| Validator depth | Minimal (one clean case) | No test asserting any ERROR/WARNING/INFO is ever produced |
| Exchange logic | No | `generate_exchanges` order never asserted |
| Serialization | N/A (no feature) | — |

## 4. Coverage quality verdict

The suite pins the **basic contract** (empty/single/even/odd small fields,
no-rematch, fresh-bye, locks, one absolute-color case, determinism smoke,
interface equivalence) and passes fully — VERIFIED. It does **not** exercise
the algorithm's distinctive machinery (brackets, floats, exchanges, bye
ordering nuances, validator severities, failure modes). A senior engineer
relying only on these tests would have no safety net for changes to
`pairer.py`, `floats.py`, `exchange.py`, `bracket.py`, or `color.py` beyond
the single `ww` case. Biggest missing pieces: float/bracket tests, validator
violation tests, impossible-pairing tests, multi-round simulation.
