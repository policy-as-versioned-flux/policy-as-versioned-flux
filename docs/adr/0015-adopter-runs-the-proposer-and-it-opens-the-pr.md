---
status: accepted
---

# The proposer: the adopter runs it, in its own repo, and it opens the PR

A cage tier is a priced verdict. When a feed re-prices a caged workload, the £ selects a different
tier. Nothing may apply that change on its own. ADR-0006 forbids a timed verdict change. ADR-0010
permits a timed proposal that a human must merge. This ADR says what raises that proposal, and where
it runs.

## What was already there

The estate already holds a proposer. `platform/wargamer/wargamer.py` war-games the signed feeds
against the deployed controls. `platform/honesty/proposer_bounds.py` bounds it with a confidence
floor, a rate limit and a rejection ledger. `platform/risk/appetite.json` prices the whole apparatus
on a bounded proposer being mandatory.

It stops one step short, on purpose. `platform/wargamer/propose-policy-pr.sh` renders the diff and
prints the branch name. It never commits, pushes or opens the PR.
`driftwood/scripts/bump-nist-pin.sh` uses the same rail.

## The decision

1. **The war-gamer is the proposer.** A cage-tier drift becomes a third drift row, next to the
   enforcement verdict flip and the TCoR move change. The estate gets no second proposer.
2. **The adopter runs it.** The proposer runs in the adopter's own repo, against the adopter's own
   composed artefact, on that repo's own `GITHUB_TOKEN`. The adopter calls the war-gamer through
   its pinned `platform` dependency.
3. **The PR edits `posture.acme.io/tier` on the adopter's workload manifest.** That is the label the
   `cage-tier` MutatingPolicy actually reads.
4. **The proposer scans the adopter's committed workload manifests.** The governed namespace is the
   scan boundary.
5. **A merged Renovate pin bump starts a run.** `workflow_dispatch` also starts one. No schedule
   runs anywhere.
6. **The proposer commits, pushes and opens the PR.** It still exposes no `merge()` and no
   `approve()`, which `proposer_bounds.py` asserts today.
7. **Proposals go both ways.** The proposer may propose a looser tier as well as a tighter one.

## Considered options

- **The adopter runs it, same-repo credential (chosen).** No new credential, no new trust
  relationship. It also puts the proposal where the risk sits. ADR-0013 already made selection the
  risk-bearing act.
- **`platform` runs it and opens PRs across orgs.** Rejected. A `platform` workflow's
  `GITHUB_TOKEN` cannot reach another org's repo. The only alternative is a cross-org credential.
  ADR-0007's second correction records that no scoped app or token was ever set up. The estate
  should not invent one for this.
- **Keep the stop-at-the-diff rail.** Rejected. A proposal that nobody opens is not a proposal, and
  the ticket would resolve to nothing. ADR-0010 already sanctions a machine-opened PR and names the
  two rails that make "a human must merge" real. `allow_auto_merge: false` sits at repo level. The
  `require-pr-gate` ruleset still applies.
- **Open an issue instead of a PR, as the ADR-0007 demonstrator does.** Rejected for the tier case.
  The demonstrator opens an issue because it has no diff to propose. A tier change has an exact
  diff, on an exact line.
- **A tighten-only proposer.** Rejected. It ratchets the estate toward deny and never recovers. A
  human merges either direction, so the safety story does not change.

## Consequences

- **The estate now has two rails, not one.** The two demonstrator scripts still stop at the diff.
  The tier proposer does not. A reader must not generalise either one to the other.
- **A proposed Deny never becomes a tier PR.** `select_tier` returns `deny`, but `TIERS` holds only
  `baseline`, `restricted` and `quarantine`. The `cage-tier` MutatingPolicy coerces any other label
  value to `baseline`, the loosest rung. So a merged `tier: deny` label would invert the proposal in
  silence. The proposer opens an issue for a Deny instead. **The coercion is a real `platform`
  defect and this map records it as a named gap.**
- **The EOL feed re-prices with no commit.** `feeds/to_fair_scenario.py` ramps LEF by how far
  `--as-of` sits past `eol_date`. No push follows, so no run starts. An EOL drift waits until a pin
  bump lands or a human dispatches a run. **This is a named blind spot, not a closed one.** Closing
  it needs a recurring schedule, and the estate has declined that standing decision on purpose.
- **Each adopter keeps its own rejection ledger.** `platform` holds no per-adopter state it cannot
  verify. The committed `platform/honesty/rejections.json` stays as the war-gamer's own fixture.
  Adopters do not learn from each other's rejections. Nothing did that before either.
- **The proposal commit is unsigned.** ADR-0001's floor is the signed release tag, and no ruleset
  requires signed commits. A proposal becomes an artefact when a human merges it and
  `cut-release.yml` cuts a signed tag. The existing `EXPECTED_IDENTITY_REGEXP` is unchanged, so the
  trust surface does not widen. `wargamer.py`'s docstring currently claims
  `propose-policy-pr.sh` stamps a gitsign identity at commit time. That script never commits, so the
  claim is corrected in place.
- **A tier drift uses the computed materiality**, the same band-relative measure an enforcement flip
  uses. The structural constant stays for move changes only. The `ponytail:` upgrade path in
  `proposer_bounds.py` stays unbuilt.
- **A second run updates the open PR.** The branch name that `propose()` already builds is the
  dedupe key. The proposer force-pushes the branch so the reviewer sees the current £. The rate
  limit stays as the flood guard for distinct subjects.
- **No version bump.** A workload manifest is not the policy artefact, so the release gate of
  ADR-0011 has nothing to compute. The word "proposal" means a different thing on the
  `computed-semver` map.
