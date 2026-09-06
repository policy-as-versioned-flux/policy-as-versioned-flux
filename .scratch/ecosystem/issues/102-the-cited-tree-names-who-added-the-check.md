# 102 — The cited tree names who added the check

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Close case D, the one residual route through `verify/cited-truth/`'s rule 1.

Ticket 80 built the rule: a paragraph offering a TRUTH line as proof that a check is in the gate
must cite a line `talk/truth.log` recorded, whose `hub=` commit this checkout can read, whose
**tree carries a check the ticket names** — or the ticket must carry a dated correction naming
that citation. Round 1 of review closed four cheap routes through it (a bare `verify/`, a
directory naming no script, a prefix match, and a correction supplying its own proof). One
survived, and ticket 80's Answer discloses it as not closable by reading the ticket text:

> **Case D.** A ticket that names, in its own Answer section, a check it does not own and the
> cited tree happens to carry, passes.

The round-2 reviewer found the narrowing that ticket 80 said did not exist. It is not a text
question at all — it is a **git** question, and `verify/cited-truth/` already reads git to resolve
the cited `hub=` commit to a tree.

**The rule to build.** Resolve the named check to its path in the cited tree. Then ask git who put
it there:

    git log --diff-filter=A --format=%s -- <path>

and require the adding commit's subject to **name the ticket number making the claim**. The build
brief's `Ticket NN:` commit convention is what makes a check attributable to the ticket that built
it. A ticket whose named check was added by a commit naming some other ticket, or naming none, has
not shown that the check is its own — so the claim falls back to the dated correction, exactly as
it does today.

**The escape, and it must be loud.** Some checks legitimately predate the convention or moved
between trees. So: *or* the ticket carries a dated **attribution line** naming the commit and the
ticket that added the check. Printed on every run like the exemptions rule 1 already prints, never
a silent pass.

## What was measured, 2026-09-06, before charting

All three figures were re-measured on this branch rather than taken from the review.

**1. The rule closes case D through run 7, and costs almost nothing elsewhere.** Of the **37**
hub verify scripts at `8348b8e`, **34** have an adding commit whose subject names a ticket. The
**three** that do not are exactly the three directories run 7's tree carries:

    verify/party/verify-party.sh              c9d0f20  Delete estate/ from the hub; verify and
    verify/proportionality/verify-proportionality.sh    talk move to root (mo-12)
    verify/provenance/verify-provenance.sh

`c9d0f20` names no ticket, so **every case-D route through run 7 goes red** under this rule, and
34 of 37 checks are unaffected.

**2. Rule 1's positive path is not proven by any real ticket today.** Of the **46** gate-proof
citations on the record at the merged head `8348b8e`, **43** pass by dated correction and the
other **3** are ticket 80's own paragraphs about run 7, passing through case D. So the branch that
says *yes, this citation really does prove the named check was already there* is exercised only by
the selfcheck and by 42 seam tests — never yet by a ticket. That is worth knowing before anyone
reads a green as evidence that the positive path works. (On the follow-up branch the count is 47
and 4: one more sentence about ticket 18's run 5 was added to ticket 80's Answer, and it takes the
same case-D route.)

**3. The `Ticket NN:` convention is not uniform, and the rule must not assume it is.** Six
spellings are in the log already:

    Ticket 39: ...            Tickets 62 and 77: ...      ecosystem ticket 47: ...
    ticket 61: ...            ecosystem ticket 28: ...    ecosystem: ticket 21 ... + ticket 52 ...

So the match is a case-insensitive scan for `tickets?\s+(\d+)` over the whole subject, collecting
**every** number it finds, not a `^Ticket NN:` prefix. A commit that builds two tickets' checks in
one go (`3e83a16`, tickets 21 and 52) must satisfy both.

## The decision this ticket must take

