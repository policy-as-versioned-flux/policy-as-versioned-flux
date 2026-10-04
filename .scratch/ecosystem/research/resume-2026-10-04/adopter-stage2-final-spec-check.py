"""Read-only source audit; write only the reviewer receipt next to this script."""
import copy
import hashlib
import json
import subprocess
from pathlib import Path

import yaml

OUT = Path(__file__).resolve().parent
PACKET = OUT / "adopter-stage2-final-source-A-candidates.json"
EXPECTED = {
    "driftwood": "eac40457ffb4b593dfbe17015c525db3f0914f5f",
    "tuppence": "d1dbe766e09bb8112efa609836af0aa95cbe0ee4",
    "ludlow": "926d6b38384fd9b532305c668313920ff943653a",
}
TOOLS = "703eff6aee959843c4160aa54fd03413f62858cc"
HUB = "5bc47331a536476f3580542be794908f5053f816"
FX = "8c84a66951ce89834f33e008380b2c47f054b7c0"
FX_OBJECT = "f6edadce94b98a01479a517a1babda92ce8b2243"
EXTENSIONS = {
    "rests_on_grade": {"type": "integer", "enum": [1, 2, 3]},
    "valuation": {
        "type": "object",
        "required": ["amount", "currency", "native_amount", "native_currency", "party_fact", "fx"],
        "properties": {
            "amount": {"type": "number"}, "currency": {"type": "string"},
            "native_amount": {"type": "number"}, "native_currency": {"type": "string"},
            "party_fact": {"type": "string"}, "fx": {"type": ["object", "null"]},
        },
        "additionalProperties": False,
    },
}


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args], stderr=subprocess.STDOUT)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def preserves(owned, canonical):
    base = dict(owned)
    base["properties"] = {k: v for k, v in owned["properties"].items() if k not in EXTENSIONS}
    return (base == canonical
            and all(owned["properties"].get(k) == v for k, v in EXTENSIONS.items())
            and not (set(EXTENSIONS) & set(owned["required"])))


packet = json.loads(PACKET.read_text())
producers = json.loads((OUT / "adopter-stage2-final-producers.json").read_text())
checks = json.loads((OUT / "adopter-stage2-final-checks.json").read_text())
replay = json.loads((OUT / "adopter-stage2-final-postcommit-byte-replay.json").read_text())
result = {"scope": "independent exact committed source inspection; no external actions or source edits",
          "packet_sha256": digest(PACKET.read_bytes()), "adopters": {}}
