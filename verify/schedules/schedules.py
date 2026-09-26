#!/usr/bin/env python3
"""schedules.py -- ADR-0024 made checkable.

Four questions, in this order:

  1. Does every unit carry the clocks its own party artefact says it needs?
     A publisher needs a `fetch` clock, an adopter needs `renovate-run` and
     `propose-tier`, a repository with a `twin/` overlay needs `twin-sweep`, and
     the hub needs `truth`. Derived from what each repository actually is, never
     from a list in this file, so a unit that grows an overlay tomorrow starts
     failing tomorrow until it grows the clock too.

  2. Is every scheduled job caged? A `run:` script that pushes the default
     branch may only `git add` paths inside the observation allow-list
     (`talk/truth.log`, `drift/samples.jsonl`, `captures/**`, `observations/**`),
     it must declare that allow-list in the workflow's own `env:` so the cage
     step and this checker read the same data, and it must carry a cage step
     that fails the run on anything else. The workflow YAML is PARSED -- job
     structure, `on:`, `env:` and each step's own `run:` string -- never grepped.

  3. Can a clock mint a signed artefact? A scheduled job that can `git tag` or
     `gh release create` can sign a release without a human, which is the one
     thing the whole release path exists to prevent. No scheduled job may.

  4. Live, where GitHub is reachable: did each clock actually run inside its own
     period? A `schedule:` that GitHub silently stopped honouring is a clock
     that reports nothing while looking present in the file.

WHERE THE LIVE FACTS COME FROM (ticket 56, 2026-09-04). Questions 3b and 4 need a GitHub
credential, and the gate step that runs this file deliberately holds none: `talk/verify-all.sh`
runs 84 verify scripts cloned unpinned off eight other organisations' default branches, and a
token in that job's environment is a token those scripts can read. So on every CI run the whole
live half SKIPped, and the citable surface could not see whether a single clock had run --
permanent blindness recorded nowhere.

The fix is a SEPARATE JOB, not a wider gate. `schedules.py clocks --out FILE` runs in
truth.yml's `clocks` job, which holds `actions: read` and runs no third-party code, and writes
the four live facts (per unit: the ruleset state; per clock: the remote's `schedule:` state and
the newest scheduled run) into a JSON file. That file is an OBSERVATION -- dates, conclusions,
cron strings -- and carries no verdict and no credential. The gate job takes it as an artifact
and this file grades from it with `CLOCK_VERDICT` set, holding nothing a verify script could
steal. Precedence: `CLOCK_VERDICT` if set, else `gh` if authenticated, else offline. A verdict
file that is missing, malformed, stale, or written by a different run or repository (round 2:
`binding_fault`) is a could-not-look that says so by name -- never a silent fall back to a
credential the gate is not supposed to have.

WHAT IS GRADED (eco-system ticket 142, 2026-09-25). Every unit is read at its SERVED ref:
`refs/remotes/origin/main` after a best-effort fetch, the branch GitHub actually runs a clock
from and a composition actually reads. Until ticket 142 this file read each `.estate-clone/<unit>`
WORKING TREE, which lagged origin/main by two to seven commits on the day it was measured, so the
gate was grading yesterday's workflow text. The INFO line per unit names the sha it graded. A
unit whose origin/main cannot be read is a named could-not-look (SKIP) for that unit, never a
silent fall back to the working tree.

Not graded here, on purpose (2026-09-03, ticket 92): the LOCAL clock, `talk/local-clock.sh`,
the third clock ADR-0024 point 6 adds. It is a launchd job on the owner's machine, not a
workflow, so there is no YAML for questions 2 to 4 to parse, and its lane is a gitignored run
root plus a pull request rather than the observation lane. `verify/local-clock/` grades it:
the marker it leaves, and that no injected rehearsal signal reached a citable path.

Exit precedence: any FAIL -> 1; else any SKIP -> 3; else 0. Offline, questions
1 to 3 still run in full -- absence of a network is never a pass and never a
reason to skip the static half.

Usage:
    schedules.py check      [--offline]
    schedules.py clocks     --out FILE
    schedules.py selfcheck
"""
from __future__ import annotations

import base64
import datetime as dt
import glob
import json
import os
import re
import subprocess
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)
from _estate import ESTATE  # noqa: E402
import lost_recordings  # noqa: E402

HUB = os.path.normpath(os.path.join(ESTATE, ".."))
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "..", "talk"))
from truth_manifest import parse_truth  # noqa: E402

# ADR-0024, D1. The complete list of paths a scheduled run may ever commit.
# Everything else is a declaration: a tier, a pin, a floor, an overlay, a
# priced evidence file, a published feed.
# `talk/captures`, not `captures`: talk/verify-all.sh writes captures to
# talk/captures/ and there is no top-level captures/ anywhere in the estate, so
# the old entry made the two halves of the cage disagree -- a workflow naming the
# REAL path would have been failed by this checker (review, 2026-08-28).
# The platform composer carries a copy as OBSERVATION_PATHS in its
# compose/comparison_history.py (eco-system ticket 134), because it runs in each
# adopter's CI with no hub checkout. lane.py fails when that copy on platform
# main differs from this one, so change both together.
ALLOW_LIST = ("talk/truth.log", "drift/samples.jsonl", "talk/captures", "observations")

# A clock that ran longer ago than this has stopped. One day is the declared
# period; GitHub delays scheduled runs under load and drops them entirely on a
# repository with no recent pushes, so the window carries a day of slack and
# names that as the reason rather than pretending the period is 48 hours.
PERIOD_HOURS = 48

# The clocks documented to exit non-zero on purpose, and the ONE conclusion each is excused for.
# truth.yml re-raises the gate's own verdict (its "fail if the gate failed" step), so a red gate
# is a failed run AND a recorded observation.
#
# 2026-09-04, ticket 56: the exception used to be by workflow name alone -- `conclusion !=
# "success" and workflow not in RED_GATE_EXITS_NONZERO` -- so EVERY non-success excused truth.yml,
# `cancelled` included. Observed that day: the scheduled run of 09:55:43Z was cancelled by the
# `truth` concurrency group when a push queued behind it, recorded nothing, and graded PASS. A
# cancelled run is a clock that did not tick. The excuse is now the exact conclusion the exit is
# documented for and nothing else.
RED_GATE_EXITS_NONZERO = {"truth.yml": "failure"}

# How many scheduled runs of a clock the collector reads before deciding which one it may grade.
# One was too few: the newest scheduled run of `truth.yml`, seen from a scheduled run of
# `truth.yml`, is the run doing the looking (`newest_gradable`). Ten is deep enough to look past
# this run and past a second one still in flight without paging the API.
RUN_SCAN_LIMIT = 10

# How many merged pull requests the collector reads per unit, newest first, so lane.py can ask
# who merged a commit GitHub committed (ticket 142). The hub held 137 on 2026-09-25, the largest.
MERGED_SCAN_LIMIT = 500

# The clock verdict file (ticket 56). Written by `clocks`, read by `check` when CLOCK_VERDICT
# names it. Facts only: no verdict, no credential.
VERDICT_SCHEMA = "clock-verdict/v1"
# A verdict file older than this describes yesterday's clocks. The gate reads one minutes old
# (truth.yml's `clocks` job runs immediately before the gate job); six hours is slack for a slow
# gate, not a licence to grade from a stale file.
VERDICT_MAX_AGE_HOURS = 6

# Which open ticket owns a clock that is red today (ticket 85). Data, beside this file, so a red
# names its owner in the gate's own output instead of in someone's head.
OWNERS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clock-owners.yaml")


class CouldNotLook(Exception):
    """A live fact this run has no way to reach. Never a FAIL: it is a SKIP with a reason."""

# `uses:` actions that provably do not write to the repository: they fetch the
# checkout, install a toolchain, or move artefacts. Anything else under
# `contents: write` is an opaque binary this checker cannot read, and an
# unreadable step is reported, never silently passed.
INERT_ACTIONS = (
    "actions/checkout", "actions/setup-", "actions/cache",
    "actions/upload-artifact", "actions/download-artifact",
)

DEFAULT_BRANCH = "main"
REMOTE = "policy-as-versioned-{unit}/{unit}"
HUB_REMOTE = "policy-as-versioned-flux/policy-as-versioned-flux"

_PUSH = re.compile(r"git\s+(?:-C\s+\S+\s+)?push\b([^\n]*)")
_ADD = re.compile(r"git\s+(?:-C\s+\S+\s+)?add\b([^\n]*)")
# `git add -A`, `git add .`, `git add -u`, a bare `git add`, and `git commit -a`
# all stage whatever the tree holds, which is every path at once. The old regex
# only ever looked at path OPERANDS, so all five read as staging nothing
# (review, 2026-08-28).
_STAGES_EVERYTHING = re.compile(
    r"git\s+(?:-C\s+\S+\s+)?commit\b[^\n]*(?:\s-[A-Za-z]*a|\s--all\b)")

# Every shape a clock could use to mint or merge a signed artefact (eco-system ticket 142, from
# ticket 30's facts of 2026-09-25). Until then this was ONE regex over four shapes -- `git tag`,
# `gh release create|upload`, `gh pr merge` and the literal `/git/refs/tags` -- and it missed a
# merge by REST (`gh api -X PUT .../pulls/N/merge`, `curl -X PUT .../merge`), a release or a ref
# minted by REST (`gh api .../releases`, `gh api .../git/refs`), a GraphQL mutation, `git
# update-ref`, and a tag pushed by refspec (`git push origin v1.2.3`, `refs/tags/...`, `--tags`).
# Each entry is (pattern, what it does). The REST shapes are graded separately below, because
# the same path is a read or a write depending on the method and the body flags.
_SIGNED_ARTEFACT: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bgit\b(?:\s+-C\s+\S+)?\s+tag\b"), "makes a tag"),
    (re.compile(r"\bgit\b(?:\s+-C\s+\S+)?\s+update-ref\b"), "moves a ref directly"),
    (re.compile(r"\bgh\s+release\s+(?:create|upload|edit|delete|delete-asset)\b"),
     "makes or changes a release"),
    (re.compile(r"\bgh\s+pr\s+merge\b"), "merges a pull request"),
    (re.compile(r"\bgh\s+pr\s+[^\n]*--auto\b"), "merges a pull request on a delay"),
    # a tag reaches origin by refspec: the tags namespace, every tag, the `tag <name>` form, or
    # a version-shaped refspec (`v1.2.3`, `twin/v0.1.0`, `HEAD:v1.2.3`)
    (re.compile(r"\bgit\b(?:\s+-C\s+\S+)?\s+push\b[^\n]*(?:--tags\b|--follow-tags\b|refs/tags/"
                r"|\stag\s+\S+|[\s:](?:\S*/)?v?\d+\.\d+\.\d+(?:\S*)?(?=\s|$))"),
     "pushes a tag"),
    (re.compile(r"\b(?:mergePullRequest|enablePullRequestAutoMerge|createRef|updateRef|"
                r"deleteRef|createRelease)\b"), "runs a GraphQL mutation that merges or mints"),
)
# A REST call (`gh api` or `curl`), read as one command with its `\`-continued lines joined and
# comment lines dropped. The merge endpoints are a disposal whatever the method: GET on
# /pulls/N/merge only asks whether it was merged, and a clock has no business there either, so
# the path alone is the fault (errs closed). The releases and git-data refs collections are a
# read on GET and a mint on a write, so those need the method or a body flag as well: `gh api`
# turns POST on `-f`/`-F`/`--field`/`--raw-field`/`--input`, curl on `-d`/`--data*`/`--json`/
# `-F`/`--form`/`-T`/`--upload-file` (curl's `-f` is --fail, not a body, so the flags are per
# tool and case-sensitive).
_COMMENT_LINE = re.compile(r"(?m)^\s*#[^\n]*\n?")
_CONTINUED = re.compile(r"\\\n\s*")
_REST_LINE = re.compile(r"\b(?:gh\s+api|curl)\b[^\n]*")
_REST_DISPOSES = re.compile(r"/pulls/[^/\s\"']+/merge\b|/merges\b")
_REST_MINTS = re.compile(r"/(?:releases|git/refs)(?=[/\s\"'?]|$)")
_REST_METHOD = re.compile(r"(?:^|\s)(?:-X|--method|--request)[=\s]*[\"']?(?:POST|PUT|PATCH|DELETE)\b"
                          r"|(?:^|\s)-X(?:POST|PUT|PATCH|DELETE)\b", re.I)
