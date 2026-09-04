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

*Caveat on the figure (reviewer, 2026-09-04).* **12 of 17 is true of the integrator's real
checkout, not of a builder's.** In a linked worktree only 8 of the 12 verify: gitsign cannot open
a tag reference through a `.work/` worktree's git layer, so the other 4 come back as
could-not-look and the script exits 3 (decision 6 below is why that is a SKIP and not a FAIL).
The reviewer confirmed those four by hand against real checkouts. Anyone reading 12 of 17 off a
builder's run will not see it; the number belongs to the integrator's wave run.

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
once from `twin.evolution_judge.CORPUS_KIND` into a shell variable and spent by both surface
strings; the only assertion made about the word is that the label the harness spent equals the one
the module declares. Flipping the constant changes both sentences and turns nothing red (proved by
flipping it to `held-out` and re-running: the closing line read *"7 held-out metrics"*, exit 0).
The unit test requires the constant to match what the corpus actually is — `harness-mechanism`
while every item is one the keyword table was fitted to, `held-out` once any is not — so the word
cannot be flipped without the corpus following it. *(Corrected 2026-09-04: the first version of
this paragraph claimed the label was read rather than typed, and both surface strings typed it.)*

**The class-level net.** `verify/every-green/every_green.py` + `verify-every-green.sh` read every
verify script the gate discovers and name any statement that **prints the `SKIP` verdict token**
and then ends in `exit 0` or in no exit at all. Run against the estate as it stands on `main` it
names exactly the seven the ticket lists and nothing else — no false positives across 95 scripts.
What it does **not** grade is a could-not-look worded as prose (`echo "(skipped: kyverno CLI not
found)"`, `say "4. skipped: kubectl absent"`), and the PASS line says so; see the 2026-09-04 note
below for the measurement behind that boundary and for what catches the prose kind instead.

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
9. **(2026-09-04) The net grades the `SKIP` verdict token and says so, rather than widening to a
   skip-word vocabulary.** Measured over all 95 discovered scripts: the wider rule cannot tell a
   false green from an honestly narrowed PASS, because the difference is in the PASS sentence. The
   print form was widened instead (same 26 statements matched, so no behaviour change today), and
   the boundary is stated on the PASS line, in the header and in the docstring. See the dated note.
10. **(2026-09-04) The corpus label is read into both surfaces and only agreement is asserted.**
    Not "the surface may type the word as long as a test pins it": a test that pins the word is
    the same red-on-flip the Answer denied. The word now lives in one constant, the test requires
    that constant to match what the corpus is, and no check asks it to be any particular word.

### The TRUTH line moves

Four hub checks that reported PASS now report SKIP on this machine, each naming what it could not
look at: `verify-provenance.sh` (no rekor-cli, no SPIRE), `verify-e2e-step5-twin-forecasts.sh`
(ticket 72's sweep observation), and `verify-e2e-step6-provenance.sh` (only in a builder's
worktree; PASS against real checkouts). `verify-proportionality.sh` still PASSes here because both
clusters and kyverno were reachable and every tail was observed — which is the point: the verdict
now depends on the instruments, and says so when they are absent. On a runner without kyverno the
seven platform scripts move from PASS to SKIP as well. `talk/verify-all.sh` was not run (builders
do not run it); the moved counts belong to the integrator's wave run.

### 2026-09-04 (later) — the spec review's two blocking defects, fixed

Both were the same fault the ticket exists to close, one level up: **a claim wider than what was
observed**, this time in the check's own PASS sentence and in this Answer.

**(1) The PASS line claimed the whole class and graded one shape.** It read *"a could-not-look is
exit 3 everywhere"*, while `every_green.py` read only a literal `echo "SKIP…"` / `printf 'SKIP…'`.
Re-scanning the pre-fix tree (hub `verify/` at `main` beside the eight unit checkouts, 95 scripts)
confirmed the reviewer: the net names the seven computed-semver scripts and does **not** name
`verify-proportionality.sh:75` (`echo "    (skipped: kyverno CLI not found — offline body proof
unavailable here)"`, then an unconditional PASS) or `verify-provenance.sh:48` (`echo "  (openssl
absent — …skipped)"`, then PASS), which were members of the same class.

*Widening was tried first and measured, not assumed.* A vocabulary rule — a print pairing a skip
word with an absence word — was run over all 95 discovered scripts. It named nine sites: the two
above (real false greens, fixed here) **and** `platform/currency-controller/verify-currency.sh:103,
105`, `platform/oscal/verify-upflow.sh:65`, `tuppence/reset/verify-reach-secrets.sh:49,125`
(which print a prose skip and then **narrow the closing sentence to what they did observe** — not
false greens; `verify-reach-secrets.sh` has three closing sentences precisely so it can), plus
`verify/sampler-wait-order/verify-sampler-wait-order.sh:99`, a `PASS:` line describing planted
selfcheck behaviour. So the vocabulary rule cannot separate a false green from an honest
narrowing: the difference lives in the PASS **sentence**, which no regex reads. Widening it would
have made this check red about two scripts that are not wrong, or forced a doctrinal edit to two
other units' scripts to keep it green.

