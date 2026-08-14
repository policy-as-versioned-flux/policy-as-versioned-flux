# 78 — Forced-drift latency campaign: bounded actions, a real cluster, no wait

**What to build:** A second, separate instrument alongside build ticket 64's passive probe — one that
forces plausible operator actions on the real `kind-driftwood` cluster, at high resolution, and
captures how Flux and the probe respond. Where ticket 64 waits on organic behaviour over 91 days,
this runs now, in hours, because it does not wait for anything to happen on its own — it makes
something happen, on purpose, and measures the real system's real response.

**Decided via a `/wayfinder` grilling session, 2026-08-13/14**, opened on "we must be able to do
this better, not have a big long wait and need real data for our synthetic companies." Three
mechanisms were weighed and rejected before this one:

1. **Reconstructing history for the existing window** — rejected. `kind-driftwood` is 12 days old
   and carries no retained telemetry predating this instrument; there is nothing to reverse into.
2. **Fabricated synthetic samples** — rejected. The harness guard that protects `samples.jsonl`
   checks only that a timestamp postdates `window.yaml`'s first commit, not that a sample came
   from a real probe run. Fabricated data would pass undetected and hand build ticket 65 a false
   verdict on whether continuous reconciliation matters.
3. **An LLM-generated adversary producing realistic-looking synthetic drift** (the planter/detector
   pattern from build ticket 52, applied to this domain) — rejected. Decision ticket 12 Q2 already
   settled this for the reason that generalises here: planter and detector share model priors, so
   "a synthetic result is never evidence the twin anticipates the world, only evidence that the
   detection machinery works" (`twin/planter.py`, `SHARED_PRIOR_LIMITATION`). That bar was set on
   purpose and this ticket does not find a way around it — it goes around the *problem* instead, by
   staying on real infrastructure.

**What this measures, and what it explicitly does not.** This campaign answers a *mechanism*
question: when a plausible change happens, do Flux and the probe catch it, and how fast? It does
**not** answer build ticket 65's *organic base-rate* question — whether drift happens **without
anyone intending it**, in ordinary operation. Forcing the very thing you are trying to measure the
unforced rate of is not evidence of the unforced rate. The two instruments run alongside each
other on the same cluster, never merged: this campaign's events are excluded from ticket 65's
organic-drift tally by construction, not by discipline after the fact.

**Blocked by:** none — does not depend on build ticket 64's window and can start immediately.

**Status:** instrumented, **CAMPAIGN NOT YET RUN** — 2026-08-14. Same honest split ticket 64 itself
drew: the instrument is built, tested and verified against the real cluster's actual resource
shapes, and the campaign has not yet been executed for real. `forced-campaign-samples.jsonl` does
not exist yet. Running it takes roughly two hours of real, repeated mutation against
`kind-driftwood` and needs the operator's go-ahead to start — see the note at the foot of this
file.

**Reading list:** Build ticket 64 (the passive probe it runs alongside), build ticket 52 and
decision ticket 12 Q2 (the shared-prior limitation this ticket routes around rather than crosses).

- [x] A fixed, named action set — not an improvising agent choosing freely, which would itself
      carry model-prior bias about what "realistic" tampering looks like. Four trials, one action
      each: a manual `kubectl edit` on a ConfigMap outside GitOps; a `kubectl scale` left
      unreverted; the Flux Kustomization suspended and left suspended; a Flux-managed resource
      deleted outright.
      `estate/driftwood/drift/forced-campaign.yaml`'s `trials:` list names exactly these four,
      each with a `describes`, `action`, `undo` and `baseline_check`.
      `twin/drift.py`'s `ForcedCampaign.load` refuses any file that declares a different set
      (`REQUIRED_FORCED_TRIALS`) or a trial missing either its action or its undo —
      `tests/test_drift.py::test_a_forced_campaign_missing_a_trial_does_not_load`,
      `::test_a_trial_with_no_undo_does_not_load`, `::test_a_trial_with_no_action_does_not_load`.
      Checked against the live cluster before committing: `driftwood` runs no Deployment (Phase 0
      is ConfigMaps only), so trial 2 targets `flux-system/git-server` instead — the nearest real,
      reversible Deployment a plausible operator could scale and forget, named as such in the file.
