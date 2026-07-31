# 02 — Estate + cluster + Flux bootstrap

**What to build:** The six `policy-as-versioned-*` repos scaffolded and a `driftwood` KinD cluster reconciling from a gitsign-signed GitRepository via Flux — the provenance base everything stacks on.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [ ] Six org repos scaffolded (`platform`, `driftwood`, `tuppence`, `ludlow`, `nist`, `ico`)
- [ ] `driftwood` KinD cluster up; Flux installed and reconciling
- [ ] GitRepository pinned to a signed tag+commit (gitsign); reconcile healthy
- [ ] Idempotent bring-up + reset script (touring requirement)
