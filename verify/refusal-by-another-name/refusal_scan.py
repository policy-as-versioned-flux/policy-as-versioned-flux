#!/usr/bin/env python3
"""refusal_scan.py -- a refusal by another name: a MUTATION whose product the API server rejects.

Eco-system ticket 98. The estate's doctrine is that nothing is denied and a workload that does
not fit its cage runs on a tighter rung; ticket 89 built the register that grades every
Deny-shaped rule. Nothing graded the other direction. A mutating policy carries no Deny-shaped
text at all and can still stop a workload dead, four ways this estate has actually produced:

  1. 2026-08-28 (ticket 26). `spec.priorityClassName` written from a mutating webhook without
     the `spec.priority` and `spec.preemptionPolicy` the built-in Priority admission plugin
     re-derives from that same class. Every pod on every released line was refused:
       "the integer value of priority (0) must not be provided in pod spec; priority admission
        controller computed -10 from the given PriorityClass name"
     Same day, same class of thing: a `waf-sidecar` appended unconditionally, so the SECOND
     admission of an already-caged pod produced `duplicate entries for key [name="waf-sidecar"]`
     and the API server refused every `kubectl label` on a running caged pod.
  2. 2026-09-05 (ticket 89 round 2). A machinery cage named the PriorityClass `cage-isolated`
     while every class the estate SHIPS is version-suffixed (`cage-isolated-4-0-0`). The plain
     name existed on no cluster, and the Priority plugin refuses a pod naming a class that does
     not exist. The cage built to REPLACE a refusal would have made every pod it caged
     inadmissible.
  3. 2026-09-05 (ticket 89 round 2, again). An UPDATE arm on the bottom-rung cage, applying the
     full cage body to a RUNNING pod: a container appended to an immutable list,
     `priorityClassName` and `priority` rewritten. It would have refused ticket 91's currency
     controller re-cage patch.
  4. LIVE TODAY, and decided rather than fixed (ticket 89 S3). A pod the guard caged on the
     bottom rung, given a served-version claim, is taken over by `cage-tier`, which rewrites
     `tier`, `priorityClassName` and `priority` -- the last two immutable on a running pod. The
     API server refuses the edit, and ticket 89 decided that refusal is the CORRECT outcome:
     letting it through would be a workload moving itself off the bottom rung by asserting a
     label, the self-service exemption principle 1 bans. The remediation is a recreate.

So the fourth instance must be REPORTED without being called a defect, which is what
`register.yaml` is for, and why the join below is graded in both directions: an unrecorded
hazard FAILS, and a row that no longer describes the code FAILS too.

WHAT IS CHECKABLE OFFLINE. Whether an API server accepts a mutated object depends on the
cluster. Three things do not, and between them they catch all four:

  A. every name a mutation writes into a REFERENCE field must be one the same release ships
     (`reference_names` / `dangling_references`) -- instance 2;
  B. an UPDATE-scoped mutation must be byte-identical applied to an already-mutated object
     (this file supplies the facts; the shell script executes it, because reading a body has
     never once caught one of these) -- instance 1's sidecar;
  D. a mutation that writes `priorityClassName` must write the whole priority trio
     (`priority_trio`) -- instance 1's trio;
  C. a field a mutation writes must be one the resource allows to change on that OPERATION
     (`hazards`, joined to `register.yaml`) -- instances 3 and 4.

THE SERVED SURFACE, not a proxy for it. `classify()` is the whole definition of what is graded.
A version directory on disk is NOT a served policy: `distribution/policies/v2.0.0/` exists and
no cluster carries it, because the array in `versions.yaml` no longer declares it. An element
the array declares with no `commit` is an UNCUT tail: no signed tag exists, so Flux delivers
nothing (the same `cut`/`uncut` partition `verify-declared-versions-admit.sh` uses, and for the
same reason). `graded/policies/` is an AUTHORING tree that no Kustomization applies, and
reasoning from it is the round-1 mistake ticket 89 shipped and had caught.

Usage:
    refusal_scan.py [--root DIR] [--register FILE]   # the verdict, exit 0/1/3
    refusal_scan.py --inventory                      # every mutation found, one row each
    refusal_scan.py --selfcheck                      # the grader's own asserts
"""

from __future__ import annotations

import argparse
import fnmatch
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

