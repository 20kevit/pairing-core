# Domain Model Audit — pairing-core v0.1.0 (STAGE 1)

All claims VERIFIED against `src/pairing_core/models.py` (458 lines) unless noted.

## 1. Concept inventory

| FIDE/tournament concept | Representation in this repo | Status |
|---|---|---|
| Player | `PlayerData` (input) / `EnginePlayer` (runtime) | VERIFIED |
| Rating | `PlayerData.rating: int` — stored, passed through, **never read by algorithm** | VERIFIED (see §3) |
| Score | `PlayerData.points: float` — grouping key + sort key | VERIFIED |
| Color (history) | `color_hist: str` (`w`/`b`/`-`); `-` = no game | VERIFIED |
| Color preference/state | `ColorPref` enum; `ColorState` (balance, last, last_two, games_played, preference, due_color) | VERIFIED |
| Previous opponents | `opponents: FrozenSet[int]` | VERIFIED |
| Pairing / board | `PairingCard` (board, white_id, black_id, is_bye, floats) | VERIFIED |
| Round | `round_number: int` (opaque label; only echoed into `RoundResult` + error messages) | VERIFIED |
| Bye (pairing-allocated) | `PairingCard(is_bye=True, black_id=None)` + `RoundResult.bye_player_id` + `PlayerData.received_bye` input flag | VERIFIED |
| Float | `float_hist: str` (`D`/`U`/`-`) → `FloatStatus`; output tags `white_float`/`black_float` ∈ {`D`,`U`,``} | VERIFIED |
| Bracket / group | `Bracket` class (`bracket.py`) — score-homogeneous resident list + merged downfloaters | VERIFIED |
| Ranking / seed | `pairing_no` (initial number; lower = higher ranked) — the **only** ordering key besides score | VERIFIED |
| Pairing history (results) | **NOT modeled** — no win/loss/draw, no result entry, no standings computation | NOT IMPLEMENTED |
| Constraints / exclusions | Rematch set + absolute color + absolute float; `locked_pairs` preassignments | VERIFIED (partial — see §6) |
| Tournament / lifecycle | **NOT modeled** — no tournament object, rounds list, registration, withdrawals (but see silent `status` filter §5) | NOT IMPLEMENTED |
| Engine / rules / validation | `SwissEngine`/`NativeDutchEngine`; `validator.py` rule codes | VERIFIED |
| Time controls, titles, federations, clocks, venues | Absent | NOT IMPLEMENTED |

## 2. Field-by-field semantics

### `PlayerData` (frozen dataclass — immutable, VERIFIED)

- `id: int` — unique player key. Uniqueness is **assumed, never validated**:
  duplicate ids would collapse in `player_map` dicts (`engine.py:132`,
  `validator.py:65`) with silent last-wins behavior. No test covers it.
- `pairing_no: int` — initial ranking; lower = stronger. Tiebreak in
  `EnginePlayer.sort_key` (`models.py:433-434`: `(-points, pno, id)`) and in
  every S1/S2 split, exchange order, bye order, downfloater order. The
  docstring says "typically assigned by rating desc, then title, then
  alphabetical" — **UNVERIFIED** (no assignment code exists here; caller-owned).
- `rating: int` — **write-only input**. VERIFIED unused: the audit probe paired
  rating-2800 vs 1200 with identical result shape, and `grep rating` shows no
  algorithmic read (only constructor passthrough + legacy normalization).
  Implication: initial ranking is 100% caller-controlled via `pairing_no`.
- `points: float` — grouping key for brackets (exact float equality,
  `bracket.py:333-335`). Fractional scores (0.5) supported by type; no rounding.
- `color_hist: str` — chronological `w`/`b`/`-`. Only `w`/`b` counted
  (`compute_color`, `models.py:227`); all other chars (including `-` and
  garbage) silently ignored — no validation of alphabet or length-vs-round.
- `opponents: FrozenSet[int]` — symmetric rematch check (`can_meet`,
  `models.py:417-421`, checks both directions; `_PairingContext.have_played`,
  `pairer.py:126-141`, checks played_map both ways AND per-player sets).
  One-sided data still blocks pairing (defensive, VERIFIED).
- `received_bye: bool` — "True if player already received a
  pairing-allocated bye. Requested byes (half/zero) do NOT count" — the
  distinction is **caller-enforced and UNVERIFIED** here (a bare bool arrives;
  engine trusts it).
- `float_hist: str` — `D`/`U`/`-`; `-` **breaks** consecutive streaks
  (`compute_floats`, `models.py:321-370`). Total counts (`total_downs/ups`)
  count all-time occurrences; consecutive counts only the trailing run.

### `ColorState` derivation (`compute_color`, `models.py:225-282`) — VERIFIED

`balance = whites − blacks`; `games_played` = count of `w`/`b`;
`last`/`last_two` from played games only; `due_color`: negative balance → `w`,
positive → `b`, zero with history → opposite of last, else `""`.
`_classify_preference`: `ww`→ABSOLUTE_BLACK, `bb`→ABSOLUTE_WHITE,
`balance≥+2`→ABSOLUTE_BLACK, `≤−2`→ABSOLUTE_WHITE, `+1`→STRONG_BLACK,
`−1`→STRONG_WHITE, `0+last=w`→MILD_BLACK, `0+last=b`→MILD_WHITE, else NONE.
Note the docstring in `color.py:50` says "3 consecutive same color" while the
code triggers absolute on **2** (`last_two == "ww"`, `models.py:266-269`) —
the *effect* (3rd same color forbidden) matches FIDE, but the Priority-1
wording is imprecise (PARTIALLY VERIFIED, see CURRENT_LIMITATIONS.md §B).

