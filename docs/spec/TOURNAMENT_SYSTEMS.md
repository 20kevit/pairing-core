# Tournament Systems Taxonomy (STAGE 3 SPEC — PROPOSED)

Separate abstractions per family; no forced unification (§3.9).

## 1. Swiss family (shared: scoregroups, floats, colours, PAB, rematch ban)

- **Dutch** (C.04.3): S1/S2 bracket search + criteria optimisation (2026).
  First native target.
- **Dubov** (C.04.4.1): upfloat-only brackets; two-step pair-count then choice.
  Distinct bracket-handling strategy — separate module, shared colour/bye code.
- **Burstein** (C.04.4.2): Buchholz-ordered groups + median cracking. Needs
  tie-break *inputs* as data (not a tie-break engine).
- **Lim** (C.04.4.3): bi-directional median pairing; strictest colours.
  Retrieval debt before spec detail.
- **Double Swiss** (C.04.5): match wrapper over a host system + match-score
  results. Thin layer, needs RESULT_MODEL match extension.
- **Accelerated (Baku, C.04.7)**: virtual-points pre-pass over host system +
  history-aware float computation (JaVaFo XXA lesson). Modifier, not a system.

## 2. Round robin (C.05)

Berger table lookup + bye rotation + double-cycle reversal. No search, no
engine selection. Simplest module; doubles as test-data generator.
IMPLEMENTED (expansion wave): `pairing_core.roundrobin.round_robin`,
validated against Handbook C.05 Annex 1 rows for even N 4..12, structural
coverage for odds; maturity VALIDATED; standalone module (not forced into
the Swiss provider abstraction).

## 2b. Team / Knockout / Match investigation outcome (expansion wave)

Team Swiss needs C.04.6 full text (still unretrieved) plus a team/match/
board domain layer — NOT implemented; stays deferred with reason (no
authoritative spec in hand). Knockout/match/playoff formats have no single
authoritative pairing text applicable here; a bracket generator alone would
be speculative scope without a requesting use case — NOT implemented.
Neither is pretended production-ready; both remain roadmap phases.

## 3. Team systems (C.04.6 + Olympiad rules)

Team/match/board entities; MP/GP duality; board colours; line-up constraints.
New domain layer; spec blocked on C.04.6 text retrieval. Late roadmap.

## 4. Elimination / match / hybrid

Bracket generator (deterministic, trivial) only; orchestration OUT
(OTHER_FORMATS.md). No FIDE pairing text applies; manager composes core calls.
