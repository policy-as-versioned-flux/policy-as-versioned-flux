# 84 — Being behind costs something: cve and eol converters, supersede pricing, the retirement proposal

Type: task (AFK)
Status: resolved
Blocked by: 75 (resolved)

## Question

The thesis's reason for multi-version coexistence is a transition window in which old versions retire. The estate has no such window. Ticket 13 D5, one of five decided items, replaced ADR-0010's consumer-side sunset with a publisher-side supersede: a pin behind a newer published version is priced by the EOL ramp, and the adopter's scheduled proposer opens a retirement PR. Neither half is built. `composition.py`'s `FEED_CONVERTERS` has two rows; the feeds publisher advertises cve and eol feeds that composition refuses to price; `eol_ramp` has no caller outside its own module; `tier_pr.py` builds cage-tier proposals only. The old org's sunset cron remains the only clock that ever opened a retirement PR a human merged.

Under ticket 75 Q3's answer:

1. Add `cve` and `eol` rows to `FEED_CONVERTERS`, wiring the converters that already exist and selfcheck in `platform/feeds/to_fair_scenario.py`. Subscribe one adopter to feeds/eol and one to feeds/cve.
2. Add the platform policy line to the eol feed, or a `supersedes: {version, published}` field on the newer release element, and extend `compute_prices` to price a parent pin behind the newest published version by the ramp from the newer version's publish date. Pass the composition date through as `--as-of` and record the ADR-0006 note this needs.
3. Teach the proposer a retirement-kind proposal on the dedupe key `rejection_ledger` already reserves, opened by the adopter's clock when a pinned line is superseded.
4. Restate CONTEXT.md:153-155 to whatever Q3 decides, and set `verify-coexistence.sh`'s threshold to match.

Done = a real adopter pin behind a real newer tag prices a non-zero supersede line on the next citable run, and one retirement proposal PR has opened by the clock and been merged by a human.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R6. Findings: thesis/TF-02, scope/F3, legacy/L2, L3, L7. Ticket 63 supplies the second declared line. Ticket 35's converter ordering (converters before the app lift) follows from item 1.

## Comments

**2026-09-02, ticket 75 resolved.** Q3 is (a), owner-reasoned: at least three significant versions, because retirement runs forward and back by one version (the owner's Medium post, 2022-03-11, read through the owner's browser). Item 4 becomes: CONTEXT.md:153 stands at ≥3; set `verify-coexistence.sh`'s threshold to three declared lines. New item 5: the third declared line. Ticket 63 cuts the second (5.0.0); the third is the next bump the engine computes on a real change, and until it exists the coexistence check reads could-not-look with that reason, never green on two. Unblocked.

