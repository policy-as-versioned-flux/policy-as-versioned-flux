# 83 — The TRUTH line says what it measured

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

`pass=57 fail=7 skip=18 total=84` cannot tell a loosely coupled eco-system from one party testing itself. Platform owns 45 of the 84 scripts and 29 of the 57 passes; 24 of those 29 grade platform's own modules against platform's own fixtures. On the truth-surface auditor's classification, 20 of 57 passes turn on an artefact published by another party or on live external state, 5 are simulations, and 12 of the 18 skips can never look on the runner. Nothing states the ceiling.

1. Tag every script in a committed manifest with its class: estate-observation, self-proof, simulation, meta. Most scripts already say which they are in their header. Emit the split in the TRUTH line, for example `pass=57 [observed=20 self=31 simulated=5 meta=1]`.
2. Publish the structural ceiling beside the number, derived from the same manifest, and fail the gate if a script skips for a reason the manifest does not declare.
3. Step 2's PASS line says "a merged pin bump re-prices tuppence" about an offline probe on a throwaway copy. Give it step 3's SYNTHETIC wording, and record that the only real merged bump moved no money.
4. `schedules.py:561` emits nothing for the eight server-side ruleset questions when it cannot look. A question that emits nothing is a fourth outcome. Print a SKIP with the reason.
5. Ticket 59's fall-checker reads the same manifest so a fall is compared class by class.

Done = the TRUTH line carries the split and the ceiling; every skip on the next citable run is either declared in the manifest or fails the gate; the deck quotes the split, not the bare number.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R3 and R5. Findings: truth-surface/TS-M6, TS-C2 (refuted as critical, kept as the ceiling), demo-steps/DS-F3, truth-surface/TS-M2 (ruleset half). Whether the ceiling is cosmetic or load-bearing is ticket 75 Q8.

## Answer

**2026-09-04.** Built on branch `ticket-83-the-truth-line-says-what-it-measured`, hub only. No
enactment repo is touched: the estate's scripts are classified, not edited.

Map line: The TRUTH line carries the split by class and the ceiling; an undeclared could-not-look
and an unplaced script are now reds, and the deck quotes what the run measured.

### What was built