### `FloatStatus` derivation (`compute_floats`, `models.py:321-370`) — VERIFIED

Trailing-run semantics with `-` as breaker; `last_dir` = last `D`/`U` in full
history (ignores `-`); `would_violate_down/up` = consecutive ≥ 2; probes during
audit confirmed `--D-U` → 1 consecutive up, `DD` → 2 consecutive downs.

### `EnginePlayer` (mutable runtime, `models.py:377-448`)

- `__slots__` runtime; holds `data`, `pno`, `color`, `floats`, `_opponents`,
  `bracket_idx`, `is_downfloater`, `is_upfloater` flags.
- Equality/hash **id-based** (`__eq__` compares `id`, `__hash__ = hash(id)`) —
  two records with same id but different data compare equal. **Hazard**:
  `exchange.py:208-209` uses `p not in s1_group` (list membership → `__eq__`),
  so duplicate ids would corrupt swaps. No test covers duplicate ids.
- Ordering: `sort_key = (-points, pno, id)` — rating plays no role. `id` is the
  final deterministic tiebreak everywhere it appears.
- Mutability: `bracket_idx`, `is_downfloater`, `is_upfloater` mutated during
  search (with save/restore in `_recurse_with_downfloaters`, `pairer.py:299-310`;
  but `with_downfloaters`, `bracket.py:264-284`, sets flags **without**
  restore — VERIFIED asymmetry, see ARCHITECTURE_AUDIT.md).

### `PairingCard` / `RoundResult` — see PUBLIC_API.md §1.3–1.4.

- Float output tags are set from runtime flags (`_Pair._ _init__`,
  `pairer.py:152-160`): a downfloater's side gets `D`, the opponent's side `U`.
  An upfloater flag (`is_upfloater`) is read in `float_pair_legal` but,
  per code inspection, `is_upfloater` is **only ever reset to False**
  (`pairer.py:303`) and never set True anywhere in the search — upfloat
  *constraint* path appears dead; upfloat *output tags* still emitted via the
  opponent-is-down logic. Status: PARTIALLY VERIFIED, flagged in OPEN_QUESTIONS.md Q6.

## 3. Invariants (stated vs enforced)

| Invariant | Stated | Enforced | Evidence |
|---|---|---|---|
| `pairing_no` fixed at start, unique | docstring | **No** (no check) | `models.py` has no `__post_init__` |
| `opponents` symmetric | assumed | Defensive both-ways reads | `models.py:417-421`, `pairer.py:126-141` |
| `color_hist` alphabet/length | docstring | **No** (garbage ignored) | `models.py:227` |
| One bye per player | FIDE rule | Soft: fresh-preferred, repeat allowed if all used | `engine.py:299-309`, `bye.py:62-71` |
| No 3× color / balance ±2 | FIDE rule | Yes (engine + validator) | `color.py:135-174`, `validator.py:366-449` |
| No 3× consecutive float | docstring "MUST NOT" | Yes (both passes) | `floats.py:63-112`, `pairer.py:68-80` |
| `id` uniqueness | assumed | **No** | dict-keyed maps throughout |

## 4. Relationships / lifecycle / serialization

- Relationships: `PlayerData` ─(opponent ids)→ `PlayerData`;
  `RoundResult` 1→N `PairingCard`; `Bracket` N→M `EnginePlayer` (shared refs,
  not copies); `EnginePlayer` →1 `PlayerData` (immutable source) + derived states.
- Lifecycle: caller builds `PlayerData` list → `make_engine_players` sorts by
  `sort_key` → `Bracket`s reference them → search mutates flags →
  `PairingCard`s emitted → engine returns; input list never mutated (VERIFIED —
  no write to `_raw_players` elements; only new `PlayerData` built in
  normalization). Caller is responsible for rolling results into next round's
  `color_hist`/`float_hist`/`opponents`/`points` — **no helper for this
  roll-forward exists** (NOT IMPLEMENTED, see CURRENT_LIMITATIONS.md).
- Serialization: **none** — no `to_dict`/`from_dict`/JSON/TRF/CSV anywhere
  (VERIFIED by grep for `json|to_dict|from_dict|dump|load` — no hits in
  `src/pairing_core/*.py` besides the finding). Dataclasses are pickle-able by
  accident, not by contract.

## 5. Hidden behavior: silent `status` filter — VERIFIED

`SwissEngine._normalize_input` (`engine.py:314-364`) drops any object with
`status != "active"` (default `"active"` when attr missing). Audit probe:
a `status="withdrawn"` player was silently excluded and the remaining player
got a bye. `PlayerData` itself has **no** `status` field, so this only affects
legacy donor objects — but the silent-drop (no warning, no report) is
confirmed behavior with no test coverage.

## 6. Dependency / relationship map (data flow)

```
caller data ──► PlayerData ──► EnginePlayer ──┬──► Bracket ──► S1/S2 ──► _Pair ──► PairingCard
                                              ├──► ColorState ──► color.py ──┘         │
                                              └──► FloatStatus ──► floats.py ─────────┘
played_map ◄── opponents (both directions checked)
bye: EnginePlayer.points/pno/id + received_bye ──► bye.py ──► PairingCard(is_bye)
validator: RoundResult + PlayerData ──► findings (independent recompute via make_engine_players)
```

`rating` has no outgoing edge in this graph (VERIFIED dead weight at v0.1.0).
`round_number` flows only to `RoundResult.round_number` and error strings.
