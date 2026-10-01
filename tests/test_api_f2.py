"""F2 API-layer tests: strict boundary, compat wrapper, versions report."""

import json
import os

import pytest

from pairing_core import (
    ConstraintSet,
    DUTCH_TILL2026_COMPAT,
    EngineRequest,
    PlayerData,
    RulesetId,
    pair,
    validate_request,
    versions,
)
from pairing_core.errors import (
    ImpossiblePairingError,
    InvalidPlayerError,
    InvalidRequestError,
    PairingError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
)
from tests.test_v010_behavioral import _engine_cases, _player

COMPAT = DUTCH_TILL2026_COMPAT


def _req(players, **kw):
    kw.setdefault("ruleset", COMPAT)
    return EngineRequest(players=players, **kw)


def _pd(pid, **kw):
    base = dict(pairing_no=pid, rating=1500, points=0.0)
    base.update(kw)
    return PlayerData(id=pid, **base)


# -- boundary: adversarial inputs ------------------------------------------

def test_rejects_non_request():
    with pytest.raises(InvalidRequestError):
        validate_request(object())


def test_rejects_non_playerdata():
    class Legacy:
        pass
    with pytest.raises(InvalidRequestError):
        validate_request(_req([Legacy()]))


def test_rejects_duplicate_ids():
    with pytest.raises(InvalidPlayerError) as exc:
        validate_request(_req([_pd(1), _pd(1, pairing_no=2)]))
    assert exc.value.player_id == 1


def test_rejects_bad_pairing_no_and_duplicates():
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, pairing_no=0)]))
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1), _pd(2, pairing_no=1)]))


def test_rejects_bad_rating_points():
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, rating=-5)]))
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, points=float("nan"))]))
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, points=-0.5)]))


def test_rejects_bad_histories():
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, color_hist="wx")]))
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, float_hist="d")]))


def test_rejects_self_and_asymmetric_opponents():
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, opponents={1})]))
    a = _pd(1, opponents={2})
    b = _pd(2, pairing_no=2, rating=1400)
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([a, b]))


def test_rejects_bad_round_and_non_bool_bye():
    with pytest.raises(InvalidRequestError):
        validate_request(_req([_pd(1)], round_number=0))
    with pytest.raises(InvalidPlayerError):
        validate_request(_req([_pd(1, received_bye=1)]))


def test_rejects_bad_forced_shape_and_unknown_ruleset():
    with pytest.raises(InvalidRequestError):
        validate_request(_req([_pd(1), _pd(2, pairing_no=2, rating=1400)],
                              constraints=ConstraintSet(
                                  forced_pairs=[(1,)])))
    with pytest.raises(UnsupportedRulesetError):
        validate_request(_req([_pd(1)], ruleset="dutch-2026"))


def test_unsupported_capabilities_refused_not_ignored():
    players = [_pd(1), _pd(2, pairing_no=2, rating=1400)]
    with pytest.raises(UnsupportedCapabilityError):
        validate_request(_req(players, constraints=ConstraintSet(
            forbidden_pairs=[(1, 2)])))
    with pytest.raises(UnsupportedCapabilityError):
        validate_request(_req(players, constraints=ConstraintSet(
            bye_directive="lowest")))


def test_valid_request_resolves_compat_ruleset():
    rid = validate_request(_req([_pd(1)]))
    assert rid == RulesetId(system="dutch", effective_date="2026-01-31")


# -- compat wrapper: identical outputs on the whole golden corpus -----------

def _fingerprint(result):
    return ([(c.board, c.white_id, c.black_id, c.is_bye,
              c.white_float, c.black_float) for c in result.pairings],
            result.bye_player_id)


def test_wrapper_matches_goldens_exactly():
    for case in _engine_cases():
        req = EngineRequest(
            players=[_player(p) for p in case["players"]],
            ruleset=COMPAT, round_number=case["round"],
            constraints=ConstraintSet(
                forced_pairs=[tuple(x) for x in case["locked"]]
                if case["locked"] else []))
        got = _fingerprint(pair(req))
        want = ([(p["board"], p["white"], p["black"], p["bye"],
                  p["white_float"], p["black_float"])
                 for p in case["expected"]["pairings"]],
                case["expected"]["bye_player_id"])
        assert got == want, case["id"]


def test_wrapper_translates_kernel_failures():
    from tests.test_v010_behavioral import _error_cases
    for case in _error_cases():
        req = EngineRequest(
            players=[_player(p) for p in case["players"]],
            ruleset=COMPAT, round_number=case["round"],
            constraints=ConstraintSet(
                forced_pairs=[tuple(x) for x in case["locked"]]
                if case["locked"] else []))
        with pytest.raises(PairingError) as exc:
            pair(req)
        assert str(exc.value) == case["expected"]["error"]["message"]
    # spot-check categories
    imp = [c for c in _error_cases() if c["id"] == "X-impossible"][0]
    with pytest.raises(ImpossiblePairingError):
        pair(EngineRequest(players=[_player(p) for p in imp["players"]],
                           ruleset=COMPAT, round_number=imp["round"],
                           constraints=ConstraintSet()))


def test_versions_report_statuses():
    v = versions()
    assert v["library"] == {"version": "0.1.0", "status": "implemented"}
    assert v["engines"]["native-dutch"]["status"] == "implemented"
    assert "dutch@2026-01-31" in v["rulesets"]
    assert v["external"]["status"] == "not-implemented"
    assert v["formats"]["TRF16"] == "not-implemented"


def test_new_names_do_not_shadow_legacy():
    import pairing_core as pc
    assert "pair_round" in pc.__all__ and "SwissEngine" in pc.__all__
    assert "pair" in pc.__all__ and "EngineRequest" in pc.__all__
