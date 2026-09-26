# 71 — Which kyverno versions does the estate support?

Type: grilling (HITL)
Status: resolved
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

> **Corrected 2026-09-26.** Item 2 is refuted. Under the offline CLI the generated NetworkPolicies
> are the same on both engines. Only the report for an unmatched trigger differs. See
> `.scratch/ecosystem/research/kyverno-1.19-cage-diagnosis/`.

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
  `tested_engines: { scope: published-cage-fixtures-v1, kyverno: ["1.18.2"] }` to the 4.0.0 and
  5.0.0 elements of `distribution/versions.yaml` (4.0.0 has since retired) and a grader, `computed-semver/engine_compatibility.py`, which
  `verify-cage-engine.sh` runs. The platform README says that this is "not a runtime support
  range" and that it completes "only ticket 71's bounded offline matrix subtask".
- The grader requires `tested_engines.kyverno == [running version]`. A list with two engines
  therefore reads could-not-look, and that turns the hub gate red.
- Policy 4.0.0 is retired. All three adopters compose `[5.0.0]` only. Ticket 63's cut was 5.0.0,
  tagged 2026-09-10, so a 1.19 fix cannot ride with it.
- No adopter reconciles a platform path. Each adopter serves its own composed set, and
  `gitops/platform/platform-distribution.yaml` is opt-in (corrected 2026-09-26; this line first
  said that adopters sync platform `./distribution`). Each adopter's `drift-sample.yml` installs
  Kyverno 1.18.2 itself. No adopter declares
  its engine version, and `party/schema.json` has `additionalProperties: false`.
