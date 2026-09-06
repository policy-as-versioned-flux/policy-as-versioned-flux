#!/usr/bin/env python3
"""refusal_probe.py -- leg B: is this mutation byte-identical on an already-mutated object?

A pod spec is nearly immutable after creation, so a mutation that is not byte-identical when it
meets its own output is a refusal by another name. That is exactly what bit the estate on
2026-08-28: the WAF sidecar was appended unconditionally, so the second admission of an
already-caged pod produced `spec.containers: duplicate entries for key [name="waf-sidecar"]`
and the API server refused every `kubectl label` on a running caged pod.

Reading the body never caught one of these. This leg EXECUTES the mutation, twice.

THE PROBLEM, AND IT IS THE WHOLE DIFFICULTY OF THIS TICKET. `kyverno apply` (1.18.2, the pinned
CLI) has no UPDATE mode. It evaluates every resource as a CREATE, and against an UPDATE-scoped
policy it matches NOTHING -- not even a skip. So:

  * feeding an UPDATE-scoped policy to the CLI and reading a green off it would be a step that
    passed because nothing applied. `assert_no_update_mode()` MEASURES that, on every run,
    rather than disclosing it in prose: it feeds an UPDATE-only policy to the CLI and requires
    zero applications. The day the CLI grows an UPDATE mode that probe FAILS and says so, which
    is the only way a disclosed limit does not quietly go stale.
  * so the operation scoping is asserted STRUCTURALLY, from the manifest (refusal_scan.hazards
    reads `matchConstraints.resourceRules[].operations`), and the mutation CONTENT is measured
    functionally against a throwaway copy whose operations have been rewritten to CREATE. The
    copy also loses `namespaceSelector`, which the CLI cannot evaluate offline
    (kyverno/kyverno#13605), and any `oldObject` gate, which the CLI cannot populate. Every
    change is printed with the run.
  * and no probe may pass because nothing applied: a policy that matches none of the candidate
    pods is a FAIL naming the policy, never a quiet skip.

Usage:
    refusal_probe.py --root DIR      # probe every UPDATE-scoped mutation on the served surface
    refusal_probe.py --selfcheck     # the CLI's no-UPDATE-mode probe, and a planted defect
"""

from __future__ import annotations

import argparse
import copy
import json
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refusal_scan as rs  # noqa: E402

VERSION_RE = re.compile(r"(\d+\.\d+\.\d+)")


def _pod(name: str, claim: str | None) -> dict:
    labels = {"policy-as-versioned.dev/policy-version": claim} if claim else {}
    return {"apiVersion": "v1", "kind": "Pod",
            "metadata": {"name": name, "namespace": "governed-ns", "labels": labels},
            "spec": {"containers": [{"name": "app", "image": "nginx",
                                     "resources": {"limits": {"cpu": "2", "memory": "1Gi"}}}]}}


def declaw(doc: dict) -> tuple[dict, list[str]]:
    """A throwaway copy the offline CLI can evaluate, and the list of what was changed.

    Nothing here is a claim about the estate: it is a copy, it is thrown away, and every
    difference from the served body is printed beside the result.
    """
    out = copy.deepcopy(doc)
    changed: list[str] = []
    for rule in (((out.get("spec") or {}).get("matchConstraints") or {})
                 .get("resourceRules") or []):
        if rule.get("operations") and rule["operations"] != ["CREATE"]:
            changed.append(f"operations {rule['operations']} -> ['CREATE'] "
                           "(the CLI has no UPDATE mode; scoping is asserted structurally)")
            rule["operations"] = ["CREATE"]
    mc = (out.get("spec") or {}).get("matchConstraints") or {}
    if "namespaceSelector" in mc:
        mc.pop("namespaceSelector")
        changed.append("namespaceSelector dropped (the CLI cannot evaluate it offline, "
                       "kyverno/kyverno#13605)")
    conds = (out.get("spec") or {}).get("matchConditions") or []
    keep = [c for c in conds if "oldObject" not in str(c.get("expression", ""))]
    if len(keep) != len(conds):
        changed.append("the oldObject gate dropped (the CLI has no UPDATE, so it cannot "
                       "populate oldObject and every resource would fail the gate -- the step "
                       "would then pass because NOTHING applied)")
    ranged = [c for c in keep if rs.TEMPLATE_MARK in str(c.get("expression", ""))]
    if ranged:
        # flux-operator renders the version array INTO this expression; offline there is no
        # renderer, so the condition is a half-rendered string that matches nothing. Dropping it
        # is the same call as the two above: what the mutation WRITES is measured, and its
        # scoping is asserted structurally from the manifest by refusal_scan.hazards.
        changed.append(f"{len(ranged)} template-ranged matchCondition(s) dropped "
                       f"({', '.join(str(c.get('name')) for c in ranged)}): the version array is "
                       "rendered into them by flux-operator and nothing offline renders it")
        keep = [c for c in keep if c not in ranged]
    if len(keep) != len(conds):
        out["spec"]["matchConditions"] = keep
    return out, changed


