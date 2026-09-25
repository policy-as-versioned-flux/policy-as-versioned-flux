#!/usr/bin/env python3
"""lane.py -- the observation lane graded on what LANDED (ticket 70, ADR-0023 amended 2026-09-03).

schedules.py reads each scheduled workflow's YAML and grades the cage step it carries: a promise
about what the next run may stage. This file reads history: for every unit in .estate-clone/ and
for the hub, it walks the first-parent log of each observation ref -- `origin/main`, and the
orphan `origin/observations` where a publisher clock has created it -- and grades every commit a
scheduled identity has landed there.

    a scheduled-identity commit    the COMMITTER email is one the unit's own scheduled workflows
                                   configure (`git config user.email ...` / `-c user.email=...`
                                   inside a job under `on: schedule:`), or GitHub's own
                                   github-actions[bot]. Committer, not author: a clock that pushes
                                   a ref writes the commit object itself, so both names are the
                                   clock's; a clock-authored commit that reached the ref through a
                                   human's merge, squash or rebase carries the human's or GitHub's
                                   committer and is a reviewed proposal, not a lane write.
    the lane                       the union of the OBSERVATION_LANE declarations in the unit's
                                   scheduled jobs (local checkout and the graded ref's own copy),
                                   restricted to ADR-0024 point 3's list; that list alone when a
                                   unit declares none.
    a violation                    a scheduled-identity commit that touches any path outside the
                                   lane, or that is a merge. A clock appends; it never merges.
    a merge GitHub committed       (eco-system ticket 142, from ticket 30's facts of 2026-09-25)
                                   a merge made through the REST API or the web is committed by
                                   `GitHub <noreply@github.com>`, so the committer never names a
                                   scheduled identity and the rule above graded such a merge as
                                   a reviewed proposal. Who merged is read another way:
                                   - a MERGE commit GitHub wrote carries the merging account as
                                     its AUTHOR (observed: every pavc-other-hand merge on every
                                     unit is authored `pavc-other-hand[bot]`, committed GitHub).
                                     A scheduled or automation author is a FAIL, offline, from
                                     the commit alone. `app/pavc-other-hand` is the reviewed
                                     second hand (ticket 88, owner-instructed) and is a NOTE.
                                   - a SQUASH or REBASE GitHub wrote keeps the proposal's author,
                                     so who merged is not in the commit at all. For one authored
                                     by a scheduled identity the merged pull requests are asked
                                     (`mergedBy`: the clock verdict file the collector wrote, or
                                     an authenticated `gh`); a bot merger is a FAIL, a person a
                                     NOTE, and no source is a named could-not-look, never clean.
    out of scope                   a human's commit, whatever it touches; a bot-authored commit a
                                   human merged; automation identities no scheduled workflow
                                   configures (platform's release bot writes evidence to main from
                                   cut-release.yml, a workflow_dispatch -- a human act, ADR-0023).
                                   Those are counted and named in a NOTE line, never graded.

Why this exists: the server-side ruleset ADR-0023 and ADR-0024 promised cannot be applied --
GitHub allows a push ruleset (the only kind carrying file_path_restriction) on private and
internal repositories only, and every repository here is public (ticket 58 Q4(b)). So prevention
is the workflow's cage step, and detection is this file: a declaration that slips past the step is
a FAIL on the next citable run, with the commit named.

Not graded here: the gitsign signature on each landed commit. `%G?` reads N or U for every one
of them because gitsign is not in git's verify chain; the Rekor-backed identity check belongs to
ticket 73's verifier. Absence of a signature check is named, not hidden.

Exit precedence: any FAIL -> 1; else any SKIP -> 3; else 0. Offline in full: it reads the refs the
clone already holds after a best-effort fetch of each observation ref origin actually has, and
its INFO line says per ref whether that fetch happened, was not needed, or failed.

Usage:
    lane.py check
    lane.py selfcheck
"""
from __future__ import annotations

import ast
import dataclasses
import os
import re
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import schedules as S  # noqa: E402  -- one allow-list, one workflow parser, one unit walk

OBSERVATIONS_BRANCH = "observations"
REFS = (S.DEFAULT_BRANCH, OBSERVATIONS_BRANCH)

# GitHub's own Actions identity. Renovate commits as it; so does any action that leaves the
# default committer in place. Never configured in a workflow, so it cannot be parsed out of one.
ALWAYS_SCHEDULED = frozenset({"41898282+github-actions[bot]@users.noreply.github.com"})

# The committer GitHub itself writes on a merge, squash or rebase made through the API or the
# web (ticket 142). It says a person or a token merged through GitHub; it never says which.
WEB_FLOW = "noreply@github.com"
# The reviewed second hand (ticket 88; ticket 75 Q6 and Q14, owner-instructed): merges as the App
# `pavc-other-hand`. Its author email on a merge commit, and its login in a pull request's
# `mergedBy`, as GitHub spells each.
OTHER_HAND_EMAIL = re.compile(r"\+pavc-other-hand\[bot\]@users\.noreply\.github\.com$")
OTHER_HAND_LOGINS = frozenset({"app/pavc-other-hand", "pavc-other-hand[bot]"})

# `git config user.email X`, `git -C dir config user.email X`, `-c user.email=X`, quoted or not.
_USER_EMAIL = re.compile(r"""user\.email\s*(?:=|\s)\s*["']?([^"'\s]+)""")
_OWNER_VAR = re.compile(r"\$\{?GITHUB_REPOSITORY_OWNER\}?|\$\{\{\s*github\.repository_owner\s*\}\}")
_FETCH_TIMEOUT = 20

LINES: list[str] = []


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


@dataclasses.dataclass(frozen=True)
class Commit:
    sha: str
    author: str
    committer: str
    committer_name: str
    parents: int
    subject: str


