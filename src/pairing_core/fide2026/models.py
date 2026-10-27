"""2026 value model + ruleset identities (FIDE articles only).

P26Player carries everything the 2026 texts require:
- TPN (all systems), rating (Dubov-mandatory, Lim Maxi-guard, Olympiad seeding),
- score (primary), secondary (team game points / colour tiebreak input),
- colors: per-round 'W'/'B'/'u' (unplayed) history in round order,
- opponents: played opponent ids (unplayed pairings excluded per C.04.2 3.5),
- unplayed: count of unplayed games (Dutch C9; PAB preferences),
- last_float / prev_float: 'D'/'U'/'' for previous / two-ago rounds (C14-C21,
  Dubov C8-C10, Double/Team C7/C8/C10),
- got_pab / forfeit_win: C2 blockers; played: games/matches actually played
  (PAB "most games" tiebreaks).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

from pairing_core.controls import CancelToken
from pairing_core.envelope import digest_canonical
from pairing_core.errors import (
    InvalidPlayerError,
    InvalidRequestError,
    UnsupportedRulesetError,
    VersionMismatchError,
)

def _finite_number(value: object) -> bool:
    """Whether a non-boolean int/float has a finite float representation."""
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return False
    try:
        return math.isfinite(float(value))
    except (OverflowError, TypeError, ValueError):
        return False


DUTCH_2026 = "dutch-2026"
DUBOV_2026 = "dubov-2026"
BURSTEIN_2026 = "burstein-2026"
LIM_2026 = "lim-2026"
DOUBLE_2026 = "double-2026"
TEAM_2026 = "team-2026"
OLYMPIAD_2022 = "olympiad-2022"


@dataclass(frozen=True)
class P26RulesetId:
    """Dated 2026 ruleset identity: system + effective date (+ options)."""

    system: str
    effective_date: str
    acceleration: Optional[str] = None
    team_colour_type: Optional[str] = None  # team-2026: "A" (default), "B", "none"

    def __post_init__(self) -> None:
        if not isinstance(self.system, str) or not self.system.strip():
            raise InvalidRequestError("ruleset system must be non-empty text")
        if not isinstance(self.effective_date, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", self.effective_date):
            raise InvalidRequestError("ruleset effective_date must use YYYY-MM-DD")
        if self.acceleration is not None and not isinstance(self.acceleration, str):
            raise InvalidRequestError("ruleset acceleration must be text or None")
        if self.team_colour_type is not None and not isinstance(self.team_colour_type, str):
            raise InvalidRequestError("team_colour_type must be text or None")

    def to_dict(self) -> Dict[str, object]:
        return {"system": self.system, "effective_date": self.effective_date,
                "acceleration": self.acceleration,
                "team_colour_type": self.team_colour_type}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "P26RulesetId":
        if not isinstance(data, dict):
            raise InvalidRequestError("P26RulesetId data must be an object")
        allowed = {"system", "effective_date", "acceleration", "team_colour_type"}
        unknown = set(data) - allowed
        if unknown:
            raise InvalidRequestError(
                f"unknown P26RulesetId fields: {', '.join(sorted(unknown))}")
        try:
            return P26RulesetId(
                system=data["system"], effective_date=data["effective_date"],
                acceleration=data.get("acceleration"),
                team_colour_type=data.get("team_colour_type"))
        except KeyError as exc:
            raise InvalidRequestError(
                f"missing required P26RulesetId field: {exc.args[0]}") from exc


#: Exact-match table of implemented 2026 rulesets (separate from the frozen
#: v0.1.0 KNOWN_RULESETS — that table stays len==1 per regression pin).
SYSTEM_RULESETS: Dict[P26RulesetId, Dict[str, str]] = {
    P26RulesetId(system="dutch", effective_date="2026-02-01"): {
        "label": DUTCH_2026, "source": "F-0105", "engine": "fide2026.dutch",
        "note": "C.04.3 full C1-C21 search; evidence DUTCH_2026_EVIDENCE.md"},
    P26RulesetId(system="dubov", effective_date="2026-02-01"): {
        "label": DUBOV_2026, "source": "F-0108", "engine": "fide2026.dubov",
        "note": "C.04.4.1 ARO engine; evidence DUBOV_2026_EVIDENCE.md"},
    P26RulesetId(system="burstein", effective_date="2026-02-01"): {
        "label": BURSTEIN_2026, "source": "F-0110", "engine": "fide2026.burstein",
        "note": "C.04.4.2 Index engine; evidence BURSTEIN_2026_EVIDENCE.md"},
    P26RulesetId(system="lim", effective_date="2026-02-01"): {
        "label": LIM_2026, "source": "F-0112", "engine": "fide2026.lim",
        "note": "C.04.4.3 procedural engine; evidence LIM_2026_EVIDENCE.md"},
    P26RulesetId(system="double", effective_date="2026-02-01"): {
        "label": DOUBLE_2026, "source": "F-0114", "engine": "fide2026.double_team",
        "note": "C.04.5 match engine; evidence DOUBLE_SWISS_2026_EVIDENCE.md"},
    P26RulesetId(system="team", effective_date="2026-02-01"): {
        "label": TEAM_2026, "source": "F-0115", "engine": "fide2026.double_team",
        "note": "C.04.6 team engine; evidence TEAM_SWISS_2026_EVIDENCE.md"},
    P26RulesetId(system="olympiad", effective_date="2022-01-01"): {
        "label": OLYMPIAD_2022, "source": "F-0601", "engine": "fide2026.olympiad",
        "note": "Olympiad Pairing Rules; evidence OLYMPIAD_EVIDENCE.md"},
}

ALIASES_2026: Dict[str, P26RulesetId] = {
    DUTCH_2026: P26RulesetId(system="dutch", effective_date="2026-02-01"),
    DUBOV_2026: P26RulesetId(system="dubov", effective_date="2026-02-01"),
    BURSTEIN_2026: P26RulesetId(system="burstein", effective_date="2026-02-01"),
    LIM_2026: P26RulesetId(system="lim", effective_date="2026-02-01"),
    DOUBLE_2026: P26RulesetId(system="double", effective_date="2026-02-01"),
    TEAM_2026: P26RulesetId(system="team", effective_date="2026-02-01"),
    OLYMPIAD_2022: P26RulesetId(system="olympiad", effective_date="2022-01-01"),
}


def resolve_2026_ruleset(ruleset: object) -> P26RulesetId:
    """Exact-match resolver for 2026 rulesets (no fallback, typed errors).

    Team-2026 colour-type options (Art.1.7: "A" default, "B", "none") are
    facets of the same dated ruleset, not distinct rulesets: any of the
    three (or unset) resolves.
    """
    candidate = None
    if isinstance(ruleset, P26RulesetId):
        candidate = ruleset
    elif isinstance(ruleset, str) and ruleset in ALIASES_2026:
        return ALIASES_2026[ruleset]
    if candidate is not None:
        if candidate in SYSTEM_RULESETS:
            return candidate
        if (candidate.system, candidate.effective_date,
                candidate.acceleration) == ("team", "2026-02-01", None) \
                and candidate.team_colour_type in ("A", "B", "none"):
            return candidate
    known = sorted(ALIASES_2026)
    raise UnsupportedRulesetError(
        f"Unsupported 2026 ruleset {ruleset!r}. Known: {', '.join(known)}.")


@dataclass(frozen=True)
class P26Player:
    """One entrant's pairing-relevant state for one 2026 round."""

    id: int
    tpn: int
    score: float = 0.0
    rating: Optional[int] = None
    secondary: float = 0.0
    colors: str = ""
    opponents: Tuple[int, ...] = ()
    unplayed: int = 0
    last_float: str = ""
    prev_float: str = ""
    got_pab: bool = False
    forfeit_win: bool = False
    played: int = 0
    late_entry: bool = False  # joined after round-1 publication
    # (Olympiad Art.4.2.3 bye ineligibility; management-side fact)

    def __post_init__(self) -> None:
        if not isinstance(self.opponents, (tuple, list)):
            raise InvalidPlayerError("player.opponents must be an ordered sequence")
        opponents = tuple(self.opponents)
        for oid in opponents:
            if not isinstance(oid, int) or isinstance(oid, bool) or oid < 1:
                raise InvalidPlayerError("opponent ids must be positive integers")
        object.__setattr__(self, "opponents", tuple(sorted(opponents)))
        _validate_player(self)
        object.__setattr__(self, "score", float(self.score))
        object.__setattr__(self, "secondary", float(self.secondary))

    def to_dict(self) -> Dict[str, object]:
        return {"id": self.id, "tpn": self.tpn, "score": self.score,
                "rating": self.rating, "secondary": self.secondary,
                "colors": self.colors, "opponents": list(self.opponents),
                "unplayed": self.unplayed, "last_float": self.last_float,
                "prev_float": self.prev_float, "got_pab": self.got_pab,
                "forfeit_win": self.forfeit_win, "played": self.played,
                "late_entry": self.late_entry}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "P26Player":
        if not isinstance(data, dict):
            raise InvalidPlayerError("P26Player data must be an object")
        try:
            return P26Player(
                id=data["id"], tpn=data["tpn"],
                score=data.get("score", 0.0),
                rating=data.get("rating"),
                secondary=data.get("secondary", 0.0),
                colors=data.get("colors", ""),
                opponents=data.get("opponents", ()),
                unplayed=data.get("unplayed", 0),
                last_float=data.get("last_float", ""),
                prev_float=data.get("prev_float", ""),
                got_pab=data.get("got_pab", False),
                forfeit_win=data.get("forfeit_win", False),
                played=data.get("played", 0),
                late_entry=data.get("late_entry", False))
        except KeyError as exc:
            raise InvalidPlayerError(
                f"missing required P26Player field: {exc.args[0]}") from exc


