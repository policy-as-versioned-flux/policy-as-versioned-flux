# 01 — Create feeds and insurer orgs

Type: task (HITL)
Status: open
Blocked by: none

## Question

Create the two missing publisher parties as real GitHub organisations: `policy-as-versioned-feeds` (threat register, CVE, EOL, market intel, prediction-market moves, news events) and `policy-as-versioned-insurer` (signed quotes against an adopter's declared attachment, limit and exclusions). Install the Renovate app on both (Renovate Only, not silent, require-config off). Record the org URLs and who holds admin.

## Notes

Owner action. Decided 2026-08-28 (charting Q4): real orgs now. Checklist for the owner: 1) create both orgs with the `policy-as-versioned-` prefix; 2) install Renovate as on the six existing orgs; 3) create an empty `feeds` repo and an empty `insurer` repo; 4) grant the assistant push via the existing gh identity. Resolved when both repos exist and Renovate is onboarded.
