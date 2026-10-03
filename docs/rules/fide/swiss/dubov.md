# Dubov System — Structured Research Note

## Identity
- System: Dubov System, C.04.4.1. Devised by GM Daniil Dubov (NOTE, secondary-consistent).
- Rulesets: till-2026 [F-0109] → 2026 [F-0108] (Council 28/10/2025, effective 01/02/2026).
- Purpose (NOTE, Held comparison study S-0107): reduce rating-spread unfairness of
  Dutch ("Swiss gambit" resistance); best in central scoregroups (~20–30 Elo ARO
  variability reduction, vanishing at top).

## Authoritative sources
- [F-0108] C040401202602 (CURRENT); [F-0109] C040401Till2026 + container
  OtherApprovedPairingSystemsTill2026 (SUPERSEDED); [F-0201] enacting bundle
  (C.04.4.1 text included); [F-0101]/[F-0103] common rules.

## Inputs
- Same base as Dutch (TPN, scores, colour/opponent/float histories) plus rating-aware
  ARO mechanics (DEFINITION, frame): low-ARO players paired vs high-rated opponents.

## Definitions
- ARO = average rating of opponents (DEFINITION, secondary-consistent).
- "No downfloaters in the Dubov system" — brackets pull UPfloaters from lower
  scoregroups (MANDATORY RULE, PRIMARY excerpts via prior wave).
- Two-step procedure (ALGORITHM STEP, PRIMARY): (1) fix number of pairs/floaters
  under criteria C1–C5; (2) choose best pairing.
- Completion criterion C4 (MANDATORY RULE); quality criteria C5 (max pairs),
  C6 (max incoming floaters by number then score), C7 (outgoing floaters optimise
  next bracket) (ALGORITHM STEPs, PRIMARY excerpts).

## Pairing process / Ordering / Constraints / Preferences
- Adjacent-style pairing inside groups per implementations (IMPLEMENTATION GUIDANCE,
  not FIDE text).
- Score groups processed with up-only float direction (MANDATORY RULE).
- Colour rules: same E-rules family as Dutch (NOTE, frame).
- Bye: per Basic rules [F-0101] (MANDATORY RULE).

## Colour / Float / Bye / Exchange / Special cases
- Floats: up-only; C6/C7 govern incoming/outgoing optimisation (MANDATORY RULE frame).
- Exchanges/transpositions: full article text pending (GAP; no claim recorded).
- Special cases: none verified beyond upfloater mechanics.

## Examples
- Official examples: in full text (G-01). Implementation reference: py4swiss `dubov`
  engine (from-2026, compared vs CPPDubovSystem — SECONDARY S-0103).

## Ambiguities
- A-D1: criterion numbering overlap with Dutch C1–C21 (same labels, possibly
  different content) — article text required.
- A-D2: full priority ordering of C5 vs C6 vs C7 in conflict cases.

## Implementation assessment
- Needs distinct bracket model (upfloaters-only, two-step optimisation); does not fit
  native `Bracket` abstraction without extension (NOTE, carried from Stage 3 taxonomy).
- Status: RESEARCH CONTINUES (not blocked: chapter located, frame verified).
