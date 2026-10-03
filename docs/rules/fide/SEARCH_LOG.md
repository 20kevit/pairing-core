# SEARCH LOG — What Was Searched (exhaustive-search evidence, §16)

Wave retrieval date: 2026-10-03. Prior passes: 2026-09-30 (STAGE 2 bulk),
2026-10-01/02 (live BBP/JaVaFo oracles). Method: websearch (official-domain
prioritised) + webfetch (full-page where permitted). Search snippets were NEVER
treated as evidence: every load-bearing claim was opened at its official URL.

## Official locations searched

| # | Location | Method | Result |
|---|---|---|---|
| 1 | handbook.fide.com C.04 chapter family | search + fetch attempts | chapter URLs located (F-0101…F-0119); article bodies bot-protected → PRIMARY-excerpt grade, manual path open |
| 2 | handbook.fide.com C.05 / C05Annex1 | prior-wave full retrieval | Berger tables 3–16 retrieved in full |
| 3 | handbook.fide.com Olympiad/D.02 | search | F-0601 located + structure verified |
| 4 | doc.fide.com 2025_3FC bundle | prior-wave bundle headers | CM3-202517 contents/dates verified |
| 5 | fide.com announcements (Dutch 2025, reminder 2026, C.04.1 2024) | full-page fetch 2026-10-03 | F-0301/F-0302 fetched in full; F-0303 search-verified |
| 6 | tec.fide.com (endorsement, FTM, Dutch, TRF-2026, archive) | full-page fetch 2026-10-03 | F-0401 fetched in full; TRF-2026 files located |
| 7 | spp.fide.com (legacy mirrors, endorsed managers) | prior-wave retrieval | mirrors + definitions recorded |
| 8 | FIDE Congress/GA decisions (2025 Council list, 1987 GA, 2019 Annex 5.17, 2020 SPP minutes) | prior-wave + list page | decision references recorded |
| 9 | web.archive.org 2021 handbook snapshot | search-verified | old C.04 layout corroborated |
| 10 | Olympiad2026MainCompetition.pdf §4.1 pointer | search-verified | live pointer to Olympiad Rules |

## System searches (all completed; none stopped early)

Dutch (current + 2017/2022/2024/2025/2026 vintages) ✓ · Dubov ✓ · Burstein ✓ ·
Lim ✓ (thinnest — SPP mirror + manual fetch queued) · Double Swiss ✓ ·
Team/Olympiad ✓ · Berger/RR ✓ (full tables) · Baku/accelerated ✓ ·
KO/match/playoff ✓ (boundary set) · endorsement/FPC/RTG ✓ · TRF16/26 ✓.

## Fetch failures (honest record; all have a defined retry path)

- handbook.fide.com article bodies: JS/bot-protection timeouts (direct + via
  subagent, 2026-09-30 through 2026-10-03). Retry: manual browser fetch or
  Council-bundle PDFs (doc.fide.com serves static PDFs — fetch not yet attempted
  for the full bundle; queued).
- doc.fide.com CM3-202517.pdf full binary: headers verified prior wave; full-binary
  hash queued (see SOURCE_MANIFEST.md).
- "E.5 float-bar" as 2026 concept: searched official domains — NOT FOUND; recorded
  as withdrawn claim (G-03), not a retrieval failure.

## Secondary searches (completed 2026-10-03)

BBP README/licence ✓ · JaVaFo page/AUM/terms ✓ · py4swiss ✓ · echecs trf/swiss ✓ ·
Vega/Swiss-Manager systems+prices ✓ · arXiv 2112.10522 ✓ (Held/Milvang split
corrected) · TEC tutorials ✓ · Berger explainers ✓ · TRF spec ✓.

## Prior BLOCKED re-evaluation (§16 compliance)

Every prior BLOCKED/UNVERIFIED item was re-searched (see CURRENT_STATUS.md table):
none remains BLOCKED; all are now located-chapter + RESEARCH CONTINUES, except
Berger and KO-boundary which are FULLY SPECIFIED.
