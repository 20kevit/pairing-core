"""F4-S4 provider-path tests: explicit wiring, seam guards, no fallback."""

import pytest

from pairing_core import (
    EngineRequest,
    RoundPairing,
    create_default_registry,
    pair_detailed,
    pair_via,
)
from pairing_core.envelope import RoundPairing as EnvelopeRoundPairing
from pairing_core.errors import InternalError, InvalidRequestError
from pairing_core.provider import (
    Capability,
    EngineMetadata,
    EngineProvider,
)
from pairing_core.registry import Registry
from pairing_core.rulesets import ConstraintSet
from tests.test_v010_behavioral import _engine_cases, _player

COMPAT = "dutch-till2026-compat"


def _req(case):
    return EngineRequest(
        players=[_player(p) for p in case["players"]],
        ruleset=COMPAT, round_number=case["round"],
        constraints=ConstraintSet(
            forced_pairs=[tuple(x) for x in case["locked"]]
            if case["locked"] else []))


class FixedProvider(EngineProvider):
    """Test double returning a canned envelope (or garbage)."""

    def __init__(self, pid, result):
        self._meta = EngineMetadata(provider_id=pid, engine_version="t")
        self._result = result

    @property
    def metadata(self):
        return self._meta

    @property
    def capabilities(self):
        from pairing_core.rulesets import resolve_ruleset
        return Capability(rulesets=(resolve_ruleset(COMPAT),))

    def pair(self, request):
        return self._result


def test_pair_via_native_matches_detailed_on_goldens():
    for case in _engine_cases():
        req = _req(case)
        assert pair_via("native-dutch", req) == pair_detailed(req)


def test_pair_via_uses_given_registry():
    reg = Registry()
    canned = RoundPairing(round_number=1)
    reg.register(FixedProvider("stub", canned))
    req = _req([c for c in _engine_cases() if c["id"] == "E-empty"][0])
    assert pair_via("stub", req, registry=reg) == canned


def test_pair_via_rejects_invalid_provider_result():
    reg = Registry()
    reg.register(FixedProvider("bad", "not-a-roundpairing"))
    req = _req([c for c in _engine_cases() if c["id"] == "E-empty"][0])
    with pytest.raises(InternalError):
        pair_via("bad", req, registry=reg)


def test_pair_via_unknown_provider_never_substitutes():
    req = _req([c for c in _engine_cases() if c["id"] == "E-r1-2"][0])
    with pytest.raises(InvalidRequestError):
        pair_via("bbp", req)
    with pytest.raises(InvalidRequestError):
        pair_via("bbp", req, registry=create_default_registry())


def test_pair_via_rejects_non_registry():
    req = _req([c for c in _engine_cases() if c["id"] == "E-empty"][0])
    with pytest.raises(InvalidRequestError):
        pair_via("native-dutch", req, registry=object())


def test_envelope_identity_single_model():
    assert EnvelopeRoundPairing is RoundPairing
