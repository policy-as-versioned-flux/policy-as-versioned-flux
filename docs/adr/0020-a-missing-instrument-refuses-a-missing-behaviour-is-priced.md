---
status: accepted
---

# A missing instrument refuses; a missing behaviour is priced

The north star says price and cage, never count, refuse or file. Ticket 07 needed a rule for two
cases the £ cannot compute: an obligation with no regime in any subscribed pricing feed, and a sum
across currencies with no FX rate for the date. Decided 2026-08-28 in `.scratch/ecosystem/issues/07`.

## The decision

- A missing **behaviour** (a control unimplemented, a size fact stale, a pin revoked) is priced.
  Stale size facts widen the loss triple back to the statutory cap. Nothing refuses.
- A missing **instrument** (no price for a declared regime, no FX rate for the date) refuses the
  composition. The gate cannot read, so it cannot price, so it must not emit a number.

## Alternatives

- Price the unknown regime at the largest known cap. Rejected: it invents a number with no source.
- Sum unconverted currencies. Rejected: it was the live bug (GAPS 3.18).

## Consequences

The verify script for this ticket must fail on a regime or a date with no instrument, and must
distinguish that from a priced hole in its output.

## Note, 2026-09-04 (ticket 69, delegated under ADR-0025): an untagged pin is a priced hole

An adopter may pin a feed version that no signed tag on the publisher's remote carries. Ticket 58
Q5(b) recommended pricing it; this note decides it and says how, so no new ADR number is spent on a
consequence of the rule above.

- **An untagged pin is a missing behaviour, not a missing instrument.** The instrument is present:
  the feed envelope is on the parent's disk and prices fine. What is absent is the publisher's
  signature over the version the adopter pinned — a behaviour the publisher has not performed yet.
  So composition prices it and never refuses. It is the same reading that made a revoked pin a
  priced hole (the decision above) and that [ADR-0026](0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md)
  applied to every other hole-shaped refusal.
- **The premium edge prices the hole at the premium itself**, booked under the adopter's own
  perspective and currency (ADR-0021's £ seam), with a `priced_by` naming the pin. A premium is a
  cost the adopter has already committed to and is deliberately left out of the exposure it was
  priced from (ticket 36), so the covered exposure is the wrong quantity: nothing about the cover
  is unproven, the *purchase* is — money paid against a quote no signature carries. A zero-amount
  hole was rejected: it would move nothing and would read as free, which is the thing the rule
  exists to prevent. This is the whole edge's amount, not a partition of it, so the hole sits as a
  singular `hole` object on the `premium` entry and never as a `holes[]` member — `holes[]` still
  means "these partition their entry" (pound-seam check 4), and this hole does not partition.
- **Signature state is read twice, at two seams, and the two are not the same claim.**
  `composition.py` runs offline in the adopter's CI and reads the pinned parent's *checkout* tags:
  `signed` (a tag of the pinned form carries a signature block), `untagged` (no such tag, or one
  with no block), `unobserved` (no git metadata to read). It never claims a signature *verifies*.
  The hub check `verify/feed-contract/verify-untagged-pin-is-priced.sh` reads the publisher's real
  remote — `ls-remote` for existence, then the platform's own identity-pinned gitsign verifier over
  the tag fetched read-only, under the publisher's own `release.yml` regexp and issuer — and grades
  the adopter's composed evidence against what it saw. A tag that exists but does not verify under
  its publisher's pins is untagged: an unverifiable signature signs nothing.
- **Could-not-look is neither.** An unreachable remote, an absent verifier, absent trust material
  or absent identity pins exits 3 with `SKIP`, never a PASS and never a refusal. Composition's
  `unobserved` keeps a recorded hole open and opens none. A missing instrument still refuses; not
  being able to look at one is not the same as it being missing.
- **The hole heals itself.** The first signed tag that carries the pin closes it on the next
  composition with no edit, printed as a `closed-untagged-pin` delta, the way `new-untagged-pin`
  printed it when it opened.
