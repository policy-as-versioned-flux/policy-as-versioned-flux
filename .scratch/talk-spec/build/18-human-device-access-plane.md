# 18 — Human + device access plane

**What to build:** Pomerium Core in front of the cluster API consumes estate OIDC + enforces phishing-resistant WebAuthn; SPIRE `tpm_devid` issues a device SPIFFE ID on the same root; the Mac Secure-Enclave key is the live genuine hardware root. (Not Teleport — Enterprise-only Device Trust/OIDC.)

**Blocked by:** 14

**Status:** ready-for-agent

- [ ] Pomerium Core proxies cluster-API access via estate OIDC + WebAuthn
- [ ] SPIRE `tpm_devid` issues a device SVID on the same root; Mac Secure-Enclave key bound
- [ ] Access requires a valid device SVID + WebAuthn
