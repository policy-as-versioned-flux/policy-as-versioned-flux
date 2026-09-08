# 59 — Build the two unbuilt §5 bullets: a fall blocks, Status is derived

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

(a) truth.yml diffs the new TRUTH line against the previous one and raises a distinct, unmissable failure on any fall in pass or rise in fail — including a pass-to-skip degradation with zero fails — with a committed-reason escape hatch mirroring the exclusions-file pattern; decide in the ticket what it blocks (release dispatch is the natural candidate). (b) Build the checker GAPS 2.9 already specifies: map each resolved ecosystem ticket to its named gate check and flag Status from the scheduled run, as the twin harness already does for its own tracker; normalise the 16 free-typed 'Status: open' lines to the issue-tracker vocabulary. Done = both mechanisms run in the gate and a synthetic fall demonstrably fires.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M14 (fall-is-blocking and derived-Status, 2 confirmed findings), minor pass-to-skip-goes-green.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Still unbuilt. Run 17 to 18 fell from 59 pass to 57 and nothing fired; 17 of 21 truth runs fail at the same step so the signal is saturated. Ticket 83 puts a class manifest and a published ceiling on the TRUTH line; build the fall-checker over that manifest so a fall is compared class by class. Record: REVIEW-2026-09-02.md R3, truth-surface/TS-M4.

**2026-09-04, ticket 83.** The contract to build against is written and committed: the module
docstring of `talk/truth_manifest.py`, section **CONTRACT FOR TICKET 59 (the fall-checker)** —
read it there, it is the only copy, and ticket 83's Answer only summarises it. In short: read two
consecutive TRUTH lines with `parse_truth()` and compare class by class; a FALL is any class's
pass count falling, `fail` rising, `ceiling` falling with no manifest change in the same commit,
or `total` falling with no exclusions change — and a pass that became a skip *inside one class* is
a fall even when `fail` is unchanged. The escape hatch is a committed `talk/verify-falls.txt` of
`run=N | reason` lines, validated the way `talk/verify-exclusions.txt` is. Read classes through
`load_manifest()`; never re-derive one from a script header at check time. `truth_manifest.py`
implements `parse_truth()` and deliberately none of the comparison.

Two things ticket 83 learned that this checker inherits. **`ceiling` moves for two different
reasons** and only one is a fall: a script re-classed `never` lowers it (manifest change, same
commit — not a fall), and an exclusion lowers `total` as well (exclusions change — not a fall);
compare against the diff, not the numbers alone. **There are two `never` counts**: the skip
split's, which counts only the never-classed scripts that skipped, and the ceiling's population,
`total - excluded - ceiling`. Use the second wherever the question is "how many can never pass".
Runs 65 and 70 are a usable pair to build against: `pass=59 [observed=13 self=37 simulated=6
meta=3] ... ceiling=77` then `pass=61 [observed=13 self=37 simulated=6 meta=5] ... ceiling=80`.
The two extra passes are both `meta` and both real: `verify/truth-line/verify-truth-line.sh` is
new on run 70, and `verify/demo/verify-demo.sh` turned green when ticket 90 regenerated the deck.
No class fell between the two, which is what a fall-checker should say about that pair.

## Answer

Built 2026-09-06. Both §5 bullets existed only as sentences; neither was rebuilt, because neither
had ever been built. The two bullets, quoted from NORTH-STAR §5:

> - Ticket `Status:` is derived from a named check, in the way `twin grade` already derives depth
>   from `twin/capabilities/*.yaml`.
> - The number and its date are recorded on every run. A fall is a blocking event.

The first half of the second bullet has been true since GAPS 2.1. Everything else here is new.

### (a) A fall is a blocking event

`talk/fall_check.py` is the comparison and only the comparison, implementing the CONTRACT FOR
TICKET 59 written into `talk/truth_manifest.py`'s module docstring by ticket 83. It reads two
consecutive TRUTH lines through `parse_truth()` and compares class by class: a class's pass count
falling is a fall (and when `fail` did not move in the same step the message says a pass became a
could-not-look, which is the pass-to-skip degradation that used to go green); `fail` rising is a
fall; `ceiling` falling is a fall only when `talk/verify-manifest.txt` did not change between the
two commits the lines name; `total` falling is a fall only when `talk/verify-exclusions.txt` did
not. Lines predating the manifest carry no split, so those fall back to the bare count and say so.
A diff this checkout cannot read is reported as a fall, naming that it could not be read.

