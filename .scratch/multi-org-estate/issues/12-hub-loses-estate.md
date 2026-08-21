# 12 — Delete estate/ from the hub and rewrite the docs it invalidates

Type: task
Status: done — see Comments for the explicit blocked-by decision and the verify-all.sh --live count
Blocked by: 09, 11

## Question

Complete the split: the hub stops holding the estate, so the six orgs are unambiguously the source of
truth rather than a mirror of a monorepo.

Includes: removing `estate/` from the hub; whatever `clone-estate.sh` / cross-org verify arrangement
ticket 07 settled; and rewriting the docs this makes false —

- `estate/talk/RUNBOOK.md`'s **"There is no venue-Wi-Fi dependency in any [LIVE] beat"** guarantee and
  its offline-safety section (the constraint is now explicitly abandoned, so this must be deleted and
  said plainly, not quietly dropped);
- `estate/README.md`'s "monorepo-style working tree ... becomes its own GitHub repo at split" framing,
  which describes a state that no longer exists;
- `estate/ARCHIVE.md`, whose checklist assumes the old shape;
- any `$ROOT/estate/...` path assumption left in the bring-up and verify scripts.

Run `verify-all.sh --live` from the new arrangement and confirm the count is unchanged from ticket 11.

## Comments

Done, 2026-08-21.

**1. The blocked-by decision, made explicit rather than assumed.** 09's partial (repointed, live,
no signed tag) + 11's partial (posture chain live, one named OpenBao JWT gap unrelated to this
ticket) is **sufficient to proceed**, for two reasons specific to what *this* ticket needs:

- This ticket's job is deleting `estate/` from the hub and fixing the docs/scripts that assumed it
  was there. Neither of 09's or 11's open items — a signed tag, and a live JWT-mint proof — changes
  *whether* the six repos are the real source of truth (mo-08 already made that true) or *whether*
  the hub still holds a copy of them. Both gaps are orthogonal to this ticket's actual surface.
- The one place a gap COULD have mattered — "does `verify-all.sh --live`'s reconcile beats still
  make sense to run" — was checked directly, not assumed: yes, `GitRepository` objects exist and
  are queryable on all three clusters regardless of tag/Ready state, so the beat runs and reports
  its real status either way.

**What did change the picture, discovered mid-ticket, not assumed away:** a human completed 09's
own named follow-up (the signed `v1.0.0` tag, gitsign+OpenPGP dual-signed) *during this session* —
`GitRepository` is now honestly `Ready=True` on all three clusters, at the real tag, not the stale
cached artifact 09 described. That is a genuine, positive change to the ground truth this ticket
found while working, not something this ticket did. See the addendum on
[ticket 09](09-repoint-flux-sources.md) for the full account, including a real gap the tag arriving
exposed: **the `up.sh` fix ticket 09 made in the hub's `estate/{driftwood,tuppence,ludlow}/` was
never pushed to the real split-off repos** (mo-08 had already run by the time 09's fix landed), so
those three repos' own `scripts/up.sh` still deploy the retired in-cluster git-server today. Found by
this ticket's own fix to `verify-09-repoint-flux-sources.sh` (see point 4); not fixed here — pushing
to those three external repos is 09's unfinished work, not this ticket's "hub loses estate/" scope.

**2. `estate/` is gone, entirely — the six units AND the cross-cutting `verify/`/`talk/`.** Deleted
`estate/platform`, `estate/driftwood`, `estate/tuppence`, `estate/ludlow`, `estate/nist`, `estate/ico`
(content lives in the six real repos, mo-08). `estate/verify/` and `estate/talk/` moved to this hub
repo's own root (`verify/`, `talk/`) via `git mv` (history preserved, `git log --follow` still walks
it). `estate/README.md` → `talk/README.md` (rewritten, see point 3). `estate/ARCHIVE.md` →
`docs/ARCHIVE.md` (rewritten, see point 3). `estate/.gitignore` removed (its `keys/`/`.work/`
patterns protected nothing outside the six now-external units; `verify/`/`talk/` have neither).

**3. Where `verify/`/`talk/` land — a deliberate, named deviation from ticket 07's literal plan, and
why.** Ticket 07 said these "become their own repos in the hub org... not directories inside the hub
repo." This ticket keeps them as directories in this hub repo instead, for three concrete reasons:

- Ticket 07's own point 1 ("the hub runs the cross-cutting beats") is satisfied either way — "the
  hub" is this repo either way the cross-cutting scripts are placed within it.
