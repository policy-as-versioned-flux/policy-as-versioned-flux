# 33 — The trade-off curve across the ensemble

**What to build:** The output shape: a **trade-off curve across the ensemble with a marked default** — never a
verdict. When two world models disagree about pay-rise-versus-hardening, **that disagreement is the
headline**.

A single number ends a conversation; a map sustains one. Every place this system could collapse to a
verdict, it deliberately does not, because terminating the argument would destroy the thing's
function.

**Blocked by:** 30, 32

**Status:** ready-for-agent

**Reading list:** Decision tickets 09, 13. Spec stories 34, 36.

- [ ] Output is a curve over the ensemble, with the default marked and its basis stated.
- [ ] `no_recommended_action_field` is re-asserted against this richer output.
- [ ] Ensemble disagreement is surfaced prominently rather than averaged away.
- [ ] A test that no consumer-facing path reduces the curve to a scalar.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