- **`talk/verify-manifest.txt`** — one line per script the gate discovers,
  `path | class | skip`, with a trailing comment for every borderline call. 99 scripts are
  discovered at HEAD; 8 are excluded and declared in `talk/verify-exclusions.txt` (the six
  identity scripts ticket 90 shelved on this same branch, plus two argument-taking helpers), so
  91 are run. The manifest carries 97 lines: the 91 run, plus a kept-and-inert line for each of
  the six identity scripts recording what it would have measured. Two of the 97 name scripts that
  live on unit build branches the owner has not pushed, so run 70 printed two NOTE lines and
  graded 97 rows. Classes: `estate-observation`, `self-proof`,
  `simulation`, `meta`. The skip column is `-` (no could-not-look expected), `never: <regex>` (the
  runner cannot do it as built) or `waits: <regex>` (the estate's state has not arrived).
- **`talk/truth_manifest.py`** — the only counter. Parses the manifest, judges a SKIP against its
  declared pattern, checks coverage in both directions, computes the split, the skip split and the
  ceiling, and reads a TRUTH line back (`parse_truth`, `measured`). CLI: `check`, `paths`, `judge`,
  `isnever`, `summarise`, `selfcheck`.
- **`talk/verify-all.sh`** — loads the manifest before anything runs. A discovered script with no
  manifest line is a FAIL whatever it exits; a SKIP whose last line does not match its declared
  pattern is a FAIL; a `never` script that passes is a FAIL (the ceiling was stale). The TRUTH line
  now reads
  `pass=P [observed=a self=b simulated=c meta=d] fail=F skip=S [never=x waits=y] excluded=E total=T ceiling=C`.
  New `--selfcheck` proves the instrument over a fixture of nine tiny scripts without touching the
  estate; a fixture run stamps `fixture=1` and is never citable.
- **`verify/truth-line/verify-truth-line.sh`** (new, discovered, `meta`) — the gate's own check on
  all of this: the loader bites, `verify-all.sh --selfcheck` bites, the manifest covers what is
  discovered right now, and the last recorded TRUTH line's arithmetic holds.
- **`talk/build_deck.py`** — the title slide carries a `measured:` sentence computed from the
  quoted TRUTH line by `truth_manifest.measured()`, and `--check` FAILs a deck that quotes the line
  without it. A deck therefore cannot state a split the run did not carry. `talk/deck.md`
  regenerated at the same run 22 it already named.
- **`verify/e2e/step2_reprice.py`** — the PASS now says SYNTHETIC, names the throwaway copy, and
  records the fact: the one Renovate feed-pin bump that really was merged is driftwood #20
  (`feeds/threat-register` v1 → v2); its diff to driftwood's `composed/evidence.json` moved three
  version fields over three lines — the source pin's `version`, and the repricing record's
  `old_version` and `new_version`, all v1 → v2 — and no money: `old_price` and `new_price` are
  both 19558.549772440045, unchanged either side of the bump. Verified by
  `git diff 27f1cf2^1 27f1cf2 -- composed/evidence.json` in the driftwood clone.
- **`verify/e2e/verify-e2e-step7-honesty.sh`** — steps 2 and 3 are probes over material they make
  themselves, so a PASS from either that does not say SYNTHETIC is now UNGRADED. Selfcheck extended
  on its own planted estate (caught without the word, not caught with it).
- **`verify/schedules/schedules.py`** — 3b extracted to `ruleset_line()` and given every branch a
  verdict. The offline run now prints nine named could-not-looks where it printed nothing; its
  selfcheck covers both silent branches. Deliberately minimal: step 4 is ticket 56's.
- **`talk/RUNBOOK.md`** — a new "What the number is made of" section under §6.
- **`tests/test_truth_manifest.py`** — 16 tests at the seam.

### The contract ticket 59 builds against

Written in `talk/truth_manifest.py`'s module docstring so 59 need not reopen this ticket. In short:
read two consecutive lines with `parse_truth()`; a FALL is any class's pass count falling, `fail`
rising, `ceiling` falling with no manifest change in the same commit, or `total` falling with no
exclusions change — and a pass that became a skip *inside one class* is a fall even when `fail` is
unchanged. Accepted falls live in a committed `talk/verify-falls.txt` of `run=N | reason` lines,
validated the way exclusions are. The manifest is the shared input; a class is never re-derived
from a script header at check time. `truth_manifest.py` implements `parse_truth()` and deliberately
none of the comparison.

### Decisions (all delegated, ADR-0025, 2026-09-04)

1. **Format and location: `talk/verify-manifest.txt`, `path | class | skip`, beside
   `verify-exclusions.txt`.** Not YAML. Discovery, exclusions and now classification are one
   family of facts about the same list, read by the same shell, and a line-per-script file diffs
   one line per change in review. The skip column runs to end of line so a regex may use `|`.
2. **The classification rule: a pass is an observation of the estate only when its verdict turns
   on the CONTENT of another party's artefact or on live state outside the script's own
   repository.** Using another party's schema or engine as the *ruler* to grade your own artefact
   is self-proof, not observation — that is the distinction the bare count hides. Every borderline
   call carries its reason in the line's own comment (feeds' envelope schema, the insurer pricing
   its own quotes through platform's `fair.py`, ico's penalty feed resolving a real nist tag).
   A script whose live tail needs a cluster is classed by what its PASS would rest on, so the
   cluster tails are `estate-observation` with `never:`.