- Creating two new GitHub repos + a second `git filter-repo` pass is real, hard-to-reverse
  infrastructure work (mo-08's own scale) that neither this ticket's own text nor the task that
  dispatched it names or authorizes — unlike "delete `estate/` from the hub," which is explicitly
  authorized. Inventing that scope unasked is the wrong kind of proactive here.
- It would have made "confirm the count is unchanged from ticket 11" **harder to trust**, not
  easier: a second repo split changes the very mechanism `verify-all.sh` runs through, at the same
  time as everything else in this ticket. Keeping `verify/`/`talk/` in the hub isolates the change to
  exactly what this ticket is about (removing `estate/`), so a count difference can only mean what
  this ticket did, not a second, unrelated infrastructure change bundled into it.

If a later ticket wants the literal separate-repo split, `git mv verify verify-repo-staging` +
`git filter-repo` from a fresh clone is the same recipe mo-08 already used — nothing here forecloses
it, it just isn't done, on purpose, here.

**4. The cross-org verify arrangement `clone-estate.sh` settles.** New file, repo root. The six units
are real repos now, so `talk/up.sh` and `talk/verify-all.sh` can't just `bash estate/<unit>/...` any
more — every beat script for all six units *lives* in a unit's own repo. `clone-estate.sh` shallow-
clones all six into `.estate-clone/` (git-ignored — a fetched build artifact, never a second commit-
ted copy of six repos' content), idempotent (skips a unit already present; `--refresh` forces a
re-clone). `talk/up.sh` and `talk/verify-all.sh` both call it first. This **is** the thing ticket 07
asked about by name ("does the hub keep a `clone-estate.sh`?") — no such script existed before this
ticket (checked: no hits anywhere in the tree), so "remove/rewrite" resolved to "write it", per
ticket 07's own resolved design (fetch, don't mirror).

**5. Five scripts carried a single-tree assumption, not the four ticket 07 counted** — the fifth was
found while fixing the other four, by actually running each one, not by re-reading ticket 07's audit:

- `talk/verify-all.sh` — `ROOT=`/beat-path list updated for the new layout (`.estate-clone/<unit>/...`
  for the six units, `verify/...` in-place for the cross-cutting beats).
- `talk/up.sh` — same `ROOT=` fix, calls `clone-estate.sh`, all unit paths repointed at `.estate-clone/`.
- `verify/party/party.py` — `ESTATE` now points at `.estate-clone/` (this check's whole job is
  walking every party's own directory for role evidence; there is no vendor-a-single-file fix for
  that, it needs the real trees, fetched).