def _git(root: str, *args: str, timeout: int = 60) -> str:
    done = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                          check=True, timeout=timeout)
    return done.stdout


def _owner(unit: str) -> str:
    return "policy-as-versioned-flux" if unit == "hub" else f"policy-as-versioned-{unit}"


# --- what the workflows declare ------------------------------------------------
def workflows_on_ref(root: str, ref: str) -> dict[str, dict]:
    """The workflow files as they are on the graded ref, so a clock whose local copy has moved
    on is still judged by the identity and lane the ref's own copy configured."""
    found: dict[str, dict] = {}
    try:
        names = _git(root, "ls-tree", "--name-only", ref, "--", ".github/workflows/").split()
    except (subprocess.SubprocessError, OSError):
        return found
    for path in names:
        if not path.endswith((".yml", ".yaml")):
            continue
        try:
            doc = yaml.safe_load(_git(root, "show", f"{ref}:{path}"))
        except (subprocess.SubprocessError, OSError, yaml.YAMLError):
            continue
        if isinstance(doc, dict):
            found[os.path.basename(path)] = doc
    return found


def _working_tree_workflows(root: str) -> dict[str, dict]:
    """The workflow files as the checkout's working tree holds them: the second copy the union
    below grades. A file that does not parse is skipped here; schedules.py fails it."""
    found: dict[str, dict] = {}
    directory = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(directory):
        return found
    for name in sorted(os.listdir(directory)):
        if not name.endswith((".yml", ".yaml")):
            continue
        try:
            with open(os.path.join(directory, name)) as fh:
                doc = yaml.safe_load(fh)
        except (OSError, yaml.YAMLError):
            continue
        if isinstance(doc, dict):
            found[name] = doc
    return found


def scheduled_identities(unit: str, *docsets: dict[str, dict]) -> set[str]:
    """Every user.email a scheduled job configures, with the owner variable resolved. Several
    document sets (the checkout's workflows and the graded ref's own copy) are read as one
    union: a filename present in both is graded on BOTH copies, never on one of them."""
    emails: set[str] = set(ALWAYS_SCHEDULED)
    for docs in docsets:
        for doc in docs.values():
            for _name, job in S.scheduled_jobs(doc):
                for step in job.get("steps") or []:
                    for email in _USER_EMAIL.findall(str(step.get("run") or "")):
                        emails.add(_OWNER_VAR.sub(_owner(unit), email))
    return emails


def declared_lane(*docsets: dict[str, dict]) -> tuple[str, ...]:
    """The union of OBSERVATION_LANE across scheduled jobs in every document set given, kept
    inside ADR-0024's list (a path declared outside it is schedules.py's FAIL, not this file's
    allowance). The ADR list when nothing is declared anywhere."""
    lane: list[str] = []
    for docs in docsets:
        for doc in docs.values():
            for _name, job in S.scheduled_jobs(doc):
                for path in str(S._env(doc, job).get("OBSERVATION_LANE") or "").split():
                    path = S._bare(path)
                    if S._allowed(path) and path not in lane:
                        lane.append(path)
    return tuple(lane) if lane else tuple(S.ALLOW_LIST)


def in_lane(path: str, lane: tuple[str, ...]) -> bool:
    return any(path == a or path.startswith(a + "/") for a in lane)


# --- what landed -------------------------------------------------------------------
def commits(root: str, ref: str) -> list[Commit]:
    """First-parent walk, newest first. A commit on a second parent reached the ref inside a
    merge somebody made; the merge commit is the thing on the ref."""
    fmt = "%H%x00%ae%x00%ce%x00%cn%x00%P%x00%s"
    # `--`: the branch is called `observations` and so is the directory it holds.
    raw = _git(root, "log", "--first-parent", f"--format={fmt}", ref, "--")
    found = []
    for line in raw.splitlines():
        if not line:
            continue
        sha, author, committer, cname, parents, subject = line.split("\x00", 5)
        found.append(Commit(sha, author, committer, cname, len(parents.split()), subject))
    return found


def touched(root: str, sha: str) -> list[str]:
    """Paths the commit changed against its first parent; `--root` so an orphan branch's first
    commit is graded on everything it introduced rather than crashing on having no parent."""
    raw = _git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "--root", "-m",
               "--first-parent", sha)
    return [p for p in raw.splitlines() if p]


def _automation(email: str) -> bool:
    return email.endswith(".invalid") or "[bot]" in email


def _bot_login(login: str) -> bool:
    return login.startswith("app/") or login.endswith("[bot]")


def _no_source(sha: str) -> dict:
    raise S.CouldNotLook("no source for who merged was given")


