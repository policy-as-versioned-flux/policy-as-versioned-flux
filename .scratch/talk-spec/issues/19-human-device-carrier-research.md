# Research: human+device access carrier — is Teleport the mature best-in-class, or is there better?

Type: research
Status: resolved
Blocked by: 18

## Question

For the human+device projection of the policy (ticket 18), what is the **current (2026)
best-in-class, mature, genuinely-open** solution for identity-aware access to Kubernetes + infra with:
phishing-resistant human auth (WebAuthn/FIDO2/OIDC), **hardware-attested device trust / EUD posture**,
per-session RBAC, and session recording/audit for provenance?

Evaluate **Teleport** specifically — is it the leader, and critically **is Device Trust + Session
Recording in the OSS Community edition or Enterprise-only?** (If the device-attestation feature is
paywalled, Teleport-OSS may not deliver the demonstrable device-trust story — which changes the pick.)
Compare against the current field (Boundary, Pomerium, Cloudflare Access, Pritunl Zero, StrongDM,
Tailscale, Ory, osquery/Kolide/Fleet for device posture, WebAuthn device attestation, SPIFFE-for-
humans efforts). Recommend the pick + KinD wiring, honest about OSS/licensing caveats.

Output: cited findings at `research/18-human-device-access-carrier.md` with a verdict.

## Answer (2026-07-31) — resolved

**Teleport OSS = wrong pick.** **Device Trust is Enterprise-only** (verbatim in docs); OIDC/SAML SSO
connectors are **Enterprise-only** too (Community = GitHub-only) → Teleport OSS can't even consume the
estate OIDC. Session recording / per-session MFA / hardware-key touch *are* in Community. Community
binaries are also commercially restricted (<100 emp / <$10M rev, since v16) — no longer Apache.

**Recommended stack:** **Pomerium Core** (Apache-2.0) identity-aware proxy in front of the KinD API
server — consumes estate OIDC, enforces WebAuthn + enclave-bound device key. **Genuinely-attested
device trust:** SPIRE **`tpm_devid`** node attestor issues a **TPM-rooted SPIFFE ID to the laptop** —
hardware-real AND on the estate's *same SPIFFE root* (the "not a bolt-on" answer: workloads and the
operator's device share **one attestation root**). Software-rich but spoofable (labelled) posture:
Fleet/osquery (MIT). Optional Teleport OSS only if recorded-kubectl is wanted.

**Field:** Boundary = BSL (not OSS), no k8s session recording; Cloudflare/BeyondCorp/StrongDM/Twingate
= proprietary/SaaS; Tailscale control-plane proprietary, posture just re-reads 3rd-party MDM.

**Risks:** (1) strong attestation needs a **TPM — Apple Silicon has none** → strong tier from a Linux
VM w/ swtpm/vTPM (dents "my real laptop"). (2) WebAuthn ≠ hardware attestation by default (conveyance
`none`); Pomerium device identity ≈ "enclave/browser identity" — be precise. (3) No single OSS box
does device-attestation-over-OIDC *and* terminal session recording — Pomerium + optional Teleport OSS.
Full detail + citations: [`research/18-human-device-access-carrier.md`](../research/18-human-device-access-carrier.md).
