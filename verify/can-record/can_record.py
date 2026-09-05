#!/usr/bin/env python3
"""The clock says whether it can record, before it measures (eco-system ticket 100).

`.github/workflows/truth.yml` runs on every push that touches the gate, on every branch. Until
this ticket it wrote its TRUTH line, committed it, ran `git pull --rebase --autostash origin main`
and pushed `HEAD` to `${GITHUB_REF_NAME}`. On `main` the rebase is a no-op and the push
fast-forwards. On a ticket branch the rebase replays the branch's own commits onto `origin/main`,
giving every one a new SHA, so `HEAD` stops being a descendant of `origin/<branch>` and the push
is refused non-fast-forward. The line was produced, committed and thrown away, and nothing said
so: run 98 on `ticket-89-deny-is-not-a-rung` printed `Rebasing (12/12)`, `Successfully rebased`
and then `! [rejected] (non-fast-forward)` with nobody pushing and the remote tip unmoved.

This module holds the three questions that are decidable from data. It deliberately answers none
of the questions that are only decidable by running git: whether the guard's verdict is TRUE is
graded by `verify-can-record.sh`, which runs the workflow's own shell over two throwaway
repositories and compares the verdict with what the push does to the remote ref.

    can_record.py shape <workflow.yml>     grade the workflow's shape; print each fault
    can_record.py log <root>               grade talk/truth.log against its own git blame
    can_record.py step <workflow.yml> <job> <name fragment>
                                           print that step's shell, made portable, with every
                                           substitution printed on stderr as `note: a -> b`
    can_record.py selfcheck                the pure functions grade planted data as documented

Exit 0 clean, 1 with faults. There is no could-not-look: everything it reads is in this
repository, so a reason it cannot look is a red, not a shrug.
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import yaml

# The step names the shape check reads. They are fragments, matched against `name:`, because the
# names carry prose the ticket wanted a builder to see in the log.
GUARD_STEP = "does this run record"
GATE_STEP = "the gate"
RECORD_STEP = "record the TRUTH line"
CAGE_STEP = "observation cage"

# The clock's own identity, set by the cage step itself.
CLOCK_EMAIL = "truth@users.noreply.github.com"

# talk/truth.log carries exactly one line that no CI run wrote: `run=local`, 2026-08-28, from the
# gate run by hand on the owner's machine before the clock existed. It says `local` rather than
# borrowing a run number, so it is honest about what it is; ADR-0024 point 6 records that a local
# run is not citable. It is grandfathered by COUNT, not by date or by content, so a second
# hand-written line -- the exact thing this ticket refuses -- turns the check red.
LOCAL_LINES_ALLOWED = 1

_RUN = re.compile(r"\brun=(\S+)")
_RECORD_SUBJECT = re.compile(r"^truth: record run (\d+) \[skip ci\]$")


class TruthRow(NamedTuple):
    """One TRUTH line of `talk/truth.log` with the commit `git blame` attributes it to."""
    line: str
    email: str
    subject: str
    commit: str


# -- the shape of the workflow ---------------------------------------------------------------------

def _steps(doc: dict, job: str) -> list[dict]:
    return list((doc.get("jobs") or {}).get(job, {}).get("steps") or [])


def _index_of(steps: list[dict], fragment: str) -> int:
    for i, step in enumerate(steps):
        if fragment in str(step.get("name") or ""):
            return i
    return -1


def step_shell(doc: dict, job: str, fragment: str) -> str:
    """The `run:` of the one step in `job` whose name carries `fragment`.

    Raises KeyError when no step matches: a fixture that silently ran an empty string would
    report a green for a step that is not there, which is the shape of false green this estate
    keeps finding."""
    steps = _steps(doc, job)
    i = _index_of(steps, fragment)
    if i < 0:
        raise KeyError(f"no step in job {job!r} is named {fragment!r}")
    return str(steps[i].get("run") or "")


def shape_faults(doc: dict, text: str) -> list[str]:
    """The workflow still has the shape ticket 100 decided, or the reasons it does not.

    `text` is the raw YAML, read for the two things a parsed document flattens away -- but read
    line by line with comment lines skipped, so a force push written in a COMMENT is not a fault
    (the docstring claimed otherwise until 2026-09-05; the code has always skipped them, and the
    code is right: a comment describing what the cage must never do is not the cage doing it).
    The two things are: a force
    push written anywhere at all, including in a comment or a step this checker does not name."""
    faults: list[str] = []
    steps = _steps(doc, "gate")
    if not steps:
        return ["truth.yml has no `gate` job with steps"]

    checkout = [s for s in steps if str(s.get("uses") or "").startswith("actions/checkout")]
    if not checkout:
        faults.append("the gate job has no actions/checkout step")
    for step in checkout:
        with_ = step.get("with") or {}
        if str(with_.get("fetch-depth")) != "0":
            faults.append(
                "the gate's checkout does not set fetch-depth: 0 -- a shallow checkout cannot "
                "tell whether `git pull --rebase origin main` will replay this ref's commits, so "
                "the guard would be guessing")

    i_guard = _index_of(steps, GUARD_STEP)
    i_gate = _index_of(steps, GATE_STEP)
    i_record = _index_of(steps, RECORD_STEP)
    i_cage = _index_of(steps, CAGE_STEP)
    for name, i in ((GUARD_STEP, i_guard), (GATE_STEP, i_gate),
                    (RECORD_STEP, i_record), (CAGE_STEP, i_cage)):
        if i < 0:
            faults.append(f"the gate job has no step named {name!r}")
    if i_guard < 0:
        return faults

    if not (0 <= i_guard < i_gate):
        faults.append(f"{GUARD_STEP!r} does not run before {GATE_STEP!r} -- a run that says what "
                      "it can record AFTER it measured has not said it before measuring")
    guard = str(steps[i_guard].get("run") or "")
    if "GITHUB_ENV" not in guard or "CAN_RECORD=" not in guard:
        faults.append(f"{GUARD_STEP!r} does not write CAN_RECORD= to $GITHUB_ENV, so the later "
                      "steps have nothing to read")
    # The decision itself: the default branch, and nothing else, records (ticket 100). The name
    # comes from the event rather than a literal, so a repository that renames its default branch
    # does not quietly stop recording.
    guard_env = steps[i_guard].get("env") or {}
    if "default_branch" not in str(guard_env.get("DEFAULT_BRANCH", "")):
        faults.append(f"{GUARD_STEP!r} does not take DEFAULT_BRANCH from "
                      "github.event.repository.default_branch, so it would be comparing the ref "
                      "against a literal that can go stale")
    if "${GITHUB_REF_NAME}" not in guard or "${DEFAULT_BRANCH}" not in guard:
        faults.append(f"{GUARD_STEP!r} does not compare GITHUB_REF_NAME with DEFAULT_BRANCH -- "
                      "recording on the default branch and nowhere else IS the decision "
                      "(ticket 100), and nothing else in the file carries it")

    if i_record >= 0:
        record = str(steps[i_record].get("run") or "")
        if "CAN_RECORD" not in record:
            faults.append(f"{RECORD_STEP!r} appends to talk/truth.log without consulting "
                          "CAN_RECORD -- it would write a line the push cannot carry")
        if "talk/truth.log" not in record:
            faults.append(f"{RECORD_STEP!r} no longer names talk/truth.log")

    if i_cage >= 0:
        cage = str(steps[i_cage].get("run") or "")
        if "CAN_RECORD" not in cage:
            faults.append(f"the {CAGE_STEP} does not consult CAN_RECORD at all, so it commits a "
                          "line that cannot be pushed")
        elif "git commit" in cage and cage.index("CAN_RECORD") > cage.index("git commit"):
            faults.append(f"the {CAGE_STEP} reads CAN_RECORD only after `git commit` -- the "
                          "commit this ticket exists to stop is already made")
        if 'push origin HEAD:"${GITHUB_REF_NAME}"' not in cage:
            faults.append("the cage no longer pushes the one refspec it is allowed to push, "
                          'push origin HEAD:"${GITHUB_REF_NAME}"')

    # F2: the cage must rebase onto the branch it was TOLD is default, never a literal. The
    # guard takes the name from the event so a rename cannot silently stop the clock, and this
    # half kept a hardcoded `main` -- so on a rename the guard says can=yes, the commit is made,
    # the pull fails and the push never runs. Loudly lost is still lost. Its own scan, because
    # the push scan below only visits lines carrying `git ... push` and a pull carries neither.
    for line in re.sub(r"\\\n\s*", " ", text).splitlines():
        if line.strip().startswith("#"):
            continue
        if re.search(r"\bgit\b[^\n]*\bpull\b[^\n]*\brebase\b[^\n]*\borigin\s+[\"']?(main|master)\b",
                     line):
            faults.append("the cage rebases onto a literal branch name rather than the default "
                          "branch it was given, so a rename stops the clock after the commit is "
                          "already made: " + line.strip())

    # Continuations first: the one real push in this workflow is written `git -c http.extraheader=
    # ... \` then `push origin HEAD:...` on the next line, so a per-line scan would read the push
    # and the `git` as two different statements and see neither.
    for line in re.sub(r"\\\n\s*", " ", text).splitlines():
        if line.strip().startswith("#") or not re.search(r"\bgit\b.*\bpush\b", line):
            continue
        # An optional quote between the whitespace and the `+`: `git push origin "+HEAD:main"`
        # and `'+HEAD:${GITHUB_REF_NAME}'` both slipped through, because the old pattern needed
        # whitespace IMMEDIATELY before the plus and a quote intervenes (review F5).
        if "--force" in line or "-f " in line or re.search(r"""push[^\n]*\s["']?\+\S+:""", line):
            faults.append(f"the workflow can force push, which would rewrite a builder's branch "
                          f"to land an observation: {line.strip()}")
    return faults


