# 71 — Which kyverno versions does the estate support?

Type: grilling (HITL)
Status: open
Blocked by: none

## Question

Ticket 54 pinned the gate to kyverno 1.18.2, the version the estate is authored against. That
makes the gate honest, but it does not answer the real question: the composed v4.0.0 that all
three adopters pin does not load on a 1.19 cluster at all.

Two incompatibilities are proven, and they are not the same size:

1. `cage-tier`'s label map fails to compile: `expected type 'string' but found 'dyn'` at
   `"posture.acme.io/tier": variables.tier`. `string(variables.tier)` compiles under both 1.18.2
   and 1.19.0, so this one is a one-line, backward-compatible fix.
2. With that applied, `cage-netpol`'s per-tier reach matrix then fails under 1.19 with a
   behavioural difference in the generated NetworkPolicy, not a compile error. Depth unknown.

The decisions the owner owns. What engine versions does a published policy line claim to support,
and where is that claim declared and graded? Does a supported-version claim belong on the
`versions.yaml` array element, so an adopter can price a cluster it cannot serve? Is fixing 1.19
a new policy version (the engine computes the bump), and if so does it ride with ticket 63's
isolated-default cut or stand alone? And does an adopter's declared cluster version become a fact
composition reads, so an unsupported pairing is a priced hole rather than a surprise at admission?

## Notes

Raised by the ambition review of 2026-08-31 and split out of ticket 54, which fixed the instrument
only. Evidence and the A/B table are in ticket 54's Answer.

## Comments

**2026-09-02, review.** One fact to add: every shipped policy is `policies.kyverno.io/v1alpha1` (69 files estate-wide), and no participant publishes a supported-engine-version matrix. A policy-as-a-versioned-dependency thesis owes its consumers a substrate compatibility window. Grade (a) whether the API is GA, (b) whether any artefact declares its substrate range, (c) whether a Kyverno bump goes through the computed-semver gate. Record: REVIEW-2026-09-02.md, completeness C4.

**2026-09-25, round 1 decided. The grilling continues.**

The owner grilled this ticket on 2026-09-25. The assistant proposed an answer to each question. The
owner answered round 1 with a bare "agree". Under ADR-0025, a bare agree is a delegation, so each
decision below is labelled delegated.

**The facts that shaped the answers, read on 2026-09-25.**

- Part of this ticket is already built. Platform PR 26 (97dd40d, 2026-09-10) added
  `tested_engines: { scope: published-cage-fixtures-v1, kyverno: ["1.18.2"] }` to the 5.0.0 element
  of `distribution/versions.yaml` and a grader, `computed-semver/engine_compatibility.py`, which
  `verify-cage-engine.sh` runs. The platform README says that this is "not a runtime support
  range" and that it completes "only ticket 71's bounded offline matrix subtask".
- The grader requires `tested_engines.kyverno == [running version]`. A list with two engines
  therefore reads could-not-look, and that turns the hub gate red.
- Policy 4.0.0 is retired. All three adopters compose `[5.0.0]` only. Ticket 63's cut was 5.0.0,
  tagged 2026-09-10, so a 1.19 fix cannot ride with it.
- The adopter installs its own engine. Adopters sync platform `./distribution` only, not
  `./engine`. Each adopter's `drift-sample.yml` installs Kyverno 1.18.2 itself. No adopter declares
  its engine version, and `party/schema.json` has `additionalProperties: false`.
- Every served body is `policies.kyverno.io/v1alpha1`. The `install.yaml` of Kyverno 1.18.2 and of
  1.19.1 both serve `v1`, mark `v1alpha1` deprecated, and store `v1beta1`, for all five policy kinds.
- ADR-0003 says the bodies are `v1`, that the build is all-`ValidatingPolicy`, and that the engine
  is bumped by a Renovate PR. All three are false.
- `.github/scripts/cut-release-update-array-commit.sh` rebuilds only quoted scalar keys. An element
  that carries `tested_engines` before its cut loses the field and gains a stray `}`.
- The cage-netpol difference under 1.19 is recorded only in prose, in ticket 54. No capture exists.

**The decisions. Each is delegated, 2026-09-25.**

