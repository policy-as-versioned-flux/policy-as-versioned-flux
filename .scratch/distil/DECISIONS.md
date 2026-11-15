# Decisions: the owner's answers of 2026-11-14

The owner answered the ten decisions of `DISTILLATION.md` section 7 on 2026-11-14, in one message. Each answer is quoted exactly. "Read as" is the assistant's reading, not the owner's words. Where the reading changes the design in `DISTILLATION.md` or `TARGET.md`, this file wins.

| # | Question | The owner's words | Read as | What it changes |
|---|---|---|---|---|
| 1 | Can the cage ever release? | "Yes doesn't need person to merge" | The cage tightens and releases by itself. A release needs no person. | Section 5.3 had a person merge each release. The margin and the dwell stay as settings, so one release does not cause the next tightening. |
| 2 | Who merges? | "All AI machine driven" | Every merge in the loop is made by a machine identity. No hop waits for a person. | Goes further than the recommended option. Releases, feed bumps of every size and publisher tags are machine-made too. The app's key would have to be a secret in feeds and ico. That is a grant of identity, to be confirmed with the owner when that step is built. |
| 3 | What is the tolerance, and on what basis? | "What is the industry norm?" | A question back. Not yet decided. | See "Tolerance" below. Until the owner names a figure the loop compares against GBP 40,000 and labels it a fixture. |
| 4 | Mean year or bad year? | "Ok" | The mean loss a year, by formula. | As recommended. Monte-Carlo stays as a cross-check in the tests. |
| 5 | May the loop act unattended on unsourced numbers? | "Yes. No limitation" | Yes, across the whole ladder, including a rung where the workload stops serving. | The `may_stop_serving` setting is not needed. The range is the whole ladder. |
| 6 | Does the cage's running cost count? | "Always" | Cost always enters the comparison. | Section 7 recommended printing it only. Each rung's running cost is now part of the figure, so a notch that costs more than it saves is not taken. Today's four cost figures have no source and are labelled so. |
| 7 | Is the loop now the purpose, setting aside the twin, the talk chain and the calibration programme? | "It's all purpose" | Nothing is set aside as a lesser thing. All of it is purpose. What is not being worked on now is archived and can come back. | The record does not call any part a by-product. Parked parts are named as parked, with where they are kept. |
| 8 | Remove driftwood's floor and reset its rung? | "Sure" | Yes. | As recommended. Recorded in the ledger as `cause: reset` when it is done. |
| 9 | Where does the cage run? | "Ok" | The daily throwaway cluster now; a cluster that stays up for the proof. | As recommended. |
| 10 | Archive the parked repositories and local-only work? | "Archive anything you're not working on. Push as you go though to work in the open and use GitHub workflows" | Archiving is authorised. Work is pushed as it is done, in the open, and runs on GitHub's workflows. | See `ARCHIVE.md` for what was archived and how to bring it back. |

The owner then gave one instruction:

> "Clear up and archive all branches worktrees and repos we don't intend to proceed with, we can always bring back"

`ARCHIVE.md` records what that clean-up did.

## Later the same day

The owner wrote: "Remove all redundant code. Simplify everything". The assistant then asked two things, each a yes or no:

1. May the first signed tags of the new design be cut? Tags on these repositories can never be moved or deleted.
2. May the app's key be added to feeds and ico, so that the publishers can land and tag unattended?

The owner's reply, in full: "I'm afk. Jfdi".

Read as: yes to both, and do not wait for the owner.

- **Tags: given and used.** Each tag is cut by its repository's own signing workflow. A tag can never be moved or deleted, so the first tags were cut only at commits the loop had already run against (`CONTRACT.md` section 8, steps 6 to 8): ico `v5.0.0`, feeds `threat-register/v5.0.0`, platform `policy/v8.0.0`. From then on a publisher's merge cuts its own tag.
- **The key in feeds and ico: read as given, and not used.** The design that was then built (`CONTRACT.md`) leaves nothing in feeds or ico that would read the key: a publisher's only unattended act is to cut a tag, and the default token can do that. A secret with no reader is redundant, so it was not added. A returning fetch would need it.

## Where the build departs from the option the owner chose

