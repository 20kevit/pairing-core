# Non-Functional Requirements (STAGE 3 SPEC — PROPOSED)

Supplements PRODUCT_REQUIREMENTS.md (functional IDs live there).

- **Determinism**: byte-identical output for identical logical input; no
  wall-clock, hash-seed, thread, or dict-order dependence; initial-colour lots
  only via explicit seed (cf. JaVaFo hash-seeded default — document, don't copy
  silently). Priority P0.
- **Reproducibility**: see REPRODUCIBILITY.md; retention horizon for replay
  (PROPOSED: metadata sufficient for N years given pinned versions).
- **Performance**: budgets TBD by measurement (no invented numbers):
  P1 targets — round pairing <1 s at ≤100 players normal spread; bounded
  failure (typed, <30 s) on pathological brackets; memory O(n·r). Scale
  scenarios defined in Stage 4 readiness.
- **Reliability**: no silent absorption (S-IN-01); resource caps (steps/time)
  surfaced as typed errors; recursion depth bounded by construction.
- **Security**: pure-library posture retained (no subprocess/network/fs in
  core; adapters isolated in opt-in extras); untrusted-input suite;
  ReDoS-free parsing for future TRF (linear grammar, fuzz-tested).
- **Observability**: structured diagnostics (O-DIAG-01); no logging framework
  dependency (return diagnostics, don't log).
- **Compatibility**: semver + contract tiers + deprecation windows (≥1 minor
  for behavioural changes; immediate only for safety violations with advisory).
- **Portability**: core pure-Python, stdlib-only, 3.10+ floor re-validated by CI
  matrix; adapters declare extras (`bbp`, `javafo`) with platform notes.
- **Licensing**: L-MIT-01; SBOM-friendly (zero runtime deps to attest).
- **Documentation**: spec suite versioned with code; FIDE-rule citations carry
  system + effective date; uncertainty labels retained in user docs.
