# 47 — The generated deck

Type: task (AFK)
Status: open
Blocked by: 03, 10

## Question

Build the `talk/` generator (lifted from pitch-v6 `build_deck.py`) that emits `talk/deck.md` from `talk/captures/`, the per-script capture write in `verify-all.sh` and `truth.yml` inside ticket 10's caged observation lane, marp-cli render in CI, `verify-demo.sh` per Q4, dated banners on `talk/deck.md` and the RUNBOOK beat table, pitch-v6 text/captures/scripts committed and `pitch-v6.mp4` as a hub release asset. Measure one run's stdout size before choosing commit versus workflow artifact.

## Notes

Graduated 2026-08-28 from ticket 20's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.
