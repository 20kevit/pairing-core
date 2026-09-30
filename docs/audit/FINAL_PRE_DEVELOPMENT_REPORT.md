# Final Pre-Development Report (STAGE 4, §8)

## Executive summary

pairing-core v0.1.0 is a small, clean, deterministic Dutch-kernel library with
an honest but narrow evidence base. Its search is solution-complete (proven in
this mission, overturning the initial suspect flag) but pre-2026 in formulation
and untested beyond basics. The mission produced 44 documents across
audit/research/spec/gate layers, converging on a PROPOSED strategy D
(native + bring-your-own-binary adapters + conformance harness) with 8 explicit
owner decisions outstanding. Gate verdict: **READY FOR OWNER REVIEW**.
No code, deps, commits, or pushes were touched — VERIFIED below.

## Repository findings

Single-commit repo at 2cb570b=v0.1.0, clean; 10 modules, 15 passing tests;
zero runtime deps; no CI/licence-file/changelog. Notable behaviours proven by
probe: rating inert, silent legacy `status` filter, id-based equality hazard,
`validate_and_fix` never fixes, `is_upfloater` permanently False (harmless),
bye bottom-up fresh-first greedy, first-local shortcut COMPLETE (not a bug).

## FIDE findings

2026 rewrite (C1–C21 optimisation, played-only colours, win-PAB, forfeit
exclusion, topscorers) supersedes the kernel's formulation; repo's "1 July
2025" string matches neither citable text. System map (Dutch/Dubov/Burstein/
Lim/Double/Team/Baku) with chapter references and mechanics researched;
full 2026-Dutch article text + C.04.6 remain retrieval debts (non-blocking).

## Algorithm findings

Native ≈ pre-2026 legality kernel + independent first-wins search; gaps vs
2026: optimisation framing (C6–C9/C12–C21), MDP/BSN/Limbo concepts, E.3/E.5
allocation, C9, topscorer split. 30 adversarial fixtures defined (data only).

## Existing engine findings

BBP (Apache-2.0, blossom matching, TRF-2026, error codes 0–5, Dutch-2025;
Burstein self-declared flawed) = first oracle/adapter. JaVaFo 2.2 (reference
role, TRF(x), FPC/RTG, free+attribution, redistribution UNKNOWN, JVM) = second
oracle, BYO-binary only. Vendors standardise on these via TRF; none offers a
library API — the open niche. py4swiss/echecs/go-chesspairing mapped as
reference/oracle/inspiration, none directly dependable.

## Architecture findings

Hypothesis adopted with modifications: domain + RulesetId/ConstraintSet data +
provider interface/registry + native/external + validation sidecar +
reproducibility envelope; core stdlib-only; TRF at adapter edge. Team/KO/
tie-breaks OUT; match model minimal (Double only).

## Product requirements

ID catalog (functional → release engineering) with acceptance gates per phase;
10-phase roadmap foundation-first; no invented performance numbers.

## Testing strategy

12 suites from unit to API-compat; oracle-differential with seeded corpora;
every bug → regression test; v0.1.0 goldens as compat harness.

## Compatibility strategy

Behavioural goldens + 5 independent versions + semver + deprecation windows;
implicit surfaces tiered (owner call).

## Licensing recommendation

Retain MIT (PROPOSED); NOTICE hygiene for Apache-2.0 derivations; no in-process
GPL; JaVaFo BYO-binary + attribution, never bundled without clearance.

## Major risks

1. 2026-conformance is rewrite-scale (criteria optimisation). 2. Repeat-bye
   ruleset tension unresolved (blocks Dutch-2026 detailing). 3. External
   binaries/JVM operational burden. 4. Silent-input legacy behaviours must be
   converted to strict errors without breaking chess-manager (compat harness
   mitigates). 5. Endorsement-distance honesty must be maintained publicly.

## Open questions / owner decisions required

O01 strategy adoption; O02 partial-result policy; O03 defaults/fallbacks;
O04 JaVaFo clearance; O05 tie-break adjacency; O06 licence adoption;
O07 roadmap timing; O08 compat windows/tiers. Plus retrieval debts and
measurement-first budgets (OPEN_QUESTIONS.md).

## Development readiness

READY FOR OWNER REVIEW (criteria in DEVELOPMENT_READINESS.md). Architecture,
requirements, testing, compatibility, licensing, and FIDE positions are
reviewable; 8 decisions are explicitly parked.

## Recommended next step

Owner reviews MASTER_SPECIFICATION + DECISIONS + OPEN_QUESTIONS, records O01–O08,
then authorises Foundation phase ONLY (errors, validation, tiers, versioning,
harness, determinism suite) — the one phase with no FIDE-text dependency.

## Mission hygiene (END CONDITION check)

Stages 1–4 complete (17 + 13 + 17 + 3 docs = 50 files under docs/);
MASTER_SPECIFICATION, DECISIONS, OPEN_QUESTIONS, DEVELOPMENT_READINESS, and
this report all exist; production code, dependencies, and git history untouched;
no commits, no pushes. `git status` shows only untracked `docs/` (+ nothing
else). STOPPING — awaiting explicit owner approval.