def _validate_player(p: "P26Player") -> None:
    if not isinstance(p.id, int) or isinstance(p.id, bool) or p.id < 1:
        raise InvalidPlayerError("player id must be a positive integer")
    if not isinstance(p.tpn, int) or isinstance(p.tpn, bool) or p.tpn < 1:
        raise InvalidPlayerError("tpn must be a positive integer")
    if not _finite_number(p.score) or p.score < 0:
        raise InvalidPlayerError("score must be a finite non-negative number")
    if p.rating is not None and (
            not isinstance(p.rating, int) or isinstance(p.rating, bool)
            or p.rating < 0):
        raise InvalidPlayerError("rating must be a non-negative integer or None")
    if not _finite_number(p.secondary) or p.secondary < 0:
        raise InvalidPlayerError("secondary must be a finite non-negative number")
    if not isinstance(p.colors, str) or any(ch not in ("W", "B", "u") for ch in p.colors):
        raise InvalidPlayerError("colors must use W/B/u only")
    if not isinstance(p.last_float, str) or p.last_float not in ("", "D", "U"):
        raise InvalidPlayerError("last_float must be '', 'D', or 'U'")
    if not isinstance(p.prev_float, str) or p.prev_float not in ("", "D", "U"):
        raise InvalidPlayerError("prev_float must be '', 'D', or 'U'")
    for name in ("unplayed", "played"):
        value = getattr(p, name)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise InvalidPlayerError(f"{name} must be a non-negative integer")
    for name in ("got_pab", "forfeit_win", "late_entry"):
        if not isinstance(getattr(p, name), bool):
            raise InvalidPlayerError(f"{name} must be a boolean")
    if len(set(p.opponents)) != len(p.opponents):
        raise InvalidPlayerError("opponents must not contain duplicates")
    if p.id in p.opponents:
        raise InvalidPlayerError(f"player {p.id} lists self as opponent")


