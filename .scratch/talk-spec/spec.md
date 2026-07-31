# Spec: risk-based, versioned, shift-left governance — talk + demo estate

Status: ready-for-agent

Collapses the decision-complete wayfinder map ([`map.md`](map.md)) and synthesis
([`the-whole-model.md`](the-whole-model.md)) into one buildable spec. Every decision below is
**locked** upstream — this document does not re-open any of them. Detail behind each lives in
[`issues/*.md`](issues/) and [`research/{07,08,09}-*.md`](research/).

---

## Problem Statement

A principal engineer or a security/risk leader watching a governance talk is shown GitOps plumbing
and told to trust that it makes them "compliant". They can't answer the only questions that matter to
the business: *what does a breach actually cost us, is this control proportionate to that cost, and
how do I know the number is honest today rather than the day it was written?* Governance is presented
as a binary (pass/fail, compliant/not) when the real thing is a **continuously re-tuned economic
judgement**. Meanwhile the tooling that makes those judgements — increasingly AI-assisted — is asked
to be trusted rather than verified. There is no worked, end-to-end, demonstrable example that ties
**quantified risk (£)** to **proportionate enforcement**, versions the whole chain, and makes every
actor (human or machine) attestable.

## Solution

A **conference-grade talk** (first-class **Marp** deck, ~35–40 min, touring) whose single thesis is:
*governance is a proportionate, informed, continuously re-tuned response to quantified risk, and
versioning the whole chain from risk-appetite to evidence — with every actor attestable — is how
proportionality stays honest.* The talk works **backwards from live demonstration**, so the solution
includes the **delivery refactor**: a fresh six-org estate (`policy-as-versioned-{platform,driftwood,
tuppence,ludlow,nist,ico}`), one KinD cluster per institution, where every claim is demo-live rather
than narrated.

The mechanism is an **hourglass**: `RISK APPETITE (£)` → `PRINCIPLES → CONTROLS → ENFORCEMENT`
(controls *tuned* to risk — Audit vs Deny, CVE tolerance, lifecycle pace; versioned, so a bump is
proportionality moving as the world moves) → `EVIDENCE (OSCAL)` flows back up → minus the residual of
each permissive branch → a **balance-sheet £**. Flux is the load-bearing distribution plane; Kyverno
CEL is enforcement; a **FAIR risk engine** turns versioned `(min,mode,max)` triples into moving £; a
**war-gaming agent** stress-tests controls against signed feeds and, on drift, **opens a signed
policy PR — proposing, never disposing**; `gitsign` keyless → Rekor makes the whole
feed→scenario→PR→review→merge→release chain verifiable.

Three beats are demoed **live**: *proportionality* (same control, Audit in `driftwood` vs Deny in
`ludlow`, because the £ differs), the *living loop* (war-gamer → signed PR → human + gate → £ moves),
and *provenance* (verify in Rekor). *Breach-cost* opens and *balance-sheet* closes — both narrated.

## User Stories

**Platform maintainer** (owns `policy-as-versioned-platform`, the inherited discipline)

1. As a platform maintainer, I want the discipline (Flux distribution templates, FAIR engine, the
   ledger→PolicyException render, the shift-left harness, OSCAL plumbing, the war-gamer, the Wardley
   layer) to live in one `platform` repo that institutions consume as a **pinned, signed dependency**,
   so the same governance machinery is inherited rather than copy-pasted per institution.
2. As a platform maintainer, I want each institution to pin a specific signed version of `platform`,
   so I can ship an improvement and let each institution adopt it by a reviewed bump PR on its own
   cadence.
3. As a platform maintainer, I want to fan out coexisting signed policy versions from a single
   version array, so installing or retiring a policy version is one array edit, not hand-maintained
   YAML.
4. As a platform maintainer, I want a single orphan-guard whose allow-list is rendered from that same
   array, so no policy version can run that the array doesn't declare.
5. As a platform maintainer, I want the platform to govern **itself** under the same risk model
   (Kyverno/Flux/platform in scope), so the apparatus passes its own test rather than being exempt
   from it.

