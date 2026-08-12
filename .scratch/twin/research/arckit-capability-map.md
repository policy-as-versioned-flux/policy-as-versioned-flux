# arckit capability map — skills, artefacts, and the Claude Code automation seam

Research note for the digital-twin epic. Source: the installed **arckit** plugin on disk,
`~/.claude/plugins/cache/arc-kit/arckit/6.7.5/` (active version, `VERSION` = 6.7.5; author
TractorJuice; "Enterprise Architecture Governance Harness — 73 slash commands"). Read-only
investigation of `commands/`, `skills/`, `agents/`, `schemas/`, `templates/`, `hooks/`,
`scripts/`, `config/`. No arckit commands were executed.

---

## 1. What arckit actually is (the substrate that matters to us)

arckit is not a bag of prompts. It is a **governance harness with a machine-readable
artefact graph** underneath it. Five substrate facts drive everything downstream and are
the real reason it is interesting for the twin:

1. **Every artefact is an ID'd, typed, versioned markdown file.** Naming convention
   `ARC-{PROJECT}-{TYPE}-{NNN}-v{VERSION}.md` under `projects/{NNN}-{name}/{subfolder}/`.
   Type codes are a single source of truth in `config/doc-types.mjs` (WARD, REQ, RISK, ADR,
   DPIA, ATRS, AIPB, DATA, FINOPS, CONF, TRAC, PRIN, STKE, WVCH, WDOC, WCLM, WGAM, …).
   A `PreToolUse(Write)` hook `validate-arc-filename.mjs` *blocks* any write that doesn't
   conform. So the corpus is guaranteed parseable.

2. **A dependency graph is derived from that corpus on demand.** `hooks/graph-inject.mjs`
   walks all artefacts, extracts cross-references and requirement IDs, builds
   `{ nodes, edges, reqIndex }` JSON (each node carries `type`, `project`, `severity`,
   `status`, `version`, `lastModified`), and *injects it into context* whenever you run
   `/arckit:impact`, `/arckit:health`, `/arckit:traceability`, `/arckit:navigator`,
   `/arckit:analyze`, `/arckit:graph-report`, or `/arckit:search`. This is the reflexive-
   governance backbone: the model reasons over a graph, not raw files.

3. **Writes are stamped and manifested.** `PostToolUse(Write|Edit)` runs
   `update-manifest.mjs` + `provenance-stamp.mjs` (fail-soft, `continueOnBlock:true`), so the
   graph and provenance stay current without a rebuild step.

4. **Wardley maps carry deterministic maths, enforced by a hook.**
   `hooks/validate-wardley-math.mjs` (`PreToolUse(Write)`, scoped to `wardley-maps/`) blocks
   a map write unless stage↔evolution alignment, coordinate ranges [0,1], OWM/table
   coordinate agreement, dangling refs, pipeline ranges, and Mermaid `wardley-beta` syntax
   all pass. The strategic metrics themselves live in
   `skills/wardley-mapping/references/mathematical-models.md`.

5. **Six live-data MCP servers ship with the plugin** (`.mcp.json`, all `alwaysLoad`):
   `aws-knowledge`, `microsoft-learn`, `google-developer-knowledge`, `datacommons-mcp`
   (UN/World Bank/Census stats), `govreposcrape` (24.5k UK-gov repos), `uk-tenders` (UK
   procurement award data at `tenders.run.cns.me`). These are the external-signal feeds a
   scenario engine can pull "reality" from.

---

## 2. Per-skill capability map

Each command declares `doc-type`, `effort`, and machine-readable `handoffs` (next commands +
`condition`) in YAML frontmatter — the handoff graph is itself automatable. Below, grouped by
the twin workstream each best serves.

### 2a. Wardley / evolution engine

| Command | Type | Artefact + schema | What it gives the twin |
|---|---|---|---|
| `/arckit:wardley` | WARD | Full map doc (`templates/wardley-map-template.md`): OWM `wardley` code block (canonical), converted Mermaid `wardley-beta` block, component inventory table (visibility, evolution, stage), evolution/build-vs-buy/inertia/movement tables, **strategic-metric table (D/K/R)**, risk analysis, 0-3/3-12/12-24mo recommendations, requirements traceability. | The core evolution model. Components are `[visibility, evolution]` coordinates in [0,1]; movement = `evolve X 0.85` and `pipeline` ranges. This is the twin's terrain map. |
| `/arckit:wardley.value-chain` | WVCH | Value-chain decomposition (user need → capabilities → components, visibility scores, deps). Feeds `wardley`. | Structured input: the need-graph before positioning. |
| `/arckit:wardley.doctrine` | WDOC | Doctrine-maturity scorecard (Wardley 4-phase: communication/development/operation/learning), gaps, priorities. | Organisational-readiness axis of the twin (can we actually enact the move?). |
| `/arckit:wardley.climate` | WCLM | Climatic-pattern assessment: external forces per component (everything evolves, co-evolution, inertia, tech waves) + evolution predictions. | The **scenario driver** — climate patterns are the "what forces will move X" catalogue. |
| `/arckit:wardley.gameplay` | WGAM | Selected plays from 60+ patterns (`references/gameplay-patterns.md`) with execution steps + play-position scores. | The enactment options once a scenario is chosen. |

