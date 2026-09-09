# 108 — The commit that records the number turns two checks red, and `[skip ci]` means nothing re-measures

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

`truth.yml` measures main, writes its TRUTH line into `talk/truth.log` and the run's captures into
`talk/captures/`, and commits that with `[skip ci]`. Two checks READ those files. So the commit
that records the number changes the input of two checks that were green when the number was
taken — and `[skip ci]` guarantees nothing measures main again afterwards.

The estate's citable `fail=` is therefore taken one commit before the state it describes.

## The measurement

Both checks were run on plain worktrees of two adjacent commits of `main`, with no branch and no
uncommitted change in either:

| commit | `verify/a-fall-blocks/` | `verify/derived-status/` |
|---|---|---|
| `691a32a` (the tree run 184 measured) | exit 0, PASS | exit 0, PASS |
| `6772a7a` (`truth: record run 184 [skip ci]`) | exit 1 | exit 1 |

    FAIL: 1 fault(s) -- a fall in the citable number is not a blocking event (ticket 59)
    FAIL: 1 fault(s) -- a ticket's Status: is typed rather than derived (ticket 59)

`git log 691a32a..6772a7a` is exactly one commit and it touches only `talk/truth.log`,
`talk/captures/_grades.tsv` and 28 capture files. Nothing else in the estate moved.

So main's newest recorded line, run 184, says `fail=10` about a tree that no longer exists;
`main` as it stands is `fail=12`. Run 185 (a branch run, not citable) measured the same 12 and
its extra two are exactly these.

Both checks are ticket 59's. This is not a defect in either of them: each reads the newest
recorded line, which is what it was built to do.

## Why it matters

