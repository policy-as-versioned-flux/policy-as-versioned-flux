# 50 — Spine anchoring and free-running

**What to build:** Anchor the substrate to the **immutable public spine** — the real dated record — but let it
free-run where the record is silent.

Both halves matter: anchoring makes the ground truth real, and free-running is what stops plants
being trivially findable by diffing the substrate against the public spine.

**Blocked by:** 49

**Status:** ready-for-agent

**Reading list:** Decision tickets 06 (flagship OSINT scoping), 12. Spec story 57.

- [ ] Substrate reconciles with the public spine at every dated checkpoint.
- [ ] Where the record is silent the substrate free-runs, and a diff against the spine does not reveal plant locations.
- [ ] A test attempting the diff attack and failing to locate plants.
- [ ] Spine facts carry knowability dates so regime gating works over the substrate.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
