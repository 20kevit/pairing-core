# Berger / Round Robin — Research Note

## Identity
- Single/double round robin; Berger system. Source: C.05 Annex 1 [F-0501] (CURRENT).

## Authoritative sources
- [F-0501] C05Annex1 — full Berger tables for 3–16 players (retrieved in full,
  prior wave: PRIMARY).
- Parent C.05 General Regulations (§5.1 mandates Berger; §5.3 Varma Annex 2 for
  restricted draws).
- Compilation PDF Competition_Rules.pdf (see F-0501 entry).

## Rules
- MANDATORY RULE: fixed schedules by pairing number; N players → N−1 rounds (even N).
- MANDATORY RULE: odd N → highest number = bye (rotating bye; no lowest-score logic).
- DEFINITION: first-named = white (tables encode colours per round).
- RECOMMENDATION (ECU Berger doc, secondary-consistent): double RR second cycle
  swaps colours; reverse the last two rounds of the first cycle to avoid 3× colour.
- Circle-method construction (Berger Explained, SECONDARY — constructive verification
  by inspection, not normative).

## Inputs
- Pairing-number assignment (caller-owned, frozen — same policy as Swiss).
- Bye-as-round bookkeeping distinct from Swiss PAB (rotates; no score logic).

## pairing-core status
- `round_robin` Berger schedules IMPLEMENTED, validated against C.05 Annex 1 tables.
- Remaining (NOTE): double-cycle swap, rounds-schedule result type
  (current `RoundResult` is single-round).
- Status: FULLY SPECIFIED.

## Ambiguities
- None load-bearing. A-R1 (minor): Varma Annex 2 restricted-draw detail
  (out of pairing-core scope unless requested).
