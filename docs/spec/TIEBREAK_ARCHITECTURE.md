# Tiebreak-Core Architecture (O09 — boundary + contract, NO implementation)

Future independent project/library `tiebreak-core`, conceptually independent
from chess-manager. Status: OWNER DECISION (boundary/contract specified);
implementation DEFERRED (no phase assigned before Dutch conformance).

## 1. Boundary

tiebreak-core OWNS: standardized tie-break calculation (Buchholz + cuts,
Sonneborn-Berger + team variants, Direct Encounter, Performance/TPR, Progressive,
Koya, Neustadtl, others subject to research), deterministic versioned APIs,
per-system diagnostics/explanations, golden/reference suites. It does NOT own:
pairing, standings publication, rating reports, tournament state.
pairing-core OWNS pairing; chess-manager OWNS orchestration. No component
duplicates another's calculations (single-source rule below).

## 2. System taxonomy (PROPOSED, explicitly non-final)

Official FIDE-defined (Handbook 07 + C.04-referenced: BH/cuts, SB/ESB, DE, WIN/
WON, PS, Koya, TPR/PTP) vs commonly used (Median, Cumulative, Kashdan,
Hort, Baumbach — each with provenance note) vs application-specific (namespaced,
never in the standard registry) vs deprecated/historical (marked, retained for
verification of old events only). Registry closed for standard, open via
namespace for application-specific.

## 3. Proposed API shape (contract only)

`calculate(system_id, standings_view, options) -> TiebreakTable`;
`explain(system_id, standings_view, player) -> breakdown`;
`systems() -> registry` with rule-version per system; typed errors
(unknown-system, insufficient-data, version-mismatch). Pure functions; no I/O.

## 4. Data contract (minimal standings view — NOT tournament state)

Ordered player records: id, points, per-round (opponent id | bye-kind, colour
where played, result class incl. forfeit/unplayed taxonomy), withdrawn/removed
markers. Producers: chess-manager (primary), pairing-core test harnesses
(synthetic). tiebreak-core never imports pairing-core or chess-manager.

## 5. Versioning

Per-system rule versions (`buchholz.cut1@2026-03`) + library semver; Handbook
07 effective dates tracked; deprecated systems frozen, never silently changed.

## 6. Relationships & dependency direction

```
chess-manager ──► tiebreak-core ◄── pairing-core (narrow ranking/index inputs only)
      │                  │                    │
   owns state      owns calculation      owns pairing
```
pairing-core depends on tiebreak-core ONLY for Burstein-required
ranking/index data, via the narrow data contract (scalar/vector inputs, never
callbacks into calculation). chess-manager may use both independently.
Dependency direction is one-way toward tiebreak-core; it depends on nothing
domain-specific (stdlib-only, mirroring pairing-core core).

## 7. Burstein interaction

Burstein's Buchholz-ordered groups consume precomputed Buchholz/SB vectors
through the narrow contract; ordering semantics versioned with the ruleset.
If tiebreak-core is unavailable, Burstein is unavailable (typed
unsupported-capability, never silent fallback to rating order — O03 applies).

## 8. Duplicate-calculation prevention

Single-source rule: exactly one implementation per (system, version); pairing-core
and chess-manager both call it; conformance goldens shared. No vendored copies.

## 9. Anti tournament-core guard

No shared "tournament-core" aggregating pairing + tie-break + state. Each
library stays single-purpose; composition happens in managers. Revisit ONLY if
a concrete duplicated need (not hypothetical elegance) forces it — OWNER
DECISION REQUIRED.