# -- the record: who wrote each line of talk/truth.log ---------------------------------------------

def truth_log_faults(rows: list[TruthRow]) -> list[str]:
    """Every recorded TRUTH line came from a run that could record it.

    The rule, in full. A line naming a run NUMBER is a citable observation, so the commit that
    introduced it must be the clock's own (`truth surface`) and its message must name the same
    run: `truth: record run N [skip ci]`. A line naming no number must say `run=local`, must not
    be the clock's, and there may be LOCAL_LINES_ALLOWED of them. Anything else is a line whose
    provenance the log cannot support."""
    faults: list[str] = []
    local = 0
    for row in rows:
        m = _RUN.search(row.line)
        run = m.group(1) if m else ""
        stamp = row.line.split(" hub=")[0].strip()
        if run.isdigit():
            subject = _RECORD_SUBJECT.match(row.subject)
            if row.email != CLOCK_EMAIL:
                faults.append(f"{stamp}: run={run} claims a citable run, but the commit that "
                              f"wrote it ({row.commit}) is by {row.email}, not the clock "
                              f"({CLOCK_EMAIL}) -- a hand does not author a clock's observation")
            elif not subject:
                faults.append(f"{stamp}: run={run} is blamed to {row.commit}, whose message "
                              f"{row.subject!r} is not a clock's record commit")
            elif subject.group(1) != run:
                faults.append(f"{stamp}: the line says run={run} and the commit that wrote it "
                              f"({row.commit}) says run {subject.group(1)}")
        elif run != "local":
            faults.append(f"{stamp}: run={run or '(absent)'} is neither a run number nor `local`, "
                          f"so nothing says which run could record it")
        elif row.email == CLOCK_EMAIL:
            faults.append(f"{stamp}: a run=local line was ADDED by the clock ({row.commit}); the "
                          f"clock records a run number or it records nothing")
        else:
            local += 1
    if local > LOCAL_LINES_ALLOWED:
        faults.append(f"talk/truth.log carries {local} run=local lines and "
                      f"{LOCAL_LINES_ALLOWED} is grandfathered: a local run is not citable "
                      f"(ADR-0024 point 6) and a TRUTH line is not written by hand")
    return faults


