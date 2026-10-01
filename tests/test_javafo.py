"""W5 JaVaFo-adapter tests (fixture stub binary; no JVM needed)."""

import os
import sys

import pytest

from pairing_core.adapters.javafo import (
    JaVaFoConfig,
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
    InternalError,
    InvalidRequestError,
)

STUB = os.path.join(os.path.dirname(__file__), "stubs", "fake_javafo.py")


def _wrapper(monkeypatch, mode, **kw):
    """Executable sh wrapper: [sh] -> python stub (BYO shape)."""
    import tempfile
    monkeypatch.setenv("FAKE_JAVAFO_MODE", mode)
    # Emulate `java -jar jar`: wrapper strips the -jar pair, then execs
    # the python stub with the remaining args.
    fd, wrap = tempfile.mkstemp(prefix="fake-javafo-", suffix=".sh")
    with os.fdopen(fd, "w") as fh:
        fh.write(f'#!/bin/sh\nif [ "$1" = "-jar" ]; then shift; shift; fi\n'
                 f'exec {sys.executable} {STUB} "$@"\n')
    os.chmod(wrap, 0o755)
    cfg = JaVaFoConfig(java_executable=wrap, jar_path=STUB,
                       timeout_seconds=kw.pop("timeout_seconds", 20.0),
                       **kw)
    return cfg, wrap


def _tournament():
    return TournamentInput(
        players=(
            TrfPlayer(pairing_id=1, name="A", rating=2000, points=1.0,
                      rounds=(TrfRound(2, "w", "1"),)),
            TrfPlayer(pairing_id=2, name="B", rating=1900, points=0.0,
                      rounds=(TrfRound(1, "b", "0"),)),
        ),
        rounds_total=2, name="T")


def test_success_and_capture(monkeypatch, tmp_path):
    cfg, wrap = _wrapper(monkeypatch, "ok")
    cap = str(tmp_path / "in.trf")
    monkeypatch.setenv("FAKE_JAVAFO_CAPTURE", cap)
    try:
        out = pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)
    assert out.pairs == ((1, 2), (3, None))
    assert "JaVaFo" in out.engine_version
    assert out.command[1] == "-jar"
    with open(cap, encoding="utf-8") as fh:
        assert "XXR 2" in fh.read()


def test_failure_modes(monkeypatch):
    cfg, wrap = _wrapper(monkeypatch, "fail")
    try:
        with pytest.raises(InternalError):
            pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)
    cfg, wrap = _wrapper(monkeypatch, "malformed")
    try:
        with pytest.raises(InternalError):
            pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)
    cfg, wrap = _wrapper(monkeypatch, "slow", timeout_seconds=1.0)
    try:
        with pytest.raises(EngineTimeoutError):
            pair_tournament(cfg, _tournament())
    finally:
        os.unlink(wrap)


def test_unavailable_paths():
    with pytest.raises(EngineUnavailableError):
        pair_tournament(JaVaFoConfig(java_executable="/nonexistent/java",
                                     jar_path="/nonexistent.jar"),
                        _tournament())
    with pytest.raises(EngineUnavailableError):
        pair_tournament(JaVaFoConfig(java_executable=sys.executable,
                                     jar_path="/nonexistent.jar"),
                        _tournament())
    with pytest.raises(EngineUnavailableError):
        probe_version(JaVaFoConfig(java_executable="/nonexistent/java",
                                   jar_path="/nonexistent.jar"))


def test_bad_version_output(monkeypatch):
    cfg, wrap = _wrapper(monkeypatch, "badversion")
    try:
        with pytest.raises(EngineUnavailableError):
            probe_version(cfg)
    finally:
        os.unlink(wrap)


def test_config_validation():
    with pytest.raises(InvalidRequestError):
        JaVaFoConfig(java_executable="x", jar_path="y", timeout_seconds=0)
