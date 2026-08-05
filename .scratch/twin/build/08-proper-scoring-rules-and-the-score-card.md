# 08 — Proper scoring rules and the score card

**What to build:** Brier and log scores, regime tagging on every score, and the score card as a real artefact.

**Moved deliberately to directly after the skeleton.** An earlier draft of this plan blocked scoring
behind the whole causal and time chain, which contradicts the spec's own reason for putting scoring
in the first slice. Proper scoring rules need a forecast and an outcome — nothing else.

**Blocked by:** 07

**Status:** ready-for-agent

**Reading list:** Decision tickets 08, 11, 19. Spec stories 40, 44.

- [ ] Brier and log scores implemented with property tests (proper-scoring behaviour under a shifted forecast).
- [ ] Every score carries an information-regime tag; `only_as_consumed_scores` goes live even though only one regime exists yet.
- [ ] The **answer-key fixture format** is defined and committed here — the boundary fixture the answer-key track tests against.
- [ ] A score is refusable: a forecast with no resolvable outcome yields an explicit unscoreable result, not a zero.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
