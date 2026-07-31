# platform/eud — the Windows/Linux vTPM End-User Devices

**Ticket 20.** Blocked by / builds on ticket 18 (`../access`): that ticket
wired the `tpm_devid` node attestor and the device-SVID gate onto ticket 14's
SPIRE root, using the operator's **Mac** as the live example — except the Mac
has no TPM, so ticket 18 could only narrate the Windows/Linux side. This
ticket builds it: two UTM vTPM VMs (Windows 11, Linux) that actually attest
via `tpm_devid` and earn a device SVID on the same `acme.internal` root.

## What's here

| Piece | File | Role |
|---|---|---|
| VM specs | `vms/windows11-vtpm.json`, `vms/linux-vtpm.json` | declarative source of truth: sizing + vTPM 2.0/swtpm config |
| Disk/vTPM prep | `build-vm.sh` | offline, idempotent: creates the qcow2 disk + swtpm state dir, prints the venue boot command |
| Enrolment template | `tpm-devid-enroll.sh` | renders a `ClusterStaticEntry` per EUD — same pattern as ticket 18's `operator-macbook-device`, parameterised |
| WHfB runbook | `windows-hello-for-business.md` | Windows Hello enrolment + why it is NOT the same thing as the device SVID gate |
| Bring-up | `up.sh` | idempotent offline prep + best-effort apply; prints the human/hardware venue steps |
| Verify | `verify-eud.sh` | offline asserts + best-effort live check |

## Why UTM, why vTPM, why "narrated as virtual"

The presenting Mac (Apple Silicon) has **no TPM** — the Secure Enclave is not
IEEE-802.1AR/DevID-compatible (see `../access/device/secure-enclave.md`), so
it cannot run `tpm_devid`. UTM (open-source, MIT, QEMU-based) gives two VMs a
software TPM 2.0 (`swtpm`) that behaves identically to a real TPM at the
protocol level — `tpm_devid`'s proof-of-residency challenge really runs,
WHfB's key really never leaves the (virtual) TPM. The one thing that differs
from a fleet laptop is the **endorsement key's trust anchor**: swtpm mints its
own self-signed EK on first boot, not a manufacturer-issued one. That is the
"emulated EK" caveat — narrated honestly everywhere in this directory, never
glossed over. Swap the EK/DevID CA paths in
`../access/device/spire-tpm-devid-values.yaml` for the real manufacturer roots
and the identical config attests genuine fleet hardware; **the mechanism
carries, only the anchor is a demo one.**

```mermaid
flowchart LR
  subgraph VM[UTM VM — Windows 11 or Linux]
    SWTPM[swtpm<br/>emulated TPM 2.0]
    WHFB[Windows Hello for Business<br/>local sign-in, TPM-bound key]
  end
  SWTPM -->|tpm_devid attest<br/>proof-of-residency| SPIRE[(SPIRE server<br/>acme.internal — ticket 14)]
  SPIRE -->|device SVID<br/>spiffe://…/device/…| GATE[access.py<br/>the graded gate — ticket 18]
  WHFB -.local sign-in only,.->|not consumed by the gate| GATE
```

## Run it

```bash
estate/driftwood/scripts/up.sh            # cluster + Flux
estate/platform/identity/up.sh            # SPIRE/Istio/OpenBao
estate/platform/access/up.sh              # Dex + Pomerium + tpm_devid attestor
estate/platform/eud/up.sh                 # disk/vTPM prep + SVID templates (offline)
estate/platform/eud/verify-eud.sh         # offline asserts (+ best-effort live)
```

`up.sh` never boots a VM or installs an OS — that's GUI/ISO-gated and cannot
run headless. It prepares everything that can run offline (disks, vTPM state,
enrolment templates) and prints the exact venue steps (boot command, WHfB
enrolment, reading the attested fingerprint off the SPIRE server log, applying
the real `ClusterStaticEntry`) — the same "offline prep + printed venue steps"
shape as ticket 18's `up.sh`/`secure-enclave.md`.

## Acceptance mapping

- **A UTM Windows 11 (vTPM) VM and a Linux (vTPM) VM enroll device SVIDs via
  `tpm_devid`.** VM specs + `build-vm.sh` build the vTPM-backed VMs;
  `tpm-devid-enroll.sh` renders the `ClusterStaticEntry` for each, on the same
  root as ticket 18's Mac entry (`verify-eud.sh` asserts this offline). Live
  attestation (real fingerprint) needs a running VM + live SPIRE server —
  venue step, printed by `up.sh`.
- **Windows Hello for Business demonstrated; access gated on the device
  SVID.** `windows-hello-for-business.md` — WHfB is enrolled on the VM's
  vTPM (genuine TPM-key-non-exportability), but the estate's access gate
  (`../access/access.py`, reused not re-implemented) checks the **device
  SVID**, not WHfB. `verify-eud.sh` asserts a WHfB-enrolled EUD with no device
  SVID is still refused break-glass.
- **Runbook narrates the emulated-EK caveat honestly.** Stated in this
  README, in both VM specs, and in `windows-hello-for-business.md`'s "honest
  caveat" section — every place a viewer might read only one file.

## Calibration knobs

- **VM sizing** (`vms/*.json`) — bump `memory_mib`/`cpu` if the venue laptop
  has headroom; the vTPM mechanism is unaffected by sizing.
- **`iso` paths** — placeholders; point at the actual Windows 11 / Linux
  installer ISOs at the venue (licensing/download is out of scope here).
- **EK/DevID trust anchors** — swtpm-emulated here; the real-fleet swap point
  is `../access/device/spire-tpm-devid-values.yaml`, unchanged by this ticket.