#: What this scan cannot see. Every line is DATED, because a disclosed limit is an assertion and
#: goes stale like any other one (ludlow's harness disclosed "cannot prove cosign ACCEPTS a valid
#: bundle" and that became false without anyone noticing). Two of these are not prose at all:
#: the kyverno CLI's missing UPDATE mode is MEASURED on every run by the shell script's step 0,
#: and the absence of a cluster is the live tail's own exit 3.
BLIND_SPOTS = (
    "2026-09-06: whether the API SERVER accepts the mutated object. That is a cluster fact -- "
    "which PriorityClasses exist, which admission plugins are on, what the object looked like "
    "before -- and deciding it offline would be guessing. The live half is "
    "platform/graded/verify-graded.sh's cluster tail, which has never had a cluster on a "
    "citable run (review finding P2-6)",
    "2026-09-06: a mutation whose written VALUE differs from what the object already carries. "
    "Writing an immutable field on UPDATE only refuses when the value CHANGES, and whether it "
    "can change depends on the pod's namespace and labels at that moment. This scan grades the "
    "field and the operation; leg B measures byte-identity on an already-mutated object; "
    "neither can enumerate every object a policy will ever meet",
    "2026-09-06: the 2022 Kyverno ClusterPolicy's `rules[].mutate` and any other engine's "
    "mutation (Gatekeeper assign, a plain admission webhook). None ships in this estate today; "
    "the day one does, `mutation()` returns None for it and nothing here would have said so",
    "2026-09-06: only the POD's mutability table is tabulated (MUTABLE_ON_UPDATE). A mutation "
    "on any other resource is counted and NAMED as untabulated rather than graded -- a "
    "could-not-look, never a pass",
    "2026-09-06: a field written through a JSONPatch whose `path` is computed from something "
    "other than string concatenation of literals is read as a wildcard, so a narrower defect "
    "inside it is invisible",
    "2026-09-06: every tree is read at the clone's HEAD, and an ADOPTER serves the tree at the "
    "tag its own composed GitRepository pins (driftwood: v1.1.0). Where HEAD and that tag "
    "differ, the bytes graded are not the bytes served -- the same proxy this ticket is about, "
    "one level out. It bites nothing today because no adopter's composed-set array declares a "
    "version whose directory exists at HEAD, and every such directory is NAMED in the excluded "
    "list on each run. Closing it means reading each path out of `git show <pinned tag>:<path>`",
)

# ------------------------------------------------------------------ the pod mutability table

#: What a running pod ALLOWS to change on UPDATE. Everything else under `spec` is immutable, so
#: a mutation that writes it on UPDATE turns a change into a refusal. Kubernetes' own list
#: (pkg/api/pod/util.go, `ValidatePodUpdate`): the image of a container or initContainer,
#: `activeDeadlineSeconds`, `tolerations` (additions only) and `terminationGracePeriodSeconds`
#: (downward, for eviction). `metadata` and `status` are freely mutable, which is exactly why
#: ticket 89's labels-only holds are safe on UPDATE where the full cage body is not.
MUTABLE_ON_UPDATE = (
    "metadata",
    "status",
    "spec.containers[*].image",
    "spec.initContainers[*].image",
    "spec.activeDeadlineSeconds",
    "spec.tolerations",
    "spec.terminationGracePeriodSeconds",
)

#: Why a particular write is a refusal, where the estate has observed the sentence. Anything not
#: named here gets the general reason.
IMMUTABLE_WHY = {
    "spec.priorityClassName":
        "the Priority admission plugin recomputes priority from the class and the API server "
        "refuses the change on a running pod (observed live 2026-08-28, kind-driftwood)",
    "spec.priority":
        "`spec.priority` is derived by the Priority admission plugin and is immutable on a "
        "running pod",
    "spec.preemptionPolicy":
        "`spec.preemptionPolicy` is derived from the PriorityClass and is immutable on a "
        "running pod",
    "spec.containers":
        "a pod's container LIST is immutable: appending one produces "
        "`spec.containers: duplicate entries` or `field is immutable` (observed live "
        "2026-08-28, ticket 26)",
}
_RESOURCES_WHY = (
    "container resources are immutable except through in-place resize, which is feature-gated "
    "and does not cover limits on every resource"
)

#: A field whose VALUE is the name of another object. `priorityClassName` is the one that bit.
REFERENCE_FIELDS = {
    "spec.priorityClassName": "PriorityClass",
    "spec.runtimeClassName": "RuntimeClass",
    "spec.serviceAccountName": "ServiceAccount",
    "spec.ingressClassName": "IngressClass",
    "spec.storageClassName": "StorageClass",
}
REFERENCE_KINDS = frozenset(REFERENCE_FIELDS.values())

#: The trio the Priority admission plugin re-derives from a PriorityClass. Writing one without
#: the other two refuses the pod outright; it took the whole estate down on 2026-08-28.
PRIORITY_TRIO = ("spec.priorityClassName", "spec.priority", "spec.preemptionPolicy")

#: Fields of a pod spec that are lists, so a typed constructor naming one addresses an ELEMENT.
LIST_FIELDS = frozenset({
    "containers", "initContainers", "ephemeralContainers", "volumes", "tolerations",
    "imagePullSecrets", "hostAliases", "env", "ports", "volumeMounts", "envFrom",
})

MUTATING_KINDS = frozenset({"MutatingPolicy"})
SUPPORTED_RESOURCES = frozenset({"pods"})

SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".work", ".estate-clone", "estate"}


# ------------------------------------------------------------------------------- the parsers

_CONSTRUCTOR = re.compile(r"\bObject((?:\.[A-Za-z_][A-Za-z0-9_]*)*)\s*\{")
_KEY = re.compile(r"""\s*(["']?)([A-Za-z_][A-Za-z0-9_./-]*)\1\s*:""")


def _segment(name: str) -> str:
    """One path segment, marked as a list element where the pod schema says it is a list."""
    return f"{name}[*]" if name in LIST_FIELDS else name


def _constructor_path(dotted: str) -> str:
    """`.spec.containers` -> `spec.containers[*]`. A typed constructor naming a LIST field
    constructs one ELEMENT of it -- `Object.spec.containers{name: ...}` is a container, not the
    list -- so the segment carries the wildcard."""
    return ".".join(_segment(p) for p in dotted.split(".") if p)


