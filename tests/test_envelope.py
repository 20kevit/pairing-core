"""F3 envelope tests: invariants, serialization, digests, kernel conversion."""

import pytest

from pairing_core.envelope import (
    Pairing,
    RoundPairing,
    canonical_json,
    digest_canonical,
    from_kernel,
    input_digest,
)
from pairing_core.errors import (
    InternalError,
    InvalidRequestError,
    VersionMismatchError,
)
from pairing_core.rulesets import RulesetId

RS = RulesetId(system="dutch", effective_date="2026-01-31")


def _pairing(**kw):
    base = dict(board=1, white_id=1, black_id=2)
    base.update(kw)
    return Pairing(**base)


def _round(**kw):
    base = dict(round_number=1, pairings=(_pairing(board=1, white_id=1,
                                                  black_id=2),
                                         _pairing(board=2, white_id=3,
                                                  black_id=4)),
                engine_id="native-dutch", engine_version="0.1.0",
                ruleset=RS, library_version="0.1.0",
                input_digest="ab" * 32)
    base.update(kw)
    return RoundPairing(**base)


# -- Pairing invariants -----------------------------------------------------

def test_pairing_rejects_self_dup_boards_and_bad_tags():
    with pytest.raises(InvalidRequestError):
        _pairing(white_id=1, black_id=1)
    with pytest.raises(InvalidRequestError):
        _pairing(board=0)
    with pytest.raises(InvalidRequestError):
        _pairing(white_float="X")
    with pytest.raises(InvalidRequestError):
        _pairing(is_bye=True, black_id=2)
    with pytest.raises(InvalidRequestError):
        _pairing(is_bye=False, black_id=None)


def test_bye_pairing_ok():
    assert _pairing(board=3, white_id=5, black_id=None,
                   is_bye=True).is_bye


# -- RoundPairing invariants: partials unrepresentable -----------------------

def test_empty_round_ok_but_nonsequential_rejected():
    assert RoundPairing(round_number=1).pairings == ()
    with pytest.raises(InvalidRequestError):
        _round(pairings=(_pairing(board=1, white_id=1, black_id=2),
                         _pairing(board=3, white_id=3, black_id=4)))


def test_duplicate_player_and_double_bye_rejected():
    with pytest.raises(InvalidRequestError):
        _round(pairings=(_pairing(board=1, white_id=1, black_id=2),
                         _pairing(board=2, white_id=2, black_id=4)))
    with pytest.raises(InvalidRequestError):
        _round(pairings=(_pairing(board=1, white_id=1, black_id=None,
                                  is_bye=True),
                         _pairing(board=2, white_id=3, black_id=None,
                                  is_bye=True)),
               bye_player_id=1)


def test_bye_consistency_enforced():
    ok = _round(pairings=(_pairing(board=1, white_id=1, black_id=2),
                          _pairing(board=2, white_id=5, black_id=None,
                                   is_bye=True)),
                bye_player_id=5)
    assert ok.bye_player_id == 5
    with pytest.raises(InvalidRequestError):
        _round(pairings=(_pairing(board=1, white_id=1, black_id=2),),
               bye_player_id=9)
    with pytest.raises(InvalidRequestError):
        _round(pairings=(_pairing(board=1, white_id=1, black_id=None,
                                  is_bye=True),),
               bye_player_id=None)


# -- serialization: deterministic, versioned ---------------------------------

def test_round_trip_and_canonical_stability():
    rp = _round(warnings=("COL-SCP",))
    d = rp.to_dict()
    assert d["schema"] == 1 and "digest" in d
    assert RoundPairing.from_dict(d) == rp
    assert canonical_json(d) == canonical_json(
        RoundPairing.from_dict(d).to_dict())


def test_digest_mismatch_and_schema_rejected():
    d = _round().to_dict()
    d["bye_player_id"] = 999
    with pytest.raises(VersionMismatchError):
        RoundPairing.from_dict(d)
    with pytest.raises(VersionMismatchError):
        RoundPairing.from_dict({"schema": 999})
    with pytest.raises(InvalidRequestError):
        Pairing.from_dict({"board": 1})


def test_digest_changes_with_content():
    assert digest_canonical({"a": 1}) != digest_canonical({"a": 2})


# -- input digests: order- and hash-independent ---------------------------------

def test_input_digest_stable_and_order_independent():
    from pairing_core import PlayerData
    mk = lambda i: PlayerData(id=i, pairing_no=i, rating=1500, points=1.0,
                              color_hist="w", opponents=frozenset({9 - i}),
                              float_hist="-")
    a = input_digest([mk(1), mk(2)], 2, RS)
    b = input_digest([mk(2), mk(1)], 2, RS)
    assert a == b and len(a) == 64
    assert input_digest([mk(1)], 2, RS) != a


# -- from_kernel: O02 enforcement -------------------------------------------------

def test_from_kernel_rejects_illegal_output():
    from pairing_core import PairingCard, RoundResult
    bad = RoundResult(round_number=1, pairings=[
        PairingCard(board=1, white_id=1, black_id=1)])
    with pytest.raises(InternalError):
        from_kernel(bad, engine_id="native-dutch", engine_version="0.1.0",
                    ruleset=RS, library_version="0.1.0",
                    input_digest_hex="x", warnings=(),
                    validator_errors=("GEN-SELF",))


def test_from_kernel_ok():
    from pairing_core import PairingCard, RoundResult
    good = RoundResult(round_number=2, pairings=[
        PairingCard(board=1, white_id=1, black_id=2)])
    rp = from_kernel(good, engine_id="native-dutch",
                     engine_version="0.1.0", ruleset=RS,
                     library_version="0.1.0", input_digest_hex="x",
                     warnings=("COL-SCP",), validator_errors=())
    assert rp.round_number == 2 and rp.warnings == ("COL-SCP",)
    assert rp.pairings[0].white_id == 1