def grade_ref(root: str, label: str, ref: str, identities: set[str],
              lane: tuple[str, ...], merger=None) -> list[tuple[str, str]]:
    """(status, message) lines for one ref. Pure over the repository at `root`, plus `merger`:
    a callable that answers who merged the pull request whose merge commit is a given sha (the
    shape schedules.py's `merged_by` returns) or raises `S.CouldNotLook`. It is asked only for
    a squash or rebase GitHub wrote of a scheduled identity's commit; none given is a
    could-not-look for those, never a pass."""
    merger = merger or _no_source
    lines: list[tuple[str, str]] = []
    try:
        history = commits(root, ref)
    except (subprocess.SubprocessError, OSError) as e:
        return [("SKIP", f"{label}: could not read {ref} ({str(e).splitlines()[0]})")]
    graded = 0
    human_merged = 0
    other_hand = 0
    merged_by_people: dict[str, int] = {}
    other_bots: dict[str, int] = {}
    for c in history:
        if c.committer == WEB_FLOW and c.committer not in identities:
            # GitHub committed it: a merge, squash or rebase made through the API or the web.
            if c.parents > 1:
                # the merging account is the merge commit's author
                if c.author in identities or (_automation(c.author)
                                              and not OTHER_HAND_EMAIL.search(c.author)):
                    lines.append(("FAIL", f"{label}: {c.sha[:9]} is a MERGE onto {ref} made "
                                          f"through GitHub by {c.author} ({c.subject!r}) -- a "
                                          f"merge made with a scheduled or automation "
                                          f"identity's token is disposal with nobody at the "
                                          f"keyboard; a clock appends, it never merges"))
                elif OTHER_HAND_EMAIL.search(c.author):
                    other_hand += 1
                continue                       # a person's merge: out of scope
            if c.author not in identities:
                continue                       # a person's own squash or rebase: out of scope
            # a squash or rebase of a clock's proposal: the commit does not say who merged
            try:
                who = merger(c.sha)
            except S.CouldNotLook as e:
                lines.append(("SKIP", f"{label}: {c.sha[:9]} authored by scheduled identity "
                                      f"{c.author} ({c.subject!r}) was squashed or rebased onto "
                                      f"{ref} by GitHub, which does not record who merged, and "
                                      f"the merged pull requests could not be read ({e}) -- a "
                                      f"merge by a scheduled token would look exactly like "
                                      f"this, so it is not graded either way"))
                continue
            login = str(who.get("merged_by") or "")
            if login in OTHER_HAND_LOGINS:
                other_hand += 1
            elif who.get("is_bot") or _bot_login(login):
                lines.append(("FAIL", f"{label}: {c.sha[:9]} authored by scheduled identity "
                                      f"{c.author} ({c.subject!r}) reached {ref} through pull "
                                      f"request #{who.get('pr')} merged by {login or '(unnamed)'}"
                                      f" at {who.get('merged_at') or '?'} -- a merge made with "
                                      f"a scheduled or automation identity's token is disposal "
                                      f"with nobody at the keyboard; a clock appends, it never "
                                      f"merges"))
            else:
                merged_by_people[login or "(unnamed)"] = merged_by_people.get(login or "(unnamed)", 0) + 1
            continue
        if c.committer not in identities:
            if c.author in identities:
                human_merged += 1
            elif _automation(c.committer):
                other_bots[c.committer] = other_bots.get(c.committer, 0) + 1
            continue
        graded += 1
        if c.parents > 1:
            lines.append(("FAIL", f"{label}: {c.sha[:9]} is a MERGE committed by scheduled "
                                  f"identity {c.committer} ({c.subject!r}) -- a clock appends, "
                                  f"it never merges"))
            continue
        try:
            paths = touched(root, c.sha)
        except (subprocess.SubprocessError, OSError) as e:
            lines.append(("SKIP", f"{label}: could not read what {c.sha[:9]} touched "
                                  f"({str(e).splitlines()[0]})"))
            continue
        outside = [p for p in paths if not in_lane(p, lane)]
        if outside:
            lines.append(("FAIL", f"{label}: {c.sha[:9]} by scheduled identity {c.committer} "
                                  f"({c.subject!r}) landed {outside} -- outside the observation "
                                  f"lane {list(lane)}; a clock appends observations, never a "
                                  f"declaration"))
    if not any(s == "FAIL" for s, _ in lines):
        if graded:
            lines.append(("PASS", f"{label}: {graded} commit(s) by a scheduled identity on the "
                                  f"first-parent history, every one inside the lane "
                                  f"{list(lane)} and none a merge"))
        else:
            lines.append(("PASS", f"{label}: no scheduled identity has landed a commit here -- "
                                  f"the lane holds vacuously; whether the clock runs at all is "
                                  f"verify-schedules' question, not this one's"))
    if human_merged:
        lines.append(("NOTE", f"{label}: {human_merged} commit(s) authored by a scheduled "
                              f"identity reached the ref through a human's own merge, squash or "
                              f"rebase (the person is the committer) -- a reviewed proposal, "
                              f"not graded"))
    for login, n in sorted(merged_by_people.items()):
        lines.append(("NOTE", f"{label}: {n} commit(s) authored by a scheduled identity were "
                              f"squashed or rebased onto the ref by GitHub for a pull request "
                              f"merged by {login} -- a reviewed proposal, not graded"))
    if other_hand:
        lines.append(("NOTE", f"{label}: {other_hand} merge(s) made through GitHub by "
                              f"pavc-other-hand, the reviewed second hand (ticket 88, "
                              f"owner-instructed) -- a human's act by the owner's instruction, "
                              f"not graded"))
    for email, n in sorted(other_bots.items()):
        lines.append(("NOTE", f"{label}: {n} commit(s) committed by automation identity {email}, "
                              f"which no scheduled workflow configures -- outside this lane "
                              f"(a dispatched workflow is a human act, ADR-0023) and not graded"))
    return lines


def pushes_observations(docs: dict[str, dict]) -> bool:
    return any(f"push origin {OBSERVATIONS_BRANCH}" in str(s.get("run") or "")
               for doc in docs.values() for _n, job in S.scheduled_jobs(doc)
               for s in (job.get("steps") or []))


def _has_ref(root: str, ref: str) -> bool:
    return subprocess.run(["git", "-C", root, "rev-parse", "--verify", "-q", ref],
                          capture_output=True, text=True, check=False).returncode == 0


def is_shallow(root: str) -> bool:
    return subprocess.run(["git", "-C", root, "rev-parse", "--is-shallow-repository"],
                          capture_output=True, text=True, check=False).stdout.strip() == "true"


def _first(text: str, fallback: str) -> str:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    return lines[0] if lines else fallback


