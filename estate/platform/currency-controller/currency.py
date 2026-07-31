#!/usr/bin/env python3
"""currency.py — the currency controller (ticket 16).

Kyverno stamps posture at *admission* (ticket 15): a pod claiming
`policy-as-versioned.dev/policy-version=vN` gets `posture.acme.io/version=vN`,
and a ClusterSPIFFEID bakes `posture/vN` into its SVID path. But Kyverno only
fires at admission — the posture is a FROZEN SNAPSHOT. When vN is later retired
from the platform version array (distribution/versions.yaml), every already-
running pod admitted under vN keeps its "current" SVID until something re-
evaluates it. That gap is exactly what research 16 flagged as the single biggest
risk. This controller closes it.

  supported := the versions still declared in the ResourceSet array (the SAME
               array the orphan-guard allow-lists — one source of truth).
  stale pod := a running, postured pod whose posture.acme.io/version is NOT in
               `supported` (i.e. its admitted version has since been retired).

For each stale pod, one bounded reconcile pass either:

  * DE-POSTURES it (default) — a single patch that removes BOTH the posture
    label AND the policy-version claim. This is the ONLY durable re-patch,
    because `stamp-posture` (the mutating webhook) re-clobbers posture := claim
    on every UPDATE: remove only the posture and the mutate puts it straight
    back; remove only the claim and `posture-trust-boundary` DENIES the update
    (posture with no claim). Removing both in one patch sails through — no claim
    ⇒ stamp-posture is out of scope, no posture ⇒ trust-boundary is out of
    scope, orphan-guard is out of scope — and the pod stops matching the posture
    ClusterSPIFFEID. spire-controller-manager drops its entry within ~10s and
    the posture SVID stops renewing within one jwtTtl (5m); it falls back to the
    plain base-mesh SVID. The pod keeps running, but out of currency ⇒ it loses
    posture-gated reach and its OpenBao secret (ticket 17). "Keep running but
    caged", priced into TCoR (user story 2).

  * EVICTS it (--action evict) — deletes the pod; its controller recreates it,
    re-admission hits the orphan-guard (version retired ∉ array) → DENIED, so it
    cannot come back on a retired version. The blunt end of the same lever.

Runtime: pure stdlib. In-cluster (the CronJob) it talks to the API server with
urllib + the mounted ServiceAccount token — no kubectl, no pip deps, so it runs
in a bare `python:3-slim`. `select_stale` / `deposture_patch` are pure and
unit-tested offline (`currency.py selfcheck`); the urllib glue is thin.

Usage:
    currency.py selfcheck                      # runnable asserts (no cluster)
    currency.py plan   < pods.json             # offline: print the reconcile plan
    currency.py reconcile [--action deposture|evict] [--dry-run]   # in-cluster
"""
from __future__ import annotations

import argparse
import json
import os
import ssl
import sys
import urllib.parse
import urllib.request

CLAIM_LABEL = "policy-as-versioned.dev/policy-version"
POSTURE_LABEL = "posture.acme.io/version"

DEPOSTURE, EVICT = "deposture", "evict"


# ---------------------------------------------------------------------------
# Pure core (no cluster; this is the tested logic)
# ---------------------------------------------------------------------------
def select_stale(supported: set[str], pods: list[dict]) -> list[dict]:
    """The postured pods whose admitted version is no longer supported.

    `pods` is the trimmed shape {namespace, name, posture} (as extracted from the
    k8s pod list). A pod with no posture is not our concern (base mesh workload).
    A pod whose posture IS in `supported` is in currency — left alone.
    """
    out = []
    for p in pods:
        posture = p.get("posture")
        if posture and posture not in supported:
            out.append(p)
    return out


def deposture_patch() -> dict:
    """The clobber-beating merge patch: remove BOTH labels in ONE update.

    JSON-merge-patch semantics — a null value deletes the key. Removing the claim
    takes the pod out of scope for stamp-posture (so the mutate can't re-add the
    posture), the orphan-guard, and the versioned require-* policies; removing the
    posture takes it out of scope for posture-trust-boundary. The pod is left un-
    versioned and un-postured: it keeps running, drops to the base-mesh SVID.
    """
    return {"metadata": {"labels": {POSTURE_LABEL: None, CLAIM_LABEL: None}}}


# ---------------------------------------------------------------------------
# Live I/O — in-cluster only (urllib + ServiceAccount token). Thin glue.
# ---------------------------------------------------------------------------
SA = "/var/run/secrets/kubernetes.io/serviceaccount"


def _api():
    """(base_url, opener) for the in-cluster API server, or raise if not in a pod."""
    host = os.environ.get("KUBERNETES_SERVICE_HOST")
    port = os.environ.get("KUBERNETES_SERVICE_PORT", "443")
    if not host:
        raise SystemExit("reconcile runs in-cluster only (no KUBERNETES_SERVICE_HOST); "
                         "use `plan` for an offline dry-run, or trigger the CronJob for a live pass")
    with open(f"{SA}/token") as fh:
        token = fh.read().strip()
    ctx = ssl.create_default_context(cafile=f"{SA}/ca.crt")
    base = f"https://{host}:{port}"

    def call(method: str, path: str, body: dict | None = None, content_type: str | None = None):
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(base + path, data=data, method=method)
        req.add_header("Authorization", f"Bearer {token}")
        req.add_header("Accept", "application/json")
        if content_type:
            req.add_header("Content-Type", content_type)
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.load(resp)

    return call


