# 135 — A lifted app gets no verdict from the bottom rung

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Truth run 314 graded `verify/lifted-apps/verify-lifted-apps.sh`
FAIL for the first time, after each adopter moved to platform tools v3.3.0 and its composed set
to v2.0.0 with the array 4.0.0 and 5.0.0 (tickets 111, 130). Its capture:

```
FAIL ledger: tuppence's composed set does not admit tuppence/gitops/apps/ledger.yaml -- policy
cage-baseline-4-0-0 produced no verdict at all (no row in the kyverno table) (pass: 8, fail: 0, ...)
```

and the same for driftwood's storefront and ludlow's reports. Run 310 graded it PASS.

What this ticket owes:

1. Establish which is true: the served set really fails to cage these workloads at CREATE, or the
   check asks a policy for a verdict that the new composition no longer gives, for example
   because the rung moved, a policy was renamed, or the check renders the set differently from
   how the adopter's ResourceSet serves it. Measure under kyverno 1.18.2 with each adopter's
   served set at v2.0.0.
2. If the cage is wrong, fix it where it is wrong and say which release carries the fix. If the
   check is wrong, make it ask the question the adopter's served set answers today, and keep a
   planted failure that it still catches.

## Done

`verify-lifted-apps.sh` grades each lifted app by what the served set does to it, and the reason
for run 314's FAIL is recorded.
