# 34 — Handbook as a compose-time render

Type: task (AFK)
Status: resolved
Blocked by: none

> **Unblocked 2026-09-06 (record correction).** This line read `Blocked by: 09` until today. Ticket 09 resolved on 2026-08-28; nobody re-read this line, so the ticket sat behind a blocker that no longer existed. A `Blocked by:` line is a claim about another file and rots the same way a cited figure does (ticket 80).

## Question

Publish the generator as a platform tool each adopter's compose step runs over its composed artefact, landing the render in the same PR and gitsign tag; wire verify-fresh.sh into the gate; retire verify.sh; move claude -p summaries into a human-run skill.

## Notes

Graduated 2026-08-28 from ticket 13's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

Built 2026-09-06. The estate now renders a handbook; before this it rendered none (ADR-0007's own
line, written the same morning by ticket 80, said so). All four clauses of the question are
answered, one of them by finding that there was nothing to do and saying so.

**1. The generator is a platform tool the compose step runs.** `platform/compose/handbook.py`
renders one page of Markdown from an adopter's composed artefact. `composition.py`'s `compose()`
calls it after it has built the evidence document and puts the page in the same `rendered` mapping
as `HEADER.yaml`. That one placement is what buys every clause of the ticket at once: the page
lands in the same pull request as the artefact, `verify()` compares it byte-for-byte like every
other rendered file, each adopter's `compose-check` job fails on any drift in it, and
`cut-release.yml` proves it re-renders from the recorded parent SHAs before the gitsign tag is cut.

**2. `verify-fresh.sh` is in the gate.** `platform/compose/verify-fresh.sh <dir> <ref>` re-renders
from the artefact **as served at a ref** and compares bytes with the page served at that same ref.
With no arguments it reads no adopter at all and proves the tool over planted repositories, because
NORTH-STAR §2 forbids the publisher reading an institution's repository and that script ships in
the publisher's tree. The estate-wide read is the hub's
`verify/handbook/verify-handbook-is-a-compose-time-render.sh`, discovered by `talk/verify-all.sh`,
with a manifest row declaring both could-not-looks it can print.

**3. `verify.sh` is retired, and nothing was deleted for it.** The end-to-end script belongs to the
archived `handbook-generator` repository and was never lifted into this estate, so there was no file
here to remove. The retirement is a paragraph in `platform/compose/README.md` giving the reason:
the chain that justified it is now three checks the estate already runs on every change.

**4. The `claude -p` summaries are a human-run skill.** `.claude/skills/handbook-summaries/`, whose
output lands **outside** `composed/`.

**The property the whole thing rests on.** The render is a pure function of the artefact: it reads
no clock, no environment, no network and no file outside the composed tree it is handed. So it is
re-derivable by anyone holding the artefact, and a page that said something the artefact does not
could not survive a byte comparison against a re-render. That is not asserted, it is measured three
ways on the real artefact every gate run: bytes, purity (the same served bytes rendered again from
another directory under a scrambled environment must be identical) and sensitivity (one field of
the served artefact moved in memory must move the page).

### Decisions

1. **The handbook is a function of the composed ARTEFACT, not of the parents.** `delegated`
   (ADR-0025). Rendering from the parents would have made freshness un-gradable offline: a verifier
   would need all five parent trees at their pinned SHAs and a network to check one page. Reading
   only `composed/` makes `verify-fresh.sh` a `git show` and a byte comparison. Nothing is lost,
   because the artefact's own faithfulness to its parents is already proved by
   `composition.py verify`, which `cut-release.yml` runs before the tag is cut. Two checks, each
   with one job, instead of one that needs the whole estate to answer.
2. **The page goes in `rendered`, not beside it.** `delegated`. Everything the ticket asks for —
   same pull request, same drift check, same signed tag — falls out of that single placement with
   no new workflow step in any adopter. The alternative, a separate generator step in each
   adopter's CI, is three workflow edits that can each rot independently.
3. **A summary is not a render, and cannot live in the page.** `delegated`. A `claude -p` paraphrase
   is not derivable from the artefact, so it would fail the byte comparison on every run; dropping
   the comparison to accommodate it would give back a page nobody can check. Summaries land outside
   `composed/`, by their own pull request, and nothing in the gate grades their content — there is
   no instrument that could, and inventing one would be inventing a number (ADR-0020).