**`--follow`, or not.** `--diff-filter=A` names where the bytes first appeared *at this path*, not
who wrote the check. `verify/` moved to the repository root in `c9d0f20`, so for anything older
than that move the adding commit is the move. `git log --follow --diff-filter=A` gives a different
answer — for `verify/party/verify-party.sh` it gives `1f2b3d4 Add a machine-checked roles:
declaration per party`, which also names no ticket, so run 7 stays red either way — but `--follow`
takes a single file and not a directory, which is half of what a named check can be. Recommendation
to be decided in the build: **no `--follow`**, and let the attribution line carry a moved check;
the rule is meant to be cheap and legible, and a directory cannot be followed anyway.

## Two alternatives, both rejected by the round-2 reviewer

- **"The check must be absent from the prior recorded run and present in this one."** Rejected: it
  fails every legitimate *later* citation. A ticket may honestly cite a run well after the one that
  first carried its check, and this rule would call that a lie.
- **"The ticket's own diff added the check."** Rejected: it is the same git question in a worse
  form. The check would have to know which commits belong to the ticket, and that is not readable
  from the ticket file — which is the thing case D is stuck on in the first place.

## Also folded in, from round 2 of the ticket-80 review

**R2-1 is done**, in the ticket-80 follow-up PR, and is recorded here only so the trail is
complete: code spans and link targets are blanked before the phrase test, `not` joined
`_NEGATION`, and the negation window came down from 30 characters to 12 — at 30 it swallowed "no
run recorded it, so it is not citable", which disowns its own figure perfectly well. Four tests
and a selfcheck leg.

**R2-5 is not done**, and is this ticket's:

- **R2-5.** The three facts added for the D1–D5 ruling (ticket 13, `map.md`, ADR-0025) carry a
  marker sentence and no load-bearing one, unlike the other items after review F5. Give each a
  second sentence, so an entry gutted to its heading is red.

## Done

`verify/cited-truth/` refuses a gate-proof citation whose named check was added by a commit naming
no ticket, or naming a different ticket, unless the ticket carries a dated attribution line naming
the commit — and prints every such attribution as it prints every exemption. Red-first tests at the
seam with an injected git log, so the rule is exercised without a repository. Ticket 80's disclosed
case-D limit is struck from its Answer and this ticket's number put in its place. The three
ticket-80 paragraphs that pass through case D today either gain a dated correction or a dated
attribution line, and the run says which.

## Answer

Resolved 2026-09-06. Every decision below is labelled; under
[ADR-0025](../../../docs/adr/0025-the-assistant-decides-architecture-and-records-it.md) the
unlabelled default is **delegated** — the assistant decided, recorded the reason, and did not
interrupt the owner.

Case D is closed, and `verify/cited-truth/` was **extended** rather than joined by a second check:
the rule it already runs is the one that grew a clause, so there is still one row in the manifest,
one selfcheck and one place a reader looks.

### The rule now

A gate-proof citation passes rule 1 when the cited `hub=` tree carries a check the ticket names
**and git says that ticket added it**. The named check is resolved to its PATH in the cited tree —
a script token to the path it matches by suffix, a directory token to every `verify*.sh` the cited
tree carries under it — and then

    git log --diff-filter=A --format=%H%x09%s <hub> -- <path>

is asked who put it there. The adding commit's subject must name the ticket making the claim: the
number the ticket's own filename carries. Reading the history AS OF THE CITED COMMIT is what binds
the answer to the tree that was measured; a commit that added the path later is not in that log at
all, so no separate ancestry test is needed.

