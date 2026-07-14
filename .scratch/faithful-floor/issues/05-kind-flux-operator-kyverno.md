# 05 — KiND + FluxInstance + Kyverno engine running

**What to build:** The reproducible runtime floor: a KiND cluster stood up from the fleet config via Flux Operator (`FluxInstance`, ADR-0005) with the Kyverno engine (≥1.18, ADR-0003) installed by a pinned `HelmRelease` and healthy. `wait` + CEL health checks, no jsonpath polling. Anyone can recreate it for free (CONTEXT proof posture). The engine HelmRelease pin is a governed dependency like policy itself.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] One documented command sequence takes a laptop from nothing to a KiND cluster with Flux Operator and Kyverno healthy
- [x] Kyverno installed via a pinned HelmRelease; readiness gated by `wait`/health checks, not polling
- [x] Tear-down and re-create is clean and repeatable

## Comments

Done 2026-07-14. `fleet/` — `flux-instance.yaml` (FluxInstance, pinned Flux `2.9.2`,
`upstream-alpine`), `infrastructure/kyverno/` (Namespace + HelmRepository + HelmRelease, pinned
chart `3.8.2` == Kyverno `v1.18.2`). `fleet/up.sh`/`down.sh` are the one documented command sequence
(native `kubectl wait --for=condition=Ready` throughout, no jsonpath polling); verified live on a
KiND cluster `cluster1`, including a full teardown + clean recreate.