_REST_BODY = {
    "gh api": re.compile(r"(?:^|\s)(?:-f|-F|--field|--raw-field|--input)(?:[=\s]|$)"),
    "curl": re.compile(r"(?:^|\s)(?:-d|--data(?:-\w+)?|--json|-F|--form|-T|--upload-file)(?:[=\s]|$)"),
}


def signed_artefact_hits(script: str) -> list[str]:
    """Every way this shell could mint or merge a signed artefact, each named."""
    text = _CONTINUED.sub(" ", _COMMENT_LINE.sub("", script or ""))
    hits: list[str] = []
    for pattern, what in _SIGNED_ARTEFACT:
        found = pattern.search(text)
        if found:
            hits.append(f"{what} ({found.group(0).strip()[:80]!r})")
    for found in _REST_LINE.finditer(text):
        line = found.group(0)
        tool = "gh api" if line.startswith("gh") else "curl"
        if _REST_DISPOSES.search(line):
            hits.append(f"merges through the REST API ({line.strip()[:80]!r})")
        elif _REST_MINTS.search(line) and (_REST_METHOD.search(line)
                                           or _REST_BODY[tool].search(line)):
            hits.append(f"mints a release or a ref through the REST API ({line.strip()[:80]!r})")
    return hits


# What a `run:` step executes that is NOT inline shell this checker can read: a program from the
# checkout (`python3 x.py`, `python3 -m pkg`, a heredoc `python3 -`, `bash x.sh`, `./x`), a
# package fetched to run (`npx renovate`), or node. Read per line, after a leading `if`/`!` and
# any `VAR=value` prefixes. This is what the PASS line used to call "nothing it runs is opaque to
# this checker" while every twin-sweep ran hub Python under `contents: write` (ticket 142).
_PROGRAM = re.compile(
    r"(?m)(?:^|(?<=[;&|]))\s*(?:(?:if|then|else|do|!|-)\s+)*(?:[A-Za-z_][\w]*=\S*\s+)*"
    r"(?P<call>(?:python3?|bash|sh|npx|node)\s+[^\n|;&]*|\./[^\s|;&]+[^\n|;&]*)")


def _program_name(call: str) -> str:
    """The program a call runs, without its arguments: `python3 x.py`, `python3 -m pkg.mod`,
    `python3 - (heredoc)`, `python3 -c (inline)`, `bash x.sh`, `npx renovate@1`, `./x`."""
    words = call.split()
    head = words[0]
    if head.startswith("./"):
        return head
    rest = [w for w in words[1:] if w]
    if head.startswith("python"):
        if rest and rest[0] == "-m" and len(rest) > 1:
            return f"{head} -m {rest[1]}"
        if rest and rest[0] == "-":
            return f"{head} - (heredoc)"
        if rest and rest[0].startswith("-c"):
            return f"{head} -c (inline)"
        return f"{head} {rest[0]}" if rest else head
    if head == "npx":
        rest = [w for w in rest if not w.startswith("-")]
        return f"npx {rest[0]}" if rest else head
    return f"{head} {rest[0]}" if rest else head


def called_programs(job: dict) -> list[str]:
    """The programs the job's `run:` steps execute, in order, each named once."""
    seen: list[str] = []
    for step in job.get("steps") or []:
        text = _CONTINUED.sub(" ", _COMMENT_LINE.sub("", str(step.get("run") or "")))
        for found in _PROGRAM.finditer(text):
            name = _program_name(found.group("call"))[:60]
            if name not in seen:
                seen.append(name)
    return seen


LINES: list[str] = []


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


# --- the served ref: what a unit IS, read where GitHub reads it (ticket 142) ------------------
FETCH_TIMEOUT = 20


class Served:
    """One unit's committed tree at `refs/remotes/origin/main`, the ref a scheduled run is
    started from and a composition reads. Every read below is `git show <sha>:<path>` or
    `git ls-tree <sha>`, never a path on disk: the working tree is nobody's artefact."""

    def __init__(self, root: str, sha: str, how: str) -> None:
        self.root, self.sha, self.how = root, sha, how

    def _git(self, *args: str) -> str | None:
        done = subprocess.run(["git", "-C", self.root, *args], capture_output=True, text=True,
                              check=False, timeout=30)
        return done.stdout if done.returncode == 0 else None

    def show(self, path: str) -> str | None:
        """The file's text at the served ref, or None when the ref does not carry it."""
        return self._git("show", f"{self.sha}:{path}")

    def ls(self, directory: str) -> list[str]:
        """Basenames directly under `directory` at the served ref; [] when it is not there."""
        raw = self._git("ls-tree", "--name-only", self.sha, f"{directory.rstrip('/')}/") or ""
        return sorted(os.path.basename(line) for line in raw.splitlines() if line)

    def isdir(self, path: str) -> bool:
        raw = self._git("ls-tree", "-d", "--name-only", self.sha, f"{path.rstrip('/')}") or ""
        return path.rstrip("/") in [line.rstrip("/") for line in raw.splitlines()]


def served(root: str) -> tuple[Served | None, str]:
    """(the served tree, how it was reached). A best-effort fetch of origin/main first, so a kept
    clone grades today's tip; a fetch that fails is said so and the last-fetched ref stands,
    dated by the run; no origin/main at all is (None, why) and the caller names it as a
    could-not-look. Never the working tree."""
    ref = f"refs/remotes/origin/{DEFAULT_BRANCH}"
    try:
        done = subprocess.run(["git", "-C", root, "fetch", "--quiet", "origin",
                               f"+refs/heads/{DEFAULT_BRANCH}:{ref}"],
                              capture_output=True, text=True, check=False, timeout=FETCH_TIMEOUT)
        if done.returncode == 0:
            how = "fetched now"
        else:
            first = (done.stderr.strip().splitlines() or [f"fetch exit {done.returncode}"])[0]
            how = f"fetch FAILED ({first[:80]}); as last fetched"
    except (subprocess.SubprocessError, OSError) as e:
        how = f"fetch FAILED ({str(e).splitlines()[0][:80]}); as last fetched"
    done = subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", ref],
                          capture_output=True, text=True, check=False, timeout=30)
    sha = done.stdout.strip() if done.returncode == 0 else ""
    if not sha:
        return None, f"no {ref} in the checkout at {root} ({how})"
    return Served(root, sha, how), how


# --- what each repository is --------------------------------------------------
def required_clocks(unit: str, tree: Served) -> dict[str, str]:
    """{workflow file: why} -- derived from the repository AT ITS SERVED REF, not declared here."""
    need: dict[str, str] = {}
    try:
        party = yaml.safe_load(tree.show("party.yaml") or "") or {}
    except yaml.YAMLError:
        party = {}
    if not isinstance(party, dict):
        party = {}
    roles = party.get("roles") or []
    # forward-intel is the twin's own feed; the twin-sweep clock publishes it, so
    # a party whose only publication is forward-intel needs no separate fetch.
    #
    # Neither does a record that declares NO payload schema. That is a section of the party's own
    # signed artefact rather than an envelope it fetches from anywhere -- the adopter's `exposure`,
    # which composition renders into composed/HEADER.yaml and the adopter's own tag signs. Its
    # clock is propose-tier.yml's daily recompose, required below because the party is an adopter;
    # a fetch.yml would be a scheduled job with nothing to fetch.
    publishes = [p for p in (party.get("publishes") or [])
                 if p.get("name") != "forward-intel" and p.get("payload_schema", "") is not None]
    if publishes:
        need["fetch.yml"] = f"{unit} publishes {', '.join(p['name'] for p in publishes)}"
    if "adopter" in roles:
        need["renovate-run.yml"] = f"{unit} is an adopter, and Renovate's PR starts every re-price"
        need["propose-tier.yml"] = f"{unit} is an adopter, and the price moves with the date"
    if tree.isdir("twin"):
        need["twin-sweep.yml"] = f"{unit} carries a twin overlay under twin/"
    return need


def units() -> list[tuple[str, str, str]]:
    """(unit, checkout root, remote) for every unit plus the hub."""
    found = []
    for entry in sorted(os.listdir(ESTATE)):
        root = os.path.join(ESTATE, entry)
        # `exists`, not `isdir` (2026-09-04): in a git WORKTREE `.git` is a file holding a
        # gitdir: pointer, and the build brief has every builder edit a unit inside a nested
        # worktree. With isdir, such a unit was not a unit at all -- the checker silently
        # dropped it and graded eight clocks instead of thirteen while reporting no could-not-
        # look. A checker that can be blinded by how its input was checked out is not a checker.
        if os.path.exists(os.path.join(root, ".git")):
            found.append((entry, root, REMOTE.format(unit=entry)))
    found.append(("hub", HUB, HUB_REMOTE))
    return found


def workflows(tree: Served) -> tuple[dict[str, dict], dict[str, str]]:
    """({filename: parsed workflow}, {filename: parse error}), read at the served ref. A
    workflow GitHub cannot parse is a clock that does not exist, so the error is carried out
    and reported rather than swallowed or crashed on."""
    parsed: dict[str, dict] = {}
    broken: dict[str, str] = {}
    for name in tree.ls(".github/workflows"):
        if not name.endswith((".yml", ".yaml")):
            continue
        text = tree.show(f".github/workflows/{name}")
        if text is None:
            broken[name] = "the served ref names it and does not carry it"
            continue
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError as e:
            broken[name] = str(e).splitlines()[-1].strip()
            continue
        if isinstance(doc, dict):
            parsed[name] = doc
    return parsed, broken


def triggers(doc: dict) -> dict:
    """`on:` -- YAML 1.1 reads a bare `on` as the boolean True, so both keys."""
    on = doc.get("on", doc.get(True))
    return on if isinstance(on, dict) else {}


def crons(doc: dict) -> list[str]:
    return [s["cron"] for s in (triggers(doc).get("schedule") or []) if "cron" in s]


# --- the cage -----------------------------------------------------------------
def _env(doc: dict, job: dict) -> dict:
    merged = dict(doc.get("env") or {})
    merged.update(job.get("env") or {})
    return merged


# Shell punctuation that shows up in a `git add` line and is not a path.
_NOISE = {";", "do", "done", "&&", "||", "\\", "then", "fi", "|"}
_FOR = re.compile(r"\bfor\s+(\w+)\s+in\s+([^\n;]*)")


_TRIM = re.compile(r"""^[\s"';\\]+|[\s"';\\]+$""")


def _bare(word: str) -> str:
    return _TRIM.sub("", word).rstrip("/")


def _expand(word: str, env: dict) -> list[str]:
    """`${OBSERVATION_LANE}` and a loop variable bound to it both resolve to the
    paths they name. A word this checker cannot resolve comes back as itself and
    is then judged on its own merits -- an unresolvable path in a step that
    pushes the default branch is a fault, not a shrug."""
    match = re.fullmatch(r"\$\{?(\w+)\}?", _bare(word))
    if match and match.group(1) in env:
        return str(env[match.group(1)]).split()
    return [_bare(word)]


def _bindings(script: str, env: dict) -> dict:
    """`for path in ${OBSERVATION_LANE}` binds `path` to the lane. This is how
    every cage step in the estate is written, so the checker has to read it."""
    local = dict(env)
    for var, words in _FOR.findall(script):
        resolved = []
        for word in words.split():
            if word in _NOISE:
                continue
            resolved += _expand(word, local)
        if resolved:
            local[var] = " ".join(resolved)
    return local


def _allowed(path: str) -> bool:
    path = _bare(path)
    if not path or path in _NOISE or path.startswith("-"):
        return True                      # a flag or shell punctuation, not a path
    return any(path == a or path.startswith(a + "/") for a in ALLOW_LIST)


