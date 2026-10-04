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
  speculation. New FIDE readings require source → code → test traceability
  (`docs/rules/fide/RULE_SOURCE_MATRIX.md`).
- **Preserve behavior**: the v0.1.0 kernel is a permanent golden reference.
  Any behavior change needs a regression test, a changelog entry, and a
  version bump per `docs/spec/VERSIONING.md` (O08: two-minor deprecation
  window for public API/behavior).
- **No partials as success** (O02): success results are complete and valid;
  failures are typed errors with diagnostics.
- **No FIDE endorsement claims**: interpretations must be registered in the
  conformance matrix (`docs/audit/FIDE_CONFORMANCE_MATRIX.md`).

## Workflow

1. Python `>=3.10`, zero runtime dependencies — keep it that way. New
   dependencies need justification; test-only dependencies must be
   optional and documented.
2. Editable install with test tooling: `pip install -e ".[test]"`
   (runtime stays dependency-free; pytest is an opt-in extra).
3. Full suite: `python3 -m pytest tests/ -q` (oracle tests skip without
   `BBP_EXE` / `JAVAFO_JAR`; benchmarks refresh only with
   `PAIRING_UPDATE_BASELINES=1`).
4. Every genuine bug fix ships with a regression test. No fix without one
   unless the reason is documented in the commit message.
5. Keep the tree clean: no `dist/`, `build/`, `__pycache__`, or baseline
   churn (all git-ignored or opt-in).

## Commit style

Focused commits, present tense, area prefix (`pkg:`, `docs:`, `fix:`,
`test:`, `ci:`). Linear history on `main`; no force-push.
