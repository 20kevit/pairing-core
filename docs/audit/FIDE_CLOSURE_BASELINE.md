# FIDE Conformance Closure — Baseline (closure wave)

Date (UTC): 2026-10-03. Baseline commit: `973d5d2` (branch `main`).
Working tree: clean. Package version: `0.3.1`. Current release: `v0.3.1`.

## Verification commands (all run pre-change)

- `git rev-parse HEAD` → `973d5d20ff4459e02cb4e02e4dedfc5e646f18c6`
- `git branch --show-current` → `main`
- `git status --porcelain` → clean (no output)
- `python3 -m pytest tests/ -q` → **477 passed, 16 skipped** (75.4s)
- `python3 -m pairing_core.validator` → exit 0 (green)
- `python3 -m build` → `pairing_core-0.3.1.tar.gz` + wheel OK
- Hash-seed determinism (0/42, determinism+canonical+hostile): 45 passed each

## Starting conformance state (from FIDE_CONFORMANCE_MATRIX.md)

- 12 open interpretations: I-D-PAB, I-D-MDPVALID, I-T-C7, I-T-MATCH,
  I-T-C1FB, I-T-C3, I-L-334, I-L-38, I-L-412, I-L-44, I-L-55, I-O-RANK.
- 4 evidence gaps: U-O-823, U-O-88 (+ Dutch RSL pre-sizing and Double/Team
  full-completion lookahead recorded as approximations in the matrix;
  the closure brief counts 4 gaps — enumerated exactly in
  FIDE_REMAINING_ITEMS.md).
- 4 reported owner decisions: exact-search ceilings, I-T-C7 alternative,
  Olympiad PDF retrieval, Double C3 / forfeit-both extensions.

No code was modified before this baseline was recorded.
