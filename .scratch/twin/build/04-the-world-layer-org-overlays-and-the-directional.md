# 04 — The world layer, org overlays, and the directional reference rule

**What to build:** A shared **world layer** (landscape, technologies, markets, geopolitics) and **per-org overlays**
each org owns and never shares, as separate versioned units. An overlay may reference the world
layer; the world layer may **never** reference an overlay. That single directional rule is what
makes multi-tenancy and the credibility-theory prior the same mechanism rather than two.

**Blocked by:** 03

**Status:** ready-for-agent

**Reading list:** Decision ticket 07 (domain data model). Spec stories 4, 5, 10.

- [ ] World layer and overlays are separately versioned units with independent refs.
- [ ] `world_never_references_overlay` goes live and fails on a planted violation.
- [ ] An overlay resolves world-layer references at a pinned world ref, so an overlay is reproducible against a moving world.
- [ ] Two overlays over one world layer coexist with no cross-visibility.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
