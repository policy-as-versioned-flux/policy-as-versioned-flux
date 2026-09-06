# 50 — Build the news feed and the headline skill

Type: task (AFK)
Status: resolved
Blocked by: 10, 21, 25

## Question

Ship `kind: feed, name: news` from the feeds repo with `payload.events[]` (`id, date, source, statement, provenance{url}`), its changed-rule file, and no niobium row. Make `steep` optional until bound in the twin signal schema. Package signal-classify plus evolution-judge as one Claude Code skill a human runs over the unbound pool, opening a PR on the adopter's overlay with a binding claim and an optional override. Wire a gate check that the skill's PR carries only existing claim kinds and that `derived_from` names them.

## Notes

Graduated 2026-08-28 from ticket 23's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The news feed carries a minimal payload. The classify-and-judge step is a skill a human runs, writing binding and override, and only override prices. A verify script proves niobium is absent from the feed.

Definition of done: its check is in `talk/verify-all.sh`. The run that recorded it is the TRUTH line of 2026-08-29.

> **Correction, 2026-09-06 (eco-system ticket 80 item 1).** The done-line above cites "the TRUTH
> line of 2026-08-29" as proof this ticket's check is in the gate. That citation is withdrawn.
> The line is run 7, `hub=918022b`, recorded at 2026-08-29T12:03Z, and `git ls-tree -r 918022b`
> carries three verify directories -- `verify/party/`, `verify/proportionality/` and
> `verify/provenance/` -- and none of the checks this ticket names. It was graded BEFORE the
> build it is offered as proof of, so it recorded nothing at all about this check. What this
> check actually rests on is whichever later run first discovered it, which the gate names for
> itself on every run. `verify/cited-truth/` grades this rule from today and refuses the next
> citation of a measurement that did not measure the thing.
