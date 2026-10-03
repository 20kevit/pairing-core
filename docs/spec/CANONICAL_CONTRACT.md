# Canonical Consumer Contract (Phase B)

Status: IMPLEMENTED (master wave). Authority: `src/pairing_core/canonical.py`.

## 1. FACT — what exists

- `CanonicalPlayer`: frozen value object (`id`, `pairing_no`, `rating`,
  `points`, `color_hist`, `opponents` sorted tuple, `received_bye`,
  `float_hist`). No engine/bracket/search concepts. Converters:
  `from_legacy()` / `to_legacy()` (duck-typed, function-local imports).
- `CanonicalRequest` (schema v1): `players`, mandatory `ruleset`
  (`RulesetId` or alias, never defaulted), `round_number`, `system`
  (`"dutch"` | `"berger-rr"`), `constraints` (`ConstraintSet`),
  `budgets` (`ExecutionBudgets`), `provider_id` (`None` = default native,
  explicit — no fallback), `deterministic` (must be `True`).
- `pair_canonical(request, registry=None) -> RoundPairing`: validated
  request in, complete success value out (O02). `system="berger-rr"` is
  refused here with direction to `round_robin()`; unknown systems,
  `deterministic=False`, and missing rulesets fail with typed errors.
- Serialization: `to_dict`/`from_dict` with schema versions,
  `canonical_json()` (sorted keys, compact, ASCII). Unknown schema ->
  `VersionMismatchError`; malformed -> `InvalidRequestError`.
- `describe_systems()` names supported systems + serving paths.

## 2. DESIGN DECISION — layering

```text
Consumer (CanonicalPlayer/CanonicalRequest/pair_canonical)
   │  implementation-independent; no engine names, not even lazily
   ▼
EngineRequest + validate_request (typed boundary)
   │
   ▼
pair_detailed / pair_via → provider abstraction → frozen kernel
```

Legacy `SwissEngine`/`PlayerData`/`pair_round` remain supported underneath
as the compatibility surface (see `docs/MIGRATION_V010_TO_CANONICAL.md`);
they are not part of the canonical contract.

## 3. IMPLEMENTATION STATUS

IMPLEMENTED + tested (`tests/test_canonical.py`, 11 tests): legacy
round-trips, `pair_canonical == pair_detailed` on identical logical input,
provider routing, refusal paths, serialization round-trips, and module
isolation (standalone load pulls zero `pairing_core.*` modules; AST import
scan; no `SwissEngine`/`NativeDutchEngine`/`EnginePlayer` references).
