# Security Review (master wave, Phase AB)

Re-audit of all trust boundaries. Verdict: CLEAN — no findings requiring
code changes. Prior wave controls confirmed still in force by source
inspection 2026-10-03; new `canonical.py` surface reviewed below.

## Subprocess (`adapters/_process.py`, `bbp.py`, `javafo.py`)

- argv-only construction, no shell (`shell=False` — verified, no
  `shell=True` string anywhere in `src/`).
- `check_executable` gates missing/unexecutable binaries →
  `EngineUnavailableError`; no PATH probing/discovery.
- Kill-after-grace on timeout; 10 MiB output caps; strict UTF-8 decode;
  `temp_workdir` cleanup (try/finally); explicit file paths only.

## Parsers (`adapters/trf.py`, `api.validate_request`, `canonical`)

- TRF: line-linear parsing, bounded ints (1..9999), duplicate detection,
  malformed → typed errors, no recursion, no eval/pickle.
- Canonical layer: frozen dataclasses, type/shape checks before execution,
  unknown schema → `VersionMismatchError`; no I/O, no subprocess, no time,
  no randomness, no global state.

## Secrets / dependencies

- `grep` for password/secret/token/api_key in `src/` (excl. CancelToken):
  none. No network code. Zero runtime dependencies (`pyproject.toml` has no
  `dependencies`). No vendored binaries (BBP/JaVaFo BYO-only).

## New-surface check (`canonical.py`)

- Imports at module top: stdlib only (`json`, `dataclasses`, `typing`).
- All `pairing_core` imports function-local; no file/network/process access.
- `canonical_json`: `sort_keys` + ASCII; no key material handled anywhere.