for name, expected in EXPECTED.items():
    p = packet[name]
    repo = Path(p["directory"])
    assert p["head"] == expected == git(repo, "rev-parse", "HEAD").decode().strip()
    assert p["tree"] == git(repo, "rev-parse", "HEAD^{tree}").decode().strip()
    assert not git(repo, "status", "--porcelain").strip()
    signature = git(repo, "verify-commit", expected).decode().strip()
    actual_hashes = {}
    for path, expected_hash in p["critical_file_sha256"].items():
        data = git(repo, "show", f"{expected}:{path}")
        assert data == (repo / path).read_bytes()
        assert digest(data) == expected_hash
        actual_hashes[path] = digest(data)
    assert digest(Path(p["patch"]).read_bytes()) == p["patch_sha256"]
    baseline_apps = set(git(repo, "ls-tree", "-r", "--name-only", p["base"], "gitops/apps").decode().splitlines())
    assert all((repo / path).is_file() for path in baseline_apps)
    platform = repo.parent / "platform"
    canonical_bytes = (platform / "feeds/forward-intel.payload.schema.json").read_bytes()
    assert canonical_bytes == git(platform, "show", f"{TOOLS}:feeds/forward-intel.payload.schema.json")
    canonical = json.loads(canonical_bytes)
    owned = json.loads((repo / "twin/forward-intel/payload.schema.json").read_text())
    assert preserves(owned, canonical)
    mutations = []
    for label in ["base_required", "unknown_extension", "required_optional_metadata", "grade_outside_ladder"]:
        bad = copy.deepcopy(owned)
        if label == "base_required":
            bad["required"] = []
        elif label == "unknown_extension":
            bad["properties"]["undeclared"] = {"type": "number"}
        elif label == "required_optional_metadata":
            bad["required"].append("valuation")
        else:
            bad["properties"]["rests_on_grade"]["enum"].append(4)
        assert not preserves(bad, canonical)
        mutations.append(label)
    pin = yaml.safe_load((repo / "twin/PIN.yaml").read_text())
    assert pin["hub_commit"] == HUB and pin["tag_cut"] is False
    party = yaml.safe_load((repo / "party.yaml").read_text())
    apps_docs = list(yaml.safe_load_all((repo / "gitops/flux-system/gotk-sync.yaml").read_text()))
    app_source = next(d for d in apps_docs if d["kind"] == "GitRepository")
    assert app_source["spec"]["ref"] == {"tag": "v3.0.1", "commit": p["base"]}
    assert next(d for d in apps_docs if d["kind"] == "Kustomization")["spec"]["path"] == "./gitops/apps"
    comp_docs = list(yaml.safe_load_all((repo / "gitops/composed/composed-set.yaml").read_text()))
    comp_source = next(d for d in comp_docs if d["kind"] == "GitRepository")
    assert comp_source["spec"]["ref"]["tag"] == "v3.0.0"
    producer = producers["adopters"][name]
    for generated in producer["generated"]:
        assert digest(git(repo, "show", f"{expected}:{generated['path']}")) == generated["sha256"]
    assert producer["rests_on_grade"] == 3 and producer["borrowed_frequency"]["version"] == "4"
    check = checks[name]["overlay_selfcheck"]
    assert check["exit"] == 0 and "PASS: owned payload schema preserves" in check["stdout"]
    assert "could-not-look" in check["stdout"] and "0 could-not-look" in check["stdout"]
    assert checks[name]["existing_tests_exit"] == 0
    assert replay[name]["exit"] == 0 and replay[name]["source_composed_unchanged"] is True
    if name == "ludlow":
        fx_pin = yaml.safe_load((repo / "gitops/flux-system/gotk-sync-fx.yaml").read_text())["spec"]["ref"]
        assert fx_pin == {"tag": "fx/v2.0.0", "commit": FX}
        feeds = repo.parent / "feeds"
        assert git(feeds, "rev-parse", "fx/v2.0.0").decode().strip() == FX_OBJECT
        assert git(feeds, "rev-parse", "fx/v2.0.0^{commit}").decode().strip() == FX
        assert git(feeds, "rev-parse", "HEAD").decode().strip() == producers["generic_feeds_head"]
        valuation = producer["valuation"]
        assert valuation["native_amount"] == 8475000000.0 and valuation["native_currency"] == "USD"
        assert valuation["fx"]["period"] == "2025-12" and valuation["fx"]["valuation_date"] == "2025-12-31"
        assert valuation["fx"]["from_rate"] == 1.3126 and valuation["fx"]["version"] == "2.0.0"
        assert abs(valuation["amount"] - 8475000000 / 1.3126) < 0.000001
        workflow = yaml.safe_load((repo / ".github/workflows/twin-sweep.yml").read_text())
        assert workflow["permissions"] == {"contents": "read"}
        observer = workflow["jobs"]["twin"]
        assert observer["permissions"] == {"contents": "read"}
        assert all(s["with"]["persist-credentials"] is False for s in observer["steps"] if s.get("uses", "").startswith("actions/checkout@"))
        assert workflow["jobs"]["write"]["if"] == "needs.twin.outputs.agent_rung != 'isolated'"
    result["adopters"][name] = {
        "head": expected, "tree": p["tree"], "normal_signature": signature, "clean": True,
        "critical_file_sha256": actual_hashes, "patch_sha256": p["patch_sha256"],
        "retained_upstream_apps_paths": len(baseline_apps),
        "canonical_sha256": digest(canonical_bytes), "typed_optional_schema_extensions": "PASS",
        "schema_negative_mutations_refused": mutations,
        "served_apps_ref_retained": app_source["spec"]["ref"],
        "composed_ref_retained": comp_source["spec"]["ref"],
        "clean_producer_payloads_match_committed_tree": True,
        "canonical_present_helper_and_postcommit_byte_replay": "PASS",
    }
dest = OUT / "adopter-stage2-final-spec-checks.json"
dest.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps({n: {"head": v["head"], "tree": v["tree"], "result": "PASS"} for n, v in result["adopters"].items()}, indent=2))