The escape hatch is a committed `talk/verify-falls.txt` of `run=N | reason` lines, validated the
way `talk/verify-exclusions.txt` is: a malformed line, a line with no reason, and a line naming a
run `talk/truth.log` does not record are each faults.

**What it blocks, and where the stop is enforced.** The served artefact is the `truth` workflow's
own run conclusion, which NORTH-STAR §5 makes the only source any document may cite for what
works. The operation is `.github/workflows/truth.yml`, job `gate`, a new step named
`a fall is a blocking event` that runs AFTER the observation cage — so the line is recorded
whatever it says, because a clock appends observations (ADR-0024) and a clock that hid a fall
would be worse than one that reported it — and exits 1 with its own `::error::` and its own step
summary line. It is deliberately distinct from `fail if the gate failed`: the 2026-09-02 comment
on this ticket is right that the gate's own red is saturated, and a fall inside a red gate was
invisible. On a branch the comparison is printed and blocks nothing, because a branch records no
line (ticket 100), so the newest transition in the log is the default branch's and not that run's.

Release dispatch was the ticket's suggested candidate and is NOT what it blocks. Measured: this
repository has two workflows, `truth` and `twin`, and neither is triggered by another workflow
finishing; every release workflow in this estate lives in one of the eight independently
versioned unit repositories. Gating a unit's release on the hub's number would make that unit
hostage to this repository's record, which NORTH-STAR §2 says the platform must never be. So the
stop is this repository's own citable conclusion, and
`verify/a-fall-blocks/verify-a-fall-blocks.sh` PRINTS, on every run, how many workflows here key
off another workflow finishing (0 of 2 on 2026-09-06), so the day one is added the scope of the
stop changes visibly instead of a disclosed limit going quietly stale.

**How the stop is proved.** `verify/a-fall-blocks/verify-a-fall-blocks.sh` lifts that step's own
shell verbatim out of `truth.yml` through `verify/can-record/can_record.py step` — the same
extractor ticket 100 uses — and runs it over throwaway git repositories in fourteen states,
counted by the fixture as it runs them and printed in its PASS line, each graded by what the step
DOES (its exit status, whether it printed `::error::`, what it wrote to the step summary): nothing
moved; a class lost a pass; `fail` rose; a pass became a could-not-look with `fail` unchanged; the
ceiling fell with a manifest commit in the span, without one, and with a comment-only touch; the
total fell with an exclusions commit, without one, and with a comment-only touch; a re-class of a
passing script; a fall with a committed reason; a falls file naming a run the log does not record;
and a fall on a branch. The ceiling states and the total states differ ONLY in what the second
commit touched, so the diff rule is measured rather than described. Nothing is inferred from the
YAML looking right.

### (b) Status is derived from a named check

The blocker, found while building and worth recording: **there was nothing to derive from.** The
TRUTH line carries the counts; nothing carried the grade of each named script. The captures are
not a substitute — `talk/verify-all.sh` grades a script by its EXIT CODE and a capture's last
line is only the reason, and 29 of the 107 captures committed on 2026-09-06 end in the
continuation of a multi-line `PASS:` sentence. A prototype that read grades out of capture text
named two tickets regressed that were green. So `talk/verify-all.sh` now writes
`talk/captures/_grades.tsv`, one row per discovered script (`path`, `STATUS`, the capture's last
line), opening with that run's own TRUTH line, inside `talk/captures` — which is already in the
observation lane the cage commits, so no change to `OBSERVATION_LANE` or to
`verify/schedules/schedules.py`'s allow-list was needed. `.tsv`, so no `*.out` glob picks it up.