4. **An absent field is named, never defaulted.** `delegated`, applying ADR-0020. The render carries
   no sentence it cannot derive: no `exposure` means "no exposure is published, `exposure` is absent
   from `HEADER.yaml`", never a zero. The absences are counted on the page and again in its footer,
   so a disclosed limit is a number that moves rather than a sentence that goes stale. Live today:
   driftwood names `prices[2].lef_basis` absent (a premium is a committed cost, not a modelled
   loss), tuppence and ludlow each name `selection-policy` absent.
5. **A price with no `perspective` or no `currency` is refused, not printed.** `delegated`. The £
   seam's rule is that a price carries both; a page that printed a bare amount would be laundering
   a broken price into prose.
6. **`HEADER.yaml` and `evidence.json` disagreeing about `parents` is refused.** `delegated`. The
   artefact states its publishers twice and the page states them once, so the render observes that
   the two agree before it writes either. Found while writing the seam tests, and it is now one of
   the 26.
7. **Four legs of `composition.py --selfcheck` were narrowed, not deleted.** `delegated`. They
   asserted that *no* rendered file moves when a signature state or a price moves. The handbook
   moves on both — correctly, because it reports both, and ticket 69's whole point is that money
   committed against an unsigned quote is the one number a reader can act on. Each leg is now
   scoped to the files the **engine** reads and paired with the opposite assertion about the page:
   it must move when the price moves, must name the tier a crossing bump proposes, must report an
   untagged pin, and must state the holes, the selected set and the ungoverned namespaces that the
   engine's own files must never carry. A handbook that hid any of them would be the dashboard the
   north star refuses. Five printed sentences that said "no rendered file changes" now say "no file
   the engine reads changes, and the handbook does".
8. **The hub check carries no renderer of its own.** `delegated`. It loads `compose/handbook.py`
   from the ref **platform serves** — the tag the adopter pins where that tag carries it, platform's
   branch tip otherwise, printing which. A hub copy would grade the hub's idea of the render rather
   than the estate's, which is the proxy this project keeps finding in its own reviews.
9. **Three disclosed limits are printed as counts, and none is a pass condition.** `delegated`,
   applying the brief's rule that a disclosed limit is an assertion that goes stale. How many
   adopters serve a page, how many were graded at a signed tag rather than a branch tip, and how
   many pin a platform tag already carrying the renderer. Today that reads `3 / 0 / 0`. Each moves
   on its own the day a tag is cut or a pin moves, with no edit to any file.

### What is still true and unflattering

- **No signed tag carries a handbook yet.** The ticket's phrase is "under the artefact's own tag",
  and today the pages are graded at branch tips. Cutting a tag is `cut-release.yml` in Actions, not
  something a builder does; the check prints `0 of 3` until one is cut and will print `1 of 3` the
  day it is, unprompted.
- **No adopter's compose step has produced the page yet.** All three pin platform `v2.0.1`, which
  predates `compose/handbook.py`. Until each pin moves, their `compose-check` runs the older
  `composition.py`, which neither writes nor deletes the file — so nothing breaks and nothing goes
  red, but the committed page is one a human ran the published tool to produce, not one the compose
  step emitted. This is the same ordering hazard `tier_binding.py` records for itself. Counted, not
  claimed: `0 of 3`.
- **Nothing grades whether the page is any good.** It is derived, not argued. It says so on itself:
  two things it can never tell a reader are whether the rules are the right rules and whether a
  human accepted the change that produced them. ADR-0007's residual open problem stands.

### Which check grades it

`verify/handbook/verify-handbook-is-a-compose-time-render.sh` (hub, `estate-observation`), plus
`platform/compose/verify-fresh.sh` and the render seam's own 26 tests in `handbook.py --selfcheck`.

### Waits on the owner

Nothing. Four pull requests are open and unmerged, as the brief requires: platform #18,
driftwood #29, tuppence #23, ludlow #20, and the hub's own.

Map line: 34 — Handbook as a compose-time render: `platform/compose/handbook.py` renders `composed/HANDBOOK.md` from the composed artefact and nothing else, `composition.py` emits it in the same `rendered` mapping so it rides the same pull request, drift check and signed tag; `verify-fresh.sh` and the hub's `verify/handbook/` grade it by re-rendering the served bytes and comparing, with purity and sensitivity legs so the comparison cannot pass vacuously; an absent field is named and counted, never defaulted (ADR-0020); `claude -p` summaries become a human-run skill landing outside `composed/`; the legacy `verify.sh` is retired with a reason and no file to delete; three disclosed limits are printed as counts (3 adopters serve a page, 0 at a signed tag, 0 on a pin carrying the renderer) and each heals itself.
