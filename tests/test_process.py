"""Bounded external-process capture: adversarial output-limit tests.

Proves OUTPUT_CAP is enforced DURING collection (reader threads kill the
child as soon as either stream exceeds the cap), not after unlimited
accumulation. The distinguishing cases are infinite-output children: a
post-hoc `len() > cap` check after communicate() could never raise the cap
error there (it would time out or exhaust memory instead).
"""
import os
import signal
import sys
import time
from pathlib import Path

import pytest

from pairing_core.adapters import _process
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


def test_simultaneous_stdout_stderr_floods_rejected():
    # Both pipes flooding at once: no deadlock (concurrent pumps), and
    # the first stream past the cap kills the child -> InternalError.
    start = time.monotonic()
    prog = ("import sys;"
            "so=sys.stdout.buffer.write;se=sys.stderr.buffer.write;"
            "c=b'x'*65536\nwhile True:\n so(c);se(c)")
    with pytest.raises(InternalError, match="capture cap"):
        run_command([PY, "-c", prog], timeout_seconds=60)
    assert time.monotonic() - start < 50


def test_exactly_at_cap_accepted():
    # Boundary: the cap trips only when EXCEEDED (len > cap), so exactly
    # OUTPUT_CAP bytes are a complete successful capture.
    run = run_command(
        [PY, "-c",
         f"import sys;sys.stdout.buffer.write(b'e'*{OUTPUT_CAP})"],
        timeout_seconds=60)
    assert len(run.stdout) == OUTPUT_CAP


def test_one_byte_over_cap_rejected():
    with pytest.raises(InternalError, match="capture cap"):
        run_command(
            [PY, "-c",
             f"import sys;sys.stdout.buffer.write(b'o'*{OUTPUT_CAP + 1})"],
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


@pytest.mark.skipif(os.name != "posix", reason="requires POSIX process groups and fork")
def test_timeout_terminates_forked_descendant(monkeypatch, tmp_path):
    """A timed-out adapter must not leave a grandchild running or holding pipes."""
    monkeypatch.setattr(_process, "KILL_GRACE_SECONDS", 0.1)
    pid_file = tmp_path / "grandchild.pid"
    program = (
        "import os,signal,sys,time\n"
        "pid=os.fork()\n"
        "if pid == 0:\n"
        " signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        " with open(sys.argv[1], 'w') as f: f.write(str(os.getpid()))\n"
        " while True: time.sleep(0.05)\n"
        "else:\n"
        " signal.signal(signal.SIGTERM, signal.SIG_IGN)\n"
        " print('child-ready', flush=True)\n"
        " while True: time.sleep(0.05)\n"
    )
    grandchild_pid = None
    try:
        with pytest.raises(EngineTimeoutError, match="wall-clock budget"):
            run_command([PY, "-c", program, str(pid_file)], timeout_seconds=0.2)
        assert pid_file.exists(), "grandchild should have started before timeout"
        grandchild_pid = int(pid_file.read_text())
        # On Linux, treat an orphaned zombie as stopped; it cannot execute or
        # retain the adapter's pipe descriptors.
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            try:
                os.kill(grandchild_pid, 0)
            except ProcessLookupError:
                break
            proc_stat = Path(f"/proc/{grandchild_pid}/stat")
            if proc_stat.exists() and proc_stat.read_text().split(") ", 1)[-1][:1] == "Z":
                break
            time.sleep(0.02)
        else:
            pytest.fail(f"forked descendant {grandchild_pid} survived timeout")
    finally:
        if grandchild_pid is not None:
            try:
                os.kill(grandchild_pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