`verify/derived-status/derived_status.py` derives from that file and refuses it unless the TRUTH
line it opens with is the newest one `talk/truth.log` records. For each ticket written
`resolved`, the checks named in its `## Answer` section — and nowhere else, because a check named
in the Question is what the ticket was asked for — are looked up: any FAIL derives `regressed`,
otherwise a PASS derives `resolved`, only could-not-looks derive `resolved-unobserved`, and no
check the table carries derives `resolved-ungraded`. A ticket written `resolved` that derives
`regressed` is a fault unless a DATED paragraph in the file names that red check. Three things
deliberately do not dispose of it, each with a test: the Answer's own words (every Answer names
its own check, so that would let every ticket dispose of its own red — the shape ticket 80 was
defeated by this morning), a dated paragraph naming a different check, and an undated paragraph
naming the right one.

`verify/derived-status/verify-derived-status.sh` runs the record half FIRST, so a fault there is
a FAIL on any day, and only then the derivation, which exits 3 `waits:` until a run has recorded
a grade table. The could-not-look therefore can never hide a fault in the record.

The normalisation the ticket asks for is done, on the eight lines that were free-typed by
2026-09-06 (the review of 2026-08-31 counted sixteen free-typed `Status: open` lines; those had
already been normalised, and what remained was seven `resolved (…)` parentheticals plus one
`closed (…)`). Each ticket keeps its qualification verbatim in a dated Status note in its own
body. Command and output are in the report.

### Decisions

1. **What a fall blocks: this repository's own citable run conclusion, not a release.**
   `delegated` (ADR-0025). Reason above: no unit may be made hostage to the hub's number
   (NORTH-STAR §2), and the hub has no release dispatch to block. The reach is printed as a live
   number rather than asserted.
2. **The stop runs after the cage, not before it.** `delegated`. A clock appends observations
   (ADR-0024); a fall that stopped the recording would destroy the evidence of itself.
3. **Only the NEWEST transition is graded; older ones are counted.** `delegated`.
   `talk/truth.log` is append-only and ticket 100's check refuses a hand-edited line, so a fall
   between two 2026-08-31 runs has no finishing move, and a red with no finishing move is the
   shape ticket 55 rules out. Thirteen of the log's forty-two transitions carried an unaccounted
   fall on 2026-09-06; the number is printed on every run.
4. **`talk/verify-falls.txt` ships empty.** `delegated`. No reason for any of the thirteen
   historical falls was written down at the time, and inventing thirteen now would be the estate
   telling itself a story. The file carries its format and that decision, and nothing else.
5. **The grade table goes in `talk/captures/`, not a new lane path.** `delegated`. The lane is
   declared in `truth.yml` and mirrored in `verify/schedules/schedules.py`'s `ALLOW_LIST`;
   widening it is ADR-0024's business, and `talk/captures` already holds exactly this run's
   per-script output.
6. **`closed` needs a dated paragraph, not an `## Answer`.** `delegated`. `closed` means taken
   out of scope (ticket 90's shape), so there is nothing to answer; demanding an Answer would
   have made the record write a fake one. Ticket 68's 2026-09-02 closure line is the shape.
7. **Neither new script declares a could-not-look for its own instruments.** `delegated`,
   following the calls tickets 100 and 80 recorded for their own checks. Everything they read is in this
   repository and everything they run is git and python, so a missing interpreter is RED, not a
   shrug. The derived-status wrapper does declare a `waits:` — but for the ESTATE's state (no
   grade table recorded yet), which is what `waits:` means.
8. **A resolved ticket naming no gate check is counted, never failed.** `delegated`. Research,
   grilling and org-setup tickets exist and no gate check can grade a reading list; failing them
   would push the record towards naming a check it does not own. The count is printed.

### What this ticket did not do, and what comes next

`verify/derived-status/verify-derived-status.sh` will SKIP until the first scheduled run of the
default branch records a grade table. Dry-run against an approximate table built locally from
capture text on 2026-09-06 (an approximation, not an observation — it is exactly the proxy the
real table replaces), the derivation named eleven tickets written `resolved` whose named check
graded FAIL: 38, 56, 57, 62, 72, 73, 77, 80, 85, 89 and 99. That is M14's finding arriving rather
than a new defect, and the finishing move per ticket is one dated line naming the red check and
what owns it. Those lines were deliberately NOT written here: written against an approximation
they could each be false, and a check whose green came from prose its own builder wrote to satisfy
it is the failure this ticket was told to avoid.

