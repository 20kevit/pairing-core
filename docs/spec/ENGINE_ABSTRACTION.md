# Engine Abstraction Specification (STAGE 3 SPEC — PROPOSED)

One interface for native and external engines, without leaking process details
into the domain. All PROPOSED.

## 1. Identity & metadata (every engine exposes)

- `engine_id` (e.g. `native-dutch`, `bbp`, `javafo`), `engine_version`
  (native: library version + kernel version; external: reported release/build,
  e.g. JaVaFo `Rel. 2.2 (Build 3222)`), `ruleset` (RulesetId: system +
  effective date + acceleration), `capabilities()` (systems, bye handling,
  seeds, forbidden/forced pairs, TRF dialects, max field hints).

## 2. Call contract

- `pair(request) -> RoundPairing` where request = (players, round, ruleset,
  constraints, seed-or-none, timeout, diagnostics-level). Pure for native;
  supervised-subprocess for external (timeout → typed error; non-zero exit →
  mapped error code à la BBP 0–5; malformed output → typed error with raw
  capture for diagnosis).
- Determinism contract: same request → byte-identical result; seed semantics
  declared per engine (native: no randomness; BBP RTG-seed vs pairing
  determinism distinguished; JaVaFo: hash-seeded R1 colour documented).
- Diagnostics: per-call (criteria costs where applicable, warnings, engine
  stdout/stderr capture for external, TRF round-trip echo).

## 3. Registry & selection

Named lookup + capability filtering; default engine per ruleset (native Dutch
when conformant, else explicit fallback policy — OWNER DECISION REQUIRED for
defaults). Version-mismatch between requested and available engine/ruleset is
a typed error, never silent substitution.

## 4. Conformance obligations

Every engine ships: capability declaration, golden corpus slice, oracle-
differential results, and version-pinned behaviour notes. Adding an engine
without these is rejected by policy (TESTING_STRATEGY.md).
