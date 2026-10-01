# Tournament Boundaries (STAGE 3 SPEC — PROPOSED)

## 1. pairing-core owns (one round/match at a time)

Who-plays-whom, board order, colours, bye + float metadata, legality
validation, diagnostics, reproducibility envelope — under a named ruleset.
Plus pure helpers: roll-forward (state+results→next state), Berger schedules,
TRF build/parse (adapter layer), seeded corpus generation (test asset).

## 2. chess-manager / tournament management owns (OUT, explicitly)

Registration, pairing-number assignment policy, payments, accounts, ratings
database, result entry UI, standings publication, notifications, scheduling,
venues, money/prizes, admin workflows, arbiter judgment calls (incl. FIDE
"arbiter shall decide" impossibilities — core reports, human decides),
general tie-break computation (Handbook 07, adjacent — future tiebreak-core;
O05/O09), rating reports.

## 3. Shared seams (contracts, not code)

State handoff schema (PlayerState list + round + ruleset + constraints);
result consumption (RoundPairing + diagnostics); error taxonomy mapping to
arbiter UX (impossible → manual-pairing workflow); version compatibility
matrix between manager and core. Changes to seams follow deprecation policy.
