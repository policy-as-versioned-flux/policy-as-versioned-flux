# 24 — Provenance end-to-end (every actor)

**What to build:** Every actor — commit (gitsign), workload (SPIFFE), human (OIDC/gitsign), device (`tpm_devid`/enclave) — attestable to one root. `verify-provenance.sh` walks feed→scenario→PR→merge→release and the runtime identities in Rekor/SPIRE.

**Blocked by:** 15, 18, 22

**Status:** ready-for-agent

- [ ] `verify-provenance.sh` verifies a commit/PR in Rekor and a workload + device SVID against SPIRE
- [ ] The chain feed→scenario→PR→review→merge→release is verifiable end to end
- [ ] It names which actor (AI or human) proposed what, when, from which evidence
