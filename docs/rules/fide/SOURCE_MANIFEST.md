# SOURCE MANIFEST — Retrieval Records + Legal Posture

## Copyright / licence discipline (§27; legally clean by construction)

- FIDE Handbook / Council / announcement texts are FIDE ©. This repository
  vendors **no bulk FIDE text**: facts are extracted in our own words with short
  necessary quotations only. Full documents live at official URLs in SOURCE_INDEX.md.
- No PDF binaries are committed in this wave (all local-artifact fields: "none —
  link + metadata only"). If a future wave manually retrieves article bodies,
  record here: filename, source URL, retrieval date, SHA-256, document version/date.
- Secondary licences respected: BBP Apache-2.0 (subprocess/oracle only, never
  vendored); JaVaFo custom free+attribution (no bundling); py4swiss MIT;
  echecs MIT; vendor tools proprietary (no inclusion).

## Retrieval records (this wave)

| Source ID | URL | Retrieved | Method | Artifact | Hash |
|---|---|---|---|---|---|
| F-0301 | fide.com …february-1-2026 | 2026-10-03 | webfetch full page | none (metadata) | n/a (HTML) |
| F-0302 | fide.com …july-1-2025 | 2026-10-03 | webfetch full page | none (metadata) | n/a (HTML) |
| F-0401 | tec.fide.com/endorsement | 2026-10-03 | webfetch full page | none (metadata) | n/a (HTML) |
| F-0101…F-0119 | handbook.fide.com chapters | 2026-10-03 | search excerpts + Council headers | none | n/a |
| F-0201 | doc.fide.com CM3-202517.pdf | 2026-09-30 / 2026-10-03 | headers verified | none | QUEUED (full binary) |
| F-0501 | C05Annex1 tables | 2026-09-30 | full retrieval | none (facts extracted) | n/a |
| F-0601 | OlympiadPairingRules2022 | 2026-10-03 | search-verified structure | none | n/a |
| S-0101…S-0108 | secondary URLs | 2026-09-30 → 2026-10-03 | fetch/search per SEARCH_LOG | none vendored | n/a |

## Queued (next wave, manual path)

- Q-01: full binary of CM3-202517.pdf → SHA-256 + version/date record.
- Q-02: manual browser fetch of F-0105/0108/0110/0112/0114/0115/0117 article bodies
  (handbook bot-protection blocks machine fetch) → per-article SHA-256 records.
- Q-03: direct re-verification of F-0106 chapter URL.
