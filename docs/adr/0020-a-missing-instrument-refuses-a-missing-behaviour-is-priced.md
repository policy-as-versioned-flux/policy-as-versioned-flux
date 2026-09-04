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
  hole was rejected, and honestly: the hole built here moves no total either — it sits beside the
  premium entry, is not summed into `prices[]` and is deliberately not in the exposure. The
  difference is the quantity reported. A zero says the pin costs nothing to leave unsigned; the
  premium says how much money is committed against a quote no signature carries, which is the one
  number a reader can act on. This is the whole edge's amount, not a partition of it, so the hole sits as a
  singular `hole` object on the `premium` entry and never as a `holes[]` member — `holes[]` still
  means "these partition their entry" (pound-seam check 4), and this hole does not partition.
- **Signature state is read twice, at two seams, and the two are not the same claim.**
  `composition.py` runs offline in the adopter's CI and reads the pinned parent's *checkout* tags:
  `signed` (a tag of the pinned form is an annotated tag object carrying a signature block),
  `untagged` (the checkout shows the publisher's tags and none of them signs the pin), `unobserved`
  (this checkout is in no position to say: no git metadata, no tag at all, or a matched tag that is
  not an annotated object). Only a checkout that can show the publisher's tag namespace may say
  `untagged`, because from inside a checkout an absent tag and an unfetched one look identical, and
  a fabricated hole of the whole premium is worse than a missed one. It never claims a signature
  *verifies*.
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

## Note, 2026-09-04 (ecosystem ticket 76): the rule binds the gate's own scripts too

The rule above was written about the £. The 2026-09-02 review found fourteen places where the
gate itself broke it: a check whose instrument was absent — the kyverno CLI, `rekor-cli`, a SPIRE
server, a reachable cluster — printed a note or a `SKIP:` line and then exited 0, which
`talk/verify-all.sh` grades PASS. A green on the absence of the instrument is the same invention
of a number this ADR refused, one layer up.

- A **verify script** whose instrument is missing exits 3 with its reason on the last line. It
  never exits 0, and it never FAILs for want of an instrument. Where a script has an offline core
  and a live tail, one unlooked tail makes the whole script SKIP: the claim is what the last line
  says, and half of it was not observed. `lib.sh` (platform) and `verify/lib-observation.sh`
  (hub) carry the helpers.
- That branch must itself be **run** on a machine that has the instrument. `selfcheck_absent`
  re-executes the script with the named tools unreachable and requires exit 3 with a `SKIP:` last
  line; a script's normal run does this before it looks. A branch nobody runs rots back.
- The same rule applies to a recorded verdict, not only to an exit code: a falsifier that was
  never run records `null`, never `false`.

`verify/every-green/verify-every-green.sh` reads every verify script the gate discovers and names
any `SKIP` that ends in `exit 0`, or in no exit at all, by file and line. Decided delegated
(ADR-0025) in `.scratch/ecosystem/issues/76`.
