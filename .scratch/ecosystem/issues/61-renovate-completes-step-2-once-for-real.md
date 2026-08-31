# 61 — Renovate completes step 2 once, for real

Type: task (AFK)
Status: open
Blocked by: none

## Question

Every Renovate PR ever raised was autoclosed; every landed bump was hand-made; and the feed pin step 2 prices cannot arrive by Renovate at all because the customManager over inherits[] (deferred by ticket 22 to ticket 21, never written) does not exist. Write that customManager; make a Renovate bump able to go green (the pin file, party.yaml's inherits entry and the composed/ re-render must move together — a completing workflow job on the Renovate branch is the likely shape); then let threat-register v2 (or the next real tag) arrive as a Renovate PR and have a human merge it — the first real step-2 event, which triggers propose-tier for real. Done = one merged Renovate PR on one adopter, graded by a check that reads the PR record, not a simulation.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M8 (step 2 never real / feed pin un-raisable, 2 confirmed findings).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).
