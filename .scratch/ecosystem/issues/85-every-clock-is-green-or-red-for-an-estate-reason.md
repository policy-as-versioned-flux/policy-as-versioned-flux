# 85 — Every clock is green, or red for an estate reason

Type: task (AFK)
Status: resolved for what an agent can build (both unowned reds fixed and every red now names its ticket; "green on the newest run" waits on the merges of the three pushed unit branches and the next scheduled runs)
Blocked by: none

## Question

Five of thirteen clocks are red on their newest scheduled run and the citable surface cannot see any of it. Three are owned: driftwood twin-sweep (ticket 72, `bash -e`), tuppence and ludlow propose-tier (ticket 62, the deleted branch), the insurer requote (ticket 77, the exposure pin). Two are not:

1. Feeds' fetch dies in its own observation cage on stray `__pycache__/*.pyc` left by its own python. `fetch.yml:120` cleans without `-x` before switching to the orphan `observations` branch. Five of the six declared feeds have never recorded an observation. Fix the cage step once, and share the fix with the hub's and insurer's clocks, which have the same shape.
2. Nist's fetch succeeds every day and writes null, because its reader looks for `catalog/v<N>/feed.json` and the catalogue lives at `catalog/`. Point it at `catalog/` plus `CATALOG_VERSION.json`, or record that a controls catalogue has no observable feed version and remove the clock's claim.

Done = every scheduled workflow in the nine repos is green on its newest run, or red with an open ticket named in `verify-schedules`' output; feeds' observation branch carries a dated observation for every declared feed.

## Notes

Charted by [REVIEW-2026-09-02.md](../REVIEW-2026-09-02.md) R8. Finding: participants/P9. Ticket 56 owns the surface's ability to see the clocks at all.

## Answer

Built 2026-09-04. Every decision below is **delegated** (ADR-0025).

**1. Feeds' fetch died in its own cage.** `.github/workflows/fetch.yml:120` cleaned with
`git clean -fd -e .git`. Without `-x` that leaves exactly the files `.gitignore` hides, and the
largest of those is the `fetch/__pycache__` the `python3 fetch/<feed>.py` step above it writes when
it imports `fetch/lib.py`. Two lines later the job switches to the orphan `observations` branch,
which carries no `.gitignore`, and the cage step's
`git status --porcelain --untracked-files=all` read the `.pyc` files as untracked paths outside the
observation lane and failed the run -- every run, for every feed. Five of the six declared feeds
(threat-register, cve, eol, fx, news) have never recorded an observation.

Fixed twice over, and both on purpose: the clean becomes `git clean -ffdx -e .git`, character for
character the same clean the orphan path a dozen lines below already used (one clean in the file,
not two spellings of it), and the workflow declares `PYTHONDONTWRITEBYTECODE: "1"` so the bytecode
is never written at all. Two mechanisms because the failure is silent in the worst way: a cage
refusing its own bytecode looks exactly like a cage refusing a real declaration.

Shared with the two clocks of the same shape. The insurer's append step (`fetch.yml`, the
`observations` switch) had **no clean at all** and gains the same two lines plus the env; nist's
had none either and gains the same. Both also gain `PYTHONDONTWRITEBYTECODE`. Their readers are
python heredocs today so they write no bytecode into the tree, but the insurer's `requote` job runs
`python3 pricing/quote.py`, which does, and "it happens not to break today" is not a cage.

*The hub's `truth.yml` cage is deliberately left without a clean* (an open decision, decided
here). The hub never leaves `main`, so its own `.gitignore` is in scope for the cage's
`--untracked-files=all` and `.estate-clone/` and `__pycache__/` stay invisible to it. The bug is
specific to switching to a branch that carries no `.gitignore`. Adding a `-ffdx` clean to a job
that has just run 84 third-party scripts would delete the gate's own captures before the lane
stages them. Left alone, recorded, not forgotten.