def remote_heads(root: str) -> tuple[bool, set[str], str]:
    """(origin reachable, which of REFS exist on it, error). One `ls-remote` asked for the
    observation refs by name: it is the fact of which refs origin has, so an absent
    `observations` branch is never mistaken for an unreachable origin or the other way round."""
    try:
        done = subprocess.run(["git", "-C", root, "ls-remote", "--heads", "origin",
                               *[f"refs/heads/{r}" for r in REFS]],
                              capture_output=True, text=True, check=False, timeout=_FETCH_TIMEOUT)
    except (subprocess.SubprocessError, OSError) as e:
        return False, set(), _first(str(e), "ls-remote failed")
    if done.returncode != 0:
        return False, set(), _first(done.stderr, f"ls-remote exit {done.returncode}")
    heads = {line.split("\t", 1)[1].removeprefix("refs/heads/")
             for line in done.stdout.splitlines() if "\t" in line}
    return True, heads, ""


def refresh(root: str, network: bool) -> tuple[bool, str, bool]:
    """(network still usable, what was graded, still shallow).

    Best-effort, and honest about the result: `how` names each ref that was fetched, each that
    origin does not have, and any fetch that failed. A failed fetch or an unreachable origin
    turns `network` off for the rest of the run, so the unshallow step is not attempted and
    the SKIP text does not claim a fetch that never happened.

    The observation refs first, each on its own (a single two-refspec fetch fails as a whole
    when one ref is absent, and `observations` is absent on every adopter and on the hub), so a
    kept clone grades today's tip rather than the day it was cloned. Then `--unshallow` where
    the checkout is shallow: actions/checkout's default depth is 1, so on the citable run the
    hub's own `main` would otherwise be one commit deep and the lane graded on nothing while
    reading as PASS. A history that stays shallow is a could-not-look, never a pass."""
    parts: list[str] = []
    if not network:
        parts.append("as cloned (no fetch attempted: origin was unreachable earlier in this run)")
    else:
        reachable, heads, err = remote_heads(root)
        if not reachable:
            network = False
            parts.append(f"as cloned; origin unreachable ({err})")
        for ref in REFS if reachable else ():
            if ref not in heads:
                parts.append(f"{ref} absent on origin")
                continue
            try:
                done = subprocess.run(
                    ["git", "-C", root, "fetch", "--quiet", "origin",
                     f"+refs/heads/{ref}:refs/remotes/origin/{ref}"],
                    capture_output=True, text=True, check=False, timeout=_FETCH_TIMEOUT)
                failed = "" if done.returncode == 0 else \
                    _first(done.stderr, f"fetch exit {done.returncode}")
            except (subprocess.SubprocessError, OSError) as e:
                failed = _first(str(e), "fetch failed")
            if failed:
                network = False
                parts.append(f"{ref} as cloned, fetch FAILED ({failed})")
            else:
                parts.append(f"{ref} fetched now")
    was_shallow = is_shallow(root)
    if was_shallow and network:
        try:
            done = subprocess.run(["git", "-C", root, "fetch", "--quiet", "--unshallow", "origin"],
                                  capture_output=True, text=True, check=False,
                                  timeout=3 * _FETCH_TIMEOUT)
            if done.returncode != 0:
                parts.append(f"unshallow FAILED ({_first(done.stderr, f'exit {done.returncode}')})")
        except (subprocess.SubprocessError, OSError) as e:
            parts.append(f"unshallow FAILED ({_first(str(e), 'fetch failed')})")
    shallow = is_shallow(root)
    if was_shallow and not shallow:
        parts.append("shallow checkout deepened to full history")
    elif was_shallow and not network:
        parts.append("shallow checkout left shallow: no fetch could be made")
    return network, "; ".join(parts), shallow


# --- the platform composer's copy of the list (eco-system ticket 134) ------------------------
# The platform's compose/comparison_history.py leaves the declared lane out of the comparison
# identity, so it reads OBSERVATION_LANE exactly as declared_lane() does: scheduled jobs only,
# top-level and job env, inside ADR-0024's list. It runs in each adopter's CI with no hub
# checkout, so it carries its own copy of S.ALLOW_LIST. This grade is what keeps the two from
# drifting: the copy on platform main must equal the list here, or the lane check fails.
PLATFORM_UNIT = "platform"
PLATFORM_COPY = "compose/comparison_history.py"
PLATFORM_CONSTANT = "OBSERVATION_PATHS"


def platform_copy(text: str | None) -> tuple[str, str]:
    """Grade the platform composer's copy of ADR-0024's list against S.ALLOW_LIST."""
    where = f"{PLATFORM_UNIT}@{S.DEFAULT_BRANCH}: {PLATFORM_COPY}"
    if text is None:
        return ("FAIL", f"{where} is missing, so nothing states which lane the comparison "
                        f"identity leaves out")
    try:
        tree = ast.parse(text)
    except SyntaxError as error:
        return ("FAIL", f"{where} does not parse ({error})")
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == PLATFORM_CONSTANT for t in node.targets):
            try:
                value = ast.literal_eval(node.value)
            except ValueError:
                return ("FAIL", f"{where} {PLATFORM_CONSTANT} is not a literal list")
            if isinstance(value, (list, tuple)) and tuple(value) == tuple(S.ALLOW_LIST):
                return ("PASS", f"{where} {PLATFORM_CONSTANT} equals ADR-0024's list here")
            return ("FAIL", f"{where} {PLATFORM_CONSTANT} is {value!r}, and ADR-0024's list "
                            f"here is {tuple(S.ALLOW_LIST)!r}: the copies have drifted")
    return ("FAIL", f"{where} carries no {PLATFORM_CONSTANT}, so its comparison identity is "
                    f"not held to ADR-0024's list")


def check_platform_copy() -> None:
    for unit, root, _remote in S.units():
        if unit != PLATFORM_UNIT:
            continue
        try:
            text: str | None = _git(root, "show", f"origin/{S.DEFAULT_BRANCH}:{PLATFORM_COPY}")
        except (subprocess.SubprocessError, OSError):
            text = None
        out(*platform_copy(text))
        return
    out("SKIP", f"no {PLATFORM_UNIT} checkout, so its copy of ADR-0024's list was not compared")