def _candidate_claims(doc: dict, path: str) -> list[str | None]:
    """The version claims worth trying, read off the policy's OWN scoping.

    Every served cage carries `only-this-policy-version`, so a pod that claims anything else is
    not matched at all -- which is the fact that made ticket 89's round 1 wrong. The claim is
    taken from the policy's matchConditions first, then from the version directory it ships in,
    and finally an orphan claim and no claim at all, so the two machinery populations are
    reachable too.
    """
    found: list[str | None] = []
    for cond in ((doc.get("spec") or {}).get("matchConditions") or []):
        for lit in re.findall(r"['\"](\d+\.\d+\.\d+)['\"]", str(cond.get("expression", ""))):
            if lit not in found:
                found.append(lit)
    m = re.search(r"/v(\d+\.\d+\.\d+)/", path)
    if m and m.group(1) not in found:
        found.append(m.group(1))
    return found + ["9.9.9", None]


@dataclass
class Probe:
    policy: str
    path: str
    ok: bool
    detail: str


_COUNTS = re.compile(r"pass:\s*(\d+),\s*fail:\s*(\d+),\s*warn:\s*(\d+),\s*error:\s*(\d+),"
                     r"\s*skip:\s*(\d+)")


@dataclass
class Run:
    """One `kyverno apply`: what it counted and what object it left behind.

    `applied` is the PASS COUNT, never the existence of the output file. That distinction is
    load-bearing and was measured here on 2026-09-06: against an UPDATE-scoped policy the CLI
    prints "Mutation has been applied successfully", writes `<name>-mutated.yaml` and counts
    `pass: 0` -- and the file it writes is the UNMUTATED resource. A beat that reads the file's
    existence, or greps that reassuring sentence, measures nothing at all and calls it a pass.
    """

    rc: int
    text: str
    counts: tuple[int, ...]
    obj: dict | None

    @property
    def applied(self) -> bool:
        return bool(self.counts) and self.counts[0] >= 1


#: The rungs of the ladder. The tier comes from the pod's NAMESPACE (ADR-0022), and the offline
#: CLI populates `namespaceObject` only from a values file -- so without one every probe lands on
#: whatever the body's fail-closed else-branch happens to be, and the rungs that inject a WAF
#: sidecar are never reached at all. Measured 2026-09-06: probing without the values file, the
#: v4.0.0 body lands on `baseline`, which carries no sidecar, and the 2026-08-28 duplicate-sidecar
#: defect replays GREEN. A leg that cannot reach the rung the defect lived on is not a leg.
TIERS = (None, "baseline", "restricted", "quarantine", "isolated")


def _values(tier: str | None) -> dict:
    sel = [{"name": "governed-ns",
            "labels": {"policy-as-versioned.dev/governed": "true",
                       **({"posture.acme.io/tier": tier} if tier else {})}}]
    return {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Values",
            "metadata": {"name": "values"}, "namespaceSelector": sel}


