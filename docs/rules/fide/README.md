# FIDE Authoritative Documentation — Repository Source of Truth

Evidence-first, versioned registry of the latest applicable FIDE pairing rules,
sufficient to drive subsequent implementation of pairing-core.

- Retrieval wave: **2026-10-03** (this wave) + 2026-09-30/10-02 (prior STAGE 2 wave).
- Baseline: `bf77d7f` / release `v0.2.0`. This wave changes **no pairing behavior**.
- Date discipline is mandatory: never write "FIDE rules" without
  document + revision/version + effective date (§26 of the wave brief).
- Copyright discipline: facts/rules are extracted **in our own words** with short
  necessary quotations only; no bulk FIDE text is vendored into this repository.
  Full documents live at their official URLs; this tree stores metadata,
  section references, and retrieval records.

## Layout

```text
docs/rules/fide/
  README.md                — this file (how to use the registry)
  SOURCE_INDEX.md          — master registry; every claim traces to a Source ID
  VERSION_TIMELINE.md      — chronological revision history
  CURRENT_STATUS.md        — per-system latest-source answers
  RULE_SOURCE_MATRIX.md    — Rule ID → Source ID → section/page/version
  SYSTEM_COVERAGE.md       — per-system specification completeness
  SECONDARY_SOURCES.md     — BBP / JaVaFo / vendors / papers (never primary)
  SEARCH_LOG.md            — what was searched, what succeeded/failed
  SOURCE_MANIFEST.md       — retrieval records + hashes (where applicable)
  FINAL_RESEARCH_REPORT.md — wave completion report (§33 of the brief)
  swiss/dutch.md           — Dutch (C.04.3) structured research note
  swiss/dubov.md           — Dubov (C.04.4.1)
  swiss/burstein.md        — Burstein (C.04.4.2)
  swiss/lim.md             — Lim (C.04.4.3)
  swiss/double.md          — Double Swiss (C.04.5) + Accelerated/Baku (C.04.7)
  team/olympiad.md         — Team Swiss (C.04.6) + Olympiad Pairing Rules
  round_robin/berger.md    — Berger / round robin (C.05 Annex 1)
  match/knockout.md        — KO / match / playoff boundary analysis
```

## Source-ID scheme

- `F-xxxx` — Tier 1 primary FIDE sources (Handbook, Council, TEC/SPP, fide.com).
- `S-xxxx` — Secondary technical references (BBP, JaVaFo, vendors, papers).
- Status values: `CURRENT` / `HISTORICAL` / `SUPERSEDED` / `UNKNOWN`.
- Statement classes (§13): `MANDATORY RULE` / `ALGORITHM STEP` / `DEFINITION` /
  `EXAMPLE` / `NOTE` / `RECOMMENDATION` / `IMPLEMENTATION GUIDANCE` / `HISTORICAL RULE`.

## Relationship to older research

`docs/research/*.md` (STAGE 2) remains the narrative research corpus.
This tree is the **auditable registry**: canonical Source IDs, exact URLs,
dates, supersession links. Where both cover the same fact, this tree wins on
provenance; the narrative docs win on depth. Known divergences are recorded in
`CURRENT_STATUS.md`, not silently resolved.

## Verification

`tools/validate_sources.py` checks index hygiene (unique IDs, required fields,
URL shape, status vocabulary, matrix back-references). It does **not** scrape
FIDE — sources are manually verified by a human-readable fetch trail in
`SEARCH_LOG.md`.
