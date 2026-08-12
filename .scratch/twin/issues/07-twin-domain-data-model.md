# 07 — The twin domain + data model (the spine)

Type: grilling
Status: RESOLVED (2026-08-04)
Blocked by: 01 (resolved), 06 (resolved)

## Question

The structured, versioned world-model the whole engine attaches to — the domain model + data model of
the twin, grounded in the Netflix / Intel co-flagship subjects. Pin, one at a time:

- **Core ontology & backbone** — the central entities + relationships. Is the **Wardley value-chain
  dependency graph** the single backbone everything hangs off, or is the twin a set of coupled graphs?
- **Layering** — one typed knowledge graph vs separate coupled graphs (value-chain, org/people,
  asset/data, threat). Where do people/roles/knowledge-concentration, assets, market position attach?
- **Edge semantics** — structural dependency vs a distinct **causal/influence** edge (Pearl rungs 2–3,
  per the fable blind-spots) so fast-forward/rewind/play is interventional, not just correlational.
- **Temporal / versioning model** — git history as the temporal spine; scenarios as branches; every
  node/edge/attribute versioned and map-diffable.
- **Representation / format** — build on the OWM DSL (Wardley maps-as-code) + arckit's machine-readable
  artefact graph, or a custom graph store? What's authored-by-hand vs derived?
- **Where £/risk attaches** — loss-exposure on nodes, propagation weight on edges, or a separate risk
  overlay keyed to the graph?

## Acceptance criteria

- [ ] A named core ontology (entity types + relationship types + the backbone) in ubiquitous language.
- [ ] The layering decision (one graph vs coupled) with the seam(s) defined.
- [ ] Edge-semantics decision incl. the structural-vs-causal distinction.
- [ ] The temporal/versioning model + how scenarios are represented.
- [ ] The representation/format decision (reuse vs custom) with what's authored vs derived.
- [ ] Where the £/risk, people, assets and signals attach to the graph.
- [ ] Exercised against Netflix + Intel (does the model actually hold each subject?).

## Decided so far (grilling 2026-08-04)

**Q1 — backbone: (a) a single typed knowledge graph spined on the Wardley value-chain.** Nodes =
components carrying an evolution coordinate; edges = typed dependencies. People, assets, data, market
position, £ exposure, signals and provenance are typed nodes/attributes on that spine — not separate
models. Rationale: a DTO is best built as a live knowledge graph + ontology + feedback loop, and
Wardley already gives that shape; one structure means signal-propagation, blast-radius
(`/arckit:impact` is reverse-dependency traversal) and the £ engine all operate on the same thing.

**Q1b — tenancy: a SHARED WORLD graph + PER-ORG PRIVATE OVERLAYS.** The world layer holds the common
landscape (technologies, markets, geopolitics, how components evolve at large). Each org owns a scoped
overlay — its value chain, assets, people, and its own beliefs — **retained, never shared with other
orgs**. Consequences:
- This is the **multi-tenant shape** purpose-(c) (shippable product) needs, with data sovereignty by
  construction.
- It is *also* the **credibility-theory (Bühlmann–Straub) structure** from `research/risk-threat-sota.md`:
  the **industry prior = the world layer**, the **org's sparse own-data = the overlay**. Cross-org
  learning happens in the shared layer **without private facts leaving the tenant**. Architecture and
  statistics want the same shape — a strong signal this layering is right.

**Q1c — MULTIPLE COMPETING WORLD MODELS is a first-class dimension** (human insight, 2026-08-04). Three
distinct senses, all needed:
1. **Per-org *believed* map** — where the org *thinks* components sit. Can be wrong. **The delta between
   believed and actual IS the anticipation failure** (the Nokia case: the signal reached the top and the
   organisational filter suppressed it). Without this, the twin can't model what kills most correctly-
   anticipated signals.
2. **Rival forecasts** — several plausible evolution trajectories held *simultaneously* with credence
   weights (how fast does quantum really arrive?). The honest representation of Knightian uncertainty on
   the evolution axis, and the legitimate source of scenarios.
3. **Revealed truth** — what actually happened; knowable only retrospectively. The backtest answer key.

**The three compose into the scoring rubric:** at time T you hold belief, forecasts, and (later) revealed
truth. **belief vs revealed** = did the org see it (Nokia). **forecast vs revealed** = was the twin right
(the backtest — Carillion/Enron/NMC). **belief vs forecast** = what the twin should be telling the org
*right now* (the live product, and the Intel forward case). Open: how credences are held and updated.

