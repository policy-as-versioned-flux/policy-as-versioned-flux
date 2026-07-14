# North-Star — The Modern Reference for Policy as Versioned Code on Flux

> **Purpose.** The [PRD](PRD.md) specifies the *faithful-to-intent* build. This report documents the
> fuller **modern reference** — what the design becomes when we stop being constrained by fidelity
> to 2022 and by current Flux limitations. Nothing here contradicts the floor; each item is an
> **in-place upgrade** of a floor component or a net-new capability. Read it as the destination the
> floor is deliberately built to grow into.

## 1. The delta at a glance

| Area | Faithful floor (PRD) | North-star (this report) |
|---|---|---|
| Transport | signed git tags ([gitsign](https://github.com/sigstore/gitsign)), CI-verified | **[OCI artifacts](https://fluxcd.io/flux/cmd/flux_push_artifact/) + [cosign](https://github.com/sigstore/cosign) keyless**, source-controller-verified; OR keyless **git** once [#1068](https://github.com/fluxcd/source-controller/issues/1068) lands |
| The "why" | carried as advisory metadata | **enforced** via signed cosign attestation + Kyverno `verifyImages` |
| Supply chain | gitsign + Rekor transparency | **SBOM + SLSA provenance** attestations on the artifact digest |
| Verification gate | in CI / at-merge | **Flux-native, pre-apply** (`spec.verify`) on both OCI and (post-#1068) git |
| Compliance catalogue | NIST 800-53r5 (from collie) | **UK NCSC CAF / GovAssure** [OSCAL](https://pages.nist.gov/OSCAL) catalogue (+ NIST retained) |
| Proof | KiND (admission/spec-based, no cloud) | **real-cloud multi-cluster fleet e2e** (multi-account, live RDS/S3, C2P over realized state) |
| Governance agent | bounded demonstrator | **production risk-intelligence agent** with live [Wardley mapping](https://medium.com/wardleymaps/exploring-the-map-ad0266fad59b) |
| Engine | Kyverno-only | **engine-agnostic** mapping (Gatekeeper, Kubewarden, native VAP) |
| Fleet | `ResourceSet` matrix (static inputs) | `ResourceSetInputProvider` pulling tags/PRs; **ephemeral policy previews** |

## 2. Transport: OCI artifacts (and keyless git, eventually)

The floor stays on git tags because OCI was solving a Flux gap, not a thesis need (ADR-0001). The
north-star adds OCI as the **distribution plane** while git remains the **authoring plane**:

- `flux push artifact oci://…/policies:2.1.1` on release; immutable, digest-addressed.
- **cosign keyless** signing (OIDC, no GPG custody) and `OCIRepository.spec.verify` with
  `matchOIDCIdentity` → the `SourceVerified` condition **blocks unverified policy pre-apply** —
  the Flux-native gate the floor does in CI.
- **Parallel path:** if **fluxcd/source-controller#1068** lands (gitsign verifier for
  `GitRepository`), the floor's *existing* gitsign-signed tags become Flux-natively verified with
  **no transport change** — the most faithful end-state (keyless + git + native gate). The two
  paths converge; OCI is the no-wait option, #1068 is the stay-on-git option. Both are documented;
  the upstream comment (`docs/upstream/`) pursues the latter.

## 3. Enforcing the "why" (not just carrying it)

The floor *carries* rationale as advisory metadata (ADR-0007). The north-star **enforces** it:

- `cosign attest --type <threat-model>` attaches a signed risk/threat-model **predicate** to the
  policy artifact's digest.
- Kyverno `verifyImages` (or an admission check) refuses to admit a policy version whose rationale
  attestation is **absent or unsigned** → "no defended rationale, no admission." This makes
  "purposeless policy is pointless" *mechanically true*, not merely aspirational.
- Note the boundary: Flux verifies *signatures*, not predicate *contents* — content gating is the
  engine's job, which is why this lives at Kyverno, not source-controller.

## 4. Supply chain: SBOM + SLSA

With OCI in play, attach an **SBOM** and **SLSA provenance** to the policy artifact digest. Policy
is now a dependency with the same supply-chain hygiene as any other — closing the thesis's "supply
chain is not a new problem" point that the floor only gestures at via Rekor.

## 5. UK compliance catalogue

collie ships **NIST 800-53r5** (US-federal); the floor keeps it as the worked example (ADR-0004,
ADR-0008). The north-star authors a **UK NCSC Cyber Assessment Framework / GovAssure** OSCAL
catalogue and maps the cloud policies to it, retaining NIST for portability. OSCAL is
framework-agnostic, so this is additive — the same C2P `result2oscal` mapping (ADR-0009) attests
against either.

## 6. Real-cloud fleet e2e

The floor proves coexistence and cloud-admission on KiND+LocalStack (no spend). The north-star runs
a **multi-cluster, multi-account fleet**: clusters subscribing to different policy semver sets via
`ResourceSet`, real RDS/S3 provisioned by [Crossplane](https://crossplane.io), C2P attesting control satisfaction from
PolicyReports over live resources, notification-controller posting commit-status compliance back to PRs across the
fleet. This is the "show the CIO the whole estate" proof at production shape.

## 7. The production governance agent

The floor ships a **bounded demonstrator** (one signal source, opens review PRs; ADR-0007). The
north-star agent:

- Ingests **multiple live signal sources** — CVE feeds, cloud-provider change logs, regulatory
  bulletins, threat intel — and correlates them to each policy's embedded rationale.
- Runs **live Wardley mapping**: tracks climatic movement (commoditisation, evolution) of the
  components a policy governs, and flags when a control's rationale is becoming obsolete (e.g. a
  mitigation now provided natively by a commoditised platform) or when a *new* risk is emerging
  that no policy covers.
- Produces **noise-reduced business decisions** at fleet scale, still as reviewed PRs — never
  editing enforcement (the boundary is permanent, not a floor limitation).
- Optionally drafts the *candidate policy change* (CEL + rationale + fixtures) for human review,
  turning "this is stale" into "here's the proposed defended replacement."

## 8. Engine-agnosticism

Kyverno is the reference engine (floor). The north-star documents the **identical shape** on OPA
Gatekeeper, Kubewarden, and Kubernetes-native `ValidatingAdmissionPolicy` — proving the
*versioned-dependency mechanism* is engine-independent (the talk's "I could have picked any tool").
The version self-selector, coexistence, and Audit/Deny split map onto each; only the policy body
language changes.

## 9. Fleet templating maturity

Replace the `ResourceSet`'s static matrix inputs with **`ResourceSetInputProvider`** pulling
semver-filtered tags (auto-discovering newly released versions for the matrix) and GitHub PR inputs
for **ephemeral policy previews** — spin up a throwaway cluster pinned to a policy *PR branch* so a
proposed change can be exercised against real workloads before merge. This makes the "debate in a
PR" loop runnable, not just reviewable.

## 10. On pin-vs-range (revisited)

The floor rejects live ranges for policy (ADR-0002) and the north-star does **not** reverse this —
reviewed upgrades are thesis-core. The only north-star nuance: live `ref.semver` ranges remain
acceptable for **non-policy** sources (e.g. the engine's own minor versions) where no organisational
risk debate is implicated. Policy stays pinned-and-reviewed at every tier.

## 11. Migration path (floor → north-star)

Designed so each step is independent and in-place:

1. Add `flux push artifact` + cosign to the release pipeline → flip consumers `GitRepository` →
   `OCIRepository` (or wait for #1068 and keep git). *Transport upgrade, no thesis change.*
2. Add the cosign rationale attestation + Kyverno `verifyImages`. *Enforce the why.*
3. Author the UK CAF OSCAL catalogue alongside NIST. *Compliance breadth.*
4. Stand up the real-cloud fleet. *Proof at scale.*
5. Grow the agent demonstrator into the production agent. *Governance depth.*

## 12. What never changes (the thesis core)

Semver-with-meaning; multi-version coexistence via `nameSuffix` + version self-selector; **reviewed
upgrades** (PR as the unit of debate); **lane-keeping + gate** proportionality; **carry (then
enforce) the why**; **deterministic policy** (no time conditions); the **human-governance** loop;
and the honestly-named **last-mile** residual. The north-star deepens the plumbing; it does not
touch the argument.
