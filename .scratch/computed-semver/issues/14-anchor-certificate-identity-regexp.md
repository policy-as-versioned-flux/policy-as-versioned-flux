# 14 — Anchor the certificate identity regexp in all six repos

Type: task
Status: ready-for-agent
Blocked by: none

Source: [`spec.md`](../spec.md), *Signing and verification*, and *One cross-repo change*.

## What to build

A backport is dispatched from a maintenance branch. Its certificate identity therefore ends with that
branch ref, not with `@refs/heads/main`. Every repo pins `main` today, so a backport fails
verification. [Ticket 16](16-backport-1-0-1.md) cannot land until this does.

Replace the exact identity with an anchored `--certificate-identity-regexp`. The regexp allows `main`
and one maintenance branch shape. It still pins the organisation, the repository and the workflow
path. An unanchored regexp would accept a foreign identity, so anchor both ends.

This is one mechanical change across six repos. Do it as one expand step. No repo needs the old form
afterwards.

## Acceptance criteria

- [ ] All six repos verify with an anchored `--certificate-identity-regexp`.
- [ ] The regexp matches `main` and the maintenance branch shape, and nothing else.
- [ ] The regexp pins the organisation, the repository and the workflow path.
- [ ] A test or a documented check proves that a foreign organisation fails the regexp.
- [ ] Existing releases signed from `main` still verify.
