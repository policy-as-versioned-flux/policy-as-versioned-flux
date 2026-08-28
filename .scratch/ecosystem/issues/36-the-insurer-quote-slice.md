# 36 — the insurer quote slice

Type: task (AFK)
Status: open
Blocked by: 10, 21, 25

## Question

Insurer party.yaml with roles [publisher] and inherits[] (platform, driftwood exposure); quote-driftwood feed with priced_against, validity, conditions; scheduled pricer opening a PR under perspective insurer; verify script (retained + transferred + excluded == simulated total, premium from pinned quote, expiry priced, breached condition priced per consequence) wired into verify-all.sh.

## Notes

Graduated 2026-08-28 from ticket 14's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
