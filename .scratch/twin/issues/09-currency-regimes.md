# 09 — The £ currency: regimes, constraints, and whose £

Type: grilling
Status: RESOLVED (2026-08-05)
Blocked by: 07 (resolved)

## Question

Fable's #3 finding: reducing everything to £ silently destroys information and launders the
incommensurable into false comparability. Decide the regime split before the engine is built.

- **Whose £?** The currency is silently *the firm's* — it prices employees like patches. Name the
  stakeholder(s) explicitly; decide whether multiple stakeholder views are modelled.
- **Hard constraints vs prices** — ruin-class risks and ethically-forbidden trades must be
  **constraints, not prices**. Which classes? Who decides membership? How represented in the schema?
- **The comparable remainder** — only the recoverable/compensable remainder is legitimately
  £-comparable. Define the boundary.
- **The incommensurables** — reputation, morale, human cost, option value, existential/tail risk,
  ethical harms: modelled how (shadow prices? separate registers? explicit refusal to price)?
- **Objective function** — is "cheapest proportionate response" right, or seductively wrong? What
  replaces or qualifies it?
- **Model-relativity** — per ticket 07 every £ is relative to a named world-model; how is the spread
  across rival forecasts surfaced as information rather than noise?

## Acceptance criteria
- [ ] Named stakeholder(s) for the currency; multi-stakeholder decision made.
- [ ] An explicit constraint class (ruin + forbidden) with schema representation and a membership rule.
- [ ] The comparable-remainder boundary defined and defensible.
- [ ] Treatment of each named incommensurable, incl. where we refuse to price.
- [ ] A stated objective function with its qualifications.
- [ ] How rival-model £ spread is reported.

## Decided so far (grilling 2026-08-04/05)

**Q1 — whose £: the PERSPECTIVE OF WHOEVER IS PAYING TO IMPLEMENT IT. The twin is perspectival by
construction** (human answer, 2026-08-05: *"It's the eye of who's paying to implement it. You can
implement your own for your perspective"*).
The currency is **openly partisan, not dressed as neutrality**. A union, a regulator, a customer body or
an employee group can each **instantiate their own twin** — sharing the world layer, holding their own
overlay, scenarios and valuations. Consequences:
- **Architecturally free** — this is exactly ticket 07's shared-world + per-org-private-overlay tenancy
  shape; no new machinery.
- **Dissolves the arbitration problem.** No twin has to invent illegitimate cross-stakeholder weights,
  because no twin pretends to arbitrate between stakeholders. Rejected: a single "multi-stakeholder"
  book (breaks the decision function), and an unstated firm's-£ (launders a moral question into an
  efficiency one — the fable critique).
- **Every recommendation must name its perspective.** "Cheapest proportionate response" is only
  meaningful relative to a declared eye; the declaration is part of the output.

**Q1b — within a perspective, externalised costs with a CAUSAL PATH BACK are priced in that
perspective's own terms.** Not altruism — correct modelling. Track 05's mechanism is real (~80% of
malicious insiders acted on a grievance; attrition degrades bus factor), so "skip the pay rise, add
monitoring" carries a genuine causal edge back into the firm's own ledger. This is the ticket-08 causal
layer doing its job: the grievance→insider path is an evidence-graded edge, not a moral entry smuggled
into an efficiency calculation. Externalities with **no** causal path back remain genuinely external —
and are visible as such, priced only in a twin run from a perspective that bears them.