def adding_commit(root: Path, line: str, log_path: str = "talk/truth.log") -> tuple[str, str, str]:
    """(sha, author email, subject) of the commit that LAST ADDED `line` to `log_path`.

    Not `git blame`, and the difference is load-bearing (measured 2026-09-05). Blame answers
    "which commit does git attribute this line to", which at a merge prefers the parent where
    identical content already existed. So after a hand-authored line was REVERTED and re-added
    by the clock's own cherry-picked commits -- the correct repair -- blame still named the
    hand's commit on `main`, and this check reported three faults on a log that had been put
    right. The rule wants the commit that put the line where it now is, which is a different
    question, and `git log --full-history -S` answers it: every commit that changed the line's
    presence, newest first, including both sides of a merge that history simplification would
    otherwise hide. The newest one in which the line is PRESENT is the one that added it.

    Raises GitFailed rather than guessing: an unattributable line is the thing this check exists
    to notice."""
    out = _git_checked(root, "log", "--full-history", "--format=%H\x1f%ae\x1f%s",
                       "-S", line, "--", log_path)
    for record in [r for r in out.splitlines() if r.strip()]:
        sha, email, subject = record.split("\x1f", 2)
        if line in _git_checked(root, "show", f"{sha}:{log_path}"):
            return sha[:7], email, subject
    raise GitFailed(
        f"no commit in this history adds the line {line[:60]!r}... to {log_path}. A recorded "
        f"line nothing can be shown to have written is exactly what this check exists to catch")


