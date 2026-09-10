# 109 — A ticket's map line is not checked against the map, and four instruments carry a moving count

Type: task
Status: open
Blocked by: none

## Question

Two findings from ticket 48's second and third review rounds, both cheap, both about a record
saying something the estate never checks.

**1. Nothing compares a ticket's `Map line:` block with `.scratch/ecosystem/map.md`.** Ticket 48
carried a false present tense on the video by-product. It was corrected in the ticket's own
transcription of its map line and NOT in the map, so the live wayfinder kept asserting as fact a
release asset that does not exist. The review that found it said the cause plainly: nothing reads
the two against each other, so a divergence is invisible. A dozen lines comparing every ticket's
backticked `Map line:` block against the matching `- [NN — ` line, byte for byte, would have caught
it outright and costs nothing to run. That is the whole of item 1.

Grade the pair, not the prose. A ticket with no `Map line:` block is not a fault; a block that does
not match the map is. Say which of the two you believe when they differ, and why, because a reader
who sees the red will fix the wrong one otherwise.

**2. Four instrument headers carry a hand-maintained census that nothing reads and no argument
rests on, and it has been wrong twice.** `talk/build_deck.py` (twice), `talk/verify-demo.sh` and
`talk/verify-manifest.txt` each state how many recorded runs carry a `talk/captures/_grades.tsv`.
Ticket 48 shipped that number stale once, corrected it, and the correction itself shipped stale
after a rebase. It is now dated and anchored to a run, which is honest, and it still moves on every
scheduled run.

The review answered the obvious question against expectation: **deriving it is not cheap.** The
module's own `run_commit()` costs about 48 seconds of wall time in a full clone, and it is
unreliable in the gate's shallow checkout by the same reachability limit that already leaves runs
76, 84 and 88 unmeasurable. So the advice is to DELETE the moving number from all four instrument
sites, keep only the half that does not move — a table can lack a ROW for one script, and six of
run 186's own 120 captures do, on every table-carrying run — and leave one dated census line in the
ticket, where a stale number is a record of what was measured rather than a live argument in a
header a reader of a green meets.

Decide whether to delete or to derive, and record why. If you derive, price it first.

## Also charted here, from the same review, and smaller

- **The declared-row-count parser closes one construct of six.** `_phrase_table()` in
  `talk/build_deck.py` skips backtick fences and table rows when it looks for the sentence stating
  how many rows the refused-vocabulary table carries. A count sentence inside an HTML comment, a
  blockquote, a tilde fence or an indented code block still sets it, first match wins. Measured:
  deleting a row AND planting a matching count through any of those four is a silent green, with
  the record's visible prose still reading five while the lint applies four, and the phrase the
  lint exists for is the one that drops out. The code comment claims a rule wider than the code
  enforces ("The count is a sentence a reader reads, so neither may set it"). The one-line fix that
  closes the class outright: collect EVERY match and make disagreement, or more than one match, a
  named red.
- **An unclosed backtick fence inside that section swallows the rest of it,** because `fenced` is
  never reset at the next `## ` heading. It fails red, so nothing is hidden, but the message sends
  a reader looking for a missing table rather than an unbalanced fence.
- **A trivial one:** ticket 48's line 52 cites `map.md` line 52 for ticket 20's map line, which is
  line 53. The sentence is there and correct.

## Notes

Charted 2026-09-10 from ticket 48's review rounds 2 and 3. Item 1's evidence is ticket 48's own R1;
item 2's is its R2, twice. Neither is a false green in any check's primary job, which is why both
were returned as minor and neither blocked the merge.

Record: ticket 48's `## Review round 2` section and its round-3 findings; `talk/build_deck.py`'s
`_phrase_table()` and `grades_table()`; `talk/verify-demo.sh`'s header; `talk/verify-manifest.txt`
line 159.

## Answer — built 2026-09-10, review pending

