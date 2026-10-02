"""Stable engine abstraction for pairing-core.

Canonical contract owned by pairing-core. External engines
(JavaFo, BBP) will later be adapters to this interface.
"""
from __future__ import annotations

import math
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from pairing_core.models import PlayerData, RoundResult
from pairing_core.controls import CancelToken, ExecutionBudgets


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


# ═══════════════════════════════════════════════════════════════════
#  F2 foundation: explicit request, validation boundary, compat wrapper,
#  versions report. All additive; v0.1.0 names above are untouched.
# ═══════════════════════════════════════════════════════════════════

@dataclass(frozen=True)
class EngineRequest:
    """PUBLIC. Explicit single-round pairing request (F2).

    Unlike PairingRequest, the ruleset is MANDATORY (O03: no silent default
    drift) and constraints are a ConstraintSet. Optional F5 execution
    controls (budgets/cancel_token, both defaulting to legacy behavior).
    This wrapper returns the v0.1.0 RoundResult so F1 goldens keep applying
    byte-for-byte.
    """
    players: List[PlayerData] = field(default_factory=list)
    ruleset: object = None  # RulesetId | str alias; validated, never defaulted
    round_number: int = 1
    constraints: object = None  # ConstraintSet; None == empty
    budgets: Optional[ExecutionBudgets] = None  # F5; None == legacy caps
    cancel_token: Optional[CancelToken] = None  # F5; None == no cancel


def _is_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def validate_request(request: object) -> object:
    """PUBLIC. Strict validation boundary for EngineRequest (D15).

    New-path semantic: reject malformed/corrupt input with typed errors
    instead of silently absorbing it. The legacy pair_round() path keeps its
    exact v0.1.0 tolerance (goldens pin it); callers needing legacy donor
    objects stay on that path.
    Returns the resolved canonical RulesetId. Raises InvalidRequestError
    (incl. InvalidPlayerError/DuplicatePlayerIdError), UnsupportedRulesetError
    or UnsupportedCapabilityError.
    """
    from pairing_core.errors import (
        DuplicatePlayerIdError,
        InvalidPlayerError,
        InvalidRequestError,
        UnsupportedCapabilityError,
    )
    from pairing_core.rulesets import ConstraintSet, resolve_ruleset

    if not isinstance(request, EngineRequest):
        raise InvalidRequestError(
            f"EngineRequest required, got {type(request).__name__}.")
    players = request.players
    if not isinstance(players, (list, tuple)):
        raise InvalidRequestError("players must be a list of PlayerData.")
    if not isinstance(request.round_number, int) or \
            isinstance(request.round_number, bool) or request.round_number < 1:
        raise InvalidRequestError(
            f"round_number must be an int >= 1, got {request.round_number!r}.")
    seen_ids = set()
    seen_pnos = set()
    opp_map: Dict[int, set] = {}
    for p in players:
        if not isinstance(p, PlayerData):
            raise InvalidRequestError(
                "new request path accepts PlayerData only; legacy donor "
                "objects remain supported via pair_round().")
        pid = p.id
        if not _is_int(pid):
            raise InvalidPlayerError(f"player id must be int, got {pid!r}.")
        if pid in seen_ids:
            raise DuplicatePlayerIdError(f"duplicate player id {pid}.",
                                         player_id=pid)
        seen_ids.add(pid)
        if not _is_int(p.pairing_no) or p.pairing_no < 1:
            raise InvalidPlayerError(
                f"pairing_no must be int >= 1, got {p.pairing_no!r}.",
                player_id=pid)
        if p.pairing_no in seen_pnos:
            raise InvalidPlayerError(
                f"duplicate pairing_no {p.pairing_no}.", player_id=pid)
        seen_pnos.add(p.pairing_no)
        if not _is_int(p.rating) or p.rating < 0:
            raise InvalidPlayerError(
                f"rating must be int >= 0, got {p.rating!r}.", player_id=pid)
        if (not isinstance(p.points, (int, float)) or
                isinstance(p.points, bool) or
                not math.isfinite(p.points) or p.points < 0):
            raise InvalidPlayerError(
                f"points must be a finite number >= 0, got {p.points!r}.",
                player_id=pid)
        if not isinstance(p.color_hist, str) or \
                any(c not in "wb-" for c in p.color_hist):
            raise InvalidPlayerError(
                f"color_hist must use alphabet w/b/-, got {p.color_hist!r}.",
                player_id=pid)
        if not isinstance(p.float_hist, str) or \
                any(c not in "DU-" for c in p.float_hist):
            raise InvalidPlayerError(
                f"float_hist must use alphabet D/U/-, got {p.float_hist!r}.",
                player_id=pid)
        opps = p.opponents
        if not isinstance(opps, (frozenset, set, list, tuple)):
            raise InvalidPlayerError("opponents must be a collection of ids.",
                                     player_id=pid)
        for o in opps:
            if not _is_int(o):
                raise InvalidPlayerError(
                    f"opponent id must be int, got {o!r}.", player_id=pid)
            if o == pid:
                raise InvalidPlayerError("player lists themselves as "
                                         "opponent.", player_id=pid)
        opp_map[pid] = set(opps)
        if not isinstance(p.received_bye, bool):
            raise InvalidPlayerError("received_bye must be bool.",
                                     player_id=pid)
    for pid, opps in opp_map.items():
        for o in opps:
            if o in opp_map and pid not in opp_map[o]:
                raise InvalidPlayerError(
                    f"asymmetric opponent memory: {pid} lists {o} but not "
                    f"vice versa.", player_id=pid)

    resolved = resolve_ruleset(request.ruleset)

    constraints = request.constraints
    if constraints is None:
        constraints = ConstraintSet()
    if not isinstance(constraints, ConstraintSet):
        raise InvalidRequestError("constraints must be a ConstraintSet.")
    for group_name, group in (("forced_pairs", constraints.forced_pairs),
                              ("forbidden_pairs",
                               constraints.forbidden_pairs)):
        if not isinstance(group, (list, tuple)):
            raise InvalidRequestError(f"{group_name} must be a list of pairs.")
        for g in group:
            if (not isinstance(g, (list, tuple)) or len(g) != 2 or
                    not all(_is_int(x) for x in g)):
                raise InvalidRequestError(
                    f"{group_name} entries must be int pairs, got {g!r}.")
    if constraints.forbidden_pairs:
        raise UnsupportedCapabilityError(
            "forbidden pairs are not enforceable by the v0.1.0 kernel; "
            "constrained search is Dutch-phase work (refusing, not ignoring).")
    if constraints.bye_directive is not None:
        raise UnsupportedCapabilityError(
            "bye directives are not honoured by the v0.1.0 kernel "
            "(refusing, not ignoring).")
    if request.budgets is not None and \
            not isinstance(request.budgets, ExecutionBudgets):
        raise InvalidRequestError("budgets must be an ExecutionBudgets.")
    if request.cancel_token is not None and \
            not isinstance(request.cancel_token, CancelToken):
        raise InvalidRequestError("cancel_token must be a CancelToken.")
    return resolved


