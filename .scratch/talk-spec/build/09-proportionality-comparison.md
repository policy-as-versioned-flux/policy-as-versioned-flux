# 09 — Proportionality comparison (the money shot)

**What to build:** The *same* control resolves to Audit in `driftwood` and Deny in `ludlow` because their £ differ — proportionality proven by comparison. The load-bearing live beat.

**Blocked by:** 07, 08

**Status:** ready-for-agent

- [ ] The same control (encrypt-at-rest / no-EOL-log4j) is Audit in `driftwood`, Deny in `ludlow`
- [ ] `verify-proportionality.sh` asserts the divergent verdicts and the £ that drives them
