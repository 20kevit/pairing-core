"""Conformance corpus loader + native runner (W4 harness).

Corpus JSON (tests/data/conformance/*.json): hand-authored INPUTS with
outcome CLASSES (not recorded pairings) — expectations are rule-anchored:
"valid" means pair_via succeeds AND the independent validator reports no
errors; "error" means the exact typed error. Optional exact pins (bye id)
exist only for documented policy behavior. Mismatches yield structured
failure records; the runner never auto-baselines.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from pairing_core import (
    ConstraintSet,
    EngineRequest,
    PlayerData,
    pair_via,
    validate_round,
)
from pairing_core.errors import PairingError
from pairing_core.harness.compare import (
    ComparisonOutcome,
    ENGINE_LIMITATION,
    fingerprint_of,
)


@dataclass(frozen=True)
class FailureRecord:
    """Structured mismatch diagnosis (stored, never auto-applied)."""
    case_id: str
    expected: str
    observed: str
    detail: str = ""


def load_corpus(path: str) -> Dict[str, Any]:
    """Load and shape-check a conformance corpus file."""
    from pairing_core.errors import InvalidRequestError

    with open(path, encoding="utf-8") as fh:
        doc = json.load(fh)
    if not isinstance(doc, dict) or not isinstance(doc.get("cases"), list):
        raise InvalidRequestError(f"bad corpus file: {path}")
    return doc


def build_request(case: Dict[str, Any]) -> EngineRequest:
    """Build an EngineRequest from a corpus case (compat ruleset)."""
    players = [PlayerData(
        id=p["id"], pairing_no=p["pairing_no"],
        rating=p.get("rating", 0), points=p.get("points", 0.0),
        color_hist=p.get("color_hist", ""),
        opponents=frozenset(p.get("opponents", [])),
        received_bye=p.get("received_bye", False),
        float_hist=p.get("float_hist", "")) for p in case["players"]]
    forced = [tuple(x) for x in case.get("forced", [])]
    return EngineRequest(
        players=players, ruleset=case.get("ruleset",
                                          "dutch-till2026-compat"),
        round_number=case.get("round", 1),
        constraints=ConstraintSet(forced_pairs=forced))


def run_case(case: Dict[str, Any]) -> Optional[FailureRecord]:
    """Execute one case against the native provider; None == as expected."""
    expect = case.get("expect", {})
    try:
        result = pair_via("native-dutch", build_request(case))
    except PairingError as exc:
        if expect.get("outcome") == "error" and \
                type(exc).__name__ == expect.get("error"):
            return None
        return FailureRecord(case["id"], str(expect),
                             f"error:{type(exc).__name__}: {exc}")
    if expect.get("outcome") != "valid":
        return FailureRecord(case["id"], str(expect),
                             "unexpected-success (rule-gap? investigate)")
    rep = validate_round(result, build_request(case).players)
    if rep.has_errors:
        return FailureRecord(case["id"], "valid",
                             "validator-ERROR on native output: "
                             + repr(rep.error_summary))
    if "bye" in expect and result.bye_player_id != expect["bye"]:
        return FailureRecord(case["id"], f"bye={expect['bye']}",
                             f"bye={result.bye_player_id}")
    return None


def run_corpus(path: str) -> List[FailureRecord]:
    """Run every case; return failure records (empty == full pass)."""
    doc = load_corpus(path)
    failures = []
    for case in doc["cases"]:
        record = run_case(case)
        if record is not None:
            failures.append(record)
    return failures
