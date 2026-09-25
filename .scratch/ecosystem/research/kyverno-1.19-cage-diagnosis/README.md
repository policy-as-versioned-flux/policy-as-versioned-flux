# Kyverno 1.19 and the 5.0.0 cage bodies: diagnosis, 2026-09-25

Ticket 71 asked for this capture. Ticket 54 recorded the cage-netpol difference under 1.19 in prose
only. This directory holds the capture.

One agent ran the diagnosis. A second agent downloaded the engines again, extracted the tagged bytes
again, and tried to refute each claim. The second agent confirmed the classification and corrected
two claims. This file states the corrected result.

## Method

- Engines: the Kyverno CLI 1.18.2 and 1.19.1, darwin_arm64, downloaded from the GitHub releases.
  `kyverno version` reports commits 945ac9ce and 40ec788d. These are the commits of the upstream tags.
- Bytes: `policy/v5.0.0` from the platform repo, read with `git archive`, never the working tree.
- Harness: a byte-identical copy of platform `computed-semver/engine_compatibility.py`. `driver.py`
  calls `_published_row` directly, because `check()` refuses an engine that is not in
  `tested_engines`. It calls `_matrix` on scratch copies of edited trees.
- No in-cluster admission ran. Every result is from the offline CLI.

## Results

| Variant | 1.18.2 cage-tier | 1.18.2 cage-netpol | 1.19.1 cage-tier | 1.19.1 cage-netpol |
|---|---|---|---|---|
| Tagged 5.0.0 | 13/0 | 11/0 | compile error | 9/2 |
| `string(variables.tier)` only | 13/0 | 11/0 | 13/0 | 9/2 |
| The same, plus all five bodies at `policies.kyverno.io/v1` | 13/0 | 11/0 | 13/0 | 9/2 |

1. **cage-tier.** Under 1.19, `"posture.acme.io/tier": variables.tier` does not compile: `expected
   type 'string' but found 'dyn'`. `string(variables.tier)` fixes it on both engines. The mutated
   output does not change: `kyverno apply` gives 26 equal documents for the tagged body on 1.18.2
   and for the fixed body on both engines. See `diffs-b-string-tier.cage-tier.diff`.
2. **cage-netpol.** The generated NetworkPolicies are the same on both engines (9 documents, equal
   once parsed). Only the two `result: skip` rows change. These rows are for triggers that fail the
   policy's `matchConditions` (`caged-baseline` and `healthy`). 1.18.2 reports `Pass / Excluded`.
   1.19.1 reports `Fail / Not found`. See `diffs-c-netpol-test-table-1.18.2-vs-1.19.1.diff`.
3. **The cause is an engine response change, not a policy change.** Upstream commit fd90931fad
   (PR #16505, "add auditAnnotations support to GeneratingPolicy") changed the behaviour on a
   `matchConditions` miss. 1.18.2 returned a pass with nothing generated. 1.19.1 returns no result.
   The CLI then drops the response (`if res.Result == nil { continue }`) and prints "Not found".
   The PR text does not mention this change. On a miss, ValidatingPolicy and MutatingPolicy return
   a skip in both versions. See `diffs-kyverno-src-gpol-*.diff` and `pr-16505.txt`.
4. **The skip rows were a real check on 1.18.2.** They go red if the trigger generates anything:
   with the tier gate removed, 1.18.2 gives 10/3. They never compared the status word. On 1.19.1 no
   body change measured makes them green: a miss gives "Not found" and a generation gives "Want
   skip, got pass". So 1.19.1 loses a check that worked.
5. **A PolicyException is not a fix.** A fixture-carried PolicyException makes the row green on
   1.19.1. But Kyverno evaluates the exception before the policy's `matchConditions`, so the row
   stays green even with the gate deleted from the policy.
6. **A gap in the fixture.** With the `is-caged` gate removed, 1.18.2 still gives 11/0. The
   `healthy` trigger defaults to tier baseline, so the tier gate still excludes it. No row tests
   the `is-caged` gate alone.
7. **PolicyReports.** Under `kyverno apply -p`, 1.18.2 writes a pass entry for each unmatched pod.
   1.19.1 writes none (pass count 5 on 1.18.2, 3 on 1.19.1). This was measured offline only, not on
   a live cluster.
8. **`v1`.** For generating, mutating and validating policies, the `v1` and `v1alpha1` schemas
   are identical in both engines' CRDs. Moving all five bodies to `v1` gave the same results in
   every cell. The move does not fix either 1.19 issue.

## Classification

The cage-tier failure is a policy defect with a one-token fix that keeps the behaviour. The
cage-netpol failure is a change in how Kyverno reports a GeneratingPolicy that did not match. The
policy's behaviour is the same. The fixture's skip rows cannot express a "generates nothing" check
on 1.19.1.

## Limits

- Only the offline CLI ran. There was no admission and no background controller.
- Only 1.18.2 and 1.19.1 ran. Ticket 54's 1.19.0 did not run.
- The Kyverno source came from codeload tag tarballs, which have no integrity pin.
- The claim that no body fix exists rests on the source and on the levers measured: the expression
  gate, the `objectSelector` gate and the exception. The search was not exhaustive.
- `minimal/run.sh` needs `BIN` set to a directory that holds `bin/<version>/kyverno`.
