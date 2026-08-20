#!/usr/bin/env python3
"""result2oscal.py — the C2P up-flow: PolicyReports -> OSCAL assessment-results.

This is the small glue ADR-0009 says we own: the one Kyverno engine already emits
wgpolicyk8s.io PolicyReports for both planes; this normalises them into an OSCAL
`assessment-results` document that maps each NIST 800-53r5 control to
satisfied / not-satisfied, via observations (the evidence) and findings (the
verdict). It is the offline, dependency-free twin of C2P `result2oscal` for our
exact case (one component-definition, our hand-authored policy names).

It carries the two ADR-0009 shims inline (proven in spikes/c2p-validatingpolicy-oscal):
  1. Kyverno >=1.18 puts the subject in `.scope` and leaves results[].resources
     null -> copy `.scope` into each result's resources.
  2. Coexisting versions deploy as `<policy>-<version>` -> strip the version
     suffix off results[].policy so one component-definition maps every version.

The up-flow only means something if the chain RESOLVES: a cage (05, ../graded/
cage.py) emits a `risk` whose related-observations points at "the not-satisfied
observation for the failing check". To guarantee that pointer lands, every
observation here uses cage.py's own `observation_uuid` formula (single source
of truth) — so `risk.related-observations[].observation-uuid` is byte-identical
to an observation we emit here. verify-upflow.sh (and this module's own
selfcheck) assert exactly that join.

Usage:
    result2oscal.py [fixtures/policyreports.yaml ...]   # print assessment-results
    result2oscal.py --selfcheck                         # runnable asserts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
COMP_DEF = HERE / "component-definition.json"
FIXTURES = HERE / "fixtures" / "policyreports.yaml"

# cage.py (ticket 05) owns the shared OSCAL uuid namespace + observation_uuid
# formula — reuse it rather than a second copy that could drift.
sys.path.insert(0, str(HERE.parent / "graded"))
import cage  # noqa: E402

_SUFFIX = re.compile(r"-\d+-\d+-\d+$")  # slugified semver suffix, e.g. -1-0-0


def check_to_control(comp_def: dict) -> dict[str, str]:
    """{Check_Id (unsuffixed policy name) -> control-id} from the component-definition."""
    out: dict[str, str] = {}
    for comp in comp_def["component-definition"]["components"]:
        for ci in comp.get("control-implementations", []):
            for ir in ci.get("implemented-requirements", []):
                for p in ir.get("props", []):
                    if p.get("name") == "Check_Id":
                        out[p["value"]] = ir["control-id"]
    return out


def shim(report: dict) -> None:
    """ADR-0009 normalisation, in place: subject into resources, strip version suffix."""
    scope = report.get("scope")
    for r in report.get("results") or []:
        if not r.get("resources") and scope:
            r["resources"] = [scope]
        r["_base"] = _SUFFIX.sub("", r["policy"])  # unsuffixed check id
        r["_version"] = r["policy"][len(r["_base"]) + 1:] or None


def _subject(scope: dict) -> tuple[str, str]:
    ns = scope.get("namespace", "")
    name = scope.get("name", "")
    return (f"{ns}/{name}" if ns else name), scope.get("kind", "")


def convert(reports: list[dict], comp_def: dict) -> dict:
    """PolicyReports -> OSCAL assessment-results (observations + findings)."""
    c2c = check_to_control(comp_def)

    observations: list[dict] = []
    # control-id -> {"obs": [uuids], "any_fail": bool}
    by_control: dict[str, dict] = {}

    for rep in reports:
        shim(rep)
        scope = rep.get("scope") or {}
        subj_title, subj_kind = _subject(scope)
        for r in rep.get("results") or []:
            base, result = r["_base"], r["result"]
            control = c2c.get(base)
            if control is None:
                continue  # policy not mapped to a control; not our concern
            # cage.py's formula: the ONE observation id for this subject+check —
            # a cage's OSCAL risk (../graded/cage.py) points back at exactly this.
            obs_uuid = cage.observation_uuid(subj_title, base)
            subj_uuid = str(uuid.uuid5(cage.NS, f"subject:{scope.get('uid', subj_title)}"))
            obs = {
                "uuid": obs_uuid,
                "description": f"{r['policy']} {result} on {subj_kind} {subj_title}",
                "methods": ["TEST-AUTOMATED"],
                "types": ["control-objective"],
                "subjects": [
                    {"subject-uuid": subj_uuid, "type": "resource", "title": f"{subj_kind} {subj_title}"}
                ],
                "relevant-evidence": [
                    {"description": f"Kyverno PolicyReport result: policy={r['policy']} result={result}"}
                ],
                "props": [
                    {"name": "policy", "value": r["policy"]},
                    {"name": "policy-version", "value": r.get("_version") or "unversioned"},
                    {"name": "result", "value": result},
                ],
            }
            observations.append(obs)
            slot = by_control.setdefault(control, {"obs": [], "any_fail": False})
            slot["obs"].append(obs_uuid)
            slot["any_fail"] = slot["any_fail"] or (result == "fail")

    findings = []
    for control, slot in sorted(by_control.items()):
        state = "not-satisfied" if slot["any_fail"] else "satisfied"
        findings.append({
            "uuid": str(uuid.uuid5(cage.NS, f"finding:{control}")),
            "title": f"{control} is {state}",
            "target": {
                "type": "statement-id",
                "target-id": control,
                "status": {"state": state},
            },
            "related-observations": [{"observation-uuid": u} for u in slot["obs"]],
        })

    return {
        "assessment-results": {
            "uuid": str(uuid.uuid5(cage.NS, "assessment-results:pavf")),
            "metadata": {
                "title": "policy-as-versioned-flux — control satisfaction (C2P result2oscal)",
                "last-modified": "2026-07-31T00:00:00Z",
                "version": "1.0.0",
                "oscal-version": "1.1.2",
            },
            "import-ap": {"href": ""},
            "results": [
                {
                    "uuid": str(uuid.uuid5(cage.NS, "result:pavf")),
                    "title": "Kyverno PolicyReport ingest",
                    "description": "Observations + findings normalised from wgpolicyk8s.io PolicyReports.",
                    "start": "2026-07-31T00:00:00Z",
                    "observations": observations,
                    "findings": findings,
                }
            ],
        }
    }


def load_reports(paths: list[str]) -> list[dict]:
    reps: list[dict] = []
    for p in paths:
        for doc in yaml.safe_load_all(Path(p).read_text()):
            if doc and doc.get("kind") in ("PolicyReport", "ClusterPolicyReport"):
                reps.append(doc)
    return reps


def build(paths: list[str] | None = None) -> dict:
    comp_def = json.loads(COMP_DEF.read_text())
    reports = load_reports(paths or [str(FIXTURES)])
    return convert(reports, comp_def)


def selfcheck() -> None:
    doc = build()
    res = doc["assessment-results"]["results"][0]
    obs, finds = res["observations"], res["findings"]
    assert len(obs) == 3, f"expected 3 observations, got {len(obs)}"

    fmap = {f["target"]["target-id"]: f["target"]["status"]["state"] for f in finds}
    assert fmap["nist-800-53:AC-6"] == "not-satisfied", fmap   # legacy-till fails
    assert fmap["nist-800-53:CM-6"] == "satisfied", fmap       # RDS passes

    # THE up-flow join: a cage's risk related-observation resolves to an
    # observation we emit here (identical uuid), by construction not by luck.
    # No ledger — legacy-till fails the conditional policy's condition C, so
    # ../graded/cage.py prices and cages the residual instead of exempting it.
    root_sc = cage.fair.load(str(HERE.parent / "policy" / "scenarios" / "driftwood-root-residual.json"))
    till = cage.select(root_sc, "driftwood", cage.enforce.tolerance_for("driftwood"), mode="warn")
    risk = cage.oscal_risk(till, subject="shop/legacy-till-0", policy="may-run-root-if-attested",
                            control="nist-800-53:AC-6")
    linked = risk["related-observations"][0]["observation-uuid"]
    emitted = {o["uuid"] for o in obs}
    assert linked in emitted, f"broken chain: risk points at {linked}, not among {emitted}"

    # that resolved observation is the failing one, and its control's finding
    # is not-satisfied (evidence -> verdict -> risk).
    linked_obs = next(o for o in obs if o["uuid"] == linked)
    assert {"name": "result", "value": "fail"} in linked_obs["props"], linked_obs
    ac6 = next(f for f in finds if f["target"]["target-id"] == "nist-800-53:AC-6")
    assert {"observation-uuid": linked} in ac6["related-observations"], ac6

    # determinism: re-render is byte-identical.
    assert build() == doc, "not deterministic"
    print(f"selfcheck ok: {len(obs)} observations, {len(finds)} findings; "
          f"AC-6 not-satisfied, CM-6 satisfied; cage risk->observation {linked[:8]} resolves")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("reports", nargs="*", help="PolicyReport YAML (default: fixtures)")
    ap.add_argument("--selfcheck", action="store_true")
    ap.add_argument("--json", action="store_true", help="emit JSON instead of YAML")
    args = ap.parse_args(argv[1:])
    if args.selfcheck:
        selfcheck()
        return 0
    doc = build(args.reports or None)
    print(json.dumps(doc, indent=2) if args.json else yaml.safe_dump(doc, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
