# 78 — The proposer can only tighten, the enacted tier is bound to the priced tier, and the proposal is signed

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Ticket 74 waits for the first real band crossing. The 2026-09-02 review found that when it comes, the proposer will loosen the cage. `tier_pr.apply_tier_declaration()` writes the proposed tier onto the governed Namespace unconditionally, and nothing under `platform/wargamer/` clamps tighten-only. The proposer fires per price line. Driftwood's only reachable crossing is its threat-register line moving baseline to restricted, which would stamp `restricted` over a namespace declared `isolated`, because the other two lines already select isolated. ADR-0022 says the cage mutation is tighten-only; the proposer is not.

Three builds, all before 74 may fire:

1. Selection over the party, not the line: the tier the proposer writes is the strictest `proposed_tier` across the party's `prices[]`, clamped to the declared `overlay.floor`, and never looser than the current declaration unless the party's aggregate residual justifies it and the PR body says so. Record the rule in the selection-policy package the adopter publishes, and bump its version.
2. One check binds the enacted tier to the priced tier: read `proposed_tier` from `composed/evidence.json` and `posture.acme.io/tier` from the governed Namespace manifest, and refuse a label looser than the strictest priced tier. Wire it into each adopter's shift-left and into the gate.
3. The proposal commit is gitsign-signed with the workflow's Actions identity (reversal 16): copy `twin-sweep.yml`'s gitsign block into `propose-tier.yml` on all three adopters, add `propose-tier.yml` to each adopter's expected-identity regexp, and delete the `"signed": True` literal in `wargamer.py` (ticket 76 item 6).

Done = a test plants a per-line crossing on a party already at isolated and asserts the proposer writes nothing looser; the binding check is in `talk/verify-all.sh`; the first real proposal commit verifies under gitsign against the adopter's own regexp.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R2. Findings: scope/F1 (skeptic's corrected form), twin-validity/TWIN-09, security/SS-08, principles/P5-3. Blocks ticket 74. Whether the selection compares one line or the summed retained residual to the band is pound-engine/PE-05 and Q4 in ticket 75; item 1 takes the strictest-line rule as the safe interim and says so.

## Answer

Built 2026-09-04. Map line: The proposer folds the party to its strictest priced tier and lands nothing looser, one check binds the enacted tier to the priced tier in three shift-lefts and the gate, and the proposal commit is gitsign-signed against a second, proposer-only identity regexp.

### 1. Selection over the party, not the price line

`wargamer.select_party_tier(prices, current, floor)` (new, `platform/wargamer/wargamer.py`) folds
`prices[]` to the **strictest** `proposed_tier` on the ladder
`baseline < restricted < quarantine < isolated`, clamps **up** to the declared `overlay.floor`, and
returns `held=True` when writing that tier would not tighten what the governed Namespace declares
today. An unpriced line (a premium) selects nothing. Any tier off the ladder -- in a line, in the
floor, or in the declaration -- raises, because a proposer that cannot tell tighter from looser must
not guess (ADR-0020).

`tier_pr.run()` now finds the governed Namespace **before** it war-games, reads the declaration off
it (`declared_tier()`, new) and the floor off `party.yaml` (`read_overlay_floor()`, new), folds once
for the party, and passes the selection into `wargame_cage_tier()`. `_propose_tier()` writes
`change.to = selection.tier` and keeps the line's own move beside it as `line_from`/`line_to` for the
body. `_land()` re-judges tighten-only against what `origin/<base>` declares at the moment of the
write, so a declaration that moved under the run cannot be loosened by it. A held proposal creates
no branch, no commit and no pull request, and says why on stderr and in the returned row.

driftwood's own package records the same rule: `selection-policy/selection_policy.py:select_party()`
at **VERSION 1.1.0** (PIN.yaml bumped with it, as its own comment requires). The hub's
`verify/tier-binding/` folds every combination of up to three line tiers x every declared tier x
every floor -- **875 cases** -- through both implementations and refuses a disagreement (ADR-0021's
two-implementations guard, the same one `verify/pound-seam/` applies to the per-line `select()`).

### 2. One check binds the enacted tier to the priced tier

`platform/shift-left/tier_binding.py` (new, stdlib only, `check` + `selfcheck`) reads
`proposed_tier` off every `prices[]` line of a composed `evidence.json` and `posture.acme.io/tier`
off the governed Namespace manifest -- found by its `governed: "true"` label, never by a path -- and
refuses a declaration looser than the strictest priced line clamped to the floor. Exit 0 bound, 1
refused, 3 could-not-look. It exists because the proposer only writes proposals: a hand edit to the
Namespace, or a merge that races a re-price, is what this catches.

