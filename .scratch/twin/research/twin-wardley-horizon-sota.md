# State of the art: living digital twin of an organisation + Wardley automation, horizon scanning & scenario simulation

Research briefing for ticket `03-research-twin-wardley-horizon-sota`. Cited, with pitfalls, and a
practical seam for our engine at the end.

Scope: (1) enterprise / organisational digital twins, (2) Wardley mapping + automation, (3) horizon
scanning / strategic foresight, (4) scenario simulation. All four are combined in the seam section —
the point of the ticket is that they're one engine, not four.

---

## 1. Enterprise / organisational digital twins (DTO)

### What it is (the vendor/analyst definition)
Gartner coined **Digital Twin of an Organization (DTO)** in 2017. Their working definition: *"a dynamic
software model … that relies on operational and contextual data to understand how an organization
operationalizes its business model, connects with its current state, responds to changes, deploys
resources, simulates future states, and delivers customer value."* The key word is **dynamic** — a DTO
is an EA model with a live feedback loop from operational data, not a static architecture diagram.

- Gartner, *Quick Answer: What Is a Digital Twin of an Organization?* — https://www.gartner.com/en/documents/4004172
- Gartner Peer Insights market page (DTO platforms) — https://www.gartner.com/reviews/market/digital-twin-of-an-organization-platforms
- Gartner ran a **first-ever Magic Quadrant for DTO Platforms in 2026** (18 vendors), which is the clearest signal the category has crossed from concept into a named market — https://www.gartner.com/en/conferences/emea/applications-uk/sessions/detail/4956515-Magic-Quadrant-for-Digital-Twin-of-an-Organization-Platforms ; SAP named a leader — https://news.sap.com/2026/07/sap-leader-gartner-magic-quadrant-digital-twin-organization-platforms/

Gartner buckets DTO use cases into four: **business operations** (supply chain, process intelligence),
**customer excellence**, **governance/risk/compliance**, and **strategy realisation** (transformation,
cost optimisation). Our engine sits squarely in the last one.

### What's real vs marketing
- **Real:** process-mining / operations twins. Vendors like Celonis, SAP Signavio, Software AG (ARIS)
  do genuinely mine event logs and reflect the *as-is* process. This is the mature, shipping end.
- **Real (EA end):** Ardoq, QualiWare, LeanIX-style tools that keep a live-ish graph of
  business/application/technology architecture and overlay operational data.
  - Ardoq, *Evolution of EA: Digital Twin of an Organization* — https://www.ardoq.com/blog/digital-twin-of-an-organization
  - QualiWare DTO — https://www.qualiware.com/digital-twin-of-an-organization
- **Marketing / aspirational:** the "simulate future states" half. Most "DTO" products are excellent
  *mirrors* of the present and weak *simulators* of the future. Predictive/what-if is where the
  category over-promises. BMC's overview is candid that DTO is largely repositioned EA + analytics —
  https://www.bmc.com/blogs/digital-twins/

### Academic reference models & data models (the useful prior art)
The strongest academic thread models a DTO as an **enterprise knowledge graph + ontology**, not a
simulation engine:

- **Riss, Maus, Javaid et al. (DFKI, 2020), *Digital Twins of an Organization for Enterprise Modeling*** —
  the anchor paper. A DTO draws on a **graph-based, machine-readable knowledge representation** of
  enterprise models, and introduces **"Context Spaces"** that present the model's information
  semantically structured for a given decision context. Springer chapter:
  https://link.springer.com/chapter/10.1007/978-3-030-63479-7_3 · DFKI record: https://www.dfki.de/en/web/research/projects-and-publications/publication/11197
- **Architectural Concerns for Digital Twin of the Organization** (Springer, 2020) — enumerates the
  architectural concerns (continuous feedback loop between EA models and operational data, situational
  awareness) you have to solve to *evolve* a DTO — https://link.springer.com/chapter/10.1007/978-3-030-58923-3_18
- **Ontologies in Digital Twins: A Systematic Literature Review** (arXiv 2308.15168) — confirms the
  field's convergence on ontology/RDF/knowledge-graph as the twin's data model —
  https://arxiv.org/pdf/2308.15168
