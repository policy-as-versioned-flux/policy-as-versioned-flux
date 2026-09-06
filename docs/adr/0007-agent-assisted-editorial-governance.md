---
status: accepted
---

# Governance: agent-assisted editorial review (the human layer the mea-culpa demands)

The full human-governance layer is in scope, realised as **editorial review** (per ADR-0006: a
reviewed PR changes/removes a policy; nothing time-triggered), supported by an **AI/agent
governance layer** that is *specified as first-class architecture* and *demonstrated* with a thin
reference agent (not a full production risk-intelligence system).

## The agent layer contract

- **Inputs:** the versioned policy + its embedded rationale / risk / ethos metadata, plus external
  signals — new CVEs, cloud-provider changes, regulatory shifts, and Wardley-style climatic
  movement (e.g. a control whose risk profile changed because the underlying tech commoditised).
- **Output:** noise-reduced, surfaced **business decisions** ("this policy's rationale may be stale
  because X — here is the consequence; do you still defend it?") as **review issues/PRs** against
  the policy repo.
- **Boundary:** the agent **never edits enforcement** and never mutates policy state directly. It
  prompts the human editorial decision. The policy code stays deterministic (ADR-0006).

## Advisory metadata (carried, not enforced)

Each policy version carries `created`, `lastReviewed`, rationale/`why`, and risk/ethos — as
annotations + a versioned `rationale.md`, mappable to OSCAL. This metadata is **advisory input for
humans and agents only**; the engine never consumes it. (Resolves the old D8.1: the "why" is
*carried* on the floor, not hard-enforced; enforcing it via a signed cosign attestation needs the
OCI path and is a north-star item.)

## Last-mile to non-technical consumers

> **Confirmed 2026-08-28 (eco-system ticket 13 Q4), written 2026-09-06 (ticket 80 item 7).** This
> section carried "(proposed — confirm)" inside an accepted ADR for the whole of the original
> build. It is confirmed, with a mechanism: the handbook is a **compose-time render**. A tool the
> platform publishes runs inside each adopter's compose step over that adopter's own composed
> artefact; the render lands in the same PR and under the same gitsign tag as the artefact; and
> `verify-fresh.sh` (render-at-tag equals committed render) becomes the truth-surface script,
> gradable offline, with the end-to-end `verify.sh` retired beside it. The `claude -p`
> plain-language summaries become a Claude Code skill a human runs, whose output lands by PR.
>
> **Why this shape and not the original's.** A scheduled job committing a render to `main` is a
> machine write outside the reviewed PR, which the eco-system forbids
> ([ADR-0023](0023-a-clock-appends-observations-and-one-signature-verified-by-a-controller.md): a
> clock appends observations, never declarations), so "on a schedule, signed with the artefact"
> could not both hold. Rendering from the signed tag cannot drift from the enforced policy, which
> is the owner's dashboard objection in reverse. Full adoption by non-technical humans stays
> partly cultural and stays named as a residual open problem.
>
> Delegated ([ADR-0025](0025-the-assistant-decides-architecture-and-records-it.md)): the owner
> answered ticket 13's round with "ive already read the recommendations and I can't find fault
> with a single one", a bare agree, recorded as the assistant's decision and not re-asked. Record:
> [issues/13](../../.scratch/ecosystem/issues/13-lift-or-retire-the-original-mechanisms.md) Q4.
> **Not yet built**: nothing in the estate renders a handbook today.

Attempt the last mile by **auto-generating an always-in-sync, human-readable policy handbook** from
the versioned source (so the "operational manual" the talk's Cleaner reads can never drift from the
enforced policy), with **agent-authored plain-language summaries** of each policy and its "why".
Full adoption by non-technical humans remains partly cultural and is named as a residual open
problem — honest, as the mea-culpa frames it.

## Consequences

- A new component (the governance agent) and a metadata schema enter the design.
- The agent demonstrator is bounded: one external signal source, proves the contract. **Correction
  (2026-07-18, wave-1 audit)**: this originally said "opens PRs" -- the actual demonstrator
  (issue 24, `governance-agent/SPEC.md` §4) deliberately opens GitHub issues instead, because the
  agent has no policy-content edits to propose; a PR implies a diff, and this signal path never
  has one. The never-edits-enforcement invariant is the point, not an implementation detail this
  line should have overridden. **Second correction (2026-07-18, wave-2 audit)**: the first
  correction's own wording ("issues:write only, no contents/pull-requests write") repeated the
  same overclaim `governance-agent/SPEC.md`/`README.md` had already been corrected to retract the
  same day -- no scoped GitHub App or token was ever set up; every write in this estate runs on
  the same full-access personal `gh` auth throughout. The real guarantee is code-level only: the
  demonstrator's only write path anywhere is `gh issue create`, grep-verified.
- This is the most novel, least-Flux part of the work and the clearest original contribution beyond
  both the 2022 implementation and collie.
