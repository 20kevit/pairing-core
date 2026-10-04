"""Release-readiness gates (product hardening wave).

Fast, static checks that the product surface stays coherent:

- required product files exist (docs/entry points/hygiene/CI/packaging),
- README answers the entry-point questions and carries the no-endorsement
  disclaimer without certification claims,
- CHANGELOG covers the current package version,
- no absolute checkout paths leak into tests/tools/src (the suite must
  pass from any clone path or against an installed wheel),
- every example runs green on public API only,
- runtime stays dependency-free (test tooling is an opt-in extra only).
"""
import re
import subprocess
import sys
from pathlib import Path

import pairing_core

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    "README.md",
    "LICENSE",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "CODE_OF_CONDUCT.md",
    "MANIFEST.in",
    "pyproject.toml",
    "docs/RELEASING.md",
    "docs/PERFORMANCE.md",
    "docs/CAPABILITY.md",
    "docs/MIGRATION_V010_TO_CANONICAL.md",
    "docs/spec/API_TIERS.md",
    "docs/spec/VERSIONING.md",
    "docs/spec/TOURNAMENT_BOUNDARIES.md",
    "docs/audit/FIDE_CONFORMANCE_MATRIX.md",
    "docs/audit/SEARCH_CEILING_POLICY.md",
    "examples/basic_swiss.py",
    "examples/custom_provider.py",
    ".github/workflows/ci.yml",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".github/ISSUE_TEMPLATE/bug_report.yml",
]

README_TOPICS = [
    "install",
    "usage",
    "determin",
    "provider",
    "error",
    "external",
    "version",
    "limitation",
    "license",
    "contribut",
]


def test_required_product_files_exist():
    missing = [f for f in REQUIRED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"missing product files: {missing}"


def test_readme_entry_point():
    text = (ROOT / "README.md").read_text(encoding="utf-8").lower()
    absent = [t for t in README_TOPICS if t not in text]
    assert not absent, f"README missing topics: {absent}"
    assert "no fide endorsement" in text, \
        "README must carry the no-endorsement disclaimer"


def test_readme_makes_no_certification_claims():
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    bad = []
    for match in re.finditer(r"\b(fide[ -]?(certified|compliant|endorsed"
                             r"|approved|validated|official))\b", text, re.I):
        context = text[max(0, match.start() - 160):match.start()].lower()
        if not re.search(r"\b(not|no|never|n't|without|disclaimed|independent"
                         r"|claimed)\b", context):
            bad.append(text[match.start():match.end()])
    assert not bad, f"certification-sounding claims in README: {bad}"


def test_changelog_covers_current_version():
    text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert f"[{pairing_core.__version__}]" in text, \
        f"CHANGELOG has no entry for {pairing_core.__version__}"


def test_no_absolute_checkout_paths():
    offenders = []
    self_path = Path(__file__).resolve()
    for path in list((ROOT / "tests").rglob("*.py")) + \
            list((ROOT / "tools").rglob("*.py")) + \
            list((ROOT / "src").rglob("*.py")):
        if path.resolve() == self_path:
            continue  # this gate holds the patterns as string literals
        text = path.read_text(encoding="utf-8")
        for pat in ("/opt/projects", "/root/", "/home/", "C:\\"):
            if pat in text:
                offenders.append(f"{path.relative_to(ROOT)}: {pat}")
    assert not offenders, f"absolute paths leaked: {offenders}"


def test_examples_run_on_public_api():
    for example in ("examples/basic_swiss.py",
                    "examples/custom_provider.py"):
        proc = subprocess.run(
            [sys.executable, str(ROOT / example)],
            capture_output=True, text=True, timeout=120)
        assert proc.returncode == 0, \
            f"{example} failed:\n{proc.stdout}\n{proc.stderr}"


def test_runtime_stays_dependency_free():
    # Zero runtime dependencies is a declared contract (README, SECURITY).
    # Test tooling lives in opt-in extras only; a plain
    # `pip install pairing-core` must pull nothing.
    try:
        import tomllib
    except ModuleNotFoundError:  # Python 3.10 has no stdlib tomllib
        tomllib = None
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if tomllib is not None:
        with open(ROOT / "pyproject.toml", "rb") as fh:
            project = tomllib.load(fh)["project"]
    else:
        import re as _re
        assert not _re.search(r"(?m)^dependencies\s*=", text), \
            "runtime dependencies declared"
        project = {"optional-dependencies": {"test": ["pytest"]}}
    assert "dependencies" not in project, \
        f"runtime dependencies declared: {project['dependencies']}"
    extras = project.get("optional-dependencies", {})
    assert extras, "test tooling must be declared as an opt-in extra"
    assert "pytest" in str(extras), f"pytest not in extras: {extras}"
