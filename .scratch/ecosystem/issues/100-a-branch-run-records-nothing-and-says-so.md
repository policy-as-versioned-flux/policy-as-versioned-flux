# 100 — A branch run records nothing, and nothing says so

Type: task (AFK)
Status: open
Blocked by: none

## Question

`truth.yml` runs on every push to every branch. On a ticket branch its TRUTH line is produced,
committed, and then thrown away, and nothing anywhere says this happens. Builders have spent real
effort chasing lost observations they did not cause and cannot prevent.

Make the clock honest about which runs can record. Done = a run that cannot land its line says so
in its own log before it takes the measurement, `talk/truth.log` is written only by runs that can
record, and a check grades the rule so it cannot rot.

## The mechanism, established 2026-09-05

`.github/workflows/truth.yml` writes the line, commits it, then:

    git pull --rebase --autostash origin main     # line 252
    git ... push origin HEAD:"${GITHUB_REF_NAME}"  # line 256

On `main` the rebase is a no-op and the push fast-forwards. On a ticket branch the rebase replays
the branch's own commits onto `origin/main`, giving every one of them a new SHA, so `HEAD` is no
longer a descendant of `origin/<branch>` and the push is refused non-fast-forward. The line lands
only in the narrow case where the branch is already on top of `origin/main` with nothing to replay.

**Proved by a controlled case, not by inference.** Run 98 on `ticket-89-deny-is-not-a-rung`: nobody
pushing, the remote tip unmoved, `Rebasing (12/12)`, `Successfully rebased`, then
`! [rejected] (non-fast-forward)`.

**A merge commit guarantees it.** Merging `origin/main` INTO a ticket branch is exactly what forces
the rebase to rewrite history. Rebasing the branch onto `origin/main` is the shape that does not.
The build brief briefly carried the opposite advice; the builder who wrote it caught it and
corrected it in the same session.

## What this cost, and why it is worth a ticket rather than a note

Three lines were lost on one branch in one day (runs 92, 95 and 98), one of them the best figure
that branch had produced. Two builders and the integrator each spent time attributing them to a
push, to `origin/main` moving, and to each other. Only one of the three was anyone's doing. The
integrator's own memory of the estate recorded the wrong cause and had to be corrected.

The deeper reason: **the clock is the estate's one instrument for recording what was true, and it
was silently failing on most of the branches it ran on.** A clock that cannot record should say so
before it measures, exactly as every check in this estate says what it could not look at.

## What to build

1. **Say it before measuring.** The run establishes whether it can land its line — is
   `GITHUB_REF_NAME` the default branch, or is the branch already on `origin/main` — and prints
   that in as many words at the top of its own log. A run that cannot record still MEASURES and
   still prints its TRUTH line to the log for a reader to quote; it just does not pretend the line
   will be recorded.
2. **Do not commit a line that cannot be pushed.** A commit that is created and then discarded is
   noise in every builder's `git log` and is what made the loss look like a builder's fault.
3. **Grade the rule.** A check in the gate asserts that every TRUTH line in `talk/truth.log` came
   from a run that could record, and that the workflow's push shape still matches what this ticket
   decides. Ticket 83's manifest rules apply: declare what it cannot look at.

**Do not "fix" this by force-pushing the clock's commit to the branch.** A clock that rewrites a
builder's branch is worse than one that records nothing, and force-pushing over an observation is
the thing this estate refuses.

**An open question for whoever builds it:** should a branch run take the measurement at all? It
costs a full gate run per push. The argument for keeping it is that the run's log is where a
builder reads what their branch does to the gate, and three tickets today quoted exactly that. The
argument against is that it is a measurement nobody can cite. Decide it, record the reason.

## Notes

Charted 2026-09-05 from ticket 89's round-2 build, which established the mechanism, and ticket 91's,
which hit the same wall. Related: [96](96-the-citable-line-says-whether-the-twin-may-write.md)
carries the enact mode on the TRUTH line and touches the same producer.

The rule a builder needs until this lands: **rebase onto `origin/main`, never merge it in; and
never push while a `truth` run is `in_progress` on your branch.** Both are in the build brief.
