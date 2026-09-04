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

Built 2026-09-04; three blocking review defects and five minors fixed the same day, then a second review's one blocking defect -- the party fold collapsed two named feeds from one publisher and could grade a loose Namespace bound -- and one minor, fixed the same day too (see the dated notes below). Map line: The proposer folds the party to its strictest priced tier and lands nothing looser, one check binds the enacted tier to the priced tier in the gate and in three shift-lefts that say SKIP with the reason until platform tags the rule and each adopter bumps its pin, and the proposal commit is gitsign-signed against a second, proposer-only identity regexp.

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
every floor, each laid out both as one publisher per line and as several named feeds from one
publisher of one kind in each order -- **2,610 cases** -- through both and refuses a disagreement (ADR-0021's
two-implementations guard, the same one `verify/pound-seam/` applies to the per-line `select()`).

Be exact about what that guard buys here, because it is weaker than the one on `select()`.
driftwood's `select_party` is a **transliteration** of `platform/wargamer`'s fold -- written from
it, line by line, not derived independently from the rule -- so 2,610 agreements prove **copy
fidelity**: the pinned package has not drifted from the rule it mirrors, and a change to either
that is not made to the other is caught. They are not two implementations reaching the same answer,
and this check would not catch a mistake made once in platform's fold and copied faithfully. The
per-line `select()` the pound-seam check compares *is* independent; this one is not, and the check
now says so in its own PASS line rather than letting the case count imply otherwise.

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

### Note, 2026-09-04: three blocking review defects and five minors, fixed

The spec review of PR 20 found three defects that would each have put a red or a false green on
something real. All three are fixed on this branch, red demonstrated first in every case.

**1. The hub check graded a could-not-look as observed-false.**
`verify/tier-binding/verify-tier-binding.sh` ran `tier_binding_estate.py selfcheck` *before*
establishing that this estate's platform checkout carries the rule, and that selfcheck asserted
unconditionally that `platform/shift-left/tier_binding.py` exists (it plants its estate around the
real platform tree, so it needs one). On the real `.estate-clone/` -- where platform still predates
this ticket until the owner pushes -- it therefore raised `AssertionError: the selfcheck needs a
platform checkout to copy the published rule from` and the wrapper printed `FAIL: ... no longer
bites` and **exited 1**. That is an unnamed red on the gate the moment this merges, and it says a
false thing: the planted case bites fine, the rule is simply not here yet. The `check` subcommand
already got this right and exited 3.

Fixed both ways the review offered. `check` runs **first** and its `SKIP` wins and returns
immediately; the selfcheck runs only where `check` could look, which is exactly where the rule
exists to plant against. And `selfcheck` no longer asserts: it takes `--estate-clone` and returns 3
with its own `SKIP:` line where the platform checkout carries no rule. The script also honours
`ESTATE_CLONE`, so it can be pointed at a tree of ticket worktrees.

- red, pre-fix script against the real estate clone: `AssertionError` + `FAIL: ...` + `EXIT=1`
- green, fixed script against the real estate clone: `SKIP: /Users/.../\.estate-clone/platform/shift-left/tier_binding.py is not in this platform checkout -- the binding rule is platform's to publish`, `EXIT=3`
- green, fixed script against the ticket-78 worktrees: `PASS: ...`, `EXIT=0`

**2. The adopters' new compose-check step would have failed file-not-found on the first PR.**
The step ran `python3 platform/shift-left/tier_binding.py`, but that job checks platform out at the
adopter's **pinned tag** (`ref: ${{ steps.pins.outputs.platform_tag }}`), and all three pin
`v2.0.1`, which does not carry the module. Every first pull request in driftwood, tuppence and
ludlow would have gone red on a missing file.

Fixed by making the step honest about the ordering rather than by hiding it: it tests for the
module, and where the pinned checkout does not carry it, prints `SKIP:` **with the reason and the
pinned tag** to the log and to the job summary and exits 0. The ordering it waits on -- platform
cuts a tag carrying the module, then each adopter bumps its pin -- is named in `## Waits on the
owner` above and in the workflow comment itself. Nothing is silent: a reader of the run sees the
step and sees why it could not look.

**3. The check read only the FIRST governed Namespace document in a manifest.**
`find_governed_namespaces()` guarded ambiguity across FILES; `governed_namespace_span()` stopped at
the first matching document. So a second governed Namespace in the *same* file, declared looser,
was invisible: the binding check read the first and passed, and `apply_tier_declaration()` rewrote
the first and left the second exactly as it was.

