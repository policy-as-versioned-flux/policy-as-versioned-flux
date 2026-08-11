# 01 — Model repository layout and the `twin` CLI shell

**What to build:** A `twin` command loads a **pinned model repository** and emits an artefact to a declared output
path. Nothing is modelled yet — the point is that the repository shape, the pin mechanism and the
artefact envelope exist and are stable, because every later ticket writes into them.

Git-versioned text is the source of truth; any store is a derived index rebuildable from it. Bulk
synthetic substrate is the sole exception and is addressed by content hash rather than held inline —
establish the *hook* for that here even though nothing uses it until the substrate track.

**Blocked by:** None — can start immediately

**Status:** done (2026-08-05)

**Reading list:** Decision tickets 07 (domain data model), 14 (provenance and attestation). Constitution: `00-constitution.md`.

- [x] `twin` loads a model repository at a named git ref and refuses to run against a dirty tree.
- [x] The artefact envelope carries: input pins, the producing command, a depth grade slot, and an authored/derived mark.
- [x] A content-hash reference form exists for bulk substrate and round-trips, even with no substrate present.
- [x] Running the same command twice against the same ref produces byte-identical output.
- [x] `store_rebuildable_from_git` — a demonstration that any derived index can be dropped and rebuilt from the repository alone.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.

## Built (2026-08-05)

`twin/repo.py`, `twin/artefact.py`, `twin/attest.py`, `twin/blob.py`, `twin/index.py`, `twin/cli.py`.

- Reads go through a git **tree object**, never the working tree, so the pin describes exactly what was
  read. A dirty model root — untracked files included — is refused outright rather than warned about.
- The envelope carries pins (model repo, world, overlay, tool), the producing command, a computed depth
  block and an authored/derived mark. It carries **no wall clock, host or interpreter**: those would break
  `identical_pins_identical_bytes` across architectures, so they live in the attestation sidecar
  `<artefact>.att.json` instead. That split is the one non-obvious decision here and it is load-bearing.
- The recorded command is canonicalised rather than `sys.argv`: `--repo` and `--out` are where the work
  happened, not inputs to the derivation, and a machine path in the envelope would break byte-identity.
  A forecast being scored is named by digest for the same reason.
- Substrate reference form is `sha256:<64 hex>:<size>`; it round-trips through the envelope with no
  substrate present, exercised by an Intel fixture signal whose reference resolves to nothing on purpose.
- The derived index is written per unit (`world.json`, `orgs/<org>.json`) so no derived artefact mixes
  tenants, and `store_rebuildable_from_git` drops and rebuilds it.

Not built: cryptographic signing (build ticket 11 — `signature` is null and says so); any schema beyond
what the walking skeleton needs (12); any substrate to resolve a reference against.
