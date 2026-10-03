# Lim System — Structured Research Note

## Identity
- System: Lim System (Singapore), C.04.4.3. Named in 1987 list as "GMB Lim"
  (HISTORICAL RULE [F-0701]) — lineage to 1980s.
- Rulesets: till-2026 [F-0113] → 2026 [F-0112] (Council 28/10/2025, effective
  01/02/2026; "new/promoted 2026" per chapter record).
- Thinnest retrieved detail of the four Swiss systems — re-retrieval queued (NOTE).

## Authoritative sources
- [F-0112] C040403202602 (CURRENT); [F-0113] C040403Till2026 (SUPERSEDED);
  mirror https://spp.fide.com/c-04-4-3-lim-system/ ; [F-0201] enacting instrument.

## Inputs
- Base Swiss inputs (TPN, scores, colour/opponent/float histories). No Lim-specific
  input extensions verified.

## Definitions
- Median scoregroup = the middle scoregroup of the field (DEFINITION, frame).
- Bi-directional processing: pairing runs top-down to just before the median
  scoregroup, then bottom-up (ALGORITHM STEP, PRIMARY excerpt).
- NOT merely a Dutch variant: distinct processing order + strict colour rules
  (NOTE — do not assume Dutch-variant status per brief §19).

## Pairing process (frame)
1. Process scoregroups top-down down to (not including) the median group (STEP).
2. Process remaining groups bottom-up from the bottom (STEP).
3. Median-group up/down pairing with exchange rules (STEP, chapter summary).
4. Strict colour rules throughout (MANDATORY RULE, frame — article detail pending).

## Ordering / Constraints / Preferences
- Score grouping retained; float direction: both (up + down) around the median (NOTE).
- Bye: to lowest-ranked of bottom group (MANDATORY RULE, secondary-consistent,
  article pending).

## Colour / Float / Bye / Exchange / Special cases
- Colour logic: strict (article detail pending — GAP).
- Exchanges/transpositions: median-group exchange rules exist (chapter summary);
  detail pending.
- Purpose (NOTE, secondary-consistent): better colour distribution, fewer floaters.

## Examples
- Official examples: in full text (G-01). No verified implementation reference
  (py4swiss: NO Lim engine; echecs claim only — SECONDARY).

## Ambiguities
- A-L1: nearly all article-level detail (algorithm, ordering thresholds, colour
  strictness definition, exchange rules).
- A-L2: median definition for even-numbered scoregroup counts.

## Implementation assessment
- Algorithm genuinely distinct (bi-directional); needs own bracket processor.
- Status: RESEARCH CONTINUES — thinnest file; next retrieval should target the
  SPP mirror + manual browser fetch of [F-0112].
