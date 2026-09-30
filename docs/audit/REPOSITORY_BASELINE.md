# Repository Baseline — pairing-core (STAGE 1)

Status legend used in all Stage 1 documents: **VERIFIED** (confirmed against
source/tests/config), **PARTIALLY VERIFIED** (partly confirmed),
**UNVERIFIED** (claimed but not confirmed), **NOT IMPLEMENTED** (confirmed
absent), **UNKNOWN** (cannot be determined from this repository alone).

## 1. Identity — VERIFIED

| Item | Value | Evidence |
|---|---|---|
| Repository | `20kevit/pairing-core` | `pyproject.toml:14-15` (`project.urls.Repository`), `README.md:4` |
| Package name | `pairing-core` | `pyproject.toml:6` |
| Version | `0.1.0` | `pyproject.toml:7`, `src/pairing_core/__init__.py:30` (`__version__`) |
| Description | "Standalone FIDE Dutch Swiss pairing engine (extracted from chess-manager)" | `pyproject.toml:8` |
| License declaration | MIT (`license = { text = "MIT" }`) | `pyproject.toml:11` |
| Author | `20kevit` | `pyproject.toml:12` |
| FIDE reference claimed | `C.04.2 + C.04.3 (effective 1 July 2025)` | `README.md:8`, `src/pairing_core/__init__.py:31` |

## 2. Git baseline — VERIFIED (recorded 2026-09-30, read-only commands only)

| Item | Value |
|---|---|
| Current branch | `main` (`git branch --show-current`) |
| Current commit SHA | `2cb570b023a2f5f457b0716adc1e70d49631a251` |
| Commit message | `pairing-core 0.1.0: extract FIDE Dutch engine behavior-preserving from chess-manager domain/pairing` |
| Commit date | 2026-09-30 (short date from `git log`) |
| Repository status | **Clean** — `git status --porcelain` returned empty; `git status --short --branch` showed only `## main...origin/main` |
| Remotes | `origin  git@github.com:20kevit/pairing-core.git` (fetch + push) |
| Tags | `v0.1.0` (single tag) |
| Latest release/tag | `v0.1.0`, pointing at `2cb570b` |
| Diff vs `v0.1.0` | **None** — `git diff v0.1.0 --stat` empty; `git describe --tags --long --always` → `v0.1.0-0-g2cb570b` |
| Commit history | **Single commit** — `git log --oneline` shows exactly 1 commit; no prior history in this repo |
| Local changes | None (working tree clean) — VERIFIED |

## 3. What the single commit contains — VERIFIED

`git show v0.1.0 --stat` lists 19 files, +3801 insertions, 0 deletions
(trivially true for an initial import):

- `README.md`, `pyproject.toml`
- `src/pairing_core.egg-info/` (4 generated files: `PKG-INFO`, `SOURCES.txt`, `dependency_links.txt`, `top_level.txt`)
- `src/pairing_core/`: `__init__.py`, `api.py`, `bracket.py`, `bye.py`, `color.py`, `engine.py`, `exchange.py`, `floats.py`, `models.py`, `pairer.py`, `validator.py`
- `tests/__init__.py` (empty), `tests/test_contract.py`

No deletions, no renames are possible in a single-commit repo. There is no
`docs/`, no `.github/`, no CI config, no `LICENSE` file, no `CHANGELOG`,
no lock file in the commit — VERIFIED by `git show --name-only HEAD` and
filesystem listing.

## 4. Provenance claim — PARTIALLY VERIFIED

`README.md:3-4` and `src/pairing_core/__init__.py:4-5` claim the code was
"extracted verbatim (behavior-preserving) from `20kevit/chess-manager`
`domain/pairing/`". Evidence inside this repo:

- Supporting: `engine.py` contains `_normalize_input` and
  `_build_legacy_color_hist` shims for legacy `PlayerSnapshot`-style objects
  with `status`, `start_number`, `played_against`, `color_balance`,
  `last_color` attributes (`engine.py:314-431`) — consistent with an
  extraction from a larger domain model. `validator.py:85-136`
  (`validate_and_fix`) is explicitly marked "Legacy backward-compatible
  entry point". `pairer.py:244` contains a non-English (Persian) inline
  comment, consistent with a verbatim port rather than a clean rewrite.
- Against / missing: the `chess-manager` source is **not present** in this
  repo and was **not fetched** (read-only stage, no network dependency
  audit performed). Byte-for-byte equivalence with the donor cannot be
  confirmed from inside this repository.

Verdict: extraction provenance is **PARTIALLY VERIFIED** (internal legacy
shims corroborate the story; verbatim equivalence is **UNVERIFIED**).

## 5. Runtime environment observed (informational, not a baseline guarantee)

- `python3 --version` → `Python 3.12.3`
- `pip show pairing-core` → Version 0.1.0, editable install from
  `/opt/projects/pairing-core`, `Requires:` empty.
- `python3 -m pytest tests/ -q` → **15 passed in 0.11 s** (run read-only;
  no packages installed, no code changed).

## 6. Baseline conclusion

The repository is exactly at `v0.1.0` on `main`, clean, single-commit,
with no divergence between working tree, `HEAD`, and tag. This document
plus the git SHA above constitute the Stage 1 baseline. All downstream
audit documents take this state as ground truth.