**Wardley maths (`references/mathematical-models.md`)** — the quantitative engine:
- Evolution scoring: ubiquity × certainty rubrics → S-curve → stage boundaries.
- **Decision metrics** (also computed inline by `/arckit:wardley`): Differentiation Pressure
  `D(v)=vis·(1−evo)` (high → build/differentiate), Commodity Leverage `K(v)=(1−vis)·evo`
  (high → buy/rent), Dependency Risk `R(a,b)=vis(a)·(1−evo(b))` (high → visible thing on
  immature dependency = risk). The hook cross-checks these against the build/buy verdicts.
- Weak-signal detection (4 readiness factors → transition threshold → publication signal).
- Play-position scoring and climate-pattern impact weighting (aggregate scoring matrix).

These formulas are pure functions of coordinates — **they can be recomputed by a script
without a model call**, which is the hook for a cheap scheduled recompute (see §3).

### 2b. £ / risk engine

| Command | Type | Artefact + schema | Twin role |
|---|---|---|---|
| `/arckit:risk` | RISK | HM Treasury Orange Book register (`risk-register-template.md`): inherent & residual 5×5 matrices, R-NNN entries (likelihood/impact/owner/controls/appetite), category analysis (strategic/operational/financial/compliance/reputational/technology), risks-exceeding-appetite. Handoffs → `sobc`, `secure`, `tenders`. | The £-exposure ledger. Residual-vs-appetite is the number a scenario perturbs. |
| `/arckit:finops` | FINOPS | FinOps strategy (`finops-template.md`): spend baseline & trends, tagging, cost allocation, budget/forecast, optimisation, unit economics. | The cost half of the £ engine; forecast tables are scenario-sensitive. |
| `/arckit:tenders` / `/arckit:competitors` | TNDR / CMPT | Market intelligence from `uk-tenders` MCP: award-value benchmarks, top suppliers, incumbency, concentration; handoff schema `schemas/tenders-handoff.schema.json`. | Grounds supplier-concentration risk in *real award data* — external £ signal. |

`/arckit:risk` explicitly handoffs to `/arckit:tenders` to "ground supplier-concentration
risk in real UK procurement award data" — a built-in seam from internal register to live data.

### 2c. Enactment / governance arm

| Command | Type | Artefact | Twin role |
|---|---|---|---|
| `/arckit:principles` | PRIN | EA principles (global, in `000-global`). `wardley` treats PRIN as MANDATORY input. | The rule-set the twin must satisfy; policy anchor. |
| `/arckit:requirements` | REQ | BR/FR/NFR + DR requirement register. Root of most traceability chains. | The intent the twin is governed against. |
| `/arckit:adr` | ADR | Decision record with options analysis; handoffs → `hld-review`, `diagram`, `traceability`. | Enacted decisions = state transitions in the governance arm. |
| `/arckit:stakeholders` | STKE | Driver/goal/outcome analysis with measurable outcomes. | Who the twin serves; risk-owner + outcome mapping. |
| `/arckit:conformance` | CONF | Conformance assessment: ADR-implementation, cross-decision consistency, principle alignment, **architecture drift**, tech debt, custom constraint rules. | Drift detection = the enactment arm's feedback signal. |
| `/arckit:traceability` | TRAC | Requirements→design→test matrix (graph-injected). | The wiring the whole reflexive loop runs on. |

### 2d. Reflexive governance & ethics

