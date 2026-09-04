# 64 — The twin is three adopters, tagged and signed

Type: task (HITL)
Status: resolved
Blocked by: none

## Question

REGRILL answer 39 promises a twin each for driftwood, tuppence and ludlow; only driftwood has one, and ticket 29 is resolved claiming all three. Author the tuppence and ludlow overlays (vendored world layer, six standing scenarios, forward-intel emitter) as ticket 29 did for driftwood, and make the gate name the absence until then (verify-e2e-step5 hardcodes driftwood today). Cut the signed twin/v0.1.0 tag on the hub (build the release workflow truth.yml lacks; the owner dispatches), cut a driftwood release covering twin/forward-intel v1 (queue its bump.yaml), and correct ticket 29's Answer to driftwood-only with a dated note. Also harden step 5 to assert a dated scheduled sweep observation once twin-sweep first fires. Done = overlays exist and grade per adopter, twin/v0.1.0 and the forward-intel tag exist signed, and PIN.yaml's tag_cut flips true.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M15 (twin driftwood-only), M16 (untagged twin and forward-intel), minor step-5-presence-only.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** The review adds four facts. Step 5 grades six path-existence checks and passes in the same run in which twin-overlay and twin-scenarios fail on the same file (ticket 76 item 4 hardens it). All seven twin-evals metrics sit at 1.000 against a baseline recorded once on 2026-08-13, and evolution-judge's eval scores a lookup table against its own values (76 item 7). Every probability the twin scores is a YAML constant, and the world-model schema forbids a source or evidence grade; whether the twin must derive one is ticket 75 Q10. The forward-intel feed that produces driftwood's largest price line sits outside every signed tag; this ticket's tag cut is what closes it. Record: REVIEW-2026-09-02.md R7.

## Answer

Built 2026-09-04. Branch `ticket-64-the-twin-is-three-adopters` in the hub and in
tuppence, ludlow and driftwood.

### The twin is three adopters

tuppence and ludlow now carry the overlay ticket 29 built for driftwood, authored rather than
copied: the hub's standing-library world layer vendored verbatim (30 files each, byte-identical
to driftwood's and staging to the same content-addressed `world_ref`
`c2d07330a778ed547b60cfbb87217bcf9813181f`), an overlay with a caged workload, a pinned cage
policy line, the regulated data, a declared cash flow, one visible-and-unpriced capability, two
roles, one causal edge, four priced rungs, the six standing scenarios across the same four
committed classes, the pin-to-signal lookup, and a forward-intel emitter.

**They are complete and unpriced, and that is the finding rather than a gap.** Each emitter exits
3 and names both instruments it does not have (ADR-0020):

1. neither party artefact publishes a `size:` block, so no valuation can derive from a signed
   fact and the valuation on the declared cash flow carries no amount — which the twin's own
   `valuation` schema enforces from the other side, since a grade outside the pricing threshold
   may not carry a figure at all;
2. the one causal edge to that cash flow is graded 3, because its elasticity triple is arithmetic
   on a comparable firm's own published regulatory record (`.scratch/ecosystem/research/94-studied-firms.md`)
   rather than this institution's own dated incident, and `path_admission_threshold` is 2.

So there is no `forward-intel/v1/feed.json`, no `rule.yaml`, no `bump.yaml` and no `publishes[]`
record for a feed nobody emitted, in either repository. Each adopter's `verify-twin-overlay.sh`
grades 15 pass / 3 could-not-look and `twin/verify-twin-scenarios.sh` grades 14 pass /
2 could-not-look, both offline, with the refusals planted and proven to bite.

### The gate names the absence

* `verify/twin-per-adopter/verify-twin-per-adopter.sh` (new, in the gate, manifest row added).
  It derives the adopter list from the party artefacts that claim the adopter role, surveys each
  one's overlay, and reports an adopter with none by name at could-not-look. On `main`'s estate
  clone today: `SKIP: 2 of 3 adopters carry no twin overlay and are named rather than omitted:
  ludlow, tuppence`. On a staged estate carrying the three built branches: `PASS ... 3 of 3`.
* `verify/e2e/verify-e2e-step5-twin-forecasts.sh` no longer hardcodes `driftwood`. It reads its
  adopter list from `twin_per_adopter.py --list`, loops, and consumes each adopter's own three
  checks rather than re-deriving them.
* Step 5 now asserts the schedule half of its own sentence: each adopter's
  `observations/twin-sweep.jsonl` must carry at least one record with a parseable `swept_at`, and
  until one exists the line names the file and the cron. This is the weaker, prior claim to
  `twin/verify-twin-sweep-moved.sh`'s: that one asks whether the *moved* branch fired, this one
  asks whether the sweep *ran* and wrote down when.

### driftwood's `compose-check`, re-composed

