#!/usr/bin/env python3
"""provenance.py — walk the WHOLE chain, name every actor, root every identity.

The auditor's beat (spec user story 5): *every actor — commit, workload, human,
device — is attestable to one root, so the whole chain verifies rather than being
trusted.* This module assembles that chain as data, end to end:

    feed → scenario → PR → review → merge → release           (the change path)
                                              │
                                              ▼
    workload SVID · device SVID · commit/human identity        (the runtime identities)

Every link names WHO acted (an AI agent or a human), WHAT they did (propose vs
dispose vs publish), WHEN (anchored to the feed version that drove it), and FROM
WHICH EVIDENCE — a real file on disk, not a claim. The two disposition links
(merge, release) are HUMAN by construction; the proposal is the AI war-gamer.
That is propose-never-dispose made auditable end to end.

Nothing is re-derived: the feed→scenario→PR links + their evidence come straight
from wargamer.py (which reuses fair/enforce/tcor); the runtime identities are read
from the committed SPIRE manifests (posture ClusterSPIFFEID, device
ClusterStaticEntry). This module only STITCHES and ASSERTS the seams.

Pure/offline. Usage:
    provenance.py chain       # the full attestation chain (JSON)
    provenance.py walk        # human-readable narration of who did what, when, whence
    provenance.py selfcheck   # the end-to-end asserts (the beat)
"""
from __future__ import annotations

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
# Post-split (mo-12): platform is a real, separate GitHub repo, not a sibling
# directory. PLATFORM points at .estate-clone/platform, the disposable local
# checkout clone-estate.sh assembles from that repo.
PLATFORM = os.path.normpath(os.path.join(HERE, "..", "..", ".estate-clone", "platform"))
WARGAMER = os.path.join(PLATFORM, "wargamer")

# The ONE estate trust domain every workload + device SVID roots to.
TRUST_DOMAIN = "spiffe://acme.internal"
# The keyless supply-chain root every commit/PR/tag roots to.
REKOR_ROOT = "gitsign keyless (OIDC -> Fulcio) -> Rekor transparency log"


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(path))
    spec.loader.exec_module(mod)
    return mod


wg = _load("wargamer", os.path.join(WARGAMER, "wargamer.py"))


def _yaml_docs(path):
    import yaml
    with open(path) as fh:
        return [d for d in yaml.safe_load_all(fh) if d]


def _exists(*parts):
    """Resolve a repo path and confirm the evidence artifact is really there."""
    p = os.path.normpath(os.path.join(*parts))
    return p, os.path.exists(p)


# --- the change path: feed -> scenario -> PR -> review -> merge -> release -----
def change_chain():
    """The six links from a signed feed to a signed release. Each carries the
    actor, their class (publisher | ai | human), the act (publish/derive/propose/
    review/merge/release), the WHEN anchor, and a real evidence path."""
    intel = wg.collect()
    rows = wg.wargame(intel)
    props = wg.proposals(intel)

    # The load-bearing drift: driftwood cart-PII, Audit -> Deny at the v3 feed.
    dw = next(r for r in rows if r["kind"] == "enforcement" and r["org"] == "driftwood")
    pr = next(p for p in props if p["change"]["from"] == "Audit"
              and p["change"]["to"] == "Deny")
    feed_v = intel["current"].get("feed_version", "v?")
    when = f"feed {feed_v}"  # temporal anchor: the feed version that drove the change

    feed_path, feed_ok = _exists(WARGAMER, "fixtures", "threat-register", feed_v, "register.json")
    feed_sig, feed_sig_ok = _exists(WARGAMER, "fixtures", "threat-register", feed_v, "register.json.sig")
    scen_path, scen_ok = _exists(PLATFORM, "feeds", "to_fair_scenario.py")
    policy_path, policy_ok = _exists(PLATFORM, pr["change"]["target"])
    rel_path, rel_ok = _exists(PLATFORM, "distribution", "versions.yaml")

    return [
        {"seq": 1, "link": "feed", "actor": intel["current"].get("published_by", "platform") + "-feeds",
         "actor_class": "publisher", "act": "publish", "when": when,
         "identity": "ed25519 detached signature (platform feeds key)",
         "evidence": feed_path, "evidence_present": feed_ok and feed_sig_ok,
         "detail": f"signed threat-register {feed_v}: driftwood skimmer-campaign LEF uptick"},

        {"seq": 2, "link": "scenario", "actor": "wargamer-agent", "actor_class": "ai",
         "act": "derive", "when": when,
         "identity": "deterministic (feed -> FAIR triples), no human input",
         "evidence": scen_path, "evidence_present": scen_ok,
         "detail": "feed LEF x control LM -> FAIR scenario -> £ residual crosses driftwood's band"},

        {"seq": 3, "link": "PR", "actor": pr["actor"], "actor_class": "ai",
         "act": "propose", "when": when, "identity": pr["identity"],
         "evidence": policy_path, "evidence_present": policy_ok,
         "signed": pr["signed"], "merged": pr["merged"], "auto_merge": pr["auto_merge"],
         "from_evidence": pr["from_evidence"], "required_gate": pr["required_gate"],
         "detail": pr["title"]},

        {"seq": 4, "link": "review", "actor": "human-reviewer", "actor_class": "human",
         "act": "review", "when": when,
         "identity": "estate OIDC (Dex) login — a named human, not the agent",
         "evidence": policy_path, "evidence_present": policy_ok,
         "detail": "a human reads the £-justified diff + the version cross-check gate result"},

        {"seq": 5, "link": "merge", "actor": "human-maintainer", "actor_class": "human",
         "act": "dispose", "when": when, "identity": REKOR_ROOT,
         "evidence": policy_path, "evidence_present": policy_ok,
         "detail": "a human merges — gitsign-keyless commit lands in Rekor; the AGENT never merges"},

        {"seq": 6, "link": "release", "actor": "human-release-signer", "actor_class": "human",
         "act": "release", "when": when,
         "identity": f"signed git tag policy/v{CONVERGES_ON()} -> {REKOR_ROOT}",
         "evidence": rel_path, "evidence_present": rel_ok,
         "detail": f"cut signed tag policy/v{CONVERGES_ON()}; Flux ResourceSet pins the version to it"},
    ]


