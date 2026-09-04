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
file that is missing, malformed or stale is a could-not-look that says so by name -- never a
silent fall back to a credential the gate is not supposed to have.

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
from _estate import ESTATE  # noqa: E402

HUB = os.path.normpath(os.path.join(ESTATE, ".."))

# ADR-0024, D1. The complete list of paths a scheduled run may ever commit.
# Everything else is a declaration: a tier, a pin, a floor, an overlay, a
# priced evidence file, a published feed.
# `talk/captures`, not `captures`: talk/verify-all.sh writes captures to
# talk/captures/ and there is no top-level captures/ anywhere in the estate, so
# the old entry made the two halves of the cage disagree -- a workflow naming the
# REAL path would have been failed by this checker (review, 2026-08-28).
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
_SIGNED_ARTEFACT = re.compile(r"git\s+tag\b|gh\s+release\s+(?:create|upload)|"
                              r"gh\s+pr\s+merge\b|/git/refs/tags")

LINES: list[str] = []


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


# --- what each repository is --------------------------------------------------
def required_clocks(unit: str, root: str) -> dict[str, str]:
    """{workflow file: why} -- derived from the repository, not declared here."""
    need: dict[str, str] = {}
    party_path = os.path.join(root, "party.yaml")
    party = {}
    if os.path.exists(party_path):
        with open(party_path) as fh:
            party = yaml.safe_load(fh) or {}
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
    if os.path.isdir(os.path.join(root, "twin")):
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


def workflows(root: str) -> tuple[dict[str, dict], dict[str, str]]:
    """({filename: parsed workflow}, {filename: parse error}). A workflow GitHub
    cannot parse is a clock that does not exist, so the error is carried out and
    reported rather than swallowed or crashed on."""
    directory = os.path.join(root, ".github", "workflows")
    parsed: dict[str, dict] = {}
    broken: dict[str, str] = {}
    if not os.path.isdir(directory):
        return parsed, broken
    for name in sorted(os.listdir(directory)):
        if not name.endswith((".yml", ".yaml")):
            continue
        try:
            with open(os.path.join(directory, name)) as fh:
                doc = yaml.safe_load(fh)
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
        hit = _SIGNED_ARTEFACT.search(step.get("run") or "")
        if hit:
            faults.append(f"step {step.get('name') or '(unnamed)'!r} can run {hit.group(0)!r} "
                          f"-- a clock may not mint or merge a signed artefact")
    return faults


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


def last_run(remote: str, workflow: str) -> dict | None:
    raw = _gh("run", "list", "--repo", remote, "--workflow", workflow,
              "--event", "schedule", "--limit", "1",
              "--json", "createdAt,conclusion,status")
    runs = json.loads(raw or "[]")
    return runs[0] if runs else None


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