def _apply(kyverno: str, policy: Path, resource: Path, out: Path,
           values: Path | None = None) -> Run:
    cmd = [kyverno, "apply", str(policy), "--resource", str(resource), "-o", str(out)]
    if values is not None:
        cmd += ["--values-file", str(values)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    text = proc.stdout + proc.stderr
    m = _COUNTS.search(text)
    counts = tuple(int(g) for g in m.groups()) if m else ()
    obj = None
    for f in sorted(out.glob("*-mutated.yaml")) if out.is_dir() else []:
        docs = [d for d in yaml.safe_load_all(f.read_text()) if isinstance(d, dict)]
        # The CLI writes the same object more than once (twice, for one policy over one
        # resource). The last one is the settled result; feeding the file back verbatim would
        # hand the next run two resources of the same name and no comparison would ever match.
        if docs:
            obj = docs[-1]
    return Run(proc.returncode, text, counts, obj)


def _canonical(obj: dict) -> str:
    return yaml.safe_dump(obj, sort_keys=True, default_flow_style=False)


def assert_no_update_mode(kyverno: str) -> tuple[bool, str]:
    """MEASURE the CLI limit this whole file is built around, rather than asserting it in prose.

    An UPDATE-only mutating policy, a resource it would match on UPDATE, and the requirement
    that the CLI applies NOTHING. If a future CLI grows an UPDATE mode this returns False, and
    the caller goes red with "the disclosed limit has lifted" -- which is the point: a
    disclosed limit is an assertion and goes stale like any other.
    """
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        policy = {"apiVersion": "policies.kyverno.io/v1alpha1", "kind": "MutatingPolicy",
                  "metadata": {"name": "update-only-probe"},
                  "spec": {"matchConstraints": {"resourceRules": [
                      {"apiGroups": [""], "apiVersions": ["v1"],
                       "operations": ["UPDATE"], "resources": ["pods"]}]},
                      "mutations": [{"patchType": "ApplyConfiguration", "applyConfiguration": {
                          "expression": 'Object{metadata: Object.metadata{labels: '
                                        '{"probe": "applied"}}}'}}]}}
        (t / "p.yaml").write_text(yaml.safe_dump(policy))
        (t / "r.yaml").write_text(yaml.safe_dump(_pod("probe", None)))
        run = _apply(kyverno, t / "p.yaml", t / "r.yaml", t / "o")
        wrote_label = bool(run.obj and (run.obj.get("metadata") or {}).get("labels", {})
                           .get("probe") == "applied")
        if run.applied or wrote_label:
            return False, ("the pinned kyverno CLI APPLIED an UPDATE-scoped policy "
                           f"(counts {run.counts}, label written {wrote_label}): the disclosed "
                           "limit has LIFTED and leg B should now measure the real UPDATE path "
                           "instead of a rewritten copy -- rewrite this file")
        return True, (f"measured, not disclosed: the CLI evaluates an UPDATE-scoped policy as "
                      f"nothing at all -- it prints \"Mutation has been applied successfully\", "
                      f"writes an UNMUTATED <name>-mutated.yaml and counts pass:0 "
                      f"(counts {run.counts}). So operation scoping is asserted structurally "
                      f"and the body is measured on a rewritten copy, and this leg reads the "
                      f"PASS COUNT rather than the file's existence")


def probe(kyverno: str, doc: dict, path: str) -> Probe:
    """Apply the mutation, then apply it to its own output, and require byte-identity."""
    declawed, changed = declaw(doc)
    name = (doc.get("metadata") or {}).get("name", "?")
    claims = _candidate_claims(doc, path)
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / "p.yaml").write_text(yaml.safe_dump(declawed))
        reached: list[tuple[str | None, str | None, Run]] = []
        for claim in claims:
            for j, tier in enumerate(TIERS):
                tag = f"{claims.index(claim)}-{j}"
                (t / f"r{tag}.yaml").write_text(yaml.safe_dump(_pod("probe", claim)))
                (t / f"v{tag}.yaml").write_text(yaml.safe_dump(_values(tier)))
                run = _apply(kyverno, t / "p.yaml", t / f"r{tag}.yaml", t / f"o{tag}",
                             t / f"v{tag}.yaml")
                if run.applied and run.obj:
                    reached.append((claim, tier, run))
            if reached:
                break
        if not reached:
            return Probe(name, path, False,
                         "no candidate pod on any rung made this mutation apply at all (pass "
                         "count 0 on every one), so nothing was measured -- a step that passes "
                         "because nothing applied is the defect this ticket exists to catch")
        # REVIEW, 2026-09-06 (F3b). A policy whose `mutations` are emptied still comes back
        # `pass: 2` from the CLI, and 'identical applied to its own output' is then true and
        # vacuous. The mutation must actually WRITE something to the pod it was handed, or this
        # leg passed on a policy that does nothing -- the same defect one level in.
        wrote = any(_canonical(r.obj) != _canonical(_pod("probe", c))
                    for c, _, r in reached if r.obj)
        if not wrote:
            return Probe(name, path, False,
                         "the mutation applied and changed NOTHING on any rung: the object came "
                         "back exactly as it went in, so byte-identity on its own output is "
                         "vacuously true and this leg measured a policy that writes nothing")
        for claim, tier, first in reached:
            assert first.obj is not None
            tag = f"{claims.index(claim)}-{TIERS.index(tier)}"
            (t / f"once{tag}.yaml").write_text(_canonical(first.obj))
            (t / f"vv{tag}.yaml").write_text(yaml.safe_dump(_values(tier)))
            again = _apply(kyverno, t / "p.yaml", t / f"once{tag}.yaml", t / f"again{tag}",
                           t / f"vv{tag}.yaml")
            where = f"claim={claim or 'none'} rung={tier or 'unlabelled'}"
            if not again.applied or again.obj is None:
                said = [ln.strip() for ln in again.text.splitlines()
                        if ("error" in ln.lower() or "duplicate" in ln.lower())
                        and not _COUNTS.search(ln)]
                return Probe(name, path, False,
                             f"applied once at {where} and then FAILED on its own output "
                             f"(counts {again.counts}): {said[-1] if said else 'no verdict'} -- "
                             f"a mutation the engine cannot re-apply to an already-mutated "
                             f"object is a refusal of every UPDATE to a running pod")
            a, b = _canonical(first.obj), _canonical(again.obj)
            if a != b:
                return Probe(name, path, False,
                             f"NOT identical on an already-mutated object at {where} -- the "
                             f"second admission of a running pod rewrites it, and the API "
                             f"server refuses that. First difference: {_first_difference(a, b)}")
        note = "; ".join(changed) or "no change needed"
        rungs = ", ".join(sorted({t2 or "unlabelled" for _, t2, _ in reached}))
        # REVIEW, 2026-09-06 (F5). The sentence above used to name the rungs ATTEMPTED, not the
        # rungs OBSERVED: dropping the tier label from _values() left it byte-identical while
        # all five probes landed on the same fail-closed rung. A body that reads its Namespace's
        # tier must produce at least two DIFFERENT objects across the ladder, or the values file
        # is not reaching it and this leg is measuring one rung five times.
        seen = {t2 or "unlabelled": _canonical(r.obj) for _, t2, r in reached if r.obj}
        distinct = len(set(seen.values()))
        if _rung_dependent(doc) and distinct < 2:
            return Probe(name, path, False,
                         f"this body reads its Namespace's tier and yet every rung it reached "
                         f"({rungs}) produced the SAME object: the values file is not reaching "
                         f"it, so the rungs are attempted and not observed, and the identity "
                         f"above is one rung measured {len(seen)} times")
        return Probe(name, path, True,
                     f"identical applied to its own output on every rung it reaches ({rungs}), "
                     f"which produced {distinct} distinct object(s)"
                     + ("" if _rung_dependent(doc) else " -- this body does not read the tier")
                     + f"; throwaway copy: {note}")


