# Releasing `twin`

`twin` lives inside the hub repository but is consumed from outside it: each adopter vendors this
package's world layer into its own repo and renders its overlay with this package's loader
(ticket 11 answer item 1). A consumer that cannot name a version is pinning a branch, so the
package self-versions.

## The version

`twin/VERSION` is the release. It is the same string as `twin.TOOL_VERSION`, which every emitted
artefact already carries as a pin, and `verify/twin-evals/verify-twin-evals.sh` fails if the two
ever disagree — one version, spelled in a file a shell can read and a constant Python can import,
never two numbers that drift.

## The tag the owner must cut

    twin/v0.1.0

Prefixed, because the hub repository is not the twin: `talk/`, `verify/` and the twin all live
here, and an unprefixed `v0.1.0` would claim the whole repository. Cut on the commit that carries
this file, by the hub's release workflow with gitsign, exactly the way every other unit's tag is
cut (ADR-0012, D3). **It is not cut yet.** Nothing in this build can cut it: a signed tag is cut
in Actions, never locally, so until the owner merges and the workflow runs, an adopter's
`VENDORED.md` records the tag it is waiting for beside the commit it actually vendored from.

## What an adopter pins

An adopter vendors the standing-library world layer
(`twin.fixtures.LIBRARY_WORLD_FILES`) into `<adopter>/twin/world/` and records the release in
`<adopter>/twin/PIN.yaml`:

```yaml
twin_version: 0.1.0
twin_tag: twin/v0.1.0
tag_cut: false
```

The adopter's emitter refuses to render if `twin_version` is not this file's `VERSION` — a pin
that does not describe the code it is rendered by is not a pin. Once the tag exists, Renovate can
bump both lines with the `git-refs` datasource the estate already uses for `platform`, and
`tag_cut` becomes true.

## Bumping it

Bump `twin/VERSION` and `twin.TOOL_VERSION` in the same commit as the change that alters emitted
bytes, then re-vendor into each adopter (`VENDORED.md` in each carries the two-line recipe). A
world-layer change that adopters vendor is a release, not an internal edit.
