# STAGE 1 Current-State Report — pairing-core v0.1.0

## 1. Exact repository state

`20kevit/pairing-core` at `main` = `2cb570b` = tag `v0.1.0`, working tree
**clean**, single-commit repo, no divergence (REPOSITORY_BASELINE.md). 19
tracked files: 10 source modules (~3.7k lines incl. tests), 1 test file
(15 tests, all passing), `pyproject.toml`, `README.md`, committed `egg-info/`.
No CI, docs (pre-audit), LICENSE file, CHANGELOG, lock files, CLI, or I/O.

## 2. Architecture

Zero-dependency src-layout library. `api.py` (thin adapter) → `engine.py`
(`SwissEngine` orchestration: normalize → locked pairs → bye loop → brackets
→ board numbering) → `pairer.py` (recursive Dutch search with transposition
DFS + exact matching-pruning + dead-end caches + 2M-step cap) fed by
`bracket`/`color`/`floats`/`exchange`/`bye` units over the `models.py`
substrate; `validator.py` sidecar (independent, caller-invoked, never
self-run). No Flask/SQLAlchemy/persistence/network/subprocess/threads
(ARCHITECTURE_AUDIT.md). Tournament-management boundary is clean except one
silent legacy `status` filter.

## 3. Domain

`PlayerData` in (id, pairing_no, rating[unused], points, color_hist,
opponents, received_bye, float_hist) → `EnginePlayer` runtime (derived
`ColorState`/`FloatStatus` + search flags) → `PairingCard`/`RoundResult` out
with `D`/`U` float tags. No results/standings/tournament objects, no
serialization, no roll-forward helpers; caller owns all inter-round state
(DOMAIN_MODEL.md).

## 4. Current engine

Dutch-family score-bracket search, two passes (strict then relaxed floats,
absolute bars never relaxed), first-legal-in-FIDE-order wins. Deterministic
(no entropy; ordering by points/pno/id). FIDE-conformance is **claimed, not
proven**: no handbook, no traceability matrix, no reference corpus
(PAIRING_ENGINE.md §2). Notable risks: search-completeness suspect
(first-local shortcut vs docstring, §5.1); upfloat-constraint path looks dead;
greedy bye choice; exponential worst case bounded only by step cap.

## 5. Public API

14 `__all__` names: `PlayerData`/`PlayerSnapshot`, `PairingCard`,
`RoundResult`, `PairingRequest`, `PairingEngine`, `NativeDutchEngine`,
`SwissEngine` (export/doc inconsistent), `pair_round`, `validate_round`,
`ValidationReport`, `Finding`, version/FIDE constants. No validation at
construction; no entry points; implicit internal surfaces importable but not
contracted (PUBLIC_API.md). v0.1.0 preliminary compatibility contract recorded
(COMPATIBILITY.md).

## 6. Tests

15 contract tests pin small-field basics (empty/single/even/odd, no-rematch,
fresh-bye, locks, one absolute-color case, pair-set determinism, interface
equivalence, trivial round-1 goldens). Zero coverage of brackets, floats,
exchanges, bye nuances, validator violations, impossibility, multi-round play,
performance, or property/conformance testing (TESTING_CURRENT_STATE.md).

## 7. Dependencies / packaging

Zero runtime deps (pure stdlib); build `setuptools>=68`; `requires-python
>=3.10` (floor only, no matrix); no classifiers/entry points/test-deps;
MIT declared without LICENSE text; committed `egg-info/` staleness risk
(DEPENDENCIES.md).

## 8. Capabilities / limitations / risks / unknowns

- Capabilities: Dutch Swiss PARTIAL; determinism SUPPORTED; rematch SUPPORTED;
  bye/color/float/validation PARTIAL; everything else (RR, teams, KO, TRF/CLI,
  BBP/JavaFo, benchmarks) ABSENT (CURRENT_CAPABILITIES.md).
- Limitations: 14 confirmed (A1–A14), 6 suspected (B1–B6), 7 unknowns (C1–C7),
  8 missing-capability groups (D1–D8) — see CURRENT_LIMITATIONS.md. Top risks:
  **search-completeness question, silent input absorption, dead-weight rating,
  flat error model, untested float/bracket machinery, no conformance basis**.
- Unknowns center on donor equivalence, FIDE-text traceability, and scale
  envelope (OPEN_QUESTIONS.md, 11 questions).

## 9. Compatibility baseline

v0.1.0 behaviors consumers may already depend on (round-1 shapes, bye-last
boards, fresh-bye preference, `ValueError` signals, severity split, silent
normalization) are recorded as the contract future stages must preserve or
deliberately version (COMPATIBILITY.md).

## 10. Evidence references

Every document cites `file:line` evidence; the full map + live-probe log is in
EVIDENCE_INDEX.md. Audit performed READ-ONLY: no source/config/test/packaging
change, no installs, no commits (only `docs/audit/*.md` created — 14 files:
this report + the 13 companions listed in the task brief, with the
documentation audit folded into EVIDENCE_INDEX.md and ARCHITECTURE_AUDIT.md §9
since no prior docs structure existed to displace).

## 11. Stage 2 handoff

Stage 2 research questions are listed in OPEN_QUESTIONS.md (FIDE text, donor
diff, completeness proof-case, contract tiering, benchmarks, test strategy).
No design decisions taken. Awaiting explicit Stage 2 authorization — STOPPING
here per instructions.
