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
from pairing_core.rulesets import ConstraintSet, resolve_ruleset
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


def test_native_provider_engine_identity_matches():
    # Self-execution: provider id and effective engine id coincide.
    req = _req([c for c in _engine_cases() if c["id"] == "E-r1-2"][0])
    result = pair_via("native-dutch", req,
                      registry=create_default_registry())
    assert result.engine_id == "native-dutch"


def test_pair_via_never_rewrites_engine_provenance():
    # Delegation honesty: the envelope reports the EFFECTIVE engine, not
    # the selecting provider. pair_via returns the provider envelope
    # unchanged (no silent provenance rewriting).
    from pairing_core import PlayerData

    class DelegatingProvider(EngineProvider):
        @property
        def metadata(self):
            return EngineMetadata(provider_id="demo-delegating",
                                  engine_version="0")

        @property
        def capabilities(self):
            return Capability(
                rulesets=(resolve_ruleset(COMPAT),))

        def pair(self, request):
            return pair_detailed(request)

    players = [PlayerData(id=i, pairing_no=i, rating=2000 - i, points=0.0)
               for i in range(1, 5)]
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=1,
                        constraints=ConstraintSet())
    reg = create_default_registry()
    reg.register(DelegatingProvider())
    result = pair_via("demo-delegating", req, registry=reg)
    assert result.engine_id == "native-dutch"
    assert result.ruleset == resolve_ruleset(COMPAT)


def test_pair_via_returns_provider_envelope_object_unchanged():
    from pairing_core import PlayerData
    players = [PlayerData(id=i, pairing_no=i, rating=2000 - i, points=0.0)
               for i in range(1, 5)]
    req = EngineRequest(players=players, ruleset=COMPAT, round_number=1,
                        constraints=ConstraintSet())
    envelope = pair_detailed(req)
    reg = Registry()
    reg.register(FixedProvider("stub", envelope))
    assert pair_via("stub", req, registry=reg) is envelope
