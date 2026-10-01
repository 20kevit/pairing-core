"""Conformance/differential comparison taxonomy (W4 harness).

Pure functions, no engines, no I/O. Compares two pairing outcomes for the
SAME logical input and classifies the relationship — never declaring one
side correct merely for differing (the authoritative ruleset, checked via
the independent validator, is the source of truth; this module only
DESCRIBES differences).

Outcome kinds (wave taxonomy):
  EXACT_EQUIVALENT, REORDERED_EQUIVALENT, VALID_ALTERNATIVE (with
  differing dimensions: pairing/colour/bye/float/ordering),
  NATIVE_VIOLATION / REFERENCE_VIOLATION (validator-ERROR on one side),
  CONSTRAINT_VIOLATION (forced/forbidden/bye-directive breach, side named),
  ENGINE_LIMITATION (one side errored: impossible/timeout/unsupported),
  NONDETERMINISM (same engine, same input, outputs differ across runs),
  SERIALIZATION_MISMATCH (round-trip inequality), RULESET_MISMATCH
  (compared across different rulesets — harness misuse, reported).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

EXACT_EQUIVALENT = "exact-equivalent"
REORDERED_EQUIVALENT = "reordered-equivalent"
VALID_ALTERNATIVE = "valid-alternative"
NATIVE_VIOLATION = "native-violation"
REFERENCE_VIOLATION = "reference-violation"
CONSTRAINT_VIOLATION = "constraint-violation"
ENGINE_LIMITATION = "engine-limitation"
NONDETERMINISM = "nondeterminism"
SERIALIZATION_MISMATCH = "serialization-mismatch"
RULESET_MISMATCH = "ruleset-mismatch"


@dataclass(frozen=True)
class Fingerprint:
    """Comparable pairing shape: board-ordered white/black/floats/bye."""
    pairs: Tuple[Tuple[int, Optional[int], str, str], ...]
    bye: Optional[int]


@dataclass(frozen=True)
class ComparisonOutcome:
    """PUBLIC. One classified comparison."""
    kind: str
    dimensions: Tuple[str, ...] = ()
    detail: str = ""


def fingerprint_of(result: object) -> Fingerprint:
    """Build a Fingerprint from RoundPairing or RoundResult."""
    pairs = tuple(
        (c.white_id, c.black_id, c.white_float, c.black_float)
        for c in result.pairings)
    bye = getattr(result, "bye_player_id", None)
    return Fingerprint(pairs=pairs, bye=bye)


def _pair_sets(fp: Fingerprint):
    return {frozenset((w, b)) for (w, b, _, _) in fp.pairs if b is not None}


def _color_map(fp: Fingerprint):
    return {frozenset((w, b)): (w, b) for (w, b, _, _) in fp.pairs
            if b is not None}


def compare(native_fp: Fingerprint, ref_fp: Fingerprint, *,
            native_valid: bool, ref_valid: bool,
            native_error: Optional[str] = None,
            ref_error: Optional[str] = None,
            same_ruleset: bool = True,
            same_engine_run: bool = False) -> ComparisonOutcome:
    """Classify native-vs-reference for one input (pure, deterministic)."""
    if not same_ruleset:
        return ComparisonOutcome(RULESET_MISMATCH,
                                 detail="compared across rulesets")
    if native_error or ref_error:
        if native_error and ref_error:
            if native_error == ref_error:
                return ComparisonOutcome(
                    ENGINE_LIMITATION, ("error",),
                    f"both sides failed identically: {native_error}")
            return ComparisonOutcome(
                ENGINE_LIMITATION, ("error",),
                f"both failed differently: {native_error} vs {ref_error}")
        side = "native" if native_error else "reference"
        return ComparisonOutcome(
            ENGINE_LIMITATION, ("error",),
            f"{side} failed ({native_error or ref_error}); "
            f"other side produced a pairing")
    if same_engine_run and native_fp != ref_fp:
        return ComparisonOutcome(NONDETERMINISM,
                                 detail="same engine+input, outputs differ")
    if not native_valid and not ref_valid:
        return ComparisonOutcome(
            ENGINE_LIMITATION, ("validity",),
            "both sides produced validator-ERROR pairings")
    if not native_valid:
        return ComparisonOutcome(NATIVE_VIOLATION,
                                 detail="native output has validator errors")
    if not ref_valid:
        return ComparisonOutcome(REFERENCE_VIOLATION,
                                 detail="reference output has validator errors")
    if native_fp == ref_fp:
        return ComparisonOutcome(EXACT_EQUIVALENT)
    dims = []
    if _pair_sets(native_fp) != _pair_sets(ref_fp):
        dims.append("pairing")
    else:
        if _color_map(native_fp) != _color_map(ref_fp):
            dims.append("colour")
    if native_fp.bye != ref_fp.bye:
        dims.append("bye")
    nw = sorted((w, wf) for (w, b, wf, _) in native_fp.pairs
                if b is not None)
    rw = sorted((w, wf) for (w, b, wf, _) in ref_fp.pairs
                if b is not None)
    if nw != rw or sorted(bf for (_, _, _, bf) in native_fp.pairs) != \
            sorted(bf for (_, _, _, bf) in ref_fp.pairs):
        if "pairing" not in dims:
            dims.append("float")
    if not dims:
        return ComparisonOutcome(REORDERED_EQUIVALENT,
                                 detail="same pairs/colours, board order differs")
    return ComparisonOutcome(VALID_ALTERNATIVE, tuple(dims),
                             detail="both valid, differ in: "
                             + ",".join(dims))


def check_constraints(fp: Fingerprint, forced: Tuple[tuple, ...],
                      forbidden: Tuple[tuple, ...]) -> Tuple[str, ...]:
    """List constraint breaches in a fingerprint (empty == honoured)."""
    present = _pair_sets(fp)
    breaches = []
    for w, b in forced:
        if frozenset((w, b)) not in present:
            breaches.append(f"forced-missing:{w}-{b}")
    for w, b in forbidden:
        if frozenset((w, b)) in present:
            breaches.append(f"forbidden-present:{w}-{b}")
    return tuple(breaches)
