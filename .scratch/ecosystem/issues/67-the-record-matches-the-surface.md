# 67 — The record matches the surface

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

One hygiene pass, every item dated, nothing rewritten in place. The map's false 65/0/16 citation and the stale fog list were corrected at charting time on 2026-08-31; this ticket owns the rest: (a) add the reversals-confirmed update line to the drift-review NORTH-STAR copy, or repoint the map's link at the root copy, so the two copies agree; (b) reset ico's penalty-schema bump.yaml to none now that v3.0.0 is cut; (c) trim the unit repos' OBSERVATION_LANE lists to paths each repo owns; (d) wire a small check into the gate: any pass/fail figure that map.md quotes must exist as a line in talk/truth.log. Done = a reader following the map meets no claim the truth surface contradicts, and the gate enforces it.

## Notes

Charted by the ambition review of 2026-08-31. Closes review findings: M13 (map cites uncited number / Nothing-is-red, 2 confirmed findings), minors: stale fog, NORTH-STAR copies disagree, stale ico bump, hub-only lane paths.
Record: [REVIEW-2026-08-31.md](../REVIEW-2026-08-31.md).

## Comments

**2026-09-02, review.** Sibling ticket 80 carries the ADR, ticket and glossary corrections the review found: fifteen build tickets cite run 7 as proof; ADR-0010 and ADR-0008 lack banners; ADRs 0019 to 0021 and 0023 do not mark their provisionality; CONTEXT.md contradicts ADR-0022's Deny addendum. Widen (d) so any TRUTH figure quoted in issues/*.md must resolve to a real line whose tree contains the named check. Record: REVIEW-2026-09-02.md R10.

## Answer

Built 2026-09-06. Four items: **all four done**, one of them by correcting the check that made it
impossible. The durable half is not the sweep — it is one new check.

### The check: `verify/map-surface/verify-map-surface.sh`

In the gate, manifest row `verify/map-surface/verify-map-surface.sh | estate-observation | -`,
tests at the pure seam in `tests/test_map_surface.py` (31, no git, no estate). Five rules over
`.scratch/ecosystem/map.md`:

1. **Figures** (item (d)). Every pass/fail figure the map quotes — `57/7/18 of 84`, `65 pass, 0
   fail, 16 could-not-look of 83`, or the `pass= fail= skip=` keys of a quoted TRUTH line — must
   equal the corresponding figure of a line `talk/truth.log` records. Quoted beside a run number
   it must be **that run's** figure, and a run the log never recorded is red.
2. **Checks.** Every check the map names in backticks must be one the gate discovers, read from
   `talk/verify-manifest.txt` — the row `talk/verify-all.sh` requires for every script it runs.
3. **Links.** Every relative link must resolve. "A reader following the map" is this ticket's own
   definition of done, and a dead link is the cheapest way to fail it.
4. **Lanes** (item (c)). No unit repository may declare an `OBSERVATION_LANE` path it does not own.
5. **Record.** Item (a)'s two corrections as four literal facts the record must carry or must no
   longer carry.

**How it composes with `verify/cited-truth/`** (ticket 80, PR 44, which merged to main on
2026-09-06 while this was being built; this branch was rebased onto it).
That module grades the same class of claim — a record citing a measurement that never measured the
thing — in `.scratch/ecosystem/issues/*.md`, and its own docstring names `map.md` as out of its
scope and this ticket's question. The populations are **disjoint** and neither reads the other's
files, so nothing is graded twice and the union covers the ticket record and the wayfinder. What is
shared is the **parser**: both resolve a citation through `talk/truth_manifest.py`'s `parse_truth`,
so there is one reader of the TRUTH line in the estate and a change to the line's shape cannot make
one of the two quietly wrong. This module imports nothing of 80's, so it stood before PR 44
merged and stands after. Proved both ways: `verify/cited-truth/verify-cited-truth.sh` was run over 80's branch with this ticket
file copied in and passed, and it passes again on main with this branch rebased onto it.

