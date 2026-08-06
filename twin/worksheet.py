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

# Which emitted artefact each family of keys is resolved against. One worksheet, several
# artefacts: the graph stopped being the only place a hand-computable number lands at build
# ticket 19.
GRAPH, BLAST, EXPOSURE = "graph", "blast", "exposure"


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


# Which pocket-org artefacts the worksheet is checked against, and the arguments that produce
# them. Named here so the CLI and the suite check the same three things rather than drifting.
BLAST_ORIGIN = "shared-database"
SCENARIO = "portal-availability-2026"


def bodies_for(repo: Any, caps: Any) -> dict[str, dict[str, Any]]:
    """Emit the pocket org's graph, blast radius and exposure, and return their bodies."""
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
    }
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