Reproduced locally against platform v2.0.1's own `compose/composition.py` with every parent at
the ref the workflow names. Two lines moved and nothing else: `composed/HEADER.yaml`'s
`selection-policy: 1.0.0 -> 1.1.0` and `composed/evidence.json`'s `policy_version` on the twin
price line. Ticket 78 raised `selection-policy/VERSION` and its `PIN.yaml` to 1.1.0 without
re-running composition, so the composed artefact had been stale against driftwood's own package
since then. Committed on driftwood's ticket branch.

### tuppence's `shift-left`: the honest diagnosis

**The owner must review a major, and the major is platform policy version 4.0.0.** Evidence, from
the runs rather than from reading the code:

    FAIL: composed bump is major -- refusing to adopt v2.0.1 without human review
    ok  platform checked out at v2.0.1, resolved commit matches the pinned commit field
    declared (platform tag v2.0.1 -> v2.0.1): none
    composed (this institution, across ['4.0.0'] and retired []): major

* The bump is `major`. It comes from `platform/computed-semver/evidence/4.0.0.json` at tag
  `v2.0.1`, whose `bump` records `{"declared": "major", "computed": "major"}` — platform's own
  signed evidence, verified by the gate with `cosign verify-blob` against an identity constant
  tuppence holds itself.
* The **declared** bump for the pull request is `none`: the platform pin does not move
  (`v2.0.1 -> v2.0.1`). Nothing in the pull request proposes adopting anything.
* Ticket 62's landed note is wrong on this point and has been corrected in place. The identical
  FAIL line, with the identical numbers, is in run `33884942977`, which ran before the pin landed;
  `adopter-gate.py:checkout_tag()` already re-checked platform out at the pinned tag before
  reading evidence, so the workflow's `ref:` never reached this decision.
* The reason it is *permanent* is a divergence between the three adopters. tuppence's `compose()`
  folds `bump.computed` for every version in the institution's whole current supported window;
  driftwood's and ludlow's fold only the versions the pull request adds or retires. That window
  has been exactly `['4.0.0']` since 2026-08-29 (`f7b4501` retired 2.0.0/2.0.1/3.0.0, `6e9aab6`
  added 4.0.0), so every pull request since has been refused. tuppence's last green `shift-left`
  is 2026-08-28; ludlow's `shift-left` was green on 2026-09-04, twice, on the same platform tag
  and the same evidence.
* **ludlow is NOT in the same state**, checked rather than assumed: runs `33915624899` and
  `33918324944`, both green on 2026-09-04.
* Nothing was loosened and no review was invented. The diagnosis is written into tuppence's own
  `.github/scripts/adopter-gate.py` module docstring, with the run ids, as a comment with no
  behaviour change.

### Decisions

1. **Unit ticket branches are cut from `origin/main`, not from `ecosystem/build-2026-09-03`** —
   *delegated*. The brief of 2026-09-03 says local `main` equals `origin/main`; on 2026-09-04 six
   unit pull requests merged and every local clone was a day stale. Branching from a superseded
   integration branch would have re-proposed merged work.
2. **tuppence's and ludlow's overlays are authored complete and unpriced; the emitter refuses and
   names both instruments** — *delegated*. The alternative was to invent a turnover and an
   elasticity, which is money the owner has not signed and a measurement nobody made. A refusal
   that names two instruments is a checkable statement; a number would not be.
3. **The perspective's cash-flow valuation is graded 3, not 5** — *delegated*. Grade 5 is "a model
   asserted it"; nothing was asserted. Grade 3 is "published work, not observed here", which is
   exactly what a comparable firm's own filed revenue is. The schema then refuses an amount at
   that grade, which is the behaviour wanted.
4. **The rungs are declared in a new `twin/ladder.yaml` rather than in a second selection-policy
   package** — *delegated*. driftwood reads its rungs from its own versioned `selection-policy`;
   authoring two more of those is ticket 25's shape and not this ticket's. `ladder.yaml` names the
   platform release that published the rungs (`graded/cage.py`, `ORDER`, TABLE_VERSION 1.0.0, at
   v2.0.1) and `verify-twin-overlay.sh` compares it against that module when a platform checkout
   is present, and says it could not look when one is not.
5. **The response cost and reduction triples are platform's published figures, degenerate and
   graded 5** — *delegated*. One figure per rung is what the publisher publishes; widening it into
   a range would be this institution inventing a spread the source does not carry. Grade 5 because
   platform's own comment beside the table says the numbers are evidenced by nothing but that
   comment.
