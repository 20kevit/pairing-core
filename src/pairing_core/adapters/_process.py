"""Supervised subprocess execution for engine adapters (INTERNAL).

Not exported from pairing_core.adapters. Rules (SECURITY.md posture,
blueprint H, O10):

- argv lists only, never shell strings (no shell=True, no unsanitized
  interpolation). Timeouts kill after a grace period and reap (no zombies).
- Bounded stdout/stderr capture (10 MiB each; beyond -> InternalError, not
  memory exhaustion). Strict UTF-8 decode; undecodable bytes -> InternalError.
- Args, executable path, and working directory are caller-supplied and
  explicit (BYO binaries). No PATH searching, no downloading, no guessing.
- Returns CompletedRun; interpretation (exit-code mapping) belongs to the
  per-engine adapter, which has the authoritative manual.
"""

from __future__ import annotations

import os
import subprocess
import tempfile
import time
from dataclasses import dataclass
from typing import Optional, Sequence

from pairing_core.errors import EngineTimeoutError, InternalError

OUTPUT_CAP = 10 * 1024 * 1024
KILL_GRACE_SECONDS = 5.0


@dataclass(frozen=True)
class CompletedRun:
    """INTERNAL. Captured outcome of one supervised execution."""
    argv: tuple
    returncode: int
    stdout: str
    stderr: str
    elapsed_seconds: float
    timed_out: bool


def run_command(argv: Sequence[str], *, timeout_seconds: float,
                workdir: Optional[str] = None) -> CompletedRun:
    """Run argv (no shell) with timeout; kill-after-grace; bounded capture.

    Timeout -> EngineTimeoutError (after terminating + reaping the child).
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
    try:
        try:
            out, err = proc.communicate(timeout=timeout_seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            proc.kill()
            try:
                out, err = proc.communicate(timeout=KILL_GRACE_SECONDS)
            except subprocess.TimeoutExpired:
                proc.wait()
                out, err = b"", b""
            elapsed = time.monotonic() - start
            raise EngineTimeoutError(
                f"engine exceeded {timeout_seconds}s wall-clock budget "
                f"(killed after {elapsed:.1f}s).") from None
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait()
    elapsed = time.monotonic() - start
    if len(out) > OUTPUT_CAP or len(err) > OUTPUT_CAP:
        raise InternalError("engine output exceeded 10 MiB capture cap.")
    try:
        stdout = out.decode("utf-8")
        stderr = err.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InternalError(
            f"engine output is not UTF-8: {exc}") from exc
    return CompletedRun(argv=tuple(argv), returncode=proc.returncode,
                        stdout=stdout, stderr=stderr,
                        elapsed_seconds=elapsed, timed_out=timed_out)


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