1. **The citable number understates main by 2, permanently and by construction.** It is not a
   race and waiting does not fix it: `[skip ci]` is deliberate (ticket 104's lane), so the next
   measurement of main is the next scheduled run, which records a new line and moves the goalposts
   again.
2. **It makes a real red indistinguishable from this one.** A reader comparing a branch run's
   `fail=` with main's recorded `fail=` will find a difference on every branch, and will learn to
   discount it — which is how a genuine regression gets waved through.
3. **`verify/a-fall-blocks/` is the check that blocks on a fall.** A check whose own input is
   changed by the commit that records the number it grades is the shape ticket 59 exists to
   refuse, one level up.

## What has to be decided, not just typed

Two candidate fixes, neither chosen here.

1. **The recording commit re-runs the two checks it invalidates**, and records their new grades
   in the same commit. Smallest change to the checks (none), largest change to `truth.yml`, and it
   raises "what if re-running changes something else" — the fixed point may not be reached in one
   step.
2. **The two checks grade the transition ENDING at the run being recorded**, rather than the
   newest line on disk. Then the commit that records the line does not change what they read.
   Larger change to two checks, no change to the clock, and it needs an answer for what they say
   before any line has been recorded.

There may be a third: record the line without committing captures, or commit captures under a path
no check reads. That trades one coupling for a different one and is not obviously better.

## Notes

Charted 2026-09-09. Found by ticket 105's review: ticket 105's own branch gate showed `fail=12`
against main's recorded `fail=10`, and the two extra reds reproduced on plain `origin/main` with no
part of that branch present. Neither red is ticket 105's and neither is fixed there.

## Answer

Resolved 2026-09-09. **Fix 2, delegated (ADR-0025): the two checks grade the transition ENDING AT
THE RUN BEING RECORDED, not the newest line on disk. The clock is not touched.** The fall that had
already happened is acknowledged in `talk/verify-falls.txt`, in that file's own grammar, and
nothing was written into `talk/truth.log`.

### The decision, and why fix 1 was refused

**Fix 1 (the recording commit re-runs the two checks) is unsound, not merely larger.** Measured,
not argued:

1. **`verify/derived-status/` has two fixed points, so the re-run does not converge.** Its verdict
   is a function of its OWN row in `talk/captures/_grades.tsv`: `.scratch/ecosystem/issues/59-*`
   names `verify/derived-status/verify-derived-status.sh` in its Answer and owns it by git, so a
   `FAIL` row derives `regressed` for ticket 59, which fails the check, which writes `FAIL` again.
   `(PASS, PASS)` and `(FAIL, FAIL)` are both stable. Re-running inside the commit picks whichever
   one the first iteration lands on. The ticket suspected this; it is real and it is live — runs
   186 and 192 both carry `verify/derived-status/... FAIL`, and **by construction no later run
   could ever have cleared it.**
2. **It puts minutes of work on the clock's recording path.** `verify-a-fall-blocks.sh` builds
   throwaway git repositories in fourteen states. Ticket 100's review F3 removed network work from
   that path for exactly this reason: a transient failure there kills the day's citable
   observation before it is written.
3. It changes the clock, which fix 2 does not (the ticket's own comparison).

The third candidate — record the line without committing captures — was not taken. It removes the
*capture* coupling and leaves the *log* coupling, which is the one that moves
`verify/a-fall-blocks/`; and a run whose grades are not committed cannot derive a ticket's status
at all, which deletes NORTH-STAR §5's fourth bullet to fix its fifth.

### What the defect actually is, measured

Inside run N's gate, `talk/truth.log`'s newest line is run N-1's, so `verify/a-fall-blocks/` graded
the transition **ending at N-1** — the transition run N-1's own `a fall is a blocking event` step
had already graded and already blocked on. A fall therefore blocked **twice, one run apart**, and
the second block was committed into `talk/captures/_grades.tsv`, where `verify/derived-status/`
reads it as a live regression of ticket 59.

Measured on `origin/main` at `302bf73`, before this branch:

| | says |
| --- | --- |
| `talk/captures/_grades.tsv` (recorded by run 192) | `verify/a-fall-blocks/verify-a-fall-blocks.sh FAIL` |
| the same script, run on the tree that table is committed on | **PASS**, exit 0 |

The committed grade disagrees with the tree it is committed on. That is the whole defect, and it
is why the citable number understates main.

The chain, from the grade tables themselves (`git show <recording commit>:talk/captures/_grades.tsv`):

| run | `a-fall-blocks` | `derived-status` | `handbook` (ticket 34) |
| --- | --- | --- | --- |
| 181 | PASS | SKIP | PASS |
| 184 | PASS | PASS | **FAIL** |
| 186 | **FAIL** | **FAIL** | FAIL |
| 192 | FAIL | FAIL | FAIL |

One real regression (ticket 34's handbook, between runs 181 and 184) became **three** reds one run
later, and `fail` went 10 → 12 with class `meta` 10 → 8 — the two lost meta passes ARE these two
checks. That is the fall the whole estate then blocked on.

### (A) The fall is acknowledged

One line in `talk/verify-falls.txt`, `run=186 | <reason>`, dated 2026-09-09, naming both checks,
the recording commit `6772a7a` and the handbook regression under it, with ticket 108 owning the
coupling and ticket 34 owning the handbook. Red first, on the real log — `talk/truth.log` as
`git show 9517d98:talk/truth.log`, which is exactly what run 192's gate read:

```
$ python3 talk/fall_check.py check --log <main's log at 9517d98> --falls talk/verify-falls.txt
  newest recorded transition: run 184 (2026-09-08T23:26Z) -> run 186 (2026-09-09T08:28Z)
  FALL class-pass: class `meta` fell from 10 passes to 8 and `fail` rose in the same step, ...
  FALL fail: `fail` rose from 10 to 12
exit 1                       # before the entry
exit 0                       # after it, with `accepted by talk/verify-falls.txt: ...` printed
```

**An acknowledgement that accepts everything is worse than none**, so five wrong shapes were run
against the same log and all five still exit 1: `186 the recording commit...` (no `run=`),
`run=186 |` (no reason), `run=185 | ...` (a run the log does not record — 185 was a branch run and
recorded nothing), `run=999 | ...` (no such run), and `run=181 | ...` (a transition that did not
fall). The older fifteen unaccounted falls are still not listed, and the file says so.

### (B) The fix

`talk/fall_check.py`'s `report()` takes **`recording_run`**, the run the process belongs to, and
grades the transition ending at it:

- **empty** — a builder, a review, a throwaway merge onto `origin/main`: the run being recorded is
  the newest line the log carries, and that transition is graded exactly as before. **A fall on the
  record still blocks here.**
- **equal to the newest recorded run** — `truth.yml`'s own step, which runs after the cage has
  appended the line. Identical. **This is NORTH-STAR §5's stop and ticket 108 does not touch it.**
- **naming a run the log does not carry** — the GATE of a clock run. **DEFERRED.** That line does
  not exist and *cannot*: this check's own verdict is one of the counts in it. The transition
  ending at that run is graded by `truth.yml`'s step once the cage records it. The older transition
  is still compared, still printed and still counted — nothing stops looking — and never faulted a
  second time.
- **naming a run the log carries that is not the newest** — a problem, not a shrug: the log moved
  under the run.

`--recording-run` is passed by `verify-a-fall-blocks.sh` from `GITHUB_RUN_NUMBER` and is
deliberately **not** read inside the module: leg 3 lifts `truth.yml`'s own step shell and runs it
over planted logs whose runs are named `fixture-N`, and an implicitly inherited run number would
have deferred all fourteen of those states the moment the script ran in CI.

`verify/derived-status/derived_status.py` gains one rule: **this check's own grade row is not
evidence about the ticket that built it** (`THIS_CHECK`). It is counted and printed instead. That
is the latch in item 1 above, and it is ticket 108's shape one level up — a check whose output is
its own input. **Nothing is less safe**: the FAIL still reds the gate by its own exit status on the
same day; every OTHER check the ticket owns still derives its status (test:
`test_any_other_red_check_the_ticket_owns_still_derives_regressed`); and a ticket left with only
this row derives `resolved-ungraded`, never `resolved`, so the row is not evidence *for* it either.

### The proof that the loop closes

A recording commit simulated the way `truth.yml` makes one — append the run's TRUTH line, `git
commit -m "truth: record run 102 [skip ci]"`, hooks path emptied — over a throwaway repository, in
both a falling and a flat mode:

| reader | before the commit | after the commit (a real fall) |
| --- | --- | --- |
| the gate of run 102 (`--recording-run 102`) | **DEFERRED, exit 0** | — |
| `truth.yml`'s stop step (`--recording-run 102`, post-cage) | — | **exit 1, THE FALL BLOCKS** |
| any later reader of the record (no run in flight) | — | **exit 1**, same two FALL lines |
| the NEXT run's gate (`--recording-run 104`) | — | **exit 0**, counted: `fall, already graded by the run that recorded it` |

The same fixture under `origin/main`'s `talk/fall_check.py`: the next run's gate **exits 1** — the
stale red this ticket exists to remove. In flat mode every reader exits 0 at every point.

### (C) What is still true and unflattering — as numbers

- **12 of 54** recorded transitions went from green to red at the moment the run recorded its own
  line. `inversions()` computes it and leg 5 prints it on every run. It is not zero and this fix
  does not make it zero: a fall is still graded once by the run that records it and once by every
  later checkout of the record, and `[skip ci]` still means **no run ever measures the tree the
  recording commit made**. Only a clock that re-measures after committing would close that, and
  fix 1 is the unsound way to get there.
- **15 of 54** recorded transitions carry an unaccounted fall older than the one graded. Unchanged
  by this ticket and still not invented.
- This check's own rows are counted rather than derived from, and the instrument prints how many. Quoted verbatim from the run rather than typed, because a typed number drifts (the first draft of this bullet said 3 and the run said 5):
  > `5 are THIS check's own row, which is not evidence about the ticket that built it (ticket 108: a check whose output is its own input latches)`
- `verify/derived-status/` is **still FAIL after this change**, on
  `.scratch/ecosystem/issues/34-...`: `verify/handbook/verify-handbook-is-a-compose-time-render.sh`
  has been red since run 184 and ticket 34 owns it. This ticket does not fix it and does not
  acknowledge it on ticket 34's behalf. On a throwaway merge onto `origin/main` at `46ea3f7` that
  is the **only** fault left; on plain `46ea3f7` there are **two**, the second being ticket 59's
  latch. See `## Record` below.
- **Could not look: no clock run has recorded a grade table under this change yet.** A builder
  cannot make the clock tick, so the claim that the gate will record a deferred PASS rests on the
  script's exit status here and on the simulation above, not on a recorded run. The first
  scheduled run of the default branch after this merges is what settles it.

### Verify commands run, and WHICH TREE each was measured on

A PASS with no tree named is not a measurement (review F3). Three trees: **B** = this branch,
**M** = clean `origin/main` at `c1aee32`, **X** = a throwaway merge of B onto M.

| command | B | M | X |
| --- | --- | --- | --- |
| `verify/a-fall-blocks/verify-a-fall-blocks.sh` | 0 | 0 | 0 |
| `verify/a-fall-blocks/verify-a-fall-blocks.sh selfcheck` (14 fixture states) | 0 | 0 | 0 |
| `verify/derived-status/verify-derived-status.sh` | 1 | 1 | 1 |
| `verify/derived-status/verify-derived-status.sh selfcheck` | 0 | 0 | 0 |
| `verify/can-record/`, `verify/truth-line/`, `verify/every-green/`, `verify/map-surface/` | 0 | — | 0 |
| `verify/cited-truth/` | **1** | 0 | **0** |

**`verify/cited-truth/` is RED on the branch and green on the merge, and that is correct, not a
flake.** `## Record` below quotes run 194, which exists only in `origin/main`'s `talk/truth.log`;
the branch was cut at `302bf73`, before run 194 recorded, so on the branch the citation has no
line — `no-such-line: run 194`. It resolves the moment the branch is merged, which is the tree the
gate actually reads. An earlier draft of this section listed it PASS without saying where, which is
the defect the tree column exists to stop.

`bash talk/verify-all.sh --selfcheck` — 0 (B). `python3 talk/fall_check.py selfcheck`,
`verify/derived-status/derived_status.py selfcheck`, `talk/truth_manifest.py selfcheck` — ok (B).
`talk/truth_manifest.py check talk/verify-manifest.txt` — 0 (B).
`pytest tests/test_fall_check.py tests/test_derived_status.py -n0` — **93 passed** (B).
`mypy twin tests conftest.py` — clean (B).

**A word on the counts, because two different things are being counted.** The wrapper's verdict
line reads `FAIL: 1 fault(s)` and that is one **leg** — the derivation leg — failing. The table in
`## Record` counts **tickets** in disagreement, of which there are two on plain main and one on the
merge. One failing leg can name any number of tickets.

## Waits on the owner

Nothing. Everything here is architecture and is decided under ADR-0025.

## Record

**2026-09-09, later the same day: the stale row cleared itself, as predicted, before this merged.**
While this branch was being built, run 194 recorded (`hub=302bf73`, `pass=79 fail=9`) and its grade
table carries the fall checker as PASS — because run 194's gate graded the transition 186 -> 192,
which is flat. So the one red this ticket left standing on its own check is gone from the newest
table, and the acknowledgement written here earlier in the day has been removed rather than left
in place: an acknowledgement that outlives the red it names is a hatch that would silently accept
the next one. **No path is backticked in this paragraph on purpose.** What remains true, measured
on a throwaway merge of this branch onto `origin/main` at `46ea3f7`:

| | `verify/derived-status/` faults |
| --- | --- |
| plain `origin/main` at `46ea3f7` | **2** — `.scratch/ecosystem/issues/34-...` and `.scratch/ecosystem/issues/59-...` |
| the same tree with this branch merged in | **1** — `.scratch/ecosystem/issues/34-...` only |

Ticket 59's fault on plain main is the latch: run 192's table carries the status checker itself as
FAIL, ticket 59 owns it, and deriving `regressed` from that row fails the check again. It is gone
on the merge because a check's own row is no longer evidence about the ticket that built it.
Ticket 34's remains, is not this ticket's, and keeps the check red.

**2026-09-09, review round 2. THE FIRST PUSH OF THIS BRANCH DISABLED ITS OWN CI, and the cause is
a trap for every ticket in this area.** No run fired: `runs?head_sha=` returned 0, `check-runs`
returned 0, `gh pr checks` said "no checks reported" — even though `truth.yml`'s `paths:` carries
`verify/**`, `talk/fall_check.py`, `talk/verify-falls.txt` and `talk/verify-manifest.txt`, all
changed, and `twin.yml`'s carries `tests/**`, also changed. My first diagnosis — that a
branch-CREATION push does not evaluate path filters — is **wrong**, and two controls refute it:

- `e6075bf` on `ticket-81-record-round-3-landed` was a single branch-creation push and fired
  **truth 187 AND twin 247**. So branch creation is not the cause.
- `ebe89f7` on `ticket-105-pinned-trust-roots` was a push to an EXISTING branch that already had
  runs; it touched `verify/**`, `tests/**` and the manifest and got **0 runs**. So an existing
  branch is not a cure.

The one property the two unmeasured commits share is the literal skip-ci marker **in the commit
message body** — mine on line 3, `ebe89f7`'s on line 33 — where each was *describing* the clock's
recording commit. GitHub honours a skip directive anywhere in the head commit's message, not only
on the subject line. **So a ticket about the recording commit silently disables its own CI by
quoting the marker it is about, and this has already merged unmeasured once: PR 65, ticket 105.**

**The convention, for anyone writing about this mechanism.** In a non-clock commit message, write
it `[skip-ci]` or say "the skip-ci marker" in prose. Never the literal two-word form, anywhere in
subject or body. Files may contain it freely — `talk/verify-falls.txt` and this ticket both do —
because GitHub reads the commit message, not the diff.

**The control ran on this branch.** Re-pushed at head `5f1fd47` under a message carrying no literal
marker and otherwise describing the same mechanism at the same length, `runs?head_sha=5f1fd47`
immediately returned **three** runs where the previous head returned none: `truth` 34357816071,
`twin` 34357816064 (push) and `twin` 34357822393 (pull_request). The `truth` run was `pending`
rather than started, because `truth.yml`'s concurrency group is `truth-${{ github.event_name }}`
with `cancel-in-progress: false` and main's own run was in flight — queued is a run, and zero is
not. Nothing else about the push changed: same branch, same paths, same files.

**2026-09-09, two residuals recorded rather than fixed.**

**F6 — re-running an older truth run is now red where it used to be green.** A re-run carries the
original `GITHUB_RUN_NUMBER`, so `--recording-run` names a run the log already carries and is no
longer its newest line: `the log moved under this run`, exit 1. That is the honest answer — neither
reading is that run's — but it is a behaviour change, and that run's cage would commit the FAIL as
this check's grade row, so a re-run for an unrelated reason now leaves a red row behind. The
problem string says `RE-RUN` in as many words so the next reader is not left guessing.

**F8 — `truth.yml`'s stop step is identical to the new semantics only conditionally.** It grades
the same transition as a later reader only while the cage actually appended this run's line. If
`CAN_RECORD=yes` but the cage short-circuits on `git diff --cached --quiet` — nothing staged to
commit — the step grades the PREVIOUS run's transition, and the two readings are not
unconditionally the same. Not fixed here: fixing it means changing the clock, which is what fix 2
was chosen to avoid. Recorded in `talk/fall_check.py`'s docstring as well.

**F7 — the hatch's key is not globally unique.** `run=N` is `GITHUB_RUN_NUMBER`; a re-run reuses
it and a deleted-and-recreated workflow restarts at 1. Today every number in `talk/truth.log` is
distinct and increasing, which is checkable and checked. Recorded in `talk/verify-falls.txt`'s
own header.

**F4 and F5, hardened in code rather than described.** `THIS_CHECK` is derived from the module's
own location and asserted to exist at import — as a literal it was unpinned and every reference,
both selfchecks and all five tests, was written in terms of the constant, so a plant that renamed
the wrapper brought the latch back with nothing red. The defer key is validated as digits and
compared by value: `--recording-run abc` used to defer and exit 0, and `0200` deferred where `200`
graded. Both are now FAULTS, never defers, because deferring means not grading and an escape hatch
keyed on an unchecked string is the shape this ticket exists to refuse. And DEFERRED reaches
further than the first draft said: every branch and pull-request CI run sets `GITHUB_RUN_NUMBER`,
so leg 5 defers there too, where it used to redden on the default branch's newest unaccounted
fall. That is right and blocks nothing — a branch records no line — and it is now said in the
wrapper header and the manifest row.
