# 97 — A flip nobody recorded goes red

Type: decision (HITL)
Status: open
Blocked by: none

## Question

`twin/ENACT_MODE` is one word in a checked-in file, and it decides whether the twin may merge and
may push to an enactment repository. Since 2026-09-04 nothing goes red when it moves. Pair the
switch with a companion record that names the mode, the commit that authorised it and the date,
and assert that the two agree. A recorded flip like `f959187` stays green. A flip nobody recorded
goes red, under a test whose name says which switch moved. Done = the owner has decided the shape
of the acknowledgement, one test asserts it, and flipping the mode without the record is proved
red.

## Notes

Charted 2026-09-04 from the round-2 review of the hub CI repair; the record is
`.scratch/ecosystem/CI-2026-09-04.md`.

**This is ticket 87's item 3, narrowed, and it should be answered with it.** Ticket 87 already
says: "`twin/ENACT_MODE` is a file the agent writes. Replace it with a declaration in a repo the
agent cannot push to, with a price attached, or record why not." I charted this ticket on
2026-09-04 without noticing that, so read the two together. 87 item 3 is the stronger answer,
because it moves the declaration out of the agent's reach; this ticket is the weaker one that
works where the declaration stays put. If the owner takes 87 item 3, close this as covered.

**Why this is HITL and not delegated.** It invents an authorisation shape: a file whose content is
"the owner said so, here". ADR-0025 delegates architecture and keeps authorisations with the
owner. The assistant should not design the form in which the owner's permission is recorded.

**The history, because both previous positions were wrong and the third should not be a guess.**

1. Until 2026-08-29 an autouse fixture in `tests/test_enact.py` exported
   `TWIN_ENACT_MODE=operations`, so the suite asserted a guard nobody shipped and the shipped
   default was asserted by nothing.
2. From 2026-08-29 the fixture only cleared an ambient variable, and one test hard-coded the
   shipped word. The note there predicted that a flip to `development` would turn thirteen tests
   red, "because a weakening that shows in a test is the only kind anybody notices".
3. On 2026-09-04 the owner flipped it, standing, and the prediction came true at thirty-five. The
   same CI run carried two unrelated real defects, a missing `jsonschema` pin and a dead
   `type: ignore`, and both were invisible behind the wall. The fixture now arms the guard at a
   named mode, which the reviewer proved is a STRONGER capability test: mutating `decide()` to
   admit everything moves the armed count from 0 failures to 39, where on the old arrangement it
   moved 35 to 40.

So a permanently-red test is not a signal, and no signal is not the answer either. The property
worth having is narrower than both: not "the mode is X" and not "the mode never changes", but
"the mode and the record of who authorised it agree".

**What is already done, so this ticket does not redo it.** Invariant 48 reports the ambient mode
on its detail line (2026-09-04). Ticket 96 carries it on the TRUTH line. Both make the mode
VISIBLE. Neither makes an unrecorded flip FAIL, which is this ticket.

## Questions for the owner

1. What shape should the acknowledgement take? A sibling file (`twin/ENACT_MODE.why`), a header
   inside `ENACT_MODE` itself, or a signed commit trailer?
2. Should the record name an expiry? A development window that nobody closes becomes the default
   by silence, which is how position 1 above happened.
3. Should the assistant be able to write that record, or only the owner? If the assistant can
   write it, the alarm catches accident but not intent.

## Comments

**2026-09-24, decided in three rounds. The build waits.**

The owner grilled this ticket on 2026-09-24. In each round, the assistant proposed an answer to
each question. The owner answered each round with a bare "agree". Under ADR-0025, a bare agree is
a delegation, so each decision below is labelled delegated. The owner then answered "record only".
That answer is owner-instructed: record the decisions, and do not build yet. So `Status:` stays
`open` until the build proves the Done line.

**The facts that shaped the answers, read on 2026-09-24.**

- Ticket 87 says that the ruleset is "the declaration the agent cannot write". That is false. The
  assistant pushes with the owner's `gh` token. It signs every commit with the owner's key,
  `~/.ssh/id_ed25519`, and no prompt stops it. `f959187` has a good signature, and the assistant
  made that commit. The assistant also approves and merges as `pavc-other-hand`. So a required
  review from a second identity does not keep `twin/ENACT_MODE` out of the assistant's reach.
- The hub got three rulesets on 2026-09-24. `main` has no pull-request rule. The eight unit
  repositories have no rule on `main`, from a ruleset or from classic branch protection. Ticket 87
  records the details.
- Outside the tests, three places set `TWIN_ENACT_MODE`. `twin/invariants/harness.py` and
  `talk/local-clock.sh` set `operations`. The selfcheck in `talk/verify-all.sh` sets each mode in
  turn.
- The TRUTH line gets its `enact=` field from `enact_mode()`, at `talk/verify-all.sh:308`. Nothing
  on that line reads a record.
- The `tests` job of the twin workflow failed on every scheduled run from 2026-08-28 to 2026-09-24.
  On 2026-09-24, the cause was `test_the_suite_is_green`, which fails on
  `flux_coverage_floor_is_still_reachable`. So a new red in that job is not a signal.
- No file in the hub held the owner's words of 2026-09-04. Only the assistant's memory held them,
  outside the repository. This entry is their first record in the repository.

**The owner's words that the first mode record cites.**

On 2026-09-04, in a Claude Code session, the owner wrote: "can we just always assume we're in development mode until further notice?"

