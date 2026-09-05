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

# The key may carry quotes: the same line shape appears in YAML and in the python renderers
# that emit it (`"validationActions": ["Deny"],`), and a source that still emits the refusal is
# exactly what `converted-at-source` has to be able to see.
_DENY_ACTIONS = re.compile(r"^\s*[\"']?validationActions[\"']?:\s*\[([^]]*)\]")
_ACTIONS_KEY = re.compile(r"^(\s*)[\"']?validationActions[\"']?:\s*$")
_LIST_ITEM = re.compile(r"^(\s*)-\s*(\S+)\s*$")
_ENFORCE = re.compile(r"^\s*[\"']?validationFailureAction[\"']?:\s*[\"']?(\w+)")
_NAME = re.compile(r"^\s*name:\s*([^\s#]+)")
_KIND = re.compile(r"^\s*kind:\s*([^\s#]+)")

SHAPE_ACTIONS = "validationActions: Deny"
SHAPE_ENFORCE = "validationFailureAction: Enforce"

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

def _nearest(pattern: re.Pattern, lines: list[str], idx: int) -> str | None:
    """The value of the nearest `pattern` match at or above `idx`. YAML nests, so the closest
    `name:` above a `validationActions:` is that policy's own metadata name and the closest
    `kind:` above it is its own kind -- true inside a ResourceSet template string too, where
    there is no document to parse."""
    for i in range(idx, -1, -1):
        m = pattern.match(lines[i])
        if m:
            return m.group(1)
    return None


def scan_text(text: str, path: str) -> list[Finding]:
    """Every Deny-shaped rule in one file's text, in file order."""
    lines = text.splitlines()
    out: list[Finding] = []
    for i, line in enumerate(lines):
        shape = None
        flow = _DENY_ACTIONS.match(line)
        if flow and any(v.strip().strip("'\"") == "Deny" for v in flow.group(1).split(",")):
            shape = SHAPE_ACTIONS
        key = _ACTIONS_KEY.match(line)
        if key:
            # A block sequence under `validationActions:`. Read the items that follow at a
            # deeper-or-equal indent and stop at the first line that is not one.
            for item in lines[i + 1:]:
                m = _LIST_ITEM.match(item)
                if not m or len(m.group(1)) < len(key.group(1)):
                    break
                if m.group(2).strip("'\"") == "Deny":
                    shape = SHAPE_ACTIONS
                    break
        enforce = _ENFORCE.match(line)
        if enforce and enforce.group(1).lower() == "enforce":
            shape = SHAPE_ENFORCE
        if shape:
            out.append(Finding(path=path, line=i + 1,
                               name=_nearest(_NAME, lines, i),
                               kind=_nearest(_KIND, lines, i),
                               shape=shape))
    return out


def _excluded(rel: str, excluded: list[dict]) -> bool:
    return any(rel == e["path"] or rel.startswith(e["path"]) or fnmatch.fnmatch(rel, e["path"])
               for e in excluded)


def scan_tree(root: Path, excluded: list[dict]) -> list[Finding]:
    """Every Deny-shaped rule under `root`, paths relative to `root`, excluded trees skipped.

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
                if not fn.endswith((".yaml", ".yml")):
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
                    f"{name}: the register says converted, but {len(mine)} copy(ies) still carry "
                    f"it -- first at {mine[0].path}:{mine[0].line}")
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
        if state == "converted-at-source":
            for src in sources:
                if src not in source_text:
                    failures.append(f"{name}: source {src} could not be read, so 'converted at "
                                    f"source' is unproved")
                elif scan_text(source_text[src], src):
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
        return Verdict("FAIL",
                       f"FAIL: {len(failures)} Deny-shaped rule(s) the register does not "
                       f"honestly account for (eco-system ticket 89)",
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
