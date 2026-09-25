# 142 — The twin cage check, and the schedule checker's blind spots

Type: task
Status: open
Blocked by: none

## Question

Graduated 2026-09-25 from grilling ticket 30, decisions 8, 14 and 16 (delegated), and ADR-0031.
This ticket carries ticket 30's definition of done: its check is wired into `talk/verify-all.sh`.

1. **The twin cage check.** A new `verify/twin-cage/verify-twin-cage.sh`, discovered by
   `talk/verify-all.sh`. It grades each adopter's served `origin/main`, never the local clone:
   - the twin-agent line in `composed/evidence.json` `prices[]` selects a rung on the ladder;
   - the twin-sweep jobs match that rung's dial row (ticket 30 decision 11): the twin job holds
     `contents: read`; the writer job has no hub checkout and no `uses:` step that is not inert;
     the hub checkout ref equals the commit in `twin/PIN.yaml`; every download is pinned by hash;
     the writer's steps fit the rung, for example no proposal step at `quarantine`;
   - on the hub side, the local-clock child holds no push capability (item 3).
   Until tickets 143 and 145 land, the check FAILs by name on each adopter. That red is the
   point: it measures the served workflow, not the plan.
2. **The schedule checker's blind spots** (`verify/schedules/schedules.py`):
   - `_SIGNED_ARTEFACT` misses `gh api ... pulls/N/merge`, `gh api ... releases`,
     `gh api ... git/refs`, `curl -X PUT .../merge`, `git update-ref` and `git push origin <tag>`;
   - the PASS line "nothing it runs is opaque to this checker" claims more than the check reads:
     it flags only `uses:` actions, and every sweep runs hub Python. Narrow the sentence or widen
     the measurement;
   - it grades each `.estate-clone/<unit>` working tree, not `origin/main`;
   - `lane.py` would grade a REST merge made with a scheduled token as a NOTE, not a FAIL.
3. **The local-clock child holds no push capability** (ticket 30 decision 14): no credential
   helper, no `GH_TOKEN`, `--strict-mcp-config`, a clock-only settings file, and Bash limited to
   named scripts instead of `python3 *`. Measured 2026-09-25: under `operations` the guard admits
   an adopter push made inside `python3 -c 'subprocess.run([...])'`.
4. **Delete the stale row** `driftwood/twin-sweep.yml: ticket: 72` from
   `verify/schedules/clock-owners.yaml`; that clock is green, and the file's own rule says delete.

## Notes

Every item reads the served artefact and the operation that reaches it. Test each fix against the
check as an adversary: a check that reads the text it grades takes the fix as input.
