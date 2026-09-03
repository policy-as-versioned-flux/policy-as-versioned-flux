# 66 — The deck check grades the run its own TRUTH line names

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

verify-demo's on-clock premise — the scheduled workflow rebuilds and commits the deck — is false: truth.yml has no deck step and its cage refuses talk/deck.md, so the check reds every scheduled run whose grades moved and will red again on run 14. Take the no-lane-change route: grade the committed deck against the run its own quoted TRUTH line names, not against "this run"; note the alternative (widen the observation lane to include a generated deck) for the owner if drift-by-a-run proves annoying. Rebuild and commit the deck from the newest run's captures as part of landing. Done = a scheduled run with moved grades no longer reds verify-demo falsely, proven by the next TRUTH line.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M18 (demo check's false premise), minor deck-misstates-three-steps.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Two facts from the review. No workflow builds the deck: `grep -rn build_deck .github/workflows/` is empty, and `talk/deck.md` is outside OBSERVATION_LANE, so the check reds every scheduled run whose grades moved and nothing can clear it without an ADR-0024 decision to let the clock write a deck. And the deck carries no pound sign at all: none of driftwood's four real prices appears under talk/. Whether the £ beats become beats is fog on the map. Record: REVIEW-2026-09-02.md R12, truth-surface/TS-M1, completeness C7.

**2026-09-03, build (wave 1 of the everything-open run).** Built on hub branch
`ticket-66-the-deck-check-grades-the-run-its-own-truth-line-names`. The false red is gone in the
only way that does not touch the lane: the deck names its run and is graded against that run.
Proven locally three ways (a step-1 capture on disk rewritten to FAIL while the committed deck
stays green; a depth-1 clone whose HEAD's newest run is the deck's; a depth-1 clone whose deck
names an older run, deepened once and found). What remains is the clock's own word, below.

## Answer

**What was built (hub only).**

- `talk/build_deck.py`: a deck carries `<!-- deck run=N hub=H source=recorded -->`, quotes run N's
  TRUTH line, and is built from run N's captures read out of the lane commit that recorded them
  (`git archive <sha> talk/captures`), never off the disk. `--check PATH` grades a deck against the
  run it names (status, honesty-table cross-read, figures, the quoted line), and exits 3 with
  `could not look:` when the recording commit is unreachable. `--name PATH` prints
  `run=N hub=H commit=SHA`. `--out PATH` without `--run` builds a deck of the disk captures, which
  names `source=disk` and may quote no TRUTH line. The old "quoted line must match HEAD's sha" rule
  is gone: it could never match a rebuild, by construction.
- `talk/verify-demo.sh`: the two clock-only branches (beat comparison, `--check` over the committed
  file) now run everywhere, against the named run's committed captures. A shallow checkout is
  deepened once (`git fetch --deepen=100`), and otherwise the check says `SKIP:` with the reason.
  The committed deck must name a recorded run, or it is `FAIL:`. Drift-by-a-run (a newer run in
  the log than the deck names) is printed as a note, not graded. Header comment and PASS wording
  corrected: the PASS line names the run the committed deck was graded against.
- `talk/deck.md`: rebuilt from run 22's committed captures (`hub=14cc731`, lane commit `0dbdb32`),
  beats PASS PASS PASS FAIL PASS PASS PASS, quoting run 22's TRUTH line. `deck.html` is gitignored,
  so there is nothing to render into the commit.
- `tests/test_build_deck.py`: ten tests at the seam, against a throwaway git repository with two
  recorded runs, a `run=local` line, and disk captures that belong to neither run.
- `talk/README.md`, `talk/RUNBOOK.md`: what the name means and the rebuild cadence.
- `docs/adr/0024`: a dated note recording the lane is unchanged and why the alternative was not
  taken.

**Which check grades it.** `verify/demo/verify-demo.sh` (symlink to `talk/verify-demo.sh`),
capture `talk/captures/verify_demo_verify-demo.out`.

**Decisions, all delegated (ADR-0025).**

1. *How the deck names its run.* By `run=N` and `hub=H` from the newest TRUTH line with a numbered
   run (`run=local` is never nameable: a local run's captures are throwaway and never committed),
   in a `<!-- deck ... -->` marker and the quoted line. Captures get no run stamp: the lane commit
   already binds a run's line to its captures (both land in the one commit), so the pairing is
   checkable from git without touching `verify-all.sh`, whose push trigger would fire the clock.
2. *Where the named run's captures are read from.* The newest commit touching `talk/truth.log` at
   which the log's last TRUTH line is run N; `talk/captures` at that commit. Not `git log -S`: on
   a shallow clone the boundary commit "adds" the whole file, and `-S` would pair run N's line with
   a later run's captures. Unreachable is `CouldNotLook`, exit 3, `SKIP:` -- never PASS, never a
   read off the disk.
3. *The on-clock figure check moves to the named run too.* Both committed-deck checks are graded
   against the named run, everywhere. Grading the committed file against "this run" has no honest
   answer on or off the clock, since the clock does not write the deck.
4. *The committed deck names a recorded run, never `run=local`.* `python3 talk/build_deck.py` with
   no arguments builds the newest recorded run; `--run N` a chosen one. The RUNBOOK says: rebuild
   before a talk, read it, commit it. The check prints the lag as a note.
5. *The rejected alternative is recorded in ADR-0024's dated note*, for the owner: widening the
   lane makes the clock commit a declaration (prose rendered as a signed commit to `main` with no
   reviewer), the thing D1 exists to stop; the lag it would remove is printed, not graded.
6. *A bounded deepen inside a verify script.* `git fetch --deepen=100 origin` runs only when the
   name lookup returns 3 and the repository is shallow; a failed fetch falls through to `SKIP:`.
   The gate already needs the network to clone the estate, so this adds no new dependency.

**Verified.** `python -m pytest tests/test_build_deck.py -n0 -q`: 10 passed. `python3
talk/build_deck.py --selfcheck`: ok. `python -m mypy talk/build_deck.py`: no issues.
`bash verify/demo/verify-demo.sh` at the worktree: PASS naming run 22; with a step-1 capture on
disk rewritten to FAIL (and the honesty table to match): still PASS; in a `--depth 1` clone: PASS;
in a `--depth 1` clone whose deck names run 21: deepened, PASS with the lag note.

Map line: 66 -- the deck names the recorded run it describes and verify-demo grades it against that run's committed captures, everywhere; the lane is unchanged, lag is a note, the widened-lane alternative is the owner's to reopen (ADR-0024 note).

## Waits on the owner

- The ticket's own proof, "a scheduled run with moved grades no longer reds verify-demo falsely,
  proven by the next TRUTH line": the next `truth.yml` firing after this branch is merged to
  `main`. Its `talk/captures/verify_demo_verify-demo.out` should end `PASS: ... describing recorded
  run 22 ...` on the clock; the run after that prints the lag note (run 23 recorded, deck names 22)
  and still passes. The assistant cannot make the clock fire or move the date.
- Whether to reopen the lane: if the lag note grows tiresome, widening `OBSERVATION_LANE` to
  include a generated `talk/deck.md` is an ADR-0024 change to what the clock's signature vouches
  for. Recorded as rejected for now; the owner's call.
