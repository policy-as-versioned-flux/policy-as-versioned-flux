# 14 — Anchor the certificate identity regexp in all six repos

Type: task
Status: done (2026-08-24)
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

- [x] All six repos verify with an anchored `--certificate-identity-regexp`.
- [x] The regexp matches `main` and the maintenance branch shape, and nothing else.
- [x] The regexp pins the organisation, the repository and the workflow path.
- [x] A test or a documented check proves that a foreign organisation fails the regexp.
- [x] Existing releases signed from `main` still verify.

## Comments

Shipped in `platform` at `379aade` (cs-14). Also rolled out to all five downstream repos, real and pushed to their real GitHub remotes: `driftwood` at `e23be9b` + `325b854`, `tuppence` at `74ceed1`, `ludlow` at `c94f45c`, `nist` at `76cd4cb`, `ico` at `8902b66`.
