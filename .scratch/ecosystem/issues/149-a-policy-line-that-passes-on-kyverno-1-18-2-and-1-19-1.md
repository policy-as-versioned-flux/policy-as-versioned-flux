# 149 — A policy line that passes on Kyverno 1.18.2 and 1.19.1

Type: task
Status: resolved
Blocked by: 146, and the owner's authorisation for the signed policy tag

## Question

Graduated 2026-09-25 from grilling ticket 71, decisions 3, 4, 10, 12, 15, 16 and 19 (delegated),
and ADR-0033 points 4 and 6.

The diagnosis is in `.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`. On Kyverno 1.19.1,
the 5.0.0 cage-tier body does not compile, and two cage-netpol fixture rows fail. The tagged 5.0.0
bodies cannot change, so the fix is a new line. It is the next declared line, so it also carries a
retirement that two records already commit to it. It carries four changes:

1. **`string(variables.tier)` in cage-tier.** The diagnosis measured that this compiles on both
   engines and gives the same mutated output as the tagged body.
2. **`posture-trust-boundary` retires** (decision 15). Ticket 89's register
   (`verify/deny-is-not-a-rung/register.yaml`) and `NORTH-STAR.md:54` commit its retirement to the
   next declared line, which the register assigns to ticket 84. The reason is recorded in the
   register: `stamp-posture` already enforces the boundary as a mutation, so the Deny cannot fire.
   Other platform code reads the rule, so it changes too:
   - `distribution/render-version-tree.py` makes the rule a mandatory member of every tree;
   - `compose/composition.py` uses it as its Deny-inheriting selfcheck fixture;
   - `computed-semver/cage_engine.py` cases 15a and 15b read it from the rendered tree;
   - `currency-controller/verify-currency.sh` reads it.

   Update the register's `state:` when the line is cut.
3. **The four remaining bodies move to `policies.kyverno.io/v1`.** The diagnosis measured, under
   the offline CLI, that the move changes no result for the two cage matrices, and no per-resource
   result for `require-nonroot` and `stamp-posture` under `kyverno apply`. The `v1` and `v1alpha1`
   schemas are identical in both engines' CRDs.
