# verify/supersede — being behind costs something (eco-system ticket 84)

`verify-supersede.sh` grades, on SERVED artefacts only, ticket 13 D5's publisher-side supersede:
an adopter feed pin behind a newer major its publisher has tagged carries a `supersede` line in
the adopter's `composed/evidence.json` at `origin/main` (fetched, then `git show`), under the
adopter's own perspective and reporting currency, naming the tag the publisher's real remote
carries, the day it was cut (read off the fetched tag object), and `amount = base x (ramp - 1)`
with `ramp` platform's EOL ramp from that day to the entry's own `as_of` and `base` the feed
line's own amount. Which composer wrote the evidence is read off the adopter's own platform pin
at that commit: a pinned composer that carries no supersede rule is a could-not-look naming the
tag, because no edit of the adopter's own could put the line there.

It prints, as numbers, on every run: pins behind a newer tagged major and how many carry the
line; untagged-feed pins and how many carry a hole (graded by `verify-untagged-pin-is-priced.sh`,
one grader per fact); retirement PRs opened/merged on `wargamer/retire-*` branches, counted off
GitHub and never graded -- opened is the clock's, merged is a human's.

Exit codes follow the gate contract: 0 true, 3 could not look (`SKIP:`), 1 false (`FAIL:`).
`supersede.py selfcheck` plants fourteen grades and proves each bites. What it refuses to grade
is in the module's docstring: whether a tag verifies (the identity-pinned verifier's claim, in
the untagged-pin check), the untagged hole's shape, and the eol feed's own time-varying price
(composition's selfcheck's seam).
