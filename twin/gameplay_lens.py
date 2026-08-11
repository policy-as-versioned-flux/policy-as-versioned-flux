"""`gameplay-lens` (build ticket 46, decision ticket 13 Q3) — the third of the six skills seam 3
(build ticket 42, `twin/skills.py`) exists to evaluate.

Decision ticket 13 Q3: Wardley plays whose **preconditions actually hold**, checked against the
current map — "land grab: this component is about to commoditise, you own the adjacent capability,
no incumbent holds position", with the reason attached. **Threats push; opportunities must be
pulled**: a signal arrives and binds, but nothing arrives to say a component is about to
commoditise in a way the org could exploit, so `sweep()` below scans the map for precondition
matches on every scheduled run rather than waiting for one. Search/optimisation over the whole
what-if space was rejected (false precision at scale against a £ model already known to be
uncertain); an LLM's own suggestion was rejected as an *authority* (grade-5 model assertion by
construction) but is exactly the shape a candidate generator upstream of this module may take —
this module is the pattern-matcher that checks a proposal's preconditions against the map, and
`propose()` below is the deterministic reference implementation of that check.

`ponytail:` the catalogue below covers **two** of Wardley's ~100+ named gameplay patterns —
`land-grab` and `exploit-commoditisation` — chosen because both have preconditions genuinely
checkable from what this map represents: evolution position/stage, `needs`-edge dependency
structure, and ownership (`maintains`/`knows`/`owns` edges). Decision ticket 13's own worked
example also names **incumbency** ("no incumbent holds position") — this map carries no data on
rival occupancy anywhere, so that leg is never checked and every reason names the gap rather than
silently dropping it. Upgrade path: widen `_PLAY_CHECKS` as new, similarly checkable preconditions
are identified, or add a rival-occupancy signal and a third leg to `_land_grab`; nothing else in
this module, its tests, or its harness guard changes, because `evaluate()` (`twin/skills.py`)
reads `skill_fn` as a bare callable.

A proposed play is evaluated only for a component the org's **own overlay** declares (`org_components`
in the payload) — its actionable value chain — even though adjacency and ownership are checked
across the wider merged graph, which may include world-layer neighbours the org does not author
itself. Suggesting a play about a component the org has no standing to act on would not be an
opportunity for it.

Each proposed play carries a grade-5 claim-shaped dict (`kind`, `component`, `evidence_grade`,
`claimed_by`, `evidence`) — decision ticket 20's framing, "skills produce grade-5 claims" — but it
does not (yet) round-trip through `schema.SCHEMAS["claim"]`: no acceptance criterion here asks for
a proposed play to be authored into a model repository, only presented, so `schema.py`'s closed
`claim.kind` enum is left untouched rather than widened for a use nothing exercises.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from . import TOOL_VERSION, fixtures, wardley
from .artefact import Artefact, DERIVED
from .grades import Capabilities
from .model import Overlay, orgs
from .repo import ModelRepo
from .schema import PERSON_EDGES, STRUCTURAL_EDGE

SKILL = "gameplay-lens"
KIND_OPPORTUNITY_SWEEP = "opportunity-sweep"

# The same capability set `verbs.CAPS_RUN` carries: a sweep is the scenario engine's scheduled
# execution, unconditional, and this is its opportunity-side sibling (decision ticket 13 AC 4).
CAPS_GAMEPLAY_SWEEP = ["domain-model", "provenance", "scenario-engine"]


class GameplayLensError(RuntimeError):
    """A malformed payload."""


# -- the catalogue: two plays, both checkable purely from position, dependency and ownership ----

# Deep into the product band, nearing the commodity boundary — "about to commoditise" rather than
# already there. wardley.BANDS puts product at [0.5, 0.75); 0.6 is the round point 40% of the way
# through it, not a fitted one.
_LAND_GRAB_MIN_POSITION = 0.6

_YOUNG_STAGES = ("genesis", "custom-built")


def _index(
    payload: dict[str, Any],
) -> tuple[dict[str, dict[str, Any]], dict[str, set[str]], dict[str, set[str]], dict[str, set[str]]]:
    positions = {str(p["component"]): p for p in payload["positions"]}
    needs_out: dict[str, set[str]] = {}
    needs_in: dict[str, set[str]] = {}
    held_by: dict[str, set[str]] = {}
    for edge in payload["edges"]:
        etype, source, target = str(edge["type"]), str(edge["from"]), str(edge["to"])
        if etype == STRUCTURAL_EDGE:
            needs_out.setdefault(source, set()).add(target)
            needs_in.setdefault(target, set()).add(source)
        elif etype in PERSON_EDGES:
            held_by.setdefault(target, set()).add(source)
    return positions, needs_out, needs_in, held_by


def _land_grab(
    component: str,
    positions: dict[str, dict[str, Any]],
    needs_out: dict[str, set[str]],
    needs_in: dict[str, set[str]],
    held_by: dict[str, set[str]],
) -> dict[str, Any] | None:
    pos = positions.get(component)
    if pos is None or pos["stage"] != "product" or float(pos["evolution"]) < _LAND_GRAB_MIN_POSITION:
        return None
    adjacent = sorted(needs_out.get(component, set()) | needs_in.get(component, set()))
    owned = [(a, sorted(held_by[a])) for a in adjacent if held_by.get(a)]
    if not owned:
        return None
    held_component, holders = owned[0]
    return {
        "play": "land-grab",
        "component": component,
        "reason": (
            f"{component} sits at evolution position {float(pos['evolution']):.2f} in the product "
            "stage, nearing commodity. The org already holds an adjacent capability, "
            f"{held_component} (held by {', '.join(holders)}), in the value chain next to it. "
            "Incumbency is not checked: this map carries no data on whether a rival already holds "
            "the emerging position."
        ),
        "preconditions": {
            "stage": pos["stage"],
            "evolution_position": pos["evolution"],
            "adjacent_component_held": held_component,
            "held_by": holders,
            "incumbency_checked": False,
        },
    }


def _exploit_commoditisation(
    component: str,
    positions: dict[str, dict[str, Any]],
    needs_out: dict[str, set[str]],
    needs_in: dict[str, set[str]],
    held_by: dict[str, set[str]],
) -> dict[str, Any] | None:
    pos = positions.get(component)
    if pos is None or pos["stage"] != "commodity":
        return None
    young = sorted(
        d for d in needs_in.get(component, set()) if positions.get(d) and positions[d]["stage"] in _YOUNG_STAGES
    )
    if not young:
        return None
    dependent = young[0]
    return {
        "play": "exploit-commoditisation",
        "component": component,
        "reason": (
            f"{component} has reached the commodity stage (evolution position "
            f"{float(pos['evolution']):.2f}). {dependent} still depends on it from the "
            f"{positions[dependent]['stage']} stage — an immature layer sitting on a base that has "
            "just become a utility, which is what makes new genesis-stage value above it cheap to build."
        ),
        "preconditions": {
            "stage": pos["stage"],
            "evolution_position": pos["evolution"],
            "young_dependent": dependent,
            "young_dependent_stage": positions[dependent]["stage"],
        },
    }


# Sorted iteration keeps `propose()`'s output order deterministic without depending on dict order.
_PLAY_CHECKS: dict[str, Callable[..., dict[str, Any] | None]] = {
    "exploit-commoditisation": _exploit_commoditisation,
    "land-grab": _land_grab,
}
PLAYS = tuple(sorted(_PLAY_CHECKS))


def propose(payload: dict[str, Any]) -> dict[str, Any]:
    """The skill. `payload` is `{"positions": [...], "edges": [...], "org_components": [...]}` —
    `positions` is `wardley.positions(...)`'s own `.as_dict()` form, `edges` is `Graph.edges`'
    `.as_dict()` form, and `org_components` is the org's own overlay component ids (its actionable
    value chain, as opposed to the merged world+overlay graph adjacency and ownership are checked
    across).

    Returns `{"opportunities": [{"play", "component", "reason", "preconditions", "claim"}, ...]}`
    — every entry names the play, the component it targets, the concrete precondition evidence
    checked against the map, and a grade-5 claim-shaped dict (see module docstring). No parameter
    here can set a different grade.
    """
    missing = [f for f in ("positions", "edges", "org_components") if f not in payload]
    if missing:
        raise GameplayLensError(f"{SKILL}: payload declares no {', '.join(missing)}")

    positions, needs_out, needs_in, held_by = _index(payload)
    opportunities = []
    for component in sorted(payload["org_components"]):
        for name in PLAYS:
            hit = _PLAY_CHECKS[name](component, positions, needs_out, needs_in, held_by)
            if hit is None:
                continue
            opportunities.append(
                {
                    **hit,
                    "claim": {
                        "kind": "opportunity",
                        "component": component,
                        "evidence_grade": 5,
                        "claimed_by": f"{SKILL} (skill)",
                        "evidence": hit["reason"],
                    },
                }
            )
    return {"opportunities": opportunities}


def scorer(actual: Any, expected: Any) -> bool:
    """A pass needs the exact same set of (play, component) pairs — no more, no fewer — the same
    discipline `signal_classify.scorer` applies to (steep, component): a missing opportunity is a
    counterweight that did not happen, and an extra one is noise a human would have to triage."""
    actual_set = {(o.get("play"), o.get("component")) for o in actual.get("opportunities", [])}
    expected_set = {(pair[0], pair[1]) for pair in expected.get("opportunities", [])}
    return actual_set == expected_set


def payload_for(overlay: Overlay) -> dict[str, Any]:
    """The current map, in the shape `propose()` reads — built from the same graph
    `verbs.graph()` already emits (`Overlay.graph()`, `wardley.positions()`), not a second model."""
    built = overlay.graph()
    return {
        "positions": [p.as_dict() for p in wardley.positions(built.components).values()],
        "edges": [e.as_dict() for e in built.edges],
        "org_components": sorted(overlay.components),
    }


# -- the scheduled sweep: opportunity candidates, unconditionally --------------------------------


def sweep(repos: list[ModelRepo], caps: Capabilities, command: list[str]) -> Artefact:
    """Scan every org overlay of every named repository for gameplay-lens precondition matches.

    Unconditionally, and with no human naming a component — the structural fix for the negativity
    bias (decision ticket 13 Q3): a threat announces itself when a signal lands, but nothing
    arrives to say a component is about to commoditise in an exploitable way, so this has to go
    looking on every scheduled run rather than wait to be told. `twin/schedule.py`'s own `sweep()`
    is this function's threat-side sibling — same "list of already-opened repositories, no
    staleness skip" shape (build ticket 09) — and each org's bound-signal count is carried here
    as the push-side volume so the two are reported side by side rather than each living in its
    own artefact a reader has to go and subtract.
    """
    repo_pins = [repo.pin.as_dict() for repo in repos]
    opportunities: list[dict[str, Any]] = []
    by_org: list[dict[str, Any]] = []

    for repo in repos:
        for org in orgs(repo):
            overlay = Overlay.load(repo, org)
            result = propose(payload_for(overlay))
            for hit in result["opportunities"]:
                opportunities.append({"repo": repo.pin.as_dict(), "org": org, **hit})
            by_org.append(
                {
                    "repo": repo.pin.as_dict(),
                    "org": org,
                    "opportunities": len(result["opportunities"]),
                    "signals": len(overlay.signals),
                }
            )

    return Artefact(
        kind=KIND_OPPORTUNITY_SWEEP,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "repos": repo_pins,
        },
        depth=caps.depth_block(CAPS_GAMEPLAY_SWEEP),
        body={
            "opportunities": opportunities,
            "by_org": by_org,
            "counts": {
                "repos": len(repos),
                "orgs": len(by_org),
                "opportunities": sum(e["opportunities"] for e in by_org),
                "signals": sum(e["signals"] for e in by_org),
            },
            "reading_note": (
                "opportunities are pulled: this sweep scans the map for gameplay preconditions on "
                "every scheduled run, unconditionally, whether or not anything arrived. signals are "
                "pushed: they arrive and get bound, one at a time. The two counts sit side by side "
                "here so the counterweight to the evidence record's negativity bias (decision "
                "ticket 13 Q3) is measurable rather than only claimed."
            ),
        },
    )


# -- the labelled corpus: preconditions known to hold, and known not to ---------------------------


def labelled_corpus(tmp_dir: Path) -> list[dict[str, Any]]:
    """The labelled corpus `gameplay-lens` is evaluated against: three org maps built fresh from
    the existing fixtures (`twin/fixtures.py`) — not a fossilised duplicate of them — with the
    play the fixture-author knows to be present or absent under this catalogue's own preconditions.

    `netflix`: `streaming-experience` is product-stage at 0.625, nearing commodity, and the org
    holds the adjacent `cloud-compute` via `alex-rivera` (`knows`) — `land-grab` fires. `intel`:
    `foundry-services` is custom-built at 0.375, below the land-grab threshold, and intel's overlay
    declares no person edges at all — nothing fires, the negative case. `pocket`: `shared-database`
    is commodity at 0.9 and `identity-store` still depends on it from custom-built — that is
    `exploit-commoditisation`'s own positive case, which neither of the other two fixtures reaches
    (their commodity-stage components have no genesis/custom-built dependent).
    """
    items: list[dict[str, Any]] = []

    default_dir = fixtures.build(tmp_dir / "default")
    default_repo = ModelRepo.open(default_dir)
    expected_by_org: dict[str, list[list[str]]] = {
        "netflix": [["land-grab", "streaming-experience"]],
        "intel": [],
    }
    for org in sorted(expected_by_org):
        overlay = Overlay.load(default_repo, org)
        items.append(
            {
                "id": org,
                "input": payload_for(overlay),
                "expected": {"opportunities": expected_by_org[org]},
            }
        )

    pocket_dir = fixtures.build_pocket_org(tmp_dir / "pocket")
    pocket_overlay = Overlay.load(ModelRepo.open(pocket_dir), "pocket")
    items.append(
        {
            "id": "pocket",
            "input": payload_for(pocket_overlay),
            "expected": {"opportunities": [["exploit-commoditisation", "shared-database"]]},
        }
    )
    return items
