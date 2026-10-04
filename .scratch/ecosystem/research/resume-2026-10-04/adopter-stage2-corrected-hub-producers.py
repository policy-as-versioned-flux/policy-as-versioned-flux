"""Replay corrected genuinely published hub against actual current immutable FX pins."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

day = Path(__file__).resolve().parent
hub = day.parents[3]
published = hub / ".estate-publish/hub"
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
pin = "5bc47331a536476f3580542be794908f5053f816"
main = "14ec4902bcbd4be58ac43e0ab47d0ea1f4c8250d"
feed_commit = "974e73514e0d8d4cad2e6906acf51d1cc27028b3"
subprocess.run(["git", "-C", str(published), "merge-base", "--is-ancestor", pin, main], check=True)
verified = subprocess.run(["git", "-C", str(published), "verify-commit", pin], capture_output=True, text=True)
assert verified.returncode == 0, verified.stderr
results = {"hub_commit": pin, "published_main_merge": main,
           "published_main_contains_pin": True, "hub_signature_verification": verified.stderr,
           "feeds_checkout": feed_commit, "current_FX_pin": "fx/v1.1.0",
           "scope": "unchanged actual producers, exact clean published corrected hub, genuine existing signedFX1.1 source; local disposable copies only",
           "adopters": {}}
with tempfile.TemporaryDirectory(prefix="pavf-stage2-corrected-hub-") as temporary:
    clean = Path(temporary) / "hub"
    subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", str(published), str(clean)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clean), "checkout", "--detach", pin], check=True, capture_output=True)
    copies = clean / ".estate-clone"
    copies.mkdir(exist_ok=True)
    for org, loc in locator["adopters"].items():
        source = Path(loc["dir"])
        assert f"hub_commit: {pin}" in (source / "twin/PIN.yaml").read_text()
        shutil.copytree(source, copies / org, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    feeds = copies / "feeds"
    source_feeds = Path(locator["adopters"]["driftwood"]["estate"]) / "feeds"
    subprocess.run(["git", "clone", "--no-hardlinks", str(source_feeds), str(feeds)], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(feeds), "checkout", "--detach", feed_commit], check=True, capture_output=True)
    results["FX_tag_object"] = subprocess.check_output(["git", "-C", str(feeds), "rev-parse", "fx/v1.1.0"], text=True).strip()
    assert subprocess.check_output(["git", "-C", str(feeds), "rev-parse", "fx/v1.1.0^{}"], text=True).strip() == feed_commit
    env = {**os.environ, "GITSIGN_REKOR_MODE": "offline"}
    for org, loc in locator["adopters"].items():
        source = Path(loc["dir"])
        before = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (source / "twin/forward-intel").rglob("feed.json")}
        proc = subprocess.run([sys.executable, str(copies / org / "twin/emit-forward-intel.py"), "--check"],
                              cwd=clean, env=env, capture_output=True, text=True, timeout=120)
        unchanged = before == {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in (source / "twin/forward-intel").rglob("feed.json")}
        if org == "ludlow":
            correct = proc.returncode == 3 and "CANNOT LOOK" in proc.stdout and "2025-12" in proc.stdout and "2026-08" in proc.stdout
            semantic = "honest missing dated instrument; not emitted or admitted"
        else:
            correct = proc.returncode == 0 and "byte-identical" in proc.stdout
            semantic = "actual same-currency producer exact bytes PASS"
        results["adopters"][org] = {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "correct_semantic_result": correct, "result_semantics": semantic,
            "source_forward_intel_unchanged": unchanged}
        (day / f"{org}-stage2-corrected-hub-producer.log").write_text(proc.stdout + proc.stderr)
        (day / "adopter-stage2-corrected-hub-producers.json").write_text(json.dumps(results, indent=2) + "\n")
        print(f"{org}: corrected hub producer exit{proc.returncode}; {semantic}")
    results["clean_hub_tracked_tree_unchanged"] = not subprocess.check_output(["git", "-C", str(clean), "status", "--porcelain", "--untracked-files=no"], text=True).strip()
(day / "adopter-stage2-corrected-hub-producers.json").write_text(json.dumps(results, indent=2) + "\n")
sys.exit(0 if all(r["correct_semantic_result"] and r["source_forward_intel_unchanged"] for r in results["adopters"].values()) else 1)
