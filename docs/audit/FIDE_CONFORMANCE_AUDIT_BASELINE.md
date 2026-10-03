# FIDE Conformance Audit — Baseline (hostile audit wave)

Date (UTC): 2026-10-03. Baseline commit: `b418bbe` (branch `main`).
Working tree: clean. Package version: `0.3.0`. Previous release: `v0.3.0`.

## Verification commands (all run pre-change)

- `git rev-parse HEAD` → `b418bbea0c9e8cca1536de19cafdcb156fa5017d`
- `git branch --show-current` → `main`
- `git status --porcelain` → clean (no output)
- `python3 -m pytest tests/ -x -q` → **310 passed, 10 skipped** (21.3s)
- `python3 -m pairing_core.validator` → exit 0 (green)
- `python3 -m pytest tests/test_determinism.py -q` → 4 passed
- `python3 -m build` → `pairing_core-0.3.0.tar.gz` + `pairing_core-0.3.0-py3-none-any.whl` OK

## Implemented systems at baseline

| # | System | Engine | Ruleset label |
|---|---|---|---|
| 1 | Dutch 2026 (C.04.3) | `fide2026/dutch.py` (563 lines) | `dutch-2026` |
| 2 | Dubov 2026 (C.04.4.1) | `fide2026/dubov.py` (464 lines) | `dubov-2026` |
| 3 | Burstein 2026 (C.04.4.2) | `fide2026/burstein.py` (417 lines) | `burstein-2026` |
| 4 | Lim 2026 (C.04.4.3) | `fide2026/lim.py` (418 lines) | `lim-2026` |
| 5 | Double Swiss 2026 (C.04.5) | `fide2026/double_team.py` (385 lines) | `double-2026` |
| 6 | Team Swiss 2026 (C.04.6) | `fide2026/double_team.py` | `team-2026` |
| 7 | Baku acceleration (C.04.7) | `fide2026/baku.py` (63 lines) | pure functions |
| 8 | Olympiad 2022 (F-0601) | `fide2026/olympiad.py` (260 lines) | `olympiad-2022` |
| 9 | Berger (C.05 Annex 1) | `roundrobin.py` (114 lines) | `round_robin()` |
| 10 | Frozen legacy Dutch | `pairer.py`/`engine.py` + `dutch-till2026-compat` | legacy API |

Shared: `fide2026/common.py`, `fide2026/models.py`, `fide2026/api.py`.

## Authoritative sources available for this audit

- `/tmp/opencode/CM3-202517.pdf` (.txt, 1871 lines): Council bundle with full
  C.04.3 (Dutch), C.04.4.1 (Dubov), C.04.4.2 (Burstein), C.04.4.3 (Lim),
  C.04.5 (Double), C.04.6 (Team), C.04.7 (Baku). SHA matches SOURCE_MANIFEST.
- `/tmp/opencode/annotated.txt` (Annotated Dutch V2026) incl. 4.4.1/4.4.2
  validity + ordering commentary with worked MDP-set example.
- `/tmp/opencode/mastering_dutch_2026.txt`, `terms2026.txt`, `fide2026.html`.
- Olympiad F-0601 primary PDF **not** locally available (handbook fetch
  blocked); Olympiad audit rests on `docs/rules/fide/evidence/OLYMPIAD_EVIDENCE.md`.
- Nothing vendored into the repo (legal posture unchanged).

## Known evidence gaps at baseline (carried, to be closed or labelled)

- `docs/rules/fide/extracted/` references `DOUBLE_2026_RULES.md` and
  `OLYMPIAD_RULES.md`, which do not exist (only OTHER_2026_RULES.md covers them).
- Dutch PAB post-(score,unplayed) tiebreak: C.04.3 states no further rule.
- Double/Team "first … that complies" (3.5.5/3.6.4) vs minimise+order-tiebreak.
- Lim Art.4 numbering phrasing vs worked 4.2/4.3 tables; upward-search mirroring.

## Known implementation assumptions at baseline (to be hostile-audited)

- Dutch PAB "largest-TPN family convention"; Dutch C8 one-bracket restricted
  look-ahead; Double/Team min-vector+generation-tiebreak; Lim 3.9 folded into
  selection order; Burstein BSN-space fix from `deffe5d`; caller-duty typing
  for ratings/upfloats/result-codes/PAB valuations.

No code was modified before this baseline was recorded.
