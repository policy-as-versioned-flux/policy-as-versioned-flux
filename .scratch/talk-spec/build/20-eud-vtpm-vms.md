# 20 — Windows/Linux EUD vTPM VMs

**What to build:** UTM Windows 11 + Linux VMs with vTPM enrolled; Windows Hello for Business + `tpm_devid` → device SVID. Narrated as virtual (emulated EK; genuine on real fleet hardware — the point carries).

**Blocked by:** 18

**Status:** ready-for-agent

- [ ] A UTM Windows 11 (vTPM) VM and a Linux (vTPM) VM enroll device SVIDs via `tpm_devid`
- [ ] Windows Hello for Business demonstrated; access gated on the device SVID
- [ ] Runbook narrates the emulated-EK caveat honestly
