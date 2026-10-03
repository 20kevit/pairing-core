# CURRENT STATUS — Per-System Latest-Source Answers (completion wave)

> HOSTILE-AUDIT AMENDMENT (2026-10-03): the per-system sections below predate
> the audit wave and contain superseded implementation claims (notably "NOT
> implemented" rejections and the Lim-3.9/Dutch-PAB/Double-min-vector readings).
> Authoritative implementation status is now docs/audit/FIDE_CONFORMANCE_MATRIX.md
> (+ docs/audit/FIDE_CONFORMANCE_FINAL_REPORT.md); research history is preserved
> below unmodified.


Seven-stage state per system (§17 — never collapsed):
located → verified → full-text → extracted → possible → implemented → tested.
Conformance (§16): Dutch-2026 etc. are IMPLEMENTED_WITH_EXPLICIT_EVIDENCE_GAPS
where documented readings exist (PAB-TPN tiebreak, Double/Team min-vector
selection, Lim 3.9 folding, Burstein/Baku caller-side duties); Berger is
FULLY_IMPLEMENTED_AND_EVIDENCED; KO/match is OUT_OF_SCOPE_WITH_REASON.

| System | Located | Verified | Full-text | Extracted | Possible | Implemented | Tested |
|---|---|---|---|---|---|---|---|
| Dutch-2026 | YES | YES | YES (bundle) | YES | YES | YES `dutch-2026` | YES (47-suite) |
| Dubov-2026 | YES | YES | YES (bundle) | YES | YES | YES `dubov-2026` | YES |
| Burstein-2026 | YES | YES | YES (bundle) | YES | YES | YES `burstein-2026` | YES |
| Lim-2026 | YES | YES | YES (bundle) | YES | YES | YES `lim-2026` | YES |
| Double-2026 | YES | YES | YES (bundle) | YES | YES | YES `double-2026` | YES |
| Team-2026 | YES | YES | YES (bundle) | YES | YES | YES `team-2026` | YES |
| Baku-2026 | YES | YES | YES (bundle) | YES | YES | YES (modifier) | YES |
| Olympiad-2022 | YES | YES | YES (annex PDF) | YES | YES | YES `olympiad-2022` | YES |
| Berger | YES | YES | YES (tables) | YES | YES | YES (pre-existing) | YES |
| KO/match | YES | YES | boundary | YES | n/a | OUT (boundary) | n/a |

## Dutch — C.04.3 [F-0105]

- Latest source: C.04.3 FIDE (Dutch) System, effective from 1 February 2026
  (Council 28/10/2025, CM3-202517).
- Effective: 01/02/2026. Currently applicable: YES.
- Superseded: till-2026 text [F-0107]; interim 2025 text [F-0106].
- Algorithm-defining sections: criteria [C1]–[C21] (C1 no-rematch mandatory;
  C2 no second PAB; C3 same-absolute-colour non-topscorers; C4 completion;
  C5 PAB lowest score; C6–C9 downfloater/PAB minimisation; C10–C13 colour
  controls incl. topscorer split; C14–C21 float repetition/score-gap minimisation).
- Ambiguities: article-level optimisation semantics need full text (G-01).
- Examples: TEC tutorials exist (S-0106 set); official pairing examples in full text TBD.
- Full algorithm specified? PARTIALLY (structure verified; article bodies pending manual retrieval).
- Implementation possible? PARTIALLY — architecture (criteria optimiser) is established;
  exact criterion semantics await full text.
- pairing-core status: frozen `dutch-till2026-compat` kernel ≈ pre-2026 formulation;
  `dutch-2026` NOT implemented (explicitly rejected by resolver).
- 2026 evidence: E.5 (initial-colour parity) is a **till-2026** article; no 2026
  E.5 location exists. "Float-bar" claims must cite 2026 C14–C17 minimisation
  framing, not an absolute bar (live BBP evidence: no absolute bar in BBP source).

## Dubov — C.04.4.1 [F-0108]

- Latest: effective 01/02/2026, Council 28/10/2025. Applicable: YES.
- Superseded: [F-0109]. Sections: two-step procedure (fix pair/floater counts
  under C1–C5, then best pairing); completion C4; quality C5 (max pairs),
  C6 (max incoming floaters by number then score), C7 (outgoing floaters optimise
  next bracket); **no downfloaters** (upfloaters only).
- Ambiguities: criterion numbering vs Dutch C1–C21 overlap TBD (full text).
- Examples: official examples in full text TBD.
- Full algorithm? PARTIALLY. Implementation possible? PARTIALLY.
- pairing-core: NO Dubov engine; architecture note only. Status: RESEARCH CONTINUES.

## Burstein — C.04.4.2 [F-0110]

- Latest: effective 01/02/2026 (index-equalising, Dutch-seeded rounds). Applicable: YES.
- Superseded: [F-0111]. Sections: Buchholz-then-SB ranking order; median-scoregroup
  cracking (§2.6.1/2.6.2); own acceleration semantics (without XXA codes Burstein
  defaults to its own acceleration; Dutch defaults to none — BBP README, S-0101).
- Ambiguities: full recodified text pending (G-01).
- Full algorithm? PARTIALLY. Implementation possible? PARTIALLY.
- pairing-core: NO Burstein engine. BBP's own Burstein is self-declared flawed /
  non-endorsed (S-0101) — never an oracle for conformance. Status: RESEARCH CONTINUES.

## Lim — C.04.4.3 [F-0112]

- Latest: effective 01/02/2026. Applicable: YES. Superseded: [F-0113].
- Sections: median-scoregroup up/down pairing with exchange rules; bi-directional
  processing (top-down to just before median, then bottom-up); strict colour rules;
  bye to bottom-group lowest-ranked.
- Ambiguities: thinnest retrieved detail of the four Swiss systems; full text pending.
- Full algorithm? PARTIALLY (mechanics directionally verified). Implementation possible? NO —
  article text required. Status: RESEARCH CONTINUES (thinnest file; re-retrieval queued).

## Double Swiss — C.04.5 [F-0114]

- Latest: standalone chapter effective 01/02/2026. Applicable: YES.
- Sections: every pairing = 2-game alternating-colour match; match score = sum;
  PAB = win+draw value; upfloater pairing.
- Full algorithm? PARTIALLY (frame verified; detail pending). Implementation possible?
  PARTIALLY (needs match-score result model pairing-core lacks).
- pairing-core: NO Double engine. Status: RESEARCH CONTINUES.

## Team Swiss — C.04.6 [F-0115] + Olympiad [F-0601]

- Latest: C.04.6 effective 01/02/2026 (TPN/brackets/upfloaters; PAB = draw value).
  Olympiad Pairing Rules effective 01/01/2022 (Council 27/10/2021) — no newer text found.
- Applicable: YES (both). Superseded: [F-0116] (C.04.6 till text).
- Sections: team-as-unit scoregroups; board-1 colour rules (Olympiad); match-vs-board
  point duality (Handbook 07 §11–13 for team tie-breaks — context).
- Ambiguities: full article bodies pending (G-01).
- Full algorithm? PARTIALLY. Implementation possible? PARTIALLY (needs team/match
  domain layer — Stage 3 OUTSIDE-core boundary PROPOSED).
- pairing-core: NO team engine. Status: RESEARCH CONTINUES.

## Accelerated / Baku — C.04.7 [F-0117]

- Latest: effective 01/02/2026 (GA/GB split + virtual points, generalised scoring).
  Applicable: YES. Superseded: [F-0118].
- Implementation possible? PARTIALLY (virtual-point input model; JaVaFo `-b`/XXA
  carriage verified S-0102).
- pairing-core: NO acceleration model. Status: RESEARCH CONTINUES.

## Berger / Round Robin — C.05 Annex 1 [F-0501]

- Latest: Berger tables 3–16 players; odd N → highest number bye; double-RR
  last-two-rounds reversal note. Applicable: YES.
- Full algorithm? YES (tables retrieved in full, prior wave). Implementation possible? YES.
- pairing-core: `round_robin` Berger schedules implemented, validated vs C.05 Annex 1.
- Status: FULLY SPECIFIED. No prior BLOCKED status to revisit.

## KO / Match / Playoff

- FIDE specifies: format/colour/pairing-number allocation must be regulated per event
  (Handbook 07 art. 3); C.05 §5.3 Varma Annex 2 for restricted draws; 07 tie-break
  regs updated 01/03/2026 (context [F-0301]).
- Pairing-logic portion: bracket generation only (trivial); rest is tournament
  management (OUT of pairing-core per boundary principle).
- Status: FULLY SPECIFIED as a boundary (no pairing search to implement).

## Prior BLOCKED statuses — re-evaluation (§16)

| Prior claim | Re-evaluation 2026-10-03 |
|---|---|
| C.04.6 Team Swiss article text "not retrieved" | PARTIALLY RESOLVED: chapter URL + applied date + frame (TPN/brackets/upfloaters, PAB draw) located; article body still pending → RESEARCH CONTINUES (no longer BLOCKED) |
| 2026 Dutch article text "fetch timeouts" | PARTIALLY RESOLVED: structure ([C1]–[C21], PAB-min-score, topscorer split, PPB/CLB removal) corroborated by TEC tutorials + Council bundle; body still pending → RESEARCH CONTINUES |
| Lim detail "thin, flagged for re-retrieval" | CONFIRMED GAP: 2026 chapter located [F-0112] with frame; body pending → RESEARCH CONTINUES |
| Dubov exact priority ordering | PARTIALLY RESOLVED: two-step + C4–C7 frame verified; full ordering pending → RESEARCH CONTINUES |
| "E.5 float-bar" for 2026 | CORRECTED: E.5 is till-2026 parity; 2026 float control = C14–C21 minimisation. Claim withdrawn pending 2026 citation |

No system remains `BLOCKED — NO AUTHORITATIVE SPECIFICATION`: every system has a
located current chapter; gaps are article-body depth, with a defined retrieval path
(manual browser fetch — see SEARCH_LOG.md).
