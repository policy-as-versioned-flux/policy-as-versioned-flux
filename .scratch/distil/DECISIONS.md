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

- **Tags: given and used.** Each tag is cut by its repository's own signing workflow, and only at a commit the loop has already run against, because a tag can never be moved or deleted.
- **The key in feeds and ico: granted and not used.** The design that was then built (`CONTRACT.md`) leaves nothing in feeds or ico that would read the key: a publisher's only unattended act is to cut a tag, and the default token can do that. A secret with no reader is redundant, so it was not added. A returning fetch would need it.

Two questions were settled by the write-up as following from the owner's sentence. The owner has not commented on either: the pound is a real figure, not a ranking; and the exposure compared is the whole organisation's.

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
