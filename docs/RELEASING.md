# Releasing pairing-core

Releases are cut from a clean `main` checkout. No developer-machine state,
untracked files, or environment variables may affect the artifact. External
engines (BBP, JaVaFo) stay bring-your-own and are never bundled.

## Preconditions

- `git status` clean, branch `main`, remote `origin` =
  `git@github.com:20kevit/pairing-core.git`.
- Version decided per `docs/spec/VERSIONING.md` (semver library version;
  v0.1.0 kernel behavior permanently golden). Do not manufacture a major
  bump: documentation/packaging/hygiene-only waves ship as patch or minor.

## Steps

1. Set the version in **both** places (they must agree; enforced by
   `tests/test_import_api.py`):
   - `pyproject.toml` (`[project] version`)
   - `src/pairing_core/__init__.py` (`__version__`)
2. Add a `CHANGELOG.md` entry (all five version axes where relevant).
3. Run the release gate (same as CI):
   ```bash
   python3 -m pytest tests/ -q
   rm -rf dist/ build/ && python3 -m build --wheel --sdist
   # inspect: no __pycache__/.pyc/egg-info beyond the standard manifest,
   # LICENSE present, METADATA version matches
   tar tzf dist/pairing-core-<ver>.tar.gz | sort | head
   python3 examples/basic_swiss.py > /dev/null && echo EXAMPLE-OK
   ```
4. Verify in a clean environment (no repo on `sys.path`):
   ```bash
   python3 -m venv /tmp/pc-release-check && /tmp/pc-release-check/bin/python \
     -m pip install dist/pairing-core-<ver>-py3-none-any.whl
   /tmp/pc-release-check/bin/python examples/basic_swiss.py > /dev/null \
     && echo INSTALL-OK
   ```
5. Commit, tag `v<ver>`, push both:
   ```bash
   git commit -m "release: v<ver>"
   git tag v<ver>
   git push origin main v<ver>
   ```
6. Remove local build outputs (`rm -rf dist/ build/`) so the tree stays
   clean; both are git-ignored.

## Artifact policy

- Wheel + sdist from `python -m build` only. Reproducible: same commit →
  same file list (timestamps inside archives differ; content does not).
- The sdist contains the standard setuptools `egg-info/SOURCES.txt`
  manifest record only — no caches, tests artifacts, credentials, or
  local paths.
- Never commit `dist/`, `build/`, `*.egg-info/`, or refreshed benchmark
  baselines unless the refresh itself is the change (use
  `PAIRING_UPDATE_BASELINES=1` explicitly, then commit deliberately).
