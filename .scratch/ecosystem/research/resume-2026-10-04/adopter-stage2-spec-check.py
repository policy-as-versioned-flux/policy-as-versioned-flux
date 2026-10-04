"""Local read-only independent Stage2 source checks; never a publication approval."""
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import yaml

ROOT = Path(__file__).resolve().parents[4]
ARTIFACTS = Path(__file__).parent
locator = json.loads((ARTIFACTS / "adopter-stage2-isolated.json").read_text())
spec = importlib.util.spec_from_file_location(
    "stage2_spec_inventory", ROOT / ".estate-clone/platform/wargamer/inventory.py"
)
inventory_module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = inventory_module
spec.loader.exec_module(inventory_module)
result = {
    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "scope": "Independent source/pre-pin Spec review; no final composition approval",
    "adopters": {},
}
for name, declaration in locator["adopters"].items():
    adopter = Path(declaration["dir"])

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=adopter, text=True).strip()

    provenance = json.loads((adopter / "inventory/PROVENANCE.json").read_text())
    inventory = json.loads((adopter / "inventory/images.json").read_text())
    inventory_module.validate(adopter, inventory)
    inventory_hash = hashlib.sha256((adopter / "inventory/images.json").read_bytes()).hexdigest()
    assert inventory_hash == provenance["inventory_sha256"]
    pin = provenance["apps_source"]
    assert git("rev-parse", pin["tag"] + "^{commit}") == pin["commit"]
    assert git("rev-parse", "refs/tags/" + pin["tag"]) == pin["tag_object"]
    assert git("cat-file", "-t", pin["tag_object"]) == "tag"
    rows = []
    for image in provenance["images"]:
        raw = ROOT / image["raw_report"]
        data = raw.read_bytes()
        assert hashlib.sha256(data).hexdigest() == image["raw_report_sha256"]
        report = json.loads(data)
        assert report["ArtifactName"] == image["requested_image"] == image["reported_artifact"]
        assert image["requested_image"].split("@")[-1] in [
            digest.split("@")[-1] for digest in report["Metadata"]["RepoDigests"]
        ]
        rows.append(inventory_module.trim(image["requested_image"], report, provenance["scanner"]["version"]))
    assert sorted(rows, key=lambda row: row["image"]) == sorted(
        inventory["images"], key=lambda row: row["image"]
    )
    tracked = git("ls-tree", "-r", "--name-only", "HEAD").splitlines()
    retained = [
        path for path in tracked
        if path.startswith(("apps/", "gitops/apps/"))
        or path in ("drift/samples.jsonl", "observations/twin-sweep.jsonl", "deploy/pod.yaml")
    ]
    for path in retained:
        assert (adopter / path).read_bytes() == subprocess.check_output(
            ["git", "show", "HEAD:" + path], cwd=adopter
        ), path
    checks = {}
    for instrument in ("five-facts.py", "served_apps.py", "oscal_lane.py"):
        completed = subprocess.run(
            [sys.executable, str(adopter / "drift" / instrument), "selfcheck"],
            text=True, capture_output=True, timeout=40,
            env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
        )
        checks[instrument] = {
            "rc": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr
        }
        assert completed.returncode == 0, (name, instrument, completed.stderr)
    party = yaml.safe_load((adopter / "party.yaml").read_text())
    assert party["overlay"]["restate"] == []
    assert any(
        parent.get("party") == "feeds" and parent.get("name") == "cve" and parent["version"] == "v3"
        for parent in party["inherits"]
    )
    result["adopters"][name] = {
        "baseline": git("rev-parse", "HEAD"),
        "apps_tag": pin["tag"], "apps_commit": pin["commit"], "apps_tag_object": pin["tag_object"],
        "images": inventory_module.served_images(adopter),
        "primary_raw_trim_matches": True, "inventory_sha256": inventory_hash,
        "upstream_apps_observations_unchanged": True, "retained_upstream_paths": len(retained),
        "declared_workload_restatement_bindings": 0,
        "engine": yaml.safe_load((adopter / "gitops/engine/kyverno.yaml").read_text()),
        "selfchecks": checks,
        "reviewed_source_sha256": {
            path: hashlib.sha256((adopter / path).read_bytes()).hexdigest()
            for path in (
                "party.yaml", "gitops/flux-system/gotk-sync.yaml", "drift/served_apps.py",
                "drift/oscal_lane.py", "drift/window.yaml",
            )
        },
    }
    (ARTIFACTS / "adopter-stage2-spec-pre-pin-checks.json").write_text(json.dumps(result, indent=2) + "\n")
    print(name, "immutable graph, primary trim, retained upstream and selfchecks PASS", flush=True)