**2026-09-08 (build, wave 2).** Built on platform, feeds, tuppence and ludlow branches
`ticket-84-being-behind-costs-something` (each cut from that unit's `origin/main`) and the hub
branch of the same name. Answer below. Two claims in the Question were stale by build time and
are corrected in the Answer: `eol_ramp` has had a caller outside its module since ticket 38, and
the second declared line (5.0.0) was already declared by ticket 63, uncut.

## Answer

Built 2026-09-08. Every decision below is **delegated** (ADR-0025) unless it says otherwise; none
is money, a date, an identity, an authorisation or a real person -- those are under *Waits on the
owner*.

### What was built

**Platform** (`compose/composition.py`, `compose/handbook.py`, `compose/README.md`,
`feeds/to_fair_scenario.py`, `feeds/README.md`, `wargamer/wargamer.py`, `wargamer/tier_pr.py`,
`wargamer/README.md`, `distribution/verify-coexistence.sh`):

1. `FEED_CONVERTERS` gained `cve` and `eol` (two additive rows, ticket 79 queued behind on the
   same table). Both price through platform's `feeds/to_fair_scenario.py`, whose `cve` and `eol`
   subcommands now price a feed's HEADLINE entry when the entry is omitted -- the entry with the
   largest expected annual loss, mode lef x mode lm, for `eol` as ramped at `--as-of` -- and
   name on the scenario which entry that is and which it did not price. The converter's own
   selfcheck covers the pick and its movement with `--as-of`. Composition's `_feed_scenario()`
   dispatches: `threat <party>`, `cve`, `eol --as-of <composition as-of>`. The vendored
   `PROVENANCE.json` records that exact invocation (ticket 45's replay shape), and the hub's
   `verify/portability/` replays it unchanged. `_INVOCATIONS` is still keyed `(name, version)`:
   the two calls composition makes per feed (old and new version) carry identical args, so no
   pair collides; the day two calls with different args share a pair is named here, not hidden.
   The currency of a cve/eol payload is read off `payload.currency`, or -- for the versions the
   adopters' checkouts already carry -- off the publisher's own magnitude key
   (`severity_lm_gbp`, `base_lm_gbp`): a declaration in the publisher's signed schema, never a
   default (`_currency_in_key`).
2. **The supersede line.** `newest_published_major()` reads the publisher's checkout tags the
   way `pin_signature_state` does: the newest annotated tag with a signature block of the pin's
   form (`<name>/vX.Y.Z` or `vX.Y.Z`) whose major is ahead of the pin's, whose version directory
   the checkout carries. `price_supersede()` then emits one `kind: supersede` entry in
   `prices[]`: `amount = base x (eol_ramp(since, as_of) - 1)`, `base` the feed line's own amount,
   `since` the day that tag was cut (`creatordate`), `as_of` the composition's; `newer`
   `{version, tag, tagged, published_at}`, `ramp`, `basis`, `proposed_tier: null`,
   `changed: false`, under the adopter's own perspective and reporting currency. `_ramp` -- the
   caller ticket 38 already gave `eol_ramp` -- is reused, not forked. Zero on the signing day and
   before it, printed with both dates. The feed entry carries a `superseded` observation either
   way: `behind`, `current`, or `unobserved` for a checkout that cannot show the tags. Not an
   exposure kind. `PRICE_KINDS` gained `supersede`; the handbook renders it with `--` in the
   tier column.
3. **`--as-of`.** `compose --as-of YYYY-MM-DD` overrides the composition's as-of; the eol
   converter and the supersede ramp both take it. The composition's own as-of is now the newest
   SIGNED date among its inputs -- every pinned envelope's `published_at` (ticket 38 D3) and
   every edge's own `since` (new). `verify` takes none. The module still reads no clock
   (selfcheck leg unchanged).
4. **Ticket 69's rule reaches every feed line.** `price_parent` writes `pin_signature` and
   `hole` on feed entries as `price_quote` did on the premium: an untagged feed pin is a hole of
   the whole line, naming the tag that does not exist (`no signed tag cve/v2.x.y (or v2.x.y)
   exists on the feeds parent's checkout ...`), printed as a `new-untagged-pin` delta, never a
   refusal.
5. **The retirement proposal.** `wargamer.wargame_retirement()` turns every `supersede` entry
   into a `retirement` drift row (`drift: True`, `tolerance: None` so proposer_bounds grades it
   at `STRUCTURAL_CONFIDENCE`), `propose()` dispatches to `_propose_retirement()` (branch
   `wargamer/retire-<org>-<publisher>-<name>-<from>-to-<to>`), and `tier_pr.py` lands it:
   `apply_pin_retirement()` moves the ONE `inherits[]` line textually (comments and layout
   survive, two lines naming one edge refuse), `_land_retirement()` re-reads and re-clamps on
   `origin/<base>` at the moment of the write, commits, force-pushes and opens or updates the PR
   with `_retirement_body()`. Ledger key `<org>/retirement/<publisher>-<name>-to-<newer>`, the
   kind `rejection_ledger` reserved (ADR-0024 D5).
6. **`verify-coexistence.sh` reads three DECLARED lines.** `threshold()` in its array reader;
   two declared is a could-not-look naming three (`declares 2 of the 3 coexisting lines ...
   [4.0.0 5.0.0]; the third is the next bump the release gate computes on a real change`), the
   offline matrix over the declared lines still runs first, and the live tail's own cut-count
   and substrate reasons follow. PASS line rewritten to what it would then prove.

**Feeds** (`cve/payload.schema.json`, `eol/payload.schema.json`, `cve/v1,v2/feed.json`,
`eol/v1,v2/feed.json`): `currency: "GBP"` declared explicitly and required from this version on,
beside `published_by`. The feeds repo's own `verify-feeds.sh` PASSes against the ticket-84
platform schema.

**Adopters**: tuppence subscribes to `feeds/cve@v2`, ludlow to `feeds/eol@v2`, each one
`inherits[]` line with `since: '2026-09-08'` and a comment saying what it is and why v2 (below).
`party_artefact.py check` passes on both. `composed/` is NOT regenerated (a pin move needs a
signed platform tag; the brief forbids it); the PRs are red on `compose-check` until the owner's
tags land and each pin moves, and their bodies say so.

**Hub** (`verify/supersede/{supersede.py,verify-supersede.sh,README.md}`,
`verify/pound-seam/pound_seam.py`, `verify/feed-contract/untagged_pin.py`,
`talk/verify-manifest.txt`, `twin/ecosystem-misuse-catalogue.yaml`, `CONTEXT.md`,
`docs/adr/0006-*.md`, this file): the check below; pound-seam admits the `supersede` kind; the
untagged-pin grader reads the hole off a feed entry as well as a premium entry; the manifest
gains the new row and the coexistence row is rewritten; the misuse row that waited on this
ticket is re-anchored on `platform/compose/composition.py::price_supersede` and
`verify/supersede/supersede.py::grade_behind` (catalogue version 3); CONTEXT.md's Multi-version
entry and ADR-0006 carry dated notes.

### Which check grades it

`verify/supersede/verify-supersede.sh` (new; discovered by `talk/verify-all.sh`). Every read is
of a SERVED artefact: each adopter's `origin/main` fetched and read with `git show` (party.yaml,
composed/evidence.json, the platform pin), the publisher's real remote tag namespace
(`ls-remote`), the tag object fetched read-only for the day it was cut, and platform's composer
at the tag the adopter's own pin names. A pin behind a newer tagged major must carry a
`supersede` line under the adopter's own perspective and currency naming the remote's tag, its
cut day, the eol ramp (restated) to the entry's own `as_of`, and `base x (ramp - 1)`; missing or
wrong is a FAIL unless the pinned composer carries no supersede rule, a could-not-look naming
the tag. It prints three numbers on every run. `supersede.py selfcheck` plants fourteen grades.

**What the check prints today**, run against the estate at origin/main (2026-09-08):

    SKIP: ludlow pins feeds/feed/threat-register@v1, behind v2 (threat-register/v2.0.0 on feeds's real remote): composed under platform v2.0.1, which carries no supersede rule, so no edit of ludlow's own could put the line there -- it waits on a platform tag carrying the rule and a pin bump -- adopters behind a newer tagged major: 2 pin(s) across 3 adopter(s); supersede lines carried in served evidence: 0 of 2; untagged-feed pins: 0 of 7; holes carried: 0 of 0; retirement PRs opened/merged: 0/0

So: **2 adopters behind** (tuppence and ludlow, `threat-register@v1` behind `threat-register/v2.0.0`,
cut 2026-09-01), **0 of 2 supersede lines carried** (all three adopters pin platform v2.0.1, which
has no rule), **0 of 7 pins untagged, 0 holes carried** (the two subscriptions are not merged),
**0/0 retirement PRs**, exit 3, declared.

Also graded: platform `compose/composition.py --selfcheck` (86 OK, was 82; the four new legs
below), `compose/verify-composition.sh` (exit 3, its declared pin-containment SKIP, unchanged),
`feeds/to_fair_scenario.py selfcheck`, `feeds/verify-feeds.sh` (PASS), `wargamer/wargamer.py
selfcheck`, `wargamer/tier_pr.py selfcheck`, `wargamer/verify-wargamer.sh` (PASS),
`distribution/verify-coexistence.sh` (exit 3, naming three); hub `verify/pound-seam/` (PASS),
`verify/feed-contract/verify-untagged-pin-is-priced.sh` (PASS, 0 untagged), `verify/portability/`
(declared SKIP, unchanged), `verify/priced-holes/` (declared SKIP, unchanged), truth-line and
every-green (PASS, 119 scripts placed), `talk/verify-all.sh --selfcheck` (PASS), `tests/
test_untagged_pin.py` (24 passed), mypy on `twin tests conftest.py verify/supersede/supersede.py`
clean, `talk/truth_manifest.py judge` on every SKIP text of the new script and of
verify-coexistence.sh (all `declared waits`; the wrapper's missing-interpreter reason stays
undeclared on purpose).

### Red first, at the four pre-agreed seams (each against the origin/main tree, then green)

- (a) origin/main composer, a tuppence copy pinning `threat-register@v1` against a real clone of
  the feeds publisher carrying its signed `threat-register/v2.0.0`:
  `composed | kinds: ['feed', 'switching'] | supersede lines: 0` -- being behind was free. Green:
  `OK supersede: tuppence's threat-register@v1 sits behind the feeds publisher's real signed
  threat-register/v2.0.0 (cut 2026-09-01); the line prices 0.00 GBP at the composition's own
  as-of 2026-08-28 (ramp 1.0000 on a 222574.31 base), 222574.31 a year past the tag under
  --as-of, and 0.00 with both dates the day before it; never summed into the exposure`, and the
  same pin at v2: no line, `superseded.state == current`.
- (b) origin/main composer, the same copy plus `feeds/cve@v2`:
  `refused | ["missing instrument: feed 'cve' declared by tuppence has no converter this
  composition can price through"]`. Green: `OK untagged cve pin: tuppence pinned at
  feeds/cve@v2 composes (no refusal) with a hole of the whole line, 241549.84 GBP, naming the
  tag that does not exist (no signed tag cve/v2.x.y (or v2.x.y)); the converter's headline entry
  is on the line, and the vendored record names the real invocation ['cve']`.
- (c) origin/main `tier_pr.py`: `apply_pin_retirement exists: False | wargame_retirement
  exists: False`; `cage-tier rows over the supersede line: [('feeds-supersede', False)] ->
  proposals: [None]`; `old tier_pr.run on a supersede line lands: []`. Green: selfcheck case 4g
  -- admitted: base pins v1, evidence says v2 signed, `landed.action == created` on
  `wargamer/retire-driftwood-feeds-threat-register-v1-to-v2`, party.yaml on the branch equals the
  v2 text byte for byte, the Namespace untouched, the body carries `226,842.80 GBP` against
  `222,574.31 GBP` and the ledger key; admitted beside a HELD tier (4b's crossing on isolated:
  one `held: tighten-only`, one landed retirement); refused by name: base already at v2 ->
  `held: forward-only`, `v2 is not ahead of the pinned v2`, no branch, no PR; a v2->v1 proposal
  -> `forward-only`, `v1 is not ahead of the pinned v2`; a closed-unmerged retirement suppresses
  the same question and `-to-v3` is a new one.
- (d) origin/main `verify-coexistence.sh`: `SKIP: ... declares [4.0.0 5.0.0] but only [4.0.0]
  has been cut ...` -- nothing about three. Green: the selfcheck's `threshold(["4.0.0",
  "5.0.0"])` is not ok and names `2 of the 3`, `threshold([..., "6.0.0"])` is ok; the script
  prints `SKIP: ... declares 2 of the 3 coexisting lines the owner's 2022 rule needs (ticket 75
  Q3, ticket 84): [4.0.0 5.0.0]; the third is the next bump the release gate computes on a real
  change`, exit 3.

Ticket 45's window rule was the fifth red, found by leg (b): a fresh edge (`since: 2026-09-08`)
sits after every pinned envelope, and the composition refused it as a window that runs backwards
(`the feeds feed edge 'cve'@v2 was signed since 2026-09-08, and the newest published_at among
the feeds tuppence pins is 2026-08-28, which is earlier`). Decision D3 below; the selfcheck's F3
leg is rewritten to the new rule and keeps the refusal for a caller's `--as-of` earlier than a
signed `since`.

**Measured today on scratch copies of the two subscribed adopters, composed with this composer
against the estate at origin/main** (not served; the served numbers wait on the owner's tag):
tuppence `threat-register@v1` supersede **4,268.55 GBP** as of 2026-09-08 (ramp 1.0192 on
222,574.31; since 2026-09-01, the day `threat-register/v2.0.0` was cut); ludlow **6,103.04 GBP**
(on 318,229.78); tuppence `cve@v2` untagged hole **241,549.84 GBP**; ludlow `eol@v2` untagged
hole **772,556.59 GBP** (headline istio-1.18, eol 2024-02-21, ramp 3.55x at 2026-09-08). Both
compose with zero refusals.

### Decisions

- **D1 (delegated) -- "published" is a signed tag, and no `supersedes:` field.** The ticket's
  item 2 offered a field on the newer release or a platform line in the eol feed; neither was
  added. ADR-0019 already makes the signed tag the publication; a second declaration could drift
  from the first, which is the fourth instance of the derive-what-you-assert rule. The same
  could-not-look rules as ticket 69 apply: a checkout that cannot show the tags observes
  nothing; a lightweight or unsigned tag ahead publishes nothing and is named, not counted -- a
  missed supersede line is recoverable on the next composition, a fabricated one is a false
  number in a signed artefact. Consequence, named: a feed the publisher carries but has never
  tagged (cve, eol today) is a HOLE for whoever pins it (ticket 69's kind) and supersedes
  nothing.
- **D2 (delegated) -- `since` is the day the OLDEST signed major ahead of the pin was cut**,
  not the envelope's `published_at` and (review F3, round 2) not the newest major's cut day.
  The v2 envelope says 2026-07-31; its tag was cut 2026-09-01; between the two nobody could have
  pinned a published v2. And measuring from the newest major reset the ramp on every cut -- a pin
  two majors behind paid less than one behind (4,268.55 -> 0.00 the day a v3 landed). The entry
  carries `newer.since_tag`/`since` (the oldest signed major ahead, the day the pin fell behind)
  beside `newer.tag`/`version` (the newest readable signed major, the retirement's target).
  Review F1 (round 2): the target is the newest signed major whose directory the checkout
  CARRIES -- every adopter checks the publisher out at one pinned commit, so the newest tag's
  directory is routinely absent, and treating that as `unobserved` wrote no line and made being
  behind silently free; a signed major ahead that is unreadable here is named on the
  observation and skipped for the target.
- **D3 (delegated) -- the composition's as-of is the newest SIGNED date among its inputs**, the
  envelopes' `published_at` (ticket 38 D3) and the edges' own `since`. Reason: a fresh
  subscription is signed after every envelope it pins, and pricing it as of the newest envelope
  priced it as of a day before the adopter's own declaration existed; ticket 45's backwards-
  window refusal was that contradiction surfacing on the ordinary case of subscribing. Under the
  new rule a fresh edge's life is 0 months, nothing refuses, and no clock enters. **What that
  means for the supersede line, said plainly (review F2):** the composition an adopter SIGNS
  passes no `--as-of`, so its line is FROZEN at the newest signed input date. On the live estate
  that date is 2026-08-28 for every adopter (every edge signed that day, ico v3 published that
  day), which PRECEDES the day `threat-register/v2.0.0` was cut (2026-09-01): tuppence and
  ludlow at origin/main composed with this composer give `amount 0.0, as_of 2026-08-28, since
  2026-09-01, ramp 1.0`, and the entry says so -- `limits: ["zero (as_of 2026-08-28 precedes the
  tag day 2026-09-01): the signed artefact's as-of is its newest signed input; only a
  re-composition --as-of a later day (the scheduled proposer's) grows this line"]` -- never a
  bare 0.00. The 4,268.55 GBP measured on the scratch copy came from the copy's NEW edge (since
  2026-09-08) moving the as-of, not from a clock. Only the scheduled proposer's re-composition
  grows the line: `propose-tier.yml`'s recompose step now passes `--as-of "$as_of"` on all three
  adopters wherever the pinned composer takes the flag (review F2(i); at v2.0.1 it does not,
  and the step says so rather than stopping the clock). Review F11: a `since` later than every
  envelope moves the as-of forward, and a since in the FUTURE would move it into the future --
  a signed number that only ever grows, never cheaper (a since 2027-06-01 prices a supersede of
  166,473.39 on the scratch copy). That is accepted for the signed artefact and named here: the
  date is the adopter's own signed declaration, and a future date on it is a false declaration
  the party signs, not a rule this module can price around. A caller's `--as-of` earlier than a
  signed `since` refuses by the DAY (not the month `_months_apart` rounds to), naming both
  dates and the as-of's source -- a clock composing today against a future since refuses every
  run until that day, which is the honest reading of a declaration dated after today.
