"""Execution controls: deterministic budgets + cooperative cancellation (F5).

PUBLIC. Rules (O10, blueprint F5):

- Step budget is PRIMARY and deterministic: the same (input, max_steps)
  always fails or succeeds identically, across runs, seeds, and machines.
  ``max_steps=None`` preserves the legacy 2,000,000-node cap.
- Wall-clock budget is SECONDARY: polled at bracket boundaries and every
  1024 search nodes — never inside tight matching inner loops — so it can
  only turn an over-budget run into a typed timeout, never change a
  within-budget result. Expiry is environment-dependent and therefore NOT
  replayable to success (see REPRODUCIBILITY.md timeout semantics).
- Cancellation is cooperative: the token is checked at the same checkpoints;
  a cancelled run raises CancelledError, never a partial result (O02).
- Both controls live OUTSIDE the pairing algorithm: the kernel receives
  plain values (ints, timestamps, token) and knows nothing about threads,
  registries, or providers.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class ExecutionBudgets:
    """PUBLIC. Bounds for one pairing run. All-None == legacy behavior."""
    max_steps: Optional[int] = None  # None -> legacy 2,000,000-node cap
    wall_clock_seconds: Optional[float] = None  # None -> no clock checks

    def __post_init__(self) -> None:
        from pairing_core.errors import InvalidRequestError

        if self.max_steps is not None and (
                not isinstance(self.max_steps, int)
                or isinstance(self.max_steps, bool)
                or self.max_steps < 1):
            raise InvalidRequestError(
                f"max_steps must be int >= 1 or None, "
                f"got {self.max_steps!r}.")
        if self.wall_clock_seconds is not None and (
                not isinstance(self.wall_clock_seconds, (int, float))
                or isinstance(self.wall_clock_seconds, bool)
                or not self.wall_clock_seconds > 0):
            raise InvalidRequestError(
                "wall_clock_seconds must be a number > 0 or None, "
                f"got {self.wall_clock_seconds!r}.")


class CancelToken:
    """PUBLIC. Cooperative cancellation token (thread-safe).

    Any thread may call cancel(); the kernel polls cancelled() at
    deterministic checkpoints. Not a result, not serializable, never part
    of the reproducibility envelope (a cancelled run has no success replay).
    """

    def __init__(self) -> None:
        self._event = threading.Event()

    def cancel(self) -> None:
        """Request cancellation (idempotent)."""
        self._event.set()

    @property
    def cancelled(self) -> bool:
        """True once cancel() has been called."""
        return self._event.is_set()


def deadline_from(seconds: Optional[float],
                  start: float) -> Optional[float]:
    """INTERNAL. Monotonic deadline timestamp, or None when unbounded."""
    if seconds is None:
        return None
    return start + seconds


def now_monotonic() -> float:
    """INTERNAL. Clock source (single seam for tests)."""
    return time.monotonic()
