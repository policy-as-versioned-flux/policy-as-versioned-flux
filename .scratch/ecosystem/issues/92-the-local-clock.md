# 92 — The local clock

Type: task (AFK)
Status: open
Blocked by: none

## Question

Ticket 75 Q10: the owner permits a model call in the twin, but the model must run inside Claude Code on this machine, because no tokens exist anywhere else. The owner's instruction: set up schedules or shell scripts, with run instructions, that run from this machine and simulate what the cron and then the real world would do.

Build the local half of the clock:

1. One entry point, `talk/local-clock.sh` (or under `twin/`), that a human or a launchd job runs on this machine. It performs, in order, what the GitHub clocks cannot: the steps that need a model, and any step that needs a cluster the runner never has and that ticket 86's lane does not cover. Each step calls Claude Code non-interactively with a named skill, and each result lands as a PR or a caged observation, never as a direct commit to main.
2. Run instructions in a README beside it: prerequisites, the one command, what it writes, how to read the result, how to stop it. Written for the owner, who will run it before the tour.
3. A launchd plist (this machine is macOS) that runs it on a schedule the owner picks, with logs under the repo's ignored scratch path, and a documented way to run it once by hand. Nothing in the plist holds a credential.
4. A "world simulator" mode: the same script can be told to inject a dated external signal (a headline, a market move, a regulator publish) so a demonstration can be rehearsed end to end without waiting on the real feeds. Every injected signal is marked as injected in its envelope, so a rehearsal is never cited.
5. The gate gains `verify-local-clock.sh`: the script exists, its README matches its flags, its last run left a dated marker, and no injected signal reached a citable run.

Done = the owner runs one command on this machine and a model-backed step lands a PR; the truth surface grades the marker and refuses an injected signal on a citable line.

## Notes

Charted by ticket 75 (Q10). Consistent with the map's note that reasoning is packaged as Claude Code skills a human runs; this ticket adds a schedule on the human's machine. Ticket 93 depends on it for the model call.
