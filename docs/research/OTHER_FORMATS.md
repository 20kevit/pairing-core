# Other Formats Research (STAGE 2, §2.11)

Scope verdict per format: IN pairing-core (pairing logic proper) vs OUT
(tournament management). All PROPOSED; OWNER DECISION REQUIRED for scope.

## 1. Knockout / single elimination

Fixed bracket from seeding; no pairing search after draw (except redraw rules).
IN-scope only as a deterministic bracket generator (trivial); draw/lot
management is OUT (management). FIDE tie-break regs cover KO playoff formats
(PRIMARY: Handbook 07 art. 3: format, pairing-number allocation, colour
allocation must be regulated). Verdict: PROPOSED OUT except bracket-generation
helper (low value, defer).

## 2. Double elimination / playoffs / qualification

Losers-bracket bookkeeping is standings/management, not pairing search.
Verdict: OUT (management). No FIDE pairing text applies.

## 3. Match play (individual/team, best-of-N)

Two-player colour-alternating series; Double Swiss (C.04.5) already covers the
two-game match form IN-scope when Double Swiss is specified (needs match-score
result model). Longer matches: OUT (scheduling + conditions).

## 4. Best-of-N / gauntlet / hybrid Swiss+KO

Format composition/orchestration across phases. Verdict: OUT (management
orchestration); pairing-core serves per-phase pairing calls.

## 5. Boundary principle (carried to Stage 3)

pairing-core answers "who plays whom, on which board, with which colour, with
what float/bye metadata, under which ruleset" for ONE round/match. Anything
about phases, qualification, draws, scheduling, publication, or money is
tournament management. Hybrid formats compose core calls; they don't extend them.
