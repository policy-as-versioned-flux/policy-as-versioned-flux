# RESEARCH: state of the art — org digital twins, Wardley automation & horizon scanning

Type: research
Status: resolved
Blocked by: none

## Question

How do people build a **living digital twin of an organisation/enterprise**, and how is the
sensing/reasoning around it automated? Cited briefing on:

- **Enterprise / organisational digital twins** — prior art, reference models, what's real vs
  marketing, data models, tooling.
- **Wardley mapping automation** — maintaining maps at scale, tracking component **evolution**,
  propagating change through a value/dependency graph; how `/arckit:wardley` fits (defer tool
  specifics to ticket 04).
- **Horizon scanning / strategic foresight** — STEEP(LE), weak-signal detection, futures practice,
  scenario planning, and how "seemingly irrelevant" signals get classified against a model.
- **Scenario simulation** — fast-forward / rewind / play mechanics; what tools do temporal what-if
  over a structured model.

Output: `research/twin-wardley-horizon-sota.md` — cited, with pitfalls and the practical seam for our
Wardley + horizon-scanning + scenario engine.

## Answer (2026-08-04) — resolved

A **digital twin of an organisation (DTO)** (Gartner term; first Magic Quadrant 2026) is best built
not as a simulator but as **a live knowledge graph of the org + an ontology + a feedback loop from
operational data**, sliced per-decision (DFKI "Context Spaces"). Vendors are strong *mirrors of the
present*, weak *simulators of the future* — the oversold half. **Wardley** gives the right shape: a
value-chain dependency graph + one evolution scalar per node + three automatable lenses (climate =
rules, doctrine = lint, gameplay = suggestions), with a maps-as-code format (**OWM DSL**) + parsers +
the installed `/arckit:wardley*` skills — don't reinvent map tooling. **Horizon scanning** = STEEP-
tagged weak signals that are irrelevant *until interpreted against the model* (Hiltunen "future sign"
= exactly the materials-paper→quantum binding step); detection automates cheaply (DoV/DoD term-
tracking, LDA, LLM classifiers), classification stays explainable judgement. **Scenario sim needs a
versioned model — and git history IS the temporal spine**: branch-per-scenario + map-diff gives
fast-forward/rewind/**play** for free (framed by Three Horizons / UK GO-Science Futures Toolkit). Our
edge: "play" is **replay of real versioned state**, not a black-box forecast. Full: `research/twin-wardley-horizon-sota.md`.
