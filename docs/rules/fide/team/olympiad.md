# Team Swiss + Olympiad — Research Note

## C.04.6 Swiss Team Pairing System [F-0115] (CURRENT, effective 01/02/2026)

### Identity
- Teams paired as units; TPN (team pairing numbers) / brackets / upfloaters
  (chapter summary). Till text [F-0116] (…082024, till 31/01/2026) SUPERSEDED.

### Rules (frame)
- MANDATORY RULE (frame): PAB scores as draw value (differs from individual win-default).
- ALGORITHM STEP (frame): scoregroups of match points; team colour balancing across matches.
- Line-up order constraints: board 1 = first board, not a player (NOTE, Olympiad excerpt).

### Inputs needed beyond pairing-core (NOTE)
- Team entity; board count/line-ups; match-vs-board point duality; team colour
  histories; board-order constraints; team bye/match-default handling.

## Olympiad Pairing Rules [F-0601] (CURRENT, effective 01/01/2022)

### Identity
- Approved Council 27/10/2021; 11-round team Swiss by matchpoints with median-group
  top-down/bottom-up + board-1 colour rules (chapter summary). No newer text found
  2026-10-03. Live pointer: Olympiad2026MainCompetition.pdf §4.1 references the Rules.

### Rules (frame)
- Match points primary (vs game points); board colours per board-1 rules (frames).
- Team tie-break context: Handbook 07 §11–13 (MP, GP, ESB variants, board count,
  top-board results, bottom-board elimination) (NOTE, context).

### Implementations (SECONDARY/vendor PRIMARY)
- Vega/Orion: Olympiad + ECU systems, to 1000 teams (S-0105).
- Swiss-Manager: team Swiss to 300 teams/23 rounds (S-0105).
- echecs `team` subpath: teams-as-players, Type A colours (claim only, S-0104).

## Boundary (NOTE, Stage 3 taxonomy carried)
- Team play is a second domain layer above individual pairing — PROPOSED OUTSIDE
  core v1 scope. pairing-core answers per-round individual pairing; team/match
  orchestration is management.

## Examples / Ambiguities
- Official examples: in full texts (G-01).
- A-T1: full C.04.6 article body (pending); A-T2: Olympiad article body (pending).

## Status
- RESEARCH CONTINUES (chapter-level frame for both; bodies pending). Prior
  "UNVERIFIED detail" BLOCKED-adjacent status is retired: sources are located,
  depth remains.
