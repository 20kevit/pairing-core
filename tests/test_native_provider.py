"""F4-S2 native-provider tests: identity, gating, seam, propagation."""

import pytest

from pairing_core import EngineRequest, __version__, pair_detailed
from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidRequestError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
)
from pairing_core.provider import Capability, NativeDutchProvider
from pairing_core.rulesets import (
    ConstraintSet,
    RulesetId,
    resolve_ruleset,
)
from tests.test_v010_behavioral import _engine_cases, _error_cases, _player

COMPAT = "dutch-till2026-compat"


def _req(case):
    return EngineRequest(
        players=[_player(p) for p in case["players"]],
        ruleset=COMPAT, round_number=case["round"],
        constraints=ConstraintSet(
            forced_pairs=[tuple(x) for x in case["locked"]]
            if case["locked"] else []))


def _fp(result):
    return ([(c.board, c.white_id, c.black_id, c.is_bye,
              c.white_float, c.black_float) for c in result.pairings],
            result.bye_player_id)


def test_identity_and_capability():
    p = NativeDutchProvider()
    assert p.provider_id == "native-dutch"
    assert p.engine_version == __version__
    caps = p.capabilities
    assert isinstance(caps, Capability)
    assert caps.rulesets == (resolve_ruleset(COMPAT),)
    assert caps.supports_forced_pairs is True
    assert caps.supports_forbidden_pairs is True
    assert caps.supports_bye_directives is False
    assert caps.deterministic is True
    # honest identity: compat ruleset only, never relabelled
    assert caps.rulesets == (RulesetId(system="dutch",
                                       effective_date="2026-01-31"),)


def test_native_matches_detailed_seam_on_goldens():
    p = NativeDutchProvider()
    for case in _engine_cases():
        assert _fp(p.pair(_req(case))) == _fp(pair_detailed(_req(case)))


def test_unsupported_ruleset_and_constraints():
    p = NativeDutchProvider()
    base = [c for c in _engine_cases() if c["id"] == "E-r1-4"][0]
    with pytest.raises(UnsupportedRulesetError):
        p.pair(EngineRequest(
            players=[_player(x) for x in base["players"]],
            ruleset=RulesetId(system="dutch", effective_date="2026-02-01"),
            round_number=1, constraints=ConstraintSet()))
    with pytest.raises(UnsupportedCapabilityError):
        p.pair(EngineRequest(
            players=[_player(x) for x in base["players"]],
            ruleset=COMPAT, round_number=1,
            constraints=ConstraintSet(bye_directive="lowest")))
    with pytest.raises(InvalidRequestError):
        p.pair(object())


def test_error_propagation_typed():
    p = NativeDutchProvider()
    imp = [c for c in _error_cases() if c["id"] == "X-impossible"][0]
    with pytest.raises(ImpossiblePairingError):
        p.pair(EngineRequest(
            players=[_player(x) for x in imp["players"]],
            ruleset=COMPAT, round_number=imp["round"],
            constraints=ConstraintSet()))
