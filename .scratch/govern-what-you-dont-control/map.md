# Map — governing the workloads you don't control

Label: `wayfinder:map`. Charted 2026-08-20.

## Destination

**A workload nobody can modify is still governed, and still carries a policy version.** COTS
products, vendor images and anything else that cannot be made to wear a
`policy-as-versioned.dev/policy-version` label are brought under the same versioned, priced,
proportionate model as first-party workloads — reached by a **policy-dependency shim** at the infra
decision point, or by **policy describing them**, or both.

Reaching it means an unversioned workload has an answerable compliance state, a cage spec, and a
place in the £, rather than passing freely because nothing matched it.

## Notes

**Why this exists.** Owner, 2026-08-20: *"there'll always be COTS products that we must facilitate
and support — it won't all be custom build."* Unversioned workloads are a **permanent, legitimate
population**, not an edge case to be tidied away.

**The gap, precisely.** Every versioned policy self-scopes with `matchConditions` on the version
label, and the orphan-guard's own `matchConditions` require a *non-empty* version label
(`render-orphan-guard.py`). So a pod carrying no version label is out of scope of **everything**,
including the guard — it passes freely. That is the exact opposite of "facilitated": the estate's
strictest treatment is reserved for workloads that *do* declare a version, and its most permissive
for those that declare nothing.

**Domain.** Read `CONTEXT.md` (*Policy version*, *Lane-keeping vs. gate*), the self-scoping comments
in `estate/platform/distribution/policies/v1.0.0/require-nonroot.yaml`,
`estate/platform/distribution/render-orphan-guard.py`, and
`estate/platform/graded/policies/cage-tier.yaml`.

**Standing preferences.**
- **Facilitate, don't exclude.** The goal is that a COTS workload can be adopted and governed, not
  that it is denied for failing to be first-party.
- **The vendor cannot be asked to change.** Any design requiring the upstream image or chart to carry
  our label is not a solution to this problem.
- **Whatever assigns a version is making a claim, and claims are evidence.** The estate signs and
  grades its evidence everywhere else; a shim asserting "this COTS thing is effectively 2.0.0" is an
  assertion that needs the same treatment.
- Skills each session should consult: `/grilling`, `/domain-modeling`.

## Decisions so far

<!-- index of closed tickets; one line each, linking the ticket that holds the detail -->

- [Where does the shim sit: procurement, build, or admission?](issues/02-where-does-the-shim-sit.md)
  — **three layered sources: procured → wrapped → identified.** The wrapper makes the product a real
  pinned signed dependency; the procurement record carries the declared version; SPIFFE identity is
  checkable at runtime. A platform-side allow-list was **rejected** — it would assert a compliance
  claim about software nobody inspected. `stamp-posture` already proves trust-bounded stamping works;
  what was missing was the *source* of the claim.
- [What does compliance mean when the vendor image cannot comply?](issues/03-what-does-compliance-mean-for-a-vendor-image.md)
  — **compliance is achieved by the cage, not the image; the composite complies.** Already true in
  code: `cage-tier` stamps `readOnlyRootFilesystem`, drops caps, adds a WAF sidecar, and generates an
  egress lockdown. Conditional policy decides admission, the tier decides tightness, the residual
  lands in the institution's own band **tagged**. Surfaced: COTS partly *outsources* risk via vendor
  recourse, which the £ engine cannot express.
- [Is "COTS" the boundary, or is it "can we change the pod spec"?](issues/01-what-is-the-real-boundary.md)
  — the axis is *can we change the pod spec*, defined by its remedy: **wrap it or shim it**, never
  exempt and never deny. The population is mostly **us**: five unlabelled third-party charts (SPIRE,
  Istio, OpenBao, Pomerium, Dex) plus `git-server`. The platform's own infrastructure is in scope and
  is the **leading case**. Institution owns the risk and the £; platform owns the mechanism.

## Not yet specified

- **Whether the shim is admission-time, build-time, or procurement-time.** "At the infra decision
  point" suggests earlier than admission — possibly where the thing is *chosen*, not where it runs.
- **Whether "wrap" and "shim" are two mechanisms or one.** The remedy was given as a pair. A *wrap*
  (a chart or overlay we control, patching the pod template before it is applied) and a *shim* (a
  layer decorating the workload at the infra decision point) have different owners, different
  failure modes, and different answers to "who asserted this compliance claim". Sharpens once the
  shim-location ticket runs.
- **What a COTS workload's compliance even means** when the policy body assumes it can dictate the
  pod spec. Some rules (`runAsNonRoot`) a vendor image may simply be incapable of satisfying.
- **How this lands in the £.** An ungovernable-but-necessary product is retained risk; the estate has
  a vocabulary for that (`transfer`, `retain`, the constraint pre-filter) and it may already fit.

## Out of scope

- **Computing the semver bump.** Its own effort — see
  [`.scratch/computed-semver/map.md`](../computed-semver/map.md). This map's answers change that
  map's corpus, and it is recorded there as a dependency, but the gate is not built here.
