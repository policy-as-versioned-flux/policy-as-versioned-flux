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
