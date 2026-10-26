"""The public wrapper must not hide an undeclared wait behind a declared one.

Only the money child is a fixture. The shell wrapper, complete manifest and judge CLI
are copied unchanged from this checkout and run as production callers invoke them.
No estate grading, financial calculation, native engine or cryptographic check runs.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = "verify/pound-seam/verify-pound-seam.sh"
KNOWN = (
    "SKIP: driftwood prices[5] (feeds/threat-register switching) could not be priced, "
    "and says why: missing instrument: forward-intel supplies no lef")
OTHER_KNOWN = (
    "SKIP: driftwood prices[3] (feeds/cve feed) could not be priced, and says why: "
    "No scanned CVE is in the pinned KEV feed; 334 scanned CVE(s) outside it are named "
    "absences carrying no amount.")
UNKNOWN = (
    "SKIP: tuppence prices[0] (twin/forward-intel feed) could not be priced, "
    "and says why: missing instrument: GBP conversion table unavailable")


@pytest.fixture
def wrapper_root(tmp_path: Path) -> Path:
    for name in (WRAPPER, "verify/pound-seam/pound_seam.py",
                 "talk/truth_manifest.py", "talk/verify-manifest.txt"):
        target = tmp_path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / name, target)
    (tmp_path / ".estate-clone/platform").mkdir(parents=True)
    adapter = tmp_path / ".venv/bin/python"
    adapter.parent.mkdir(parents=True)
    adapter.write_text(
        f"#!{sys.executable}\n"
        "import os, sys\n"
        "from pathlib import Path\n"
        "if len(sys.argv) > 2 and Path(sys.argv[1]).name == 'pound_seam.py':\n"
        "    if sys.argv[2] == 'selfcheck':\n"
        "        sys.exit(0)\n"
        "    sys.stdout.write(os.environ['POUND_FIXTURE_OUTPUT'])\n"
        "    sys.exit(int(os.environ['POUND_FIXTURE_EXIT']))\n"
        f"os.execv({sys.executable!r}, [{sys.executable!r}, *sys.argv[1:]])\n")
    adapter.chmod(0o755)
    return tmp_path


def run_wrapper(root: Path, output: str, child_exit: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [shutil.which("bash") or "bash", str(root / WRAPPER)],
        env={**os.environ, "POUND_FIXTURE_OUTPUT": output,
             "POUND_FIXTURE_EXIT": str(child_exit), "PYTHONDONTWRITEBYTECODE": "1"},
        capture_output=True, text=True, timeout=10)


def judge(root: Path, line: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(root / "talk/truth_manifest.py"), "judge",
         str(root / "talk/verify-manifest.txt"), WRAPPER, line],
        capture_output=True, text=True, timeout=10)


@pytest.mark.parametrize("output,child_exit,expected", [
    pytest.param(KNOWN + "\n", 3, 3, id="single-declared-wait"),
    pytest.param(UNKNOWN + "\n", 3, 1, id="single-undeclared-wait"),
    pytest.param(KNOWN + "\n" + UNKNOWN + "\n", 3, 1, id="declared-then-undeclared"),
    pytest.param(UNKNOWN + "\n" + KNOWN + "\n", 3, 1, id="undeclared-then-declared"),
    pytest.param(KNOWN + "\n" + OTHER_KNOWN + "\n", 3, 3, id="multiple-declared-waits"),
    pytest.param(KNOWN + "\n" + UNKNOWN, 3, 1, id="unterminated-undeclared-tail"),
    pytest.param("PASS: child produced no SKIP reason\n", 3, 1, id="missing-SKIP-reason"),
    pytest.param("FAIL: backend refused the price\n" + KNOWN + "\n", 1, 1,
                 id="backend-FAIL-precedes-declared-wait"),
    pytest.param("FAIL: backend refused the price\n" + KNOWN + "\n", 3, 1,
                 id="FAIL-line-with-inconsistent-child-wait-exit"),
    pytest.param("PASS: every child assertion held\n", 0, 0, id="backend-PASS"),
])
def test_every_reason_controls_the_actual_wrapper_and_final_gate_line(
        wrapper_root: Path, output: str, child_exit: int, expected: int) -> None:
    result = run_wrapper(wrapper_root, output, child_exit)
    assert result.returncode == expected, (result.stdout, result.stderr)
    assert result.stdout.startswith(output), "raw child output must be preserved"
    last = result.stdout.splitlines()[-1]
    if expected == 3:
        assert last == output.splitlines()[0]
        assert judge(wrapper_root, last).returncode == 0
    elif expected == 1:
        assert last.startswith("FAIL:"), result.stdout
    else:
        assert last.startswith("PASS:"), result.stdout


@pytest.mark.parametrize("missing", ["talk/truth_manifest.py", "talk/verify-manifest.txt"])
def test_a_judge_instrument_failure_cannot_accept_a_declared_wait(
        wrapper_root: Path, missing: str) -> None:
    (wrapper_root / missing).unlink()
    result = run_wrapper(wrapper_root, KNOWN + "\n", 3)
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert result.stdout.startswith(KNOWN + "\n")
    assert result.stdout.splitlines()[-1].startswith("FAIL:")
