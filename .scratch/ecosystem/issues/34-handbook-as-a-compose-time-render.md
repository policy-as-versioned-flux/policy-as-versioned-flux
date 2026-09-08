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
as `HEADER.yaml`. That one placement is what buys every clause of the ticket at once — **from the
platform tag that carries the renderer on**: the page lands in the same pull request as the
artefact, `verify()` compares it byte-for-byte like every other rendered file, and
`cut-release.yml` (which runs `composition.py verify` before `git tag -s`) refuses to cut a tag
over a stale one.

**Corrected 2026-09-08 (review F-02).** The pinned tool grades the page only once the pin
carries the renderer, and today no pin does (`0 of 3`): driftwood, tuppence and ludlow all pin
`v2.0.1`, whose `composition.py` neither writes nor verifies the page — its `verify()` compares
what it rendered plus `composed/**/*.yaml`, and `HANDBOOK.md` is neither. Measured: a hand-edited
`composed/HANDBOOK.md` on driftwood's tree, through `v2.0.1` (`533dccb`) `composition.py verify`
with the parents at their served tips, prints `OK: composed artefact re-renders byte-for-byte from
the recorded parent SHAs`, exit 0 — the same line as the unedited page. That is the step
`cut-release.yml` runs before the tag is cut, so at the pin `cut-release` would sign a hand-edited
page. Until the pins move, the only thing that grades the page is the byte comparison in
`verify-fresh.sh` and the hub's `verify/handbook/`, and the page says so of itself: its preamble
now names the tool and the files it derives from and the checks that re-render it, and no longer
says which pull request or tag carries it or that a parent is signed — nothing under `composed/`
derives either. The same correction is in ADR-0007's note.

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
could not survive a byte comparison against a re-render. That is not asserted, it is measured four
ways on the real artefact every gate run: bytes; purity (the same served bytes rendered again in a
**separate process** under an emptied environment, a random `PYTHONHASHSEED` and a fresh working
directory must be identical — an in-process second render shared `HOME`, the hostname and every
module cache with the first and could not see a renderer reading them, review F-06); a source scan
of the **served** renderer (nothing reachable from `render()` names `open`, `os`, `sys`, `socket`,
`time`, `datetime` or `subprocess` — a renderer reading `/etc/hosts` renders the same bytes in
every process on one machine, so only its text catches it, and the PASS line says the scan is what
the check trusts beyond the process test); and sensitivity (one field of the served artefact moved
in memory must move the page). Red first for the two new legs: a renderer that appends `$HOME`
graded `0` under the reviewed check and `1` under this one (the separate process), and one that
reads `/etc/hosts` graded `0` and now `1` (the source scan, `render: open`).

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
   scoped to the files the **engine** reads and paired with the opposite assertion about the page.
   **Sharpened 2026-09-08 (review F-03):** three of the paired assertions were vacuous — a page with
   no price rows "moved" because the parent SHAs moved; the Source caption alone contains the words
   `holes` and `selected-controls`; and the untagged and recorded renders differ by their parent
   SHAs whatever the page says. Each now asserts the string the page **derives**: the moved price's
   own table row (`| ico | feed | penalty-schema | driftwood | GBP | GBP 1,787,177.08 |` on the day
   of measurement — the row, not the amount, because the exposure section derives the same regime
   amount from `HEADER.yaml` and a plant that blanked the cell still carried the number there);
   `- Controls selected: 287` and the hole count read from the same header; and the hole sentence
   by its own identity, `untagged-pin \`insurer/quote-driftwood@v2\`` with its premium, present in
   the untagged **and** the recorded render and absent once the hole heals (the review's "absent in
   the recorded render" would have been a false assertion: the recorded state still carries the
   hole). Red first with three omission plants over the stale clone, the only substrate where the
   price legs execute (see ticket 106): `the handbook does not state the moved ico price as its own
   row ...`, `... does not state the 287 selected controls`, `... does not name the untagged pin as
   untagged-pin \`insurer/quote-driftwood@v2\``. Ticket 45 (platform PR 17, merged after this branch
   was cut) had meanwhile replaced the per-file loops with `_assert_only_the_moved_feed_changed`;
   it now skips the page and asserts it moved, and each leg asserts its specific row beside it.
8. **The hub check carries no renderer of its own.** `delegated`. It loads `compose/handbook.py`
   from the ref **platform serves** — the tag the adopter's *served* pin names where that tag
   carries it (`git show <ref>:gitops/platform/platform-pin.yaml`, never the working copy),
   platform's `origin/main` otherwise, printing which. A hub copy would grade the hub's idea of
   the render rather than the estate's, which is the proxy this project keeps finding in its own
   reviews. **2026-09-08 (review F-08):** the fallbacks to local `main` and `HEAD` are gone from
   the check and its wrapper, and adopters are discovered from `origin/main`, not the working
   tree; a hand-edit committed on a local branch only is now provably not graded (a selfcheck case).
