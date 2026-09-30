# Public API Audit — pairing-core v0.1.0 (STAGE 1)

Source of truth: `src/pairing_core/__init__.py:33-48` (`__all__`) cross-checked
against defining modules. All items below VERIFIED by direct source inspection.

## 1. Explicit public API (in `__all__`)

### 1.1 `PlayerData` (frozen dataclass, `models.py:27-64`)

| Aspect | Detail |
|---|---|
| Purpose | Sole input record: one player's tournament state for one round |
| Fields | `id: int` (required), `pairing_no: int` (required), `rating: int` (required), `points: float` (required), `color_hist: str = ""`, `opponents: FrozenSet[int] = frozenset()`, `received_bye: bool = False`, `float_hist: str = ""` |
| Input validation | **None at construction** — frozen dataclass, no `__post_init__`. Negative ids, `pairing_no=0`, inconsistent histories all accepted at type level — VERIFIED (`models.py` has no validation code) |
| Exceptions | None raised by constructor |
| Side effects / determinism | Immutable (frozen); hashable provided `opponents` is a frozenset |
| Tested | Yes — every test builds `PlayerData` via `pd()` helper (`test_contract.py:12-17`) |
| Documented | Field-level docstrings VERIFIED (`models.py:35-55`) |

> Note: `rating` is **required but algorithmically unused** — `EnginePlayer.sort_key`
> (`models.py:433-434`) orders by `(-points, pno, id)` only, and no other module
> reads `.rating`. VERIFIED by grep (no `rating` reference outside
> `models.py`/`engine.py` normalization passthrough). Callers must still supply it.

### 1.2 `PlayerSnapshot` (legacy alias, `models.py:68`)

`PlayerSnapshot = PlayerData` (simple alias). Re-exported with a tolerant
`try/except ImportError` fallback (`__init__.py:21-24`). Purpose: allow donor
`chess-manager` code importing `PlayerSnapshot` to keep working. Intended as
public-compat alias — VERIFIED. No behavioral difference.

### 1.3 `PairingCard` (mutable dataclass, `models.py:75-93`)

Fields: `board: int`, `white_id: int`, `black_id: Optional[int] = None`,
`is_bye: bool = False`, `white_float: str = ""`, `black_float: str = ""`.
No validation, no invariants enforced (a card with `is_bye=True` and a
non-`None` `black_id` is constructible). `board` is assigned post-hoc by
`SwissEngine._assign_board_numbers` (`engine.py:378-390`). Mutable by design
(board renumbering mutates in place). Tested indirectly via `pair_set`/`paired_ids`
helpers. Documented with field docstrings.

### 1.4 `RoundResult` (mutable dataclass, `models.py:96-108`)

Fields: `round_number: int`, `pairings: List[PairingCard]`, `bye_player_id:
Optional[int]`. Empty result (`pairings=[]`, `bye=None`) is the defined
zero-player output (`engine.py:78-79`, tested `test_zero_players`). No
validation (e.g. no check that `bye_player_id` matches an `is_bye` card).

### 1.5 `PairingRequest` (frozen dataclass, `api.py:15-27`)

Fields: `players: List[PlayerData]`, `round_number: int = 1`,
`locked_pairs: List[Tuple[int,int]] = []`. No validation (empty players,
`round_number=0`, self-pairs all accepted at construction; errors surface in
`SwissEngine`). Tested (`test_engine_interface_equivalence`).

### 1.6 `PairingEngine` (ABC, `api.py:29-38`)

Abstract `pair(request) -> RoundResult` + concrete `name` property returning
class name. `pair` raises `NotImplementedError`. Stability: described as the
"Stable pairing interface" and "Canonical contract" — but this is v0.1.0 with
a single implementor; stability claim is **UNVERIFIED** beyond the docstring.

### 1.7 `NativeDutchEngine(PairingEngine)` (`api.py:41-55`)

`pair()` builds a `SwissEngine(players, round_number, locked_pairs)` and
returns `generate()`. Claimed "behavior identical" to `SwissEngine` —
VERIFIED by `test_engine_interface_equivalence` (pair-set + bye equality on a
6-player case). Lazy-imports `SwissEngine` inside the method (avoids import
cycle). Deterministic (delegates fully). No state held between calls.

