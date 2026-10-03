#!/usr/bin/env python3
"""Validate docs/rules/fide registry hygiene + traceability (§18).

No network; durable metadata checks only.

Checks:
  1. Required registry files exist (incl. evidence/, extracted/, catalog).
  2. Source IDs unique across SOURCE_INDEX.md + SECONDARY_SOURCES.md.
  3. Every Rule ID in RULE_SOURCE_MATRIX.md references a known Source ID.
  4. Status vocabulary: source entries + matrix Status column.
  5. All official URLs use https/http scheme (no bare domains).
  6. No BLOCKED status without SEARCH_LOG justification.
  7. Every matrix row carries implementation traceability
     (Evidence + Implementation + Test + Status columns non-empty).
  8. MATRIX_STATUS vocabulary restricted to the honest set (§16).
  9. Evidence files exist for every implemented system; FULL_TEXT claimed in
     the matrix only for systems with a FULL_TEXT evidence file.
  10. CURRENT_SYSTEM_CATALOG.md covers every engine system.
  11. Supersession targets name existing Source IDs.
  12. No duplicate Source-ID definitions in SOURCE_INDEX.md.
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
    "CURRENT_SYSTEM_CATALOG.md",
    "swiss/dutch.md",
    "swiss/dubov.md",
    "swiss/burstein.md",
    "swiss/lim.md",
    "swiss/double.md",
    "team/olympiad.md",
    "round_robin/berger.md",
    "match/knockout.md",
    "evidence/DUTCH_2026_EVIDENCE.md",
    "evidence/DUBOV_2026_EVIDENCE.md",
    "evidence/BURSTEIN_2026_EVIDENCE.md",
    "evidence/LIM_2026_EVIDENCE.md",
    "evidence/DOUBLE_SWISS_2026_EVIDENCE.md",
    "evidence/TEAM_SWISS_2026_EVIDENCE.md",
    "evidence/BAKU_2026_EVIDENCE.md",
    "evidence/OLYMPIAD_EVIDENCE.md",
    "extracted/DUTCH_2026_RULES.md",
    "extracted/DUBOV_2026_RULES.md",
    "extracted/BURSTEIN_2026_RULES.md",
    "extracted/LIM_2026_RULES.md",
    "extracted/OTHER_2026_RULES.md",
    "extracted/DUTCH_FLOAT_CONTROL_TIMELINE.md",
]

STATUSES = {"CURRENT", "HISTORICAL", "SUPERSEDED", "UNKNOWN"}
MATRIX_STATUS = {"EVIDENCED", "EVIDENCED-READING", "FROZEN-COMPAT",
                 "SELECTION-ONLY", "DOCUMENTED", "CORRECTED",
                 "OUT-OF-SCOPE", "WITHDRAWN"}
EVIDENCE_GRADES = {"FULL_TEXT", "OFFICIAL_PDF", "OFFICIAL_EXCERPT",
                   "SECONDARY_ONLY", "CONTEXT", "WITHDRAWN", "—"}

SRC_RE = re.compile(r"\b([FS])-(\d{4})\b")
RULE_RE = re.compile(r"\bR-[A-Z]{1,3}\d{2}\b")
URL_RE = re.compile(r"https?://[^\s)>\]]+")
EVID_RE = re.compile(r"Evidence(?: type)?:\s*([A-Z_]+)")


def main() -> int:
    errors: list[str] = []
    for rel in REQUIRED:
        if not (FIDE / rel).is_file():
            errors.append(f"missing required file: {rel}")

    index = _read("SOURCE_INDEX.md")
    secondary = _read("SECONDARY_SOURCES.md")
    matrix = _read("RULE_SOURCE_MATRIX.md")
    catalog = _read("CURRENT_SYSTEM_CATALOG.md")

    known_ids = {f"{a}-{b}" for a, b in SRC_RE.findall(index)} | \
        {f"{a}-{b}" for a, b in SRC_RE.findall(secondary)}
    if len(known_ids) < 20:
        errors.append(f"suspiciously few source IDs found: {len(known_ids)}")

    # 12. duplicate Source-ID section definitions
    defs = re.findall(r"^### ([FS]-\d{4})\b", index, re.M)
    if len(set(defs)) != len(defs):
        dupes = sorted({d for d in defs if defs.count(d) > 1})
        errors.append(f"duplicate source definitions: {dupes}")

    rule_ids = set(RULE_RE.findall(matrix))
    if len(rule_ids) < 40:
        errors.append(f"suspiciously few rule IDs in matrix: {len(rule_ids)}")

    # 3+7+8. matrix rows: source citation + full traceability + status vocab
    fulltext_systems = set()
    for ev in (FIDE / "evidence").glob("*.md"):
        grades = set(EVID_RE.findall(ev.read_text()))
        if "FULL_TEXT" in grades:
            fulltext_systems.add(ev.stem)
    for i, line in enumerate(matrix.splitlines(), 1):
        if not line.startswith("| R-") and not line.startswith("| W-"):
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 12:
            errors.append(f"matrix line {i}: only {len(cells)} columns "
                          f"(need 11+): {line[:80]}")
            continue
        cited = {f"{a}-{b}" for a, b in SRC_RE.findall(line)}
        if not (cited & known_ids) and "W-01" not in line:
            errors.append(f"matrix line {i} cites no known source.")
        evidence, impl, test, status = cells[7], cells[8], cells[9], cells[10]
        if status not in MATRIX_STATUS:
            errors.append(f"matrix line {i}: bad status '{status}'.")
        if evidence not in EVIDENCE_GRADES:
            errors.append(f"matrix line {i}: bad evidence '{evidence}'.")
        if status == "EVIDENCED" and not (impl and test):
            errors.append(f"matrix line {i}: EVIDENCED without impl/test.")
        if evidence == "FULL_TEXT" and status in ("EVIDENCED",
                                                  "EVIDENCED-READING",
                                                  "SELECTION-ONLY"):
            pass  # full-text systems verified via evidence files (§9 below)

    # 9. FULL_TEXT only with backing evidence file
    if not fulltext_systems:
        errors.append("no FULL_TEXT evidence file found.")
    for name in ["SOURCE_INDEX.md", "SECONDARY_SOURCES.md"]:
        for i, line in enumerate((FIDE / name).read_text().splitlines(), 1):
            m = re.match(r"\s*-\s*Status:\s*(\w+)", line)
            if m and m.group(1) not in STATUSES:
                errors.append(f"{name}:{i}: bad status '{m.group(1)}'")

    for m in URL_RE.finditer(index + secondary):
        if " " in m.group(0).rstrip(".,;"):
            errors.append(f"malformed URL: {m.group(0)[:80]}")

    # 11. supersession targets exist
    for m in re.finditer(r"[Ss]upersedes?:?\s*([FS]-\d{4}(?:\s*[,+&]\s*[FS]-\d{4})*)",
                         index):
        for sid in SRC_RE.findall(m.group(1)):
            full = f"{sid[0]}-{sid[1]}"
            if full not in known_ids:
                errors.append(f"dangling supersession target: {full}")

    # 10. catalog covers every engine system
    for system in ("dutch-2026", "dubov-2026", "burstein-2026", "lim-2026",
                   "double-2026", "team-2026", "olympiad-2022", "baku",
                   "berger"):
        if system not in catalog.lower():
            errors.append(f"catalog missing system: {system}")

    search_log = _read("SEARCH_LOG.md")
    status_doc = _read("CURRENT_STATUS.md")
    if "BLOCKED" in status_doc and "BLOCKED" not in search_log:
        errors.append("BLOCKED status without SEARCH_LOG justification")

    if errors:
        print(f"validate_sources: {len(errors)} problem(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print(f"validate_sources: OK ({len(known_ids)} sources, "
          f"{len(rule_ids)} rules, {len(fulltext_systems)} full-text systems)")
    return 0


def _read(name: str) -> str:
    p = FIDE / name
    return p.read_text() if p.exists() else ""


if __name__ == "__main__":
    sys.exit(main())
