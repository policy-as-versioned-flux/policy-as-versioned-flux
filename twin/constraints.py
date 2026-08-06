"""The constraint set: the universal floor, the published scope exclusions, and the positions.

Build ticket 27, from decision tickets 09 and 15. The authored governance artefact comes **before**
the code that enforces it: the pre-filter that actually removes an excluded option from a choice
set is build ticket 28, and it filters on what is declared here.

Three things, and they are separate on purpose.

**The universal floor** is the legal and ethical bottom, identical in every twin and not
negotiable by the operator. A perspective may **add** constraints; it has no way to remove one,
because the perspective schema has no field for removing anything and a perspective whose
constraint reuses a floor id does not load.

**The scope exclusions** are what the twin was not asked to model, named individually. Publishing
them does not stop strategic non-modelling — it removes its deniability.

**The positions** are the three the design carries openly rather than patching, plus the one that
must never be confused with them. Each is required by name below, because "presumably covered" is
how an absence happens, and because `covert sensing is permanently excluded` and `reflexivity is
deferred` are different claims that would otherwise blur into each other.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

from . import PACKAGE_DIR
from .canon import digest_of

if TYPE_CHECKING:  # pragma: no cover
    from .artefact import Artefact

CONSTRAINTS_PATH = PACKAGE_DIR / "constraints.yaml"
SCHEMA = "twin.constraints/v1"

FORBIDDEN, RUIN = "forbidden", "ruin"
CLASSES = (FORBIDDEN, RUIN)

STATED, UNSOLVED, DEFERRED, PERMANENTLY_EXCLUDED = (
    "stated", "unsolved", "deferred", "permanently-excluded",
)
STATUSES = (STATED, UNSOLVED, DEFERRED, PERMANENTLY_EXCLUDED)

# Named individually and required by name. A position that quietly disappears from the file is
# the failure mode this dictionary exists to catch, and the last entry is here because "covert
# sensing is permanently excluded" reads as a deferral unless the record says otherwise.
REQUIRED_POSITIONS: dict[str, str] = {
    "no-power-layer": STATED,
    "exit-cost-asymmetry": UNSOLVED,
    "reflexivity-and-goodhart-on-the-twin": DEFERRED,
    "covert-sensing": PERMANENTLY_EXCLUDED,
}


class ConstraintError(RuntimeError):
    """The constraint set does not say what it must, or a perspective tried to override it."""


@lru_cache(maxsize=8)
def load(path: Path | None = None) -> dict[str, Any]:
    """The versioned constraint set, validated on read.

    Validated rather than trusted, for the same reason the evidence ladder is: a constraint set
    that has quietly lost its floor still looks published.

    `ponytail:` cached per path, like the ladder. Every perspective validated asks for the floor
    ids, and the floor is immutable within a process.
    """
    source = path or CONSTRAINTS_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise ConstraintError(f"{source}: not a {SCHEMA} document")

    entries = doc.get("universal_floor")
    if not isinstance(entries, list) or not entries:
        raise ConstraintError(
            f"{source}: declares no universal floor. An empty floor is a twin in which every "
            "option has a price, which is the thing the two-tier split exists to prevent."
        )
    for entry in entries:
        _require(source, entry, "a universal-floor constraint", ("id", "forbids", "because", "source"))
        if entry.get("class") not in CLASSES:
            raise ConstraintError(
                f"{source}: constraint {entry.get('id')!r} has class {entry.get('class')!r}; "
                f"a constraint is one of {', '.join(CLASSES)}"
            )
    if len({str(e["id"]) for e in entries}) != len(entries):
        raise ConstraintError(f"{source}: two universal-floor constraints share an id")
    if not any(e["class"] == RUIN for e in entries):
        raise ConstraintError(f"{source}: the floor declares no ruin-class constraint")

    exclusions = doc.get("scope_exclusions")
    if not isinstance(exclusions, list) or not exclusions:
        raise ConstraintError(
            f"{source}: declares no scope exclusions. A twin that publishes none is claiming it "
            "was asked to model everything, which is never true."
        )
    for entry in exclusions:
        _require(source, entry, "a scope exclusion", ("id", "excluded", "because", "source"))

    positions = doc.get("positions")
    if not isinstance(positions, list) or not positions:
        raise ConstraintError(f"{source}: declares no positions")
    by_id: dict[str, dict[str, Any]] = {}
    for entry in positions:
        _require(source, entry, "a position", ("id", "status", "states", "source"))
        if entry["status"] not in STATUSES:
            raise ConstraintError(
                f"{source}: position {entry['id']!r} has status {entry['status']!r}; "
                f"a position is one of {', '.join(STATUSES)}"
            )
        by_id[str(entry["id"])] = entry
    for name, status in REQUIRED_POSITIONS.items():
        if name not in by_id:
            raise ConstraintError(
                f"{source}: position {name!r} is not stated. It is required by name because "
                "'presumably covered' is how an absence happens."
            )
        if by_id[name]["status"] != status:
            raise ConstraintError(
                f"{source}: position {name!r} is recorded as {by_id[name]['status']!r}; it is "
                f"{status!r}, and the two are different claims"
            )
    return doc


def _require(source: Path, entry: Any, what: str, fields: tuple[str, ...]) -> None:
    if not isinstance(entry, dict):
        raise ConstraintError(f"{source}: {what} is not a mapping")
    missing = [f for f in fields if not str(entry.get(f, "")).strip()]
    if missing:
        raise ConstraintError(
            f"{source}: {what} ({entry.get('id', '<no id>')!r}) declares no {', '.join(missing)}"
        )


def pin() -> dict[str, Any]:
    doc = load()
    return {"version": int(doc["version"]), "digest": digest_of(doc)}


def floor() -> list[dict[str, Any]]:
    return [_constraint(e, "universal") for e in load()["universal_floor"]]


def floor_ids() -> set[str]:
    return {str(e["id"]) for e in load()["universal_floor"]}


def _constraint(entry: dict[str, Any], tier: str) -> dict[str, Any]:
    return {
        "id": str(entry["id"]),
        "tier": tier,
        "class": str(entry["class"]),
        "forbids": str(entry["forbids"]).strip(),
        "because": str(entry["because"]).strip(),
        "source": str(entry["source"]).strip(),
    }


def published() -> dict[str, Any]:
    """The constraint set as a published artefact body: floor, exclusions, positions."""
    doc = load()
    return {
        "pin": pin(),
        "tiers": {
            "universal": "the legal and ethical floor; identical in every twin and not negotiable",
            "perspective": "a perspective's own red lines; may add to the floor, never remove from it",
        },
        "universal_floor": floor(),
        "scope_exclusions": [
            {
                "id": str(e["id"]),
                "excluded": str(e["excluded"]).strip(),
                "because": str(e["because"]).strip(),
                "source": str(e["source"]).strip(),
            }
            for e in doc["scope_exclusions"]
        ],
        "positions": [
            {
                "id": str(e["id"]),
                "status": str(e["status"]),
                "states": str(e["states"]).strip(),
                "source": str(e["source"]).strip(),
            }
            for e in doc["positions"]
        ],
    }


def declared_by(perspective: dict[str, Any]) -> list[dict[str, Any]]:
    """A perspective's own constraints, in both classes, as constraint records."""
    out: list[dict[str, Any]] = []
    for klass, field in ((FORBIDDEN, "forbidden"), (RUIN, "ruin")):
        for ident, forbids in sorted((perspective.get(field) or {}).items()):
            out.append(
                {
                    "id": str(ident),
                    "tier": "perspective",
                    "class": klass,
                    "forbids": str(forbids).strip(),
                    "because": f"declared by perspective {perspective['id']!r}",
                    "source": f"perspective {perspective['id']}",
                }
            )
    return out