- Cross-domain reference architectures worth stealing structure from: the IETF **Network Digital Twin**
  reference architecture (data / modelling / management / twin-entity layers) —
  https://datatracker.ietf.org/doc/draft-irtf-nmrg-network-digital-twin-arch/09/ — and Enterprise
  Knowledge's *Digital Twins and Knowledge Graphs* (ontology as the schema that fuses many systems) —
  https://enterprise-knowledge.com/digital-twins-and-knowledge-graphs/

**Takeaway for us:** the credible prior art says a DTO = **a live knowledge graph of the org with an
ontology on top and a feedback loop from operational data**, sliced by *context* for decisions. That is
exactly a repo/policy/fleet dependency graph. We already have the graph (the org of repos); the twin is
that graph made queryable + a feedback loop.

### Pitfalls (DTO)
- **Model rot / freshness.** A twin that isn't continuously fed from operational data is just an EA
  diagram that lies with confidence. The feedback loop is the product, not the model.
- **Boiling the ocean.** DTO programmes die trying to model the whole enterprise. Context Spaces exist
  precisely so you model *per decision*, not exhaustively.
- **"Simulate future states" is the weakest, most-oversold capability.** Don't inherit that promise
  unless the simulation is grounded (see §4).

---

## 2. Wardley mapping — the method and automating it at scale

### The method (Simon Wardley)
A Wardley Map plots a **value chain (y-axis, user need at top → components below)** against
**evolution (x-axis)**. Evolution has four stages: **Genesis → Custom-Built → Product (+rental) →
Commodity (+utility)**. The map sits inside the **Strategy Cycle**: Purpose → Landscape → **Climate**
(external forces that act regardless of you) → **Doctrine** (universal, context-free good practice) →
**Leadership/Gameplay** (context-specific moves). Roughly ~30 climatic patterns, ~40 doctrine
principles, ~100+ gameplay patterns.

- Wardley's book, *Doctrine* chapter — https://medium.com/wardleymaps/doctrine-8bb0015688e5
- Primers: https://learnwardleymapping.com/ · https://www.davesresearch.com/wardley-mapping/ · Wikipedia — https://en.wikipedia.org/wiki/Wardley_map

