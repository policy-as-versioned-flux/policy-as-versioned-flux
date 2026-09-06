#!/usr/bin/env python3
"""replays.py -- the four instances, replayed against the estate's OWN bodies.

A grader that has never gone red is a grader nobody has tested. Each replay below takes a real
body out of the estate clone, puts it back in the state the defect was in, and requires the
check to FAIL on it. Where a body is no longer on disk the replay says so and derives the
fixture from the served body instead, so a check cannot go quietly untested because history was
tidied away.

  1a. THE PRIORITY TRIO (2026-08-28, ticket 26). `distribution/policies/v2.0.0/cage-tier.yaml`
      is still on disk, retired from the array and pruned from every cluster. It writes
      `priorityClassName` and neither `priority` nor `preemptionPolicy`, which is exactly why
      every 2.x and 3.x line refused every pod. Leg D must go red on it.
  1b. THE DUPLICATE SIDECAR (2026-08-28, ticket 26). The served cage body with its
      `.filter(c, c.name != "waf-sidecar")` removed -- the whole of that day's fix. Leg B must
      go red on it, and can only do so by RUNNING it.
  2.  THE UNSUFFIXED PRIORITYCLASS (2026-09-05, ticket 89 round 2). `graded/policies/
      cage-tier.yaml` is the authoring body the machinery cage was copied from, and its dial
      table names `cage-baseline`, `cage-restricted`, `cage-quarantine`, `cage-isolated` --
      unsuffixed, because it belongs to no version. Put that body in a served version's release
      group, where every class is suffixed, and leg A must go red on all four names.
  3.  THE FULL CAGE BODY ON UPDATE (2026-09-05, ticket 89 round 2). The served cage body on a
      policy the register does not cover, matching UPDATE. Leg C must go red: a container
      appended to an immutable list and two immutable priority fields rewritten on a running
      pod.
  4.  THE LIVE ONE (2026-09-05, ticket 89 S3). Not a defect and not replayed: the served
      `cage-tier` writes those same fields on UPDATE today, and the register records the
      decision. The assertion is that the check REPORTS it, names the remediation, and would go
      red if the row stopped describing the code.
"""

from __future__ import annotations

import copy
import shutil
import sys
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import refusal_probe as rp  # noqa: E402
import refusal_scan as rs  # noqa: E402

ROOT = HERE.parents[1]
CLONE = ROOT / ".estate-clone"


def _apply_expression(doc: dict) -> str | None:
    """The body's first ApplyConfiguration expression, or None if it has none.

    REVIEW, 2026-09-06 (F6). Every replay reached into `mutations[0]` and crashed with an
    IndexError when the served body's `mutations` was emptied -- a traceback instead of the
    replay's own "the estate's body changed, rewrite this replay" sentence, which is the whole
    point of a replay saying it can no longer put the defect back.
    """
    for mut in ((doc.get("spec") or {}).get("mutations") or []):
        expr = (mut.get("applyConfiguration") or {}).get("expression")
        if expr:
            return str(expr)
    return None


def _served_cage() -> tuple[dict, str]:
    """The cage body the estate SERVES today: declared, cut, and reconciled by a Kustomization."""
    mutations, _, _ = rs.scan_tree(ROOT)
    served = [m for m in mutations
              if m.surface == "served-cut" and m.name.startswith("cage-tier")]
    if not served:
        raise SystemExit("no served cage-tier on the surface at all -- nothing to replay against")
    m = sorted(served, key=lambda x: x.path)[-1]
    for doc in rs.read_documents((CLONE / m.path).read_text()):
        if (doc.get("metadata") or {}).get("name") == m.name:
            return doc, m.path
    raise SystemExit(f"could not re-read {m.path}")


def replay_1a() -> bool:
    body = CLONE / "platform/distribution/policies/v2.0.0/cage-tier.yaml"
    docs = ([d for d in rs.read_documents(body.read_text()) if d.get("kind") in rs.MUTATING_KINDS]
            if body.is_file() else [])
    if docs and _apply_expression(docs[0]):
        doc = docs[0]
        where = "platform/distribution/policies/v2.0.0/cage-tier.yaml, the real retired body"
    else:
        doc, path = _served_cage()
        doc = copy.deepcopy(doc)
        expr = _apply_expression(doc)
        if expr is None:
            print("  FAIL replay 1a: neither the retired v2.0.0 body nor the served cage carries "
                  "an ApplyConfiguration expression any more, so this replay cannot put the "
                  "2026-08-28 priority trio back -- rewrite it")
            return False
        for drop in ("priority: int(variables.dial.prio),", 'preemptionPolicy: "Never",'):
            expr = expr.replace(drop, "")
        doc["spec"]["mutations"][0]["applyConfiguration"]["expression"] = expr
        where = f"derived from {path} (v2.0.0 is no longer on disk)"
    broken = rs.priority_trio(rs.mutation(doc, surface="served-cut"))
    print(f"  {'ok  ' if broken else 'FAIL'} replay 1a, the priority trio ({where}): "
          f"{broken[0].why[:120] if broken else 'NOT CAUGHT -- leg D grades nothing'}")
    return bool(broken)


