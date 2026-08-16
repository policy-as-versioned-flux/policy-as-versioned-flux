# 73 — Netflix: the spine and the substrate

**What to build:** The Netflix public spine plus a Netflix-specific **deep behavioural substrate** generated against
it — a ticket-49-shaped job on a real subject, which is why it is separate from running the engine.
The substrate machinery gives the mechanism; it does not give the content.

**Blocked by:** 52, 70

**Status:** spine and substrate built, **PLANTS AND REPORTING NOT WIRED** — 2026-08-16. The same
honest split build tickets 64, 65 and 66 carry: what exists is described, what does not is named
rather than left to be inferred from a green tick.

**Reading list:** Decision tickets 06, 12, 22. Spec story 91.

- [x] Public spine assembled with dated checkpoints and quarterly cadence.
      `fixtures.build_netflix_org()`: six checkpoints, every one an EX-99.1 letter to shareholders
      filed with the SEC, **read from the filing rather than from coverage of it** — 2011-01-26
      (20.01m subscribers), 2011-04-25 (23.6m), 2011-07-25 (over 25m, price changes framed as a
      strength), 2011-09-15 (the interim guidance cut), 2011-10-24 (24.6m to 23.8m domestic, the
      loss attributed to the pricing change and the cancelled rebrand) and 2012-01-25 (2bn hours,
      47 countries). The cadence is the subject's own quarterly reporting, with the September
      interim sitting between two of them because that is where the subject itself broke cadence
      to disclose. Validates against the closed schema, the world layer names no tenant, commit
      history is dated to the real timeline, and `Spine.from_overlay` gates to 4 of 6 facts at
      2011-09-30.
      **No answer key, deliberately** (decision ticket 22): Netflix cannot carry falsifiability,
      because its fame makes anticipation indistinguishable from recital. Kept distinct from the
      toy `netflix` overlay in `fixtures.build()`, which cites `example.invalid` and exists only
      to exercise the walking skeleton.
- [x] Behavioural substrate generated against the spine via the ticket-48 recipe mechanics.
      `twin/netflix-substrate-recipe.yaml` — a versioned recipe, not a stored corpus, because
      decision ticket 12 chose regenerable over stored. 24 templates across the four channels plus
      four planted signals, all **free-running**: no line restates, contradicts or hints at a spine
      fact, because generating the substrate from the spine is what would make the plants findable
      by diffing against it (decision ticket 12 Q3). The subscriber numbers and the Qwikster
      reversal appear nowhere in it — they are the spine's business, anchored in at evaluation.
- [ ] Fidelity measured by the ticket-51 eval suite and reported.
      **Measured, not yet reported.** `substrate_eval.evaluate_fidelity` against the real spine at
      the 2011-10-24 checkpoint puts all five dimensions inside their target bands first time:
      signal_to_noise 0.121 (0.05-0.25), plant_difficulty 0.275 (0.05-0.5), spine_consistency
      1.000, reporting_asymmetry 0.667 (0.6-0.95), mundanity 0.879 (0.7-1.0). What is missing is
      the *reported* half: there is no `twin` verb that emits a fidelity artefact, so the figures
      exist only when someone calls the library. This criterion stays unticked until that surface
      exists, rather than being ticked on the measurement alone.
- [ ] Plants placed with actionability horizons, planter/detector/scorer split enforced.
      The four planted signals are written and camouflaged — each borrows vocabulary from the lines
      it sits among, which is what keeps `plant_difficulty` off its trivially-findable floor. **No
      actionability horizon is declared for any of them yet**, so `planter.plant()` would refuse
      this recipe today, exactly as decision ticket 12 Q3b intends. The planter/detector/scorer
      walk is not wired.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