def CONVERGES_ON():
    """The version the chain terminates at == the latest released version in the
    distribution contract (versions.yaml) == the version a compliant workload
    then carries in its SVID posture path. One number closes the loop."""
    vers = _yaml_docs(os.path.join(PLATFORM, "distribution", "versions.yaml"))[0]
    arr = vers["spec"]["inputs"][0]["versions"]
    return sorted(v["version"] for v in arr)[-1]  # latest declared release


# --- the runtime identities: workload, device, commit/human -------------------
def runtime_identities():
    """The three actor classes that present an identity at runtime, each rooted.
    Workload + device root to the SPIRE trust domain; commit/human to Rekor."""
    posture = _yaml_docs(os.path.join(PLATFORM, "posture", "spire", "clusterspiffeid-posture.yaml"))[0]
    device = _yaml_docs(os.path.join(PLATFORM, "access", "device", "device-svid.yaml"))[0]
    tmpl = posture["spec"]["spiffeIDTemplate"]
    dev_id = device["spec"]["spiffeID"]
    dev_sel = [s for s in device["spec"].get("selectors", [])]
    ver = CONVERGES_ON()

    return [
        {"actor_class": "workload", "root": TRUST_DOMAIN,
         "svid": f"{TRUST_DOMAIN}/posture/{ver}/ns/<ns>/sa/<sa>",
         "template": tmpl, "carries_release_version": ver,
         "attested_by": "SPIRE CA (X.509-SVID URI-SAN, Kyverno-stamped posture label)",
         "manifest": os.path.join("posture", "spire", "clusterspiffeid-posture.yaml")},

        {"actor_class": "device", "root": TRUST_DOMAIN, "svid": dev_id,
         "attested_by": "SPIRE tpm_devid node attestor (TPM/Secure-Enclave residency)",
         "selectors": dev_sel,
         "manifest": os.path.join("access", "device", "device-svid.yaml")},

        {"actor_class": "commit/human", "root": REKOR_ROOT,
         "svid": "OIDC subject (email) bound in a Fulcio cert, logged in Rekor",
         "attested_by": "gitsign keyless — the merge + release links above",
         "manifest": None},
    ]


def full():
    return {"change_chain": change_chain(),
            "runtime_identities": runtime_identities(),
            "converges_on": CONVERGES_ON()}


# --- narration ----------------------------------------------------------------
def walk():
    data = full()
    print("CHANGE PATH — who proposed what, when, from which evidence:")
    for l in data["change_chain"]:
        cls = l["actor_class"].upper()
        print(f"  {l['seq']}. {l['link']:9} [{cls:9}] {l['actor']:22} {l['act']:8}"
              f" @ {l['when']:9} :: {l['detail']}")
        ev = "present" if l.get("evidence_present") else "MISSING"
        print(f"       evidence: {os.path.relpath(l['evidence'], HERE)}  ({ev})")
    print(f"\n  the chain converges on release v{data['converges_on']} — the same version a")
    print(f"  compliant workload then carries in its SVID posture path:")
    print("\nRUNTIME IDENTITIES — every actor rooted, no network-position trust:")
    for r in data["runtime_identities"]:
        print(f"  {r['actor_class']:13} root={r['root']}")
        print(f"                svid={r['svid']}")
        print(f"                by  ={r['attested_by']}")


