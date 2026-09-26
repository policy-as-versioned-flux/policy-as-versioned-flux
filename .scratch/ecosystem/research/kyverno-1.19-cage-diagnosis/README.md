# Kyverno 1.19 and the 5.0.0 bodies: diagnosis, 2026-09-25

Ticket 71 asked for this capture. Ticket 54 recorded the cage-netpol difference under 1.19 in prose
only. This directory holds the capture.

One agent ran the diagnosis. A second agent downloaded the engines again, extracted the tagged bytes
again, and tried to refute each claim. The second agent confirmed the classification and corrected
two claims. This file states the corrected result. On 2026-09-26 a review found that some results
were not committed. The captures below were then copied in from the session's scratch directory.

## Method

- Engines: the Kyverno CLI 1.18.2 and 1.19.1, darwin_arm64, downloaded from the GitHub releases.
  `kyverno version` reports commits 945ac9ce and 40ec788d, which are the commits of the upstream
  tags. The checksums are in `captures-engine-versions.txt`.
- Bytes: `policy/v5.0.0` from the platform repo, read with `git archive`, never the working tree.
- Harness: `engine_compatibility.py` in this directory is a byte-identical copy of platform
  `computed-semver/engine_compatibility.py` at commit 97dd40d (sha256 prefix 45e8f5cd). `driver.py`
  calls `_published_row` directly, because `check()` refuses an engine that is not in
  `tested_engines`. It calls `_matrix` on scratch copies of edited trees. `verifier/vdriver.py` is
  the second agent's own driver.
- Only the offline CLI ran. No admission controller and no background controller ran. Every result
  below is an offline CLI result.
- Paths inside the captures are replaced: `<scratch>` for the session's scratch directory, `<tmp>`
  for a system temporary directory. `<work>` in `captures/c-apply/apply-policyreport-*.txt` was
  written by the first agent's own commands. Nothing else is changed.

## Results

| Variant | 1.18.2 cage-tier | 1.18.2 cage-netpol | 1.19.1 cage-tier | 1.19.1 cage-netpol |
|---|---|---|---|---|
| Tagged 5.0.0 | 13/0 | 11/0 | compile error | 9/2 |
| `string(variables.tier)` only | 13/0 | 11/0 | 13/0 | 9/2 |
| The same, plus five bodies at `policies.kyverno.io/v1` | 13/0 | 11/0 | 13/0 | 9/2 |

Captures: `assertion-counts.txt`, `captures/a1-row-*`, `captures/b-string-tier-*`,
`captures/f-v1-on-*`, and the second agent's `verifier/captures/row-*`, `b-*`, `fb-*`, `ft-*`.

1. **cage-tier.** Under 1.19.1, `"posture.acme.io/tier": variables.tier` does not compile:
   `expected type 'string' but found 'dyn'`. `string(variables.tier)` fixes it on both engines. The
   mutated output does not change: `kyverno apply` gives 26 equal documents for the tagged body on
   1.18.2 and for the fixed body on both engines. See `diffs-b-string-tier.cage-tier.diff` and
   `verifier/captures/tier-apply/`. In that directory, `work` is the tagged body and `workb` is the
   body with `string(variables.tier)`.
2. **cage-netpol.** Under the offline CLI, the generated NetworkPolicies are the same on both engines
   (9 documents, equal once parsed). Only the two `result: skip` rows change. These rows are for
   triggers that fail the policy's `matchConditions` (`caged-baseline` and `healthy`). 1.18.2
   reports `Pass / Excluded`. 1.19.1 reports `Fail / Not found`. See
   `diffs-c-netpol-test-table-1.18.2-vs-1.19.1.diff`, `diffs-c-generated-text.diff` and
   `captures/c-apply/`.
