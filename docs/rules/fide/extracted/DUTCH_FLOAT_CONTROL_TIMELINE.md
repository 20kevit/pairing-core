# Dutch Float-Control Timeline (E.5 question resolved)

## What E.5 is
- Till-2026 Dutch Art.E.5 (F-0107): with initial colour by lot, the higher-ranked
  player of each pair gets the initial colour iff their pairing number is ODD,
  else the opposite. Effective: till 31/01/2026 (Baku-2016/Goynuk-2017 lineage).
  Status: SUPERSEDED. pairing-core: CONFIRMED deviation, frozen (CONFORMANCE_STATUS §3).

## 2026 successor
- 2026 Dutch Art.5.2.5 (F-0105, FULL_TEXT verified): "If the higher ranked player has
  an odd TPN (see Article 1.1), give them the initial-colour; otherwise, give them the
  opposite colour." The parity rule SURVIVES (moved from E.5 to 5.2.5, now last step
  after 5.2.4 higher-ranked preference).
- Same successor exists in Dubov 5.2.1 (odd-TPN higher-ranked, unplayed-only context),
  Burstein 5.2.1, Double 4.3.1 (HRP), Team 4.3.1 (first-team), all verified FULL_TEXT.

## "Float-bar" — the withdrawn claim
- No absolute float bar exists in 2026. Float control = minimisation criteria:
  Dutch C6–C9 (counts/scores) + C14–C17 (repeat counts, residents vs MDP-opponents) +
  C18–C21 (score gaps, descending). BBP source implements weighted minimisation only
  (no absolute gate besides rematch/absolute-colour/completeness) — consistent.
- Interim 2025 text (F-0106, TOCh verified): forfeit/zero-bye downfloat marking REMOVED
  explicitly because C9 now handles PAB-after-absence ("Now, the new C.9 criterion
  prevents this from happening").
- Native kernel's absolute bar (consecutive_downs ≥ 2 ⇒ never downfloat) has ZERO FIDE
  citation in any era; stays frozen per O08; the 2026 engine does not contain it.

## C14–C21 meaning (verified verbatim)
- C14/C16: resident downfloaters floated previous / two-ago round (counts).
- C15/C17: MDP opponents upfloated previous / two-ago round (counts).
- C18/C20: score gaps (desc) of MDPs downfloated previous / two-ago.
- C19/C21: score gaps (desc) of MDP opponents upfloated previous / two-ago.
- Design per Annotated: residents-only C14/C16 (MDPs covered by C7/C8/C18/C20);
  downfloater gaps outrank resident gaps; last-priority anti-repeat guards.