The three lenses map cleanly onto automation:
- **Climate** = rules you can *evaluate* against a map ("everything evolves"; "efficiency enables new
  value"). Automatable as assertions over the graph.
- **Doctrine** = a *lint pass* ("use a common language", "focus on user need", "remove duplication /
  bias"). Automatable as checks.
- **Gameplay** = *suggestion engine* given position + movement.

### Automating / maintaining maps at scale — existing tooling (reuse, don't build)
- **Online Wardley Maps (OWM)** — open-source, and the de-facto **"maps as code" DSL** (a plain-text
  format: `component X [value, evolution]`, `X->Y` dependencies, `evolve`, `anchor`, notes). This is
  the serialization to standardise on. https://onlinewardleymaps.com/ · docs https://docs.onlinewardleymaps.com/ · "Maps as Code" https://learnwardleymapping.com/project-type/maps-as-code/
- **MapScript** (Mario Platt) — Wardley maps as *programmable* Observable notebooks; treats a map as a
  data structure you can compute over. https://medium.com/@marioplatt/using-mapscript-for-wardley-mapping-6a77390157e4
- Community hub of parsers, validators, generators (Python OWM parsers, Go generator, Mermaid, VS Code
  / Obsidian plugins) — https://github.com/wardley-maps-community/awesome-wardley-maps
- An existing **Claude Code skill for Wardley maps** (haberlah) proves the LLM-generates-OWM-text
  pattern works — https://github.com/haberlah/wardley-mapping
- **We already have `/arckit:wardley` + `wardley.value-chain / .climate / .doctrine / .gameplay`
  skills** in this environment. Those are the reasoning passes; OWM DSL is the storage format. Ticket 04
  covers wiring specifics.

### Propagating change through a value/dependency graph
This is the crux and it's under-served by existing tools — most Wardley tooling *draws* maps; it
doesn't *react* to change. The pieces to assemble:
- A map is already a **directed dependency graph** (value chain edges). Component evolution is a scalar
  moving left→right on x. So "propagate change" = when a component's evolution advances (e.g. a
  capability commoditises), walk the graph and re-evaluate: (a) parents that depended on it (their cost
  model / build-vs-buy flips), (b) climatic pattern triggers ("commoditisation enables new higher-order
  genesis above it"). This is a graph traversal + rule evaluation, not ML.
- Change *source* is horizon scanning (§3): a signal nudges a component's evolution position; the graph
  propagation shows the blast radius. That coupling is the novel bit of our engine.

### Pitfalls (Wardley automation)
- **Auto-placing evolution is subjective.** The x-position is a judgement (ubiquity + certainty).
  Automated placement should *propose* and keep a human/`ponytail:` calibration knob, not assert.
- **Doctrine as dogma.** Applying doctrine checks blindly ignores context — Wardley himself warns
  doctrine is universal but gameplay is not. https://medium.com/swlh/doctrine-or-dogma-2abeaef0cbc7
- **Map sprawl.** At org scale you get hundreds of maps; without a shared component vocabulary they
  don't compose. The OWM `anchor`/shared-component discipline (and a single ontology from §1) is the fix.

---

## 3. Horizon scanning / strategic foresight

### The method
**Horizon scanning** systematically hunts **weak signals** of change across **STEEP(LE)** domains —
Social, Technological, Economic, Environmental, Political (+ Legal, Ethical). Weak signals are *early,
ambiguous, easy-to-ignore, rivalrously-interpretable* indicators that may (or may not) grow into trends.

- UNDP Foresight toolkit, horizon scanning — https://www.undp.org/future-development/foresight-cpd-toolkit/chapter-1/chapter-1/chapter-1/horizon-scanning
- ITONICS, *10 Strategic Foresight Methods* (Sense → Analyze → Synthesize → Act) — https://www.itonics-innovation.com/blog/powerful-foresight-methods
- **UK GO-Science Futures Toolkit** — the authoritative UK-gov practitioner reference (horizon
  scanning, scenarios, policy stress-testing, "pathways" that chain tools). Directly relevant given the
  gov context of this estate. https://www.gov.uk/government/case-studies/futures-toolkit-tools-for-strategic-futures-for-policymakers-and-analysts · GO-Science foresight blog https://foresightprojects.blog.gov.uk/ · Civil Service analysis-function guide https://analysisfunction.civilservice.gov.uk/blog/horizon-scanning-and-futures-thinking-tools-for-government-analysts

### How a "seemingly irrelevant" signal gets classified against a model
This is the exact mechanism the ticket asks about (materials discovery → quantum evolution). Two
theory anchors plus the automation pattern:

1. **Hiltunen's "future sign" (2008)** — the best formal model for *interpretation*. A future sign has
   three dimensions: **signal** (quantity/visibility), **issue** (the events spreading it), and
   **interpretation** (the receiver's sense-making). A weak signal *by definition* has **rival
   interpretations** and is *surprising* — it forces you to challenge current assumptions. The value is
   not the signal, it's the signification process. https://www.researchgate.net/publication/229190938_The_future_sign_and_its_three_dimensions
   - This is precisely why "a room-temperature superconductor paper" only *becomes* a quantum-computing
     signal when interpreted **against a model**: the interpretation dimension is where the signal is
     bound to a component ("quantum") and a position ("evolution / genesis→custom"). No model → no
     interpretation → the signal reads as irrelevant.
2. **STEEP as the classification schema.** Signals are first tagged S/T/E/E/P, then routed to the
   components they touch. STEEP is the coarse router; the org ontology/Wardley components are the fine
   router.

### Automating weak-signal detection (the real techniques)
The literature is mature and mostly **text-mining over news/patents/papers**, not magic:
- **Degree of Visibility (DoV)** = how often a term appears over time; **Degree of Diffusion (DoD)** =
  across how many distinct sources. Rising DoV+DoD on a low-base term = strengthening weak signal.
  Yoon (2012), *Detecting weak signals … text mining of Web news* — https://www.sciencedirect.com/science/article/abs/pii/S0957417412006562
- **Keyword-portfolio / future-signal maps** (visibility × diffusion quadrants) — Land Administration
  future-signals study — https://www.mdpi.com/2073-445X/8/12/181 ; system implementation via text mining + NLP — https://www.mdpi.com/2071-1050/12/19/7848
- **Topic modelling (LDA)** and **graph methods** (keyword co-occurrence networks + Graph Convolutional
  Networks) to cluster and *predict* signal emergence — https://www.sciencedirect.com/science/article/abs/pii/S0950705120307796 · https://www.sciencedirect.com/science/article/pii/S0016328723001064
- **LLM-era**: WISDOM (arXiv 2409.15340) — LLM + advanced topic modelling for emerging-research
  detection via weak-signal analysis — https://arxiv.org/pdf/2409.15340
- Commercial automated scanners (ITONICS: >50M signals in a curated data lake, scored on velocity,
  geographic spread, temporal trajectory, plotted onto **trend radars**) — https://www.itonics-innovation.com/blog/weak-signals ; Horizon Scan AI — https://horizon-scanning.org/

### Pitfalls (horizon scanning)
- **Hindsight & confirmation bias.** You find the signals you already believe in. Rival interpretation
  (Hiltunen) is a feature — force ≥2 readings of each signal.
- **Noise = cost.** 50M signals is only useful with aggressive scoring + a model to bind them to. Raw
  volume is a liability, not an asset.
- **Signal → trend inflation.** Most weak signals *don't* become trends. Track DoV/DoD trajectory;
  don't promote on a single spike (hype-cycle trap).
- **The interpretation step is irreducibly human/LLM-judgement.** Detection automates; *classification
  against your model* is the reasoning step and should stay explainable.

---

## 4. Scenario simulation — temporal what-if (fast-forward / rewind / play)

### The method
Two distinct traditions, don't conflate them:
- **Narrative scenario planning** (GBN / Shell 2×2, GO-Science) — a handful of qualitative,
  internally-consistent "plausible futures" built from the critical uncertainties. Not a simulation;
  a *sense-making* device. GO-Science Futures Toolkit (scenarios, policy stress-testing) as above.
- **Three Horizons** (Bill Sharpe et al.) — H1 declining present / H3 desired future / H2 transitional
  innovations. This is the framework that most naturally **maps onto Wardley evolution over time**: H1
  = today's commodity/product components, H3 = today's genesis components matured, H2 = the contested
  middle. Good structuring device for "play forward". https://en.wikipedia.org/wiki/Three_Horizons · toolkit https://training.itcilo.org/delta/Foresight/3-Horizons.pdf

### Temporal what-if over a *structured* model (the tooling reality)
- **Branch-and-compute** is the dominant pattern: a baseline branch + counterfactual branches, each
  wired to a computational backend that re-runs the model under that branch's assumptions. (Described
  generically in temporal-what-if / branching-conversation work — https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/12561533)
- **System dynamics / Monte-Carlo simulation** gives outcome *distributions* not point forecasts — the
  honest output of a simulator. But structured simulators have a well-known limitation: **you must
  re-run scenarios whenever the model *structure* changes**, not just the inputs.
- **AI-assisted scenario tooling** is emerging (WEF "scenario game"; Futures Platform; arXiv 2511.21570
  *From Prediction to Foresight*) but is still mostly narrative-generation, not grounded simulation —
  https://www.weforum.org/stories/2025/02/scenario-game-navigate-uncertainty-and-develop-foresight/ · https://www.futuresplatform.com/blog/scenario-planning-process · https://arxiv.org/pdf/2511.21570

### The fast-forward / rewind / play insight
"Play" over a structured model needs **the model to be versioned/time-indexed**. If each state of the
twin is an immutable snapshot, then:
- **rewind** = check out an earlier snapshot,
- **play** = replay the sequence of state transitions,
- **fast-forward** = apply projected transitions (evolution advances + signal impacts) forward.

Nobody needs a bespoke temporal database for this if the model already lives in **version control** —
which, in this estate, **it does** (`policy-as-versioned-flux`). Git history *is* the temporal spine.

### Pitfalls (scenario simulation)
- **Spurious precision.** Distributions/point-forecasts imply confidence the inputs don't support.
  Keep scenarios *plausible-not-probable* unless inputs are genuinely quantitative.
- **Structure-change invalidation.** If a horizon signal changes the *graph shape* (not just a
  position), cached simulation results are void — recompute, don't trust.
- **Combinatorial explosion.** N uncertainties → 2^N branches. Three Horizons / 2×2 exist to cap this
  to a handful of meaningful worlds.

---

## Practical seam for our engine

The four topics collapse into **one loop over one versioned graph**. The lazy, reuse-first design:

1. **The twin = the graph we already have.** The org is a GitHub org of repos (hub/policy/fleet). That
   dependency graph *is* the DTO's knowledge graph (per DFKI's "graph-based machine-readable enterprise
   model"). Don't build a modelling tool — derive the twin from the estate that already exists. Add an
   ontology/vocabulary only as thin as decisions need ("Context Spaces", not boil-the-ocean).

2. **Wardley map = a view over that graph, stored as OWM DSL.** Reuse the **OWM text format** as the
   serialization (it's already maps-as-code) and the **existing `/arckit:wardley*` skills** as the
   reasoning passes (value-chain, climate, doctrine, gameplay). A component = a node; value-chain edge =
   dependency edge; evolution = one scalar attribute per node. No new map engine.

3. **Horizon scanning = signals tagged STEEP, bound to components via interpretation.** A signal is
   irrelevant until *interpreted against the model* (Hiltunen's interpretation dimension). The binding
   step is: `signal → STEEP class → candidate component(s) → proposed evolution nudge`. Detection can be
   as simple as DoV/DoD term-tracking or an LLM classifier; the *reasoning* — "materials paper ⇒ affects
   `quantum` component ⇒ nudges it genesis→custom" — is the valuable, explainable part and should stay
   an LLM/human judgement with a recorded rationale (rival-interpretation-aware).

4. **Change propagation = graph traversal + climatic-pattern rules.** When a signal nudges a node's
   evolution, walk value-chain edges to recompute affected parents (build-vs-buy flips, new genesis
   opportunities above a newly-commoditised component). Pure graph + rules, no ML.

5. **Scenario play = git over the versioned twin.** `policy-as-versioned-flux` already versions the
   model. rewind = checkout; play = replay commits; fast-forward = apply projected evolution+signal
   deltas as a candidate branch and diff the resulting maps. Three Horizons is the framing for the
   forward projection (H1 today's commodities / H3 today's genesis matured). Branch-per-scenario, diff
   the maps — the same pattern as the temporal-what-if literature, for free.

**The whole engine in one sentence:** *a versioned knowledge graph of the estate, projected as Wardley
maps, nudged by STEEP-classified weak signals that propagate along dependency edges, and replayed /
fast-forwarded through git history for scenario what-if.*

### Prior art to build on (shortlist)
- **DFKI Riss/Maus DTO + Context Spaces** — the credible academic data model (graph + ontology, sliced
  per decision). https://link.springer.com/chapter/10.1007/978-3-030-63479-7_3
- **OWM DSL + awesome-wardley-maps parsers** — the serialization + existing tooling; don't reinvent.
  https://docs.onlinewardleymaps.com/ · https://github.com/wardley-maps-community/awesome-wardley-maps
- **In-repo `/arckit:wardley*` skills** — the reasoning passes already installed here.
- **Hiltunen future sign + DoV/DoD text mining** — the horizon-scanning theory + a dead-simple
  automatable detection metric. https://www.researchgate.net/publication/229190938_The_future_sign_and_its_three_dimensions · https://www.sciencedirect.com/science/article/abs/pii/S0957417412006562
- **UK GO-Science Futures Toolkit + Three Horizons** — practitioner-grade scenario/foresight process,
  gov-appropriate. https://www.gov.uk/government/case-studies/futures-toolkit-tools-for-strategic-futures-for-policymakers-and-analysts · https://en.wikipedia.org/wiki/Three_Horizons

### One honest caveat
The market's weakest, most-oversold capability (§1, §4) is exactly the one we're aiming at:
grounded future-state *simulation*. Our advantage is that we don't have to fake it — the model is a
real versioned graph, so "play" is replay of real state, and "fast-forward" is an explicit, inspectable,
rival-interpretation-tagged projection, not a black-box forecast. Keep it explainable and keep a
calibration knob on every automated evolution placement.