**The scan for a ticket number is a scan, not a prefix (delegated).** `tickets?\s+#?(\d+)`,
case-insensitive, over the whole subject, collecting **every** number, plus a trailing list
(`, and & + /`). Six spellings are in the hub log — `Ticket 39:`, `ticket 61:`, `Tickets 62 and
77:`, `ecosystem ticket 28:`, `ecosystem ticket 47:`, `ecosystem: ticket 21 ... + ticket 52 ...` —
and `3e83a16` built two tickets' checks in one commit, so a `^Ticket NN:` prefix would have
satisfied neither of them. The number must FOLLOW the word, and that is not fussiness: the
`--follow` answer for two of run 7's directories is `26770f8 Estate build: 27 tickets implemented
via dependency-wave workflow`, and a scan that also read `\d+\s+tickets?` would hand **ticket 27**
a check it never wrote.

### The `--follow` decision: no `--follow` (delegated), with what was measured

Re-measured on this branch at `caefdd3`, not taken from the charting:

| path | `--diff-filter=A` | with `--follow` |
| --- | --- | --- |
| `verify/party/verify-party.sh` | `c9d0f20 Delete estate/ from the hub; verify and talk move to root (mo-12)` | `1f2b3d4 Add a machine-checked roles: declaration per party` |
| `verify/proportionality/verify-proportionality.sh` | `c9d0f20` (as above) | `26770f8 Estate build: 27 tickets implemented via dependency-wave workflow (waves 2-9)` |
| `verify/provenance/verify-provenance.sh` | `c9d0f20` (as above) | `26770f8` (as above) |
| `verify/party/` (a directory) | `c9d0f20` | `c9d0f20` — **git accepted `--follow` and ignored it**, exit 0, no warning |

Three reasons, in the order they weigh:

1. **It changes no verdict here.** None of the three followed subjects names a ticket either, so
   every case-D route through run 7 is red both ways.
2. **Half of what a named check can be cannot be followed.** A directory is a legitimate named
   check — that is ticket 80's own rule — and git takes `--follow` on one without complaining and
   quietly does nothing with it. A flag that looks applied and is not is worse than an absent one.
3. **It is a trap for the ticket scan.** The one place `--follow` does change the answer is the
   place whose subject carries a number that looks like a ticket and is not.

A check that genuinely moved between trees is carried by the attribution line, which is the escape
this ticket built for exactly that case — with bind 4's qualifier: a moved check is carried only
where the moving commit names no ticket, and the line must name that moving commit, which is what
`git log --diff-filter=A` returns at the new path; a move commit that names another ticket leaves
only the dated correction.

### The escape, and what it can and cannot be planted against

A dated **attribution line**, in this shape and no other —

    > **Attribution, 2026-09-06 (ticket NN).** `verify/x/` was added by `sha`, which names no ticket.

— carries a check whose adding commit predates the convention or moved between trees under a
commit that names no ticket (bind 4; a move commit naming another ticket is not carried). The lesson
that has cost every review this week is that a check reading the text it grades treats the fix
somebody writes into that text as input, so the line is verified and never believed. **Five binds**,
four of them refusing text on the strength of git:

1. **The ticket, from the line's own header.** `(ticket NN)` must be the number the claiming
   file's name carries. A line copied from another ticket carries nothing — and the number is read
   from the header alone, because collecting it from anywhere in the paragraph let a line headed
   `(ticket 80)` hold for file 99 on the strength of its prose saying "as ticket 99 noted".
2. **The check.** The line must name the check being claimed. A line about a different check
   carries nothing.
3. **The sha, against git.** It must be one `git log --diff-filter=A` actually returns for that
   path as of the cited commit. A planted sha is `attribution-does-not-hold`, and the finding
   prints both what the line claims and what git says. It is the sha after `added by`, or the only
   one in the paragraph: five backticked shas with one of them right is a guess, and a guess must
   not be able to hold.
4. **That sha's subject must name no ticket.** *This is review F1 of PR 51, and it was the
   blocker.* The first cut of this rule confirmed that the sha EXISTED and added the file, and
   never asked what the sha SAID — the very defect this ticket exists to close, one level up.
   Measured on the record: `99-plant.md` attributing
   `verify/feed-contract/verify-feed-contract.sh` to `3e83a16` **passed**, though that subject
   names tickets 21 and 52; and with a directory token the sha of any script under it would do, so
   `verify/provenance/` attributed to `065e497` — ticket 53's release-evidence script — **passed**
   too. An attribution is the escape for a check git attributes to **nobody**. Where git attributes
   it to somebody else, that is an answer and not a gap, and no line may overrule it:
   `attribution-over-a-named-commit`, printing the ticket(s) the subject names.
5. **It cannot supply its own subject.** Attribution paragraphs are stripped from `named_checks`,
   exactly as correction paragraphs already were (review F1 of the ticket-80 round): an attribution
   may say who added a check the claim ALREADY names in its own section, never introduce one.
   Otherwise one planted paragraph would supply both halves of the proof.

**What it cannot bind, said plainly rather than left for the next reviewer.**

- A ticket may still claim a check whose adding commit is **genuinely nameless**. Three such paths
  exist in the hub, all added by `c9d0f20`. What the rule denies that claim is **silence**: every
  attribution used is printed with its path, line, sha and the subject of the commit it names, and
  — since review F4 — every attribution **consulted and refused** is printed too, so a false one
  standing beside a true one leaves a trace instead of being silently stepped over.
- **The claiming ticket's identity is the record file's own name, which is text the ticket
  controls.** Rename a file, or add one, under another ticket's number and it inherits that
  ticket's checks: `69-plant.md` whose H1 reads `# 99` passes by commit today. Two cheap greens
  are available and **neither is built here** (review F2, named not built): the `# NN` heading
  agrees with the filename in **103 of 103** issue files today, and no number is used twice. Both
  would raise the cost of the forgery; neither closes it, because an author who edits the filename
  and the heading in one diff passes both. The honest statement is that this rule trusts the
  filename for identity, and that nothing in the estate currently checks it.

