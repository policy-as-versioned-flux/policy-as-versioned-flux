# 56 — The citable run can see whether the clocks ran

Type: task (AFK)
Status: resolved (the surface grades clock liveness from 2026-09-04; the first CITABLE grade waits on the next scheduled truth run)
Blocked by: none

## Question

verify-schedules' live half SKIPs on every CI run because the gate step deliberately carries no GitHub credential — a recorded security decision whose consequence (permanent blindness to clock liveness) is recorded nowhere. Grade clock health with a read-scoped credential isolated from the untrusted verify scripts: a separate workflow step or job that runs before the gate, queries the runs API, and hands a verdict file into the TRUTH accounting; or an equivalent design that keeps the token out of the eight orgs' unpinned scripts. Reconcile with ADR-0024 and correct ticket 28's over-claiming Answer with a dated note. Done = "ran inside its period" grades for real on a scheduled run without exposing a credential to third-party scripts.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M6 (verify-schedules blind, 3 confirmed findings).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Two additions. verify-schedules can never PASS on the clock for a second reason: ico, nist and platform fetch.yml carry no `gh pr create`, so schedules.py emits three unconditional D2 SKIPs even with a token. And its ruleset half emits no line at all when it cannot look (`if live and ...`), so eight server-side questions vanish, a fourth outcome against §5's three; ticket 83 item 4 fixes the silence. Five real clocks were red on 2026-09-02 and this surface showed one SKIP. Record: REVIEW-2026-09-02.md R8, security/SS-07 for the write-credential half.

## Answer

Built 2026-09-04. Every decision below is **delegated** (ADR-0025) unless it says otherwise.

**What was built.** `truth.yml` now has two jobs. `clocks` holds `permissions: {contents: read,
actions: read}` and `GH_TOKEN: ${{ github.token }}`, runs no third-party code, and writes the raw
live facts to `$RUNNER_TEMP/clocks.json` (`schedules.py clocks --out FILE`, schema
`clock-verdict/v1`): per unit the observation-lane ruleset state, per clock the remote
`schedule:` tri-state and the newest scheduled run's `createdAt` and `conclusion`. It uploads that
as the `clock-verdict` artifact. `gate` takes it back down, points `CLOCK_VERDICT` at it, and
`verify/schedules/verify-schedules.sh` grades questions 3b and 4 from the file while holding no
credential at all. The file carries observations and no verdicts, so the 84 unpinned scripts that
run in that job can read nothing they could not read from the public API themselves.

Precedence in `schedules.py observer()`: `CLOCK_VERDICT` if set, else an authenticated `gh`, else
offline -- and a verdict file that is absent, malformed, of the wrong schema or older than six
hours becomes an `Offline` source whose reason says so and says explicitly that this job does not
fall back to a credential. That is the one rule the whole design rests on: the failure mode of the
hand-off must be a named could-not-look, never a quiet reach for a token.

**Which check grades it.** `verify/schedules/verify-schedules.sh`, unchanged in the gate's eyes
except that its live half now answers. Its manifest line moves from `never: GitHub unreachable` to
`never: no observation-lane ruleset|github unreachable`: the liveness question is no longer part
of the ceiling, and what remains permanently unpassable is the server-side ruleset question (a
push ruleset is private/internal-only; all nine repos are public). New tests:
`schedules.py selfcheck` gains the verdict-file fixtures, and `tests/test_schedules_clock.py`
holds the same seam under pytest (16 tests).

**Decisions.**

1. *A separate job, not a pre-gate step in the same job.* SS-07's argument wins: a step's `env:`
   lives in the job's environment for that step only, but the token would still be minted in the
   same job as the untrusted scripts and would be one workflow edit away from leaking. A job
   boundary is a runner boundary. The cost is one extra checkout, a `pip install` and a
   `clone-estate.sh` (~1 min) per run. Paid.
2. *The hand-off is a file of FACTS, consumed by `schedules.py`, not a pre-gate step printing its
   own PASS/FAIL lines.* Two reasons. The grading rules -- the 48-hour window, the tri-state
   remote `schedule:`, the excused conclusion, the ticket map -- would otherwise exist in two
   places and drift. And a clock verdict is an observation: "a clock appends observations, never
   declarations" is the estate's own rule, and a file of dates and conclusions honours it in a way
   a file of verdicts would not.
3. *`github.token` is enough for the other eight organisations.* Their repositories are public and
   the Actions runs API reads public repositories with any valid token; verified locally that all
   nine are reachable (`9 of 9 organisations reached, 13 clock(s) read`). This is the reason no
   PAT and no App token is minted, which keeps the whole design off the owner's desk. If CI
   proves otherwise, the collector already records `reachable: false` with the reason per
   organisation and the gate SKIPs that one by name -- a wrong guess degrades to an honest
   could-not-look, never to a false green. Named as the one thing only a real run can confirm.
