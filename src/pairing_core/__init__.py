"""
pairing-core — standalone FIDE Dutch Swiss pairing engine.

Extracted verbatim (behavior-preserving) from 20kevit/chess-manager
``domain/pairing/``. No Flask, no SQLAlchemy, no persistence.

Public contract:
    PlayerData, PairingCard, RoundResult,
    PairingRequest, PairingEngine, NativeDutchEngine,
    pair_round(...), validate_round(...), ValidationReport, Finding

Canonical engine abstraction:
    PairingEngine.pair(request) -> RoundResult

Future engines (JavaFo, BBP) will be adapters to this contract.
They are NOT implemented here.
"""

from pairing_core.models import PlayerData, PairingCard, RoundResult

try:
    from pairing_core.models import PlayerSnapshot
except ImportError:  # pragma: no cover
    PlayerSnapshot = PlayerData  # type: ignore

from pairing_core.engine import pair_round, SwissEngine
from pairing_core.validator import validate_round, ValidationReport, Finding
from pairing_core.api import PairingRequest, PairingEngine, NativeDutchEngine
from pairing_core.api import (
    EngineRequest,
    pair,
    pair_detailed,
    validate_request,
    versions,
)
from pairing_core.errors import (
    CancelledError,
    DuplicatePlayerIdError,
    EngineTimeoutError,
    EngineUnavailableError,
    ImpossiblePairingError,
    InternalError,
    InvalidPlayerError,
    InvalidRequestError,
    PairingError,
    UnsupportedCapabilityError,
    UnsupportedRulesetError,
    VersionMismatchError,
)
from pairing_core.rulesets import (
    DUTCH_TILL2026_COMPAT,
    ConstraintSet,
    RulesetId,
    resolve_ruleset,
)
from pairing_core.envelope import Pairing, RoundPairing

__version__ = "0.1.0"
__fide_reference__ = "C.04.2 + C.04.3 (effective 1 July 2025)"

__all__ = [
    "PlayerData",
    "PlayerSnapshot",
    "PairingCard",
    "RoundResult",
    "PairingRequest",
    "PairingEngine",
    "NativeDutchEngine",
    "SwissEngine",
    "pair_round",
    "validate_round",
    "ValidationReport",
    "Finding",
    "EngineRequest",
    "pair",
    "pair_detailed",
    "validate_request",
    "versions",
    "RulesetId",
    "ConstraintSet",
    "resolve_ruleset",
    "DUTCH_TILL2026_COMPAT",
    "Pairing",
    "RoundPairing",
    "PairingError",
    "InvalidRequestError",
    "InvalidPlayerError",
    "DuplicatePlayerIdError",
    "ImpossiblePairingError",
    "EngineTimeoutError",
    "CancelledError",
    "EngineUnavailableError",
    "UnsupportedCapabilityError",
    "UnsupportedRulesetError",
    "VersionMismatchError",
    "InternalError",
    "__version__",
    "__fide_reference__",
]
