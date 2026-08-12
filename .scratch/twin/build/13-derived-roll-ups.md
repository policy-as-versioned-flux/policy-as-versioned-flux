# 13 — Derived roll-ups

**What to build:** Roll-ups are derived, never authored, so an aggregate can never drift from its constituents.

**Blocked by:** 12

**Status:** done (2026-08-06)

**Reading list:** Decision ticket 07. Spec story 9.

- [x] A roll-up is computed from constituents on read and has no authored form.
- [x] An attempt to author a roll-up value directly is rejected.
- [x] Changing a constituent changes the roll-up with no separate step.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-06)

`Graph.rollups()` in `twin/model.py`, `refuse_authored_rollups` in `twin/schema.py`, and the
`rollups` block in every graph artefact.

- **No second copy, so nothing can drift.** A roll-up is computed from its constituents on every read
  and exists only for as long as it takes to serialise. "An aggregate can never drift from its
  constituents" is therefore structural rather than a discipline — there is nothing to drift *from*.
- **No authored form.** The closed schemas are the guarantee: no schema declares an aggregate, so
  there is nowhere to write one. Eight aggregate field names are additionally refused at any depth,
  which is the only place closure cannot reach — inside a free-form `provenance` mapping. That list
  is a net, like the Article 9 one, and it is deliberately narrow: `count` and `summary` are ordinary
  words in provenance prose.
- **No stored form either.** The derived index is the one store in the system and the invariant now
  asserts it holds no aggregate.
- `store_rebuildable_from_git` was extended rather than a seventeenth invariant added: the
  constitution names sixteen, and the manifest may not grow without the constitution changing first.

Not built: nothing in this ticket ticks a decision-ticket criterion. Decision ticket 07's AC 5 covers
the authored/derived split, but it also covers the representation/format reuse-vs-custom decision,
which is not recorded anywhere in code — so it stays unticked rather than being ticked on one clause.
