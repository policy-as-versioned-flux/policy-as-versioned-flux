# 04 — The world layer, org overlays, and the directional reference rule

**What to build:** A shared **world layer** (landscape, technologies, markets, geopolitics) and **per-org overlays**
each org owns and never shares, as separate versioned units. An overlay may reference the world
layer; the world layer may **never** reference an overlay. That single directional rule is what
makes multi-tenancy and the credibility-theory prior the same mechanism rather than two.

**Blocked by:** 03

**Status:** done (2026-08-05)

**Reading list:** Decision ticket 07 (domain data model). Spec stories 4, 5, 10.

- [x] World layer and overlays are separately versioned units with independent refs.
- [x] `world_never_references_overlay` goes live and fails on a planted violation.
- [x] An overlay resolves world-layer references at a pinned world ref, so an overlay is reproducible against a moving world.
- [x] Two overlays over one world layer coexist with no cross-visibility.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/model.py`.

- World and overlays are separately versioned units with genuinely independent refs — the unit ref is the
  last commit touching that subtree plus its tree hash, so they advance separately inside one repository
  and the same form still works if they are ever split into separate repositories.
- An overlay's `meta.yaml` **must** declare `world_ref`; without it the overlay refuses to load, because
  an overlay that floats against a moving world is not reproducible. Tested by advancing the world and
  showing the overlay does not shift.
- `world_never_references_overlay` is live: exact-match on any scalar string in the world layer against
  org ids and overlay-declared ids, plus paths into the overlay tree and overlay-scoped keys. A planted
  violation is caught.
- Loading an overlay reads that org's subtree and the world, nothing else. Netflix cannot see Intel's
  components, world models or signals, and scoring across the boundary fails.
