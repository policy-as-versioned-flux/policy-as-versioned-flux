# Upstream workstream: keyless (gitsign) verification for Flux `GitRepository`

**Status:** **project action** — CNS will rework the drafted comment below and post it as part of
this work. Contribution-of-implementation decision deferred until a maintainer signals appetite.

## Why this is in scope

The transport decision for *Policy as Versioned Flux* landed on **signed git tags, keyless via
gitsign** (see ADR-0001) — faithful to the 2022 original and key-custody-free. We explicitly
rejected adopting OCI just to obtain a verification gate.

The consequence we accepted: `GitRepository.spec.verify` is **PGP/GPG-only**, so Flux **cannot
verify gitsign signatures today**. On the floor we therefore verify in CI / at-merge
(`gitsign verify` against Rekor) and treat the missing Flux-native gate as a **current Flux
limitation to push upstream**, not a reason to change transport.

Closing this gap upstream would give the chosen transport a **Flux-native, keyless, pre-apply
verification gate** — completing the design without OCI — and benefits the whole Flux community.
This is the single upstream dependency between our design and Flux, which is why we are actively
raising it rather than merely noting it.

## Existing issue (do NOT file a duplicate)

- **[fluxcd/source-controller#1068](https://github.com/fluxcd/source-controller/issues/1068)** —
  "add gitsign as an additional verifier for Git commit signatures"
- Opened **2023-04-09** by `developer-guy` (w/ `@dentrax`); pinged `@dlorenc`, `@wlynch`.
- State: **OPEN**, **dormant** — 1 👍, 0 comments, no labels, no linked PR in ~3 years.

The ask is exactly ours: add gitsign (Sigstore — Fulcio + Rekor, OIDC keyless) as an *additional*
verifier alongside the existing PGP path for git commit/tag signatures.

## The genuine technical hard part (be honest about it in any contribution)

gitsign is **not** verifiable with `git verify-commit` + a static key. A correct verifier must:

1. Parse the commit's signature header (CMS/x509 from Fulcio, not OpenPGP).
2. Validate the ephemeral Fulcio cert **as of the commit time** (the cert is short-lived; naive
   "is it valid now" always fails) — i.e. check the **Rekor** transparency-log inclusion proof and
   the signed cert timestamp.
3. Match the certificate's OIDC identity (issuer + subject) against a configured trust policy —
   the git analogue of `OCIRepository`'s `matchOIDCIdentity`.

This is why it stalled: it is real work, and it overlaps the `gitsign verify` semantics. A
contribution should likely reuse `sigstore-go` / gitsign's verification libraries rather than
re-implement Rekor validation. Air-gapped/no-Rekor environments (UK public sector) need a story
for offline verification (bundled inclusion proofs) — worth raising explicitly.

## Proposed actions

### (a) Revival comment to post on #1068 — DRAFT (for CNS to post under his account)

> Picking this up three years on — there's a concrete production use case that would benefit.
>
> I maintain "Policy as [Versioned] Code", a pattern that distributes organisational policy as a
> semantically-versioned dependency and consumes it via Flux. We want the policy artifact's
> signature **verified before it is admitted to a cluster**, and we want **keyless** signing so
> there are no long-lived GPG keys to custody across a fleet (a real operational cost in
> regulated/large estates).
>
> Today the only path that gives keyless signing *and* a Flux-enforced gate is
> `OCIRepository` + cosign keyless. For teams whose source of truth is git tags (the most legible,
> reviewable form of "what is the policy and what version is it"), there is no equivalent:
> `GitRepository.spec.verify` is PGP-only, so adopting gitsign means losing the verification gate.
>
> Would the maintainers be open to a contribution adding a `gitsign`/sigstore provider to
> `GitRepository.spec.verify`, mirroring the `cosign` keyless model on `OCIRepository`
> (`provider: cosign|notation|gitsign`, `matchOIDCIdentity`)? Happy to scope it. Two design points
> I'd want to settle first: (1) cert-validity-at-commit-time via Rekor inclusion proofs, and
> (2) an offline/air-gapped verification story (bundled proofs) for regulated environments.

### (b) Contribution decision — for CNS

- **Comment only** — add weight, let maintainers/community implement. (Low effort, slow.)
- **Contribute the implementation** — ControlPlane (a Flux maintainer org) authors the
  `gitsign` provider. High value, on-brand, but a real chunk of work; would be its own project,
  not part of the policy reference build. Recommend: raise intent in the comment, decide after a
  maintainer signals appetite.

## How this feeds the PRD

- Faithful floor ships on **signed git tags + gitsign**, verifying in CI/at-merge; it does **not**
  block on #1068.
- #1068 landing upgrades the floor in place: the same gitsign signatures become **Flux-natively
  verified at the source** (`GitRepository.spec.verify` gitsign provider), closing the only
  upstream gap in the design.
- The drafted revival comment above is a **project action** for CNS to rework and post.