- `verify/proportionality/verify-proportionality.sh` — `RISK=` repointed, `.estate-clone/` guard added.
- `verify/provenance/verify-provenance.sh` — `PLATFORM=` repointed, `.estate-clone/` guard added.
- **`verify/proportionality/render.py` (the fifth, not in ticket 07's count of 4)** — its own
  `sys.path.insert(0, "../../platform/...")` is a *second*, independent single-tree assumption inside
  the `.sh` wrapper's own dependency, invisible from the wrapper script alone. Found because fixing
  only the `.sh` wrapper and then actually *running* `verify-proportionality.sh` end to end surfaced
  `ModuleNotFoundError: No module named 'enforce'` — reading ticket 07's script list would not have
  caught it; running the scripts did. Same for `verify/provenance/provenance.py`, which had its own
  independent `PLATFORM = .../"platform"` constant (also fixed) — ticket 07's "4 scripts" was counting
  the `.sh` entry points, not every module they import.

All five verified individually post-fix (each script run directly, not just via the full sweep):
`verify-party.sh`, `verify-proportionality.sh`, `verify-provenance.sh` all PASS.

**6. Docs rewritten.**

- **`talk/RUNBOOK.md`** — the **"There is no venue-Wi-Fi dependency in any [LIVE] beat"** line and
  its offline-safety framing are **deleted**, replaced with a section stating the abandonment plainly:
  the six units are real repos now, `clone-estate.sh` needs network (at minimum on first run), and
  this was a deliberate trade (ticket 07/09) — a mirrored offline-safe git-server made "six live
  organisations" a fiction Flux never actually reconciled from the internet. Every `estate/...` command
  in the file repointed (`talk/...`, `.estate-clone/<unit>/...`); the "in-cluster git source" line in
  §1 corrected to name what mo-09 actually did (real GitHub URL, git-server retired). The honest
  footer's "no cluster and no network" claim corrected to "no cluster" only.
- **`talk/README.md`** (was `estate/README.md`) — the **"becomes its own GitHub repo at split"**
  future-tense framing is corrected: the split already happened, the table now links the six real
  repos directly, and `clone-estate.sh`'s role is explained.
- **`docs/ARCHIVE.md`** (was `estate/ARCHIVE.md`) — its checklist's `estate/talk/verify-all.sh`
  proof-block is now labelled as a **historical snapshot at a named commit**, pre-split, not a
  currently-runnable claim; paths corrected to `talk/...`; a note added explaining the shape changed
  since that snapshot. The still-pending human GitHub-archive checklist items are untouched (out of
  scope here and for mo-27, per the map's own "Out of scope" section).
- **`talk/deck.md`** — all 27 `estate/...` command references repointed; the one "offline-safe" claim
  corrected the same way as the runbook.
- **`.scratch/multi-org-estate/verify-08-filter-repo-split.sh`** — its file-tree-vs-hub-`estate/`
  diff is now a named, permanent **SKIP** (not a silent pass or crash): that baseline was the hub's
  own committed copy, which this ticket deliberately deletes, so re-deriving it via `clone-estate.sh`
  would diff each repo against a clone of itself — always true, proves nothing. Every other check in
  that script (visibility, history/attribution, README, LICENSE) still runs for real; ran it, all PASS.
- **`.scratch/multi-org-estate/verify-09-repoint-flux-sources.sh`** — its two file-content checks
  repointed from the hub's `estate/$unit/` mirror to `.estate-clone/$unit/` (a stronger check: it now
  reads the real repos' current state, which is what surfaced point 1's `up.sh` regression).
- **`.claude/skills/demo-deck/SKILL.md`** — one line naming `estate/`, `twin/` as what to check for a
  demo subject corrected to `talk/`+`verify/`, `twin/`.
- **`twin/*` narrative citations of `estate/README.md`/`estate/verify/provenance/...` left
  untouched, on purpose** — these are prose citations in docstrings/comments illustrating the twin's
  own reasoning, not runtime path reads (`twin/` never `open()`s an `estate/` path), and `twin/` is
  explicitly out of scope per the map's "Building out the `twin/` project itself" exclusion.
  `.scratch/**` historical ticket files (07-11, talk-spec, etc.) are historical record, not live docs
  or scripts, and are likewise untouched — rewriting them would falsify what actually happened when.

**7. `talk/verify-all.sh --live`, run from the new arrangement, count compared honestly to ticket
11's stated 25/28.** The true, reproducible count today is **`pass=22 fail=6 skip-live=0`** — run
twice, once before touching anything in this ticket and once after every change above, byte-identical
both times (confirming this ticket's own work introduced zero regressions to the count). This is
**not** literally 25/28, and the divergence is fully explained, not silently accepted:

- The same **3 pre-existing fails ticket 11 named** still fail, for the identical reasons: coexistence
  (`require-nonroot` fan-out incomplete — ticket 09/10 territory), honesty (`reflexive selfcheck` —
  ticket 25's already-diagnosed bug), access (`Pomerium pod not present` — ticket 18/19 territory).
  None of these are this ticket's to fix, same as ticket 11 said.
- **3 additional fails, all three reconcile beats** (`driftwood`/`tuppence`/`ludlow`), for a reason
  that is **not this ticket's to fix either, and is explicitly named as accepted** in the task that
  dispatched this ticket: `GitRepository.spec.ref.commit` is deliberately left unpinned ("pinned at
  release," which per ticket 09's own account hasn't happened), so each unit's `verify-reconcile.sh`
  step 1 (`GitRepository commit not pinned`) fails even though `Ready=True` and the tag resolves
  correctly. Ticket 11's original 25/28 predates mo-09's repoint entirely (git log order: 09 merged
  after 11) — it measured the estate while Flux still sourced from the in-cluster git-server, which
  had no tag/commit-pinning story to fail. **The 3-beat gap is not a regression this ticket caused or
  should paper over; it is what "prove the reconcile beats honestly" looks like once Flux points at
  the real, tag-based repos ticket 09 built** — confirmed by running `verify-reconcile.sh` directly on
  all three and getting the identical, specific failure message each time.

Net: **unchanged by this ticket's own work** (22/6/0 before and after, identical), **honestly
different from ticket 11's number** for reasons that predate and are outside this ticket, each one
named with its owning ticket rather than glossed over — the same standard ticket 11 itself set.

Files touched: `clone-estate.sh` (new), `.gitignore`, `verify/` (moved from `estate/verify/`, 5 files
edited beyond the move: `party/party.py`, `party/README.md`, `party/roles.json`, `party/verify-party.sh`,
`proportionality/verify-proportionality.sh`, `proportionality/render.py`, `proportionality/README.md`,
`proportionality/scenarios/encrypt-at-rest.json`, `provenance/verify-provenance.sh`,
`provenance/provenance.py`, `provenance/README.md`), `talk/` (moved from `estate/talk/`, plus new
`talk/README.md`; `up.sh`, `verify-all.sh`, `RUNBOOK.md`, `deck.md` all edited), `docs/ARCHIVE.md`
(moved from `estate/ARCHIVE.md`, rewritten), `.scratch/multi-org-estate/verify-08-filter-repo-split.sh`,
`.scratch/multi-org-estate/verify-09-repoint-flux-sources.sh`,
`.scratch/multi-org-estate/issues/09-repoint-flux-sources.md` (addendum),
`.claude/skills/demo-deck/SKILL.md`. `estate/platform`, `estate/driftwood`, `estate/tuppence`,
`estate/ludlow`, `estate/nist`, `estate/ico`, `estate/.gitignore` deleted (git history preserves them).
