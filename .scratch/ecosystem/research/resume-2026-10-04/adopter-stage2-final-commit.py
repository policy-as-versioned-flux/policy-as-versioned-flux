"""Normal signed source commits in the isolated adopter branches; no external writes."""
import json
from pathlib import Path
import subprocess

day = Path(__file__).resolve().parent
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
checks = json.loads((day / "adopter-stage2-final-checks.json").read_text())
rows = {}
for org, loc in locator["adopters"].items():
    assert checks[org]["existing_tests_exit"] == 0
    assert checks[org]["overlay_selfcheck"]["exit"] == 0
    assert "owned payload schema preserves" in checks[org]["overlay_selfcheck"]["stdout"]
    repo = Path(loc["dir"])
    before = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    changes = subprocess.check_output(["git", "-C", str(repo), "status", "--short"], text=True)
    assert changes.strip(), org
    subprocess.run(["git", "-C", str(repo), "diff", "--check"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "--all"], check=True)
    message = ("Complete dated twin producer sources and observer dependencies\n\n"
               "Bind the genuinely published corrected hub and dated financial instruments; "
               "retain actual evidence grades, immutable app inputs and gated delivery.\n\n"
               "Prepared-by: Codex agent; no human was present during preparation.")
    subprocess.run(["git", "-C", str(repo), "commit", "-m", message], check=True)
    head = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    verified = subprocess.run(["git", "-C", str(repo), "verify-commit", head], capture_output=True, text=True)
    assert verified.returncode == 0, verified.stderr
    status = subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain"], text=True)
    assert not status.strip(), status
    rows[org] = {"before": before, "head": head,
                 "tree": subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD^{tree}"], text=True).strip(),
                 "changes": changes, "normal_ssh_signature": verified.stderr, "clean": True}
    (day / "adopter-stage2-final-signed-commits.json").write_text(json.dumps(rows, indent=2) + "\n")
    print(org + ": normal signed source commit " + head, flush=True)
