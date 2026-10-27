# Packaging and dependency audit

**Source snapshot:** unreleased `0.4.2.dev0`, audited 2026-10-27.
**Immutable release:** `v0.4.1` and its published artifacts are unchanged.
This report supersedes the Stage-1 `v0.1.0` inventory formerly in this file;
that inventory's claims about missing license text, absent classifiers, and
undeclared test tooling described a historical checkout.

## Current metadata

| Field | Verified value |
|---|---|
| Build backend | `setuptools.build_meta`, build requirement `setuptools>=77` |
| Package version | `0.4.2.dev0` in `pyproject.toml` and `pairing_core.__version__`; unreleased development snapshot |
| Python metadata floor | `>=3.10` |
| CI interpreter matrix | Configured for CPython 3.10–3.15; this audit revision still requires a green CI run across the matrix |
| License | MIT declared in project metadata and present in root `LICENSE` |
| Runtime dependencies | None declared; runtime stays stdlib + intra-package |
| Optional test dependencies | `pytest>=8` and pinned `ruff==0.17.3` in the `test` extra |
| Package layout | `src/`; no console scripts or runtime entry points |
| Published release | `v0.4.1` is immutable; audit work is not released under that version |

The build backend requirement is a build-time dependency, not an installed
runtime dependency. Test and static-check tooling is optional and installed
only with the `test` extra.

## Python compatibility policy

The `>=3.10` floor is retained to avoid dropping the published compatibility
floor during this audit. The CI workflow exercises 3.10–3.15; matrix
configuration is not a substitute for a passing run on the exact source
revision. CPython 3.10 reached upstream end-of-life on 2026-10-01. It remains
in CI as a compatibility check, but this package cannot provide upstream
interpreter security fixes for it. CPython 3.11–3.15 are the maintained
release branches listed by the Python Developer's Guide as of the audit date.
The `Requires-Python` lower bound alone does not promise tested compatibility
with every future Python minor.

Source: <https://devguide.python.org/versions/> (retrieved 2026-10-27).
See G-09 in [`GAP_REGISTER.md`](GAP_REGISTER.md) for the outstanding
revision-specific CI evidence.

## Verification and remaining limits

- This audit built the `0.4.2.dev0` wheel and sdist, checked version,
  `Requires-Python`, MIT license, optional-only dependencies, and source
  inclusion, then installed the wheel in an isolated environment and ran the
  public API and example smoke checks. The exact current results are in
  [`GAP_REGISTER.md`](GAP_REGISTER.md); the hosted interpreter matrix remains
  pending.
- The targeted Ruff CI gate checks undefined names (`F821`) only. It does not
  claim broad lint cleanliness; unused-import/style debt outside the touched
  scope remains separately triaged.
- No new third-party runtime dependency is introduced by the Burstein input
  seam or process-group supervision.
- The release/tag verification for `v0.4.1` is recorded in
  [`GAP_REGISTER.md`](GAP_REGISTER.md); do not rebuild or move it.

## Dependency boundary

Pairing-Core remains pairing-only. `tiebreak-core` is a separate library and
is not a runtime dependency. The inspected tiebreak-core v1.2.0 source has
C.07 calculators but no C.04.4.2 Burstein Index calculator; no C.07 value is
silently substituted. See [`../spec/TIEBREAK_ARCHITECTURE.md`](../spec/TIEBREAK_ARCHITECTURE.md).
