# Human & device identity — completing the zero-trust actor picture

Type: grilling
Status: resolved
Blocked by: None (extends 16)

## Question

Posture-as-identity (ticket 16) covered *workloads*. Where does **human identity** fit, and fold in
**EUD (End User Device) handling** for the whole picture. The frame: **posture-as-identity was never
workload-specific — it generalises to three actor classes, workload · human · device, all under one
policy**, all proportional, all attestable, all in provenance.

- **Human identity** — the supply-chain half is *already real*: gitsign keyless binds every commit/PR
  to a verified human OIDC identity → Rekor. The missing half is **operational access**
  (kubectl / dashboards / break-glass): OIDC/SSO + phishing-resistant **WebAuthn/FIDO2**, gated
  proportionally — a risky op (break-glass, prod deploy, `ludlow` patient data) demands higher
  identity assurance than a low-risk read.
- **EUD / device posture** — the *same shape as workload posture*: a device carries currency /
  attestation (TPM / hardware-root, MDM-compliant, patched, EDR present); access is gated **by
  degree** — compliant device → full; stale / unmanaged → **caged** (read-only, scoped-down,
  session-recorded, step-up auth) or denied. A device behind on patching **is** a workload behind on
  patching — same graded model, same £.
- **Carrier candidate** — an identity-aware access proxy with device trust: **Teleport** (TPM-attested
  device certs + identity + k8s/CLI/DB access + session recording/audit; OSS) as the **human/device
  twin of SPIRE-for-workloads**.
- **Closes "provenance for every actor"** — commits (gitsign) + workloads (SPIFFE) + humans
  (OIDC/gitsign) + devices (attestation): *every* actor. War-gamer now wargames human/device attack
  paths (phishing, stolen laptop, insider). TCoR absorbs human/device loss-frequency + the controls.

**To decide:** the access carrier (Teleport vs lighter OIDC-proxy); demonstrable-core vs narrated
(gitsign human-provenance is real; Teleport device-trust real-ish on the demo laptop; fleet MDM/EDR
narrated); how human identity + device posture plug into the policy's proportionality + £; break-glass
handling. Reopens the map; build-ticket publish stays paused.

## Carrier — research verdict (ticket 19, 2026-07-31)

**Pivot off Teleport** (Device Trust + OIDC both Enterprise-only). **Recommended: Pomerium Core
(OIDC + WebAuthn) + SPIRE `tpm_devid` node attestor** → the operator's laptop gets a TPM-rooted
**SPIFFE ID on the estate's same root**. Human/device and workload identity then share **one
attestation root** — more consistent with "it's all the policy" than a Teleport bolt-on would've been.
**Awaiting:** human confirm + the Mac/TPM fidelity call (Apple Silicon = no TPM → strong tier needs a
Linux VM w/ vTPM, or lead with the Secure-Enclave WebAuthn key live + narrate TPM).

## Rig decision + per-OS EUD matrix (2026-07-31)

**Decision:** primary demo rig = the **Mac**; device tier = **Secure-Enclave WebAuthn key, live**
(real, hardware-*bound* "enclave identity"); the manufacturer-attested TPM tier is narrated (or shown
on real hardware — open below).

**Per-OS EUD device-attestation reality:**
- **macOS (Apple Silicon):** Secure Enclave, **no TPM** → live enclave-bound WebAuthn key; manufacturer-
  attested tier = **Apple Managed Device Attestation** (ACME + Secure Enclave, via MDM).
- **Windows:** **TPM 2.0 mandatory on Win11** → SPIRE `tpm_devid` + **Windows Hello for Business**
  (TPM-backed) = the *strongest native real-world* attestation story. Enterprise EUD majority.
- **Linux:** TPM 2.0 if present → SPIRE `tpm_devid` native.

**Honesty point (matters for "real not narrated"):** *genuine manufacturer-rooted* attestation needs
**real hardware with a real TPM** — a VM's swtpm/vTPM makes the *mechanism* real (TPM→DevID→SPIFFE) but
the endorsement key is **emulated, not manufacturer-signed**. So a VM demonstrates the wiring, not the
hardware root of trust.

**Open:** (a) add **one real TPM machine** (a cheap Win11 laptop, or any TPM-equipped Linux box) to
make the manufacturer-attested tier *live* — it doubles as the Windows EUD and covers Linux too (same
`tpm_devid` mechanism); or (b) narrate the TPM tier, keep the demo Mac-only. A focused research pass
on SPIRE-`tpm_devid`-on-Windows + Apple-Silicon-vTPM fidelity + Apple Managed Device Attestation +
Windows Hello/Entra would lock the logistics before any hardware spend.

## Answer (2026-07-31) — resolved

Posture-as-identity generalises to **three actor classes — workload · human · device — under one
policy**, on one attestation root (SPIFFE + gitsign/Rekor).

- **Human identity:** supply chain already real via **gitsign keyless** (commit/PR → verified OIDC
  identity → Rekor). Operational access (kubectl / dashboards / break-glass) via **Pomerium Core**
  (Apache-2.0 identity-aware proxy) consuming estate OIDC + phishing-resistant **WebAuthn**, gated
  proportionally (risky op → higher assurance).
- **Device / EUD:** same graded posture as workloads. Carrier = **SPIRE `tpm_devid`** issuing device
  SPIFFE IDs on the estate's *same* SPIRE root (no bolt-on). **Mac Secure-Enclave WebAuthn key = the
  genuine live hardware root** (unclonable). **Windows + Linux EUDs built + demoed via UTM vTPM VMs**
  — full mechanism (Windows Hello, `tpm_devid` → SPIFFE) — **narrated as virtual** (emulated EK; on
  real fleet hardware the EK is manufacturer-signed; the point carries). No extra hardware → keeps the
  touring "runs on my laptop" requirement. Fleet/osquery (MIT) = optional richer, honestly-spoofable
  software posture.
- **Carrier is NOT Teleport** — Device Trust + OIDC connectors are Enterprise-only (ticket 19).
- **Closes "provenance for every actor":** commits (gitsign) + workloads (SPIFFE) + humans
  (OIDC/gitsign) + devices (`tpm_devid`/enclave) — *every* actor. War-gamer wargames phishing /
  stolen-laptop / insider; TCoR absorbs human/device loss-frequency + the controls.
- **Build delta:** Pomerium + SPIRE `tpm_devid` access plane; posture-gated human-access beat; UTM
  Windows/Linux vTPM demo VMs. Folds into the build-ticket set alongside the enforcement-gradient slices.
