# Remaining closure items (enumerated 2026-10-03)

Source: `FIDE_CONFORMANCE_MATRIX.md` interpretation register + final report
§§8–9, 16. No "miscellaneous" category: every row is individually closable.

## A. The 12 interpretations

| ID | System | Issue | Current reading | Evidence needed to close | Autonomous? |
|---|---|---|---|---|---|
| I-D-PAB | Dutch | PAB tiebreak past (score, unplayed) | largest TPN (family convention) | C.04.3 text + sibling-system PAB articles + annotated material | yes: re-audit wording |
| I-D-MDPVALID | Dutch | MDP-set validity (C7+C4) pre-filter vs global-min selection | 4.4.1 + annotated RSL commentary | yes: re-audit wording |
| I-T-C7 | Double/Team | "first complies" (3.5.5/3.6.4) vs min-vector + order tiebreak | 2.3 intro + 3.5.5/3.6.4 + criterion-by-criterion filter/minimise analysis | yes: re-audit wording |
| I-T-MATCH | Double | match↔game decomposition + PAB valuation placement | Preface + 1.4/1.6 + result table | yes: contract analysis |
| I-T-C1FB | Double | forfeit-both repeat exception | 2.1.1 + Preface forfeit-both rule | yes: re-audit wording |
| I-T-C3 | Double/Team | completion = next-bracket probe vs full lookahead | 2.2.1/3.1.2 + 3.5.5/3.6.4 scope | yes: re-audit wording |
| I-L-334 | Lim | 3.3/3.4 "opponents of other floaters" exclusion exactness | 3.3/3.4 + 3.9 | yes: re-audit wording |
| I-L-38 | Lim | 3.8 "due the alternate colour" referent | 3.8 + 3.2.2 due-colour def | yes: re-audit wording |
| I-L-412 | Lim | upward search mirroring | 4.1.2 + 4.2 example (downward only) | partially: mirror derivation |
| I-L-44 | Lim | 4.4 culprit identity ("#2"-analogue) | 4.4–4.4.2 + 4.2/4.3 examples | yes: re-audit wording |
| I-L-55 | Lim | 5.5/5.6 round-parity equalisation exactness | 5.1–5.6 + Art.6 | yes: re-audit wording |
| I-O-RANK | Olympiad | initial seeding (avg-top-4) placement | F-0601 §3.1 (evidence record) | partially: needs PDF |

## B. The 4 evidence gaps

| ID | System | Missing evidence | Status at audit-wave end |
|---|---|---|---|
| G1 (U-O-823) | Olympiad | 8.x.3 played-all preference rule text | unresolved: needs F-0601 PDF |
| G2 (U-O-88) | Olympiad | 88-team worked example | unresolved: needs F-0601 PDF |
| G3 | Dutch | RSL (required-score-list) pre-sizing machinery for 4.4.1 validity | approximated: annotated mentions RSL as facilitator, not normative rule |
| G4 | Double/Team | full-completion (C3) lookahead beyond next bracket | approximated: next-bracket probe only |

## C. The 4 reported owner decisions — representation check

| # | Decision (final report §16) | Represented in repo? | Disposition this wave |
|---|---|---|---|
| 1 | exact-search ceilings | Partially: budgets + typed errors exist; no ceiling POLICY doc | DERIVE: formalize as execution policy (§6) |
| 2 | I-T-C7 alternative | Yes: matrix + code docstring + H-graceful test | RE-AUDIT then encode/keep explicitly (§7) |
| 3 | Olympiad PDF retrieval | Yes: evidence record + U-O-823/U-O-88 | RETRIEVE or exhaust (§8) |
| 4 | Double C3 / forfeit-both | Partially: I-T-C3 + I-T-C1FB rows; no contract doc | DERIVE: caller-contract analysis (§9) |

Owner-direction docs (O01–O10 in `docs/DECISIONS.md`) cover architecture/API
tiers, not these four FIDE-semantics items: all four are live for this wave.
No other OWNER DECISION / TODO / FIXME / XXX / HACK markers exist in
`src/pairing_core/fide2026/` (grep-verified 2026-10-03).
