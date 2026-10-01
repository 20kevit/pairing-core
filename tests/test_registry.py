"""F4-S3 registry tests: explicitness, determinism, resolution ladder."""

import pytest

from pairing_core import EngineRequest
from pairing_core.errors import (
    InvalidRequestError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
)
from pairing_core.provider import (
    Capability,
    EngineMetadata,
    EngineProvider,
    NativeDutchProvider,
)
from pairing_core.registry import Registry, create_default_registry
from pairing_core.rulesets import ConstraintSet, RulesetId
from tests.test_v010_behavioral import _engine_cases, _player

COMPAT = "dutch-till2026-compat"


class StubProvider(EngineProvider):
    def __init__(self, pid):
        self._meta = EngineMetadata(provider_id=pid, engine_version="1")

    @property
    def metadata(self):
        return self._meta

    @property
    def capabilities(self):
        return Capability()

    def pair(self, request):
        raise AssertionError("stub never pairs")


def _req():
    case = [c for c in _engine_cases() if c["id"] == "E-r1-4"][0]
    return EngineRequest(players=[_player(p) for p in case["players"]],
                         ruleset=COMPAT, round_number=1,
                         constraints=ConstraintSet())


def test_register_lookup_and_sorted_listing():
    reg = Registry()
    assert reg.providers() == ()
    b, a = StubProvider("b"), StubProvider("a")
    reg.register(b)
    reg.register(a)
    assert reg.providers() == ("a", "b")
    assert reg.get("a") is a and reg.get("b") is b


def test_duplicate_same_object_ok_other_object_rejected():
    reg = Registry()
    a = StubProvider("a")
    reg.register(a)
    reg.register(a)
    assert reg.get("a") is a
    with pytest.raises(InvalidRequestError):
        reg.register(StubProvider("a"))


def test_register_rejects_non_providers_and_unknown_lookup():
    reg = Registry()
    with pytest.raises(InvalidRequestError):
        reg.register(object())
    with pytest.raises(InvalidRequestError) as exc:
        reg.get("bbp")
    assert "bbp" in str(exc.value)


def test_resolve_success_and_identity():
    reg = create_default_registry()
    p = reg.resolve(_req(), "native-dutch")
    assert isinstance(p, NativeDutchProvider)
    assert reg.resolve(_req(), "native-dutch") is p


def test_resolve_unknown_provider_never_substitutes():
    reg = create_default_registry()
    with pytest.raises(InvalidRequestError):
        reg.resolve(_req(), "bbp")


def test_resolve_unknown_and_unimplemented_ruleset():
    reg = create_default_registry()
    req = _req()
    bad_alias = EngineRequest(players=req.players, ruleset="dubov",
                              round_number=1,
                              constraints=ConstraintSet())
    with pytest.raises(UnsupportedRulesetError):
        reg.resolve(bad_alias, "native-dutch")
    bad_date = EngineRequest(
        players=req.players,
        ruleset=RulesetId(system="dutch", effective_date="2026-02-01"),
        round_number=1, constraints=ConstraintSet())
    with pytest.raises(UnsupportedRulesetError):
        reg.resolve(bad_date, "native-dutch")


def test_resolve_unsupported_constraints():
    reg = create_default_registry()
    req = _req()
    bad = EngineRequest(players=req.players, ruleset=COMPAT, round_number=1,
                        constraints=ConstraintSet(forbidden_pairs=[(1, 2)]))
    with pytest.raises(UnsupportedCapabilityError):
        reg.resolve(bad, "native-dutch")


def test_resolve_rejects_non_request():
    reg = create_default_registry()
    with pytest.raises(InvalidRequestError):
        reg.resolve(object(), "native-dutch")


def test_default_registry_content_and_determinism():
    for _ in range(3):
        reg = create_default_registry()
        assert reg.providers() == ("native-dutch",)
        assert isinstance(reg.get("native-dutch"), NativeDutchProvider)


def test_registries_are_independent():
    assert create_default_registry() is not create_default_registry()
