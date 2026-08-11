# 65 — The Flux falsification verdict

**What to build:** **Run the test rather than assume the answer.** What does the risk basis require?

**The question was widened from two branches to three on 2026-08-10**, three days into the 91-day
measurement window and before any verdict could be read from the data. The original pair:

1. **Continuous proof of force**, meaning reconciliation from a signed pinned source.
2. **Point-in-time proof**, meaning a deploy-time attestation suffices.

The third branch, which did not exist when the pair was framed:

3. **Continuous proof at the ACTION boundary rather than the STATE boundary.** Flux proves the
   *state* of a control between deploys. An action-boundary monitor proves *no action crossed* the
   control, continuously and fail-closed. Both are continuous. They are continuous about different
   things, and a control can hold its declared state for a whole window while an action crosses it.

**Ticket 64's window cannot see branch 3, and its addendum now says so.** It measures state drift
only. So a null result falsifies branch 1 and leaves branch 3 untouched. Reading a null result as
"Flux is a convenience, therefore point-in-time suffices" would be a false dichotomy, on the
critical path, written into a durable artefact.

**This branch is not an AWS product decision.** Action-boundary monitoring has at least five
independent implementations, of which AWS Dogwood (2026-08-06) is the newest and, on the evidence,
not the best: Progent (Apr 2025), AgentSpec (ICSE 2026, Mar 2025), Agent-C (Mar 2026), Causal Past
Logic (May 2026), VIGIL (Jun 2026). Judge the *class*, not the product.

**If branch 1 fails, Flux is a convenience rather than an enabler, and the spec is amended.** Write
the amendment either way; a test whose negative result changes nothing was not a test.

**Blocked by:** 64, 29, 11

**Status:** ready-for-agent

**Reading list:** Decision ticket 22. Spec stories 81, 85.

- [ ] The verdict is derived from ticket 64's measured drift data, not from argument.
- [ ] The risk basis is stated precisely: which priced impact, at which evidence grade, requires continuity.
- [ ] A written verdict either way, with the spec amendment drafted for the failing case before the result is known.
- [ ] If Flux survives, its role is stated as narrowly as the evidence supports.
- [ ] **All three branches are answered separately.** A null state-drift result closes branch 1 only, and the verdict says so explicitly rather than concluding branch 2 by elimination.
- [ ] **Branch 3 is answered on the class, not on any product.** If the answer needs evidence, it needs its own pre-registered window; the verdict records that no such window is open rather than inferring one is unnecessary.
- [ ] The verdict cites `estate/driftwood/drift/window.yaml`'s `scope_limit` addendum and states what the instrument could not see.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