def _keys_at_top_level(text: str, start: int) -> list[str]:
    """The keys of one brace-delimited object literal, at ITS level only.

    Only a token in KEY POSITION counts -- the first thing after the opening brace or after a
    comma at that depth. That is what keeps a ternary's `:` (`a ? b : c`) and a nested map's own
    keys out: both sit in value position.
    """
    depth = 0
    i = start
    keys: list[str] = []
    expect_key = False
    n = len(text)
    while i < n:
        ch = text[i]
        if ch in "\"'":
            quote = ch
            j = i + 1
            while j < n and text[j] != quote:
                j += 2 if text[j] == "\\" else 1
            if expect_key and depth == 1:
                m = _KEY.match(text, i)
                if m:
                    keys.append(m.group(2))
                    i = m.end()
                    expect_key = False
                    continue
            i = j + 1
            expect_key = False
            continue
        if ch in "{[(":
            depth += 1
            expect_key = ch == "{" and depth == 1
            i += 1
            continue
        if ch in "}])":
            depth -= 1
            if depth == 0:
                break
            expect_key = False
            i += 1
            continue
        if ch == "," and depth == 1:
            expect_key = True
            i += 1
            continue
        if ch.isspace():
            i += 1
            continue
        if expect_key and depth == 1:
            m = _KEY.match(text, i)
            if m:
                keys.append(m.group(2))
                i = m.end()
                expect_key = False
                continue
        expect_key = False
        i += 1
    return keys


def object_literal_paths(expr: str) -> set[str]:
    """Every field path a CEL `ApplyConfiguration` expression writes.

    The typed constructor carries the path: `Object.spec.containers.resources{limits: ...}`
    writes `spec.containers[*].resources.limits`. A path that is only the PREFIX of another
    written path is dropped -- writing `spec.containers` by writing its elements is one write,
    not two -- so the set is the leaves the mutation actually sets.
    """
    paths: set[str] = set()
    for m in _CONSTRUCTOR.finditer(expr):
        base = _constructor_path(m.group(1))
        for key in _keys_at_top_level(expr, m.end() - 1):
            paths.add(f"{base}.{_segment(key)}" if base else _segment(key))
    return _collapse(paths)


def _collapse(paths: set[str]) -> set[str]:
    return {p for p in paths
            if not any(q != p and (q.startswith(p + ".") or q.startswith(p + "[*]"))
                       for q in paths)}


_JSONPATCH_PATH = re.compile(r"""\bpath\s*:\s*""")
_STRING = re.compile(r"""(["'])((?:\\.|(?!\1).)*)\1""")


def jsonpatch_paths(expr: str) -> set[str]:
    """Every field path a CEL `JSONPatch` expression writes.

    `"/spec/containers/" + string(...) + "/securityContext/capabilities"` is read as
    `spec.containers[*].securityContext.capabilities`: the literal chunks are kept and every
    computed chunk becomes the wildcard index it is.
    """
    out: set[str] = set()
    for m in _JSONPATCH_PATH.finditer(expr):
        i, n = m.end(), len(expr)
        depth = 0
        chunks: list[str] = []
        buf = ""
        while i < n:
            ch = expr[i]
            if ch in "\"'":
                s = _STRING.match(expr, i)
                if not s:
                    break
                buf += s.group(2)
                i = s.end()
                continue
            if ch in "{[(":
                depth += 1
            elif ch in "}])":
                if depth == 0:
                    break
                depth -= 1
            elif depth == 0 and ch == ",":
                break
            elif depth == 0 and ch == "+":
                i += 1
                continue
            elif depth == 0 and not ch.isspace():
                # a computed chunk: an index, a name, anything not a literal
                chunks.append(buf)
                buf = ""
                j = i
                while j < n and (expr[j].isalnum() or expr[j] in "._"):
                    j += 1
                if j < n and expr[j] == "(":
                    d = 0
                    while j < n:
                        if expr[j] == "(":
                            d += 1
                        elif expr[j] == ")":
                            d -= 1
                            if d == 0:
                                j += 1
                                break
                        j += 1
                chunks.append("\x00")
                i = max(j, i + 1)
                continue
            i += 1
        chunks.append(buf)
        raw = "".join(chunks)
        segs: list[str] = []
        for seg in raw.split("/"):
            if not seg:
                continue
            if "\x00" in seg or seg.isdigit():
                if segs:
                    segs[-1] = f"{segs[-1]}[*]"
                continue
            segs.append(seg)
        if segs:
            out.add(".".join(segs))
    return _collapse(out)


def written_paths(doc: dict) -> set[str]:
    """Every field path every mutation in one policy writes."""
    out: set[str] = set()
    for mut in ((doc.get("spec") or {}).get("mutations") or []):
        apply_cfg = (mut.get("applyConfiguration") or {}).get("expression")
        if apply_cfg:
            out |= object_literal_paths(apply_cfg)
        patch = (mut.get("jsonPatch") or {}).get("expression")
        if patch:
            out |= jsonpatch_paths(patch)
    return _collapse(out)


def _value_expression(expr: str, key: str) -> str | None:
    """The raw value text a CEL object literal assigns to `key`, at any depth."""
    pat = re.compile(r"""(?:^|[{,])\s*["']?""" + re.escape(key) + r"""["']?\s*:""")
    m = pat.search(expr)
    if not m:
        return None
    i, n = m.end(), len(expr)
    depth = 0
    buf = ""
    while i < n:
        ch = expr[i]
        if ch in "\"'":
            s = _STRING.match(expr, i)
            if s:
                buf += s.group(0)
                i = s.end()
                continue
        if ch in "{[(":
            depth += 1
        elif ch in "}])":
            if depth == 0:
                break
            depth -= 1
        elif depth == 0 and ch == ",":
            break
        buf += ch
        i += 1
    return buf.strip()


