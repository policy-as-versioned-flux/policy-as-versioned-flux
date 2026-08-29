---
status: accepted
---

# A clock appends observations, never declarations; one signature, verified at the source by a controller

Five held rounds answered the same two questions differently: whether a scheduled run may commit
to `main` (tickets 03, 10, 16, 20) and whether Flux needs a second signature on the tag
(tickets 12, 16, 18). Put to the owner on 2026-08-28 with a three-lens panel. The owner wrote
"I agree with you're more advanced reasoning". Decided in `.scratch/ecosystem/issues/10` and `16`.

## Amendment, 2026-08-29: what "one signature" is true of today

D3 below says the gitsign tag is the only signature. Three verification mechanisms are live in the
gate, and the two that are not gitsign are inherited, not new. Recorded here rather than left as an
ADR asserting something the gate contradicts. Nothing in this amendment permits a new signer: hard
rule 6 stands, no new `.sig`, key or bundle may be added for any artefact.

1. **The cosign evidence bundle.** `platform/computed-semver/evidence/*.json.bundle`, produced by
   `.github/scripts/cut-release-gate.py` with `cosign sign-blob` and verified by every adopter's
   `.github/scripts/adopter-gate.py`. It is the only signature a consumer actually verifies today,
   and it covers a release-gate evidence blob rather than an artefact. **Retires when** the
   adopter gate reads the release evidence out of the signed tag instead of a detached blob.
2. **platform's ed25519 feed key**, `feeds/keys/feeds-signing-key.pub.pem` with the `.sig` files
   beside the threat-register, cve and eol feeds. Its feeds have migrated to the `feeds` party on
   this branch, and every adopter now pins the migrated versions. **Retires when** the `feeds`
   party has cut the tags those pins wait for: delete `feeds/keys/`, the `.sig` files and the five
   openssl blocks that read them (`platform/feeds/verify-feeds.sh`, `wardley/`, `honesty/`,
   `wargamer/`, and the hub's `verify/provenance/`).
3. **ico's ed25519 schema key**, `schema/keys/ico-signing-key.pub.pem`, `schema/sign.sh` and the
   `.sig` files beside `schema/v1` and `schema/v2`. The penalty schema now publishes in the
   ADR-0019 envelope and all three adopters pin `penalty-schema` v3. **Retires when** ico has cut
   the `v3.0.0` tag those pins wait for: delete `schema/keys/`, `schema/sign.sh`, the `.sig` files
   and `verify-penalty-feed.sh`'s openssl block.

Both key-based signers are past the trigger their own migration set and are waiting only on tags
`cut-release.yml` cuts after a merge, which no agent may cut (hard rule 3). Until those tags exist
the estate cannot say "one signature" without this paragraph beside it.

## The decision

- A scheduled run may **append observations** to `main`: the truth log, drift samples, gate
  captures. It may **never commit a declaration**: a tier, a pin, a floor, an overlay, a priced
  evidence file. The lane is caged. A repo ruleset limits the scheduled identity to the
  observation paths and its commits are signed. `verify-schedules.sh` asserts that no scheduled
  run ever changed a signed artefact.
- A scheduled publisher fetch opens a PR when the computed bump is not `none`. Each feed defines
  "changed" in its own versioned rule file. Sub-threshold observations append to an observation
  branch so a series survives.
- The **gitsign tag** stays the only signature on every artefact (ADR-0012, ADR-0019). Cluster-side
  verification is an identity-pinned gitsign-verifying **controller** at the Flux source boundary,
  time-boxed until Flux #1068 lands. No key re-signs any ref.
- The demo's step-4 number comes only from the scheduled CI run. A presenter-run number is
  rehearsal, never cited.
- A pin behind a newer published version is priced by the existing EOL ramp from the newer
  version's publish date. `revoked[]` stays withdrawal, priced now.

## Alternatives

- No clock commits to `main`. Rejected: it silently reverses ticket 03, whose daily `truth.log`
  is the only citable number.
- SSH on the tag, gitsign on the commit. Rejected: a tag carries one signature block, every
  `release.yml` verifies the tag with gitsign, and a bridge key is a second signer under another
  name.
- A dated supersede in `revoked[]`. Rejected: two formulas for one state. Revisit with an explicit
  `supersedes: {version, eol_date}` if the ramp misprices.

## Consequences

ADR-0010's line (timed proposals, never timed application) gains the sharper wording above. The
controller is a trust boundary and the truth surface grades it as one. Step 4 reports
could-not-look until the ephemeral KinD run lands.