Map line: - [59 — Build the two unbuilt §5 bullets](issues/59-build-the-two-unbuilt-5-bullets-a-fall-blocks-status-is.md) — a fall in the citable number now blocks: `talk/fall_check.py` compares two consecutive TRUTH lines class by class against the diff of the commits they name, `talk/verify-falls.txt` is the committed-reason escape, and a step of its own in `truth.yml` — after the cage, so the line is still recorded — turns the run red with its own `::error::`, proved by lifting that step's shell verbatim and running it over throwaway repositories in fourteen states; what it blocks is this repository's citable run conclusion and not any unit's release, because no unit may be hostage to the hub's number, and the reach is printed as a number (0 of 2 workflows). Status became derivable only once the run recorded WHAT IT GRADED: `talk/verify-all.sh` now writes `talk/captures/_grades.tsv` inside the observation lane, and `verify/derived-status/` derives each resolved ticket's status from the checks its Answer names, refusing a table that is not the newest run's and refusing a red disposed of by the Answer's own words; the eight free-typed Status lines are normalised to the tracker's vocabulary with their qualifications kept verbatim in the body. Reviewed 2026-09-06: the step runs under the runner's `bash -e {0}`, which killed it at `out=$(...)` before it printed anything, so the fall path had never executed — the step, `can_record.py`'s new `step_shell_flags()` and the fixture now share one answer to "what will the runner run this under", and the fixture's fourteen states run under it, counted by the fixture and printed in its PASS line. Ownership of a check is read from git rather than from an Answer's prose, which took the first derivation's twelve named tickets down to the seven genuinely resolved-but-red on a check they own (38, 56, 62, 77, 85, 89, 99), each now carrying a dated follow-up; the rest were discussing somebody else's red. Re-reviewed the same day: the ticket-number scan could not read the estate's own plural commit subjects (`Tickets 62 and 77: ...` added verify-branch-refs.sh), so it had reported four of those seven as not owning the check they built — it now imports ticket 102's `ticket_numbers`; `shared_contract()` pins the behaviours it depends on. Round 3 (2026-09-08), measured on a rebase onto today's main against run 179's table: the derivation named an eighth resolved ticket, 101, which git owns for ticket 99's unreviewed-major check only through ticket 99's "ticket 101 is charted" subject -- the accepted over-attribution, loud by design -- and 101 now carries its dated follow-up, so the derivation is clean: 86 resolved, 22 green, 8 regressed all acknowledged, 3 unobserved, 53 ungraded.

## Review round, 2026-09-06

Six findings. One was blocking and it is the one worth reading.

**F1 — the fixture's shell was not the runner's, so the fall path had never run.** The step
declares no `shell:`, so Actions executes it as `/usr/bin/bash -e {0}`. `set -uo pipefail` does
not clear `-e` — `set -o` adds a flag, it never removes one — and `out="$(python3 …)"; rc=$?` is a
bare assignment, so on any non-zero exit the shell died at that line: nothing printed, nothing in
the step summary, no `::error::`, and the `CAN_RECORD` guard never reached, which would also have
blocked a BRANCH run on the default branch's newest fall. Reproduced in one line:
`bash -e -c 'set -uo pipefail; out="$(exit 1)"; rc=$?; echo reached'` prints nothing and exits 1.
The fixture had passed only because it ran the lifted shell under a plain `bash`. Run 135's green
was the no-fall path; the fall path had never executed anywhere but under the wrong shell.

