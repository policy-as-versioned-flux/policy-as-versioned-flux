# Flux drift measurement — instrument and wait

Build ticket 64 of `.scratch/twin/`, from spec story 85. **Run the test rather than assume the
answer.**

The spec claims policy-as-code needs *continuous* proof-of-force. Drift between deploys is the
candidate justification: a control silently removed after deployment is exactly the case a
point-in-time attestation misses and reconciliation catches. That must be demonstrated. If
controls do not drift, a deploy-time attestation suffices, Flux is a convenience rather than an
enabler, and the spec is amended.

This directory is the **instrument**. It reaches no conclusion. The verdict is build ticket 65 and
it reads this data — writing the conclusion into the instrument is how a measurement becomes a
demonstration.

It is started near the front of the build on purpose. It needs elapsed calendar time and nothing
from the twin, so starting it at its natural dependency position would delay the answer by a
whole measurement window on top of everything else.

## The four files

| file | what it is |
|---|---|
| [`window.yaml`](window.yaml) | The **pre-registration**. The question, both window bounds, the cadence, the subjects, what counts as a drift event, and what outcome would falsify the spec. |
| [`preconditions.yaml`](preconditions.yaml) | Open preconditions with named owners. Today: the org-level "Actions may create pull requests" toggle is off, which blocks build ticket 66. |
| [`probe.sh`](probe.sh) | One sample of control state, appended to `samples.jsonl`. A fact, never a verdict. |
| `samples.jsonl` | The log. Untracked — it is machine-local measurement output, and committing it would put a growing binary-shaped blob in a repository whose other artefacts are all reproducible. |

The reduction lives in [`twin/drift.py`](../../../twin/drift.py), because build ticket 65 builds
its verdict on top of it and the twin's test suite is where a wrong number gets caught.

## Run it

```sh
estate/driftwood/scripts/up.sh          # the cluster this measures
estate/driftwood/drift/probe.sh         # one sample
./bin/twin drift                        # the measurement so far: coverage, events, no verdict
```

On a cadence, on the machine holding the cluster:

```
0 * * * * cd <repo> && estate/driftwood/drift/probe.sh >> estate/driftwood/drift/probe.log 2>&1
```

Not a hosted CI runner. The cluster is local KinD and a hosted runner cannot reach it, so a
scheduled workflow would record an unreachable cluster every hour and prove nothing.

## Two properties worth stating

**The window was declared before the data arrived, and that is checked rather than claimed.** The
harness guard `drift_window_was_declared_before_it_was_measured` reads `window.yaml`'s git history
and fails if any sample predates its first commit. Retuning the window once the results looked
inconvenient fails the suite. `twin/drift.py` also refuses a window that names no falsifying
outcome and one that names no operator.

**A probe that cannot reach the cluster still writes a sample.** An instrument whose silence
reads as stability is worse than no instrument, so an outage appears as a coverage hole rather
than as a quiet stretch of no drift. `twin drift` reports what fraction of the declared window was
actually observed, and every gap wider than the declared cadence — including the one a stopped
cron leaves at the end. "No drift in 91 days" and "no drift in the hours we were looking" are
different claims, and only one of them is falsifiable.

## The known ceiling

The interval between deploy and divergence is an **upper bound**. The probe samples hourly, so a
divergence began somewhere in the hour before the sample that caught it. A watch on the Kubernetes
API would give the moment rather than the bound; it also needs a process that stays up, which is a
different reliability claim from a cron job that writes a gap when it fails. The bound is enough
to answer the question the window asks — *does it drift between deploys at all* — and the artefact
says so rather than presenting the figure as the moment.
