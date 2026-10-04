"""Bounded external-process capture: adversarial output-limit tests.

Proves OUTPUT_CAP is enforced DURING collection (reader threads kill the
child as soon as either stream exceeds the cap), not after unlimited
accumulation. The distinguishing cases are infinite-output children: a
post-hoc `len() > cap` check after communicate() could never raise the cap
error there (it would time out or exhaust memory instead).
"""
import sys
import time

import pytest

from pairing_core.adapters._process import OUTPUT_CAP, run_command
from pairing_core.errors import EngineTimeoutError, InternalError

PY = sys.executable

FLOOD_STDOUT = (
    "import sys;w=sys.stdout.buffer.write;c=b'x'*65536\n"
    "while True:\n w(c)"
)
FLOOD_STDERR = (
    "import sys;w=sys.stderr.buffer.write;c=b'e'*65536\n"
    "while True:\n w(c)"
)


def test_small_output_exact_bytes_preserved():
    run = run_command(
        [PY, "-c", "import sys;sys.stdout.write('hi');sys.stderr.write('er')"],
        timeout_seconds=30)
    assert (run.stdout, run.stderr, run.returncode, run.timed_out) == \
        ("hi", "er", 0, False)


def test_infinite_stdout_rejected_by_cap_not_timeout():
    start = time.monotonic()
    with pytest.raises(InternalError, match="capture cap"):
        run_command([PY, "-c", FLOOD_STDOUT], timeout_seconds=60)
    assert time.monotonic() - start < 50


def test_infinite_stderr_rejected_by_cap_not_timeout():
    start = time.monotonic()
    with pytest.raises(InternalError, match="capture cap"):
        run_command([PY, "-c", FLOOD_STDERR], timeout_seconds=60)
    assert time.monotonic() - start < 50


def test_finite_oversize_stdout_rejected():
    over = OUTPUT_CAP + 1024
    with pytest.raises(InternalError, match="capture cap"):
        run_command(
            [PY, "-c",
             f"import sys;sys.stdout.buffer.write(b'z'*{over})"],
            timeout_seconds=60)


def test_just_under_cap_accepted():
    under = OUTPUT_CAP - 1024
    run = run_command(
        [PY, "-c", f"import sys;sys.stdout.buffer.write(b'q'*{under})"],
        timeout_seconds=60)
    assert len(run.stdout) == under


def test_timeout_still_typed_with_output_flowing():
    with pytest.raises(EngineTimeoutError, match="wall-clock budget"):
        run_command(
            [PY, "-c",
             "import sys,time\n"
             "for _ in range(600):\n"
             " sys.stdout.write('tick\\n');sys.stdout.flush();time.sleep(0.2)"],
            timeout_seconds=2)


def test_non_utf8_rejected():
    with pytest.raises(InternalError, match="not UTF-8"):
        run_command(
            [PY, "-c", "import sys;sys.stdout.buffer.write(bytes([0xff]))"],
            timeout_seconds=30)


def test_spawn_failure_typed():
    with pytest.raises(InternalError, match="cannot spawn"):
        run_command(["/nonexistent-engine-binary-xyz"], timeout_seconds=5)


def test_timeout_validation():
    with pytest.raises(InternalError, match="timeout_seconds"):
        run_command([PY, "-c", "pass"], timeout_seconds=0)
    with pytest.raises(InternalError, match="timeout_seconds"):
        run_command([PY, "-c", "pass"], timeout_seconds=None)


def test_nonzero_exit_preserved():
    run = run_command([PY, "-c", "import sys;sys.exit(3)"],
                      timeout_seconds=30)
    assert run.returncode == 3
