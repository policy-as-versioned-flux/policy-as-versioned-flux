# TS-M1 skeptic pass — NOT REFUTED, corrections required

Re-derived 2026-09-02 from primary sources. Helper scripts in `../ts-m1-*.sh`;
throwaway trees in `../tree20/`, `../tree21/` (built with `git archive`, the hub
repo was not touched).

## Confirmed

1. Grade history (`ts-m1-hist.sh`, reading `<sha>:talk/captures/verify_demo_verify-demo.out`):
   run 9 FAIL (missing captures), 10/11/12 **PASS**, 13, 15, 16, 17, 18, 19, 20, 21 FAIL
   `FAIL: talk/deck.md has been hand edited or is stale; run python3 talk/build_deck.py`.
   Run 14 (`gh run view 33435351306`) never reached the gate — the CLI-install step failed —
   so eight consecutive *graded* runs is right.
2. `.github/workflows/truth.yml:38` `OBSERVATION_LANE: "talk/truth.log drift/samples.jsonl talk/captures observations"`;
   the cage (`:126-144`) exits 1 on anything staged or left outside the lane. deck.md is outside.
3. `grep -rn "build_deck\|deck" .github/workflows/` → no match (exit 1). Only truth.yml and
   twin.yml exist. truth.yml's gate step is `bash talk/verify-all.sh` (`:96`); `build_deck` appears
   in no workflow and not in verify-all.sh.
4. False header premise at `talk/verify-demo.sh:31` (reached as `verify/demo/verify-demo.sh`,
   a symlink). A second false claim at `:44` — "CI renders it on the scheduled run"; `DECK_RENDER`
   appears nowhere under `.github/`.
5. Exactly 7 committed captures at a209496 end in `FAIL`, verify_demo among them; TRUTH run 21
   says `fail=7`. So it is one of the seven reds.
6. Ticket 66 open; REVIEW-2026-08-31:83 M18.
7. "Goes stale within one run" — verified by experiment: deck built from run-20 captures passes
   `build_deck.py --check` against run-20 captures (exit 0) and FAILS against run-21 captures on
   five step-4 figures. `git diff 62eddf8 a209496 -- talk/captures/verify_e2e_...step4...out` shows
   the churn is a per-run cluster name/run id (`dsample-33556795181` → `dsample-33558850420`) and an
   OpenSSL error pointer (`285BED407E7F0000` → `281B2D59A47F0000`).

## Corrections

- **Not red on every scheduled run.** Runs 10, 11, 12 graded PASS. Cause: until run 12 the
  committed e2e captures were all SKIP, matching the locally-built all-SKIP deck. Run 12 was the
  first run whose captures moved (steps 2/3/5 → PASS), so run 13 was the first FAIL.
- **"Cannot pass on the clock" is overstated.** verify/demo sorts before verify/e2e in the gate
  glob (stated at `talk/verify-demo.sh:28-33`), so on the clock it grades the committed deck against
  the *previous* recorded run's captures. A local `python3 talk/build_deck.py` over the newest
  recorded run's captures reproduces the clock's beats exactly — proven: in `tree21/`, with no CI
  env set, the rebuild gives `PASS PASS PASS FAIL PASS PASS PASS`, identical to the run-21 capture's
  rebuild. Only step 4 is `scheduled_only` and its capture is FAIL, so the local downgrade never
  fires. Committing that file makes the next run green; the run after goes red again on step 4's
  volatile figures.
- **"Permanently unfixable by any estate change"** — right about the *estate* (no unit-repo change
  can help), wrong as "permanent": it is a hub-side instrument fault with an open hub ticket (66).
- **Line 27 of the deck is not wrong.** `talk/truth.log records no run of the truth surface at this
  commit` is true as generated: the clock records the TRUTH line one commit *behind* the record
  commit (run 21's line says `hub=7b92990`, the parent of a209496), so `truth_tail()` can never match
  the deck's own commit. What is wrong on the shipped deck is the six SKIP beats and their local
  reasons ("KinD cluster 'driftwood' absent", "python lacks jsonschema/pyyaml") where the clock
  observes PASS PASS PASS FAIL PASS PASS.
