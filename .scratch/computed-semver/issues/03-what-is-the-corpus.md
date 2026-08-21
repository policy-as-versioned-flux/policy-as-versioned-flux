# 03 — What represents "currently-compliant workloads"?

Type: grilling
Status: resolved
Blocked by: 01

## Question

The rule is defined against *currently-compliant workloads*, and nothing in the estate represents
that population. `estate/platform/shift-left/fixtures/` holds exactly two pods
(`workload-flip.yaml`, `workload-unversioned.yaml`), authored to demonstrate a flip — not to be
evaluated against.

A computed bump is only as good as the corpus it is computed over, and this is the ticket where that
is either taken seriously or quietly fudged.

**Decide:**

1. **What the corpus is.** Options: the estate's own deployed workloads harvested from the clusters;
   a hand-authored matrix of pod shapes chosen to span the policy surface; generated permutations
   over the fields the policies actually read; the institutions' real fixtures; or some combination.
2. **Who owns it.** One shared corpus in `platform`, or one per institution? An institution's real
   workloads are the honest population for *its* upgrade decision, but `platform` cuts the release —
   and after the six-org split they are different repos in different organisations.
3. **How it stays honest.** A corpus curated by the same people who choose the bump can be curated
   *toward* the bump they want. What stops that? Generation from the policy surface rather than
   hand-selection is one answer; signing and versioning the corpus is another.
4. **Whether it must be exhaustive.** It cannot be. That is fine only if the incompleteness is
   *stated* — see the coverage ticket, which this blocks in spirit.

Blocked by the rederivation ticket, whose "cannot distinguish X without Y" findings name the
properties the corpus must actually have — rather than guessing them now.

## Answer

Resolved by grilling, 2026-08-21, over seven rounds. Four environment facts drove it, and two of them
overturned decisions taken earlier in the same session.

**The shape in one line: the corpus is a *generated* population of plain pods, owned by `platform`,
enumerated from the policy surface — with a second *witness* population of real workloads whose only
job is to prove the generator did not miss a shape.** Nobody hand-picks an entry, so nobody can
curate toward a wanted bump.

### The four facts

1. **The clusters cannot be harvested.** `kind-ludlow` and `kind-tuppence` run only Flux and
   `kube-system`; `kind-driftwood` adds Dex, Istio and Kyverno. There is no first-party workload
   population to collect.
2. **The policy surface is tiny.** Across `policy/`, `distribution/` and `graded/` the CEL reads only
   `object.metadata.labels`, `object.metadata.namespace` and `object.spec.containers`. Generating
   every shape the rules can distinguish is a small job.
3. **`cage-tier.yaml` is a `MutatingPolicy` driven by a *label*, not by the £.** It reads
   `posture.acme.io/tier` and expands it into dials by a pure CEL map. `cage.py`'s
   `select_tier(uncaged_ale, tolerance)` runs *upstream*, outside admission. So a corpus entry needs
   a **tier label**, never an invented residual — this replaced a residual axis settled earlier in
   the session.
4. **Five of the eight live Kyverno policies carry no version.** Versioned:
   `distribution/policies/v1.0.0/require-nonroot.yaml`, `.../v2.0.0/require-nonroot.yaml`,
   `policy/policies/v1.0.0/may-run-root-if-attested.yaml`. Unversioned: the orphan guard in
   `distribution/versions.yaml`, `graded/policies/cage-tier.yaml`, `graded/policies/cage-netpol.yaml`,
   `posture/policies/posture-trust-boundary.yaml`, `posture/policies/stamp-posture.yaml`. Two of the
   five mutate every claiming pod. This widened the definition of "the subject" mid-session.

### 1. What the corpus is

- **Two populations.** The **generated spine** decides bumps. The **witness set** proves the generator.
- The generator enumerates **per CEL expression** — satisfied, violated, absent — not per field. The
  field space is infinite; the expression space is finite and grows with the policy body.
- **Second axis: the version pin**, inside the platform version array and outside it, so the
  **orphan guard** is exercised.
- **Third axis: the tier label** — absent, `baseline`, `restricted`, `quarantine`. Absent is a real
  case, because `cage-tier` defaults it to `baseline` rather than skipping it.
- **Combine pairwise, not fully.**
- **Generate from both subjects** (old and new) and take the union. A rule only the *old* policy can
  distinguish does not exist in a corpus generated from the new one, and a retirement is exactly the
  case a release must be able to see. State both counts and the union count.
- The **witness set** is ticket 01's five fixtures plus the six real unlabelled infrastructure
  workloads the COTS effort named (SPIRE, Istio, OpenBao, Pomerium, Dex, `git-server`).
- **An entry is a plain pod carrying a version pin.** No band and no residual: the band belongs to the
  institution, and a residual for Dex would manufacture the very assertion this ticket exists to
  prevent. Witness entries test *shape*, not residual.
- **Composites enter** as post-wrap pod specs — what admission actually sees.
- **No size ceiling.** Publish the entry count and the wall-clock instead. A ceiling truncates
  silently, and silent truncation is the bug this map exists to kill. Ticket 05 may set one later with
  a real number in hand.

### 2. Who owns it

