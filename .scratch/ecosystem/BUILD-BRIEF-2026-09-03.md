# Build brief — everything open, 2026-09-03

Read this first. Then `spec.md` here, then the ticket you build (`issues/NN-*.md`, whole file, the
newest dated comment last), then the ADRs it names (`docs/adr/0019` to `0025`). Vocabulary is
`CONTEXT.md`. The purpose and the build order are `NORTH-STAR.md` §0 and §4. The rules of
`BUILD-BRIEF.md` (2026-08-28) still hold except where this file says otherwise.

## What changed since the 2026-08-28 brief

- **The hub may be pushed.** The owner asked for it. Ticket branches in the hub are pushed and
  opened as pull requests. Merging is done by the integrator only, as `pavc-other-hand` (below).
- **Every push to an enactment repo is still refused** (`-platform`, `-driftwood`, `-tuppence`,
  `-ludlow`, `-nist`, `-ico`, `-feeds`, `-insurer`). The owner pushes those. Commit locally.
- **The assistant decides architecture and records it** (ADR-0025). When a build finds a fact that
  forces a call, decide, write the decision and its reason in the ticket under `## Answer`,
  labelled `delegated`, and continue. Never write "provisional". Do not stop to ask. Only money,
  dates, identities, authorisations and real persons go to the owner; list those under
  `## Waits on the owner` in the ticket and build everything else.
- **No gate, in the owner's words.** A mutating admission controller. Price and cage; never count,
  refuse, deny or file. The only refusal is a missing instrument (ADR-0020).
- **Identity is shelved** (ticket 90). **The currency controller is un-retired** (ticket 91).

## Branch discipline

Hub (`/Users/cns/httpdocs/controlplane/policy-as-versioned-flux`):
- Builders work in an isolated git worktree of the hub. First command in the worktree:
  `git checkout -b ticket-NN-<slug>`. Symlink the estate clone in:
  `ln -s /Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.estate-clone .estate-clone`.
- Python: `/Users/cns/httpdocs/controlplane/policy-as-versioned-flux/.venv/bin/python` (absolute
  path; the worktree has no venv). Tests: `<venv>/bin/python -m pytest tests/test_x.py -n0 -q`.
  Builders run single test files only. The integrator runs the full suite once per wave.
- Commit on the ticket branch, message first line under 72 chars, plain English, no attribution
  lines. Then `git push -u origin ticket-NN-<slug>` and open a pull request with `gh pr create`
  (base `main`, title `Ticket NN: <what>`, body: what, why, how verified, what waits on the owner).
- Never merge. Never run `gh pr merge`. The integrator merges after review.

Units (`.estate-clone/<unit>/`, gitignored clones of the real repos, local `main` equals
`origin/main` on 2026-09-03):
- One integration branch per unit for this run: `ecosystem/build-2026-09-03`, from `main`.
- A builder that touches a unit works in a nested worktree of that unit:
  `git -C .estate-clone/<unit> worktree add .estate-clone/<unit>/.work/ticket-NN -b ticket-NN-<slug> ecosystem/build-2026-09-03`.
  `.work/` is gitignored in every unit and excluded from the gate's glob. Edit and commit there.
- Never `git checkout` a different branch in `.estate-clone/<unit>` itself: the gate reads that
  checkout and the integrator owns it.
- The integrator merges each reviewed ticket branch into `ecosystem/build-2026-09-03`, checks that
  branch out in `.estate-clone/<unit>`, and runs the gate.

**Amended 2026-09-05.** Two lines above are out of date and one hazard is new.

- `twin/ENACT_MODE` reads `development` by the owner's standing instruction, so a builder MAY push
  a unit branch. The owner no longer pushes the eight branches; the integrator does, and merges as
  `pavc-other-hand`. Cut unit branches from that unit's `origin/main`, NOT from
  `ecosystem/build-2026-09-03`: many unit pull requests merged on 2026-09-04 and 09-05, so that
  integration branch is behind and branching from it re-proposes merged work.
