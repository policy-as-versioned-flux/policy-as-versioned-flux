# 128 — Being behind a major the checkout cannot read costs nothing

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-23 by the integrator. No open ticket owns this red. Ticket 84 (resolved) owns
the composer rule, and its dated correction of 2026-09-23 records the defect. Ticket 110 measured
it.

`verify/supersede/verify-supersede.sh` FAILs with four lines on run 296. driftwood, ludlow and
tuppence pin `ico/penalty-schema@v3` behind `v4.0.0`, tagged 2026-09-10. driftwood also pins
`feeds/threat-register@v2` behind `threat-register/v3.0.0`. None of the four carries a supersede
line in its served evidence.

The cause, measured by ticket 110: each feed entry records `superseded.state: unobserved`,
because the publisher checkout at the adopter's pin has no directory for the newer major, so
`newest_published_major()` writes no line. The composer does not read the publisher's tags, so
being behind is free again. Ticket 84's review said being behind must never be free.

What this ticket owes, in platform `compose/composition.py`:

1. A newer major that is tagged on the publisher's real remote prices the pinned line, even when
   the pinned checkout has no directory for it. Ticket 110's portability rule still holds: the
   observation is recorded in the vendored `PROVENANCE.json` and replayed offline.
2. A red-first test at the `compose()` seam, and a selfcheck case.
3. The hub's `verify-supersede.sh` reads the new lines. Ticket 127 must grade the new
   `kind: supersede` ico prices correctly, so land 127 first or together.

## Done

Composing each adopter under the new composer writes a supersede line for each of the four pins,
the offline replay is byte-identical, and the hub check passes once the adopters recompose under
a platform tools release that carries this change.
