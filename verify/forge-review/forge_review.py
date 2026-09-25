#!/usr/bin/env python3
"""The forge enforces the review (eco-system ticket 87 item 1).

Every identity pin in the estate is an anchored regexp over a Fulcio certificate identity, for
example `...cut-release\\.yml@refs/heads/(main|release/[0-9]+\\.[0-9]+\\.x)$`. A tag signed from
ANY branch that pattern admits is accepted by every consumer. So every branch it admits must be
one nobody can move without a reviewed pull request, and one nobody can create unreviewed. If the
pin and the protection drift apart, a signed tag from an unreviewed branch is accepted. This check
is the assertion that they have not.

What it grades, per repository:

  1. PINNED BRANCHES. Every anchored identity pattern the estate serves is read out of the served
     files (`scan`). For each repository a pattern names, the branches it admits are worked out
     from the repository's live branches plus a fixed set of probe names (`admitted`). For each
     admitted branch, GitHub's own answer for that branch name (`rules/branches/<name>`) must carry
     `pull_request` with at least one approving review, `non_fast_forward` and `deletion`; a
     branch other than the default must also carry `creation`, or anyone may create a branch the
     pin accepts. The forge resolves `~DEFAULT_BRANCH`, includes, excludes and any org ruleset
     itself, so this reads the effective rules rather than re-deriving them.
  2. THE FLOOR, on all nine repositories: the default branch carries `deletion` and
     `non_fast_forward`, and the repository has at least one active ruleset.
  3. RELEASE TAGS: every tag on the remote is held by an active tag ruleset carrying `update` and
     `deletion`, so a tag a consumer accepted cannot be moved or removed.
  4. BYPASS: where the collector could read a ruleset's `bypass_actors`, the list must be empty.
     An anonymous or read-scoped token is not shown the list; that is said on the PASS line and
     is not graded as a pass.

The probes are a ceiling, stated: a regexp admits an unbounded set of names, and this check asks
the forge about the live ones and a fixed sample of the rest. The ruleset patterns in force are
`refs/heads/release/**` and `~DEFAULT_BRANCH`, which the forge answers for any name, so a sample
that misses a shape the pattern admits is the gap this ceiling names, not a hole in the rule.

`collect` needs GitHub and runs where a credential may be (truth.yml's `clocks` job, or a local
authenticated `gh`). `check` grades from the file `collect` wrote and holds nothing. Exit 0 observed
true, 1 observed false, 3 could not look.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
HUB_REMOTE = "policy-as-versioned-flux/policy-as-versioned-flux"
# The nine repositories the ticket names, held fixed. The check grades exactly these: a facts file
# or a clone that carries fewer is a could-not-look by name, never a pass over the ones it did carry.
ESTATE_REMOTES: dict[str, str] = {
    "hub": HUB_REMOTE,
    "platform": "policy-as-versioned-platform/platform",
    "driftwood": "policy-as-versioned-driftwood/driftwood",
    "tuppence": "policy-as-versioned-tuppence/tuppence",
    "ludlow": "policy-as-versioned-ludlow/ludlow",
    "nist": "policy-as-versioned-nist/nist",
    "ico": "policy-as-versioned-ico/ico",
    "feeds": "policy-as-versioned-feeds/feeds",
    "insurer": "policy-as-versioned-insurer/insurer",
}
ESTATE_ORG = re.compile(r"^policy-as-versioned-[a-z0-9-]+$")

REVIEW_RULES = {"pull_request", "non_fast_forward", "deletion"}
FLOOR_RULES = {"non_fast_forward", "deletion"}
TAG_RULES = {"update", "deletion"}

# Branch names asked about beside the live ones. Chosen to hit each alternative the estate's
# patterns carry and a few near misses, so a pattern that widens is caught by a name it now admits.
PROBES = ["main", "master", "develop", "release/0.0.x", "release/1.0.x", "release/2.0.x",
          "release/10.20.x", "release/99.99.x", "release/1.0", "release/x"]

# The head of an anchored identity pattern: org, repo and workflow, each still escaped.
HEAD = re.compile(r"^\^https://github\\\.com/((?:[^/\\]|\\.)+)/((?:[^/\\]|\\.)+)/\\\.github/"
                  r"workflows/((?:[^@\\]|\\.)+)@refs/heads/")
# The same shape as an ERE for `git grep`. In a bracket expression ERE takes a backslash
# literally, so the excluded set must not carry one or every escaped dot stops the match.
GREP_ERE = "\\^https://github\\\\\\.com/[^ \"'`)]*@refs/heads/[^ \"'`]*"
# Paths whose patterns are fixtures, copies or records, never a pin a consumer serves.
NOT_SERVED = re.compile(r"(^|/)(tests?|testdata|fixtures?|captures|\.scratch|research)/"
                        r"|\.(md|jsonl|out|tsv|log)$")


@dataclass(frozen=True)
class Pattern:
    text: str
    repo: str
    workflow: str
    where: str = ""


def _unescape(s: str) -> str:
    return re.sub(r"\\(.)", r"\1", s)


def parse_pattern(text: str, where: str = "") -> Pattern | None:
    if not text.startswith("^") or not text.endswith("$"):
        return None
    m = HEAD.match(text)
    if not m:
        return None
    try:
        re.compile(text)
    except re.error:
        return None
    return Pattern(text, f"{_unescape(m.group(1))}/{_unescape(m.group(2))}",
                   _unescape(m.group(3)), where)


def admitted(p: Pattern, live: list[str]) -> list[str]:
    rx = re.compile(p.text)
    names = list(dict.fromkeys([*PROBES, *live]))
    return [b for b in names
            if rx.search(f"https://github.com/{p.repo}/.github/workflows/{p.workflow}"
                         f"@refs/heads/{b}")]


def scan(root: str) -> list[Pattern] | None:
    """Every anchored identity pattern in the files `root` tracks at HEAD, fixtures excluded.
    None when `root` could not be read, which is not the same as a checkout serving no pin."""
    try:
        done = subprocess.run(["git", "-C", root, "grep", "--cached", "-I", "-o", "-E", "-e",
                               GREP_ERE,
                               "--"], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode not in (0, 1):  # git grep exits 1 for "no match"
        return None
    out = done.stdout
    seen: dict[tuple[str, str], Pattern] = {}
    for line in out.splitlines():
        path, text = line.split(":", 1)
        if NOT_SERVED.search(path):
            continue
        p = parse_pattern(text.rstrip(",;"), path)
        if p and ESTATE_ORG.match(p.repo.split("/")[0]):
            seen.setdefault((p.text, p.repo), p)
    return list(seen.values())


def cloned(estate: str) -> dict[str, str]:
    """unit name -> checkout directory, for each unit whose clone under the directory `estate`
    exists and whose origin is the remote ESTATE_REMOTES names. Anything else is left out."""
    dirs: dict[str, str] = {}
    for unit, remote in ESTATE_REMOTES.items():
        d = os.path.join(estate, unit)
        if unit == "hub" or not os.path.isdir(d):
            continue
        try:
            url = subprocess.run(["git", "-C", d, "remote", "get-url", "origin"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            continue
        m = re.match(r"^https://github\.com/([^/]+/[^/]+?)(\.git)?$", url)
        if m and m.group(1) == remote:
            dirs[unit] = d
    return dirs


def patterns_by_repo(root: str, estate: str) -> dict[str, list[Pattern]]:
    """name -> the pins that name that repository. A name is present only when its own checkout
    was read, so `grade` can say by name which of the nine it could not read pins from."""
    dirs = {"hub": root, **cloned(estate)}
    by_remote = {v: k for k, v in ESTATE_REMOTES.items()}
    found: dict[str, list[Pattern]] = {}
    pins: dict[str, list[Pattern]] = {k: [] for k in ESTATE_REMOTES}
    for name, d in dirs.items():
        got = scan(d)
        if got is None:
            continue
        found[name] = pins[name]
        for p in got:
            owner = by_remote.get(p.repo)
            if owner and all(q.text != p.text for q in pins[owner]):
                pins[owner].append(p)
    return found


# --- collect: the only half that talks to GitHub ------------------------------------------------

def _gh_json(path: str, paginate: bool = False):
    args = ["gh", "api", *(["--paginate", "--jq", ".[]"] if paginate else []), path]
    done = subprocess.run(args, capture_output=True, text=True, timeout=120)
    if done.returncode != 0:
        tail = (done.stderr or done.stdout or "gh failed").strip().splitlines()
        raise RuntimeError(f"gh api {path}: {tail[-1] if tail else 'failed'}")
    if paginate:
        return [json.loads(line) for line in done.stdout.splitlines() if line.strip()]
    return json.loads(done.stdout or "null")


def collect(root: str, estate: str) -> dict:
    doc: dict = {"collector": "verify/forge-review/forge_review.py collect",
                 "run_id": os.environ.get("GITHUB_RUN_ID", ""),
                 "repository": os.environ.get("GITHUB_REPOSITORY", ""), "repos": {}}
    pats = patterns_by_repo(root, estate)
    for name, remote in ESTATE_REMOTES.items():
        entry: dict = {"remote": remote}
        doc["repos"][name] = entry
        try:
            entry["default_branch"] = _gh_json(f"repos/{remote}")["default_branch"]
            entry["branches"] = [b["name"] for b in
                                 _gh_json(f"repos/{remote}/branches?per_page=100", True)]
            entry["tags"] = [t["name"] for t in
                             _gh_json(f"repos/{remote}/tags?per_page=100", True)]
            entry["rulesets"] = []
            for r in _gh_json(f"repos/{remote}/rulesets?per_page=100", True):
                entry["rulesets"].append(_gh_json(f"repos/{remote}/rulesets/{r['id']}"))
            asked = {entry["default_branch"]}
            for p in pats.get(name, []):
                asked.update(admitted(p, entry["branches"]))
            entry["branch_rules"] = {b: _gh_json(f"repos/{remote}/rules/branches/{quote(b)}")
                                     for b in sorted(asked)}
        except (RuntimeError, OSError, subprocess.SubprocessError, ValueError, KeyError) as e:
            entry["error"] = str(e)
    return doc


# --- check: grades from the file, holds nothing ---------------------------------------------------

def _glob(pattern: str, ref: str) -> bool:
    # GitHub's fnmatch: `*` stays inside one path segment, `**` crosses them.
    rx = "".join(".*" if tok == "**" else "[^/]*" if tok == "*" else re.escape(tok)
                 for tok in re.split(r"(\*\*|\*)", pattern))
    return re.fullmatch(rx, ref) is not None


def ref_matches(ref: str, include: list[str], exclude: list[str], default: str) -> bool:
    def hit(pats: list[str]) -> bool:
        for p in pats:
            if p == "~ALL" or (p == "~DEFAULT_BRANCH" and ref == f"refs/heads/{default}"):
                return True
            if not p.startswith("~") and _glob(p, ref):
                return True
        return False
    return hit(include) and not hit(exclude)


def _rule_types(rules: list[dict]) -> dict[str, dict]:
    """Rule type -> parameters. Two rulesets may both apply a `pull_request` rule to one branch,
    and the forge enforces the strictest, so the highest review count is the one kept."""
    out: dict[str, dict] = {}
    for r in rules or []:
        kind, params = r.get("type", ""), r.get("parameters") or {}
        if kind in out and _reviews(out[kind]) >= _reviews(params):
            continue
        out[kind] = params
    return out


def _reviews(params: dict) -> int:
    return int(params.get("required_approving_review_count") or 0)


def _ref_name(ruleset: dict) -> tuple[list[str], list[str]]:
    cond = (ruleset.get("conditions") or {}).get("ref_name") or {}
    return list(cond.get("include") or []), list(cond.get("exclude") or [])


def binding_fault(doc: dict, env: dict) -> str:
    run_id = str(env.get("GITHUB_RUN_ID") or "")
    if run_id and str(doc.get("run_id") or "") != run_id:
        return (f"it was written by run {doc.get('run_id') or '(none)'} and this is run "
                f"{run_id}, so it is not this run's observation")
    return ""


def grade(doc: dict, pats: dict[str, list[Pattern]], env: dict,
          remotes: dict[str, str] | None = None) -> list[tuple[str, str]]:
    """Grades exactly the repositories `remotes` names (the nine by default). One the facts file
    does not carry, or whose checkout the gate did not read pins from, is a SKIP by name."""
    fault = binding_fault(doc, env)
    if fault:
        return [("SKIP", f"the forge facts file cannot be graded: {fault}")]
    lines: list[tuple[str, str]] = []
    facts = doc.get("repos") or {}
    for name, remote in sorted((ESTATE_REMOTES if remotes is None else remotes).items()):
        if name not in pats:
            lines.append(("SKIP", f"{name}: the gate's checkout carries no readable clone of "
                                  f"{remote}, so the pins it serves were not read"))
        repo = facts.get(name)
        if repo is None:
            lines.append(("SKIP", f"{name}: the forge facts file does not name {remote}, so "
                                  f"the forge was not looked at for it"))
            continue
        if repo.get("remote") != remote:
            lines.append(("SKIP", f"{name}: the forge facts file reads {repo.get('remote')} "
                                  f"where the estate names {remote}"))
            continue
        if repo.get("error"):
            lines.append(("SKIP", f"{name}: could not read the forge for {remote}: "
                                  f"{repo['error']}"))
            continue
        default = repo.get("default_branch", "main")
        rulesets = repo.get("rulesets") or []
        active = [r for r in rulesets if r.get("enforcement") == "active"]
        br = repo.get("branch_rules") or {}
        bad: list[str] = []
        if not active:
            bad.append(f"no active ruleset at all on {remote}")
        needed: dict[str, set[str]] = {}
        for p in pats.get(name, []):
            for b in admitted(p, repo.get("branches") or []):
                needed.setdefault(b, set()).add(p.workflow)
        floor = _rule_types(br.get(default, []))
        if default in needed:
            pass  # graded below against the stricter review rule, which includes the floor
        elif default not in br:
            lines.append(("SKIP", f"{name}: the collector did not ask the forge about "
                                  f"{default}, so the floor on it was not looked at"))
        elif FLOOR_RULES - set(floor):
            bad.append(f"{default} lacks {sorted(FLOOR_RULES - set(floor))}")
        for b in sorted(needed):
            if b not in br:
                lines.append(("SKIP", f"{name}: {b} is admitted by the {sorted(needed[b])} "
                                      f"pin and the collector did not ask the forge about it"))
                continue
            have = _rule_types(br[b])
            want = REVIEW_RULES | ({"creation"} if b != default else set())
            missing = sorted(want - set(have))
            if "pull_request" in have and _reviews(have["pull_request"]) < 1:
                missing.append("pull_request with at least one approving review")
            if missing:
                bad.append(f"{b} is admitted by the {', '.join(sorted(needed[b]))} pin and "
                           f"lacks {missing}")
        tag_sets = [r for r in active if r.get("target") == "tag"
                    and TAG_RULES <= set(_rule_types(r.get("rules")))]
        loose = [t for t in repo.get("tags") or []
                 if not any(ref_matches(f"refs/tags/{t}", *_ref_name(r), default)
                            for r in tag_sets)]
        if loose:
            bad.append(f"{len(loose)} tag(s) no active tag ruleset holds against update and "
                       f"deletion, first {loose[:3]}")
        seen_bypass = [r for r in rulesets if "bypass_actors" in r]
        for r in seen_bypass:
            if r["bypass_actors"]:
                bad.append(f"ruleset {r.get('name')} ({r.get('id')}) lets "
                           f"{[a.get('actor_type') for a in r['bypass_actors']]} bypass it")
        if bad:
            lines.extend(("FAIL", f"{name}: {b}") for b in bad)
        else:
            bypass = ("bypass lists read and empty" if seen_bypass and
                      len(seen_bypass) == len(rulesets) else
                      "bypass lists not shown to this token, so not graded")
            lines.append(("PASS", f"{name}: {len(active)} active ruleset(s) on {remote}; "
                                  f"{len(needed)} pinned branch(es) reviewed; "
                                  f"{len(repo.get('tags') or [])} tag(s) held; {bypass}"))
    if not lines:
        lines.append(("SKIP", "the forge facts file names no repository"))
    return lines


def _exit(lines: list[tuple[str, str]]) -> int:
    # A repository that could not be looked at never hides behind the others' passes.
    if any(s == "FAIL" for s, _ in lines):
        return 1
    if any(s == "SKIP" for s, _ in lines) or not any(s == "PASS" for s, _ in lines):
        return 3
    return 0


def selfcheck() -> int:
    """Planted facts: each refusal must bite and the protected shape must pass."""
    pin = parse_pattern(r"^https://github\.com/policy-as-versioned-x/x/\.github/workflows/"
                        r"cut-release\.yml@refs/heads/(main|release/[0-9]+\.[0-9]+\.x)$")
    assert pin is not None
    pr = {"type": "pull_request", "parameters": {"required_approving_review_count": 1}}
    main = [{"type": "deletion"}, {"type": "non_fast_forward"}, pr]
    rel = [{"type": "creation"}, *main]
    tags = {"id": 2, "target": "tag", "enforcement": "active",
            "conditions": {"ref_name": {"include": ["~ALL"], "exclude": []}},
            "rules": [{"type": "update"}, {"type": "deletion"}]}

    def facts(main_rules, rel_rules, tagset=tags):
        br = {b: rel_rules for b in PROBES}
        br["main"] = main_rules
        return {"repos": {"x": {"remote": "policy-as-versioned-x/x", "default_branch": "main",
                                "branches": ["main"], "tags": ["v1.0.0"],
                                "rulesets": [{"id": 1, "target": "branch",
                                              "enforcement": "active"}, tagset],
                                "branch_rules": br}}}
    cases = [
        (facts(main, rel), 0, "the protected shape"),
        (facts(main[:2], rel), 1, "a pinned main with no review rule"),
        (facts(main, rel[1:]), 1, "an admitted release branch anyone may create"),
        (facts(main, rel, dict(tags, enforcement="evaluate")), 1, "a tag ruleset not in force"),
    ]
    for doc, want, what in cases:
        got = _exit(grade(doc, {"x": [pin]}, env={}, remotes={"x": "policy-as-versioned-x/x"}))
        if got != want:
            print(f"selfcheck: {what} graded exit {got}, wanted {want}", file=sys.stderr)
            return 1
    return 0


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("collect")
    c.add_argument("--out", required=True)
    c.add_argument("--estate", default=os.path.join(ROOT, ".estate-clone"))
    k = sub.add_parser("check")
    k.add_argument("--facts", required=True)
    k.add_argument("--estate", default=os.path.join(ROOT, ".estate-clone"))
    sub.add_parser("selfcheck")
    a = ap.parse_args(argv)
    if a.cmd == "selfcheck":
        return selfcheck()
    if a.cmd == "collect":
        doc = collect(ROOT, a.estate)
        with open(a.out, "w") as fh:
            json.dump(doc, fh, indent=1, sort_keys=True)
        print(f"wrote {a.out}: {len(doc['repos'])} repositories, "
              f"{sum(1 for r in doc['repos'].values() if 'error' in r)} unreadable")
        return 0
    try:
        with open(a.facts) as fh:
            doc = json.load(fh)
    except (OSError, ValueError) as e:
        print(f"SKIP: no readable forge facts file at {a.facts}: {e}")
        return 3
    pats = patterns_by_repo(ROOT, a.estate)
    for name in sorted(pats):
        for p in pats[name]:
            print(f"pin: {name} {p.workflow} {p.text} (first read in {p.where})")
    lines = grade(doc, pats, dict(os.environ))
    for status, msg in lines:
        print(f"{status}: {msg}")
    return _exit(lines)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