On 2026-09-24, the assistant put round 2 of this ticket to the owner. Its Q6 (b) was a 28-day
development window from 2026-09-24 to 2026-10-22. The owner answered "agree".

**The decisions. Each is delegated, 2026-09-24.**

1. **Q1 (a). The alarm catches accidents only.** The assistant may write the record. The check
   catches a stray edit, a bad merge resolution or a subagent that goes past its scope. It does
   not catch an agent that records its own flip. This ticket stands. Ticket 87 item 3 records why
   no declaration is out of the assistant's reach.
2. **Q2 (b). Only `development` has an expiry.** `operations` and `other-hand` refuse enactment
   pushes, so silence in those modes fails safe.
3. **Q3 (b). `TWIN_ENACT_MODE` may tighten the mode, but it may not loosen it.** From strictest to
   loosest, the order is `operations`, `other-hand`, `development`. The guard ignores a looser
   value and says so.
4. **Q4 (a). The record is a sibling file, `twin/ENACT_MODE.why`, in YAML.** Only the check reads
   it. The guard continues to read one word.
5. **Q5 (b). The assistant may write an `operations` record alone, with its own reason.** A record
   for `other-hand` or `development` must quote the owner.
6. **Q6 (b). A `development` window ends 28 days after the newest entry, or earlier.** The first
   window runs from 2026-09-24 to 2026-10-22.
7. **Q7 (a). A lapse stops no work.** The guard continues to admit merges and pushes. The only
   effect of a lapse is a red.
8. **Q8 (a). The red is a gate check, `verify/enact-record/verify-enact-record.sh`.** A red drops
   the pass count, so the truth run records a fall. A fall needs a dated line in
   `talk/verify-falls.txt`. The Q7 text said that the TRUTH line shows a lapse. That was false,
   and Q8 replaces it.
9. **Q9 (b). The record holds a dated list of the owner's words.** Each entry names the file that
   holds its words. The check must find the words, inside quotation marks, in the same paragraph
   as the entry's date. The newest entry must be `by: owner` unless the mode is `operations`.

The Question asked for a record that names "the commit that authorised it". The record names the
owner's words instead, for two reasons. Under Q1 (a), a commit shows who pushed, not who decided.
Also, a file cannot name the commit that adds it.

The first record, as decided:

```yaml
mode: development
until: 2026-10-22
said:   # Oldest first. Append a new entry. Do not edit an old one.
  - on: 2026-09-04
    by: owner
    words: "can we just always assume we're in development mode until further notice?"
    where: .scratch/ecosystem/issues/97-a-flip-nobody-recorded-goes-red.md
  - on: 2026-09-24
    by: owner
    words: "agree"
    where: .scratch/ecosystem/issues/97-a-flip-nobody-recorded-goes-red.md
```

**What follows from the decisions.**

- The window ends on 2026-10-22. The assistant asks the owner for new words before that date. It
  writes them as a dated comment in this ticket, and a new entry cites that comment. After the
  build, a lapse makes the next truth run record a fall.
- If the assistant moves the mode to `operations` alone, its entry becomes the newest one. After
  that, only new words from the owner can loosen the mode.
- An agent that writes a false, dated quote gets a green check. Q1 (a) accepts this limit.

**The assistant's calls for the build, under ADR-0025.**

1. No git-history rule and no `flip_commit` field. The mode check and the expiry catch every case
   that such a rule would catch. An old record can agree with a new flip only if the mode moved
   away and then back. In that case, the authorisation in the record is still valid.
2. The check has a selfcheck. It must go red for six mutations:
   - The mode file moves, and the record does not.
   - The window lapses.
   - `until` is more than 28 days after the newest entry.
   - An entry's date moves, but the cited file has no words for the new date.
   - The newest entry of a `development` record is `by: assistant`.
   - A cited file does not hold its quote.

   A quote matches only inside quotation marks. So "agree" does not match "agreed".
3. `twin/ENACT_MODE` and `twin/ENACT_MODE.why` go into the push paths of
   `.github/workflows/truth.yml`. The truth workflow then grades an unrecorded flip at once.
4. The `## Answer` of this ticket names the check. So a lapse also turns
   `verify/derived-status/verify-derived-status.sh` red, until a dated paragraph here records the
   lapse. That is correct. During a lapse, the property that this ticket names is false.
5. Invariant 48 does not get the lapse date, although the Q7 text promised it. Q8 moved the red to
   the gate. A second reader of the record would add nothing.
6. The environment rule has three parts:
   - `enact_mode()` ignores a looser value, and each refusal names the ignored value.
   - The selfcheck in `talk/verify-all.sh` expects the stricter of the variable and the file.
   - No variable may point the guard at a different mode file. Such a variable would be a way to
     loosen the mode.

   The test at `tests/test_enact.py:269` changes.
7. The live proof is a tightening. In a throwaway worktree, the build moves the mode to
   `operations` without a record, and runs the check. If that change merged by accident, the guard
   would become stricter.
8. Three documents change. NORTH-STAR §6 gets a dated correction and the Q1 (a) limit. Its
   "development-window theatre" bullet says that ticket 87 protects `main` with a required review.
   It also says that the guard admits no other merge shape. Both statements are false on
   2026-09-24. NORTH-STAR §8 gets one line for this ticket. `CONTEXT.md` gets two terms,
   *development window* and *mode record*.

**What Done still needs.** The owner has decided the shape of the acknowledgement. Two parts of
Done wait for the build: the check that asserts it, and the proof that a flip without the record
is red.
