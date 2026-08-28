---
status: accepted
---

# A clock appends observations, never declarations; one signature, verified at the source by a controller

Five held rounds answered the same two questions differently: whether a scheduled run may commit
to `main` (tickets 03, 10, 16, 20) and whether Flux needs a second signature on the tag
(tickets 12, 16, 18). Put to the owner on 2026-08-28 with a three-lens panel. The owner wrote
"I agree with you're more advanced reasoning". Decided in `.scratch/ecosystem/issues/10` and `16`.

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
