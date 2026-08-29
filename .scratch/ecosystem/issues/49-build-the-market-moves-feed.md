# 49 — Build the market-moves feed

Type: task (AFK)
Status: resolved
Blocked by: 10, 21

## Question

In policy-as-versioned-feeds/feeds: the versioned signed rule file (categories, liquidity floor, horizon window, seeded valve, and the change threshold), the Polymarket adapter, the daily LLM-free schedule that appends to the observation branch, the series-only payload_schema with no probability-shaped field, `publishes[]` entry, and a verify script the gate discovers via the feeds clone. Read Polymarket redistribution terms before the first tag. Definition of done: verify-feed-contract.sh passes and the twin binds the pinned series.

## Notes

Graduated 2026-08-28 from ticket 22's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The market-moves feed publishes a series from one mechanical rule over one source. The clock opens a PR only on the feed own threshold and appends sub-threshold readings to the observation branch. Classification is a skill a human runs.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.