| Command | Type | Artefact | Twin role |
|---|---|---|---|
| `/arckit:impact` | *(no doc; console)* | Reverse-dependency blast-radius over the injected graph. Levels 0-5, severity HIGH/MED/LOW per node, recommends specific `/arckit:*` re-runs. | **The "what if X moves?" primitive** — see §3. |
| `/arckit:analyze` | ANAL | Cross-artefact governance-quality analysis (graph-injected). | Whole-corpus health/quality read. |
| `/arckit:health` | *(no doc)* | Stale research, forgotten ADRs, unresolved review conditions, orphans, missing traceability, version drift. | The reflexive "is the model rotting?" scan. |
| `/arckit:navigator` | *(no doc)* | Coverage vs essential baseline; DRAFT/stale/orphan surfacing; next-command recommendation. | Project GPS — what to refresh next. |
| `/arckit:graph-report` | *(no doc)* | Governance dashboard: coverage by category, cross-ref density, compliance readiness, project comparison. | Reflexive metrics over time. |
| `/arckit:secure` | SECD | Secure by Design assessment (UK civilian). | Assurance gate. |
| `/arckit:dpia` | DPIA | UK GDPR Art.35 DPIA. | Data-ethics gate; HIGH severity in impact graph. |
| `/arckit:atrs` | ATRS | Algorithmic Transparency Recording Standard record. | AI transparency artefact — the ethics-publication obligation. |
| `/arckit:ai-playbook` | AIPB | UK Gov AI Playbook compliance assessment. | Responsible-AI gate; drives human-oversight/bias components onto the Wardley map. |
| `/arckit:data-model` | DATA | Entity model + GDPR + governance. | The twin's data schema; feeds `wardley` optionally. |

`impact`, `health`, `analyze`, `graph-report`, `navigator`, `traceability`, `search` are the
**seven graph-injected commands** — the ones that read the derived dependency graph rather
than raw files. They are the reflexive-governance surface.

### 2e. Orchestration (not a workstream — the automation itself)

| Command / asset | What it is |
|---|---|
| `/arckit:build` | Bulk-build harness (`skills/arckit-build/SKILL.md`). Resolves a YAML **recipe** → dependency DAG → parallel **waves** of `general-purpose` subagents (one per target, ≤20/wave) → validate → **one git commit per wave** → persist `projects/{P}/.arckit/state.json` for resume. Flags: `--plan`, `--resume`, `--refresh NAME`, `--target`, `--recipe`, `--enable/--exclude`, `--skip-hash-check`. **SHA-256 input-hashing** detects staleness and cascades a rebuild through the DAG. Recipes shipped: `uk-saas`, `uk-mod-sovereign`, `uk-fs-payments`, `uk-nhs-clinical-safety`. |
| `experimental.monitors` (plugin.json) | `stale-artifact-scan` → `scripts/bash/detect-stale-artifacts.sh`, `when:"always"`. Emits one line per artefact whose **Next Review Date** is past or whose DRAFT is >30 days untouched. |
| `hooks/notify-stale-artifacts.mjs` | Same signal pushed at `SessionStart`. |
| `scripts/owm-to-mermaid.mjs`, `hooks/owm-tidy.mjs`, `tidy-wardley-labels.mjs` | Deterministic map tooling — convert/tidy without a model call. |

---

## 3. The automation seam — scheduled refresh + "what if X moves?"

The question was: can a Wardley map + scenario be **refreshed on a schedule** and **re-run**
via Claude Code today? Yes — arckit already ships four of the five pieces; we supply the
scheduler. Nothing needs to be forked.

### 3.1 Pieces arckit already gives us

- **Deterministic refresh trigger.** Wardley docs auto-set a *Next Review Date = created +
  30 days* and a *Status*. `detect-stale-artifacts.sh` (a plain bash one-shot, no model)
  already reports exactly which artefacts are overdue. That is the "is a refresh due?" oracle,
  runnable from cron with zero tokens.
- **Idempotent, resumable rebuild.** `/arckit:build {P} --refresh WARD-001` (or `--resume`)
  force-rebuilds a target *and everything downstream in the DAG*, commits per wave, and
  records SHA-256 input hashes so an unchanged input is skipped. This is the refresh executor.
- **The "what if X moves?" primitive is `/arckit:impact`.** It does reverse-dependency
  traversal over the injected graph and tells you the blast radius + which HIGH-severity
  artefacts (DPIA, SECD, RISK, TRAC, CONF) need re-assessment, with the exact `/arckit:*`
  commands to re-run. A scenario ("GPT-4 LLM Service commoditises to 0.85") becomes: edit the
  map coordinate → `impact WARD-001` → it lists RISK/FINOPS/ADR downstream → re-run those.
- **Pure-function maths.** D/K/R and evolution/climate scoring are arithmetic on coordinates.
  A scenario that moves one component's `evolution` from 0.72→0.85 flips its K(v)/D(v) and its
  build-vs-buy verdict *without a model call* — a ~30-line Node script over the OWM block
  reproduces the metric table the hook already validates. Cheap enough to run per-scenario in
  a sweep.