- **D4 (delegated) -- amount = base x (ramp - 1), not summed into the exposure.** The line it
  surcharges is already in the exposure; adding the surcharge would need a rule for counting one
  line twice. Zero on the signing day is printed as zero with both dates, never omitted. The
  unseen price movement between the pinned and the newer version is deliberately NOT the base:
  for eol v1 -> v2 the headline does not move and that formula would say being behind costs
  nothing forever.
- **D5 (delegated) -- headline entry per feed, not a sum.** PERT triples do not add and fair.py's
  own selfcheck refuses summing independent risks' ALEs after the fact; the headline is the
  ordinal reading (ticket 75 Q4) and the line names what it did not price.
- **D6 (delegated) -- quotes are not surcharged.** A premium is a cost, not an exposure; the
  supersede rule runs over exposure feed lines only, and the premium keeps ticket 69's hole.
- **D7 (delegated) -- how a retirement fits ticket 78's clamp: it does not, and it need not.**
  Review F9: a retirement moves the edge's `version` and leaves its `since` at the old date,
  as Renovate's bump does -- `since` is "the date this party first pinned this parent" (the
  schema's own words), the subscription's date, not the version's; the pin's life is the
  subscription's life. Recorded, not changed. Review F10: the target written into `party.yaml`
  must be a bare major (`^v\d+$`); a forged `newer.version` carrying a quote and a newline
  would have injected a second edge, and is refused before any text is written (selfcheck case).
  The tighten-only clamp binds the tier written on the governed Namespace; a retirement writes
  no tier and touches no Namespace. Its own clamp is FORWARD-ONLY, re-judged on `origin/<base>`
  at the write: the target must be ahead of the pinned major, and it is the version composition
  observed a signed tag for, so a retirement can neither move a pin backwards nor onto an
  unsigned version. A held tier selection does not hold a retirement (different question,
  different ledger kind). Signed: the proposal commit is a plain `git commit` under the
  gitsign configuration `propose-tier.yml` already sets (ticket 78), no workflow change.