@dataclass(frozen=True)
class BursteinIndexProvenance:
    """Declared source for caller-supplied C.04 Burstein Index values.

    Pairing-Core records provenance but does not calculate or independently
    validate the Index. A caller must ensure supplied values have the intended
    C.04 semantics; a C.07 calculation is not assumed equivalent.
    """

    source: str
    producer: Optional[str] = None
    producer_version: Optional[str] = None
    producer_ruleset: Optional[str] = None
    scope: Optional[str] = None

    def __post_init__(self) -> None:
        if self.source not in ("caller-supplied", "library-calculated"):
            raise InvalidRequestError(
                "Burstein Index source must be 'caller-supplied' or 'library-calculated'")
        for name in ("producer", "producer_version", "producer_ruleset", "scope"):
            value = getattr(self, name)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise InvalidRequestError(f"Burstein provenance {name} must be non-empty text")
        producer_fields = (self.producer, self.producer_version, self.producer_ruleset)
        if self.source == "caller-supplied" and any(v is not None for v in producer_fields):
            raise InvalidRequestError(
                "caller-supplied provenance cannot claim a calculating producer")
        if self.source == "library-calculated" and any(v is None for v in producer_fields):
            raise InvalidRequestError(
                "library-calculated provenance requires producer, version, and ruleset")

    def to_dict(self) -> dict:
        return {"source": self.source, "producer": self.producer,
                "producer_version": self.producer_version,
                "producer_ruleset": self.producer_ruleset, "scope": self.scope}

    @classmethod
    def from_dict(cls, data: dict) -> "BursteinIndexProvenance":
        if not isinstance(data, dict):
            raise InvalidRequestError("Burstein Index provenance must be an object")
        allowed = {"source", "producer", "producer_version", "producer_ruleset", "scope"}
        unknown = set(data) - allowed
        if unknown:
            raise InvalidRequestError(
                f"unknown Burstein provenance fields: {', '.join(sorted(unknown))}")
        try:
            return cls(**data)
        except TypeError as exc:
            raise InvalidRequestError(f"invalid Burstein Index provenance: {exc}") from exc


