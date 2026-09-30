# Stage 2 Research Report (STAGE 2 GATE + second pass)

## 1. Coverage check (§2.1–2.14)

Swiss systems (Dutch/Dubov/Burstein/Lim/Double/Team/accel) in FIDE_SYSTEMS.md;
Dutch deep dive + native-vs-FIDE + 30 adversarial cases in
DUTCH_SYSTEM_SPECIFICATION.md; BBP/JaVaFo/mature vendors in PAIRING_ENGINES.md;
open-source table in OPEN_SOURCE_ECOSYSTEM.md; RR/Team/Other formats in own
docs; endorsement in FIDE_ENDORSEMENT.md; licences in LICENSE_RESEARCH.md;
capability matrix + strategy options + sources register complete. Gate: COVERED.

## 2. Second research pass (skeptical-principal-engineer review)

"What did we fail to investigate?" Findings + dispositions:
1. *Full 2026 Dutch article text not in hand* — acknowledged in SOURCES.md;
   spec labels secondary claims; mitigation PROPOSED: retrieval + article-level
   traceability matrix as a foundation-phase task. NOT blocking Stage 3.
2. *C.04.6 Team text missing* — team scope deferred to late roadmap; retrieval
   tasked before any team spec. NOT blocking.
3. *JaVaFo redistribution terms unknown* — contained by bring-your-own-binary
   default + OWNER DECISION REQUIRED. NOT blocking.
4. *Lim mechanics thin* — Lim is a late-roadmap system; no Lim claims load-bearing
   for Dutch work. NOT blocking.
5. *Topology check*: initial-colour-by-lot, played-only colour history,
   PAB=win-points, C2-forfeit-win, topscorer split — captured as 2026 deltas.
   No further second-pass gaps found. STOPPING Stage 2 here.