def resolve(perspective: dict[str, Any]) -> dict[str, Any]:
    """The constraint set in force for one perspective: the floor, plus what it declared.

    The floor is listed first and is never filtered by anything the perspective says. There is no
    argument to this function that could remove one.
    """
    refuse_floor_override(perspective)
    return {
        "pin": pin(),
        "constraints": floor() + declared_by(perspective),
        "floor_is_negotiable": False,
    }


KIND = "constraint-set"
# Who is accountable for what is published. A role, never a person.
ROLE = "constraint-owner"


def artefact(command: list[str]) -> "Artefact":
    """The constraint set as an artefact: authored, and signed as a role by the caller.

    **Authored**, like the worksheet and for the same reason: no capability produced it. It is a
    declaration, and the declaration is the authority. So it carries no depth grade rather than a
    grade of `authored` — a depth grade measures how much of a decision ticket a capability has
    realised, and there is no capability here to measure.

    The evidence ladder ships in the same artefact on purpose. Changing what may be **priced** is
    the same kind of act as changing what may be **chosen**, so the two are published together and
    a reader sees both or neither.
    """
    from .artefact import AUTHORED, Artefact
    from .canon import sha256_hex
    from .evidence import LADDER_PATH, published as ladder_published

    return Artefact(
        kind=KIND,
        mark=AUTHORED,
        command=command,
        pins={
            "constraints_sha256": sha256_hex(CONSTRAINTS_PATH.read_bytes()),
            "evidence_ladder_sha256": sha256_hex(LADDER_PATH.read_bytes()),
            "role": ROLE,
        },
        depth={
            "grade": None,
            "capabilities": {},
            "note": "declared by a human in a role; no capability produced it",
        },
        body={
            "constraints": published(),
            "evidence_ladder": ladder_published(),
            "published_together": (
                "the pricing threshold is published beside the constraint set because changing "
                "what may be priced is the same kind of act as changing what may be chosen"
            ),
        },
    )


def refuse_floor_override(perspective: dict[str, Any]) -> None:
    """A perspective may add a constraint. Reusing a floor id is the only way it could shadow one.

    The perspective schema is closed and has no field for removing a constraint, so this is the
    remaining route: declare your own entry under a floor id and hope the resolver takes the last
    one it saw. It does not — this refuses the repository outright.
    """
    reserved = floor_ids()
    declared = {str(i) for i in (perspective.get("forbidden") or {})} | {
        str(i) for i in (perspective.get("ruin") or {})
    }
    clashing = sorted(declared & reserved)
    if clashing:
        raise ConstraintError(
            f"perspective {perspective.get('id')!r} declares {', '.join(clashing)}, which the "
            "universal floor already declares. A perspective may add constraints and may never "
            "override the floor, so an id it already holds is refused rather than merged."
        )
