# 44 — `evolution-judge`, and human override with pushback

**What to build:** Infer a component's evolution position **from accumulated evidence first**, then let a human
correct it — and have the twin **push back** on the override.

The two halves are one contract: a correction is a provenanced claim that is **itself scored**.
Humans get calibrated against evidence too, which is the whole reason inference comes first rather
than starting from opinion.

**Blocked by:** 42, 14

**Status:** ready-for-agent

**Reading list:** Decision ticket 11. Spec stories 13, 14.

- [ ] Position inferred from accumulated evidence before any human input is accepted.
- [ ] An override is recorded as a provenanced, graded claim attributable to a role.
- [ ] The twin states its disagreement and its basis when overridden — silence is not an option.
- [ ] Override accuracy is scored over time on the same footing as the twin's inference.
- [ ] Evaluated against dated positions from the public spine.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
