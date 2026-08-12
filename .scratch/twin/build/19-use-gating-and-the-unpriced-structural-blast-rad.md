# 19 — Use-gating and the unpriced structural blast-radius

**What to build:** **Only grades 1–2 may price a scored forecast.** Grade-5 model assertions are exactly where
contamination hides, so they must never silently become the basis of a number someone acts on.

The consequence is the second output: when a path is real but too weakly evidenced to price, the
answer is an **unpriced structural blast-radius** — "we know this is connected but cannot price
it" as a first-class result rather than a gap papered over.

Blast-radius traversal is **inherited from `/arckit:impact`**, whose known limits (no history, £
deltas as prose) apply.

**Blocked by:** 18

**Status:** done (2026-08-06)

**Reading list:** Decision tickets 08, 09; research 04. Spec stories 23, 24.

- [x] `grade_5_only_path_never_prices` goes live: a scenario whose only causal path runs through a grade-5 edge emits blast-radius, never a price.
- [x] Blast-radius is a distinct artefact type, not a price with a null field.
- [x] The gating threshold is a versioned, published parameter — changing it is as visible as changing the constraint set.
- [x] Reverse-dependency traversal inherited rather than rebuilt, with the arckit caveats recorded.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`Graph.blast_radius`, `twin blast`, the closed blast-radius body, and the
`grade_5_only_path_never_prices` invariant going live.

- **One traversal, two outputs.** A causal hop follows an `influences` edge forwards, where
  somebody claimed a mechanism and it carries a grade. A structural hop follows a `needs` edge
  backwards to whoever depends on the node — real exposure with no claimed mechanism. A path
  prices only when every hop is causal *and* every grade is at or inside the published threshold.
- **Blast radius is a distinct artefact type, not a price with a null field.** The body is
  **closed**: every key it may carry at any depth is declared in `verbs.BLAST_BODY_KEYS`, and
  there is no `price`, `cost`, `loss` or `severity` in that set. An unpriced result has nowhere
  to put a number, which is the same structural move as the closed model schemas.
- **The threshold is a published, versioned parameter**, and it ships in the same artefact as the
  constraint set (`twin constraints`) because changing what may be priced is the same kind of act
  as changing what may be chosen. Every gating artefact pins the ladder's version, threshold and
  digest, so moving the threshold moves a digest and cannot be done quietly.
- **The gate reaches the one artefact that emits a figure.** A traversal emits no money, so a gate
  asserted only there would be asserted only where nothing could go wrong. A perspective's
  valuation therefore carries its own evidence grade, and only one inside the threshold carries an
  amount at all — the rest is a register entry with no figure, which the schema enforces at the
  source. The invariant asserts at four depths: the ladder, the traversal, the scenario exposure
  and the closed bodies.
- **The gate is a gate, not a wall.** The invariant asserts the positive leg as hard as the
  negative one: a fully-graded path *is* admitted and every perspective *does* price something, or
  a check that refuses everything would pass every refusal test while making the system useless.
- **Reverse-dependency traversal inherited from `/arckit:impact`**, with its limits recorded in
  the artefact rather than in a footnote: no history, currency deltas as prose in the inherited
  tool and none at all here, simple paths only.
- The fixture gained `brand-goodwill` and a grade-5 edge to it, so the invariant has a real
  subject — a component every path to which crosses a model assertion.

Not built: nothing prices. The gate decides **admission**, and there is no pricing engine behind
it (build tickets 23-25 and 30), so the artefact reports which paths could carry a price rather
than what it would be. The traversal caps at depth 6 and says so in `traversal`, and a truncated
answer is flagged rather than silently partial.
