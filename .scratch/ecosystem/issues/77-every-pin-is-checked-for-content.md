# 77 — Every pin is checked for content, and the estate consumes itself the way it tells adopters to

Type: task (AFK build, HITL tag dispatch)
Status: resolved (items 2 and 3 wait on the owner's dispatch; item 6 is the 56+85 builder's)
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
`--fail`) was handed to the ticket 56+85 builder and is not touched here.

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
`gitops/platform/platform-pin.yaml` (v1.1.1 at 58ef9c5, checked); ico and feeds pin
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

**Which checks grade it.** `verify/branch-refs/verify-branch-refs.sh` (new, 49 PASS / 1 SKIP);
`verify/feed-contract/verify-feed-contract.sh`, whose PASS lines now say the tree carries the
section and whose three insurer `exposure v1.1.0` lines went from PASS to could-not-look;
`platform/compose/verify-composition.sh` step 1a (`pin_content.py --selfcheck`);
`insurer/verify-insurer-quote.sh`.

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

Map line: Tickets 62 and 77: every cross-org checkout in the eight units names a tag its own
repository pins, and a pinned tree is checked for the section the pin is used for.

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
3. **Push and merge** the seven unit branches (`ticket-62-and-77` on platform, driftwood,
   tuppence, ludlow, ico, feeds, insurer), as `pavc-other-hand`.