**Q2 — no privileged "actual" world map: (c) the twin's own belief is the default reference, and is
itself a scored model.** There is a "best current estimate" map used as the default reference so
downstream (£ pricing, blast-radius, scenarios) isn't forced to integrate over a distribution on day
one — but it holds **no privileged status**: it carries its own credence, sits alongside org beliefs and
rival forecasts, and is **falsified by revealed truth like any other model**. Consequences:
- Satisfies **"put the twin inside the twin"** (fable #4) at the *ontology* level, not as a bolt-on, and
  makes the falsifiability claim non-circular — the twin's map can be publicly marked wrong.
- **Every £ number is relative to a named world-model.** Two credible forecasts can price the same risk
  very differently; that spread is *information*, not noise — the honest form of the one-currency claim.
- Option (b) (a pure distribution over maps, no default) remains reachable later: (c)'s credence-carrying
  models are exactly (b)'s components, so it is a widening, not a rewrite.

**Q3 — edge semantics: (b) structural edges + a distinct typed CAUSAL layer on the same graph.**
Structural edges (X *needs* Y) stay and carry blast-radius/propagation (what `/arckit:impact` already
traverses). **Causal edges** are added only where a mechanism can be claimed, carrying **direction, sign,
lag, strength, and the evidence backing the claim**. Interventions (`do(pay rise)`) evaluate on the causal
layer; the graph **degrades gracefully to structural-only** where no mechanism is justified.
Rationale: structural-only (a) makes rewind/play *correlational cosplay* (fable #2) and silently breaks
calibration; a full SCM (c) is the right theory but the wrong whole-graph bet — identification demands
assumptions and data we won't have across an entire org landscape, and it would stall the build on
causal-inference purism.
Two consequences baked in:
- **Causal edges are hypotheses with provenance** — who claimed this, from what evidence, at what
  confidence. Folds directly into the provenance workstream; honesty is visible, not assumed.
- **Intervention-aware scoring is mandatory** — the forecast record must know a prediction was *acted
  upon*, or a mitigated risk that then doesn't occur scores as a bad forecast and poisons calibration.
Both co-flagships exercise it: "Qwikster *caused* the subscriber loss", "the EUV delay *causes* the
process-node slip" — directional mechanism claims, not co-movement.

**Q4 — source of truth: (a) git-versioned text, with a bulk-data exception.** The twin *is* files —
Wardley maps as **OWM DSL**, entities/edges/overlays as typed markdown/YAML in the arckit
artefact-graph style. Any graph store is a **derived, rebuildable index — never authoritative**.
Rationale: git is already the committed temporal spine, so making it authoritative gets versioning,
diffing, branch-per-scenario, blame ("who changed this belief, when, on what evidence") and **signing**
for free instead of reimplementing them in a DB; `/arckit:build --refresh` already does resumable,
hash-staleness-cascading refresh *over files*. Decisively: it is the only option where **the enactment
arm's own thesis applies to the twin itself** — signed, versioned, attestable, reviewable-by-PR — making
reflexive governance structural rather than aspirational.
**Exception (bulk observational data):** the high-volume synthetic substrate (millions of emails/chats/
commits/telemetry) does **not** live in git — it lives in a store, and only its **derived signals** land in
the versioned graph.
Accepted cost: graph queries need an index build step, and very large graphs will eventually strain it —
the right trade for a system whose credibility rests on "you can see exactly what changed, when, and why."

**Q5 — £/risk attaches as (b) first-class scenario objects referencing nodes, with (c) roll-ups as a
derived view.** A **risk scenario** names the threat/event, the affected nodes, the loss form, and holds
the FAIR decomposition (LEF × LM, PERT leaves, Monte-Carlo output). Nodes stay descriptive; cached
roll-ups may be denormalised onto nodes **for query speed only — never authoritative**.
Rationale:
1. **FAIR is scenario-scoped** ("threat actor × asset × effect"), so £-on-nodes fights the committed method.
2. Scenarios span many nodes and nodes join many scenarios — a many-to-many node attributes can only fake.
3. **Candidate responses must be priced too**, and a control attaches to *the scenario it modifies* by
   changing a named FAIR factor (track 05: least-privilege→blast radius, JIT→exposure window,
   SoD→difficulty, UEBA→latency). That mapping only expresses cleanly if scenario *and* response are
   first-class.
Composes with Q2: every scenario references **{graph-version, world-model, time}**, making it the natural
unit for the **backtest** (evaluated at T, scored later against revealed truth) and for **pre-registered
forecasts**. Node attributes could never carry that.

**Q6 — people: (c) individuals as nodes with a SENSITIVITY-SPLIT schema.** The **graph** holds only
*structural* facts — person ↔ component `maintains` / `knows` / `owns` edges — which is all bus-factor and
blast-radius ever needed. All *behavioural* inference (morale, grievance, working patterns) lives in a
**separate gated overlay**: DPIA-controlled, advisory-only (Art. 22), retention-limited, minimised. **Special-
category attributes have no schema slot at all** — Art. 9 compliance becomes an *impossibility*, not a policy
someone must remember to enforce. Detaching the overlay is a demonstrable act (the demo value track 05
identified). Roles-only (b) was rejected because it structurally deletes bus-factor and insider risk. The
behavioural overlay is the most private object in the system and sits inside the per-org scoped overlay
that never leaves the tenant.

## RESOLVED (2026-08-04) — the core ontology

**Backbone:** one typed knowledge graph spined on the **Wardley value-chain**, source-of-truth in
**git-versioned text**, split into a **shared world layer** + **per-org private overlays**.

**Entity types**
- **Component** — the Wardley node (capability / activity / practice / data), carrying an **evolution
  coordinate** + visibility. The spine.
- **WorldModel** — a *named, credenced* belief-set about component positions and trajectories. Instances:
  the **twin's own** (default reference, itself scored), each **org's believed** map, **rival forecasts**,
  and **revealed truth** (retrospective).
- **Org** + **Overlay** — the scoped, owned, private per-tenant layer.
- **Person** — structural `maintains`/`knows`/`owns` edges only.
- **BehaviouralOverlay** — gated, DPIA-controlled, advisory-only, minimised; **no special-category slot**.
- **Asset / DataAsset**, **Signal** (STEEP-tagged observation with provenance, interpreted *against* a
  WorldModel), **RiskScenario**, **Response/Control**, **Forecast** (pre-registered, scored later),
  **Provenance** (on every claim).

**Relationship types**
- **Structural dependency** (`needs`) — carries blast-radius + propagation.
- **Causal/influence** — direction, sign, lag, strength, **evidence + confidence**; interventions
  (`do(x)`) evaluate here; degrades gracefully to structural-only.
- **Knowledge/maintenance** (person↔component) — the bus-factor substrate.
- **Scenario references** — RiskScenario → {nodes, graph-version, world-model, time}.
- **Response modifies** — Control → a named FAIR factor of a Scenario.

**Authored vs derived.** *Authored:* components, dependencies, causal claims + evidence, world-models,
overlays, scenarios, responses, forecasts. *Derived (rebuildable, never authoritative):* the graph
index/store, £ roll-ups on nodes, Wardley D/K/R metrics, blast-radius results, signals extracted from the
bulk substrate.

**Exercised against the co-flagships**
- **Netflix** — backbone: streaming experience → content pipeline → CDN/encoding → cloud compute →
  talent/culture. Evolution shift (DVD→streaming) propagates up the chain; causal edge "Qwikster →
  subscriber loss" with dated evidence; behavioural overlay carries culture/keeper-test/comp *as gated
  synthetic substrate*; scenarios priced against the twin's world-model at dated points; **belief vs
  revealed** scoring available across 2011 and 2022.
- **Intel** — backbone: product → design → **process node / fab** → EUV tooling → capital. The live crisis
  is one node sliding and dragging everything above it; rival forecasts (foundry-recovery trajectories)
  held simultaneously with credences; **pre-registered forward forecasts** referencing
  {graph-version, world-model, time}, scored later against what materialises.
- The same shape absorbs two very different orgs — which is what a single typed backbone must do.

## Acceptance criteria — all met
- [x] Named core ontology (entities + relationships + backbone) in ubiquitous language.
- [x] Layering decision (shared world + per-org overlays) with the tenancy seam defined.
- [x] Edge semantics incl. the structural-vs-causal distinction.
- [x] Temporal/versioning model (git-native) + scenarios as first-class, branch-per-scenario.
- [x] Representation/format (OWM DSL + arckit artefact-graph style; store = derived index) + authored-vs-derived.
- [x] Where £/risk (scenario objects), people (sensitivity-split), assets and signals attach.
- [x] Exercised against Netflix + Intel.
