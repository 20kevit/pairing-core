"""Supervised subprocess execution for engine adapters (INTERNAL).

Not exported from pairing_core.adapters. Rules (SECURITY.md posture,
blueprint H, O10):

- argv lists only, never shell strings (no shell=True, no unsanitized
  interpolation). Timeouts kill after a grace period and reap (no zombies).
- Bounded stdout/stderr capture (10 MiB each; beyond -> InternalError, not
  memory exhaustion). The bound is enforced DURING collection by reader
  threads that kill the child as soon as either stream exceeds the cap, so
  a hostile executable cannot grow parent memory by writing unlimited
  output. Strict UTF-8 decode; undecodable bytes -> InternalError.
- Args, executable path, and working directory are caller-supplied and
  explicit (BYO binaries). No PATH searching, no downloading, no guessing.
- Returns CompletedRun; interpretation (exit-code mapping) belongs to the
  per-engine adapter, which has the authoritative manual.
"""

from __future__ import annotations

import os
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
    """INTERNAL. Drain one child pipe in chunks, enforcing OUTPUT_CAP.

    Runs on a daemon reader thread so both pipes drain concurrently (no
    deadlock when the child fills one pipe while writing the other).
    Sets over/over_event the moment this stream exceeds the cap; the
    main thread then kills the child. Parent memory per stream never
    exceeds OUTPUT_CAP + one chunk, regardless of child output volume.
    A closed/torn-down pipe reads as EOF (ValueError/OSError tolerated).
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


def _finish_readers(proc: subprocess.Popen,
                    readers: List[threading.Thread]) -> None:
    """INTERNAL. Bounded drain of reader threads, then close pipe fds.

    Readers normally finish on child EOF. If a thread is still blocked
    (e.g. a grandchild inherited the pipe), closing the fds unblocks it:
    the pump treats the resulting ValueError as EOF. Threads are daemon,
    so nothing here can hang interpreter shutdown.
    """
    for thread in readers:
        thread.join(timeout=KILL_GRACE_SECONDS)
    for pipe in (proc.stdout, proc.stderr):
        try:
            if pipe is not None:
                pipe.close()
        except (OSError, ValueError):
            pass
    for thread in readers:
        thread.join(timeout=KILL_GRACE_SECONDS)


def _kill_quietly(proc: subprocess.Popen) -> None:
    """INTERNAL. SIGKILL that tolerates an already-exited child."""
    try:
        proc.kill()
    except OSError:
        pass


def run_command(argv: Sequence[str], *, timeout_seconds: float,
                workdir: Optional[str] = None) -> CompletedRun:
    """Run argv (no shell) with timeout; kill-after-grace; bounded capture.

    Timeout -> EngineTimeoutError (after terminating + reaping the child).
    Either stream exceeding 10 MiB -> InternalError, raised promptly while
    the child is still producing output (the child is killed first).
    Spawn failures (missing/unexecutable) -> InternalError here; adapters
    pre-check paths and raise EngineUnavailableError with better context.
    """
    if timeout_seconds is None or not timeout_seconds > 0:
        raise InternalError("run_command requires timeout_seconds > 0.")
    start = time.monotonic()
    try:
        proc = subprocess.Popen(
            list(argv), stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=workdir, shell=False)
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
        deadline = start + timeout_seconds
        timed_out = False
        while True:
            if over_event.is_set():
                _kill_quietly(proc)  # no-op if the child already exited
                break
            if proc.poll() is not None:
                break
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                _kill_quietly(proc)
                break
            over_event.wait(timeout=min(_POLL_INTERVAL_SECONDS, remaining))
        if timed_out:
            _finish_readers(proc, readers)
            elapsed = time.monotonic() - start
            raise EngineTimeoutError(
                f"engine exceeded {timeout_seconds}s wall-clock budget "
                f"(killed after {elapsed:.1f}s).") from None
        if over_event.is_set():
            _finish_readers(proc, readers)
            raise InternalError(
                "engine output exceeded 10 MiB capture cap.")
        # Normal exit: bounded drain of already-buffered pipe data.
        _finish_readers(proc, readers)
        out = bytes(out_buf)
        err = bytes(err_buf)
    finally:
        # Absolute cleanup on every path: no zombies, no leaked fds.
        try:
            if proc.poll() is None:
                proc.kill()
        except OSError:
            pass
        try:
            proc.wait(timeout=KILL_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
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
        raise InternalError(
            f"engine output is not UTF-8: {exc}") from exc
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
