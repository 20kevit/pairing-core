"""JaVaFo external reference adapter (W5 foundation).

Bring-your-own JVM + jar; never bundled, never auto-discovered (O04/O06:
custom free-of-charge + attribution terms — mentioning rrweb.org/javafo is
required when used, notably in commercial products; no redistribution
assumed). No JaVaFo structures leak into core: TRF conversion happens here.

Authoritative behavior source: JaVaFo Advanced User Manual, Rel. 2.2
(primary, retrieved in full): CLI ``java -jar javafo.jar TRF -p OUT``
(``-c`` checker, ``-l`` checklist, ``-g`` RTG, ``-b`` Baku, ``-r`` release),
TRF(x) input (XXR mandatory; XXZ/XXC/XXA/XXP/XXS extensions), output =
pair count then ``<white> <black>`` lines with bye as ``<id> 0``.

Differences from BBP handling (documented, by design):
- JaVaFo documents NO exit-code taxonomy: any failure surfaces as missing
  output and/or hard-to-interpret stdout/stderr (AUM). All mid-run failures
  therefore map to InternalError with capture (never a pretended
  ImpossiblePairingError — we cannot distinguish it honestly).
- Missing/unrunnable JVM or jar, or a failed version probe, maps to
  EngineUnavailableError (BYO prerequisite missing).
- Initial colour defaults to JaVaFo's hash-seeded choice (reproducible per
  input per AUM); no XXC line is emitted by this adapter (documented).

Live-binary verification is PENDING (no JVM/binary here); the execution path
is tested against fixture stub executables.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
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
    validate_external_pairs,
)
from pairing_core.errors import (
    EngineTimeoutError,
    EngineUnavailableError,
    InternalError,
    InvalidRequestError,
)


@dataclass(frozen=True)
class JaVaFoConfig:
    """PUBLIC. Explicit BYO JVM + jar configuration (no discovery)."""
    java_executable: str
    jar_path: str
    timeout_seconds: float = 60.0

    def __post_init__(self) -> None:
        if not isinstance(self.timeout_seconds, (int, float)) or \
                isinstance(self.timeout_seconds, bool) or \
                not self.timeout_seconds > 0:
            raise InvalidRequestError("timeout_seconds must be a number > 0.")


@dataclass(frozen=True)
class JaVaFoPairing:
    """PUBLIC. Captured outcome of one JaVaFo Dutch pairing run."""
    pairs: Tuple[Tuple[int, Optional[int]], ...]
    engine_version: str
    elapsed_seconds: float
    command: Tuple[str, ...] = ()
    stdout: str = ""
    stderr: str = ""


def probe_version(config: JaVaFoConfig) -> str:
    """Run the bare jar (prints ``JaVaFo ... Rel. X (Build Y)`` per AUM).

    Failure (any) -> EngineUnavailableError: version identity is required
    for reproducibility metadata, never guessed.
    """
    java = check_executable(config.java_executable, "Java executable")
    if not isinstance(config.jar_path, str) or \
            not os.path.isfile(config.jar_path):
        raise EngineUnavailableError(
            f"JaVaFo jar not found: {config.jar_path!r} (BYO binary).")
    try:
        run = run_command([java, "-jar", config.jar_path],
                          timeout_seconds=min(config.timeout_seconds, 30.0))
    except (InternalError, EngineTimeoutError) as exc:
        raise EngineUnavailableError(
            f"JaVaFo version probe failed: {exc}") from exc
    for line in run.stdout.splitlines():
        if "JaVaFo" in line:
            return line.strip()
    raise EngineUnavailableError(
        f"JaVaFo version probe unrecognized output: "
        f"stdout={run.stdout[:300]!r} stderr={run.stderr[:300]!r}.")


def pair_tournament(config: JaVaFoConfig,
                    tournament: TournamentInput) -> JaVaFoPairing:
    """Run JaVaFo Dutch pairing over a TRF input; return captured pairs.

    Mid-run failures -> InternalError with capture (no exit taxonomy
    exists upstream to map). Timeout -> EngineTimeoutError.
    """
    java = check_executable(config.java_executable, "Java executable")
    if not os.path.isfile(config.jar_path):
        raise EngineUnavailableError(
            f"JaVaFo jar not found: {config.jar_path!r} (BYO binary).")
    version = probe_version(config)
    text = build_trf(tournament)
    with temp_workdir() as workdir:
        src = os.path.join(workdir, "input.trf")
        out = os.path.join(workdir, "output.txt")
        try:
            with open(src, "w", encoding="utf-8") as fh:
                fh.write(text)
        except OSError as exc:
            raise InternalError(
                f"cannot write JaVaFo input file: {exc}") from exc
        argv = [java, "-jar", config.jar_path, src, "-p", out]
        try:
            run = run_command(argv, timeout_seconds=config.timeout_seconds,
                              workdir=workdir)
        except EngineTimeoutError:
            raise
        if run.returncode != 0:
            raise InternalError(
                f"JaVaFo exit {run.returncode}; "
                f"stderr={run.stderr[:500]!r}.")
        pairs = _read_output(out)
        validate_external_pairs(
            pairs,
            tuple(p.pairing_id for p in tournament.players),
            absent_ids=tuple(tournament.absent_ids),
            engine="JaVaFo")
    return JaVaFoPairing(pairs=tuple(pairs), engine_version=version,
                         elapsed_seconds=run.elapsed_seconds,
                         command=tuple(argv), stdout=run.stdout,
                         stderr=run.stderr)


def _read_output(path: str) -> List[Tuple[int, Optional[int]]]:
    try:
        with open(path, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as exc:
        raise InternalError(
            "JaVaFo produced no readable output file "
            f"(unpairable or engine error): {exc}") from exc
    try:
        return parse_pairing_output(text)
    except InternalError as exc:
        raise InternalError(f"JaVaFo malformed pairing output: "
                            f"{exc}") from exc
