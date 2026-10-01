"""F4-S1 provider-contract tests (ABC, metadata, capability, supports)."""

import pytest

from pairing_core.envelope import RoundPairing
from pairing_core.errors import PairingError
from pairing_core.provider import Capability, EngineMetadata, EngineProvider
from pairing_core.rulesets import (
    DUTCH_TILL2026_COMPAT,
    ConstraintSet,
    RulesetId,
    resolve_ruleset,
)

COMPAT = resolve_ruleset(DUTCH_TILL2026_COMPAT)
OTHER = RulesetId(system="dutch", effective_date="2026-02-01")


class StubProvider(EngineProvider):
    def __init__(self, caps, pid="stub", version="0"):
        self._caps = caps
        self._meta = EngineMetadata(provider_id=pid, engine_version=version)

    @property
    def metadata(self):
        return self._meta

    @property
    def capabilities(self):
        return self._caps

    def pair(self, request):
        raise PairingError("stub never pairs")


def test_abc_not_instantiable():
    with pytest.raises(TypeError):
        EngineProvider()


def test_metadata_conveniences():
    p = StubProvider(Capability(), pid="x", version="9")
    assert p.metadata == EngineMetadata(provider_id="x", engine_version="9")
    assert p.provider_id == "x" and p.engine_version == "9"


def test_capability_defaults_deny_everything():
    p = StubProvider(Capability())
    assert p.supports(COMPAT, ConstraintSet()) is False


def test_supports_matrix():
    full = StubProvider(Capability(
        rulesets=(COMPAT,), supports_forced_pairs=True,
        supports_forbidden_pairs=True, supports_bye_directives=True))
    assert full.supports(COMPAT, ConstraintSet()) is True
    assert full.supports(
        COMPAT, ConstraintSet(forced_pairs=[(1, 2)])) is True
    assert full.supports(
        COMPAT, ConstraintSet(forbidden_pairs=[(1, 2)])) is True
    assert full.supports(
        COMPAT, ConstraintSet(bye_directive="lowest")) is True
    assert full.supports(OTHER, ConstraintSet()) is False

    forced_only = StubProvider(Capability(
        rulesets=(COMPAT,), supports_forced_pairs=True))
    assert forced_only.supports(COMPAT, ConstraintSet()) is True
    assert forced_only.supports(
        COMPAT, ConstraintSet(forced_pairs=[(1, 2)])) is True
    assert forced_only.supports(
        COMPAT, ConstraintSet(forbidden_pairs=[(1, 2)])) is False
    assert forced_only.supports(
        COMPAT, ConstraintSet(bye_directive="lowest")) is False
    assert forced_only.supports(OTHER, ConstraintSet()) is False


def test_capability_is_value_and_frozen():
    c = Capability(rulesets=(COMPAT,), deterministic=True)
    assert c == Capability(rulesets=(COMPAT,), deterministic=True)
    with pytest.raises(Exception):
        c.deterministic = False  # frozen dataclass


def test_pair_contract_returns_envelope_or_typed_error():
    p = StubProvider(Capability(rulesets=(COMPAT,)))
    with pytest.raises(PairingError):
        p.pair(object())
    # abstract pair must be overridden: removing it breaks instantiation
    with pytest.raises(TypeError):
        class NoPair(EngineProvider):
            @property
            def metadata(self):
                return EngineMetadata("n", "0")

            @property
            def capabilities(self):
                return Capability()
        NoPair()


def test_roundpairing_success_shape_preserved():
    # The contract's success type is the F3 envelope (no parallel model).
    assert RoundPairing(round_number=1).pairings == ()
