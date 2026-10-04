# Engine Abstraction Specification (OWNER DECISION O01/O03/O04/O10)

One interface for native and external engines, without leaking process details
into the domain.

## 1. Identity & metadata (every engine exposes)

- `engine_id` (e.g. `native-dutch`, `bbp`, `javafo`), `engine_version`
  (native: library version + kernel version; external: reported release/build,
  e.g. JaVaFo `Rel. 2.2 (Build 3222)`), `ruleset` (RulesetId: system +
  effective date + acceleration), `capabilities()` (systems, bye handling,
  seeds, forbidden/forced pairs, TRF dialects, max field hints).

## 1b. Provider identity vs engine identity (provenance rule)

- A **provider** (`EngineProvider.provider_id`) is the selected execution
  route. An **engine** (`RoundPairing.engine_id`) is what actually computed
  the pairing. They coincide for self-executing providers
  (`native-dutch`), but a provider may legitimately DELEGATE (wrap another
  engine or an external binary): the envelope then reports the EFFECTIVE
  engine, never the selecting provider.
- `pair_via()` never rewrites provenance: it returns the provider's
  envelope unchanged (non-`RoundPairing` results are `InternalError`).
  Requested-vs-actual distinction lives in the caller's selection
  (`pair_via(provider_id, ...)`), not in rewritten metadata.

## 2. Call contract

- `pair(request) -> RoundPairing` where request = (players, round, ruleset,
  constraints, seed-or-none, timeout{wall_clock, step_budget}, cancellation
  token, diagnostics-level). Pure-bounded for native (step budget enforced at
  bracket-boundary checkpoints; wall-clock polled, never inside tight matching
  loops); supervised-subprocess for external (timeout → typed error; non-zero
  exit → mapped error code à la BBP 0–5; malformed output → typed error with raw
  capture for diagnosis). No partial pairings on any failure path (O02).
- Determinism contract: same request → byte-identical result; seed semantics
  declared per engine (native: no randomness; BBP RTG-seed vs pairing
  determinism distinguished; JaVaFo: hash-seeded R1 colour documented).
- Diagnostics: per-call (criteria costs where applicable, warnings, engine
  stdout/stderr capture for external, TRF round-trip echo).

## 3. Registry, selection, defaults, fallback (O03 FINAL)

Three distinct request modes: (1) **default engine** — resolved ONLY for
demonstrated-conformant (engine, ruleset) pairs via a versioned default table;
unsupported systems resolve to typed `UnsupportedCapability`, never to a guess;
(2) **explicitly selected engine** — used as requested or typed error (incl.
version mismatch); (3) **explicit fallback** — caller pre-authorises an ordered
standby list; any fallback records requested engine, actual engine, fallback
reason, both versions, ruleset, and reproducibility info in the envelope, and
surfaces a `fallback_occurred` warning. There is NO code path for unconfigured
fallback: "native failed → silently run BBP → return success" is
architecturally unrepresentable. Capability filtering answers the Stage-4
capability model (system/ruleset/version/bye/colour-via-ruleset/constraints/
seed/team/RR/TRF).

## 4. Conformance obligations

Every engine ships: capability declaration, golden corpus slice, oracle-
differential results, and version-pinned behaviour notes. Adding an engine
without these is rejected by policy (TESTING_STRATEGY.md).
