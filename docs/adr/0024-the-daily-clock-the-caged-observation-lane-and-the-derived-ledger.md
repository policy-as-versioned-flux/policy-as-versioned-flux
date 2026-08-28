---
status: accepted
---

# The daily clock, the caged observation lane, and the rejection ledger derived from closed PRs

ADR-0015 point 5 said "No schedule runs anywhere". It was written when a recurring re-price was a
standing automation decision nobody had made, and every copy of `propose-tier.yml` repeated it as
"Nothing timed, ever -- no `schedule:` anywhere". ADR-0015's own Consequences section then names
the cost honestly: "The EOL feed re-prices with no commit... An EOL drift waits until a pin bump
lands or a human dispatches a run. **This is a named blind spot, not a closed one.**"

Ticket 28 closes it. NORTH-STAR principle 5 needs cages that re-price on a schedule; ticket 07 made
the price an explicit function of the date (the EOL ramp moves with `--as-of`, a stale signed size
widens to the cap), so a proposer that only runs on a push reads last month's number. The owner
settled the boundary on 2026-08-28 across tickets 10 and 16, with decisions **D1** and **D2**
recorded in ADR-0023. This ADR is the build's half of it: what runs on a clock, what the clock may
write, and what it may never write.

## The decision

1. **A daily clock on every unit.** Each publisher gets a `fetch` clock, each adopter a
   `renovate-run` and a `propose-tier` clock, each repository carrying a twin overlay a
   `twin-sweep` clock, and the hub keeps its `truth` run. **Each org picks its own UTC time and no
   cross-org ordering is promised**: 01:23 platform, 02:41 nist, 03:17 feeds, 04:09 ico, 05:31
   insurer, 05:47 the hub, 06:11/06:47/07:05 driftwood, 08:13/08:49 tuppence, 09:07/09:43 ludlow.
   GitHub delays scheduled runs under load, every joint in the chain waits on a human merge, and
   the truth run grades whatever state it finds.

2. **The adopter's clock re-composes at today's date and commits nothing.** `propose-tier` re-runs
   the composition at the parents it pins today, writes the result into the runner's temp directory
   and proposes from those fresh `prices[]`. A date-driven band crossing with no new tag is a
   proposal trigger like any other. The proposal carries its own priced evidence in the pull
   request body, so nothing needs writing back to `main`, and the run's last step fails if the
   working tree carries one byte.

3. **The observation lane is a cage, not a promise (D1).** A scheduled run may append
   `talk/truth.log`, `drift/samples.jsonl`, gate captures and `observations/**`. It may never commit
   a tier, a pin, a floor, an overlay, a priced evidence file or a published feed. Three things
   carry that, in three different places, so no single edit lifts it:
   - **in the workflow**: each scheduled job declares the allow-list as `env.OBSERVATION_LANE` and
     ends with a cage step that stages only those paths and fails the run when the tree holds
     anything else;
   - **on the server**: `.github/rulesets/observation-lane.json`, committed in every unit, restricts
     every declaration path. GitHub rulesets have no "this identity, only these paths" rule, so the
     cage is written as the complement, with an always-bypass for the organisation admin. A
     **human** still merges a reviewed tier PR; the scheduled identity has no bypass and cannot.
     The owner applies it with `gh api` -- no agent in this build holds, or should hold, that
     credential.
     **AMENDED 2026-08-28: this leg is prepared, not in force.** As first written the file was a
     *branch* ruleset carrying `file_path_restriction`, which is a *push*-ruleset rule; the shape
     is corrected, but GitHub allows a push ruleset only on a private or internal repository and
     every repository in this estate is public, with no ruleset applied on any of them (checked
     live that day). Until the repositories go private -- or a required status check on the
     default branch replaces it -- the two halves that actually hold are the workflow cage step
     and the gate. See `.github/rulesets/README.md` for both routes;
   - **in the gate**: `verify/schedules/verify-schedules.sh` parses every workflow's YAML and
     asserts all of the above, plus that no scheduled job can `git tag`, `gh release create` or
     `gh pr merge`. A release stays a human act.
     **Ceiling, named 2026-08-28:** that checker reads each step's inline `run:` shell, so a push
     from inside a called program (driftwood's `propose-tier` pushes from
     `platform/wargamer/tier_pr.py`) or from a marketplace action is invisible to it. What catches
     those is capability, not syntax: a scheduled job carrying `contents: write` with no cage step
     is a fault, and a non-inert `uses:` step in such a job is reported as unresolvable rather than
     passed. Its PASS line now says "no shell step in this job stages a declaration" instead of a
     flat "caged".

