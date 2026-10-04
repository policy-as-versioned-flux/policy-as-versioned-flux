"""Finite existing adopter tests and actual overlay diagnostics at the published hub pin."""
from __future__ import annotations
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

day = Path(__file__).resolve().parent
hub = day.parents[3]
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
pin = "5bc47331a536476f3580542be794908f5053f816"
env = {**os.environ, "GITSIGN_REKOR_MODE": "offline"}
results = {}
for org, loc in locator["adopters"].items():
    repo = Path(loc["dir"])
    done = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"], cwd=repo,
                          env=env, capture_output=True, text=True, timeout=180)
    (day / f"{org}-stage2-final-tests.log").write_text(done.stdout + done.stderr)
    results[org] = {"existing_tests_exit": done.returncode, "test_output": done.stdout + done.stderr}
    (day / "adopter-stage2-final-checks.json").write_text(json.dumps(results, indent=2) + "\n")
    assert done.returncode == 0, (org, done.stdout, done.stderr)
    print(f"{org}: existing source tests PASS", flush=True)
with tempfile.TemporaryDirectory(prefix="pavf-stage2-final-selfchecks-") as temporary:
    clean = Path(temporary) / "hub"
    for repo, source in ((clean, hub / ".estate-publish/hub"),):
        subprocess.run(["git", "clone", "--no-hardlinks", str(source), str(repo)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(repo), "checkout", "--detach", pin], check=True, capture_output=True)
    (clean / ".venv").symlink_to(hub / ".venv", target_is_directory=True)
    copies = clean / ".estate-clone"
    copies.mkdir(exist_ok=True)
    for org, loc in locator["adopters"].items():
        shutil.copytree(Path(loc["dir"]), copies / org, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    estate = Path(locator["adopters"]["ludlow"]["estate"])
    for name in ("platform", "feeds"):
        target = copies / name
        subprocess.run(["git", "clone", "--no-hardlinks", str(estate / name), str(target)], check=True, capture_output=True)
        subprocess.run(["git", "-C", str(target), "checkout", "--detach",
                       subprocess.check_output(["git", "-C", str(estate / name), "rev-parse", "HEAD"], text=True).strip()],
                       check=True, capture_output=True)
    for org in locator["adopters"]:
        done = subprocess.run(["bash", str(copies / org / "verify-twin-overlay.sh")], cwd=clean,
                              env=env, capture_output=True, text=True, timeout=120)
        (day / f"{org}-stage2-final-overlay.log").write_text(done.stdout + done.stderr)
        results[org]["overlay_selfcheck"] = {"exit": done.returncode, "stdout": done.stdout, "stderr": done.stderr}
        (day / "adopter-stage2-final-checks.json").write_text(json.dumps(results, indent=2) + "\n")
        assert done.returncode == 0, (org, done.stdout, done.stderr)
        assert "threshold (3)" in done.stdout, done.stdout
        print(f"{org}: actual declared-threshold3 overlay diagnostic PASS", flush=True)
