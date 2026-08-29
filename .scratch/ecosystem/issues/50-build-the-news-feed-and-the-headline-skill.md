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
