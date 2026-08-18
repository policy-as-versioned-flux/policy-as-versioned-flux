"""The named core ontology (decision ticket 07 AC 1 and AC 6; build ticket 79).

Decision ticket 07 pinned the entity types, relationship types and backbone at the design level
(2026-08-04); nothing collected them into one named, checked artefact. `twin/schema.py`'s
`SCHEMAS`, `EDGE_TYPES` and component vocabulary already **are** the ontology — every entity type
this system accepts is a key of `SCHEMAS`, every relationship type is a member of `EDGE_TYPES`.
This module assembles them into one place rather than re-typing them, the same shape
`does_not_do.py` takes against `grades.py`: a pure function of code that already exists, so the
artefact cannot drift out from under a schema change the way a hand-typed doc could.

**AC 6** (where £/risk, people, assets and signals attach) is the one part of this artefact that
is genuinely authored rather than derived — schema.py has no field that says "this is money" or
"this is a person" and none should exist to derive it from. `ATTACHMENT` below is that short,
hand-written mapping, and `_check_attachment_vocabulary` is what stops it drifting silently: every
schema kind and edge type it names is checked against `schema.py`'s own vocabulary at publish
time, so a rename there breaks this at generation time rather than only in a suite an author might
forget to run.
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from . import model, schema

if TYPE_CHECKING:  # pragma: no cover
    from .artefact import Artefact
    from .grades import Capabilities

KIND = "domain-model-ontology"


def entity_types() -> list[dict[str, Any]]:
    """One entry per schema kind `schema.py` declares, with its own required/optional fields.

    Reads `schema.SCHEMAS` directly rather than a hand-typed list: adding, renaming or reshaping
    a schema changes what this reports with no second edit anywhere.
    """
    return [
        {
            "kind": kind,
            "required_fields": sorted(sch.required),
            "optional_fields": sorted(sch.optional),
        }
        for kind, sch in sorted(schema.SCHEMAS.items())
    ]


def relationship_types() -> list[dict[str, Any]]:
    """Every edge type `schema.py` declares, and which family it belongs to.

    `schema.EDGE_TYPES` is the whole vocabulary; `STRUCTURAL_EDGE`/`CAUSAL_EDGE`/`PERSON_EDGES`
    are how `_refine_edge` already tells the families apart at validation time (decision ticket 07
    AC 3, ticked by build ticket 17) — this reads the same constants rather than re-deciding a
    split that is already load-bearing elsewhere.
    """
    out = []
    for edge_type in schema.EDGE_TYPES:
        if edge_type == schema.STRUCTURAL_EDGE:
            family, carries = "structural", "blast-radius and propagation; no measured effect"
        elif edge_type == schema.CAUSAL_EDGE:
            family, carries = "causal", "sign, lag, elasticity and evidence grade"
        elif edge_type in schema.PERSON_EDGES:
            family, carries = "knowledge", "no magnitude — the bus-factor substrate only"
        else:  # pragma: no cover - schema.py declares no fourth family today
            family, carries = "unclassified", ""
        out.append({"type": edge_type, "family": family, "carries": carries})
    return out


def backbone() -> dict[str, Any]:
    """The Wardley spine everything else positions against (decision ticket 07 Q1)."""
    return {"component_kinds": list(schema.COMPONENT_KINDS), "evolution_stages": list(schema.EVOLUTION)}


# AC 6 — where the named things attach to the graph. Short and hand-written, unlike the tables
# above: schema.py has no field that says "this is £" or "this is a person" for a table to derive
# from. Every `schema_kinds` entry is checked against `schema.SCHEMAS` by
# `_check_attachment_vocabulary` below, so a rename in schema.py fails this rather than drifting
# past it silently.
ATTACHMENT: tuple[dict[str, Any], ...] = (
    {
        "named": "£/risk",
        "attaches_as": "first-class scenario objects referencing nodes, never a node attribute",
        "schema_kinds": ("scenario", "response", "perspective"),
        "note": (
            "a `scenario` names the affected components and world models; a `response` prices a "
            "candidate lever against the component it `addresses`; a `perspective` holds the "
            "valuations and the £ boundary. Roll-ups onto nodes are a derived, "
            "never-authoritative view only (decision ticket 07 Q5)."
        ),
    },
    {
        "named": "people",
        "attaches_as": "structural person-edges to a component, never a node attribute",
        "schema_kinds": ("person", "edge"),
        "note": (
            f"a `person` is a node; {', '.join(schema.PERSON_EDGES)} edges connect it to a "
            "component — the whole of what bus-factor and blast-radius need. Behavioural facts "
            "live in the separately gated behavioural overlay, never here (decision ticket 07 Q6)."
        ),
    },
    {
        "named": "assets",
        "attaches_as": "a component of kind 'data' on the value-chain spine, like any other node",
        "schema_kinds": ("component",),
        "note": "a data asset is a component — same schema, same evolution axis, same edges.",
    },
    {
        "named": "signals",
        "attaches_as": "dated observations bound to a component or a response by a claim",
        "schema_kinds": ("signal", "claim"),
        "note": (
            "a `signal` is the dated observation; a `claim` "
            f"({', '.join(schema.SIGNAL_BINDING_KINDS)}) binds it to the component or response it "
            "is evidence about."
        ),
    },
)


def _check_attachment_vocabulary() -> None:
    """Every schema kind `ATTACHMENT` names must be real, checked at generation time."""
    for entry in ATTACHMENT:
        for kind in entry["schema_kinds"]:
            if kind not in schema.SCHEMAS:
                raise KeyError(
                    f"ontology.ATTACHMENT names schema kind {kind!r}, which schema.py no longer declares"
                )
    if "data" not in schema.COMPONENT_KINDS:
        raise KeyError("ontology.ATTACHMENT assumes 'data' is a component kind; schema.py has changed")
    for edge in schema.PERSON_EDGES:
        if edge not in schema.EDGE_TYPES:  # pragma: no cover - schema.py's own invariant
            raise KeyError(f"ontology.ATTACHMENT assumes {edge!r} is a declared edge type")


def published() -> dict[str, Any]:
    """The ontology as a publishable body."""
    _check_attachment_vocabulary()
    return {
        "backbone": backbone(),
        "entity_types": entity_types(),
        "relationship_types": relationship_types(),
        "attachment": list(ATTACHMENT),
    }


def artefact(
    command: list[str], caps: "Capabilities | None" = None, body: dict[str, Any] | None = None,
) -> "Artefact":
    """The ontology as a derived artefact, pinned to the exact schema/model source it read.

    Two source files, because AC 6's attachment table names both `schema.py` kinds and
    `model.py`'s person-edge / collection vocabulary — a change to either changes what this
    artefact reports.

    `body` lets a caller that already computed `published()` (to print it, say) pass that same
    dict through rather than paying for the walk over `schema.SCHEMAS` a second time — the same
    shape `does_not_do.artefact` takes.
    """
    from .artefact import DERIVED, Artefact
    from .canon import sha256_hex
    from .grades import Capabilities

    loaded = caps or Capabilities.load()
    return Artefact(
        kind=KIND,
        mark=DERIVED,
        command=command,
        pins={
            "schema_sha256": sha256_hex(Path(str(schema.__file__)).read_bytes()),
            "model_sha256": sha256_hex(Path(str(model.__file__)).read_bytes()),
        },
        depth=loaded.depth_block(["domain-model"]),
        body=body if body is not None else published(),
    )
