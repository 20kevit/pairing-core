"""Supervised subprocess execution for engine adapters (INTERNAL).

Not exported from pairing_core.adapters. Rules (SECURITY.md posture,
blueprint H, O10):

- argv lists only, never shell strings. POSIX launches in a fresh session and
  terminates the complete process group on timeout, output overflow, or
  completion. Windows currently guarantees direct-child cleanup only.
- Bounded stdout/stderr capture (10 MiB each; beyond -> InternalError, not
  memory exhaustion). The bound is enforced DURING collection by reader
  threads that stop the process group as soon as either stream exceeds the
  cap. Strict UTF-8 decode; undecodable bytes -> InternalError.
- Args, executable path, and working directory are caller-supplied and
  explicit (BYO binaries). No PATH searching, no downloading, no guessing.
- Returns CompletedRun; interpretation (exit-code mapping) belongs to the
  per-engine adapter, which has the authoritative manual.
"""

from __future__ import annotations

import errno
import math
import os
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from typing import BinaryIO, List, Optional, Sequence

from pairing_core.errors import EngineTimeoutError, InternalError

OUTPUT_CAP = 10 * 1024 * 1024
KILL_GRACE_SECONDS = 5.0
_READ_CHUNK = 65536
_POLL_INTERVAL_SECONDS = 0.05


@dataclass(frozen=True)
class CompletedRun:
    """INTERNAL. Captured outcome of one supervised execution."""
    argv: tuple
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool


def _pump_pipe(stream: BinaryIO, buf: bytearray, lock: threading.Lock,
               over: List[bool], over_event: threading.Event) -> None:
    """Drain one child pipe in chunks, enforcing OUTPUT_CAP.

    Runs on a daemon reader thread so both pipes drain concurrently (no
    deadlock when the child fills one pipe while writing the other). Sets
    over/over_event as soon as a stream exceeds the cap. Parent memory per
    stream is bounded by OUTPUT_CAP plus one read chunk. A closed/torn-down
    pipe reads as EOF (ValueError/OSError tolerated).
    """
    try:
        while True:
            chunk = stream.read(_READ_CHUNK)
            if not chunk:
                return
            with lock:
                buf += chunk
                if len(buf) > OUTPUT_CAP and not over[0]:
                    over[0] = True
                    over_event.set()
                    return
    except (OSError, ValueError):
        return


def _group_exists(pgid: int) -> bool:
    """Whether a POSIX process group still has members."""
    try:
        os.killpg(pgid, 0)
        return True
    except OSError as exc:
        if exc.errno == errno.ESRCH:
            return False
        if exc.errno == errno.EPERM:
            return True
        raise


def _signal_group(proc: subprocess.Popen, sig: int) -> None:
    """Signal this run's isolated POSIX process group, tolerating exit races."""
    try:
        os.killpg(proc.pid, sig)
    except OSError as exc:
        if exc.errno not in (errno.ESRCH, errno.EPERM):
            raise