Wired in three places:

- each adopter's `shift-left.yml` `compose-check` job, immediately after the step that proves the
  committed `composed/` matches a fresh recomposition, running through the pinned platform checkout;
- `platform/shift-left/verify-tier-binding.sh` (new), platform's own proof that the check bites;
- `verify/tier-binding/verify-tier-binding.sh` + `tier_binding_estate.py` (new, hub), which asks the
  question of every party committed in `.estate-clone/` and runs the two-implementation comparison.
  Discovered by `talk/verify-all.sh`'s own `find`.

All three adopters bind today: each declares `isolated` over a strictest priced line of `isolated`.

### 3. The proposal commit is signed, and its identity is a separate power

`propose-tier.yml` on driftwood, tuppence and ludlow now takes `id-token: write`, installs gitsign
**0.17.1 by sha256** (the same pinned block `twin-sweep.yml` uses -- binary + checksum, no
marketplace action), and configures `gpg.format=x509`, `gpg.x509.program=gitsign`,
`commit.gpgsign=true` repo-locally before running `tier_pr.py`, so the plain `git commit` the
proposer makes is signed by the workflow's own keyless Actions identity. The proposer's JSON is
tee'd to `$RUNNER_TEMP` (never into the repository -- the observation cage would rightly trip on
it), and a following step runs `gitsign verify` on every branch the run actually wrote, against
`EXPECTED_PROPOSAL_IDENTITY_REGEXP` and `EXPECTED_ISSUER`. `actionlint` is clean on all six edited
workflows, with no finding that was not already there.

The three `"signed": True` sites in `wargamer.py` are gone: the two literals in `propose()` and
`_propose_tier()`, and the `assert p["signed"] is True` in its selfcheck, which is now
`assert "signed" not in p`. `verify-wargamer.sh` greps for the literal returning, so it cannot come
back quietly (ticket 76 item 6, closed here).

The identity-regexp family across all six repositories now proves the two powers do not overlap.
platform, ico and nist (no proposer) reject a `propose-tier.yml` identity for a release tag.
driftwood, tuppence and ludlow do the same **and** exercise the new constant: it matches only
`propose-tier.yml@refs/heads/main`, and rejects `cut-release.yml`, `twin-sweep.yml`, a maintenance
branch, the `wargamer/retune-*` branch the proposal is written to, another adopter's proposer,
another repo, a smuggled prefix or suffix, and `githubXcom`.

### Test-first, red then green