@dataclass(frozen=True)
class BursteinIndexValue:
    """One caller-provided Burstein value pair, keyed by entrant ID."""

    player_id: int
    buchholz: float
    sonneborn_berger: float

    def __post_init__(self) -> None:
        if (not isinstance(self.player_id, int) or isinstance(self.player_id, bool)
                or self.player_id < 1):
            raise InvalidRequestError("Burstein Index player_id must be a positive integer")
        for name in ("buchholz", "sonneborn_berger"):
            value = getattr(self, name)
            if not _finite_number(value) or value < 0:
                raise InvalidRequestError(
                    f"Burstein Index {name} must be a finite non-negative number")
            object.__setattr__(self, name, float(value))

    def to_dict(self) -> dict:
        return {"player_id": self.player_id, "buchholz": self.buchholz,
                "sonneborn_berger": self.sonneborn_berger}

    @classmethod
    def from_dict(cls, data: dict) -> "BursteinIndexValue":
        if not isinstance(data, dict):
            raise InvalidRequestError("Burstein Index value must be an object")
        try:
            return cls(**data)
        except TypeError as exc:
            raise InvalidRequestError(f"invalid Burstein Index value: {exc}") from exc


@dataclass(frozen=True)
class BursteinIndexSet:
    """Complete caller-supplied Burstein values for a pairing request."""

    values: Tuple[BursteinIndexValue, ...]
    provenance: BursteinIndexProvenance

    def __post_init__(self) -> None:
        if not isinstance(self.values, (tuple, list)):
            raise InvalidRequestError("Burstein Index values must be an ordered sequence")
        values = tuple(self.values)
        if any(not isinstance(value, BursteinIndexValue) for value in values):
            raise InvalidRequestError("Burstein Index values must be BursteinIndexValue objects")
        ids = [value.player_id for value in values]
        if len(ids) != len(set(ids)):
            raise InvalidRequestError("Burstein Index values contain duplicate player ids")
        if not isinstance(self.provenance, BursteinIndexProvenance):
            raise InvalidRequestError("Burstein Index provenance is required")
        object.__setattr__(self, "values", tuple(sorted(values, key=lambda value: value.player_id)))

    def by_player_id(self) -> Dict[int, BursteinIndexValue]:
        return {value.player_id: value for value in self.values}

    def to_dict(self) -> dict:
        return {"values": [value.to_dict() for value in self.values],
                "provenance": self.provenance.to_dict()}

    @classmethod
    def from_dict(cls, data: dict) -> "BursteinIndexSet":
        if not isinstance(data, dict) or set(data) != {"values", "provenance"}:
            raise InvalidRequestError(
                "Burstein Index set must contain exactly 'values' and 'provenance'")
        try:
            values = tuple(BursteinIndexValue.from_dict(value) for value in data["values"])
            provenance = BursteinIndexProvenance.from_dict(data["provenance"])
            return cls(values=values, provenance=provenance)
        except TypeError as exc:
            raise InvalidRequestError(f"invalid Burstein Index set: {exc}") from exc


