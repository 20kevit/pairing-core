# Architecture Audit — pairing-core v0.1.0 (STAGE 1)

Descriptive only — no redesign proposed (per Stage 1 rule 24).

## 1. Layering as found — VERIFIED

```
caller (tournament app, external)
  │  List[PlayerData] + round_number + locked_pairs
  ▼
api.py          PairingRequest / PairingEngine / NativeDutchEngine (thin adapter)
  ▼
engine.py       SwissEngine: normalize → locks → bye loop → brackets → boards
  ├──► bracket.py   Bracket, build_brackets (grouping/splitting)
  ├──► pairer.py    pair_all_brackets (recursive search, owns _Pair → PairingCard)
  │      ├──► color.py     assign/is_legal/has_legal
  │      ├──► floats.py    can_*/violation/rank/float_pair_legal
  │      └──► exchange.py  generate_exchanges (lazy import)
  └──► bye.py       ordering + select + create_bye_card
models.py       data substrate for all layers (stdlib only)
validator.py    sidecar: RoundResult + PlayerData → findings (never called by engine)
```

Dependency direction is clean: algorithm modules import only `models`
(+ `itertools`/`abc`/`dataclasses` stdlib); `engine` orchestrates; `api`
adapts; `validator` observes. No cycles except the deliberate lazy imports
(`api→engine` inside method, `pairer→exchange` inside function) — VERIFIED.

## 2. Coupling audit (domain × algorithm × I/O × app concepts)

- Domain↔algorithm: **moderate, by design**. `EnginePlayer` fuses domain facts
  (`data`, `_opponents`) with search scratch (`bracket_idx`,
  `is_downfloater/is_upfloater`). Search mutates shared instances rather than
  copying — the one coupling smell found (see §4).
- Algorithm↔I/O: **none**. No file, network, subprocess, env, clock, or stdout
  I/O anywhere in `src/` (grep VERIFIED; only stdlib data imports). Pure
  functions of input → output (modulo in-place board numbering).
- Serialization/file formats (TRF/CSV/JSON): **absent**, hence uncoupled — VERIFIED.
- CLI: absent. Persistence: absent. UI: absent.
- chess-manager assumptions (residue): `_normalize_input` legacy fields
  (`status`, `start_number`, `played_against`, `color_balance`, `last_color`,
  `color_history`/`float_history` aliases), `validate_and_fix` legacy shape
  adapter, `PlayerSnapshot` alias. These are **compat shims**, not live
  coupling (no Flask/SQLAlchemy imports — VERIFIED absent). Risk: they widen
  accepted input shapes without spec or tests.
- Tournament management: **correctly absent** — no registration, lifecycle,
  payment, accounts, ratings DB, result entry, publication, notifications,
  scheduling, admin workflows. The library consumes precomputed per-player
  state and returns board assignments. Boundary verdict: CLEAN — VERIFIED.

## 3. Existing boundaries (what's already separated)

- Public contract (`__init__`/`api`/`models`-public) vs internals: explicit
  `__all__`, though leaky by Python nature (see PUBLIC_API.md §2).
- Engine vs checker: `validator.py` recomputes from scratch, imports nothing
  from `engine`/`pairer` — genuine independence, VERIFIED.
- Color/float/bye/exchange as standalone stateless units with own docstrings:
  VERIFIED separable (each imports only `models`).
- Orchestration (`SwissEngine`) vs search (`pair_all_brackets`) vs enumeration
  (`exchange`): VERIFIED separated; `engine.py` owns bye loop + boards, which is
  why bye-choice greediness lives there, not in the search.

## 4. Missing boundaries / structural smells (observed, not fixed)

