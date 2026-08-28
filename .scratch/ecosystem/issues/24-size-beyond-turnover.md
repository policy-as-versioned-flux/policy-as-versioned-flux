# 24 — Size beyond turnover

Type: grilling (HITL)
Status: open
Blocked by: 07

## Question

Ticket 07 scales `pct_of_global_turnover` by turnover. Three regimes do not use turnover: PCI prices per month, HIPAA per violation, FCA on relevant revenue plus discretion. Settle how each reads the size facts (owner, 2026-08-19: "cost per customer"): does HIPAA scale by `data_subjects`, PCI by card-holding `customers`, FCA by a declared `relevant_revenue`? Does the party artefact need per-obligation counts, or do the four size facts suffice? Also: the `fx` feed's fetch cadence and source, which ticket 10 owns unless it is settled here.

## Notes
