# 05 — The proposer

Type: grilling
Status: resolved
Blocked by: none

Graduated from the map's Not yet specified: "The proposer." Ticket
[`01`](01-does-composition-hold-up.md)'s prototype prints a proposed tier when a feed re-prices a
cage. Nothing raises the PR from that proposal, and the map's standing preference is clear that a
feed may re-price but never apply: every resulting change must land as a reviewed PR.

## Question

What raises the PR for a proposed tier change, and where does it run? `docs/adr/0007` says the agent
layer prompts editorial review and never edits enforcement directly, so what shape does the proposer
take within that constraint?

## Answer

**A proposer already exists. The adopter runs it, and it now opens the PR.** Recorded as
[ADR-0015](../../../docs/adr/0015-adopter-runs-the-proposer-and-it-opens-the-pr.md) and a new
**Proposer** term in `CONTEXT.md`, which also amends **Agent governance layer**.

### The premise was half wrong

Four facts changed the question before any decision was taken.

1. **A proposer exists.** `platform/wargamer/wargamer.py` is "the governance-agent evolved into a
   war-gaming policy-PR proposer". `platform/honesty/proposer_bounds.py` bounds it with a confidence
   floor, a rate limit and a rejection ledger keyed `<org>/<control>`.
   `platform/risk/appetite.json` already prices the apparatus on a bounded proposer being mandatory.
2. **It stops one step short, on purpose.** `platform/wargamer/propose-policy-pr.sh` renders the diff
   and prints the branch name. It never commits, pushes or opens the PR.
   `driftwood/scripts/bump-nist-pin.sh` uses the same rail.
3. **The proposed tier has no committed home.** No adopter repo sets `posture.acme.io/tier`. The
   `cage-tier` MutatingPolicy defaults it with `.orValue('baseline')`. Every real workload in the
   estate is `baseline` by omission, so a PR had no line to change.
4. **The estate runs no clock.** Every workflow in all six repos is push or `workflow_dispatch`.
   `renovate-run.yml` records that a recurring schedule is a standing decision the estate declined to
   make unilaterally.

So the missing piece was never the proposer. It was the last step and the target line.

### What was decided

| Question | Answer |
| --- | --- |
| Which proposer | The war-gamer, with a third drift row. No second proposer. |
| What the PR diffs | `posture.acme.io/tier` on the adopter's workload manifest. |
| Where it runs | The adopter's own repo, on that repo's own `GITHUB_TOKEN`. |
| Which subjects | The adopter's committed workload manifests, bounded by governed namespace. |
| What starts a run | A merged Renovate pin bump, or `workflow_dispatch`. Never a clock. |
| Does it open the PR | Yes. It still exposes no `merge()` and no `approve()`. |
| Which direction | Both. Tighter and looser. |
| Which bound | The computed materiality, the same one an enforcement flip uses. |
| Signing | Unsigned. The floor is the signed release tag, not every commit. |
| A second run | Force-push the same branch. The branch name is the dedupe key. |
| Version bump | None. A workload manifest is not the policy artefact. |

### Why the adopter runs it, and not `platform`

A `platform` workflow's `GITHUB_TOKEN` cannot open a PR in another org's repo. The only alternative
is a cross-org credential. ADR-0007's second correction records that no scoped GitHub App or token
was ever set up, and that every write in this estate runs on one full-access personal `gh` auth. The
estate should not invent that credential for this.

Inverting it removes the problem instead of solving it. The adopter already pins `platform`, so it
calls the war-gamer as a pinned dependency. That is the composition model doing the work. ADR-0013
already made selection the risk-bearing act, so the risk-bearer proposes against itself.

### The sixth gap: a proposed Deny inverts on merge

`select_tier` returns `"deny"`, but `TIERS` holds only `baseline`, `restricted` and `quarantine`.
The `cage-tier` MutatingPolicy coerces any other label value to `baseline`:

```
variables.rawTier in ['baseline', 'restricted', 'quarantine'] ? variables.rawTier : 'baseline'
```

So a merged `posture.acme.io/tier: deny` label makes the workload the **loosest** it can be. The
proposal inverts, in silence, at the moment a human approves it.

The proposer therefore opens an **issue** for a Deny, not a tier PR. A Deny is not a tier change. It
means the workload should not admit at all, which is a `ValidatingPolicy` decision. The coercion
itself is a `platform` defect, and this map names it rather than repairs it.

### Named residuals

- **The EOL feed re-prices with no commit.** `feeds/to_fair_scenario.py` ramps LEF by how far
  `--as-of` sits past `eol_date`. No push follows, so no run starts. An EOL drift waits for a pin
  bump or a manual dispatch. Closing this needs a recurring schedule, which is the estate's standing
  decision and not this map's.
- **The estate now has two rails.** The two demonstrator scripts still stop at the diff. This
  proposer does not. Neither generalises to the other.
- **Adopters stop learning from each other's rejections.** Each keeps its own ledger. Nothing did
  the shared version before either.
- **`wargamer.py` overclaims today.** Its docstring says `propose-policy-pr.sh` stamps a gitsign
  identity at commit time. That script never commits. ADR-0015 corrects the claim in place.

### Honesty note

A plain read of `wargamer.py`, `proposer_bounds.py` and `propose-policy-pr.sh` finds facts 1 and 2.
A plain grep for `posture.acme.io/tier` finds fact 3, and reading the `cage-tier` policy next to
`cage.py` finds the Deny coercion. **None of this needed composition.** What composition contributed
is the reason the question was asked at all.
