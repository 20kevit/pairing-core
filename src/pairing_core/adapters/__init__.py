"""External-engine adapters (adapter edge, NOT core domain).

Never imported by pairing-core core modules (import-lint enforced):
TRF types, subprocess execution, and vendor-specific conventions live
exclusively here. Adapters are bring-your-own-binary (O04/O06); absence of a
binary is a typed failure, never a silent fallback.
"""

from pairing_core.adapters.trf import (
    TournamentInput,
    TrfPlayer,
    TrfRound,
    build_trf,
    from_engine_request,
    parse_pairing_output,
    parse_trf,
)

__all__ = [
    "TournamentInput",
    "TrfPlayer",
    "TrfRound",
    "build_trf",
    "from_engine_request",
    "parse_pairing_output",
    "parse_trf",
]
