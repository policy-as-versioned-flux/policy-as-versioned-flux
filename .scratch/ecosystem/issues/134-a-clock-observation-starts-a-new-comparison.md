# 134 — A clock observation starts a new comparison

Type: task
Status: open
Blocked by: none

## Question

Charted 2026-09-24 by the integrator during the v3.3.0 rollout.

`compose/comparison_history.py` `identity()` at platform v3.3.0 hashes every non-hidden file in
the adopter repository outside `composed/`. Its comment says "a source edit deliberately starts a
new comparison". But the adopters' own clocks append to non-hidden files every day:
`drift/samples.jsonl`, `observations/twin-sweep.jsonl` and the lane's captures. ADR-0023 says a
clock appends observations and never declarations, so those files are observations, not source.

The consequences, measured or read on 2026-09-24:

1. After any lane commit, the recorded `comparison-inputs.after` in `composed/HEADER.yaml` no
   longer matches. `compose-check` then fails on every later pull request
   (`RealCompilerLayout.test_composition_bytes_do_not_depend_on_checkout_prefix`), and the
   pre-tag verify in `cut-release.yml` refuses with "comparison history does not match current
   source inputs". Tickets 131 and 132 hit the same failure from a test edit.
2. With replay off, `resolve()` then takes the working tree's header as the "before" (ticket 133),
   so a daily observation can reset what a comparison compares against.
3. Adopters moved to tools v3.3.0 on 2026-09-24, so this starts with their next lane commit.

What this ticket owes:

1. The identity hashes the adopter's declared source inputs only. Decide the rule and record why:
   an allow-list of the inputs the composer reads, or an exclusion of the paths each unit
   declares as its observation lane (the hub's map-surface check already reads those
   declarations).
2. A test at the `compose()` seam: appending a line to a lane file leaves the identity unchanged,
   and editing `party.yaml` changes it.
3. The platform change ships in a tools release, and each adopter moves its tools pin and
   recomposes once. Record what that costs.

## Done

A clock's observation no longer changes the comparison identity, and an adopter's
`compose-check` and pre-tag verify stay green across a lane commit.
