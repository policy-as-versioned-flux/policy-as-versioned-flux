# 84 — Being behind costs something: cve and eol converters, supersede pricing, the retirement proposal

Type: task (AFK)
Status: open
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
