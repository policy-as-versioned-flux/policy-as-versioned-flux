# 70 — The observation lane is detectively enforced and honestly recorded

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 58 Q4(b): the repos stay public, so push-time prevention is impossible (GitHub refuses push rulesets on public repos, and required_signatures would reject gitsign). Build the detective control: the gate's lane verifier grades every commit on the observation refs against the lane rules as a named check, and a violation is a red. Amend ADR-0023 with a dated note recording the limitation and the revisit trigger (going private). Correct ticket 28's Answer, whose ruleset plan was falsified after resolution, with a dated note. Done = the check runs in the gate and the record matches reality.

## Notes

Graduated from ticket 58 (2026-08-31), decision provisional on a bare "Agree".
