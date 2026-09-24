# 136 — The composer selfcheck breaks on driftwood's new main

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator. Truth run 314 graded
`.estate-clone/platform/compose/verify-composition.sh` FAIL on `composition.py --selfcheck`,
after driftwood moved to platform tools v3.3.0 (driftwood PR 40) and its composed set to v2.0.0
(driftwood PR 39). Run 310 graded it SKIP.

Ticket 134's builder measured the selfcheck against driftwood's main `3f8943d` and saw it stop
with "two feed edges of feeds at v2 both vendor to composed/feeds/feeds/v2". The selfcheck uses
the real driftwood as its fixture, so a real change in driftwood broke an assumption in it.

What this ticket owes:

1. Find which assumption broke and whether driftwood's state is valid. If driftwood now carries
   two feed edges at the same major that the composer cannot vendor apart, that is a composer
   defect or a driftwood defect, not a selfcheck one; say which.
2. Fix it where it is wrong, red first, on platform main, so the next tools release carries it.

## Done

`composition.py --selfcheck` passes against the real estate at each adopter's main, and the
record says what broke.

## Build, 2026-09-22

Built 2026-09-24. Platform PR: https://github.com/policy-as-versioned-platform/platform/pull/40
(branch `ticket-136-vendor-by-feed-name`, commit f4de16c).

### What broke

The estate I measured against: a detached worktree of each unit at origin/main. platform 38089a6,
driftwood b5eb409, tuppence 8d71d47, ludlow 194accc, nist f83126f, ico abcb3a8, feeds ff3ac9a,
insurer d1c1844. The shared `.estate-clone/driftwood` lagged at 3f8943d.

On platform 38089a6 the selfcheck exits 1 at "threat bump, after" with the refusal the ticket
quotes. The failing case copies **tuppence**, not driftwood. It bumps tuppence's
threat-register pin from v1 to v2. Tuppence has pinned `feeds/cve@v2` since 55f8c23
(2026-09-23, ticket 84). The composer vendored each feed to `composed/feeds/<party>/<version>`, so
cve@v2 and threat-register@v2 both landed on `composed/feeds/feeds/v2` and refused.

Answer to question 1: driftwood's state is valid. It pins one feed per publisher. The defect is
the composer's. Ticket 45's layout left the feed name out of the vendored path. Ticket 84 recorded
that as a named limit (its D10) and picked v2 for both new subscriptions to avoid it. The
selfcheck's bump is the same edit a real Renovate PR would make. So tuppence (cve@v2) and ludlow
(eol@v2, 421b1a0) could never move threat-register to v2, which driftwood already pins.

Two more selfcheck legs broke on the same two subscriptions once the first was fixed:

- The supersede leg composes tuppence as of the day before threat-register/v2.0.0 was cut
  (2026-08-31). The cve edge is signed since 2026-09-08, so that composition refused as a
  backwards window. The refusal is right; the leg asked the wrong question.
- The untagged cve leg and the eol leg added a cve@v2 edge to tuppence and an eol@v2 edge to
  ludlow. Both already pin those feeds, so each copy carried one feed pinned twice, and that
  refused.

### The fix (composition.py beyond the selfcheck: yes)

- `vendored_rel(party, name, version)` now returns `composed/feeds/<party>/<name>/<version>`.
  `vendored_tree` takes the name too. Its three callers in `compose()` and `vendor_feed` pass
  `_feed_name(edge)`. The duplicate-path guard stays; only one feed pinned twice reaches it now.
- Selfcheck: every vendored path it asserts goes through `vendored_rel`, not a literal. The
  day-before supersede leg composes a copy holding only the edges signed by that day
  (`_drop_edges_signed_after`). `_add_feed_pin` restates an existing pin instead of adding a
  second edge.

### Tests (all run in this task)

- Red first: new `TwoFeedsOfOnePublisherAtOneMajor.test_each_feed_vendors_to_its_own_directory` in
  `compose/test_portable_observations.py`. One fixture publisher, cve@v1 and eol@v1. On the old
  layout the composition refused with "two feed edges of fixture-publisher at v1 both vendor to
  composed/feeds/fixture-publisher/v1". Green after the fix. The fixture setup moved to a
  `PublisherFixture` base class, and the four literal provenance paths now use `vendored_rel`.
- `python3 -m unittest test_portable_observations`: 9 tests, OK.
- `PAVC_ESTATE_CLONE=<fresh estate> python3 composition.py --selfcheck`: rc=1 on 38089a6, rc=0
  on f4de16c.
- `PAVC_ESTATE_CLONE=<fresh estate> bash compose/verify-composition.sh`: rc=0, ends "PASS: the
  composition seam holds".

### Decisions

- **D1 (delegated): fix the composer, not the selfcheck or the adopters.** Bumping tuppence to v3
  in the selfcheck would pass and leave the real Renovate bump refusing. Dropping tuppence's cve
  pin would undo ticket 84. A feed is (party, name, version) under ADR-0019, so its vendored copy is
  keyed the same way.
- **D2 (delegated): no read fallback to the old layout.** The composer already says "verify older
  artefacts with their pinned composer", and every adopter workflow checks platform out at a
  pinned tag. An artefact composed by v3.3.0 is verified by v3.3.0.
- **D3 (delegated): the day-before leg drops edges signed after that day.** The party as it stood
  that day did not carry them. Moving their `since` back would invent a date nobody signed.
- **D4 (delegated): `_add_feed_pin` restates an existing pin.** The helper means "pin this feed".
  On a copy that already pins it, a second edge is a fixture fault, not a subscription.

### Named residual (not fixed here)

With a publisher's clone absent, a second feed of the same publisher reads the first feed's
vendored tree and refuses: "observation does not belong to this feed pin and parent SHA".
`compose()` keeps one parent tree per party. I measured it on platform 38089a6 with a fixture
publisher carrying cve@v1 and eol@v2 (different majors, so no path collision). The refusal
predates this change. Tuppence (threat-register@v1 and cve@v2 from feeds) has the same shape; I
did not run the real tuppence with feeds absent. It refuses by name and never prices from the wrong bytes. Fixing it needs one parent tree per feed
edge in `compose()`, a wider change. It is not charted here; the integrator can number it.

### What remains

- Merge platform PR 40 (integrator).
- A platform tools release carrying it: waiting on the owner, who cuts releases and signed
  tags. Adopters then take it by Renovate and recompose. Each
  adopter's `composed/feeds/` moves to the name-keyed layout on that recompose. Nothing moves
  before then, because adopters compose with a pinned platform tag.
- The next truth run grades `verify-composition.sh` against the shared `.estate-clone`. I did
  not run it there. That clone's platform needs this commit, and its driftwood lags at 3f8943d.