3. **A declared skip matches on the REASON, not the path.** The pattern is a case-insensitive
   `re.search` against the script's last line. A script may not skip for a new reason under an old
   declaration — that is precisely the hiding place the ticket names. Two limits belong here.
   - **The 160-character cut (fixed 2026-09-04).** `verify-all.sh` used to judge the same string it
     printed, cut at 160 characters. On this branch's own run 70 the runner's absolute path pushed
     `verify/tier-binding`'s declared phrase past the cut and a correctly declared could-not-look
     was graded `FAIL (undeclared skip)`; the citable line said `fail=13 skip=15 [never=9 waits=6]`
     where the honest figures are `fail=12 skip=16 [never=9 waits=7]`. The judge now sees the whole
     last line and the cut is display only, with a selfcheck leg whose declared reason only matches
     past character 160. A pattern may sit anywhere in the line.
   - **An aggregate reason still hides a new one (open).** Four declared patterns match a sentence
     that COUNTS could-not-looks rather than naming one, so a new underlying reason still passes
     under the old declaration: `insurer/verify-insurer-quote.sh` (`[0-9]+ of [0-9]+ checks could
     not be looked at`), `platform/verify-publisher-gate.sh` (`part(s).* could not look`),
     `verify/e2e/verify-e2e-step6-provenance.sh` (`could not (be )?look`) and
     `verify/feed-contract/verify-untagged-pin-is-priced.sh` (`could not look at the signature`).
     Narrowing them means each of those four scripts naming its own reason on its last line —
     four scripts in four repositories — so it is recorded as a known limit in
     `talk/verify-manifest.txt`'s header, not silently carried.
4. **The ceiling counts the five version-line-dark scripts as `waits`, not `never`, so the ceiling
   is the larger number.** They are dark because `distribution/versions.yaml` declares one major
   line — the estate's own state, which ticket 84/86 changes without touching the runner. `never`
   means the runner as built cannot do it. Keeping the two apart is what makes `ceiling` mean
   something: the day 84 lands, `waits` falls and `pass` rises with no manifest edit.
5. **The undeclared-skip check fails immediately. No grace run.** A grace run is a green that could
   not look, which is the thing this whole ticket exists to refuse. It is safe to be strict because
   every skip of the last real run (run 65, 22 of them) was replayed against the manifest before
   commit and every one is declared; the three that were not are fixed in the file.
6. **A manifest line whose script is missing is asymmetric: a fail for `verify/`, a NOTE for
   `.estate-clone/`.** The hub commits a script and its line together, so a hub line with no script
   is rot. A unit is an independently versioned repository the hub only clones, and a script that
   exists on its build branch but not yet on its main is the normal state of this eco-system
   between a builder's commit and the owner's push. Failing for that would make the hub's record
   hostage to another party's release train, which is the coupling NORTH-STAR §2 refuses. **Two**
   lines are in that state today, not five: run 70 (hub `b2e87fc`) printed exactly two NOTE lines,
   for `.estate-clone/driftwood/twin/verify-twin-sweep-moved.sh` and
   `.estate-clone/platform/shift-left/verify-tier-binding.sh`. The earlier count of five came from
   comparing the manifest against run 65, whose hub commit (`824959d`) predates three hub scripts
   this branch adds — `verify/truth-line/verify-truth-line.sh`,
   `verify/tier-binding/verify-tier-binding.sh` and
   `verify/feed-contract/verify-untagged-pin-is-priced.sh`. Those three are hub scripts committed
   with their lines, present at HEAD, and were never in this state. The note prints on every run,
   so the rot stays loud.
7. **A separate `verify/truth-line/verify-truth-line.sh` rather than living only inside
   `verify-all.sh`.** The discoverer is not discovered, so nothing would ever have run the
   instrument's own selfcheck on the clock — the same gap ticket 55 found in step 7. The script
   costs about two seconds and makes ticket 83 gradeable by the gate like every other ticket.
8. **It does not duplicate ticket 76's `verify/every-green/`.** That one reads the SHAPE of every
   discovered script and refuses a printed SKIP that reaches exit 0: *was this green honestly
   reached*. This one reads the manifest: *what does this green rest on, and was this
   could-not-look expected*. Both scripts' headers now say so in the other's terms, and neither
   re-runs the other's question.
9. **`verify/local-clock/verify-local-clock.sh` is `meta` with a `never:` skip.** Its marker exists
   only on the owner's machine, so on the runner it is outside the ceiling by construction, and it
   grades a clock rather than the estate.
10. **A `FAIL manifest[row]:` is printed but not counted.** A script the manifest does not place
    already gets a FAIL row of its own, whatever it exited; counting the coverage problem too would
    have made `fail=` overstate how many scripts are wrong. One wrong script, one count.
11. **`talk/deck.md` was regenerated at run 22, the run it already named**, not at the newest run.
    The deck's identity is the run it describes; ticket 83's change is what it says about that
    run's line, and run 22's line honestly says it carries no split.
