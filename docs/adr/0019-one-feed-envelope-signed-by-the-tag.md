---
status: accepted
---

# One feed envelope, signed by the tag, with a closed parent kind and a free name

Five signed feeds used three version keys and five payload shapes. The party schema's parent-kind
enum was closed to four values, so a sixth feed could not be declared. No private key existed, so
nobody could publish a feed version. Decided 2026-08-28 in `.scratch/ecosystem/issues/04`.

## The decision

1. **One envelope.** `kind`, `name`, `version`, `published_by`, `published_at`, `payload_schema`,
   `payload`. JSON Schema beside the party schema. Every feed, including a regulator's penalty
   schema and a prediction-market move, is this object. Only `payload` differs.
2. **The signature is the gitsign tag.** No in-band signature field, no cosign bundle. ADR-0012
   already made the tag the one signing mechanism. A signature inside the object cannot cover
   itself. A bundle returns only if a consumer that reads outside git appears.
3. **Parent kind is closed, name is free.** `controls`, `implementations`, `feed`. The composer does
   three different things with these and nothing else. Under `feed`, `name` is free, so a new
   publisher ships a new feed with no platform change.
4. **The subscription is the pin.** `inherits[]` gains `name` and `since`. No second record.
5. **Discovery is `publishes[]` on the publisher's party artefact.** No central catalogue. The set
   of signed publisher artefacts is the catalogue.
6. **Revocation is a new version plus `revoked[]`.** Tags are never deleted. A pin to a revoked
   version is a priced hole, never a refusal.

## Alternatives rejected

- A fully open `kind` string. The composer needs to know whether a parent gives a catalogue, rules
  or prices. Three parents, one free name, is enough.
- A central feed catalogue. It would be one more party everyone depends on, against loose coupling.
- Tag deletion for revocation. It rewrites history and breaks every pinned consumer at once.

## Consequences

The five live feeds and the ico schema migrate (ticket 21). What a feed costs is undecided; that is
the £ seam.

## Note, 2026-09-04 (eco-system tickets 62 and 77; delegated, ADR-0025)

Point 4, "the subscription is the pin", was read for a year as *the tag resolves*. It is not
enough, and the gap was not theoretical: the insurer's three signed quotes named
`<adopter> exposure v1.1.0`, that tag existed on every adopter's real remote, and not one of
those trees carried an `exposure` section. A pin resolved, a number was priced from a working
copy, and the tag was recorded as its provenance.

A pin resolves to CONTENT, not to a name. The publisher's own `publishes[]` record (point 5)
says where the thing lives; the pinned tree must actually carry it:

- `controls` / `implementations` -- `<path>` is in the tree;
- `feed` with a `payload_schema` -- `<path>/v<MAJOR>/feed.json` is in it;
- `feed` with `payload_schema: null` -- `<path>/HEADER.yaml` is in it AND carries a section
  keyed by the feed's `name`. This is the adopter's `exposure`: a section of that party's own
  signed artefact, never an envelope of its own.

A pin whose tree lacks its section is a missing instrument (ADR-0020) and refuses. Where the
publisher's BRANCH carries the section, nothing is wrong with the code and what is missing is a
release, so a checker says could-not-look rather than observed-false -- the same queued state
this ADR already gives a feed whose envelope is on the branch and not yet tagged.

The rule is written once, in `platform/party/pin_content.py`, and applied by composition and by
the insurer's pricer through their pinned platform dependency. The hub's
`verify/feed-contract/` states it a second time in git plumbing, on purpose: the hub is not a
party and pins no platform release, and importing a party's code to grade that party would be
worse than two implementations of one rule.

Point 4 also implies what ticket 62 landed: a subscription consumed at a BRANCH is not a pin at
all. Every cross-organisation checkout in the eight units now names a tag one of the consuming
repository's own `{tag, commit}` pin records declares, and `verify/branch-refs/` grades it.