**2. Nist's fetch wrote `published_version: null` every day and reported success.** Its inline
reader globbed `catalog/v*/feed.json` -- the shape of a feed *envelope* -- while a controls
catalogue is a flat `catalog/` holding the OSCAL document beside `CATALOG_VERSION.json`, the
wrapper that names the version institutions actually pin. party.yaml's own comment says why the
two shapes differ ("a `controls` catalogue is OSCAL, not a feed payload, so there is no
payload_schema to point at"). Every day the glob matched nothing, the else branch fired, and the
clock ran green while observing nothing.

Decision: **point the reader at the catalogue, do not drop the claim.** The catalogue has an
observable version; what it lacked was a reader that knew the shape. A new `catalogue(feed_dir)`
reads `CATALOG_VERSION.json` for `publishedVersion` and `source.fetchedAt`, computes the sha256 of
the document `file` names, and records `payload_matches_declared` -- so a hash that moves while
the version stands still is a tamper this clock can see, and a hash that disagrees with the
wrapper's own is the same fact one step earlier. `newest()` is left in place for the envelope
shape, so nothing is lost the day nist publishes one. Verified by extracting the heredoc and
running it against the real checkout: `published_version 1.1.0`, `upstream_version 5.2.0`,
`payload_sha256 d820835a…`, `payload_matches_declared true` -- the first real reading this clock
has ever produced.

**3. Every red clock names the open ticket that owns it.** `verify/schedules/clock-owners.yaml`
maps `<unit>/<workflow>` to a ticket number and one line of what that ticket owns about that
clock; `schedules.py` prints it in the FAIL line itself.

Decisions inside that:
- *A YAML beside `schedules.py`, not the ticket files' own headers.* The relation is
  clock-to-ticket and a ticket can own several clocks; putting it in ticket headers means grepping
  49 files to answer one question, and a clock with no ticket would then be indistinguishable from
  a clock nobody had looked at.
- *A red with a named ticket stays a **FAIL**, not a SKIP and not a new outcome.* Ticket 83's
  concern is exact: a fourth outcome is one the gate cannot count. Naming the owner is text inside
  the FAIL line, so the arithmetic is untouched and the estate's number still carries the red.
- *The map cannot rot, and its anti-rot rules are themselves graded.* An entry naming a ticket
  file that does not exist is a FAIL; an entry naming a workflow this checker does not grade is a
  FAIL. An entry whose ticket reads `resolved` is **not** an error -- a fix lands hours before the
  clock next ticks -- and the line says which of the two it is instead of guessing: "either the fix
  has not reached a scheduled run yet, or this red is a new one wearing an old ticket's name".
- *`hub/truth.yml` is in the map because it is red for an estate reason.* Its newest scheduled run
  read `cancelled`: the single `truth` concurrency group cancels a queued scheduled run when a
  push queues behind it. Ticket 56 splits the group per event and stops excusing a cancelled run;
  the red stands until the clock next ticks.

**Which check grades it.** `verify/schedules/verify-schedules.sh`. Its selfcheck gains the owner
map fixtures (owned, unowned, stale entry, both anti-rot faults, and an assertion that the map
that ships names only tickets that exist); `tests/test_schedules_clock.py` holds the same seam
under pytest. Ticket 56 is what lets any of this be seen on a citable run at all.

**Where the done-line stands.** "Red with an open ticket named in `verify-schedules`' output" is
true today: the live run names all six with their tickets. "Every scheduled workflow green on its
newest run" is not, and cannot be made so by an agent -- three of the six reds are owned by
tickets 62, 72 and 77, and the two this ticket fixes only go green when the three pushed unit
branches are merged (only `pavc-other-hand` may) and the clocks next tick. "Feeds' observation branch carries a dated observation for
every declared feed" likewise waits on six real runs of a fixed clock. Nothing here fakes one.

### Round 2, 2026-09-04 — the red this ticket was being blamed for was the checker's

Review found that `hub/truth.yml` would have been reported red **for ever**, with ticket 85 named
as its owner, for a reason no fix here could ever touch: `last_run` read the newest scheduled run
with no status filter, so on a scheduled `truth.yml` run it read the run doing the grading
(`conclusion` "", `status` `in_progress`), and round 1's narrowed excuse graded that FAIL. A clock
grading its own liveness by looking at itself. Fixed in ticket 56's round 2 —
`newest_gradable()` drops the grading run and prefers the newest completed one, and `run_line()`
makes a run still in flight a **named SKIP with no owner clause**, because a could-not-look must
never blame a ticket for a red. `hub/truth.yml` stays in `clock-owners.yaml`: its real red, the
`cancelled` run of 09:55:43Z, is real and still owned here.

Also corrected here: the three unit branches this ticket's fixes live on were listed under "waits
on the owner" as un-pushed. They were pushed on 2026-09-04 (see that section for who and the
SHAs); what waits is the merge, which only `pavc-other-hand` may do. And the count of red clocks
now reads six wherever the 2026-09-04 run is cited, matching that run rather than the 2026-09-02
review's five.

Map line: Ticket 85 -- the two unowned red clocks are fixed at the source (feeds' cage read the `__pycache__` its own python wrote; nist's reader globbed a feed envelope at a controls catalogue and wrote null every day), the fix is shared verbatim with insurer and nist, and every red clock now names the open ticket that owns it in the gate's own output.

## Waits on the owner

1. ~~Push `ticket-56-and-85` in policy-as-versioned-feeds, -nist and -insurer.~~ **Done
   2026-09-04: the three branches are already pushed.** The owner's standing instruction of
   2026-09-04 sets `twin/ENACT_MODE` to `development`, under which `enact_guard` admits a unit
   push, so the builder pushed them itself on 2026-09-04 as the owner's git identity (Chris
   Nesbitt-Smith <chris@cns.me.uk>) -- not the owner by hand. Verified from the remotes on
   2026-09-04 with `git ls-remote origin ticket-56-and-85`: feeds `5276280`, nist `78b5397`,
   insurer `49e3fed`. What is left of this item is not a push but a **merge**: these are branches,
   not `main`, and only `pavc-other-hand` may merge them (the standing guard mode `other-hand`).
2. **The next scheduled run of each fixed clock**, or a dispatch of it: feeds (03:17), nist
   (02:41), insurer (05:31), and the hub's truth run (05:47). Only then does feeds' `observations`
   branch gain a line per declared feed and do these clocks read green. An agent cannot make an
   upstream clock run and must not fake one.
3. **The three reds this ticket does not own**: driftwood twin-sweep (72), tuppence and ludlow
   propose-tier (62), insurer requote (77). Each is named in the gate's output with its ticket.
