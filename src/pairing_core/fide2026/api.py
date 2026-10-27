"""Validated public dispatcher for the dated 2026 pairing engines."""

from __future__ import annotations

from dataclasses import replace

from pairing_core.envelope import digest_canonical
from pairing_core.errors import (
    CancelledError,
    InternalError,
    InvalidRequestError,
    UnsupportedRulesetError,
)
from pairing_core.fide2026.models import (
    P26Pairing,
    P26Provenance,
    P26Request,
    SYSTEM_RULESETS,
    resolve_2026_ruleset,
)


def pair_2026(request: P26Request) -> P26Pairing:
    """Pair one round under an exact dated ruleset and validate engine output.

    The returned envelope carries a deterministic request digest and the
    resolved ruleset/engine identity. This checks pairing postconditions; it
    is not a formal FIDE conformance evaluation.
    """
    if not isinstance(request, P26Request):
        raise InvalidRequestError("pair_2026 requires a P26Request")
    tok = request.cancel_token
    if tok is not None and tok.cancelled:
        # Entry checkpoint: fast paths tick nothing, so a pre-cancelled run
        # must fail here rather than return a pairing.
        raise CancelledError("pairing run cancelled.")

    # Resolve before checking the roster so unknown rulesets retain their
    # exact-match typed error even when the request is otherwise empty.
    resolved = resolve_2026_ruleset(request.ruleset)
    if not request.players:
        raise InvalidRequestError("at least one player is required")
    if resolved.system != "burstein" and request.burstein_indices is not None:
        raise InvalidRequestError(
            "burstein_indices are only valid for the Burstein ruleset")
    if resolved.system == "burstein" and request.round_results:
        raise InvalidRequestError(
            "round_results are not a Burstein Index calculation input; "
            "Pairing-Core does not calculate Burstein Index values")
    if resolved.system != "dubov" and request.prior_upfloats:
        raise InvalidRequestError(
            "prior_upfloats are only valid for the Dubov ruleset")
    if resolved.system != "lim" and request.maxi_tournament:
        raise InvalidRequestError(
            "maxi_tournament is only valid for the Lim ruleset")

    routed_request = req_with(request, resolved)
    if resolved.system == "dutch":
        from pairing_core.fide2026 import dutch as eng
        result = eng.pair_dutch(routed_request)
    elif resolved.system == "dubov":
        from pairing_core.fide2026 import dubov as eng
        result = eng.pair_dubov(routed_request)
    elif resolved.system == "burstein":
        from pairing_core.fide2026 import burstein as eng
        result = eng.pair_burstein(routed_request)
    elif resolved.system == "lim":
        from pairing_core.fide2026 import lim as eng
        result = eng.pair_lim(routed_request)
    elif resolved.system == "double":
        from pairing_core.fide2026 import double_team as eng
        result = eng.pair_double_or_team(routed_request, system="double")
    elif resolved.system == "team":
        from pairing_core.fide2026 import double_team as eng
        result = eng.pair_double_or_team(routed_request, system="team")
    elif resolved.system == "olympiad":
        from pairing_core.fide2026 import olympiad as eng
        result = eng.pair_olympiad(routed_request)
    else:  # Defensive: resolver and dispatcher must stay in lockstep.
        raise UnsupportedRulesetError(f"no 2026 engine for {resolved.system!r}")

    _validate_2026_result(routed_request, resolved, result)
    if tok is not None and tok.cancelled:
        # Do not publish a result if cancellation arrived after an engine's
        # final search checkpoint but before the public boundary completed.
        raise CancelledError("pairing run cancelled.")

    metadata = next((item for key, item in SYSTEM_RULESETS.items()
                     if key.system == resolved.system
                     and key.effective_date == resolved.effective_date), None)
    if metadata is None:
        raise InternalError(f"no metadata for resolved ruleset {resolved!r}")
    try:
        from pairing_core import __version__ as library_version
        provenance = P26Provenance(
            ruleset=resolved,
            engine_id=metadata["engine"],
            engine_version=library_version,
            input_digest=digest_canonical(request.to_dict(ruleset=resolved)),
            burstein_index_provenance=(
                request.burstein_indices.provenance
                if request.burstein_indices is not None else None
            ),
        )
        return replace(result, round_number=request.round_number,
                       provenance=provenance)
    except Exception as exc:
        if isinstance(exc, InternalError):
            raise
        raise InternalError(f"could not seal 2026 pairing result: {exc}") from exc


def req_with(request: P26Request, resolved) -> P26Request:
    """Return a copy with the canonical resolved ruleset attached."""
    return replace(request, ruleset=resolved)


def _validate_2026_result(request: P26Request, resolved, result: object) -> None:
    """Validate public pairing coverage and core legality postconditions."""
    if not isinstance(result, P26Pairing):
        raise InternalError(
            f"2026 engine returned {type(result).__name__}, expected P26Pairing")

    metadata = next((item for key, item in SYSTEM_RULESETS.items()
                     if key.system == resolved.system
                     and key.effective_date == resolved.effective_date), None)
    if metadata is None or result.ruleset != metadata["label"]:
        raise InternalError(
            f"engine result ruleset {result.ruleset!r} does not match {resolved!r}")

    players = {player.id: player for player in request.players}
    expected = set(players)
    seen = set()
    for pair in result.pairs:
        for player_id in (pair.white_id, pair.black_id):
            if player_id not in expected:
                raise InternalError(
                    f"engine paired unknown player {player_id}")
            if player_id in seen:
                raise InternalError(
                    f"engine used player {player_id} more than once")
            seen.add(player_id)
        from pairing_core.fide2026.common import rematch
        if rematch(players[pair.white_id], players[pair.black_id]):
            raise InternalError(
                f"engine returned a rematch: {pair.white_id} vs {pair.black_id}")

    if len(request.players) % 2:
        if result.bye_id is None:
            raise InternalError("odd roster requires exactly one bye")
        if result.bye_id not in expected:
            raise InternalError(f"engine returned unknown bye player {result.bye_id}")
        if result.bye_id in seen:
            raise InternalError("bye recipient is also paired")
        seen.add(result.bye_id)
    elif result.bye_id is not None:
        raise InternalError("even roster must not have a bye")

    if seen != expected:
        missing = sorted(expected - seen)
        extra = sorted(seen - expected)
        raise InternalError(
            f"engine result does not cover the roster exactly; missing={missing}, extra={extra}")

    for player_id, _tag in result.floats:
        if player_id not in expected:
            raise InternalError(f"engine returned float for unknown player {player_id}")

    if result.bye_id is not None:
        from pairing_core.fide2026.common import pab_eligible
        bye_player = players[result.bye_id]
        eligible = pab_eligible(bye_player)
        if resolved.system == "olympiad":
            eligible = eligible and not bye_player.late_entry
        if not eligible:
            raise InternalError(
                f"engine assigned a bye to ineligible player {result.bye_id}")
