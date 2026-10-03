# KO / Match / Playoff — Boundary Analysis

Purpose (§23): establish (1) whether FIDE specifies them; (2) what; (3) which
portion is pairing logic; (4) which belongs to tournament management.

## Findings

### Knockout / single elimination
- FIDE Tie-break regs Handbook 07 art. 3: format, pairing-number allocation and
  colour allocation must be regulated per event (PRIMARY, prior wave).
- Pairing-logic portion: deterministic bracket generation from seeding (trivial).
  Draw/lot management = management (OUT).
- Verdict: PROPOSED OUT except bracket-generation helper (low value, defer).

### Double elimination / playoffs / qualification
- Losers-bracket bookkeeping = standings/management, not pairing search.
- No FIDE pairing text applies. Verdict: OUT.

### Match play (individual/team, best-of-N)
- Two-player colour-alternating series. Double Swiss (C.04.5 [F-0114]) covers the
  two-game match form IN-scope when specified (needs match-score result model).
- Longer matches: scheduling + conditions = OUT.

### Best-of-N / gauntlet / hybrid Swiss+KO
- Format composition across phases = orchestration (OUT); pairing-core serves
  per-phase pairing calls.

### Adjacent 2026 context
- 07. Play-Off and Tie-Break Regulations updated 01/03/2026 ([F-0301] context);
  C.05 §5.3 Varma Annex 2 covers restricted draws ([F-0501] parent).

## Boundary principle (carried)
pairing-core answers "who plays whom, on which board, with which colour, with what
float/bye metadata, under which ruleset" for ONE round/match. Phases, qualification,
draws, scheduling, publication, money = tournament management.

## Status
- FULLY SPECIFIED as a boundary (no pairing search to implement; no BLOCKED item).
