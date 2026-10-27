> **Historical snapshot — preserved before the clause-registry migration (2026-10-27).** This file records the earlier research wave and is not the current source, coverage, or readiness authority. Use the current [source index](../SOURCE_INDEX.md), [source manifest](../SOURCE_MANIFEST.md), [rule/source matrix](../RULE_SOURCE_MATRIX.md), [system catalog](../CURRENT_SYSTEM_CATALOG.md), and [coverage dashboard](../COVERAGE_DASHBOARD.md); current audit findings are in [`GAP_REGISTER.md`](../../../audit/GAP_REGISTER.md). The original findings below are retained rather than silently rewritten.

> **HISTORICAL SNAPSHOT — preserved 2026-10-27, not current rights authority.** The phrase “legally clean by construction” below was not substantiated by a licence or permission review and is withdrawn as current guidance. No FIDE reuse licence or written redistribution permission was identified in this audit; the current link-only policy and source/fixture-specific caveats are in [`../SOURCE_MANIFEST.md`](../SOURCE_MANIFEST.md). This snapshot is retained to preserve the earlier finding, not to authorize reuse.

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

## Retrieval records (completion wave — full evidence set)

| Source ID | URL | Retrieved | Method | Artifact | SHA-256 |
|---|---|---|---|---|---|
| F-0201 (+F-0101/03/05/08/10/12/14/15/17) | doc.fide.com …/2025_3FC/CM3-202517.pdf | 2026-10-03 | curl+pdftotext, read in full (1,872 lines) | none vendored (/tmp) | `6b12df0e692d517624709ff79b1c55048e68f344d13e24f4c96748e7c846b93b` |
| F-0106 (interim Dutch) | doc.fide.com …/2024%201FC/2024_FC1_TEC_Dutch.pdf | 2026-10-03 | curl+pdftotext, read (312 lines) | none vendored | `e006e2d9f342198b5ad8d2367fb01423bebcf69b5d283a5310bd6606c3031770` |
| F-0106 TOCh | …/2024_FC1_TEC_Dutch_TOCh.pdf | 2026-10-03 | curl+pdftotext, read (92 lines) | none vendored | `384cdb61449d7567656ea00ff6934f924306c9633109245da21f6dc2f28ba474` |
| F-0101int/F-0103int (2025) | …/2024_FC1_TEC_Swiss.pdf + …_References.pdf | 2026-10-03 | curl+pdftotext, read (25+655 lines) | none vendored | `f61597e18c4480a8b1cde2ba4f03696476925d139ddacf5c80a78fb4cab21831` / `e1117bcb40a58daab2bc7f37aa99adef41097202853b7296058f21a3480b5259` |
| F-0601 Olympiad | doc.fide.com …/3FC2021/Annex 3.2.3…pdf | 2026-10-03 | curl+pdftotext, read in full (210 lines) | none vendored | `e7c995b923f40b024306394d60a54c996154b572b25997610139039fd832f017` |
| S-0106 Annotated Dutch V2026 | tec.fide.com …/2026/08/AnnotatedDutch-V2026-1.pdf | 2026-10-03 | curl+pdftotext (2,184 lines) | none vendored | `c0515191ff457cac80842d5d7e1ef8e7314b8d6b858cec4dd3024d8f7666e1de` |
| S-0106 Terms 2026 | tec.fide.com …/2026-fide-dutch-terms-and-definitions-1.pdf | 2026-10-03 | curl+pdftotext (165 lines) | none vendored | `e32c753a8854607bcbc2e6a4f6d21d537a42cf60d280b1dfe06c087b1e9a658c` |
| S-0106 Mastering Dutch | tec.fide.com …/2026/07/Mastering_the_Dutch_2026.pdf | 2026-10-03 | curl+pdftotext (3,346 lines) | none vendored | `00445682142f88899ecb7320ec49f027a9b38300a800ce1c76585e38dad745ca` |
| F-0301/F-0302/F-0401 | fide.com / tec.fide.com pages | 2026-10-03 | webfetch full page | metadata only | n/a (HTML) |

## Direct Handbook re-verification (2026-10-27 audit)

The current audit accessed official FIDE Handbook chapter pages directly via
Arena's page-fetch interface. Complete parsed page content was returned in one
or more chunks and read for the current texts listed below:

- C.04.1 Basic Rules; C.04.2 General Handling Rules; C.04.3 Dutch;
  C.04.4.1 Dubov; C.04.4.2 Burstein; C.04.4.3 Lim; C.04.5 Double Swiss;
  C.04.6 Swiss Team; and C.04.7 Accelerated Systems (all effective
  2026-02-01).
- C.05 Annex 1 Berger tables; Olympiad Pairing Rules (effective 2022-01-01);
  C.07 Tie-Break Regulations (effective 2026-03-01); and C.02.03 (effective
  2026-03-01).
- Official C.04 Annex 3 FIDE Endorsed Programs PDF, vintage 2022, checked for
  Pairing-Core's listing.

The page-fetch interface exposes parsed Markdown chunks, not the original
response bytes or downloadable HTML. No full source bodies are committed or
hashed; the audit therefore records official URLs, source identity/effective
dates, and retrieval date rather than claiming a source-text digest. The
complete source list and verified dates are in
[`../../../audit/GAP_REGISTER.md`](../../../audit/GAP_REGISTER.md). This is evidence
of which texts were read, not evidence that Pairing-Core implements them
conformantly.

## Prior-wave retrieval queue (status updated 2026-10-27)

- Q-01: raw CM3-202517.pdf binary/hash is not retained. Current effective
  rules were read directly from the official Handbook pages; a raw Council
  bundle hash is not required for the present audit.
- Q-02: CLOSED for the current C.04 chapters listed above by direct official
  Handbook page retrieval. Raw article hashes remain unavailable for the
  reason stated above.
- Q-03: direct re-verification of the superseded 2025 interim F-0106 chapter
  remains historical research debt and is not a current-rule source gap.

## Closure-wave retrieval (2026-10-03, F-0601 Olympiad chapter text)

- F-0601 chapter text: `http://web.archive.org/web/2023id_/https://handbook.fide.com/chapter/OlympiadPairingRules2022`
  (official Handbook content via archive; live handbook fetch blocked by
  bot-wall, doc.fide.com Annex URL 404). Retrieved 2026-10-03 via curl.
  HTML SHA-256: `f2b50d0346a679376fe7493ad56f40570a7d259337532227cc3edf604d97b0a3`
  (82,436 bytes); stripped article text (21,210 chars) SHA-256:
  `d92b378efbce05a3e16e45a2d422f318c08b89e3d954e1272c975be86c32ffbd`.
  Artifact: /tmp only, nothing vendored. Full §§1–11 read (8.x/9.x quoted
  into implementation docstrings). Closes U-O-823 and U-O-88.
- Direct PDF attempts (all failed, recorded): handbook
  `.../files/handbook/Olympiad2026MainCompetition.pdf` (inaccessible);
  doc.fide.com `.../3FC2021/Annex%203.2.3...pdf` (404 nginx);
  `web.archive.org/web/2024/...` (empty). Chapter HTML is the complete
  normative text (all articles + 15-table + 88-team example present).
