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
