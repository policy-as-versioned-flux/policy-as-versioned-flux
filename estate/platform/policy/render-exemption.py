#!/usr/bin/env python3
"""render-exemption.py — a ledger entry, rendered two ways from one source.

The exemptions ledger (ledger/exemptions.yaml) is the single register AND the
live Flux ResourceSet: flux-operator renders one PolicyException per spec.inputs[]
entry (Flux prune on delete + cleanup.kyverno.io/ttl backstop). This is its
OFFLINE twin — the verify-*.sh beats run without flux-operator in the loop and
need to derive the SAME PolicyException deterministically — AND it is the
generator of each entry's OSCAL `risk` object (status deviation-approved, £ facet).

One ledger entry -> {PolicyException, OSCAL risk}. Delete the entry -> both
vanish (Flux prune); the TTL is the backstop if git ever fails to prune.

The £ on the risk is not invented here: it is fair.py's residual ALE for the
entry's scenario, so the ledger row's price and the balance sheet agree by
construction.

Usage:
    render-exemption.py [exemptions.yaml]              # print PolicyException(s)
    render-exemption.py --oscal [exemptions.yaml]      # print OSCAL risk object(s)
    render-exemption.py --selfcheck                # runnable asserts
"""
from __future__ import annotations

import argparse
import sys
import uuid
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
FAIR = HERE.parent / "fair" / "fair.py"
# Deterministic UUIDs so re-rendering an unchanged entry is stable (git-diff clean).
NS = uuid.UUID("d5f0e0b2-0000-4000-8000-706176662d64")  # constant "pavf" namespace
RISK_SYS = "https://pavf.dev/ns/risk"
GBP_SYS = "https://pavf.dev/ns/risk/gbp"


def slug(s: str) -> str:
    return s.lower().replace(".", "-")


def load_entries(path: Path) -> list[dict]:
    """The ledger IS a flux-operator ResourceSet; each spec.inputs[] is one entry."""
    doc = yaml.safe_load(path.read_text())
    return doc["spec"]["inputs"] or []


def policy_ref(entry: dict) -> str:
    return f"{entry['policy']}-{slug(entry['version'])}"


def policy_exception(entry: dict) -> dict:
    """Ledger entry -> Kyverno PolicyException, scoped by the entry's CEL, TTL-capped.

    cleanup.kyverno.io/ttl (absolute date) is the backstop: even if git never
    prunes this, the Kyverno cleanup controller deletes it at `expires`, so an
    exemption cannot outlive its declared expiry.
    """
    return {
        "apiVersion": "policies.kyverno.io/v1alpha1",
        "kind": "PolicyException",
        "metadata": {
            "name": slug(entry["id"]),
            "namespace": entry["namespace"],
            "labels": {
                "app.kubernetes.io/part-of": "platform",
                "policy-as-versioned.dev/exemption": entry["id"],
            },
            "annotations": {
                # absolute date -> cleanup controller deletes it when reached.
                "cleanup.kyverno.io/ttl": entry["expires"],
                "policy-as-versioned.dev/owner": entry["owner"],
                "policy-as-versioned.dev/reason": " ".join(entry["reason"].split()),
            },
        },
        "spec": {
            "policyRefs": [{"name": policy_ref(entry), "kind": "ValidatingPolicy"}],
            "matchConditions": [
                {"name": "exemption-scope", "expression": entry["scope"]},
            ],
        },
    }


def _price(entry: dict) -> int | None:
    """Residual ALE (£) for the entry's scenario, via fair.py. None if unavailable."""
    scen = entry.get("scenario")
    if not scen or not FAIR.exists():
        return None
    import importlib.util

    spec = importlib.util.spec_from_file_location("fair", FAIR)
    fair = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fair)
    sc = fair.load(str(HERE / "scenarios" / scen))
    st = fair.state(sc, "warn")  # 'warn' = the deviation in place = the residual carried
    return round(fair.summarize(fair.simulate(**st))["ale"])


def observation_uuid(entry: dict) -> str:
    """Stable id of the C2P 'control not satisfied' observation this risk links to."""
    return str(uuid.uuid5(NS, f"obs:{entry['id']}:{entry['control']}"))


