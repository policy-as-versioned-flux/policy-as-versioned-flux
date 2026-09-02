# 88 — The second identity

Type: task (HITL)
Status: open
Blocked by: none

## Question

Ticket 75 Q6 and Q14 decided that principle 5 binds for the demonstration and that, for the development window, the assistant reviews and merges as a second identity while the owner authors and pushes. Today one identity exists (chrisns) and the only app installed on the org is Renovate. Nothing can require a review from a different identity until a second identity exists.

The owner does, in this order:

1. Create one machine identity for the assistant. Preferred: a GitHub App owned by the org, named so a reader of any PR sees it is the assistant (for example `fable-reviewer`), with `contents: write`, `pull_requests: write` and `metadata: read`, installed on all nine repositories. Second choice: a machine user account with the same reach. Record the choice and the identity's name here.
2. Put the credential where the assistant's shell can read it without it entering any file in any repo. Record the location, not the value, here.
3. Tell the assistant. The assistant then verifies the identity by reading its own login through the API and records the result here.

After 1 to 3, the assistant does:

4. Flip `twin/ENACT_MODE` to `development` and add a dated line to the `enact_guard.py` docstring that cites ticket 75 Q6 and Q14 and names the identity. The guard's `operations` behaviour stays tested by the harness invariant.
5. Update the memory note on push and merge authorisation so a later session does not refuse what this ticket permits.

Done = a PR authored by chrisns is approved and merged by the second identity on one repo, and the merge is recorded here with its URL. Ticket 87 then applies the protection that requires it.

## Notes

Charted by ticket 75 (Q6, Q14). Blocks 87 and 74. The guard's own docstring already names this shape: "a credential that cannot merge" was the upgrade path; the owner chose the reverse for the development window, and the narrative still says a human merges. Ticket 95 records the theatre in NORTH-STAR §6.