Fixed in three places, because fixing one would let it come back. The step now uses
`rc=0; out="$(…)" || rc=$?`. `verify/can-record/can_record.py` gained `step_shell_flags()`, which
reads a step's effective interpreter out of the workflow (`-e` where nothing is declared, none
where the step opts out, whatever a custom `shell:` says) and a `stepshell` subcommand; the `step`
extractor now prints the flags as a note, so a fixture that ignores them is ignoring something it
was told. And `verify/a-fall-blocks/verify-a-fall-blocks.sh` runs the lifted shell under exactly
those flags. Red-first, with the old step restored under the new fixture: **14 faults** — all six
blocking states `rc=1 blocked=no` with no summary line, plus `fall-on-a-branch rc=1` where this
ticket decided 0.

**F2 — the acknowledgement rule was thinner than the Answer claimed.** It treated only the first
paragraph naming the check as the claim, searched the whole file, and matched the path as a bare
substring. So a second dated paragraph inside the same Answer, a `## Comments` note that PREDATES
the Answer, a URL or a plain mention could all dispose of a red. An acknowledgement is now a
paragraph that starts after the `## Answer` section ends, carries a dated bolded lead-in, and
names the check in backticks by the same prefix rule the grade table is read with — so a
directory acknowledgement works, which it did not before. Four adversarial tests.

**F3 — `compare()` reported a cause it could not see.** It said "a pass became a could-not-look"
whenever `fail` had not risen, which is false for the most ordinary movement there is: a re-class
moves a PASSING script between classes, one class falls, another rises, the total is unchanged and
nothing stopped looking. The cause is now read — passes moved between classes / became reds /
became could-not-looks / left the surface altogether — and the no-split message names WHICH line
lacks the split rather than saying "neither". A re-class of a passing script is still a fall by
the contract and still needs a line in `talk/verify-falls.txt`; the message now says so.

**F4 — the lag, the local table, and the day-one collision.** `verify-all.sh` writes the grade
table after its loop, so at run N the derivation reads run N−1's table against a log whose newest
line is also run N−1's: one clock tick behind and always self-consistent. Stated in the script,
the module and the manifest row rather than left to be found. A table written by `run=local` or a
`fixture=1` selfcheck is now a could-not-look, not a failure, so a local gate run is not reddened
for having been run. The collision itself is answered below.

**F5.** A reason may now contain `#` (only a whole-line comment is a comment); a committed reason
for a transition that did not fall is a fault rather than silently accepted; and the ceiling and
total excuses are granted on the record files' MEANING, not their names — a comment-only touch to
`talk/verify-manifest.txt` or `talk/verify-exclusions.txt` no longer excuses any drop, which is
two more fixture states. `truth.yml`'s push `paths:` filter gained the four `talk/` files the
gate's own arithmetic lives in. Found while fixing it: `git rev-parse --verify` takes exactly one
parameter and exits 128 on two, so the first version of the material-change lookup called every
span unreadable and turned both excused states into falls — caught by the fixture the moment it
landed, which is what the fixture is for.

**F6 — charted as [ticket 104](104-a-branch-push-cancels-main-s-own-recording-run.md).** The
concurrency hazard is worse than this build first found. `truth-${{ github.event_name }}` is one
lane for every push on every branch, so branch pushes cancel `main` push runs, which CAN record:
8 of the newest 22 `main` push runs were cancelled and none of those eight run numbers is in
`talk/truth.log`. Ticket 56's per-event group protected the scheduled lane; ticket 100 then made
branch runs pure measurement that still occupies main's lane.

### The day-one collision, and what it cost the record

The first derivation was going to flip SKIP → FAIL with twelve findings, raising `fail` 11 → 12
and firing the fall stop. Against run 135's REAL grade table — read out of that run's own gate log,
113 rows summing exactly to its `pass=72 fail=11 skip=22 excluded=8 total=113` — the twelve were:
38, 56, 57, 62, 72, 73, 77, 80, 83, 85, 89, 99. **Nine of them were discussing somebody else's
check**: ticket 80 quoting 89's check while correcting the record, ticket 83 citing driftwood's
sweep script as an example of a manifest class, four tickets mentioning `verify-schedules.sh`
where ticket 57's own Answer says in as many words that "ticket 56 owns" the reason it is red.
Writing an acknowledgement into each would have put nine false ownership statements into the
record — which is exactly what refusing to write eleven against the earlier approximate table
avoided, one round earlier.

