"""Scheduled execution across the standing scenario set (build ticket 09; decision tickets 11, 13).

Calibration is a property measured over volume (spec story 44), and volume that only arrives when
a forecaster feels like it is not volume — it is a selected sample (decision ticket 11 Q5: "we
cannot only forecast when we feel confident"). `sweep()` is the scheduled half: it runs every
scenario in every org overlay of every named model repository, unconditionally, and is meant to be
invoked by a scheduler that names no scenario itself.

Inherited machinery, and the two adaptations
---------------------------------------------
Research 04 named `/arckit:build --refresh` as the shape to inherit: resumable, DAG-cascading,
per-target SHA-256 staleness, one commit per wave. Two of its assumptions do not survive contact
with this system, and both are named here rather than folded in silently — the build ticket's own
instruction is that this adaptation "is this ticket's work, not a footnote."

1. **Single repository, widened to an org of repositories.** arckit's refresh state lives in one
   `projects/{P}/.arckit/state.json`, which assumes a single working tree. This system already
   holds several distinct model repositories — the default fixture, the pocket org, the
   regime-straddling fixture, and eventually one per flagship subject (build tickets 71-77) — so
   "the standing scenario set" has no single repository to be scoped to. `sweep()` therefore takes
   a **list** of already-opened repositories and walks every org overlay inside each of them,
   rather than assuming one.
2. **Hash-staleness is refused, on purpose.** arckit's refresh skips a target whose input hash has
   not moved since the last run. That is exactly the selection-bias mechanism decision ticket 11
   Q5 warns against: a twin that only re-forecasts when something changed would score beautifully
   and mean nothing, because the boring "no material change expected" days are precisely what a
   reliability diagram needs to see. So this sweep carries **no staleness check at all** — every
   scenario in the standing set runs every time `sweep()` is called, regardless of what did or did
   not change since the previous call. Harness guard `scheduled_emission_ignores_signal_presence`
   (`twin/invariants/harness.py`) asserts the consequence: two sweeps back to back over the same,
   unchanged repository emit the same forecast count, never a shrinking one.

What this does not build: the actual cron/CI cadence that calls `sweep()` on a clock (the same gap
build ticket 64 left for `estate/driftwood/` to own), and the standing library's own curation —
admissibility, precondition-triggered plays, event-triggered re-runs — which is build ticket 69.
Absent that curation, "the standing scenario set" means exactly what it says: every scenario
currently declared in every overlay this sweep is pointed at. Nothing here selects a subset, and
nothing here ranks one scenario over another.
"""

from __future__ import annotations

from typing import Any

from .artefact import Artefact, DERIVED
from .grades import Capabilities
from .model import ModelError, Overlay, orgs
from .regimes import AS_CONSUMED, RegimeError
from .repo import ModelRepo
from .schema import SchemaError
from . import verbs

KIND_SWEEP = "sweep"

# The scenario-engine capability owns "scheduled execution of the standing library is the forecast
# production line" (decision ticket 13, resolved Q1) — the same capability set `twin run` already
# carries, because a sweep is that verb invoked without a human naming the scenario.
CAPS_SWEEP = verbs.CAPS_RUN


def sweep(
    repos: list[ModelRepo],
    caps: Capabilities,
    command: list[str],
    at: str | None = None,
) -> Artefact:
    """Run every scenario in every org overlay of every named repository. Unconditionally.

    No human names a scenario here — contrast `twin run --scenario X`, which is the event-driven
    half decision ticket 11 Q5 keeps beside this one. `at` overrides every scenario's own declared
    time when given; left `None`, each scenario runs at the time it declares, exactly as `twin run`
    already does for one scenario at a time.

    A scenario that cannot run — no declared time, no world model, a regime refusal — is recorded
    in `failures` with the reason and the sweep continues. A scheduler with nobody watching it must
    not stop producing the calibration record because one scenario among many is malformed.
    """
    executions: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    repo_pins = [repo.pin.as_dict() for repo in repos]

    for repo in repos:
        for org in orgs(repo):
            overlay = Overlay.load(repo, org)
            for scenario_id in sorted(overlay.scenarios):
                run_command = verbs.command_for(
                    "run", org=org, scenario=scenario_id, regime=AS_CONSUMED, at=at
                )
                try:
                    bundle = verbs.run(repo, caps, org, scenario_id, AS_CONSUMED, run_command, at=at)
                except (verbs.VerbError, ModelError, RegimeError, SchemaError) as exc:
                    failures.append(
                        {
                            "repo": repo.pin.as_dict(),
                            "org": org,
                            "scenario": scenario_id,
                            "reason": f"{type(exc).__name__}: {exc}",
                        }
                    )
                    continue
                executions.append(
                    {
                        "repo": repo.pin.as_dict(),
                        "org": org,
                        "scenario": scenario_id,
                        "forecast_bundle": {
                            "sha256": bundle.digest(),
                            "pins": bundle.pins,
                            "forecast_count": len(bundle.body["forecasts"]),
                        },
                        "body": bundle.body,
                    }
                )

    return Artefact(
        kind=KIND_SWEEP,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": verbs.TOOL_VERSION, "capabilities_digest": caps.digest},
            "repos": repo_pins,
        },
        depth=caps.depth_block(CAPS_SWEEP),
        body={
            "regime": AS_CONSUMED,
            "at_override": at,
            "executions": executions,
            "failures": failures,
            "counts": {
                "repos": len(repos),
                "executed": len(executions),
                "failed": len(failures),
                "forecasts": sum(e["forecast_bundle"]["forecast_count"] for e in executions),
            },
        },
    )
