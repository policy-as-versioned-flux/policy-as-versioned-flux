# 20 — The skill inventory: which capabilities become skills, and in what order

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07–15, 18 (all resolved)

## Question

"Skills-first, from basics" was a founding constraint. With the engine now decided, pin which reusable
capabilities become **agent skills**, what each owns, and the build order.

Candidate capabilities surfaced across the resolved tickets:
- **twin-model** — authoring/validating the graph (components, edges, overlays, world-models)
- **signal-classify** — ingest → STEEP-tag → bind to components (ticket 11)
- **wardley-engine** — evolution positions, D/K/R maths, climate/doctrine/gameplay lenses
- **causal-claims** — authoring evidence-graded causal edges + confounder flagging (ticket 08)
- **scenario-runner** — scenario → execution → forecasts; time + intervention primitives (ticket 13)
- **£-pricing** — FAIR scenarios, calibrated triples, Monte-Carlo, TVaR, constraint pre-filter (09)
- **substrate-generator** — the synthetic world + planted signals + eval suite (ticket 12)
- **calibration/scoring** — proper scoring rules, reliability diagrams, the forecast book (08, 11)
- **provenance/attest** — signing, pinning, reproducibility checks (ticket 14)
- **ethics-gate** — the sensor admission ladder, DPIA gate, misuse constraints (ticket 15)

## Open

- **What is a skill here** — a reusable agent capability, a library, or a workflow? What is the unit?
- **Which of the above are genuinely skills** vs plain code vs already covered by `/arckit:*`?
- **Build order** — what must exist first for anything else to be testable?
- **The bootstrap problem** — several capabilities are mutually dependent; where does it start?

## Acceptance criteria
- [ ] A definition of "skill" for this project, and the unit of packaging.
- [ ] The inventory: which capabilities are skills, which are code, which are inherited from arckit.
- [ ] A build order with the bootstrap sequence made explicit.
- [ ] Each skill's owned decision-record (which resolved ticket defines its contract).

## Decided so far (grilling 2026-08-05)

**Q1 — the unit: (c) SPLIT BY DETERMINISM.** Anything on the derivation path is **code**; anything
irreducibly interpretive is a **skill**; and a skill's job is to **drive the code correctly**.
**Ticket 14 forced this, not aesthetics:** derivation must be **deterministic given the pins** (seeds,
model versions, prompts) or the attestation is a claim rather than a proof. *"An agent did it, roughly"*
cannot be recomputed. So Monte-Carlo, D/K/R maths, TVaR, proper scoring rules, graph validation and
blast-radius traversal are **code — because attestation demands it.**
**What remains genuinely skill is the irreducibly interpretive:** binding a signal to a component,
proposing a causal claim with its evidence grade, judging evolution position, generating substrate.
**And ticket 08 already grades exactly those as grade 5 (model assertion), the lowest rung.** So the
partition is not arbitrary: **skills produce grade-5 claims that code then validates, prices and scores.**
The architecture and the evidence ladder agree on the boundary.
**The test for the whole inventory:** *if it must be reproducible from pins → code; if it is a judgement
landing at grade 5 → skill.*
**Explains the arckit relationship too:** `/arckit:wardley` carries deterministic maths validated on write
→ we inherit **code**; the gameplay/doctrine/climate lenses are suggestion-shaped → **skill**.

**Q2 — build order: (d) WALKING SKELETON, with SCORING IN THE FIRST SLICE.**
One thin vertical cut through every layer — one dated signal → binds to a component → an inferred position
moves → one scenario execution → a forecast with its pins → a score against a known outcome — then deepen
each layer. The mutual dependency only bites if you build layer-by-layer; a vertical cut goes through all
of them at once. Also fable's independently-recommended voluntary external gate (*"a walking skeleton
end-to-end loop on a named date"*), which puts a date against the magnum-opus-with-no-floor risk.
**Scoring is IN the first slice, not deferred:** everything decided in this project is about measurement,
so without a scoring harness we cannot tell whether any later capability helped — we would build blind. It
is also cheapest to build early and most expensive to retrofit, because **scoring dictates what every
other component must record.**

