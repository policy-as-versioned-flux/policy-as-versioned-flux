# RESEARCH: the arckit toolkit — capabilities & Claude Code wiring

Type: research
Status: resolved
Blocked by: none

## Question

Exactly what do the `/arckit:*` skills do and produce, and how could they be wired to Claude Code for
scheduled refresh + automated what-if scenario runs? Investigate the installed arckit plugin
(commands, skills, agents, schemas, templates on disk) and write a capability map:

- Per skill — its **artefact**, schema, and what decision/workstream it serves:
  `wardley` (+ `value-chain`/`doctrine`/`climate`/`gameplay`), `risk`, `requirements`, `stakeholders`,
  `principles`, `adr`, `secure`, `dpia`, `atrs`, `ai-playbook`, `data-model`, `finops`, `roadmap`,
  `impact`, `conformance`, `traceability`.
- The **automation seam**: how a Wardley map + scenario could be *refreshed on a schedule* and re-run
  ("what if X moves?") via Claude Code (cron/loop/subagents) — what's feasible today.
- Which arckit artefacts map onto which of our workstreams (the twin, the £ engine, the enactment
  arm, reflexive governance).

Output: `research/arckit-capability-map.md` — arckit → our workstreams, plus the automation wiring.

## Answer (2026-08-04) — resolved

arckit **6.7.5** is a **73-command governance harness on a machine-readable artefact graph** — not a
prompt bag. Every output is an ID'd/typed/versioned markdown file (`ARC-{P}-{TYPE}-{NNN}-v{V}`,
filename-hook-enforced); `hooks/graph-inject.mjs` derives a `{nodes, edges, reqIndex}` dependency
graph injected into 7 commands. **Wardley maps carry deterministic maths** — `D=vis·(1−evo)`,
`K=(1−vis)·evo`, `R=vis(a)·(1−evo(b))` — validated on write, recomputable without a model call.
**Two primitives we need already exist:** `/arckit:impact` = reverse-dependency **blast-radius**
("what if X moves?") over the graph; `/arckit:build --refresh` = resumable, SHA-256-input-hashed,
DAG-cascading **scheduled refresh** that commits per wave. Six live MCP feeds (datacommons,
uk-tenders, govreposcrape, cloud docs) supply external "has the world moved?" signal. **The genuine
net-new for us is a scenario object** `{baseline, moves[], drivers[]}` — arckit has maps +
climate-drivers (WCLM) + plays (WGAM) but **no named-scenario-with-perturbations** model; its own
≤20-subagent build harness is the fan-out pattern a scenario sweep would use. **Caveats that shape
our seams:** `impact` is console-only (no history to diff), £/risk deltas are model-authored *prose
not formulas* (so our £ engine bolts on, not in), and refresh assumes **one repo** — our estate is an
**org of repos** and org Actions-create-PRs is OFF. The 5 most central: `wardley`, `impact`, `build`,
`risk`(+`finops`/`tenders`), `health`/`graph-report`/`navigator`. Full: `research/arckit-capability-map.md`.