**Decided (delegated, ADR-0025): narrow the claim, widen only the print form.** The graded shape
is now stated on the PASS line, in the script header and in `every_green.py`'s docstring: *a print
statement whose first printed token is the `SKIP` verdict word, reaching exit 0 or no exit at
all.* That token is the estate's verdict word (`verify-all.sh` reads the last line), so spending
it and then reaching exit 0 is a contradiction no reading of the script can excuse. The print form
was widened from `echo|printf` + quote to `echo`/`printf`/`say`/`note`/`warn`/`log`, with flags,
bare or quoted, behind a colour escape or an `==>` prefix — measured over the same 95 scripts,
both spellings match the same 26 statements, so it costs nothing today and catches
`say "SKIP: …"` tomorrow. **What catches the prose kind** is execution, not text: the per-script
`selfcheck_absent` leg, which re-runs the script with the instrument hidden and requires exit 3
with a `SKIP:` last line. That is a per-script obligation this net cannot impose; the four scripts
above do not carry one, and a ticket that gives every live-tail script that leg would close the
half this net cannot see.

Net after the fix: pre-fix tree — the same seven named, exit 1; current tree — 95 scripts, none
named, exit 0.

**(2) §7 claimed the label was read and it was typed, twice.** `verify-twin-evals.sh:129` and
`:243` typed `harness-mechanism` into the surface strings and `:136` asserted
`CORPUS_KIND == "harness-mechanism"`, so flipping the constant turned the check **red** — the
opposite of what the Answer, the source comment at `:133-134` and the commit message all claimed.
Fixed: the shell reads the label once (`CORPUS_KIND="$($PY -c 'from twin.evolution_judge import
CORPUS_KIND; print(CORPUS_KIND)')"`, and exits 3 if the twin will not import), hands it to the
harness, and both surface strings spend it; the assertion is now `LABEL == CORPUS_KIND` — the
label and the surface agree. `tests/test_evolution_judge.py` no longer pins the word either: it
requires the constant to be the one the corpus earns. §7, the source comment and this note say the
same thing, and the flip was run to prove it.

**Minors, also fixed.**

- **A dangling symlink crashed the scan.** `verify/demo/verify-demo.sh` is a symlink into `talk/`;
  where its target is absent, `open()` raised `FileNotFoundError` out of `scan()` and the shell
  printed a `FAIL` naming nothing. A could-not-read is a could-not-look: `read_tree()` now returns
  `(offences, could-not-read)`, `scripts_under()` reports an unwalkable root or directory instead
  of walking it as empty, and `every_green.py scan` exits **3** with `?? could not read <path>`
  when nothing worse was found. The script's SKIP line says the rest of the surface was not
  observed to be whole. Proved by planting a dangling symlink in `verify/every-green/`: the check
  printed the `??` line and exited 3, where before it exited 1 naming nothing.

**Ceiling recorded (`ponytail:` in `verify/lib-observation.sh` and `.estate-clone/platform/
lib.sh`): `selfcheck_absent` doubles the work.** The leg re-runs the *whole* script, so each of
the seven computed-semver scripts and both hub tails now do their work twice, plus the cost of
building the PATH symlink farm. Measured 2026-09-04: `verify-provenance.sh` 19.5s with the leg,
5.5s with it disabled (`PAV_SELFCHECK_CHILD=1`) — 3.5x, paid on every gate run. The ponytail names
the two ways out: expose the could-not-look branch as one function and re-run only that, or gate
the leg behind a flag the gate sets once per wave.

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
- **(2026-09-04) A `selfcheck_absent` leg for the four scripts that print a prose could-not-look**
  — `platform/currency-controller/verify-currency.sh`, `platform/oscal/verify-upflow.sh`,
  `tuppence/reset/verify-reach-secrets.sh` (two sites). None of them is a false green today (each
  narrows its closing sentence to what it observed), and none of them is graded by the class-level
  net, which reads the verdict token and not prose. Giving every live-tail script that leg is what
  would close the half this net cannot see; it touches three scripts in two units and is its own
  ticket, not a review fix.

**Re-review fixes, 2026-09-04 (the assistant, delegated).** Round 1 of the re-review found the
narrowed PASS line still carried a claim wider than the estate: it told the reader the ungraded
prose kind "is graded by each script's own selfcheck_absent leg", when only some scripts carry that
leg and no prose site does. Round 2 found the replacement traded that for a wrong count (four prose
sites, when the estate has five across three scripts, and a sixth in verify-access.sh), and that
both figures were typed rather than measured.

Both are closed by measuring instead of quoting. The run now counts how many discovered scripts
carry a `selfcheck_absent` leg and prints that figure, so the sentence follows the estate and the
ticket that gives a prose site its leg cannot falsify it. The number of prose sites is deliberately
**not** counted: a text scan cannot tell a false green from an honest narrowing, which is the whole
reason this net grades the verdict token, so the sentence says only that a prose could-not-look in
a script carrying no leg is graded by nothing. The SKIP line now subtracts the scripts that could
not be read, however many, instead of assuming one. The same boundary is stated in the script
header, in `every_green.py`'s docstring and in the test docstring that documents it.
