# 02 — Audit all 27 talk-spec build ticket statuses

Type: task
Status: open
Blocked by: none

## Question

What is actually done in `.scratch/talk-spec/build/`? 25 of 27 tickets read `Status: ready-for-agent`
despite the estate demonstrably working; only 14 and 17 carry honest `REOPENED — NOT DONE` detail.
The board cannot be trusted as a picture of reality.

**The job:** for each ticket 01–27, verify its acceptance criteria against the actual tree and the
verify scripts, then set an accurate Status and tick/untick its ACs with a citation (file, test, or
command output) — the same discipline the `twin/` capability checklists use. Where a ticket is
genuinely incomplete, say so with the specific unmet AC rather than a blanket status.

**Method (owner's instruction):** parallel, medium-effort Sonnet agents, one per ticket or small
batch. Do not let an agent tick an AC without a citation.

Report the corrected done/not-done split. Expect this to surface work nobody is tracking.
