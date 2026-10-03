"""Import/API boundary tests (master wave, Phase F).

- Every __all__ entry resolves on the package.
- No internal machinery leaked as top-level names.
- Package version consistent with pyproject.toml.
"""
import tomllib

import pairing_core


def _pyproject_version():
    with open("/opt/projects/pairing-core/pyproject.toml", "rb") as fh:
        return tomllib.load(fh)["project"]["version"]


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
