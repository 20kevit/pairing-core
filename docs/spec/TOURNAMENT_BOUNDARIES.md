# Tournament and pairing boundaries

**Current product boundary:** Pairing-Core is a pairing-only library. It
accepts caller-owned state needed for a named one-round pairing operation and
returns pairings plus pairing metadata. Its validation and provenance
features do not turn it into a tournament manager or prove full FIDE
conformance.

## Pairing-Core owns

- Pairing search/procedures under explicitly identified rulesets.
- Pairing-specific board order, colour assignment, bye/floater procedures,
  and core pairing legality checks.
- Deterministic result models, typed errors, execution bounds, and source /
  engine provenance where supported.
- The fixed Berger table generator and explicit external-engine adapters.

## The integrating tournament application owns

Registration, identities, pairing-number assignment policy, ratings data,
round lifecycle, result entry/correction, standings and score roll-forward,
withdrawals/late entry, team lineups, event-specific score valuation,
publication, persistence, permissions, UI, notifications, scheduling,
venues, prizes, and arbiter decisions when rules delegate a choice. Pairing-
Core cannot verify that these facts are complete or true merely because a
request passes structural validation.

## Tie-break library boundary

General tournament tie-break calculations belong to the separate
`tiebreak-core` project when that project's API supports the exact requested
rules. Pairing-Core has no dependency on it and does not duplicate its
algorithms. The inspected tiebreak-core v1.2.0 release provides C.07
calculations, not a C.04.4.2 Burstein Index calculator; C.07 results are not
silently treated as C.04 values. Burstein pairing therefore takes a complete
external `BursteinIndexSet` and provenance after its seeding rounds. The
caller remains responsible for the value's C.04 semantics and provenance
claim. See [`TIEBREAK_ARCHITECTURE.md`](TIEBREAK_ARCHITECTURE.md).

## Composition

The application assembles state and decides how Pairing-Core, tie-break
libraries, and any other components interact. These seams are data contracts,
not shared tournament state or hidden callbacks. Changes to public schemas
follow the compatibility/deprecation policy; no generic tournament-core is
introduced.
