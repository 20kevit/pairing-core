"""BBP external reference adapter (W3 foundation).

Bring-your-own-binary; never bundled, never auto-discovered (O04/O06).
No BBP structures leak into core: conversion happens here, at the adapter
boundary, via the TRF subset (adapters/trf.py). No EngineProvider is shipped
yet — provider integration waits until request histories can carry
per-round data (later phase); this module is the execution + conversion
layer the harness and a future provider will share.

Authoritative behavior source: BBP README (primary, retrieved in full —
CLI ``--dutch/--burstein -p/-c/-g/-r/-s``, TRF-2026 + TRF(bx), exit codes
0-5, checklist + RTG, Apache-2.0). Only the Dutch pairing path is wrapped;
Burstein is self-declared flawed upstream and NOT wrapped (refusing, not
misrepresenting).

Exit-code mapping (per BBP manual):
  0 ok | 1 no valid pairing -> ImpossiblePairingError
  2 unexpected -> InternalError | 3 invalid request -> InvalidRequestError
  4 unhandleable size -> InternalError (resource exhaustion, captured)
  5 file access -> EngineUnavailableError | other -> InternalError.
Timeout (ours, wall-clock) -> EngineTimeoutError with termination.
Missing/unexecutable binary or failed version probe -> EngineUnavailableError.
Malformed pairing output -> InternalError with captured excerpt.

Live-binary verification is PENDING (no binary in this environment); the
execution path is tested against fixture stub executables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from pairing_core.adapters._process import (
    CompletedRun,
    check_executable,
    run_command,
    temp_workdir,
)
from pairing_core.adapters.trf import (
    TournamentInput,
    build_trf,
    parse_pairing_output,
)
from pairing_core.errors import (
    EngineTimeoutError,
    EngineUnavailableError,
    ImpossiblePairingError,
    InternalError,
    InvalidRequestError,
)

BBP_SYSTEM_DUTCH = "--dutch"
EXIT_DESCRIPTIONS = {
    1: "no valid pairing exists for the current round",
    2: "unexpected engine error",
    3: "invalid request (e.g. malformed input file)",
    4: "unhandleable data size / out of memory",
    5: "file access error",
}


@dataclass(frozen=True)
class BBPConfig:
    """PUBLIC. Explicit BYO-binary configuration (no discovery)."""
    executable: str
    timeout_seconds: float = 60.0
    system: str = BBP_SYSTEM_DUTCH

    def __post_init__(self) -> None:
        if self.system != BBP_SYSTEM_DUTCH:
            raise InvalidRequestError(
                "only --dutch is wrapped (Burstein upstream is "
                "self-declared flawed; refusing to wrap it).")
        if not isinstance(self.timeout_seconds, (int, float)) or \
                isinstance(self.timeout_seconds, bool) or \
                not self.timeout_seconds > 0:
            raise InvalidRequestError("timeout_seconds must be a number > 0.")


@dataclass(frozen=True)
class BBPPairing:
    """PUBLIC. Captured outcome of one BBP Dutch pairing run."""
    pairs: Tuple[Tuple[int, Optional[int]], ...]
    engine_version: str
    elapsed_seconds: float
    command: Tuple[str, ...] = ()
    stdout: str = ""
    stderr: str = ""


def probe_version(executable: str,
                  timeout_seconds: float = 30.0) -> str:
    """Run `<exe> -r`; return the release/build line.

    Failure (any) -> EngineUnavailableError: version identity is required
    for reproducibility metadata, never guessed.
    """
    exe = check_executable(executable, "BBP executable")
    try:
        run = run_command([exe, "-r"], timeout_seconds=timeout_seconds)
    except (InternalError, EngineTimeoutError) as exc:
        raise EngineUnavailableError(
            f"BBP version probe failed for {exe!r}: {exc}") from exc
    first = run.stdout.strip().splitlines()
    if run.returncode != 0 or not first:
        raise EngineUnavailableError(
            f"BBP version probe failed for {exe!r}: exit "
            f"{run.returncode}, stderr={run.stderr[:500]!r}.")
    return first[0].strip()


def pair_tournament(config: BBPConfig,
                    tournament: TournamentInput) -> BBPPairing:
    """Run BBP Dutch pairing over a TRF input; return captured pairs.

    Raises per the exit-code mapping above. stdout/stderr/command/version
    are captured for harness diagnostics and reproducibility.
    """
    exe = check_executable(config.executable, "BBP executable")
    version = probe_version(exe)
    text = build_trf(tournament)
    with temp_workdir() as workdir:
        src = os.path.join(workdir, "input.trf")
        out = os.path.join(workdir, "output.txt")
        try:
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as exc:
            raise InternalError(
                f"cannot write BBP input file: {exc}") from exc
        argv = [exe, config.system, src, "-p", out]
        try:
            run = run_command(argv, timeout_seconds=config.timeout_seconds,
                              workdir=workdir)
        except EngineTimeoutError:
            raise
        _check_exit(run, exe)
        pairs = _read_output(out, exe)
    return BBPPairing(pairs=tuple(pairs), engine_version=version,
                      elapsed_seconds=run.elapsed_seconds,
                      command=tuple(argv), stdout=run.stdout,
                      stderr=run.stderr)


def _check_exit(run: CompletedRun, exe: str) -> None:
    code = run.returncode
    if code == 0:
        return
    detail = EXIT_DESCRIPTIONS.get(code, f"unknown exit code {code}")
    context = f"BBP {exe!r} exit {code} ({detail}); stderr={run.stderr[:500]!r}."
    if code == 1:
        raise ImpossiblePairingError(context)
    if code == 3:
        raise InvalidRequestError(context)
    if code == 5:
        raise EngineUnavailableError(context)
    raise InternalError(context)


def _read_output(path: str, exe: str) -> List[Tuple[int, Optional[int]]]:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise InternalError(
            f"BBP {exe!r} produced no readable output file: {exc}") from exc
    try:
        return parse_pairing_output(text)
    except InternalError as exc:
        raise InternalError(f"BBP {exe!r} malformed pairing output: "
                            f"{exc}") from exc