### No could-not-look, three more reds

Following `verify/can-record/`'s call and this check's own (delegated): history this checkout
cannot read is `unreadable-history`; a path git names no adding commit for is `no-adding-commit`;
a record file whose own name carries no ticket number, so nothing can be attributed to it, is
`no-ticket-number`. A shallow checkout was already refused in the wrapper and still is. None of
the three is a shrug and none has a `SKIP`.

### What the committed record grades as, and the number that must not go stale

    103 ticket files, 44 recorded TRUTH lines, 47 gate-proof citation(s) and 10 quoted figure line(s) graded
    gate-proof citations: 0 proved by an adding commit naming the ticket, 0 by a dated attribution
    line, 47 disposed of by a dated correction, 0 observed false; 0 attribution(s) consulted and refused

(Quoted from the run at `7046106`, this ticket's head after its rebase onto fb06798 — the sha first
written here, 417ac08, was the pre-rebase commit and no longer exists; the recorded-lines figure
moves with the clock, the rest with the record.)

The charting recorded "rule 1's positive path is proven by no real ticket" as a sentence. It is now
a **printed number on every run**, and the number is starker than the sentence was: the four
citations that used to pass because the cited tree happened to carry a check (all four in ticket
80, three about run 7 and one about run 5) now fall to ticket 80's dated corrections instead, so
**nothing on the record passes rule 1's positive path at all**. Every gate-proof citation the
estate carries is a withdrawal. That is worth reading before anyone treats a green here as
evidence that the estate cites its own measurements correctly; it means only that it no longer
cites them falsely.

### Ticket 80

- Its Answer's case-D bullet is **struck**, not restated: it now records that the limit is closed,
  by this ticket, on 2026-09-06, with the rule and the re-measured 36-of-39, and discloses what is
  left as this ticket's limit rather than as an open route.
- Its one paragraph that mentioned **run 5** — reported speech about a citation *ticket 18* makes
  correctly — gains a dated correction naming run 5. Under ticket 80's rule that sentence passed
  silently, because run 5's tree does carry a check named somewhere in the same section; under this
  one it was the only red on the committed record until the correction landed. **The run says
  which**: it is counted in the 47 disposed, not in the 0 proved.
- Its three run-7 paragraphs are disposed of by the dated correction it already carried. Nothing
  was written to make them pass; the correction that was already true simply started doing work.

### R2-5, folded in