def blame_rows(root: Path) -> list[TruthRow]:
    """Every TRUTH line of talk/truth.log with the commit that LAST ADDED it, its author and
    subject. Named `blame_rows` for its callers; it no longer uses `git blame` -- see
    `adding_commit` for the measurement that forced the change.

    A shallow checkout cannot answer the question at all (the history past the graft is not
    there), so this raises rather than returning a comfortable answer."""
    root = Path(root)
    shallow = subprocess.run(["git", "-C", str(root), "rev-parse", "--is-shallow-repository"],
                             capture_output=True, text=True, check=True).stdout.strip()
    if shallow != "false":
        raise RuntimeError("this checkout is shallow: the commit that added a line is not in "
                           "this history, so every line would attribute to the graft boundary "
                           "and the log would read clean for the wrong reason")
    rows = []
    for content in (root / "talk" / "truth.log").read_text().splitlines():
        if not content.startswith("TRUTH "):
            continue
        commit, email, subject = adding_commit(root, content)
        rows.append(TruthRow(line=content, email=email, subject=subject, commit=commit))
    return rows


# -- the third failure mode: a line that landed on a branch and was orphaned by its own merge ------

class Stranded(NamedTuple):
    """A TRUTH line the clock committed somewhere that is not the default branch."""
    commit: str
    ref: str
    line: str
    in_main_log: bool   # the line, byte for byte, is in the default branch's talk/truth.log
    tree_on_main: bool  # the `hub=` commit it measured is reachable from the default branch


def stranded_faults(entries: list[Stranded]) -> tuple[list[str], list[str]]:
    """Faults and notes for clock lines committed off the default branch.

    A line whose measured tree NEVER reached the default branch describes a state the citable
    history never had, so its absence from that log is correct and it is a note. A line whose
    measured tree IS on the default branch was a citable observation, and its absence is the
    estate losing a number it had -- run 101 on 2026-09-05, and runs 76, 84 and 88 before it,
    which nobody had noticed. Presence is judged on the LINE, not on the commit, because the
    repair for one of these is a cherry-pick of the clock's own commit, which lands the same
    bytes under a new sha."""
    faults: list[str] = []
    notes: list[str] = []
    for e in entries:
        stamp = e.line.split(" hub=")[0].strip()
        if e.in_main_log:
            notes.append(f"{stamp}: committed on {e.ref} and its line is in the default branch's "
                         f"log (commit {e.commit} was rescued, or the branch merged with it)")
        elif not e.tree_on_main:
            notes.append(f"{stamp}: committed on {e.ref} ({e.commit}); the tree it measured never "
                         f"reached the default branch, so the line is correctly absent from a log "
                         f"that is citable only for that branch's history")
        else:
            faults.append(f"{stamp}: {e.commit} on {e.ref} measured a tree that IS on the default "
                          f"branch, so the observation was citable, and its line never reached "
                          f"that branch's talk/truth.log -- the record lost a number it had")
    return faults, notes


def _git(root: Path, *args: str) -> str:
    """git, best effort. Use ONLY where an empty answer is a legitimate result and not a fault."""
    return subprocess.run(["git", "-C", str(root), *args],
                          capture_output=True, text=True).stdout


class GitFailed(Exception):
    """A git command whose failure changes a verdict (review F4, 2026-09-05).

    `_git` discards the exit status and stderr, which is right where an empty answer means
    something and wrong everywhere else. Part 1b degraded to a comfortable note because of it:
    in a `git clone -s` whose `origin/main` pointed at a stale local main, it reported runs 100
    and 101 as "the tree it measured never reached the default branch, so the line is correctly
    absent" -- when both lines were in fact present. A check that declares no could-not-look may
    not answer a question it could not look at."""


