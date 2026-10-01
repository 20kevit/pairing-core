"""F2 error-taxonomy tests: hierarchy, categories, kernel translation."""

import pytest

from pairing_core.errors import (
    CancelledError,
    DuplicatePlayerIdError,
    EngineTimeoutError,
    EngineUnavailableError,
    ImpossiblePairingError,
    InternalError,
    InvalidPlayerError,
    InvalidRequestError,
    PairingError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
    VersionMismatchError,
    translate_kernel_error,
)


def test_all_taxonomy_is_pairing_error_and_value_error():
    for cls in (InvalidRequestError, InvalidPlayerError,
                DuplicatePlayerIdError, ImpossiblePairingError,
                EngineTimeoutError, CancelledError, EngineUnavailableError,
                UnsupportedCapabilityError, UnsupportedRulesetError,
                VersionMismatchError, InternalError):
        assert issubclass(cls, PairingError)
        # v0.1.0 isinstance-compatibility (O08): old `except ValueError`
        # handlers keep catching the new typed errors.
        assert issubclass(cls, ValueError)


def test_hierarchy_nesting():
    assert issubclass(InvalidPlayerError, InvalidRequestError)
    assert issubclass(DuplicatePlayerIdError, InvalidPlayerError)
    for cls in (ImpossiblePairingError, EngineTimeoutError, CancelledError,
                EngineUnavailableError, UnsupportedCapabilityError,
                UnsupportedRulesetError, VersionMismatchError, InternalError):
        assert not issubclass(cls, InvalidRequestError)


def test_categories_are_distinct():
    assert not issubclass(ImpossiblePairingError, InvalidRequestError)
    assert not issubclass(EngineTimeoutError, ImpossiblePairingError)
    assert not issubclass(UnsupportedRulesetError,
                           UnsupportedCapabilityError)


def test_player_id_carried():
    err = InvalidPlayerError("bad pno", player_id=7)
    assert err.player_id == 7
    assert str(err) == "bad pno"


def test_translate_locked_pair():
    src = ValueError("Locked pair #1: players 1 and 2 have already played.")
    out = translate_kernel_error(src)
    assert type(out) is InvalidRequestError
    assert str(out) == str(src)
    assert out.__cause__ is src


def test_translate_impossible():
    src = ValueError("Round 4: No legal FIDE Dutch pairing exists for 4.")
    out = translate_kernel_error(src, ruleset="dutch-till2026-compat",
                                 round_number=4)
    assert type(out) is ImpossiblePairingError
    assert str(out) == str(src)
    assert out.__cause__ is src


def test_translate_step_cap_is_timeout():
    src = ValueError("Pairing complexity exceeded limit (2000000 nodes).")
    out = translate_kernel_error(src)
    assert type(out) is EngineTimeoutError
    assert out.__cause__ is src


def test_translate_unknown_is_internal():
    src = ValueError("something entirely unexpected")
    out = translate_kernel_error(src)
    assert type(out) is InternalError
    assert out.__cause__ is src
