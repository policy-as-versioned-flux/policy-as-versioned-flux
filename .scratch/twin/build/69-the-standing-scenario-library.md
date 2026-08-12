# 69 — The standing scenario library

**What to build:** Populate the committed set — **quantum/HNDL, bus-factor and key-person, insider and coercion,
supply shock, sanctions, M&A, memory cost, AI-model access, climate event** — plus opportunity plays
and backtest cases, each executable on the schedule.

**This is a ticket because leaving it as authoring work spread across other tickets was a scope
drop.** Only the entries the demo beats happen to need would have been written; nothing would have
forced the rest to exist, and the map treats the library contents as the acceptance tests each
workstream satisfies. Ownerless contents means dropped acceptance tests.

**A dated signal for the AI-model-access class, recorded 2026-08-10.** AWS published Dogwood on
2026-08-06 under Apache 2.0 and shipped it in Bedrock AgentCore Policy. Read as a world-layer
signal rather than a tool decision, it dates a movement on the evolution axis:

- **Point-in-time tool-call authorisation has reached commodity.** The OpenID AuthZEN Authorization
  API 1.0 shipped Standards Track in March 2026, OPA is discussing native support, and Styra's
  commercial layer collapsed after an Apple acqui-hire. A vendor-neutral wire protocol plus a
  collapsing premium layer is the commodity marker.
- **Temporal, sequence-of-actions authorisation is still genesis.** No standards body has a temporal
  profile. Five competing syntaxes exist and none maps to another.

The scenario should carry both halves, because the doctrine they imply is opposite: inherit the
commodity layer, do not build on the genesis one.

**Blocked by:** 09, 33, 37

**Status:** done (2026-08-11)

**Reading list:** Decision ticket 13; the map's committed signal classes. Spec story 43.

- [x] One executable scenario per committed class, all nine named above.
      `fixtures.build_library_org()` (`twin/fixtures.py`) authors all nine as world-layer
      components + propositions + scenarios in one `library` org overlay; each runs to a real
      forecast under `verbs.run()`, exercised in `tests/test_scenario_library.py`. The AI-model-
      access scenario carries both halves of this ticket's own dated signal — `point-in-time-
      tool-authorisation` (commodity) and `temporal-sequence-authorisation` (genesis) — as two
      named components on one proposition, because the doctrine differs and one field could not.
- [x] Opportunity plays represented, not only threats.
      The M&A class is framed as the seize rather than the defend ("Can the organisation acquire
      a strategically adjacent capability before a rival does?"), demonstrated by
      `test_the_m_and_a_class_is_framed_as_an_opportunity_not_a_threat` rather than asserted in
      prose.
- [x] Backtest cases included in the same library — no separate harness, per ticket 37.
      `fixtures.build_standing_library()` returns the co-flagships, the committed-class library
      and all six backtest answer keys (Carillion, NMC Health, Wirecard, Enron, AstraZeneca,
      Sanofi) as one repo list; one `schedule.sweep()` call runs all nine repos, zero failures —
      `test_the_standing_library_sweeps_with_no_separate_harness`.
- [x] `standing_library_covers_committed_classes` added to the invariant suite, enumerating the committed set so a silently dropped class fails CI.
      Live in `twin/invariants/manifest.yaml`; the check (`twin/invariants/checks.py`) builds the
      library fresh and diffs its scenarios' `class` values against `schema.COMMITTED_SCENARIO_CLASSES`.
      `test_dropping_a_committed_class_from_the_library_fails_the_invariant` plants exactly that
      failure and asserts the check names the missing class.
- [x] The whole library executes on the schedule from ticket 09.
      `schedule.sweep()` is unmodified — the standing library is simply one more entry in the repo
      list `sweep()` already accepted, per its own "org of repositories" adaptation.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      One invariant added (`standing_library_covers_committed_classes`, was already `pending` in
      the manifest, activated here); no existing check's body or refused keys changed. The checks
      module hash moved because a new function was added to it, authorised in the manifest as
      "decision ticket 13 — build ticket 69".
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      `twin/capabilities/scenario-engine.yaml` criterion 5 (admissibility rule) moves from
      unchecked to checked, with evidence; `scenario-engine` moves from 2/7 to 3/7 of decision
      ticket 13, computed by `twin grade` rather than typed. Criteria 4 and 6 stay unchecked
      honestly — this ticket authors library content, not the precondition-sweep engine (build
      ticket 46) that would tick them.
