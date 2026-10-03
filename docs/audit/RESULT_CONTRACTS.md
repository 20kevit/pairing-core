# Caller contracts: tournament-result data vs pairing inputs (closure wave)

Pairing needs standings, not games. Everything below is typed, validated,
and never silently defaulted: missing data raises `InvalidPlayerError`
(ratings/results) or `InvalidRequestError`, never a guessed pairing.

## Match ↔ game mapping (Double Swiss, Preface + 1.4 + 1.6)

- `score` = match points (ordering, 1.2). Per-game decomposition
  (2-0 vs 1½-½ etc.) never enters pairing: no game-level input exists.
- `colors` char per round = first-game scheduled colour **if at least one
  game of the match was actually played** (1.6); `'u'` for unplayed matches.
- PAB value (win + draw match value, 1.4, uniform) is added to `score` by the
  caller before invoking (management-side regulation value).
- Byes apply to matches only (Preface): `got_pab` blocks repeats (C2).

## Forfeit conventions (Double Preface + C.04.2 Art.3.5)

- `opponents` = matches treated as played: regularly played matches AND
  single-game-forfeit matches (Preface: treated as played for standings).
- A match that ended by forfeit (≥1 side forfeited BOTH games) was never
  played: it is EXCLUDED from `opponents`, so the Preface repeat exception
  holds structurally (no flag needed, nothing to mis-set).
- "Won a match by forfeit" (C2 PAB block) → `forfeit_win=True`.
- Colours of forfeit matches: no games played → no colour recorded
  (consistent with 1.6).

## Other caller duties (unchanged, re-verified)

- Dubov ratings (1.1.1–1.1.2, provisional by arbiter): missing → typed error.
- Dubov `prior_upfloats` cumulative counts (C8–C10 maximum-upfloat guards).
- Burstein `round_results` W/D/L per played opponent (1.7); virtual points
  stripped caller-side (1.7.2.2); self-game points live in current scores.
- Unplayed counts (`unplayed`, `'u'` rounds) feed Dutch C9 / PAB preferences.
- Team TPN = competition-assigned number (C.04.6 1.1); Olympiad TPN =
  initial pairing number (F-0601 3.1 — helper `seed_initial_numbers`
  provided for the FIDE-defined avg-top-4/5th/alpha computation).
- Board-level data (line-ups, board colours): management-side; team match
  colour derives from board-1 scheduled colour, encoded by the caller.

## Deterministic helpers provided (FIDE-defined, no policy embedded)

- `baku.split_groups/virtual_points/pairing_scores` (C.04.7 pure functions).
- `olympiad.seed_initial_numbers` (F-0601 3.1).
- Colour-difference/preference primitives in `common` (article formulas).