6. **ludlow's overlay models the record store and never its contents** — *delegated*, and it is
   forced. `twin/schema.py:refuse_special_category` refuses an Article 9 category anywhere in a
   loaded document, at any depth, by blunt substring match. Three documents were refused at load
   while authoring: the data component, an affected-parties line, and the perspective's own
   trading name. The response is not a rename to get past the check — the overlay models the
   store, its dependency and its cage, and models no category, cohort or attribute of any person,
   which is what the refusal exists to secure. The limit is stated in
   `orgs/ludlow/components/member-record-store.yaml` and written up in `twin/VENDORED.md`. **The
   residue named for the owner: an adopter whose own trading name contains one of those words
   cannot be described by name in a loaded document.** That is a fact about the model, not a
   defect this ticket may fix by loosening the check.
7. **tuppence's adopter gate was not changed** — *delegated*, and it is the brief's own
   instruction. Narrowing its fold to the added set would loosen this institution's gate, and
   choosing between the two readings of ADR-0011 is an architectural call that belongs in an ADR
   and a ticket of its own, not in a build that came here to author a twin overlay.
8. **`verify-twin-per-adopter` grades structure and parity only; it runs no adopter's emitter** —
   *delegated*. A hub check that re-derived half of an adopter's own check could pass while the
   repository owning the artefact failed, which is the shape this ticket exists to end.

### Which check grades it

`verify/twin-per-adopter/verify-twin-per-adopter.sh`, discovered by `talk/verify-all.sh` and
listed in `talk/verify-manifest.txt` as `estate-observation | waits: carry no twin overlay and are
named rather than omitted`. Its rules are tested at the seam in `tests/test_twin_per_adopter.py`
(12 tests, written first and proven red against a missing module) and re-proved on planted
directories by `twin_per_adopter.py --selfcheck` on every run before the estate is read. Four new
manifest rows carry the two adopters' own checks.

## Waits on the owner

1. **A signed `size:` block for tuppence and for ludlow.** Money, so the owner's (ADR-0025
   point 6). Without one neither twin can price anything, and both emitters refuse by name. What
   is needed is a turnover amount, a currency and an `as_of` on each `party.yaml`, the shape
   driftwood already signs. `.scratch/ecosystem/research/94-studied-firms.md` records candidate
   figures from real filings and explicitly does not pick one.
2. **A recorded human review of platform policy version 4.0.0's major for tuppence** — or a ruling
   on which reading of ADR-0011 the estate means, so that a ticket can change the adopters that
   do not match. Until one of the two happens, tuppence's `shift-left` refuses every pull request.
   This is an authorisation, so it is the owner's.
3. **`twin/v0.1.0`, signed.** The hub has no release workflow that cuts it; a signed tag is cut by
   `cut-release.yml` in Actions and only the owner dispatches. All three adopters carry
   `tag_cut: false` and pin `world_ref` instead, which is the only pin with bytes behind it.
   Ticket 29's own definition of done is still open on this.
4. **A signed release covering driftwood's `twin/forward-intel` v1.** Same reason: the feed that
   produces driftwood's largest price line sits outside every signed tag, and only the owner
   dispatches the workflow that changes that.
5. **The three unit branches pushed** (`ticket-64-the-twin-is-three-adopters` in tuppence, ludlow
   and driftwood). Pushing an enactment repository is refused to the assistant; the commits are
   local. Until they are pushed and merged, `verify-twin-per-adopter` reads could-not-look and
   names tuppence and ludlow, which is the correct verdict for the estate as it stands.

## Not done

* **The first dated `swept_at` observation.** driftwood's `twin-sweep` has fired four times
  (2026-09-01 to 2026-09-04) and failed every time; the ticket-72 `set +e` repair reached
  `main` at 14:50 on 2026-09-04, after that day's 12:05 firing, so the next scheduled run is the
  first that can append one. Step 5 asserts it and names the file and the cron until then. Only
  the clock can close this, and faking a line in an observations series is the exact thing the
  brief forbids.
* **`PIN.yaml`'s `tag_cut` does not flip.** It cannot: the tag does not exist and cutting one
  locally would be faking a signature.
* **No twin-sweep workflow for tuppence or ludlow.** Their emitters refuse, so a sweep would have
  nothing to re-render and no proposal to open. It is authored the day a signed size makes a
  price possible.
* **tuppence's and ludlow's `selection-policy` packages.** Ticket 25's shape; `ladder.yaml`
  carries the rungs in the meantime and is checked against platform's own published ladder.

Map line: `Ticket 64 (2026-09-04): the twin is three adopters — tuppence and ludlow overlays authored complete and unpriced (no signed size, one grade-3 edge, emitters refuse by name), verify/twin-per-adopter names an adopter without one, step 5 derives its adopter list and asserts a dated swept_at, driftwood re-composed to selection-policy 1.1.0, and tuppence's permanent shift-left refusal is diagnosed as platform policy 4.0.0's major awaiting the owner.`