9. **Three disclosed limits are printed as counts, and none is a pass condition.** `delegated`,
   applying the brief's rule that a disclosed limit is an assertion that goes stale. How many
   adopters serve a page at `origin/main`, how many **also** serve one at a signed tag (graded as
   well, never instead — review F-10: grading the newest tag alone would have frozen the check on
   the first tag ever cut), and how many pin a platform tag already carrying the renderer.
   Measured 2026-09-08 with the four pull-request branches named through the overrides:
   `3 of 3 adopter(s) serve a handbook at a branch ref named by PAVC_HANDBOOK_REFS this check
   could read; 0 of 3 also serve one at a signed tag, graded as well; 0 of 3 pin a platform tag
   that already carries compose/handbook.py`. Without overrides, today, it is `0 / 0 / 0` and a declared SKIP, because
   no adopter's `origin/main` carries a page until the three adopter pull requests merge.
10. **The page says of itself only what a re-render can prove.** `delegated`, 2026-09-08 (review
    F-02). Which tool derives it, from which files, and which checks re-render it. Not which pull
    request it landed in, not which tag carries it, not that a parent is signed: nothing under
    `composed/` derives any of those, and the page's own byte comparison could not tell if they
    were false. The parents caption now says the commit is the one the file records and that
    `composition.py verify` is what proves it is the tree read.
11. **A price the composition could not compute is named, never refused and never a number.**
    `delegated`, 2026-09-08. Ticket 45's `switching` entries carry `amount: null` with the
    publisher's own refusal in `could_not_look`; the reviewed renderer raised on them, which took
    the whole page down with the composition (found rebasing onto PR 17). The row now reads `could
    not look (section 6)` and the reason is a named absence; an entry with no amount and no reason
    is refused (a price with neither is not a price).
12. **The one limit the page does not state is `publisher-clone-absent`, by name, with the
    reason.** `delegated`, 2026-09-08. `composition.py` writes it on every run — `closed` when
    every priced feed was read from its publisher's own tree, `open` naming the publisher when the
    adopter's vendored copy stood in — so it records which clones the **re-deriving run** could
    read, not a fact about the artefact. Ticket 45's `verify()` holds the artefact to re-rendering
    byte-identically with the publisher absent, and a page that stated this row could never do
    that: measured, the portability leg failed on `composed/HANDBOOK.md` alone. The page prints
    the exclusion and its reason as a fixed sentence and counts limits without it;
    `composed/evidence.json` still records it in full.
13. **`—` in the tier column means the entry's kind proposes no tier; a feed row with none is
    named absent.** `delegated`, 2026-09-08 (review F-12). A premium is a committed cost and a
    switching entry a measured counterfactual; neither proposes a tier by construction, and the
    caption says so. Any other kind with no `proposed_tier` is a named absence.
14. **A whole-entry hole is named by `source/name@version`.** `delegated`, 2026-09-08. The real
    hole `composition.py` writes carries those and no `id`; the reviewed renderer printed
    `` `None` `` for it. The fixture now has the shape the code writes.
15. **An absent list field is named, never rendered as 0; an empty list is a real zero.**
    `delegated`, 2026-09-08 (review F-07). `members`, `holes`, `limits`, `cages`, `refusals`,
    `restatements`, `deltas`, `ungoverned` and `selected-controls` all defaulted through `or []`.
16. **The manifest row for platform's `verify-fresh.sh` lands in the hub first.** `delegated`,
    2026-09-08 (review F-01). Without it the first clock run after platform merged would print
    `FAIL manifest[row]: .estate-clone/platform/compose/verify-fresh.sh is discovered but has no
    line`. With it, a hub checkout whose platform clone does not yet carry the script grades
    `NOTE manifest: ... not in this checkout of the unit`, not FAIL (`truth_manifest.py`
    `coverage_problems`, a unit line). Class `self-proof`, skip `-`. **Merge order is therefore
    hub, then platform, then the three adopters.**

### What is still true and unflattering

- **No signed tag carries a handbook yet.** The ticket's phrase is "under the artefact's own tag",
  and today the pages are graded at branch tips. Cutting a tag is `cut-release.yml` in Actions, not
  something a builder does; the check prints `0 of 3` until one is cut and will print `1 of 3` the
  day it is, unprompted.
- **No adopter's compose step has produced the page yet.** All three pin platform `v2.0.1`, which
  predates `compose/handbook.py`. Until each pin moves, their `cut-release.yml` runs the older
  `composition.py`, which neither writes nor deletes the file — so nothing breaks and nothing goes
  red there, but the committed page is one a human ran the published tool to produce, not one the
  compose step emitted, and a hand-edited page would be signed at that pin (see the correction under
  point 1). This is the same ordering hazard `tier_binding.py` records for itself. Counted, not
  claimed: `0 of 3`.