def _pushes_default_branch(script: str) -> bool:
    for args in _PUSH.findall(script):
        refspec = args.split("#", 1)[0]
        if re.search(r"\b(?:HEAD:)?(?:refs/heads/)?" + DEFAULT_BRANCH + r"\b", refspec):
            return True
        if "GITHUB_REF_NAME" in refspec:
            return True
        # a bare `git push` on a checkout of the default branch
        if not refspec.split():
            return True
        if refspec.split() == ["origin"]:
            return True
    return False


def _job_can_write(doc: dict, job: dict) -> bool:
    """`contents: write` anywhere in scope. Read from `permissions:`, which this
    checker never looked at before 2026-08-28 -- and capability is the only thing
    that catches a job whose writing happens inside an opaque tool (`npx renovate`,
    a `uses:` action, a called python script) rather than in a `run:` string."""
    for scope in (job.get("permissions"), doc.get("permissions")):
        if scope is None:
            continue
        if scope in ("write-all",):
            return True
        if isinstance(scope, dict):
            return str(scope.get("contents", "")) == "write"
        return False        # a job-level `permissions:` shadows the workflow's
    return False


def cage_faults(doc: dict, job: dict) -> list[str]:
    """Every way this scheduled job could commit a declaration.

    CEILING, named rather than implied: everything below reads each step's own
    inline `run:` string. A push from inside a called program (driftwood's
    propose-tier.yml pushes from platform/wargamer/tier_pr.py) or from a `uses:`
    action is invisible to it. That is why the capability check below --
    `contents: write` with no cage step -- is the load-bearing half, and why the
    PASS line this function's absence produces says "no shell step in this job
    stages a declaration" rather than a flat "caged"."""
    env = _env(doc, job)
    faults = []
    writes_default = False
    can_write = _job_can_write(doc, job)
    has_cage = any(_is_cage_step(s) for s in (job.get("steps") or []))
    if can_write and not has_cage:
        faults.append("is a scheduled job with `contents: write` and no `observation cage` "
                      "step -- whatever it writes (including from inside a `uses:` action or "
                      "a called script this checker cannot read) is uncaged")
    for step in job.get("steps") or []:
        uses = str(step.get("uses") or "")
        if uses and can_write and not any(uses.startswith(a) for a in INERT_ACTIONS):
            faults.append(f"step {uses!r} is a `uses:` action in a scheduled job with "
                          f"`contents: write` -- this checker reads only inline `run:` shell, "
                          f"so it cannot read what that action writes and cannot grade it caged")
        script = step.get("run") or ""
        if not script:
            continue
        if _pushes_default_branch(script):
            writes_default = True
        elif not _PUSH.search(script):
            continue
        # A step that opens a pull request is a PROPOSER: what it stages is a
        # diff a human reads and merges, so it may stage a declaration. A step
        # that pushes without opening one is writing to a branch nobody reviews,
        # so everything it stages must be an observation -- whether that branch
        # is `main` or the `observations` series branch.
        if "gh pr create" in script:
            continue
        where = DEFAULT_BRANCH if _pushes_default_branch(script) else "a branch, unreviewed"
        local = _bindings(script, env)
        if _STAGES_EVERYTHING.search(script):
            faults.append(
                f"runs `git commit -a` in a step that pushes {where} without opening a pull "
                f"request -- that stages every modified path, not the observation lane")
        for args in _ADD.findall(script):
            words = [w for w in args.split()
                     if not w.startswith("-") and _bare(w) not in _NOISE and _bare(w)]
            # A path operand SCOPES the add, whatever the flags: `git add -Af -- p`
            # stages p and nothing else. No operand at all (or `.`) is the whole tree.
            if not words or "." in [_bare(w) for w in words]:
                faults.append(
                    f"runs `git add{args.rstrip()}` -- no path operand, or one that stages the "
                    f"whole tree -- in a step that pushes {where} without opening a pull "
                    f"request; the observation lane {list(ALLOW_LIST)} must be named")
                continue
            for word in words:
                for path in _expand(word, local):
                    if not _allowed(path):
                        faults.append(
                            f"stages {path!r} in a step that pushes {where} without opening a "
                            f"pull request -- outside the observation lane {list(ALLOW_LIST)}")
    if not writes_default:
        return faults                    # a proposer: it never touches main at all
    lane = env.get("OBSERVATION_LANE")
    if not lane:
        faults.append("pushes the default branch but declares no OBSERVATION_LANE in env: -- "
                      "the cage step and the checker must read the same list")
    else:
        for path in str(lane).split():
            if not _allowed(path):
                faults.append(f"declares {path!r} in OBSERVATION_LANE, which is not an "
                              f"observation path")
    if not any(_is_cage_step(s) for s in (job.get("steps") or [])):
        faults.append("pushes the default branch with no `observation cage` step (one whose "
                      "shell actually resets the index, stages only OBSERVATION_LANE and fails "
                      "the run on anything else) to fail the run when the tree carries a "
                      "declaration")
    return faults


# The shell a real observation cage runs, as five substrings its `run:` must
# carry. 2026-08-29 review: this used to be satisfied by the step's NAME alone
# -- `any("observation cage" in step.name)` -- so a scheduled job with
# `contents: write` whose real writing happens inside a called script passed by
# carrying a step merely CALLED "the observation cage". That matters more than
# it would otherwise, because the server-side leg of ADR-0024 cannot be applied
# at all here (GitHub allows a push ruleset, the only kind carrying
# file_path_restriction, on private or internal repositories only, and these are
# public), so this checker plus the client-side step ARE the whole cage. A cage
# that is the whole cage is graded on what it does, not on what it is called.
# Two real shapes, both graded on what the shell does.
#   LANE  -- the job appends to OBSERVATION_LANE: reset the index first, stage
#            only the declared lane, judge the STAGED set against that same
#            list, and fail the run on anything else.
#   CLEAN -- the job declares nothing on the default branch at all (it opens a
#            pull request instead): assert the tree is clean and fail if it is
#            not.
# Either way the step must be able to FAIL the run; a cage that cannot fail is
# a print statement.
CAGE_SHELL_LANE = ("git reset", "OBSERVATION_LANE", "git add",
                   "git diff --cached --name-only", "exit 1")
CAGE_SHELL_CLEAN = ("git status --porcelain", "exit 1")


def _is_cage_step(step: dict) -> bool:
    """A step is the observation cage when its shell does the cage's work. The
    name is a label; this reads the `run:`."""
    if "observation cage" not in str(step.get("name") or ""):
        return False
    script = str(step.get("run") or "")
    return (all(f in script for f in CAGE_SHELL_LANE)
            or all(f in script for f in CAGE_SHELL_CLEAN))


def signed_artefact_faults(job: dict) -> list[str]:
    faults = []
    for step in job.get("steps") or []:
        for hit in signed_artefact_hits(step.get("run") or ""):
            faults.append(f"step {step.get('name') or '(unnamed)'!r} {hit} -- a clock may not "
                          f"mint or merge a signed artefact")
    return faults


def caged_line(doc: dict, job: dict) -> str:
    """The PASS sentence for a scheduled job with no fault, saying exactly what was read.

    Until ticket 142 it ended "nothing it runs is opaque to this checker" for every clean job,
    while `cage_faults`' own docstring names the ceiling: only inline `run:` shell is read, and
    a called program is invisible. Every twin-sweep ran hub Python under `contents: write` and
    read PASS with that sentence. Decided (ticket 142, delegated): NARROW the sentence rather
    than widen the fault, and derive the clause from the job -- name each program it runs and
    the permission it runs under. Widening would have turned every scheduled job that runs a
    script red at once (the three twin sweeps, three propose-tier jobs, three renovate runs,
    the publishers' fetches and the hub's own truth gate: 14 jobs on 2026-09-25) with no ticket
    owning any of them, and would have pre-empted ticket 142 item 1, whose twin-cage check is
    what grades the twin job's `contents: read` once ticket 143 has split the sweep. What a
    called program lands is graded after the fact by verify-lane.sh, and this line says so."""
    programs = called_programs(job)
    held = "contents: write" if _job_can_write(doc, job) else "no contents: write"
    if not programs:
        return ("caged -- no inline shell step in this job stages a declaration or mints a "
                "signed artefact, and every step is inline shell or an inert `uses:` action "
                "this checker read in full")
    return (f"caged as far as this checker reads -- no inline shell step stages a declaration "
            f"or mints a signed artefact; {len(programs)} program(s) it runs from its checkout "
            f"are not read here ({'; '.join(programs)}), so what they write is bounded by the "
            f"job's permission ({held}) and by verify-lane.sh's read of what landed, not by "
            f"this line")


def ruleset_state(remote: str) -> tuple[str, str]:
    """The SERVER-SIDE half of ADR-0024's cage, looked at rather than assumed.

    Until 2026-08-28 nothing checked this at all, and the committed
    `.github/rulesets/observation-lane.json` declared a shape GitHub does not
    accept (`file_path_restriction` is a PUSH rule; the file targeted a branch),
    so the leg the ADR called "on the server" had never existed on any repo.

    Returns (verdict, reason) where verdict is "in-force", "unavailable" or
    "missing"."""
    try:
        rules = json.loads(_gh("api", f"repos/{remote}/rulesets") or "[]")
    except (subprocess.SubprocessError, OSError, ValueError) as e:
        return ("unknown", str(e).splitlines()[0])
    if any(r.get("name") == "observation-lane" for r in rules):
        return ("in-force", "an observation-lane ruleset is applied")
    try:
        visibility = _gh("api", f"repos/{remote}", "--jq", ".visibility").strip()
    except (subprocess.SubprocessError, OSError):
        visibility = "unknown"
    if visibility == "public":
        return ("unavailable",
                "the repository is public and GitHub allows a push ruleset -- the only kind that "
                "carries file_path_restriction -- on private or internal repositories only, so "
                "the server-side leg of ADR-0024 cannot be applied here at all")
    return ("missing", f"the repository is {visibility} and carries no observation-lane ruleset")


def ruleset_line(unit: str, remote: str, live: bool, unreachable: str,
                 declared: bool, source=None) -> tuple[str, str]:
    """The 3b question -- is the server-side half of the cage in force? -- as exactly one
    verdict, always (eco-system ticket 83).

    This used to be an `if live and <rulesets dir exists>` with no else, so on every offline run
    the eight units' server-side questions emitted nothing at all: not PASS, not FAIL, not SKIP.
    A question that emits nothing is a fourth outcome. The gate cannot count it, the TRUTH line
    cannot carry it, and a reader sees eight questions that were never asked as eight that were
    not there. Both silences are could-not-looks and now say so.
    """
    if not live:
        return ("SKIP", f"{unit}: GitHub unreachable ({unreachable}) -- cannot look at whether "
                        f"the observation-lane ruleset is applied on {remote}, which is the "
                        f"server-side half of the cage (ADR-0024 point 3)")
    if not declared:
        return ("SKIP", f"{unit}: no .github/rulesets/ in this checkout, so there is no "
                        f"observation-lane ruleset declared for {remote} to be asked about; "
                        f"the client-side cage step and this checker are the whole cage here")
    try:
        verdict, reason = (source or Gh()).ruleset_state(remote)
    except CouldNotLook as e:
        return ("SKIP", f"{unit}: cannot look at whether the observation-lane ruleset is applied "
                        f"on {remote}, the server-side half of the cage (ADR-0024 point 3): {e}")
    if verdict == "in-force":
        return ("PASS", f"{unit}: the observation-lane ruleset is applied on {remote} -- "
                        f"the cage has its server-side half")
    if verdict == "unavailable":
        return ("SKIP", f"{unit}: no observation-lane ruleset on {remote}: {reason}. The "
                        f"client-side cage step and this checker are the whole cage today "
                        f"(ADR-0024 point 3, amended 2026-08-28)")
    if verdict == "missing":
        return ("FAIL", f"{unit}: {reason}, and it could be applied -- ADR-0024 point 3 "
                        f"claims a server-side leg this repository does not have")
    return ("SKIP", f"{unit}: could not read the rulesets on {remote} ({reason})")


def scheduled_jobs(doc: dict):
    if not crons(doc):
        return
    for name, job in (doc.get("jobs") or {}).items():
        yield name, job


# --- live ---------------------------------------------------------------------
def _gh(*args: str) -> str:
    done = subprocess.run(["gh", *args], capture_output=True, text=True, check=True,
                          timeout=60)
    return done.stdout


