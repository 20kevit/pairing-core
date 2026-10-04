# Versioning Specification (ADOPTED)

Status: adopted and enforced — CHANGELOG practice, O08 deprecation window,
and version-consistency tests (`test_import_api.py`, `test_release.py`).
(Stage-3 draft label removed 0.4.1; body unchanged.)

Five independent versions (mission §3.13), never conflated:

1. **Library version** (semver): public API + behaviour contract. Breaking =
   major; additive = minor; fixes = patch. Behavioural changes (search order,
   bye choice, float tags, board order) are MAJOR or minor-with-deprecation.
2. **Engine version**: per-engine kernel identity (`native-dutch 2.x`,
   `bbp 5.0.1`, `javafo 2.2/b3222`). Recorded on every result; mismatch with
   request = typed error.
3. **Ruleset version**: `(system, effective-date)` + acceleration/point-value
   profile. New FIDE text ⇒ new ruleset id; old ids keep working (compat
   harness pins them).
4. **External engine version**: release+build as reported (`-r` output stored
   in envelope); re-verify on change.
5. **Input format version**: TRF dialect + revision (`TRF16`, `TRF26`, `TRFx`
   + extension set); strict parser matrix per dialect.

Policy: changelog entries cite all five where relevant; **two-minor-release
deprecation window for normal public API/behaviour deprecations** (O08 FINAL;
documented security/critical exceptions only, with advisory); safety fixes may
break immediately with a
security advisory. `__version__` reports library version only; the rest is
queryable (`versions()` report) and envelope-recorded.
