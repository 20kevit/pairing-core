"""Stable engine abstraction for pairing-core.

Canonical contract owned by pairing-core. External engines
(JavaFo, BBP) will later be adapters to this interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from pairing_core.models import PlayerData, RoundResult


@dataclass(frozen=True)
class PairingRequest:
    """Plain input for one round of pairing.

    Independent of Flask/SQLAlchemy/ORM/HTTP. The caller
    (e.g. chess-manager round lifecycle) builds this from
    tournament persistence and passes it to the engine.
    """

    players: List[PlayerData] = field(default_factory=list)
    round_number: int = 1
    locked_pairs: List[Tuple[int, int]] = field(default_factory=list)


class PairingEngine(ABC):
    """Stable pairing interface: pair(request) -> result."""

    @abstractmethod
    def pair(self, request: PairingRequest) -> RoundResult:
        raise NotImplementedError

    @property
    def name(self) -> str:
        return self.__class__.__name__


class NativeDutchEngine(PairingEngine):
    """Current chess-manager Dutch algorithm, preserved verbatim.

    Wraps SwissEngine so behavior (inputs -> outputs) is identical.
    """

    def pair(self, request: PairingRequest) -> RoundResult:
        from pairing_core.engine import SwissEngine

        engine = SwissEngine(
            players=list(request.players),
            round_number=request.round_number,
            locked_pairs=list(request.locked_pairs or []),
        )
        return engine.generate()