Fixed by counting **spans, not files**. `governed_namespace_spans()` (new) returns every governed
Namespace document; `find_governed_namespaces()` lists one entry per document, so `len(hits) > 1`
now means what all four call sites already read it to mean; `governed_namespace_span()`,
`declared_tier()` and `apply_tier_declaration()` raise `AmbiguousDeclaration` rather than answering
about the first of two. `tier_binding.check()` grades that **SKIP (exit 3)** with the file named and
`(N documents in it)` in the reason, and `tier_pr.run()` lands nothing and says the same. Planted
cases added at both seams, red first against the pre-fix code:

- `RED 3a two governed docs in one file -> (0, "OK: gitops/apps/namespace.yaml declares 'isolated'; ... bound")` -- a silent pass over a `baseline` second document
- `RED 3b apply_tier_declaration rewrote -> 1 of 2 documents`
- green: `tier_binding.py selfcheck` case 11 requires exit 3, `"2 governed Namespace declarations"` and `"2 documents in it"` in the reason; `tier_pr.py selfcheck` case 4f requires no branch, no PR, the same reason on the returned row, and `apply_tier_declaration` raising rather than half-writing

**Minors, same day.**

- **`set -uo pipefail` under `bash -e {0}`.** All three new steps read `status=${PIPESTATUS[0]}`
  after a pipeline, but GitHub runs a `run:` block as `bash -e {0}` and `set -uo pipefail` does not
  lift `-e`, so a non-zero exit aborted the step at the pipeline and the summary block and both
  `::error::` annotations were dead code. This is the identical defect driftwood's `twin-sweep.yml`
  documents from ticket 72 (run 33627910027). Fixed with `set +e` around the check and `set -e`
  after it, and the comment says why, pointing at the run that proved it.
- **`infra`.** Excluded from `LADDER`, but ADR-0022 gives a platform-role party the right to
  declare it -- so it graded as a missing instrument, a refusal of a legitimate declaration
  (`FAIL: missing instrument -- the Namespace declares tier 'infra', which is not on the ladder`).
  Decision below; recorded in the ADR note too.
- **The Answer's claim about `compose-check`.** It said the pound-seam red closes when the
  `compose-check` job recomposes on the pull request. It does not: that job recomposes into the
  checkout and exits 1 on drift, so the PR is refused, not fixed. Corrected in `## Waits on the
  owner` with what actually closes it.
- **`read_overlay_floor()`.** Its docstring said "the top-level `overlay:` block ->
  `  floor:`" but the regexp matched `floor:` at any depth under `overlay:`, so a nested decoy above
  the real floor won: `overlay: {restate: {defaults: {floor: baseline}}, floor: quarantine}` read as
  `baseline`, a looser floor than the party declared. The read now matches only a **direct child**
  of `overlay:` -- the indent of the block's own first key -- and a planted case covers both the
  decoy and an overlay with no floor of its own.
- **The 875 (now 2,610) agreements.** Said plainly above and in the check's own PASS line: they
  prove copy fidelity, not independence.

### Decisions added on review (delegated, ADR-0025)

