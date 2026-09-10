# 110 — A supersede surcharge cannot be re-derived offline, so a signed artefact stops re-rendering

Type: task
Status: open
Blocked by: none

## Question

Two features this estate built and signed now contradict each other, and the contradiction became
observable on 2026-09-10 the moment `ico v4.0.0` was tagged.

**Ticket 45's claim:** an adopter re-verifying its own signed composed tree OFFLINE gets the same
bytes. `verify()` is a byte comparison over every rendered file, so the vendored payload plus
`PROVENANCE.json` must be sufficient and the publisher's clone must not be needed.
`composition.py --selfcheck` asserts exactly that at the seam:
`assert rendered_absent == rendered_present`.

**Ticket 84's surcharge:** when a publisher supersedes the major an adopter pins, the composed
document carries a `supersede` price row, an EOL ramp of `+1x` per year behind capped at `+4x`,
where `since` is the day the newer major's SIGNING TAG was cut.

The surcharge is computed from the publisher's TAG DATES. A vendored copy of a payload cannot
carry the date of a tag that did not exist when it was vendored. So the row appears when the
publisher's clone is present and vanishes when it is absent, and ticket 45's assertion fails.

Measured first-hand in a private estate clone at platform `5b88f1d`, composing driftwood:

```
--- ico ABSENT
+++ ico PRESENT
 | ico | feed      | penalty-schema | driftwood | GBP | GBP 1,787,177.08 | no | isolated |
+| ico | supersede | penalty-schema | driftwood | GBP | GBP 0.00         | no | —        |
```

and, downstream of the extra row, every later price index shifts (`prices[6]` becomes `prices[7]`)
and the artefact's own footer count moves from 8 prices to 9. So the divergence is not one line: it
renumbers the named absences that cite price indices.

The amount is `GBP 0.00` **because the tag was cut that same day** and the ramp is zero on day zero.
It will not stay zero. Tomorrow it is a real number, and the two renders will differ by a priced
amount rather than by a zero.

## What has to be decided

1. **Which claim wins.** Portability and the surcharge cannot both hold in their current form. If
   portability wins, the surcharge has to be derived from something the adopter's own signed tree
   carries. If the surcharge wins, ticket 45's assertion and its promise have to be narrowed, and
   the deck and record that repeat the promise have to be narrowed with them.
2. **If portability wins, where does `since` come from?** The candidate is the vendored
   `PROVENANCE.json`: record the publisher's newest major and the date its tag was cut AT VENDOR
   TIME, so the ramp is a function of the artefact rather than of the world. That makes the number
   reproducible and stale by construction, which is a different honesty problem, and it needs
   saying out loud on the page.
3. **Whether a zero-valued row should render at all.** Today's difference is a row priced at zero.
   A rule that a zero surcharge is recorded but not rendered would postpone this exact failure
   rather than fix it, and would hide the day the clock starts. Decide deliberately, do not drift
   into it.

Done = `composition.py --selfcheck` passes with a publisher clone present and absent, and the
record states which of the two claims was narrowed and why.

## Notes

Charted 2026-09-10. The tag did not break this; it made it reachable. Ticket 84's own record
already names a related half: the supersede line vanished when a newer major's directory was
absent from the pinned checkout, and no adopter workflow passed `--as-of`, so a served line read
0.00 for a tag cut later. This is the same fault line seen from the portability side.

Two adopter pull requests are HELD on ticket 84 (tuppence 27, ludlow 24). Whatever is decided here
governs them, because both subscribe an adopter to a feed whose publisher can supersede it.

Record: ticket 45's `verify-portability`; ticket 84; `composition.py`'s selfcheck at the
`rendered_absent == rendered_present` assertion; `talk/verify-falls.txt` `run=234`.
