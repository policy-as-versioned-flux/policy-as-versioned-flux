#!/usr/bin/env python3
"""Export exact published commits; preserve the earlier preparation snapshots."""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent / "complete"
INPUT = ROOT / ".scratch/ecosystem/research/resume-2026-10-04/publication-delivered-source-manifest.json"
BASELINES = ROOT / ".scratch/ecosystem/patches/resume-2026-10-03/complete/manifest.json"


def git(repo: Path, *args: str) -> bytes:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, check=True).stdout


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', type=Path, default=INPUT)
    parser.add_argument('--output', type=Path, default=OUTPUT)
    options = parser.parse_args()
    options.manifest = options.manifest.resolve()
    options.output = options.output.resolve()
    source = json.loads(options.manifest.read_text())
    baselines = {row["repository"]: row["base"] for row in json.loads(BASELINES.read_text())["repositories"]}
    assert set(source["repositories"]) == set(baselines), "all nine estate repositories must be explicit"
    options.output.mkdir(parents=True, exist_ok=True)
    records = []
    for name, row in source["repositories"].items():
        repo = Path(row["directory"])
        target = row["commit"]
        assert git(repo, "rev-parse", target + "^{commit}").decode().strip() == target
        git(repo, "merge-base", "--is-ancestor", target, "origin/main")
        original_status = git(repo, "status", "--porcelain")
        base = baselines[name]
        patch = git(repo, "diff", "--binary", "--full-index", base, target)
        paths = git(repo, "diff", "--name-status", base, target).decode().splitlines()
        destination = options.output / (name + ".patch")
        destination.write_bytes(patch)
        with tempfile.TemporaryDirectory(prefix="pavf-published-export-") as temporary:
            clone = Path(temporary) / "repository"
            subprocess.run(["git", "clone", "--quiet", "--no-checkout", "--no-hardlinks", str(repo), str(clone)], check=True)
            git(clone, "checkout", "--quiet", "--detach", target)
            git(clone, "apply", "--check", "--reverse", str(destination))
        assert git(repo, "status", "--porcelain") == original_status, "export changed the source repository"
        records.append({
            "repository": name, "base": base, "published_commit": target,
            "published_tree": git(repo, "rev-parse", target + "^{tree}").decode().strip(),
            "remote": git(repo, "remote", "get-url", "origin").decode().strip(),
            "reachable_from_origin_main": True, "reverse_apply_check": "PASS",
            "patch": destination.name, "bytes": len(patch),
            "sha256": hashlib.sha256(patch).hexdigest(), "paths": paths,
        })
        print(f"{name}: {target[:12]}, {len(paths)} paths, reverse apply PASS")
    (options.output / "manifest.json").write_text(json.dumps({
        "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "Exact published source commits; live observation grades remain in their separately signed lanes",
        "publication_manifest_sha256": hashlib.sha256(options.manifest.read_bytes()).hexdigest(),
        "repositories": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
