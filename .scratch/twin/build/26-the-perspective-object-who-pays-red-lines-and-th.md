# 26 — The perspective object: who pays, red lines, and the universal floor

**What to build:** The £ is **perspectival** — it belongs to whoever pays to run the twin. A union, a regulator or an
employee body can instantiate their own perspective rather than inherit the employer's, and the same
scenario prices differently under each.

A **universal legal and ethical floor** is distinguished from perspective-declared red lines: a
perspective may add constraints, never remove the floor.

Blocked on the schema, not on severity modelling — an earlier draft queued the whole governance stack
behind tail maths for no reason.

**Blocked by:** 12

**Status:** done (2026-08-06)

**Reading list:** Decision tickets 09, 15. Spec stories 29, 32.

- [x] A perspective declares who pays, what they value, and their red lines, as a versioned artefact.
- [x] The universal floor is separate and cannot be overridden by a perspective, demonstrated by a failing attempt.
- [x] Two perspectives over one scenario produce two different prices, and the difference is attributable.
- [x] A perspective is instantiable by a non-employer party without special privilege.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

The `perspective` schema and collection, `twin exposure`, and the `currency-regimes` capability.

- **A perspective declares who pays, what they value and their red lines**, as a file in the
  git-versioned model repository — so it is a versioned artefact with no new machinery, exactly
  as decision ticket 09 Q1 says it should be. `party` is enumerated and flat: employer, employee
  body, union, regulator, customer body, supplier, other. Nothing anywhere ranks them and there
  is no field by which anything could.
- **The universal floor cannot be overridden, demonstrated by a failing attempt.** The schema is
  closed, so there is no field for removing a constraint; the remaining route is to declare your
  own under a floor id and hope the resolver takes the last one it saw. It does not — a
  perspective whose constraint reuses a floor id refuses to load, named in the error.
- **A valuation is graded, and the £ boundary is the same use-gate.** Decision ticket 09 Q4
  rejected shadow prices, so a perspective may not simply declare what an incommensurable is
  worth: a valuation carries its own evidence grade, and only one inside the published threshold
  carries an amount. Anything weaker is a **register entry** — named beside the figure, with no
  number, because the schema refuses one at that grade. One rule, three jobs.
- **Two perspectives over one scenario produce two different figures, and the difference is
  attributable.** The exposure artefact carries one entry per perspective plus a per-component
  breakdown, so the disagreement is in the artefact rather than in whoever runs the diff. With no
  `--perspective` given, **every** perspective is reported: defaulting to the operator's would be
  the unstated firm's-£ the design refuses.
- **A non-employer party needs no privilege.** The pocket org and the flagship both carry a staff
  council alongside the operator, loaded by the same code path, with the same schema and the same
  standing in the output.
- **Ruin is required, not optional.** Ruin is perspective-relative — insolvency for a firm,
  livelihood for a person — so a perspective that declares no boundary has silently inherited
  somebody else's.
- A component this perspective never valued is `null`, not zero, and is listed in `unvalued` —
  which is distinct from one it valued too weakly to price, and that is in the register. Zero says
  "worth nothing to them", which is a different claim from both and usually a false one.
- The pocket-org worksheet gained lines 36-40, hand-computable by eye.

Not built: this is a **declared valuation, not a modelled price**, and the artefact says so in
`basis`. Nothing propagates (build ticket 20), no severity is sampled (23-25), no causal path is
priced (30), and the constraint pre-filter that must run before any pricing is build ticket 28 —
recorded in `prefilter.applied: false` rather than implied. Decision ticket 09's AC 1 is ticked;
ACs 3-6 stay unticked because the comparable remainder, the incommensurables, the objective
function and the rival-model spread all need the engine that is not here.
