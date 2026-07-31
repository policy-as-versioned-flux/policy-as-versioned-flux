# 04 — `nist` real OSCAL controls feed

**What to build:** The `nist` repo ships genuine 800-53 OSCAL controls; `driftwood` consumes them as a pinned, signed dependency, so a regulator change arrives as a reviewable PR.

**Blocked by:** 02

**Status:** ready-for-agent

- [ ] `nist` publishes real 800-53 OSCAL catalog, versioned + signed
- [ ] `driftwood` pins a specific signed version
- [ ] A version bump arrives as a reviewable PR
