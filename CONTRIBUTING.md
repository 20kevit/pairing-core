# Contributing to pairing-core

## Scope first

pairing-core owns one-round pairing decisions (algorithms, constraints,
ruleset logic, validation, deterministic output, provider abstraction,
execution controls, external-engine adapters). Tournament lifecycle,
ratings, tie-breaks, UI, and APIs belong elsewhere — see
`docs/spec/TOURNAMENT_BOUNDARIES.md`. Proposals that expand scope need an
explicit owner decision; bug fixes and hardening inside scope do not.

## Ground rules

- **Evidence before changes**: reproduce first; never modify behavior on
  speculation. New FIDE readings must name the exact source edition and clause,
  use the canonical JSON registry under `docs/rules/fide/registry/`, and link
  inspected implementation symbols and named tests in
  `docs/rules/fide/RULE_SOURCE_MATRIX.md`. Implementation and
  independent-verification statuses are separate; links are not conformity.
- **Source rights and history**: public access is not redistribution
  permission. Do not commit full FIDE texts, OCR, translations, or originals
  without recorded permission and a verified checksum. Keep project paraphrase,
  official example, independent evidence, and repository interpretation
  distinguishable. Preserve prior findings as dated history rather than
  silently replacing them.
- **Pairing-only boundary**: Pairing-Core does not manage tournaments, calculate
  standings, or implement general tie-breaks. C.04 Burstein Index inputs and
  their provenance remain distinguishable from caller-supplied C.07 values;
  do not assume semantic equivalence.
- **Preserve behavior**: the v0.1.0 kernel is a permanent golden reference.
  Any behavior change needs a regression test, a changelog entry, and a
  version bump per `docs/spec/VERSIONING.md` (O08: two-minor deprecation
  window for public API/behavior).
- **No partials as success** (O02): success results are complete and valid;
  failures are typed errors with diagnostics.
- **No FIDE approval/endorsement claims**: use the current source and clause
  registry for evidence links, and the audit gap register for readiness status.
  Never infer conformance from source/code/test links or the coverage counts.

## Workflow

1. Python `>=3.10`, zero runtime dependencies — keep it that way. New
   dependencies need justification; test-only dependencies must be
   optional and documented.
2. Editable install with test tooling: `pip install -e ".[test]"`
   (runtime stays dependency-free; pytest is an opt-in extra).
3. Full suite: `python3 -m pytest tests/ -q` (oracle tests skip without
   `BBP_EXE` / `JAVAFO_JAR`; benchmarks refresh only with
   `PAIRING_UPDATE_BASELINES=1`).
4. For FIDE registry edits, update the JSON source of truth, regenerate views
   with `python tools/fide_evidence.py build`, then run
   `python tools/fide_evidence.py check` and `python tools/validate_sources.py`.
   These checks are offline and are also a CI gate; never hand-edit generated
   Markdown.
5. Every genuine bug fix ships with a regression test. No fix without one
   unless the reason is documented in the commit message.
6. Keep the tree clean: no `dist/`, `build/`, `__pycache__`, or baseline
   churn (all git-ignored or opt-in).

## Commit style

Focused commits, present tense, area prefix (`pkg:`, `docs:`, `fix:`,
`test:`, `ci:`). Linear history on `main`; no force-push.
