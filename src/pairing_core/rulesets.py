"""Dated ruleset identities + constraint sets (F2 foundation).

PUBLIC. Rules (O03/D13, VERSIONING.md):

- Every pairing call names a RulesetId ``(system, effective_date,
  acceleration, pab_value)``. No silent default drift: resolution is by
  EXACT match against KNOWN_RULESETS (or its string aliases). Any deviation
  (unknown system, other date, acceleration set, custom PAB value) raises
  UnsupportedRulesetError — the v0.1.0 kernel implements exactly one ruleset.
- ConstraintSet carries forced pairs (mappable to the kernel's locked_pairs),
  forbidden pairs, and bye directives. Only forced pairs are honoured by the
  v0.1.0 kernel; anything else raises UnsupportedCapabilityError at the
  boundary (O03: never silently ignored). Enforcement of the rest is
  Dutch-phase work.
- Five-version reporting lives behind ``versions()`` in ``api.py``; the
  implemented-ruleset table here feeds it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from pairing_core.errors import UnsupportedRulesetError

#: Ruleset implemented by the frozen v0.1.0 kernel: pre-2026 Dutch
#: formulation (rules in force through 31 January 2026).
DUTCH_TILL2026_COMPAT = "dutch-till2026-compat"


@dataclass(frozen=True)
class RulesetId:
    """Dated pairing-ruleset identity: system + effective date (+ options).

    Examples: RulesetId("dutch", "2026-01-31") for the frozen compat ruleset;
    RulesetId("dutch", "2026-02-01") names the 2026 rewrite (NOT implemented
    in F2 — resolution rejects it explicitly).
    """
    system: str
    effective_date: str  # YYYY-MM-DD
    acceleration: Optional[str] = None
    pab_value: Optional[float] = None

    def to_dict(self) -> Dict[str, object]:
        """PUBLIC. Stable dict form (canonical key order via sort_keys)."""
        return {"system": self.system,
                "effective_date": self.effective_date,
                "acceleration": self.acceleration,
                "pab_value": self.pab_value}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "RulesetId":
        """PUBLIC. Rebuild; malformed -> InvalidRequestError."""
        from pairing_core.errors import InvalidRequestError

        try:
            system = data["system"]
            date = data["effective_date"]
            if not isinstance(system, str) or not isinstance(date, str):
                raise KeyError("types")
            return RulesetId(system=system, effective_date=date,
                             acceleration=data.get("acceleration"),
                             pab_value=data.get("pab_value"))
        except (KeyError, TypeError, AttributeError) as exc:
            raise InvalidRequestError(
                f"malformed RulesetId dict: {exc}") from exc


@dataclass(frozen=True)
class ConstraintSet:
    """Caller constraints for one round (data, not a layer).

    forced_pairs: (white_id, black_id) tuples placed verbatim (kernel lock).
    forbidden_pairs: unordered (id, id) pairs that must not meet — enforced
        by the kernel as virtual already-played pairs (rematch-equivalent).
    bye_directive: reserved; any non-None value is rejected
        (Dutch-phase work).
    """
    forced_pairs: Tuple[Tuple[int, int], ...] = ()
    forbidden_pairs: Tuple[Tuple[int, int], ...] = ()
    bye_directive: Optional[str] = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "forced_pairs",
                           tuple(tuple(p) for p in self.forced_pairs))
        object.__setattr__(self, "forbidden_pairs",
                           tuple(tuple(p) for p in self.forbidden_pairs))

    def to_dict(self) -> Dict[str, object]:
        """PUBLIC. Stable dict form."""
        return {"forced_pairs": [list(p) for p in self.forced_pairs],
                "forbidden_pairs": [list(p) for p in self.forbidden_pairs],
                "bye_directive": self.bye_directive}

    @staticmethod
    def from_dict(data: Dict[str, object]) -> "ConstraintSet":
        """PUBLIC. Rebuild; malformed -> InvalidRequestError."""
        from pairing_core.errors import InvalidRequestError

        try:
            return ConstraintSet(
                forced_pairs=[tuple(p) for p in
                              data.get("forced_pairs", [])],
                forbidden_pairs=[tuple(p) for p in
                                 data.get("forbidden_pairs", [])],
                bye_directive=data.get("bye_directive"))
        except (KeyError, TypeError, AttributeError) as exc:
            raise InvalidRequestError(
                f"malformed ConstraintSet dict: {exc}") from exc


#: String aliases accepted by resolve_ruleset().
ALIASES: Dict[str, RulesetId] = {
    DUTCH_TILL2026_COMPAT: RulesetId(system="dutch",
                                     effective_date="2026-01-31"),
}

#: Rulesets the frozen v0.1.0 kernel implements (exact-match table).
KNOWN_RULESETS: Dict[RulesetId, Dict[str, str]] = {
    RulesetId(system="dutch", effective_date="2026-01-31"): {
        "label": DUTCH_TILL2026_COMPAT,
        "engine": "native-dutch",
        "engine_version": "0.1.0",
        "note": "frozen v0.1.0 kernel behaviour; pinned by F1 goldens",
    },
}


def resolve_ruleset(ruleset: object) -> RulesetId:
    """Resolve a RulesetId or alias string to its canonical RulesetId.

    Raises UnsupportedRulesetError for anything not exactly known —
    including real future systems (e.g. dutch 2026-02-01): unsupported
    systems must not pretend to resolve (O03).
    """
    candidate: Optional[RulesetId] = None
    if isinstance(ruleset, RulesetId):
        candidate = ruleset
    elif isinstance(ruleset, str) and ruleset in ALIASES:
        return ALIASES[ruleset]
    if candidate is not None and candidate in KNOWN_RULESETS:
        return candidate
    known: List[str] = sorted(
        [k for k in ALIASES] +
        [f"{r.system}@{r.effective_date}" for r in KNOWN_RULESETS
         if f"{r.system}@{r.effective_date}" not in ALIASES])
    raise UnsupportedRulesetError(
        f"Unsupported ruleset {ruleset!r}. Known: {', '.join(known)}.")


def describe_known_rulesets() -> Dict[str, Dict[str, str]]:
    """Implemented-ruleset table for versions() reporting (api.py)."""
    return {rid.system + "@" + rid.effective_date: dict(meta)
            for rid, meta in KNOWN_RULESETS.items()}
