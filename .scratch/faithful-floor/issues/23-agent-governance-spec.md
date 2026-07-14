# 23 — Agent governance layer: architectural spec

**What to build:** The complete architecture for the agent governance layer (ADR-0007): inputs (versioned policy + embedded rationale/risk/ethos + external signals — CVEs, cloud/regulatory change, Wardley climatic movement), output (noise-reduced business decisions surfaced as review PRs/issues), and the hard boundary — it prompts editorial review, it never edits enforcement. Spec only; the demonstrator is the next ticket.

**Blocked by:** 22 — Advisory metadata schema.

**Status:** done

- [x] Spec covers signal ingestion, noise reduction, decision framing ("rationale may be stale because X; consequence Y; do you still defend it?"), and PR/issue surfacing
- [x] The never-edits-enforcement boundary is stated as an invariant with its enforcement mechanism
- [x] The bounded demonstrator's scope (one signal source) is carved out explicitly

## Comments

Done 2026-07-14. New repo `governance-agent`
([`SPEC.md`](https://github.com/policy-as-versioned-flux/governance-agent/blob/main/SPEC.md)),
split out same as the other planes rather than folded into `policy` -- this is a consumer of the
policy repo's advisory metadata (issue 22), not part of it.

Three signal classes given genuinely different treatment rather than one generic "external
signals" polling loop: CVEs (fully automatable, GitHub Security Advisories/OSV.dev against a small
watched-dependencies manifest), cloud/regulatory change (partially -- detecting change is
automatable, judging relevance isn't), Wardley climatic movement (not automatable at all --
modelled honestly as a human-curated YAML file rather than pretending there's an API for "this
technology just commoditised"). Noise reduction is four gated stages (relevance match, severity
threshold, dedup, batching) so a raw signal only becomes a surfaced decision if it survives all
four -- the whole point is a human sees one sentence, not a CVE feed. Decision framing is the
ADR-0007 template verbatim, fixed regardless of which signal triggered it.

The enforcement mechanism for "never edits enforcement" is a real technical boundary, not a
behavioural promise: the agent's GitHub App token is scoped `issues: write`, `contents: read` on
the `policy` repo, no `contents: write`/`pull-requests: write` at all -- so even a buggy agent
gets a 403 from GitHub's own API if it ever tried to push a commit. Same pattern as issue 22's
determinism proof: the guarantee comes from what's structurally possible, not from asking nicely.

Bounded demonstrator scope (issue 24) committed to one concrete signal source: GitHub Security
Advisories for `kyverno/kyverno` itself -- already this project's own governed dependency
(ADR-0003), traceable to every policy since all depend on the engine, no new credentials needed
beyond this org's existing `gh` auth. Everything else in the signal table is explicitly out of
scope for the demonstrator.
