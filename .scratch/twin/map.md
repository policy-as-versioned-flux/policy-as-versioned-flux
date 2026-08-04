# Organisational digital twin + anticipatory governance — the whole thing

`wayfinder:map`

## Destination

A rigorous, comprehensive **digital twin of an organisation** and an **anticipatory
strategic-intelligence engine**: it senses *any* signal — external (quantum, memory cost, AI-model
access, sanctions, East–West realignment, climate, supply-chain, M&A) and internal (people, morale,
knowledge concentration, comp, working patterns) — maps it onto the org's Wardley/dependency
landscape, **war-games the what-ifs (fast-forward · rewind · play)**, prices every impact *and every
candidate response* in **one £ risk currency**, and recommends the **cheapest proportionate response
wherever it lives** — an HR lever, a security control, a strategic play. Versioned, attestable
governance is *one enactment arm*, not the point.

**Plan the whole thing to full ambition — everything is modelled. The demo scope is worked backwards
from the plan, later.** Built **skills-first, from basics**, on **real risk modelling and real
Wardley** — nothing inherited from the toy prior.

Done when: the whole is charted comprehensively (all workstreams, seams, and explicit acceptance
criteria), grounded in real methodology, with a worked-backwards demo slice — such that a build could
start any track without re-deciding its basis.

## Notes

**This is a fresh chart. The old `.scratch/talk-spec/` effort is a *prior to test*, not a foundation.**
Git holds all history; the **specs (`.scratch/talk-spec/spec.md`, `the-whole-model.md`) are the
reference-grade detail** — look back only when needed. Every old idea (proportionality hourglass,
policy-as-versioned-dependency, graded enforcement, posture-as-identity, TCoR, the living loop,
provenance-for-every-actor) is a **hypothesis** the real risk + Wardley work confirms or refutes.

**Settled framing (from charting grilling 2026-08-04 — do not re-litigate without the human):**
- **Destination = the rigorous real system**, not a talk. Optimising for a demo is exactly what
  produced the monorepo + toy risk; making the real, right, comprehensive thing the north star stops
  the shortcuts. The talk is a *byproduct*.
- **The reframe:** the project is an **org digital twin + anticipation engine**; versioned governance
  is one enactment arm (the IT/security slice).
- **Scope is total.** Any factor that can move the org's landscape is in scope — external and
  internal. Quantum was one example; nothing is excluded by category.
- **One £ risk currency → cross-domain comparison** is the payoff: a *pay rise* (HR control) and
  *security hardening* (tech control) become comparable options against the same modelled risk;
  pick the cheaper proportionate one. Governance stops being siloed.
- **Fear *and* opportunity.** The same intelligence that says "defend" surfaces the strategic play to
  *seize* (Wardley gameplay). The engine feeds strategy/roadmap, not just the risk register.
- **Falsifiability.** The twin's what-if projections are checked against **what actually
  materialises**; it earns trust by being wrong in public sometimes and calibrating.
- **Reflexive governance + ethics is a design requirement, not a footnote.** The twin governs its own
  surveillance and its own AI — DPIA, minimisation, transparency, consent, AI assurance. Sensing
  morale/comp/behaviour to predict insider risk is legally and ethically loaded and must be governed.
- **Synthetic substrate.** The org's operational + behavioural data (email, chat, commits, HR events,
  supply-chain, telemetry) is **AI-synthesised with realistic noise** — never real surveillance. This
  resolves the cardboard-org problem, sidesteps the real-data ethics for the *demo* (the ethics
  guardrail then governs *real* deployment), and — because *we* generate it — lets us **plant weak
  signals with known ground truth**, making signal-detection and the what-if→materialises loop
  *validatable* rather than asserted.
- **Multi-org reality.** Keep + use the **six real GitHub orgs** (`policy-as-versioned-*`). The
  enactment arm is real separate repos with real signed dependency pins — never a monorepo. Bin the
  `estate/` monorepo + the KinD clusters.
