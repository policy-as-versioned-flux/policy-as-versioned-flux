# 64 — Flux drift measurement: instrument and wait

**What to build:** **Started near the front deliberately, because it needs elapsed calendar time and nothing from the
twin.** Instrument real enactment repositories and measure whether controls actually drift between
deploys, and whether that drift matters.

The falsification verdict (ticket 65) cannot be honest without a measurement window, and starting
the measurement at its natural dependency position would delay the answer by that window on top of
everything else.

Record now, as a precondition rather than a ticket-66 discovery: the **org-wide GitHub setting that
blocks Actions from creating PRs is currently off and needs an admin** to change.

**Scope limit, recorded 2026-08-10 in `window.yaml` and not a change to the measurement.** This
instrument measures **state** drift: every subject compares a control's observed state against its
declared state. It cannot see **action** drift, where a control holds its declared state for the
whole window while an action crosses it. The window, subjects, drift definition and falsifiers are
exactly as pre-registered, and the guard still reads this file's first commit against the samples.
What the addendum corrects is the inference ticket 65 may draw, not the data.

**Blocked by:** 01

**Status:** instrumented, **NOT MEASURING** — corrected 2026-08-10. Window 2026-08-07..2026-11-06.

> **The probe has never run.** There is no `samples.jsonl`, there is no crontab entry, and the
> harness reports `0 sample(s)`. The `kind-driftwood` cluster exists and `probe.sh` is executable,
> so the instrument was built and never scheduled. Three of ninety-one days are already gone.
>
> The status line said "measuring" for three days. It was wrong, and this file was the only place
> anybody would have looked.
>
> This is the exact failure `window.yaml` predicted in its own words: *"a probe nobody owns stops
> running and nobody notices, and a stopped probe is what produces a confident 'no drift'."* It
> predicted it, and it still happened, because nothing checked that a sample had ever arrived.

**Reading list:** Decision ticket 22 (the Flux falsification test as recorded). Spec story 85.

- [x] Real enactment repositories instrumented to record control state continuously.
      `estate/driftwood/drift/probe.sh` samples the real `kind-driftwood` cluster: three control
      subjects, the Flux Kustomization's `lastAppliedRevision` as the deploy marker, and the
      suspend state. One JSON line per run, appended. **A run that cannot reach the cluster still
      writes a sample**, because an instrument whose silence reads as stability is worse than no
      instrument.
- [~] **The probe is actually scheduled and a sample has arrived.** Reopened 2026-08-10, part done.
      The instrument is **verified working**: run by hand at 09:51Z, cluster reachable, Flux ready,
      all three subjects sampled. The guard `drift_window_is_actually_being_sampled` is now on the
      suite and proven to bite on both silence and staleness. **What remains is the schedule** — no
      crontab entry exists, and installing one is the operator's to run, not the twin's.
- [x] Measurement runs for a declared window and the window is stated up front, not chosen after seeing results.
      `estate/driftwood/drift/window.yaml` declares both bounds, the cadence, the subjects, what
      counts as a drift event, and the two outcomes that would falsify the spec. Its first commit
      is the proof: the harness guard `drift_window_was_declared_before_it_was_measured` reads the
      file's git history and fails if any sample predates it. `Window.load` refuses a window that
      names no falsifier and one that names no operator.
- [x] Drift events recorded with the interval between deploy and divergence.
      `twin/drift.py events()` — a subject that changed between two consecutive samples with no
      revision change between them, carrying `since_deploy_seconds` from the last observed deploy.
      Declared as an **upper bound** in the window and again in the event, because the probe
      samples on a cadence.
- [x] The org Actions-create-PRs setting is recorded as an open precondition with a named owner.
      `estate/driftwood/drift/preconditions.yaml`, and `twin drift` prints it. Owner: an
      organisation administrator — the twin operator cannot change it. It blocks build ticket 66.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and cites the authorising decision ticket.
      A **harness guard**, not a seventeenth invariant: the constitution names sixteen and may not
      grow one without changing first, and this guards a yardstick — the pre-registration — the
      same way `worksheet_matches_the_pocket_org` guards the worksheet.
- [x] Declares its depth grade as a **computed checklist** against the owning decision ticket's acceptance criteria — `full` is derived from the checklist, never asserted.
      **No capability file, and that is the honest answer.** There is no decision ticket 22 in
      `.scratch/twin/issues/` — the reading list names one that was never written — so there are
      no acceptance criteria to compute a checklist against. A capability file with an invented
      yardstick would be a slot claiming a capability existed, which is the same refusal decision
      ticket 15 got at build ticket 27.

## Comments

**This ticket does not close today; it starts a clock.** Everything buildable is built and the
window runs to 2026-11-06. `twin drift` reports coverage first and events second on purpose: "no
drift observed" at 0% coverage and "no drift observed" at 95% coverage are different claims, and
build ticket 65 needs to be able to tell them apart.

**The reading list names a decision ticket that does not exist.** Build ticket 65 cites the same
one. The Flux falsification test is recorded in the spec (story 85) and nowhere else, so 65 has
no resolved decision to derive its verdict's *form* from. Worth resolving before 65 opens, and
recorded here rather than discovered then.

**No scheduled workflow, on purpose.** The cluster is local KinD and a hosted runner cannot reach
it, so a cron in GitHub Actions would record an unreachable cluster every hour and prove nothing.
The runner is operator cron on the machine holding the cluster, named in the window with its
crontab line. That is a genuine weakness — a probe nobody runs produces a coverage hole, and the
guard against it is that the hole is visible rather than that it cannot happen.

**Observation-only, decided 2026-08-13, before the crontab was installed.** `window.yaml`'s
`intervention_policy` addendum records it: no subject's state is deliberately changed for the
whole window, mirroring the planter/detector split build ticket 52 already draws elsewhere in this
repository. Named alongside it as a limitation rather than a fix: `kind-driftwood` has no real
operator population doing routine maintenance, which is what the window's 91-day sizing assumed
would eventually hand-edit something. A null result at close may mean "controls hold" or "nobody
was here" — this instrument cannot tell the two apart, and observation-only does not resolve that,
only refuses to manufacture a false answer to it.
