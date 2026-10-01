"""Conformance/differential harness (permanent engineering asset).

Compares pairing outcomes with a fixed taxonomy (compare.py) and runs
rule-anchored conformance corpora (corpus.py). Engine-agnostic: native runs
today; external references plug in when binaries are available. Mismatches
are diagnosed, never auto-baselined; the authoritative ruleset (checked via
the independent validator) stays the source of truth.
"""

from pairing_core.harness.compare import (
    ComparisonOutcome,
    Fingerprint,
    check_constraints,
    compare,
    fingerprint_of,
)
from pairing_core.harness.corpus import (
    FailureRecord,
    build_request,
    load_corpus,
    run_case,
    run_corpus,
)

__all__ = [
    "ComparisonOutcome",
    "FailureRecord",
    "Fingerprint",
    "build_request",
    "check_constraints",
    "compare",
    "fingerprint_of",
    "load_corpus",
    "run_case",
    "run_corpus",
]
