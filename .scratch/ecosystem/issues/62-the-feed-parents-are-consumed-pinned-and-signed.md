# 62 — The feed parents are consumed pinned and signed

Type: task (AFK)
Status: resolved (the done clause's citable green run waits on the owner's three adopter releases -- see ticket 77's Waits item 1)
Blocked by: 57

## Question

Every adopter's CI checks out ico at ref: main and feeds/insurer at ref: ecosystem/thin-slice — unpinned, unsigned consumption against §2's own definition. Move every parent checkout to the tag+commit pair party.yaml declares (ico to v3.0.0 now; feeds and insurer once ticket 57 cuts their first tags); add ico's Flux pin per GAPS 1.6; and add a verifier that refuses branch refs in composing jobs so the gate catches regression. Done = verify-feed-contract passes on a citable run (unblocked by ticket 54's jsonschema fix) and the new branch-ref check is green.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M10 (unpinned feed parents).
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-01 (from ticket 60's clock watch): the defect now fails hard, not just unpinned.**
The `ecosystem/thin-slice` branch no longer exists on feeds, so every checkout that names it
dies at fetch. First observed live: tuppence propose-tier's first scheduled firing (13:42Z)
failed with "A branch or tag with the name 'ecosystem/thin-slice' could not be found". Twelve
checkouts carry the ref: tuppence and ludlow × {shift-left.yml, propose-tier.yml,
cut-release.yml} × {feeds, insurer}. Until this ticket lands, tuppence and ludlow cannot
propose, shift-left or cut a release — their step-3 path is dead on the clock, not merely
unsigned. Driftwood was re-pinned by ticket 61 and is unaffected. Note for the fix: feeds now
carries real tags (threat-register/v1.0.0, v2.0.0), so the feeds half no longer waits on
ticket 57; the insurer half still does.

**2026-09-02, review.** Confirmed live 2026-09-02: twelve `ecosystem/thin-slice` refs across tuppence and ludlow ({propose-tier, shift-left, cut-release} × {feeds, insurer}); both adopters' scheduled propose-tier runs died at checkout on 2026-09-01 and 2026-09-02. Two additions from the review: driftwood consumes ico, feeds and insurer at `ref: main` in nine places with no Flux source, and ico, insurer and feeds `release.yml` check platform out with no ref. Ticket 77 carries those with the shared content-of-pin check; land the twelve refs together with it. Record: REVIEW-2026-09-02.md R4.

## Answer

Built 2026-09-04 on one hub branch with ticket 77: the reader review found the two share
`gotk-sync-ico.yaml`, the propose-tier/shift-left/cut-release parent refs, `feed_contract.py`
and the tree-contains-section refusal.

**What was built.** Every cross-organisation checkout in driftwood, tuppence and ludlow now
names a tag one of that repository's own pin files declares. The twelve dead
`ecosystem/thin-slice` refs and every `ref: main` are gone; ticket 77 item 5's nine driftwood
refs went with them, as the 2026-09-02 review asked.

* Three new `{tag, commit}` pin files per adopter, in the `gotk-sync-nist.yaml` pattern
  (verified source, gates nothing): `gitops/flux-system/gotk-sync-ico.yaml` (v3.0.0 at
  9d09222), `gotk-sync-feeds.yaml` (tuppence and ludlow `threat-register/v1.0.0`, driftwood
  `threat-register/v2.0.0`, both at 69c89b0) and, on driftwood only, `gotk-sync-insurer.yaml`
  (v1.0.0 at 632db22). Each tag was resolved off the publisher's real remote and every pin in
  all three repositories was re-checked tag-by-tag against `git rev-list -n1 <tag>` before the
  workflows were wired to it -- thirteen pins, thirteen matches, so the new assertion below
  cannot break a job that works today.
* `read-two-pins.py` became `read-pins.py` and takes any number of (pin file, prefix) pairs;
  the nine composing jobs read four or five pins instead of two.
* A new `.github/scripts/verify-pinned-checkouts.py` per adopter, with `--selfcheck`, asserts
  the other half of each pair: the tree the runner actually got is the commit the pin names.
* `renovate.json` in each adopter gains a customManager per new pin, so the pairs are bumped
  the way the nist and platform pins already are.
* Hub: `verify/branch-refs/verify-branch-refs.sh` + `branch_refs.py` (selfcheck first, then
  the code), discovered by `talk/verify-all.sh`, with its line in `talk/verify-manifest.txt`.

**Which check grades it.** `verify/branch-refs/verify-branch-refs.sh` -- 53 PASS, 1 SKIP,
exit 3 (round 3, 2026-09-04; it read 50 PASS before the three insurer checkouts below were
made visible). The one could-not-look is driftwood's `twin-sweep.yml` consuming the HUB, which
has cut no tag for it to pin to; ticket 64 cuts it. All 52 `repository: policy-as-versioned`
lines in the eight units are graded. It grades `.github/workflows/*.yml` and `actions/checkout@`
steps only, and a `repository:` no literal matrix decides is a named could-not-look rather than
a grade; those three limits are stated in `branch_refs.py`'s docstring and on its manifest line,
and none of the three exists in the eight units today (checked 2026-09-04).
`verify/feed-contract/verify-feed-contract.sh` passes every ico and feeds pin by name and tree.

**This ticket's done clause is NOT met, and cannot be until the owner releases.** It reads
"verify-feed-contract passes on a citable run". It does not pass: it exits 3, on the three
insurer `<adopter> exposure v1.1.0` pins, because ticket 77's content rule reads those trees and
none carries an `exposure` section. That is a could-not-look and the honest reading -- the code
is right, a release is missing -- but it is not a pass, and saying otherwise would be the exact
fabrication ticket 77 exists to stop. The three adopter releases in ticket 77's Waits item 1 are
what closes it. Every ico, feeds, nist and platform pin this ticket moved does pass by name and
by tree.

### Decisions (all delegated, ADR-0025, 2026-09-04)

1. **`ref:` is the TAG, and a step asserts the commit.** `actions/checkout` takes one ref. A
   signature lives on a tag, so a SHA ref could not be verified as signed; pinning the tag and
   asserting `git rev-parse HEAD` against the pin's `commit` gives both halves. It reuses the
   shape driftwood's `propose-tier.yml` already had for platform, now uniform across all three
   adopters and all nine jobs.
2. **The pin lives in a GitRepository file, not in `party.yaml`.** `party.yaml` declares the
   pin by MAJOR (`v3`, `v1`, `v2`) because that is what ADR-0019's feed contract resolves; a
   workflow needs a concrete tag. Growing `inherits[]` a `tag:`/`commit:` field would put two
   versions of the same fact in one artefact and change the party schema. The estate already
   has one shape for "which signed version of X am I on" -- the GitRepository pin -- and
   Renovate already bumps that shape, so ico, feeds and insurer get it too.
3. **The verifier grades EVERY cross-org checkout in the eight units, not only composing
   jobs.** Ticket 77's done clause is the wider one and the narrower reading would have left
   the three `release.yml` platform checkouts ungraded, which is 77 item 4. (Corrected in
   round 3, 2026-09-04: as first built this said EVERY and graded 51 of the 52. The 52nd,
   insurer/fetch.yml's templated `repository:`, is graded now -- see the round-3 note below.)
4. **A computed `ref:` is not followed back to the step that set it.** A workflow expression
   is evaluated by GitHub, not by the checker; pretending to resolve it would be a guess. What
   is checkable offline is that the consuming repository declares a version of that publisher
   and that the declared tag is one the publisher signed. That is what is graded.
5. **The insurer checkout is REMOVED from tuppence's and ludlow's three composing jobs.**
   Neither party's `party.yaml` declares an insurer parent, so there is no pin to move the ref
   to and composition never reads the tree. Pinning it would have invented a dependency; the
   honest diff is to stop fetching it. (Residual, named not fixed: the insurer publishes
   `quote-tuppence` and `quote-ludlow` that nobody pins, so two of its three quotes reach no
   adopter's sheet. That is a party-artefact question, not a ref question.)
6. **Driftwood's insurer pin stays at v1.0.0** even though 77 item 2 shows that tag's tree
   lacks the exposure the insurer priced from. Whether a tag's TREE carries its section is
   ticket 77's content rule and is now graded by feed-contract; this ticket's job was to stop
   consuming a branch.
7. **The `gotk-sync-feeds.yaml` Renovate manager captures the semver, not the whole tag**
   (round 2, 2026-09-04). As first built it captured `threat-register/v2.0.0` as `currentValue`
   and gave it to `semver` versioning, which cannot parse it, so the one pin this ticket added
   that a per-feed publisher signs could never have been bumped -- a pin nothing maintains is
   how the estate got here. Rewritten in the shape each adopter's existing `party.yaml` feeds
   manager already uses: the feed prefix outside the capture group, so Renovate rewrites only
   the semver and the prefix survives, plus an `extractVersionTemplate` mapping the publisher's
   per-feed tags back onto it. Same fix in all three adopters, not only driftwood.

Map line: Tickets 62 and 77: every cross-org checkout in the eight units names a tag its own
repository pins, and a pinned tree is checked for the section the pin is used for.


### Round 2, 2026-09-04 -- review fixes recorded here

* `verify-branch-refs.sh` grades **50 PASS**, not the 49 this Answer and ticket 77's both
  claimed. Corrected above.
* The done clause is stated honestly above: `verify-feed-contract` exits 3 today and this ticket
  cannot close on its own terms until the owner's three adopter releases land.
* `branch_refs.py`'s two limits (the `*.yml` glob and the `actions/checkout@`-only rule) are
  written into its docstring and its manifest line, so a green run is not read as more than it
  is.
* The `gotk-sync-feeds.yaml` Renovate manager is fixed in driftwood, tuppence and ludlow
  (decision 7 above).
* Tuppence's and ludlow's `propose-tier.yml` and `shift-left.yml` still carried comments about
  fetching an insurer parent that decision 5 removed, quoting a refusal for a parent neither
  party declares. Rewritten to say what those jobs now do and why the insurer checkout is gone
  rather than pinned.
* Two blocking faults on the insurer -- a re-quote clock that would have refused for ever on an
  unreleased rule, and a release gate pinned to a platform tag whose party schema this party
  fails -- are recorded in ticket 77's Answer under **Round 2**, with the measurements.

### Round 3, 2026-09-04 -- review fixes recorded here

* **The blocking one: 51 of 52 cross-organisation checkouts were graded, and the 52nd was
  invisible.** `grade()` began `m = ORG.match(repo); if not m ... return`, and `ORG` cannot match
  a `repository:` that is itself a workflow expression. insurer/fetch.yml:305 is one --
  `policy-as-versioned-${{ matrix.adopter }}/${{ matrix.adopter }}`, over a matrix of driftwood,
  tuppence and ludlow -- so it returned before the seen-counter moved: not a PASS, not a FAIL,
  not a SKIP. Changing that step's `ref:` to `main` left the check green, which is exactly the
  regression it exists to catch. Counted by hand: 52 `repository: policy-as-versioned` lines
  across the eight units, all 52 cross-organisation, and the check graded 51.
* **Fixed by expanding the matrix, not by shrugging.** A templated `repository:` is expanded
  from the job's OWN `strategy.matrix` -- the values are written in the file; GitHub evaluates
  the expression but does not decide them -- and each expansion is graded like any other
  checkout. All 52 lines are graded now; 54 grade lines come out of them because the templated
  one is graded once per adopter. Where no literal matrix decides the name (a step output, an
  env var, an `include:` block), the checkout is COUNTED and SKIPped by name: could-not-look,
  never a pass and never silence. None exists in the estate today.
* **Proof the regression now bites**, run before and after on the real estate: with
  fetch.yml's `ref:` neutered to `main`, `verify-branch-refs.sh` exits 1 with
  `FAIL: insurer/fetch.yml checks out policy-as-versioned-driftwood/driftwood at 'main', which
  is not a tag driftwood has signed` (and the same for tuppence and ludlow). Restored after.
  Five selfcheck fixtures were written red first: a templated repository at a branch, at a tag,
  with no `ref:`, with a computed `ref:`, and one no matrix resolves. The selfcheck also asserts
  the seen-counter equals the number of planted checkouts, which is what proves nothing falls
  through again.
* **A third declared shape for a pin, needed by that expansion** (delegated, ADR-0025). The
  insurer declares which version of each adopter it is on in its own `party.yaml` `inherits[]`,
  which is the file `fetch.yml` reads to build the ref -- not in a GitRepository pin. So
  `party.yaml` is read as a declaration, but ONLY where neither `gitops/` nor a `<PUBLISHER>_TAG`
  env constant names that publisher: most `inherits[]` versions are ADR-0019 feed MAJORs (`v3`,
  `v2`, `2.0.1`) and not git tags, and reading them as tags everywhere would invent refusals.
  Scoped this way the fallback can only turn a FAIL into a grade, never a PASS into a FAIL.
* **Three limits, not two, and all four claims corrected.** `branch_refs.py`'s docstring, this
  ticket's decision 3, the manifest line and ADR-0019's note all said the check grades every
  cross-organisation checkout. They now say what it does and name the third limit: a
  `repository:` no literal matrix decides is a named could-not-look and not a grade.
* **Round 4: a matrix carrying `include:` was expanded anyway, and that was the round-3 defect
  wearing a new hat.** `expand_matrix()` read the literal lists and ignored `include:`, so a job
  written `adopter: [driftwood, tuppence]` plus `include: [- adopter: ludlow]` graded two legs
  and passed over the third in silence -- not graded, not counted, not skipped. The docstring
  already promised the opposite, so the promise was false as well. One guard fixes it: a matrix
  with `include:` or `exclude:` decides nothing here, because `include:` adds combinations and
  `exclude:` removes them. The step is counted and SKIPped by name instead. Proved red first --
  with the guard disabled the planted `p-matrix-include.yml` grades `PASS` and the selfcheck
  fails on it; with the guard it is a named could-not-look and the selfcheck passes. No workflow
  in the eight units carries `include:` or `exclude:` today (0 hits across 35 files), so no real
  checkout was ungraded. The estate count is unchanged at 53 PASS, 0 FAIL, 1 SKIP, exit 3.
* **`verify-branch-refs.sh --selfcheck` and `verify-feed-contract.sh --selfcheck` now do what
  their Answers say.** Both accepted the flag and silently ran the full estate check instead.
  Each runs its python selfcheck alone and prints one PASS or FAIL line.
* **The manifest row for `verify-feed-contract.sh` declared two of six could-not-look reasons.**
  `feed_contract.py` can print six, and `could not reach https://github.com/...` and
  `payload_schema is a URL (...); not fetched offline` were undeclared, so a network blip read as
  red. All six are declared now, and each script's reasons were re-judged one by one against the
  widened patterns. The wrapper's own missing-interpreter and missing-clone could-not-looks stay
  undeclared on purpose, the same call `verify-untagged-pin-is-priced.sh`'s row already records:
  a runner that has lost its venv or its clone should go red, not shrug.
* **The head-of-SKIP-list convention in both wrappers is untouched.** It is an inherited estate
  convention and the manifest's known-limit note (ticket 83 decision 3) already covers it.
* **The branch is NOT rebased on `origin/main`, deliberately** (delegated, ADR-0025). `main`
  moved to `13234b5` while this round ran, and the rebase itself was clean -- but the clock had
  meanwhile committed `7f61920 truth: record run 79` to this branch, an observation of
  `hub=5ee9e44` that `main` does not carry. Replaying it onto `main` conflicts in `talk/truth.log`
  and eleven capture files, and resolving that by hand would mean choosing which run's captures
  survive: a truth-record decision, not a builder's. Force-pushing over it would delete an
  observation, which a clock's record is never for. So round 3 was replayed on top of the clock's
  commit and pushed fast-forward -- nothing discarded, nothing rewritten. The integrator merges.
* `verify-branch-refs.sh` now grades **53 PASS and 1 SKIP** (the SKIP is unchanged: driftwood's
  `twin-sweep.yml` consuming the hub, which has cut no tag). The three new PASSes are the
  insurer's three adopter checkouts, which nothing graded before.

## Landed 2026-09-04

Hub pull request 24 merged as `pavc-other-hand`, merge commit `e127209`, a true merge commit and
not a squash. `5ee9e44` and `7f61920` are ancestors of `main`, so run 79's TRUTH line stays
citable and every `hub=` in `main`'s `talk/truth.log` is still reachable from `main`. The log
keeps runs 79, 80 and 81 in timestamp order; nothing was deleted. The eleven conflicting capture
files took `main`'s side, because those were the newer observations, and the next clock run
re-captures against the merged tree.

Six of the seven unit pull requests merged as `pavc-other-hand`: platform 11 (`bbda376`),
driftwood 24 (`cd63472`), tuppence 16 (`e44ad89`), ludlow 14 (`64492d3`), ico 4 (`6217c3a`),
feeds 3 (`b6eaa0a`).

**Two unit checks are red, and both are true statements about the estate rather than defects in
this change.** Neither is caused by this branch, and both were established by comparing `main`
against the branch, not assumed.

1. **driftwood `compose-check` fails, and it fails on `main` too.** `selection-policy/
   selection_policy.py` reads `VERSION = "1.1.0"` on both `main` and the branch, while
   `composed/HEADER.yaml` records `selection-policy: 1.0.0` on both. The composed artefact is
   stale against driftwood's own package. The branch changes neither file. This belongs to the
   re-compose pass in ticket 64.
2. **tuppence `shift-left` fails, and the branch is what made it able to fail.** On `main`,
   `shift-left.yml`'s first platform checkout carried NO `ref:`, so tuppence composed against
   platform's default branch. The branch pins it to the declared tag. Composing against the
   signed `v2.0.1` instead of platform's `main` produces a MAJOR bump for this institution, and
   the adopter gate refuses to adopt a major without human review, which is what it is for. So
   the pin did not break the gate. It revealed that tuppence's adopted composition had been built
   from an unpinned, unsigned default branch, and that the signed tag composes to something a
   major apart. That is the exact defect tickets 62 and 77 exist to find, found by the fix.
   Ticket 64 moves the pins and re-composes; the major bump needs the owner's review by design.

## Waits on the owner

* **insurer pull request 3 cannot be merged by the assistant.** GitHub refuses the merge API call:
  "refusing to allow a GitHub App to create or update workflow `.github/workflows/fetch.yml`
  without `workflows` permission". The `pavc-other-hand` installation carries
  `contents:write, metadata:read, pull_requests:write` on every organisation and `workflows` on
  none, on all nine. The refusal is NOT uniform, and the counts are exact rather than impressions.
  Five merges by the same app on the same day carried workflow changes and were admitted:
  driftwood `cd63472` (3 files), tuppence `e44ad89` (3), ludlow `64492d3` (3), ico `6217c3a` (1)
  and feeds `b6eaa0a` (1). Platform's `bbda376` carried none, so it proves nothing either way. The
  hub's own `fbdbc6d` also changed `.github/workflows/twin.yml` and was admitted. Insurer's
  installation is not older or differently configured: same three permissions, created within two
  minutes of feeds' on 2026-09-03. The REST merge endpoint refuses with the same message as the
  GraphQL one, so it is not an API-surface difference either. Why insurer alone refuses is not
  established, and no guess is recorded here.

  The fix is one owner action: grant the app the `workflows` permission. Merging with the owner's
  own token instead would defeat the point of the second identity, so it was not done, and neither
  was a local merge pushed straight to `main`. The pull request is open, mergeable and clean.
* The citable run: `verify-feed-contract` and `verify-branch-refs` green on a TRUTH line the
  owner or the clock produces. Both were run locally and their output is in the pull request.
  `verify-branch-refs` is green (53 PASS, 1 declared SKIP); `verify-feed-contract` is NOT, and
  cannot be until the three adopter releases in ticket 77's Waits item 1 exist. This ticket's
  done clause waits on that dispatch and on nothing this build can do.

## Correction, 2026-09-04 (eco-system ticket 64)

Item 2 of "Landed 2026-09-04" above says tuppence's `shift-left` red is one "the branch is what
made it able to fail", and that composing against the signed tag rather than platform's default
branch is what produced the major. **Both halves are wrong, and the runs say so.**

The identical failure, with the identical numbers, is in Actions run `33884942977` on branch
`ecosystem/build-2026-09-03`, which ran at 14:38 on 2026-09-04 — before this branch pinned the
checkout:

    FAIL: composed bump is major -- refusing to adopt v2.0.1 without human review
    declared (platform tag v2.0.1 -> v2.0.1): none
    composed (this institution, across ['4.0.0'] and retired []): major

and the same four lines are in run `33915621021` on `ticket-62-and-77` afterwards. The `ref:` on
the workflow's platform checkout could not have changed the outcome either way, because
`adopter-gate.py:checkout_tag()` re-checks that same directory out at the pinned tag before it
reads a single evidence file. The pin is a real improvement; it is not the cause of this red.

What the red actually is: tuppence's `compose()` folds `bump.computed` for **every version in the
institution's current supported window**, which has been exactly `['4.0.0']` since 2026-08-29, and
platform's own signed evidence for policy 4.0.0 records `major`. driftwood and ludlow fold only
the versions a pull request **adds or retires**, so both are green the same day on the same tag
against the same evidence. tuppence's last green `shift-left` is 2026-08-28. Nothing was changed
to make it green; the diagnosis is recorded in the file itself and in ticket 64's Answer, and what
it waits on is in ticket 64's `## Waits on the owner`.