# --- who merged: the source is opened only when a commit needs it (ticket 142) ----------------
class _Merger:
    """Who merged, for one unit, from schedules.py's observer: the clock verdict file when
    CLOCK_VERDICT names one, else an authenticated `gh`, else a could-not-look. Opened lazily so
    a run whose refs carry no squash or rebase of a clock's commit asks nothing of anyone."""

    source: S.Offline | None = None

    def __init__(self, remote: str) -> None:
        self.remote = remote

    def __call__(self, sha: str) -> dict:
        if _Merger.source is None:
            _Merger.source = S.observer()
        return _Merger.source.merged_by(self.remote, sha)


# --- the check ------------------------------------------------------------------------
def check() -> int:
    network = True
    for unit, root, remote in S.units():
        network, refreshed, shallow = refresh(root, network)
        if shallow:
            visible = _git(root, "rev-list", "--count", "HEAD").strip()
            out("SKIP", f"{unit}: the checkout is shallow and could not be deepened ({refreshed}) "
                        f"-- a first-parent walk of {visible} visible commit(s) is not the lane's "
                        f"history, so nothing here is graded")
            continue
        main_ref = f"origin/{S.DEFAULT_BRANCH}"
        on_ref = workflows_on_ref(root, main_ref)
        # the checkout's own copy, read from its working tree by this file's reader (schedules.py
        # reads only the served ref since ticket 142; the union here is deliberate, see above)
        local = _working_tree_workflows(root)
        # The union of the two copies, not a merge by filename: a clock whose checkout copy has
        # moved on is still graded by the identity and lane the ref's own copy configured.
        identities = scheduled_identities(unit, on_ref, local)
        lane = declared_lane(on_ref, local)
        print(f"INFO: {unit}: scheduled identities {sorted(identities - ALWAYS_SCHEDULED)}, "
              f"lane {list(lane)}, refs {refreshed}")
        for ref in REFS:
            full = f"origin/{ref}"
            if not _has_ref(root, full):
                if ref == OBSERVATIONS_BRANCH and not (pushes_observations(on_ref)
                                                       or pushes_observations(local)):
                    continue                       # this unit has no observation series
                out("SKIP", f"{unit}@{ref}: the ref does not exist on {remote} yet -- the clock "
                            f"that creates it has not landed a commit, so there is nothing to "
                            f"grade and nothing to clear")
                continue
            for status, msg in grade_ref(root, f"{unit}@{ref}", full, identities, lane,
                                         _Merger(remote)):
                if status == "NOTE":
                    print(f"NOTE: {msg}")
                else:
                    out(status, msg)
    check_platform_copy()
    if "FAIL" in LINES:
        return 1
    if "SKIP" in LINES:
        return 3
    return 0