- **Skills-first, from basics; no rush; right + comprehensive; ambition = everything.**
- **Structure = disconnected parallel workstreams**, each with its **own checkpoints** and
  **explicit acceptance criteria**, wired at defined seams.
- **External falsifiability gates (added 2026-08-04, from the fable blind-spots pass).** Magnum-opus
  governs *scope* — no external gate on ambition or coverage. But a small, non-negotiable set of
  external *reality* gates governs the **honesty** claim: a **pre-registered forecast book** on
  real-world externals (scored later against what happens), **blind/adversarial planting** (the grader
  never saw the ground truth), **one external witness**, and a **frozen portfolio**. Own standard = how
  comprehensive; reality = whether it is true. This closes fable's meta-critique: otherwise every loop
  — validation, calibration, falsification, and the yardstick itself — closes through one mind.
- **History IS the external ground truth (added 2026-08-04).** Reconstruct the flagship's **real,
  documented history** as a time-series of Wardley/dependency states; back-test the anticipation engine
  by rewinding to a real past state, fast-forwarding, and scoring projected movement against what
  *actually* happened. The org's past is surprise we did not author — the strongest falsifiability
  mechanism. Implies the flagship needs a **real historical spine** (a single real org's public
  history); only the internal behavioural substrate is synthesised. "If we don't know where we've been,
  we can't know where we're going."

**Methodology backbone — use the `/arckit:*` toolkit** where it fits: `requirements`, `stakeholders`,
`principles`, `adr`, `wardley` (+ `value-chain`/`doctrine`/`climate`/`gameplay`), `risk` (Orange
Book), `secure`, `dpia`, `atrs`, `ai-playbook`, `data-model`, `finops`, `roadmap`; plus the
`wardley-mapping` / `mermaid-syntax` skills. **Skills each session should also consult:** `/grilling`,
`/domain-modeling`; the repo's `docs/agents/issue-tracker.md`.

## Decisions so far

<!-- index of closed tickets; the settled framing above came from charting, not from tickets -->

- [Rigorous risk & threat modelling SotA](issues/02-research-risk-threat-sota.md) — keep the FAIR skeleton; add calibrated estimation (Hubbard), empirical heavy-tailed anchoring (Cyentia/DBIR), credibility theory (Bühlmann–Straub) + back-testing; threat-modelling (STRIDE/attack-trees/ATT&CK) grounds frequencies; copulas + TVaR; reject risk matrices, CVSS-arithmetic, black-box CRQ. Full: `research/risk-threat-sota.md`.
- [Org digital twins, Wardley automation & horizon scanning SotA](issues/03-research-twin-wardley-horizon-sota.md) — DTO = a live knowledge-graph + ontology + feedback loop (not a simulator); Wardley (OWM DSL + arckit) is the shape; STEEP weak-signals interpreted against the model (Hiltunen); **git history IS the temporal spine** — branch-per-scenario + map-diff = fast-forward/rewind/play. Full: `research/twin-wardley-horizon-sota.md`.
- [Insider-risk modelling + ethics guardrail SotA](issues/05-research-insider-ethics.md) — CERT Critical Pathway (features) + FAIR (£); MICE(S); ~80%% grievance-driven; levers map to FAIR factors (least-priv/JIT/SoD/UEBA) so pay-rise-vs-hardening is computable; guardrail for real deploy = LIA + mandatory DPIA + advisory-only (Art.22) + no special-category (Art.9); synthetic data means demo is exempt. Full: `research/insider-risk-and-ethics.md`.
- [The arckit toolkit — capability map](issues/04-research-arckit-toolkit.md) — arckit 6.7.5 = a 73-command governance harness on a machine-readable artefact graph; Wardley maths (D/K/R) recomputable; **`/arckit:impact` (blast-radius) and `/arckit:build --refresh` (DAG-cascading refresh) already exist**; net-new = a scenario object `{baseline,moves[],drivers[]}`; caveats: impact has no history, £ deltas are prose not formulas, refresh assumes one repo (we are org-of-repos). Full: `research/arckit-capability-map.md`.
- [The subject & purpose — the keystone](issues/01-subject-and-purpose.md) — **RESOLVED.** Subject = a fictitious org with an AI-synthesised noisy substrate + planted ground truth, realism grounded in deep cross-sector OSINT study; **1 flagship (max depth) + a portfolio (shallower-but-convincing, independently depth-upgradable)**; N-org model + per-org depth grade; flagship identity picked by an exhaustive OSINT survey (NOT Disney). Purpose priority: **magnum-opus > product > research > persuasion**. Success = coverage + runnable + honest + legible, every workstream with its own ACs. Refined: flagship = **real-history spine (backtest ground truth) + synthetic behavioural substrate**.

