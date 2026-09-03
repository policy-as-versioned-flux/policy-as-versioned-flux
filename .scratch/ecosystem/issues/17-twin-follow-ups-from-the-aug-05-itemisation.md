# 17 — Twin follow ups from the aug 05 itemisation

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Split twin build ticket 66 so the propose-only PR channel is not gated behind the Flux verdict, and relax `66 <- 65`. Give twin spec story 2 (git-versioned text is the source of truth) an owning ticket. Mark the demo-slice narrowing (P010/P012) rejected in the record and de-duplicate the register.

## Notes

AUG-05-CUT.md; reversals 3 and 4.

## Comments

- 2026-08-31 (ambition review): Re-cut: the 66/65 split ask is overtaken (Flux verdict closed unmeasured 2026-08-16; the propose-only channel demonstrably works — it landed the 2026-08-31 slice PRs). Close that half with a dated note and update the two stale twin build Status lines. Keep the spec-story-2 ownership, P010/P012 record-keeping and register de-dup asks.

## Answer

Resolved 2026-09-03. Pure record-keeping under `.scratch/`; nothing touches an enactment repo, a
tag, or code. No verify script is warranted and none was added: the only code-adjacent claim
(spec story 2 is held by the constitution invariant `store_rebuildable_from_git`) is graded by the
existing twin invariant suite, and that invariant was run alone as part of this ticket
(`python -m twin verify --only store_rebuildable_from_git`: 1 passed, exit 0). A check that
grades Status lines as derived rather than hand-edited belongs to ticket 59, not here.

**1. The 66/65 split half, closed with a dated note.** Overtaken, as the 2026-08-31 comment says.
The Flux verdict settled *unmeasured* from 2026-08-16T05:00Z (build ticket 70's reachability
finding; the owner chose to record it rather than restart the probe), so the chain
`65 → 66 → 67 → 68 → 70` was gating the enactment arm on a question with no answer. Recorded in
three twin files, each as a dated amendment beside the 2026-08-15 text rather than over it:

- `.scratch/twin/build/65-the-flux-falsification-verdict.md`: Status now reads `CLOSED UNMEASURED
  — 2026-09-03` (was `VERDICT PENDING`), with what follows for each branch, the drafted amendment
  (does not fire) and the checklist. Decision, delegated (ADR-0025): the 7/9 checklist is left
  as the 2026-08-15 record and the two open items close as *unmeasured*, not as met, because
  ticking a criterion that reads data the window never carried would be the act the ticket's own
  harness guard refuses. A dated bracket at the "blocking chain" paragraph and a closing section
  "Closed unmeasured — 2026-09-03" carry the reasoning. Corrected 2026-09-04 after review: the
  closing section named both harness guards as red; run that day, only
  `flux_coverage_floor_is_still_reachable` is red (`3/1966 sample(s) ... ceiling of 69.4%`) and
  `drift_window_is_actually_being_sampled` passes (`15 sample(s) in an open window, newest
  2026-09-03`). The section now quotes both readings and cites no memory file.
- `.scratch/twin/build/66-propose-only-enactment-prs-and-policy-as-a-signe.md`: `Blocked by: none
  — was 65, relaxed 2026-09-03`; Status now reads `PR CHANNEL IS THE ESTATE'S, NOT twin/'S —
  2026-09-03` (was `PR CHANNEL NOT WIRED`).
- `.scratch/twin/build/00-constitution.md`: a dated correction under "The critical path" relaxes
  `66 ← 65` and leaves the 2026-08-05 path as the record it is.

**2. Spec story 2 has an owning ticket: twin build ticket 01.** Its reading list now cites story 2
with the reason. Decision, delegated (ADR-0025): 01 already holds the story's words verbatim in
its "What to build" and its fifth criterion *is* `store_rebuildable_from_git`, so it owned the
story in everything but the citation; 10 and 11 own the pin and signature stories (61 to 64, 73)
and would carry story 2 as a neighbour rather than as their subject; a new build ticket 92 would
be a ticket with nothing to build, which is the shape the skeleton-as-ceiling guard exists to
refuse. AUG-05-CUT §2.5 and put-back 2 both name 01 first. One line changed.

