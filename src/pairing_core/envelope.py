"""Pairing result envelope (F3 foundation).

PUBLIC value objects + deterministic serialization. Design rules (O02/O03,
blueprint D/RESULT_MODEL, F3 scope):

- RoundPairing is a SUCCESS value only: complete, valid, internally
  consistent. Construction enforces the O02 invariants; anything else raises
  InvalidRequestError (builder misuse) — partial/intermediate states are
  unrepresentable by construction.
- from_kernel() converts a v0.1.0 RoundResult and REJECTS validator-ERROR
  states with InternalError (a kernel that emits illegality broke its own
  contract; O02 forbids returning it as success).
- No F4/F5 fields: no seed, budgets, modes, fallback, criteria costs, TRF.
  Engine identity is two flat strings (engine_id/engine_version), NOT a
  provider EngineMetadata (F4). Ruleset is the F2 RulesetId.
- Deterministic serialization: to_dict/from_dict with schema version,
  canonical_json() (sorted keys, compact separators, ASCII) and sha256
  digests. Digest mismatch or unknown schema -> VersionMismatchError.
- Hash-seed independent: no set iteration anywhere in canonical paths
  (opponent lists sorted; pairings in board order).
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from pairing_core.errors import (
    InternalError,
    InvalidRequestError,
    VersionMismatchError,
)
from pairing_core.rulesets import RulesetId

SCHEMA_VERSION = 1
_FLOAT_TAGS = ("D", "U", "")


@dataclass(frozen=True)
class Pairing:
    """PUBLIC. One board: immutable, validated."""
    board: int
    white_id: int
    black_id: Optional[int] = None
    is_bye: bool = False
    white_float: str = ""
    black_float: str = ""

    def __post_init__(self) -> None:
        if not isinstance(self.board, int) or isinstance(self.board, bool) \
                or self.board < 1:
            raise InvalidRequestError(
                f"board must be int >= 1, got {self.board!r}.")
        for name in ("white_id", "black_id"):
            value = getattr(self, name)
            if name == "black_id" and value is None:
                continue
            if not isinstance(value, int) or isinstance(value, bool):
                raise InvalidRequestError(
                    f"{name} must be int, got {value!r}.")
        if self.black_id is not None and self.white_id == self.black_id:
            raise InvalidRequestError("self-pairing is not representable.")
        if not isinstance(self.is_bye, bool):
            raise InvalidRequestError("is_bye must be bool.")
        if (self.is_bye and self.black_id is not None) or \
                (not self.is_bye and self.black_id is None):
            raise InvalidRequestError(
                "bye ⟺ black_id None (v0.1.0 convention).")
        for name in ("white_float", "black_float"):
            if getattr(self, name) not in _FLOAT_TAGS:
                raise InvalidRequestError(
                    f"{name} must be one of {_FLOAT_TAGS}.")

    def to_dict(self) -> Dict[str, Any]:
        return {"board": self.board, "white": self.white_id,
                "black": self.black_id, "bye": self.is_bye,
                "white_float": self.white_float,
                "black_float": self.black_float}

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Pairing":
        try:
            return Pairing(board=data["board"], white_id=data["white"],
                           black_id=data.get("black"),
                           is_bye=bool(data.get("bye", False)),
                           white_float=data.get("white_float", ""),
                           black_float=data.get("black_float", ""))
        except (KeyError, TypeError) as exc:
            raise InvalidRequestError(
                f"malformed Pairing dict: {exc}") from exc


@dataclass(frozen=True)
class RoundPairing:
    """PUBLIC. Complete successful pairing for one round + envelope."""
    round_number: int
    pairings: Tuple[Pairing, ...] = ()
    bye_player_id: Optional[int] = None
    engine_id: str = ""
    engine_version: str = ""
    ruleset: RulesetId = field(
        default_factory=lambda: RulesetId(system="dutch",
                                          effective_date="2026-01-31"))
    library_version: str = ""
    input_digest: str = ""
    warnings: Tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not isinstance(self.round_number, int) or \
                isinstance(self.round_number, bool) or self.round_number < 1:
            raise InvalidRequestError("round_number must be int >= 1.")
        pairings = tuple(self.pairings)
        object.__setattr__(self, "pairings", pairings)
        if [p.board for p in pairings] != list(range(1, len(pairings) + 1)):
            raise InvalidRequestError("boards must be exactly 1..N in order.")
        seen = set()
        byes = 0
        for p in pairings:
            for pid in (p.white_id,) + \
                    ((p.black_id,) if p.black_id is not None else ()):
                if pid in seen:
                    raise InvalidRequestError(
                        f"player {pid} appears twice.")
                seen.add(pid)
            byes += 1 if p.is_bye else 0
        if byes > 1:
            raise InvalidRequestError("at most one bye in a success result.")
        bye_whites = [p.white_id for p in pairings if p.is_bye]
        if (self.bye_player_id is None) != (not bye_whites):
            raise InvalidRequestError(
                "bye_player_id must match the bye card.")
        if bye_whites and self.bye_player_id != bye_whites[0]:
            raise InvalidRequestError(
                "bye_player_id must match the bye card.")
        object.__setattr__(self, "warnings", tuple(self.warnings))
        for name in ("engine_id", "engine_version", "library_version",
                     "input_digest"):
            if not isinstance(getattr(self, name), str):
                raise InvalidRequestError(f"{name} must be str.")
        if not isinstance(self.ruleset, RulesetId):
            raise InvalidRequestError("ruleset must be a RulesetId.")
        for w in self.warnings:
            if not isinstance(w, str):
                raise InvalidRequestError("warnings must be strings.")

    def to_dict(self, *, with_digest: bool = True) -> Dict[str, Any]:
        body: Dict[str, Any] = {
            "schema": SCHEMA_VERSION,
            "round": self.round_number,
            "pairings": [p.to_dict() for p in self.pairings],
            "bye_player_id": self.bye_player_id,
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "ruleset": {"system": self.ruleset.system,
                        "effective_date": self.ruleset.effective_date,
                        "acceleration": self.ruleset.acceleration,
                        "pab_value": self.ruleset.pab_value},
            "library_version": self.library_version,
            "input_digest": self.input_digest,
            "warnings": list(self.warnings),
        }
        if with_digest:
            body["digest"] = digest_canonical(body)
        return body

    @staticmethod
    def from_dict(data: Dict[str, Any], *,
                  verify_digest: bool = True) -> "RoundPairing":
        if not isinstance(data, dict) or data.get("schema") != SCHEMA_VERSION:
            raise VersionMismatchError(
                f"unsupported RoundPairing schema: "
                f"{data.get('schema') if isinstance(data, dict) else type(data)} "
                f"(expected {SCHEMA_VERSION}).")
        if verify_digest and "digest" in data:
            body = {k: v for k, v in data.items() if k != "digest"}
            if digest_canonical(body) != data["digest"]:
                raise VersionMismatchError("RoundPairing digest mismatch: "
                                           "data corrupted or tampered.")
        try:
            rs = data["ruleset"]
            ruleset = RulesetId(system=rs["system"],
                                effective_date=rs["effective_date"],
                                acceleration=rs.get("acceleration"),
                                pab_value=rs.get("pab_value"))
            return RoundPairing(
                round_number=data["round"],
                pairings=tuple(Pairing.from_dict(p)
                               for p in data["pairings"]),
                bye_player_id=data.get("bye_player_id"),
                engine_id=data["engine_id"],
                engine_version=data["engine_version"],
                ruleset=ruleset,
                library_version=data["library_version"],
                input_digest=data["input_digest"],
                warnings=tuple(data.get("warnings", [])))
        except (KeyError, TypeError) as exc:
            raise InvalidRequestError(
                f"malformed RoundPairing dict: {exc}") from exc


def canonical_json(data: Dict[str, Any]) -> bytes:
    """Deterministic bytes for dicts (sorted keys, compact, ASCII)."""
    return json.dumps(data, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True).encode("utf-8")


def digest_canonical(data: Dict[str, Any]) -> str:
    """sha256 hex over canonical_json(data)."""
    return hashlib.sha256(canonical_json(data)).hexdigest()


def _player_norm(p: object) -> Dict[str, Any]:
    return {"id": p.id, "pairing_no": p.pairing_no, "rating": p.rating,
            "points": p.points, "color_hist": p.color_hist,
            "opponents": sorted(p.opponents),
            "received_bye": p.received_bye, "float_hist": p.float_hist}


def input_digest(players: object, round_number: int,
                 ruleset: RulesetId) -> str:
    """INTERNAL. Deterministic digest of normalized request input.

    Players sorted by id (input-list order independent); opponent lists
    sorted (hash-seed independent).
    """
    body = {"players": [_player_norm(p) for p in
                        sorted(players, key=lambda q: q.id)],
            "round": round_number,
            "ruleset": {"system": ruleset.system,
                        "effective_date": ruleset.effective_date,
                        "acceleration": ruleset.acceleration,
                        "pab_value": ruleset.pab_value}}
    return digest_canonical(body)


def from_kernel(result: object, *, engine_id: str, engine_version: str,
                ruleset: RulesetId, library_version: str,
                input_digest_hex: str, warnings: Tuple[str, ...],
                validator_errors: Tuple[str, ...]) -> RoundPairing:
    """INTERNAL. Convert a v0.1.0 RoundResult, enforcing O02.

    validator_errors: rule codes at ERROR level for this output (from
    validate_round). Non-empty means the kernel emitted illegality ->
    InternalError (never returned as success).
    """
    if validator_errors:
        raise InternalError(
            "kernel emitted an illegal pairing "
            f"({', '.join(validator_errors)}); refusing success result.")
    return RoundPairing(
        round_number=result.round_number,
        pairings=tuple(
            Pairing(board=c.board, white_id=c.white_id, black_id=c.black_id,
                    is_bye=c.is_bye, white_float=c.white_float,
                    black_float=c.black_float)
            for c in result.pairings),
        bye_player_id=result.bye_player_id,
        engine_id=engine_id, engine_version=engine_version,
        ruleset=ruleset, library_version=library_version,
        input_digest=input_digest_hex, warnings=tuple(warnings))