def replay_1b(kyverno: str) -> bool:
    doc, path = _served_cage()
    broken = copy.deepcopy(doc)
    expr = _apply_expression(broken)
    if expr is None:
        print("  FAIL replay 1b: the served cage carries no ApplyConfiguration expression any "
              "more, so the 2026-08-28 sidecar cannot be put back -- rewrite this replay")
        return False
    if '.filter(c, c.name != "waf-sidecar")' not in expr:
        print("  FAIL replay 1b: the served cage no longer carries the 2026-08-28 sidecar "
              "filter, so this replay cannot put the defect back -- rewrite it")
        return False
    broken["spec"]["mutations"][0]["applyConfiguration"]["expression"] = expr.replace(
        '.filter(c, c.name != "waf-sidecar")', "")
    p = rp.probe(kyverno, broken, f"<{path} with the 2026-08-28 sidecar filter removed>")
    print(f"  {'ok  ' if not p.ok else 'FAIL'} replay 1b, the duplicate sidecar ({path}): "
          f"{p.detail if not p.ok else 'NOT CAUGHT -- leg B grades nothing'}")
    return not p.ok


def replay_2() -> bool:
    authoring = CLONE / "platform/graded/policies/cage-tier.yaml"
    authored = ([d for d in rs.read_documents(authoring.read_text())
                 if d.get("kind") in rs.MUTATING_KINDS] if authoring.is_file() else [])
    if authored and rs.reference_names(authored[0]):
        doc = authored[0]
        where = "platform/graded/policies/cage-tier.yaml, the authoring body it was copied from"
    else:
        doc, path = _served_cage()
        doc = copy.deepcopy(doc)
        for var in (doc.get("spec") or {}).get("variables") or []:
            var["expression"] = str(var.get("expression", "")).replace("-4-0-0", "").replace(
                "-5-0-0", "")
        if not rs.reference_names(doc):
            print("  FAIL replay 2: no served cage writes a reference field any more, so the "
                  "unsuffixed PriorityClass cannot be replayed -- rewrite this replay")
            return False
        where = f"derived from {path} (the authoring body is no longer on disk)"
    m = rs.mutation(doc, path=where, surface="served-cut", group="platform:v4.0.0")
    _, groups, _ = rs.scan_tree(ROOT)
    shipped = groups.get("platform:v4.0.0", {})
    dangling = rs.dangling_references(m, shipped)
    names = ", ".join(d.name for d in dangling)
    print(f"  {'ok  ' if dangling else 'FAIL'} replay 2, the unsuffixed PriorityClass ({where}): "
          f"{'names ' + names + ' where the release ships ' + ', '.join(sorted(shipped.get('PriorityClass') or [])) if dangling else 'NOT CAUGHT -- leg A grades nothing'}")
    return bool(dangling)


def replay_3(register: dict) -> bool:
    doc, path = _served_cage()
    doc = copy.deepcopy(doc)
    if _apply_expression(doc) is None:
        print("  FAIL replay 3: the served cage writes nothing, so the full-body-on-UPDATE shape "
              "cannot be replayed -- rewrite this replay")
        return False
    # ticket 89 round 2's shape: the bottom-rung cage, full body, matching UPDATE. The register
    # covers `cage-tier*` and nothing else, so this must be an unrecorded hazard.
    doc["metadata"]["name"] = "governed-namespace-cage"
    for rule in doc["spec"]["matchConstraints"]["resourceRules"]:
        rule["operations"] = ["CREATE", "UPDATE"]
    m = rs.mutation(doc, path=path, surface="served-cut", group="platform:v4.0.0")
    _, groups, _ = rs.scan_tree(ROOT)
    v = rs.grade([m], groups.get("platform:v4.0.0", {}), register)
    caught = v.code == 1 and any("no register row" in ln for ln in v.lines)
    n = len([ln for ln in v.lines if "no register row" in ln])
    print(f"  {'ok  ' if caught else 'FAIL'} replay 3, the full cage body on UPDATE "
          f"(governed-namespace-cage, from {path}): "
          f"{str(n) + ' unrecorded writes on a running pod' if caught else 'NOT CAUGHT -- leg C grades nothing'}")
    return caught


def replay_4(register: dict) -> bool:
    mutations, groups, _ = rs.scan_tree(ROOT)
    v = rs.grade(mutations, groups, register)
    # The question is about the ROW, not about the whole run's exit code. Asking `v.code == 0`
    # made any could-not-look anywhere -- an unplaceable path, an untabulated resource, an
    # unresolvable name -- report a stale register row that was not stale, and exit the run
    # before the SKIP line the manifest declares could ever be printed (review R1).
    ok, why = rs.live_instance_reported(v)
    print(f"  {'ok  ' if ok else 'FAIL'} instance 4, LIVE and decided: "
          f"{'reported as an accepted refusal with its remediation, not as a defect' if ok else why}")
    # ...and the row is not a blanket permission: narrow it and the check goes red
    narrowed = copy.deepcopy(register)
    if narrowed.get("accepted"):
        narrowed["accepted"][0]["fields"] = ["spec.priorityClassName"]
    still_red = rs.grade(mutations, groups, narrowed).code == 1
    print(f"  {'ok  ' if still_red else 'FAIL'} the acceptance is not a blanket permission: a "
          f"row narrower than the code {'fails' if still_red else 'PASSES, so the row grades nothing'}")
    return ok and still_red


def main() -> int:
    kyverno = shutil.which("kyverno")
    if not kyverno:
        print("FAIL: the kyverno CLI is not on PATH, so the replay that can only be measured by "
              "RUNNING a policy could not run")
        return 1
    register = yaml.safe_load((HERE / "register.yaml").read_text()) or {}
    results = [replay_1a(), replay_1b(kyverno), replay_2(), replay_3(register),
               replay_4(register)]
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