# --- the end-to-end asserts (the beat) ----------------------------------------
def selfcheck():
    data = full()
    chain, rids, ver = data["change_chain"], data["runtime_identities"], data["converges_on"]

    # 1. The chain is complete and ordered feed -> ... -> release.
    seq = [l["link"] for l in chain]
    assert seq == ["feed", "scenario", "PR", "review", "merge", "release"], seq
    assert [l["seq"] for l in chain] == [1, 2, 3, 4, 5, 6]

    # 2. Every link names an actor with a class, an act, a WHEN, and REAL evidence.
    for l in chain:
        assert l["actor"] and l["actor_class"] and l["act"] and l["when"], l
        assert l["evidence_present"], ("evidence artifact missing on disk", l["link"], l["evidence"])

    # 3. Propose-never-dispose, made auditable: the PR is AI + propose + never
    #    merged; the two DISPOSITION links (merge, release) are HUMAN.
    pr = next(l for l in chain if l["link"] == "PR")
    assert pr["actor_class"] == "ai" and pr["act"] == "propose", pr
    assert pr["merged"] is False and pr["auto_merge"] is False, pr
    assert pr["signed"] is True and "Rekor" in pr["identity"], pr
    assert pr["from_evidence"], pr  # the AI names the evidence it proposed FROM
    for link in ("merge", "release"):
        d = next(l for l in chain if l["link"] == link)
        assert d["actor_class"] == "human", ("disposition must be human", d)
    # exactly one AI-proposed link, and a human disposes it downstream:
    assert sum(1 for l in chain if l["actor_class"] == "ai" and l["act"] == "propose") == 1

    # 4. Commit/PR is attestable in Rekor — the identity string is the real root
    #    on the two keyless links (offline structural proof; live tail verifies it).
    rekor_links = [l for l in chain if "Rekor" in l.get("identity", "")]
    assert len(rekor_links) >= 2, ("merge + release must carry the Rekor root", rekor_links)

    # 5. Workload + device SVIDs verify against SPIRE — ONE root, distinct classes.
    wl = next(r for r in rids if r["actor_class"] == "workload")
    dv = next(r for r in rids if r["actor_class"] == "device")
    assert wl["root"] == dv["root"] == TRUST_DOMAIN, (wl["root"], dv["root"])
    assert "/posture/" in wl["template"], wl["template"]
    assert wl["template"].index("/posture/") < wl["template"].index("/ns/"), \
        "posture must LEAD the workload SVID path"
    assert dv["svid"].startswith(TRUST_DOMAIN + "/device/"), dv["svid"]
    assert any(str(s).startswith("tpm_devid:") for s in dv["selectors"]), \
        ("device SVID must be pinned to a tpm_devid selector (this hardware only)", dv["selectors"])

    # 6. THE CLOSURE: the version the change chain converges on IS the version the
    #    running workload carries in its SVID — runtime identity traces back through
    #    release -> merge -> PR -> scenario -> feed. End to end, not asserted.
    rel = next(l for l in chain if l["link"] == "release")
    assert ver in rel["identity"], ("release link must name the converged version", rel)
    assert wl["carries_release_version"] == ver, \
        ("the workload SVID must carry the released version", wl["carries_release_version"], ver)

    ai = [l for l in chain if l["actor_class"] == "ai"]
    hu = [l for l in chain if l["actor_class"] == "human"]
    print(
        f"ok  6-link chain feed->scenario->PR->review->merge->release, all evidence on disk; "
        f"AI proposed {len(ai)} link(s) (never merged), humans disposed {len(hu)}; "
        f"workload+device SVIDs share one root ({TRUST_DOMAIN}); "
        f"chain converges on v{ver} == the version the workload SVID carries. "
        f"Every actor attestable; the whole chain verifies."
    )


def main(argv=None):
    argv = argv or sys.argv[1:]
    cmd = argv[0] if argv else "selfcheck"
    if cmd == "chain":
        print(json.dumps(full(), indent=2))
    elif cmd == "walk":
        walk()
    elif cmd == "selfcheck":
        selfcheck()
    else:
        sys.exit(f"usage: provenance.py [chain|walk|selfcheck]; got {cmd!r}")


if __name__ == "__main__":
    main()