def _git_checked(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if r.returncode != 0:
        raise GitFailed(f"git {' '.join(args)} failed (rc={r.returncode}): "
                        f"{r.stderr.strip() or 'no stderr'}")
    return r.stdout


def default_ref(root: Path) -> str:
    """The ref this checkout's default branch actually lives at.

    Derived, never assumed (review F2): the guard step takes the branch name from the event so a
    rename cannot silently stop the clock, and this half hardcoded `origin/main` with a literal
    `main` fallback -- so the rename-safety existed in only half the path. `origin/HEAD` is what
    the remote itself says its default is; a plain `origin/<name>` and then a local branch are
    the fallbacks, and if none resolves this raises rather than guessing."""
    head = _git(root, "symbolic-ref", "-q", "--short", "refs/remotes/origin/HEAD").strip()
    candidates = [head] if head else []
    candidates += ["origin/main", "origin/master", "main", "master"]
    for ref in candidates:
        if _git(root, "rev-parse", "-q", "--verify", f"{ref}^{{commit}}").strip():
            return ref
    raise GitFailed(
        "no default branch ref resolves in this checkout: tried "
        + ", ".join(candidates)
        + ". Without one, 'is this line on the default branch' has no answer, and reporting "
          "every line as correctly absent would be a false green")


def stranded_entries(root: Path) -> tuple[list[Stranded], list[str]]:
    """Every clock commit in this checkout that is not on the default branch, and the refs looked
    at. It can only see the refs the checkout carries: a branch already deleted is gone, and this
    reports what it examined rather than claiming to have examined everything."""
    root = Path(root)
    main_ref = default_ref(root)
    refs = [r for r in _git(root, "for-each-ref", "--format=%(refname:short)",
                            "refs/heads", "refs/remotes").split() if r != main_ref]
    if not refs:
        # Part 2 asserts the workflow checks out with `fetch-depth: 0`, so a checkout carrying no
        # ref other than the default contradicts the shape this same script just passed. Before
        # this it printed "ok ... among the 0 other ref(s)" and passed (review F4).
        raise GitFailed(
            f"this checkout carries no ref other than {main_ref}, so nothing could be stranded "
            f"on one and this check has measured nothing. Part 2 asserts fetch-depth: 0, which "
            f"is what makes that a contradiction rather than a quiet pass")
    commits = _git(root, "rev-list", f"--author={CLOCK_EMAIL}", *refs, "--not", main_ref).split()
    main_log = _git(root, "show", f"{main_ref}:talk/truth.log")
    entries: list[Stranded] = []
    for commit in commits:
        added = [ln[1:] for ln in _git(root, "show", "--format=", "--unified=0", commit,
                                       "--", "talk/truth.log").splitlines()
                 if ln.startswith("+TRUTH ")]
        containing = _git(root, "for-each-ref", "--contains", commit,
                          "--format=%(refname:short)", "refs/heads", "refs/remotes").split()
        ref = next((r for r in containing if r != main_ref), "(no ref)")
        for line in added:
            hub = re.search(r"\bhub=([0-9a-f]+)", line)
            # A line with no readable `hub=` measured a tree nobody can locate, so it is treated
            # as not on the default branch and reported as a note rather than a loss.
            on_main = False
            if hub:
                on_main = subprocess.run(
                    ["git", "-C", str(root), "merge-base", "--is-ancestor",
                     hub.group(1), main_ref], capture_output=True).returncode == 0
            entries.append(Stranded(commit=commit[:7], ref=ref, line=line,
                                    in_main_log=line in main_log, tree_on_main=on_main))
    return entries, refs


# -- the extraction the shell fixture runs ----------------------------------------------------------

# Two substitutions, and the fixture prints both. The runner has gitsign and a Fulcio to reach;
# a laptop has neither, and a fixture that planted a stub signer would be faking a signature to
# grade a check about not faking observations. `base64 -w0` is GNU; BSD base64 has no -w and
# fails the whole command. Neither touches the push, which is the line under test.
SUBSTITUTIONS = (
    ("git config commit.gpgsign true", "git config commit.gpgsign false"),
    ("base64 -w0", "base64 | tr -d '\\n'"),
)


def portable(shell: str) -> tuple[str, list[str]]:
    """The step's shell as it can run off the runner, and every change made to get it there."""
    notes: list[str] = []
    for before, after in SUBSTITUTIONS:
        if before in shell:
            shell = shell.replace(before, after)
            notes.append(f"{before} -> {after}")
    return shell, notes


# -- selfcheck ----------------------------------------------------------------------------------

def selfcheck() -> int:
    clock = CLOCK_EMAIL
    good = [TruthRow("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a", clock,
                     "truth: record run 99 [skip ci]", "7348692")]
    assert truth_log_faults(good) == [], truth_log_faults(good)
    hand = [TruthRow("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a", "chris@cns.me.uk",
                     "Ticket 100: tidy the log", "deadbee")]
    assert len(truth_log_faults(hand)) == 1
    wrong = [TruthRow("TRUTH 2026-09-05T09:44Z run=99 hub=e68a82a", clock,
                      "truth: record run 87 [skip ci]", "deadbee")]
    assert len(truth_log_faults(wrong)) == 1
    local = TruthRow("TRUTH 2026-08-28T04:00Z run=local hub=2326f31", "chris@cns.me.uk",
                     "the local gate", "0f0f0f0")
    assert truth_log_faults([local]) == []
    assert len(truth_log_faults([local, local])) == 1
    odd = [TruthRow("TRUTH 2026-09-05T09:44Z run=rehearsal hub=e", clock, "truth: record", "a")]
    assert len(truth_log_faults(odd)) == 1
    rescued = Stranded("f8968f6", "origin/ticket-89", "TRUTH x run=101 hub=6bca5a3 pass=68",
                       in_main_log=True, tree_on_main=True)
    lost = Stranded("2545d1a", "origin/ticket-64", "TRUTH x run=88 hub=17106c2 pass=60",
                    in_main_log=False, tree_on_main=True)
    never = Stranded("aaaaaaa", "origin/ticket-9", "TRUTH x run=9 hub=deadbee pass=1",
                     in_main_log=False, tree_on_main=False)
    f, n = stranded_faults([rescued, lost, never])
    assert len(f) == 1 and "run=88" in f[0], (f, n)
    assert len(n) == 2, n
    shell, notes = portable("git config commit.gpgsign true\nbase64 -w0\n")
    assert notes == [f"{a} -> {b}" for a, b in SUBSTITUTIONS], notes
    assert "commit.gpgsign false" in shell and "base64 | tr -d" in shell
    try:
        step_shell({"jobs": {"gate": {"steps": []}}}, "gate", "nothing")
    except KeyError:
        pass
    else:
        print("selfcheck: an unknown step name did not raise")
        return 1
    print("  ok   selfcheck: a hand-written line, a line whose run number disagrees with its "
          "commit, a second run=local line, a run that is neither a number nor `local`, a "
          "citable line stranded off the default branch, and an unknown step name each fail as "
          "documented; a rescued line and one whose measured tree never reached the default "
          "branch are notes, not faults")
    return 0


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]
    if cmd == "selfcheck":
        return selfcheck()
    if cmd == "shape":
        path = Path(argv[2])
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        faults = shape_faults(doc, path.read_text(encoding="utf-8"))
        for f in faults:
            print(f"  !! {f}")
        return 1 if faults else 0
    if cmd == "log":
        rows = blame_rows(Path(argv[2]))
        faults = truth_log_faults(rows)
        for f in faults:
            print(f"  !! {f}")
        if not faults:
            n_local = sum(1 for r in rows if "run=local" in r.line)
            # F6: an empty log is not a clean log. Zero recorded lines used to print
            # "ok 0 recorded TRUTH line(s)" and pass -- the pytest guarded it, the gate
            # script did not, so the one place a reader looks would have called an empty
            # record spotless.
            if not rows:
                print("FAIL: talk/truth.log carries no TRUTH line at all. An empty record is not a clean record")
                return 1
            print(f"  ok   {len(rows) - n_local} recorded TRUTH line(s), each ADDED by the clock "
                  f"commit whose message names the same run; {n_local} declared run=local line(s)")
        return 1 if faults else 0
    if cmd == "stranded":
        entries, refs = stranded_entries(Path(argv[2]))
        faults, notes = stranded_faults(entries)
        for n in notes:
            print(f"  --   {n}")
        for f in faults:
            print(f"  !! {f}")
        if not faults:
            print(f"  ok   no clock line is stranded off the default branch, among the "
                  f"{len(refs)} other ref(s) this checkout carries (a branch already deleted "
                  f"cannot be looked at from here)")
        return 1 if faults else 0
    if cmd == "step":
        path = Path(argv[2])
        doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        shell, notes = portable(step_shell(doc, argv[3], argv[4]))
        for n in notes:
            print(f"note: {n}", file=sys.stderr)
        sys.stdout.write(shell)
        return 0
    print(f"unknown command {cmd!r}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
