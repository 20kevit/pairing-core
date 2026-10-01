"""Typed pairing error taxonomy (F2 foundation).

PUBLIC. Design notes (see blueprint D/E, O02/O03/O10):

- Every error subclasses ``PairingError``, which subclasses ``ValueError``.
  The ``ValueError`` base preserves backward-compatible ``isinstance`` checks
  against the v0.1.0 kernel, whose frozen raise sites still raise plain
  ``ValueError``. New code raises the typed subclasses; a translation layer
  (``translate_kernel_error``) maps kernel failures at the new API boundary.
- Original messages are preserved verbatim in ``str(exc)`` and the kernel
  exception is chained via ``__cause__`` — diagnostics are never discarded.
- Categories never flattened: invalid request, impossible pairing, timeout,
  cancellation, engine availability, capability/ruleset support, version
  mismatch, and internal failures are distinct types callers can branch on.
"""

from __future__ import annotations

from typing import Optional


class PairingError(ValueError):
    """Base of all pairing-core errors. Subclasses ValueError for v0.1.0
    isinstance-compatibility (O08)."""


class InvalidRequestError(PairingError):
    """The request itself is malformed (bad players, bad locks, bad fields).

    Raised by the validation boundary BEFORE any search runs. Never raised
    for a well-formed request that merely has no legal pairing (that is
    ImpossiblePairingError).
    """


class InvalidPlayerError(InvalidRequestError):
    """One player record is malformed. Carries the offending ``player_id``
    (or ``None`` when the record has no usable id)."""

    def __init__(self, message: str, player_id: Optional[int] = None):
        super().__init__(message)
        self.player_id = player_id


class DuplicatePlayerIdError(InvalidPlayerError):
    """Two records share one ``player_id``. Equality in this library is
    id-based, so duplicates would silently corrupt maps and swaps."""


class ImpossiblePairingError(PairingError):
    """Well-formed request, but no legal pairing exists under the ruleset.

    Carries ``ruleset`` and ``round_number`` where known. Partial results are
    never attached (O02)."""


class EngineTimeoutError(PairingError):
    """Execution exceeded its bound (step budget and/or wall-clock).

    Carries ``budget`` and ``elapsed`` where known. Step-budget exhaustion is
    deterministic; wall-clock expiry is environment-dependent (see
    REPRODUCIBILITY.md)."""


class CancelledError(PairingError):
    """Execution was cancelled via the cancellation token (F5 consumer).

    Defined in F2 so the taxonomy is complete; first raised by F5
    interruption points."""


class EngineUnavailableError(PairingError):
    """The selected engine cannot run (missing BYO binary, no JVM, crash at
    startup). First raised by F3+ adapters; defined here for taxonomy
    completeness."""


class UnsupportedCapabilityError(PairingError):
    """Well-formed request the selected engine/ruleset cannot honour
    (e.g. forbidden pairs or bye directives on the v0.1.0 kernel).

    Raised INSTEAD of silently ignoring the constraint (O03)."""


class UnsupportedRulesetError(PairingError):
    """The requested ruleset id is unknown or not implemented by the
    selected engine. Never falls back to another ruleset (O03)."""


class VersionMismatchError(PairingError):
    """Requested engine/ruleset/format version does not match what is
    available. Never substitutes another version (O03). First raised by
    F3+ selection paths; defined here for taxonomy completeness."""


class InternalError(PairingError):
    """The library failed in a way no other category describes (unknown
    kernel failure, invariant violation). Carries the chained cause;
    never silently swallowed."""


def translate_kernel_error(exc: ValueError, *,
                           ruleset: str = "",
                           round_number: int = 0) -> PairingError:
    """Map a v0.1.0 kernel ``ValueError`` to the typed taxonomy.

    Mapping (by stable message fragment; full original text preserved):
      - ``Locked pair #``        -> InvalidRequestError
      - ``No legal FIDE Dutch``  -> ImpossiblePairingError
      - ``Pairing complexity``    -> EngineTimeoutError (legacy 2M-step cap)
      - anything else            -> InternalError
    """
    text = str(exc)
    if text.startswith("Locked pair #"):
        mapped: PairingError = InvalidRequestError(text)
    elif "No legal FIDE Dutch" in text:
        mapped = ImpossiblePairingError(text)
        mapped.ruleset = ruleset  # type: ignore[attr-defined]
        mapped.round_number = round_number  # type: ignore[attr-defined]
    elif text.startswith("Pairing complexity"):
        mapped = EngineTimeoutError(text)
    else:
        mapped = InternalError(f"unexpected kernel failure: {text}")
    mapped.__cause__ = exc
    return mapped