## Not yet specified

<!-- the whole ambition lives here as fog until the foundation resolves it into tickets;
     these are the parallel workstreams, each will graduate with its own acceptance criteria -->

- **The digital twin model** — the org's structured, live world-model: value chains (Wardley),
  supply chain, tech + data assets, people/roles/**knowledge concentration**, dependencies, risk
  posture, market position. The domain model + data model of the twin. (Graduates after the
  foundation names the subject org.)
- **The synthetic org substrate** — the AI-generated, noisy, realistic operational + behavioural data
  (email, chat, commits, HR events, supply-chain, telemetry) the twin *senses*, with **planted weak
  signals + known ground truth** so detection and the what-if→materialises loop are validatable. The
  generator itself is a capability/skill.
- **The Wardley evolution engine** — every tracked factor on genesis→commodity; signals move
  components; movements **propagate through the dependency graph**; automated/maintained via
  `/arckit:wardley`.
- **Omni-signal horizon scanning** — ingest *anything* (external + internal) and classify each signal
  against the twin: does it move a component? The ever-growing factor set; STEEP/foresight practice;
  the **people/behavioural sensors** (comp, promotion, workload, email/chat/commit/working-patterns)
  — each gated by the ethics/law guardrail.
- **Retrospective history modelling + backtest (the falsifiability spine)** — reconstruct the
  flagship's *real* documented history as versioned Wardley/dependency states; score the engine's
  rewind→fast-forward projections against what actually happened. Doubles as the external honesty gate.
  Needs the causal layer (Pearl rungs 2–3), not just a correlational graph.
- **The scenario / gameplay engine — fast-forward · rewind · play** — project a trend, replay a
  counterfactual, run a scenario; Wardley gameplay + climate + doctrine; the **scenario library**
  (quantum/HNDL, bus-factor/key-person, insider/coercion, supply-shock, sanctions, M&A, memory cost,
  AI-model access, climate event) — these double as the **acceptance tests** each workstream satisfies.
- **The £ risk currency + cross-domain pricing** — price impacts *and* candidate responses in one
  currency; the pay-rise-vs-hardening comparison; calibration, back-testing, falsifiability.
- **The enactment arm — versioned multi-org governance** — the original thesis re-grounded: six real
  org repos, signed dependency pins, graded controls, posture-identity — each control now *justified
  by real risk*, not assumed. Also: the non-IT enactments (HR/process/strategy levers).
- **Provenance / attestation / evidence** — every signal → inference → decision → action attestable
  and auditable end to end.
- **Reflexive governance & ethics** — the twin governs its own surveillance + AI (DPIA, minimisation,
  transparency, AI assurance via ATRS / AI-playbook); the honesty/falsifiability discipline.
- **The skill inventory (skills-first)** — which reusable capabilities become agent skills
  (twin-model, signal-classify, wardley-engine, scenario-runner, £-pricing) and their build order.
- **Work backwards to the demo** — once the whole is planned, define the minimal demonstrable slice +
  its acceptance criteria. (Blocked by the plan being fleshed out.)

## Out of scope

<!-- ruled beyond the destination; never graduates -->
- **Talk-first framing** (the old map's destination). The conference talk is now a *byproduct* of the
  real system, not its driver. It returns only as a downstream showcase, never as the thing we
  optimise for.