The three facts added for the D1–D5 ruling (ticket 13, `map.md`, ADR-0025) carried a marker
sentence and no load-bearing one, unlike every other item after review F5. Each gains a second
graded sentence, so an entry gutted to its heading is a red: ticket 13's "the assistant's decision,
recorded with the assistant's reason, not re-asked and not reopened"; the map's "the ranking that
put a panel verdict above a bare agree is what ADR-0025 retired"; ADR-0025's "an endorsement of the
assistant's reasoning is a delegation whatever shape the question was put in". The fact table is
32 sentences across items 2 to 9 in 15 files, up from 29.

### One thing found while building, and fixed (delegated)

A finding pointed at the wrong line. `para_citations` located a citation by searching each physical
line for the citation's VALUE, so a citation of run 5 was reported fourteen lines early, against
the totals of a quoted TRUTH line, which happen to contain the digit. It now looks for the line the
run is actually CITED on and falls back to the old search. A red nobody can look at is a red nobody
can check. One test.

(This paragraph is also review F6's: it used to quote that run and that figure on one text line,
which made it the eleventh graded figure line on the record and made the run output quoted below
wrong by one. A ticket about false citations should not need luck to pass its own rule.)

### Tests at the seam, red first

`tests/test_cited_truth.py`, still pure — file texts, log text, an injected `tree_lookup` and now
an injected `add_lookup`, so the rule is exercised with no repository and no estate. Red first,
twice:

- the build's own 20 new tests were red before the code existed (`20 failed, 46 passed`), and the
  two record-level plants were green under the old rule and red under this one;
- the review round's 7 more were red before their fix (`7 failed, 68 passed`), including both of
  review F1's measured plants, and the **selfcheck leg that had asserted the defective behaviour
  went red too** — which is how the defect survived the first build and is worth recording.

**75 pass now**, and the exact commands and outputs are in the pull request. The commit subjects
the tests assert on are quoted from the real hub log, because the convention's spellings are the
thing under test and an invented subject would test the invention.

### Verified

    bash talk/verify-all.sh --selfcheck                            PASS (exit 0)
    bash verify/cited-truth/verify-cited-truth.sh                  PASS (exit 0)
    bash verify/cited-truth/verify-cited-truth.sh selfcheck        PASS (exit 0)
    bash verify/truth-line/verify-truth-line.sh                    PASS (exit 0)
    bash verify/every-green/verify-every-green.sh                  PASS (exit 0)
    bash verify/can-record/verify-can-record.sh                    PASS (exit 0)
    .venv/bin/python -m pytest tests/test_cited_truth.py -n0 -q    75 passed
    .venv/bin/python -m mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
                                                                  Success: no issues, 177 files
    .venv/bin/python -m mypy verify/cited-truth/cited_truth.py --ignore-missing-imports --warn-unused-ignores
                                                                  Success: no issues

The full `pytest tests/` was not run here, per the build brief: a builder runs the files it
touched, and CI on the branch is quoted in the pull request. Standing reds are unchanged and
unrelated: invariant 45 everywhere, 44 on this laptop whenever the newest drift sample is over a
day old, and `tests/test_seam1_cli.py` serial-only.

## Waits on the owner

Nothing. No money, date, identity, authorisation or real person is touched by this ticket; the
change is one hub check, its tests and three record files.