**Q2b — STANDING GUARDS on the skeleton** (human, 2026-08-05: *"be careful not to allow scope to drop and
prematurely declare things done, and be prepared to always change our code and never be married to
previous investments"*).
Named failure modes:
- **Skeleton-as-ceiling** — the thin slice quietly becomes the definition of done rather than the scaffold.
- **Premature done** — a layer that "works" in the skeleton is marked complete when it is a stub.
- **Sunk-cost architecture** — early code shapes later decisions because rewriting feels wasteful.
Guards:
- **Each resolved ticket's FULL acceptance criteria remain the yardstick.** The skeleton satisfies a
  *slice* of them and **never redefines them**. "Done" means done against the decision, not the demo.
- **Per-capability depth grades** (stub / partial / full) against the owning ticket's contract — the same
  device as ticket 01's per-org depth ladder.
- **Code is disposable by default.** Structurally consistent: the durable artefacts are the **versioned
  model and the decision record**; code is nearer a *derived* artefact than an authored one, so replacing
  it is normal rather than wasteful.

## Q3 (derived from Q1's test, not separately grilled) — the inventory

Applying *"reproducible from pins → code; grade-5 judgement → skill"*:

**CODE (on the derivation path; must be deterministic and attestable)**
- graph schema + validation; authored/derived enforcement (07, 14)
- D/K/R Wardley maths — **inherited from `/arckit:wardley`** (research 04)
- blast-radius / reverse-dependency traversal — **inherited from `/arckit:impact`**
- causal propagation: Monte-Carlo through the graph, depth attenuation, shared-ancestry handling (08)
- intervention vs observation semantics — `do()` vs bidirectional belief update (08, 11)
- FAIR engine: PERT sampling, heavy-tailed severity, TVaR, constraint pre-filter, trade-off curve (09)
- scenario/execution/forecast objects + pin capture; time-gating by information regime (13)
- **scoring harness**: proper scoring rules, reliability diagrams, regime tagging, contamination discount (08, 11, 19)
- decay/rescue of the unbound signal pool + retrospective sweep (11)
- provenance: signing, pin capture, reproducibility checks (14)
- substrate **eval suite** (the fidelity target is measured, not asserted) (12)
- scheduled-execution orchestration — **inherited from `/arckit:build --refresh`** (research 04)

**SKILL (irreducible judgement; produces grade-5 claims that code validates)**
- **signal-classify** — STEEP-tag + bind signals to components (11)
- **causal-claims** — propose causal edges with sign/lag/elasticity, evidence grade, alternatives (08)
- **evolution-judge** — infer component position from accumulated evidence (11)
- **substrate-generator** — generate the world + plant signals against the eval targets (12)
- **gameplay-lens** — Wardley plays whose preconditions hold; doctrine/climate suggestions (13)
- **ethics-gate** — walk the sensor admission ladder; DPIA triage (15)

**NEITHER (governance artefacts, not capabilities):** the constraint set, scope exclusions, the
affected-parties register, the misuse catalogue — authored, human-signed, versioned.

**Each skill's contract is defined by its owning resolved ticket** (listed above), so a skill's
acceptance criteria are that ticket's criteria — not a fresh invention.

## RESOLVED (2026-08-05)

**Split by determinism:** derivation-path work is **code** (attestation demands reproducibility);
irreducible judgement is a **skill**, and skills produce exactly the grade-5 claims the evidence ladder
already distrusts — architecture and epistemics agreeing on the same boundary. Build via a **walking
skeleton with scoring in the first slice**, guarded against skeleton-as-ceiling, premature-done and
sunk-cost architecture by **keeping each ticket's full acceptance criteria as the yardstick**,
**depth-grading every capability**, and treating **code as disposable** — the decisions are what endure.

## Acceptance criteria — all met
- [x] A definition of "skill" for this project and the unit of packaging (determinism split).
- [x] The inventory: skills vs code vs inherited from arckit.
- [x] A build order with the bootstrap sequence made explicit (walking skeleton, scoring included).
- [x] Each skill's owned decision-record (the resolved ticket defining its contract).
