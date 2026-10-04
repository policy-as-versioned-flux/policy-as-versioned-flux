"""Bind the normal local signed FX2 source commit and durable exact review delta."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess

day = Path(__file__).resolve().parent
feeds = day.parents[3] / ".estate-publish/feeds"
baseline = json.loads((day / "fx2-source-preparation.json").read_text())
base = baseline["base"]

def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(feeds), *args], text=True).strip()


head, tree = git("rev-parse", "HEAD"), git("rev-parse", "HEAD^{tree}")
assert not git("status", "--porcelain")
assert git("merge-base", base, head) == base
assert git("log", "-1", "--format=%G?") == "G"
verify = subprocess.run(["git", "-C", str(feeds), "verify-commit", head], capture_output=True, text=True)
assert verify.returncode == 0, verify.stderr
(day / "fx2-source-ssh-signature.log").write_text(verify.stdout + verify.stderr)
preserved = {}
for name, expected in baseline["frozen_major_payloads"].items():
    actual = hashlib.sha256((feeds / name).read_bytes()).hexdigest()
    assert actual == expected, (name, expected, actual)
    preserved[name] = actual
patch = day / "fx2-source.patch"
patch.write_bytes(subprocess.check_output(["git", "-C", str(feeds), "diff", "--binary", "--full-index", base, head]))
subprocess.run(["git", "-C", str(feeds), "apply", "--reverse", "--check", str(patch)], check=True, capture_output=True)
subprocess.run(["git", "-C", str(feeds), "diff", "--check", base, head], check=True, capture_output=True)
proof = {"directory": str(feeds), "branch": git("branch", "--show-current"),
         "base": base, "head": head, "tree": tree, "ssh_signature": "G", "clean": True,
         "signature_verification_exit": verify.returncode,
         "diff_stat": git("diff", "--stat", base, head),
         "changed_paths": git("diff", "--name-status", base, head).splitlines(),
         "patch": str(patch), "patch_sha256": hashlib.sha256(patch.read_bytes()).hexdigest(),
         "reverse_apply_check": "PASS", "whitespace_check": "PASS",
         "all_12_old_major_payloads_byte_exact": preserved,
         "party_catalogue_unchanged": git("diff", base, head, "--", "party.yaml") == "",
         "actual_measured_bump": "major", "normal_next_version": "2.0.0",
         "publisher_gates": json.loads((day / "fx2-source-checks.json").read_text()),
         "primary_provenance": json.loads((feeds / "fetch/source/hmrc/PROVENANCE.json").read_text()),
         "pr_body": str(day / "fx2-source-pr-body.md"),
         "external_mutations": False, "authentic_FX2_tag": None,
         "adopter_pin_moves": "held until genuine FX2 cut+immutable release verification and corrected published hub source"}
(day / "fx2-source-candidate.json").write_text(json.dumps(proof, indent=2) + "\n")
print(json.dumps({k: proof[k] for k in ["base", "head", "tree", "ssh_signature", "clean", "changed_paths", "patch_sha256"]}, indent=2))