@dataclass(frozen=True)
class Reference:
    """A reference field a mutation writes, and the names it can write into it."""

    field: str
    kind: str
    names: frozenset[str]
    unresolved: bool
    expression: str


_VAR_REF = re.compile(r"^variables\.([A-Za-z_][A-Za-z0-9_]*)\.([A-Za-z_][A-Za-z0-9_]*)$")
_VAR_PLAIN = re.compile(r"^variables\.([A-Za-z_][A-Za-z0-9_]*)$")


def reference_names(doc: dict) -> dict[str, Reference]:
    """Every reference field the policy writes, resolved to the literal names it can write.

    Two shapes resolve: a literal (`priorityClassName: "cage-isolated"`) and a lookup into a
    variable whose expression is a map of maps (`variables.dial.pc`, which is how the estate's
    cage carries one dial table per rung). Anything else is UNRESOLVED and is reported as a
    could-not-look, never as a pass: a name this file cannot read is a name it cannot grade.
    """
    variables = {v.get("name"): v.get("expression", "")
                 for v in ((doc.get("spec") or {}).get("variables") or [])}
    out: dict[str, Reference] = {}
    for mut in ((doc.get("spec") or {}).get("mutations") or []):
        expr = (mut.get("applyConfiguration") or {}).get("expression") or ""
        for path, kind in REFERENCE_FIELDS.items():
            leaf = path.rsplit(".", 1)[1]
            value = _value_expression(expr, leaf)
            if value is None:
                continue
            names, unresolved = _resolve(value, variables)
            out[path] = Reference(path, kind, frozenset(names), unresolved, value)
    return out


_INDEXED = re.compile(
    r"""\}\s*\[\s*(?:variables\.([A-Za-z_][A-Za-z0-9_]*)|["']([^"']+)["'])\s*\]\s*$""")


def _row_of(table: str, variables: dict[str, str]) -> str:
    """One row of a dial table, when the table is indexed by a key this file can pin.

    The machinery cages share `cage-tier`'s dial table and index it with a `tier` variable pinned
    to the literal `'isolated'` (ticket 89 D2: what the ladder cannot place goes to the bottom).
    Reading every rung's PriorityClass out of that table would demand the machinery ship three
    classes no policy of its can ever name -- a red that is WRONG, which is worse than no check.
    Where the index is computed (`cage-tier`'s own ternary), every rung is reachable and every
    row is read.
    """
    m = _INDEXED.search(table.strip())
    if not m:
        return table
    key = m.group(2)
    if key is None:
        pinned = variables.get(m.group(1) or "", "").strip()
        lit = _STRING.fullmatch(pinned)
        if not lit:
            return table
        key = lit.group(2)
    at = re.search(r"""["']""" + re.escape(key) + r"""["']\s*:\s*\{""", table)
    if not at:
        return table
    start = table.index("{", at.end() - 1)
    depth = 0
    for i in range(start, len(table)):
        if table[i] == "{":
            depth += 1
        elif table[i] == "}":
            depth -= 1
            if depth == 0:
                return table[start:i + 1]
    return table


def _resolve(value: str, variables: dict[str, str]) -> tuple[set[str], bool]:
    lit = _STRING.fullmatch(value.strip())
    if lit:
        return {lit.group(2)}, False
    m = _VAR_REF.match(value.strip())
    if m and m.group(1) in variables:
        table = _row_of(variables[m.group(1)], variables)
        key = m.group(2)
        found = re.findall(r"""["']?""" + re.escape(key) + r"""["']?\s*:\s*["']([^"']+)["']""",
                           table)
        if found:
            return set(found), False
        return set(), True
    m2 = _VAR_PLAIN.match(value.strip())
    if m2 and m2.group(1) in variables:
        return _resolve(variables[m2.group(1)], {})
    return set(), True


# ------------------------------------------------------------------------------ the facts

@dataclass(frozen=True)
class Mutation:
    """One mutating policy, and what it writes where."""

    name: str
    path: str
    unit: str
    surface: str
    group: str
    operations: tuple[str, ...]
    resources: tuple[str, ...]
    writes: frozenset[str]
    references: dict[str, Reference] = field(compare=False, default_factory=dict)

    @property
    def untabulated(self) -> bool:
        """A resource whose mutability this file does not tabulate. Named, never graded."""
        return bool(self.resources) and not (set(self.resources) & SUPPORTED_RESOURCES)


def mutation(doc: dict, path: str = "-", unit: str = "-", surface: str = "served-cut",
             group: str = "-") -> Mutation | None:
    """The facts of one document, or None if it is not a mutating policy at all."""
    if not isinstance(doc, dict) or doc.get("kind") not in MUTATING_KINDS:
        return None
    spec = doc.get("spec") or {}
    rules = ((spec.get("matchConstraints") or {}).get("resourceRules") or [])
    ops: list[str] = []
    res: list[str] = []
    for rule in rules:
        ops += list(rule.get("operations") or [])
        res += list(rule.get("resources") or [])
    return Mutation(
        name=((doc.get("metadata") or {}).get("name") or "?"),
        path=path, unit=unit, surface=surface, group=group,
        operations=tuple(dict.fromkeys(ops)), resources=tuple(dict.fromkeys(res)),
        writes=frozenset(written_paths(doc)), references=reference_names(doc),
    )


