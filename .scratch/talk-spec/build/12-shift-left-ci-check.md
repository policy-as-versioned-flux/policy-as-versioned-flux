# 12 — Shift-left CI ±1 check

**What to build:** CI resolves the target's supported version window (±1 skew off the ResourceSet array) and runs the target version's real `kyverno apply` offline, so an Audit→Deny flip is caught before merge.

**Blocked by:** 03

**Status:** ready-for-agent

- [ ] CI reads the version array (±1 skew) and runs `kyverno apply` for the target version offline
- [ ] An Audit→Deny flip fails CI pre-merge; a compliant change passes
