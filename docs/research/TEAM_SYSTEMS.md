# Team Systems Research (STAGE 2, §2.10)

## 1. Team Swiss

Teams paired as units on match points (PRIMARY: FIDE tie-break regs distinguish
match-points-decided vs game-points-decided competitions; Olympiad Pairing Rules
chapter exists — detail UNVERIFIED in retrieved sources). Implementations
(SECONDARY + vendor PRIMARY): Vega/Orion (Olympiad, ECU systems, up to
1000 teams/30 players), Swiss-Manager (team Swiss to 300 teams/23 rounds),
echecs/swiss `team` subpath (teams-as-players, Type A colours). Mechanics
analogue: scoregroups of match points, board-colour balancing across matches,
line-up order constraints (board 1 = first board, not a player — PRIMARY:
Olympiad rules excerpt).

## 2. Team round robin, multi-board matches

Berger schedules apply at team level; boards pair by line-up order
(SECONDARY: Swiss-Manager team-RR to 50 teams; Vega/Orion double RR).
Match points (2/1/0) vs board/game points dual scoring (PRIMARY: Handbook 07
§11–13: MP, GP, ESB team Sonneborn-Berger variants, board count, top-board
results, bottom-board elimination).

## 3. What team play needs that pairing-core lacks

Team entity, board count/line-ups, match-vs-board point duality, team colour
histories, board-order constraints, team bye/match-default handling. This is a
second domain layer above individual pairing — Stage 3 places it OUTSIDE core
v1 scope (boundary decision PROPOSED). No FIDE team-Swiss article text retrieved
(UNVERIFIED detail) — deeper retrieval required before any team spec.
