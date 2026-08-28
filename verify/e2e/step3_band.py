#!/usr/bin/env python3
"""step3_band.py — NORTH-STAR §4 step 3, the python half, offline: a priced residual that
crosses the adopter's OWN signed appetite band selects a different tier, and the proposer would
open a pull request editing the tier declaration.

Nothing is opened. `tier_pr.py run --dry-run` returns before it ever calls git or gh, and it is
run against a throwaway copy of the adopter's workload manifest in a temp directory that is not
a git repository at all — so a real push or a real `gh` call could not succeed even if the
dry-run flag were ignored.

The band is read from the adopter's own party.yaml (appetite.tolerance), never from a platform
fixture (ADR-0021). A party with no appetite is a MISSING INSTRUMENT and refuses (ADR-0020).
The selection is made BY the adopter's own published selection-policy package -- the version in
the PASS line is the one that picked, not a string read out of a file beside it -- with
platform/graded/cage.py as the cross-check the two must agree on (ADR-0021).

Exit 0 observed true; 3 could not look; 1 observed false.
"""
from __future__ import annotations

import copy
import glob
import importlib.util
import json
import os
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

PLATFORM = os.path.join(ESTATE, "platform")
TIER_PR = os.path.join(PLATFORM, "wargamer", "tier_pr.py")
TIER_LABEL = "posture.acme.io/tier"


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def skip(msg):
    print(f"SKIP: {msg}")
    sys.exit(3)


def fail(msg):
    print(f"FAIL: {msg}")
    sys.exit(1)


def adopters():
    for p in sorted(glob.glob(os.path.join(ESTATE, "*", "party.yaml"))):
        doc = load_yaml(p)
        if "adopter" in (doc.get("roles") or []):
            yield os.path.basename(os.path.dirname(p)), doc


