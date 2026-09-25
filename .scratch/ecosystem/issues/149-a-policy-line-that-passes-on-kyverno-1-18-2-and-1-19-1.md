# 149 — A policy line that passes on Kyverno 1.18.2 and 1.19.1

Type: task
Status: open
Blocked by: 146, and the owner's authorisation for a signed `policy/v5.0.x` tag

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 3, 4, 10 and 12 (delegated), and
ADR-0033 point 6.

The diagnosis is in `.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`. On Kyverno 1.19.1,
the 5.0.0 cage-tier body does not compile, and two cage-netpol fixture rows fail. The tagged 5.0.0
bodies cannot change, so the fix is a new line. The line carries three changes only:

1. **`string(variables.tier)` in cage-tier.** The diagnosis measured that this compiles on both
   engines and gives the same mutated output as the tagged body.
2. **All five bodies at `policies.kyverno.io/v1`.** The diagnosis measured that this changes no
   result on either engine. The `v1` and `v1alpha1` schemas are identical in both engines' CRDs.
3. **A cage-netpol fixture that compares generated documents.** Kyverno 1.19 returns no result
   for a GeneratingPolicy that does not match (upstream PR #16505). So a `result: skip` row reads
   "Fail / Not found", and no body change fixes it. Instead:
   - The two `result: skip` rows leave `kyverno-test.yaml`.
   - For each trigger, the grader runs `kyverno apply -o` and compares the generated documents
     with an expected set in the fixture. For an unmatched trigger the expected set is empty.
   - A new trigger tests the `is-caged` gate alone: a pod that is not caged, at a tier that
     restricts reach. Today no row tests that gate. With it removed, 1.18.2 still gives 11/0.
   - The grader continues to read the old fixture format, because it grades the tagged 5.0.0
     fixtures.

Write the red tests first: the tier gate removed must fail on both engines, and the `is-caged`
gate removed must fail on both engines.

Then the cut. The engine computes the bump. The diagnosis predicts no behaviour change, so a patch
is expected, but the engine decides. The new element's `tested_engines` is `[1.18.2, 1.19.1]`. It
is written only after every cell passes, and ticket 146's fix to the cut script keeps it. 5.0.0
stays served, because it still supports 1.18.2. No adopter moves to the new line in this ticket.

## Done

Platform `distribution/versions.yaml` carries the new element, with its signed tag, its commit and
`tested_engines: [1.18.2, 1.19.1]`. On `origin/main`, the hub cage-engine check grades three cells
and all three pass: 5.0.0 on 1.18.2, the new line on 1.18.2, and the new line on 1.19.1.

## Notes

- The diagnosis ran the offline CLI only. It says nothing about admission on a live cluster.
  Ticket 150 measures that.
- Kyverno 1.19.1 writes no pass PolicyReport entry for an unmatched pod, and 1.18.2 writes one.
  This was measured offline with `kyverno apply -p`. Ticket 150 measures it live.
