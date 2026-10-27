#!/usr/bin/env python3
"""Compatibility entry point for offline FIDE source/evidence validation.

The canonical validation logic lives in ``tools/fide_evidence.py``. This
stable wrapper remains for existing contributor workflows and tests. It does
not access the network and does not issue a conformity verdict.
"""
from __future__ import annotations

import sys

from fide_evidence import load_registry, run


def main() -> int:
    result = run("check")
    if result:
        return result
    sources, systems, clauses = load_registry()
    print(
        "validate_sources: OK "
        f"({len(sources['records'])} sources, "
        f"{len(clauses['records'])} clause records, "
        f"{len(systems['records'])} system views; offline evidence checks)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