- **`bash clone-estate.sh --refresh` used to delete `<unit>/.work/` along with the clone.** The
  integrator did that on 2026-09-05 while a builder was working and destroyed three worktrees, one
  of them in use. Nothing was lost only because the branch was already pushed. The script now
  KEEPS any unit carrying `.work/` and says so; `--refresh-force` is the way to delete them on
  purpose. Push your unit branch as soon as it is coherent, and do not rely on a worktree
  surviving: the clone is shared with every other builder and with the integrator.

## Definition of done, per ticket

1. A `verify-*.sh` in the gate (exit 0 true, 3 could-not-look with `SKIP: <reason>` last line,
   other exit false with `FAIL: <reason>` last line), discovered by `talk/verify-all.sh`.
2. Unit tests at the agreed seam (hub `tests/` for twin code; a `selfcheck` mode for a verify
   script) written first where the seam is pure code, red then green.
3. Typecheck when the change is hub Python: `<venv>/bin/python -m mypy twin` on the touched
   modules is clean or not worse than `main`.
4. The ticket file: `Status: resolved`, `## Answer` with what was built, which check grades it,
   every decision with its reason and label, and `## Waits on the owner` if anything does.
5. The map: one line under `Decisions so far` in `.scratch/ecosystem/map.md` (the integrator does
   this at merge time to avoid conflicts; the builder writes the line into the ticket's Answer as
   `Map line:`).
6. The final report lists files changed per repo, commits (hash, message), the exact verify
   command and its last five lines, and what was not done. A claim without a command output is a
   fail.

## Rules that do not bend

- Never fake a signature, a tag, a cluster or an observation. A check that cannot look exits 3.
- A clock appends observations, never declarations.
- Every price carries `perspective` and `currency`.
- Smallest diff that works. Reuse `fair.py`, `cage.py`, `party_artefact.py`, `adopter-gate.py`,
  `lib.sh`, `composition.py`. No new dependencies beyond pyyaml and jsonschema in the hub venv;
  estate scripts use `python3` stdlib plus pyyaml.
- Do not touch `.work/` of other tickets, `__pycache__`, `.venv`, `estate/` (stale),
  `.scratch/talk-spec/`, and do not edit `.claude/settings.json`.
- Do not edit `twin/enact_guard.py` unless the ticket is about it (65); commit such a change alone.
- KinD clusters `driftwood`, `tuppence`, `ludlow` exist locally. Do not delete them. An ephemeral
  cluster uses a fresh name and deletes itself.
- Do not run `talk/verify-all.sh` as a builder. Run your own script and the ones you changed.
- **`truth.yml` cannot land an observation on a branch that has DIVERGED from main, and a push
  is not what breaks it.** After writing its TRUTH line the workflow commits and runs
  `git pull --rebase --autostash origin main`, then pushes to the BRANCH. On `main` that rebase is
  a no-op and the push fast-forwards. On a ticket branch it rewrites every commit, so the result is
  not a descendant of the branch's own remote ref and the push comes back
  `! [rejected] ... (non-fast-forward)`. The observation is gone; the next run measures a different
  tree.
  Measured on 2026-09-05 during ticket 89, three times, including a controlled case: run 98 was
  rejected while the remote tip had not moved and nobody had pushed at all. Runs 92 and 95 went the
  same way. So **do not conclude from a lost observation that somebody pushed at the wrong moment**;
  on a branch it happens anyway.
  What follows for a builder:
  * **Do not merge `origin/main` into your ticket branch. Rebase onto it.** A merge commit
    guarantees the rebase rewrites history and guarantees the loss. A branch whose commits already
    sit linearly on current `origin/main` rebases to a no-op and its runs can land.
  * Still do not push while a run on YOUR branch is `in_progress`: it is a separate way to lose the
    same thing, and reading the top rows of `gh run list` is not enough because `truth` serialises
    across every branch at once, so the newest row is often somebody else's. Check with
    `gh run list --branch <yours> --json status --jq '[.[]|select(.status=="in_progress")]|length'`.
    A `pending` run has started nothing and can be superseded safely.
  * A branch TRUTH line is therefore usually only in the Actions log. Quote it from there if you
    need it, mark it as not citable, and never hand-write it into `talk/truth.log`: a builder does
    not author a clock's observation.
