# 77 — Every pin is checked for content, and the estate consumes itself the way it tells adopters to

Type: task (AFK build, HITL tag dispatch)
Status: resolved (items 2 and 3 wait on the owner's dispatch; the insurer's half of item 1 is armed but inert until a platform release carries the rule -- Waits item 3; item 6 is the 56+85 builder's)
Blocked by: none

## Question

NORTH-STAR §2's "consumed only through a pinned, signed dependency" is applied to the policy artefact and to almost nothing else, and where a pin exists the check is that the tag resolves, never that its tree contains what the consumer prices or enforces from it. Close the family:

1. One assertion, shared: a pinned tree must contain the section the pin is used for. Add it to composition (a parent pin whose tree lacks the declared feed path refuses as a missing instrument), to `insurer/pricing/quote.py` (never emit `priced_against` naming a tag whose tree lacks `exposure`), and to `verify/feed-contract`.
2. The insurer's quotes assert `<adopter> exposure v1.1.0`; no adopter's v1.1.0 tree has an exposure section. The owner dispatches one adopter release per adopter whose tree carries `exposure` and `composed/policies/v4.0.0`, then the insurer re-quotes from it. HITL for the dispatch.
3. The adopters' clusters reconcile composed 2.0.0, 2.0.1 and 3.0.0 from tag v1.1.0, the three retired lines. The same release in item 2 adds the `{ version: "4.0.0" }` element and bumps the composed pin, as the file's own comment prescribes.
4. Ico, insurer and feeds `release.yml` check platform out with no `ref:`. Pin each to the tag its own party artefact or platform pin names.
5. Driftwood consumes ico, feeds and insurer at `ref: main` in nine places, with no Flux source. Move them to the tag and commit `party.yaml` declares, and add an ico `GitRepository` in the nist pattern. Tuppence's and ludlow's twelve deleted-branch refs are ticket 62; land them together.
6. `.github/workflows/truth.yml:91` installs Flux with `curl -s https://fluxcd.io/install.sh | sudo bash` under a comment that says every tool is pinned. Copy `drift-sample.yml`'s pinned tarball form. Add `--fail` to every curl in the file.
7. `clone-estate.sh` clones default branches against its own comment that promises to pin once a signed tag lands. Whether the truth surface grades tags or branches is Q8 in ticket 75; until answered, record the tag beside each SHA in the TRUTH line so a reader can tell.

Done = a gate check resolves every declared pin in every party artefact against the tag it names and refuses a tree that lacks the named section; no workflow in the eight units checks another organisation out at a branch; the insurer's clock succeeds for real on the next scheduled run.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R4. Findings: participants/P1, P3, P4, P5, pound-engine/PE-11, principles/P4-2, security/SS-06, SS-03 (federation literals, ticket 68). Ticket 62 owns the tuppence and ludlow refs. Ticket 64 owns the twin tag. The insurer already recorded one fabricated version on 2026-08-29; this is the third artefact of that class.

## Answer

Built 2026-09-04 on one hub branch with ticket 62. Item 6 (truth.yml's Flux install and
`--fail`) was handed to the ticket 56+85 builder and is not touched here; their note for it is
kept below, in item order, exactly as they wrote it. A round-2 review on 2026-09-04 found two
ways this branch broke a working clock and seven smaller faults; both fixes and all seven are
recorded under **Round 2** at the end of this Answer, and the numbers and claims above were
corrected in place rather than left to contradict it.

**Item 1 -- one rule, three statements of it, and the third is deliberate.**
`platform/party/pin_content.py` is the rule, written once:

```
kind controls / implementations   <path> exists in the pinned tree
kind feed, payload_schema set     <path>/v<MAJOR>/feed.json exists (an ADR-0019 envelope)
kind feed, payload_schema null    <path>/HEADER.yaml exists AND carries a section keyed by
                                  the feed's `name` -- the adopter's `exposure`
```

A pin whose tree lacks its section is a missing instrument (ADR-0020) and refuses. It is
applied in:

* `platform/compose/composition.py` -- every parent edge, after `resolve_sha`, before the
  parent is recorded. A self-pin is exempt: its tree IS the tree under composition.
* `insurer/pricing/quote.py` -- imported out of the insurer's own PINNED platform checkout
  (`PLATFORM_DIR`), and called BEFORE `exposure_of`, so the refusal a reader sees is the
  estate's one sentence and not this file's private restatement of half of it. Proven live:
  handed driftwood's real `v1.1.0` tree, the pricer now refuses with *"the pinned driftwood
  tree's party.yaml declares no publishes[] record for feed/exposure, so this pin names
  nothing"* -- that tag has neither the section nor the record.
* the hub's `verify/feed-contract/feed_contract.py`, restated in git plumbing over the
  publisher's real tag (`git show <tag>:<path>`), in the same three cases and the same words.

**Item 2 and item 3** are the owner's dispatch; see below. Nothing was pre-staged: writing a
tag that does not exist is fabrication, and `gitops/composed/composed-set.yaml`'s own comment
already says the `{ version: "4.0.0" }` element and the self-pin bump must land in ONE reviewed
pull request or the Kustomization reconciles a path that does not exist. That comment is right
and this build left it alone.

**Item 4 -- the three `release.yml` platform checkouts are pinned.** The insurer reads its own
`gitops/platform/platform-pin.yaml` (v2.0.1 at 533dccb, moved there by the round-2 fix
below -- it read v1.1.1 and that broke the release gate); ico and feeds pin
`PLATFORM_TAG`/`PLATFORM_COMMIT` (v2.0.1 at 533dccb) in the workflow's own `env:`, beside
`GITSIGN_VERSION`. Each gains a step asserting the checked-out HEAD is the pinned commit. The
insurer's `fetch.yml` also gains the pinned platform checkout, because its pricer now reads the
shared rule out of it.

**Item 5** landed with ticket 62: driftwood's nine `ref: main` checkouts and the new
`gotk-sync-ico.yaml` are in that ticket's Answer.

**Item 6 only, 2026-09-04 (delegated, ADR-0025), built by the 56+85 builder** so that two builders
did not edit `.github/workflows/truth.yml` at once. Everything else in this ticket belongs to the
62+77 builder working in parallel; nothing of theirs was touched.

`truth.yml` installed Flux with `curl -s https://fluxcd.io/install.sh | sudo bash`, under a comment
claiming every tool the gate observes with is pinned by version and checksum. It was the one
unpinned tool in the instrument, and it ran as root. It now uses the pinned tarball form copied
verbatim from the adopters' `drift-sample.yml` -- `FLUX_VERSION: 2.9.3` and `FLUX_SHA256:
eae4e860…` in the workflow `env:`, `curl -fsSL` to a tarball, `sha256sum -c -`, `tar xzf`,
`flux --version` -- so the gate and the adopters' sampler run the same Flux, and a difference
between them is a version bump somebody made on purpose. `--fail` (the `-f` in `-fsSL`) is on all
four curls in the file, not only this one: without it a 404 writes an HTML error page into the
target and the failure surfaces as a confusing checksum mismatch three lines later. `actionlint`
clean.

Map line: Ticket 77 item 6 -- the hub gate's Flux install is pinned to 2.9.3 by tarball and sha256 like the adopters' sampler, and every curl in truth.yml carries `--fail`.

**Item 7 -- the TRUTH line says what was graded.** `talk/verify-all.sh` prints
`unit=<sha>@<tag-or-branch>`: the tag when HEAD is exactly one, else the branch, else
`detached`. `driftwood=4b28aa3@main` and `driftwood=4b28aa3@v1.2.0` are now visibly different
runs. `parse_truth` needed no change (ticket 83 left the value as text). `clone-estate.sh`
keeps cloning default branches, and now says why: a gate pinned to the last tag could never go
red on work in flight, which is the opposite of what it is for.

**Which checks grade it.** `verify/branch-refs/verify-branch-refs.sh` (new, 53 PASS / 1 SKIP
since the round-3 fix below; 50 / 1 before it);
`verify/feed-contract/verify-feed-contract.sh`, whose PASS lines now say the tree carries the
section and whose three insurer `exposure v1.1.0` lines went from PASS to could-not-look;
`platform/compose/verify-composition.sh` step 1a (`pin_content.py --selfcheck`);
`insurer/verify-insurer-quote.sh --selfcheck`, a leg added by the round-2 fix below -- until it
existed the insurer's whole half of item 1 was graded by no check anywhere, and the sentence
that said otherwise was wrong.

### Decisions (all delegated, ADR-0025, 2026-09-04)

1. **The rule lives in `platform/party/`, beside `party_artefact.py`,** because that is what
   every consumer already pins and imports through. `compose/` would have made the pricer
   import the composer to ask a question about a pin.
2. **The hub re-implements the rule instead of importing it.** The hub is not a party and pins
   no platform release; importing a party's code to grade that party is worse than two
   implementations of one rule. The three cases are written in the same order and the same
   words on both sides so a reader can see they are one rule.
3. **The tree is read with `git show <tag>:<path>` out of the local clone, not fetched.**
   `clone-estate.sh` fetches full history and tag objects on purpose (its own comment says
   why), so the content of a signed tag is already on disk. A tag object this checkout does
   not carry is a could-not-look, never a pass.
4. **A tag whose tree lacks the section is a could-not-look when the publisher's BRANCH carries
   it, and observed false when it does not.** This is the existing queued/nowhere pair
   `local_version()` already draws for envelope feeds, extended to sections. The three insurer
   `exposure v1.1.0` pins are the queued case: every adopter's branch carries the section, so
   what is missing is a release, not a fix -- which is exactly item 2, and exactly what the
   owner's dispatch closes. Grading them FAIL would have said the code was wrong.
5. **`pin_content.refusal_for_pin` is silent on a tree with no `party.yaml` unless the caller
   passes `require_declaration=True`.** The rule grades a DECLARED section against a tree;
   with no declaration there is nothing to grade, and refusing would have failed every
   synthetic parent tree composition's own selfcheck composes against while saying nothing
   about the estate. That every real unit carries a party.yaml is verify/party's question.
6. **ico and feeds pin the platform in `env:`, not in a `gitops/` pin file.** Neither runs a
   cluster or carries a `renovate.json`, so a pin file would gain nothing a constant beside
   `GITSIGN_VERSION` does not already give. Named residual: those two pins are bumped by hand
   until either repository gains a Renovate config, at which point the comment in each file
   says to move it to `gitops/platform/platform-pin.yaml` in the insurer's shape.
7. **`quote.py` grades the tree it is handed and does not assert that tree is at the pinned
   tag.** Whether it is, is asserted where it can be: `fetch.yml` checks the adopter out at
   `ref: <the pin>` and nowhere else, and the hub's feed-contract resolves the same pin against
   the adopter's real remote. Making the pricer refuse a working tree would have broken
   `verify-insurer-quote.sh`'s offline re-price, which is a real check of a real number.
8. **A pinned platform release that does not carry the rule is a COULD-NOT-LOOK, not a refusal**
   (round 2, 2026-09-04). `pin_content()` returns `None` and the pricer prints a NOTE on stderr
   naming what was not checked and who does check it, then prices on. Reason: no platform tag
   carries `party/pin_content.py` -- checked tag by tag, v0.1.0 through v2.0.1 and policy/v2.0.0
   through policy/v4.0.0, none has it -- so the refusal as first built would have stopped the
   insurer's scheduled re-quote on every adopter for want of a rule the estate has not released.
   A check must not break the thing it grades. The refusal arms itself with no further change on
   the day the insurer's platform pin moves to a release that carries the file.
9. **The insurer's platform pin moves to v2.0.1** (round 2, 2026-09-04), and `party.yaml`'s
   `platform/implementations` edge with it, because `party_artefact.py` grades that edge against
   this file's tag. Reason: item 4 pinned `release.yml`'s platform checkout to a pin file that
   said v1.1.1, a value nothing had ever exercised because the checkout had carried no `ref:` at
   all. v1.1.1's `party/schema.json` predates `reporting_currency` and `publishes`, both of which
   the insurer's own `party.yaml` carries, so the release gate refused
   (`REFUSED: unknown top-level field 'reporting_currency'`). v2.0.1 is the tag the three
   adopters already pin and the oldest whose schema this party validates against. The quotes did
   not re-render: `quote.py` takes no arithmetic from `fair.py`.

Map line: Tickets 62 and 77: every cross-org checkout in the eight units names a tag its own
repository pins, and a pinned tree is checked for the section the pin is used for.

### Round 2, 2026-09-04 -- the review found two ways this branch broke a clock

Both were the same mistake in two places: a pin file is the right shape, and the VALUE in it had
never been exercised, so pinning a checkout to it moved a stale value onto a live path.

1. **The re-quote clock would have refused on every adopter, for ever.** `payload()` calls
   `pin_content()`, which loads `platform/party/pin_content.py` out of `PLATFORM_DIR`;
   `fetch.yml` checks platform out at the tag the pin file names; and NO platform tag carries
   that file -- it is new on `ecosystem/build-2026-09-03` and unreleased. Every scheduled
   re-quote would have died `REFUSED: missing instrument: no .../party/pin_content.py`, exit 1
   under `set -euo pipefail`, which contradicts this ticket's own done clause. Fixed as decision
   8 above: absent rule = could-not-look, announced on stderr, price on.

   Measured while fixing it, and worth writing down because it changes what "the clock works
   today" means: the clock is ALREADY refusing, and was before this branch. `fetch.yml` checks
   each adopter out at the pinned tag `v1.1.0`, and no `v1.1.0` tree carries an `exposure`
   section, so `exposure_of()` refuses first -- the pre-branch `quote.py` refuses identically on
   all three adopters when handed the real pinned trees. The two refusals have one cause (no
   released tag carries the exposure section) and one fix (Waits item 1). What this branch would
   have added is a refusal that the owner's dispatch could NOT clear, because no adopter release
   puts `pin_content.py` into a platform tag.

2. **The release gate would have refused.** Item 4 pinned `release.yml`'s platform checkout to
   `gitops/platform/platform-pin.yaml`, which said v1.1.1; `verify-insurer-party.sh` validates
   `party.yaml` through `<PLATFORM_DIR>/party/party_artefact.py`, and v1.1.1's schema predates
   `reporting_currency` and `publishes`. Run against the real v1.1.1 tree the gate refused three
   fields and exited 1; today's unpinned step gets the default branch and passes. Fixed as
   decision 9 above: the pin, and the `inherits[]` edge that must move with it, are v2.0.1.
   Checked both ways against real trees: `PLATFORM_DIR=<v1.1.1> ./verify-insurer-party.sh` exits
   1, `PLATFORM_DIR=<v2.0.1>` exits 0.

Which platform tags carry what, checked tag by tag on 2026-09-04 and the reason no other pin
would serve:

| tag | `party/schema.json` has `reporting_currency` + `publishes` | `party/pin_content.py` |
|---|---|---|
| v0.1.0, v0.1.1, v1.0.0, v1.1.0, v1.1.1 | no | no |
| v2.0.0, v2.0.1, policy/v4.0.0 | yes | no |

**Seven smaller corrections in the same round.**

* `verify-branch-refs.sh` grades **50 PASS / 1 SKIP**, not 49; both Answers said 49.
* **This ticket claimed `verify-insurer-quote.sh` grades the new rule. It did not** -- that
  script never calls `payload()` or `envelope()`, so the refusal path was exercised by nothing.
  The seam asked for is now built: `verify-insurer-quote.sh --selfcheck` drives
  `refuse_unless_tree_carries_exposure` over synthetic driftwood trees and proves three things --
  rule absent = could-not-look and price on, rule present + tree without the section = refused as
  a missing instrument, rule present + tree with the section = graded. The main run executes it
  first and records its verdict into its own aggregate, so the gate grades it too (22 checks now,
  not 21).
* **`branch_refs.py`'s limits are stated**, in its docstring and in its manifest line: it globs
  `.github/workflows/*.yml` and grades `actions/checkout@` steps only, so a `.yaml` workflow, a
  composite action or a `git clone` in a `run:` block is invisible to it. Checked 2026-09-04:
  none of the three exists anywhere in the eight units, so the glob misses nothing that is there
  -- it would miss the first one added.
* **`talk/verify-manifest.txt` rows 133 and 144 were too narrow.** Each script can print a
  could-not-look reason its declared pattern did not carry (`carries no clone of <party>`;
  `does not carry the tag object`), so an honest skip would have been graded FAIL. Both patterns
  widened, with the reason on the line.
* **The `gotk-sync-feeds.yaml` Renovate manager could never have bumped anything** in any of the
  three adopters: it captured `threat-register/v2.0.0` whole as `currentValue` and handed it to
  `semver` versioning, which cannot parse it. Rewritten in the shape the repositories' existing
  feed manager already uses -- the feed prefix outside the capture group, an
  `extractVersionTemplate` mapping the publisher's per-feed tags back onto the captured semver.
* **Stale comments removed** from tuppence's and ludlow's `propose-tier.yml` and `shift-left.yml`:
  they still described fetching an insurer parent those jobs no longer fetch (decision 5 in
  ticket 62 removed it), including a refusal line for a parent neither party declares.
* The false half of `party.yaml`'s own comment is corrected: it said v1.1.0 is "the one whose
  tree carries the exposure section". No v1.1.0 tree does. That is the whole of item 2.

### Round 3, 2026-09-04 -- review fixes recorded here

* **`verify-branch-refs.sh` graded 51 of the estate's 52 cross-organisation checkouts.** The
  52nd, insurer/fetch.yml's `repository: policy-as-versioned-${{ matrix.adopter }}/...`, was
  invisible: neither passed, refused nor skipped, so moving it to a branch was free. It is
  expanded from the job's own matrix and graded now -- 53 PASS / 1 SKIP, all 52 lines covered.
  The reasoning, the counted number and the corrected claims are in ticket 62's round-3 note.
* **`verify-insurer-quote.sh` selfcheck leg 3 is wrapped.** Legs 1 and 2 caught `quote.Refused`;
  leg 3 -- the tree that DOES carry the exposure section, which proves the refusal is not a
  blanket one -- did not, so a rule that OVER-refuses ended the run on a raw traceback instead
  of the `FAIL:` line the gate reads. Measured both ways with a stub `pin_content.py` that
  refuses whatever the tree holds: before, `quote.Refused: missing instrument: ...` and a
  traceback; after, `FAIL: quote.py pin-content seam: a pinned tree that DOES carry the exposure
  section was refused (...); the refusal is a blanket one and would stop every re-quote in the
  estate`. With the real rule (`PLATFORM_DIR=.estate-clone/platform`) the leg passes.
* **`verify-feed-contract.sh --selfcheck` runs the selfcheck alone**, as this Answer already
  said it did; it accepted the flag and ran the full estate check instead. Its manifest row
  declared two of the six could-not-look reasons `feed_contract.py` can print, so a network blip
  or an offline payload schema read as red; all six are declared now.

## Waits on the owner

1. **Item 2 and item 3, one dispatch per adopter.** `cut-release.yml` on driftwood, tuppence
   and ludlow, cutting a tag whose tree carries the `exposure` section and
   `composed/policies/v4.0.0`. A signed tag comes only from Actions; an agent never fakes one.
   In the SAME reviewed pull request as that release, per `gitops/composed/composed-set.yaml`'s
   own comment: add `{ version: "4.0.0" }`, drop `2.0.0`/`2.0.1`/`3.0.0`, bump the
   `driftwood-composed` (and tuppence/ludlow equivalent) self-pin to the new tag, and move the
   `gitsign-gates` annotation to `flux-system/composed-v4-0-0`. Until then feed-contract says
   could-not-look on the three exposure pins, which is the honest reading.
2. **After those tags exist:** bump `insurer/party.yaml`'s three exposure pins to them, let
   `fetch.yml` (cron 31 5) re-quote for real, then dispatch the insurer's `cut-release` so the
   re-quote tag exists for Renovate to bump the adopters' `quote-<adopter>` pins.
3. **A platform release that carries `party/pin_content.py`** (round 2, 2026-09-04).
   Who: the owner, dispatching `cut-release.yml` on `policy-as-versioned-platform/platform`
   after this run's `ticket-62-and-77` branch is merged there. What it unblocks: until that tag
   exists, `insurer/pricing/quote.py` says could-not-look on the tree-carries-the-section rule
   and prices on, and `verify-insurer-quote.sh --selfcheck` grades only the could-not-look half
   of the seam (it exits 3 on any runner whose platform checkout lacks the file). After it
   exists, bump `insurer/gitops/platform/platform-pin.yaml` and the matching `inherits[]` edge
   to it in one reviewed pull request, and the refusal arms itself with no code change. Nothing
   here can be pre-staged: writing a tag that does not exist is fabrication.
4. **Push and merge** the seven unit branches (`ticket-62-and-77` on platform, driftwood,
   tuppence, ludlow, ico, feeds, insurer), as `pavc-other-hand`.
