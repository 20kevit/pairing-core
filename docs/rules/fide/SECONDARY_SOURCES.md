# SECONDARY SOURCES — BBP / JaVaFo / Vendors / Papers

Secondary evidence. Must NEVER silently override FIDE primary text. Uses: clarify
implementation details, identify historical behavior, find examples, detect
ambiguities, build differential tests. Retrieved 2026-10-03 (detailed research
passes 2026-09-30/10-02; licence posture from repo docs).

## Engines / libraries

### S-0101 — BBP Pairings
- URL: https://github.com/BieremaBoyzProgramming/bbpPairings
- Licence: Apache-2.0 (vendoring OK w/ NOTICE; subprocess use clean).
- Scope: C++ pairing-only engine, JaVaFo-1.4-compatible CLI; README states 2025
  Dutch rules; TRF-2026 with backward compat to TRF(bx)/TRF(x).
- Burstein: self-declared "flawed… not endorsed" — NEVER a Burstein oracle.
- Live evidence: built commit 8f9e3c5 (2026-07-30); float repetition = weighted
  minimisation only (no absolute bar — dutch.cpp); C9 minimisation weights;
  round-1 E.5 parity demo; 42-tournament differential vs native (see
  DUTCH_CONFORMANCE_STATUS §7–§10).
- Conformance mapping: BBP behavior → FIDE rule → ruleset/version → status lives in
  docs/research/DUTCH_CONFORMANCE_STATUS.md (unchanged by this wave).

### S-0102 — JaVaFo (Roberto Ricca, SPP/TEC)
- URLs: https://www.rrweb.org/javafo/JaVaFo.htm ; AUM `aum/JaVaFo2_AUM.htm/.pdf` ;
  integration https://www.rrweb.org/javafo/JaVaFo1.html
- Terms: free of charge provided `rrweb.org/javafo` cited in commercial products +
  author notified (javafo@rrweb.org). NO OSI licence — bundling UNKNOWN, subprocess OK.
- Scope: Java engine for Dutch C.04.3; v2.2 (2017-rules lineage per own 092 tag;
  v1.4 = 2013-rules). TRF(x) codes (XXC/XXZ/XXP/XXA/XXS/XXC/XXR), `-b` Baku flag,
  `-c` checklist/FPC mode, hash-seeded R1 colour.
- Live evidence: v2.2 b3223 differential (10 tournaments) in DUTCH_CONFORMANCE_STATUS §10.

### S-0103 — py4swiss (Moritz72)
- URL: https://github.com/Moritz72/py4swiss (PyPI py4swiss)
- Licence: MIT own code; /cpp from bbpPairings stays Apache-2.0.
- Scope: TRF(x) in; `dutch` (≈BBP pre-2026), `dubov` (from-2026 vs CPPDubovSystem),
  `burstein` (from-2026, stated immature).

### S-0104 — echecs trf + swiss (echecsjs)
- URLs: https://trf.echecs.dev/ + https://github.com/echecsjs/trf ;
  https://swiss.echecs.dev/ + https://github.com/echecsjs/swiss
- Licence: MIT (both).
- Scope: TRF16/26 + TRFx parser; `pair(players,games)` for 6 systems via subpaths
  (Dutch, Dubov, Burstein, Lim, Double, Team) — claims only, no conformance evidence.

### S-0105 — Vendors: Vega/Orion, Swiss-Manager
- Vega https://www.vegachess.com/ (proprietary; 50€/25€ edu; Linux freeware):
  Dutch via JaVaFo + Dubov/Lim/Burstein/Dutch-variant/USCF/RR/Baku; endorsements
  Dutch Istanbul-2012 + Goynuk-2017, Dubov Turin-2006 (older rules).
- Swiss-Manager https://swiss-manager.at/ (150€/75€ light): FIDE mode = JaVaFo
  engine (endorsed Minsk-2018 v13.0.0.11); own engine/Gacrux option; Baku +
  other accelerations; manual/forced/forbidden pairings.

### S-0106 — TEC Dutch tutorials (FIDE-hosted, explanatory — treat as secondary)
- https://tec.fide.com/annotateddutchv2026/
- https://tec.fide.com/2026-fide-dutch-terms-and-definitions/
- https://tec.fide.com/wp-content/uploads/2026/07/Mastering_the_Dutch_2026.pdf
  (Held tutorial: 2024 PPB/CLB removal + PAB-min-score rule; M1/M0/x/z/MaxPairs concepts)
- Grade: FIDE-hosted but explanatory; corroborates [C1]–[C21] structure, never a
  substitute for Handbook article text.

### S-0107 — Papers / studies
- Held IA, *SWISS DUBOV AND FIDE SWISS (DUTCH) – A COMPARISON* (15k-tournament
  simulation, manuscript): http://tec.fide.com/wp-content/uploads/2024/10/Dubov-vs-FIDE-Swiss.pdf
- Milvang outcome distribution (~4M games): https://pairings.fide.com/images/stories/downloads/2016-probability-of-the-outcome.pdf ;
  Baku/acceleration analysis: http://tec.fide.com/wp-content/uploads/2024/10/AcceleratedPairing-v6.pdf
- Sauer/Cseh/Lenzner arXiv:2112.10522 (max-weight-matching critique; uses Milvang
  distribution). NOTE: no single "Held/Milvang BBP arXiv paper" exists — prior
  phrasing corrected.
- Use: motivation/context only, never rules.

### S-0108 — Table explainers
- chesspairings.org RR guide: https://chesspairings.org/en/guide/round-robin-berger-tables
- Berger Explained (Gacrux): https://www.gacrux.no/spp/berger/BergerExplained.pdf
- Licence for all: not found (link + facts only).

## BBP / JaVaFo → FIDE mapping (summary; detail in DUTCH_CONFORMANCE_STATUS.md)

| Observed behavior | Reference | FIDE rule | Ruleset | Conformance |
|---|---|---|---|---|
| Round-1 E.5 parity (even-pno black) | BBP live demo | E.5 | till-2026 | native DEVIATES (frozen) |
| No absolute float bar (weighted minimisation) | BBP source | C14–C17 frame | 2026 | native over-strict (frozen; 2026 engine dissolves) |
| C9 unplayed-games minimisation | BBP fixture + source | C9 | 2026 | IMPLEMENTED (additive, pinned) |
| PAB = U-coded, win-valued | BBP source + live | C.04.1 art.3 | 2026 | caller-side (unmodelled value) |
| XXR>0 + initial colour required | BBP live rejects | input completeness | engine-level | adapter concern, not FIDE |
| JaVaFo 092 = 2017 vintage | JaVaFo own tag | n/a (vintage marker) | 2017 Dutch | read disagreements accordingly |
| BBP Burstein flawed | BBP README | n/a | previous Burstein | NEVER oracle |
