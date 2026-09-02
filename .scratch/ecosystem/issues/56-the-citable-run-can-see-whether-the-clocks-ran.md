# 56 — The citable run can see whether the clocks ran

Type: task (AFK)
Status: open
Blocked by: none

## Question

verify-schedules' live half SKIPs on every CI run because the gate step deliberately carries no GitHub credential — a recorded security decision whose consequence (permanent blindness to clock liveness) is recorded nowhere. Grade clock health with a read-scoped credential isolated from the untrusted verify scripts: a separate workflow step or job that runs before the gate, queries the runs API, and hands a verdict file into the TRUTH accounting; or an equivalent design that keeps the token out of the eight orgs' unpinned scripts. Reconcile with ADR-0024 and correct ticket 28's over-claiming Answer with a dated note. Done = "ran inside its period" grades for real on a scheduled run without exposing a credential to third-party scripts.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M6 (verify-schedules blind, 3 confirmed findings).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Two additions. verify-schedules can never PASS on the clock for a second reason: ico, nist and platform fetch.yml carry no `gh pr create`, so schedules.py emits three unconditional D2 SKIPs even with a token. And its ruleset half emits no line at all when it cannot look (`if live and ...`), so eight server-side questions vanish, a fourth outcome against §5's three; ticket 83 item 4 fixes the silence. Five real clocks were red on 2026-09-02 and this surface showed one SKIP. Record: REVIEW-2026-09-02.md R8, security/SS-07 for the write-credential half.
