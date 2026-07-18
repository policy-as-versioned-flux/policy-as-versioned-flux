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

## Last-mile to non-technical consumers (proposed — confirm)

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
  has one. The never-edits-enforcement invariant (issues:write only, no contents/pull-requests
  write) is the point, not an implementation detail this line should have overridden.
- This is the most novel, least-Flux part of the work and the clearest original contribution beyond
  both the 2022 implementation and collie.
