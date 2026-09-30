# Evidence Index — pairing-core STAGE 1 (STAGE 1)

How to verify any claim in this audit: every substantive statement cites a
`file:line` pointer. This index maps claims → primary evidence. All paths are
relative to repo root at SHA `2cb570b` (see REPOSITORY_BASELINE.md).

## Source files (all read in full)

| File | Lines | Covers |
|---|---|---|
| `src/pairing_core/__init__.py` | 48 | exports, `__all__`, version/FIDE constants |
| `src/pairing_core/api.py` | 55 | `PairingRequest`, `PairingEngine`, `NativeDutchEngine` |
| `src/pairing_core/models.py` | 458 | `PlayerData`, outputs, color/float derivation, `EnginePlayer` |
| `src/pairing_core/engine.py` | 431 | `pair_round`, `SwissEngine`, locks, bye loop, normalization |
| `src/pairing_core/bracket.py` | 376 | `Bracket`, `build_brackets`, S1/S2, remainder ranking |
| `src/pairing_core/pairer.py` | 642 | search, DFS, pruning, caches, step cap, materialization |
| `src/pairing_core/color.py` | 249 | priority chain, legality gates |
| `src/pairing_core/floats.py` | 284 | 3-level float model, ranking, pair legality |
| `src/pairing_core/exchange.py` | 215 | exchange enumeration order |
| `src/pairing_core/bye.py` | 153 | bye ordering/selection/validation/card |
| `src/pairing_core/validator.py` | 635 | 16 checks, `ValidationReport`/`Finding`, legacy adapter |
| `tests/test_contract.py` | 142 | all 15 tests + helpers |
| `pyproject.toml` | 21 | build/meta/testpaths |
| `README.md` | 31 | claims, usage |
| `src/pairing_core.egg-info/*` | 4 files | generated manifest (PKG-INFO/SOURCES/top_level/dependency_links) |

## Key claim → evidence map

| Claim | Evidence |
|---|---|
| Clean tree at v0.1.0, single commit | `git status --porcelain` (empty), `git describe` → `v0.1.0-0-g2cb570b`, `git log --oneline` (1 entry) |
| Zero runtime dependencies | `pyproject.toml` (no `dependencies` key) + import scan (stdlib + intra-package only) |
| No CI/docs/license/changelog | filesystem + `git show --name-only HEAD` (19 files, none of these) |
| 15/15 tests pass | read-only `python3 -m pytest tests/ -q` → `15 passed` |
| Rating unused | `models.py:433-434` sort key; grep: no algorithmic `.rating` read; live probe (2800 vs 1200 identical shape) |
| Determinism (no RNG) | grep for random/shuffle/seed/subprocess/IO (no hits in `src/*.py`); `test_contract.py:116-124` |
| First-local-pairing shortcut vs docstring | `pairer.py:14-17` (docstring) vs `pairer.py:241-255` (code) |
| Silent `status` filter | `engine.py:322-324` + live probe (withdrawn player silently dropped) |
| `is_upfloater` only reset | `pairer.py:299-310`; no `= True` assignment found (grep) |
| `with_downfloaters` un-restored mutation | `bracket.py:264-284` vs `_recurse_with_downfloaters` save/restore `pairer.py:299-310` |
| Greedy bye choice | `engine.py:267-292` (return on first success) |
| Odd-tail returns None | `pairer.py:313-328` |
| Engine never calls validator | no `validate_round` reference in `engine.py`/`pairer.py` (grep) |
| `validate_and_fix` never repairs | `validator.py:85-136` body |
| Flat `ValueError`-only errors | raise-site grep list (see ARCHITECTURE_AUDIT.md §6) |
| Export/doc inconsistency (`SwissEngine`) | `__init__.py:7-10` (omitted) vs `:33-48` (`__all__` includes) |
| Non-English comment | `pairer.py:244` |
| Priority-1 wording imprecision | `color.py:50` vs `models.py:266-269` |
| Bye order double-negation correct | `bye.py:146-152` + live 3-player probe (bye → pno 3) |
| Float `-` breaks streak | `models.py:340-360` + live probes (`--D-U`, `DD`) |

## Live probes run (read-only, no installs, no code changes)

1. Rating swap (2800 vs 1200) → identical pairing shape (rating unused).
2. `compute_color('ww')` → ABSOLUTE_BLACK/balance +2; `('')` → NONE.
3. `compute_floats('--D-U')` → 1 consecutive up; `('DD')` → 2 consecutive downs.
4. 3-player same-score field → `[(1,2),(bye 3)]`, bye to lowest-ranked (bye order).
5. Legacy `status="withdrawn"` object → silently excluded (filter behavior).

## Documentation audit note (existing docs)

Pre-audit docs consisted solely of `README.md` (31 lines): purpose/install/use
statements VERIFIED accurate against code (`pip install -e .` matches
setuptools backend; usage snippet imports/round-1 call succeed); FIDE reference
line is an uncited claim (UNVERIFIED, see PAIRING_ENGINE.md §2); "Layout" line
matches actual tree. No contradictions with code behavior found; incompleteness
(no API reference, no behavior notes, no license/test docs) is the gap. No
other documentation existed to audit.