# --- selfcheck: planted repositories, each refusal must bite -------------------------
def selfcheck() -> None:
    bot = "fetch-bot@policy-as-versioned-x.invalid"
    human = "someone@example.org"
    lane = tuple(S.ALLOW_LIST)
    ids = {bot} | ALWAYS_SCHEDULED

    def run(root: str, *args: str, who: str = human) -> None:
        env = dict(os.environ, GIT_AUTHOR_NAME=who, GIT_AUTHOR_EMAIL=who,
                   GIT_COMMITTER_NAME=who, GIT_COMMITTER_EMAIL=who)
        subprocess.run(["git", "-C", root, "-c", "commit.gpgsign=false", *args],
                       capture_output=True, text=True, check=True, env=env)

    def write(root: str, path: str, text: str) -> None:
        full = os.path.join(root, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "a") as fh:
            fh.write(text)

    def commit(root: str, path: str, msg: str, who: str = human) -> None:
        write(root, path, msg + "\n")
        run(root, "add", "--", path)
        run(root, "commit", "-q", "-m", msg, who=who)

    def statuses(root: str, ref: str = "main") -> list[str]:
        return [s for s, _ in grade_ref(root, "x", ref, ids, lane)]

    def fails(root: str, ref: str = "main") -> list[str]:
        return [m for s, m in grade_ref(root, "x", ref, ids, lane) if s == "FAIL"]

    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "unit")
        os.makedirs(repo)
        run(repo, "init", "-q", "-b", "main")

        # a human declares whatever they like: never a lane violation
        commit(repo, "party.yaml", "roles: [adopter]")
        commit(repo, "composed/evidence.json", "{}")
        assert statuses(repo) == ["PASS"], statuses(repo)

        # a clock appends an observation: inside the lane
        commit(repo, "observations/policy.jsonl", '{"observed": 1}', who=bot)
        commit(repo, "drift/samples.jsonl", '{"sample": 1}', who=bot)
        assert statuses(repo) == ["PASS"], statuses(repo)
        assert "2 commit(s)" in grade_ref(repo, "x", "main", ids, lane)[0][1]

        # a clock-authored declaration a HUMAN merged: a reviewed proposal, not graded
        run(repo, "checkout", "-q", "-b", "fetch/policy-2.0.0")
        commit(repo, "policy/v2/feed.json", '{"version": "2.0.0"}', who=bot)
        run(repo, "checkout", "-q", "main")
        run(repo, "merge", "-q", "--no-ff", "-m", "Merge pull request #1", "fetch/policy-2.0.0")
        assert statuses(repo) == ["PASS"], statuses(repo)   # off the first-parent line entirely

        # ...and a squash of it: bot author, human committer -- on the line, named, not graded
        write(repo, "policy/v2/bump.yaml", "bump: minor\n")
        run(repo, "add", "--", "policy/v2/bump.yaml")
        env = dict(os.environ, GIT_AUTHOR_NAME=bot, GIT_AUTHOR_EMAIL=bot,
                   GIT_COMMITTER_NAME=human, GIT_COMMITTER_EMAIL=human)
        subprocess.run(["git", "-C", repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
                        "squashed"], capture_output=True, text=True, check=True, env=env)
        assert statuses(repo) == ["PASS", "NOTE"], statuses(repo)
        assert any("authored by a scheduled identity" in m
                   for s, m in grade_ref(repo, "x", "main", ids, lane) if s == "NOTE")

        # an automation identity no scheduled workflow configures: named, not graded
        commit(repo, "computed-semver/evidence/1.0.0.json", "{}",
               who="releases@policy-as-versioned-x.invalid")
        assert fails(repo) == [], fails(repo)
        assert any("automation identity releases@" in m
                   for s, m in grade_ref(repo, "x", "main", ids, lane) if s == "NOTE")

        # the orphan observations branch: its root commit is graded on everything it introduced
        run(repo, "checkout", "-q", "--orphan", "observations")
        run(repo, "rm", "-rfq", "--cached", ".")
        run(repo, "clean", "-fdq")
        commit(repo, "observations/README.md", "# observations", who=bot)
        commit(repo, "observations/policy.jsonl", '{"observed": 2}', who=bot)
        assert statuses(repo, "observations") == ["PASS"], statuses(repo, "observations")
        # ...and a declaration on it bites just the same
        commit(repo, "policy/v3/feed.json", "{}", who=bot)
        hit = fails(repo, "observations")
        assert len(hit) == 1 and "policy/v3/feed.json" in hit[0], hit
        run(repo, "checkout", "-q", "main")

        # THE BITE: a clock lands a declaration on main
        commit(repo, "deploy/tier.yaml", "tier: gold", who=bot)
        hit = fails(repo)
        assert len(hit) == 1 and "deploy/tier.yaml" in hit[0] and bot in hit[0], hit
        # a second clock identity writing observations does not clear the first's violation
        commit(repo, "observations/twin-sweep.jsonl", "{}",
               who="41898282+github-actions[bot]@users.noreply.github.com")
        assert len(fails(repo)) == 1, fails(repo)

        # a clock that MERGES is a fault even when the merged tree is all observations
        run(repo, "checkout", "-q", "-b", "side")
        commit(repo, "observations/side.jsonl", "{}", who=bot)
        run(repo, "checkout", "-q", "main")
        run(repo, "merge", "-q", "--no-ff", "-m", "clock merged", "side", who=bot)
        assert any("MERGE" in m for m in fails(repo)), fails(repo)

        # --- a merge GitHub committed (ticket 142): `GitHub <noreply@github.com>` is the
        # committer of every merge, squash or rebase made through the API or the web, so the
        # committer never names the credential that merged. On a fresh repository:
        actions = "41898282+github-actions[bot]@users.noreply.github.com"
        hand = "324560547+pavc-other-hand[bot]@users.noreply.github.com"

        def as_(root, author, committer, *args):
            env = dict(os.environ, GIT_AUTHOR_NAME=author, GIT_AUTHOR_EMAIL=author,
                       GIT_COMMITTER_NAME="GitHub" if committer == WEB_FLOW else committer,
                       GIT_COMMITTER_EMAIL=committer)
            subprocess.run(["git", "-C", root, "-c", "commit.gpgsign=false", *args],
                           capture_output=True, text=True, check=True, env=env)

        def never_asked(sha):
            raise AssertionError(f"who merged {sha[:9]} was asked, and the commit already says")

        def merged_by(login, is_bot):
            return lambda sha: {"pr": 7, "merged_by": login, "is_bot": is_bot,
                                "merged_at": "2026-09-25T10:00:00Z"}

        def graded(root, merger, ref="main"):
            return [(s, m) for s, m in grade_ref(root, "x", ref, ids, lane, merger)]

        gh = os.path.join(tmp, "gh")
        os.makedirs(gh)
        run(gh, "init", "-q", "-b", "main")
        commit(gh, "party.yaml", "roles: [adopter]")
        # (a) a MERGE commit GitHub wrote for the sweep's own credential, whose author is the
        #     Actions identity. A FAIL from the commit alone, and nobody is asked who merged.
        run(gh, "checkout", "-q", "-b", "sweep/observe")
        commit(gh, "observations/twin-sweep.jsonl", "{}", who=bot)
        run(gh, "checkout", "-q", "main")
        as_(gh, actions, WEB_FLOW, "merge", "-q", "--no-ff", "-m", "Merge pull request #7", "sweep/observe")
        hit = [m for s, m in graded(gh, never_asked) if s == "FAIL"]
        assert len(hit) == 1 and "MERGE onto main made through GitHub by " + actions in hit[0], hit
        run(gh, "reset", "-q", "--hard", "HEAD~1")
        # (b) the same merge made by the reviewed second hand: a NOTE naming it, not graded
        as_(gh, hand, WEB_FLOW, "merge", "-q", "--no-ff", "-m", "Merge pull request #7", "sweep/observe")
        assert [s for s, _ in graded(gh, never_asked)] == ["PASS", "NOTE"], graded(gh, never_asked)
        assert any("second hand" in m for s, m in graded(gh, never_asked) if s == "NOTE")
        run(gh, "reset", "-q", "--hard", "HEAD~1")
        # (c) the same merge made by a person through the web: out of scope, no line
        as_(gh, human, WEB_FLOW, "merge", "-q", "--no-ff", "-m", "Merge pull request #7", "sweep/observe")
        assert [s for s, _ in graded(gh, never_asked)] == ["PASS"], graded(gh, never_asked)
        run(gh, "reset", "-q", "--hard", "HEAD~1")
        # (d) a SQUASH GitHub wrote of the clock's proposal: the author is the clock, the
        #     committer GitHub, and who merged is not in the commit. No source: a named SKIP,
        #     never clean. A bot merger: FAIL. The second hand: NOTE. A person: NOTE.
        write(gh, "observations/twin-sweep.jsonl", "{}\n")
        run(gh, "add", "--", "observations/twin-sweep.jsonl")
        as_(gh, bot, WEB_FLOW, "commit", "-q", "-m", "twin sweep: observe (#7)")
        no_source = graded(gh, None)
        assert [s for s, _ in no_source] == ["SKIP", "PASS"], no_source
        assert "does not record who merged" in no_source[0][1] and "not graded either way" in no_source[0][1]
        hit = [m for s, m in graded(gh, merged_by("app/github-actions", True)) if s == "FAIL"]
        assert len(hit) == 1 and "pull request #7 merged by app/github-actions" in hit[0], hit
        hit = [m for s, m in graded(gh, merged_by("renovate[bot]", False)) if s == "FAIL"]
        assert len(hit) == 1 and "merged by renovate[bot]" in hit[0], hit
        by_hand = graded(gh, merged_by("app/pavc-other-hand", True))
        assert [s for s, _ in by_hand] == ["PASS", "NOTE"] and "second hand" in by_hand[1][1], by_hand
        by_person = graded(gh, merged_by("someone", False))
        assert [s for s, _ in by_person] == ["PASS", "NOTE"] and "merged by someone" in by_person[1][1], by_person
        # (e) a squash of a PERSON's commit by GitHub is out of scope, and a squash a person made
        #     locally (the person is the committer) is the NOTE it always was, with nobody asked
        run(gh, "reset", "-q", "--hard", "HEAD~1")
        write(gh, "composed/evidence.json", "{}\n")
        run(gh, "add", "--", "composed/evidence.json")
        as_(gh, human, WEB_FLOW, "commit", "-q", "-m", "compose (#8)")
        assert [s for s, _ in graded(gh, never_asked)] == ["PASS"], graded(gh, never_asked)
        write(gh, "observations/x.jsonl", "{}\n")
        run(gh, "add", "--", "observations/x.jsonl")
        as_(gh, bot, human, "commit", "-q", "-m", "squashed by hand")
        assert [s for s, _ in graded(gh, never_asked)] == ["PASS", "NOTE"], graded(gh, never_asked)
        assert any("the person is the committer" in m for s, m in graded(gh, never_asked))

        # a shallow checkout (actions/checkout's default) is deepened when it can be, and is a
        # could-not-look when it cannot -- never a thin walk graded as the whole lane
        for name, network in (("deep", True), ("thin", False)):
            clone = os.path.join(tmp, name)
            subprocess.run(["git", "clone", "-q", "--depth", "1", "--branch", "main",
                            f"file://{repo}", clone], check=True, capture_output=True)
            assert is_shallow(clone), name
            _net, how, shallow = refresh(clone, network)
            assert shallow is (not network), (name, how, shallow)
            assert ("deepened" in how) is network, (name, how)
        assert len(commits(os.path.join(tmp, "deep"), "origin/main")) > 1
        assert len(commits(os.path.join(tmp, "thin"), "origin/main")) == 1
        _net, how, _sh = refresh(os.path.join(tmp, "deep"), True)
        assert "main fetched now" in how and "observations fetched now" in how, how

        # a remote WITHOUT an observations branch (every adopter, and the hub): main is still
        # refreshed, the absence is named, and nothing claims a fetch of a ref that is not there
        plain = os.path.join(tmp, "plain")
        os.makedirs(plain)
        run(plain, "init", "-q", "-b", "main")
        commit(plain, "party.yaml", "roles: [adopter]")
        noobs = os.path.join(tmp, "noobs")
        subprocess.run(["git", "clone", "-q", f"file://{plain}", noobs],
                       check=True, capture_output=True)
        commit(plain, "drift/samples.jsonl", '{"sample": 1}', who=bot)   # after the clone
        net, how, shallow = refresh(noobs, True)
        assert net and not shallow, (net, how, shallow)
        assert "main fetched now" in how and "observations absent on origin" in how, how
        assert "FAILED" not in how and "observations fetched" not in how, how
        assert len(commits(noobs, "origin/main")) == 2, "origin/main was not refreshed"

        # an UNREACHABLE origin: no line claims freshness, network is given up, and a shallow
        # checkout is left shallow (a could-not-look for the caller), not reported deepened
        dead = os.path.join(tmp, "dead")
        subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{plain}", dead],
                       check=True, capture_output=True)
        run(dead, "remote", "set-url", "origin", f"file://{tmp}/no-such-remote")
        net, how, shallow = refresh(dead, True)
        assert not net and shallow, (net, how, shallow)
        assert "origin unreachable" in how and "fetched now" not in how, how
        assert "deepened" not in how and "left shallow" in how, how
        net, how, _sh = refresh(noobs, net)          # the next unit inherits the given-up network
        assert not net and "no fetch attempted" in how and "fetched now" not in how, how

        # the ref's copy of a workflow and the checkout's DIFFER under the same filename: both
        # identities and both lanes are graded (a union), so a clock the checkout copy no longer
        # names is still caught by what the ref's copy configured
        wf = os.path.join(tmp, "wf")
        os.makedirs(wf)
        run(wf, "init", "-q", "-b", "main")
        commit(wf, ".github/workflows/clock.yml", """\
on: {schedule: [{cron: "5 7 * * *"}]}
env: {OBSERVATION_LANE: "observations"}
jobs:
  observe:
    steps:
      - run: git config user.email "ref-bot@policy-as-versioned-x.invalid"
""")
        wfclone = os.path.join(tmp, "wfclone")
        subprocess.run(["git", "clone", "-q", f"file://{wf}", wfclone],
                       check=True, capture_output=True)
        commit(wf, "deploy/tier.yaml", "tier: gold", who="ref-bot@policy-as-versioned-x.invalid")
        refresh(wfclone, True)
        with open(os.path.join(wfclone, ".github/workflows/clock.yml"), "w") as fh:
            fh.write("""\
on: {schedule: [{cron: "5 7 * * *"}]}
env: {OBSERVATION_LANE: "drift/samples.jsonl"}
jobs:
  observe:
    steps:
      - run: git config user.email "local-bot@policy-as-versioned-x.invalid"
""")
        on_ref = workflows_on_ref(wfclone, "origin/main")
        local = _working_tree_workflows(wfclone)
        assert set(on_ref) == set(local) == {"clock.yml"}, (on_ref.keys(), local.keys())
        both = scheduled_identities("x", on_ref, local)
        assert both == ALWAYS_SCHEDULED | {"ref-bot@policy-as-versioned-x.invalid",
                                           "local-bot@policy-as-versioned-x.invalid"}, both
        assert declared_lane(on_ref, local) == ("observations", "drift/samples.jsonl"), \
            declared_lane(on_ref, local)
        only_local = scheduled_identities("x", local)
        assert "ref-bot@policy-as-versioned-x.invalid" not in only_local
        # the checkout copy alone would miss it: ref-bot reads as an unscheduled automation
        # identity there -- named in a NOTE, a merge-by-filename would have graded PASS
        alone = grade_ref(wfclone, "x", "origin/main", only_local, lane)
        assert [s for s, _ in alone] == ["PASS", "NOTE"], alone
        hit = [m for s, m in grade_ref(wfclone, "x", "origin/main", both, lane) if s == "FAIL"]
        assert len(hit) == 1 and "deploy/tier.yaml" in hit[0] and "ref-bot@" in hit[0], hit

    # the identity and lane parsers, on the shapes the estate's workflows actually use
    docs = {
        "fetch.yml": yaml.safe_load("""
on: {schedule: [{cron: "5 7 * * *"}]}
env: {OBSERVATION_LANE: "observations"}
jobs:
  observe:
    steps:
      - run: |
          git -c user.name="x publisher clock" \\
            -c user.email="fetch-bot@policy-as-versioned-x.invalid" commit -m observe
          git push origin observations
      - run: |
          git config user.name "policy-as-versioned feeds bot"
          git config user.email "feeds-bot@${GITHUB_REPOSITORY_OWNER}.invalid"
"""),
        "drift-sample.yml": yaml.safe_load("""
on: {schedule: [{cron: "5 8 * * *"}]}
env: {OBSERVATION_LANE: "drift/samples.jsonl party.yaml"}
jobs:
  sample:
    steps:
      - run: git config user.email "drift-sample@policy-as-versioned-x.invalid"
"""),
        "cut-release.yml": yaml.safe_load("""
on: {workflow_dispatch: {}}
jobs:
  cut:
    steps:
      - run: git -c user.email="releases@${GITHUB_REPOSITORY_OWNER}.invalid" tag -s v1
"""),
    }
    found = scheduled_identities("x", docs)
    assert found == ALWAYS_SCHEDULED | {"fetch-bot@policy-as-versioned-x.invalid",
                                        "feeds-bot@policy-as-versioned-x.invalid",
                                        "drift-sample@policy-as-versioned-x.invalid"}, found
    assert "releases@policy-as-versioned-x.invalid" not in found, "a dispatch is not a clock"
    assert declared_lane(docs) == ("observations", "drift/samples.jsonl"), declared_lane(docs)
    assert declared_lane({"cut-release.yml": docs["cut-release.yml"]}) == tuple(S.ALLOW_LIST)
    assert pushes_observations(docs) and not pushes_observations(
        {"drift-sample.yml": docs["drift-sample.yml"]})
    assert in_lane("observations/x.jsonl", lane) and in_lane("talk/captures/a.out", lane)
    assert not in_lane("observations-of-mine/x", lane) and not in_lane("party.yaml", lane)

    # the platform composer's copy of ADR-0024's list (ticket 134): equal passes, anything else
    # fails and says why
    same = f"{PLATFORM_CONSTANT} = {tuple(S.ALLOW_LIST)!r}\n"
    assert platform_copy(same)[0] == "PASS", platform_copy(same)
    for bad in (None, "x = (\n", "OTHER = ()\n",
                f"{PLATFORM_CONSTANT} = {tuple(S.ALLOW_LIST) + ('party.yaml',)!r}\n",
                f"{PLATFORM_CONSTANT} = {tuple(S.ALLOW_LIST[:-1])!r}\n",
                f"{PLATFORM_CONSTANT} = tuple(ALLOW)\n"):
        assert platform_copy(bad)[0] == "FAIL", (bad, platform_copy(bad))

    print("ok  the lane grader bites: a clock's declaration on main or on the observations "
          "branch fails and names the commit, a clock's merge fails, a merge GitHub committed "
          "for a scheduled or automation token fails from the commit's author alone, one by the "
          "reviewed second hand or a person is not graded, a squash or rebase GitHub wrote of a "
          "clock's commit is graded by who merged the pull request (a bot fails, a person or "
          "the second hand is noted) and is a named could-not-look with no source, a clock's observations "
          "pass, an orphan root commit is graded, a human's declaration and a clock-authored "
          "commit a human merged or squashed are not graded, an unscheduled automation "
          "identity is named not graded, a shallow checkout is deepened or is a could-not-look, "
          "a fetch is reported per ref as done, absent on origin or failed and an unreachable "
          "origin never reads as fetched, the ref's and the checkout's copies of one workflow "
          "are graded as a union, identities and lanes parse from the workflows, and the "
          "platform composer's copy of ADR-0024's list must equal this one")


def main(argv: list[str]) -> int:
    if len(argv) > 1 and argv[1] == "selfcheck":
        selfcheck()
        return 0
    return check()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