12. **A clean seam is left for ticket 77.** `parse_truth` keeps each unit's value as text
    (`units=[driftwood=4b28aa3@v1.2.0]` parses today), so adding the tag beside the SHA needs no
    change here.
13. **The three adopters' `verify-reconcile.sh` are `self-proof`, not `estate-observation`
    (2026-09-04).** Decision 2 classes a script by what the PASS it can actually reach rests on.
    On the scheduled runner there is no cluster, so the only PASS these three can reach grades the
    adopter's OWN committed `drift/samples.jsonl` — the adopter's file, in the adopter's
    repository. That is self-proof by decision 2's own words, and the line's own comment had said
    as much while the class said otherwise. The estate-observation path is the live one below
    `need_substrate`, where facts 1 to 3 read the publishers' real remotes; it needs a kind
    cluster and never runs on the runner. Each line now names that path. The re-class moves no
    count on either recorded run — all three FAIL on runs 65 and 70 — but the day the lane sample
    grades green it moves up to three passes from `observed` to `self`, which is the point: the
    number would otherwise have credited the estate with an observation of a committed file.
14. **`measured()` counts the ceiling's `never` population, not the skip split's (2026-09-04).**
    Two different numbers can be called `never`: the skip split counts the never-classed scripts
    that SKIPPED, while the ceiling subtracts every non-excluded never-classed row whatever it
    exited. They diverge the moment a never-classed script fails instead of skipping, and the
    published sentence then stopped adding up. `measured()` now states `total - excluded -
    ceiling`, recovered from the line itself, and keeps the skip split's number inside the skip
    clause where it belongs. `verify-truth-line.sh` step 5 grades this against a planted divergent
    line and against the last recorded line.

### Verified

- `.venv/bin/python -m pytest tests/test_truth_manifest.py -n0 -q` → 17 passed.
- `.venv/bin/python -m pytest tests/test_build_deck.py -n0 -q` → 10 passed.
- `bash talk/verify-all.sh --selfcheck` → PASS (red first: the fixture caught a broken
  `never`-detection in the draft, which is why `truth_manifest.py isnever` exists).
- `bash verify/truth-line/verify-truth-line.sh` → PASS (red first: it named itself as the one
  discovered script with no manifest line).
- `bash verify/e2e/verify-e2e-step7-honesty.sh selfcheck` → PASS, including the new SYNTHETIC leg.
- `.venv/bin/python verify/schedules/schedules.py selfcheck` → ok; `check --offline` now prints
  nine server-side ruleset lines where it printed none.
- `.venv/bin/python talk/build_deck.py --check talk/deck.md` → no bad rows; breaking the
  `measured:` line by hand produces one.
- **The replay (re-run 2026-09-04 against the fixed files).** Two real grade tables, fetched with
  `gh run view --log` and replayed row by row through `truth_manifest.summarise`:
  - run 65 (94 rows, hub `824959d`) → `pass=59 [observed=13 self=37 simulated=6 meta=3] fail=11
    skip=16 [never=9 waits=7] excluded=8 total=94 ceiling=77`; 0 undeclared, 0 stale `never`.
  - run 70 (97 rows, hub `b2e87fc`, this branch's own run) → `pass=61 [observed=13 self=37
    simulated=6 meta=5] fail=12 skip=16 [never=9 waits=7] excluded=8 total=97 ceiling=80`;
    0 undeclared, 0 stale `never`. Run 70's own printed line said `fail=13 skip=15 [never=9
    waits=6]`: that one row is the truncation bug, and it is the whole difference.
  The earlier figures in this Answer (`skip=22 ... excluded=2`) were replayed before ticket 90's
  commits on this same branch excluded the six identity scripts; six declared `never` skips became
  exclusions, which is where `skip 22 → 16`, `never 15 → 9` and `excluded 2 → 8` come from.

**The citable split comes from the next clock run, not from here.** The figures above are a replay
of a recorded run and a fixture proof of the instrument; no hand-run line was appended to
`talk/truth.log`. `talk/verify-all.sh` was not run over the estate by this builder (build brief).

### Not done

- The auditor's classification counted 20 observed of 57; this manifest's rule gives 13 of 59 on
  run 65. The difference is decision 2 being stricter than the audit was about a party's schema or
  engine used as a ruler. The number is lower and the rule is written down; if the owner wants the
  looser reading, one column changes.
- Item 3's second half is recorded in step 2's PASS wording, not fixed: the pound-inputs defect
  that made the real bump move no money is tickets 77 and 79 (ticket 75 D2).
- The four aggregate `waits:` patterns named in decision 3 still let a new underlying reason hide
  under an old declaration. Fixing that means four scripts in four repositories naming their own
  reason; it is recorded in `talk/verify-manifest.txt`'s header, not built here.

## Comments

**2026-09-04, review fixes.** Seven findings against this ticket's own build, all fixed on the
same branch. Verified by the commands in `### Verified`, re-run.