- [x] Each trial samples every 15 seconds for a 30-minute window following the forced action —
      well past the ~5-minute reconcile interval already observed on this cluster
      (`ReconciliationSucceeded` events, ~103m/97m/92m apart in the sampled history) — so the
      actual correction curve is captured, not just its endpoints.
      `forced-campaign.sh`'s `sample_for_window()` calls the same unmodified `probe.sh` every
      `SAMPLE_EVERY_SECONDS=15` until `WINDOW_MINUTES=30` have elapsed, both pinned to match
      `forced-campaign.yaml`'s `resolution:` block exactly.
- [x] Every action is scripted with a companion, pre-recorded undo step. The cluster is verified
      back to declared-state baseline before the next trial runs, and before build ticket 64's
      passive probe's next hourly sample — a trial that leaves the cluster divergent would
      contaminate the organic measurement it runs beside.
      `forced-campaign.sh`'s `run_trial()` checks baseline before acting and again after undo,
      exiting the whole campaign rather than proceeding if either check fails.
      `wait_for_safe_start_window()` refuses to start a trial with fewer than
      `SAFETY_MARGIN_MINUTES=40` left before the next hour boundary, so action + 30-minute sample +
      undo + verify always finishes inside the current hour — the cluster is never mid-divergence
      when build ticket 64's `0 * * * *` cron fires.
- [x] Its own pre-registration file, sibling to `estate/driftwood/drift/window.yaml` in form and
      rigor (declares the action set, resolution, and guardrails up front) — proposed at
      `estate/driftwood/drift/forced-campaign.yaml`. States explicitly, in the file itself, that it
      is not evidence for build ticket 65's organic-drift claim.
      Built at that exact path. `not_organic_drift_evidence:` names build ticket 65 by number and
      `ForcedCampaign.load` refuses a file where that field omits it —
      `test_a_campaign_silent_on_organic_evidence_does_not_load`. The samples path
      (`forced-campaign-samples.jsonl`) is declared separately from ticket 64's `samples.jsonl`,
      and the loader refuses a file that reuses that name —
      `test_a_campaign_reusing_the_organic_samples_path_does_not_load`.
- [x] Coexists safely with build ticket 64's crontab probe against the same cluster — does not
      suspend, pause, or otherwise interfere with the hourly passive sampling while a trial runs.
      `forced-campaign.sh` never references `probe.sh`'s crontab or edits `probe.sh`; it calls the
      unmodified script with `DRIFT_SAMPLES` pointed at its own log. The safety-margin guard above
      is the mechanism that keeps the two from contaminating each other, not discipline after the
      fact.
- [x] Extends the invariant suite; never weakens it. Any invariant change names the invariant and
      cites the authorising decision ticket.
      One harness guard added, `forced_campaign_pre_registered_and_walled_off`
      (`twin/invariants/harness.py`) — same class of addition build ticket 34's precedent allows
      and build ticket 56 already used for its own harness guard ("extend the invariant suite only
      if you find a genuine gap the suite itself should close"). No constitutional invariant, no
      `twin/invariants/manifest.yaml` entry and no `checks_module_sha256` changed — harness guards
      sit outside that hash lock, which pins only `twin/invariants/checks.py`. `./bin/twin verify`
      run clean against it (see Evidence).
- [x] Declares its depth grade as a **computed checklist** against this ticket's own acceptance
      criteria — `full` is derived from the checklist, never asserted.
      This ticket has no owning decision ticket, the same position build ticket 56 (and, before
      it, 34) found for a ticket of this shape — so `twin/grades.py`'s machinery (which grades a
      capability against a *decision* ticket) does not apply, and this checklist itself, computed
      against the six items above, is the evidence: six checked, zero unchecked, all six citing
      the file, test or command that makes each true rather than asserting it.

## Also found and fixed: two-axis review of the diff (`d9448a7...HEAD`)

Same discipline build ticket 56 names for itself: findings recorded and fixed, not glossed over.

- **Standards axis.** `twin/README.md`'s own "The invariants" section — the file's own
  documented convention of listing every harness check by name and the live `./bin/twin verify`
  pass count — had gone stale the moment this ticket's tenth harness guard was added and never
  reflected there, the same shape of drift build ticket 56's audit found and fixed once before.
  Fixed: pass count corrected 57 → 58 (re-derived from a live run, not carried forward),
  `forced_campaign_pre_registered_and_walled_off` added to the enumerated list, "Nine checks" →
  "Ten checks", `pytest -q` count corrected to the live 1236.
