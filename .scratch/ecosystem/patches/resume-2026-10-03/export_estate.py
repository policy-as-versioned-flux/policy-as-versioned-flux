#!/usr/bin/env python3
"""Preserve the resumed estate changes without changing any repository's real index."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[4]
OUTPUT = Path(__file__).resolve().parent / "complete"
REPOSITORIES = {
    **{name: ROOT / ".estate-clone" / name
       for name in ("platform", "feeds", "driftwood", "tuppence", "ludlow")},
    **{"app-" + name: ROOT / ".estate-apps" / name
       for name in ("ledger", "storefront", "api", "reports")},
}


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    records = []
    for name, repo in REPOSITORIES.items():
        def git(*args: str, env: dict[str, str] | None = None) -> bytes:
            return subprocess.run(["git", "-C", str(repo), *args], env=env,
                                  capture_output=True, check=True).stdout

        base = git("rev-parse", "HEAD").decode().strip()
        with tempfile.TemporaryDirectory(prefix="pavf-export-index-") as temporary:
            env = {**os.environ, "GIT_INDEX_FILE": str(Path(temporary) / "index")}
            git("read-tree", "HEAD", env=env)
            git("add", "--all", env=env)
            patch = git("diff", "--binary", "--full-index", "--cached", "HEAD", env=env)
            paths = git("diff", "--cached", "--name-status", "HEAD", env=env).decode().splitlines()
        target = OUTPUT / (name + ".patch")
        target.write_bytes(patch)
        records.append({"repository": name, "base": base, "patch": target.name,
                        "bytes": len(patch), "sha256": hashlib.sha256(patch).hexdigest(),
                        "paths": paths})
        print(f"Preserved {name}: {len(paths)} paths, {len(patch)} bytes, base {base[:12]}")
    (OUTPUT / "manifest.json").write_text(json.dumps({
        "exported_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "scope": "local implementation snapshots; not signed releases or rollout evidence",
        "repositories": records,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