**What it refuses to grade, counted rather than asserted.** Whether the figure the map quotes is
the *right* figure, or the check it names the right check — it grades that both exist on the
surface: necessary, never sufficient. Item (b) is graded by ico's own
`verify-declared-bump.sh` (in the manifest), because reading another party's declaration from a
working copy here would be the proxy this ticket exists to end. Three populations are excused and
each is **printed as a number on every run**, so a disclosed limit cannot go stale: figures whose
own text line calls them local, a rehearsal, a fixture, planted, hypothetical, not citable or an
Actions-log quote (0 today); figures a **dated** correction elsewhere in the map disposes of (1
today); and checks the map names and declares on the same line as not in the gate yet (1 while ticket 80's
check was unmerged, 0 now that it is). A correction never excuses the replacement figure standing inside
itself; that one is graded like any other, or a correction could excuse its own wrong number.

**No could-not-look**, by decision (delegated, ADR-0025), following `verify/can-record/`'s and
`verify/cited-truth/`'s call. Rules 1–3 and 5 read only files in this repository; rule 4 reads
`.estate-clone/`, which `verify/schedules/verify-lane.sh` already refuses rather than shrugs for.
A missing map, a missing `truth.log`, a missing manifest, a missing parser and a missing unit are
each red with their own line. The manifest row therefore declares no skip pattern, and there is
none to declare.

### Item by item

**(a) The two NORTH-STAR copies agree. DONE, by repointing *and* correcting.** The ticket offered
either. Both were needed and both are cheap: the map's Destination now links
[`NORTH-STAR.md`](../../../NORTH-STAR.md) at the repository root — the one referent since ticket 02,
and the copy ticket 95 rewrote on 2026-09-03 — instead of the drift-review original, and the
drift-review original no longer says the 22 reversals await an answer. It said so for nine days
after they were confirmed (REGRILL-ANSWERS.md, GAPS.md line 0.7, both dated 2026-08-28). The
sentence is corrected in place under a dated banner rather than contradicted below itself, because
a correction appended under a claim it never removed leaves the record saying both things at once.
Graded by rule 5, four facts.

**(b) ico's `penalty-schema/bump.yaml` is `none`. DONE — and the gate that made it impossible is
corrected in the same commit.** Measured on the real remote, not on a proxy:
`git ls-remote --tags origin` resolves `v3.0.0^{}` to `9d09222`, and
`git diff v3.0.0 origin/main -- penalty-schema` is empty. So v3.0.0 is cut and nothing is queued,
which is exactly the condition the file's own 2026-08-29 note named.

Setting it to `none` turned ico's release gate red, and the gate was wrong, not the ticket.
`declared-bump-gate.py` computed the bump between the **two newest published majors** (v2 → v3) and
compared the declaration to that. That is a fact about the **last** release; it stays `major` for
as long as v3 is the newest directory, while `bump.yaml` says on its face that it declares the bump
for the **next** one. The same conflation was already refusing a legitimate patch release:
`declared-bump-gate.py v3.0.1` demanded `major` from a tree byte-identical to what v3.0.0
published. The predecessor is now the release this one follows — a released tag of the same major
where one exists, read from git as nist's copy of this gate already does; the major below on disk
where none does. Both entry points share one function, so the named-tag path and `--tree` cannot
drift apart. It refuses rather than shrugs: the hub's manifest declares no could-not-look for that
row, so an exit 3 would grade FAIL there anyway, and a named refusal says more than a shrug that is
failed for being one. `--selfcheck` now asserts the refusal.

