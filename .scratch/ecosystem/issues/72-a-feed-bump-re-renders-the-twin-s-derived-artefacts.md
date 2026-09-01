# 72 — A feed bump re-renders the twin's derived artefacts

Type: task (AFK)
Status: open
Blocked by: none

## Question

TRUTH run 18 (2026-09-01T09:41Z, hub 031b91a, driftwood 27f1cf2) shows two new driftwood reds
that are direct fallout of the first real step 2 (ticket 61, PR #20: threat-register v1 → v2 in
one bot commit):

- `verify-twin-overlay.sh`: `twin/forward-intel/v1/feed.json` is not what the overlay renders.
- `verify-twin-scenarios.sh`: the signal lookup has no row for `feeds/feed/threat-register/v2`
  and still carries rows for `v1`, which party.yaml no longer pins.

Ticket 61's postUpgradeTasks completer updates `party.yaml` and `composed/` but leaves the twin's
derived artefacts (the signal-lookup rows and the rendered forward-intel feed) at the old pin.
Every future feed bump will redden the same two checks the same way. Make the completer (or the
same bot commit) re-derive the twin's artefacts from the new pin, and prove it: the next merged
feed-bump PR leaves both checks green on the TRUTH line that reads it. Done = both checks green
on a citable run whose driftwood commit contains a Renovate feed bump.

## Notes

Surfaced by ecosystem ticket 60 while watching the first post-61 truth run. The reds are real
estate defects (ticket 55's rule: every red real, explained, finishable), not instrument faults.
The fix lands in driftwood; the enact guard means the owner pushes and merges it.

**2026-09-01, 12:31Z: the same defect killed twin-sweep's first scheduled firing.** The sweep
step runs `python3 twin/emit-forward-intel.py --check`, which exits 1 on the stale feed, and the
run fails. Two findings:

1. The sweep exists precisely to re-render a moved feed, but it cannot: the job step executes
   under GitHub's default `bash -e`, so the `rc=$?` branch that maps exit 1 to `moved=true` is
   unreachable — any real move aborts the step before the branch runs. The step needs `set +e`
   around the check (the same pattern verify-reconcile.sh uses), or `|| rc=$?`.
2. Even with that fixed, the sweep re-renders the feed but does not touch the signal-lookup
   rows, so the second red (`no row for feeds/feed/threat-register/v2`) needs the completer (or
   the sweep) to re-derive the lookup too.