So ownership is now read from git, not from prose: a check is owned by the tickets whose commits
touched its file, looked up in the unit's own repository for a `.estate-clone/` path. The
narrowing kept three tickets while the ticket-number scan was singular, and SEVEN once the
re-review found that scan wrong (R2-1, below). Each kept ticket now carries a dated
`## Follow-up` naming its red check, quoting run 135's exact verdict line, saying it is not
citable, and saying what git names as owning it. With those written the derivation is clean, so
the first table to land will PASS rather than raise `fail` — the collision is answered by
narrowing and by true sentences, not by twelve invented ones.

### Re-review round 2, 2026-09-06

**R2-1, blocking, and it made the narrowing itself wrong.** The ticket-number scan was
`\bticket\s+(\d{1,4})\b`, which reads NOTHING from the estate's own plural commit subjects.
`Tickets 62 and 77: no branch refs, and pins are checked for content` is the commit that added
`verify/branch-refs/verify-branch-refs.sh`; `Tickets 56 and 85: the clocks are read, graded and
named` added `verify/schedules/verify-schedules.sh`. So branch-refs came back UNOWNABLE, schedules
lost two of its four owners, and the derivation printed "the red check(s) it names are not its
own" for tickets 56, 62, 77 and 85 on every run — four false ownership statements, which is the
exact defect decision 12 exists to prevent. Round 1's "exactly three" and "2 unownable" rested on
it and were wrong; they are corrected here, in the manifest row and in the wrapper's header.

Reading every number in a `[Tt]ickets? N(, N)*( and N)?` list, the corrected picture against run
135's real grade table is:

| | tickets |
| --- | --- |
| resolved, and red on a check they OWN | **38, 56, 62, 77, 85, 89, 99** (seven) |
| naming a red check they own none of | 57, 72, 73, 80, 83 (seven red rows) |
| red and unownable | none (was two, both an artefact of the singular scan) |

All seven now carry a dated `## Follow-up`. The four new ones are as real as the first three: 56
and 85 name `verify/schedules/verify-schedules.sh` and its verdict `FAIL: 3 schedule/cage check(s)
observed false: insurer/fetch.yml ludlow tuppence`, which is the estate state ticket 85's own
Status note already describes as waiting on three unit merges; 62 and 77 name
`verify/branch-refs/verify-branch-refs.sh` and its verdict about the insurer's `release.yml`
checking out the platform with no `ref:`, which both tickets' own Status notes already record as
waiting on the owner. That was measured against run 135's table on 2026-09-06. **Measured again
on 2026-09-08 against run 179's table (review round 3, below), on this branch rebased onto
`origin/main` at `0af3a38`: the derivation named an EIGHTH ticket, 101, and only after 101's own
dated follow-up is the derivation clean** — 86 tickets written `resolved`, 22 derive resolved
from a check that passed, 8 derive regressed and all 8 are acknowledged, 3 rest on could-not-looks,
53 name no check the table carries; 7 red rows are another ticket's and 0 are unownable. The
first recorded grade table PASSES this check only on a tree that carries those eight follow-ups;
on `main` before this merges it does not, and the sentence this replaces said otherwise.

**Ranges are deliberately not read.** `tickets 54-67 chart the remediation` and its two siblings
are review-and-charting commits; measured over the whole hub log on 2026-09-06, no commit that
TOUCHES a verify script spells a range at all, so reading one would add a guess and attribute
nothing real. Ticket 102 does not read them either.

**R2-2, and it resolved itself mid-round.** Ticket 102 owns "which ticket does a commit subject
name" and defines `ticket_numbers()` in `verify/cited-truth/cited_truth.py`. When this round
started that work was on an unmerged pull request, so the function was imported when present and
mirrored when not, with the two asserted to agree. Pull request 51 then merged (`a6b823a`), and
the mirror is **deleted**: this module imports `ticket_numbers` and there is no second copy of the
regex anywhere. The agreement guard is replaced by something better — `shared_contract()` declares
executably which of that function's behaviours this check is built on, and a change over there
now fails this check by name instead of moving its verdicts in silence. The one disagreement the
guard did catch before the mirror went is worth recording, because it is what the guard is for:
the mirror read `tickets 54-67 chart the remediation` as `{54}` and ticket 102's final function
reads it as `{}`.