Row 6 says a notch that costs more than it saves is not taken. That is a consequence written in the option the owner chose. Option (c) of `DISTILLATION.md` section 7 item 6, shown to the owner before the answer, reads "cost is added to exposure, so a notch that costs more than it saves is not taken", and the owner answered "Always". The loop that was built does not judge a notch by itself. It never starts a climb unless some tighter rung predicts a lower figure with cost included, and one notch on the way may cost more than it saves (`CONTRACT.md`, K16).

The reason is today's ladder and rows. The first notch, to `quarantine`, closes `egress`, and no published row needs `egress`. Judged by itself that notch costs GBP 5,500 a year and saves nothing, so it would never be taken, and the loop would stay at `baseline` for ever, red, with the shop serving. That is not what the owner was told to expect under decision 5 (`DISTILLATION.md` section 7 item 5: "the first automatic act could take a shop off the network"). Judged by where the climb ends, `isolated` lowers the figure from GBP 17,909,890.06 to GBP 1,643,518.63, cost included, so the climb is started.

The owner's word was "Always", and cost is in the compared figure on every line. The departure is the assistant's, delegated (K16). The owner can reverse it: with a notch judged by itself, the loop holds at `baseline` on today's inputs.

## Tolerance: what the industry does

There is no single norm. Two conventions are in common use, and both express the figure as a share of annual revenue.

- **Cyber-risk practice.** Appetite is set as a share of revenue and read against a curve of loss against likelihood. ISACA's guidance works in basis points of revenue. One vendor's tool offers 0.01%, 0.1%, 1% and 2% of revenue as ready-made thresholds, the 2% chosen to match the lower tier of GDPR fines. Most detailed examples come from vendors.
- **Audit materiality.** The amount that would matter to a reader of the accounts is conventionally 0.5% to 1% of revenue, or 5% of profit before tax. These are rules of thumb. The auditing standard sets no formula.

Insurance retentions are sized to what the firm can fund in cash. No credible share-of-revenue benchmark was found for them.

What each would mean for driftwood, whose declared turnover is GBP 86,000,000:

| Basis | Share of turnover | Tolerance a year |
|---|---|---|
| Today's fixture | 0.047% | GBP 40,000 |
| Cyber-risk preset, low | 0.1% | GBP 86,000 |
| Audit materiality, low end | 0.5% | GBP 430,000 |
| Audit materiality, high end | 1% | GBP 860,000 |
| Cyber-risk preset, high | 2% | GBP 1,720,000 |

**The assistant's pick: 0.5% of turnover.** The loop compares a mean year, and a figure that is tolerable every year should sit at the low end of what would be material in any one year. A share of turnover also scales with the firm, which today's fixtures do not: ludlow's GBP 5,000 is the smallest of the three for the largest firm. The figure is the owner's to set.

Sources:

