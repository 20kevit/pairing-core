# FIDE Endorsement Research (STAGE 2, §2.12)

"Uses a FIDE-related engine" ≠ "FIDE endorsed". Endorsement attaches to a
(program, version, pairing system, engine) tuple via congress/PB decision.

## 1. Process (PRIMARY: SPP/TEC pages, endorsed-program tables, 2019 congress annex)

- Authority: FIDE Systems of Pairings and Programs Commission (SPP/SPPC),
  now under Technical Commission (TEC). References: C.04 Appendix A
  (endorsement appendix; FPC §A.4, RTG §A.5 per SPP page).
- Instruments: FPC = Free Pairings Checker (engine usable standalone without
  UI); RTG = Random Tournament Generator (full-TRF simulation; JaVaFo model:
  Milvang outcome formula, seed-recorded). Most JaVaFo-based programs satisfy
  FPC/RTG *through* JaVaFo; SwissSys through BBP; Swiss-Chess ships console
  FPC/RTG binaries.
- Verification: VCL checklist (e.g. VCL.04 pairing-service behaviour; VCL.19
  tie-breaks per Handbook — PRIMARY: 2019 minutes). Interim certificates
  possible (UTU/Tornelo/ChessManager 2019–20 show pass-then-interim flow).
- Maintenance: errors reported to supplier, classified major (pairing,
  tie-break) / minor; unfixed major → automatic suspension (PRIMARY: congress
  annex A.2.3). Certificates pin versions (e.g. Vega 7.6.0, SwissSys 9.6,
  Swiss-Manager 13, WinSwiss 9.05, Chess Online 7.7 in 2024).
- Current endorsed set (PRIMARY tables, latest seen): Vega, SwissSys,
  SwissMaster, Swiss-Manager, Swiss-Chess, UTU Swiss, ChessManager, STOP,
  TournamentService, Tornelo (+JavaPairing historically, Chess Online 7.7
  2024-04-13). Engines in the set: JaVaFo (most), bbpPairings (SwissSys),
  internal (Swiss-Chess, Vega-Dubov).

## 2. What endorsement would require of pairing-core (research reading)

1. A *program* (not just a library) with pinned version + system + engine
   identity; 2. FPC-equivalent (standalone checkable pairing function over TRF);
   3. RTG-equivalent or RTG-compatibility (thousands of seeded tournaments as
   test mass); 4. VCL-style checklist passing incl. tie-breaks *as implemented*;
   5. version-pinned re-endorsement on rule changes (cf. 2026 rewrite invalidates
   old Dutch endorsements in spirit — treat as UNKNOWN until TEC states it).
   Endorsement scope would cover the *checked artefact*, never "the library in
   general".

## 3. Honest positioning (no endorsement claimed)

Stage 3 sets "endorsement preparation" as a late-roadmap phase with
FPC/RTG-compatible artefacts (checker mode + seeded corpus tooling) as the
concrete enablers — NOT a promise of endorsement. Any public claim before a
certificate exists would be false.
