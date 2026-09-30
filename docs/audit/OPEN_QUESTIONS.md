# Open Questions for Stage 2 (STAGE 1 — no decisions made)

Research needed before any architectural/implementation decision. Staged for
explicit authorization; nothing below is decided.

1. **Search completeness — RESOLVED Stage 1.6 as FALSE POSITIVE (bug), OPEN as
   FIDE-order fidelity**: first-local shortcut proven complete relative to the
   engine's own constraint model (downstream depends only on downfloater set;
   0/4000 differential mismatches). Remaining: docstring correction + whether
   first-wins matches FIDE's choice among legal alternatives (Stage 2).
2. **FIDE traceability**: acquire the actual C.04.2/C.04.3 text (effective
   1 July 2025) and build a rule-by-rule matrix for: exchange order, bye
   ordering scope, mild-preference force, absolute-conflict resolution,
   upfloat-strictness (`floats.py:240-241`), odd-tail upfloat rule.
3. **Donor equivalence**: obtain `chess-manager domain/pairing/` and diff
   behavior (locked-card float tags, `status` filter intent, `validate_and_fix`
   contract, `SwissEngine` export intent, Persian comment context).
4. **External-engine strategy**: BBP/JavaFo adapter decision explicitly
   deferred (Stage 1 rule 24) — needs FIDE-conformance harness first.
5. **Contract tiering**: which implicit surfaces (`validate_and_fix`,
   module-deep imports, `SwissEngine`, message texts, rule codes) become
   versioned public vs internal? Needs compatibility policy + CHANGELOG start.
6. **`is_upfloater` — RESOLVED Stage 1.6 as dead flag without behavioral impact**
   (only `= False` assignments exist; upfloat enforcement via opponent-down
   inference covers all in-bracket upfloats). Remaining: FIDE-model fidelity of
   that inference (Stage 2) + donor-design context if obtainable.
7. **Input-validation policy**: strict (typed errors) vs lenient (current
   silent absorption)? Affects A2/A4/A5/A6 fixes; needs caller-impact review.
8. **License hygiene**: add LICENSE text / SPDX expression? (Legal, not technical.)
9. **Performance envelope**: benchmark 10→1000 players incl. pathological
   single-bracket states; validate 2M-step cap and cache effectiveness.
10. **Test strategy**: float/bracket/exchange unit tests, validator violation
    tests, impossibility tests, multi-round simulations, external reference
    corpus — scope and priority for Stage 2+.
11. **Documentation structure**: this audit created `docs/audit/` (no prior
    docs dir existed — VERIFIED — so no competing structure was displaced).
    Confirm it as the ongoing home for stage reports.
