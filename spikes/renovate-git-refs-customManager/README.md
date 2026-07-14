# Spike: Renovate git-refs `customManager` vs. the nested `{version, commit}` array

**Question (PRD §10, last named risk before P1).** Renovate's native `flux` manager tracks a
`GitRepository`'s tag *or* its commit, exclusively — it cannot maintain the `{tag, commit}` pair the
integrity model requires (ADR-0001). §6.2 proposes one `customManager` (git-refs datasource,
`currentValue` = tag, `currentDigest` = resolved commit SHA) for every pin. That pattern was
documented but never exercised against the exact **nested-array** shape the fleet's single
`ResourceSet` input carries (§6.4) — only against a flat consumer-style pin. Does it actually work?

**Verdict: YES.** Verified 2026-07-14 against Renovate `42.99.0`.

## What the spike shows

One `customManagers` regex entry, one `git-refs` datasource pointed at a real (local, tagged) git
fixture, bumps **both**:

| File | Shape | Result |
|---|---|---|
| `consumer-pin.yaml` | flat `spec.ref.{tag,commit}` (§6.1) | `1.0.0@<sha>` → `1.1.0@<sha>` ✓ |
| `fleet-resourceset-input.yaml` | nested `spec.defaultValues.policyVersions[].{version,commit}` (§6.4) | `1.0.0@<sha>` → `1.1.0@<sha>` ✓ |

The regex (`(?:version\|tag): ...\s*\n\s*commit: ...`) doesn't care how deep the match sits in the
YAML tree — it matches the two adjacent lines wherever they occur, so the nested-array element and
the flat pin are indistinguishable to the customManager. **One config, both shapes.**

### How it's proven
`run.sh` builds a real upstream git fixture (tagged `1.0.0`), pins a fleet fixture to it, lands a
*new* upstream tag `1.1.0` the fleet fixture doesn't know about yet, then runs Renovate with
`platform: local` (a dry run — it reports what update it would make without writing files or
opening a PR) against the fleet fixture. The verdict script parses Renovate's own debug-logged
`packageFiles with updates` for both files and asserts `currentValue`/`currentDigest`/`newValue`/
`newDigest` are all correct — i.e. it reads the exact diff content the real PR would carry, not just
"an update was found".

## Gotcha found along the way
Renovate's package cache is keyed on the git-refs `packageName` (the upstream path) and survives
across runs. Because the fixture mutates a repo at a fixed path each run, a stale cache serves the
*previous* run's resolved tag/SHA. Fixed with a fresh `RENOVATE_CACHE_DIR` per run — irrelevant to
production (a real Renovate run against a real Renovate app/CI job manages its own cache lifecycle
correctly; this only bites a fixture that reuses one path across repeated local runs).

## What's *not* proven (out of scope for this spike)
Multi-entry arrays (today's fixture has one `{version, commit}` element) — whether the regex
correctly targets only the intended element when the array holds several versions side by side is
exercised later, when issue 11 ("Renovate customManager maintaining every pin") wires this against
the real multi-version coexistence matrix.

## Consequence for the build
The `customManager` design in PRD §6.2 is sound as specified — no fallback shape needed. The risk
is retired; issue 11 can proceed directly with this pattern.

## Run it
```sh
./run.sh   # ~15s: fixture repos, new tag, Renovate dry run, asserts the verdict
```
Prereqs: git, node/npx, python3.