@dataclass(frozen=True)
class P26Request:
    """Single-round 2026 pairing request (ruleset mandatory, never defaulted)."""

    players: Tuple[P26Player, ...] = ()
    ruleset: object = None
    round_number: int = 1
    total_rounds: int = 9
    is_last_round: Optional[bool] = None
    initial_colour: str = "W"
    maxi_tournament: bool = False
    prior_upfloats: Tuple[Tuple[int, int], ...] = ()
    # Legacy per-opponent results retained for compatibility/serialization;
    # never used to calculate tie-break values. Burstein rejects non-empty.
    round_results: Tuple[Tuple[int, Tuple[str, ...]], ...] = ()
    max_steps: Optional[int] = None
    wall_clock_seconds: Optional[float] = None
    cancel_token: Optional[CancelToken] = None
    burstein_indices: Optional[BursteinIndexSet] = None

    def __post_init__(self) -> None:
        if not isinstance(self.players, (tuple, list)):
            raise InvalidRequestError("players must be an ordered sequence")
        players = tuple(self.players)
        if any(not isinstance(player, P26Player) for player in players):
            raise InvalidRequestError("players must contain only P26Player objects")
        object.__setattr__(self, "players", tuple(sorted(players, key=lambda p: p.id)))
        players = self.players
        if self.ruleset is None:
            raise InvalidRequestError("ruleset is mandatory; no default ruleset is used")
        if not isinstance(self.ruleset, (P26RulesetId, str)):
            raise InvalidRequestError("ruleset must be a P26RulesetId or its known string alias")
        for name in ("round_number", "total_rounds"):
            value = getattr(self, name)
            if not isinstance(value, int) or isinstance(value, bool) or value < 1:
                raise InvalidRequestError(f"{name} must be a positive integer")
        if self.round_number > self.total_rounds:
            raise InvalidRequestError("round_number must not exceed total_rounds")
        derived_last_round = self.round_number == self.total_rounds
        if self.is_last_round is None:
            object.__setattr__(self, "is_last_round", derived_last_round)
        elif not isinstance(self.is_last_round, bool):
            raise InvalidRequestError("is_last_round must be a boolean or None")
        elif self.is_last_round != derived_last_round:
            raise InvalidRequestError(
                "is_last_round must agree with round_number and total_rounds")
        if self.initial_colour not in ("W", "B"):
            raise InvalidRequestError("initial_colour must be W or B")
        if not isinstance(self.maxi_tournament, bool):
            raise InvalidRequestError("maxi_tournament must be a boolean")

        if not isinstance(self.prior_upfloats, (tuple, list)):
            raise InvalidRequestError("prior_upfloats must be an ordered sequence")
        upfloats = []
        for entry in self.prior_upfloats:
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise InvalidRequestError("prior_upfloats entries must be (player_id, count)")
            pid, count = entry
            if (not isinstance(pid, int) or isinstance(pid, bool) or pid < 1
                    or not isinstance(count, int) or isinstance(count, bool) or count < 0):
                raise InvalidRequestError(
                    "prior_upfloats entries require positive ids and non-negative integer counts")
            upfloats.append((pid, count))
        if len({pid for pid, _ in upfloats}) != len(upfloats):
            raise InvalidRequestError("prior_upfloats contains duplicate player ids")
        object.__setattr__(self, "prior_upfloats", tuple(sorted(upfloats)))

        if not isinstance(self.round_results, (tuple, list)):
            raise InvalidRequestError("round_results must be an ordered sequence")
        result_entries = []
        for entry in self.round_results:
            if not isinstance(entry, (tuple, list)) or len(entry) != 2:
                raise InvalidRequestError("round_results entries must be (player_id, codes)")
            pid, codes = entry
            if not isinstance(pid, int) or isinstance(pid, bool) or pid < 1:
                raise InvalidRequestError("round_results player ids must be positive integers")
            if not isinstance(codes, (tuple, list)):
                raise InvalidRequestError("round_results codes must be an ordered sequence")
            codes = tuple(codes)
            if any(not isinstance(code, str) or code not in ("W", "D", "L") for code in codes):
                raise InvalidRequestError("round_results codes must contain only W/D/L")
            result_entries.append((pid, codes))
        result_ids = [pid for pid, _ in result_entries]
        if len(result_ids) != len(set(result_ids)):
            raise InvalidRequestError("round_results contains duplicate player ids")
        object.__setattr__(self, "round_results", tuple(sorted(result_entries)))

        by_id = {player.id: player for player in players}
        ids = set(by_id)
        if len(by_id) != len(players):
            raise InvalidRequestError("duplicate player ids")
        tpns = [player.tpn for player in players]
        if len(set(tpns)) != len(tpns):
            raise InvalidRequestError("duplicate tpns; TPN must be unique")
        for player in players:
            for opponent_id in player.opponents:
                if opponent_id not in ids:
                    raise InvalidRequestError(
                        f"player {player.id} lists unknown opponent {opponent_id}")
        for player_id, _count in self.prior_upfloats:
            if player_id not in ids:
                raise InvalidRequestError(
                    f"prior_upfloats references unknown player {player_id}")
        for player_id, codes in self.round_results:
            player = by_id.get(player_id)
            if player is None:
                raise InvalidRequestError(
                    f"round_results references unknown player {player_id}")
            if len(codes) != len(player.opponents):
                raise InvalidRequestError(
                    f"round_results for player {player_id} must align with its opponents")

        if self.cancel_token is not None and not isinstance(self.cancel_token, CancelToken):
            raise InvalidRequestError("cancel_token must be a CancelToken or None")
        if self.max_steps is not None and (
                not isinstance(self.max_steps, int) or isinstance(self.max_steps, bool)
                or self.max_steps < 1):
            raise InvalidRequestError("max_steps must be a positive integer or None")
        if self.wall_clock_seconds is not None and (
                not _finite_number(self.wall_clock_seconds)
                or self.wall_clock_seconds <= 0):
            raise InvalidRequestError("wall_clock_seconds must be finite and positive or None")
        if self.burstein_indices is not None and not isinstance(
                self.burstein_indices, BursteinIndexSet):
            raise InvalidRequestError("burstein_indices must be a BursteinIndexSet or None")

    def round_results_dict(self) -> Dict[int, Tuple[str, ...]]:
        """Convert legacy request data to id -> codes; no calculation occurs."""
        return {pid: tuple(codes) for pid, codes in self.round_results}

    def to_dict(self, *, ruleset: Optional[P26RulesetId] = None) -> Dict[str, object]:
        selected_ruleset = ruleset if ruleset is not None else self.ruleset
        ruleset_data = (selected_ruleset.to_dict()
                        if isinstance(selected_ruleset, P26RulesetId)
                        else selected_ruleset)
        return {
            "schema": "pairing-core/p26-request/v1",
            "players": [player.to_dict() for player in
                        sorted(self.players, key=lambda player: player.id)],
            "ruleset": ruleset_data,
            "round_number": self.round_number,
            "total_rounds": self.total_rounds,
            "is_last_round": self.is_last_round,
            "initial_colour": self.initial_colour,
            "maxi_tournament": self.maxi_tournament,
            "prior_upfloats": [list(entry) for entry in self.prior_upfloats],
            "round_results": [[pid, list(codes)] for pid, codes in self.round_results],
            "max_steps": self.max_steps,
            "wall_clock_seconds": self.wall_clock_seconds,
            "burstein_indices": (self.burstein_indices.to_dict()
                                 if self.burstein_indices is not None else None),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "P26Request":
        if not isinstance(data, dict):
            raise InvalidRequestError("P26Request data must be an object")
        schema = data.get("schema")
        if schema is not None and schema != "pairing-core/p26-request/v1":
            raise VersionMismatchError(f"unsupported P26Request schema {schema!r}")
        allowed = {
            "schema", "players", "ruleset", "round_number", "total_rounds",
            "is_last_round", "initial_colour", "maxi_tournament", "prior_upfloats",
            "round_results", "max_steps", "wall_clock_seconds", "burstein_indices",
        }
        unknown = set(data) - allowed
        if unknown:
            raise InvalidRequestError(
                f"unknown P26Request fields: {', '.join(sorted(unknown))}")
        ruleset = data.get("ruleset")
        if isinstance(ruleset, dict):
            ruleset = P26RulesetId.from_dict(ruleset)
        raw_indices = data.get("burstein_indices")
        try:
            return cls(
                players=tuple(P26Player.from_dict(player) for player in data.get("players", ())),
                ruleset=ruleset,
                round_number=data.get("round_number", 1),
                total_rounds=data.get("total_rounds", 9),
                is_last_round=data.get("is_last_round"),
                initial_colour=data.get("initial_colour", "W"),
                maxi_tournament=data.get("maxi_tournament", False),
                prior_upfloats=data.get("prior_upfloats", ()),
                round_results=data.get("round_results", ()),
                max_steps=data.get("max_steps"),
                wall_clock_seconds=data.get("wall_clock_seconds"),
                burstein_indices=(BursteinIndexSet.from_dict(raw_indices)
                                 if raw_indices is not None else None),
            )
        except (TypeError, ValueError) as exc:
            raise InvalidRequestError(f"malformed P26Request data: {exc}") from exc


@dataclass(frozen=True)
class P26Provenance:
    """Engine and request identity carried by public 2026 results."""

    ruleset: P26RulesetId
    engine_id: str
    engine_version: str
    input_digest: str
    burstein_index_provenance: Optional[BursteinIndexProvenance] = None

    def __post_init__(self) -> None:
        if not isinstance(self.ruleset, P26RulesetId):
            raise InvalidRequestError("provenance.ruleset must be a P26RulesetId")
        try:
            resolve_2026_ruleset(self.ruleset)
        except UnsupportedRulesetError as exc:
            raise InvalidRequestError(
                f"provenance.ruleset is not implemented: {self.ruleset!r}") from exc
        for name in ("engine_id", "engine_version"):
            value = getattr(self, name)
            if not isinstance(value, str) or not value.strip():
                raise InvalidRequestError(f"provenance.{name} must be non-empty text")
        if not isinstance(self.input_digest, str) or not re.fullmatch(
                r"[0-9a-f]{64}", self.input_digest):
            raise InvalidRequestError("provenance.input_digest must be a lowercase SHA-256 hex digest")
        if (self.burstein_index_provenance is not None and
                not isinstance(self.burstein_index_provenance, BursteinIndexProvenance)):
            raise InvalidRequestError(
                "provenance Burstein Index source has an invalid type")

    def to_dict(self) -> dict:
        return {
            "ruleset": self.ruleset.to_dict(),
            "engine_id": self.engine_id,
            "engine_version": self.engine_version,
            "input_digest": self.input_digest,
            "burstein_index_provenance": (
                self.burstein_index_provenance.to_dict()
                if self.burstein_index_provenance is not None else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "P26Provenance":
        expected = {
            "ruleset", "engine_id", "engine_version", "input_digest",
            "burstein_index_provenance",
        }
        if not isinstance(data, dict) or set(data) != expected:
            raise InvalidRequestError("malformed P26 provenance fields")
        try:
            ruleset = P26RulesetId.from_dict(data["ruleset"])
            index_data = data["burstein_index_provenance"]
            return cls(
                ruleset=ruleset,
                engine_id=data["engine_id"],
                engine_version=data["engine_version"],
                input_digest=data["input_digest"],
                burstein_index_provenance=(
                    BursteinIndexProvenance.from_dict(index_data)
                    if index_data is not None else None
                ),
            )
        except (KeyError, TypeError) as exc:
            raise InvalidRequestError(f"malformed P26 provenance: {exc}") from exc


@dataclass(frozen=True)
class P26Pair:
    white_id: int
    black_id: int

    def __post_init__(self) -> None:
        for name in ("white_id", "black_id"):
            value = getattr(self, name)
            if (not isinstance(value, int) or isinstance(value, bool) or value < 1):
                raise InvalidRequestError(
                    f"P26Pair {name} must be a positive integer, got {value!r}.")
        if self.white_id == self.black_id:
            raise InvalidRequestError(
                f"P26Pair self-pairing is unrepresentable: {self.white_id}.")


@dataclass(frozen=True)
class P26Pairing:
    """Complete 2026 round pairing, optionally sealed with provenance."""

    pairs: Tuple[P26Pair, ...]
    bye_id: Optional[int]
    floats: Tuple[Tuple[int, str], ...]  # (player id, 'D'/'U')
    ruleset: str
    notes: Tuple[str, ...] = ()
    round_number: Optional[int] = None
    provenance: Optional[P26Provenance] = None

    def __post_init__(self) -> None:
        if not isinstance(self.pairs, (tuple, list)):
            raise InvalidRequestError("P26Pairing pairs must be an ordered sequence")
        if not isinstance(self.floats, (tuple, list)):
            raise InvalidRequestError("P26Pairing floats must be an ordered sequence")
        if not isinstance(self.notes, (tuple, list)):
            raise InvalidRequestError("P26Pairing notes must be an ordered sequence")
        object.__setattr__(self, "pairs", tuple(self.pairs))
        object.__setattr__(self, "floats", tuple(tuple(entry) if isinstance(
            entry, (tuple, list)) else entry for entry in self.floats))
        object.__setattr__(self, "notes", tuple(self.notes))
        seen = set()
        for pair in self.pairs:
            if not isinstance(pair, P26Pair):
                raise InvalidRequestError(
                    f"P26Pairing pairs must be P26Pair, got {type(pair).__name__}.")
            for pid in (pair.white_id, pair.black_id):
                if pid in seen:
                    raise InvalidRequestError(f"player {pid} appears twice in P26Pairing")
                seen.add(pid)
        if self.bye_id is not None:
            if (not isinstance(self.bye_id, int) or isinstance(self.bye_id, bool)
                    or self.bye_id < 1):
                raise InvalidRequestError("bye_id must be a positive integer or None")
            if self.bye_id in seen:
                raise InvalidRequestError(f"bye player {self.bye_id} is also paired")
        for entry in self.floats:
            if not isinstance(entry, tuple) or len(entry) != 2:
                raise InvalidRequestError(f"malformed floats entry {entry!r}")
            fid, tag = entry
            if (not isinstance(fid, int) or isinstance(fid, bool) or fid < 1
                    or not isinstance(tag, str) or tag not in ("D", "U")):
                raise InvalidRequestError(
                    f"floats entries must be (positive id, 'D'/'U'), got {entry!r}")
        if not isinstance(self.ruleset, str) or not self.ruleset.strip():
            raise InvalidRequestError("ruleset must be a non-empty label")
        for note in self.notes:
            if not isinstance(note, str):
                raise InvalidRequestError(f"notes must be strings, got {note!r}")
        if self.round_number is not None and (
                not isinstance(self.round_number, int) or isinstance(self.round_number, bool)
                or self.round_number < 1):
            raise InvalidRequestError("round_number must be a positive integer or None")
        if self.provenance is not None and not isinstance(self.provenance, P26Provenance):
            raise InvalidRequestError("provenance must be P26Provenance or None")
        if (self.round_number is None) != (self.provenance is None):
            raise InvalidRequestError(
                "round_number and provenance must either both be present or both be absent")
        if self.provenance is not None:
            # The public dispatcher performs the authoritative exact label
            # check. This also protects hand-built or deserialized envelopes.
            expected = next((item["label"] for key, item in SYSTEM_RULESETS.items()
                             if key.system == self.provenance.ruleset.system
                             and key.effective_date == self.provenance.ruleset.effective_date),
                            None)
            if expected is not None and self.ruleset != expected:
                raise InvalidRequestError("pairing ruleset label conflicts with provenance")

    def _body(self) -> Dict[str, object]:
        body: Dict[str, object] = {
            "pairs": [{"white": p.white_id, "black": p.black_id}
                      for p in self.pairs],
            "bye_id": self.bye_id,
            "floats": [list(f) for f in self.floats],
            "ruleset": self.ruleset,
            "notes": list(self.notes),
        }
        if self.provenance is not None:
            body.update({
                "schema": "pairing-core/p26-pairing/v1",
                "round_number": self.round_number,
                "provenance": self.provenance.to_dict(),
            })
        return body

    def to_dict(self, *, with_digest: bool = True) -> Dict[str, object]:
        body = self._body()
        if with_digest and self.provenance is not None:
            body["digest"] = digest_canonical(body)
        return body

    @classmethod
    def from_dict(cls, data: Dict[str, object], *, verify_digest: bool = True) -> "P26Pairing":
        if not isinstance(data, dict):
            raise InvalidRequestError("P26Pairing data must be an object")
        schema = data.get("schema")
        if schema is not None and schema != "pairing-core/p26-pairing/v1":
            raise VersionMismatchError(f"unsupported P26Pairing schema {schema!r}")
        if schema is not None:
            digest = data.get("digest")
            if digest is None and verify_digest:
                raise VersionMismatchError("P26Pairing envelope is missing its digest")
            if digest is not None and (
                    not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest)):
                raise VersionMismatchError("P26Pairing envelope has a malformed digest")
            if "provenance" not in data or "round_number" not in data:
                raise VersionMismatchError("P26Pairing envelope is missing provenance")
            body = {key: value for key, value in data.items() if key != "digest"}
            if verify_digest and digest is not None:
                try:
                    calculated = digest_canonical(body)
                except (TypeError, ValueError) as exc:
                    raise VersionMismatchError(
                        f"P26Pairing envelope is not canonical JSON: {exc}") from exc
                if calculated != digest:
                    raise VersionMismatchError("P26Pairing digest mismatch")
        elif "digest" in data or "provenance" in data or "round_number" in data:
            raise VersionMismatchError(
                "P26Pairing provenance/digest requires a recognized schema")
        allowed = {
            "schema", "pairs", "bye_id", "floats", "ruleset", "notes",
            "round_number", "provenance", "digest",
        }
        unknown = set(data) - allowed
        if unknown:
            raise InvalidRequestError(
                f"unknown P26Pairing fields: {', '.join(sorted(unknown))}")
        try:
            pairs = tuple(P26Pair(pair["white"], pair["black"])
                          for pair in data.get("pairs", ()))
            raw_provenance = data.get("provenance")
            return cls(
                pairs=pairs,
                bye_id=data.get("bye_id"),
                floats=tuple(tuple(entry) for entry in data.get("floats", ())),
                ruleset=data["ruleset"],
                notes=tuple(data.get("notes", ())),
                round_number=data.get("round_number"),
                provenance=(P26Provenance.from_dict(raw_provenance)
                            if raw_provenance is not None else None),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise InvalidRequestError(f"malformed P26Pairing data: {exc}") from exc