4. *The three unconditional D2 SKIPs (platform, nist, ico `fetch.yml`) become PASSes with a named
   limit, not FAILs and not SKIPs.* SKIP means could-not-look and the checker had looked: it
   parsed the workflow and saw no `gh pr create`. It is also not an undecided shortfall -- ADR-0024
   Consequences says in as many words that those four parties "observe rather than fetch... That
   is a real series". The PASS line now says the clock is declared and timed AND that it opens no
   pull request, records what the party has already published and the hash of it, that D2's
   proposal half is vacuous for a party whose feed is its own artefact, and that the
   upstream-reading half of story 9 is not built there and is not graded by that line. Without
   this, three SKIPs held the script at exit 3 forever whatever any credential could see, and the
   ticket's own done-line was unreachable.
5. *The excused non-zero exit is one conclusion, not "anything but success".* `RED_GATE_EXITS_
   NONZERO` becomes `{"truth.yml": "failure"}`. Found by doing it: the hub's newest scheduled run
   on 2026-09-04 read `cancelled` and graded PASS. A cancelled run recorded nothing.
6. *`truth.yml`'s concurrency group is per event.* One `truth` group with
   `cancel-in-progress: false` keeps the running job and the newest queued one and cancels the
   rest, so a scheduled run that queued behind a push was cancelled before it recorded anything --
   which is what happened at 09:55:43Z. `group: truth-${{ github.event_name }}` lets the clock
   queue only behind other clock runs. Two truth runs can now overlap; the cage step's
   `git pull --rebase --autostash` is already written for exactly that contention.
7. *`units()` finds a unit by `os.path.exists(root/.git)`, not `isdir`.* In a git worktree `.git`
   is a file, and the build brief has every builder edit a unit inside a nested worktree -- under
   which this checker silently graded **ten** clocks instead of thirteen and reported no
   could-not-look for the **three** it dropped. A checker that can be blinded by how its input
   was checked out is not a checker.

   (Counted again 2026-09-04, round 2: the first write of this decision said "eight instead of
   thirteen ... the five it dropped" and neither number reproduces. Three units are symlinked at
   nested worktrees in this build -- feeds, insurer, nist -- so `.git` is a file in exactly
   three, and each of those carries one clock: `fetch.yml`. Ten graded, three dropped. The defect
   and the fix are unchanged; only the size of the hole was wrong.)
8. *SS-07's write half is not taken here, and is recorded rather than done quietly.* The cage
   step's `GH_TOKEN` is still handed to a step in the job the gate ran in. Moving the
   commit-and-push to a third job means handing the whole tree between runners with
   `id-token: write` for gitsign, which is a larger change than this ticket. Noted in ADR-0024.
9. *`verify-schedules.sh` gains no `selfcheck_absent` leg* (ticket 76's shape). That leg re-runs a
   script with a TOOL hidden; this script's could-not-look is a missing credential or a missing
   verdict file, and `schedules.py selfcheck` already exercises both paths as fixtures at a
   twentieth of the cost. Its FAIL summary now names the red clocks rather than counting them.
10. *Ticket 83's silent ruleset half* (`if live and ...` with no else) had already been fixed by
    83 itself before this landed; `ruleset_line` is reused as-is and now also routes through the
    verdict file. No second copy.

**What the first real grade said** (local run against the live API, 2026-09-04, the same code path
CI takes): 13 clocks read, 6 red -- `driftwood/twin-sweep.yml` (ticket 72),
`feeds/fetch.yml` (85), `insurer/fetch.yml` (77), `ludlow/propose-tier.yml` and
`tuppence/propose-tier.yml` (62), `hub/truth.yml` (85). The gate will be red on this check until
those clocks tick green, which is the point of the ticket: the surface can now see them.

Ticket 28's over-claiming done-line carries its correcting note, dated 2026-09-04. ADR-0024
carries the read-credential leg and the three smaller corrections.

### Round 2, 2026-09-04 — the checker was grading itself

Review found one blocking defect and four smaller ones. All fixed on this branch; every call below
is **delegated** (ADR-0025).

**Blocking: the newest scheduled run of `truth.yml` was this run.** `last_run` asked
`gh run list --event schedule --limit 1` with no status filter, and on a scheduled `truth.yml` run
the newest scheduled run of `truth.yml` is the run doing the grading: `conclusion` "", `status`
`in_progress`. Round 1 narrowed the excuse to exactly `failure`, so the two together gave
`FAIL: hub/truth.yml: last scheduled run 0h ago concluded 'in_progress'` on **every scheduled run
for ever**, blaming ticket 85 for it, and no fix in any estate repository could clear it. The same
false red hits any clock whose newest scheduled run happens to be in flight when the collector
looks. Reproduced before the fix: a verdict file in which every clock is green and `hub/truth.yml`
is the in-flight self-run graded FAIL.

Fixed at both ends, and the seam made pure so the fix is testable without a network:
`newest_gradable(runs, this_run_id)` drops the run doing the grading by `databaseId`
(`GITHUB_RUN_ID`), then prefers the newest **completed** run over a newer one still in flight
(`--limit 10`, and `databaseId` added to the `--json` fields). `run_line(unit, workflow, run, now,
owns)` — the old inline grading block, lifted out whole — grades an unfinished run as a **named
SKIP** and never a FAIL: a run in flight has concluded nothing, so it is a could-not-look, and the
SKIP line carries no owner clause because a could-not-look must not blame a ticket. Six new tests
in `tests/test_schedules_clock.py`, written red first, plus the same fixtures in `selfcheck`.

1. **The verdict file was bound to nothing.** No run id, no repository, no sha, and its only
   freshness was its own `collected_at`. Proved: rewriting every conclusion in it to `success`
   gave 0 FAIL and 50 PASS. `collect()` now stamps `run_id` and `repository` from the GitHub
   context, and `binding_fault(doc, env)` refuses a file whose run id or repository is not the run
   reading it — the reader falls back to Offline with the reason, never to a credential. Recorded
   plainly, because it matters: this **narrows the window, it does not close a trust boundary**.
   The gate job runs 84 unpinned third-party scripts over the whole workspace and one of them
   could rewrite `schedules.py` itself, verdict check included. What it stops is the cheap
   version — a stale, stray or hand-written `clocks.json` on the `CLOCK_VERDICT` path being graded
   from as if it were this run's own observation. Outside Actions (`GITHUB_RUN_ID` unset) there is
   nothing to bind to and the check says so rather than pretending.
2. **Decision 7's numbers did not reproduce**; corrected in place above (ten graded, three
   dropped, three symlinked worktrees carrying one clock each).