- Every served body is `policies.kyverno.io/v1alpha1`. The `install.yaml` of Kyverno 1.18.2 and of
  1.19.1 both serve `v1`, mark `v1alpha1` deprecated, and store `v1beta1`, for each policy kind
  that has a `v1alpha1`.
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
- The cage-netpol failure is not a policy behaviour change under the offline CLI. The generated
  NetworkPolicies are the same on both engines, and the offline PolicyReport differs. Kyverno 1.19 (upstream PR #16505) returns no result when a
  GeneratingPolicy's `matchConditions` do not match. So the fixture's two `result: skip` rows read
  "Fail / Not found". On 1.18.2 those rows were a real "generates nothing" check. No body change
  measured makes them green on 1.19.1, and a PolicyException masks the gate.
- The fixture has a gap on both engines: no row tests the `is-caged` gate alone.
- Moving the five bodies to `policies.kyverno.io/v1` changed no result on either engine, under the
  offline CLI: the two cage matrices, and `kyverno apply` of the other three bodies over the
  cage-tier fixture pods. Those three bodies compile on 1.19.1. Their own fixtures did not run.

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

**2026-09-25, round 3 decided.** The owner answered round 3 with a bare "agree". Each decision is
delegated.

9. **Q9 (a). ADR-0033 records the claim and the price, and ADR-0003 gets a dated amendment.** Both
   are written on this branch. ADR-0003 chose the engine and the API. ADR-0033 decides the engine
   version window, so it is a separate record. The amendment corrects the three false statements
   and points to ADR-0033.
10. **Q10 (a). The new line's fixture compares generated documents.** For each trigger, the grader
    runs `kyverno apply -o` and compares the generated documents with an expected set in the
    fixture. For an unmatched trigger the expected set is empty. The `result: skip` rows leave
    `kyverno-test.yaml`. A new trigger tests the `is-caged` gate alone: a pod that is not caged, at
    a tier that restricts reach. The reason: the check reads the served behaviour, which is the
    same on both engines, and not how the engine reports a miss.
11. **Q11 (a). "The running engine equals the declared engine" is a drift fact.** The drift sample
    records it, and a false fact is a red, as with the existing facts. The reason: a declaration
    that nothing checks is a proxy. Composition prices the declared engine, and the drift fact
    proves that the price describes the real cluster.
12. **Q12 (a). The new line carries three changes only.** They are `string(variables.tier)` in
    cage-tier, all five bodies at `policies.kyverno.io/v1`, and the Q10 fixture. Its
    `tested_engines` is `[1.18.2, 1.19.1]`. The engine computes the bump. The diagnosis predicts no
    behaviour change, so a patch is expected, but the engine decides. 5.0.0 stays served, because
    it still supports 1.18.2.

**Held for the owner, 2026-09-26 at the earliest.** On 2026-09-25 the three grilling sessions used
the five owner-only decisions for the day. Two questions here are owner-only:

- **An authorisation to build and cut.** The owner's instruction of 2026-09-23 left the grilling
  tickets, and all work that they block, with the owner. The new line needs a signed
  `policy/v5.0.x` tag.
- **An authorisation to report upstream.** A Kyverno GeneratingPolicy returns no result on a
  `matchConditions` miss, but ValidatingPolicy and MutatingPolicy return a skip. A report to
  kyverno/kyverno is public and is made under the owner's identity.

**2026-09-25, round 4 decided.** The owner answered round 4: "I ageee with your recommendations".
That gives no reason, so each decision is delegated.

13. **Q13 (a). The build is five tickets.** 146 is the grader for many engines, the engine table
    and the check on the estate's own pins. 147 is the adopter's engine declaration and the
    engine drift fact. 148 is the price of an unsupported pairing. 149 is the new line. 150 is the
    live proof on one adopter. 146 and 147 run first. 148 and 149 run next. 150 runs last. The
    reason for the order: if composition prices before the adopters declare, all three adopters
    get the `undeclared-engine` price and the gate records a fall.
14. **Q14 (a). This ticket is resolved.** Each part of the build has a ticket with a Done line, so
    this ticket holds no work.

**Two notes from grilling ticket 152, recorded in 147 and 150.** No adopter moves to 1.19.1 while a
served cage-tier body that it composes does not compile there. Ticket 161 reads the adopter's
engine version from the file that ticket 147 names.

**On 2026-09-25 the owner also said:** "You have explicit permission to merge your own PRs.
Remember this".

**2026-09-26, a review of the record, and round 5.** Before the merge, a review workflow checked
the record: one agent looked for conflicts with standing records, and a second agent checked every
factual claim against the estate. It returned 34 findings. Thirty were corrections, made on
2026-09-26 without a decision. Four needed a decision, and one conflict was found before the
review. The owner answered round 5 with "Agree". Each decision is delegated.

15. **Q15 (a). The ticket 149 line also retires `posture-trust-boundary`.** Ticket 89's register,
    `NORTH-STAR.md:54` and ticket 84 each commit the retirement to the next declared line. The line
    carries four changes, and `render-version-tree.py` changes too. The patch prediction of
    decision 12 is withdrawn. If the computed bump is a major, each institution needs an acceptance
    record, which the owner writes.
16. **Q16 (a). "Supported" covers every body that the line serves.** Each body compiles on the
    engine and its fixtures pass. The machinery carries its own `tested_engines`, and composition
    prices cm-6 the same way. The reason: the price counts the control claims, and the old scope
    never graded a body that carries a claim.
17. **Q17 (a), replacing decision 11. The declared engine installs on every cluster the adopter
    runs.** `kind-driftwood` got the platform's Kyverno from `talk/up.sh`, and no adopter's Flux
    reconciles `gitops/engine/`. So `talk/up.sh` installs each named cluster's engine from its
    adopter's file. Adopters that share a cluster declare the same engine. A static check replaces
    the drift fact: the file's version, URL and checksum agree with the platform engine table. The
    reason: the lane installs from the same file, so the drift fact could only read true. Because
    the static check reads the engine table, ticket 147 now waits on ticket 146, which changes the
    order of decision 13: 146 runs first, then 147.
18. **Q18 (a). The adopter's shift-left check runs each line only on engines that the line
    supports.** A line in the window that does not support the declared engine is reported by name
    as an unsupported pairing.
19. **Q19 (a), changing decision 12's cut sentence. An uncut line is graded on its candidate tree.**
    The cut is signed only after every cell passes. This reverses the platform README's "deliberately
    not a pre-cut gate".

## Answer

Resolved 2026-09-25 in four grilling rounds, and revised on 2026-09-26 in a fifth round after a
review. The owner answered each round with an agreement and no reason, so every decision is
**delegated** under ADR-0025. Decisions 1 to 19 are recorded above, round by round. The architecture
is
[ADR-0033](../../../docs/adr/0033-a-policy-line-supports-exactly-the-engines-it-passed-on-and-any-other-engine-is-priced.md).
ADR-0003 and `docs/PRD.md` have dated amendments.

- **What a line supports.** Exactly the engine versions on which every body it serves compiles and
  its fixtures pass. No range, and no neighbouring patch. The machinery has its own supported
  engines.
- **Who owns the engine.** The adopter. Its engine install file in its own gitops is its declared
  engine, and every cluster it runs installs from that file. Adopters that share a cluster declare
  the same engine.
- **The price.** An unsupported pairing makes every control that the line claims a hole, under an
  `unsupported-engine` delta. It is never refused. No declaration is priced the same way. Whether a
  body that does not compile fails open at admission is not measured yet.
- **The grading.** One run grades every cell of the matrix, on the candidate tree before the cut
  and on the tag after it. An engine bump is not a policy version. The estate's own pins must name a
  supported engine of every served line.
- **1.19.** Under the offline CLI, the cage-tier failure is a one-token policy defect, and the
  cage-netpol failure is a Kyverno reporting change. The generated documents are the same. A new
  line carries the fix, the `posture-trust-boundary` retirement, the `v1` move and a fixture that
  compares generated documents.

The build is tickets 146 to 150. These steps are held for the owner, 2026-09-26 at the earliest:

- the signed policy tag for the ticket 149 line, and an acceptance record for each institution if
  its bump is a major;
- the platform tools tag and the adopter tags that ticket 148 needs;
- for ticket 150: the authorisation to merge over the adopter gate's retirement refusal, the
  adopter's signed composed tag with its composed-set move, and a platform tools tag that carries
  the 149 line;
- a public upstream report to kyverno/kyverno about the GeneratingPolicy change.
