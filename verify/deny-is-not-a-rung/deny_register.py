#!/usr/bin/env python3
"""deny_register.py -- the inventory of every Deny-shaped rule, kept honest by a check.

Eco-system ticket 89. The owner's words (2026-09-02, ticket 75 Q5): "something could find
itself unable to run, but that's only because it doesn't fit the cage, not because we
deliberately deny it ... we've built a Mutating admission controller more than a Approving
admission and control". NORTH-STAR principle 2 and CONTEXT.md's Cage entry carry that; until
this ticket the SERVED policy did not.

Item 1 of the ticket is an inventory with a recorded choice per rule. An inventory taken once
is a document that starts rotting the next day, so it is taken by a scanner and joined to a
register of recorded choices, and the join is graded on every gate run. The register cannot
lie in either direction: a rule it calls converted may not still be found, and a rule it says
is still served may not have vanished.

Three moving parts:

  * `scan_text` / `scan_tree` -- where a Deny-shaped rule IS. Two shapes count: the CEL
    `ValidatingPolicy`'s `spec.validationActions` carrying `Deny` (ADR-0003), and the 2022
    `ClusterPolicy`'s `validationFailureAction: enforce`. The scan is line-based rather than
    document-based on purpose: three of the estate's Denys live inside a ResourceSet's
    `resourcesTemplate` STRING (each adopter's `gitops/composed/composed-set.yaml`), where a
    `yaml.safe_load_all` walk sees one ResourceSet and no policy at all, and would read the
    estate as cleaner than it is.

  * `register.yaml` -- the recorded choice per rule: `re-expressed` (the rule becomes a cage
    constraint) or `retired` (the rule goes, with the engine's computed bump), the reason, the
    paths whose SOURCE must no longer emit it, the copies that may still carry it while a
    signed tag is uncut, and what each of those waits for.

  * `grade` -- the join. PASS only when nothing outstanding is left. A copy still carrying a
    declared Deny is a could-not-look that NAMES the tag it waits for (exit 3), never a pass.
    A Deny no row matches, a source that still emits one it claims to have converted, or a
    register row that disagrees with the tree is a FAIL.

`grade` takes the source texts as a dict rather than reading them itself, so the whole grader
is a pure function of (findings, register, sources) and the tests drive it without a tree.

Usage:
    deny_register.py [--root DIR] [--register FILE]   # print the verdict, exit 0/1/3
    deny_register.py --inventory                      # the inventory, one row per finding
    deny_register.py --selfcheck                      # the grader's own asserts
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent

#: A rule may only be recorded as one of these. Anything else is an unrecorded choice.
CHOICES = ("re-expressed", "retired")
#: `converted` -- gone everywhere. `converted-at-source` -- the source no longer emits it, and
#: copies composed under a pinned, signed tag still carry it. `waiting` -- not converted yet.
STATES = ("converted", "converted-at-source", "waiting")

# The key may carry quotes and may sit anywhere on the line, not only at its start: the same
# shape appears in block YAML, in a one-line flow mapping (`spec: {validationActions: [Deny]}`),
# in JSON, and in the python renderers that emit it (`"validationActions": ["Deny"]`). A source
# that still emits the refusal is exactly what `converted-at-source` has to be able to see.
_DENY_ACTIONS = re.compile(r"""["']?validationActions["']?:\s*\[([^]]*)\]""")
#: A flow sequence the author wrapped over several lines: `validationActions: [` ... `]`.
_ACTIONS_OPEN = re.compile(r"""["']?validationActions["']?:\s*\[\s*$""")
_ACTIONS_KEY = re.compile(r"""^(\s*)["']?validationActions["']?:\s*$""")
_LIST_ITEM = re.compile(r"^(\s*)-\s*(\S+)\s*$")
_ENFORCE = re.compile(r"""["']?validationFailureAction["']?:\s*["']?(\w+)""")
#: A real Kyverno field. It turns an Audit policy into Enforce for named namespaces, so a
#: policy whose top line reads `audit` can still refuse in production.
_OVERRIDES = re.compile(r"""["']?validationFailureActionOverrides["']?:""")
_ACTION_ENFORCE = re.compile(r"""["']?action["']?:\s*["']?[Ee]nforce""")
_NAME = re.compile(r"""^(\s*)["']?name["']?:\s*["']?([^\s,}#"']+)""")
_KIND = re.compile(r"""^(\s*)["']?kind["']?:\s*["']?([^\s,}#"']+)""")
#: A `- name:` under matchConditions, variables or validations is NOT the policy's name.
_LIST_NAME = re.compile(r"""^\s*-\s*["']?name["']?:""")
#: `metadata: {name: x}` and `spec: {validationActions: [Deny]}` on one line each.
_FLOW_NAME = re.compile(r"""["']?metadata["']?:\s*\{[^}]*["']?name["']?:\s*["']?([^\s,}#"']+)""")
#: A YAML document break. Name and kind are never read across one -- see `_document_bounds`.
#: A YAML document break. Indented, because inside a ResourceSet's `resourcesTemplate`
#: the embedded documents are separated by an indented `---` -- and those separators are
#: the only thing that tells one embedded policy from the next.
_DOC_BREAK = re.compile(r"^\s*---\s*$")

SHAPE_ACTIONS = "validationActions: Deny"
SHAPE_ENFORCE = "validationFailureAction: Enforce"
SHAPE_OVERRIDES = "validationFailureActionOverrides: Enforce"

#: What this scanner CANNOT see, stated so nobody reads the register as exhaustive. Every entry
#: here was planted by a reviewer and confirmed missed. The gate script and the README carry the
#: same list, and `tests/test_deny_register.py` holds it non-empty.
BLIND_SPOTS = (
    "a YAML anchor or alias: `x: &deny [Deny]` ... `validationActions: *deny` reads as neither "
    "a list nor a literal here, so an aliased refusal is not found",
    "a templating engine's own conditionals: a `<< if >>` arm that emits Deny only under some "
    "input is read as the text it is, never as the documents it can produce",
    "a policy whose action is computed at admission rather than written in the manifest",
    "OPA Gatekeeper's `enforcementAction: deny` on a Constraint -- a different engine's word for "
    "the same thing. None ships in this estate today; the line costs nothing and the day one "
    "does, nothing here would have said so",
    "the 2022 Kyverno ClusterPolicy's `rules[].validate.deny{}` block, which refuses without the "
    "word appearing as an action value anywhere",
    "a webhook's own `failurePolicy: Fail`, which turns every engine outage into a refusal of "
    "everything the webhook matches -- the broadest refusal in a cluster, and written nowhere "
    "near a policy body",
    "a REFUSAL BY ANOTHER NAME: a mutation that makes a pod inadmissible -- naming a "
    "PriorityClass that does not exist, or injecting a container into a running pod, or "
    "rewriting an immutable field on one -- refuses the workload without any Deny-shaped text "
    "in it, and is graded by nothing here. Ticket 98 owns grading it. Four instances so far, "
    "every one found by RUNNING a policy and none by reading one: 2026-08-28 ticket 26 (a "
    "sidecar appended twice); 2026-09-05 ticket 89's first cut (a PriorityClass no cluster "
    "has); 2026-09-05 ticket 89's second (the full cage body on UPDATE, which would have "
    "refused the currency controller's re-cage patch); and one that is LIVE and decided rather "
    "than fixed -- labelling a bottom-rung pod with a served version makes cage-tier rewrite "
    "priorityClassName and priority, which the API server refuses on a running pod, so adding a "
    "claim is not a remediation and the remediation is a recreate (ticket 89 S3, CONTEXT.md)",
)

#: Directories never walked. `.estate-clone` is walked explicitly by root, not by recursion,
#: so a symlinked clone is not visited twice.
SKIP_DIRS = {".git", "__pycache__", ".venv", "node_modules", ".work", ".estate-clone"}


@dataclass(frozen=True)
class Finding:
    """One Deny-shaped rule, where it was found."""

    path: str                 # POSIX, relative to the scan root
    line: int                 # 1-based
    name: str | None          # the nearest preceding `name:`, which is the policy's own
    kind: str | None
    shape: str


@dataclass
class Verdict:
    verdict: str                      # PASS | SKIP | FAIL
    line: str                         # the one line the gate reads
    failures: list = field(default_factory=list)
    outstanding: int = 0


# -- the scanner ---------------------------------------------------------------------------------

#: `resourcesTemplate: |` and friends -- a key whose value is a block scalar.
_BLOCK_KEY = re.compile(r"^(\s*)[\w.\-\"']+:\s*[|>][-+0-9]*\s*$")


def _block_scalar_bounds(lines: list[str], idx: int) -> tuple[int, int] | None:
    """The block scalar containing `idx`, if it is inside one.

    A ResourceSet parses cleanly and carries its own `metadata.name` -- `composed` -- at a
    SHALLOWER indent than anything inside its `resourcesTemplate` string. So neither the parsed
    name nor the shallowest name in the file belongs to the policy the finding is actually in;
    both are the wrapper's. Three of the estate's Denys live in exactly that position, one per
    adopter. Narrowing the region to the block scalar is what makes the embedded policy's own
    `metadata:` the shallowest thing in view.
    """
    for i in range(idx, -1, -1):
        m = _BLOCK_KEY.match(lines[i])
        if not m:
            continue
        key_indent = len(m.group(1))
        # `idx` is inside this block only if every line between is blank or deeper-indented.
        body_start = i + 1
        end = len(lines)
        for j in range(body_start, len(lines)):
            if not lines[j].strip():
                continue
            if len(lines[j]) - len(lines[j].lstrip()) <= key_indent:
                end = j
                break
        if body_start <= idx < end:
            return body_start, end
        return None
    return None


def _document_bounds(lines: list[str], idx: int) -> tuple[int, int]:
    """The half-open line range of the YAML document containing `idx`.

    Attribution never crosses a `---`. It used to: the search ran backwards to the top of the
    file, so a document whose `metadata:` follows its `spec:` inherited the PREVIOUS document's
    name -- and a second, unrecorded Deny appended to a file a register row's globs already
    covered was reported as accounted for. A reviewer planted exactly that on 2026-09-05 and it
    passed. Bounding the search is what closes it.
    """
    lo, hi = 0, len(lines)
    block = _block_scalar_bounds(lines, idx)
    if block is not None:
        lo, hi = block
    start = lo
    for i in range(idx, lo - 1, -1):
        if _DOC_BREAK.match(lines[i]):
            start = i + 1
            break
    end = hi
    for i in range(idx + 1, hi):
        if _DOC_BREAK.match(lines[i]):
            end = i
            break
    return start, end


def _shallowest(pattern: re.Pattern, lines: list[str], idx: int,
                skip: re.Pattern | None = None) -> str | None:
    """The SHALLOWEST match of `pattern` in the document containing `idx`, skipping list items.

    Nearest-first was the bug. Round 2 widened the name regex from a `match` to a `search`, so a
    `- name:` inside `matchConditions`, `variables` or `validations` became readable as the
    document's own name -- and a reviewer planted a Deny called `block-all-images-from-anywhere`
    whose only camouflage was `matchConditions: [{name: posture-trust-boundary}]` sitting
    between the real metadata name and the `validationActions` line. The backwards search landed
    on the decoy, the register's globs already covered the file, and the whole thing reported as
    an accounted-for copy of `posture-trust-boundary` while the check stayed green.

    A policy's `metadata.name` is at the shallowest indentation any `name:` reaches in its
    document; everything nested under `spec:` is deeper, and a list item is excluded outright.
    Ties go to the first, which is document order. `scan_text` only falls back here when the
    document does not parse -- inside a ResourceSet's `resourcesTemplate` string, where there is
    no document to load.
    """
    start, end = _document_bounds(lines, idx)
    best: tuple[int, str] | None = None
    for i in range(start, end):
        if skip is not None and skip.match(lines[i]):
            continue
        m = pattern.match(lines[i])
        if not m:
            continue
        indent = len(m.group(1))
        if best is None or indent < best[0]:
            best = (indent, m.group(2))
    return best[1] if best is not None else None


def _doc_carries_the_shape(doc: object) -> bool:
    """Does this PARSED document itself carry a Deny shape?

    The question decides whose name a finding belongs to. A ResourceSet parses cleanly and has
    a `metadata.name` of its own -- `composed` -- while the Deny it carries is text inside its
    `resourcesTemplate` string, belonging to an embedded policy the parser never sees. Trusting
    the parsed name there would file three of the estate's Denys under the wrapper. So the
    parsed name is used only when the parsed document is the thing that carries the shape;
    otherwise the finding came out of a string and the shallowest non-list `name:` in that
    region is the best available answer.
    """
    if not isinstance(doc, dict):
        return False
    spec = doc.get("spec")
    if not isinstance(spec, dict):
        return False
    va = spec.get("validationActions")
    if isinstance(va, list) and any(str(v) == "Deny" for v in va):
        return True
    vfa = spec.get("validationFailureAction")
    if isinstance(vfa, str) and vfa.lower() == "enforce":
        return True
    overrides = spec.get("validationFailureActionOverrides")
    if isinstance(overrides, list):
        return any(isinstance(o, dict) and str(o.get("action", "")).lower() == "enforce"
                   for o in overrides)
    return False


def _document_name(lines: list[str], idx: int) -> str | None:
    """The policy's own name: `metadata.name` where the document parses, else the shallowest
    non-list `name:` in it. Never a list item's, and never another document's."""
    start, end = _document_bounds(lines, idx)
    chunk = "\n".join(lines[start:end])
    try:
        doc = yaml.safe_load(chunk)
    except Exception:
        doc = None
    if _doc_carries_the_shape(doc):
        name = (doc.get("metadata") or {}).get("name")
        if isinstance(name, str):
            return name
    # A one-line flow mapping (`metadata: {name: x}`) survives a parse only when the whole
    # document parses; when it does not, read it directly rather than falling through.
    for i in range(start, end):
        m = _FLOW_NAME.search(lines[i])
        if m:
            return m.group(1)
    return _shallowest(_NAME, lines, idx, skip=_LIST_NAME)


def _document_kind(lines: list[str], idx: int) -> str | None:
    start, end = _document_bounds(lines, idx)
    chunk = "\n".join(lines[start:end])
    try:
        doc = yaml.safe_load(chunk)
    except Exception:
        doc = None
    if _doc_carries_the_shape(doc) and isinstance(doc.get("kind"), str):
        return doc["kind"]
    return _shallowest(_KIND, lines, idx, skip=_LIST_NAME)


def _is_deny(values: str) -> bool:
    return any(v.strip().strip("'\"") == "Deny" for v in values.split(","))


def scan_text(text: str, path: str) -> list[Finding]:
    """Every Deny-shaped rule in one file's text, in file order.

    Line-based, not document-based, and that is load-bearing: three of the estate's Denys live
    inside a ResourceSet's `resourcesTemplate` STRING, where a `yaml.safe_load_all` walk sees a
    ResourceSet and no policy at all. What it cannot see is `BLIND_SPOTS`.
    """
    lines = text.splitlines()
    out: list[Finding] = []
    for i, line in enumerate(lines):
        shape = None
        flow = _DENY_ACTIONS.search(line)
        if flow and _is_deny(flow.group(1)):
            shape = SHAPE_ACTIONS
        if shape is None and _ACTIONS_OPEN.search(line):
            # A flow sequence wrapped over several lines: read to the closing bracket.
            buf = []
            for item in lines[i + 1:]:
                if "]" in item:
                    buf.append(item.split("]")[0])
                    break
                buf.append(item)
            if _is_deny(",".join(buf)):
                shape = SHAPE_ACTIONS
        key = _ACTIONS_KEY.match(line)
        if shape is None and key:
            # A block sequence under `validationActions:`. Read the items that follow at a
            # deeper-or-equal indent and stop at the first line that is not one.
            for item in lines[i + 1:]:
                m = _LIST_ITEM.match(item)
                if not m or len(m.group(1)) < len(key.group(1)):
                    break
                if m.group(2).strip("'\"") == "Deny":
                    shape = SHAPE_ACTIONS
                    break
        enforce = _ENFORCE.search(line)
        if shape is None and enforce and enforce.group(1).lower() == "enforce":
            shape = SHAPE_ENFORCE
        if shape is None and _OVERRIDES.search(line):
            # The override list turns an Audit policy into Enforce for named namespaces. Read
            # forward to the end of this document for an `action: Enforce` entry.
            _, end = _document_bounds(lines, i)
            for item in lines[i + 1:end]:
                if _ACTION_ENFORCE.search(item):
                    shape = SHAPE_OVERRIDES
                    break
        if shape:
            out.append(Finding(path=path, line=i + 1,
                               name=_document_name(lines, i),
                               kind=_document_kind(lines, i),
                               shape=shape))
    return out


def _excluded(rel: str, excluded: list[dict]) -> bool:
    return any(rel == e["path"] or rel.startswith(e["path"]) or fnmatch.fnmatch(rel, e["path"])
               for e in excluded)


def scan_tree(root: Path, excluded: list[dict]) -> list[Finding]:
    """Every Deny-shaped rule under `root`, paths relative to `root`, excluded trees skipped.

    YAML and JSON. What no scan here can see is `BLIND_SPOTS`, which the gate script prints.

    `.estate-clone` is a symlink to the assembled units in the real checkout; it is walked as
    a root of its own so a nested worktree cannot be visited twice under two names."""
    roots = [root]
    estate = root / ".estate-clone"
    if estate.is_dir():
        roots += sorted(p for p in estate.iterdir() if p.is_dir())
    out: list[Finding] = []
    seen: set[str] = set()
    for base in roots:
        for dirpath, dirnames, filenames in os.walk(base, followlinks=False):
            dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
            for fn in sorted(filenames):
                # `.json` too: a Kyverno policy is as valid in JSON as in YAML, and a
                # reviewer planted one on 2026-09-05 that a yaml-only walk missed.
                if not fn.endswith((".yaml", ".yml", ".json")):
                    continue
                p = Path(dirpath) / fn
                rel = os.path.relpath(p, root)
                if rel in seen or _excluded(rel, excluded):
                    continue
                seen.add(rel)
                try:
                    text = p.read_text()
                except (OSError, UnicodeDecodeError):
                    continue
                out.extend(scan_text(text, rel))
    return out


# -- the register --------------------------------------------------------------------------------

def load_register(path: Path) -> dict:
    doc = yaml.safe_load(Path(path).read_text()) or {}
    doc.setdefault("rules", [])
    doc.setdefault("excluded", [])
    return doc


def rule_for(finding: Finding, rules: list[dict]) -> dict | None:
    """The register row that claims this finding, by the policy's own name. A finding whose
    name could not be recovered belongs to no row: it is reported by path instead, which is
    what makes an unnameable Deny a failure rather than a silent pass."""
    if finding.name is None:
        return None
    for rule in rules:
        if re.match(rule.get("matches", "$^"), finding.name):
            return rule
    return None


def grade(findings: list[Finding], register: dict, source_text: dict[str, str]) -> Verdict:
    """Join the scan to the register.

    `source_text` maps each row's `source_clean` path to that file's text; a path missing from
    the dict is one the caller could not read, and is reported as a failure rather than
    assumed clean."""
    rules = register.get("rules", [])
    failures: list[str] = []
    outstanding: list[tuple[dict, list[Finding]]] = []

    for f in findings:
        rule = rule_for(f, rules)
        if rule is None:
            failures.append(
                f"{f.path}:{f.line} is Deny-shaped ({f.name or 'unnamed'}) and no register row "
                f"claims it -- an undeclared refusal ships")

    for rule in rules:
        name = rule.get("rule", "<unnamed row>")
        mine = [f for f in findings if rule_for(f, rules) is rule]
        if rule.get("choice") not in CHOICES:
            failures.append(f"{name}: choice {rule.get('choice')!r} is not one of {list(CHOICES)}")
        if not str(rule.get("reason") or "").strip():
            failures.append(f"{name}: the register records no reason for its choice")
        state = rule.get("state")
        if state not in STATES:
            failures.append(f"{name}: state {state!r} is not one of {list(STATES)}")
            continue

        if state == "converted":
            if mine:
                failures.append(
                    f"{name}: the register says converted, but {len(mine)} copy/copies still "
                    f"carry it -- first at {mine[0].path}:{mine[0].line}")
            continue

        # waiting or converted-at-source: copies may remain, and the row must say what they
        # wait for and where they are allowed to be.
        if not mine:
            failures.append(
                f"{name}: the register says it is still served, but no copy of it is left -- "
                f"the record is behind the code")
            continue
        globs = rule.get("served_copies") or []
        for f in mine:
            if not any(fnmatch.fnmatch(f.path, g) for g in globs):
                failures.append(
                    f"{name}: {f.path}:{f.line} is not one of the copies the register declares "
                    f"({globs or 'none declared'})")
        if not str(rule.get("awaits") or "").strip():
            failures.append(f"{name}: a copy still carries it and the row does not name what it "
                            f"waits for")
        sources = rule.get("source_clean") or []
        # A register that names a file nobody can open is a register that cannot be checked,
        # in EITHER state: renaming a renderer would otherwise freeze a `waiting` row for good.
        for src in sources:
            if src not in source_text:
                failures.append(f"{name}: source {src} could not be read, so what it emits is "
                                f"unproved -- the register names a file that is not there")
        if state == "converted-at-source":
            for src in sources:
                if src in source_text and scan_text(source_text[src], src):
                    failures.append(f"{name}: {src} still emits a Deny, so the row may not say "
                                    f"converted-at-source")
        elif state == "waiting" and sources:
            # The record may not lag the code. Once every declared source is clean, `waiting`
            # is no longer true of anything, and the row has to say so -- otherwise the
            # register goes stale in exactly the interval between a merge and somebody
            # remembering to edit a yaml file.
            readable = [s for s in sources if s in source_text]
            if readable and len(readable) == len(sources) \
                    and not any(scan_text(source_text[s], s) for s in sources):
                failures.append(
                    f"{name}: the register says waiting, but every source it names "
                    f"({sources}) no longer emits it -- move the row to converted-at-source")
        if rule.get("awaits"):
            outstanding.append((rule, mine))

    if failures:
        # The count is of PROBLEMS, not of rules: one row can raise several, and a line that
        # said "N rules" would be a miscount of exactly the kind this check exists to catch.
        return Verdict("FAIL",
                       f"FAIL: {len(failures)} problem(s) -- the register does not honestly "
                       f"account for the Deny-shaped rules this estate carries (ticket 89)",
                       failures, len(outstanding))
    if outstanding:
        def plural(n: int) -> str:
            return "copy" if n == 1 else "copies"
        waits = "; ".join(
            f"{r['rule']} ({len(f)} {plural(len(f))}) awaits {r['awaits']}"
            for r, f in outstanding)
        copies = sum(len(f) for _, f in outstanding)
        return Verdict(
            "SKIP",
            f"SKIP: {copies} served {plural(copies)} of a declared Deny are still in the estate, "
            f"each awaiting a named tag: {waits}",
            [], len(outstanding))
    return Verdict("PASS",
                   "PASS: every Deny-shaped rule in the hub and the estate is recorded with a "
                   "choice and a reason, and none is left in a served copy",
                   [], 0)


# -- the CLI -------------------------------------------------------------------------------------

def read_sources(root: Path, register: dict) -> dict[str, str]:
    out: dict[str, str] = {}
    for rule in register.get("rules", []):
        for src in rule.get("source_clean") or []:
            p = root / src
            try:
                out[src] = p.read_text()
            except OSError:
                continue
    return out


def selfcheck() -> None:
    """The grader's own asserts: it must be able to fail, and to could-not-look."""
    reg = {"excluded": [], "rules": [{
        "rule": "r", "matches": "^r$", "choice": "re-expressed", "state": "converted-at-source",
        "reason": "because", "source_clean": ["src.py"], "served_copies": ["a/b.yaml"],
        "awaits": "tag X"}]}
    f = Finding(path="a/b.yaml", line=1, name="r", kind="ValidatingPolicy", shape=SHAPE_ACTIONS)
    assert grade([f], reg, {"src.py": ""}).verdict == "SKIP"
    assert "tag X" in grade([f], reg, {"src.py": ""}).line
    assert grade([f], reg, {"src.py": "  validationActions: [Deny]\n"}).verdict == "FAIL"
    assert grade([], reg, {"src.py": ""}).verdict == "FAIL"
    other = Finding(path="z.yaml", line=9, name="nobody", kind=None, shape=SHAPE_ACTIONS)
    assert grade([f, other], reg, {"src.py": ""}).verdict == "FAIL"
    assert scan_text("spec:\n  validationActions:\n  - Deny\n", "p")[0].shape == SHAPE_ACTIONS
    assert scan_text("spec:\n  validationActions:\n  - Audit\n", "p") == []
    assert scan_text("spec:\n  validationFailureAction: enforce\n", "p")[0].shape == SHAPE_ENFORCE
    print("selfcheck ok: the grader fails an undeclared Deny, fails a dirty source, fails a "
          "register that is behind the code, and could-not-looks with the tag named")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(HERE.parent.parent))
    ap.add_argument("--register", default=str(HERE / "register.yaml"))
    ap.add_argument("--inventory", action="store_true")
    ap.add_argument("--selfcheck", action="store_true")
    args = ap.parse_args(argv)
    if args.selfcheck:
        selfcheck()
        return 0
    root = Path(args.root).resolve()
    register = load_register(Path(args.register))
    findings = scan_tree(root, register["excluded"])
    if args.inventory:
        for f in findings:
            rule = rule_for(f, register["rules"])
            print(f"{f.path}:{f.line} | {f.kind} | {f.name} | {f.shape} | "
                  f"{(rule or {}).get('rule', 'UNRECORDED')} | "
                  f"{(rule or {}).get('choice', '-')} | {(rule or {}).get('state', '-')}")
        return 0
    verdict = grade(findings, register, read_sources(root, register))
    for f in verdict.failures:
        print(f"  FAIL {f}")
    print(verdict.line)
    return {"PASS": 0, "SKIP": 3, "FAIL": 1}[verdict.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
