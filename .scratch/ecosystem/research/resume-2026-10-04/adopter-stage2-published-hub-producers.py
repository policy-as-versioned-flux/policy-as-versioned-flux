"""Replay exact candidate producers against genuinely published clean pinned hub bytes."""
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
pin = "6ed89616d7d43dece00b5daa8f0a03c56b53d5e7"
published_main = "e62194b0c700f0d8a94787e6a2f7063608862ace"
subprocess.run(["git", "-C", str(published), "merge-base", "--is-ancestor", pin, published_main], check=True)
verified = subprocess.run(["git", "-C", str(published), "verify-commit", pin], capture_output=True, text=True)
assert verified.returncode == 0, verified.stderr
results = {"hub_commit": pin, "published_main_merge": published_main,
           "published_main_contains_exact_pin": True, "hub_signature_verification": verified.stderr,
           "scope": "actual unmodified producer --check in disposable copies, clean exact published hub, genuine feeds; no external mutation", "adopters": {}}
refresh = "--refresh" in sys.argv
with tempfile.TemporaryDirectory(prefix="pavf-stage2-published-hub-") as temporary:
    clean = Path(temporary) / "hub"
    subprocess.run(["git", "clone", "--no-hardlinks", "--no-checkout", str(published), str(clean)],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(clean), "checkout", "--detach", pin], check=True, capture_output=True)
    assert subprocess.check_output(["git", "-C", str(clean), "rev-parse", "HEAD"], text=True).strip() == pin
    copies = clean / ".estate-clone"
    copies.mkdir(exist_ok=True)
    for org, loc in locator["adopters"].items():
        source = Path(loc["dir"])
        assert f"hub_commit: {pin}" in (source / "twin/PIN.yaml").read_text()
        shutil.copytree(source, copies / org, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    feed_source = Path(locator["adopters"]["driftwood"]["estate"]) / "feeds"
    subprocess.run(["git", "clone", "--no-hardlinks", str(feed_source), str(copies / "feeds")], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(copies / "feeds"), "checkout", "--detach", "974e73514e0d8d4cad2e6906acf51d1cc27028b3"], check=True, capture_output=True)
    env = {**os.environ, "GITSIGN_REKOR_MODE": "offline"}
    for org, loc in locator["adopters"].items():
        source = Path(loc["dir"])
        hashes_before = {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                         for p in (source / "twin/forward-intel").rglob("feed.json")}
        refreshed = []
        if refresh:
            emitted = subprocess.run([sys.executable, str(copies / org / "twin/emit-forward-intel.py")],
                                     cwd=clean, env=env, capture_output=True, text=True, timeout=120)
            assert emitted.returncode == 0, (org, emitted.stdout, emitted.stderr)
            for rendered in (copies / org / "twin/forward-intel").rglob("feed.json"):
                relative = rendered.relative_to(copies / org)
                target = source / relative
                before, after = target.read_bytes() if target.is_file() else None, rendered.read_bytes()
                if before != after:
                    old_doc, new_doc = json.loads(before) if before else {"payload": {}}, json.loads(after)
                    delta = {key: {"old": old_doc["payload"].get(key), "new": new_doc["payload"].get(key)}
                             for key in set(old_doc["payload"]) | set(new_doc["payload"])
                             if old_doc["payload"].get(key) != new_doc["payload"].get(key)}
                    refreshed.append({"path": str(relative), "before_sha256": hashlib.sha256(before).hexdigest() if before else None,
                                      "after_sha256": hashlib.sha256(after).hexdigest(), "payload_delta": delta})
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(after)
            results["adopters"][org] = {"producer_emit_exit": emitted.returncode, "producer_emit_stdout": emitted.stdout}
        proc = subprocess.run([sys.executable, str(copies / org / "twin/emit-forward-intel.py"), "--check"],
                              cwd=clean, env=env, capture_output=True, text=True, timeout=120)
        (day / f"{org}-stage2-published-hub-producer.log").write_text(proc.stdout + proc.stderr)
        results["adopters"][org] = {**results["adopters"].get(org, {}), "exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr,
            "pin": pin, "derived_feed_refresh": refreshed, "source_forward_intel_unchanged": hashes_before == {
                str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in (source / "twin/forward-intel").rglob("feed.json")}}
        (day / "adopter-stage2-published-hub-producers.json").write_text(json.dumps(results, indent=2) + "\n")
        print(f"{org}: actual clean published pinned hub producer check exit {proc.returncode}")
    results["clean_hub_tracked_tree_unchanged"] = not subprocess.check_output(
        ["git", "-C", str(clean), "status", "--porcelain", "--untracked-files=no"], text=True).strip()
(day / "adopter-stage2-published-hub-producers.json").write_text(json.dumps(results, indent=2) + "\n")
sys.exit(0 if all(r["exit"] == 0 and (refresh or r["source_forward_intel_unchanged"]) for r in results["adopters"].values()) else 1)