**Two behaviours of the shared function this check is built on**, written down because it is now
load-bearing for two checks:

*Ranges are not expanded, and are read conservatively rather than wrongly.* `tickets 09-16` reads
as nothing at all — the `(?!-\d)` lookahead refuses the whole range — and `tickets 88 to 95
graduated`, which is ticket 75's real subject, reads as `{75, 88}` because `to` is not a list
separator. **No range expansion is added here, and the measurement says why**: over the whole hub
log on 2026-09-06, thirteen subjects use a range or a `to` form and **none of them touches any of
the 40 hub verify scripts**. They are review, charting and worktree-sync commits
(`Ambition review: … tickets 54-67 chart the remediation`, `Sync worktree to main (tickets
01-44, 60, 62)`, and so on). If one ever does, this check will under-attribute rather than
mis-attribute, which is the direction that cannot write a false ownership statement.

*A bare number after a list separator is collected.* `Ticket 80 and 3 fixes` reads as `{3, 80}`.
Mildly over-inclusive here — it could hand a check to a ticket that never touched it, turning a
red into somebody else's regression. Accepted rather than worked around, because the alternative
is a second reading of the same vocabulary and this round has just finished deleting one; and
because the failure it would cause is loud, a ticket named for a check it plainly does not own,
in a finding a reader sees. No subject of that shape exists in the hub log today.

*A "charted" or "review" mention in a subject is read as ownership, and that is accepted.*
`721fd3b Review fixes: the resolver whitelists flags, and ticket 101 is charted` is a ticket 99
commit that touched ticket 99's unreviewed-major check (named, in backticks, in ticket 101's
Follow-up and not here: an Answer names the checks its ticket built); `git log --full-history`
therefore names 99 AND 101 for that script, and 101's own commits never touched it. So ticket 101 is asked to answer for a red it did not build. This is the same over-inclusion
as the bare number, accepted for the same reason (decision 12): the alternative is a second
reading of commit subjects that guesses what "charted" means, and the failure is loud — a named
ticket, a dated paragraph a reader sees — never a silent green. Found on 2026-09-08 (round 3) on
the first real table after ticket 101 resolved; 101's follow-up says exactly this.

**R2-3, the honest limit of the runner evidence.** Run 142's `verify/a-fall-blocks/...sh PASS` row
proves that **the fixture executed under the runner's own python, git and bash — including the
`bash -e` the lifted step runs under — and that every one of its fourteen states behaved as
decided**, because the script exits 1 if any state disagrees. It is NOT fourteen per-state lines
read off the runner: `talk/verify-all.sh` writes each script's output to
`talk/captures/<slug>.out`, and a branch run commits nothing (ticket 100), so that capture exists
only on the runner's disk. The per-state lines quoted in this ticket are from the identical script
run locally. The first scheduled run on the default branch commits the capture, and from that day
the fourteen lines are in the record.

### Further decisions

12. **Ownership of a check is read from git, never from the Answer's prose.** `delegated`. The
    served artefact is the check script and the operation that reaches it is a commit; `git log
    --full-history -- <path>` names every commit that touched it whatever merges intervened — and
    reading the estate's plural subjects is part of the rule, not a detail (R2-1). A red check a
    ticket does not own is COUNTED (7 red rows on run 135). A check no commit ties to any ticket
    is UNOWNABLE and also counted (0, once the plural subjects are read): inferring an owner from
    silence is how a false ownership statement gets written. The subjects are read by ticket
    102's `ticket_numbers`, imported from `verify/cited-truth/cited_truth.py` — one reading for
    the estate, no fork — and `shared_contract()` pins the behaviours of it this check depends on,
    ranges included.
    **This module reads every TOUCHING commit; ticket 102 reads the ADDING commit** (R2-2), and
    both are right for their own question. 102 asks who ADDED a check, so a ticket cannot claim
    proof from a tree that predates it — one commit, the first. This asks who is ANSWERABLE for a
    check being red today, and a check is maintained by more tickets than the one that created it:
    `verify/schedules/verify-schedules.sh` was added by 56 and 85 and has since been touched by 28
    and 70, and all four should hear that it is red. Same vocabulary, different span; the
    vocabulary is shared, not forked. **A subject that merely CHARTS or REVIEWS a ticket is read
    as naming it** (round 3, 2026-09-08): an over-attribution, accepted because it is loud.
