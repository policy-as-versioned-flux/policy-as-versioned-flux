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

6. **A third clock runs on the owner's machine, and a rehearsal is never citable (added
   2026-09-03, ticket 92; ticket 75 Q10 owner-reasoned, the rest delegated under ADR-0025).**
   Point 1's clocks never call a model. The owner permitted one, on the condition that it runs
   inside Claude Code on his machine because no tokens exist anywhere else. So the model-backed
   steps run from `talk/local-clock.sh`, by hand or from launchd (`talk/local-clock.plist`), each
   as `claude -p "/<skill> <adopter>"` under the hub's own PreToolUse guard in `operations` mode,
   with `gh` outside the child's tools. What it writes: a branch on the adopter's clone plus a
   pull-request body, and a dated marker under the gitignored `.local-clock/`. What it never
   writes: `main`, a merge, a tag, `talk/truth.log`. A local run is not citable (NORTH-STAR S5),
   and `verify/local-clock/verify-local-clock.sh` grades only that the clock ran and that nothing
   leaked. Three calls made under this point:
   - *a headless run writes no override.* An override is a human's judgement claimed by a role;
     nobody is at the keyboard, so the run binds and positions at grade 5 and stops. The claim
     validator refuses an override from a run marked `headless`. That keeps this clock inside
     ADR-0023 D1: it proposes, it never prices.
   - *the world simulator stamps, and the stamp refuses.* `--inject FILE` reads one dated external
     signal for a rehearsal. The envelope is written `injected: true` (with when, by what and from
     which file) only under `.local-clock/`; the branch is named `rehearsal`; the claim file must
     carry the flag, which is what makes the validator refuse it; `twin/feed_signal.py` refuses
     the envelope; `--push` is refused; the gate scans every committed envelope, claim,
     observation and capture in nine repositories for the flag and fails on one. Marked, not
     hidden: the mark is the mechanism.
   - *the push is the owner's hand.* The guard refuses every enactment push from an agent and
     the clock's child cannot push either. `--push` runs after the model has stopped, under the
     owner's own `gh` login, and is refused inside any Claude Code session. Merging stays the
     other hand's (ticket 88). `verify-schedules.sh` does not grade this clock: it parses
     workflow YAML and this clock is not a workflow; its own check is the fifth script under
     `verify/`.

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

## Note, 2026-09-03 (ticket 66, delegated under ADR-0025)

The lane is unchanged: `talk/deck.md` stays outside `OBSERVATION_LANE`. The clock writes the
captures and the TRUTH line of a run and never the deck, so the committed deck always lags the log
by however many runs since someone last ran `python3 talk/build_deck.py` and committed.
`talk/verify-demo.sh` used to grade the committed deck against "this run", on the false premise
that `truth.yml` rebuilt the deck after the gate; every scheduled run whose grades moved (runs 14
to 22) was therefore called a hand edit. The fix taken is on the deck's side: a deck names the
recorded run it describes (`<!-- deck run=N hub=H source=recorded -->`, quoting that run's TRUTH
line), and its checks read that run's captures out of the lane commit that recorded them, never off
the disk. Drift-by-a-run is printed as a note, not graded.

Rejected, and left as an option for the owner: **widen the lane so the clock commits a generated
deck** (`OBSERVATION_LANE` gains `talk/deck.md`, and `truth.yml` gains a `build_deck.py` step after
the gate). It would keep the deck one run behind at most, but it makes the clock write a
declaration -- prose from `narration.json` rendered as a signed commit to `main` with no reviewer --
which is exactly what D1 exists to stop. The lane stays an observation lane. If the lag becomes
annoying, that is the decision to reopen, and it is the owner's: it changes what the clock's
signature vouches for.

## Note, 2026-09-03 (ticket 81): the sampler's own order is graded, not assumed

The lane's sampler (`drift-sample.yml` on driftwood, tuppence and ludlow) applies the composed set
on an ephemeral cluster and records what it sees. Twice (ticket 60 rounds 1 and 2) it recorded 16
of 16 rendered objects absent because it applied before the admission webhooks were up, and the
second fix mis-ordered itself by a first-occurrence string replace that nothing checked. The lane
faithfully appended an observation of the instrument's own race, and the estate's number carried it
as a red. From ticket 81 the executed order (kyverno wait, flux-operator wait, composed apply,
Kustomization waits, ResourceSet waits, sample) is graded by
`verify/sampler-wait-order/verify-sampler-wait-order.sh` in the hub gate, against the checkout,
before any merge. A clock still appends only observations; this note records that the instrument
taking them is itself a graded artefact, so a red that is the sampler's fault is caught in the
truth surface rather than read off the lane five hours later.