**3. P010 marked rejected; the register de-duplicated by annotation, nothing deleted.**
`.scratch/drift-review-2026-08-27/evidence/PROVISIONAL_DECISIONS.md` gains a note under its title
and a `Status` line on P010 (rejected: build tickets 79-91 went to full depth, reversal verdict
`reverse`, owner confirmed full depth in REGRILL-ANSWERS row 3-4 on 2026-08-28) and on P012
(rejected; duplicate of P010, second transcript). Decision, delegated (ADR-0025): annotate rather
than delete or renumber, because `REVERSALS.json`, `DECISION_AUDIT.json`, appendix C,
`REGRILL-ANSWERS.md` row 3-4 and `drift-review.html` all cite P010 and P012 by id, and a deleted
entry breaks every one of them while an annotated one keeps the trail that two transcripts
captured the same question. Found while doing it, and handled the same way because leaving a
known triple beside a corrected pair is the record-keeping fault AUG-05-CUT §2.4 describes: P034
is a third capture of P010 (annotated rejected, duplicate), and P011/P013/P035 are three captures
of one other question (P013 and P035 annotated as duplicates of P011; P011's own verdict is not
this ticket's and is untouched). Recounted 2026-09-04 after review, which found the asserted
207 was not computed: the 211 headings were grouped by their question-time, and every group that
spans more than one transcript id was read. Four do: the P010 and P011 triples above; P037/P042
(the risk-tier question at 2026-08-20T10:50, one question in two transcripts, so P042 is now
annotated as a duplicate of P037); and P040/P044 (2026-08-20T19:30, two different questions,
not duplicates). Five duplicate captures, so 211 − 5 = **206** distinct decisions by that method,
and the register's header states the method and its limit (it finds only duplicates that share
a question-time). `REVERSALS.json`, `DECISION_AUDIT.json` and appendix C carry no status field,
only `verdict: reverse`, which already is the rejection in the reversal record; they are
generated evidence and were not hand-edited.

**4. What the 66 Status says, and why it does not say "criterion 1 met".** The comment's phrase
"the propose-only channel demonstrably works — it landed the 2026-08-31 slice PRs" was checked
against the record before being written into 66. Decision, delegated (ADR-0025): word it as the
discipline holding, not the channel. The thin-slice PRs (platform #5 at 2026-08-31T08:54Z first)
were opened by the assistant with `gh pr create` under the owner's account; the assistant's
`gh pr merge` was declined by Claude Code's permission classifier, not by `enact_guard.py`; the
owner merged every one of them by hand the same day (checked 2026-09-04 with `gh pr list
--state all --json mergedAt,mergedBy` on each repo: platform #3/#4/#5 at 13:52Z, driftwood #12,
tuppence #9 and ludlow #8 at 16:23Z, all `mergedBy: chrisns`); and hub `d81f202` the same day
fixed the guard's bare-remote hole that had admitted the pushes. Nothing in `twin/` opened them.
Corrected 2026-09-04 after review: 66's Status had read "pull requests opened, nothing merged",
which was false against that record; it now says the assistant did not merge and a human did. The eco-system's real proposer is each adopter's `propose-tier.yml`, which first
fired on schedule at 2026-09-01 12:01Z and returned `[]`; no proposal PR has ever opened (tickets
60, 74, 78). So criterion 1 of 66 stays half, and its other half is owned by ticket 74. The guard's
checked-in mode is `other-hand` since ticket 88 and is noted for the same reason.

**5. Conventions followed.** Twin build tickets record corrections as dated amendments beside the
original text (build tickets 70 and 78 set the precedent, and the constitution's own two dated
sections), so the 2026-08-15 Status paragraphs are kept under "*As written on 2026-08-15*" rather
than deleted. Decision, delegated (ADR-0025): `Blocked by` on 66 reads `none — was 65, relaxed
2026-09-03` rather than a bare `none`, so the relaxation is visible without a `git blame`; and
the constitution's critical-path paragraph gets a dated correction beside the 2026-08-05 text
rather than an in-place rewrite, following its own two dated sections.

**Not changed, on purpose.** `twin/README.md` line ~2597 and build ticket 70 lines 116 and 219
quote the 2026-08-15 Status lines (`VERDICT PENDING`, `PR CHANNEL NOT WIRED`) as what those files
read at the time of ticket 70's audit; they are that audit's record and are left as written.
`.scratch/ecosystem/map.md` is the integrator's at merge time (the Map line below).

Map line: [17 — Twin follow ups from the aug 05 itemisation](issues/17-twin-follow-ups-from-the-aug-05-itemisation.md) — the 66/65 split is overtaken and closed with a dated note (Flux verdict settled unmeasured from 2026-08-16); twin build 65 reads `CLOSED UNMEASURED`, 66 reads `Blocked by: none` and `PR CHANNEL IS THE ESTATE'S`, the constitution carries a dated correction; spec story 2 is owned by twin build ticket 01 (`store_rebuildable_from_git` is its test, run green); P010 marked rejected and P012/P034 (and P013/P035 of P011, P042 of P037) annotated as duplicate captures, nothing deleted, 206 distinct of 211 by a stated method; no verify script, record-keeping only.

## Waits on the owner

Nothing. No money, date, identity, authorisation or real person is decided here.
