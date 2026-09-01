# 61 — Renovate completes step 2 once, for real

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Every Renovate PR ever raised was autoclosed; every landed bump was hand-made; and the feed pin step 2 prices cannot arrive by Renovate at all because the customManager over inherits[] (deferred by ticket 22 to ticket 21, never written) does not exist. Write that customManager; make a Renovate bump able to go green (the pin file, party.yaml's inherits entry and the composed/ re-render must move together — a completing workflow job on the Renovate branch is the likely shape); then let threat-register v2 (or the next real tag) arrive as a Renovate PR and have a human merge it — the first real step-2 event, which triggers propose-tier for real. Done = one merged Renovate PR on one adopter, graded by a check that reads the PR record, not a simulation.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M8 (step 2 never real / feed pin un-raisable, 2 confirmed findings).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Progress — 2026-09-01, the mechanism is built and proven; the event waits on the owner

All AFK work is done. The branch `ticket-61-renovate-completes-step-2` sits on the local
driftwood clone (commit 8f7861f), unpushed. `enact_guard` blocks pushes to enactment repos in
operations mode. That block is correct.

What was built, and how each piece was verified:

1. **The customManager over `inherits[]` exists.** Ticket 22 deferred it to ticket 21, and
   nobody wrote it. `renovate.json` gains manager #3 for `party: feeds` lines and manager #4
   for `party: insurer` lines. The feeds repo tags releases as `<name>/vX.Y.Z`, so
   `extractVersionTemplate` maps the tag back to the payload-dir version (`v2`). The insurer
   uses plain `vX.Y.Z` tags. ico stays un-renovated because it ships no tags. `party.yaml`
   documents that already. `renovate-config-validator` under renovate@44.37.1 on Node 24
   validates the config. Those are the workflow's own pinned versions.
2. **A Renovate bump can now go green.** `postUpgradeTasks` runs
   `.github/scripts/complete-feed-bump.sh` on the bump branch. `fileFilters: composed/**`
   folds the re-render into the same commit, so the pin and the render move together.
   The completer clones the parents at compose-check's own refs. It composes twice, on
   purpose. Composition fills each price entry's `old_version` from the previous HEADER on
   disk. A one-shot transition record in the committed artefact would fail every later
   recompose drift check. The committed artefact must be the settled fixpoint. The PR diff is
   the record of the transition. Proof, on a scratch tree: bump the pin v1 to v2, run the
   completer, then run a CI-style recompose. The recompose reproduces the committed artefact
   exactly.
3. **Detection is proven end to end.** Renovate 44.37.1 ran with `platform=local` in a Node 24
   container against a fixture remote that carries `threat-register/v2.0.0`. Result:
   `1 flattened updates found: feeds/threat-register`, `newValue: v2`, `updateType: major`,
   branch `renovate/feeds-threat-register-2.x`. Against the real remotes, where only v1.0.0
   exists, both feed deps resolve `fixedVersion: v1` with no warnings. That silence is
   correct.
4. **The grading check reads the PR record, not a simulation.**
   `verify/renovate/verify-renovate-merged-feed-pr.sh` joins the gate by glob. It reads each
   adopter's real `main` for a merge commit from a `renovate/` branch, with bot-authored
   commits on the branch side, with `party.yaml`'s feed pin and `composed/` moved in the same
   diff, merged by a human. It grades PASS on the real event. It grades FAIL when the pin
   moved without the render, or when a bot performed the merge. It grades SKIP while the
   event has not happened. Fixture tests exercised all four outcomes. Against the estate
   today it reports SKIP.
5. **Found and fixed on the way.** Ticket 57's branch rename killed `ref: ecosystem/thin-slice`
   in every adopter workflow. Driftwood carried six dead refs, in shift-left's compose-check,
   cut-release and propose-tier. The branch fixes all six. Without that fix, no driftwood PR
   can go green at all. Tuppence and ludlow still carry twelve dead refs. Ticket 57 has a
   dated comment naming them.
6. **Found, not fixed here.** No cron has ever fired on driftwood. The repo's full run history
   has zero `schedule` events, so renovate-run's 06:11 UTC slot has been missed daily since
   2026-08-28. This is the same registration class ticket 57 hit. `workflow_dispatch` works.
   Tickets 60 and 56 own the clocks.

### Checklist (owner; steps 2 to 5 I can run on your word)

1. Push the prep branch and open its PR (needs your push):
   `cd .estate-clone/driftwood && git push origin ticket-61-renovate-completes-step-2`.
   Merge it after shift-left and compose-check go green. This PR is preparation, not the
   step-2 event.
2. Cut the next real feeds tag. The v2 payload has sat unreleased since the thin-slice build:
   `gh workflow run cut-release.yml -R policy-as-versioned-feeds/feeds -f feed=threat-register -f version=2.0.0 -f message="threat-register v2: revised tuppence account-takeover rates"`
3. Dispatch Renovate on driftwood:
   `gh workflow run renovate-run.yml -R policy-as-versioned-driftwood/driftwood`
4. Renovate opens `renovate/feeds-threat-register-2.x`. The one commit moves `party.yaml` and
   `composed/` together. Review it and merge it yourself. That merge is the first real step-2
   event, and it fires propose-tier for real (ticket 60 watches that trigger).
5. The next citable TRUTH run flips `verify-renovate-merged-feed-pr` from SKIP to PASS. Then
   this ticket resolves on that line.

## Answer — 2026-09-01, step 2 happened for real

The owner said "Do all that", so the checklist ran the same day, through the sanctioned
routes (`twin/ENACT_MODE` development for the enactment acts, restored to operations after,
recorded on the hub). The event, as the grader reads it from git:

> PASS: driftwood #20: Renovate raised threat-register v1 -> v2, Chris Nesbitt-Smith merged
> it, and party.yaml and composed/ moved together -- step 2 happened for real

That line is this session's local read. The citable record is the next scheduled TRUTH run,
which flips `verify-renovate-merged-feed-pr` from SKIP to PASS.

What the live walk added to the built mechanism (see Progress above):

1. **feeds `threat-register/v2.0.0` is cut and published.** cut-release run 33486753913,
   release run 33487519188, both green. The v2 payload had sat unreleased since the
   thin-slice build.
2. **Driftwood PR #16** (config, completer, ref repairs) went red once, honestly:
   compose-check caught the completer's `--depth 1` clones. Composition resolves an unpinned
   parent's sha with `git log` on the version-scoped subdirectory, and a shallow clone
   flattens every such lookup to the tip. Full clones fixed it; #16 merged green.
3. **Renovate's first live run refused the completer.** Renovate 44 matches
   `allowedCommands` with its regex-or-glob matcher: a plain `^...$` string is read as a
   glob and matches nothing. **PR #18** allows the command in glob-exact and slashed-regex
   forms; merged green.
4. **Two Renovates fought over one branch.** The hosted Mend app (installed org-wide by
   ticket 01) reacted to the same config, rebased the bump branch, consumed the retry
   checkbox, and can never run postUpgradeTasks; the self-hosted run then refused the branch
   ("Branch has been edited but found no PR - skipping") because it only adopts PRs it
   created itself. **PR #19** settles it: `renovate.json` says `enabled: false`, which the
   hosted app obeys, and `renovate-run.yml` force-enables itself with `RENOVATE_FORCE`,
   which only a global config can set. Exactly one Renovate acts on driftwood now, and it is
   the one that can complete a bump. The hosted app's PR #17 was closed with the reason in a
   comment. Candidate ADR when the pattern spreads to tuppence and ludlow.
5. **The self-hosted run then did the whole job**: customManager detected v2, the completer
   ran on the branch, and one bot commit (`ea1c8db`) moved `party.yaml`,
   `composed/HEADER.yaml` and `composed/evidence.json` together. Its PR-creation API call
   errored (`prBlockedBy: "Error"`), so **PR #20** was opened manually from the unmodified
   branch head. shift-left and compose-check passed; the owner's credential merged it on the
   owner's word (merge commit `27f1cf2`).
6. **The merge triggered propose-tier for real** (run 33489735149, success, no proposal PR).
   Driftwood's tier stays `baseline`, which matches the offline step-2 capture: v2 re-prices
   tuppence, not driftwood. Ticket 60 owns observing that path on the clock.

Open residue, owned elsewhere:
- Cron has never fired on driftwood (tickets 60 and 56). The whole walk ran on
  `workflow_dispatch`.
- The feed parents are consumed at `ref: main`, not pinned (ticket 62).
- Tuppence and ludlow still carry twelve dead `ecosystem/thin-slice` refs and both
  Renovates (ticket 57 comment; ticket 62 or a follow-up).
- The next citable TRUTH run converts the grader's SKIP history to PASS.