**Institution developer** (ships workloads into `driftwood`/`tuppence`/`ludlow`)

6. As an institution dev, I want the cluster to advertise which policy versions it supports (read off
   the version array, kubectl-style discovery), so I know the target contract before I deploy.
7. As an institution dev, I want a CI check that resolves the target's supported version window and
   runs the **target version's real admission action** offline (±1 version-skew), so an Audit→Deny
   flip is caught *before merge*, not at deploy.
8. As an institution dev, I want the compliant path to be the path of least resistance — a loud,
   normal CI failure — so a deploy-time denial (even to dev) is practically unheard-of.
9. As an institution dev, I want "you may do X *if* you meet conditions C" expressed as ordinary
   versioned policy, so I articulate *why* an allowance exists instead of asking for a personal
   favour, and anyone who meets C gets the same treatment.

**Security / risk officer** (tunes each institution's proportionality)

10. As a risk officer, I want risk expressed as a FAIR **£ distribution** — ALE, VaR₉₅, TVaR with a
    risk load — from versioned `(min,mode,max)` triples in the repo, so the risk number versions
    alongside the policy.
11. As a risk officer, I want to justify Audit→Deny with a number (`ALE_warn − ALE_deny` against a
    tolerance band), so an enforcement escalation is a proportionate economic decision, not "best
    practice".
12. As a risk officer, I want the *same* control to resolve to Audit in `driftwood` and Deny in
    `ludlow` because their £ differ, so proportionality is demonstrable by comparison across
    institutions.
13. As a risk officer, I want to weigh the **four risk-financing moves** — avoid · reduce · transfer
    (insure) · retain — per risk, so insurance is a first-class control option priced against the
    control £, not an afterthought.
14. As a risk officer, I want each permissive (conditional) branch to carry its residual £ into the
    total, so granting a broader condition visibly raises residual and tightening it lowers it.
15. As a risk officer, I want regulator changes (a fine schedule bump, a new control) to arrive as a
    reviewable PR that re-tunes the £ and therefore the proportionate control, so the estate re-tunes
    as the regulatory world moves.
16. As a risk officer, I want lifecycle/EOL treated as a time-varying feed (past-EOL → unpatched CVEs
    accumulate → £ ramps), so a policy version going unmaintained is priced like any other EOL risk,
    not handled as a bespoke sunset.
17. As a risk officer, I want the £ to be calibratable against emerging actual losses (credibility
    theory), so the number stays falsifiable and defensible to an auditor or insurer.

**Board / CISO** (consumes the top of the hourglass)

18. As a board member, I want technological risk as a **single £ line** framed as economic/risk-based
    capital (Solvency-II style), so I can read, defend, and act on it rather than interpret a RAG
    chart.
19. As a CISO, I want the £ to **move when I'd expect** — accept a condition → it rises; tighten a
    control → it falls; a new threat/EOL lands → it jumps — so the number is alive, not a
    point-in-time assertion.
20. As a board member, I want the residual £ to be the input an underwriter would price a premium off
    (the same controls carriers already price), so the model is validated by the insurance industry's
    own maths.

**Regulator** (`nist`, `ico` — top of the dependency graph)

21. As a regulator, I want to publish versioned, signed, machine-readable artifacts that institutions
    pin as upstream dependencies, so a regulatory change propagates down the graph as a dependency
    bump.
22. As `nist`, I want to ship the genuine 800-53 OSCAL controls catalog, so institutions consume real
    controls-as-code (the "already real today" beat).
23. As `ico`, I want a small, signed, versioned penalty schema (regime → violation-type → fine
    formula/cap) sourced from real public fine magnitudes, so it feeds FAIR loss-magnitude directly
    without being force-fit into OSCAL.

**Auditor** (reads the evidence up-flow)

24. As an auditor, I want each conditional allowance / accepted risk emitted as an OSCAL `risk`
    object (`status: deviation-approved`, remediation `type: accept`, owner, deadline,
    `related-observations` → the failing check), so the exemptions ledger *is* the OSCAL risk
    generator, evidence-linked end to end.
25. As an auditor, I want the £ magnitude attached as an OSCAL `facet` under our own `system` URI
    (the same idiom CVSS uses), so the priced deviation is standard OSCAL, not a fork.
26. As an auditor, I want to verify *which* actor (human or AI) proposed *what*, *when*, *from which
    evidence*, via `gitsign` keyless signatures in Rekor, so I verify the chain rather than trust it.
27. As an auditor, I want an exemption to exist only while a live, unexpired ledger entry backs it
    (Flux prune on retire, TTL backstop), so "no ledger entry, no exception" is literally true.

**War-gamer agent** (the evolved `governance-agent`)

28. As the war-gamer, I want to collect the five signed feeds — institution threat register · CVE ·
    EOL · regulator penalties · market-intel via AI-Wardley — so I reason over current, sourced
    intelligence.
29. As the war-gamer, I want to stress-test current controls against scenarios (ransomware / PQ /
    attack-cost-collapse class), so I detect when residual crosses tolerance or a control has gone
    over-priced.
30. As the war-gamer, I want to **open a signed policy PR** with re-tuned controls on drift and
    **never merge it myself**, so I propose while a human + the PR-gate dispose — safe *because* I
    ride the existing rails.
31. As the war-gamer, I want my every commit/PR to carry my own attestable identity (`gitsign` →
    Rekor), so my proposals are distinguishable from a human's and independently verifiable.
32. As the war-gamer, I want a forward Wardley view (commoditisation, attack-cost collapse, PQ) ahead
    of the reactive feeds, so proportionality re-tunes *before* a threat lands, not after.
33. As the war-gamer, I want my rejected proposals logged as evidence, so the loop calibrates and my
    proposer bounds (confidence, rate-limit) can learn from rejections.

**Presenter** (tours the talk)

34. As the presenter, I want the whole estate to bring up idempotently, offline-safe, and resettable
    between runs on a single laptop, so I can run the live demo at a venue without network luck.
35. As the presenter, I want to re-foreground the institution that matches the room
    (`tuppence`/fintech, `ludlow`/health, `driftwood`/general) with zero rebuild, so the talk is
    audience-modular.

## Implementation Decisions

**Topology & inheritance** (tickets 01, 11)
- Six orgs, all live, all `policy-as-versioned-*` (the prefix is the impersonation guardrail):
  `platform` (shared discipline, real) + `driftwood`/`tuppence`/`ludlow` (fictitious institutions —
  e-comm/PCI+GDPR, fintech/FCA+PCI+GDPR, US-health/HIPAA) + `nist` (real OSCAL catalog) + `ico`
  (real public fine magnitudes, repackaged).
- **Build fresh, no migration.** The existing `policy-as-versioned-flux` estate is **research-only** —
  reference on merit, never cargo-cult. Archive `-flux` as the *last* step, after the new estate stands.
- **One KinD cluster per institution** (three, separate). A per-institution dev cluster is optional and
  built only if we later want the "watch CI pass, then land clean in dev" beat live.
- `platform` is consumed by each institution as a **pinned, signed dependency** (linting `config-base`
  pattern, one level up).

**Distribution — Flux, load-bearing in six named jobs** (tickets 02, 08)
- Version fan-out from one version array (`ResourceSet`); signed `GitRepository` pinned to tag+commit
  for provenance; `prune`-on-retire; reconcile drift-heal (git is the only way cluster state changes);
  `dependsOn`/health ordering; the notification event spine.
- The version array **is** the "supported versions" contract — shift-left reads it directly; no new
  discovery endpoint.
- Crossplane stays the cloud *plane* (a policy target), and is promoted to supply *live posture inputs*
  to quantification only if that maths needs observed cloud state — not built speculatively.

**Enforcement — Kyverno CEL** (tickets 02, 05, 08)
- Keep Kyverno `ValidatingPolicy` (CEL); `validationActions` Audit/Deny/(Warn) is the proportionality
  lever, promoted Audit→Deny by editorial PR, **never on a timer** (determinism: no date logic in
  policy bodies).
- **Version self-scoping is a per-policy `matchConditions` CEL check on the policy-version label — not
  `matchConstraints.objectSelector`** (Kyverno flattens every objectSelector into one shared webhook
  config, last-reconciled-wins, which silently breaks multi-version coexistence). This is the one
  decision precise enough to pin as a snippet:

  ```yaml
  matchConditions:
    - name: only-this-policy-version
      expression: >-
        object.metadata.?labels['mycompany.com/policy-version'].orValue('') == '2.0.0'
  ```

- **Exemptions dissolve into conditional policy** — "you may X *if* conditions C" (team/location/
  attestation/data-class/time-bound), uniform CEL in the policy itself, versioned like any rule.
  `PolicyException` is reserved for a genuine one-off; mechanically an exemption is a **git ledger
  entry → rendered `PolicyException`** (Flux prune + `cleanup.kyverno.io/ttl` backstop), and that
  ledger entry **generates the OSCAL `risk`/POA&M object**.

**Risk engine — FAIR £, pure and deterministic** (tickets 04, 06, 07)
- Versioned `(min,mode,max)` triples → beta-PERT → seeded Monte Carlo → aggregate annual-loss
  distribution → **ALE + VaR₉₅ + TVaR** (Solvency-II tail measure, not just the percentile), with a
  **risk load** so the £ never charges the mean. The pipeline shape (extends the ~40-line `fair.py`
  from research 07 by adding TVaR + load):

  ```mermaid
  flowchart LR
      triples["versioned (min,mode,max) triples"] --> pert["beta-PERT<br/>sampled leaves"]
      pert --> mc["seeded Monte Carlo<br/>per year: freq ~ PERT(lef);<br/>year_loss = Σ PERT(lm) over freq events"]
      mc --> dist["annual-loss distribution<br/>(N seeded iterations)"]
      dist --> ale["<b>ALE</b> = mean"]
      dist --> var["<b>VaR₉₅</b> = 95th pct"]
      dist --> tvar["<b>TVaR</b> = mean of losses<br/>beyond VaR₉₅"]
      tvar --> carried["<b>£ carried</b> = TVaR + risk-load<br/><i>(never the mean)</i>"]
      ale --> cv["<b>control_value</b> = ALE_warn − ALE_deny<br/><i>(what tightening buys)</i>"]
  ```

- **Proportionality = the four risk-financing moves** (avoid · reduce · transfer/insure · retain); the
  war-gamer weighs them; net £ = risk-removed − cost-of-chosen-move, judged against tolerance bands.
- **Appetite locked (relative shape):** `ludlow` strictest (Deny-heavy — HIPAA, decades-confidential,
  HNDL/PQ real); `driftwood` loosest (Audit-heavy — short-life cart data); `tuppence` toward-strict
  (FCA/PCI, availability/fraud flavour). Exact £, bands, and per-institution threat registers *derive*
  during build from FAIR + feeds + org briefs.
- Calibration via **credibility theory (Bühlmann)**; the £ framed as **economic/risk-based capital**.

**Feeds & regulators as upstream dependencies** (tickets 10, 14)
- Five signed, versioned feeds: institution threat register · CVE (trivy/GHSA) · EOL
  (`endoflife.date`) · regulator penalties (`nist` OSCAL + `ico` penalty schema) · market-intel via
  AI-Wardley. Each bumps like a dependency; a change arrives as a reviewable PR.
- `ico` penalties = a small bespoke signed schema feeding FAIR loss-magnitude directly; **not** force-fit
  into OSCAL (which models controls/assessment, not fine schedules).

**Living loop & provenance** (tickets 13, 14)
- `governance-agent` evolves into the war-gamer: collect → war-game → on drift open a **signed policy
  PR**, propose-never-dispose. The PR-gate (version cross-check) + human review + `gitsign` → Rekor +
  versioned distribution are the rails. Scenarios: AI-generated + human seed; results logged back as
  calibration evidence.
- Every actor & action `gitsign`-signed → Rekor; feed→scenario→PR→review→merge→signed-release is
  verifiable end to end.

**Evidence up-flow** (ticket 09)
- `c2p`/OSCAL emits observations + findings today; the ledger extends it to emit `risk` objects
  (`related-observations` → the C2P not-satisfied observation), with £ as a `facet` under a custom
  `system` URI. Balance-sheet sums `facet.value` across `deviation-approved` risks.

**Balance-sheet close** (ticket 06)
- Narrated, not a live beat: **lead insurance** (external validator), **land on the board** (a readable
  line); valuation/diligence = one line. Built real (economic capital, TVaR, provisioning line); the
  moving-£ loop is demonstrated live even though the framing is narrated.

**Deck & runbook**
- First-class Marp deck authored *against the built estate* — every demo-live claim real. Spine: breach
  cost (narrated open) → policy as a versioned dependency → proportionality (live) → living loop (live)
  → provenance (live) → balance sheet (narrated close).
- An idempotent, offline-safe, resettable, audience-modular demo runbook — built last.

**Build order (dependency-driven, Phases 0–7)**
0. Platform skeleton — Flux + Kyverno + version array; `driftwood` minimal, one version live.
1. Risk engine + conditional policy + the £ — FAIR against `driftwood`; `nist` controls feed.
2. The other two institutions + `ico` penalties + the proportionality **comparison** (the money shot).
3. Up-flow + balance sheet (**TCoR**) + shift-left — OSCAL risk objects; residual → £; CI ±1 check.
4. **Graded enforcement** — Kyverno mutate/generate cages a workload by posture (tiers over dials); cage cost feeds TCoR.
5. **Identity plane + workload posture-as-identity** — SPIRE + Istio + OpenBao; Kyverno→SPIRE posture projection (SVID path) + currency controller + label trust-boundary; posture-gated reach + secrets (workload flagship, `tuppence`).
6. **Human/device plane** — Pomerium Core (OIDC + WebAuthn) + SPIRE `tpm_devid`; Mac Secure-Enclave live; posture-gated human access (break-glass); UTM vTPM Windows/Linux EUD VMs (narrated-virtual).
7. Living loop + honesty — feeds + war-gamer (wargames human/device paths too) + AI-Wardley + provenance-for-every-actor; calibration + feed-integrity + reflexive self-governance.

## Enforcement gradient & three-actor identity (folded in 2026-07-31)

The deepening from grilling tickets [16](issues/16-enforcement-response-gradient.md) and
[18](issues/18-human-and-device-identity.md) (research:
[SPIRE posture](research/16-posture-identity-spire.md),
[human/device carrier](research/18-human-device-access-carrier.md)). Not new subsystems — it's **the
one policy**, projected onto more surfaces.

**It's all the policy — one artifact, five projections.** "Which version of the policy do you satisfy?"
determines every surface: **admission** (may you run) · **runtime envelope** (how you're caged) ·
**identity** (the posture claim in your SPIFFE SVID) · **reach** (who you may call) · **entitlement**
(what secrets you get). Least-privilege is the floor for everyone; trust never earns *loose* — posture
only tightens you or narrows your reach.

**Graded response, not admit/deny.** Posture cages a workload's own runtime *by degree* — Kyverno
**mutate + generate** injects resource limits / NetworkPolicy / dropped caps / read-only-fs / a
heavier-WAF sidecar / eviction priority. Deny is the bottom rung. Expressed as **tiers over dials**
(PSS-style presets over independent dials), the tier selected by the £. **Economics = Total Cost of
Risk:** a cage is a *priced partial-reduce on a retained risk* (residual R′>0 **and** run-cost C_cage,
both booked) → **TCoR = residual + cost-of-controls (incl. dynamic cages) + transfer (premiums)**.
"Compliant = cheap" is a computed crossover; the war-gamer picks **fix / cage / transfer / deny** by TCoR.

**Posture-as-identity — three actor classes, one attestation root** (SPIFFE + gitsign/Rekor):
- **Workload** — Kyverno records posture at admission → SPIRE bakes it into the **SVID path**
  (`spiffe://…/posture/vN/…`) via a `ClusterSPIFFEID` template reading a Kyverno-stamped, trust-bounded
  label → **Istio `AuthorizationPolicy`** gates service-to-service, **OpenBao** gates secret issuance.
  A **currency controller** re-evaluates posture post-admission (not a frozen snapshot). Flagship:
  `customer-accounts-reset` (`tuppence`) — a caller out of currency loses reach *and* its secret, live.
  (Posture is in the SVID *path*, not a claim — SPIRE has no native per-entry custom JWT claims.)
- **Human** — supply chain already attestable via **gitsign** keyless (commit/PR → OIDC identity →
  Rekor). Operational access (kubectl / dashboards / break-glass) via **Pomerium Core** (Apache-2.0;
  OIDC + phishing-resistant WebAuthn), gated proportionally — a risky op demands higher assurance.
- **Device (EUD)** — same graded posture. **SPIRE `tpm_devid`** issues device SVIDs on the same root.
  **Mac Secure-Enclave WebAuthn key = the genuine live hardware root** (unclonable). Windows + Linux
  EUDs built + demoed via **UTM vTPM VMs** (Windows Hello; `tpm_devid` → SVID), **narrated as virtual**
  (emulated EK; genuine on real fleet hardware — the point carries). Fleet/osquery = optional,
  honestly-spoofable software posture.

**Carrier decisions (locked):** workload = **SPIFFE/SPIRE**; human/device = **Pomerium Core + SPIRE
`tpm_devid`** — **not Teleport** (Device Trust *and* OIDC connectors Enterprise-only; Community
licence-restricted); secrets = **OpenBao** (JWT-SVID role, `bound_claims` glob on the posture path;
head-start: ControlPlane `getting-started-spire-openbao`). **Provenance for every actor is now
literal** — commit, workload, human, device, one root; the war-gamer wargames human/device attack
paths (phishing / stolen laptop / insider), TCoR absorbs their loss-frequency + controls.

**Added user stories:**
1. As a workload, I carry my satisfied policy version in my SVID, so a service needing a higher bar
   verifies it cryptographically instead of trusting my network position.
2. As a risk officer, I want a workload that falls behind to *keep running but caged* (priced into
   TCoR), so I retain-with-mitigation instead of a blunt deny and the £ shows the cost.
3. As a sensitive-service owner, I accept only callers whose SVID attests the current policy version,
   so a stale caller loses reach with no per-service allowlist.
4. As an operator, break-glass demands a phishing-resistant WebAuthn login from an attested device,
   so a stolen credential or an unmanaged laptop can't invoke it.
5. As an auditor, every actor — commit, workload, human, device — is attestable to one root, so the
   whole chain verifies rather than being trusted.

## Testing Decisions

A good test asserts **external, demonstrable behaviour** — the claim a talk beat makes — not internal
wiring. One seam per independently-demonstrable claim (not per module), each reusing an existing estate
pattern (old estate = research-only prior art, patterns reused, code not).

1. **Risk £ engine — `fair.py` as a CLI seam.** Versioned `(min,mode,max)` triples in → `{ALE, VaR₉₅,
   TVaR}` out; pure, deterministic (seeded Monte Carlo), unit-testable. This is the highest seam for
   the whole risk thesis: the "£ moves when you tighten a control" beat is **two CLI invocations
   differing by one input**, asserted with a self-check (the tail exceeds the mean; a Deny buys
   positive risk vs Warn; TVaR ≥ VaR₉₅). Prior art: the ~40-line `fair.py` drafted in research 07
   (extended here with TVaR + risk load).

2. **Policy enforcement — Kyverno test fixtures per policy.** A `kyverno-test.yaml` per policy asserting
   the admission verdict on three inputs: **pass** (compliant), **fail** (violating), **unversioned**
   (missing the policy-version label → correctly out of scope, proving the `matchConditions`
   self-scoping). Prior art: existing `tests/<name>/kyverno-test.yaml` in the old policy repo.

3. **Live estate beats — one `verify-*.sh` per demonstrable-live claim.** Coexistence (multiple signed
   versions admitting side by side), shift-left ±1-skew (CI catches an Audit→Deny flip pre-merge),
   orphan-guard (a version not in the array cannot run), and the **money-shot proportionality
   comparison** (same control → Audit in `driftwood`, Deny in `ludlow`). Each script exits non-zero if
   the beat it backs would fail on stage. Prior art: existing fleet `verify-*.sh` (coexistence,
   retirement, orphan-guard, monitoring).

4. **War-gamer loop — feed→PR seam.** A signed feed-change fixture in → a policy PR out; asserts
   **propose-never-dispose**: a PR is opened, it is never auto-merged, and the version-cross-check gate
   is present on it. This is the test that makes "the AI is safe because it rides the rails"
   demonstrable rather than asserted.

5. **Graded envelope — Kyverno mutate/generate test.** A `kyverno-test.yaml` asserting a behind-posture
   pod is *mutated into its cage* (limits / netpol / dropped caps present), **not denied**; and the
   tier→dials expansion is deterministic.

6. **Posture projection — SVID integration check.** A pod admitted under vN gets an SVID whose path
   carries `posture/vN`; after vN goes stale, a currency-controller run re-patches/evicts it; a
   user-supplied `posture.*` label is **rejected** (the trust-boundary).

7. **Posture-gated reach + secrets — `verify-*.sh`.** A current-posture caller reaches
   `customer-accounts-reset` and receives its OpenBao secret; an out-of-currency caller is refused
   *both*. Exits non-zero if the beat would fail on stage.

8. **Human/device gate — access check.** A WebAuthn login from the attested Mac reaches a gated op; a
   login lacking the device SVID is refused; break-glass demands step-up.

## Out of Scope

- **Migration of the old estate.** Build fresh; `policy-as-versioned-flux` is research-only and archived
  last. No fork, no code lift.
- **A dedicated per-institution dev cluster.** Optional; the "deploy-time fail even to dev is
  unheard-of" line stays narrated unless we later choose to demo it. The CI ±1 catch *is* the shift-left
  beat.
- **Live balance-sheet / insurance / valuation beats.** Built real, but framed as the narrated close;
  only the moving-£ loop is demonstrated live.
- **Crossplane modelling the version contract.** The version array already is the contract; Crossplane
  stays the cloud plane and supplies live posture inputs only if the risk maths needs observed cloud
  state.
- **Full productionisation of the narrated-vision layer** — regulator-publishes-penalties-as-code as an
  industry norm, full underwriting/board consumption, PQ/attack-cost scenarios beyond one live-runnable
  worked example. Real and grounded, gestured not productionised.
- **FAIR engine sophistication beyond the minimum** — explicit TEF×Vulnerability decomposition, a
  separate secondary-loss simulation, cross-scenario correlation, a distribution-fitting UI. Folded into
  the triples until a scenario demands otherwise.
- **Teleport as the human/device carrier.** Rejected — Device Trust *and* OIDC connectors are
  Enterprise-only, Community is commercially licence-restricted. **Pomerium Core + SPIRE `tpm_devid`**
  instead.
- **Genuine manufacturer-TPM attestation on non-Mac EUDs, and a real MDM/EDR fleet.** The one genuine
  live hardware root is the **Mac Secure Enclave**; Windows/Linux device trust is demoed on **UTM vTPM
  VMs (emulated EK), narrated as virtual**. Real-TPM hardware + fleet MDM/EDR = narrated, not stood up.

## Further Notes

- **Nothing is a "nice-to-have."** Standing discipline for this effort: every component is built or cut,
  and none are cut. The map is decision-complete — the remaining work is build fog (Phases 0–7), not
  decisions.
- **The thesis lives in the comparison.** Portability + proportionality are proven by *comparing*
  institutions — identical control, opposite verdict, different £ — so the two-institutions-plus-the-
  comparison of Phase 2 is the load-bearing demo, not a nice extra.
- **Reflexive self-governance and feed-integrity (Phase 5)** are what make the demo honest under
  scrutiny: the apparatus prices and governs itself, feeds are signed/sourced/bounded, and the gate is
  the hard backstop on the AI proposer.
- Next step after review: `/to-tickets` to split Phases 0–7 into build tickets under
  `.scratch/talk-spec/build/`. Enforcement gradient + three-actor identity fold-in: 2026-07-31.