def _rung_dependent(doc: dict) -> bool:
    """Does this body's output depend on the Namespace's declared tier?

    If it does, the ladder is observable and leg B must prove it walked it. If it does not
    (`stamp-posture` writes one label whatever the rung), one object across five rungs is the
    correct result and saying so is the honest report.
    """
    text = yaml.safe_dump(doc.get("spec") or {})
    return "namespaceObject" in text and "posture.acme.io/tier" in text


def _first_difference(a: str, b: str) -> str:
    la, lb = a.splitlines(), b.splitlines()
    for i in range(max(len(la), len(lb))):
        x = la[i] if i < len(la) else "<end>"
        y = lb[i] if i < len(lb) else "<end>"
        if x != y:
            return f"line {i + 1}: {x.strip()!r} vs {y.strip()!r}"
    return "lengths differ with no differing line"


def collect(root: Path) -> list[tuple[dict, str]]:
    """Every UPDATE-scoped mutating policy on the SERVED surface, with the file it came from."""
    mutations, _, _ = rs.scan_tree(root)
    wanted = {(m.name, m.path) for m in mutations
              if m.surface in rs.GRADED_SURFACES and "UPDATE" in m.operations}
    out: list[tuple[dict, str]] = []
    clone = root / ".estate-clone"
    for name, rel in sorted(wanted):
        f = clone / rel
        if not f.is_file():
            continue
        for doc in rs.read_documents(f.read_text()):
            if (doc.get("metadata") or {}).get("name") == name and doc.get("kind") in rs.MUTATING_KINDS:
                out.append((doc, rel))
    return out


