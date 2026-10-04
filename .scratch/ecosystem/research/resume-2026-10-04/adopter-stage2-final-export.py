"""Export exact local candidate heads, patches and honest immutable source proof."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys

import yaml

day = Path(__file__).resolve().parent
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
snapshot = json.loads((day / "adopter-stage2-source-snapshot.json").read_text())
rows = {}


def git(repo: Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(repo), *args], text=True).strip()


def digest(path: Path) -> str | None:
    return hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None


for org, loc in locator["adopters"].items():
    repo = Path(loc["dir"])
    estate = Path(loc["estate"])
    head = git(repo, "rev-parse", "HEAD")
    base = git(repo, "rev-parse", "origin/main")
    status = git(repo, "status", "--porcelain")
    assert not status, (org, status)
    assert git(repo, "merge-base", base, head) == base
    signature = git(repo, "log", "-1", "--format=%G?")
    assert signature == "G", (org, signature)
    signature_proc = subprocess.run(["git", "-C", str(repo), "verify-commit", head],
                                    capture_output=True, text=True)
    assert signature_proc.returncode == 0, signature_proc.stderr
    signature_log = day / f"{org}-stage2-final-source-ssh-signature.log"
    signature_log.write_text(signature_proc.stdout + signature_proc.stderr)
    patch = day / f"{org}-stage2-final-source-A.patch"
    patch.write_bytes(subprocess.check_output([
        "git", "-C", str(repo), "diff", "--binary", "--full-index", base, head]))
    subprocess.run(["git", "-C", str(repo), "apply", "--reverse", "--check", str(patch)],
                   check=True, capture_output=True)
    subprocess.run(["git", "-C", str(repo), "diff", "--check", base, head],
                   check=True, capture_output=True)
    source = Path(loc["source"])
    changed_original = [name for name, expected in snapshot["adopters"][org]["desired_hashes"].items()
                        if digest(source / name) != expected]
    assert not changed_original, (org, changed_original)
    h = yaml.safe_load((repo / "composed/HEADER.yaml").read_text())
    feed_records = []
    for entry in h["vendored-feeds"]:
        if entry.get("party") != "feeds":
            continue
        name, version = entry["name"], entry["version"]
        provenance = repo / "composed/feeds/feeds" / name / version / "PROVENANCE.json"
        prov = json.loads(provenance.read_text())
        assert entry["files"] == prov["files"]
        assert entry["sha"] == prov["sha"]
        observation = prov["publisher_observation"]
        tag = observation["pin_signature"]["tag"]
        feed_repo = estate / "feeds"
        feed_records.append({
            "name": name, "version": version, "payload_last_edit_sha": entry["sha"],
            "provenance_file": str(provenance.relative_to(repo)),
            "provenance_sha256": digest(provenance),
            "header_payload_and_converter_digests_match_provenance": True,
            "provenance_blob_in_signed_candidate_tree": git(repo, "rev-parse", f"HEAD:{provenance.relative_to(repo)}"),
            "publisher_observation": observation,
            "named_tag": tag,
            "tag_object": git(feed_repo, "rev-parse", tag) if tag else None,
            "peeled_tag_commit": git(feed_repo, "rev-parse", f"{tag}^{{}}") if tag else None,
            "checkout_commit": git(feed_repo, "rev-parse", "HEAD"),
        })
    rows[org] = {
        "directory": str(repo), "branch": git(repo, "branch", "--show-current"),
        "base": base, "head": head, "tree": git(repo, "rev-parse", "HEAD^{tree}"),
        "ssh_signature": signature, "signature_verification_exit": signature_proc.returncode,
        "signature_log": str(signature_log), "clean": True,
        "stat": git(repo, "diff", "--shortstat", base, head),
        "changed_paths": git(repo, "diff", "--name-status", base, head).splitlines(),
        "patch": str(patch), "patch_sha256": digest(patch), "reverse_apply_check": "PASS",
        "whitespace_check": "PASS", "original_source_untouched": True,
        "original_changed_paths": changed_original,
        "hub_pin": yaml.safe_load((repo / "twin/PIN.yaml").read_text()),
        "source_publication_ready": False,
        "source_local_preparation_complete": True,
        "publication_hold": "Independent exact-head review and root-coordinated ordinary source PR/cut; no adopter activation yet.",
        "critical_file_sha256": {name: digest(repo / name) for name in ["verify-twin-overlay.sh", "twin/VENDORED.md", "twin/PIN.yaml", "twin/emit-forward-intel.py", "twin/forward-intel/payload.schema.json", ".github/workflows/twin-sweep.yml", "gitops/flux-system/gotk-sync-fx.yaml"]},
        "validation_receipts": ["adopter-stage2-final-producers.json", "adopter-stage2-final-checks.json", "adopter-stage2-final-compose.json", "adopter-stage2-final-relocated-replay.json", "adopter-stage2-final-policy7-corpus.json"],
        "feed_provenance": feed_records,
    }

out = day / "adopter-stage2-final-source-A-candidates.json"
out.write_text(json.dumps(rows, indent=2, default=str) + "\n")
print(json.dumps({org: {k: row[k] for k in ["base", "head", "tree", "stat", "ssh_signature", "clean", "patch_sha256", "publication_hold"]} for org, row in rows.items()}, indent=2))
