# 65 — The Flux falsification verdict

**What to build:** **Run the test rather than assume the answer.** Does the risk basis require **continuous**
proof-of-force, or would a **deploy-time attestation** suffice?

Drift between deploys is the candidate justification — a control silently removed after deployment is
exactly the case a point-in-time attestation misses and reconciliation catches — but that must be
demonstrated, not asserted.

**If it fails, Flux is a convenience rather than an enabler, and the spec is amended.** Write the
amendment either way; a test whose negative result changes nothing was not a test.

**Blocked by:** 64, 29, 11

**Status:** ready-for-agent

**Reading list:** Decision ticket 22. Spec stories 81, 85.

- [ ] The verdict is derived from ticket 64's measured drift data, not from argument.
- [ ] The risk basis is stated precisely: which priced impact, at which evidence grade, requires continuity.
- [ ] A written verdict either way, with the spec amendment drafted for the failing case before the result is known.
- [ ] If Flux survives, its role is stated as narrowly as the evidence supports.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
