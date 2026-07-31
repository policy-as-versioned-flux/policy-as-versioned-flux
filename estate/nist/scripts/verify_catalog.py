#!/usr/bin/env python3
"""Asserts the published nist catalog is genuine, well-formed OSCAL and that
CATALOG_VERSION.json's checksum matches the file on disk. Run directly or via
verify-catalog.sh."""
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
CATALOG_DIR = HERE / "catalog"


def count_controls(controls):
    n = 0
    for ctl in controls:
        n += 1
        n += count_controls(ctl.get("controls", []))
    return n


def main():
    meta = json.loads((CATALOG_DIR / "CATALOG_VERSION.json").read_text())
    catalog_path = CATALOG_DIR / meta["file"]
    raw = catalog_path.read_bytes()

    actual_sha = hashlib.sha256(raw).hexdigest()
    assert actual_sha == meta["sha256"], (
        f"catalog file has drifted from its recorded checksum: "
        f"{actual_sha} != {meta['sha256']}"
    )

    doc = json.loads(raw)
    catalog = doc["catalog"]
    assert "uuid" in catalog and "metadata" in catalog, "not a valid OSCAL catalog document"
    assert catalog["uuid"] == meta["source"]["catalogUuid"], "catalog uuid does not match recorded source"

    groups = catalog.get("groups", [])
    assert len(groups) == meta["controlGroups"], f"expected {meta['controlGroups']} control groups, got {len(groups)}"

    total = sum(count_controls(g.get("controls", [])) for g in groups)
    assert total == meta["controlCount"], f"expected {meta['controlCount']} controls, got {total}"
    assert total > 1000, "suspiciously small for the real 800-53 catalog — did a subset get committed by mistake?"

    # genuine control text is present, not a stub/placeholder
    ac2 = next(c for c in groups[0]["controls"] if c["id"] == "ac-1")
    assert "policy" in ac2["title"].lower() or "procedure" in ac2["title"].lower()

    print(f"OK: {total} controls across {len(groups)} groups, sha256 verified, "
          f"NIST rev {meta['source']['nistMetadataVersion']} (OSCAL {meta['source']['oscalVersion']})")


if __name__ == "__main__":
    main()