4. **Bot commits are signed.** Every scheduled commit is made with `gitsign` and the run's own
   Actions identity -- the same keyless OIDC -> Fulcio -> Rekor chain every `cut-release.yml`
   already uses for tags (ADR-0023, D3). This supersedes ADR-0015's "The proposal commit is
   unsigned".
   **AMENDED 2026-08-28** on two counts. First, the ruleset's `required_signatures` rule is
   REMOVED: GitHub does not recognise a gitsign signature as verified (the sigstore CA root is not
   in its trust root and the ephemeral certificate reads as expired without a Rekor lookup GitHub
   does not perform), so that rule would have refused every commit these clocks make. Provenance
   for a bot commit is the Rekor entry, not a GitHub badge. Second, the signing configuration is
   now written into each run's LOCAL git config rather than passed to the single `commit` command:
   `git pull --rebase` replays the commit, and with no `commit.gpgsign` in scope the replay came
   out unsigned -- in exactly the contended case the pull exists for.

5. **The rejection ledger is derived, and the fixture is deleted (provisional; the
   `<org>/<kind>/<slug>` key is D5).** The derivation itself, the deletion of the fixture and the
   30-day half-life are PROVISIONAL on a bare agree (`.scratch/ecosystem/issues/10-schedules-and-skills.md:80`);
   the ratified D5 is the EOL-ramp / `revoked[]` pricing decision (ADR-0023), and what it covers
   here is only the ledger's KEY shape. Corrected 2026-08-28 so the decided/provisional line stays
   readable, per the map's process rule.
   `platform/honesty/rejections.json` and `proposer_bounds.DEFAULT_REJECTIONS` are gone.
   `platform/wargamer/rejection_ledger.py` reads the closed-unmerged pull requests on the
   proposer's own dedupe branches and suppresses a key while
   `sum(0.5 ** (age_days / h)) >= reject_suppress`, keyed `<org>/<kind>/<slug>`. A rejected PR
   whose recorded curve hash or selection-policy version differs from today's does not count: a new
   GBP is a new question. `h` and the threshold are versioned in
   `platform/wargamer/rejection-decay.yaml`, a calibration knob beside `twin/decay.yaml`'s 180 days,
   not a literal. **Where the pull request list cannot be read, the ledger is empty and the proposer
   says so** -- it never suppresses in silence and never proposes in silence.

## Alternatives

- **Keep "no schedule anywhere".** Rejected. It leaves NORTH-STAR principle 5 false in the one
  place it is cheapest to make true, and ADR-0015 already recorded that as a blind spot rather than
  a decision.
- **A period per step** (feeds hourly, proposals daily). Rejected. It multiplies cron lines nobody
  can reason about for feeds that mostly do not move, and ticket 22's and ticket 24's own
  thresholds already express "how often this feed changes" as data.
- **Commit the re-composed evidence to `main` so the truth surface can read it.** Rejected. It is a
  machine commit to `main` with no reviewer, which is the exact thing the cage exists to stop; the
  proposal already carries its priced evidence.
- **A committed `rejections.json` the workflow appends to on PR close.** Rejected. It adds a file
  that can drift from the pull requests it summarises, and it needs a writer with `contents: write`
  on `main` -- another hole in the same wall.
- **Time decay with no reset for a new price.** Rejected. A rejection of GBP2,000 would silence a
  proposal of GBP20,000.
- **A ruleset that allow-lists the observation paths.** Not expressible: GitHub has
  `file_path_restriction` as a deny list and no per-identity path grant. The complement plus the
  admin bypass is the closest real cage, and the client-side step and the gate cover the rest.

## Consequences

- **ADR-0015 point 5 is superseded**, and so is its "The proposal commit is unsigned" consequence
  and its "Each adopter keeps its own rejection ledger... the committed
  `platform/honesty/rejections.json` stays as the war-gamer's own fixture". That fixture was read by
  all three adopters as their own, so a real tuppence run would have been suppressed by a rejection
  tuppence never made. ADR-0015 carries a dated banner; its file is not rewritten.
- **A clock cannot be proven from a branch.** GitHub runs the default branch's copy of a workflow
  and nothing else, so `verify-schedules.sh` reports could-not-look for every clock whose scheduled
  copy is still on `ecosystem/thin-slice`. It turns green one clock at a time as the owner merges,
  and it fails -- not skips -- for a clock that is on `main` with a `schedule:` and has stopped
  running.
- **The live window is 48 hours, not 24.** The declared period is daily; GitHub delays scheduled
  runs under load and drops them on a quiet repository. The extra day is slack, named as slack.
- **`platform`, `nist`, `ico` and `insurer` observe rather than fetch.** None ships an upstream
  fetcher yet, so their clock records what they have published and the sha256 of its payload each
  day. That is a real series: identical hashes are evidence nothing moved, and a hash that moves
  without a version moving is a tamper the clock can see. The shape to copy when a real fetch
  arrives is the feeds repo's own `fetch.yml` and `fetch/lib.py`, which already implement D2.
- **`h` is unvalidated.** 30 days is one review cycle, not a measurement. Revisit when a reviewer
  sees the same slug twice inside a month, or when a rejection re-raises before its reason changed.
- **The twin sweep's package is unpinned.** `twin-sweep.yml` reads the hub's default branch because
  the `twin` package does not self-version yet (ticket 11 answer item 1). The observation line
  records that fact on every run. Ticket 29 closes it.
