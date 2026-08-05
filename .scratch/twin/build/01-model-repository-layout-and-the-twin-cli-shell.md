# 01 — Model repository layout and the `twin` CLI shell

**What to build:** A `twin` command loads a **pinned model repository** and emits an artefact to a declared output
path. Nothing is modelled yet — the point is that the repository shape, the pin mechanism and the
artefact envelope exist and are stable, because every later ticket writes into them.

Git-versioned text is the source of truth; any store is a derived index rebuildable from it. Bulk
synthetic substrate is the sole exception and is addressed by content hash rather than held inline —
establish the *hook* for that here even though nothing uses it until the substrate track.

**Blocked by:** None — can start immediately

**Status:** ready-for-agent

**Reading list:** Decision tickets 07 (domain data model), 14 (provenance and attestation). Constitution: `00-constitution.md`.

- [ ] `twin` loads a model repository at a named git ref and refuses to run against a dirty tree.
- [ ] The artefact envelope carries: input pins, the producing command, a depth grade slot, and an authored/derived mark.
- [ ] A content-hash reference form exists for bulk substrate and round-trips, even with no substrate present.
- [ ] Running the same command twice against the same ref produces byte-identical output.
- [ ] `store_rebuildable_from_git` — a demonstration that any derived index can be dropped and rebuilt from the repository alone.
- [ ] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [ ] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
