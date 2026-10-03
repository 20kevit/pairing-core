"""Source-registry validation inside the test suite (§18).

Runs tools/validate_sources.py as a subprocess (validator stays a standalone
script; the suite pins its green status). No network use.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_source_registry_validates():
    proc = subprocess.run(
        [sys.executable, str(ROOT / "tools" / "validate_sources.py")],
        capture_output=True, text=True, cwd=str(ROOT))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "validate_sources: OK" in proc.stdout
