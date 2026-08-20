# 20 — Windows/Linux EUD vTPM VMs

**What to build:** UTM Windows 11 + Linux VMs with vTPM enrolled; Windows Hello for Business + `tpm_devid` → device SVID. Narrated as virtual (emulated EK; genuine on real fleet hardware — the point carries).

**Blocked by:** 18

**Status:** PARTIAL — specs + enrolment templates built and offline-verified; no VM has actually been built or enrolled anywhere checkable

- [ ] A UTM Windows 11 (vTPM) VM and a Linux (vTPM) VM enroll device SVIDs via `tpm_devid` — **unmet as literally stated**: only the JSON specs (`estate/platform/eud/vms/{windows11,linux}-vtpm.json`) and the `tpm_devid` `ClusterStaticEntry` render templates exist and pass their offline checks (`bash estate/platform/eud/verify-eud.sh`); no UTM VM has actually been built or booted — `swtpm`/`utmctl` are not installed in this environment (`which swtpm utmctl` → not found) and the script's own output says so: `info swtpm NOT installed (venue prereq; offline checks above don't need it)`. `estate/platform/eud/vms/` holds only the two spec files, no disk images
- [ ] Windows Hello for Business demonstrated; access gated on the device SVID — **unmet as literally stated**: `windows-hello-for-business.md` is a runbook, not a demonstration; the offline check only proves "WHfB alone does not buy device trust" at the decision-logic level (`access.py` reused), not that WHfB was ever actually run on a VM
- [x] Runbook narrates the emulated-EK caveat honestly — same run: `windows11-vtpm.json: swtpm backend (emulated EK, named honestly)`, `windows11-vtpm.json: narrated as virtual` (and same for `linux-vtpm.json`)

## Comments

- 2026-08-20 (audit mo-02): the "verified" gap here is real, not just an environment limit — `build-vm.sh`'s own offline check explicitly stops at "dry structure check, no boot"; the venue tools (`swtpm`, `utmctl`) that would actually build and boot a VM are absent, and nothing in the tree shows evidence one was ever built (`estate/platform/eud/vms/` holds only the two JSON specs). This is the ticket the master audit (`.scratch/multi-org-estate/issues/02-tracker-status-audit.md`) was looking for: `ready-for-agent` was actively misleading — genuine offline scaffolding exists (specs + `tpm_devid` templates + honest narration), but the ticket's headline claim (an actual VM enrolling an actual device SVID) has never been exercised anywhere checkable. Downgraded to `PARTIAL` with 1 of 3 ACs met.