- **Spec axis, real gap.** The `scale-left-unreverted` trial's target (`flux-system/git-server`,
  chosen because `driftwood`'s own namespace runs no Deployment) is not Flux-managed — it is
  applied by `scripts/up.sh`, outside GitOps — and `probe.sh` never observed it at all. Every one
  of that trial's 120 samples would have shown the three window subjects unchanged throughout,
  which is not evidence of anything: neither "does Flux catch it" nor "does the probe catch it"
  had a mechanism to be measured. Fixed: `probe.sh` gained a fourth, non-window field
  (`git_server_available_replicas`) — additive only, `Window.subjects` still reads only the three
  named ids, so build ticket 64's own reduction is unaffected — and `forced-campaign.yaml`'s trial
  now names the limitation and the fix in its own text rather than only in this section.
- **Spec axis, real gap.** `forced_campaign_pre_registered_and_walled_off`'s leak check (a
  timestamp-set intersection) would miss a misrouted `DRIFT_SAMPLES` override that sent a forced
  sample straight into build ticket 64's own log: a sample that never reached the campaign's own
  log leaves no timestamp there to intersect against, so it would slip through undetected — and no
  test exercised any of the check's failure branches at all, unlike every sibling harness guard.
  Fixed: `FORCED_DRIFT_MARKER` (`twin/drift.py`) — the literal value only the campaign's own
  configmap-edit trial ever writes — is now scanned for directly in the organic log, independent
  of and checked before the timestamp comparisons, so a misrouted write is caught regardless of
  which file it landed in. Three direct tests added
  (`tests/test_invariant_suite.py::test_a_forced_drift_marker_in_the_organic_log_is_caught` and two
  siblings) exercising all three failure branches via monkeypatching, matching the pattern every
  other harness guard in the suite already uses.
- **Spec axis, minor.** The sampling resolution (`SAMPLE_EVERY_SECONDS`/`WINDOW_MINUTES` in
  `forced-campaign.sh`) was cross-checked against `forced-campaign.yaml`'s `resolution:` only by
  comment, unlike the trial-id equivalence, which already had a test. Fixed:
  `test_the_orchestrator_script_resolution_matches_the_pre_registration` added.
- **Standards axis, judgement calls, not fixed** — noted, left as found: `ForcedCampaign.load`'s
  owner-refusal message is terser than `Window.load`'s sibling message (minor tone inconsistency,
  not worth the abstraction a shared helper would cost for two call sites); the orchestrator-script
  consistency tests read the bash script's literal source rather than an emitted artefact, a
  documented, deliberate trade-off (no YAML parser in bash) rather than an oversight.

## What is honestly not yet true

The instrument is built and every claim above is checked against real code, real tests and the
real cluster's real resource shapes — not simulated. What has **not** happened yet: the campaign
has not been run. No trial has fired, `forced-campaign-samples.jsonl` does not exist, and nothing
here is evidence of how fast Flux or the probe actually respond. That is a real, roughly two-hour,
repeated mutation of `kind-driftwood` and needs the operator to start it deliberately — see build
ticket 00's own "wait, plant, or force" section, added alongside this ticket: forcing is preferred
over waiting exactly because it answers the mechanism question *now*, but "now" still means a real
person choosing the moment a real cluster gets mutated four times in a row.

## Evidence

```
.venv/bin/python -m pytest tests/test_drift.py -q
  20 passed

.venv/bin/mypy twin tests conftest.py --ignore-missing-imports --warn-unused-ignores
  Success: no issues found in 130 source files

.venv/bin/python -m pytest tests/test_invariant_suite.py -q
  15 passed, 1 failed
  FAILED test_the_suite_is_green — drift_window_is_actually_being_sampled: known, pre-existing,
  unrelated (build ticket 64's own crontab probe has gone stale by >1 day; this ticket's new guard,
  forced_campaign_pre_registered_and_walled_off, is not in the failure list and passed clean)

.venv/bin/python -m pytest -q
  1235 passed, 1 failed in 319.51s (0:05:19) — re-run after the review fixes above and after
  pytest-xdist became the default (pytest.ini, `-n auto`); same single, pre-existing, unrelated
  failure as above, unmoved by anything this ticket touched.

.venv/bin/python -m twin verify
  RESULT: 58 passed, 1 failed, 2 skipped (0 pending invariants, 2 skipped and not faked)
  Same known failure. 57 → 58 is this ticket's own tenth harness guard going live, not a change
  elsewhere in the suite.
```
