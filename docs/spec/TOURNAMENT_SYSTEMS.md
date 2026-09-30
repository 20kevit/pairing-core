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

## 3. Team systems (C.04.6 + Olympiad rules)

Team/match/board entities; MP/GP duality; board colours; line-up constraints.
New domain layer; spec blocked on C.04.6 text retrieval. Late roadmap.

## 4. Elimination / match / hybrid

Bracket generator (deterministic, trivial) only; orchestration OUT
(OTHER_FORMATS.md). No FIDE pairing text applies; manager composes core calls.
