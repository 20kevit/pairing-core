"""W3 BBP-adapter tests (fixture stub binary; no real BBP needed)."""

import os
import stat
import sys

import pytest

from pairing_core.adapters.bbp import (
    BBPConfig,
    pair_tournament,
    probe_version,
)
from pairing_core.adapters.trf import (
    TournamentInput,
    TrfPlayer,
    TrfRound,
)
from pairing_core.errors import (
    EngineTimeoutError,
    EngineUnavailableError,
    ImpossiblePairingError,
    InternalError,
    InvalidRequestError,
)

STUB = os.path.join(os.path.dirname(__file__), "stubs", "fake_bbp.py")
EXE = [sys.executable, STUB]


def _tournament():
    return TournamentInput(
        players=(
            TrfPlayer(pairing_id=1, name="A", rating=2000, points=1.0,
                      rounds=(TrfRound(2, "w", "1"),)),
            TrfPlayer(pairing_id=2, name="B", rating=1900, points=0.0,
                      rounds=(TrfRound(1, "b", "0"),)),
            TrfPlayer(pairing_id=3, name="C", rating=1800, points=1.0,
                      rounds=(TrfRound(None, "-", "F"),)),
        ),
        rounds_total=2, name="T")


def _run_with_python_stub(monkeypatch, mode, **kw):
    """Point the adapter at the stub through a tiny executable wrapper.

    check_executable requires a directly-executable path, so tests invoke
    python explicitly via a shell-free argv wrapper script.
    """
    import subprocess
    import tempfile
    monkeypatch.setenv("FAKE_BBP_MODE", mode)
    st = os.stat(STUB)
    os.chmod(STUB, st.st_mode | stat.S_IEXEC)
    fd, wrap = tempfile.mkstemp(prefix="fake-bbp-", suffix=".sh")
    with os.fdopen(fd, "w") as fh:
        fh.write(f'#!/bin/sh\nexec {sys.executable} {STUB} "$@"\n')
    os.chmod(wrap, 0o755)
    cfg = BBPConfig(executable=wrap, timeout_seconds=kw.pop(
        "timeout_seconds", 20.0), **kw)
    return cfg, wrap


def test_success_and_capture(monkeypatch, tmp_path):
    cfg, wrap = _run_with_python_stub(monkeypatch, "ok")
    cap = str(tmp_path / "in.trf")
    monkeypatch.setenv("FAKE_BBP_CAPTURE", cap)
    try:
        out = pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)
    assert out.pairs == ((1, 2), (3, None))
    assert "fake" in out.engine_version
    assert out.command[0] == wrap and "--dutch" in out.command
    with open(cap, encoding="utf-8") as fh:
        assert "XXR 2" in fh.read()


def test_exit_mapping(monkeypatch):
    for mode, exc in (("impossible", ImpossiblePairingError),
                      ("invalid", InvalidRequestError),
                      ("crash", InternalError),
                      ("malformed", InternalError)):
        cfg, wrap = _run_with_python_stub(monkeypatch, mode)
        try:
            with pytest.raises(exc):
                pair_tournament(cfg, _tournament())
        finally:
            os.unlink(wrap)


def test_semantic_output_faults_rejected(monkeypatch):
    # Syntactically valid but semantically corrupt engine output must not
    # become a trusted pairing: unknown/dup/self-paired/multi-bye/missing.
    for mode in ("unknownplayer", "duplicate", "selfpair", "multibye",
                 "missing"):
        cfg, wrap = _run_with_python_stub(monkeypatch, mode)
        try:
            with pytest.raises(InternalError):
                pair_tournament(cfg, _tournament())
        finally:
            os.unlink(wrap)


def test_timeout_kills_and_reaps(monkeypatch):
    cfg, wrap = _run_with_python_stub(monkeypatch, "slow",
                                      timeout_seconds=1.0)
    try:
        with pytest.raises(EngineTimeoutError):
            pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)


def test_missing_and_nonexecutable_binary():
    with pytest.raises(EngineUnavailableError):
        pair_tournament(BBPConfig(executable="/nonexistent/bbp"),
                        _tournament())
    with pytest.raises(EngineUnavailableError):
        probe_version("/nonexistent/bbp")


def test_version_probe(monkeypatch):
    cfg, wrap = _run_with_python_stub(monkeypatch, "ok")
    try:
        assert "fake" in probe_version(wrap)
    finally:
        os.unlink(wrap)
    with pytest.raises(EngineUnavailableError):
        probe_version(STUB + ".missing")


def test_config_validation():
    with pytest.raises(InvalidRequestError):
        BBPConfig(executable="x", system="--burstein")
    with pytest.raises(InvalidRequestError):
        BBPConfig(executable="x", timeout_seconds=0)


def test_nonstandard_system_never_wrapped():
    # Burstein is self-declared flawed upstream: the adapter refuses the
    # flag rather than exposing it.
    with pytest.raises(InvalidRequestError):
        BBPConfig(executable="x", system="--burstein")
