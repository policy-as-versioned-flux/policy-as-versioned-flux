# 34 — Handbook as a compose-time render

Type: task (AFK)
Status: open
Blocked by: none

> **Unblocked 2026-09-06 (record correction).** This line read `Blocked by: 09` until today. Ticket 09 resolved on 2026-08-28; nobody re-read this line, so the ticket sat behind a blocker that no longer existed. A `Blocked by:` line is a claim about another file and rots the same way a cited figure does (ticket 80).

## Question

Publish the generator as a platform tool each adopter's compose step runs over its composed artefact, landing the render in the same PR and gitsign tag; wire verify-fresh.sh into the gate; retire verify.sh; move claude -p summaries into a human-run skill.

## Notes

Graduated 2026-08-28 from ticket 13's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