Map line: [102 — The cited tree names who added the check](issues/102-the-cited-tree-names-who-added-the-check.md) — case D is closed, and it was a git question rather than a text one: `verify/cited-truth/` resolves a named check to its path in the cited tree, reads `git log --diff-filter=A --format=%H%x09%s <hub> -- <path>`, and requires the adding commit's subject to name the ticket making the claim — the number the ticket's own filename carries — or the ticket to carry a dated attribution line that is bound to the ticket (read from its own header), to the check, to a sha git agrees added that path (the one after `added by`) and to that sha's subject naming NO ticket — an attribution is the escape for a check git attributes to nobody, and where git attributes it to somebody else that is an answer and not a gap — printed on every run with the subject it names, as is every attribution consulted and refused. The ticket scan is case-insensitive, collects every number and a trailing list because the convention has six spellings and one commit built two tickets' checks, and requires the number to FOLLOW the word because `27 tickets implemented` names no ticket. **No `--follow`** (delegated), measured: it changes no verdict for run 7's three directories, git accepts it on a directory and silently ignores it, and the subject it surfaces for two of them is the one a looser scan would misread as ticket 27; a moved check is carried by the attribution line. Three more states are red rather than a shrug — `unreadable-history`, `no-adding-commit`, `no-ticket-number`. Measured 2026-09-06 at `caefdd3`: 36 of 39 hub verify scripts have an adding commit naming a ticket and the three that do not are exactly run 7's `verify/party/`, `verify/proportionality/` and `verify/provenance/`, all added by `c9d0f20`, which names none. On the committed record all 47 gate-proof citations now pass by dated correction, 0 by an adding commit and 0 by attribution — rule 1's positive path is exercised by no real ticket at all, printed as a number every run instead of disclosed as a sentence. Two limits are named rather than closed: a check whose adding commit is genuinely nameless can still be claimed, and the claiming ticket's identity is the record file's own name, which the ticket controls (the `# NN` heading agrees with the filename in 103 of 103 files today, and an author who edits both in one diff passes anyway). Ticket 80's case-D bullet is struck and its run-5 paragraph gains a dated correction; R2-5 gives the three D1–D5 facts a load-bearing sentence each (32 graded sentences, up from 29); and a finding now points at the line the run is cited on rather than the first line its digits appear on.

## Notes

Charted 2026-09-06 by the round-2 review of ticket 80 (hub PR #44, merged `8348b8e`). Sibling of
ticket 80; the rule it narrows is ticket 80 item 1's.

Map line: [102 — The cited tree names who added the check](issues/102-the-cited-tree-names-who-added-the-check.md) — case D is closed, and it was a git question rather than a text one: `verify/cited-truth/` resolves a named check to its path in the cited tree, reads `git log --diff-filter=A --format=%H%x09%s <hub> -- <path>`, and requires the adding commit's subject to name the ticket making the claim — the number the ticket's own filename carries — or the ticket to carry a dated attribution line that is bound to the ticket (read from its own header), to the check, to a sha git agrees added that path (the one after `added by`) and to that sha's subject naming NO ticket — an attribution is the escape for a check git attributes to nobody, and where git attributes it to somebody else that is an answer and not a gap — printed on every run with the subject it names, as is every attribution consulted and refused. The ticket scan is case-insensitive, collects every number and a trailing list because the convention has six spellings and one commit built two tickets' checks, and requires the number to FOLLOW the word because `27 tickets implemented` names no ticket. **No `--follow`** (delegated), measured: it changes no verdict for run 7's three directories, git accepts it on a directory and silently ignores it, and the subject it surfaces for two of them is the one a looser scan would misread as ticket 27; a moved check is carried by the attribution line. Three more states are red rather than a shrug — `unreadable-history`, `no-adding-commit`, `no-ticket-number`. Measured 2026-09-06 at `caefdd3`: 36 of 39 hub verify scripts have an adding commit naming a ticket and the three that do not are exactly run 7's `verify/party/`, `verify/proportionality/` and `verify/provenance/`, all added by `c9d0f20`, which names none. On the committed record all 47 gate-proof citations now pass by dated correction, 0 by an adding commit and 0 by attribution — rule 1's positive path is exercised by no real ticket at all, printed as a number every run instead of disclosed as a sentence. Two limits are named rather than closed: a check whose adding commit is genuinely nameless can still be claimed, and the claiming ticket's identity is the record file's own name, which the ticket controls (the `# NN` heading agrees with the filename in 103 of 103 files today, and an author who edits both in one diff passes anyway). Ticket 80's case-D bullet is struck and its run-5 paragraph gains a dated correction; R2-5 gives the three D1–D5 facts a load-bearing sentence each (32 graded sentences, up from 29); and a finding now points at the line the run is cited on rather than the first line its digits appear on.