def pair(request: EngineRequest) -> RoundResult:
    """PUBLIC. Validated compat wrapper: strict boundary, frozen kernel.

    Validates (typed errors), maps forced_pairs to kernel locked_pairs, runs
    the UNMODIFIED v0.1.0 kernel, and translates kernel ValueErrors to the
    typed taxonomy (messages preserved, causes chained). Output is identical
    to pair_round() for the same logical input — pinned by F2 compat tests
    over the F1 golden corpus.
    """
    from pairing_core.engine import SwissEngine
    from pairing_core.errors import translate_kernel_error

    resolved = validate_request(request)
    constraints = request.constraints
    locked = [tuple(p) for p in constraints.forced_pairs] \
        if constraints is not None else []
    try:
        return SwissEngine(
            players=list(request.players),
            round_number=request.round_number,
            locked_pairs=locked,
            budgets=request.budgets,
            cancel_token=request.cancel_token,
        ).generate()
    except ValueError as exc:
        raise translate_kernel_error(
            exc, ruleset=f"{resolved.system}@{resolved.effective_date}",
            round_number=request.round_number) from exc


def versions() -> Dict[str, object]:
    """PUBLIC. Five-version foundation report with explicit statuses.

    Implemented parts carry data; everything else is an explicit
    not-implemented/deferred marker — never silently complete (O03).
    """
    from pairing_core import __version__ as lib_version
    from pairing_core.rulesets import describe_known_rulesets

    return {
        "library": {"version": lib_version, "status": "implemented"},
        "engines": {
            "native-dutch": {"version": lib_version,
                             "kernel": "v0.1.0-frozen",
                             "status": "implemented"},
        },
        "rulesets": describe_known_rulesets(),
        "external": {"status": "not-implemented",
                     "note": "later-phase adapters (BBP, JaVaFo); "
                             "bring-your-own-binary"},
        "formats": {"TRF16": "not-implemented",
                    "TRF26": "not-implemented",
                    "TRFx": "not-implemented",
                    "note": "adapter edge; Dutch phase"},
    }


def pair_detailed(request: EngineRequest) -> object:
    """PUBLIC. Validated pairing with result envelope (F3 seam).

    Same kernel and validation as pair(), but returns a RoundPairing:
    complete pairings + engine/ruleset/version metadata + input digest +
    validator warning codes. Validator ERRORs become InternalError via
    from_kernel (O02: success results are never illegal). No seed, budgets,
    modes, fallback, or criteria costs — those belong to F4/F5.
    """
    from pairing_core import __version__ as lib_version
    from pairing_core.envelope import from_kernel, input_digest
    from pairing_core.validator import validate_round

    resolved = validate_request(request)
    result = pair(request)
    players = list(request.players)
    rep = validate_round(result, players)
    errors = tuple(sorted(f.rule for f in rep.errors))
    warnings = tuple(sorted(
        f.rule for f in rep.findings if f.level in ("WARNING", "INFO")))
    budgets = request.budgets
    budget_dict = None
    if budgets is not None:
        budget_dict = {"max_steps": budgets.max_steps,
                       "wall_clock_seconds": budgets.wall_clock_seconds}
    return from_kernel(
        result,
        engine_id="native-dutch",
        engine_version=lib_version,
        ruleset=resolved,
        library_version=lib_version,
        input_digest_hex=input_digest(players, request.round_number,
                                      resolved),
        warnings=warnings,
        validator_errors=errors,
        budgets=budget_dict,
    )


def pair_via(provider_id: str, request: EngineRequest,
             registry: object = None) -> object:
    """PUBLIC. Explicit provider path (F4): resolve + execute, no fallback.

    Resolution is explicit (unknown id/ruleset/capability -> typed errors,
    never substitution). The provider result must be a RoundPairing;
    anything else is an InternalError (seam guard against invalid
    provider results). registry=None builds the default registry.
    """
    from pairing_core.envelope import RoundPairing
    from pairing_core.errors import InternalError
    from pairing_core.registry import Registry, create_default_registry

    reg = registry if registry is not None else create_default_registry()
    if not isinstance(reg, Registry):
        from pairing_core.errors import InvalidRequestError

        raise InvalidRequestError("registry must be a Registry.")
    provider = reg.resolve(request, provider_id)
    result = provider.pair(request)
    if not isinstance(result, RoundPairing):
        raise InternalError(
            f"provider {provider_id!r} returned "
            f"{type(result).__name__}, not RoundPairing.")
    return result
