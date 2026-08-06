# 27 — The constraint set and published scope exclusions

**What to build:** The authored governance artefacts, **before the code that enforces them** — an earlier draft had
this backwards, building the pre-filter first and authoring the constraints it filters on afterwards.

The constraint set is published upfront so paperclip-maximiser risk is disclosed rather than
discovered. Published scope exclusions make strategic non-modelling visible rather than deniable.
Also lands the three positions the spec carries openly rather than patching: the **explicit
disclaimer of a power layer**, **exit-cost asymmetry as an unsolved harm**, and **reflexivity and
Goodhart-on-the-twin as a deferred limitation with covert sensing ruled out permanently**.

**Blocked by:** 26

**Status:** done (2026-08-06)

**Reading list:** Decision ticket 15 (sensing, ethics, misuse). Spec stories 31, 71, 74, 75, 78.

- [x] The constraint set is a published, versioned, human-signed artefact.
- [x] Scope exclusions are published in the same artefact and named individually.
- [x] The power-layer disclaimer, exit-cost asymmetry and the reflexivity deferral are each stated explicitly by name — 'presumably covered' is how absences happen.
- [x] Covert sensing is recorded as permanently excluded, not deferred.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`twin/constraints.yaml`, `twin/constraints.py` and `twin constraints`.

- **The constraint set is published, versioned and human-signed.** `twin constraints` emits it as
  an **authored** artefact — the second place in this system where a human declaration is the
  authority rather than a derivation — and signs it as the `constraint-owner` role, which the
  register has carried since build ticket 11 waiting for this.
- **Two tiers, and only one of them is negotiable.** The universal floor is identical in every
  twin and is not the operator's to move; a perspective adds its own red lines beside it. Six
  floor constraints across two classes, `forbidden` and `ruin`, each with what it forbids, why,
  and the decision ticket it comes from.
- **Scope exclusions are published in the same artefact and named individually** — the power
  layer, harms to non-contracting parties, disparate-impact measurement, the twin's own
  liability, individual behaviour. This does not stop strategic non-modelling. It removes its
  deniability, which is the whole of what a published list can do.
- **The three positions are stated by name and required by name.** `no-power-layer` (stated),
  `exit-cost-asymmetry` (unsolved) and `reflexivity-and-goodhart-on-the-twin` (deferred) are each
  required in `REQUIRED_POSITIONS` with their status, so a constraint set that quietly drops one
  does not load. "Presumably covered" is how an absence happens.
- **Covert sensing is recorded as permanently excluded, and the record refuses to let that blur
  into the deferral beside it.** The status is `permanently-excluded`, not `deferred`, and the
  loader checks the exact status rather than merely the presence of the entry.
- The pricing threshold ships in the same artefact, because changing what may be priced is the
  same kind of act as changing what may be chosen.

Not built: **nothing enforces any of this yet.** The pre-filter that removes a ruin-class or
forbidden option from a choice set before pricing is build ticket 28, and its two invariants,
`ruin_class_absent_not_priced` and `prefilter_precedes_pricing`, remain pending. This ticket is
the authored governance artefact the pre-filter will filter on, deliberately built first — an
earlier draft had it the other way round. The misuse catalogue and constraint-removal logging are
build ticket 62; the affected-parties register and the disparate-impact audit channel are 61.
Decision ticket 15's five acceptance criteria are all still unticked, so no `sensing-ethics`
capability file exists: a capability file with nothing behind it would be a slot claiming a
capability existed.

**The last checklist item stays unticked, deliberately.** This ticket declares no depth grade,
because there is no capability behind it to grade: the constraint set is **authored**, like the
worksheet, and carries `grade: null` rather than a computed checklist. Ticking the box would be the
"premature done" failure mode the constitution names — the mechanism is not satisfied by an
artefact that opts out of it. It becomes tickable when decision ticket 15 has code to measure,
which is build tickets 47, 61 and 62.
