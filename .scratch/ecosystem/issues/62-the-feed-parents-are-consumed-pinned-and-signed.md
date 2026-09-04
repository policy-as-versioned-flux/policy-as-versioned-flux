# 62 — The feed parents are consumed pinned and signed

Type: task (AFK)
Status: resolved
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

**Which check grades it.** `verify/branch-refs/verify-branch-refs.sh` -- 49 PASS, 1 SKIP,
exit 3. The one could-not-look is driftwood's `twin-sweep.yml` consuming the HUB, which has
cut no tag for it to pin to; ticket 64 cuts it. `verify/feed-contract/verify-feed-contract.sh`
passes every ico and feeds pin by name and tree.

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
   the three `release.yml` platform checkouts ungraded, which is 77 item 4.
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

Map line: Tickets 62 and 77: every cross-org checkout in the eight units names a tag its own
repository pins, and a pinned tree is checked for the section the pin is used for.

## Waits on the owner

* Pushing the three adopter branches (`ticket-62-and-77` on driftwood, tuppence, ludlow) and
  merging their pull requests as `pavc-other-hand`. The guard refuses enactment pushes.
* The citable run: `verify-feed-contract` and `verify-branch-refs` green on a TRUTH line the
  owner or the clock produces. Both were run locally and their output is in the pull request.
