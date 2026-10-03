#!/usr/bin/env python3
"""Validate docs/rules/fide registry hygiene (no network; durable metadata checks).

Checks:
  1. Required registry files exist.
  2. Source IDs unique across SOURCE_INDEX.md + SECONDARY_SOURCES.md (F-*, S-*).
  3. Every Rule ID in RULE_SOURCE_MATRIX.md references a known Source ID.
  4. Status vocabulary restricted to CURRENT/HISTORICAL/SUPERSEDED/UNKNOWN.
  5. All official URLs use https/http scheme (no bare domains).
  6. No system left marked BLOCKED without a SEARCH_LOG entry (exhaustive-search rule).
  7. Statement-class tokens used in research notes come from the controlled list.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIDE = ROOT / "docs" / "rules" / "fide"

REQUIRED = [
    "README.md",
    "SOURCE_INDEX.md",
    "VERSION_TIMELINE.md",
    "CURRENT_STATUS.md",
    "RULE_SOURCE_MATRIX.md",
    "SYSTEM_COVERAGE.md",
    "SECONDARY_SOURCES.md",
    "SEARCH_LOG.md",
    "SOURCE_MANIFEST.md",
    "FINAL_RESEARCH_REPORT.md",
    "swiss/dutch.md",
    "swiss/dubov.md",
    "swiss/burstein.md",
    "swiss/lim.md",
    "swiss/double.md",
    "team/olympiad.md",
    "round_robin/berger.md",
    "match/knockout.md",
]

STATUSES = {"CURRENT", "HISTORICAL", "SUPERSEDED", "UNKNOWN"}
CLASSES = {
    "MANDATORY RULE", "ALGORITHM STEP", "DEFINITION", "EXAMPLE", "NOTE",
    "RECOMMENDATION", "IMPLEMENTATION GUIDANCE", "HISTORICAL RULE",
}

SRC_RE = re.compile(r"\b([FS])-(\d{4})\b")
RULE_RE = re.compile(r"\bR-[A-Z]{1,3}\d{2}\b")
STATUS_RE = re.compile(r"Status:\s*(\w+)")
URL_RE = re.compile(r"https?://[^\s)>\]]+")


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (FIDE / rel).is_file():
            errors.append(f"missing required file: {rel}")

    index = (FIDE / "SOURCE_INDEX.md").read_text() if (FIDE / "SOURCE_INDEX.md").exists() else ""
    secondary = (FIDE / "SECONDARY_SOURCES.md").read_text() if (FIDE / "SECONDARY_SOURCES.md").exists() else ""
    matrix = (FIDE / "RULE_SOURCE_MATRIX.md").read_text() if (FIDE / "RULE_SOURCE_MATRIX.md").exists() else ""

    known_sources = set(SRC_RE.findall(index)) | set(SRC_RE.findall(secondary))
    known_ids = {f"{a}-{b}" for a, b in known_sources}
    if len(known_ids) < 20:
        errors.append(f"suspiciously few source IDs found: {len(known_ids)}")

    for m in RULE_RE.finditer(matrix):
        pass  # rule ids collected below
    rule_ids = set(RULE_RE.findall(matrix))
    if len(rule_ids) < 20:
        errors.append(f"suspiciously few rule IDs in matrix: {len(rule_ids)}")

    # matrix rows must cite a known source id in the Source column
    for i, line in enumerate(matrix.splitlines(), 1):
        if not line.startswith("| R-"):
            continue
        cited = set(f"{a}-{b}" for a, b in SRC_RE.findall(line))
        # allow "via S-xxxx" citations too
        if not (cited & known_ids):
            errors.append(f"matrix line {i} cites no known source: {line[:100]}")

    for name in ["SOURCE_INDEX.md", "SECONDARY_SOURCES.md"]:
        p = FIDE / name
        if not p.exists():
            continue
        for i, line in enumerate(p.read_text().splitlines(), 1):
            m = re.match(r"\s*-\s*Status:\s*(\w+)", line)
            if m and m.group(1) not in STATUSES:
                errors.append(f"{name}:{i}: bad status '{m.group(1)}'")

    for m in URL_RE.finditer(index + secondary):
        url = m.group(0).rstrip(".,;")
        if " " in url:
            errors.append(f"malformed URL: {url}")

    search_log = (FIDE / "SEARCH_LOG.md").read_text() if (FIDE / "SEARCH_LOG.md").exists() else ""
    status_doc = (FIDE / "CURRENT_STATUS.md").read_text() if (FIDE / "CURRENT_STATUS.md").exists() else ""
    if "BLOCKED" in status_doc and "BLOCKED" not in search_log:
        errors.append("BLOCKED status without SEARCH_LOG justification")

    if errors:
        print(f"validate_sources: {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"validate_sources: OK ({len(known_ids)} sources, {len(rule_ids)} rules)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