@dataclass(frozen=True)
class Hazard:
    """A field written on an operation the resource does not allow it to change on."""

    policy: str
    path: str
    operation: str
    why: str


def is_mutable_on_update(path: str) -> bool:
    return any(path == m or path.startswith(m + ".") or path.startswith(m + "[*]")
               for m in MUTABLE_ON_UPDATE)


def hazards(m: Mutation | None) -> tuple[Hazard, ...]:
    """Every write this mutation makes on an operation that does not allow it.

    Only UPDATE is graded, and only for pods: a CREATE writes a pod that does not exist yet, so
    no field of it is immutable.
    """
    if m is None or "UPDATE" not in m.operations or m.untabulated:
        return ()
    out = []
    for path in sorted(m.writes):
        if is_mutable_on_update(path):
            continue
        why = IMMUTABLE_WHY.get(path)
        if why is None and ".resources" in path:
            why = _RESOURCES_WHY
        if why is None:
            why = "a pod's spec is immutable after creation except for the fields in " \
                  "MUTABLE_ON_UPDATE, so writing this on UPDATE turns the mutation into a refusal"
        out.append(Hazard(m.name, path, "UPDATE", why))
    return tuple(out)


@dataclass(frozen=True)
class Dangling:
    """A name written into a reference field that the same release does not ship."""

    policy: str
    field: str
    name: str
    kind: str
    why: str


def dangling_references(m: Mutation | None, shipped: dict[str, set[str]]) -> tuple[Dangling, ...]:
    """Every reference name the release this policy travels in does not ship."""
    if m is None:
        return ()
    out = []
    for ref in m.references.values():
        have = set(shipped.get(ref.kind) or set())
        for name in sorted(ref.names):
            if name not in have:
                out.append(Dangling(
                    m.name, ref.field, name, ref.kind,
                    f"no {ref.kind} named {name} ships in {m.group or 'this release'} "
                    f"(it ships {sorted(have) or 'none'}), so the admission plugin that resolves "
                    f"the reference refuses every object this mutation touches"))
    return tuple(out)


def unresolved_references(m: Mutation | None) -> tuple[Reference, ...]:
    if m is None:
        return ()
    return tuple(r for r in m.references.values() if r.unresolved)


@dataclass(frozen=True)
class Broken:
    """A mutation that writes part of the priority trio and not the rest."""

    policy: str
    missing: tuple[str, ...]
    why: str


def priority_trio(m: Mutation | None) -> tuple[Broken, ...]:
    """`priorityClassName` written without the two fields the plugin re-derives from it.

    Observed live on kind-driftwood, 2026-08-28: every released policy line refused every pod,
    because the mutating webhook wrote the class name and the Priority admission plugin's
    validating half then found `spec.priority: 0` in the pod it had already stamped.
    """
    if m is None or PRIORITY_TRIO[0] not in m.writes:
        return ()
    missing = tuple(f for f in PRIORITY_TRIO[1:] if f not in m.writes)
    if not missing:
        return ()
    return (Broken(m.name, missing, (
        "writes spec.priorityClassName without " + " and ".join(missing) +
        " -- the Priority admission plugin stamps priority before any webhook runs and then "
        "refuses the pod: \"the integer value of priority (0) must not be provided in pod spec; "
        "priority admission controller computed -10 from the given PriorityClass name\" "
        "(observed live 2026-08-28)")),)


# -------------------------------------------------------------------------- the served surface

@dataclass(frozen=True)
class Surface:
    surface: str
    graded: bool
    why: str


_VERSION_DIR = re.compile(r"policies/v(\d+\.\d+\.\d+)/")

GRADED_SURFACES = ("served-cut", "served-machinery", "pending")


def classify(path: str, declared: dict[str, set[str]], cut: dict[str, set[str]]) -> Surface:
    """Where this file sits between an authoring copy and a policy on a cluster.

    THE RULE THIS ENFORCES ON ITSELF (ticket 89's round-4 answer, and this ticket's own hard
    rule): name the SERVED artefact and the OPERATION that reaches it. A file existing is not a
    policy serving. Four ways a policy body on disk reaches nothing:

      * `graded/policies/` -- the authoring tree. `graded/up.sh` says in its own header that it
        applies ONLY the rendered, versioned copies, and no Kustomization anywhere references
        this path. Ticket 89 round 1 measured a configuration that exists nowhere by reading it.
      * a version directory the unit's own version array no longer declares: Flux prunes what
        the array drops, so `v2.0.0/` on disk is history, not service.
      * a version the array declares with no `commit`: an UNCUT tail. No signed tag exists, so
        Flux has nothing to deliver -- but it is graded anyway, because it is what the NEXT tag
        serves and a defect in it is one the estate is about to ship.
      * `vselfcheck/` -- a fixture directory for the renderers' own asserts.
    """
    unit = path.split("/", 1)[0]
    if "/graded/policies/" in "/" + path:
        return Surface("authoring", False,
                       "the authoring tree: no Kustomization anywhere applies graded/policies/, "
                       "and graded/up.sh applies only the rendered, versioned copies")
    if "/vselfcheck/" in path:
        return Surface("authoring", False, "a renderer's own fixture directory, served nowhere")
    if path.endswith("versions.yaml") or "composed-set.yaml" in path:
        return Surface("served-machinery", True,
                       "the ResourceSet flux-operator renders: the machinery policies, "
                       "installed beside every version tree and belonging to no version")
    m = _VERSION_DIR.search(path)
    if m:
        version = m.group(1)
        if version not in (declared.get(unit) or set()):
            return Surface("unserved-on-disk", False,
                           f"v{version} is on disk and {unit}'s version array does not declare "
                           f"it, so Flux has pruned it: history, not service")
        if version not in (cut.get(unit) or set()):
            return Surface("pending", True,
                           f"v{version} is declared with no commit -- an uncut tail, on no "
                           f"cluster, and what the next signed tag will serve")
        return Surface("served-cut", True,
                       f"v{version} is declared and cut, so a Kustomization reconciles it")
    if "/composed/" in "/" + path:
        return Surface("served-machinery", True,
                       "a composed machinery object the adopter's own Kustomization reconciles")
    return Surface("other", False, "not part of any policy delivery path this scan knows")