def landed_hours_ago(unit: str, workflow: str) -> float | None:
    """How long the workflow file has existed on the branch GitHub actually runs.

    `--first-parent` on the branch GitHub runs, NOT the file's own commit date.
    A change written on a branch keeps its authoring date through the landing, so
    asking when the file last changed answers the wrong question: on 2026-08-31
    these clocks were written 64 hours earlier and reached `main` that afternoon,
    and the file date would have called them overdue on the day they arrived.
    Walking first-parent attributes a landed branch to the commit that landed it.

    A clock that landed an hour ago and has not fired is not a stopped clock --
    GitHub has not reached a scheduled slot yet. Grading that as observed-false
    says the estate is broken when it is merely new, which is the same
    turn-absence-into-a-verdict mistake this file exists to refuse in the other
    direction. Observed live on 2026-08-31: ten clocks landed on `main` with the
    thin slice and every one read FAIL within the hour.

    None when the date cannot be read, and the caller then keeps the strict
    reading: an unknown age must not buy a clock a free pass.
    """
    try:
        out = subprocess.run(
            ["git", "-C", os.path.join(ESTATE, unit), "log", "--first-parent", "-1",
             "--format=%cI", f"origin/{DEFAULT_BRANCH}", "--",
             f".github/workflows/{workflow}"],
            capture_output=True, text=True, timeout=30, check=False).stdout.strip()
        if not out:
            return None
        landed = dt.datetime.fromisoformat(out)
        return (dt.datetime.now(landed.tzinfo) - landed).total_seconds() / 3600
    except (subprocess.SubprocessError, OSError, ValueError):
        return None


def newest_gradable(runs: list[dict], this_run_id: str | None) -> dict | None:
    """The newest scheduled run this process may grade -- never the run doing the grading.

    `gh run list --event schedule --limit 1` carries no status filter, and the run that reads it
    is itself a scheduled run of the workflow it is reading. So on every SCHEDULED truth.yml run
    the newest scheduled run of `truth.yml` was THIS run: `conclusion` "", `status`
    `in_progress`. With the excused conclusion narrowed to exactly `failure` (round 1 of this
    ticket), that graded `FAIL: hub/truth.yml: last scheduled run 0h ago concluded 'in_progress'`
    on every scheduled run for ever, named ticket 85 as its owner, and no fix in any estate
    repository could ever clear it -- a checker grading its own liveness by looking at itself.

    Two things, therefore. The run doing the grading is dropped by `databaseId` (GITHUB_RUN_ID is
    the run's `databaseId`; in Actions it is always set, and locally there is no self to drop).
    Then the newest COMPLETED run wins over a newer one still in flight: a run that has not
    finished has concluded nothing, and the last thing this clock actually did is the reading.
    Only when the window holds no completed run at all is an in-flight one returned, and
    `run_line` names it as a could-not-look rather than grading it.
    """
    others = [r for r in runs
              if not this_run_id or str(r.get("databaseId") or "") != str(this_run_id)]
    completed = [r for r in others if r.get("conclusion")]
    if completed:
        return completed[0]
    return others[0] if others else None


def last_run(remote: str, workflow: str) -> dict | None:
    # RUN_SCAN_LIMIT, not 1: the window has to be deep enough to hold a completed run behind this
    # run and behind any other still in flight. `databaseId` is what makes "not myself" decidable.
    raw = _gh("run", "list", "--repo", remote, "--workflow", workflow,
              "--event", "schedule", "--limit", str(RUN_SCAN_LIMIT),
              "--json", "createdAt,conclusion,status,databaseId")
    return newest_gradable(json.loads(raw or "[]"), os.environ.get("GITHUB_RUN_ID"))


def remote_crons(remote: str, workflow: str) -> tuple[str, list[str]]:
    """TRI-STATE, not None/[]. The `schedule:` GitHub is actually honouring, read
    from the copy of this workflow on the remote default branch:

      ("absent", [])    the file is not on main yet -- a locally-added clock has
                        not started, which is a could-not-look.
      ("unparsed", [])  the file is there and GitHub cannot parse it -- whatever
                        clock it declares does not run. A FAIL.
      ("timed", crons)  the file is there and carries a `schedule:`.
      ("untimed", [])   the file is there, parses, and carries NO `schedule:` --
                        the clock was REMOVED from main. A FAIL.

    Collapsing the last two into `[]` made a deleted `schedule:` read as the same
    SKIP as a not-yet-merged one, with a reason naming a merge that had already
    happened (review, 2026-08-28)."""
    try:
        raw = _gh("api", f"repos/{remote}/contents/.github/workflows/{workflow}",
                  "--jq", ".content")
    except subprocess.CalledProcessError:
        return ("absent", [])
    try:
        doc = yaml.safe_load(base64.b64decode(raw))
    except (yaml.YAMLError, ValueError):
        return ("unparsed", [])
    if not isinstance(doc, dict):
        return ("unparsed", [])
    found = crons(doc)
    return ("timed", found) if found else ("untimed", [])


# --- where the live facts come from (ticket 56) --------------------------------
class Offline:
    """No live facts at all, and the reason said out loud once per question."""

    live = False

    def __init__(self, reason: str) -> None:
        self.unreachable = reason

    def ruleset_state(self, remote: str) -> tuple[str, str]:
        raise CouldNotLook(self.unreachable)

    def remote_crons(self, remote: str, workflow: str) -> tuple[str, list[str]]:
        raise CouldNotLook(self.unreachable)

    def last_run(self, remote: str, workflow: str) -> dict | None:
        raise CouldNotLook(self.unreachable)

    def recording_history(self, remote: str) -> dict:
        raise CouldNotLook(self.unreachable)

    def merged_by(self, remote: str, sha: str) -> dict:
        """Who merged the pull request whose merge commit is `sha` (ticket 142): {"pr",
        "merged_by", "is_bot", "merged_at"}. A commit GitHub committed on a squash or rebase
        does not say who merged it, so lane.py asks here."""
        raise CouldNotLook(self.unreachable)


def merged_pulls(remote: str) -> dict[str, dict]:
    """{merge commit sha: who merged it}, for the newest MERGED_SCAN_LIMIT merged pull requests
    of `remote`. One GraphQL-backed call per unit; `mergedBy.login` reads `app/<name>` for an
    App (observed 2026-09-25: `app/pavc-other-hand`) and the login for a person."""
    raw = _gh("pr", "list", "--repo", remote, "--state", "merged",
              "--limit", str(MERGED_SCAN_LIMIT), "--json", "number,mergeCommit,mergedBy,mergedAt")
    found: dict[str, dict] = {}
    for pr in json.loads(raw or "[]"):
        sha = str((pr.get("mergeCommit") or {}).get("oid") or "")
        if not sha:
            continue
        who = pr.get("mergedBy") or {}
        found[sha] = {"pr": pr.get("number"), "merged_by": str(who.get("login") or ""),
                      "is_bot": bool(who.get("is_bot")), "merged_at": str(pr.get("mergedAt") or "")}
    return found


def _merge_reading(merges: dict | None, remote: str, sha: str, where: str) -> dict:
    if merges is None:
        raise CouldNotLook(f"{where} carries no merged-pull-request readings for {remote}")
    hit = merges.get(sha)
    if hit is None:
        raise CouldNotLook(f"no merged pull request on {remote} among the newest "
                           f"{MERGED_SCAN_LIMIT} names {sha[:9]} as its merge commit ({where})")
    return hit


class Gh(Offline):
    """`gh`, in a process that holds a credential. Never the gate job (ticket 56)."""

    live = True

    def __init__(self) -> None:
        super().__init__("gh is authenticated")
        self._merges: dict[str, dict[str, dict]] = {}

    def merged_by(self, remote: str, sha: str) -> dict:
        if remote not in self._merges:
            try:
                self._merges[remote] = merged_pulls(remote)
            except (subprocess.SubprocessError, OSError, ValueError) as e:
                raise CouldNotLook(f"gh could not list the merged pull requests of {remote}: "
                                   f"{str(e).splitlines()[0]}") from e
        return _merge_reading(self._merges[remote], remote, sha, "gh pr list")

    def ruleset_state(self, remote: str) -> tuple[str, str]:
        return ruleset_state(remote)

    def remote_crons(self, remote: str, workflow: str) -> tuple[str, list[str]]:
        return remote_crons(remote, workflow)

    def last_run(self, remote: str, workflow: str) -> dict | None:
        return last_run(remote, workflow)

    def recording_history(self, remote: str) -> dict:
        try:
            return lost_recordings.collect(remote, _gh)
        except (subprocess.SubprocessError, OSError, ValueError, KeyError) as e:
            raise CouldNotLook(f"recording history unavailable: {e}") from e


def binding_fault(doc: dict, env: dict) -> str:
    """Why this run may not grade from this verdict file, or "" when it may.

    Round 1 of ticket 56 bound the file to NOTHING: no run id, no repository, no sha, and its
    only freshness was its own `collected_at`. A well-formed file with every conclusion rewritten
    to "success" turned every red green and the gate said PASS (proved on this branch: 0 FAIL,
    50 PASS). The file now carries the run and the repository that wrote it, from the GitHub
    context, and a reader inside a workflow run refuses any file not written by that same run.

    This NARROWS the window; it does not close a trust boundary. The gate job runs 84 verify
    scripts from eight other organisations in the same job, as root over the whole workspace, and
    one of them could rewrite `schedules.py` itself -- or the verdict file and this check with
    it. What it stops is the cheap version: a stray or stale clocks.json on the path
    `CLOCK_VERDICT` names being graded from as if it were this run's own observation. It does NOT
    stop a file written inside this job and stamped with this run's own id, because every script
    in the job can read `GITHUB_RUN_ID` from the environment.
    Outside a workflow run (`GITHUB_RUN_ID` unset) there is no run to bind to and the check does
    not pretend otherwise: local grading is only as trustworthy as the local checkout.
    """
    run_id = str(env.get("GITHUB_RUN_ID") or "")
    if not run_id:
        return ""
    if str(doc.get("run_id") or "") != run_id:
        return (f"it was written by run {doc.get('run_id') or '(none)'} and this is run "
                f"{run_id} -- not this run's observation")
    repository = str(env.get("GITHUB_REPOSITORY") or "")
    if repository and str(doc.get("repository") or "") != repository:
        return (f"it was written in {doc.get('repository') or '(none)'} and this is "
                f"{repository} -- not this run's observation")
    return ""


