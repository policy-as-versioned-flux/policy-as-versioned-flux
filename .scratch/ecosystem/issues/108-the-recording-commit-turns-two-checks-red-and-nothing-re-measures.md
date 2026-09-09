# 108 — The commit that records the number turns two checks red, and `[skip ci]` means nothing re-measures

Type: task (AFK)
Status: open
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