class Gh(Offline):
    """`gh`, in a process that holds a credential. Never the gate job (ticket 56)."""

    live = True

    def __init__(self) -> None:
        super().__init__("gh is authenticated")

    def ruleset_state(self, remote: str) -> tuple[str, str]:
        return ruleset_state(remote)

    def remote_crons(self, remote: str, workflow: str) -> tuple[str, list[str]]:
        return remote_crons(remote, workflow)

    def last_run(self, remote: str, workflow: str) -> dict | None:
        return last_run(remote, workflow)


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
        collected = dt.datetime.fromisoformat(doc["collected_at"])
        self.age_hours = (dt.datetime.now(collected.tzinfo) - collected).total_seconds() / 3600
        if self.age_hours > VERDICT_MAX_AGE_HOURS:
            raise ValueError(f"collected {self.age_hours:.0f}h ago, past the "
                             f"{VERDICT_MAX_AGE_HOURS}h freshness window")
        self.units = doc.get("units") or {}
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
def check(offline: bool = False) -> int:
    source = observer(offline)
    live = source.live
    unreachable = source.unreachable
    owned = owners()
    clocks_seen: set[str] = set()

    now = dt.datetime.now(dt.timezone.utc)
    for unit, root, remote in units():
        need = required_clocks(unit, root) if unit != "hub" else {
            "truth.yml": "the hub owns the daily truth surface (ticket 03)"}
        found, broken = workflows(root)
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
                    out("PASS", f"{unit}/{workflow} job {job_name}: caged -- no shell step in "
                                f"this job stages a declaration or mints a signed artefact, and "
                                f"nothing it runs is opaque to this checker")

        # 3b. live: the server-side half of the cage, observed on the remote.
        # Every unit gets a line here (eco-system ticket 83). This block used to emit nothing
        # when it could not look -- neither PASS nor FAIL nor SKIP -- and a question that emits
        # nothing is a fourth outcome the gate cannot count: eight server-side questions simply
        # vanished from the offline run. A could-not-look is a SKIP, said out loud, per unit.
        declared = os.path.isdir(os.path.join(root, ".github", "rulesets"))
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
                out("SKIP", f"{unit}/{workflow}: GitHub unreachable ({unreachable}) -- "
                            f"cannot look at whether this clock ran inside its period")
                continue
            try:
                state, _remote_schedule = source.remote_crons(remote, workflow)
                if state == "absent":
                    out("SKIP", f"{unit}/{workflow}: not on {remote}@{DEFAULT_BRANCH} yet -- "
                                f"it lives on the local ecosystem/thin-slice branch until the "
                                f"owner merges, so no scheduled run can have happened")
                    continue
                if state == "unparsed":
                    out("FAIL", f"{unit}/{workflow}: the copy on {remote}@{DEFAULT_BRANCH} "
                                f"does not parse, so GitHub runs no clock from it at all" + owns)
                    continue
                if state == "untimed":
                    # Two very different worlds, and the old code called both SKIP
                    # with a reason that becomes false after the merge. The LOCAL
                    # copy decides which one this is.
                    if crons(found.get(workflow) or {}):
                        out("SKIP", f"{unit}/{workflow}: the copy on {remote}@{DEFAULT_BRANCH} "
                                    f"carries no `schedule:` while the local "
                                    f"ecosystem/thin-slice copy does -- GitHub runs the default "
                                    f"branch's copy and nothing else, so this clock starts when "
                                    f"the owner merges")
                    else:
                        out("FAIL", f"{unit}/{workflow}: neither {remote}@{DEFAULT_BRANCH} nor "
                                    f"the local copy carries a `schedule:` -- the clock was "
                                    f"removed from the branch GitHub actually runs" + owns)
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
            age = (now - dt.datetime.fromisoformat(
                run["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600
            if age > PERIOD_HOURS:
                out("FAIL", f"{unit}/{workflow}: last scheduled run was {age:.0f}h ago, past "
                            f"the {PERIOD_HOURS}h window (a daily period plus a day of slack "
                            f"for GitHub's own scheduling delay) -- the clock has stopped" + owns)
                continue
            # The run's OUTCOME, not only its age. A run that dies in checkout,
            # in the gitsign install or in the cage step records nothing and used
            # to read as a healthy clock (live, 2026-08-28: "hub/truth.yml: last
            # scheduled run 2h ago (failure)" graded PASS). truth.yml is the one
            # documented exception: it ends `exit 1` whenever the gate is red,
            # which is its normal state, and its observation lands before that.
            # ponytail: the exception is by workflow name; the stronger check is
            # to read the newest line of the lane itself (talk/truth.log,
            # observations/<feed>.jsonl) off the remote and date it -- do that
            # when a second clock needs an exception.
            conclusion = run.get("conclusion") or run.get("status")
            excused = RED_GATE_EXITS_NONZERO.get(workflow)
            if conclusion == "success":
                out("PASS", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago (success)")
            elif conclusion == excused:
                out("PASS", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago "
                            f"({conclusion}), which is this clock's documented exit -- it records "
                            f"its observation and then re-raises the gate's own red verdict")
            else:
                out("FAIL", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago concluded "
                            f"{conclusion!r} -- a clock whose run dies, is cancelled or is still "
                            f"unfinished records no observation" + owns)

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
    doc = {
        "schema": VERDICT_SCHEMA,
        "collected_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "collector": "verify/schedules/schedules.py clocks",
        "units": {},
    }
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
        need = required_clocks(unit, root) if unit != "hub" else {"truth.yml": ""}
        found, _broken = workflows(root)
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

    # a clock that can cut a tag or a release, or merge a PR
    for line in ("git tag -s v1.0.0", "gh release create v1.0.0", "gh pr merge 4 --merge"):
        minting = wf(f"""
on:
  schedule: [{{cron: "5 7 * * *"}}]
jobs:
  cut:
    steps:
      - run: {line}
""")
        assert signed_artefact_faults(minting["jobs"]["cut"]), line

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

    def verdict_file(collected_at, units_doc, schema=VERDICT_SCHEMA):
        fh = tempfile.NamedTemporaryFile("w", suffix=".json", delete=False)
        json.dump({"schema": schema, "collected_at": collected_at,
                   "collector": "selfcheck", "units": units_doc}, fh)
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

    # the documented non-zero exit is ONE conclusion, not "anything but success". A cancelled
    # truth.yml run recorded nothing and graded PASS until 2026-09-04.
    assert RED_GATE_EXITS_NONZERO.get("truth.yml") == "failure"
    assert RED_GATE_EXITS_NONZERO.get("fetch.yml") is None

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
          "branch behind a PR passes, a scheduled job that can tag/release/merge fails, an "
          "unscheduled cut-release is not judged at all, the server-side ruleset question "
          "answers with a named could-not-look rather than with silence, a clock verdict file "
          "lets the liveness half grade with no credential and every gap in it is a named "
          "could-not-look, a stale or wrong-schema one falls back to offline rather than to a "
          "token, a cancelled run of the one clock excused for exiting non-zero is still a red, "
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