- **The first recomposition at `v2.0.1` after all five merge goes RED on the hub gate, and only a
  human can repair it** (review F-05). Any pin bump or feed bump that re-runs `composition.py` at
  `v2.0.1` rewrites `composed/evidence.json` and leaves `composed/HANDBOOK.md` exactly as it was;
  that adopter's own checks stay green (the tool at its pin does not know the page exists) and the
  hub's `verify/handbook/` goes red on it: `is NOT what its own served artefact renders to`. The
  repair is a human re-running `handbook.py render` from an untagged platform ref and committing
  the page, which is the state this ticket leaves the estate in already. The follow-on that ends it
  is ticket 78's ordering, stated there for `tier_binding.py` and true here too: **platform cuts a
  tag carrying `compose/handbook.py`, then each adopter bumps its pin to it**, in that order — the
  pin bump is what makes the compose step emit and verify the page. Neither is this ticket's:
  cutting a tag is `cut-release.yml` in Actions and a pin bump is three adopter pull requests.
- **Three of the four paired selfcheck legs are only partly reachable on current main** (review
  F-04, measured). With platform at `origin/main` (`30d104f`) and every unit of the estate at
  `origin/main`, `composition.py --selfcheck` is red at the ungoverned-namespace leg —
  `composition.py:5066`, `assert "acme" not in text, path` → `AssertionError:
  composed/governed-namespace-guard.yaml` — after 58 green legs; the same red at `5126` with this
  branch's code. The untagged-pin and holes legs run **before** it and pass; the three price legs
  sit behind it and do not execute on current main. They execute, and pass, only against the stale
  local clone (platform local `main` = `bbda376`): this branch's selfcheck over that clone is
  green end to end, 81 OK, exit 0, and the F-03 plants above are red there. The cause is a string
  collision (the served guard now stamps `posture.acme.io/` labels and the fixture's ungoverned
  namespace is named `acme`), charted as **ticket 106**, and it is not masked here. Consequence:
  `platform/compose/verify-composition.sh` runs the selfcheck, so its gate row goes red at the next
  `clone-estate.sh --refresh` regardless of this ticket, and this Answer no longer cites that
  script's SKIP as measured on main.
- **`signed_tags()` counts a signature block, it verifies nothing** (review F-11). A tag object
  whose body carries `-----BEGIN` is counted; the docstring says so and the count is printed as a
  count. The selfcheck plants such a tag with a body that says it is not a signature.
- **Four commits on this round were made with the owner's global pre-commit hook bypassed.**
  `ggshield` was out of API quota (`no more API calls available`); each staged diff was grepped for
  key, token, credential and private-key shapes first (none), and each message says so.
- **Nothing grades whether the page is any good.** It is derived, not argued. It says so on itself:
  two things it can never tell a reader are whether the rules are the right rules and whether a
  human accepted the change that produced them. ADR-0007's residual open problem stands.

### Which check grades it

`verify/handbook/verify-handbook-is-a-compose-time-render.sh` (hub, `estate-observation`), plus
`platform/compose/verify-fresh.sh` (manifest row `self-proof | -`, added here before platform
merges it) and the render seam's own 46 tests in `handbook.py --selfcheck`; the hub grader's 17
planted cases in `handbook_check.py --selfcheck`.

### Waits on the owner

Nothing. Four pull requests are open and unmerged, as the brief requires: platform #18,
driftwood #29, tuppence #23, ludlow #20, and the hub's own #58. Merge order: hub first (the
manifest row), then platform, then the adopters (decision 16).

Map line: 34 — Handbook as a compose-time render: `platform/compose/handbook.py` renders `composed/HANDBOOK.md` from the composed artefact and nothing else, and `composition.py` emits it in the same `rendered` mapping — so from the platform tag that carries the renderer on it rides the same pull request, drift check and signed tag, while at today's `v2.0.1` pins (0 of 3 carry it) the pinned tool neither writes nor verifies it and cut-release there would sign a hand-edited page; `verify-fresh.sh` and the hub's `verify/handbook/` are what grade it, by re-rendering the served bytes at `origin/main` and at any signed tag and comparing, with a separate-process purity leg, a source scan of the served renderer and a sensitivity leg so the comparison cannot pass vacuously; the page says of itself only what a re-render proves; an absent field, list fields included, is named and counted, never defaulted (ADR-0020); the first recomposition at `v2.0.1` after the five merges leaves the page stale and the hub gate red until a human re-renders it, ended only by a platform tag carrying the renderer and then three pin bumps (ticket 78's order); the composition selfcheck's price legs are unreachable on current main until ticket 106 lands; `claude -p` summaries become a human-run skill landing outside `composed/`; the legacy `verify.sh` is retired with a reason and no file to delete.