4. **A cage-netpol fixture that compares generated documents.** Kyverno 1.19 returns no result for
   a GeneratingPolicy that does not match (upstream PR #16505). So a `result: skip` row reads "Fail
   / Not found", and no body change that was measured fixes it. Instead:
   - The two `result: skip` rows leave `kyverno-test.yaml`.
   - For each trigger, the grader runs `kyverno apply -o` and compares the generated documents
     with an expected set in the fixture. For an unmatched trigger the expected set is empty.
   - A new trigger tests the `is-caged` gate alone: a pod that is not caged, at a tier that
     restricts reach. Today no row tests that gate. With it removed, 1.18.2 still gives 11/0.
   - `graded/verify-graded.sh` runs the same fixture, so it gets the same comparison.
   - The grader continues to read the old fixture format, because it grades the tagged 5.0.0
     fixtures.

Write the red tests first: the tier gate removed must fail on both engines, and the `is-caged`
gate removed must fail on both engines.

**Where the changes are made.** `distribution/render-version-tree.py` renders the new tree from the
authoring copies: `graded/policies/cage-tier.yaml`, `graded/policies/cage-netpol.yaml` and
`posture/policies/*.yaml`. `require-nonroot` is written by hand for each version. The fixture is
`graded/tests/cage-netpol`.

**Records that change with the declaration, in the same change.**

- `distribution/tests/require-nonroot/kyverno-test.yaml` loads the new line, because
  `verify-coexistence.sh` requires its `policies:` list to equal the declared array. The new line is
  the second of the three declared lines that ticket 84 counts.
- Hub `verify/refusal-by-another-name/register.yaml` names the new cage-tier copy in its row, with
  a dated reason, because the scan grades an uncut declared tail.

**The cut.** The new element carries `tested_engines: [1.18.2, 1.19.1]` from the moment it is
declared. Ticket 146's candidate grade grades it on the declaring commit, and the cut is signed
only after every cell passes on both engines. The element declares its `bump`, and the gate grades
the declared bump against the computed one (ADR-0011). The retirement in item 2 can make the
computed bump larger than a patch. If it is a major, each institution needs a written acceptance
before an adopter moves onto the line. The owner writes it. 5.0.0 stays served, because it still
supports 1.18.2. No adopter moves to the new line in this ticket.

## Done

Platform `distribution/versions.yaml` carries the new element, with its signed tag, its commit and
`tested_engines: [1.18.2, 1.19.1]`. On `origin/main`, the hub cage-engine check grades three cells
and all three pass: 5.0.0 on 1.18.2, the new line on 1.18.2, and the new line on 1.19.1.
`verify-coexistence.sh` and the refusal scan read the new line without a red.

## Notes

- The diagnosis ran the offline CLI only. It says nothing about admission on a live cluster.
  Ticket 150 measures that.
- Under `kyverno apply -p`, 1.19.1 writes no pass PolicyReport entry for the two unmatched pods, and
  1.18.2 writes one for each. This is offline only.

## Comments

**2026-09-26, upstream status.** Upstream already tracks the `result: skip` change as
kyverno/kyverno#17382. PR #17388 fixed it in the CLI on `main` on 2026-09-25, and no release carries
the fix yet. The engine still returns no result on a `matchConditions` miss. When a release carries
the fix, a `result: skip` row passes again as `Pass / Excluded`, which does not compare the status
word. So item 4 stands: the fixture compares generated documents. Details are in the research
README, section "Upstream status".

## Resume implementation, 2026-10-03

The compatibility candidate uses v1 policy APIs, string-typed tier output and a generated-document proof, and retires the candidate posture Deny body. The exact 1.18.2 and 1.19.1 cells pass. The isolated 6.0.0 to 6.0.1 pairwise comparison computes patch; the full publisher window is being measured separately before any cut. No signed candidate release is claimed.

The owner delegated the implementing decisions on 2026-10-03: "you tell me, you control them all, you don't need me to answer". This is recorded as delegated, not as an invented institution signature.

**Full-window correction, 2026-10-03.** The actual publisher retains both 5 and 6 when grading the compatibility candidate. That complete supported window computes a major bump and would quarantine a declared 6.0.1 patch. The final candidate therefore declares **7.0.0**; its publisher dry run passes cleanly as major and all six declared engine cells pass. The security-only intermediate remains 6.0.0, with four passing cells. All three adopters have explicitly delegated major-7 acceptance records. Frozen 5 and 6 bodies are unchanged. The old 6.0.1 receipts above are historical measurements, not a release target. Signed delivery is tracked in the dated implementation status and platform delivery records.

## Answer

**2026-10-18, authentic final line reconciled.** The delivered compatibility line is **7.0.0**.
The [immutable declared array](https://github.com/policy-as-versioned-platform/platform/blob/b91bdbb7413aed4edf578114635d20172e45fd35/distribution/versions.yaml)
records `policy/v7.0.0`, its evidence commit `393a40f707f2b23a3a174696a0c84a8473297ca9`,
and `tested_engines: [1.18.2, 1.19.1]`. The genuine signed tag targets
[703eff6aee959843c4160aa54fd03413f62858cc](https://github.com/policy-as-versioned-platform/platform/commit/703eff6aee959843c4160aa54fd03413f62858cc),
after the evidence commit; those two fields have different intended meanings. The original
[cut 37185354470](https://github.com/policy-as-versioned-platform/platform/actions/runs/37185354470)
and [policy release 37187107091](https://github.com/policy-as-versioned-platform/platform/actions/runs/37187107091)
completed with genuine signatures and claims. Frozen 5.0.0 and 6.0.0 remain unchanged and
served. Historical 6.0.1 was a rejected full-window patch proposal, not the release target.

The final source contains the string-typed tier, retires `posture-trust-boundary` from the new
line, uses `policies.kyverno.io/v1` for its four remaining bodies, and compares generated
netpol documents while retaining the old fixture format. The full-window computation and
publisher proof establish the major bump; the dated delegated major-7 acceptance records and
actual owner-authorized cut are delivered. This ticket does not move an adopter onto the line.

The [recorded TRUTH run 432 grade table](https://github.com/policy-as-versioned-flux/policy-as-versioned-flux/blob/b0911618e238abfd719ef95171869fc41d8688a8/talk/captures/_grades.tsv)
gives `.estate-clone/platform/computed-semver/verify-cage-engine.sh` PASS at platform
`b91bdbb7413aed4edf578114635d20172e45fd35`: all six declared cells passed. They include the
original required three: 5.0.0 on 1.18.2 and 7.0.0 on both 1.18.2 and 1.19.1. The same recorded
table gives `.estate-clone/platform/distribution/verify-coexistence.sh` **SKIP**, with the
offline proof holding and the local-kind live tail unobserved, and
`verify/refusal-by-another-name/verify-refusal-by-another-name.sh` **SKIP**, because its mutation
checks could not look. These are the requested nonred observations with explicit scope limits;
neither complete wrapper is claimed PASS. Coexistence belongs to ticket 63, the refusal check
to ticket 98, and the shared engine-cell check to tickets 76/146; these rows are evidence of
compatibility, not a transfer of check ownership to ticket 149.

Ticket 146 is resolved and the signed cut is complete. This closes the original declared-line
and required-cell conditions. It does not establish admission on a live named cluster, resolve
ticket 148's current required-check failure, or erase ticket 150's formal 148 dependency.