- `tier_pr.selfcheck` case 4b (the ticket's stated done: a per-line crossing planted on a party
  already declared `isolated`). Against the pre-78 production code (`run()` not folding the party,
  `_land()` writing unconditionally) it fails with
  `AssertionError: ('a per-line crossing on a party declared isolated must be HELD, not landed',
  [{... 'landed': {'action': 'created', ...}}])` -- the proposer stamps `restricted` over
  `isolated`, exactly the defect. With the fold and the guard it passes, together with 4c
  (strictest line wins and the body says so), 4d (the floor clamps up) and 4e (the current tier is
  read off the Namespace, not off the line's `old_tier`).
- `verify-wargamer.sh` leg 3b against the pre-78 `wargamer.py`: `select_party_tier` does not exist.
  Leg 3c against it: `wargamer.py:200` and `:232` both match `"signed":\s*True`, which is the fail.
  Both green after.
- `tier_binding.py selfcheck`: ten planted cases, each of which must grade as it must, including the
  hand edit (`restricted` over a party whose worst line is `isolated`) and the off-ladder tier.
- `tier_binding_estate.py selfcheck`: a planted estate with a bound party, a loose one, a party with
  nothing composed, a selection package that folds the party differently, and one that publishes no
  party fold yet.

### Decisions (delegated, ADR-0025)

1. **Strictest single line, not summed retained residual** (PE-05 / ticket 75 Q4). The ticket states
   this as the safe interim and it is what shipped. Reason: a summed rule needs a residual the
   proposer does not compute and a decision about whose money is being summed; the strictest line is
   always at least as tight, so taking it cannot under-cage while the question is open. A summed rule
   slots into exactly one place -- `select_party_tier()`'s fold of `lines` to `strictest`, mirrored
   in the adopter package -- and the 1.1.0 bump is what makes that swap reviewable.
2. **No loosening path at all in this ticket.** The ticket's "unless the aggregate residual justifies
   it and the PR body says so" has no operational meaning yet: there is no aggregate residual and no
   body that argues one. Reason: half a loosening path is worse than none. A loosening today is a
   human edit to the Namespace, in the open, under the binding check -- which is where an unargued
   loosening belongs. Recorded in the ADR-0022 note as the decision, not an omission.
3. **The party fold lives in platform, and in driftwood's package only.** tuppence and ludlow publish
   no selection-policy package, and this ticket does not create one for them. Reason: the package
   exists (ADR-0021) so the party whose money is at risk owns the rule that spends it; minting two
   empty packages to hold a rule neither party has yet chosen would be ceremony. `select_party_tier`
   is platform's, pinned by all three; driftwood's `select_party` is the second implementation the
   guard needs, and one is enough for the guard to bite.
4. **The binding check lives in `platform/shift-left/`, beside `ci-check.py`, and reads the
   COMMITTED `composed/evidence.json`.** Reason: it is a pull-request check an adopter runs through
   its pin, which is exactly what `shift-left/` is; and the `compose-check` job has already failed
   the PR on any drift by the time this step runs, so the committed copy *is* the recomposed one.
5. **A second constant, `EXPECTED_PROPOSAL_IDENTITY_REGEXP`, not an alternation widened into
   `release.yml`'s `EXPECTED_IDENTITY_REGEXP`.** Reason: proposing a tighter cage and publishing a
   signed release are different powers. Widening the release regexp to
   `(cut-release|propose-tier)\.yml` would let a workflow that may only propose sign something that
   verifies as a release -- a bigger hole than the one this ticket closes. Each adopter's check now
   proves non-overlap in both directions.
6. **The proposal identity is anchored to `@refs/heads/main` only**, not `main|release/x.y.x`.
   Reason: `propose-tier.yml` fires on a schedule, a dispatch and a merged pin bump, all on the
   default branch; admitting a maintenance branch would widen the identity for no run that exists.
7. **A dated note on ADR-0022 rather than a new ADR.** Reason: ADR-0022 already decided tighten-only
   and the floor; this is the same decision reaching the thing that writes the declaration, not a
   new one. The note records the strictest-line interim, where a summed rule would slot in, and why
   loosening is unimplemented on purpose.
8. **The commit identity stays the existing `wargamer proposer` user.name/email.** Reason: gitsign's
   certificate is what is verified; the git author line is not a security claim, and changing it
   would move the dedupe/ledger shape for nothing.

## Waits on the owner

- **The eight enactment pushes.** Every change under `.estate-clone/` is committed on
  `ticket-78-the-proposer-can-only-tighten` in each unit's `.work/ticket-78` worktree and pushed
  nowhere: platform (`wargamer/`, `shift-left/`, the identity script), driftwood, tuppence, ludlow
  (`propose-tier.yml`, `shift-left.yml`, the identity scripts, driftwood's selection-policy), ico
  and nist (the identity scripts). The guard refuses these and the owner pushes them.
- **The live gitsign observation, which is the last third of "done".** "The first real proposal
  commit verifies under gitsign against the adopter's own regexp" cannot be produced locally at all:
  it needs `propose-tier.yml` to run in Actions with the OIDC identity after these branches merge,
  and a real band crossing (ticket 74). Nothing here fakes it. What is proved offline is that the
  regexp admits exactly the identity that run will present and nothing else, and that the workflow
  installs a checksummed gitsign, signs, and verifies. The observation itself is the owner's to
  trigger or wait for.
- **driftwood's recompose under selection-policy 1.1.0.** Bumping the version makes
  `verify/pound-seam/` say, truthfully, `driftwood: names selection policy ['1.0.0'], but
  driftwood/selection-policy/VERSION says '1.1.0'` -- the committed `composed/evidence.json` was
  made by 1.0.0. Regenerating `composed/` here would have dragged ~2,900 lines of unrelated drift
  from tickets 38 and 69 into this branch, so it was not done. It closes when driftwood recomposes,
  which its own `compose-check` job does on the pull request that lands this, and which tickets 38
  and 69 already require. Named here rather than hidden.

## Not done

- `verify/e2e/step3_band.py` and `verify-e2e-step3-price-crosses-band-pr-opens.sh` are untouched.
  The per-line-crossing-on-isolated case landed at the `tier_pr.selfcheck` seam instead, which is
  where the fold and the write actually live; the e2e harness belongs to ticket 74, which this
  ticket unblocks.
- driftwood's `scripts/verify-identity-regexp.sh` leg 1 (real `gitsign verify-tag` against real
  tags) cannot run from a linked git worktree -- `error resolving tag reference: reference not
  found` -- and fails there with this change **and** with it stashed. It is green on
  `.estate-clone/driftwood` itself, which is what the gate reads. Pre-existing, named, not
  introduced here.
