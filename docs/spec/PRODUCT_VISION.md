# Product purpose and guardrails

**Current product statement (2026-10-27):** Pairing-Core is an independent,
pairing-only Python library. It validates pairing requests, selects pairings
under a named ruleset, and returns deterministic pairing results. It is not a
tournament manager, standings service, general tie-break library, or FIDE-
evaluated/endorsed program.

## Goals

- Preserve the frozen legacy compatibility API and its published behavior.
- Offer dated, explicit pairing-system implementations with caller-owned
  event facts represented as inputs rather than guessed by the library.
- Make deterministic behavior, typed failure, execution bounds, and result
  provenance reviewable and testable.
- Maintain source/evidence links and state limitations without equating local
  tests or source retrieval with full FIDE conformance.
- Keep general tie-break calculation in the separate `tiebreak-core` project;
  never duplicate its algorithms in Pairing-Core.

## Non-goals

Tournament lifecycle, player registration, pairing-number assignment policy,
results/standings persistence, rating calculation/reporting, team lineup
management, general tie-break calculations, UI, HTTP APIs, payments,
notifications, and bracket/KO orchestration. An integrating application owns
these functions and remains responsible for the facts it supplies.

## Evidence and evaluation guardrail

A ruleset identifier describes the selected ruleset target; it is not a
certification label. The authoritative readiness gates and known limitations
are in [`../audit/GAP_REGISTER.md`](../audit/GAP_REGISTER.md) and
[`../audit/COMPLETION_STANDARD.md`](../audit/COMPLETION_STANDARD.md). Pairing-
Core has not been formally evaluated by FIDE; no endorsement evidence was
found in the official list retrieved for this audit, and no endorsement claim
is made.
