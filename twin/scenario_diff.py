"""`twin scenario-diff` (build ticket 88, decision ticket 13 AC 3): "where scenarios live and how
they are versioned/diffed."

Git already supplies the storage/versioning half — research 03's branch-per-scenario is just two
refs a repository can be opened at, and `ModelRepo.open(path, ref=...)` (build ticket 06) already
opens any ref, branch or commit alike. The actual gap this closes is the **renderer**: given a
scenario id and two refs, load the scenario definition at each and load the map
(`Graph.wardley()`, build ticket 14 — no separate authoring step) at each, and report what
changed. Two legs, not one: the scenario's own declared fields (question, proposition, at,
horizon, components, world models), and the **map-diff** research 03 names — the positions
(`wardley.positions()`) of every component either side's overlay places, since a scenario's own
`moves` are what a rewind/play composition actually changes on the map, and the map is the thing
git-native versioning was built to diff.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .artefact import Artefact, DERIVED
from .grades import Capabilities
from .model import Overlay
from .repo import ModelRepo, RepoError

KIND_SCENARIO_DIFF = "scenario-diff"

# No capability file names AC 3 alone — it is one of the seven scenario-engine criteria
# (`twin/capabilities/scenario-engine.yaml`), so this reads the identical set every other
# scenario-engine verb (`verbs.CAPS_RUN`, `schedule.CAPS_SWEEP`) already carries.
CAPS_SCENARIO_DIFF = ["domain-model", "provenance", "scenario-engine"]

# Scalar scenario fields worth reporting a before/after for. `id` is never diffed — it is what
# selects the scenario at each side, not a property of it.
_SCALAR_FIELDS = ("question", "proposition", "at", "horizon", "class")
# List-valued fields, diffed as added/removed rather than before/after — a component or world
# model either side names is what a reader of a map-diff actually wants to see move.
_LIST_FIELDS = ("components", "world_models")


class ScenarioDiffError(RuntimeError):
    """No such ref, or no scenario at either side of it."""


def _side(path: str | Path, org: str, scenario_id: str, ref: str) -> tuple[ModelRepo, Overlay, dict[str, Any] | None]:
    try:
        repo = ModelRepo.open(path, ref=ref)
    except RepoError as exc:
        raise ScenarioDiffError(f"ref {ref!r}: {exc}") from None
    overlay = Overlay.load(repo, org)
    return repo, overlay, overlay.scenarios.get(scenario_id)


def _scenario_fields(a: dict[str, Any] | None, b: dict[str, Any] | None) -> dict[str, Any]:
    changed: dict[str, Any] = {}
    for key in _SCALAR_FIELDS:
        before = a.get(key) if a else None
        after = b.get(key) if b else None
        if before != after:
            changed[key] = {"before": before, "after": after}
    for key in _LIST_FIELDS:
        before_set = set(a.get(key) or []) if a else set()
        after_set = set(b.get(key) or []) if b else set()
        if before_set != after_set:
            changed[key] = {"added": sorted(after_set - before_set), "removed": sorted(before_set - after_set)}
    return changed


def _map_diff(map_a: dict[str, Any], map_b: dict[str, Any]) -> dict[str, Any]:
    by_a = {p["component"]: p for p in map_a["positions"]}
    by_b = {p["component"]: p for p in map_b["positions"]}
    moved = []
    for component in sorted(set(by_a) & set(by_b)):
        pa, pb = by_a[component], by_b[component]
        if pa["stage"] != pb["stage"] or pa["evolution"] != pb["evolution"]:
            moved.append(
                {
                    "component": component,
                    "stage": {"before": pa["stage"], "after": pb["stage"]},
                    "evolution": {"before": pa["evolution"], "after": pb["evolution"]},
                }
            )
    return {
        "added": sorted(set(by_b) - set(by_a)),
        "removed": sorted(set(by_a) - set(by_b)),
        "moved": moved,
    }


def diff(
    path: str | Path,
    caps: Capabilities,
    org: str,
    scenario_id: str,
    ref_before: str,
    ref_after: str,
    command: list[str],
) -> Artefact:
    """`scenario_id` as it stood at `ref_before` against `ref_after` — a field-level diff of the
    scenario itself, plus the map-diff of every component either overlay places on it.

    A scenario present at only one side is not a `ScenarioDiffError` by itself — a scenario
    authored on an exploration branch and not yet merged is exactly what branch-per-scenario looks
    like mid-flight — it is reported as `scenario_present` and every scalar/list field reads
    against `None` on the absent side. Absent at *both* sides is the one case refused: there is
    nothing to diff.
    """
    repo_before, overlay_before, scenario_before = _side(path, org, scenario_id, ref_before)
    repo_after, overlay_after, scenario_after = _side(path, org, scenario_id, ref_after)
    if scenario_before is None and scenario_after is None:
        raise ScenarioDiffError(f"no scenario {scenario_id!r} in overlay {org!r} at either ref")

    map_before = overlay_before.graph().wardley()
    map_after = overlay_after.graph().wardley()

    return Artefact(
        kind=KIND_SCENARIO_DIFF,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "org": org,
            "scenario": scenario_id,
            "before": {"ref": ref_before, **repo_before.pin.as_dict()},
            "after": {"ref": ref_after, **repo_after.pin.as_dict()},
        },
        depth=caps.depth_block(CAPS_SCENARIO_DIFF),
        body={
            "scenario_present": {"before": scenario_before is not None, "after": scenario_after is not None},
            "scenario_fields": _scenario_fields(scenario_before, scenario_after),
            "map": _map_diff(map_before, map_after),
        },
    )
