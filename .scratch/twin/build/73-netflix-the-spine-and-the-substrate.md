# 73 — Netflix: the spine and the substrate

**What to build:** The Netflix public spine plus a Netflix-specific **deep behavioural substrate** generated against
it — a ticket-49-shaped job on a real subject, which is why it is separate from running the engine.
The substrate machinery gives the mechanism; it does not give the content.

**Blocked by:** 52, 70

**Status:** done — 2026-08-16, in two parts. Part 1 built the spine and the substrate and left two
criteria unticked with what was missing named on each. Part 2 declared the horizons, wired the
walk, and built the `twin substrate` surface the reporting criterion asked for. What part 2 does
**not** do is move a capability grade: `synthetic-substrate` stays at 4/7, because decision ticket
12 AC 3 asks for a planting protocol of four clauses and this supplies two of them.

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
- [x] Fidelity measured by the ticket-51 eval suite and reported.
      `substrate_eval.evaluate_fidelity` against the real spine at the 2011-10-24 checkpoint puts
      all five dimensions inside their target bands first time: signal_to_noise 0.121 (0.05-0.25),
      plant_difficulty 0.275 (0.05-0.5), spine_consistency 1.000, reporting_asymmetry 0.667
      (0.6-0.95), mundanity 0.879 (0.7-1.0). **Reported** by `twin substrate`
      (`twin/substrate_report.py`), which emits a `substrate-report` artefact carrying the five
      metrics with their bands, the anchored/free-running split, and the plant walk below — one
      artefact rather than two, because both are readings of one generated batch at one checkpoint
      and a reader comparing two files would be comparing two different batches. Marked `derived`:
      it carries no substrate content, only measurements over a batch `generate()` produces with no
      external entropy, and two reports from identical pins are byte-identical.
- [x] Plants placed with actionability horizons, planter/detector/scorer split enforced.
      The four planted signals are written and camouflaged — each borrows vocabulary from the lines
      it sits among, which is what keeps `plant_difficulty` off its trivially-findable floor. Each
      now carries a declared horizon **and a reason** in `twin/plant-horizons.yaml`, a versioned
      document keyed by recipe id and read only by `twin/planter.py` — the sealed side of the split,
      the module `twin/detector.py` imports nothing from. `planter.horizons_for()` refuses a horizon
      with no reason, an unparseable date, or a signal the recipe never plants; `plant()` already
      refused a signal with no horizon at all. The walk runs end to end on the real subject and
      **the number is bad: a hit rate of 25%**, one plant of four, reported at the top of the
      output with a row for every plant including the three nothing found. `twin/detector.py` is
      ticket 52's lexical-outlier stand-in, so that figure is about the heuristic and not the
      subject — `SHARED_PRIOR_LIMITATION` travels beside it saying so.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      Harness guard `netflix_substrate_is_free_running_and_every_plant_carries_a_horizon`, five
      legs on the **committed** recipe and the **committed** spine rather than a guard-local
      stand-in: no generated line restates a spine fact; every plant carries a horizon and a
      reason; a horizons document drifted from the recipe is refused; every fidelity dimension is
      inside its band; the report reproduces byte-for-byte and scores every plant, misses included.
      No invariant body changed and no manifest hash moved.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      The report's envelope carries `synthetic-substrate` at `partial`, 4/7 of decision ticket 12,
      naming AC 3, 6 and 7 as unchecked. Nothing here ticks AC 3: the actionability horizon
      supplies its lead-time clause and `plant_difficulty` its burial clause, but "strength" is
      unmodelled and there is no declared *distribution* of difficulty across plants — one plant
      per channel at a fixed midpoint, each as hard to find as its wording happens to make it.
      Two of four clauses is not a criterion.