def main():
    if not os.path.isdir(ESTATE):
        skip(f"{ESTATE} absent — run ./clone-estate.sh first")
    if not os.path.exists(TIER_PR):
        skip(f"{TIER_PR} absent — no proposer to run")

    chosen = None
    for name, doc in adopters():
        pkg = os.path.join(ESTATE, name, "selection-policy", "selection_policy.py")
        version_file = os.path.join(ESTATE, name, "selection-policy", "VERSION")
        if os.path.exists(pkg) and os.path.exists(version_file):
            chosen = (name, doc, version_file, pkg)
            break
    if chosen is None:
        skip("no adopter publishes a selection-policy package with a VERSION yet — the "
             "versioned package ticket 25 publishes in driftwood is what MAKES the selection")
    org, party, version_file, pkg = chosen
    with open(version_file) as fh:
        declared = fh.read().strip()
    # The package that will pick, imported from the adopter's own repo. A VERSION file that
    # disagrees with the package beside it means the attribution cannot be trusted either way.
    try:
        spec = importlib.util.spec_from_file_location(f"_selpol_{org}", pkg)
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
    except Exception as exc:                                    # noqa: BLE001
        fail(f"{org}'s own selection-policy package does not import, so no versioned rule "
             f"could have picked its tier: {exc!r}")
    policy_version = getattr(policy, "VERSION", None)
    if policy_version != declared:
        fail(f"{org}/selection-policy/VERSION says {declared!r} but the package beside it is "
             f"{policy_version!r} — a tier cannot be attributed to either")

    tol = ((party.get("appetite") or {}).get("tolerance") or {})
    if not isinstance(tol.get("amount"), (int, float)):
        fail(f"{org}/party.yaml declares no appetite.tolerance — a party with no appetite is a "
             f"MISSING INSTRUMENT and refuses (ADR-0020)")
    band, ccy = float(tol["amount"]), tol.get("currency")

    # The estate's engine prices the caged residuals; the ADOPTER's own package picks from
    # them. Both run over the same numbers and must agree -- a proposal that names a policy
    # version which did not in fact pick is the unfalsifiable claim this estate refuses.
    sys.path.insert(0, os.path.join(PLATFORM, "graded"))
    try:
        import cage  # noqa: E402
    except Exception as exc:                                    # noqa: BLE001
        skip(f"cannot import {PLATFORM}/graded/cage.py: {exc!r}")
    floor = (party.get("overlay") or {}).get("floor")

    def pick(ale):
        """The tier the adopter's OWN versioned package selects for this uncaged ALE."""
        residuals = {t: {"amount": cage.caged_residual(ale, t), "currency": ccy}
                     for t in cage.ORDER}
        try:
            chose = policy.select(residuals, {"amount": band, "currency": ccy}, floor)
        except Exception as exc:                                # noqa: BLE001
            fail(f"{org}'s own selection-policy package refused to pick at an uncaged residual "
                 f"of {ale:,.2f} {ccy}: {exc}")
        theirs, ours = chose["tier"], cage.select_tier(ale, band, floor)
        if theirs != ours:
            fail(f"at an uncaged residual of {ale:,.2f} {ccy}, {org}'s own selection-policy "
                 f"package picks {theirs!r} and platform/graded/cage.py picks {ours!r} — a "
                 f"proposal could name a version that did not pick (ADR-0021)")
        return theirs

    under = band * 0.5
    tier_under = pick(under)
    over, tier_over = under, tier_under
    for _ in range(4000):
        over *= 1.02
        tier_over = pick(over)
        if tier_over != tier_under:
            break
    if tier_over == tier_under:
        fail(f"no residual between {under:,.0f} and {over:,.0f} {ccy} changes {org}'s tier off "
             f"{tier_under} against its own band of {band:,.0f} {ccy} — the band selects nothing")
    print(f"    {org} band {band:,.0f} {ccy} (its own party.yaml), selection policy "
          f"{policy_version} ({os.path.relpath(version_file, ESTATE)})")
    print(f"    residual {under:,.2f} -> tier {tier_under}; {over:,.2f} (crosses the band) -> "
          f"tier {tier_over}")

    # The crossing, as one prices[] entry the proposer reads — the adopter's real committed
    # entry with the crossing residual on it, so nothing about the entry's shape is invented.
    real = os.path.join(ESTATE, org, "composed", "evidence.json")
    if not os.path.exists(real):
        skip(f"{org} has no composed/evidence.json to take a real prices[] entry from")
    with open(real) as fh:
        evidence = json.load(fh)
    if not evidence.get("prices"):
        fail(f"{org}'s composed evidence carries no prices[] to cross a band with")
    entry = copy.deepcopy(evidence["prices"][0])
    entry.update({"old_price": under, "new_price": over, "old_tier": tier_under,
                  "proposed_tier": tier_over, "changed": True,
                  "proposed_as": "issue" if tier_over == "deny" else "label",
                  "policy_version": policy_version})

    with tempfile.TemporaryDirectory() as tmp:
        work = os.path.join(tmp, org)
        os.makedirs(os.path.join(work, "deploy"))
        shutil.copy(os.path.join(ESTATE, org, "deploy", "pod.yaml"),
                    os.path.join(work, "deploy", "pod.yaml"))
        before = open(os.path.join(work, "deploy", "pod.yaml")).read()
        ev_path = os.path.join(tmp, "evidence.json")
        with open(ev_path, "w") as fh:
            json.dump({**evidence, "prices": [entry]}, fh)

        env = {k: v for k, v in os.environ.items() if k != "GITHUB_REPOSITORY"}
        r = subprocess.run([sys.executable, TIER_PR, "run", "--adopter-dir", work,
                            "--evidence", ev_path, "--workload",
                            os.path.join(work, "deploy", "pod.yaml"), "--org", org,
                            "--dry-run"], capture_output=True, text=True, env=env)
        if r.returncode != 0:
            # The proposer EXISTS (asserted above); one that will not run is the estate
            # failing to propose, which this step observed. Not a could-not-look.
            fail(f"tier_pr.py exited {r.returncode}, so the estate cannot propose the tier it "
                 f"selected: {(r.stderr or r.stdout).strip().splitlines()[-1:]}")
        after = open(os.path.join(work, "deploy", "pod.yaml")).read()

    try:
        landed = json.loads(r.stdout)
    except ValueError:
        fail(f"tier_pr.py --dry-run printed no proposal document: {r.stdout.strip()[:200]}")
    if not landed:
        fail(f"a residual crossing {org}'s band ({under:,.0f} -> {over:,.0f} {ccy}, tier "
             f"{tier_under} -> {tier_over}) proposed nothing")
    p = landed[0]
    if p.get("landed") != "dry-run":
        fail(f"the proposer did not stop at the dry run: {json.dumps(p)[:300]}")
    if p.get("proposal_kind") != "pull_request":
        fail(f"the crossing proposed a {p.get('proposal_kind')!r}, not a pull request editing "
             f"the pod tier label")
    diff = p.get("diff", "")
    if f'"{TIER_LABEL}": "{tier_over}"' not in diff:
        fail(f"the proposed pull request does not set {TIER_LABEL} to {tier_over}: "
             f"{diff.strip()[:300]}")
    if after != before:
        fail("the dry run edited the adopter's workload manifest on disk")
    print(f"    proposal: branch {p['branch']}, {p['proposal_kind']}, landed={p['landed']}")
    print(f"    would set {TIER_LABEL}: {tier_over} on deploy/pod.yaml; nothing opened, "
          f"nothing written")
    # The pod label, NOT the governed Namespace declaration: ADR-0022 makes the Namespace the
    # declaration and the pod label an output of it, and rewiring the proposer onto the
    # Namespace is ticket 26's half. The sentence names what this run actually observed.
    print(f"PASS: a residual crossing {org}'s own appetite band selects {tier_under} -> "
          f"{tier_over} through {org}'s own selection-policy package {policy_version} (which "
          f"platform/graded/cage.py agrees with), and the proposer would open a pull request "
          f"editing the pod tier label")
    return 0


if __name__ == "__main__":
    sys.exit(main())
