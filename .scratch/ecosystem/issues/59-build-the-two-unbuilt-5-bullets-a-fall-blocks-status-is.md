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
extractor ticket 100 uses — and runs it over throwaway git repositories in eleven states, each
graded by what the step DOES (its exit status, whether it printed `::error::`, what it wrote to
the step summary): nothing moved; a class lost a pass; `fail` rose; a pass became a
could-not-look with `fail` unchanged; the ceiling fell with a manifest commit in the span and
without one; the total fell with an exclusions commit and without one; a fall with a committed
reason; a falls file naming a run the log does not record; and a fall on a branch. The two
ceiling states and the two total states differ ONLY in which file the second commit touched, so
the diff rule is measured rather than described. Nothing is inferred from the YAML looking right.

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
   `talk/truth.log` is append-only and `verify/can-record/` refuses a hand-edited line, so a fall
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
   following `verify/can-record/` and `verify/cited-truth/`. Everything they read is in this
   repository and everything they run is git and python, so a missing interpreter is RED, not a
   shrug. `verify-derived-status.sh` does declare a `waits:` — but for the ESTATE's state (no
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

Map line: **59 — the two unbuilt §5 bullets** — a fall in the citable number now blocks: `talk/fall_check.py` compares two consecutive TRUTH lines class by class against the diff of the commits they name, `talk/verify-falls.txt` is the committed-reason escape, and a step of its own in `truth.yml` — after the cage, so the line is still recorded — turns the run red with its own `::error::`, proved by lifting that step's shell verbatim and running it over throwaway repositories in eleven states; what it blocks is this repository's citable run conclusion and not any unit's release, because no unit may be hostage to the hub's number, and the reach is printed as a number (0 of 2 workflows). Status became derivable only once the run recorded WHAT IT GRADED: `talk/verify-all.sh` now writes `talk/captures/_grades.tsv` inside the observation lane, and `verify/derived-status/` derives each resolved ticket's status from the checks its Answer names, refusing a table that is not the newest run's and refusing a red disposed of by the Answer's own words; the eight free-typed Status lines are normalised to the tracker's vocabulary with their qualifications kept verbatim in the body.

## Waits on the owner

Nothing. The grade table and the first derivation arrive on the first scheduled run of the
default branch after this merges; no authorisation, money, date or identity is involved.
