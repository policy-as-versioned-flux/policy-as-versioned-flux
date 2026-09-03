# 70 — The observation lane is detectively enforced and honestly recorded

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 58 Q4(b): the repos stay public, so push-time prevention is impossible (GitHub refuses push rulesets on public repos, and required_signatures would reject gitsign). Build the detective control: the gate's lane verifier grades every commit on the observation refs against the lane rules as a named check, and a violation is a red. Amend ADR-0023 with a dated note recording the limitation and the revisit trigger (going private). Correct ticket 28's Answer, whose ruleset plan was falsified after resolution, with a dated note. Done = the check runs in the gate and the record matches reality.

## Notes

Graduated from ticket 58 (2026-08-31), decision provisional on a bare "Agree".

## Answer

Built 2026-09-03, hub only. Nothing in a unit changed.

**What was built.** `verify/schedules/lane.py` and `verify/schedules/verify-lane.sh`, beside `schedules.py`, which is untouched. The script walks the first-parent history of every observation ref -- `origin/main` on each of the eight units, `origin/observations` wherever it exists (platform, feeds, nist, ico, insurer), and the hub's own `origin/main` -- and grades every commit whose committer is a scheduled identity: it must touch only lane paths and must not be a merge. A violation is a FAIL naming the commit, the identity and the paths. The scheduled identities and the lane are parsed from the unit's scheduled workflows (`user.email` and `OBSERVATION_LANE` in jobs under `on: schedule:`), from both the checkout and the graded ref's own copy of the workflow files, with `github-actions[bot]` always in the identity set and ADR-0024 point 3's list as the lane's ceiling and fallback. It reuses `schedules.py`'s allow-list, workflow parser, env merge and unit walk. It runs offline on what `.estate-clone/` holds after one best-effort fetch of the two refs, deepens a shallow checkout (truth.yml checks the hub out at depth 1) and records a could-not-look when it cannot. `talk/verify-all.sh` discovers it through its existing glob; the TRUTH line's `total` moves by one.

**Which check grades it.** `verify/schedules/verify-lane.sh`: exit 0 every landed scheduled-identity commit is inside the lane and none is a merge; 3 a ref or a history could not be read; 1 a violation. Its selfcheck plants real git repositories in a temp directory: a clock's declaration on `main` and on the orphan `observations` branch bites and names the commit; a clock's merge bites; a clock's observations pass; the orphan root commit is graded on everything it introduced; a human's declaration, a clock-authored commit a human merged with `--no-ff`, and a squash with a clock author and a human committer are not graded; an automation identity no scheduled workflow configures is named and not graded; a `--depth 1` clone is deepened when a remote is reachable and is a could-not-look when not; identities and lanes parse from the shapes the estate's workflows actually use, including `${GITHUB_REPOSITORY_OWNER}`.

