"""FIDE 2026 pairing systems (additive namespace; v0.2.0 untouched).

Implements the 2026 FIDE Swiss family from FULL_TEXT Council-bundle evidence
(docs/rules/fide/evidence/*_EVIDENCE.md): dutch-2026, dubov-2026,
burstein-2026, lim-2026, double-2026, team-2026, olympiad-2022, plus the baku
accelerated modifier and C.04.2 board-order sorting.

Isolation rules (owner decisions O01/O03/O08):
- Nothing here touches the frozen v0.1.0/v0.2.0 kernel, KNOWN_RULESETS,
  KNOWN_SYSTEMS, or resolve_ruleset() (all pinned by regression tests).
- Own ruleset table (SYSTEM_RULESETS), own resolver, own entry point
  pair_2026(). No silent fallback: unknown system -> UnsupportedRulesetError.
- No BBP/JaVaFo/vendor concepts in the domain model; FIDE articles only.
"""

from pairing_core.fide2026.models import (
    DUBOV_2026,
    DUTCH_2026,
    BURSTEIN_2026,
    LIM_2026,
    DOUBLE_2026,
    TEAM_2026,
    OLYMPIAD_2022,
    P26Pairing,
    P26Player,
    P26Request,
    P26RulesetId,
    SYSTEM_RULESETS,
    resolve_2026_ruleset,
)
from pairing_core.fide2026.api import pair_2026

__all__ = [
    "DUBOV_2026", "DUTCH_2026", "BURSTEIN_2026", "LIM_2026",
    "DOUBLE_2026", "TEAM_2026", "OLYMPIAD_2022",
    "P26Pairing", "P26Player", "P26Request", "P26RulesetId",
    "SYSTEM_RULESETS", "resolve_2026_ruleset", "pair_2026",
]
