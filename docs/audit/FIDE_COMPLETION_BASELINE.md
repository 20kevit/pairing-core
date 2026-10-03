# FIDE Completion Baseline (completion-wave forensic start)

- Commit: `2fdba62` (branch `main`, clean tree)
- Tags: `v0.1.0`, `v0.2.0`; package version `0.2.0`
- Full suite: **262 passed, 10 skipped** (2026-10-03)
- Source validator: **OK (41 sources, 49 rules)**

## Implemented systems
- `dutch-till2026-compat` (frozen native kernel, F1 goldens = executable spec)
- Berger round-robin schedules (`round_robin`, validated vs C.05 Annex 1)
- Canonical API, TRF interchange, BBP/JaVaFo adapter edge (bring-your-own binaries)

## Partial / absent
- `dutch-2026`: explicitly rejected by resolver (not implemented)
- Dubov / Burstein / Lim / Double / Team / Baku: no engines

## Open research debt (from prior wave)
- G-01: full machine-readable bodies of 2026 chapters (F-0101/0103/0105/0108/0110/
  0112/0114/0115/0117) — PRIMARY-excerpt grade, not full text
- G-02: direct re-verification of F-0106 interim chapter URL
- G-03: resolved (E.5 float-bar claim withdrawn, W-01)
- G-04: pre-2026 archive chapter URLs for Dubov/Burstein/Lim
- Q-01/Q-02/Q-03: queued manual retrievals (Council bundle hash, article bodies)

## PRIMARY-excerpt (not full-text) sources
All of F-0101, F-0103, F-0105, F-0108, F-0110, F-0112, F-0114, F-0115, F-0117,
F-0106, F-0116, F-0118, F-0601 (structure/dates verified; article bodies pending).
Full-text in hand: F-0301, F-0302, F-0401 (fetched pages), F-0501 (Berger tables),
F-0201 (bundle headers, prior wave).
