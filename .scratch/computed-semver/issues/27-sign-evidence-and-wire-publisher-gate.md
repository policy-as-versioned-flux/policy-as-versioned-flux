# 27 — Sign the evidence and wire the publisher gate

Type: task
Status: done (2026-08-24)
Blocked by: 15, 20, 23, 26

Source: [`spec.md`](../spec.md), *Where the gate runs, and what it compares*, and *Signing and
verification*.

## What to build

A publisher dispatches `cut-release.yml` and the gate answers before the tag exists. A refusal does not
burn a version number for ever.

**The declared bump is read from the release workflow's `version` input.** The gate runs before
`git tag`. A gate after the tag can only burn the number.

**There is no override.** `CONTEXT.md` bans exemptions at any scope and under any name. An override
carrying evidence, a signature and an expiry is the exemption ledger this estate already deleted.
Over-declaring the bump is the only relief valve, and it is safe in one direction. A publisher who
believes the corpus misleads raises a reviewed pull request against the generator or the policy.

**Sign every evidence file with `cosign sign-blob` keyless, for both outcomes.** The gate emits and
signs the evidence when it refuses, not only when it passes. A refusal is the most valuable output the
gate produces. This removes the repo-local ed25519 signing shape rather than adding a mechanism.

**On success, commit the evidence and its bundle in the release commit, before the tag.** One tag then
reaches both, for ever, from any clone. Verification is offline, because the bundle carries the
certificate, the signature and the Rekor inclusion proof.

**On refusal there is no commit and no tag.** The signed file and its bundle go out as run artifacts
and a job summary.

**`release.yml` keeps a cheaper check** that the signed evidence matches the tag. That catches a tag
pushed by any other route.

**No schedule anywhere.** Every trigger is a pull request or a release dispatch. A scheduled finding
has no pull request to carry the debate.

The gate cannot ship before [ticket 15](15-the-repair-release.md). The gate fails when movement traces
to an unversioned policy, so it would refuse every release from day one for a reason unrelated to the
release.

An offline twin runs the same code path locally. CI stays the authority, because only CI holds the
signing identity.

## Acceptance criteria

- [x] The gate runs inside `cut-release.yml`, before `git tag`.
- [x] It reads the declared bump from the workflow's `version` input.
- [x] No override exists at any scope or under any name.
- [x] `cosign sign-blob` keyless signs the evidence on pass and on refusal.
- [x] On success the evidence and its bundle are committed in the release commit, before the tag.
- [x] On refusal there is no commit and no tag, and the signed file goes out as a run artifact and a job summary.
- [x] `release.yml` checks that the signed evidence matches the tag.
- [x] Verification works offline from the committed bundle.
- [x] A publisher can run the same gate on their own machine, through the offline twin.
- [x] No workflow in the change carries a schedule trigger.
- [x] The `feeds/sign.sh` repo-local ed25519 shape is removed, not duplicated.

## Comments

Shipped in `platform` at `1a8b871` + `f5c0461` + `4c67693` (cs-27). This is the mechanism that gated the real cs-16 backport release for the first time, live.