def _terminate_process_tree(proc: subprocess.Popen) -> None:
    """Terminate this run and descendants, escalating after a grace period.

    POSIX children are started in a fresh session, making ``proc.pid`` the
    process-group id. TERM is given the documented grace, then KILL is sent
    to any surviving group members. Windows falls back to Popen's direct
    process termination; Python's standard library has no portable Job
    Object API for guaranteed descendant cleanup there.
    """
    if os.name == "posix":
        _signal_group(proc, signal.SIGTERM)
        deadline = time.monotonic() + KILL_GRACE_SECONDS
        while time.monotonic() < deadline:
            if not _group_exists(proc.pid):
                break
            time.sleep(min(_POLL_INTERVAL_SECONDS,
                           max(0.0, deadline - time.monotonic())))
        if _group_exists(proc.pid):
            _signal_group(proc, signal.SIGKILL)
    elif proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=KILL_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            proc.kill()
        except OSError:
            pass
    try:
        proc.wait(timeout=KILL_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            proc.kill()
        except OSError:
            pass
        proc.wait()


def _finish_readers(proc: subprocess.Popen,
                    readers: List[threading.Thread]) -> None:
    """Drain pipes and clean up descendants that inherited their handles."""
    for thread in readers:
        thread.join(timeout=KILL_GRACE_SECONDS)
    if any(thread.is_alive() for thread in readers):
        # A normal-exit parent can leave a grandchild holding a pipe open.
        # Stop the isolated group rather than returning while it leaks.
        _terminate_process_tree(proc)
    for pipe in (proc.stdout, proc.stderr):
        try:
            if pipe is not None:
                pipe.close()
        except (OSError, ValueError):
            pass
    for thread in readers:
        thread.join(timeout=KILL_GRACE_SECONDS)


def run_command(argv: Sequence[str], *, timeout_seconds: float,
                workdir: Optional[str] = None) -> CompletedRun:
    """Run argv without a shell, with a deadline and bounded capture.

    Timeout -> EngineTimeoutError after process-tree termination and reaping.
    Either stream exceeding 10 MiB -> InternalError after terminating the
    process tree. POSIX descendants are included; on Windows only the direct
    child is guaranteed to be stopped. Spawn failures -> InternalError.
    """
    if (not isinstance(argv, Sequence) or isinstance(argv, (str, bytes))
            or not argv or any(not isinstance(arg, str) for arg in argv)):
        raise InternalError("run_command requires a non-empty argv sequence of strings.")
    try:
        timeout_value = float(timeout_seconds)
    except (TypeError, ValueError, OverflowError):
        timeout_value = float("nan")
    if (not isinstance(timeout_seconds, (int, float))
            or isinstance(timeout_seconds, bool)
            or not math.isfinite(timeout_value) or timeout_value <= 0):
        raise InternalError("run_command requires timeout_seconds > 0.")
    if workdir is not None and not isinstance(workdir, (str, os.PathLike)):
        raise InternalError("workdir must be a filesystem path or None.")

    start = time.monotonic()
    popen_options = {}
    if os.name == "posix":
        popen_options["start_new_session"] = True
    elif os.name == "nt":
        popen_options["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    try:
        proc = subprocess.Popen(
            list(argv), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=workdir, shell=False, **popen_options)
    except (OSError, ValueError) as exc:
        raise InternalError(f"cannot spawn {argv[0]!r}: {exc}") from exc

    out_buf = bytearray()
    err_buf = bytearray()
    lock = threading.Lock()
    over = [False]
    over_event = threading.Event()
    readers = [
        threading.Thread(target=_pump_pipe,
                         args=(proc.stdout, out_buf, lock, over, over_event),
                         name="pairing-core-stdout-pump", daemon=True),
        threading.Thread(target=_pump_pipe,
                         args=(proc.stderr, err_buf, lock, over, over_event),
                         name="pairing-core-stderr-pump", daemon=True),
    ]
    for thread in readers:
        thread.start()

    try:
        deadline = start + timeout_value
        timed_out = False
        while True:
            if over_event.is_set():
                _terminate_process_tree(proc)
                break
            if proc.poll() is not None:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                _terminate_process_tree(proc)
                break
            over_event.wait(timeout=min(_POLL_INTERVAL_SECONDS, remaining))

        if timed_out:
            _finish_readers(proc, readers)
            elapsed = time.monotonic() - start
            raise EngineTimeoutError(
                f"engine exceeded {timeout_seconds}s wall-clock budget "
                f"(terminated after {elapsed:.1f}s).") from None
        if over_event.is_set():
            _finish_readers(proc, readers)
            raise InternalError("engine output exceeded 10 MiB capture cap.")

        # The direct child exited. Drain output and then stop any same-session
        # descendants that outlived it, even if they closed inherited pipes.
        _finish_readers(proc, readers)
        # A reader can observe a final over-cap chunk only while draining
        # after the child has exited. Recheck after both readers finish so a
        # short-lived producer cannot evade the cap by winning this race.
        if over_event.is_set():
            raise InternalError("engine output exceeded 10 MiB capture cap.")
        if os.name == "posix":
            _terminate_process_tree(proc)
        out = bytes(out_buf)
        err = bytes(err_buf)
    finally:
        # Absolute cleanup on every path: no child zombies, leaked fds, or
        # same-process-group descendants on POSIX.
        try:
            if proc.poll() is None:
                _terminate_process_tree(proc)
            elif os.name == "posix":
                _terminate_process_tree(proc)
        finally:
            for pipe in (proc.stdout, proc.stderr):
                try:
                    if pipe is not None:
                        pipe.close()
                except (OSError, ValueError):
                    pass

    elapsed = time.monotonic() - start
    try:
        stdout = out.decode("utf-8")
        stderr = err.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InternalError(f"engine output is not UTF-8: {exc}") from exc
    return CompletedRun(argv=tuple(argv), returncode=proc.returncode,
                        stdout=stdout, stderr=stderr,
                        elapsed_seconds=elapsed, timed_out=False)


def check_executable(path: str, what: str) -> str:
    """INTERNAL. Validate an explicit binary path (exists + executable)."""
    from pairing_core.errors import EngineUnavailableError

    if not isinstance(path, str) or not path:
        raise EngineUnavailableError(f"{what}: explicit path required.")
    if not os.path.isfile(path) or not os.access(path, os.X_OK):
        raise EngineUnavailableError(
            f"{what}: not an executable file: {path!r}.")
    return path


def temp_workdir() -> tempfile.TemporaryDirectory:
    """INTERNAL. Scratch dir for one adapter run (caller cleans up)."""
    return tempfile.TemporaryDirectory(prefix="pairing-core-")