**Q2 — hard constraints, not prices. PAPERCLIP-MAXIMISING RISK IS REAL AND DISCLOSED UPFRONT** (human,
2026-08-05).
If everything carries a price, a large enough number eventually makes a monstrous option "optimal". So
some things are **removed from the choice set before any pricing happens** — filters, not penalties. A
very large penalty still asserts *a price exists*; with enough upside the optimiser finds it (and it is
numerically fragile). Two tiers:
- **Universal constraints** — the legal/ethical floor, identical in every twin, **not negotiable by the
  operator** (this is where ticket 07's structurally-unrepresentable special-category exclusion lives).
- **Perspective-declared constraints** — the operator's own red lines, declared when the twin is
  instantiated (follows from Q1's perspectivalism).

**Disclosure is a hard requirement.** The constraint set is **published as part of the twin's
configuration**, so any reader of a recommendation can see what was ruled out and by whom. A twin with a
suspiciously short constraint list is then *visibly* suspicious. The paperclip risk cannot be engineered
away — only made **inspectable**. This is the honest defence, and it matches the project-wide pattern of
making guarantees structural rather than procedural.

**Ruin is a constraint, not a large number.** An option with a real chance of destroying the org is
excluded, not priced: an expected-value average is only meaningful if you survive to keep playing
(ergodicity). Consistent with track 02's TVaR-over-VaR commitment — constraints are what you do when the
tail is *unacceptable* rather than merely expensive. **Ruin is perspective-relative**: insolvency for a
firm, livelihood or health for an employee — each twin declares its own ruin boundary.

**Q3 — objective function: (c) SHOW THE TRADE-OFF CURVE, don't pick** — with minimise-total-cost-of-risk
marked as a *default point*, not a verdict. Output = the allowed options, what each costs and buys, how
that shifts **across the ensemble**, the published constraint list (what was excluded and by whom), and a
marked default.
Rationale: (1) the twin is **advisory by law and design** (Art. 22; and fable's point that £-denominated
advice is executable political authority) — a single "the answer is X" is the overreach that turns advice
into a decision someone can hide behind; (2) it inherits the project-wide rule: **never collapse a
plurality into a false single answer.** Across ensemble members the optimum *moves*, so the honest output
is a fuzzy region, not a pin. **If two credible world-models disagree about whether the pay rise or the
hardening is cheaper, that disagreement is the most decision-relevant thing on the page** — any objective
function returning one number destroys it. (This also satisfies the rival-model-spread reporting AC.)

**Q4 — the comparable remainder: (c) CAUSAL-PATH-GATED. Price only what has an evidence-graded causal
path to a real cash flow in the declared perspective; everything else is a register entry in its own
units, reported beside the number, never inside it.**
The boundary is therefore **derived, not declared** — the £ is only ever as wide as the causal layer can
justify, which stops the currency imperialising over things it has no business valuing. In practice:
reputation is never "reputation damage = £X"; it is priced through modelled paths (customer churn, hiring
cost, regulatory attention). Morale prices through attrition, bus-factor degradation, and the
grievance→insider path (track 05). Grade 1–2 evidence → enters the £; no path, or grade 4–5 → stays a
register entry.
Rejected: (a) shadow prices (invents comparability the evidence doesn't support); (b) pure separate
registers (throws away genuinely evidenced paths). **Same use-gating rule as ticket 08 — one rule, three
jobs** (forecast scoring, causal pricing, currency scope). Key property: the answer to "why isn't morale
in the £?" is never *"we decided it doesn't count"* but *"no evidenced causal path yet"* — a falsifiable
claim someone can go and fix.

## RESOLVED (2026-08-05)

The £ is **perspectival** (it belongs to whoever pays to run the twin; others instantiate their own),
**bounded** (ruin-class and forbidden options are hard pre-filters, never prices — paperclip risk is real
and the constraint set is **published upfront**), **causally gated** (only evidence-graded paths to cash
flow enter the currency; the rest are registers beside it), and **non-verdictive** (a trade-off curve
across the ensemble with a marked default, not a single answer).

## Acceptance criteria — all met
- [x] Named stakeholder(s) for the currency; multi-stakeholder decision made (perspectival; one twin per eye).
- [x] Explicit constraint class (ruin + forbidden), universal vs perspective-declared, published upfront.
- [x] The comparable-remainder boundary defined and defensible (causal-path-gated, so derived not declared).
- [x] Treatment of each named incommensurable, incl. where we refuse to price (register entries).
- [x] A stated objective function with its qualifications (trade-off curve, marked default, advisory).
- [x] How rival-model £ spread is reported (the curve is fuzzy across the ensemble; disagreement is the headline).
