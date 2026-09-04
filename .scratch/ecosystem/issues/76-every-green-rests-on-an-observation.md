# 76 — Every green rests on an observation

Type: task (AFK)
Status: resolved (seven of the eight built; item 6 is ticket 78's, and is not done here)
Blocked by: none

## Question

Fourteen findings in the 2026-09-02 review share one root cause: a check reaches exit 0 from a path where the property was never observed. Close every one, and add a selfcheck to each so the class cannot return. The list:

1. Seven scripts under `platform/computed-semver/` print `SKIP:` and exit 0 when kyverno is absent: `verify-cage-engine.sh`, `verify-comparison-window.sh`, `verify-gate.sh`, `verify-rederive-bumps.sh`, `verify-generator-standing-check.sh`, and step 3 of `verify-corpus-generator.sh` and step 5 of `verify-witness-set.sh`. Exit 3.
2. `verify/provenance/verify-provenance.sh` and `verify/proportionality/verify-proportionality.sh` have no exit-3 path for their live tails and assert PASS after printing a note. Add one.
3. `verify/e2e/verify-e2e-step6-provenance.sh:88` selects tags with `git tag -l 'v*.*.*'`, which cannot match feeds' `threat-register/v2.0.0`, and prints "no signed tag yet" about a Rekor-validated publisher. Resolve each unit's tag shape from its own `publishes[]`, verify the newest tag per published line, and never print an absence that was inferred from a failed lookup.
4. `verify/e2e/verify-e2e-step5-twin-forecasts.sh` grades path existence and passes in the same run in which driftwood's twin-overlay and twin-scenarios checks fail on the same file. Step 5 must consume those verdicts, or run `emit-forward-intel.py --check` itself, and exit 3 naming ticket 72 until a dated sweep observation exists.
5. `driftwood/drift/five-facts.py:522-528` records `fired: false` for a falsifier that was never run. Carry `None` through so the grader's could-not-look branch fires.
6. `platform/wargamer/wargamer.py:200,232` hardcode `"signed": True` and `:324` asserts the literal. Derive the field from the commit or delete it. The signing itself is ticket 78.
7. `verify/twin-evals/verify-twin-evals.sh` scores seven heuristics at 1.000 against a baseline recorded once, and the evolution-judge eval scores a lookup table against its own values. Hold out a corpus the heuristics were not fitted on, or relabel the seven on the surface as harness-mechanism checks.
8. The five-fact sample prints fact 3 for the two publishers as three independent proofs when it is one chain. Say so in the capture text.

Done = each of the eight has a failing-before test or selfcheck, the TRUTH line moves by the honest amount, and no capture on the next citable run prints a green sentence about something the script did not observe.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R3. Findings: truth-surface/TS-C1, engineering/EQ-02, principles/P6-1, P6-2, P7-1, P5-3 (literal half), demo-steps/DS-F1, DS-F4, operability/O3, scope/F5, truth-surface/TS-M8, twin/TWIN-06, TWIN-07, security/SS-08 (literal half). The correct pattern already exists in `distribution/verify-render-version-tree.sh`. Items 1 and 2 were ticket 55's class and escaped it.

## Answer

2026-09-04. Seven of the eight items are built, each with a test or selfcheck that was red before
the fix. Item 6 (`wargamer.py`'s `"signed": True` literals) is **not done here**: ticket 78 owns
the proposer's signing, and 76 removing the literal while 78 makes a true value possible would
have two tickets editing the same three lines in the same wave. 78 does both, in one edit.

Map line: every green rests on an observation — a missing instrument now exits 3 in fourteen
places, each script runs its own could-not-look branch, and one hub check names the next one by
file and line.

### What was built

**1. The seven kyverno-absent SKIP paths (platform).** All seven now exit 3 through `lib.sh`'s
`skip()`. Six exited 0 outright; `verify-witness-set.sh`'s step 5 printed the SKIP and *fell
through* to the script's own PASS line, which is the same false green and worse. `lib.sh` gains
`selfcheck_absent <script> <tool>...`: it re-executes the script with the named tools unreachable
— each PATH directory holding one is rebuilt as a farm of symlinks to its other entries, so
python3 and pyyaml stay reachable beside kyverno — and requires exit 3 with a `SKIP:` last line.
Each of the seven calls it before it looks, and takes `--selfcheck` to run that leg alone.
`lib-selfcheck.sh` plants an honest and a false-green script and asserts both grade as planted.

**2. The two hub live tails.** New `verify/lib-observation.sh` carries `could_not_look`,
`pass_or_skip` and the hub's `selfcheck_absent`. `verify-provenance.sh`'s Rekor and SPIRE tails
and `verify-proportionality.sh`'s kyverno body proof and per-cluster dry-runs now name what they
did not look at, and one unlooked tail makes the whole script SKIP. Two distinctions were drawn
where the old code had one: SPIRE reachable with *no* registration entries is could-not-look
(nothing to read), SPIRE with entries that root elsewhere is FAIL (read, and false); `rekor-cli`
present with no entry for HEAD is could-not-look, because this repo's commits are not
keyless-signed and there was nothing to find.

**3. Step 6's tag resolution.** Every line in a unit's own `party.yaml publishes[]` resolves its
own newest tag through `feed_contract.newest_tag_per_line` (`<line>/vX.Y.Z` or bare `vX.Y.Z`), and
a line with no tag prints what shapes were looked for among how many real tags. Before, against
the real checkouts: *"7 of 8 anchored identity regexps matched ... and feeds have no signed tag
yet"* — false; feeds' `threat-register/v2.0.0` is in Rekor and the typed glob could never match
it, and platform's `policy/v4.0.0` was never reached either. After: 12 of 17 published lines
verified against Rekor, 5 genuinely untagged and said so.

**4. Step 5 consumes the adopter's verdicts.** It runs driftwood's own `verify-twin-overlay.sh`,
`twin/verify-twin-scenarios.sh` and ticket 72's `twin/verify-twin-sweep-moved.sh` and cannot
disagree with them. It exits 3 today, naming ticket 72 and the missing dated
`observations/twin-sweep.jsonl` firing. Before this change it PASSed.

**5 and 8 (driftwood).** `_falsifier_state` recorded `fired: (ok is False)`, so a falsifier that
was never run — the source is another party, its release.yml is not in this checkout,
`gitsign_verifies` is never called — recorded `false`, which reads as "ran and cleared" and rode
inside a PASS while silently disabling the grader's null-keyed could-not-look branch. It carries
`None` now. And fact 3 for a verified-source-only publisher says it is one link in the chain the
composed source's own fact 3 already observed, not a second proof; the graded capture prints
`fact 3 is ONE CHAIN, not 3 independent proofs` once, derived from the existing records.

**7. The twin's evals are relabelled.** The seven scores are `harness-mechanism` observations, on
the per-metric lines and on the final PASS line that reaches `talk/deck.md`. The label is read
from `twin.evolution_judge.CORPUS_KIND`, not typed into the shell, so holding a corpus out later
is one edit and the surface follows.

**The class-level net.** `verify/every-green/every_green.py` + `verify-every-green.sh` read every
verify script the gate discovers and name any `SKIP` statement that ends in `exit 0` or in no exit
at all. Run against the estate as it stands on `main` it names exactly the seven the ticket lists
and nothing else — no false positives across 95 scripts.

### Which check grades what

| item | graded by |
| --- | --- |
| 1 | each of the seven `--selfcheck`, `platform/lib-selfcheck.sh`, `verify-every-green.sh` |
| 2 | `verify-provenance.sh --selfcheck`, `verify-proportionality.sh --selfcheck` |
| 3 | `tests/test_every_green.py`, `feed_contract.py selfcheck` |
| 4 | `tests/test_every_green.py`, the script's own SKIP naming ticket 72 |
| 5, 8 | `driftwood drift/five-facts.py selfcheck` |
| 7 | `tests/test_evolution_judge.py`, `tests/test_every_green.py` |
| the class | `verify/every-green/verify-every-green.sh`, `tests/test_every_green.py` |

### Decisions (all delegated, ADR-0025)

1. **The seven scripts reuse `lib.sh` rather than carrying a copy each.** The first cut inlined a
   30-line selfcheck into all seven. `lib.sh` already owns this repo's could-not-look contract and
   is sourced by fourteen scripts, and the brief says reuse it; seven copies of a branch is seven
   places for it to rot apart. `selfcheck_absent` lives there, `lib-selfcheck.sh` proves it.
2. **The class-net catches the fall-through shape as well as `exit 0`.** `verify-witness-set.sh`
   printed a SKIP and exited nothing, reaching its own PASS — invisible to an exit-0 rule, and one
   of the seven. Measured across the estate first: the two rules together name the seven and
   produce no false positive, so the wider rule costs nothing.
3. **Step 5 runs the adopter's scripts rather than `emit-forward-intel.py --check`.** The finding
   was that step 5 passed in the same run in which those checks observed false on the same file.
   Consuming their verdicts is what makes disagreement structurally impossible; calling the python
   entry point would re-implement half the seam in the hub and could pass while the owner's own
   check failed. Kept to a list of three script paths so ticket 64 can loop it over three adopters.
4. **"Newest tag per published line" verifies every line that has one, and states the absence of
   the rest.** A line with no tag of either shape is not a could-not-look: the unit's real tag list
   was read and the shapes came from its own `publishes[]`, so the absence is observed. The output
   says what was looked for and among how many tags, which is the difference from the banned
   "absence inferred from a failed lookup".
5. **Item 7 is a relabel, not a held-out corpus.** `tests/test_evolution_judge.py` now asserts what
   makes the relabel true — every corpus item is one the keyword table already answers within the
   scorer's tolerance, and an item outside the table falls to the default whatever the evidence
   says. A held-out corpus is real work on four backtest orgs' dated positions and belongs in its
   own ticket; claiming skill in the meantime is the thing this ticket exists to stop.
6. **`gitsign: error resolving tag reference` is a could-not-look, not a FAIL.** `git tag -l`
   listed the tag, so it exists; gitsign's own git layer could not open it. That is what a linked
   worktree looks like to gitsign, so a builder running against `.work/` trees sees it and the
   integrator's real checkout does not. Grading it FAIL would be a red for a harness reason.
7. **The class-net is one hub pytest plus per-script `--selfcheck`, both.** They answer different
   questions: the scanner sees every script including ones nobody thought to fix, the selfcheck
   runs the branch. Neither subsumes the other.
8. **No new entries in `talk/verify-exclusions.txt`.** The TRUTH line is supposed to move by the
   honest amount; excluding the scripts that now SKIP would undo the ticket.

### The TRUTH line moves

Four hub checks that reported PASS now report SKIP on this machine, each naming what it could not
look at: `verify-provenance.sh` (no rekor-cli, no SPIRE), `verify-e2e-step5-twin-forecasts.sh`
(ticket 72's sweep observation), and `verify-e2e-step6-provenance.sh` (only in a builder's
worktree; PASS against real checkouts). `verify-proportionality.sh` still PASSes here because both
clusters and kyverno were reachable and every tail was observed — which is the point: the verdict
now depends on the instruments, and says so when they are absent. On a runner without kyverno the
seven platform scripts move from PASS to SKIP as well. `talk/verify-all.sh` was not run (builders
do not run it); the moved counts belong to the integrator's wave run.

## Waits on the owner

- **Pushing the platform branch** (`ticket-76-every-green-rests-on-an-observation`: seven
  computed-semver scripts, `lib.sh`, `lib-selfcheck.sh`, `computed-semver/README.md`). Committed
  locally; the guard refuses an enactment push.
- **Pushing the driftwood branch** (same name: `drift/five-facts.py`). Committed locally.
- **The next citable TRUTH run** against the merged unit branches, which is what turns the moved
  counts into a capture. It reads pushed unit heads.
- **No new signed tag is needed.** Step 6 verifies the newest tag *already cut* on each published
  line; five lines have none and the script now says so rather than inferring it.

## Not done

- **Item 6, the `"signed": True` literals in `platform/wargamer/wargamer.py:200,232` and the
  assertion at `:324`.** Ticket 78's, by the reasoning at the top of this Answer.
- **A held-out corpus for the seven heuristics.** Relabelled instead, with the fittedness pinned by
  test. Worth its own ticket.
- **`verify-twin-overlay.sh`'s own SKIP** (`platform/feeds/forward-intel.payload.schema.json` is
  not in the estate) is driftwood's, surfaced by step 5 consuming it, and not fixed here.
