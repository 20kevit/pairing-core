# Double Swiss + Accelerated Systems — Research Note

## Double Swiss — C.04.5 [F-0114] (CURRENT, effective 01/02/2026)

### Identity
- Every pairing = two consecutive games with alternating colours; match score = sum
  (DEFINITIONS, chapter summary verified).
- New standalone chapter 2026 (pre-2026 C.04.5 was Accelerated Systems — renumbering NOTE).

### Rules (frame)
- MANDATORY RULE (frame): alternate colours across the two games by construction
  (colour fairness structural, not searched).
- MANDATORY RULE (frame): PAB scores win+draw value (1.5 in 1-½-0).
- ALGORITHM STEP (frame): upfloater pairing mechanics.
- Brackets/floats: as Dutch (NOTE, frame).

### Inputs needed beyond pairing-core
- Match/result model: two-game results per pairing; match-score aggregation.
  Currently absent (NOTE). echecs implements bye = 1.5 = win+draw (SECONDARY).

### Status
- RESEARCH CONTINUES (frame verified; article detail pending). Implementation needs
  a match-score result type (`RoundResult` is single-round).

## Accelerated Systems — Baku, C.04.7 [F-0117] (CURRENT, effective 01/02/2026)

### Identity
- Baku Acceleration moved from C.04.5 to C.04.7 (NOTE).
- 2026 text generalised to win=2-draws scoring (beyond 1-½-0) (NOTE, chapter summary).

### Rules (frame)
- Top-half virtual win-point early, halved mid-way, removed at end (NOTE,
  secondary-consistent across sources).
- GA/GB split + virtual points (DEFINITIONS, chapter summary).
- Carriage: JaVaFo `-b` flag + XXA codes (PRIMARY S-0102); full XXA history
  mandated for floater computation (JaVaFo AUM — MANDATORY RULE for engine inputs).

### Other accelerated formats
- Sevillano/Grant and similar: not found in official FIDE material — UNKNOWN
  (do not invent; record as unlocated).

### Status
- RESEARCH CONTINUES. Implementation concern: virtual points interact with float
  histories (future input-model work).