1. **Shared-mutable search state**: `Bracket.with_downfloaters`
   (`bracket.py:264-284`) sets `p.is_downfloater = True` on the *shared*
   `EnginePlayer` objects without save/restore (contrast
   `_recurse_with_downfloaters`' careful save/restore, `pairer.py:299-310`).
   Cached `Bracket` objects and reused player lists therefore carry stale
   flags across branches. Single-use per `generate()` call masks this in
   practice (fresh `make_engine_players` each call), but the invariant is
   implicit. VERIFIED asymmetry.
2. **Error taxonomy missing**: everything is `ValueError` (user error, search
   exhaustion, resource cap) — see §6.
3. **No validation boundary at ingress**: trusting constructor + silent
   coercions spread across `_normalize_input` instead of one explicit
   input-validation step producing typed errors.
4. **Board numbering as mutation**: `_assign_board_numbers` mutates cards
   in place and reorders the list — output identity is post-hoc, not
   constructed. Minor.
5. **Lazy imports** (`api.py:48`, `pairer.py:363`) hide two real dependencies
   from static readers; harmless at runtime, noted for completeness.

## 5. Tournament-management boundary (explicit determination)

The library does pairing only. It does NOT do (all VERIFIED absent):
player registration, tournament lifecycle/rounds management, payment, user
accounts, ratings database, result entry/standings, publication, notifications,
scheduling, admin workflows. It also does NOT do: history roll-forward
(caller recomputes `color_hist`/`float_hist`/`opponents`/`points`), requested-bye
accounting (trusts `received_bye` bool), or eligibility filtering — except the
one silent legacy `status` carve-out (DOMAIN_MODEL.md §5), which is the single
observed boundary leak and is untested/undocumented.

## 6. Error model — VERIFIED exhaustive list

Hierarchy: **flat** — builtin `ValueError` (9 raise sites: 7 locked-pair,
1 no-pairing, 1 bye-exhausted in `engine.py`; 2 step-cap in `pairer.py`;
1 odd-split in `bracket.py`, unreachable via engine since odd brackets always
carry a remainder path) plus `NotImplementedError` (abstract `pair`) plus
`ValueError` from `validate_and_fix`. No custom exception class exists.
Callers **cannot** distinguish user error (bad lock) from search exhaustion
(impossible tournament state) from resource exhaustion (step cap)
programmatically — only by substring-matching messages. `KeyError`/`TypeError`
from malformed inputs are possible but undocumented. Verdict: callers can
detect failure reliably (exception vs result) but cannot classify it — PARTIAL.

## 7. Determinism & reproducibility — VERIFIED

Same input → same output: YES by construction (no entropy, total ordering by
`(points, pno, id)` + deterministic caches keyed on ids/flags). Stable
ordering/tie-breaking: YES. Seeded randomness: N/A (none exists).
Reproducible failures: YES modulo message content (step counts not exposed in
messages; caches don't affect output, only speed — the pruning/caches are
exact, VERIFIED by code: they only skip provably-impossible states).
Determinism loss points: NONE found in code; the only untested (not broken)
axis is color-orientation stability under input permutation (tests compare
pair sets only).

## 8. Performance — theoretical (no measurements exist)

See PAIRING_ENGINE.md §6 for the analysis. Summary: sort-dominated fast path;
exponential worst case per bracket bounded only by exact pruning + 2M-step cap;
 bye loop multiplies bracket solves by candidate count. No benchmarks, no
profiling hooks, no step-count exposure. Scale table: 10 trivial; 50–100 fast
in normal Swiss spreads; 250+ depends entirely on score-group sizes (normally
small → fine); pathological single-group states risk `ValueError` via step cap
at any size. All estimates theoretical — clearly labeled, per instructions.

## 9. Security & robustness — VERIFIED by inspection

- Untrusted input: absorbed silently (see VALIDATION.md §3) — availability risk
  is low (no crash paths found for well-typed garbage), but semantic-corruption
  risk is real (bad histories produce confident wrong pairings; no warnings).
- Subprocess/filesystem/network/dynamic-exec (`eval`/`exec`/`pickle-loads`):
  **none** — grep VERIFIED absent. Imports are stdlib-data-only.
- Deserialization: none exists (nothing to attack).
- Path handling: none. Resource exhaustion: attacker-controlled `points`
  collisions could force many players into one bracket → exponential search →
  2M-step `ValueError` (bounded CPU, no hang: caches + cap VERIFIED). Recursion
  depth is bracket-count-bounded (not player-bounded), so no stack risk from
  large fields; transposition DFS is iterative-generator + recursion depth =
  pairs-per-bracket (could reach ~500 frames for a 1000-player single bracket —
  near but under default limit; PARTIALLY VERIFIED reasoning, untested).
- Dependency risks: zero runtime deps → minimal supply-chain surface (see
  DEPENDENCIES.md). `__pycache__` untracked; `egg-info` committed (staleness,
  not security).
- Overall: a pure in-memory deterministic library with a bounded search cap;
  no critical security surface found. Robustness gaps are semantic (silent
  acceptance), not memory/IO safety.