### 1.8 `SwissEngine` (class, `engine.py:56-390`, exported but barely documented)

Constructor `SwissEngine(players, round_number, locked_pairs=None)`; method
`generate() -> RoundResult`. Exported in `__all__` but **absent from the
module docstring's "Public contract" list** (`__init__.py:7-10` lists
`pair_round` but not `SwissEngine`) — a minor export/doc inconsistency, VERIFIED.
Behaviorally the real engine; `NativeDutchEngine` is a thin wrapper. Tested
(`test_engine_interface_equivalence` line 133).

### 1.9 `pair_round(players, round_number, locked_pairs=None)` (`engine.py:35-50`)

Functional entry point; constructs `SwissEngine` and calls `generate()`.
`locked_pairs`: list of `(white_id, black_id)` tuples placed verbatim into
output after validation (existence, no self-pair, no repeat, no duplicate use,
legal color orientation — `engine.py:117-191`, `ValueError` on violation).
Tested: `test_locked_pairs`, `test_locked_repeat_raises`.

### 1.10 `validate_round(result, players)` (`validator.py:50-82`)

Pure function → `ValidationReport`. Never raises on bad input (unknown ids
produce findings, not exceptions — VERIFIED `_check_unknown_players`). Tested
(`test_validation_clean` asserts `is_valid` on a round-1 4-player result).

### 1.11 `ValidationReport` / `Finding` (`validator.py:143-232`)

`Finding`: `level` ∈ {ERROR, WARNING, INFO} (plain string class-attrs, not an
enum), `rule`, `message`, `board`, `player_id`. `ValidationReport`: `findings`,
`errors`, `warnings`, `has_errors`, `has_warnings`, `is_valid`
(`not has_errors`), `error_summary` (first 10), `error_count`,
`warning_count`. No serialization helpers (no `to_dict`/JSON) — VERIFIED absent.

### 1.12 `__version__ = "0.1.0"`, `__fide_reference__ = "C.04.2 + C.04.3 (effective 1 July 2025)"`

Informational constants, VERIFIED. The FIDE string is a *claim of reference*,
not a compliance certificate (see PAIRING_ENGINE.md §2).

## 2. Implicit public API (importable but not in `__all__`)

All of these are importable as `pairing_core.<module>.<name>` and several are
re-exported at top level only by accident of implementation:

- `validate_and_fix` (`validator.py:85`) — legacy adapter, NOT in `__all__`,
  NOT re-exported. Raises `ValueError` on illegal pairing; "fix" in the name
  is misleading (it never repairs — VERIFIED, body only validates). Implicit API.
- `ColorPref`, `ColorState`, `FloatStatus`, `EnginePlayer`, `compute_color`,
  `compute_floats`, `make_engine_players` (`models.py`) — internal runtime
  model, importable, used by engine/validator. Internal details.
- `build_brackets`, `Bracket`, `pair_all_brackets`, `assign_colors`,
  `is_legal_orientation`, `has_legal_assignment`, `float_pair_legal`,
  `select_bye_player`, `generate_exchanges`, etc. — algorithmic internals,
  importable but undocumented as public. Internal details.

Risk: Python offers no access control, so consumers *can* depend on any of
these; only §1 is the intended contract (see COMPATIBILITY.md).

## 3. Signatures summary (constructors / key methods)

```
PlayerData(id, pairing_no, rating, points, color_hist="", opponents=frozenset(),
           received_bye=False, float_hist="")
PairingCard(board, white_id, black_id=None, is_bye=False, white_float="", black_float="")
RoundResult(round_number, pairings=[], bye_player_id=None)
PairingRequest(players=[], round_number=1, locked_pairs=[])
PairingEngine.pair(request) -> RoundResult   (abstract)
NativeDutchEngine.pair(request) -> RoundResult
SwissEngine(players, round_number, locked_pairs=None).generate() -> RoundResult
pair_round(players, round_number, locked_pairs=None) -> RoundResult
validate_round(result, players) -> ValidationReport
```

No `async`, no generators, no context managers, no callbacks in public API.
No console scripts / entry points (VERIFIED — `pyproject.toml` has no
`[project.scripts]`). No serialization formats in public API.
