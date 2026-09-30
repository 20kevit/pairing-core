# Dependencies & Packaging Audit — pairing-core v0.1.0 (STAGE 1)

Source: `pyproject.toml` (21 lines), `src/pairing_core.egg-info/*`, import scan
of all 10 modules. All VERIFIED.

## 1. Packaging metadata (complete transcription)

| Field | Value | Location |
|---|---|---|
| `build-system.requires` | `setuptools>=68` | `pyproject.toml:2` |
| `build-system.build-backend` | `setuptools.build_meta` | `:3` |
| `project.name` | `pairing-core` | `:6` |
| `project.version` | `0.1.0` | `:7` (static, duplicated in `__init__.py:30` — manual sync, no dynamic versioning) |
| `project.description` | `Standalone FIDE Dutch Swiss pairing engine (extracted from chess-manager)` | `:8` |
| `project.readme` | `README.md` | `:9` |
| `project.requires-python` | `>=3.10` | `:10` |
| `project.license` | `{ text = "MIT" }` (string only, no SPDX `license-expression`, no LICENSE file) | `:11` |
| `project.authors` | `[{ name = "20kevit" }]` (no email) | `:12` |
| `project.urls` | `Repository = https://github.com/20kevit/pairing-core` only | `:14-15` |
| `tool.setuptools.packages.find` | `where = ["src"]` (src-layout, auto-discovery) | `:17-18` |
| `tool.pytest.ini_options` | `testpaths = ["tests"]` | `:20-21` |
| Classifiers | **none** | VERIFIED absent |
| `dependencies` | **none** (no `dependencies` key at all) | VERIFIED absent |
| `optional-dependencies` | none | VERIFIED absent |
| Entry points / console scripts | none (`[project.scripts]` absent) | VERIFIED absent |
| Package exports | `pairing_core` (`top_level.txt` VERIFIED) | egg-info |

Supported Python versions "if stated": only the floor `>=3.10` is stated; no
upper bound, no `Programming Language :: Python :: 3.x` classifiers, no CI
matrix to evidence any version (observed interpreter 3.12.3 is environmental,
not contractual). `str.removeprefix`-style 3.9+ syntax avoided anyway; `X | Y`
annotations not used in runtime paths (`from __future__ import annotations`
only in `api.py`). 3.10-floor plausibility: UNVERIFIED by test matrix (no CI).

## 2. Dependency inventory

- Runtime: **zero**. Every module imports only stdlib (`dataclasses`, `enum`,
  `typing`, `abc`, `itertools`) + intra-package modules. VERIFIED by import scan.
- Build: `setuptools>=68` only.
- Test: `pytest` assumed (no declaration — `pyproject.toml` has no test
  dependency group; pytest availability is environmental). VERIFIED gap.
- Lint/type/build-extra: none declared.

## 3. Risk assessment

- Unnecessary dependencies: **none** (there are no dependencies to trim).
- Suspicious dependencies: **none**.
- Missing dependencies: `pytest` (and any lint/type tool) undeclared — a fresh
  checkout's test path relies on ambient tooling. Minor.
- Overly broad constraints: `setuptools>=68` unbounded above (low risk);
  `requires-python >=3.10` unbounded above (standard; forward-compat risk
  unmeasured but low for this code shape).
- Incompatible constraints: **none possible** (empty set).
- Dependency/license risks: **minimal** — pure-stdlib runtime means no
  transitive license exposure. The one license risk is self-inflicted: MIT is
  *declared* as a bare string with **no LICENSE file and no SPDX expression**,
  so downstream license scanners see a claim without text (see COMPATIBILITY.md).
- `egg-info` committed: `SOURCES.txt` enumerates 19 files including egg-info
  itself; regenerates on build. Staleness risk only.

## 4. Verdict

Packaging is minimal and correct for a zero-dependency src-layout library;
`pip install -e .` (README) matches the backend. Gaps are all in assurance,
not function: no classifiers, no test-deps declaration, no version matrix,
no license text. Nothing to change in Stage 1 (read-only).