1. **Q1 (b). A line's support claim is its tested set.** A line supports exactly the engines named
   in its `tested_engines`, each an exact version. An engine that is not in the list is
   unsupported, and that includes a newer patch. No range is declared or inferred. The reason is
   the estate's rule: a claim goes no further than the measurement. The glossary gains
   **Supported engine**.
2. **Q2 (a). The adopter owns its engine version and declares it.** Composition reads the
   declaration. The drift sample observes the running engine and grades it against the
   declaration. The platform does not choose another org's engine. The glossary gains
   **Declared engine**.
3. **Q3 (a). 1.19 support is a goal now.** A new ticket first captures and diagnoses the
   cage-netpol difference. Then it cuts a new line whose bodies pass on 1.18.2 and 1.19.x. If the
   difference is a Kyverno defect, the ticket records the defect and stops. It does not bend the
   policy to fit the defect.
4. **Q4 (a). ADR-0003 is amended, and the bodies move to `v1` in the same new line as the 1.19
   fix.** One new line carries both changes, and the engine computes the bump. The amendment
   corrects the three false statements.

**2026-09-25, the 1.19 diagnosis that Q3 asked for.** The capture and its evidence are in
`.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`. One agent diagnosed and a second
agent tried to refute. The second agent confirmed the classification and corrected two claims.

- The cage-tier failure is a policy defect. `string(variables.tier)` compiles on 1.18.2 and 1.19.1,
  passes 13/0 on both, and gives the same mutated output as the tagged body.
- The cage-netpol failure is not a policy behaviour change. The generated NetworkPolicies are
  the same on both engines. Kyverno 1.19 (upstream PR #16505) returns no result when a
  GeneratingPolicy's `matchConditions` do not match. So the fixture's two `result: skip` rows read
  "Fail / Not found". On 1.18.2 those rows were a real "generates nothing" check. No body change
  measured makes them green on 1.19.1, and a PolicyException masks the gate.
- The fixture has a gap on both engines: no row tests the `is-caged` gate alone.
- Moving the five bodies to `policies.kyverno.io/v1` changed no result on either engine.

This changes the shape of the Q3 ticket. The body needs a one-token fix. The fixture needs a
"generates nothing" check that does not depend on how the engine reports a miss.

**2026-09-25, round 2 decided.** The owner answered round 2 with a bare "agree". Each decision is
delegated.

5. **Q5 (b). The adopter's engine install pin is its declaration.** Each adopter's gitops carries
   the manifest that installs Kyverno at an exact version. Composition reads the version from that
   file. The drift sample installs from that file and stops using its own `KYVERNO_VERSION`. The
   reason: a separate statement and the install are two files, and they drift apart.
6. **Q6 (a). An unsupported pairing is priced, never refused.** On an engine that is not a
   supported engine of a composed line, the line's control claims do not count, so every control
   the line claims is a hole. The evidence document shows an `unsupported-engine` delta that names
   the pairing. An adopter with no declared engine gets the same price under an
   `undeclared-engine` delta. The reason: this prices the worst case, the cage not loading, and
   claims nothing about the cage working. ADR-0026 retired refusals for holes. The glossary gains
   **Unsupported pairing**.
7. **Q7 (a). One grader run grades every cell of the matrix.** A cell is one line on one engine.
   The caller supplies one binary for each engine. A listed cell with no binary reads
   could-not-look, which is red. The platform keeps one table of engine versions, with a pinned
   checksum for each CLI and each `install.yaml`. The reason: one report shows a missing column. A
   CI matrix splits the verdict, and a job that does not run looks like a pass.
8. **Q8 (a). The engine bump route has four rules.**
   1. To add an engine to a cut line changes metadata only. The same PR must pass the new cells.
      The policy version does not change.
   2. To remove an engine from a line narrows its support. The policy version does not change. An
      adopter that declares that engine gets the `unsupported-engine` delta at its next
      composition.
   3. The estate's own engine pins must name a supported engine of every served line: the hub
      truth CLI, the platform release CLI and the platform in-cluster engine. A gate check asserts
      this. An adopter's declared engine can be any version, because Q6 prices it.
   4. No Renovate. ADR-0003's route becomes "a reviewed PR that the gate grades".
   The reason: a changed verdict on a new engine is a failed cell, and a failed cell cannot join
   the tested set, so behaviour stays guarded. An engine bump that cut a policy version would add
   versions with unchanged bytes, and each would need every adopter's acceptance.