- **2026-09-03 (ticket 72, delegated under ADR-0025): a bump commit carries the twin's derived
  artefacts, and the sweep's moved path had never run.** The first real feed bump (driftwood PR
  #20) moved `party.yaml` and `composed/` together and left `twin/forward-intel/v1/feed.json` and
  `twin/signals.yaml` at the old pin, two reds on every truth run after. Both are derived from
  `inherits[]`, so Renovate's completer now re-derives them and `fileFilters` folds them into the
  same bot commit. That commit touches declaration paths, and D1 is untouched by it: Renovate is a
  proposer, its commit sits on a pull request a human merges, and the cage step in
  `renovate-run.yml` still asserts the job checkout stays clean. The sweep stays as the day-after
  safety net -- and its moved branch, `rc=$?` after a check that exits 1, had been dead under
  GitHub's `bash -e` since it was written (run 33627910027). It now lifts `-e` around the checks,
  proposes feed and lookup together, and appends its observation line on **both** paths, with
  `moved` and the proposal branch: a moved=true line on `main` is an observation, not a
  declaration, and it is the only offline proof the branch has fired.
  `driftwood/twin/verify-twin-sweep-moved.sh` runs the step's own shell under `bash -e` on planted
  copies and reads the series for that line, could-not-look until the clock supplies it.

- **2026-09-04 (tickets 56 and 85, delegated under ADR-0025): the clocks are read by a job that
  holds a credential, and graded by one that does not.** Point 3's third leg -- "in the gate:
  `verify/schedules/verify-schedules.sh`" -- was written as though the gate could ask GitHub
  anything. It cannot, and for a good reason: the gate step runs 84 `verify*.sh` cloned unpinned
  off eight other organisations' default branches, so `truth.yml` gives it `persist-credentials:
  false` and no `GH_TOKEN`. The consequence went unrecorded for five weeks: question 4, "did each
  clock run inside its own period", SKIPped on every citable run, and on 2026-09-04 five of
  thirteen clocks were red while the surface showed one SKIP.

  The credential is not widened; the work is split. `truth.yml` gains a **`clocks` job** with
  `permissions: {contents: read, actions: read}` that runs no third-party code and writes the raw
  facts -- per unit the ruleset state, per clock the remote `schedule:` and the newest scheduled
  run -- to a JSON file (`clock-verdict/v1`). The gate job takes it as an artifact and grades from
  it through `CLOCK_VERDICT`, holding nothing. The file carries observations and no verdict, so a
  verify script that reads it learns dates and conclusions it could have read from the public API
  itself. A file that is missing, stale (over six hours) or of the wrong schema is a named
  could-not-look; it never falls back to a credential the gate is not supposed to have. Locally,
  an authenticated `gh` is still used directly.

  Three smaller calls came with it, each because the surface was reporting something it had not
  observed:
  - *the documented non-zero exit is one conclusion, not "anything but success".* `truth.yml`
    re-raises the gate's red verdict, so its `failure` is excused. Every other non-success --
    `cancelled`, `timed_out`, a run still going -- is a clock that recorded nothing, and is now a
    red. The scheduled run of 09:55:43Z that day was cancelled by the single `truth` concurrency
    group when a push queued behind it, and graded PASS under the old rule. The group is now per
    event, so a clock queues only behind other clock runs.
  - *"this clock opens no pull request" is a PASS, not a SKIP.* SKIP means could-not-look, and the
    checker looked: it parsed the workflow. platform, nist and ico publish their own artefacts and
    have nothing upstream to diff, which the Consequences above already settle in as many words.
    Three unconditional SKIPs had held `verify-schedules.sh` at exit 3 whatever any credential
    could see. The PASS line names exactly what is not built there.
  - *a red clock names the ticket that owns it.* `verify/schedules/clock-owners.yaml` maps a
    clock to the open ticket that owns its red, and the FAIL line prints it. This is not a fourth
    outcome (ticket 83): a red stays red and stays in the count. An entry naming a ticket file or
    a workflow that does not exist is itself a FAIL, so the map cannot rot.

  What this does **not** change: nothing about the lane, D1 or D2. And the write half of SS-07 is
  untouched -- the cage step's `GH_TOKEN` is still handed to a step in the same job the gate ran
  in, step-scoped. Splitting the commit-and-push into a third job means handing the whole tree
  between runners with `id-token: write` for gitsign, which is a bigger change than either of
  these tickets, and it is recorded here rather than done quietly.