9. **`infra` is a declaration this fold ranks, not a selection it can make, and it needs no role
   lookup.** `rank()` (new, in `wargamer.py` and mirrored in driftwood's package) is defined over
   `LADDER + ("infra",)`; a price naming `infra` and a floor declaring it are still refused.
   Reason: both readings of an `infra` label answer the two questions asked here identically. From
   a platform-role party the declaration stands and is tighter than any rung a price can select;
   from any other party ADR-0022 renders it `isolated`, which is `LADDER`'s own tightest rung. So
   nothing priced tightens it and nothing priced is looser than it either way, and reading
   `party.yaml`'s `roles:` to tell the two apart would buy no different verdict while adding a file
   read that can fail. If a future rule ever needs the two apart -- a *loosening* path would --
   that is the ticket that should add the role lookup, with a reason.
10. **Two governed Namespace documents is could-not-look (exit 3), not a refusal (exit 1).**
    Reason: it is a question about which document carries the party's tier, not an observation that
    either one is loose. The check has not seen a loosening; it has failed to read. ADR-0020's
    shape for that is SKIP with a named reason, and it matches what the check already did for two
    governed manifests in two files -- counting per document rather than per file makes the two
    cases one case instead of two different verdicts for the same ambiguity. The proposer's side is
    the same call it already made: land nothing, name the files.
11. **The adopter step skips loudly rather than being gated on the pin in YAML.** Reason: an
    `if:` condition on the pin would need the tag list at workflow-parse time and would make the
    step **disappear** from the run -- a check that is not there reads as a check that passed. A
    printed `SKIP:` with the pinned tag in it, in the log and in the job summary, is a
    could-not-look a reader can see. It costs one `[ -f ]` test and it deletes itself the day the
    pin moves.

### Note, 2026-09-04 (second review): the party fold collapsed two feeds from one publisher

The re-review found one blocking defect, and it was real. It is fixed, red first.

**What was wrong.** `platform/wargamer/wargamer.py:select_party_tier()` built a dict keyed
`f"{source}/{kind}"` and then folded the party out of *that dict's values*. ADR-0019 made `feed`
one kind carrying a `name`, composition's `_parent_key` identifies a feed by its NAME, and
`party/schema.json` puts no uniqueness constraint on `inherits[]` -- so two priced lines from one
publisher of one kind is a shape this estate's own model admits. Those two collapsed onto one key
and the LAST one won, not the strictest. `tier_binding.bind()` then computed `required` off the
collapsed set, so the binding check would grade a Namespace `bound` that is **looser than a real
priced line**: a false PASS on this ticket's central property.

**Red, before the fix.** Prices `[{ico,feed,penalty-schema,isolated}, {ico,feed,breach-register,
baseline}]` with `current='baseline'`:

    platform  select_party_tier: baseline True {'ico/feed': 'baseline'}
    driftwood select_party    : isolated False
    DISAGREE
    tier_binding.bind: {'bound': True, 'required': 'baseline', 'strictest_line': 'baseline'}

`bound: True` over a line that priced `isolated`. driftwood's package folds the tier VALUES, so the
two implementations already disagreed on this shape -- and the 1,050-case guard could not see it,
because `tier_binding_estate.py` synthesised a unique source `s0..sn` for every line.

**Green, after.** Same input: platform picks `isolated`, `held=False`, lines
`{'ico/feed/penalty-schema': 'isolated', 'ico/feed/breach-register': 'baseline'}`; the two folds
AGREE; `bind` returns `bound: False, required: 'isolated'`.

**The fix.**

- `select_party_tier()` now folds over the priced tiers **themselves** (a list built in the same
  loop), never over `lines`, which is only a display of them. A fold that reads a dict's values can
  always be made to drop a line; a fold over the values it was given cannot.
- `lines` is keyed by a new `_line_key()`: `source/kind/name` where the line carries a name, with a
  `#n` suffix as belt and braces for a document that repeats even that -- so no priced line can be
  silently missing from the sentence the check prints about what it folded.
- `tier_binding.py:bind()` needed no separate fix: it calls `select_party_tier()`, so the same
  correction reaches the gate, the three shift-lefts and the PR body.
- The guard now generates each combination in **both** layouts: one publisher per line (as before)
  and, wherever there is more than one line, that many named feeds from ONE publisher of one kind,
  in each order the lines can be composed in. Both orders matter:
  `combinations_with_replacement` emits tiers loosest-first, so a collapsing fold that keeps the
  LAST line keeps the strictest one and agrees **by accident** -- the first attempt at this guard
  passed against the broken fold for exactly that reason. Strictest-first is the layout that
  catches it. 1,050 cases -> 2,610.
- The PASS line now claims what the guard actually generates, in those words.
- Planted regression cases in both selfchecks (`wargamer.py` case 4 and `tier_binding.py` case 14):
  two named feeds from one publisher fold to the stricter of them in either order, every line
  survives into `lines`, and a document that repeats `source/kind/name` drops no line.

**Verified against the old fold.** With `wargamer.py` stashed back to the collapsing version, the
new guard prints `FAIL: driftwood: the two party folds disagree -- lines ['baseline',
'restricted'] laid out as one publisher, one kind, several named feeds, strictest first ...
platform/wargamer picks 'baseline' ... driftwood's own selection-policy v1.1.0 picks 'restricted'`.
With the fix restored it is `PASS ... in all 2610 cases`.

**Minor, fixed while here.** The signature-verification step's branch extractor in the three
adopters' `propose-tier.yml` (driftwood:242, tuppence:280, ludlow:290) did
`p.get("landed",{}).get("action")`. `_land()` sets `landed` to the STRING `"dry-run"` in dry-run
mode, and `.get` on a `str` raises `AttributeError` -- the step died instead of reporting there was
nothing to verify. It now tests `isinstance(p.get("landed"), dict)` first. `actionlint` clean on
all three.

### Decisions added on the second review (delegated, ADR-0025)

12. **The fold reads the tiers, and `lines` is only a display.** Reason: keying `lines` better
    (`source/kind/name`) fixes today's collapse, but any fold that reads a dict's values is one
    unmodelled field away from the same bug. Folding the list the caller passed in cannot lose a
    line whatever the key turns out to be, and the key is then free to be the most readable
    identity rather than a load-bearing one. Both were done: the fold is over the list, and the key
    identifies the line properly anyway, because the PR body and the gate's PASS sentence quote it
    to a human.
13. **`wargame_cage_tier()`'s `control` field, and so the proposal branch name, still collapses two
    lines from one publisher of one kind -- and is deliberately left alone.** `control` is
    `f"{source}-{kind}"`, the branch slug is built from it, and `tier_pr.py`'s dedupe key IS the
    branch name, so two drifting lines from one publisher would share a branch. Reason for leaving
    it: what such a proposal WRITES is the party's tier, which is party-level and identical for
    both rows, so the collision cannot loosen anything -- the two proposals differ only in which
    price their body names. Changing `control` would change every existing proposal branch name and
    orphan the derived rejection ledger's keys (ADR-0024), which is a migration with a cost and a
    reason of its own. Recorded under **Not done** rather than fixed silently.

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
  from tickets 38 and 69 into this branch, so it was not done. Named here rather than hidden.

  **Corrected 2026-09-04.** An earlier draft of this bullet said the red "closes when driftwood
  recomposes, which its own `compose-check` job does on the pull request that lands this". That is
  wrong, and it mattered: `compose-check` recomposes **into the runner's checkout** and then exits
  1 if the regenerated `composed/` differs from the committed copy. It does not commit anything.
  So the pull request carrying this change is **refused** by that job, not repaired by it. What
  actually closes the red is a commit: someone runs `python3 platform/compose/composition.py
  compose driftwood --estate-clone . --out driftwood` and commits the regenerated
  `composed/evidence.json` -- either on this branch before it merges, or as part of tickets 38 and
  69, which regenerate the same tree for their own reasons. Until one of those commits exists,
  driftwood's `shift-left.yml` fails on this change.

- **The ordering the tier-binding step depends on: a platform tag, then three pin bumps.** The new
  step in each adopter's `shift-left.yml` runs `tier_binding.py` out of the platform checkout **at
  that adopter's own pinned tag**. All three pin `v2.0.1` today, and `v2.0.1` does not carry
  `shift-left/tier_binding.py` (`git show v2.0.1:shift-left/` lists `ci-check.py`, `fixtures/`,
  `README.md`, `verify-shift-left.sh` and nothing else). Two things must happen, in this order,
  before the step can be a real check:
  1. platform cuts a release tag carrying `shift-left/tier_binding.py`;
  2. driftwood, tuppence and ludlow each bump `gitops/platform/platform-pin.yaml` to that tag.

  Both are the owner's: they are enactment pushes and a release. Until then the step prints
  `SKIP:` with that reason, in the log and in the job summary, and exits 0 -- it does not fail
  a pull request for a rule its own pin does not publish, and it does not pass silently as though
  it had looked. The hub's `verify/tier-binding/` is what grades the rule across the estate in the
  meantime, and it says `SKIP` for the same reason until the platform branch is pushed.

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
- The **`compose-check` step immediately above** the new one in all three `shift-left.yml` files
  has the same `set -uo pipefail`-under-`bash -e` defect the new steps had: its
  `status=${PIPESTATUS[0]}`, its summary block and its two `::error::` lines are dead code, so a
  composition refusal or a drift fails the step with no summary and no annotation. It is
  pre-existing (ticket 21 wrote it, ticket 18 wired it) and belongs to whichever ticket owns that
  job; fixing it here would widen this diff into a step this ticket does not otherwise touch.
  Named, not fixed.
- `platform/wargamer/verify-wargamer.sh` and `wargamer.py selfcheck` read sibling party
  directories (`platform/../driftwood/party.yaml`), so from a linked worktree they need the estate
  laid out beside the worktree. Sibling symlinks were made under the gitignored
  `.estate-clone/platform/.work/` to run them; on `.estate-clone/platform` itself, which is what
  the gate reads, the siblings are real and nothing is needed. Not a change to any repository.
- **`wargame_cage_tier()`'s `control` collapses two lines from one publisher of one kind**, and so
  do the proposal branch slug built from it and `tier_pr.py`'s dedupe key, which IS that branch
  name. Two drifting `ico/feed` lines would share one branch and one dedupe key. It cannot loosen
  anything -- the tier such a proposal writes is party-level and the same for both rows, so the two
  differ only in which price their body names -- and fixing it renames every proposal branch and
  orphans the derived rejection ledger's keys (ADR-0024). Named, decided (decision 13), not fixed
  here.