def read_documents(text: str) -> list[dict]:
    """Every YAML document in a file, INCLUDING the ones inside a ResourceSet template string.

    Ticket 89 learned this the hard way in the other direction: three of the estate's Denys live
    inside a `resourcesTemplate` STRING, where a `yaml.safe_load_all` walk sees a ResourceSet and
    no policy at all. The machinery cages live there too. Template directives are dropped (a line
    that is only `<< ... >>`) or replaced with a placeholder (inline), so the documents parse;
    a name or a value that came from a directive is therefore never read as a literal.
    """
    out: list[dict] = []
    for doc in _load_all(text):
        if not isinstance(doc, dict):
            continue
        out.append(doc)
        tmpl = (doc.get("spec") or {}).get("resourcesTemplate")
        if isinstance(tmpl, str):
            out += read_documents(_detemplate(tmpl))
    return out


#: What an unrendered template directive becomes. Distinctive on purpose: leg B DROPS a match
#: condition carrying it rather than evaluating a half-rendered expression, and says so.
TEMPLATE_MARK = "TEMPLATERANGED"


def _detemplate(text: str) -> str:
    kept = [ln for ln in text.splitlines() if not re.fullmatch(r"\s*<<.*>>\s*", ln)]
    return re.sub(r"<<[^>]*>>", TEMPLATE_MARK, "\n".join(kept))


def _load_all(text: str) -> list[object]:
    try:
        return [d for d in yaml.safe_load_all(text)]
    except yaml.YAMLError:
        out: list[object] = []
        for chunk in re.split(r"^---\s*$", text, flags=re.M):
            try:
                out.append(yaml.safe_load(chunk))
            except yaml.YAMLError:
                continue
        return out


def shipped_names(docs: list[dict]) -> dict[str, set[str]]:
    """The reference-able objects a set of documents ships, by kind."""
    out: dict[str, set[str]] = {}
    for doc in docs:
        kind = doc.get("kind")
        name = (doc.get("metadata") or {}).get("name")
        if kind in REFERENCE_KINDS and name:
            out.setdefault(str(kind), set()).add(str(name))
    return out


# ------------------------------------------------------------------------------- the join

@dataclass
class Verdict:
    code: int
    lines: list[str]


REQUIRED_ROW_FIELDS = ("policy", "operation", "fields", "decision", "reason", "remediation",
                       "recorded")


def _shipped_for(shipped: dict, group: str) -> dict[str, set[str]]:
    if shipped and all(isinstance(v, (set, list, tuple)) for v in shipped.values()):
        return {k: set(v) for k, v in shipped.items()}
    return {k: set(v) for k, v in (shipped.get(group) or {}).items()}


def grade(mutations: list[Mutation], shipped: dict, register: dict) -> Verdict:
    """The join. A hazard with no row FAILS; a row that no longer describes the code FAILS.

    An ACCEPTED row does not make the refusal go away -- it is printed on every run, with its
    reason and its remediation, because the estate decided instance 4 is the correct outcome and
    a decision that stops being visible stops being a decision.
    """
    fails: list[str] = []
    notes: list[str] = []
    could_not: list[str] = []
    rows = list((register or {}).get("accepted") or [])
    matched: dict[int, list[Hazard]] = {i: [] for i, _ in enumerate(rows)}

    graded = [m for m in mutations if m.surface in GRADED_SURFACES or m.surface == "-"]
    for m in graded:
        if m.untabulated:
            what = ",".join(m.resources) or "an unknown resource"
            could_not.append(
                f"  ??   {m.name} ({m.path}) mutates {what} and only the pod's mutability is "
                f"tabulated here -- not graded")
            continue
        for ref in unresolved_references(m):
            could_not.append(
                f"  ??   {m.name} ({m.path}) writes {ref.field} from `{ref.expression}` and this "
                f"scan could not resolve it to a name offline")
        for d in dangling_references(m, _shipped_for(shipped, m.group)):
            fails.append(f"  FAIL {d.policy} writes {d.field}: {d.name} -- {d.why}")
        for b in priority_trio(m):
            fails.append(f"  FAIL {b.policy} {b.why}")
        for h in hazards(m):
            hit = [i for i, row in enumerate(rows) if _row_matches(row, m, h)]
            if not hit:
                fails.append(
                    f"  FAIL {h.policy} writes {h.path} on {h.operation} and no register row "
                    f"records it: {h.why}")
                continue
            # A row is matched on POLICY and OPERATION, never on the field. Matching on the
            # field too would let a row narrower than the code look complete: the writes it
            # does not list would each go looking for a row of their own and find none, and the
            # row itself would still read as accurate. The field-set comparison below is what
            # grades the row against the code, in both directions.
            for i in hit:
                matched[i].append(h)

    for i, row in enumerate(rows):
        missing = [f for f in REQUIRED_ROW_FIELDS if not row.get(f)]
        if missing:
            fails.append(f"  FAIL register row {row.get('policy', '?')} is missing "
                         f"{', '.join(missing)} -- an accepted refusal with no recorded reason "
                         f"is an exemption")
            continue
        if not matched[i]:
            fails.append(
                f"  FAIL register row {row['policy']} on {row['operation']} matches no mutation "
                f"in the served surface -- the code moved and the row did not; delete it")
            continue
        want = set(row["fields"])
        got = {h.path for h in matched[i]}
        if want != got:
            fails.append(
                f"  FAIL register row {row['policy']} declares field set {sorted(want)} and the "
                f"code writes {sorted(got)} -- the row no longer describes the code")
            continue
        policies = sorted({h.policy for h in matched[i]})
        notes.append(
            f"  ok   accepted refusal ({row['recorded']}): {', '.join(policies)} "
            f"write{'' if len(policies) > 1 else 's'} {len(got)} field(s) a running pod forbids "
            f"on {row['operation']} -- {', '.join(sorted(got))}")
        notes.append(f"         reason: {' '.join(str(row['reason']).split())}")
        notes.append(f"         remediation: {' '.join(str(row['remediation']).split())}")
        if row.get("bounded_by"):
            notes.append(f"         bounded by: {' '.join(str(row['bounded_by']).split())}")

    lines = notes + could_not + fails
    if fails:
        return Verdict(1, lines)
    if could_not:
        return Verdict(3, lines)
    return Verdict(0, lines)