def get_supported(call) -> set[str]:
    """Supported versions = the ResourceSet array (one source of truth with the
    orphan-guard). `SUPPORTED_VERSIONS` (comma-list) overrides — the escape hatch
    for demo paths where flux-operator isn't installed."""
    override = os.environ.get("SUPPORTED_VERSIONS", "").strip()
    if override:
        return {v.strip() for v in override.split(",") if v.strip()}
    rs = call("GET", "/apis/fluxcd.controlplane.io/v1/namespaces/flux-system/"
                     "resourcesets/policy-versions")
    versions = rs["spec"]["inputs"][0]["versions"]
    return {v["version"] for v in versions}


def list_postured_pods(call) -> list[dict]:
    sel = urllib.parse.quote(POSTURE_LABEL)
    body = call("GET", f"/api/v1/pods?labelSelector={sel}")
    out = []
    for item in body.get("items", []):
        meta = item["metadata"]
        out.append({"namespace": meta["namespace"], "name": meta["name"],
                    "posture": meta.get("labels", {}).get(POSTURE_LABEL)})
    return out


def reconcile(action: str = DEPOSTURE, dry_run: bool = False) -> dict:
    """ONE bounded pass — no watch, nothing that blocks (a CronJob runs this)."""
    call = _api()
    supported = get_supported(call)
    stale = select_stale(supported, list_postured_pods(call))
    acted = []
    for p in stale:
        ns, name = p["namespace"], p["name"]
        if dry_run:
            acted.append({**p, "action": action, "applied": False})
            continue
        if action == EVICT:
            call("DELETE", f"/api/v1/namespaces/{ns}/pods/{name}")
        else:
            call("PATCH", f"/api/v1/namespaces/{ns}/pods/{name}",
                 body=deposture_patch(),
                 content_type="application/merge-patch+json")
        acted.append({**p, "action": action, "applied": True})
    summary = {"supported": sorted(supported), "stale": len(stale),
               "action": action, "dry_run": dry_run, "acted": acted}
    print(json.dumps(summary))
    return summary


# ---------------------------------------------------------------------------
def selfcheck() -> None:
    supported = {"1.0.0", "2.0.0"}
    pods = [
        {"namespace": "tuppence", "name": "reset-abc", "posture": "1.0.0"},   # current
        {"namespace": "tuppence", "name": "reset-old", "posture": "0.9.0"},   # retired → stale
        {"namespace": "driftwood", "name": "base", "posture": None},          # un-postured
        {"namespace": "ludlow", "name": "reset-x", "posture": "3.0.0"},       # never-supported → stale
    ]
    stale = select_stale(supported, pods)
    names = {p["name"] for p in stale}
    assert names == {"reset-old", "reset-x"}, names       # only retired/unsupported postures
    # a current pod is never touched; an un-postured pod is never touched
    assert "reset-abc" not in names and "base" not in names

    # retiring 2.0.0 makes every 2.0.0 pod stale (the demo beat: retire → out of currency)
    stale2 = select_stale({"1.0.0"}, [{"namespace": "t", "name": "v2", "posture": "2.0.0"}])
    assert [p["name"] for p in stale2] == ["v2"]
    # ...and re-adding it brings them back into currency
    assert select_stale({"1.0.0", "2.0.0"}, [{"namespace": "t", "name": "v2", "posture": "2.0.0"}]) == []

    # THE crux: the re-patch removes BOTH labels (else stamp-posture re-clobbers,
    # or posture-trust-boundary denies). Both keys present, both null.
    patch = deposture_patch()["metadata"]["labels"]
    assert patch == {POSTURE_LABEL: None, CLAIM_LABEL: None}, patch
    assert patch[POSTURE_LABEL] is None and patch[CLAIM_LABEL] is None
    assert set(patch) == {POSTURE_LABEL, CLAIM_LABEL}, "must remove BOTH, not one"

    print("currency selfcheck: all asserts passed "
          "(stale = posture ∉ supported; re-patch drops BOTH labels)")


def main(argv=None) -> int:
    p = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selfcheck", help="run the asserts (no cluster)")
    pl = sub.add_parser("plan", help="offline: read a pod list JSON on stdin, print the plan")
    pl.add_argument("--supported", default=os.environ.get("SUPPORTED_VERSIONS", "1.0.0,2.0.0"),
                    help="comma-list of supported versions (default 1.0.0,2.0.0)")
    pl.add_argument("--action", choices=[DEPOSTURE, EVICT], default=DEPOSTURE)
    rc = sub.add_parser("reconcile", help="in-cluster: one bounded reconcile pass")
    rc.add_argument("--action", choices=[DEPOSTURE, EVICT], default=DEPOSTURE)
    rc.add_argument("--dry-run", action="store_true")
    args = p.parse_args(argv)

    if args.cmd == "selfcheck":
        selfcheck()
        return 0
    if args.cmd == "plan":
        supported = {v.strip() for v in args.supported.split(",") if v.strip()}
        pods = json.load(sys.stdin)
        stale = select_stale(supported, pods)
        print(json.dumps({"supported": sorted(supported), "action": args.action,
                          "stale": [{**s, "patch": deposture_patch()} for s in stale]}, indent=2))
        return 0
    reconcile(action=args.action, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