1. **BLOCKING, fixed.** `talk/verify-all.sh` judged the same 160-character-cut string it printed.
   On run 70 the runner's absolute path pushed `verify/tier-binding`'s declared phrase past the
   cut and a correctly declared could-not-look was graded `FAIL (undeclared skip)`, so the citable
   line read `fail=13 skip=15 [never=9 waits=6]` where the honest figures are `fail=12 skip=16
   [never=9 waits=7]`. The judge now sees the whole last line (`lastfull`); the cut is display
   only. `--selfcheck` gained a ninth fixture script whose declared reason only matches past
   character 160, plus an assertion that the printed row is still cut. Red first: the new leg
   failed on the unfixed script with exactly the run-70 symptom.
2. **`measured()` and the ceiling now count the same population** — see decision 14 — with a new
   step 5 in `verify/truth-line/verify-truth-line.sh` that grades the published sentence against
   `total - excluded - ceiling` on a planted divergent line and on the last recorded line. Red
   first against the old `measured()`.
3. **The figures in this Answer were re-derived**, not adjusted: 91 run and 8 excluded of 99
   discovered at HEAD, and both replays re-run. Ticket 90's commits on this same branch moved six
   scripts from declared `never` skips to exclusions, which is the whole of the change.
4. **Decision 6's "five" was wrong**: two, named, with run 70's two NOTE lines as the citation.
5. **The three `verify-reconcile.sh` lines were re-classed** to `self-proof` — decision 13.
6. **Decision 3 now records the aggregate-pattern limit** beside the truncation one, naming the
   four lines, and `talk/verify-manifest.txt`'s header carries the same note.
7. **The merged bump's diff is described correctly**: three version fields over three lines, with
   `old_price == new_price` unchanged. The substantive claim — no money moved — stands.

Also: `talk/verify-exclusions.txt`'s header now records what excluding the six identity scripts
costs (five offline proofs that were reaching green on every run), and ticket 59 has a pointer to
the fall-checker contract, which lives only in `talk/truth_manifest.py`'s module docstring.

**Re-review fix, 2026-09-04 (the assistant, delegated).** Approved after one fix round, with three
minors closed here. `measured()` had gained arithmetic over `total` and `excluded`, which
`parse_truth` may return as `None`, so a TRUTH line carrying a ceiling but no `excluded=` raised a
TypeError inside `build_deck.py --check` instead of reporting a bad row. It now says the line does
not state the population rather than crashing or printing `None`. Two stale figures were corrected:
the selfcheck fixture is nine scripts, and `tests/test_truth_manifest.py` is 17 tests.

**Observation, 2026-09-04 (the assistant), for whoever next touches the TRUTH line.** `truth.yml`
runs on push as well as on the clock, and its cage pushes to `HEAD:${GITHUB_REF_NAME}`, so a push
to a feature branch records a full TRUTH line and its captures on that branch. Nothing is dishonest
about it: captures are observations, and the line carries its own `hub=` commit so a reader can tell
which tree it graded. But the run counter advances on branch runs, so run numbers are not a count of
scheduled runs, and a branch's line would enter `main`'s `talk/truth.log` if that branch merged
without a rebase. Checked on 2026-09-04: every `hub=` commit in `main`'s log is an ancestor of
`main`, so the citable record is clean today. Worth a rule (record only on the default branch, or
mark a branch run in the line) before it is not.
