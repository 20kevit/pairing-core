# Determinism Contract (Phase D)

Status: IMPLEMENTED for the native path; scope below is exact.

## Guarantee

Identical library version + identical ruleset + identical logical request
+ identical constraints + identical deterministic execution configuration
(`ExecutionBudgets`, `deterministic=True`) MUST produce the same logical
pairing and byte-identical `canonical_json()` output.

## Scope (what is covered)

- Repeated executions in one process; fresh processes; `PYTHONHASHSEED`
  sweeps (no set/dict iteration order leaks — opponent lists sorted, boards
  ordered, registries sorted, JSON keys sorted).
- Player input ordering (kernel sorts by `(-points, pairing_no, id)`; digest
  sorts by `id`).
- Equal-score groups, float ordering, colour allocation, bye selection
  (fresh-first + C5 + C9), forbidden/forced pairs, bracket/board/candidate
  ordering, exchange/transposition search order, round-robin table
  construction, provider metadata, serialization.

## Non-goals (explicitly outside the guarantee)

- Wall-clock budget expiry is environment-dependent (may differ across
  machines); step-budget exhaustion IS deterministic.
- External engines (BBP/JaVaFo): native-side handling is deterministic, but
  oracle output identity depends on the external binary/version (recorded in
  the envelope, never guessed).
- `CancelToken.cancel()` timing: cancellation is cooperative, not replayable.

## Evidence

- `tests/test_determinism.py` (+ hash-seed sweeps), `test_properties.py`
  (seeded), `test_canonical.py` (canonical serialization byte-equality),
  envelope round-trip/digest tests. Full suite: 247+ passed at `ff50dac`
  baseline; this wave adds 11 canonical tests.

## Adversarial coverage

Pathological brackets (e.g. single-80 legality matrix), duplicate-id and
asymmetric-memory inputs (typed rejection, deterministic), and
forbidden-pair determinism tests are pinned in-suite.
