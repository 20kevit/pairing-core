"""Canonical consumer contract (master wave, Phase B).

PUBLIC. This module is the stable, implementation-independent consumer
contract of pairing-core. Design rules (mission §2, O01/O03):

- The consumer describes WHAT pairing is requested (system, ruleset, round,
  players, constraints, budgets), never HOW an engine searches. Nothing here
  imports or names ``SwissEngine``, ``NativeDutchEngine``, ``EnginePlayer``,
  brackets, search structures, or any adapter internals — not even lazily.
  (Enforced by ``tests/test_canonical.py::test_canonical_module_isolation``.)
- ``CanonicalPlayer`` is a plain frozen value object owned by this contract.
  ``PlayerData`` (v0.1.0 domain record) is NOT imported here; converters take
  and produce duck-typed records so neither direction creates a hard
  dependency on the legacy domain module.
- ``CanonicalRequest`` carries an explicit ``system`` (pairing system id),
  an explicit ``ruleset`` (``RulesetId`` or alias string — never defaulted),
  a ``schema`` version, optional provider hint, and a ``deterministic`` flag.
  Only ``deterministic=True`` is supported today; ``False`` raises
  ``UnsupportedCapabilityError`` (never silently accepted).
- ``pair_canonical()`` is the single service entry point: validated request
  in, complete ``RoundPairing`` success value out (O02). Failures use the
  typed taxonomy. Supported systems today: ``"dutch"`` only — anything else
  raises ``UnsupportedCapabilityError`` with an exact reason. Berger
  round-robin remains the standalone ``round_robin()`` schedule function
  (a fixed table, not a searched pairing — deliberately not unified).
- Serialization is canonical: ``to_dict``/``from_dict`` with schema
  versions, ``canonical_json()`` (sorted keys, compact, ASCII). Unknown
  schema -> ``VersionMismatchError``; malformed content ->
  ``InvalidRequestError``.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

CANONICAL_REQUEST_SCHEMA = 1

#: Pairing systems named by the canonical contract. Only "dutch" is
#: implemented; the rest are reserved names so callers fail explicitly
#: instead of drifting into an unintended system.
SYSTEM_DUTCH = "dutch"
SYSTEM_ROUND_ROBIN = "berger-rr"  # served by round_robin(), not pair_canonical
KNOWN_SYSTEMS = (SYSTEM_DUTCH, SYSTEM_ROUND_ROBIN)


@dataclass(frozen=True)
class CanonicalPlayer:
    """PUBLIC. One entrant's pairing-relevant state for one round.

    Implementation-independent value object: no engine, bracket, or search
    concepts. ``opponents`` is a sorted tuple (hash-seed independent).
    """

    id: int
    pairing_no: int
    rating: int
    points: float
    color_hist: str = ""
    opponents: Tuple[int, ...] = ()
    received_bye: bool = False
    float_hist: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "opponents",
                           tuple(sorted(self.opponents)))

    def to_dict(self) -> Dict[str, Any]:
        """PUBLIC. Stable dict form."""
        return {"id": self.id, "pairing_no": self.pairing_no,
                "rating": self.rating, "points": self.points,
                "color_hist": self.color_hist,
                "opponents": list(self.opponents),
                "received_bye": self.received_bye,
                "float_hist": self.float_hist}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CanonicalPlayer":
        """PUBLIC. Rebuild; malformed -> InvalidRequestError."""
        from pairing_core.errors import InvalidRequestError

        try:
            return CanonicalPlayer(
                id=data["id"], pairing_no=data["pairing_no"],
                rating=data["rating"], points=data["points"],
                color_hist=data.get("color_hist", ""),
                opponents=tuple(data.get("opponents", [])),
                received_bye=bool(data.get("received_bye", False)),
                float_hist=data.get("float_hist", ""))
        except (KeyError, TypeError, AttributeError) as exc:
            raise InvalidRequestError(
                f"malformed CanonicalPlayer dict: {exc}") from exc

    @staticmethod
    def from_legacy(record: object) -> "CanonicalPlayer":
        """PUBLIC. Adapt a v0.1.0 ``PlayerData`` (or compatible record).

        Duck-typed: only attribute reads, no import of the legacy module.
        """
        opponents = getattr(record, "opponents", ())
        return CanonicalPlayer(
            id=getattr(record, "id"),
            pairing_no=getattr(record, "pairing_no"),
            rating=getattr(record, "rating"),
            points=getattr(record, "points"),
            color_hist=getattr(record, "color_hist", "") or "",
            opponents=tuple(sorted(set(opponents))),
            received_bye=bool(getattr(record, "received_bye", False)),
            float_hist=getattr(record, "float_hist", "") or "")

    def to_legacy(self) -> object:
        """PUBLIC. Convert to a v0.1.0 ``PlayerData`` (duck-typed target).

        The legacy constructor is resolved lazily so this module never
        depends on the legacy domain at import time.
        """
        from pairing_core.models import PlayerData

        return PlayerData(
            id=self.id, pairing_no=self.pairing_no, rating=self.rating,
            points=self.points, color_hist=self.color_hist,
            opponents=frozenset(self.opponents),
            received_bye=self.received_bye, float_hist=self.float_hist)


@dataclass(frozen=True)
class CanonicalRequest:
    """PUBLIC. Stable single-round pairing request (schema v1).

    ``ruleset`` is MANDATORY (``RulesetId`` or alias string; never
    defaulted). ``constraints`` defaults to empty. ``budgets``/provider
    selection are explicit. ``deterministic`` must be True (a
    non-deterministic mode does not exist; asking for one fails loudly).
    """

    players: Tuple[CanonicalPlayer, ...] = ()
    ruleset: object = None
    round_number: int = 1
    system: str = SYSTEM_DUTCH
    constraints: object = None
    budgets: Optional[object] = None
    provider_id: Optional[str] = None
    deterministic: bool = True
    schema: int = CANONICAL_REQUEST_SCHEMA

    def __post_init__(self) -> None:
        object.__setattr__(self, "players", tuple(self.players))

    def to_dict(self) -> Dict[str, Any]:
        """PUBLIC. Stable dict form (budgets serialized by value)."""
        from pairing_core.rulesets import ConstraintSet as _CS
        from pairing_core.rulesets import RulesetId as _RS

        constraints = self.constraints
        if constraints is None:
            constraints = _CS()
        budgets = None
        if self.budgets is not None:
            budgets = {"max_steps": self.budgets.max_steps,
                       "wall_clock_seconds":
                           self.budgets.wall_clock_seconds}
        ruleset = self.ruleset
        ruleset_dict = (ruleset.to_dict() if isinstance(ruleset, _RS)
                        else {"alias": ruleset})
        return {"schema": self.schema, "system": self.system,
                "players": [p.to_dict() for p in self.players],
                "ruleset": ruleset_dict,
                "round_number": self.round_number,
                "constraints": constraints.to_dict(),
                "budgets": budgets,
                "provider_id": self.provider_id,
                "deterministic": self.deterministic}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "CanonicalRequest":
        """PUBLIC. Rebuild; unknown schema -> VersionMismatchError,
        malformed -> InvalidRequestError."""
        from pairing_core.errors import InvalidRequestError
        from pairing_core.errors import VersionMismatchError

        try:
            schema = data.get("schema", CANONICAL_REQUEST_SCHEMA)
            if schema != CANONICAL_REQUEST_SCHEMA:
                raise VersionMismatchError(
                    f"unsupported CanonicalRequest schema: {schema!r} "
                    f"(expected {CANONICAL_REQUEST_SCHEMA}).")
            rs = data["ruleset"]
            ruleset = _ruleset_from_dict(rs)
            budgets = data.get("budgets")
            return CanonicalRequest(
                players=tuple(CanonicalPlayer.from_dict(p)
                              for p in data["players"]),
                ruleset=ruleset,
                round_number=data.get("round_number", 1),
                system=data.get("system", SYSTEM_DUTCH),
                constraints=_constraints_from_dict(
                    data.get("constraints", {})),
                budgets=(None if budgets is None
                         else _budgets_from_dict(budgets)),
                provider_id=data.get("provider_id"),
                deterministic=data.get("deterministic", True))
        except (KeyError, TypeError, AttributeError) as exc:
            raise InvalidRequestError(
                f"malformed CanonicalRequest dict: {exc}") from exc

    def to_engine_request(self) -> object:
        """PUBLIC. Lower to the validated ``EngineRequest`` path.

        The canonical layer owns validation of its own fields; full
        domain validation still happens at the ``EngineRequest`` boundary.
        """
        from pairing_core.api import EngineRequest

        _validate_canonical(self)
        constraints = self.constraints
        if constraints is None:
            from pairing_core.rulesets import ConstraintSet as _CS

            constraints = _CS()
        return EngineRequest(
            players=[p.to_legacy() for p in self.players],
            ruleset=self.ruleset,
            round_number=self.round_number,
            constraints=constraints,
            budgets=self.budgets,
            cancel_token=None)


def _ruleset_from_dict(rs: object) -> object:
    from pairing_core.rulesets import RulesetId as _RS

    if isinstance(rs, dict) and "alias" in rs:
        return rs["alias"]
    return _RS.from_dict(rs)


def _constraints_from_dict(data: object) -> object:
    from pairing_core.rulesets import ConstraintSet as _CS

    return _CS.from_dict(data)


def _budgets_from_dict(data: object) -> object:
    from pairing_core.controls import ExecutionBudgets

    return ExecutionBudgets(
        max_steps=data.get("max_steps"),
        wall_clock_seconds=data.get("wall_clock_seconds"))


def _validate_canonical(request: object) -> None:
    """Shared structural checks for the canonical layer."""
    from pairing_core.errors import (
        InvalidRequestError,
        UnsupportedCapabilityError,
    )

    if not isinstance(request, CanonicalRequest):
        raise InvalidRequestError(
            f"CanonicalRequest required, got {type(request).__name__}.")
    if request.schema != CANONICAL_REQUEST_SCHEMA:
        from pairing_core.errors import VersionMismatchError

        raise VersionMismatchError(
            f"unsupported CanonicalRequest schema: {request.schema!r}.")
    if request.system not in KNOWN_SYSTEMS:
        raise UnsupportedCapabilityError(
            f"unknown pairing system {request.system!r}. "
            f"Known: {', '.join(KNOWN_SYSTEMS)}.")
    if request.system != SYSTEM_DUTCH:
        raise UnsupportedCapabilityError(
            f"pairing system {request.system!r} is not served by "
            f"pair_canonical (berger-rr uses round_robin()).")
    if not request.deterministic:
        raise UnsupportedCapabilityError(
            "non-deterministic mode is not offered; deterministic=True "
            "is the only supported configuration.")
    if request.ruleset is None:
        raise InvalidRequestError(
            "ruleset is mandatory (no silent default drift).")
    if not isinstance(request.round_number, int) or \
            isinstance(request.round_number, bool) or \
            request.round_number < 1:
        raise InvalidRequestError(
            f"round_number must be int >= 1, got "
            f"{request.round_number!r}.")
    if request.provider_id is not None and \
            not isinstance(request.provider_id, str):
        raise InvalidRequestError("provider_id must be str or None.")


def pair_canonical(request: CanonicalRequest,
                   registry: object = None) -> object:
    """PUBLIC. Pair one round via the canonical contract.

    Validated request in, complete ``RoundPairing`` success value out
    (O02 — partials unrepresentable). ``provider_id=None`` selects the
    default native provider explicitly (no fallback: resolution failures
    raise typed errors). Failures use the typed taxonomy.
    """
    from pairing_core.api import pair_detailed, pair_via

    _validate_canonical(request)
    engine_request = request.to_engine_request()
    if request.provider_id is None:
        return pair_detailed(engine_request)
    return pair_via(request.provider_id, engine_request, registry)


def canonical_json(data: Dict[str, Any]) -> bytes:
    """PUBLIC. Deterministic bytes for canonical dicts."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def describe_systems() -> List[Dict[str, str]]:
    """PUBLIC. Pairing systems named by this contract + serving path."""
    return [
        {"system": SYSTEM_DUTCH, "status": "implemented",
         "served_by": "pair_canonical/native-dutch",
         "ruleset": "dutch-till2026-compat"},
        {"system": SYSTEM_ROUND_ROBIN, "status": "implemented",
         "served_by": "round_robin()",
         "ruleset": "berger (FIDE C.05 Annex 1 construction)"},
    ]
