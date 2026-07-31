# The Mac Secure Enclave = the live genuine hardware root

The demo presents on an Apple-Silicon Mac. It has **no TPM** — the Secure
Enclave is not IEEE-802.1AR / DevID-compatible, so it cannot mint a `tpm_devid`
SVID. That is fine, and it is the honest split the spec locks in:

| Actor / machine | Hardware root | Mechanism | Narrated as |
|---|---|---|---|
| **The presenting Mac** | **Secure Enclave** | WebAuthn passkey, enclave-bound, **unclonable** | **live, genuine hardware** |
| Windows EUD | vTPM (UTM/swtpm) | Windows Hello → `tpm_devid` → device SVID | virtual (genuine on real fleet HW) |
| Linux EUD | vTPM (UTM/swtpm) | `tpm_devid` → device SVID | virtual (genuine on real fleet HW) |

## Why the Mac's Secure-Enclave key is a *real* root, not a soft label

The WebAuthn credential Pomerium enrols is generated **inside** the Secure
Enclave. The private key never leaves it and cannot be exported or cloned — a
phishing page or a copied credential file gets you nothing, because the
signature can only be produced by *that* enclave with a user-presence gesture
(Touch ID). That is the phishing-resistance the break-glass beat relies on.

What it is **not**: a manufacturer-verified *device certificate*. WebAuthn's
default attestation conveyance is `none`, so this proves "an unclonable key
bound to this enclave", not "Apple attests this is device serial X". To claim
the stronger form you request attestation `direct` and verify the `apple`
statement against FIDO MDS. Say which one you're showing — the enclave-bound
key is honest either way; only the manufacturer-attestation claim needs MDS.

## The full device root, across the fleet

The strong, manufacturer-verified tier (`tpm_devid` → endorsement-cert chain →
proof-of-residency → device SVID on `acme.internal`) runs on the Windows/Linux
EUDs under UTM vTPM. The emulated EK means the *chain* is demo trust anchors,
but the **mechanism is identical** to real fleet hardware — swap the swtpm EK
roots for the manufacturers' DevID CA roots and the same config attests a real
laptop. That is the point the demo carries.

## Enrolment (venue steps, not run headless)

1. Bring up the plane: `estate/platform/access/up.sh` (needs the driftwood
   cluster + ticket-14 identity substrate already up).
2. On the Mac, browse to Pomerium's enrolment URL (`/.pomerium/webauthn`) and
   register the Secure-Enclave passkey (Touch ID).
3. On each UTM vTPM EUD, run the SPIRE agent with the `tpm_devid` node attestor;
   read the attested TPM fingerprint from the server log and paste it into
   `device-svid.yaml` (`selectors[0]`), then re-apply.
4. Verify the gate with `access.py`: an attested device + passkey reaches
   break-glass; drop either factor and watch it refuse / step up.

## Why this can't be fully verified in a headless CI run

Steps 2–3 need a human at a real Secure Enclave (Touch ID gesture) and a live
(v)TPM doing a proof-of-residency challenge — neither is automatable unattended.
The manifests, the attestor config, and the *decision logic* (`access.py`) are
all verified offline; the live hardware attestation is the one hardware-gated
step. `verify-access.sh` runs everything that does not need the enclave/TPM.