**What it observed on 2026-09-03.** Every landed commit was inside the lane: 4 drift samples on each of driftwood, tuppence and ludlow `main`; 3 fetch observations on each of platform, nist, ico and insurer `observations`, 1 on feeds'; 17 truth commits on the hub's `main`; nothing by a scheduled identity on platform, feeds, nist, ico or insurer `main`. Two facts it surfaced that the workflow parse cannot: driftwood's `main` copy of `twin-sweep.yml` configures `twin-sweep@` where the checkout's says `twin-agent@` (both are graded, which is why the ref's copy is read); and platform's release bot (`releases@policy-as-versioned-platform.invalid`, `cut-release.yml`, `workflow_dispatch`) has landed 4 evidence commits directly on `main`. Those are named in a NOTE line, not graded: a dispatched release is a human act (ADR-0023 D3, hard rule 3).

**The record.** ADR-0023 carries a dated amendment (2026-09-03): push-time prevention is unavailable on a public repository, the cage is preventive in the workflow step and detective in this check, the revisit trigger is going private (or a required status check), and the signature on landed commits is ticket 73's. Ticket 28's Answer carries a dated correction of "the observation lane is caged ... each repo carries the ruleset it needs". `verify-schedules.sh`'s header points at the detective half. `schedules.py`'s own "unavailable" SKIP wording is left for ticket 83 item 4, which rewrites that region.

**Decisions, all delegated (ADR-0025), each with its reason.**

1. *The observation refs* are `origin/main` on every unit, `origin/observations` wherever the ref exists, and the hub's `origin/main`. The ticket named four observation branches; platform has one too, and the hub is a clock. A hard-coded list would have missed a real ref, so the check discovers them and skips only where a unit's workflows push `observations` and the branch has not been created.
2. *A scheduled-identity commit* is one whose COMMITTER email is a `user.email` configured inside a scheduled job, or `github-actions[bot]`. Committer rather than author: a clock that pushes writes the commit object itself, so both names are the clock's; a clock-authored commit that reached the ref through a human's merge, squash or rebase carries the human's or GitHub's committer and is a reviewed proposal. The Rekor-backed gitsign identity is not read here: `%G?` reads N or U for every landed commit, and a second copy of ticket 73's verifier would be a second signer under another name.
3. *The lane* is the union of `OBSERVATION_LANE` across the unit's scheduled jobs, kept inside ADR-0024 point 3's list, with that list as the fallback. One source of truth shared with `schedules.py`; a path declared outside the ADR list is that checker's FAIL and this one does not widen the lane to match it.
4. *A separate script* rather than a section of `verify-schedules.sh`. Two different questions -- the promise in the YAML and the history on the ref -- get two rows and two captures in the TRUTH accounting, ticket 83's manifest can class them apart, and `schedules.py` stays untouched for tickets 83, 56 and 85.
5. *Full first-parent history*, not "since the first clock". The scheduled identities did not exist before 2026-08-29, so the graded set is the same either way and a date would be one more thing to maintain. A human's commit is never a lane violation whatever it touches; a merge commit made by a human is a human act; a merge commit made by a clock is a fault even when everything it brought in is an observation.
6. *Automation identities no scheduled workflow configures* (the release bot) are named in a NOTE, never graded. Grading them would red every release; ADR-0023 D3 makes a release a human act. The NOTE keeps the fact visible for a later ticket that wants the release bot's writes graded on their own terms.
7. *A shallow checkout* is deepened by a best-effort `--unshallow`, and is a SKIP naming the visible depth when that fails. A one-commit walk graded PASS would be the turn-absence-into-a-verdict mistake `schedules.py` refuses elsewhere.
8. *Zero graded commits on a ref* is a vacuous PASS whose wording defers liveness to `verify-schedules`. The absence of a violation is observed-true for this question; whether the clock runs at all is tickets 56 and 85.
9. *Coordination with ticket 56*: one dated paragraph from this ticket at the end of ticket 28's Answer; ticket 56 appends its own after it. Non-conflicting by construction.
10. *The repositories stay public*, re-recorded here with the reason ticket 58 lacked: they are the demonstration and its audience reads them, and ticket 82's licence work assumes public. That is the whole reason a detective control exists.

Map line: Ticket 70: the lane is detective -- `verify-lane.sh` walks every observation ref's first-parent history and reds a scheduled-identity commit outside the lane or a clock's merge; ADR-0023 amended (no push ruleset on a public repository, revisit on going private); ticket 28's "caged" claim corrected.

## Waits on the owner

- Taking the nine repositories private or internal is an authorisation. It is the revisit trigger recorded in ADR-0023; nothing here acts on it. If it happens, the prepared `.github/rulesets/observation-lane.json` applies as-is with the `gh api` line in each unit's `.github/rulesets/README.md`, using the `admin:repo` credential no agent holds.
- Nothing else. No unit was changed, so no unit push is owed for this ticket.

## Comments

**2026-09-03, build.** Verified with `bash verify/schedules/verify-lane.sh` (exit 0, twenty-two seconds, nine repositories, every ref PASS), `.venv/bin/python verify/schedules/lane.py selfcheck` (ok), `.venv/bin/python -m mypy --follow-imports=silent verify/schedules/lane.py` (clean; `schedules.py` carries the same two pre-existing errors on `main`), and `find .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*'`, which lists the new script. `talk/verify-all.sh` was not run, per the build brief.
