#!/usr/bin/env python3
"""step2_reprice.py — NORTH-STAR §4 step 2, offline: bumping a pinned parent version in an
adopter's own party.yaml — the one edit a merged Renovate PR makes — changes that adopter's
prices[].

Never touches a real repo: the adopter's committed tree is copied into a temp directory (minus
.git), composed once to install a header to compare against, the pin is edited from the pinned
version to the next version present locally, and it is composed again. The two prices[]
documents are diffed. The copy is thrown away; nothing is restored because nothing real moved.

Exit 0 observed true; 3 could not look (no estate, no interpreter, or no adopter pinning a feed
that has a newer version on disk); 1 observed false.
"""
from __future__ import annotations

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

# The gate never passes this. It exists so this step can be smoke-tested against a scratch
# estate (a fixture with the not-yet-published files planted) without touching a real unit.
if "--estate" in sys.argv:
    ESTATE = sys.argv[sys.argv.index("--estate") + 1]

COMPOSITION = os.path.join(ESTATE, "platform", "compose", "composition.py")
# composition.py prices a feed edge through the publisher's own converter; only these two feed
# names have one today (its own `ponytail` note says a third gets wired when one ships).
PRICEABLE = ("penalty-schema", "threat-register")
VDIR = re.compile(r"^v(\d+)$")


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def skip(msg):
    print(f"SKIP: {msg}")
    sys.exit(3)


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def parties():
    return {os.path.basename(os.path.dirname(p)): load_yaml(p)
            for p in sorted(glob.glob(os.path.join(ESTATE, "*", "party.yaml")))}


def published_path(party_doc, name):
    for rec in party_doc.get("publishes") or []:
        if rec.get("name") == name:
            return rec.get("path")
    return None


def candidates(all_parties):
    """EVERY (adopter, edge, pinned, newer) where an adopter pins a priceable feed version and
    the publisher has a newer one on disk. Every one, not the first: a bump whose payload
    prices this adopter identically is not a re-price, and the step has to keep looking rather
    than claim one it did not see."""
    missing, found = [], []
    for adopter, doc in sorted(all_parties.items()):
        if "adopter" not in (doc.get("roles") or []):
            continue
        for edge in doc.get("inherits") or []:
            if edge.get("kind") != "feed" or edge.get("name") not in PRICEABLE:
                continue
            pub = all_parties.get(edge["party"])
            path = published_path(pub, edge["name"]) if pub else None
            if not path:
                missing.append(f"{edge['party']} publishes no {edge['name']} record")
                continue
            root = os.path.join(ESTATE, edge["party"], path)
            versions = sorted(int(m.group(1)) for d in os.listdir(root)
                              if (m := VDIR.match(d)) and os.path.isdir(os.path.join(root, d))) \
                if os.path.isdir(root) else []
            pinned = VDIR.match(str(edge.get("version", "")))
            if not pinned:
                missing.append(f"{adopter} pins {edge['name']} at {edge.get('version')!r}, "
                               f"not a vN major")
                continue
            newer = [v for v in versions if v > int(pinned.group(1))]
            if not newer:
                missing.append(f"{edge['party']}/{path} has no version newer than "
                               f"{edge['version']} for {adopter} to bump to")
                continue
            found.append((adopter, edge, edge["version"], f"v{min(newer)}"))
    return found, missing


def compose(adopter_dir, out_dir, label):
    r = subprocess.run([sys.executable, COMPOSITION, "compose", adopter_dir,
                        "--estate-clone", ESTATE, "--out", out_dir],
                       capture_output=True, text=True)
    try:
        doc = json.loads(r.stdout)
    except ValueError:
        why = " | ".join((r.stderr or r.stdout).strip().splitlines()[-3:]) or "no output"
        fail(f"composition could not run for {label}: {why}")
    if r.returncode != 0:
        why = "; ".join(json.dumps(x, sort_keys=True) for x in doc.get("refusals", [])[:3])
        fail(f"composition refused {label} ({doc.get('outcome')}): "
             f"{why or 'no refusal named'}")
    return doc


def entry_for(prices, name):
    return next((p for p in prices if p.get("name") == name), None)


def main():
    if not os.path.isdir(ESTATE):
        skip(f"{ESTATE} absent — run ./clone-estate.sh first")
    if not os.path.exists(COMPOSITION):
        skip(f"{COMPOSITION} absent — nothing to compose with")
    all_parties = parties()
    found, missing = candidates(parties())
    if not found:
        skip("no adopter pins a priceable feed with a newer version present locally: "
             + "; ".join(missing or ["no adopter declares a feed edge at all"]))

    flat = []
    for adopter, edge, pinned, newer in found:
        result = try_bump(adopter, edge, pinned, newer)
        if result is not None:
            return result
        flat.append(f"{adopter}/{edge['name']} {pinned}->{newer}")
    skip("no pin bump available on disk moves any adopter's price, so no re-price could be "
         "observed: " + "; ".join(flat))


def try_bump(adopter, edge, pinned, newer):
    """Compose the adopter twice, once either side of the bump. Returns 0 when the NUMBER
    moved (the re-price this step exists to observe), None when only the recorded pin did."""
    name = edge["name"]
    print(f"    {adopter} pins {edge['party']}/{name} at {pinned}; {newer} is on disk")
    with tempfile.TemporaryDirectory() as tmp:
        # The whole committed tree, minus git and scratch: the party artefact's own check()
        # reads workflows and pin files, not just party.yaml.
        work = os.path.join(tmp, adopter)
        shutil.copytree(os.path.join(ESTATE, adopter), work,
                        ignore=shutil.ignore_patterns(".git", ".work", "__pycache__"))

        before = compose(work, work, f"{adopter} at {pinned}")["prices"]

        doc = load_yaml(os.path.join(work, "party.yaml"))
        for e in doc["inherits"]:
            if e.get("kind") == "feed" and e.get("name") == name:
                e["version"] = newer
        with open(os.path.join(work, "party.yaml"), "w") as fh:
            yaml.safe_dump(doc, fh, sort_keys=False)

        after = compose(work, os.path.join(tmp, "after"), f"{adopter} at {newer}")["prices"]

    b, a = entry_for(before, name), entry_for(after, name)
    if a is None:
        fail(f"{adopter} prices[] has no {name} entry after the bump")
    if a.get("old_version") != pinned or a.get("new_version") != newer:
        fail(f"{adopter}'s {name} entry records {a.get('old_version')} -> "
             f"{a.get('new_version')}, not the {pinned} -> {newer} bump that was made")
    old_p, new_p = a.get("old_price"), a.get("new_price")
    print(f"    {name} {pinned} -> {newer}: {old_p:,.2f} -> {new_p:,.2f} "
          f"(tier {a.get('old_tier')} -> {a.get('proposed_tier')}, "
          f"changed={a.get('changed')})")
    print(f"    before: {json.dumps(b, sort_keys=True)}")
    print(f"    after:  {json.dumps(a, sort_keys=True)}")
    # The step is named "re-prices". `before != after` proves nothing: the entry always
    # records the new version string, so the DOCUMENT moves on every bump whether or not
    # any number did. The number is the assertion; a composition that ignored the payload
    # and echoed the pin would have passed the old check.
    if old_p == new_p:
        print(f"    note: {newer}'s payload prices {adopter} exactly as {pinned} did; what "
              f"moved is the recorded pin, not the number — not a re-price, looking on")
        return None
    print(f"PASS: a merged pin bump ({name} {pinned} -> {newer}) re-prices {adopter}'s "
          f"prices[] through composition ({old_p:,.2f} -> {new_p:,.2f}), offline, with no "
          f"repo touched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