The existing `verify/map-surface/verify-map-surface.sh` now compares exact ticket/map
transcriptions through `grade_map_lines()`. Its selfcheck plants changed, missing, duplicate and
truncated copies; focused seam tests also prove that a ticket cannot borrow another ticket's
matching entry. The comparison preserves inline code and significant whitespace. A mismatch
names its ticket and directs the reader to the reviewed map unless the ticket's Answer records
a later supported decision. There is no dated-correction exemption for a current transcription.

**Decisions (delegated, ADR-0025).**

- Grade the explicit format already used by ticket 48: `Map line:` followed by a backticked,
  complete `- [NN — ...` entry on one line. Historical prose summaries were never byte-for-byte
  transcriptions; they are counted and named separately on every run. A malformed explicit
  transcription is red. Tickets without a transcription are not faults. This deliberately
  leaves prose summaries ungraded rather than rewriting them into claims they never made.
- Prefer the reviewed live map on the four disagreements (33, 96, 98, 100): those entries carry
  the current summaries. Their former transcriptions remain under dated historical labels and
  each ticket now carries a current exact copy. Tickets 89 and 91 supplied reviewed summaries
  missing from the map altogether, so those entries were restored. Ticket 48 already agreed;
  its stale line-number citation now names ticket 20's map entry without a moving line number.
- Delete the moving census from all four instrument sites. Walking historical git to derive a
  number costs time and shallow-checkout uncertainty, and no argument requires that number.
  Ticket 48 retains the dated census; the instruments retain the concrete missing-row case.
- Refuse multiple row-count declarations, including identical ones, instead of picking the
  first. The existing backtick-fence and table-cell exclusions remain; every other match is
  collected, including more than one on one line. This conservative rule catches comments,
  blockquotes, tilde fences and indented examples without adding a Markdown parser. An unclosed
  backtick fence is named at the next section boundary or end of file, and fence state resets
  at a section boundary.

**Validation.** Tests use the established pure map-grade seam and the deck's public `check()`
filesystem seam. The first transcription test failed because no comparison existed. Six planted
count-declaration attacks then all passed incorrectly before the parser fix and all failed by
name after it. Tests cover missing/duplicate map entries, malformed transcriptions, inline code,
whitespace, wrong-ticket ownership and unclosed fences. Both instrument selfchecks pass. The
existing temporary-git test helpers now disable hooks/signing only for their synthetic fixture
commits: otherwise local global signing demanded a private-key passphrase and the hook tried
GitGuardian before any assertion could run. No real repository configuration or guard changed.

This checkout's exact-copy comparison reads eight agreeing transcriptions (including this one) and reports 37
historical summaries separately; the map's check references and links also resolve. These are
local verification results, not a citable TRUTH claim. Status stays open pending both reviews.

Map line: `- [109 — A ticket's map line is not checked against the map](issues/109-a-ticket-s-map-line-is-not-checked-against-the-map.md) — built locally, review pending: the existing map-surface check compares exact backticked ticket/map transcriptions byte for byte, refusing missing, duplicate, malformed and wrong-ticket copies and naming older prose summaries separately; the reviewed map wins a disagreement unless the ticket records a later supported decision, and current transcriptions have no correction exemption. Four stale transcriptions retain their history beside corrected copies, missing reviewed entries 89 and 91 are restored, and the four instrument census statements are removed while ticket 48 retains its dated record. The deck check refuses multiple row-count declarations instead of selecting the first and names unclosed backtick fences at a section boundary or end of file. Focused seam tests and both instrument selfchecks pass; no citable run of this change is claimed.`

### Spec-review correction, 2026-09-10

The reviewer planted a second space after the bullet in an exact transcription. The initial
classifier treated the damaged prefix as historical prose, so the pair vanished from comparison.
Six variants reproduced that escape before the fix. Classification now recognizes the intended
quoted-link or list-link shape before strict validation: doubled/missing spaces, damaged bullets,
missing/doubled opening backticks and space inside the label are named malformed, while genuine
historical prose retains its reported category. The grader selfcheck also plants the reviewer's
exact doubled-space defect. No exemption was added.

Independent Spec re-review confirmed the malformed-prefix finding closed; Standards reported
no findings in this ticket. Publication remains pending the configured secret-scan hook's quota
or authorization of the proposed local-scan substitute.