- [ISACA Journal, 2024 volume 5: integrating cyber-risk quantification into risk governance](https://www.isaca.org/resources/isaca-journal/issues/2024/volume-5/from-measurement-to-management)
- [Kovrr: materiality analysis and loss thresholds](https://www.kovrr.com/blog-post/materiality-analysis-offers-risk-managers-data-driven-loss-thresholds)
- [Kovrr: quantifying cyber risk appetite](https://www.kovrr.com/blog-post/quantifying-cyber-risk-appetite-a-framework-for-decision-making)
- [Corporate Finance Institute: materiality threshold in audits](https://corporatefinanceinstitute.com/resources/accounting/materiality-threshold-in-audits)
- [Wikipedia: materiality (auditing)](https://www.wikipedia.org/wiki/Materiality_(auditing))
- [Scott Insurance: cyber risk trends](https://www.scottins.com/blog/cyber-risk-trends/)

## What follows from answers 1, 2 and 5 together

On today's inputs the first automatic act of the new loop could move driftwood's shop to a rung where it stops serving, on a penalty rate that nobody has counted and that is taken as 1. The owner was told this in decision 5 and chose it. Driftwood is a demonstration firm. Every ledger line will still print the share of the figure that is sourced.

## 15 November: "Do everything"

On the morning of 2026-11-15 the assistant's report listed two things that waited for the owner: K16, and which penalty rate ico publishes, with the tolerance. It also listed what was not done. Three paths had not yet run live: the daily schedule, a release with its dwell, and the proof on a cluster that stays up. Three things were left alone on purpose: feeds' second row, still priced although its text said the door was closed; the stale opening comments of the two cage files; and the words "FOR THIS EXAMPLE" in ico's litigation notes.

The owner's reply, in full: "Do everything".

Read as: leave to do the things listed as not done. It is not an answer to any open choice. It names no penalty rate, no tolerance, no machine or spend for a cluster that stays up, and it does not say to reverse K16. So no rate was published, the tolerance was not changed, no cluster was stood up, and K16 stays as built. Three other things wait for the owner in `LOOP.md`: the guard's hook, the hosted Renovate app and the quoted `id-token` key. They were not in the report the owner answered, and they are for the owner's own hand. They were left.

Done under it (`CONTRACT.md` section 11 has the detail):

- **Feeds' second row (K18, delegated).** Its N was read again at driftwood `main` `08ba2d0` and is 0, so the row prices at 0.00. It stays in the register, open, with `needs` empty. Feeds pull request 23 carried it as version 5.1.0, and the app's merge cut and signed `threat-register/v5.1.0`. From the first cycle that follows the tag, the figure at `isolated` falls by GBP 431.49, to GBP 1,643,087.14, still `saturated`. When this was written no cycle had yet followed it.
- **The cage comments.** Platform pull request 78, merged by the app, gives each cage file one true opening comment line. No rule changed and no tag was cut.
- **The litigation wording.** Ico pull request 14 removes the words "FOR THIS EXAMPLE" from three litigation notes. It is a draft, held so that one ico tag carries it with the penalty rate, if the owner chooses one.
- **The penalty-rate tables** were run again on `policy/v8.0.1` and feeds 5.1.0. None of the 18 outcomes changes. One threshold moves at four figures, from 0.2539 to 0.2540 (`penalty-rate/CHOICE.md`).

Not done:

- A release and its dwell. One can start only when a rate or a tolerance makes the loop release-ready, which is the owner's choice, and it then takes 7 days. The margin, the dwell and the tolerance were not touched to force one.
- The proof on a cluster that stays up. The owner has not named the machine or the spend.
- The guard's hook, the hosted Renovate app and the quoted `id-token` key, which are for the owner's own hand.

Put to the owner as four questions:

1. Which count of the penalty rate ico publishes, and which end of its interval.
2. The tolerance figure.
3. The machine or the spend for a cluster that stays up.
4. Whether K16 stays or is reversed.

## 15 November: the four answers

The four questions were put to the owner that day in one dialog. Each came with options the assistant had written, one of them marked as the assistant's recommendation. The owner chose one option for each. The labels in the third column are the options' own words, which the assistant wrote. The choice among them is the owner's. "Read as" is the assistant's reading.

| # | Question | The option the owner chose | The assistant's recommendation | Read as |
|---|---|---|---|---|
| 1 | Which counted penalty rate should ico publish? | "All reports: 0.0002095" | "Cyber only: 0.000529" | ico publishes the count over all breach reports, at its point value. The owner did not take the assistant's recommendation. |
| 2 | What is driftwood's tolerance? | "£430,000, 0.5% of turnover (Recommended)" | The same | The tolerance is 0.5% of turnover: GBP 430,000 at the declared turnover. It is no longer a fixture. The owner chose it from options the assistant offered. |
| 3 | Where should the cluster that stays up run? | "This Mac, kind left running (Recommended)" | The same | A kind cluster on the owner's own machine, left running. GitHub's runners cannot reach it, so the proof and the break test run from an agent session, not from the daily workflow, and are recorded as such. |
| 4 | Keep K16 or reverse it? | "Keep it (Recommended)" | The same | K16 stays. The owner has seen that it departs from the wording of the option chosen on 14 November, and has kept it. |

What the dialog told the owner with each option:

- **The rate.** "20 penalties over 95,466 breach reports of every kind. The most events, but its own researcher calls it too low for a serious breach. The shop reopens at either tolerance."
- **The tolerance.** "The low end of audit materiality. With any counted rate except the top of the serious-breaches count, the shop reopens." The question said the options were the assistant's suggestions, and that a release takes 7 to 8 days after the change lands.
- **The cluster.** "No spend. It needs Docker running and a few GB of disk, and stops when the Mac or Docker stops. GitHub's runners cannot reach it, so the proof and the break test would run from a session on this Mac, not from the daily workflow, and be recorded as such."
- **K16.** "A climb is judged by where it ends. Without this the loop can never reach the tightest rung on today's rows."

What follows from the answers is recorded where it lands: the rate in ico's feed, the tolerance in driftwood's `party.json`, and the proof on the cluster that stays up in `CONTRACT.md` section 11.