def selfcheck(kyverno: str) -> int:
    """The plant: the 2026-08-28 sidecar, replayed from the estate's own body.

    `cage-tier`'s container map SKIPS a container named `waf-sidecar` and the sidecar block
    re-declares it; that filter is the whole 2026-08-28 fix. Remove it from a throwaway copy and
    the second application appends the sidecar again -- which is the defect, and leg B must go
    red on it. If it does not, this leg is not measuring anything.
    """
    ok, why = assert_no_update_mode(kyverno)
    print(f"  {'ok  ' if ok else 'FAIL'} no-UPDATE-mode probe: {why}")
    if not ok:
        return 1
    body = ('Object{spec: Object.spec{containers: '
            'object.spec.containers.filter(c, c.name != "waf-sidecar").map(c, '
            'Object.spec.containers{name: c.name}) + [Object.spec.containers{'
            'name: "waf-sidecar", image: "ghcr.io/acme/coraza-waf:cage"}]}}')
    doc = {"apiVersion": "policies.kyverno.io/v1alpha1", "kind": "MutatingPolicy",
           "metadata": {"name": "cage-fixture"},
           "spec": {"matchConstraints": {"resourceRules": [
               {"apiGroups": [""], "apiVersions": ["v1"], "operations": ["CREATE", "UPDATE"],
                "resources": ["pods"]}]},
               "mutations": [{"patchType": "ApplyConfiguration",
                              "applyConfiguration": {"expression": body}}]}}
    good = probe(kyverno, doc, "<fixture: the 2026-08-28 body AFTER the fix>")
    print(f"  {'ok  ' if good.ok else 'FAIL'} the fixed body: {good.detail}")
    broken = copy.deepcopy(doc)
    broken["spec"]["mutations"][0]["applyConfiguration"]["expression"] = body.replace(
        '.filter(c, c.name != "waf-sidecar")', "")
    bad = probe(kyverno, broken, "<fixture: the 2026-08-28 body BEFORE the fix, ticket 26>")
    print(f"  {'ok  ' if not bad.ok else 'FAIL'} the 2026-08-28 body: "
          f"{'caught -- ' + bad.detail if not bad.ok else 'PASSED, so this leg measures nothing'}")
    # ...and a policy that matches nothing must FAIL rather than pass quietly
    nothing = copy.deepcopy(doc)
    nothing["spec"]["matchConditions"] = [{"name": "never",
                                           "expression": "object.metadata.name == 'no-such-pod'"}]
    none = probe(kyverno, nothing, "<fixture: a policy that matches nothing>")
    print(f"  {'ok  ' if not none.ok else 'FAIL'} a policy that applies to nothing: "
          f"{'refused to pass -- ' + none.detail if not none.ok else 'PASSED on an empty run'}")
    return 0 if (good.ok and not bad.ok and not none.ok) else 1


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parents[1]))
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args(argv)
    kyverno = shutil.which("kyverno")
    if not kyverno:
        print("SKIP: the kyverno CLI is not on PATH, so no mutation could be executed and leg B "
              "measured nothing")
        return 3
    if args.selfcheck:
        return selfcheck(kyverno)
    ok, why = assert_no_update_mode(kyverno)
    print(f"  {'ok  ' if ok else 'FAIL'} {why}")
    if not ok:
        return 1
    probes = [probe(kyverno, doc, path) for doc, path in collect(Path(args.root).resolve())]
    for p in probes:
        print(f"  {'ok  ' if p.ok else 'FAIL'} {p.policy} ({p.path}): {p.detail}")
    if not probes:
        print("FAIL: no UPDATE-scoped mutation was found on the served surface at all, so this "
              "leg measured nothing -- either the clone is missing or the scan stopped scanning")
        return 1
    bad = [p for p in probes if not p.ok]
    if bad:
        print(f"FAIL: {len(bad)} of {len(probes)} UPDATE-scoped mutations are not byte-identical "
              f"on an already-mutated object")
        return 1
    print(f"  {len(probes)} UPDATE-scoped mutations applied to their own output, byte for byte")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
