"""pair_2026 dispatcher (exact-match routing; no fallback)."""

from __future__ import annotations

from pairing_core.errors import CancelledError, UnsupportedRulesetError
from pairing_core.fide2026.models import (
    P26Pairing,
    P26Request,
    resolve_2026_ruleset,
)


def pair_2026(request: P26Request) -> P26Pairing:
    """Pair one round under an exact 2026 ruleset. Unknown -> typed error."""
    tok = request.cancel_token
    if tok is not None and tok.cancelled:
        # entry checkpoint: fast paths (R1 recipes, lex-first) tick nothing,
        # so a pre-cancelled run must fail here, never succeed silently.
        raise CancelledError("pairing run cancelled.")
    resolved = resolve_2026_ruleset(request.ruleset)
    system = resolved.system
    if system == "dutch":
        from pairing_core.fide2026 import dutch as eng
        return eng.pair_dutch(req_with(request, resolved))
    if system == "dubov":
        from pairing_core.fide2026 import dubov as eng
        return eng.pair_dubov(req_with(request, resolved))
    if system == "burstein":
        from pairing_core.fide2026 import burstein as eng
        return eng.pair_burstein(req_with(request, resolved))
    if system == "lim":
        from pairing_core.fide2026 import lim as eng
        return eng.pair_lim(req_with(request, resolved))
    if system == "double":
        from pairing_core.fide2026 import double_team as eng
        return eng.pair_double_or_team(req_with(request, resolved),
                                       system="double")
    if system == "team":
        from pairing_core.fide2026 import double_team as eng
        return eng.pair_double_or_team(req_with(request, resolved),
                                       system="team")
    if system == "olympiad":
        from pairing_core.fide2026 import olympiad as eng
        return eng.pair_olympiad(req_with(request, resolved))
    raise UnsupportedRulesetError(f"no 2026 engine for {system!r}.")


def req_with(request: P26Request, resolved) -> P26Request:
    """Return request with canonical resolved ruleset attached."""
    from dataclasses import replace

    return replace(request, ruleset=resolved)
