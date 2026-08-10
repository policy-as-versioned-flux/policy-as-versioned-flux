"""The pocket-org worksheet: hand-computed numbers, and the check that the code still matches.

Build ticket 15. A refusal test catches a reintroduced **absence**; it is satisfied by a
degenerate system — a triple that is present but garbage, an elasticity nobody recalibrated
three tickets later. This is the continuous coherence mechanism for that class: a tiny
organisation whose expected numbers are worked out by hand in a committed worksheet, checked
against the emitted artefact on every run.

The worksheet is **authored**; every line it checks is **derived**. That asymmetry is the point,
and it is the only place in this system where a human number is the authority.

A line whose key this module cannot resolve is **pending**, not passing: the arithmetic is
already written down, and the build ticket named in the worksheet is the one that must make it
computable. A pending line whose ticket has closed is a failure, the same shape as an invariant
still pending after its activating ticket (`no_invariant_pending_past_its_ticket`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import PACKAGE_DIR

WORKSHEET_PATH = PACKAGE_DIR / "pocket-org-worksheet.md"
POCKET_ORG = "pocket"

# Declared, not implicit: the expected column is decimal and the computed one is binary floating
# point, so the comparison rounds and says by how much.
DECIMAL_PLACES = 6

_ROW = re.compile(r"^\|\s*(\d+)\s*\|(.+)\|\s*$")
_ROLE = re.compile(r"^Authored-by-role:\s*(\S+)\s*$", re.M)
_D = re.compile(r"^D\((?P<component>[^)]+)\)$")
_K = re.compile(r"^K\((?P<component>[^)]+)\)$")
_R = re.compile(r"^R\((?P<source>[^\s)]+)\s*->\s*(?P<target>[^\s)]+)\)$")
_ELASTICITY = re.compile(r"^elasticity\.(?P<edge>[a-z0-9-]+)\.(?P<point>min|mode|max)$")
_ROLLUP = re.compile(r"^rollups\.(?P<name>[a-z0-9_]+)$")
_GRADE = re.compile(r"^evidence_grade\.(?P<edge>[a-z0-9-]+)$")
_BLAST = re.compile(r"^blast\.(?P<origin>[a-z0-9-]+)\.(?P<what>reached|admitted_to_pricing|unpriced)$")
_EXPOSURE = re.compile(r"^exposure\.declared\.(?P<perspective>[a-z0-9-]+)$")
_SPREAD = re.compile(r"^exposure\.spread(\.(?P<component>[a-z0-9-]+))?$")
_PERT = re.compile(r"^pert\.(?P<edge>[a-z0-9-]+)\.mean$")
_ATTENUATION = re.compile(r"^propagation\.attenuation\.(?P<component>[a-z0-9-]+)$")
_ATTENUATED = re.compile(
    r"^propagation\.attenuated\.(?P<component>[a-z0-9-]+)\.(?P<point>min|mode|max)$"
)
_COMPOSED = re.compile(r"^propagation\.(?P<component>[a-z0-9-]+)\.(?P<point>min|mode|max)$")
_JOINT = re.compile(
    r"^joint\.(?P<component>[a-z0-9-]+)\."
    r"(?P<what>paths|shared_edges|exact|if_independent|double_counting_avoided)$"
)
_QUERY = re.compile(
    r"^(?P<operation>intervene|observe)\.(?P<component>[a-z0-9-]+)\."
    r"(?P<what>severed|upstream|reached)$"
)
_OPTIONS = re.compile(
    r"^options\.(?P<perspective>[a-z0-9-]+)\.(?P<what>considered|removed|priced)$"
)
_OPTION_PRICE = re.compile(r"^option_price\.(?P<option>[a-z0-9-]+)\.mean$")
_ADMISSION = re.compile(r"^admission\.(?P<perspective>[a-z0-9-]+)\.(?P<component>[a-z0-9-]+)$")
# The join of the causal layer to the £ (build ticket 30). Keyed by origin as well as perspective,
# because a price is a fact about a *shock* — and the two origins in the table are there to show
# the gate admitting one and refusing the other.
_PRICE = re.compile(
    r"^price\.(?P<origin>[a-z0-9-]+)\.(?P<perspective>[a-z0-9-]+)\.(?P<component>[a-z0-9-]+)\."
    r"(?P<point>min|mode|max|priced)$"
)
_PRICE_SPREAD = re.compile(r"^price\.(?P<origin>[a-z0-9-]+)\.spread\.(?P<component>[a-z0-9-]+)$")
_CREDIT = re.compile(
    r"^credit\.(?P<origin>[a-z0-9-]+)\.(?P<perspective>[a-z0-9-]+)\.(?P<option>[a-z0-9-]+)\."
    r"(?P<point>min|mode|max|mean|credited)$"
)
# The credibility blend (build ticket 31), keyed by subject.
_CREDIBILITY = re.compile(
    r"^credibility\.(?P<subject>[a-z0-9-]+)\."
    r"(?P<what>n|own_mean|z|blended_min|blended_mode|blended_max)$"
)

# Which emitted artefact each family of keys is resolved against. One worksheet, several
# artefacts: the graph stopped being the only place a hand-computable number lands at build
# ticket 19.
GRAPH, BLAST, EXPOSURE = "graph", "blast", "exposure"
PROPAGATION, OPTIONS = "propagation", "options"
INTERVENTION, OBSERVATION = "intervention", "observation"
# Two priced shocks, keyed by origin (build ticket 30). One the gate admits and one it refuses,
# because a gate asserted only where it passes is asserted only where nothing could go wrong.
PRICE = "price"
# The credibility blend's own subject (build ticket 31).
CREDIBILITY = "credibility"
CREDIBILITY_SUBJECT = "identity-store-incident-cost"


class WorksheetError(RuntimeError):
    """The worksheet cannot be read, or says something it may not."""


@dataclass(frozen=True)
class Line:
    index: int
    key: str
    expected: float
    arithmetic: str
    asserted_by: str

    @property
    def ticket(self) -> str:
        found = re.search(r"build ticket\s+(\d{1,2})", self.asserted_by, re.I)
        if not found:
            raise WorksheetError(f"line {self.index} names no build ticket in its `asserted by` column")
        return found.group(1)


@dataclass(frozen=True)
class Result:
    line: Line
    actual: float | None
    pending: bool

    @property
    def ok(self) -> bool:
        return not self.pending and self.actual is not None and (
            round(self.actual, DECIMAL_PLACES) == round(self.line.expected, DECIMAL_PLACES)
        )


def _cell(text: str) -> str:
    return text.strip().strip("`").strip()


def load(path: Path | None = None) -> tuple[str, list[Line]]:
    """The authoring role and every line, in order."""
    raw = (path or WORKSHEET_PATH).read_text(encoding="utf-8")
    role = _ROLE.search(raw)
    if not role:
        raise WorksheetError(
            "the worksheet declares no `Authored-by-role:`. It is the one authored source of "
            "numbers in this system, so it says who is accountable for them."
        )
    lines: list[Line] = []
    for row in raw.splitlines():
        match = _ROW.match(row)
        if not match:
            continue
        cells = [_cell(c) for c in match.group(2).split("|")]
        if len(cells) != 4:
            raise WorksheetError(f"line {match.group(1)}: expected key, expected, arithmetic, asserted by")
        key, expected, arithmetic, asserted_by = cells
        try:
            value = float(expected)
        except ValueError:
            raise WorksheetError(f"line {match.group(1)}: {expected!r} is not a number") from None
        lines.append(Line(int(match.group(1)), key, value, arithmetic, asserted_by))
    if not lines:
        raise WorksheetError(f"{path or WORKSHEET_PATH}: no worksheet lines found")
    if [line.index for line in lines] != list(range(1, len(lines) + 1)):
        raise WorksheetError("worksheet lines must be numbered 1..N in order")
    return role.group(1), lines


def resolve(key: str, bodies: dict[str, dict[str, Any]]) -> float | None:
    """One worksheet key against the emitted artefacts. `None` means nothing computes it yet."""
    body = bodies.get(GRAPH, {})

    grade = _GRADE.match(key)
    if grade:
        for edge in body.get("edges", []):
            if edge["id"] == grade.group("edge") and "evidence_grade" in edge:
                return float(edge["evidence_grade"])
        return None

    radius = _BLAST.match(key)
    if radius:
        blast = bodies.get(BLAST)
        if blast is None or blast.get("origin") != radius.group("origin"):
            return None
        admitted, unpriced = blast["admitted_to_pricing"], blast["unpriced"]
        return float(
            {"reached": len(admitted) + len(unpriced),
             "admitted_to_pricing": len(admitted),
             "unpriced": len(unpriced)}[radius.group("what")]
        )

    moments = _PERT.match(key)
    if moments:
        for entry in bodies.get(PROPAGATION, {}).get("elasticities", []):
            if entry["edge"] == moments.group("edge"):
                return float(entry["mean"])
        return None

    for pattern, field in ((_ATTENUATED, "attenuated"), (_COMPOSED, "composed")):
        match = pattern.match(key)
        if match:
            path = _primary_path(bodies, match.group("component"))
            return None if path is None or field not in path else float(path[field][match.group("point")])

    combined = _JOINT.match(key)
    if combined:
        for reached in bodies.get(PROPAGATION, {}).get("reached", []):
            if reached["component"] != combined.group("component") or "joint" not in reached:
                continue
            joint, what = reached["joint"], combined.group("what")
            if what == "paths":
                return float(joint["paths_combined"])
            if what == "shared_edges":
                # The count, not the names: a worksheet line is a number, and how many edges two
                # paths have in common is exactly the fact the diamond is checking.
                return float(len(joint["shared_edges"]))
            return None if joint[what] is None else float(joint[what])
        return None

    asked = _QUERY.match(key)
    if asked:
        body = bodies.get(
            {"intervene": INTERVENTION, "observe": OBSERVATION}[asked.group("operation")], {}
        )
        if body.get("component") != asked.group("component"):
            return None
        what = asked.group("what")
        if what == "reached":
            return float(len(body["downstream"]["reached"]))
        return float(len(body[{"severed": "severed", "upstream": "upstream"}[what]]))

    attenuation = _ATTENUATION.match(key)
    if attenuation:
        path = _primary_path(bodies, attenuation.group("component"))
        return None if path is None else _maybe(path.get("attenuation"))

    counted = _OPTIONS.match(key)
    if counted:
        body = bodies.get(OPTIONS, {})
        if body.get("perspective") != counted.group("perspective"):
            return None
        what = counted.group("what")
        # `priced` reads the priced list rather than the pre-filter's `admitted`, so a survivor
        # that somehow failed to be costed shows up as a difference instead of being counted twice.
        if what == "priced":
            return float(len(body["priced"]))
        return float(len(body["prefilter"][what]))

    costed = _OPTION_PRICE.match(key)
    if costed:
        for entry in bodies.get(OPTIONS, {}).get("priced", []):
            if entry["option"] == costed.group("option"):
                return float(entry["cost"]["mean"])
        return None

    for pattern, reader in (
        (_PRICE, _priced_impact), (_PRICE_SPREAD, _price_spread), (_CREDIT, _mitigation_credit)
    ):
        match = pattern.match(key)
        if match:
            return reader(bodies.get(f"{PRICE}:{match.group('origin')}"), match)

    blend = _CREDIBILITY.match(key)
    if blend:
        credibility_body = bodies.get(CREDIBILITY)
        if credibility_body is None or credibility_body.get("subject") != blend.group("subject"):
            return None
        what = blend.group("what")
        if what == "n":
            return float(credibility_body["own_data"]["n"])
        if what == "own_mean":
            return _maybe(credibility_body["own_data"]["mean"])
        if what == "z":
            return float(credibility_body["credibility"]["z"])
        return float(credibility_body["blended"][what.removeprefix("blended_")])

    admitted = _ADMISSION.match(key)
    if admitted:
        for entry in bodies.get(EXPOSURE, {}).get("perspectives", []):
            if entry["id"] != admitted.group("perspective"):
                continue
            for verdict in entry.get("admission", []):
                if verdict["component"] == admitted.group("component"):
                    # 1 and 0 rather than true and false: the worksheet compares numbers, and an
                    # admission is a yes or a no with nothing in between.
                    return 1.0 if verdict["admitted"] else 0.0
        return None

    declared = _EXPOSURE.match(key)
    if declared:
        figures = bodies.get(EXPOSURE, {}).get("declared_exposure", {})
        value = figures.get(declared.group("perspective"))
        return None if value is None else float(value)

    spread = _SPREAD.match(key)
    if spread:
        exposure = bodies.get(EXPOSURE, {})
        component = spread.group("component")
        if component is None:
            value = exposure.get("exposure_spread")
            return None if value is None else float(value)
        for row in exposure.get("attribution", []):
            if row["component"] == component:
                return None if row["spread"] is None else float(row["spread"])
        return None

    rollup = _ROLLUP.match(key)
    if rollup:
        value = body.get("rollups", {}).get(rollup.group("name"))
        return None if value is None else float(value)

    positions = {p["component"]: p for p in body.get("wardley", {}).get("positions", [])}
    for pattern, field in ((_D, "differentiation_pressure"), (_K, "commodity_leverage")):
        match = pattern.match(key)
        if match:
            entry = positions.get(match.group("component"))
            return None if entry is None else float(entry[field])

    risk = _R.match(key)
    if risk:
        for entry in body.get("wardley", {}).get("dependency_risk", []):
            if (entry["from"], entry["to"]) == (risk.group("source"), risk.group("target")):
                return float(entry["dependency_risk"])
        return None

    elasticity = _ELASTICITY.match(key)
    if elasticity:
        for edge in body.get("edges", []):
            if edge["id"] == elasticity.group("edge") and "elasticity" in edge:
                return float(edge["elasticity"][elasticity.group("point")])
        return None
    return None


def _eye(body: dict[str, Any] | None, perspective: str) -> dict[str, Any] | None:
    if body is None:
        return None
    return next((e for e in body["perspectives"] if e["perspective"] == perspective), None)


def _priced_impact(body: dict[str, Any] | None, match: "re.Match[str]") -> float | None:
    """One component's price under one eye, or `0` where the gate refused it.

    `priced` is `1` or `0` rather than a figure, for the reason an admission verdict is: a refused
    impact carries no number anywhere, so the only thing the table can compare is whether it was
    priced at all.
    """
    entry = _eye(body, match.group("perspective"))
    if entry is None:
        return None
    component, point = match.group("component"), match.group("point")
    found = next((i for i in entry["impacts"] if i["component"] == component), None)
    if point == "priced":
        return 0.0 if found is None else 1.0
    return None if found is None else float(found["price"]["attenuated"][point])


def _price_spread(body: dict[str, Any] | None, match: "re.Match[str]") -> float | None:
    if body is None:
        return None
    for row in body["attribution"]:
        if row["component"] == match.group("component"):
            return None if row["spread"] is None else float(row["spread"])
    return None


def _mitigation_credit(body: dict[str, Any] | None, match: "re.Match[str]") -> float | None:
    """What a response earned, or `0` where its claim earned nothing.

    `credited` is the leg that matters: an unevidenced mitigation claim must come back with no
    figure at all, and a table that could only read figures would never notice the difference
    between "earned nothing" and "earned zero".
    """
    entry = _eye(body, match.group("perspective"))
    if entry is None:
        return None
    option = next(
        (o for o in entry["responses"]["priced"] if o["option"] == match.group("option")), None
    )
    if option is None:
        return None
    credit = option["mitigation"].get("credit")
    if match.group("point") == "credited":
        return 1.0 if credit else 0.0
    return None if credit is None else float(credit[match.group("point")])


def _primary_path(bodies: dict[str, dict[str, Any]], component: str) -> dict[str, Any] | None:
    """The ranked-first path to a component in the emitted propagation, if there is one."""
    for reached in bodies.get(PROPAGATION, {}).get("reached", []):
        if reached["component"] != component:
            continue
        return next((p for p in reached["paths"] if p["primary"]), None)
    return None


def _maybe(value: Any) -> float | None:
    return None if value is None else float(value)


# Which pocket-org artefacts the worksheet is checked against, and the arguments that produce
# them. Named here so the CLI and the suite check the same things rather than drifting.
BLAST_ORIGIN = "shared-database"
PROPAGATION_ORIGIN = "shared-database"
SCENARIO = "portal-availability-2026"
PERSPECTIVE = "the-operator"
# The subject of the do/observe pair (build ticket 22). `order-service` on purpose: it has both a
# cause above it and effects below it, so the downstream halves match and only the upstream halves
# differ — which is the whole of the distinction, isolated.
QUERY_COMPONENT = "order-service"
# The two priced shocks (build ticket 30). `order-service` is the only origin whose path to the
# portal is graded well enough to price, and `shared-database` is the one every route out of which
# crosses the grade-3 edge. Both, because a gate asserted only where it admits is not a gate.
PRICE_ORIGINS = ("order-service", "shared-database")


def bodies_for(repo: Any, caps: Any) -> dict[str, dict[str, Any]]:
    """Emit every pocket-org artefact the worksheet is checked against, and return their bodies."""
    import json

    from . import verbs

    org = POCKET_ORG
    emitted = {
        GRAPH: verbs.graph(repo, caps, org, verbs.command_for("graph", org=org)),
        BLAST: verbs.blast(
            repo, caps, org, BLAST_ORIGIN, verbs.command_for("blast", org=org, origin=BLAST_ORIGIN)
        ),
        EXPOSURE: verbs.exposure(
            repo, caps, org, SCENARIO, None, verbs.command_for("exposure", org=org, scenario=SCENARIO)
        ),
        PROPAGATION: verbs.propagate(
            repo, caps, org, PROPAGATION_ORIGIN,
            verbs.command_for("propagate", org=org, origin=PROPAGATION_ORIGIN),
        ),
        OPTIONS: verbs.options(
            repo, caps, org, PERSPECTIVE, verbs.command_for("options", org=org, perspective=PERSPECTIVE)
        ),
        INTERVENTION: verbs.intervene(
            repo, caps, org, QUERY_COMPONENT,
            verbs.command_for("intervene", org=org, component=QUERY_COMPONENT),
        ),
        OBSERVATION: verbs.observe(
            repo, caps, org, QUERY_COMPONENT,
            verbs.command_for("observe", org=org, component=QUERY_COMPONENT),
        ),
    }
    for origin in PRICE_ORIGINS:
        emitted[f"{PRICE}:{origin}"] = verbs.price(
            repo, caps, org, origin, None, verbs.command_for("price", org=org, origin=origin)
        )
    emitted[CREDIBILITY] = verbs.credibility(
        repo, caps, org, CREDIBILITY_SUBJECT,
        verbs.command_for("credibility", org=org, subject=CREDIBILITY_SUBJECT),
    )
    return {name: json.loads(art.to_bytes())["body"] for name, art in emitted.items()}


def check(bodies: dict[str, dict[str, Any]], path: Path | None = None) -> list[Result]:
    _, lines = load(path)
    results = []
    for line in lines:
        actual = resolve(line.key, bodies)
        results.append(Result(line=line, actual=actual, pending=actual is None))
    return results


def overdue(results: list[Result]) -> list[str]:
    """Pending lines whose build ticket has already closed. A silent gap in the yardstick."""
    from .invariants.harness import build_ticket_status, ticket_is_closed

    out = []
    for result in results:
        if not result.pending:
            continue
        status = build_ticket_status(result.line.ticket)
        if status is not None and ticket_is_closed(status):
            out.append(f"line {result.line.index} ({result.line.key}) waits on build ticket "
                       f"{result.line.ticket}, which is {status!r}")
    return out
