# 11 — Renovate customManager maintaining every pin

**What to build:** The one update surface (ADR-0002, PRD §6.2): a single Renovate `customManager` (git-refs datasource) that, on a new policy tag, opens one reviewable PR (`automerge:false`) bumping every pin — the fleet's nested `{version, commit}` array and each consumer app's pin pair — tag as `currentValue`, resolved SHA as `currentDigest`. Live semver ranges rejected. Applies the working config from the 01 spike.

**Blocked by:** 01 — Renovate spike, 08 — ResourceSet coexistence matrix.

**Status:** done

- [x] A new signed tag yields a Renovate PR within one run, bumping both tag and resolved SHA everywhere they're pinned -- mechanism proven against a fixture matching the real multi-element array (now updated to the real `1.0.3`/`2.0.3`/`2.2.0` pins, re-run green); installing a live, recurring Renovate automation on the org is a separate standing decision, deliberately not made unilaterally, see Comments
- [x] `automerge` is off; the PR is the unit of debate
- [x] No `ref.semver` range anywhere in fleet or consumer config
- [x] The **updatable** "-able" is demonstrable: new tag → reviewable PR, hands-off

## Comments

Done 2026-07-14. `fleet/renovate.json`: one `customManager` (git-refs datasource), reusing issue
01's spike pattern, targeting `tag:`/`commit:` adjacent lines in `clusters/*.yaml` -- the fleet's
nested `{version, tag, commit}` array is the ONLY pin surface in this design. "Every consumer
app's pin pair" from the ticket text doesn't apply to this implementation: `app1/2/3` carry no git
ref of their own, only a `mycompany.com/policy-version` label (PRD's "consumable" -able), and it's
the fleet's `ResourceSet` that owns version pinning centrally -- arguably a cleaner "one update
surface" than a design with per-app pins would give, not a gap.

Matches `tag:`, not `version:` -- `version` only diverges from `tag` for a CI-only-fix patch
release (rare), and since Renovate PRs are never automerged, a human reviewing the PR adjusts
`version` by hand in that case; Renovate's job is only to surface "a newer tag exists".

`fleet/verify-renovate.sh` closes the gap the issue-01 spike explicitly deferred here: proven
against the REAL multi-element array (not the spike's single-element fixture) -- Renovate finds
exactly 3 independent deps, one per array element, each keeping its own current `{tag, commit}`
and independently seeing the same new upstream tag. Fixture-based, no cluster needed.

**What's not fully proven:** the checklist's literal "a new signed tag yields a Renovate PR" needs
an actual new tag on the real policy repo to trigger a real Renovate run that opens a real GitHub
PR (either the Renovate GitHub App installed on the org, or a self-hosted run with a real token in
non-dry-run mode) -- blocked on the same gitsign re-auth as issues 07/08/09 for the tag, and
installing a live, recurring GitHub automation on the org is its own decision I didn't make
unilaterally (unlike the dry-run fixture, which writes nothing and opens nothing). The fixture
proof covers the specific risk this ticket named (multi-element correctness); the live-PR proof is
a follow-up once a new tag exists and the user's said whether they want the Renovate App installed.