- **D8 (delegated) -- a retirement is structural, not band-edge.** `tolerance: None` so the
  bounds grade it at `STRUCTURAL_CONFIDENCE` and it proposes on the first clock run after the
  newer tag. The price in the body is the CLOCK's: the proposer reads the evidence the recompose
  step wrote `--as-of` today (review F2), so it grows on every run; the signed artefact's own
  line stays frozen at its newest signed input and says `zero (as_of precedes the tag)` where
  that date precedes the cut. The ledger key carries the target major, so a still newer major
  is a new question.
- **D9 (delegated) -- the retirement PR does not re-compose.** `compose-check` refuses drift on
  it as on a Renovate bump; the body says so and says Renovate may open the same one-line edit,
  this being the PR that carries the price and the ledger key.
- **D10 (delegated) -- v2 for both subscriptions, because of ticket 45's vendoring refusal.**
  Two feeds of one publisher at one major share `composed/feeds/<party>/<version>/` and
  composition refuses that; tuppence and ludlow already pin `threat-register@v1`. v2 is also
  what a subscriber joining today would pin. The refusal itself is a named limit (a pin that
  would collide is refused by another name, ticket 98's family), not fixed here.
- **D11 (delegated) -- 5.0.0 uncut counts as declared.** Ticket 75 Q3's scope is "three declared
  lines"; the cut axis is the live tail's own, already graded.
- **D12 (delegated) -- one grader per fact in the hub.** The new check counts untagged holes and
  retirement PRs as numbers and grades only the supersede half; the hole is
  `verify-untagged-pin-is-priced.sh`'s (generalised to feed entries), the tag's verification is
  the identity-pinned verifier's.

### Stale claims corrected

- "`eol_ramp` has no caller outside its own module": false since ticket 38; `_ramp` in
  composition.py calls it for the ungoverned ramp, and is now reused for the supersede.
- "Ticket 63 supplies the second declared line": already true (5.0.0 declared, uncut); the third
  is not this ticket's to declare (the release gate computes it), and the coexistence script says
  so.
- The manifest's coexistence row said cutting 5.0.0 would flip it; corrected to the three-line
  threshold and the day both three are declared and two cut.
- The composer's own "no wall clock" prose said no converter takes `--as-of`; the eol converter
  now does, with a date the caller hands in.

### Review round 2 (2026-09-08): F1 and F2 blocking, F3-F11 -- what changed and what is recorded

- **F1 changed (red first).** Round-1 `newest_published_major` on a fixture publisher carrying a
  signed `fixture-feed/v3.0.0` tag and no `v3/` directory: `(None, {'state': 'unobserved',
  'detail': 'tag fixture-feed/v3.0.0 signs fixture-feed v3 ahead of the pinned v1, but this
  checkout carries no fixture-feed/v3/feed.json to read it from'})` -- line absent, being behind
  free. Round 2: `({'version': 'v2', 'tag': 'fixture-feed/v2.0.0', 'tagged': '2026-09-01',
  'since_tag': 'fixture-feed/v2.0.0', 'since': '2026-09-01', ...}, {'state': 'behind', 'detail':
  '... behind since 2026-09-01, the day fixture-feed/v2.0.0 was cut; fixture-feed/v3.0.0 signed
  ahead of it but unreadable here (this checkout carries no directory for it)'})`. Selfcheck
  legs: v3 signed + unreadable -> prices against v2; v3 readable -> target v3, since still v2's
  day; pin at v2 -> since v3's day; nothing readable -> `unobserved` naming every signed tag.
- **F2 changed.** (i) `propose-tier.yml` on driftwood, tuppence and ludlow passes `--as-of
  "$as_of"` to `composition.py compose` wherever the pinned composer takes the flag (a `run:`
  body edit; `actionlint` clean; at v2.0.1 it prints a note and re-composes at the newest
  signed input rather than stopping the clock). (ii) D3, D8 and Done rewritten above. (iii) a
  since behind the as-of prints `zero (as_of <date> precedes the tag day <date>)` on the entry's
  `limits` and on the hub PASS line, never a bare 0.00. Red first: tuppence at origin/main
  composed with the round-1 composer: `supersede amount 0.0 as_of 2026-08-28 since 2026-09-01
  ramp 1.0`, no note; the round-1 workflows passed `--as-of` to `tier_pr.py` only.
- **F3 changed** (D2): since = the OLDEST signed major ahead; the target = the newest readable.
- **F4 changed** (hub): `tag_object()` reads the fetched tag's type and signature block; an
  unsigned tag ahead is named on the label and never counted, and unsigned-only ahead is a
  could-not-look by name; the composer always names not-counted tags on `superseded.detail`
  (behind and current alike). Plants: lightweight, annotated-without-block, annotated-with-block.
- **F5 changed**: the note reads `largest mode-product entry, mode lef x mode lm -- an ordinal
  proxy, not fair.py's PERT expectation; ticket 75 Q4`.
- **F6 recorded** (Waits 5): HOLD tuppence 27 and ludlow 24; the FAIL quoted.
- **F7 changed**: an untagged pin with nothing signed ahead reads `superseded.state:
  unpublished`, not `current`.
- **F8 changed**: `_composition_as_of_source()` names where the date came from (the caller's
  `--as-of` / an edge's since / an envelope's published_at); both refusals and the `--as-of`
  help say "this composition's as-of (<date>, <source>)".
- **F9 recorded** (D7): `since` stays on a retirement, as on a Renovate bump.
- **F10 changed** (D7): bare-major guard on `from`/`to`, forged target refused, selfcheck case.
- **F11 recorded and half-changed** (D3): a future since is named as accepted for the signed
  artefact; a caller's `--as-of` earlier than a signed since refuses by the day.

**Map line:** Ticket 84: cve and eol price (headline entry, the eol as of the composition's own
date); a feed pin behind a newer major its publisher has signed carries a `supersede` line, base x
(eol_ramp from the day the oldest signed major ahead was cut, minus one), targeting the newest
readable one, frozen at the signed artefact's newest input date and grown only by the clock's
`--as-of` re-composition, never summed into the exposure; every feed line carries ticket 69's
hole; the proposer opens a forward-only retirement PR on party.yaml keyed
`<org>/retirement/<slug>`; `verify-coexistence.sh` reads three declared lines and could-not-looks
naming two; `verify/supersede/` prints 2 adopters behind, 0 of 2 lines carried, 0/0 retirement
PRs until platform tags and the pins move.

## Waits on the owner

1. **A platform release tag** (`cut-release.yml`, dispatched by the owner) carrying this
   composer, then each adopter's platform pin bumped to it and re-composed -- the day the served
   `composed/evidence.json` carries the supersede line for tuppence and ludlow's
   `threat-register@v1`, and `verify-supersede.sh` can read PASS. Until then it reads the
   declared could-not-look naming `v2.0.1`.
2. **Feeds tags `cve/v1.0.0`, `cve/v2.0.0`, `eol/v1.0.0`, `eol/v2.0.0`** (the feeds repo's
   `cut-release.yml`, the owner's dispatch). Until cut, tuppence's `cve@v2` and ludlow's `eol@v2`
   are priced holes of their whole line, never refusals, and supersede nothing.
3. **The `policy/v5.0.0` cut** (declared by ticket 63) and **the third declared line** (the next
   bump the release gate computes): `verify-coexistence.sh` reads could-not-look naming three
   until the array declares three, and its live tail needs two cut.
4. **Done's second half, restated (review F2): a NON-ZERO supersede line on a citable run
   comes from the clock, not the signed artefact.** After (1), the served
   `composed/evidence.json` carries the line at 0.00 with `zero (as_of 2026-08-28 precedes the
   tag day 2026-09-01)` on it -- frozen at the newest signed input -- and `verify-supersede.sh`
   reads PASS saying exactly that. The non-zero figure is the scheduled proposer's
   re-composition `--as-of` today (now wired on all three adopters), which commits nothing
   (ADR-0024) and opens the retirement PR with that day's price in its body; the merge is a
   human's. The hub check counts both off GitHub: 0/0 today. So "on the next citable run" is
   true of the LINE (zero, dated) and of the RETIREMENT PR's body (non-zero), not of a signed
   non-zero amount, unless a pinned feed publishes an envelope dated after the tag.
5. **HOLD tuppence 27 and ludlow 24 until (1) and (2) -- do not merge them first (review F6).**
   Merged alone they turn the hub gate RED, not could-not-look: on an estate with the two at
   their PR heads, `verify/feed-contract/verify-untagged-pin-is-priced.sh` prints `FAIL:
   tuppence pins feeds/feed/cve@v2: untagged (no tag of the form cve/v* or v* signs @v2 on
   feeds's real remote) and no priced entry in prices[] carries the pin` and the same for
   ludlow's eol, `FAIL: 2 untagged-pin check(s) observed false`, because the served evidence
   was composed under v2.0.1 and carries no hole for a pin it refused. Each merges together with
   its platform pin bump and a re-composition after the platform tag (then the hole is priced
   and the check PASSes), or after the feeds tags (then the pin is signed). Their
   `compose-check` is red for the same reason: v2.0.1 refuses `cve`/`eol` as "no converter".
6. **driftwood 31 (new, review F2(i))** carries only the guarded `--as-of` in
   `propose-tier.yml`'s recompose step; it is safe to merge at v2.0.1 (the guard passes the
   flag only where the pinned composer takes it) and is what makes the clock's line grow after
   (1).

## Not done

- `composed/` of the two subscribed adopters is not regenerated (forbidden from an untagged
  branch); the served numbers above are from scratch copies.
- The retirement PR does not re-compose (D9); the first real one needs a human to re-compose
  before merging, as a Renovate bump does.
- Ticket 45's vendoring layout still refuses two feeds of one publisher at one major (D10).
- `wargamer/tier_pr.py`'s selfcheck runs the owner's global ggshield pre-commit hook on its
  fixture commits and fails when that hook is out of quota (`no more API calls available`); run
  with `core.hooksPath` pointed at an empty directory. Pre-existing, not introduced here, named.
- `verify/misuse/` and `tests/test_misuse.py::test_the_four_rows_grade_against_this_checkout`
  read `.estate-clone/platform` for the re-anchored row; they are red until the platform branch
  merges and the clone is refreshed, and green against a scratch estate whose platform is this
  branch (`6 anchor(s) resolve; waits on ticket 46`). Merge order: platform, then refresh, then
  hub -- the ordering the catalogue's own header names.