def _row_matches(row: dict, m: Mutation, h: Hazard) -> bool:
    return (fnmatch.fnmatch(m.name, str(row.get("policy", "")))
            and str(row.get("operation", "")) == h.operation)


# ------------------------------------------------------------------------------ the scan

def _units(root: Path) -> dict[str, Path]:
    out: dict[str, Path] = {}
    clone = root / ".estate-clone"
    if clone.is_dir():
        for child in sorted(clone.iterdir()):
            if child.is_dir() and not child.name.startswith("."):
                out[child.name] = child
    return out


def declared_and_cut(unit: str, path: Path) -> tuple[set[str], set[str]]:
    """One unit's declared and CUT version sets, read from its own version array.

    The `cut`/`uncut` partition is `commit`, exactly as `verify-declared-versions-admit.sh`
    partitions it: `cut-release.yml` fills that field when it cuts the signed tag, so an element
    without one has no tag, and Flux can deliver nothing.
    """
    declared: set[str] = set()
    cut: set[str] = set()
    for candidate in (path / "distribution" / "versions.yaml",
                      path / "gitops" / "composed" / "composed-set.yaml"):
        if not candidate.is_file():
            continue
        try:
            docs = read_documents(candidate.read_text())
        except (yaml.YAMLError, OSError):
            continue
        # An ADOPTER's array carries no per-element `commit`: its whole composed tree is pinned
        # by the one GitRepository beside it (`ref.tag` + the resolved `ref.commit`), so that
        # commit is what says the tree exists and is deliverable. The PLATFORM's array carries
        # a `commit` per element, because each version is delivered from its own signed tag.
        pinned = any(((d.get("spec") or {}).get("ref") or {}).get("commit")
                     for d in docs if d.get("kind") == "GitRepository")
        for doc in docs:
            inputs = ((doc.get("spec") or {}).get("inputs") or [])
            for el in (inputs[0].get("versions") if inputs else None) or []:
                if not isinstance(el, dict) or "version" not in el:
                    continue
                declared.add(str(el["version"]))
                if el.get("commit") or pinned:
                    cut.add(str(el["version"]))
    return declared, cut


def scan_tree(root: Path) -> tuple[list[Mutation], dict[str, dict[str, set[str]]], list[str]]:
    """Every mutating policy in the hub and the estate clone, with the release each travels in."""
    units = _units(root)
    declared = {}
    cut = {}
    for unit, upath in units.items():
        declared[unit], cut[unit] = declared_and_cut(unit, upath)

    mutations: list[Mutation] = []
    groups: dict[str, dict[str, set[str]]] = {}
    excluded: list[str] = []
    docs_by_group: dict[str, list[dict]] = {}
    facts: list[tuple[dict, str, str, Surface]] = []

    for unit, upath in units.items():
        for file in sorted(upath.rglob("*.yaml")):
            rel_parts = file.relative_to(upath).parts
            if set(rel_parts) & SKIP_DIRS:
                continue
            rel = f"{unit}/" + "/".join(rel_parts)
            surface = classify(rel, declared, cut)
            if surface.surface == "other":
                continue
            try:
                docs = read_documents(file.read_text())
            except (OSError, UnicodeDecodeError):
                continue
            if not docs:
                continue
            group = _group_of(unit, rel, surface)
            docs_by_group.setdefault(group, []).extend(docs)
            for doc in docs:
                facts.append((doc, rel, unit, surface))

    for group, docs in docs_by_group.items():
        groups[group] = shipped_names(docs)

    for doc, rel, unit, surface in facts:
        group = _group_of(unit, rel, surface)
        m = mutation(doc, path=rel, unit=unit, surface=surface.surface, group=group)
        if m is None:
            continue
        mutations.append(m)
        if not surface.graded:
            excluded.append(f"{m.name} ({rel}): {surface.why}")
    return mutations, groups, excluded