def oscal_risk(entry: dict) -> dict:
    """Ledger entry -> OSCAL `risk` assembly (assessment-results / POA&M shared).

    Shape per research 09: status deviation-approved; owner as an origin actor;
    likelihood/impact facets under our system URI; the £ ALE as an
    annualised-loss-expectancy facet (the CVSS-style extension NIST intends);
    remediation type:accept; related-observations back to the failing check;
    deadline = expiry. This IS the priced-exemption OSCAL object.
    """
    rid = str(uuid.uuid5(NS, f"risk:{entry['id']}"))
    owner_uuid = str(uuid.uuid5(NS, f"party:{entry['owner']}"))
    ale = _price(entry)
    facets = [
        {"name": "likelihood", "system": RISK_SYS, "value": "likely"},
        {"name": "impact", "system": RISK_SYS, "value": "high"},
    ]
    if ale is not None:
        facets.append({
            "name": "annualised-loss-expectancy",
            "system": GBP_SYS,
            "value": str(ale),
            "props": [
                {"name": "currency", "value": "GBP"},
                {"name": "basis", "value": "priced-deviation"},
                {"name": "scenario", "value": entry["scenario"]},
            ],
        })
    return {
        "uuid": rid,
        "title": f"{entry['id']}: {entry['policy']} deviation in {entry['namespace']}",
        "description": " ".join(entry["reason"].split()),
        "statement": f"Conditional control {policy_ref(entry)} is not satisfied for "
                     f"scope [{entry['scope']}]; the residual risk is consciously accepted.",
        "props": [
            {"name": "policy", "value": policy_ref(entry)},
            {"name": "control", "value": entry["control"]},
        ],
        "status": "deviation-approved",
        "origins": [
            {"actors": [{"type": "party", "actor-uuid": owner_uuid}]},
        ],
        "characterizations": [
            {"origin": {"actors": [{"type": "party", "actor-uuid": owner_uuid}]},
             "facets": facets},
        ],
        "deadline": f"{entry['expires']}T00:00:00Z",
        "remediations": [
            {"uuid": str(uuid.uuid5(NS, f"rem:{entry['id']}")),
             "lifecycle": "planned",
             "title": f"Accept until {entry['expires']}",
             "description": " ".join(entry["reason"].split()),
             "props": [{"name": "type", "value": "accept"}]},
        ],
        "related-observations": [{"observation-uuid": observation_uuid(entry)}],
    }


def selfcheck() -> None:
    entries = load_entries(HERE / "ledger" / "exemptions.yaml")
    assert entries, "ledger has no entries"
    e = entries[0]

    pe = policy_exception(e)
    assert pe["kind"] == "PolicyException"
    assert pe["spec"]["policyRefs"][0]["name"] == "may-run-root-if-attested-1-0-0"
    assert pe["spec"]["matchConditions"][0]["expression"] == e["scope"]
    # TTL backstop present and equal to the declared expiry.
    assert pe["metadata"]["annotations"]["cleanup.kyverno.io/ttl"] == e["expires"] == "2026-10-01"

    risk = oscal_risk(e)
    assert risk["status"] == "deviation-approved", risk["status"]
    assert risk["remediations"][0]["props"][0] == {"name": "type", "value": "accept"}
    assert risk["deadline"].startswith(e["expires"])
    # the £ facet exists, is numeric-as-string, GBP, and matches fair.py's residual.
    ale_facets = [f for f in risk["characterizations"][0]["facets"]
                  if f["name"] == "annualised-loss-expectancy"]
    assert len(ale_facets) == 1, "missing the £ ALE facet"
    ale = int(ale_facets[0]["value"])
    assert 15_000 < ale < 28_000, f"residual ALE {ale} off expected band"
    assert ale == _price(e), "risk £ != fair.py residual"
    # risk links back to a stable observation (the failing check).
    assert risk["related-observations"][0]["observation-uuid"] == observation_uuid(e)
    # determinism: re-render is byte-identical.
    assert oscal_risk(e) == risk and policy_exception(e) == pe
    print(f"selfcheck ok: 1 entry -> PolicyException(ttl={e['expires']}) "
          f"+ OSCAL risk(deviation-approved, ALE=£{ale})")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("ledger", nargs="?", default=str(HERE / "ledger" / "exemptions.yaml"))
    ap.add_argument("--oscal", action="store_true", help="emit OSCAL risk objects instead")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args(argv[1:])
    if args.selfcheck:
        selfcheck()
        return 0
    entries = load_entries(Path(args.ledger))
    docs = [oscal_risk(e) if args.oscal else policy_exception(e) for e in entries]
    if args.oscal:
        # a minimal OSCAL wrapper so the risks are a valid fragment to merge upstream.
        print(yaml.safe_dump({"risks": docs}, sort_keys=False))
    else:
        print(yaml.safe_dump_all(docs, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
