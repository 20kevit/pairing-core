# Security policy

## Scope

pairing-core is a pure computation library: no network, no persistence, no
secrets, no authentication surface. The security-relevant surface is:

- **External-engine adapters** (`pairing_core.adapters`): supervised
  subprocess execution — argv lists only (never shell), caller-supplied
  explicit binary paths (BYO, never downloaded/searched), required
  timeouts with kill-after-grace, 10 MiB stdout/stderr caps enforced
  during collection (reader threads kill over-limit children; parent
  memory stays bounded), strict UTF-8
  decoding, temp-dir scratch with cleanup. See
  `src/pairing_core/adapters/_process.py`.
- **TRF/file handling** (`pairing_core.adapters.trf`): linear grammar,
  malformed/oversized input rejected with typed errors, no path traversal
  (callers supply content or explicit paths; no globbing).
- **Resource exhaustion**: exact-search ceilings terminate with typed
  `EngineTimeoutError`, never hangs or partial results
  (`docs/audit/SEARCH_CEILING_POLICY.md`).

## Reporting

Report suspected vulnerabilities via a GitHub Security Advisory (private)
on `20kevit/pairing-core`, or by opening an issue titled
`[SECURITY] <summary>` if the issue is already mitigated. Include: version,
minimal reproducer, and observed vs expected behavior.

Safety fixes may break behavior immediately with a documented advisory
(VERSIONING.md policy); normal deprecations keep the O08 two-minor window.