3. **The cause is an engine response change.** Upstream commit fd90931fad (PR #16505, "add
   auditAnnotations support to GeneratingPolicy") changed the behaviour on a `matchConditions` miss.
   1.18.2 returned a pass with nothing generated. 1.19.1 returns no result. The CLI then drops the
   response and prints "Not found". The PR text does not mention this change. On a miss,
   ValidatingPolicy and MutatingPolicy return a skip in both versions. See
   `diffs-kyverno-src-gpol-*.diff`, `diffs-kyverno-src-cli-test-output.go.diff` and `pr-16505.txt`.
4. **The skip rows were a real check on 1.18.2.** They go red if the trigger generates anything:
   with the tier gate removed, 1.18.2 gives 10/3 (`verifier/captures/g-no-tiergate-1.18.2/`; the
   edited body is `verifier/diffs-g-no-tiergate.cage-netpol.diff`). They
   never compared the status word (`captures/c-minimal-vacuous-skip.txt`). On 1.19.1 no body change
   that was measured makes them green: a miss gives "Not found", and a generation gives "Want skip,
   got pass" (`captures/e-exprgate-1.19.1/`). So 1.19.1 loses a check that worked.
5. **A PolicyException is not a fix.** A fixture-carried PolicyException makes the row green on
   1.19.1. But Kyverno evaluates the exception before the policy's `matchConditions`, so the row
   stays green even with the gate deleted from the policy. See `verifier/minimal/polex-*` and
   `verifier-minimal-transcript.txt`.
6. **A gap in the fixture.** With the `is-caged` gate removed, 1.18.2 still gives 11/0
   (`verifier/captures/g-no-cagedgate-1.18.2/`; the edited body is
   `verifier/diffs-g-no-cagedgate.cage-netpol.diff`). The `healthy` trigger defaults to tier baseline,
   so the tier gate still excludes it. No row tests the `is-caged` gate alone.
7. **PolicyReports.** Under `kyverno apply -p`, 1.18.2 writes a pass entry for each of the two
   unmatched pods. 1.19.1 writes none (pass count 5 on 1.18.2, 3 on 1.19.1). See
   `diffs-c-apply-policyreport-1.18.2-vs-1.19.1.diff`. This is offline only.
8. **The other three bodies.** `require-nonroot`, `stamp-posture` and `posture-trust-boundary` were
   applied with `kyverno apply` to the 13 cage-tier fixture pods. Their per-resource results are the
   same on both engines, at `v1alpha1` and at `v1`. So all three compile on 1.19.1. Their own
   fixtures did not run. See `captures/f-other-bodies-compare.txt` and `verifier/captures/other/`.
9. **`v1`.** For generating, mutating and validating policies, the `v1` and `v1alpha1` schemas are
   identical in both engines' CRDs (`captures/f-crd-schema-compare.txt`). Moving the five bodies to
   `v1` gave the same results in every cell (`captures/f-v1-vs-v1alpha1-output-compare.txt`). That
   file marks one cell `DIFFERS`: 1.19.1 cage-tier on the tagged bytes. Both runs of that cell are
   the same compile error, and only the resource that the error names first differs. The move does
   not fix either 1.19 issue.

## Classification

The cage-tier failure is a policy defect with a one-token fix that keeps the behaviour. The
cage-netpol failure is a change in how Kyverno reports a GeneratingPolicy that did not match. Under
the offline CLI, the generated documents are the same, and the PolicyReport differs. The fixture's
skip rows cannot express a "generates nothing" check on 1.19.1.

## Limits

- Only the offline CLI ran, with no admission. The live behaviour is ticket 150's question.
- Only 1.18.2 and 1.19.1 ran. Ticket 54's 1.19.0 did not run.
- The machinery bodies that the composer renders did not run here. `orphan-cage` and
  `governed-namespace-guard` build the same label map as cage-tier, with the literal `'isolated'`
  as their tier. A later review run compiled both on 1.19.1, but that run is not captured here.
- The Kyverno source came from codeload tag tarballs, which have no integrity pin.
- The claim that no body fix exists rests on the source and on the levers measured: the expression
  gate, the `objectSelector` gate and the exception. The search was not exhaustive.
- `minimal/run.sh` needs `BIN` set to a directory that holds `bin/<version>/kyverno`.
  `verifier/minimal/run.sh` and the two drivers still name the scratch layout, so they document the
  runs and do not re-run from this directory.
