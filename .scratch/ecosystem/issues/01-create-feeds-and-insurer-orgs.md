# 01 — Create feeds and insurer orgs

Type: task (HITL)
Status: resolved
Blocked by: none

## Question

Create the two missing publisher parties as real GitHub organisations: `policy-as-versioned-feeds` (threat register, CVE, EOL, market intel, prediction-market moves, news events) and `policy-as-versioned-insurer` (signed quotes against an adopter's declared attachment, limit and exclusions). Install the Renovate app on both (Renovate Only, not silent, require-config off). Record the org URLs and who holds admin.

## Notes

Owner action. Decided 2026-08-28 (charting Q4): real orgs now. Checklist for the owner: 1) create both orgs with the `policy-as-versioned-` prefix; 2) install Renovate as on the six existing orgs; 3) create an empty `feeds` repo and an empty `insurer` repo; 4) grant the assistant push via the existing gh identity. Resolved when both repos exist and Renovate is onboarded.

## Answer

Resolved 2026-08-28.

- Organisations created (free plan, owned by the personal account, contact chris@cns.me.uk, Terms accepted by the assistant with the owner's explicit permission): `policy-as-versioned-feeds` (id 321982950) and `policy-as-versioned-insurer` (id 321983100). Created through the owner's Chrome session.
- Repositories created with `gh`: https://github.com/policy-as-versioned-feeds/feeds and https://github.com/policy-as-versioned-insurer/insurer, both public, both empty.
- Renovate GitHub App installed on both orgs, all repositories, by the owner from a phone after a sudo prompt (verified with `gh api orgs/<org>/installations`: `renovate repos=all` on both).
- Mend dashboard settings (Renovate Only, Silent mode off, Automated PRs on, Require config file off): set by the owner in the Mend wizard. Not verified by the assistant, because the dashboard needs a GitHub sign-in in the browser. Check: https://developer.mend.io/github/policy-as-versioned-feeds/-/settings?tab=renovate and the insurer equivalent.
- Admin: the owner (chrisns). The assistant pushes with the existing gh identity.
