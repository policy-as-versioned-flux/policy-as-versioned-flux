# Talk spec → delivery refactor: risk-based, versioned, shift-left governance on Flux

`wayfinder:map`

## Destination

A **conference-grade talk** (first-class **Marp** deck) that lands one thesis — *governance
should be a **proportionate, informed response to quantified risk**, and versioning the whole
chain from risk-appetite to evidence is how you keep that proportionality honest, current, and
provable* — **backed by a fully-real, refactored demo estate** where every claim is demo-live, not
narrated. Because the map works *backwards from the talk*, the destination includes the **delivery
refactor** the demo-live claims require. Done when: the talk spec (spine, claims, deck) is locked
**and** the estate is refactored so nothing in the talk is faked or hinted.

## Notes

**This map carries execution** (override of wayfinder's plan-only default): the destination is a
built talk + built estate, so tickets may *do*, not only decide. Even so, chart decisions before
builds — the build tickets graduate out of the fog once the design decisions lock.

**The whole model on one page:** [`the-whole-model.md`](the-whole-model.md) — the consolidated
picture (integrated diagram, six-org provenance graph, components, build order, and the talk's
spine + demonstrable-core-vs-narrated-vision split). Read that for the synthesis; the framing below
is the ground truth it's built from.

**Settled framing (from charting grilling — do not re-litigate without the human):**
- **Spine = risk-based proportionality.** Open on *what a breach costs*, not on GitOps. Versioning
  is the *mechanism*; the hourglass is the *structure*; risk is the *ground and the scoreboard*.
- **The model (one page):**
  `RISK APPETITE (£ fine/breach/downtime)` → sets proportionality → `PRINCIPLES → CONTROLS →
  ENFORCEMENT` (controls *tuned* to risk: Audit vs Deny, CVE tolerance, sunset pace; versioned, so
  a bump = proportionality moving as the world moves) → `EVIDENCE (OSCAL)` flows up → minus the
  `EXEMPTIONS LEDGER` (each entry priced, scoped, expiring, versioned carried-risk) → `RESIDUAL
  RISK` → the ingredient for a **BALANCE-SHEET / INSURANCE £ number** (built real, provable).
- **Shift-left is a pillar.** Cluster advertises supported policy versions (service-discovery /
  kubectl ±1-skew analogy); dev + CI check compatibility *before* deploy. Culture: compliant path =
  path of least resistance; CI fail = big deal; deploy-time fail (even to dev) = practically
  unheard of → kills the "I'm special, grant me an exemption" reflex.
- **Exemptions dissolve into conditional policy.** Not carve-outs — "you may X *if* you meet
  conditions C" (team, location, attestation, no-PII, data-class, time-bounded), applied uniformly
  to anyone who meets them. It's all policy (CEL), versioned; the residual risk of each permissive
  branch still feeds the £. Kills the wedge (no favour to expand) and forces articulating the *why*.
- **The living loop (keeps proportionality current).** AI-Wardley (market-intel-driven, anticipates
  commoditisation) + reactive feeds (threat-landscape/CVE/EOL/penalties) → a **war-gaming agent**
  (governance-agent evolved) stress-tests the controls → on drift, **opens a policy PR** → human
  review + PR-gate + gitsign + versioned distribution *dispose* → estate re-tunes → balance-sheet £
  moves. The AI **proposes, never disposes**; it's safe *because* it rides the existing rails.
- **Provenance for every actor.** Every commit/PR — human or AI — carries its own attestable
  identity (gitsign keyless → Rekor), so feed → scenario → PR → review → merge → signed release is
  verifiable end to end: which actor proposed what, when, from which evidence. How you trust an
  AI-enabled org.
- **Balance-sheet north star:** put technological risk on the business balance sheet — insurable,
  valuable in diligence, board-legible. Build it real; the human may still cut it from the *talk*,
  but only after it's comprehensively proven.
- **Actuarially grounded (folded in 2026-07-23).** FAIR *is* frequency×severity; add **TVaR** (not
  just VaR₉₅) and a **risk load** (never charge the mean). Proportionality = the four risk-financing
  moves — **avoid · reduce · transfer (insure) · retain** — so *insurance is a control option* the
  war-gamer weighs. Calibration via **credibility theory (Bühlmann)**. Balance sheet = **economic /
  risk-based capital** (Solvency-II framing). Validations: underwriting-warranties ↔ conditional
  policy; cat-modelling ↔ war-gamer; IBNR reserving ↔ the provision.
- **Lifecycle/EOL is a risk thread, not a bespoke "sunset".** A policy version going unmaintained is
  the same shape as RHEL/Windows/Node/library EOL: past-EOL → unpatched CVEs accumulate → risk £
  ramps. It's a time-varying intelligence feed (real: `endoflife.date`) consumed like the regulator
  artifacts; the policy version's own lifecycle is one row in it. Dissolves the sunset escalator
  into the risk model.
- **Nothing is a "nice-to-have"** — every component is built or cut; none are cut. Standing
  discipline for this effort.

**Hard constraints:**
- **Flux is the anchor — must be central and load-bearing** (ControlPlane sponsors the work).
- **Everything else (incl. Kyverno) is an open design decision** — reselect tech on merit.
- **Fictitious organisation** — real cluster, real apps, real £ numbers, but not a real business;
  so modelling real fines/risk is fine and carries no real-world exposure.
- **No cuts / make it real.** No slideware, no "hint only". Not time-boxed.
- **Deliverable = Marp slides**, first-class.

**Skills each session should consult:** `/grilling`, `/domain-modeling`, `/prototype`, `/research`;
the repo's `docs/agents/issue-tracker.md` (local-markdown tracker, "Wayfinding operations").

## Decisions so far

<!-- index of closed tickets; the settled framing above came from charting, not from tickets -->

- [RESEARCH: cyber-risk quantification (FAIR)](issues/07-research-risk-quantification.md) — FAIR is
  directly implementable (Risk = LEF × Loss Magnitude → beta-PERT + Monte Carlo → ALE, VaR95,
  loss-exceedance curve); a ~40-line numpy `fair.py` reference already drafted + self-checked.
  "Audit→Deny" is a number: £ a control buys = `ALE_warn − ALE_deny`, judged against quantitative
  tolerance bands. Insurance underwriting prices the *same* controls (±20–40% premium) = real
  external validation. Because inputs are versioned triples in the repo, **the risk number versions
  with the policy.** Full doc: `research/07-risk-quantification.md`.
- [RESEARCH: OSCAL risk / POA&M](issues/09-research-oscal-risk.md) — OSCAL carries the risk half
  **natively**: `risk` assembly + POA&M with `status:deviation-approved` / remediation `type:accept`
  / owner / `deadline` / evidence link → a ledger exemption maps **1:1**. Only the £ magnitude is
  non-native, attached idiomatically as a custom `facet` (same path CVSS uses). Our C2P output stops
  at findings and never emits a `risk` — so the **exemptions ledger becomes the generator of OSCAL
  `risk` objects**. Full doc: `research/09-oscal-risk.md`.
- [Architecture skeleton & Flux's role](issues/02-architecture-and-flux-role.md) — **confirmed the
  research skeleton, everything built (no cuts):** keep Kyverno; Flux load-bearing in 6 named jobs;
  exemptions = git-ledger-entry → rendered Kyverno `PolicyException` (Flux prune + ttl); shift-left
  = ±1 skew off the `ResourceSet` array; Crossplane stays the cloud plane. `trivy`/`c2p`/`OSCAL`/
  `governance-agent`/`handbook-generator`/`policy-reporter` all in. **Sunset dissolved into
  lifecycle/EOL risk** → routed to the risk model (04) + upstream feeds (10). Subsystem diagram +
  cluster shape → ticket 11.
- [The fictitious organisation](issues/01-fictitious-organisation.md) — **not one org, a six-org
  topology, all live, all `policy-as-versioned-*`** (human created them 2026-07-23): `platform` (the
  inherited discipline) + institutions `driftwood`/`tuppence`/`caldera` (e-comm/fintech/health) +
  regulators `nist` (real OSCAL controls) & `ico` (real public fines, machine-readable). The prefix
  is the impersonation guardrail. Existing `policy-as-versioned-flux` → **archive as the last
  migration step**, not now. Portability + proportionality proven by *comparing* institutions (same
  control, different Audit/Deny + £ per regulator skin). Per-org risk numbers → ticket 04.
- [RESEARCH: enforcement engines under Flux](issues/08-research-enforcement-engines.md) — **keep
  Kyverno** (`ValidatingPolicy` CEL); it wins on all three criteria and switching buys nothing with
  Flux as the anchor. `PolicyException` has no native expiry → close it by making the exception a
  **rendered artifact of a git ledger entry** (Flux `prune` on retire + `cleanup.kyverno.io/ttl`
  backstop), which *literally implements* the ledger's "exception only valid if a live entry backs
  it". **Flux is load-bearing in six named jobs.** Crossplane stays the cloud *plane*, does **not**
  model the version contract (the `ResourceSet` array already is it). Shift-left = kubectl-style
  **±1 version-skew** read off that array, `kyverno apply` runs the target version's real action so
  Audit→Deny is caught pre-deploy. Full doc: `research/08-enforcement-engines.md`.
- [Risk & proportionality model](issues/04-risk-proportionality-model.md) — FAIR (freq×severity) →
  **ALE + VaR₉₅ + TVaR** + risk-load; proportionality = the four moves (avoid·reduce·transfer·retain);
  five signed feeds; Bühlmann calibration. **Appetite locked:** `caldera` strictest (Deny-heavy),
  `driftwood` loosest (Audit-heavy), `tuppence` toward-strict. **Money-shot:** same control = Audit in
  `driftwood`, Deny in `caldera`, because the £ differs. £/bands derive during build.
- [Exemptions → conditional policy](issues/05-exemptions-ledger.md) — dissolved into CEL "you may X
  *if* C", uniform + versioned; residual of each permissive branch feeds the £. Mechanically:
  git-ledger entry → rendered `PolicyException` (Flux prune + ttl) → generates the OSCAL `risk`/POA&M.
- [Balance-sheet quantification](issues/06-balance-sheet-quantification.md) — the **narrated close**,
  not a live beat; **lead insurance** (underwriters price the same controls = external validation),
  **land on the board** (risk as a readable line); valuation one-lined. Built real (economic capital,
  TVaR); the moving-£ loop is demonstrated.
- [Regulator-as-upstream-dependency](issues/10-regulator-as-upstream-dependency.md) — regulators are
  versioned+signed upstreams: **`nist` = real OSCAL** controls; **`ico` = a bespoke signed penalty
  schema** feeding FAIR loss-magnitude (not force-fit into OSCAL). CVE + `endoflife.date` EOL ride the
  same pattern; a regulator change arrives as a reviewable PR.
- [Multi-org topology & inheritance](issues/11-multi-org-topology-inheritance.md) — **build fresh, no
  migration** (fiction ⇒ no sunk cost; old estate is research-only, never cargo-cult); a **KinD
  cluster per institution** (big laptop); `platform` inherited as a **pinned, signed dependency**;
  archive `-flux` last.
- [War-gaming AI policy-PR agent](issues/13-wargaming-ai-policy-pr-agent.md) — `governance-agent`
  evolved: collect feeds → war-game → on drift **open a signed policy PR**; **proposes, never
  disposes** (rides human + PR-gate + gitsign→Rekor rails); every actor attestable end to end.
- [Wardley strategic layer](issues/14-wardley-strategic-layer.md) — **AI + market-intel** anticipation
  of commoditisation / attack-cost-collapse / PQ, *ahead* of the reactive feeds; hands the war-gamer a
  forward view so proportionality re-tunes before the threat lands.

## Not yet specified

**MAP DECISION-COMPLETE (2026-07-23).** Every design decision is locked — nothing remains to *decide*
before building. The frontier is empty of decision tickets; what's below is **build fog**, sequenced
by the build order in [`the-whole-model.md`](the-whole-model.md) (Phases 0–5), and is the input to
`/mattpocock-skills:implement`. These graduate into build tickets as each phase is picked up, not
before — no decision blocks them.

<!-- build fog — execution, not decisions (this map carries execution per Notes) -->
- **The delivery refactor** — the six-org estate built fresh: `platform` discipline + the three
  institution estates, Phases 0–5. The bulk of the build.
- **The Marp deck arc & build** — slide structure now sharp (spine locked); authored against the
  built estate so every demo-live claim is real.
- **Demo runbook & rehearsal** — the idempotent, offline-safe, resettable live-run script; last.
- **Calibration / back-testing** of the FAIR £ — folded into the risk-engine build (Phase 1/5).
- **Securing the security system** — feed integrity + AI-proposer bounds + gate backstop (Phase 5).
- **Reflexive self-governance** — the apparatus prices + governs itself (Phase 5).

## Out of scope

<!-- ruled beyond the destination; never graduates -->
- (none ruled out yet)
