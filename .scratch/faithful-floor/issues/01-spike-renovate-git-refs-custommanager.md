# 01 — Spike: Renovate git-refs customManager vs the nested {version, commit} array

**What to build:** A throwaway proof (same spirit as the C2P spike) that a single Renovate `customManager` using the git-refs datasource (`currentValue` = tag, `currentDigest` = resolved commit SHA) can maintain the fleet's nested `{version, commit}` array inside a ResourceSet input, and a consumer's flat `{tag, commit}` pin pair. Retires the last named risk in PRD §10 before P1 work depends on it.

**Blocked by:** None — can start immediately.

**Status:** ready-for-agent

- [x] A Renovate dry run against a fixture repo detects a new upstream tag and produces a PR bumping both the tag and the resolved SHA in the nested-array shape from PRD §6.4
- [x] The same customManager config also bumps a consumer-style flat `{tag, commit}` pin
- [x] Findings written up (working config or the fallback shape if the nested array defeats Renovate), spike marked retired

## Comments

Retired 2026-07-14. `spikes/renovate-git-refs-customManager/` — one `customManagers` regex entry
(git-refs datasource) correctly bumps both the flat consumer pin and the nested `{version,commit}`
array shape from a real local git fixture. No fallback shape needed. See the spike's README.md for
the full write-up. `./run.sh` is the runnable proof.
