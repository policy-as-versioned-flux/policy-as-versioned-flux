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
