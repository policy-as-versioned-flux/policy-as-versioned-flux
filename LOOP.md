# The loop

> "quantified risk and a reactive ratcheting process cage to mitigate the quantified risk until the risk is within financial tolerance of the organisation" (the owner, 2026-11-14)

Later that day the owner wrote: "Remove all redundant code. Simplify everything". This file says what the estate now does, where its numbers come from, what is parked and what waits for the owner. The terms are defined in `CONTEXT.md`. The decisions are in `docs/adr/0039-one-loop-three-rungs-machine-merges.md`. The full design is `.scratch/distil/CONTRACT.md`.

## The loop

A cycle runs in driftwood's `.github/workflows/loop.yml`: every day at 06:47 UTC (driftwood's schedules start hours late, so in practice in the afternoon: see the last note), on a push to `main` that changes `party.json` or `gitops/apps/`, on dispatch, and on a pull request. Each cycle checks out platform, ico and feeds at their pins, each a signed tag and its commit, and builds a new kind cluster with `kubectl apply -k`.

1. **Sense.** `probe.py` waits until the governed Namespace is settled, then tests each capability on a live connection, between two reads from the reference. If any of that fails, the verdict is `could-not-look` and nothing moves.
2. **Price.** A row's amount is `mean(events a year) x (mean(loss an event) + penalty rate x mean(penalty at the adopter's turnover))`, where `mean(l, m, h) = (l + 4m + h) / 6`. The exposure adds the amounts of the open rows.
3. **Add cost.** The figure adds the current rung's cost from `cage/rungs.json` at the pinned platform tag. This is the one formula and the one compared number.
4. **Compare.** The tolerance comes from `party.json`.
5. **Predict.** The loop finds the goal for the tolerance, and whether it is release-ready. A prediction only chooses a direction.
6. **Decide.** The verdicts are checked in the order `CONTEXT.md` lists them, and the first that applies is the cycle's verdict.
7. **One notch.** A move changes the rung line and nothing else. Cost always enters the figure (decision 6). A notch is judged by the goal it leads to (K16, delegated; kept by the owner on 2026-11-15). This departs from a consequence written in the option the owner chose. Option (c) of `.scratch/distil/DISTILLATION.md` section 7 item 6 reads "cost is added to exposure, so a notch that costs more than it saves is not taken", and the owner answered "Always". The loop instead never starts a climb unless some tighter rung predicts a lower figure, cost included, and one notch on the way may cost more than it saves. Judged one notch at a time, the first notch closes nothing today's rows need, so the loop would stay at `baseline` for ever. That is not what the owner was told to expect under decision 5, to which the owner answered "Yes. No limitation". On the inputs of 2026-11-14, option (c) as written would have left the loop at `baseline`, red, with the shop serving. The owner was asked whether to keep K16 or reverse it, and kept it on 2026-11-15 (`.scratch/distil/DECISIONS.md`, "15 November: the four answers"). A rung that has stopped earning its cost is given back by `release`.
8. **Enact.** In `act` mode the workflow opens a pull request for the notch with the default token. A second job checks that the diff is one rung line, one notch, in the direction of the verdict. The app approves and merges it. The merge starts the next cycle on a new cluster built from `main`. A pin change takes the same path and may touch pin lines only. The second job works the pins out itself, and the pull request must match its result. The loop follows ico and feeds only. It never moves the platform pin (K17, delegated).
9. **Record.** A cycle on `main` writes one JSON line to the ledger, whatever the verdict. A pull request's cycle writes none. A run whose pins cannot be checked out, or whose input is refused, is red and writes no line. The loop refuses a malformed number in a feed: a three-point value that is not three numbers, none below 0, in ascending order; a tier's rate or cap, or a pricing fine, that is not above 0; and a penalty rate that disagrees with its basis. It does not repeat every check of the publishers' tests.
10. **The rule on numbers.** An unsourced number may raise the figure. These can lower it, each by its own path. A measured, declared closure lowers it in the cycle that measures it. A publisher's change lowers it once the loop follows the new tag, which it does by itself. By decision 6, a rung's cost leaves the figure when the loop leaves that rung. The adopter's turnover in `party.json`, and a rung's cost in platform's `cage/rungs.json`, lower it only by a pull request the loop cannot write: on `main` the loop's own hand changes the rung line and the ico and feeds pin lines, and nothing else. The tolerance, the margin and the dwell do not enter the figure. They change the verdict, and they too move only by such a pull request. A missing penalty rate is 1. An uncited tier is the tier with the larger mean penalty. A row with a missing number is unpriced and named.

A red verdict does not stop the landing path. Only the workflow's `verdict` job turns red, so a pin change, which is how a publisher's correction arrives, still lands. The loop lands a pin change only if the pinned loop accepts the inputs the new pins name, so a refused input cannot land by the loop's own hand. A platform fix arrives another way (K17): by a pull request to the platform pin line, pushed from an agent session. Its own cycle runs the new platform on a cluster before the app merges it.

## Where it stands

The loop is in `act` mode and stands at `isolated`, where the shop does not serve. It is green. Ledger line 11, written at 10:55:04 UTC on 2026-11-15, reads `within` at GBP 17,290.68 against a tolerance of GBP 430,000, with the goal `baseline`, and release-ready. It was the loop's first run in which every job passed. The loop is now waiting out the dwell of 7 days, which started with line 11 and is met from 10:55:04 UTC on 2026-11-22. The first cycle on `main` after that should read `release`, `isolated` to `quarantine`. Its merge starts a cycle that releases again, to `baseline`, and that merge starts a cycle at `baseline`, where the pinned loop predicts GBP 25,697.44, `within`, with the shop serving. Those three cycles follow each other within the hour. The release depends on two things. A cycle must run on `main` on or after 10:55:04 UTC on 2026-11-22, and the only thing that starts one unattended is the daily schedule, which has not yet run once. And every line until then must be release-ready: a line that is not release-ready starts the wait again, while a `could-not-look` line is passed over. Nothing was done to hurry it: the margin and the dwell are unchanged. The climb rests on two decisions together. The owner chose a loop that may climb that far (decision 5). The assistant chose to judge a notch by its goal (K16, delegated), and without that the loop stays at `baseline`. The owner kept K16 on 2026-11-15.

It got there by itself on 2026-11-14. Driftwood landed in `measure` mode and its first cycles read `tighten` and moved nothing. Platform's cluster proof was green at the pinned tag, so the mode was changed to `act` (driftwood pull request 134). The next cycle opened pull request 135, `baseline` to `quarantine`; the checker passed it and the app merged it. At `quarantine` the probe measured `egress` closed with the shop serving 3 of 3, and the cycle opened pull request 136, to `isolated`, which landed the same way. At `isolated` the probe measured both capabilities closed and the shop serving 0 of 3. No person was on that path. The ledger holds each line.

On 2026-11-15 the loop followed a publisher by itself. Feeds merged a text correction as version 5.0.1 (feeds pull request 22), and that merge cut and signed `threat-register/v5.0.1`. The next driftwood cycle opened pull request 138 for the new pin; the checker passed it and the app merged it. The cycle after that ran on the new feed and read the same verdict at the same figure. No person was on that path either, but for its start: the cycle was started by dispatch, not by the schedule. The platform pin moved the other way, by a pull request from an agent session (137, to `policy/v8.0.1`). Its own cycle ran that platform on a cluster before the app merged it.

Later on 2026-11-15 the owner answered the assistant's report of that morning in two words: "Do everything". The report had named two things that waited for the owner: K16, and which penalty rate ico publishes, with the tolerance. It had also listed what was not done. The reply was read as leave to do what was listed as not done. It was not read as an answer to any open choice: it names no penalty rate, no tolerance, no machine or spend for a cluster that stays up, and it does not say to reverse K16. Feeds read its second row's N again and found it 0, so the row now prices at 0.00 (K18, delegated). Feeds pull request 23 carried that as version 5.1.0, and its merge cut and signed `threat-register/v5.1.0`. Platform pull request 78 gave each cage file one true opening comment line in place of four stale ones. No rule changed and no tag was cut, so the pinned `policy/v8.0.1` still carries the old comments. Ico pull request 14 removes the words "FOR THIS EXAMPLE" from three litigation notes. It is a draft, held so that one ico tag carries it with the penalty rate, if the owner chooses one. No cycle was dispatched after the tag was cut, so that the schedule finds the tag and the loop follows it with no person and no dispatch. The first scheduled run was due at 06:47 UTC and had not started by 08:33 UTC. It is watched, not dispatched. When this was written the loop had not yet followed the new tag: driftwood still pins `threat-register/v5.0.1`, and the last ledger line is line 9, run 43663748023. The schedule did not get the chance to find the tag. A push cycle, started by the tolerance merge, followed it first, and ico pull request 14 was merged with the rate (next paragraph).

Later still on 2026-11-15 the owner answered the four questions (`.scratch/distil/DECISIONS.md`, "15 November: the four answers"): the penalty rate counted over all reports, 0.0002095, not the cyber-only count the assistant had recommended; a tolerance of 0.5% of turnover, GBP 430,000; a kind cluster on the owner's own machine for the proof on a cluster that stays up; and to keep K16. Ico pull request 14 then carried the litigation wording and the rate together. The app merged it as `39ddfaf`, and the merge cut and signed `v5.1.0` (run 43705453283). Driftwood pull request 139 changed one line of `party.json`: the tolerance became `share_of_turnover` 0.005, so that it moves with the turnover. The app merged it as `f22cd9a`. That merge started a cycle on `main` (run 43705857417, cause `push`). It wrote ledger line 10 at 10:51:31 on the old pins: GBP 1,643,518.63 against GBP 430,000, `saturated`. In the same run the loop opened pull request 140 for both new pins, ico `v5.1.0` and feeds `threat-register/v5.1.0`. The checker passed it and the app merged it as `4126d2e`. That merge started the next cycle (run 43706149681, cause `push`), which wrote line 11. No person was on that path after the tolerance merge. What followed feeds 5.1.0 was a push cycle, not the schedule.

The proof on a cluster that stays up ran the same day, from an agent session on the owner's machine, with the pinned harness and loop unchanged (K19, delegated, applying the owner's answer 3). Deleting the cage's network rule on the running cluster was seen by the next probe as `cage-ineffective`, and running pods were re-caged from `isolated` to `quarantine`, and back to `isolated` by way of `baseline`, with no restart (those pods had been created at `isolated`). It found two gaps, not fixed: a pod created at `baseline` cannot be tightened while it runs, and until it is replaced it keeps `baseline`'s reach whatever the Namespace says, so on a cluster that stays up a climb from `baseline` needs the pods replaced; and loosening to `baseline` in place leaves the limits and dropped capabilities as the pod was created. The daily loop is not affected, because it builds a new cluster each cycle. On the cluster that stays up Flux is not installed, so that cluster does not follow git, and the proof's lines go to no ledger (`.scratch/distil/standing-proof/2026-11-15.md`).

To read today's verdict, follow "How to read the ledger" in driftwood's README. On `main`, a run whose only red job is `verdict` is not a fault: its line is written, and the line says which verdict it was. A pull request's run can be red at `verdict` too, and it writes no line. A red `cycle` job is a fault: an input was refused or the pins would not check out, and no line was written. A red `write`, `check` or `land` job is a fault: a line or a move did not land.

The undo is two lines: `"mode": "measure"` in driftwood's `party.json`, and the rung line in `gitops/apps/namespace.yaml` back to `baseline`. That change needs a pull request with one approving review, and the owner cannot approve the owner's own pull request, so it takes an agent session, in which the app approves and merges.

The stop the owner can use alone, at once: switch `loop.yml` off in driftwood's Actions tab (or `gh workflow disable loop.yml -R policy-as-versioned-driftwood/driftwood`). No cycle then runs, nothing moves, and the daily run stops. The rung line stays where it is.

Besides those two decisions, today's state, green at `isolated` and waiting to release, rests on three things:

- **The third row**, `insider-or-lost-device-disclosure`. No cage can close it. It is priced, not left out, by K11 (delegated, applying decision 5). Its rate is one tenth of the first row's, a ratio feeds chose, and its loss is the first row's band.
- **The penalty rate.** ico publishes a counted rate, 0.0002095, as `v5.1.0`: 20 ICO monetary penalties over 95,466 breach reports of every kind. It is the owner's choice among three counts. The other two are higher: the cyber-only count, 0.000529, and the serious-breach count, 0.0038. The published count's own researcher calls it too low for a serious breach, by an amount the method cannot state.
- **The tolerance.** GBP 430,000, 0.5% of turnover, chosen by the owner on 2026-11-15.

What would change it:

- **The release expected on 22 November.** If every line until then is release-ready and a cycle runs on `main` on or after 10:55:04 UTC on 2026-11-22, the loop releases to `quarantine` (predicted GBP 31,197.44) and then to `baseline` (predicted GBP 25,697.44, `within`), and the shop serves again.
- **A higher published rate.** At GBP 430,000 the loop still releases to `baseline` up to a rate of 0.01800. Above that it stays at `isolated`, green and closed, up to 0.2540. Above 0.2540 it is red again (`.scratch/distil/penalty-rate/CHOICE.md`).
- **A change to the rows.** At `isolated` all of the exposure, GBP 2,290.68, is the third row, which no cage can close. A release needs `baseline` predicted at or below GBP 344,000, the tolerance less the 20% margin, and it predicts GBP 25,697.44 today. The rows' bands are feeds' work, and editorial.

## On the inputs of 2026-11-14

These are the figures of the unit tests on those inputs. Today's figures are in the ledger, `loop.jsonl` on driftwood's branch `ledger`. Each line also prints the cost basis, the tolerance basis, the sourced share and the weakest basis.

The three rows, each with bound `upper`, at the higher tier's mean penalty of GBP 3,613,638.10 for driftwood's turnover:

| Row | Amount a year (GBP) | Needs |
|---|---|---|
| `checkout-pii-exfiltration` | 16,280,871.43 | `inbound` |
| `scheduled-agent-misuses-write-credential` | 431.49 | nothing |
| `insider-or-lost-device-disclosure` | 1,628,087.14 | nothing |

| Cycle at | Measured closed | Figure (GBP) | Verdict |
|---|---|---|---|
| `baseline` | nothing | 17,909,890.06: exposure 17,909,390.06, cost 500 | `tighten` to `quarantine` |
| `quarantine` | `egress` | 17,915,390.06, cost 6,000 included. No row needs `egress` | `tighten` to `isolated` |
| `isolated` | `egress`, `inbound` | 1,643,518.63, cost 15,000 included. Serving 0 of 3 | `saturated`, red. `unreachable` 1,603,518.63 |

## Where each number comes from

| Number | Where it is | Its state today |
|---|---|---|
| Turnover, GBP 86,000,000 | driftwood `party.json` | Declared by the demonstration party, as of 2026-06-30 |
| Tolerance, 0.5% of turnover, GBP 430,000 | driftwood `party.json` | Chosen by the owner on 2026-11-15, from options the assistant offered. Written as a share, so it moves with the turnover (the form is the assistant's choice, delegated) |
| Margin 0.2, dwell 7 days | driftwood `party.json` | Settings with no outside basis |
| Three rows | feeds `threat-register/feed.json` | Every basis is `editorial` except the second row's rate, which is `published`. Since 5.1.0 that rate is 0: its N was read again on 2026-11-15. The first row's `needs` is the publisher's claim, with an ATT&CK source. The other two need nothing |
| Penalties | ico `penalty-schema/feed.json`, UK GDPR | Tiers priced from ICO penalty notices. No row cites a tier, so each takes the higher one. The penalty rate is counted: 0.0002095, 20 penalties over 95,466 breach reports, chosen by the owner and published in ico `v5.1.0` |
| Rung costs, GBP 500, 6,000 and 15,000 | platform `cage/rungs.json` | Unsourced: typed on 2026-07-31 for the version 7 rungs. No measurement |
| Capabilities | the probe, each cycle | Measured live |

## What is parked

The owner's answer 7 was "It's all purpose". What is not being worked on now is parked, not dropped, and can come back. Which parts are parked for the first loop is delegated (K8). No live figure reads any of them.

| What | Where it is kept | What brings it back |
|---|---|---|
| The exploited-flaw list | feeds tag `cve/v3.0.0` | A pull request in feeds that restores it from the tag |
| The image inventory and scanner | platform tag `v6.3.0` | A pull request in platform that restores them from the tag, and a scanner in CI |
| The fetch clocks, and all else | `refs/archive/main/2026-11-14-before-simplify` in each repository | A pull request that checks the files out from that ref. A returning fetch adds rows, and would need the key in that publisher |
| The twin, the talk and the calibration programme | The hub's `refs/archive/main/2026-11-14-before-simplify`, recorded in `.scratch/distil/ARCHIVE.md` | A pull request in the hub that checks them out from that ref |

The first loop runs end to end without them. `.scratch/distil/ARCHIVE.md` lists every archive ref and the repositories archived on GitHub, and says how to bring each back.

## What waits for the owner

| What | Until then | When it comes |
|---|---|---|
| The secrets hook and the signing permission | The three `cut-release.yml` files quote the `id-token` key so that the hook passes them. The old files wrote it unquoted | The owner confirms the spelling, or adjusts the hook |
| Removing the guard's hook from the hub | `twin/` and `.claude/settings.json` stay | One commit of the owner's removes the hook and the three `twin/` files together |
| The hosted Renovate app on driftwood | `renovate.json` keeps it silent | Uninstall it, then delete the file |

Four more rows stood here until 2026-11-15: K16, the tolerance, the penalty rate and the cluster that stays up. They were put to the owner as questions that day, and the owner answered all four the same day (`.scratch/distil/DECISIONS.md`, "15 November: the four answers").

Settled on 2026-11-14 by the owner's reply "I'm afk. Jfdi" (`.scratch/distil/DECISIONS.md`, "Later the same day"). Leave to cut tags: given and used. Each repository's own workflow cut and signed the first tag of the new design at the commit the loop had already run against: ico `v5.0.0`, feeds `threat-register/v5.0.0`, platform `policy/v8.0.0`. Driftwood pinned those tags (pull request 133). It now pins platform `policy/v8.0.1` (pull request 137), and ico `v5.1.0` and feeds `threat-register/v5.1.0` (pull request 140, the loop's own; feeds 5.0.1 came before it by pull request 138, also the loop's own). `CUT_ON_MERGE` is `true` in ico and feeds, so a merged change of a feed's `version` cuts its own tag. A platform tag is cut only by dispatch, and the platform pin moves only by a pull request to the pin line (K17). The key in feeds and ico: read as given, and not used. Nothing built here would read it, and a secret with no reader is redundant. Only a returning fetch would need it.

The numbers nobody had counted were not the owner's to supply. Counting the penalty rate was ico's work, and it was done three ways. The owner chose between the counts on 2026-11-15, and ico published the count over all reports as `v5.1.0`. The third row's band is feeds' work. Feeds read its second row's N again on 2026-11-15 and found it 0 (version 5.1.0).

## Six notes

- The loop's machine merges rest on decision 2 ("All AI machine driven"), not on `twin/ENACT_MODE`. That file still governs agent sessions in the hub until the owner removes the hook.
- The cluster proof in platform's CI is not yet decision 9's proof. It runs on a throwaway cluster. Decision 9's proof ran on 2026-11-15 from an agent session, on a cluster that stays up (see the last note).
- While a release waits for its dwell, the lines can read `saturated` and red. With one cycle a day, a dwell is usually met a day late.
- GitHub disables `loop.yml`'s schedule after 60 days without repository activity. It is switched back on from the Actions tab.
- Each of the loop's own pull requests shows one run of `loop.yml` with no jobs, marked failed. It is not a failed cycle. GitHub documents that a pull request opened by the workflow token starts its runs in an approval-required state. Both `loop/rung` pull requests show such a run: runs 43651161098 and 43651510938 have no jobs. That the run ends failed because the app merges the pull request seconds later is inferred. GitHub does not document it.
- These paths have not yet run live: the daily schedule, whose first run was due at 06:47 UTC on 2026-11-15 and had still not started at 10:58 UTC; and a release and its dwell, which is now waiting and expected on 2026-11-22 (see where it stands). Driftwood's scheduled workflows start hours late as a rule. Its earlier `propose-tier`, on the same cron, started at 14:42 on 11 November, 15:35 on 12 November, 14:54 on 13 November and 13:47 on 14 November: 7 to 9 hours after 06:47. So "every day at 06:47 UTC" means a run in the afternoon, and the first run of `loop.yml` is expected between about 13:45 and 15:35 UTC. Until it runs, the schedule is unproven. It is watched, not dispatched. The proof on a cluster that stays up ran on 2026-11-15, by hand from an agent session on the owner's machine, not from `loop.yml`: GitHub's runners cannot reach that machine (`.scratch/distil/standing-proof/2026-11-15.md`). A `loop/pins` change and a tag cut by a merge both ran on 2026-11-15.
