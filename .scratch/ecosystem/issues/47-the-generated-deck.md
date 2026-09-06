# 47 — The generated deck

Type: task (AFK)
Status: resolved
Blocked by: 03, 10

## Question

Build the `talk/` generator (lifted from pitch-v6 `build_deck.py`) that emits `talk/deck.md` from `talk/captures/`, the per-script capture write in `verify-all.sh` and `truth.yml` inside ticket 10's caged observation lane, marp-cli render in CI, `verify-demo.sh` per Q4, dated banners on `talk/deck.md` and the RUNBOOK beat table, pitch-v6 text/captures/scripts committed and `pitch-v6.mp4` as a hub release asset. Measure one run's stdout size before choosing commit versus workflow artifact.

## Notes

Graduated 2026-08-28 from ticket 20's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-08-29 by the /implement run of 2026-08-28 to 29. The deck is generated from the gate captures by talk/build_deck.py, never hand edited. All seven steps appear, each carrying the grade its own capture gave, in the capture own words. talk/verify-demo.sh is in the gate: it rebuilds the deck and grades the rebuild, checks every cited capture exists in the run named, and lints four phrases. The deck refuses to quote a headline number when truth.log has no run at that commit.

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