**(c) Twelve unit workflows across eight repositories, trimmed. DONE, pull requests open.** Every
one carried the hub's four-path list `talk/truth.log drift/samples.jsonl talk/captures
observations` verbatim. Read from the repositories on 2026-09-06: `talk/truth.log` and
`talk/captures` exist nowhere but the hub; `drift/samples.jsonl` exists only in the three adopters;
`observations` is an orphan branch on the five publishers and a path driftwood's `twin-sweep.yml`
writes on main. So no unit had ever owned all four.

Not cosmetic. `verify/schedules/lane.py` grades every commit a scheduled identity landed in a
repository against the union of **that repository's own** declarations, so each copied path was one
a clock there could land and be graded green for — and the cage step in the job reads the same list
before it stages. (The first draft of this Answer, of the workflow comments and of the seven pull
request bodies said the union was taken across *all* units. That was read off the function name and
not off the call site; `check()` computes `declared_lane(on_ref, local)` per unit. Corrected before
merge, in the same way this ticket asks of everyone else.)

The new lists: driftwood `drift/samples.jsonl observations`; ludlow and tuppence
`drift/samples.jsonl`; feeds, ico, insurer, nist and platform `observations`. Measured with
`git log --first-parent` and `git show --name-only`, and **corrected 2026-09-06 (review F8)**:
7 scheduled commits in driftwood, 6 in ludlow and 6 in tuppence on `main`; on the publishers'
`observations` branches **13 in feeds** — one per matrix feed, `cve`, `eol`, `fx`, `market-moves`,
`news`, `threat-register` and the branch's `README.md` — and 6 each in ico, insurer, nist and
platform. The first draft said "6 each on the five publishers", which was true of four of them and
wrong about the busiest. Every one of the 47 falls inside the trimmed lists, so the change is
strictly stricter and breaks nothing. `verify-lane.sh` passes unchanged.

**(d) The gate enforces it. DONE, and widened per the 2026-09-02 comment.** Rule 1 above is the
item as written. The comment's widening — "any TRUTH figure quoted in `issues/*.md` must resolve to
a real line whose tree contains the named check" — was built by ticket 80 as
`verify/cited-truth/`, with the tree-lookup half this ticket did not ask for; it is not rebuilt
here. It merged to main on 2026-09-06 and this branch is rebased onto it, so both halves of the
widened item are in the gate together. See the composition note above.

### Decisions

Every decision below is **delegated** (ADR-0025: the assistant decides architecture and records it;
none of these is a purpose, date, identity, money, authorisation or a real person).

1. **Item (a) is answered by doing both halves, not either.** *delegated.* Repointing alone leaves
   the original saying something false; correcting alone leaves a reader of the map at a document
   that lost §0 on 2026-09-03. Both are one line each.
2. **The stale sentence is corrected in place, under a dated banner, not contradicted below.**
   *delegated.* Ticket 80's own reasoning: a correction appended under a claim it never removed
   leaves the estate saying both things at once. The banner carries the date and the reason.
3. **The banner does not quote the sentence it removed.** *delegated.* Discovered by the check:
   the first draft quoted it verbatim and rule 5 went red, correctly — a grep cannot tell a claim
   from a quotation of it, and the cheaper fix is to describe rather than quote.
4. **Item (b) is done by correcting ico's gate, not by declining the item.** *delegated.* The
   alternative was to leave `bump: major` standing and record that the file's own instruction is
   un-followable. The gate was asking about the last release while the file declares the next one;
   that is a defect with a second victim already (a v3 patch release), and the fix is smaller than
   the explanation of why it was not made.
5. **`--tree` refuses rather than shrugs when it cannot read tags.** *delegated.* nist's copy exits
   3 there. The hub's `talk/verify-manifest.txt` declares no could-not-look for either row, so an
   exit 3 grades FAIL in the gate anyway; a named refusal carries the reason with it. nist's latent
   copy of the same shape is left alone — it is not this ticket's, and touching it would be a
   change nothing here grades.
6. **The lane is trimmed per repository, not per job.** *delegated.* The ticket says "paths each
   repo owns". ludlow's and tuppence's `propose-tier.yml` and `renovate-run.yml` write nothing to
   main at all, so their honest per-job lane is empty — but `verify/schedules/schedules.py`
   requires a non-empty `OBSERVATION_LANE` from a job carrying the LANE-shaped cage, and moving
   those five jobs to the CLEAN cage shape is a different change with its own risk. Named under
   *not done*.
7. **The new check's manifest class is `estate-observation`, not `meta`.** *delegated.* Four of its
   five rules read this repository's own record, which is `meta` by the manifest's definition. But
   the lane rule reads the CONTENT of eight other parties' scheduled workflows, and that is what a
   red turns on today. The class should name what the verdict rests on.
8. **No could-not-look.** *delegated.* Following `verify/can-record/` and `verify/cited-truth/`.
   Every state in which this cannot see is red with its own line, and the manifest row declares no
   skip because there is none to declare.
9. **A check the map names may be excused only if the same text line says it is not in the gate
   yet, and the excuses are counted.** *delegated.* Found while writing the map line: naming ticket
   80's unmerged `verify/cited-truth/` went red, correctly. The map must be able to point at built,
   unmerged work; it must not present it as something the gate runs. The escape is on the line, in
   words, and the count is printed every run.
10. **The check grades `map.md` and no other document.** *delegated.* `NORTH-STAR.md` is graded by
    `verify/record/verify-record-states-the-purpose.sh` (ticket 95), `issues/*.md` by ticket 80's
    check, and the deck by `verify-demo.sh`. A fourth reader of the same files would be a second
    opinion, not a second check.
11. **The disclaimer is three fixed phrases, and `verify/cited-truth/`'s two plus `run=local`.**
    *delegated* (review F1). `not citable` is the estate's own words; `fixture=1` and `run=local`
    are the tokens `talk/verify-all.sh` writes itself on a line that is not a citable measurement,
    so a line quoting such a TRUTH line verbatim OUTSIDE A CODE SPAN needs no extra disclaimer
    (corrected 2026-09-06 after review: code spans are blanked before the phrase test, so a TRUTH
    line quoted in backticks -- the shape map.md line 103 uses -- is graded and must say `not
    citable` in its prose). Nothing else. The
    seven-word bag is what a reader would have written; it is also what laundered.
12. **A correction disposes only for the paragraph it immediately follows.** *delegated* (review
    F2). The alternative the review offered — require the corrected claim to be rewritten in place
    under a banner — is stricter and is what item (a) did, but it would invalidate the map's own
    2026-08-31 correction, which is correctly written and which a reader meets in the right place.
    Immediately-follows keeps that one and refuses the laundering.
13. **Rule 4 reads the served ref ONLY, and fetches it first; it does not union the checkout.**
    *delegated* (review F3). This deliberately parts from `verify/schedules/lane.py`, and the
    reason is that the two ask different questions — see the round 1 note. A stale checkout is
    reported as a note. A fetch that fails is red, not a shrug: a verdict on a ref nobody refreshed
    is the same venue-dependent reading one level down, and it cost twelve false findings the same
    morning.
14. **Rule 2 has no hatch at all.** *delegated* (review F4). The review offered a policed hatch —
    name a PR or branch and verify the script exists at that ref with `git cat-file -e`. Dropping
    it is smaller, has no laundering surface, and matches what the lane leg already did to this
    ticket's own eight pull requests: red until merged. A map may still point at unmerged work; it
    says so in a sentence rather than in a token a check reads.

### The lane leg was red, and is now green

`verify-map-surface.sh` exited 1 with **33 findings, all `lane-not-owned`**, for as long as the
eight unit pull requests were open: the trims were on branches and the rule reads what each unit
SERVES. That was ticket 81's "red until merged" shape and the honest grade — the map's claim that
item (c) was done was not true of the served estate. All eight merged on 2026-09-06 as
`pavc-other-hand` (driftwood 6e23dbe, feeds 8cb7ae8, ico, insurer c991160, ludlow cd2cc9b, nist
9dd7c31, platform a270fce, tuppence fe60091) and the leg went green with no change to the rule.

Every leg is now green: 0 figure findings, 0 check findings, 0 dead links, 0 lane findings, 0
record findings.

### Verified

Red first, at the pure seam:

    $ .venv/bin/python -m pytest tests/test_map_surface.py -n0 -q     # before the module existed
    E   FileNotFoundError: ... verify/map-surface/map_surface.py
    ERROR tests/test_map_surface.py - FileNotFoundError
    1 error in 0.20s

    $ .venv/bin/python -m pytest tests/test_map_surface.py -n0 -q     # after
    31 passed in 0.09s

    $ .venv/bin/python -m pytest tests/test_map_surface.py -n0 -q     # after review round 1
    46 passed in 5.40s

The rule, red against the real record before any of this ticket's corrections landed:

    $ bash verify/map-surface/verify-map-surface.sh
      !! driftwood/propose-tier.yml: lane-not-owned: declares 'talk/truth.log' in
         OBSERVATION_LANE, and driftwood owns no such path -- it owns ['drift/samples.jsonl',
         'observations'] ...
      ... 32 more lane findings, plus:
      !! .scratch/ecosystem/map.md: record-carries: still carries
         '](../drift-review-2026-08-27/NORTH-STAR.md)' -- item (a) ...
      !! .scratch/drift-review-2026-08-27/NORTH-STAR.md: record-carries: still carries
         "still await the owner's yes or no" -- item (a) ...
      == 37 finding(s): lane-not-owned x33, record-carries x2, record-lacks x2
    FAIL: the record and the surface disagree

…and after, with the four record findings gone and the 33 lane findings held by the eight open
pull requests:

      == 33 finding(s): lane-not-owned x33
      -- 5 figure(s) graded against talk/truth.log; 0 declared uncitable on their own line and
         1 disposed of by a dated correction, both counted and not graded
      -- 1 check(s) named and declared not in the gate yet (line [88]), counted and not graded
      -- 15 lane declaration(s) read across 8 unit(s)

Item (b), red before green in ico:

    $ bash .github/scripts/verify-declared-bump.sh     # bump: none, old gate
    FAIL: penalty-schema/bump.yaml declares 'none' but the computed bump from v2 to v3 is 'major'
    exit 1

    $ bash .github/scripts/verify-declared-bump.sh     # bump: none, corrected gate
    ok  --tree refuses a declaration off the ladder rather than shrugging at it
    OK: declared bump 'none' == computed bump 'none' (v3.0.0 -> v3.0.1)
    PASS: the bump ladder holds on fixtures, and ico's own declared bump agrees with the
    bump computed from its published tree under its own rule.yaml
    exit 0

Battery, all exit 0 on this branch:

    bash talk/verify-all.sh --selfcheck                            PASS
    bash verify/truth-line/verify-truth-line.sh                    PASS  (112 scripts placed)
    bash verify/every-green/verify-every-green.sh                  PASS  (112 discovered)
    bash verify/can-record/verify-can-record.sh                    PASS
    bash verify/adr-supersession/verify-adr-supersession.sh        PASS
    bash verify/schedules/verify-lane.sh                           PASS  (unchanged by the trim)
    bash verify/cited-truth/verify-cited-truth.sh                  PASS  (ticket 80's, over this
                                                                         ticket's own file)
    .venv/bin/python -m mypy twin tests conftest.py …              Success: no issues, 177 files

The counts are the branch's after its third rebase, onto the main that carries ticket 80's merge
(PR 44) and its follow-up (PR 46). They were 110/175, then 111/176, then 112/177; each was true of
a different tree, and each was re-run rather than left standing.

**The full `pytest tests/` was not run locally and no local figure from it is quoted here.** The
machine was loaded and a number nobody watched arrive is not a number. CI on this branch is the
citable read, and it was watched to completion — both the push run and the pull-request run, whose
results agree:

    twin, push run 34028267142, branch ticket-67-the-record-matches-the-surface at 043d77c
      tests       2 failed, 2018 passed in 194.96s
                  FAILED tests/test_invariant_suite.py::test_the_suite_is_green
                    -- invariant 44 drift_window_is_actually_being_sampled: the newest sample is
                       1 day old, so the probe has stopped
                    -- invariant 45 flux_coverage_floor_is_still_reachable: the floor can no
                       longer be reached
                  FAILED tests/test_seam1_cli.py
                         ::test_an_attestation_sidecar_accompanies_every_artefact
      invariants  RESULT: 70 passed, 2 failed, 3 skipped (0 pending, 3 skipped and not faked)
                  the two are 44 and 45, named on their own rows
      typecheck, demo, reproduce-elsewhere, determinism x4   all success

    twin, pull_request run 34028269947 (PR 45) at 043d77c
      tests       2 failed, 2018 passed in 202.71s, the same two
      invariants  RESULT: 70 passed, 2 failed, 3 skipped

Both watched to completion. Every failure is a red the build brief names as standing and
environment-dependent: invariants 44 and 45, `test_the_suite_is_green` while either is red, and
the serial-only `tests/test_seam1_cli.py` leak. Invariant 44 passed on the earlier runs of this
same branch and fails on these, which is exactly the environment-dependence the brief warns of and
the reason no fixed count is quoted. Nothing this ticket changed is in any of them.

Earlier runs of this branch, each true of a different tree: 1 failed, 1958 passed at `a176445`
(runs 34025933959, 34025966944), and 1 failed, 2000 passed at `0a26ebc` (runs 34026412998,
34026415135) after ticket 80 merged. The 18 further tests are review round 1's.

The one red is the standing one: invariant 45, `flux_coverage_floor_is_still_reachable`, and
`test_the_suite_is_green` while it is red. Invariant 44 passed on the runner — these are
environment-dependent, which is why no fixed count is quoted. Nothing this ticket changed is in
either. Nothing was written into `talk/truth.log`.

Map line:

- [67 — The record matches the surface](issues/67-the-record-matches-the-surface.md) — the map is
  graded against the truth surface, not read against it: `verify/map-surface/verify-map-surface.sh`
  reds a pass/fail figure this file quotes that no line in `talk/truth.log` records, a figure
  quoted beside a run that is not that run's, a check named in backticks that the gate does not
  discover, a relative link that resolves to nothing, and a unit repository declaring an
  observation-lane path it does not own — the counterpart to ticket 80's `verify/cited-truth/`,
  which grades `issues/*.md` and names this file as out of its scope; the two share one
  TRUTH-line parser and read no file in common.
  Item (a): the Destination now links the root `NORTH-STAR.md`, the one referent, and the
  drift-review original says the 22 reversals were confirmed. Item (b): ico's `bump.yaml` is `none`
  again, and its release gate, which had been computing the gap between the two newest published
  majors and so could never let it be, now asks about the next release. Item (c): twelve unit
  workflows across eight repositories carried the hub's four-path lane verbatim, and
  `verify/schedules/lane.py` grades a repository's landed clock commits against the union of that
  repository's OWN declarations, so each copied path was one a clock there could land and be graded
  green for; each list now names only what its repository owns, which every landed commit measured
  today already fits. The lane leg is red until those eight pull requests merge, and says so with a
  count.

**Applied to `.scratch/ecosystem/map.md` in this branch**, under *Decisions so far*.

### Not done

1. ~~The eight unit pull requests are not merged, so the lane leg is red.~~ **Done 2026-09-06:**
   all eight merged as `pavc-other-hand` and the lane leg reads green.
2. **The lane is not narrowed per job.** ludlow's and tuppence's `propose-tier.yml` and
   `renovate-run.yml`, and driftwood's `renovate-run.yml`, declare a lane they never write to.
   Decision 6 says why; the honest form is the CLEAN cage shape, which is a different change.
3. **nist's `declared-bump-gate.py` keeps the exit-3-when-no-tags shape** ico's just lost. Its
   manifest row declares no skip either, so the same latent red sits there. Out of this ticket's
   scope, and now charted with the rest of ico's inherited gate defects as
   [ticket 103](103-icos-release-gate-computes-the-bump-it-is-about-to-cut.md).
5. **ico's release gate can still agree about the wrong number three ways** (review F5, F6, F7),
   all inherited and none a regression from this ticket. Ticket 103.
4. **Rule 2 reads the manifest, not a live discovery run.** A script present in the tree, listed in
   the manifest and excluded in `talk/verify-exclusions.txt` would pass rule 2 while the gate does
   not run it. `verify-truth-line.sh` already grades manifest-versus-discovery in both directions,
   so the gap is covered there rather than re-covered here.

### Review round 1, 2026-09-06

Eight findings. Two blocking, both **the same class that defeated ticket 80's rule 1 that
morning**: a substring hatch that launders, spelled with words the map already uses. Two major on
the same theme — a rule that reads a proxy for the served thing. One minor, one of my own numbers.
Three inherited from ico's old gate, charted rather than fixed here.

**F1, blocking — the disclaimer was a bag of words.** `_UNCITABLE` was seven substrings —
`local`, `rehearsal`, `fixture`, `planted`, `hypothetical`, `not citable`, `actions log` —
matched anywhere on the line, with no negation test and no output beyond `+1` in a count. Three
routes through it, all reachable on this map: the word "local" appears on map.md at line 23
("a local clock"), line 78 ("[92 — The local clock]") and line 101 ("a local rehearsal"), so any
figure ever added to one of those lines was exempt for good; `...and that is NOT a rehearsal`
exempted itself by asserting the opposite of a disclaimer; and `run 7 recorded 43/11/0 of 56 and
was planted` excused a figure that DISAGREED with the run cited beside it.

Fixed by following `verify/cited-truth/` exactly, which was corrected for the same defect at 09:00.
**Three fixed phrases**, whole-token: `not citable` in those words, and the runner's own
`fixture=1` and `run=local` tokens — the two things `talk/verify-all.sh` itself writes on a line
that is not a citable measurement. `_NEGATION` refuses an occurrence modified by `not`, `no`,
`without` or `never` within twelve characters; a code span or a link target is blanked first, so a
marker being QUOTED spends nothing; the hatch is spent only where it actually suppresses a grade;
and **every exemption is printed by path and line number**, not counted. On the real map the
exempted list is empty and the one disposal is named:
`-- disposed .scratch/ecosystem/map.md:99 (correction of 2026-08-31, the paragraph below it)`.

**F2, blocking — a correction disposed of its figure everywhere.** The 2026-08-31 correction of
"65 pass, 0 fail, 16 could-not-look of 83" laundered a FRESH occurrence of that same sentence
written into a new section today. That is the exact sentence this ticket was charted to refuse,
excused by the correction of it. A correction now disposes only for the paragraph it **immediately
follows**, which is where the estate writes one and the only place a reader meets the two together.
A claim anywhere else must be rewritten in place under a banner, as item (a) did to the
drift-review NORTH-STAR. The disposal is named by line, and a figure inside the correction is
still graded.

**F3, major — the lane rule read the working copy, not the served ref.** The Answer, the map line
and the pull request body all said "the gate reads each unit's default branch", which was true on
CI only because `clone-estate.sh` clones fresh there. The reviewer proved it three ways: units
checked out at the ticket branch gave 0 findings, at `origin/main` 33, and an **uncommitted**
`git checkout <branch> -- fetch.yml` in ico made ico's three findings vanish.

Both halves — what a unit DECLARES and what it OWNS — now read `origin/main`, which the check
**fetches first**, because a ref nobody refreshed is the same venue-dependent reading one level
down: measured the same morning, `clone-estate.sh --refresh` KEPT platform and tuppence (they
carried `.work/` worktrees) and their stale `origin/main` produced twelve findings against an
estate that had none.

It reads the served ref *only*, and here it deliberately parts from `verify/schedules/lane.py`,
which unions the ref with the checkout. lane.py is right to union: it grades commits a clock
LANDED, and a clock is judged by the configuration in force when it landed, whichever copy carries
it. This rule asks what the estate DECLARES, and the only declaration a reader can meet is the
served one — unioning made the verdict turn on the venue in the other direction, reporting twelve
findings from two stale working copies. A checkout that disagrees is **reported as a note and
graded by nothing**. Proved by re-running the reviewer's own construction: with the old four-path
list restored into ico's working copy, uncommitted, the run prints
`-- note .estate-clone/ico: the checkout declares a different lane from origin/main in
['fetch.yml']` and still PASSES. Four git-backed tests over throwaway repositories hold it.

**F4, major — rule 2's "not in the gate yet" hatch.** It excused a check that existed nowhere, and
its phrases were ordinary prose: map.md line 29 already contains "unmerged". **Dropped.** Unmerged
work goes red until it merges, exactly as the lane leg did for its own eight pull requests, and a
map that wants to point at built-but-unmerged work says so in a sentence a reader reads rather than
in a word this check reads. The hatch existed for one line of my own map entry naming ticket 80's
then-unmerged check; ticket 80 merged, so nothing needed it.

**F8, minor — one of my own counts was wrong**, in the class this ticket polices. "6 each on the
five publishers' observations branches" was true of four and wrong about the busiest: feeds has 13,
one per matrix feed. Corrected above with the per-feed breakdown and dated.

**F5, F6, F7 — inherited from ico's old gate, charted not fixed.** All three predate this ticket
and none is a regression from it; the review found them while reading the corrected file, and each
changes what ico's release gate refuses. They are
[ticket 103](103-icos-release-gate-computes-the-bump-it-is-about-to-cut.md): an unpublished edit to
the newest major launders into the next major's bump, because a major's FIRST release reads its
predecessor on disk rather than at its tag; the tag's own increment is never compared to the
declared bump, so a `v3.0.1` may carry a minor change (the old gate refused that by accident); and
an empty local tag list cannot be told from "never released", so a `--no-tags` or shallow checkout
grades against the wrong predecessor instead of refusing.

## Waits on the owner

Nothing. Every item is built. The eight unit pull requests and the hub pull request wait on the
integrator, who merges as `pavc-other-hand`; none of them needs an owner decision.
