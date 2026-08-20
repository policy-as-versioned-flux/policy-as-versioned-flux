# 02 — Estate + cluster + Flux bootstrap

**What to build:** The six `policy-as-versioned-*` repos scaffolded and a `driftwood` KinD cluster reconciling from a gitsign-signed GitRepository via Flux — the provenance base everything stacks on.

**Blocked by:** None — can start immediately.

**Status:** PARTIAL — scaffolding done; live cluster claims unverified, no Docker daemon reachable in this environment (`docker info` hung >120s; `kind get clusters` empty)

- [x] Six org repos scaffolded (`platform`, `driftwood`, `tuppence`, `ludlow`, `nist`, `ico`) — `ls estate/`: all six dirs present, each with its own `README.md`
- [ ] `driftwood` KinD cluster up; Flux installed and reconciling — **unverified live**: no Docker daemon reachable here; `estate/driftwood/kind/driftwood.yaml` + `scripts/up.sh` exist but were not run
- [ ] GitRepository pinned to a signed tag+commit (gitsign); reconcile healthy — **unverified live**, and note `scripts/up.sh:35` tags with a plain annotated tag (`git tag -a`), not gitsign, for the offline demo; the README (`estate/driftwood/README.md`) itself documents gitsign only applies "on the real remote" — that remote's actual signed state was not checked here (no network)
- [x] Idempotent bring-up + reset script (touring requirement) — `estate/driftwood/scripts/up.sh` (comment: "safe to re-run: it skips the cluster/Flux if already up") + `scripts/reset.sh` both present; not executed to confirm behaviour (no Docker)

## Comments

- 2026-08-20 (audit mo-02): the two live ACs were never actually re-verifiable in this audit environment — `docker info` hangs indefinitely (no daemon) and `kind get clusters` returns empty, so `estate/driftwood/verify-reconcile.sh` (a LIVE-only beat in `estate/talk/verify-all.sh`) could not be run at all, not even to confirm a failure. Downgraded from `ready-for-agent` to `PARTIAL` rather than `done`, since two of four ACs are genuinely unproven, not merely unproven-here. Everything tree-checkable (scaffolding, idempotent scripts) holds.
