# API Tiers (Phase F)

## Public stable (consumer contract)

`CanonicalPlayer`, `CanonicalRequest`, `pair_canonical`, `canonical_json`,
`describe_systems`, `CANONICAL_REQUEST_SCHEMA`, `KNOWN_SYSTEMS`,
`SYSTEM_DUTCH`, `SYSTEM_ROUND_ROBIN`, `EngineRequest`, `pair`,
`pair_detailed`, `pair_via`, `validate_request`, `versions`, `RulesetId`,
`ConstraintSet`, `resolve_ruleset`, `DUTCH_TILL2026_COMPAT`, `Pairing`,
`RoundPairing`, `ExecutionBudgets`, `CancelToken`, `EngineProvider`,
`NativeDutchProvider`, `Capability`, `EngineMetadata`, `Registry`,
`create_default_registry`, `round_robin`, `explain`, `Explanation`,
`BoardExplanation`, `ByeExplanation`, all 11 error classes, `PlayerData`,
`PlayerSnapshot`, `PairingCard`, `RoundResult`, `PairingRequest`,
`PairingEngine`, `NativeDutchEngine`, `SwissEngine`, `pair_round`,
`validate_round`, `ValidationReport`, `Finding`.

Semver: additive only within majors; removals require a deprecation notice
plus the O08 two-minor window.

## Experimental

None currently. Future additions land here first, clearly marked.

## Internal (not a contract — do not import)

`pairing_core.{bracket,pairer,color,floats,exchange,bye,validator internals}`,
engine search structures, `adapters._process`, harness internals.
`adapters.{trf,bbp,javafo}` and `harness.{compare,corpus}` are
*supported submodule surfaces* (stable for their documented purpose) but not
part of the top-level consumer contract.

## Enforcement

- `tests/test_canonical.py::test_canonical_module_isolation`: the canonical
  layer has zero import-time coupling to engine internals.
- `tests/test_import_api.py` (this wave): top-level `__all__` allow-list —
  no accidental exports, no internal leakage, version consistency
  (`pyproject.toml` == `__version__`).
