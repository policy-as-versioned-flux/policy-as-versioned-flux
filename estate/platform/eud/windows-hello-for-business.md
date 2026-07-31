# Windows Hello for Business on the vTPM Windows 11 EUD — narrated honestly

**Ticket 20.** Demonstrates the Windows-side half of "device (EUD), same graded
posture" (spec: Enforcement gradient & three-actor identity). WHfB is the
*local* Windows sign-in gate (TPM-bound PIN/biometric) on the vTPM'd VM;
`tpm_devid` (below) is what turns that VM's TPM into an estate device SVID.
They compose but are not the same thing — don't conflate them on stage.

## What WHfB proves, on this VM

Windows Hello for Business provisions a TPM-bound asymmetric key pair per user:
the private key never leaves the TPM (here: the swtpm-emulated vTPM), sign-in
requires a local gesture (PIN, or biometric if the host passes one through),
and the key cannot be extracted or replayed off-box. That's genuine
TPM-key-non-exportability — the same shape of guarantee as the Mac's
Secure-Enclave WebAuthn key in `../access/device/secure-enclave.md`, on a
different actor (Windows local sign-in vs. a WebAuthn browser credential).

## Enrolment (venue steps — not run headless)

1. `build-vm.sh` prepares the disk + vTPM state (offline, this repo).
2. Boot the VM with the printed `qemu-system-x86_64` command (or import into
   UTM's GUI and enable "Trusted Platform Module" under System), install
   Windows 11, and let it discover the vTPM as a normal TPM 2.0 device
   (`tpm.msc` should show "Ready for use").
3. Join or hybrid-join the VM to the estate's directory (Dex serves OIDC for
   the estate; a full AD/Entra join is out of scope here — narrate this step,
   see the caveat below).
4. **Settings > Accounts > Sign-in options > Windows Hello** — enrol a PIN.
   `tpm.msc` / `certutil -tpminfo` confirms the WHfB key is TPM-resident.

## The gate this feeds: access on the device SVID, not WHfB alone

WHfB proves *who's signed in on this box*; it is **not** what the estate's
access gate (`../access/access.py`) checks. The gate checks the **device
SVID** — earned separately, by the VM's SPIRE agent attesting via `tpm_devid`
against the *same* vTPM WHfB just used (`tpm-devid-enroll.sh` in this
directory renders the `ClusterStaticEntry`, same pattern as ticket 18's
`operator-macbook-device`). A VM that has WHfB enrolled but has never
completed `tpm_devid` attestation has **no** device SVID and is refused any
tier-3 op by `access.py` — WHfB alone does not buy device trust in this
estate; it's local-sign-in hygiene on the same hardware root.

```bash
# same decision engine as the Mac beat, now with a Windows EUD's device SVID
../access/access.py decide break-glass --oidc --webauthn --device   # ALLOW  (device SVID present)
../access/access.py decide break-glass --oidc --webauthn            # DENY   (WHfB enrolled ≠ device SVID)
```

## The honest caveat (say this on stage)

The vTPM's endorsement key is **swtpm-emulated**, minted fresh the first time
the VM boots — it chains to no manufacturer CA. `tpm_devid`'s
`endorsement_ca_path` (`../access/device/spire-tpm-devid-values.yaml`) is
therefore pointed at swtpm's *self-signed* EK cert for this demo, not a real
TPM vendor root (Infineon/STMicro/Nuvoton). **The mechanism is identical** to
a real fleet laptop — WHfB's TPM-key-non-exportability and `tpm_devid`'s
proof-of-residency challenge both run for real against the vTPM — only the
*trust anchor* the server verifies against is a demo root instead of a
manufacturer root. Swap `devid_ca_path`/`endorsement_ca_path` for the real
manufacturer CAs and the same config attests a genuine fleet device. This
mirrors the Linux EUD exactly (see `vms/linux-vtpm.json`) and the Mac's honest
split in `../access/device/secure-enclave.md`.