class Verdict(Offline):
    """The facts a credentialled step already observed, read out of a JSON file.

    This is what lets the gate grade a clock while holding nothing: truth.yml's `clocks` job
    writes the file, the gate job reads it. Every absence is a NAMED could-not-look -- a unit the
    collector could not reach, a clock it did not collect, a file that is stale -- because a
    verdict file that quietly answers "no" would be worse than no file at all.
    """

    live = True

    def __init__(self, path: str) -> None:
        super().__init__(f"the clock verdict file {path} was read")
        self.path = path
        with open(path) as fh:
            doc = json.load(fh)
        if not isinstance(doc, dict) or doc.get("schema") != VERDICT_SCHEMA:
            raise ValueError(f"not a {VERDICT_SCHEMA} document")
        fault = binding_fault(doc, dict(os.environ))
        if fault:
            raise ValueError(fault)
        collected = dt.datetime.fromisoformat(doc["collected_at"])
        self.age_hours = (dt.datetime.now(collected.tzinfo) - collected).total_seconds() / 3600
        if self.age_hours > VERDICT_MAX_AGE_HOURS:
            raise ValueError(f"collected {self.age_hours:.0f}h ago, past the "
                             f"{VERDICT_MAX_AGE_HOURS}h freshness window")
        self.units = doc.get("units") or {}
        self.recordings = doc.get("recording_history") or {}
        self.collected_at = doc["collected_at"]

    def _unit(self, remote: str) -> dict:
        for entry in self.units.values():
            if entry.get("remote") == remote:
                if not entry.get("reachable", False):
                    raise CouldNotLook(f"the clock verdict file collected at {self.collected_at} "
                                       f"could not reach {remote} "
                                       f"({entry.get('unreachable_reason') or 'no reason given'})")
                return entry
        raise CouldNotLook(f"the clock verdict file collected at {self.collected_at} carries no "
                           f"entry for {remote} -- it was not collected, so nothing here observed "
                           f"it")

    def ruleset_state(self, remote: str) -> tuple[str, str]:
        rule = self._unit(remote).get("ruleset") or {}
        if "verdict" not in rule:
            raise CouldNotLook(f"the clock verdict file carries no ruleset reading for {remote}")
        return (str(rule["verdict"]), str(rule.get("reason") or ""))

    def _workflow(self, remote: str, workflow: str) -> dict:
        found = (self._unit(remote).get("workflows") or {}).get(workflow)
        if found is None:
            raise CouldNotLook(f"the clock verdict file carries no reading for "
                               f"{remote}/{workflow}")
        if found.get("error"):
            raise CouldNotLook(f"the clock verdict file records that {remote}/{workflow} could "
                               f"not be read ({found['error']})")
        return found

    def remote_crons(self, remote: str, workflow: str) -> tuple[str, list[str]]:
        found = self._workflow(remote, workflow)
        return (str(found["remote_state"]), list(found.get("remote_crons") or []))

    def last_run(self, remote: str, workflow: str) -> dict | None:
        return self._workflow(remote, workflow).get("run")

    def recording_history(self, remote: str) -> dict:
        if self.recordings.get("remote") != remote or self.recordings.get("error"):
            raise CouldNotLook("clock verdict carries no readable recording history for "
                               + remote + ": " + str(self.recordings.get("error") or "absent"))
        return self.recordings

    def merged_by(self, remote: str, sha: str) -> dict:
        entry = self._unit(remote)
        if entry.get("merges_error"):
            raise CouldNotLook(f"the clock verdict file records that the merged pull requests "
                               f"of {remote} could not be read ({entry['merges_error']})")
        return _merge_reading(entry.get("merges"), remote, sha,
                              f"the clock verdict file collected at {self.collected_at}")


def observer(offline: bool = False) -> Offline:
    """CLOCK_VERDICT first, then `gh`, then nothing -- and each fallback names itself."""
    path = os.environ.get("CLOCK_VERDICT")
    if path:
        try:
            return Verdict(path)
        except (OSError, ValueError, KeyError) as e:
            return Offline(f"CLOCK_VERDICT names {path}, which this run cannot grade from: "
                           f"{str(e).splitlines()[0]}. This job holds no GitHub credential on "
                           f"purpose (ticket 56), so it does not fall back to one")
    if offline:
        return Offline("--offline was asked for")
    try:
        _gh("auth", "status")
    except (subprocess.SubprocessError, OSError) as e:
        return Offline(str(e).splitlines()[0])
    return Gh()


# --- which open ticket owns a red clock (ticket 85) ----------------------------
def owners() -> dict[str, dict]:
    if not os.path.exists(OWNERS_PATH):
        return {}
    with open(OWNERS_PATH) as fh:
        return yaml.safe_load(fh) or {}


def ticket_status(number) -> str | None:
    """`open`, `resolved`, ... or None when no such ticket file exists at all."""
    found = glob.glob(os.path.join(HUB, ".scratch", "ecosystem", "issues", f"{number}-*.md"))
    if not found:
        return None
    with open(found[0]) as fh:
        for line in fh:
            if line.startswith("Status:"):
                return line.partition(":")[2].strip()
    return "unstated"


def owner_clause(unit: str, workflow: str, owned: dict[str, dict]) -> str:
    """What to append to a red clock's line so the red names its estate reason.

    Never a fourth outcome (ticket 83): a red stays a FAIL. This only says WHOSE it is.
    """
    entry = owned.get(f"{unit}/{workflow}")
    if not entry:
        return (" -- and no ticket in .scratch/ecosystem/issues names this clock in "
                "verify/schedules/clock-owners.yaml, so this red is unowned")
    number, why = entry.get("ticket"), entry.get("owns") or "no reason recorded"
    status = ticket_status(number)
    if status == "open":
        return f" -- ticket {number} owns it: {why}"
    if status is None:
        return (f" -- clock-owners.yaml names ticket {number}, and no such ticket file exists; "
                f"the map is stale")
    return (f" -- ticket {number} owns it ({why}), and that ticket reads {status!r}: either the "
            f"fix has not reached a scheduled run yet, or this red is a new one wearing an old "
            f"ticket's name")


def owners_faults(owned: dict[str, dict], clocks_seen: set[str]) -> list[str]:
    """The map cannot rot: every entry names a ticket that exists and a clock that exists."""
    faults = []
    for key, entry in sorted(owned.items()):
        number = (entry or {}).get("ticket")
        if ticket_status(number) is None:
            faults.append(f"clock-owners.yaml maps {key} to ticket {number}, and "
                          f".scratch/ecosystem/issues has no such ticket")
        if key not in clocks_seen:
            faults.append(f"clock-owners.yaml maps {key}, which is not a clock this checker "
                          f"grades -- the map names a workflow the estate does not require")
    return faults