13. **The step's effective shell is resolved in one place, `can_record.py`.** `delegated`. Two
    copies of "what will the runner run this under" is how the fixture and the workflow diverged
    in the first place.
14. **A `run=local` or `fixture=1` grade table is a could-not-look, not a fault.** `delegated`. It
    can never be the newest recorded run, and failing on it would redden a local gate run for the
    crime of having been run.

### Found while rebasing, reported, and fixed by its owner

`verify/cited-truth/verify-cited-truth.sh` was RED on `origin/main` at `e5bca74` for about an
hour, from pull request 47 (ticket 92 round 6):

    .scratch/ecosystem/issues/92-the-local-clock.md:245: no-such-line: run 131 is quoted with
    pass=71 fail=11 skip=21 excluded=8 total=111 ceiling=92, and talk/truth.log records no such line

Run 131 was a BRANCH run, so ticket 100's guard correctly stopped it recording and the line it
measured is only in the Actions log. This branch's copy of that file was byte-identical to main's,
so the red was inherited and not caused here; it was reported rather than fixed in passing, since
another builder's record is not this ticket's to edit. Ticket 92's own follow-up (pull request 55,
`a38a912`) has since fixed it, and `verify-cited-truth.sh` is green again on this branch. Recorded
because "a red appeared and then went away" is exactly the kind of thing the truth surface exists
to stop being invisible.

## Review round 3, 2026-09-08

Three findings, one blocking, all on a throwaway merge onto the current `origin/main`.

**F1 — the derivation FAILED on today's main.** Against run 179's table (118 rows, the newest
line in `talk/truth.log`) the derivation named ticket 101, resolved and merged as PR 53 after
round 2: its Answer names `verify/unreviewed-major/verify-unreviewed-major-in-window.sh`, that
check is FAIL on run 179, and git names {99, 101} for it — 101 only via ticket 99's "ticket 101
is charted" subject. 101's Answer already said the red is the owner's carried-major reason, but
not in the acknowledgement shape, so `acknowledges()` returned nothing and the merge would have
raised `fail` 10 → 11 and fired the fall stop: the exact collision this ticket exists to avoid,
and the sentence above that claimed the first table "makes this check PASS" was false on today's
main. Fixed by this ticket's own rule — a dated `## Follow-up` in 101 after its Answer, quoting
run 179's verdict and saying what git names and why — plus the corrected sentence, and the
"charted" over-attribution written down above. Re-measured on the rebased tree: clean, figures
above.

**F2 — the fixture ran FOURTEEN states and said fifteen** (its header said ten, its F1 comment
eleven, the manifest row and map line eleven). The fixture now counts `grade_case` calls and
prints the count in its PASS line; every prose copy says fourteen.

**F3 — the map line described a mirror deleted in R2-2.** Replaced, and this ticket's `Map line:`
is byte-identical to map.md's.

The rebase itself (onto `0af3a38`) conflicted only in map.md's "Decisions so far", where main had
added ticket 45's line; all three lines are kept. Also measured on the rebased tree because
another builder found it red on bare main: the RECORD leg (`derived_status.py record`) is green
— 106 tickets, `closed=1 open=18 prepared=1 resolved=86`, no free-typed Status — because this
branch carries the normalised lines for 77 and 85 and main has not touched either file since;
on main alone, until this merges, those two lines are still free-typed and that leg is red.

## Waits on the owner

Nothing. The grade table and the first derivation arrive on the first scheduled run of the
default branch after this merges; no authorisation, money, date or identity is involved.
