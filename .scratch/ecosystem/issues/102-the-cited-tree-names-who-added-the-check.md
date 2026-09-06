# 102 — The cited tree names who added the check

Type: task (AFK)
Status: open
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

## Notes

Charted 2026-09-06 by the round-2 review of ticket 80 (hub PR #44, merged `8348b8e`). Sibling of
ticket 80; the rule it narrows is ticket 80 item 1's.

Map line: [102 — The cited tree names who added the check](issues/102-the-cited-tree-names-who-added-the-check.md) — closes case D, the one route ticket 80 left open through `verify/cited-truth/` rule 1, and it is a git question rather than a text one: resolve the named check to its path in the cited tree, read `git log --diff-filter=A` for that path, and require the adding commit's subject to name the ticket making the claim, or the ticket to carry a dated, printed attribution line naming the commit. Measured 2026-09-06: 34 of 37 hub checks already have an adding commit naming a ticket, and the three that do not are exactly run 7's `verify/party/`, `verify/proportionality/` and `verify/provenance/`, all added by `c9d0f20`, which names none — so every case-D route through run 7 goes red; the `Ticket NN:` convention has six spellings in the log, so the match is a case-insensitive scan collecting every number; and of the 46 gate-proof citations at `8348b8e`, 43 pass by dated correction and the other 3 are ticket 80's own run-7 paragraphs, so rule 1's positive path is proven today by the selfcheck and 42 seam tests and by no real ticket. Two alternatives are recorded as rejected (absent-from-the-prior-run fails legitimate later citations; "the ticket's own diff added it" is the same git question the check cannot read from the ticket file), the `--follow` question is left for the build with a recommendation, and ticket-80 review items R2-1 (strip code spans and link targets before the not-citable test) and R2-5 (load-bearing sentences for the three D1–D5 facts) are folded in.