# --- the check ----------------------------------------------------------------
def run_line(unit: str, workflow: str, run: dict, now: dt.datetime,
             owns: str = "") -> tuple[str, str]:
    """Grade ONE scheduled run: (status, sentence). Pure -- a dict, a clock and the time.

    In flight first, then age, then the run's OUTCOME. A run that dies in checkout, in the gitsign install or in
    the cage step records nothing and used to read as a healthy clock (live, 2026-08-28:
    "hub/truth.yml: last scheduled run 2h ago (failure)" graded PASS). truth.yml is the one
    documented exception: it ends `exit 1` whenever the gate is red, which is its normal state,
    and its observation lands before that.

    ponytail: the exception is by workflow name; the stronger check is to read the newest line of
    the lane itself (talk/truth.log, observations/<feed>.jsonl) off the remote and date it -- do
    that when a second clock needs an exception.
    """
    age = (now - dt.datetime.fromisoformat(
        run["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600
    # In flight FIRST, and a SKIP: a run that has not finished has concluded nothing, so there is
    # nothing to grade. Grading it as a red said "concluded 'in_progress'" -- a sentence that
    # blames a ticket for the clock still being at work (round 2 of ticket 56). `newest_gradable`
    # already prefers a completed run behind it, so reaching here means the window held none.
    if not run.get("conclusion"):
        # A run in flight has concluded nothing, so it is a could-not-look -- but only while it
        # could still finish. Past the same window a stopped clock fails on, a run that has not
        # finished IS a stopped clock, and calling it a could-not-look for ever would be the
        # unbounded green this ticket exists to stop.
        if age > PERIOD_HOURS:
            return ("FAIL", f"{unit}/{workflow}: the newest scheduled run started {age:.0f}h ago "
                            f"and is still {run.get('status') or 'unfinished'}, past the "
                            f"{PERIOD_HOURS}h window -- a run that never finishes records no "
                            f"observation, so the clock has stopped" + owns)
        return ("SKIP", f"{unit}/{workflow}: the newest scheduled run started {age:.0f}h ago and "
                        f"is still {run.get('status') or 'unfinished'} -- a run in flight has "
                        f"concluded nothing, and no completed scheduled run sits behind it in "
                        f"the last {RUN_SCAN_LIMIT}, so this clock is not observed either way")
    if age > PERIOD_HOURS:
        return ("FAIL", f"{unit}/{workflow}: last scheduled run was {age:.0f}h ago, past "
                        f"the {PERIOD_HOURS}h window (a daily period plus a day of slack "
                        f"for GitHub's own scheduling delay) -- the clock has stopped" + owns)
    conclusion = run["conclusion"]
    excused = RED_GATE_EXITS_NONZERO.get(workflow)
    if conclusion == "success":
        return ("PASS", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago (success)")
    if conclusion == excused:
        return ("PASS", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago "
                        f"({conclusion}), which is this clock's documented exit -- it records "
                        f"its observation and then re-raises the gate's own red verdict")
    return ("FAIL", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago concluded "
                    f"{conclusion!r} -- a clock whose run dies or is cancelled records no "
                    f"observation" + owns)


def check(offline: bool = False) -> int:
    source = observer(offline)
    live = source.live
    unreachable = source.unreachable
    owned = owners()
    clocks_seen: set[str] = set()

    try:
        history = source.recording_history(HUB_REMOTE)
        with open(os.path.join(HUB, "talk", "truth.log")) as fh:
            parsed = [parse_truth(line) for line in fh if line.startswith("TRUTH ")]
        recorded = {int(row["run"]) for row in parsed if row["run"].isdigit()}
        out("NOTE", lost_recordings.grade(history, recorded))
    except (CouldNotLook, ValueError, OSError) as e:
        out("SKIP", f"hub/truth.yml: LOST RECORDING count=unknown -- {e}")

    now = dt.datetime.now(dt.timezone.utc)
    for unit, root, remote in units():
        # The SERVED ref, never the working tree (ticket 142). A unit whose origin/main cannot
        # be read is one named could-not-look; nothing of it is graded from what is on disk.
        tree, how = served(root)
        if tree is None:
            out("SKIP", f"{unit}: {how} -- the served ref is what GitHub runs a clock from, "
                        f"and the working tree is not a stand-in for it, so none of this "
                        f"unit's clocks is graded here")
            continue
        print(f"INFO: {unit}: graded at origin/{DEFAULT_BRANCH}@{tree.sha[:9]} ({how})")
        need = required_clocks(unit, tree) if unit != "hub" else {
            "truth.yml": "the hub owns the daily truth surface (ticket 03)"}
        found, broken = workflows(tree)
        for name, why in sorted(broken.items()):
            out("FAIL", f"{unit}/{name}: GitHub cannot parse this workflow, so whatever clock "
                        f"it declares does not run ({why})")

        # 1. the clocks exist, and they are timed
        for workflow, why in sorted(need.items()):
            doc = found.get(workflow)
            if doc is None:
                out("FAIL", f"{unit}: no .github/workflows/{workflow} -- {why}")
                continue
            if not crons(doc):
                out("FAIL", f"{unit}/{workflow}: no `schedule:` -- {why}")
                continue
            # D2 is "open a PR only when the computed bump is not none". A fetch clock with no
            # `gh pr create` anywhere cannot do that: it observes what its own repository already
            # publishes and compares it against nothing. platform, nist and ico are that shape.
            #
            # 2026-09-04, ticket 56. That used to be a SKIP, which was wrong twice over. SKIP
            # means COULD NOT LOOK, and this checker looked: it parsed the workflow and saw no
            # `gh pr create`. And it is not a shortfall the estate has failed to decide -- ADR-0024
            # Consequences settles it in as many words ("platform, nist, ico and insurer observe
            # rather than fetch. None ships an upstream fetcher yet, so their clock records what
            # they have published and the sha256 of its payload each day. That is a real series").
            # So the observed truth is a PASS whose sentence says exactly what it does and does
            # not cover: three unconditional SKIPs used to hold verify-schedules.sh at exit 3
            # forever, whatever any credential could see.
            observes_only = workflow == "fetch.yml" and not any(
                "gh pr create" in (s.get("run") or "")
                for j in (doc.get("jobs") or {}).values()
                for s in (j.get("steps") or []))
            note = ("" if not observes_only else
                    f"; it opens no pull request anywhere, so it records what {unit} has already "
                    f"published and the hash of it rather than reading upstream and computing a "
                    f"bump -- D2's proposal half is vacuous for a party whose feed is its own "
                    f"artefact (ADR-0024 Consequences), and the upstream-reading half of story 9 "
                    f"is not built here and is not graded by this line")
            out("PASS", f"{unit}/{workflow}: daily clock at {', '.join(crons(doc))} -- {why}{note}")

        # 2 and 3. every scheduled job in the repository, required or not
        for workflow, doc in sorted(found.items()):
            for job_name, job in scheduled_jobs(doc):
                faults = cage_faults(doc, job) + signed_artefact_faults(job)
                for fault in faults:
                    out("FAIL", f"{unit}/{workflow} job {job_name}: {fault}")
                if not faults:
                    out("PASS", f"{unit}/{workflow} job {job_name}: {caged_line(doc, job)}")

        # 3b. live: the server-side half of the cage, observed on the remote.
        # Every unit gets a line here (eco-system ticket 83). This block used to emit nothing
        # when it could not look -- neither PASS nor FAIL nor SKIP -- and a question that emits
        # nothing is a fourth outcome the gate cannot count: eight server-side questions simply
        # vanished from the offline run. A could-not-look is a SKIP, said out loud, per unit.
        declared = tree.isdir(".github/rulesets")
        out(*ruleset_line(unit, remote, live, unreachable, declared, source))

        # 4. live: did each clock run inside its period?
        for workflow in sorted(need):
            if workflow not in found:
                continue
            clocks_seen.add(f"{unit}/{workflow}")
            owns = owner_clause(unit, workflow, owned)
            if not live:
                # Named per unit, on purpose: "GitHub is unreachable" is a
                # could-not-look about THIS clock, not a blanket excuse.
                # A refused verdict file is not an unreachable GitHub: the run declined to grade
                # from it. Both are could-not-looks, and each says which it was.
                why = ("this run declined to grade from the clock verdict"
                       if "cannot grade from" in unreachable else "GitHub unreachable")
                out("SKIP", f"{unit}/{workflow}: {why} ({unreachable}) -- "
                            f"cannot look at whether this clock ran inside its period")
                continue
            try:
                state, _remote_schedule = source.remote_crons(remote, workflow)
                # Two readings of the same ref: origin/main as fetched into this checkout
                # (`found`, above) and the copy GitHub's API serves for the default branch.
                # They differ only when the fetch is stale or GitHub has moved on since.
                if state == "absent":
                    out("SKIP", f"{unit}/{workflow}: GitHub serves no such file on "
                                f"{remote}@{DEFAULT_BRANCH} while origin/{DEFAULT_BRANCH}@"
                                f"{tree.sha[:9]} as fetched here carries it -- the two readings "
                                f"of the served ref disagree, so whether a scheduled run could "
                                f"have happened is not observed")
                    continue
                if state == "unparsed":
                    out("FAIL", f"{unit}/{workflow}: the copy on {remote}@{DEFAULT_BRANCH} "
                                f"does not parse, so GitHub runs no clock from it at all" + owns)
                    continue
                if state == "untimed":
                    # Two very different worlds, and the old code called both SKIP with a
                    # reason that becomes false after the merge. The FETCHED copy decides.
                    if crons(found.get(workflow) or {}):
                        out("SKIP", f"{unit}/{workflow}: the copy GitHub serves on "
                                    f"{remote}@{DEFAULT_BRANCH} carries no `schedule:` while "
                                    f"origin/{DEFAULT_BRANCH}@{tree.sha[:9]} as fetched here "
                                    f"does -- the two readings of the served ref disagree, and "
                                    f"GitHub runs its own copy and nothing else")
                    else:
                        out("FAIL", f"{unit}/{workflow}: neither {remote}@{DEFAULT_BRANCH} as "
                                    f"GitHub serves it nor origin/{DEFAULT_BRANCH}@"
                                    f"{tree.sha[:9]} as fetched here carries a `schedule:` -- "
                                    f"the clock was removed from the branch GitHub actually "
                                    f"runs" + owns)
                    continue
                run = source.last_run(remote, workflow)
            except CouldNotLook as e:
                out("SKIP", f"{unit}/{workflow}: cannot look at whether this clock ran inside its "
                            f"period ({e})")
                continue
            except (subprocess.SubprocessError, OSError) as e:
                out("SKIP", f"{unit}/{workflow}: GitHub unreachable for {remote} "
                            f"({str(e).splitlines()[0]})")
                continue
            if run is None:
                landed = landed_hours_ago(unit, workflow)
                if landed is not None and landed < PERIOD_HOURS:
                    out("SKIP", f"{unit}/{workflow}: on {remote}@{DEFAULT_BRANCH} with a "
                                f"`schedule:` that landed {landed:.0f}h ago, inside the "
                                f"{PERIOD_HOURS}h window -- GitHub has not reached a scheduled "
                                f"slot yet, so there is nothing to observe rather than a clock "
                                f"observed stopped")
                    continue
                out("FAIL", f"{unit}/{workflow}: on {remote}@{DEFAULT_BRANCH} with a "
                            f"`schedule:` but GitHub has never run it on that schedule"
                            + (f", and it landed {landed:.0f}h ago, past the {PERIOD_HOURS}h "
                               f"window -- it has had its chance" if landed is not None else
                               ", and how long it has been there could not be read, so the "
                               "strict reading stands") + owns)
                continue
            out(*run_line(unit, workflow, run, now, owns))

    for fault in owners_faults(owned, clocks_seen):
        out("FAIL", fault)

    if "FAIL" in LINES:
        return 1
    if "SKIP" in LINES:
        return 3
    return 0


# --- the collector: the credentialled half, in a job of its own (ticket 56) ---
def collect() -> dict:
    """The four live facts, as facts. No verdict, no grade, no credential in the output.

    Runs where a credential is allowed to be -- truth.yml's `clocks` job, which holds
    `actions: read` and runs no third-party code -- so that `check` can grade the clocks from a
    job that holds nothing. Every failure is recorded as a reason in the document rather than
    raised, so one unreachable organisation does not blind the other eight.
    """
    doc: dict = {
        "schema": VERDICT_SCHEMA,
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "collector": "verify/schedules/schedules.py clocks",
        # What binds the file to a run instead of to nobody (`binding_fault`). Straight from the
        # GitHub context, empty outside Actions, and never anything the file's reader supplies.
        "run_id": os.environ.get("GITHUB_RUN_ID", ""),
        "repository": os.environ.get("GITHUB_REPOSITORY", ""),
        "units": {},
    }
    try:
        doc["recording_history"] = {"remote": HUB_REMOTE,
                                    **lost_recordings.collect(HUB_REMOTE, _gh)}
    except (subprocess.SubprocessError, OSError, ValueError, KeyError) as e:
        doc["recording_history"] = {"remote": HUB_REMOTE, "error": str(e)}
    for unit, root, remote in units():
        entry: dict = {"remote": remote, "reachable": True, "unreachable_reason": "",
                       "ruleset": {}, "workflows": {}}
        doc["units"][unit] = entry
        try:
            verdict, reason = ruleset_state(remote)
            entry["ruleset"] = {"verdict": verdict, "reason": reason}
        except (subprocess.SubprocessError, OSError, ValueError) as e:
            entry["reachable"] = False
            entry["unreachable_reason"] = str(e).splitlines()[0]
            continue
        # who merged each merged pull request, for lane.py's read of a commit GitHub committed
        # (ticket 142): a fact, recorded per unit, with its own failure named per unit
        try:
            entry["merges"] = merged_pulls(remote)
        except (subprocess.SubprocessError, OSError, ValueError) as e:
            entry["merges_error"] = str(e).splitlines()[0]
        tree, how = served(root)
        entry["served"] = {"sha": tree.sha if tree else "", "how": how}
        if tree is None:
            continue
        need = required_clocks(unit, tree) if unit != "hub" else {"truth.yml": ""}
        found, _broken = workflows(tree)
        for workflow in sorted(need):
            if workflow not in found:
                continue
            seen: dict = {}
            entry["workflows"][workflow] = seen
            try:
                state, remote_schedule = remote_crons(remote, workflow)
                seen["remote_state"] = state
                seen["remote_crons"] = remote_schedule
                seen["run"] = last_run(remote, workflow) if state == "timed" else None
            except (subprocess.SubprocessError, OSError, ValueError) as e:
                seen["error"] = str(e).splitlines()[0]
    return doc


def clocks(out_path: str) -> int:
    doc = collect()
    with open(out_path, "w") as fh:
        json.dump(doc, fh, indent=2, sort_keys=True)
        fh.write("\n")
    reached = sum(1 for u in doc["units"].values() if u["reachable"])
    runs = sum(len(u["workflows"]) for u in doc["units"].values())
    print(f"ok  clock verdict written to {out_path}: {reached} of {len(doc['units'])} "
          f"organisations reached, {runs} clock(s) read")
    for unit, u in sorted(doc["units"].items()):
        if not u["reachable"]:
            print(f"    {unit}: NOT reached -- {u['unreachable_reason']}")
    return 0


# --- selfcheck: planted fixtures, each refusal must bite ----------------------
def selfcheck() -> None:
    def wf(text):
        return yaml.safe_load(text)

    caged = wf("""
env:
  OBSERVATION_LANE: "talk/truth.log drift/samples.jsonl talk/captures observations"
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - name: observe
        run: |
          echo hi >> observations/x.jsonl
      - name: the observation cage -- never a declaration
        run: |
          git reset -q
          for p in ${OBSERVATION_LANE}; do git add -A -- "$p"; done
          for f in $(git diff --cached --name-only); do
            case "$f" in observations/*) ;; *) exit 1 ;; esac
          done
          git commit -S -m x
          git push origin "HEAD:${GITHUB_REF_NAME}"
""")
    assert cage_faults(caged, caged["jobs"]["sweep"]) == [], \
        cage_faults(caged, caged["jobs"]["sweep"])
    assert signed_artefact_faults(caged["jobs"]["sweep"]) == []

    # (0) a step NAMED the observation cage whose shell does none of the cage's
    # work. Until 2026-08-29 the name alone satisfied the check, so this passed.
    named_only = wf("""
env: {OBSERVATION_LANE: "observations"}
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - name: the observation cage
        run: |
          echo "trust me"
          git push origin "HEAD:${GITHUB_REF_NAME}"
""")
    faults = cage_faults(named_only, named_only["jobs"]["sweep"])
    assert any("observation cage" in f for f in faults), faults

    # --- the five shapes that read as "caged" until 2026-08-28 ----------------
    def sweep_faults(text):
        d = wf(text)
        return cage_faults(d, d["jobs"]["sweep"])

    # (1) `git add -A` with no path operand at all
    faults = sweep_faults("""
env: {OBSERVATION_LANE: "observations"}
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - name: the observation cage
        run: |
          git add -A
          git push origin main
""")
    assert any("stages the whole tree" in f or "no path operand" in f for f in faults), faults

    # (2) `git commit -am` stages every modified path
    faults = sweep_faults("""
env: {OBSERVATION_LANE: "observations"}
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - name: the observation cage
        run: |
          git commit -am retier
          git push origin main
""")
    assert any("git commit -a" in f for f in faults), faults

    # (3) a scheduled job with `contents: write` and no cage step -- the
    #     capability check, which is the only thing that catches (4) and (5)
    faults = sweep_faults("""
on:
  schedule: [{cron: "5 7 * * *"}]
permissions: {contents: write}
jobs:
  sweep:
    steps:
      - run: bash scripts/publish-tier.sh
""")
    assert any("contents: write" in f for f in faults), faults

    # (4) a `uses:` action under contents: write is unresolvable, not a pass
    faults = sweep_faults("""
on:
  schedule: [{cron: "5 7 * * *"}]
permissions: {contents: write}
jobs:
  sweep:
    steps:
      - name: the observation cage
        run: git push origin main
      - uses: stefanzweifel/git-auto-commit-action@v5
        with: {branch: main}
""")
    assert any("uses:" in f for f in faults), faults

    # (5) ...and a job WITHOUT contents: write is not tarred with that brush
    ok = sweep_faults("""
on:
  schedule: [{cron: "5 7 * * *"}]
permissions: {contents: read}
jobs:
  sweep:
    steps:
      - uses: actions/checkout@v4
      - run: python3 twin/sweep.py
""")
    assert ok == [], ok

    # a declaration staged in the same step that pushes main
    leaky = wf("""
env: {OBSERVATION_LANE: "observations"}
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - name: the observation cage
        run: |
          git add -- composed/evidence.json
          git push origin main
""")
    faults = cage_faults(leaky, leaky["jobs"]["sweep"])
    assert any("composed/evidence.json" in f for f in faults), faults

    # main pushed with no allow-list declared, and no cage step
    naked = wf("""
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  sweep:
    steps:
      - run: git push origin main
""")
    faults = cage_faults(naked, naked["jobs"]["sweep"])
    assert any("no OBSERVATION_LANE" in f for f in faults), faults
    assert any("observation cage" in f for f in faults), faults

    # a proposer never touches main, so it needs no lane and no cage step
    proposer = wf("""
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  propose:
    steps:
      - run: |
          git add -- deploy/pod.yaml
          git push origin "wargamer/retune-x"
          gh pr create --base main
""")
    assert cage_faults(proposer, proposer["jobs"]["propose"]) == []

    # ...but a step that pushes a branch WITHOUT opening a pull request is
    # writing where nobody reviews, so it is caged too -- the observations
    # series branch included.
    sideways = wf("""
on:
  schedule: [{cron: "5 7 * * *"}]
jobs:
  observe:
    steps:
      - run: |
          git add -- penalty-schema/v3/feed.json
          git push origin observations
""")
    faults = cage_faults(sideways, sideways["jobs"]["observe"])
    assert any("feed.json" in f for f in faults), faults

    # a clock that can cut a tag or a release, or merge a PR -- every shape ticket 30's facts
    # of 2026-09-25 found missing, probed BOTH WAYS: the write is a fault, its read twin is not
    def can_mint(line: str) -> bool:
        minting = wf(f"""
on:
  schedule: [{{cron: "5 7 * * *"}}]
jobs:
  cut:
    steps:
      - run: |
          {line}
""")
        return bool(signed_artefact_faults(minting["jobs"]["cut"]))

    for line in (
            "git tag -s v1.0.0", "git -C unit tag v2",
            "gh release create v1.0.0", "gh release upload v1 file", "gh release edit v1 --draft=false",
            "gh pr merge 4 --merge", "gh pr merge 4 --squash", "gh pr edit 4 --auto",
            # a merge by REST, in every method spelling, and by curl
            "gh api -X PUT repos/o/r/pulls/4/merge", "gh api --method PUT repos/o/r/pulls/4/merge",
            "gh api -XPUT repos/o/r/pulls/4/merge -f merge_method=squash",
            "gh api repos/o/r/pulls/4/merge", "gh api --method=put /repos/o/r/pulls/4/merge",
            "curl -X PUT -H 'Authorization: Bearer $T' https://api.github.com/repos/o/r/pulls/4/merge",
            'curl --request PUT "https://api.github.com/repos/o/r/pulls/${N}/merge"',
            "gh api -X POST repos/o/r/merges -f base=main -f head=x",
            # a release or a ref minted by REST
            "gh api repos/o/r/releases -f tag_name=v1 -f name=v1",
            "gh api --method POST repos/o/r/releases --input body.json",
            "gh api repos/o/r/git/refs -f ref=refs/tags/v1 -f sha=$SHA",
            "gh api -X PATCH repos/o/r/git/refs/heads/main -f sha=$SHA",
            "curl -d '{\"ref\":\"refs/tags/v1\"}' https://api.github.com/repos/o/r/git/refs",
            "curl -X POST https://api.github.com/repos/o/r/releases --data @body.json",
            "curl -X DELETE https://api.github.com/repos/o/r/git/refs/tags/v1",
            # a continuation line carries the method
            "gh api \\\n            -X PUT \\\n            repos/o/r/pulls/4/merge",
            # a ref moved directly, and a tag pushed by refspec
            "git update-ref refs/heads/main $SHA", "git -C unit update-ref -d refs/tags/v1",
            "git push origin v1.2.3", "git push -q origin twin/v0.1.0", "git push origin HEAD:v1.2.3",
            "git push origin refs/tags/v1.2.3", "git push --tags origin", "git push origin --follow-tags",
            "git push origin tag v1.2.3", "git -C unit push origin twin/v0.1.0",
            # GraphQL
            "gh api graphql -f query='mutation { mergePullRequest(input: {pullRequestId: \"x\"}) { clientMutationId } }'",
            "gh api graphql -f query='mutation { createRef(input: {repositoryId: \"r\", name: "
            "\"refs/tags/v1\", oid: \"s\"}) { ref { id } } }'",
    ):
        assert can_mint(line), f"not caught: {line!r}"
    for line in (
            "git push origin main", "git push origin HEAD:${GITHUB_REF_NAME}", "git push origin observations",
            "git push -u origin wargamer/retune-x", "git push origin HEAD:refs/heads/fetch/policy-2.0.0",
            "git describe --tags --always", "git update-index --refresh",
            "gh release list", "gh release view v1", "gh release download v1 -p '*.tgz'",
            "gh pr create --base main --title x", "gh pr view 4", "gh pr list --state merged",
            "gh api repos/o/r/pulls/4", "gh api repos/o/r/pulls/4/files", "gh api repos/o/r/pulls/4/commits",
            "gh api repos/o/r/releases/latest", "gh api repos/o/r/releases --jq '.[0].tag_name'",
            "gh api repos/o/r/git/refs/tags/v1", "gh api repos/o/r/git/ref/tags/v1",
            "gh api repos/o/r/rulesets", "gh api repos/o/r/contents/.github/workflows/x.yml --jq .content",
            "gh run list --repo o/r --workflow x.yml --json conclusion",
            'curl -sSL -o gitsign "https://github.com/sigstore/gitsign/releases/download/v1/gitsign"',
            'curl -fsSL -o kyverno.tgz "https://github.com/kyverno/kyverno/releases/download/v1/x.tgz"',
            "curl -f -o x https://github.com/o/r/releases/download/v1/x",
            "curl -s https://api.github.com/repos/o/r/releases/latest | jq -r .tag_name",
            "curl -s https://api.github.com/repos/o/r/git/refs/tags/v1",
            "# gh api -X PUT repos/o/r/pulls/4/merge is what a merge would look like",
            "echo 'the rulesets are applied by the owner with gh api'",
            "python3 twin/emit-forward-intel.py", "npx --yes renovate@44.37.1",
    ):
        assert not can_mint(line), f"wrongly caught: {line!r}"

    # the programs a job runs from its checkout are enumerated, and the PASS line names them
    # rather than calling them readable (ticket 142)
    sweeping = wf("""
on:
  schedule: [{cron: "5 7 * * *"}]
permissions: {contents: write}
env: {OBSERVATION_LANE: "observations"}
jobs:
  sweep:
    steps:
      - uses: actions/checkout@v4
      - run: |
          # a comment naming python3 x.py is not a program
          pip install pyyaml
          python3 twin/emit-forward-intel.py --check; feed_rc=$?
          python3 .github/scripts/rederive-signals.py
          if python3 -m unittest discover -s tests; then echo ok; fi
          python3 - >> observations/twin-sweep.jsonl <<'PY'
          print("{}")
          PY
          bash scripts/render.sh && ./drift/five-facts.py sample
          KIND_VERSION=1 npx --yes renovate@44.37.1
          echo done
      - name: the observation cage -- never a declaration
        run: |
          git reset -q
          for p in ${OBSERVATION_LANE}; do git add -A -- "$p"; done
          for f in $(git diff --cached --name-only); do
            case "$f" in observations/*) ;; *) exit 1 ;; esac
          done
          git commit -m x
          git push origin "HEAD:${GITHUB_REF_NAME}"
""")
    programs = called_programs(sweeping["jobs"]["sweep"])
    assert programs == ["python3 twin/emit-forward-intel.py", "python3 .github/scripts/rederive-signals.py",
                        "python3 -m unittest", "python3 - (heredoc)", "bash scripts/render.sh",
                        "./drift/five-facts.py", "npx renovate@44.37.1"], programs
    assert _program_name('python3 -c "import x"') == "python3 -c (inline)"
    line = caged_line(sweeping, sweeping["jobs"]["sweep"])
    assert line.startswith("caged as far as this checker reads") and "7 program(s)" in line, line
    assert "contents: write" in line and "verify-lane.sh" in line and "opaque" not in line, line
    assert called_programs(caged["jobs"]["sweep"]) == [], called_programs(caged["jobs"]["sweep"])
    assert caged_line(caged, caged["jobs"]["sweep"]).startswith("caged -- no inline shell step"), \
        caged_line(caged, caged["jobs"]["sweep"])

    # an UNSCHEDULED workflow that cuts a tag is exactly what cut-release.yml is
    dispatch = wf("""
on: {workflow_dispatch: {}}
jobs:
  cut:
    steps:
      - run: git tag -s v1.0.0
""")
    assert list(scheduled_jobs(dispatch)) == [], "only scheduled jobs are caged"

    # 3b: the server-side question always answers, and a could-not-look says which one it is
    # (eco-system ticket 83). No branch of it may return nothing.
    st, msg = ruleset_line("driftwood", "org/driftwood", False, "gh auth status failed", True)
    assert st == "SKIP" and "GitHub unreachable" in msg and "server-side half" in msg, msg
    st, msg = ruleset_line("feeds", "org/feeds", True, "", False)
    assert st == "SKIP" and "no .github/rulesets/" in msg, msg

    # --- the clock verdict file: the gate grades liveness holding no credential (ticket 56) ---
    import tempfile
    now = dt.datetime.now(dt.timezone.utc)

    def verdict_file(collected_at, units_doc, schema=VERDICT_SCHEMA, run_id=None):
        # Stamped with THIS run, because that is what a real verdict file carries: inside Actions
        # the fixtures must bind like the article, and outside it (GITHUB_RUN_ID unset) both are
        # unbound alike.
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"schema": schema, "collected_at": collected_at, "collector": "selfcheck",
                   "run_id": os.environ.get("GITHUB_RUN_ID", "") if run_id is None else run_id,
                   "repository": os.environ.get("GITHUB_REPOSITORY", ""),
                   "units": units_doc}, fh)
        fh.close()
        return fh.name

    fresh = (now - dt.timedelta(minutes=3)).isoformat(timespec="seconds")
    inside = (now - dt.timedelta(hours=6)).isoformat(timespec="seconds").replace("+00:00", "Z")
    stale_run = (now - dt.timedelta(hours=PERIOD_HOURS + 5)).isoformat(
        timespec="seconds").replace("+00:00", "Z")
    body = {"feeds": {
        "remote": "org/feeds", "reachable": True,
        "ruleset": {"verdict": "unavailable", "reason": "the repository is public"},
        "workflows": {
            "ok.yml": {"remote_state": "timed", "remote_crons": ["17 3 * * *"],
                       "run": {"createdAt": inside, "conclusion": "success"}},
            "red.yml": {"remote_state": "timed", "remote_crons": ["17 3 * * *"],
                        "run": {"createdAt": inside, "conclusion": "failure"}},
            "cancelled.yml": {"remote_state": "timed", "remote_crons": ["17 3 * * *"],
                              "run": {"createdAt": inside, "conclusion": "cancelled"}},
            "stopped.yml": {"remote_state": "timed", "remote_crons": ["17 3 * * *"],
                            "run": {"createdAt": stale_run, "conclusion": "success"}},
            "broken.yml": {"error": "HTTP 404"},
        }}}
    path = verdict_file(fresh, body)
    v = Verdict(path)
    assert v.live
    assert v.ruleset_state("org/feeds")[0] == "unavailable"
    assert v.remote_crons("org/feeds", "ok.yml") == ("timed", ["17 3 * * *"])
    assert v.last_run("org/feeds", "ok.yml")["conclusion"] == "success"
    # every absence is a NAMED could-not-look, never a quiet "no"
    for call, want in (
            (lambda: v.last_run("org/nowhere", "ok.yml"), "carries no entry for"),
            (lambda: v.last_run("org/feeds", "missing.yml"), "carries no reading for"),
            (lambda: v.last_run("org/feeds", "broken.yml"), "could not be read")):
        try:
            call()
            raise AssertionError("a missing fact must be a could-not-look, not a None")
        except CouldNotLook as e:
            assert want in str(e), e
    # an unreachable ORGANISATION blinds only itself
    one_down = verdict_file(fresh, {"ico": {"remote": "org/ico", "reachable": False,
                                            "unreachable_reason": "HTTP 403"}})
    try:
        Verdict(one_down).last_run("org/ico", "fetch.yml")
        raise AssertionError("an unreachable org must be a could-not-look")
    except CouldNotLook as e:
        assert "HTTP 403" in str(e), e
    # a stale file, and a file that is not a verdict at all: refused at construction, and the
    # caller falls back to Offline with the reason -- never to a credential the gate lacks
    for bad, why in ((verdict_file((now - dt.timedelta(hours=VERDICT_MAX_AGE_HOURS + 2))
                                   .isoformat(timespec="seconds"), body), "freshness window"),
                     (verdict_file(fresh, body, schema="something-else/v9"), "clock-verdict/v1")):
        try:
            Verdict(bad)
            raise AssertionError(f"a verdict file that is {why} must be refused")
        except ValueError as e:
            assert why in str(e), e
        os.environ["CLOCK_VERDICT"] = bad
        try:
            fell_back = observer()
        finally:
            del os.environ["CLOCK_VERDICT"]
        assert not fell_back.live and "does not fall back" in fell_back.unreachable, \
            fell_back.unreachable
    # ...and no CLOCK_VERDICT at all, with --offline, is the plain offline source
    assert not observer(offline=True).live

    # who merged (ticket 142): read from the verdict file when it carries the readings, and a
    # named could-not-look for a unit with none, a unit whose listing failed, or a commit no
    # merged pull request names; offline is a could-not-look too
    merged = verdict_file(fresh, {
        "feeds": {"remote": "org/feeds", "reachable": True, "ruleset": {}, "workflows": {},
                  "merges": {"a" * 40: {"pr": 7, "merged_by": "app/github-actions",
                                        "is_bot": True, "merged_at": inside}}},
        "ico": {"remote": "org/ico", "reachable": True, "ruleset": {}, "workflows": {},
                "merges_error": "HTTP 403"},
        "nist": {"remote": "org/nist", "reachable": True, "ruleset": {}, "workflows": {}}})
    who = Verdict(merged)
    assert who.merged_by("org/feeds", "a" * 40)["merged_by"] == "app/github-actions"
    for remote, sha, want in (("org/feeds", "b" * 40, "no merged pull request"),
                              ("org/ico", "a" * 40, "HTTP 403"),
                              ("org/nist", "a" * 40, "no merged-pull-request readings"),
                              ("org/nowhere", "a" * 40, "carries no entry")):
        try:
            who.merged_by(remote, sha)
            raise AssertionError(f"{remote}: who merged must be a could-not-look here")
        except CouldNotLook as e:
            assert want in str(e), (remote, e)
    try:
        Offline("no network").merged_by("org/feeds", "a" * 40)
        raise AssertionError("offline must be a could-not-look")
    except CouldNotLook:
        pass

    # the served ref is what is read (ticket 142): a unit's working tree carries a twin/ overlay
    # and a workflow that origin/main does not, and neither is graded; the unit's own copy of a
    # workflow on origin/main is; no origin/main at all is (None, why), never the working tree
    import shutil
    with tempfile.TemporaryDirectory() as tmp:
        def git(*args):
            subprocess.run(["git", "-c", "commit.gpgsign=false", "-c", "core.hooksPath=" + tmp,
                            *args], check=True, capture_output=True, text=True,
                           env=dict(os.environ, GIT_AUTHOR_NAME="s", GIT_AUTHOR_EMAIL="s@s",
                                    GIT_COMMITTER_NAME="s", GIT_COMMITTER_EMAIL="s@s"))
        origin = os.path.join(tmp, "unit.git")
        git("init", "-q", "--bare", "-b", DEFAULT_BRANCH, origin)
        clone = os.path.join(tmp, "unit")
        git("init", "-q", "-b", DEFAULT_BRANCH, clone)
        git("-C", clone, "remote", "add", "origin", origin)
        os.makedirs(os.path.join(clone, ".github", "workflows"))
        with open(os.path.join(clone, "party.yaml"), "w") as fh:
            fh.write("roles: [adopter]\n")
        with open(os.path.join(clone, ".github", "workflows", "fetch.yml"), "w") as fh:
            fh.write("on: {schedule: [{cron: '5 7 * * *'}]}\njobs: {a: {steps: []}}\n")
        git("-C", clone, "add", "party.yaml", ".github")
        git("-C", clone, "commit", "-q", "-m", "served")
        git("-C", clone, "push", "-q", "origin", DEFAULT_BRANCH)
        # the working tree moves on: a twin overlay and a second workflow, unpushed
        os.makedirs(os.path.join(clone, "twin"))
        with open(os.path.join(clone, "twin", "signals.yaml"), "w") as fh:
            fh.write("x: 1\n")
        with open(os.path.join(clone, ".github", "workflows", "twin-sweep.yml"), "w") as fh:
            fh.write("on: {schedule: [{cron: '5 8 * * *'}]}\njobs: {b: {steps: []}}\n")
        git("-C", clone, "add", "twin", ".github")
        git("-C", clone, "commit", "-q", "-m", "not served")
        tree, how = served(clone)
        assert tree is not None and how == "fetched now", how
        assert tree.sha == subprocess.run(["git", "-C", origin, "rev-parse", DEFAULT_BRANCH],
                                          capture_output=True, text=True).stdout.strip()
        assert not tree.isdir("twin") and tree.isdir(".github/workflows"), "read the working tree"
        assert sorted(workflows(tree)[0]) == ["fetch.yml"], workflows(tree)
        assert sorted(required_clocks("unit", tree)) == ["propose-tier.yml", "renovate-run.yml"]
        assert tree.show("twin/signals.yaml") is None and tree.show("party.yaml") == "roles: [adopter]\n"
        # origin gone: the last-fetched ref stands, and the how says the fetch failed
        shutil.rmtree(origin)
        tree, how = served(clone)
        assert tree is not None and how.startswith("fetch FAILED") and "as last fetched" in how, how
        # no origin/main at all: None, with why
        git("-C", clone, "update-ref", "-d", f"refs/remotes/origin/{DEFAULT_BRANCH}")
        tree, how = served(clone)
        assert tree is None and "no refs/remotes/origin/main" in how, how

    # a verdict file is bound to the run that wrote it: one from another run, or from another
    # repository, is refused and falls back to offline rather than being graded from (round 2).
    # It narrows the window on a forged file; it is not a trust boundary (see `binding_fault`).
    assert binding_fault({"run_id": "7", "repository": "org/hub"}, {}) == ""
    assert binding_fault({"run_id": "7", "repository": "org/hub"},
                         {"GITHUB_RUN_ID": "7", "GITHUB_REPOSITORY": "org/hub"}) == ""
    for planted, env, why in (
            ({"run_id": "9"}, {"GITHUB_RUN_ID": "7"}, "run 9"),
            ({}, {"GITHUB_RUN_ID": "7"}, "(none)"),
            ({"run_id": "7", "repository": "org/elsewhere"},
             {"GITHUB_RUN_ID": "7", "GITHUB_REPOSITORY": "org/hub"}, "org/elsewhere")):
        fault = binding_fault(planted, env)
        assert why in fault and "not this run's observation" in fault, (planted, fault)
    if os.environ.get("GITHUB_RUN_ID"):
        foreign = verdict_file(fresh, body, run_id="not-this-run")
        try:
            Verdict(foreign)
            raise AssertionError("a verdict file from another run must be refused")
        except ValueError as e:
            assert "not this run's observation" in str(e), e

    # the documented non-zero exit is ONE conclusion, not "anything but success". A cancelled
    # truth.yml run recorded nothing and graded PASS until 2026-09-04.
    assert RED_GATE_EXITS_NONZERO.get("truth.yml") == "failure"
    assert RED_GATE_EXITS_NONZERO.get("fetch.yml") is None

    # --- a run never grades itself, and a run in flight is a SKIP (round 2 of ticket 56) -------
    # The newest SCHEDULED run of truth.yml, read from a scheduled run of truth.yml, was this
    # run: conclusion "", status in_progress. Graded against `failure` that was a permanent FAIL
    # blaming ticket 85, unclearable by any estate fix.
    def planted_run(hours, conclusion, ident, status=None):
        when = (now - dt.timedelta(hours=hours)).isoformat(timespec="seconds")
        return {"createdAt": when.replace("+00:00", "Z"), "conclusion": conclusion,
                "status": status or ("completed" if conclusion else "in_progress"),
                "databaseId": ident}

    mine, yesterday = planted_run(0, "", 99), planted_run(24, "success", 98)
    assert newest_gradable([mine, yesterday], "99")["databaseId"] == 98
    assert newest_gradable([mine, yesterday], None)["databaseId"] == 98
    assert newest_gradable([mine], "99") is None
    assert newest_gradable([], None) is None
    status, msg = run_line("hub", "truth.yml", mine, now, " (ticket 85 owns it)")
    assert status == "SKIP" and "in_progress" in msg and "concluded nothing" in msg, msg
    assert "ticket 85" not in msg, msg
    assert run_line("hub", "truth.yml", planted_run(2, "failure", 97), now)[0] == "PASS"
    assert run_line("hub", "truth.yml", planted_run(2, "cancelled", 97), now)[0] == "FAIL"
    assert run_line("feeds", "fetch.yml", planted_run(2, "success", 97), now)[0] == "PASS"
    assert run_line("feeds", "fetch.yml",
                    planted_run(PERIOD_HOURS + 5, "success", 97), now)[0] == "FAIL"

    # --- a red clock names the open ticket that owns it (ticket 85) -----------
    owned = {"driftwood/twin-sweep.yml": {"ticket": 72, "owns": "the sweep dies under bash -e"},
             "feeds/fetch.yml": {"ticket": 85, "owns": "the cage reads its own .pyc"},
             "nowhere/none.yml": {"ticket": 999999, "owns": "no such ticket"}}
    assert "ticket 72 owns it" in owner_clause("driftwood", "twin-sweep.yml", owned)
    assert "unowned" in owner_clause("ludlow", "propose-tier.yml", {})
    assert "the map is stale" in owner_clause("nowhere", "none.yml", owned)
    faults = owners_faults(owned, {"driftwood/twin-sweep.yml", "feeds/fetch.yml"})
    assert any("no such ticket" in f for f in faults), faults
    assert any("not a clock this checker grades" in f for f in faults), faults
    assert owners_faults({"driftwood/twin-sweep.yml": owned["driftwood/twin-sweep.yml"]},
                         {"driftwood/twin-sweep.yml"}) == []
    # the map that ships must itself be clean of the first fault: every ticket it names exists
    for key, entry in owners().items():
        assert ticket_status(entry.get("ticket")) is not None, key

    # the allow-list itself
    assert _allowed("observations/twin-sweep.jsonl") and _allowed("talk/truth.log")
    assert not _allowed("composed/evidence.json") and not _allowed("party.yaml")
    assert not _allowed("twin/forward-intel/v1/feed.json")

    print("ok  the cage bites: a declaration staged beside a push to main fails, a push to "
          "main with no declared OBSERVATION_LANE or no cage step fails, a declaration pushed "
          "to any branch without opening a pull request fails, a proposer that pushes its own "
          "branch behind a PR passes, a scheduled job that can tag/release/merge fails in "
          "every shape (git tag, gh release, gh pr merge, a REST merge by gh api or curl in "
          "any method spelling, a release or ref minted by REST, a GraphQL mutation, git "
          "update-ref, a tag pushed by refspec) while each shape's read twin passes, the "
          "programs a job runs from its checkout are named in its PASS line instead of being "
          "called readable, every unit is read at origin/main as fetched and never from the "
          "working tree, who merged a commit GitHub committed is read from the verdict file or "
          "is a named could-not-look, an "
          "unscheduled cut-release is not judged at all, the server-side ruleset question "
          "answers with a named could-not-look rather than with silence, a clock verdict file "
          "lets the liveness half grade with no credential and every gap in it is a named "
          "could-not-look, a stale or wrong-schema one falls back to offline rather than to a "
          "token, a verdict file written by another run or in another repository is refused, a "
          "cancelled run of the one clock excused for exiting non-zero is still a red, a run "
          "still in flight -- this run included -- is a named could-not-look and never a red, "
          "and a red clock names the ticket that owns it")


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "selfcheck":
        selfcheck()
        return 0
    if len(argv) > 1 and argv[1] == "clocks":
        if "--out" not in argv:
            print("usage: schedules.py clocks --out FILE", file=sys.stderr)
            return 2
        return clocks(argv[argv.index("--out") + 1])
    offline = "--offline" in argv or os.environ.get("SCHEDULES_OFFLINE") == "1"
    return check(offline=offline)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
