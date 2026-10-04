"""Refresh genuine authenticated compiler output after final actual producer inputs."""
import json
import os
from pathlib import Path
import subprocess
import sys

day = Path(__file__).resolve().parent
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
results = {}
for org, loc in locator["adopters"].items():
    repo, estate = Path(loc["dir"]), Path(loc["estate"])
    results[org] = {}
    for action in ("compose", "verify"):
        argv = [sys.executable, str(repo / ".github/scripts/platform-tools.py"),
                "--adopter-dir", str(repo), "--tools-dir", str(estate / "platform-tools"),
                action, str(repo), "--estate-clone", str(estate)]
        proc = subprocess.run(argv, capture_output=True, text=True, timeout=180,
                              env={**os.environ, "GITSIGN_REKOR_MODE": "offline"})
        log = day / f"{org}-stage2-final-{action}.log"
        log.write_text(proc.stdout + proc.stderr)
        results[org][action] = {"exit": proc.returncode, "log": str(log)}
        (day / "adopter-stage2-final-compose.json").write_text(json.dumps(results, indent=2) + "\n")
        assert proc.returncode == 0, (org, action, proc.stderr, proc.stdout[-1000:])
        print(f"{org}: genuine tools5 {action} PASS", flush=True)
    doc = json.loads((repo / "composed/evidence.json").read_text())
    results[org]["outcome"] = doc["outcome"]
    results[org]["refusals"] = doc["refusals"]
    results[org]["policy_versions"] = [row["version"] for row in doc["members"]]
    (day / "adopter-stage2-final-compose.json").write_text(json.dumps(results, indent=2) + "\n")