- **Live external signal.** The `datacommons`, `uk-tenders`, `govreposcrape`, and cloud-docs
  MCP feeds let a refresh ask "has the *world* moved?" (e.g. supplier concentration shifted,
  a component genuinely commoditised) rather than just re-rendering stale assumptions.

### 3.2 Wiring it on Claude Code today (feasible now, three tiers)

**Tier 1 — cron + headless (scheduled refresh).** A launchd/cron job runs, per cadence:
```
detect-stale-artifacts.sh              # zero-token: which WARD/RISK/… are overdue?
# for each stale target:
claude -p "/arckit:build {P} --refresh {TARGET}"   # headless, resumable, auto-commits
```
The `/schedule` skill (cloud routines) or the `/loop` skill (interval re-invoke) available in
this harness can own the cadence instead of raw cron. Quarterly map review = the natural
Wardley cadence the template already prescribes.

**Tier 2 — what-if scenario sweep (subagent fan-out).** For a scenario set
`{X→0.85, Y→0.60, Z inertia}`, dispatch one subagent per scenario in a single parallel
message (arckit's own build harness proves the pattern — ≤20 concurrent). Each subagent:
clones the OWM block, applies its perturbation, recomputes D/K/R (script), runs
`/arckit:impact` for the moved component, and returns a compact delta (verdict flips, new
HIGH-severity re-assessments, £/risk deltas). Parent collates a scenario-comparison table.
This is a read-mostly analysis — it need not write artefacts unless a scenario is "adopted".

**Tier 3 — reflexive loop (adopt → cascade → re-govern).** When a scenario is chosen:
write the new map (hook validates the maths) → `PostToolUse` restamps provenance + manifest →
`/arckit:impact` cascades → `/arckit:build --refresh` rebuilds downstream RISK/FINOPS/CONF/
DPIA → `/arckit:health` + `/arckit:graph-report` confirm no new drift/orphans. The whole loop
is the enactment arm closing on itself, and every step is already a shipped command.

### 3.3 What's missing / caveats (what we'd have to add)

- **No scenario object exists.** arckit has maps, not *named scenarios with perturbation
  sets and outcomes*. A scenario is currently "edit coordinates by hand." The twin's scenario
  engine is the genuine net-new: a small schema `{baseline_map, moves[], drivers[]}` that
  compiles to OWM edits + an `impact` call. arckit gives the substrate, not the scenario model.
- **`impact` is console-only, no artefact.** Good for a loop, but a scheduled sweep that wants
  history must capture stdout itself (arckit won't persist it).
- **£ deltas aren't automatic.** RISK residual scores and FINOPS forecasts are model-authored
  prose tables, not formulas — a scenario can't recompute them arithmetically the way it can
  D/K/R. Re-running `/arckit:risk`/`/arckit:finops` (model calls) is the only faithful path;
  a cheap proxy would be our own.
- **Refresh is per-project, single-repo.** MEMORY notes this estate is a GitHub *org of repos*,
  not one tree. `projects/` and `state.json` assume one working dir — org-wide refresh means
  orchestrating N `claude -p` runs, one per repo, ourselves.
- **Org Actions-create-PRs is OFF** (per MEMORY) — a workflow-driven `gh pr create` on refresh
  is blocked without an admin; local-commit + manual push, or the `/schedule` cloud routine, is
  the workable path.

---

## 4. arckit → twin workstream crosswalk (one-liner each)

| Twin workstream | Primary arckit artefacts | Automation hook |
|---|---|---|
| Digital-twin model | WVCH + WARD (component graph as terrain), DATA | graph-inject + manifest keep it live |
| Wardley / evolution engine | WARD + `mathematical-models.md` (D/K/R, S-curve, weak-signal) | `validate-wardley-math.mjs`; pure-function recompute |
| £ / risk engine | RISK, FINOPS, TNDR/CMPT | `risk→tenders` handoff; MCP live award data |
| Enactment / governance arm | PRIN, REQ, ADR, CONF, TRAC | `impact`→`build --refresh` cascade; per-wave commits |
| Reflexive governance & ethics | impact, health, analyze, graph-report, navigator + DPIA, ATRS, AIPB, SECD | the seven graph-injected commands + stale-scan monitor |
| Scenario engine | WCLM (drivers) + WGAM (plays) + `impact` (blast radius) | **net-new scenario object needed** (§3.3); subagent sweep pattern exists |

---

*Artefact paths cited are under `~/.claude/plugins/cache/arc-kit/arckit/6.7.5/`. Version 6.7.5
was the active cache at investigation time (2026-08-04).*