def _group_of(unit: str, rel: str, surface: Surface) -> str:
    """The RELEASE a policy travels in -- the set of objects installed with it.

    A version tree is one group and the machinery is another, deliberately: the machinery
    ResourceSet installs its own objects beside every version tree, and a version can be retired
    from the array at any time and pruned. A machinery cage that borrowed a version tree's
    PriorityClass would be refusing pods the day that version retires.
    """
    m = _VERSION_DIR.search(rel)
    if m and surface.surface in ("served-cut", "pending", "unserved-on-disk"):
        return f"{unit}:v{m.group(1)}"
    return f"{unit}:machinery"


def _inventory(mutations: list[Mutation], groups: dict) -> list[str]:
    rows = []
    for m in sorted(mutations, key=lambda x: (x.unit, x.path, x.name)):
        rows.append(f"{m.surface:18} {m.group:22} {m.name:34} "
                    f"ops={','.join(m.operations) or '-':13} writes={len(m.writes):2} "
                    f"refs={','.join(sorted(n for r in m.references.values() for n in r.names)) or '-'}")
    return rows


def selfcheck() -> None:
    """The grader's own asserts, over material this file builds. Nothing is read from disk."""
    body = ('Object{metadata: Object.metadata{labels: {"a": "b"}}, spec: Object.spec{'
            'priorityClassName: "cage-isolated", priority: -10, preemptionPolicy: "Never", '
            'containers: object.spec.containers.map(c, Object.spec.containers{name: c.name})}}')
    doc = {"kind": "MutatingPolicy", "metadata": {"name": "cage-x"}, "spec": {
        "matchConstraints": {"resourceRules": [
            {"operations": ["CREATE", "UPDATE"], "resources": ["pods"]}]},
        "mutations": [{"patchType": "ApplyConfiguration",
                       "applyConfiguration": {"expression": body}}]}}
    m = mutation(doc, path="platform/distribution/policies/v4.0.0/x.yaml", surface="served-cut")
    assert m is not None
    assert "spec.priorityClassName" in m.writes, m.writes
    assert "spec.containers[*].name" in m.writes, m.writes
    assert "metadata.labels" in m.writes, m.writes
    assert priority_trio(m) == (), "the complete trio must be clean"
    assert {h.path for h in hazards(m)} == {
        "spec.priorityClassName", "spec.priority", "spec.preemptionPolicy",
        "spec.containers[*].name"}, hazards(m)
    # an unrecorded hazard fails, and a recorded one is reported rather than called a defect
    v = grade([m], {"PriorityClass": {"cage-isolated"}}, {"accepted": []})
    assert v.code == 1, v
    row = {"policy": "cage-*", "operation": "UPDATE", "decision": "accepted",
           "fields": ["spec.priorityClassName", "spec.priority", "spec.preemptionPolicy",
                      "spec.containers[*].name"],
           "reason": "r", "remediation": "recreate", "recorded": "2026-09-06"}
    v = grade([m], {"PriorityClass": {"cage-isolated"}}, {"accepted": [row]})
    assert v.code == 0, v
    assert any("accepted refusal" in ln for ln in v.lines), v.lines
    # ...and a row that no longer describes the code fails in both directions
    assert grade([m], {"PriorityClass": {"cage-isolated"}},
                 {"accepted": [dict(row, fields=["spec.priority"])]}).code == 1
    assert grade([m], {"PriorityClass": {"cage-isolated"}},
                 {"accepted": [row, dict(row, policy="gone-*")]}).code == 1
    # a name the release does not ship is a refusal by another name (instance 2)
    assert grade([m], {"PriorityClass": {"cage-isolated-4-0-0"}},
                 {"accepted": [row]}).code == 1
    assert BLIND_SPOTS and all("2026-" in b for b in BLIND_SPOTS)
    print("selfcheck ok: writes are read out of the CEL body, an unrecorded hazard fails, an "
          "accepted one is reported with its reason, a stale row fails, a row whose field set "
          "has drifted fails, and a dangling reference name fails")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parents[1]))
    ap.add_argument("--register", default=str(HERE / "register.yaml"))
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args(argv)
    if args.selfcheck:
        selfcheck()
        return 0
    root = Path(args.root).resolve()
    mutations, groups, excluded = scan_tree(root)
    if args.inventory:
        for row in _inventory(mutations, groups):
            print(row)
        for row in excluded:
            print(f"excluded          {row}")
        return 0
    register = yaml.safe_load(Path(args.register).read_text()) or {}
    verdict = grade(mutations, groups, register)
    for line in verdict.lines:
        print(line)
    graded = [m for m in mutations if m.surface in GRADED_SURFACES]
    where = ", ".join(sorted({m.group for m in graded}))
    if verdict.code == 0:
        print(f"PASS: {len(graded)} mutating policies on the served surface ({where}); every "
              f"reference name is one its own release ships, every priority trio is whole, and "
              f"every write on UPDATE that a running pod forbids is recorded with a reason and a "
              f"remediation. {len(mutations) - len(graded)} authoring or pruned copies were "
              f"named and not graded")
    elif verdict.code == 3:
        print(f"SKIP: {len([ln for ln in verdict.lines if ln.startswith('  ??')])} mutation "
              f"writes could not be resolved offline, so this run could not look at them")
    else:
        print(f"FAIL: {len([ln for ln in verdict.lines if ln.startswith('  FAIL')])} refusals by "
              f"another name on the served surface")
    return verdict.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
