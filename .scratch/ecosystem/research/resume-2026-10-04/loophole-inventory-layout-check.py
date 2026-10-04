"""Run the real loophole suite against isolated old/new adopter source layouts."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

import pytest
import yaml

ARTIFACTS = Path(__file__).resolve().parent
HUB = ARTIFACTS.parents[3]
parser = argparse.ArgumentParser()
parser.add_argument("layout", choices=("old", "new"))
parser.add_argument("--label", required=True)
args = parser.parse_args()
locator = json.loads((ARTIFACTS / "adopter-stage2-isolated.json").read_text())
temporary = Path(tempfile.mkdtemp(prefix="pavf-loophole-inventory-"))
estate = temporary / "estate"
estate.mkdir()
parent_estate = Path(locator["adopters"]["tuppence"]["estate"])
for name in ("platform", "nist", "ico", "feeds", "insurer"):
    (estate / name).symlink_to(parent_estate / name, target_is_directory=True)
platform_head = subprocess.check_output(
    ["git", "-C", str(estate / "platform"), "rev-parse", "HEAD"], text=True
).strip()
platform_release = subprocess.check_output(
    ["git", "-C", str(estate / "platform"), "rev-parse", "v5.0.0^{commit}"], text=True
).strip()
assert platform_head == platform_release == "703eff6aee959843c4160aa54fd03413f62858cc"
source_refs = {}
for name, declaration in locator["adopters"].items():
    source = Path(declaration["dir"])
    ref = "v3.0.1" if args.layout == "old" else "HEAD"
    destination = estate / name
    destination.mkdir()
    archive = subprocess.check_output(["git", "-C", str(source), "archive", ref])
    subprocess.run(["tar", "-xf", "-", "-C", str(destination)], input=archive, check=True)
    source_refs[name] = subprocess.check_output(
        ["git", "-C", str(source), "rev-parse", ref + "^{commit}"], text=True
    ).strip()
    party = yaml.safe_load((destination / "party.yaml").read_text())
    subscribed = any(edge.get("name") == "cve" for edge in party["inherits"])
    has_inventory = (destination / "inventory").is_dir()
    if args.layout == "old":
        assert not has_inventory
        if name == "tuppence":
            # Existing CVEv2 subscription predates the new inventory contract.
            assert any(edge.get("name") == "cve" and edge["version"] == "v2" for edge in party["inherits"])
    else:
        assert subscribed and has_inventory


rebound = []


class IsolatedEstate:
    def pytest_collection_modifyitems(self, items):
        for item in items:
            if Path(item.module.__file__).resolve() == HUB / "tests/test_loophole_adr_0026.py":
                item.module.ESTATE = estate
                item.module.PLATFORM = estate / "platform"
                rebound.append(item.nodeid)


status = pytest.main(
    [str(HUB / "tests/test_loophole_adr_0026.py"), "-q", "-n", "0", "-p", "no:cacheprovider", "--basetemp", str(temporary / "pytest")],
    plugins=[IsolatedEstate()],
)
(ARTIFACTS / (args.label + ".json")).write_text(json.dumps({
    "layout": args.layout, "estate": str(estate), "source_refs": source_refs,
    "platform_tools": {"tag": "v5.0.0", "commit": platform_head},
    "pytest_exit": int(status), "source_mutations": False, "isolated_cases": len(rebound),
}, indent=2) + "\n")
assert len(rebound) == 27, "the estate override must reach every case including the missing-inventory regression"
raise SystemExit(status)
