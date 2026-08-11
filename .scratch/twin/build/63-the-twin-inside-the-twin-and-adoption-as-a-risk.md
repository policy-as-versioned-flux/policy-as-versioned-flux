# 63 — The twin inside the twin, and adoption as a risk about itself

**What to build:** The twin present as an ordinary component set **in its own graph**, depth-1 bounded — subject to
its own analysis, with no inception.

And the risk it must model about itself: corporate prediction markets at Google and Ford beat their
own experts by **up to 25% MSE reduction and were killed anyway** — by manager incentives and
information control, not by being wrong. **Accuracy does not save an instrument.** A better artefact
does not automatically win the argument, and a system whose whole pitch is transparency should model
that about itself rather than assume it away.

**A second risk about itself, dated 2026-08-06 and recorded 2026-08-10.** The spec states that the £
engine's whole value depends on **most levers not being code**. AWS is betting the other way: agent
tool-call governance is being productised, and agent behaviour is a fast-growing share of
organisational action.

If agents become the dominant actuator of organisational action, the fraction of levers that **are**
code rises, and the twin's comparative advantage — comparing an HR lever against a security control
— narrows toward territory a policy engine plus a spend dashboard already covers.

This is a Wardley evolution argument against the thesis's **durability**, not its correctness. It is
exactly the shape of risk this ticket exists to price about the twin, so price it rather than note
it. The sharper reading is also worth recording: if the machine-enforceable arm just moved toward
commodity, then ticket 30's response pricing should now return a **cheaper** option in that class
than it did last week. The twin's answer changes because the world changed. That is the thesis
working, not the thesis threatened.

**Blocked by:** 33, 12

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 10 (twin inside twin). Spec stories 76, 79.

- [x] The twin appears as components in its own graph and is analysable by the normal machinery.
      `twin/fixtures.py::build_twin_self_org()` adds a standalone org overlay (`twin-self`)
      carrying the twin as two ordinary components (`the-twin-model`, `the-twin-adoption`), a
      person (`the-twin-maintainer`) giving it bus-factor 1, and a scenario (`adoption-risk-2026`)
      — `twin graph`, `twin blast`, `twin propagate`, `twin run`, `twin price` and `twin options`
      all execute against it unmodified (`tests/test_twin_inside_twin.py`).
- [x] Depth is bounded at 1, structurally — a depth-2 attempt fails rather than recursing.
      Two legs. Structural: a component's closed schema carries no field for a further nested
      "twin modelling this twin" layer — a planted `models_graph`/`nested_twin`/`twin_of` field
      does not load. Traversal: `the-twin-model` and `the-twin-adoption` close a genuine two-node
      causal cycle (accuracy earns adoption; adoption sustains the model), and
      `twin propagate --origin the-twin-model` reaches the other component once — the return leg,
      a depth-2 attempt, is cut by `twin/propagate.py`'s existing simple-path rule (build ticket
      21) rather than recursed, and disclosed (`truncated: true`, the cycle named in
      `known_limits`) rather than silent. Both legs are now a harness guard,
      `twin_self_reference_is_cut_not_recursed` (`twin/invariants/harness.py`).
- [x] Adoption is a modelled scenario with priced responses, not a note.
      `adoption-risk-2026` runs and emits forecasts (`twin run`); `the-twin-sponsor` perspective
      prices the shock at `the-twin-model` and admits the impact at `the-twin-adoption`
      (`twin price`); two candidate responses are costed through the constraint pre-filter
      (`twin options`) — both honestly earn no mitigation credit at their declared evidence
      grade (3, outside the pricing threshold), which is itself the finding: a plausible-sounding
      governance fix is not automatically evidenced any better than accuracy is.
- [x] The Google/Ford evidence is cited in the scenario's basis.
      Cowgill & Zitzewitz (2015), "Corporate Prediction Markets: Evidence from Google, Ford, and
      Firm X", *Review of Economic Studies* 82(4):1309, cited by URL in the scenario's world
      model (`documented-corporate-prediction-market-pattern`) and carried as a real dated signal
      bound to `the-twin-adoption` at evidence grade 2 (repeated cross-firm co-movement, may
      price) — not a note, a graded claim.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One harness guard added (`twin_self_reference_is_cut_not_recursed`,
      `twin/invariants/harness.py`), zero weakened. No existing invariant changed.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/twin-inside-twin.yaml` — the first capability file built for decision
      ticket 10. 2 of 5 acceptance criteria checked (`partial`, never `full`): AC1 (this ticket)
      and AC3 (contestability, retroactively ticked to build ticket 60 — exercised here against an
      artefact about the twin's own graph for the first time). AC2 (a full threat model — this
      ticket prices one risk category, adoption, not exfiltration/extraction/poisoning/gaming),
      AC4 (which sensors are most gameable — undeclared, consistent with `sense-move.yaml`'s own
      honest gap on the identical sub-topic) and AC5 (named misuse cases about the twin as
      authority) remain unchecked and carried forward, per decision ticket 10's own resolution.