3. **`truth.yml`'s gate job was `if: always()`**, which includes cancelled — so a cancelled run
   still ran the gate, recorded a TRUTH line and pushed it through the cage, while round 1's own
   new rule grades a cancelled run of that same workflow as recording no observation. Now
   `if: ${{ !cancelled() }}` (the `${{ }}` is required; a bare `!` starts a YAML tag), which still
   covers the case the guard exists for: the clocks job failing or being skipped.
4. **The count of red clocks disagreed with itself.** ADR-0024's note and ticket 28's correction
   said "five of thirteen" where the same day's run says six. Both now say six and name them; the
   2026-09-02 review's five is left as the review's own dated reading, with the reason for the
   difference (`hub/truth.yml` had not yet had its cancelled run) written where the counts are.
5. **Ticket 85's "waits on the owner"** still asked the owner to push the three unit branches;
   they were already pushed. Corrected there with who pushed, when, and the SHAs.

Map line: Ticket 56 -- truth.yml's `clocks` job holds `actions: read` and hands the gate a facts-only clock verdict file, so "did each clock run inside its period" grades on the citable run with no credential in the job that runs eight orgs' scripts; a cancelled run is no longer excused, and the three D2 SKIPs become PASSes with a named limit.

## Waits on the owner

1. **The first citable grade.** It is observed only when `truth.yml` next fires on its cron
   (47 5 UTC) or the owner dispatches it. An agent must not fake a TRUTH line. The evidence to
   look for on that run: the skip count drops by the clock lines, and `verify-schedules.sh` grades
   FAIL naming the red clocks rather than SKIP. After round 2 that run must **not** name
   `hub/truth.yml` for being `in_progress`: it grades the newest run that is neither this one nor
   still in flight, so the expected list is the reds that are really red on the day.
2. **Whether `github.token` really reads the eight foreign orgs' runs from inside Actions.** It
   does from a local token; the collector degrades to a per-organisation named SKIP if it does
   not. Only a real run settles it. No secret needs minting unless it turns out otherwise, and
   minting one would be the owner's (authorisation).

**Re-review fix, 2026-09-04 (the assistant, delegated).** Approved after one fix round, with four
minors closed here. `run_line`'s docstring said "age first" where the code checks in flight first.
The in-flight could-not-look had no upper bound, so a run stuck for ever read as a could-not-look
for ever; past the same window a stopped clock fails on, an unfinished run is now a FAIL saying the
clock has stopped, which is what it is. `binding_fault`'s docstring claimed it stopped a
hand-written verdict file; it does not, because every script in the job can read `GITHUB_RUN_ID`
from the environment, so it now says it stops a stray or stale one and names what it does not stop.
And a refused verdict file was announced as "GitHub unreachable", which is not what happened; the
line now says the run declined to grade from the verdict, with the reason after it.
