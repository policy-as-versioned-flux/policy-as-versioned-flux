# 14 — Identity plane: SPIRE + Istio + OpenBao

**What to build:** SPIRE (with `spire-controller-manager`), Istio (SPIRE-integrated), and OpenBao stood up as inherited `platform` machinery — the runtime-identity + secret substrate. Extend ControlPlane's `getting-started-spire-openbao`.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] SPIRE + `spire-controller-manager` issuing SVIDs; Istio consuming SPIRE identity; OpenBao running
- [ ] mTLS between meshed workloads on SPIFFE identity
- [ ] Delivered as inherited platform machinery
