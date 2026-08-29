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

Exit precedence: any FAIL -> 1; else any SKIP -> 3; else 0. Offline, questions
1 to 3 still run in full -- absence of a network is never a pass and never a
reason to skip the static half.

Usage:
    schedules.py check      [--offline]
    schedules.py selfcheck
"""
from __future__ import annotations

import base64
import datetime as dt
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

# The clocks documented to exit non-zero on purpose. truth.yml re-raises the
# gate's own verdict (truth.yml's "fail if the gate failed" step), so a red gate
# is a failed run AND a recorded observation.
RED_GATE_EXITS_NONZERO = {"truth.yml"}

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
        if os.path.isdir(os.path.join(root, ".git")):
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
    has_cage = any("observation cage" in str(s.get("name") or "")
                   for s in (job.get("steps") or []))
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
    names = [str(s.get("name") or "") for s in (job.get("steps") or [])]
    if not any("observation cage" in n for n in names):
        faults.append("pushes the default branch with no `observation cage` step to fail the "
                      "run when the tree carries a declaration")
    return faults


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


# --- the check ----------------------------------------------------------------
def check(offline: bool = False) -> int:
    live = not offline
    unreachable = "--offline was asked for"
    if live:
        try:
            _gh("auth", "status")
        except (subprocess.SubprocessError, OSError) as e:
            live = False
            unreachable = str(e).splitlines()[0]

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
            # D2 is "open a PR only when the computed bump is not none". A fetch
            # clock with no `gh pr create` anywhere cannot do that: it observes what
            # its own repository already publishes and compares it against nothing.
            # Four of the five publisher clocks are that shape today and their own
            # headers say so, but this check graded them PASS on the presence of a
            # `schedule:` alone, which overstated them (review, 2026-08-28).
            if workflow == "fetch.yml" and not any(
                    "gh pr create" in (s.get("run") or "")
                    for j in (doc.get("jobs") or {}).values()
                    for s in (j.get("steps") or [])):
                out("SKIP", f"{unit}/{workflow}: daily clock at {', '.join(crons(doc))}, but it "
                            f"opens no pull request anywhere -- it observes what {unit} already "
                            f"publishes rather than reading upstream and computing a bump, so "
                            f"story 9 / D2 is not implemented here ({why})")
                continue
            out("PASS", f"{unit}/{workflow}: daily clock at {', '.join(crons(doc))} -- {why}")

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
        if live and os.path.isdir(os.path.join(root, ".github", "rulesets")):
            verdict, reason = ruleset_state(remote)
            if verdict == "in-force":
                out("PASS", f"{unit}: the observation-lane ruleset is applied on {remote} -- "
                            f"the cage has its server-side half")
            elif verdict == "unavailable":
                out("SKIP", f"{unit}: no observation-lane ruleset on {remote}: {reason}. The "
                            f"client-side cage step and this checker are the whole cage today "
                            f"(ADR-0024 point 3, amended 2026-08-28)")
            elif verdict == "missing":
                out("FAIL", f"{unit}: {reason}, and it could be applied -- ADR-0024 point 3 "
                            f"claims a server-side leg this repository does not have")
            else:
                out("SKIP", f"{unit}: could not read the rulesets on {remote} ({reason})")

        # 4. live: did each clock run inside its period?
        for workflow in sorted(need):
            if workflow not in found:
                continue
            if not live:
                # Named per unit, on purpose: "GitHub is unreachable" is a
                # could-not-look about THIS clock, not a blanket excuse.
                out("SKIP", f"{unit}/{workflow}: GitHub unreachable ({unreachable}) -- "
                            f"cannot look at whether this clock ran inside its period")
                continue
            try:
                state, _remote_schedule = remote_crons(remote, workflow)
                if state == "absent":
                    out("SKIP", f"{unit}/{workflow}: not on {remote}@{DEFAULT_BRANCH} yet -- "
                                f"it lives on the local ecosystem/thin-slice branch until the "
                                f"owner merges, so no scheduled run can have happened")
                    continue
                if state == "unparsed":
                    out("FAIL", f"{unit}/{workflow}: the copy on {remote}@{DEFAULT_BRANCH} "
                                f"does not parse, so GitHub runs no clock from it at all")
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
                                    f"removed from the branch GitHub actually runs")
                    continue
                run = last_run(remote, workflow)
            except (subprocess.SubprocessError, OSError) as e:
                out("SKIP", f"{unit}/{workflow}: GitHub unreachable for {remote} "
                            f"({str(e).splitlines()[0]})")
                continue
            if run is None:
                out("FAIL", f"{unit}/{workflow}: on {remote}@{DEFAULT_BRANCH} with a "
                            f"`schedule:` but GitHub has never run it on that schedule")
                continue
            age = (now - dt.datetime.fromisoformat(
                run["createdAt"].replace("Z", "+00:00"))).total_seconds() / 3600
            if age > PERIOD_HOURS:
                out("FAIL", f"{unit}/{workflow}: last scheduled run was {age:.0f}h ago, past "
                            f"the {PERIOD_HOURS}h window (a daily period plus a day of slack "
                            f"for GitHub's own scheduling delay) -- the clock has stopped")
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
            if conclusion != "success" and workflow not in RED_GATE_EXITS_NONZERO:
                out("FAIL", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago concluded "
                            f"{conclusion!r} -- a clock whose run dies records no observation")
            else:
                out("PASS", f"{unit}/{workflow}: last scheduled run {age:.0f}h ago "
                            f"({conclusion})")

    if "FAIL" in LINES:
        return 1
    if "SKIP" in LINES:
        return 3
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
          for p in ${OBSERVATION_LANE}; do git add -A -- "$p"; done
          git commit -S -m x
          git push origin "HEAD:${GITHUB_REF_NAME}"
""")
    assert cage_faults(caged, caged["jobs"]["sweep"]) == [], \
        cage_faults(caged, caged["jobs"]["sweep"])
    assert signed_artefact_faults(caged["jobs"]["sweep"]) == []

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

    # the allow-list itself
    assert _allowed("observations/twin-sweep.jsonl") and _allowed("talk/truth.log")
    assert not _allowed("composed/evidence.json") and not _allowed("party.yaml")
    assert not _allowed("twin/forward-intel/v1/feed.json")

    print("ok  the cage bites: a declaration staged beside a push to main fails, a push to "
          "main with no declared OBSERVATION_LANE or no cage step fails, a declaration pushed "
          "to any branch without opening a pull request fails, a proposer that pushes its own "
          "branch behind a PR passes, a scheduled job that can tag/release/merge fails, and an "
          "unscheduled cut-release is not judged at all")


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "selfcheck":
        selfcheck()
        return 0
    offline = "--offline" in argv or os.environ.get("SCHEDULES_OFFLINE") == "1"
    return check(offline=offline)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
