"""Import/API boundary tests (master wave, Phase F).

- Every __all__ entry resolves on the package.
- No internal machinery leaked as top-level names.
- Package version consistent with pyproject.toml.
"""
try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 has no stdlib tomllib
    tomllib = None
from pathlib import Path

import pairing_core


def _pyproject_version():
    # Location-independent: pyproject next to the test tree when running
    # from a checkout; installed dist metadata when running against an
    # installed wheel (no repository-relative assumptions).
    candidate = Path(__file__).resolve().parents[1] / "pyproject.toml"
    if candidate.is_file():
        if tomllib is not None:
            with open(candidate, "rb") as fh:
                return tomllib.load(fh)["project"]["version"]
        import re
        text = candidate.read_text(encoding="utf-8")
        match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
        assert match, "version not found in pyproject.toml"
        return match.group(1)
    from importlib.metadata import version
    return version("pairing-core")


def test_all_entries_resolve():
    assert len(pairing_core.__all__) == len(set(pairing_core.__all__))
    for name in pairing_core.__all__:
        assert hasattr(pairing_core, name), name


def test_no_internal_leakage():
    # Boundary is __all__: submodule objects (pairing_core.bye etc.)
    # naturally appear as package attributes after import — that is not
    # leakage. Leakage = internal names promoted into the contract.
    public = set(pairing_core.__all__)
    for leaked in ("bracket", "pairer", "color", "floats", "exchange", "bye",
                   "EnginePlayer", "ColorPref", "ColorState", "FloatStatus"):
        assert leaked not in public, leaked
    for leaked in ("EnginePlayer", "ColorPref", "ColorState", "FloatStatus"):
        assert not hasattr(pairing_core, leaked), leaked


def test_version_consistency():
    assert pairing_core.__version__ == _pyproject_version()


def test_canonical_exports_present():
    for name in ("CanonicalPlayer", "CanonicalRequest", "pair_canonical",
                 "canonical_json", "describe_systems",
                 "CANONICAL_REQUEST_SCHEMA", "KNOWN_SYSTEMS",
                 "SYSTEM_DUTCH", "SYSTEM_ROUND_ROBIN"):
        assert name in pairing_core.__all__, name