- **`platform` owns one corpus and the generator**, beside `computed-semver/`. Ticket 02 already
  settled that semver is a property of the artefact, not the consumer, so **no institution owns a
  corpus** and no institution's workloads can move the published tag. An institution checking its own
  workloads before taking a Renovate PR is a real need, but it is ticket 05's adoption-end question.
- No cross-org read is needed: `platform/risk/appetite.json` is already the single source of truth for
  every band (the institutions' `risk-appetite-configmap.yaml` files say so in their own comments).
- **`computed-semver/corpus/`** holds the generated pods as plain YAML, one file per entry, plus a
  manifest carrying the checksum, the entry count and per-witness provenance.
  **`computed-semver/subject/`** holds the policy bodies and the version array. This splits the two
  meanings the current `corpus/` directory conflates — ticket 01 proved the gate needs both, since a
  new Audit-only policy moves no verdict and is visible only by structural diff.

### 3. How it stays honest

- **A witness shape missing from the spine fails the corpus build.** The repair is to extend the
  generator, **never** to add the fixture by hand. This is the mechanism that stops curation, and it
  turns each real infrastructure workload into a standing test of the generator.
- **A shape** is the tuple of outcomes each subject CEL expression gives on that pod, plus whether its
  pin is inside the version array. Implementable, indifferent to cosmetic diffs, and it is the
  coverage vocabulary ticket 04 needs.
- **The corpus is not signed.** It is generated deterministically, so CI regenerates it and fails on
  any diff — that proves the same property more cheaply than a signature. **The evidence output is
  signed**, with the existing shared `platform` key (`feeds/sign.sh`'s shape), because that is the
  artefact a reviewer trusts on the Renovate PR.
- **The generator is versioned but is not part of the subject**, so it cannot bump the policy version.
  The evidence names the generator version and the corpus checksum, and a generator change **re-runs
  ticket 01's three known-good bumps and is refused if any stops re-deriving** — the map's own
  "reproduce a human's correct answer first" rule, applied to the tool.
- **Claim source** (procured / wrapped / identified) lives in the manifest, not on the entry, so the
  entry stays a plain pod that `kyverno apply` reads unchanged. It is **printed and never
  down-weighted**: discounting a workload because its claim is weak is an `Exemption` wearing another
  name, and `CONTEXT.md` bans that concept outright.

### 4. What the subject is, and what the gate must refuse

- **The subject is every Kyverno policy that can reach a pod, plus the version array** — the array
  decides which bodies run and the orphan guard's allow-list ranges the same array, so a release that
  only retires a version changes no CEL at all.
- **The dials CEL map inside `cage-tier.yaml` is a policy body.** It is the copy admission reads;
  `verify-graded.sh` already guards `cage.py`'s table against drift from it, so there is still one
  truth. Consequence: tightening `baseline` from `cpu: 500m` downward is **major** by `CONTEXT.md`'s
  rule, because a pod that cannot schedule under the new limit is refused.
- **Movement traced to an unversioned policy fails the gate and names the file.** There is no version
  number that can carry that change. Repairing it is ticket 07's job (see the finding raised there).
- **Two versioned trees declaring the same version with different content fails the gate.**
  `distribution/policies/v1.0.0/` and `policy/policies/v1.0.0/` are separate trees in the same repo,
  each with its own `v1.0.0`, and `versions.yaml` reconciles only `./distribution/policies/v<version>`.
  Treat them as one line until proved otherwise, and let the gate surface it if they are not.
- **An entry stays a plain pod, not a pod-plus-cluster-state.** The gate evaluates it against the whole
  installed policy set for a subject and reads **per-policy** outcomes, never a pooled `kyverno apply`
  exit code — ticket 01 proved that trap empirically in `demo_pooled_exit_is_not_admission`. How the
  installed set is assembled is ticket 05's.

### The evidence splits in two

- **The corpus** proves what each tier does to a pod at admission.
- **A separate check** runs `select_tier` as the pure function it is, over all four rows of
  `platform/risk/appetite.json` (driftwood £40k, tuppence £15k, `platform` £10k, ludlow £5k), and
  prints the per-institution matrix ticket 02 asked for. `platform` is included even though
  `verify/party/party.py` excludes it from the institution count: ticket 07 binds the platform's own
  version to this rule, and `honesty/reflexive.py` exists to refuse exactly this self-exemption. The
  tag is still computed against ludlow at £5k, the strictest, so including it costs nothing.

### Honest limits, to be published by the gate

1. **The tier axis is synthetic.** The estate holds two priced scenarios in total
   (`fair/scenarios/driftwood-cart-pii.json`, `risk/scenarios/driftwood-cart-pii-tightened.json`),
   both driftwood's. Nothing maps a pod to a scenario.
2. **Deny is unobservable at admission.** `cage-tier` never denies (its own header says so) and the
   pod simply never exists. The bottom rung is proved by function test on `select_tier`, and the
   evidence must say that rather than imply corpus coverage.
3. **A claim-less composite reports "no cage spec".** `cage-tier`'s `matchConditions` deliberately
   skip pods with no version claim, and its comment says that gap is what "keeps that question
   actually open rather than silently decided by omission". Printing a cage spec for them would close
   ticket 08's spun-out question by accident.
4. **The gate may fail on its first real run for a reason unrelated to the release** — see fact 4.
   That is the finding, not a defect.
