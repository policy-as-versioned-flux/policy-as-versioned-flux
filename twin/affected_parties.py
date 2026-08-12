"""The affected-parties register (build ticket 61), from decision ticket 15's Q4 mechanism list:
"An affected-parties register — outsiders bearing modelled costs are named, though outside the
currency (finding #2). Gives them no power; refuses to let their absence look like their
non-existence." `twin/constraints.yaml`'s own `harms-to-non-contracting-parties` scope exclusion
names this ticket as where that register lands.

**Authored per scenario, aggregated here.** Who is affected and how is a claim about *this*
scenario's own consequences, so it is declared inline on the scenario (`twin/schema.py`'s
`affected_parties`, required and non-empty — the same "populated as a step of authoring, not
optionally" the ticket asks for). This module does no authoring of its own: it walks what every
scenario in an overlay already declared and reports it as one flat, published list.

**Published alongside the constraint set.** `published()` carries `constraints.pin()` — the same
version and digest `twin constraints` itself reports — so a reader of the register can tell which
published constraint set it sits beside, the same way a priced option set or a scenario exposure
pins the constraints they were resolved against.

No currency claim. `admitted_because`/`exposure_by_basis` exist in `twin/admission.py` because a
£ figure has to say what admitted it; a party in this register carries no such field, because
nothing here prices anything — visibility is the whole of what this delivers, and the constraint
set's own `harms-to-non-contracting-parties` exclusion says why nothing more is claimed.
"""

from __future__ import annotations

from typing import Any

from . import constraints
from .model import Overlay

KIND = "affected-parties-register"


def register(overlay: Overlay) -> list[dict[str, Any]]:
    """Every affected party any scenario in this overlay declares, flattened and tagged by the
    scenario that named them.

    Reads only what scenario authoring already recorded: `affected_parties` is required and
    non-empty on every scenario (`twin/schema.py`), so this walk never has to guess whether a
    scenario considered its outsiders, only report what it said. Sorted by scenario then party id,
    so the same overlay always emits the same register regardless of dict ordering.
    """
    out: list[dict[str, Any]] = []
    for scenario_id, scenario in sorted(overlay.scenarios.items()):
        for party in sorted(scenario["affected_parties"], key=lambda p: str(p["id"])):
            out.append(
                {
                    "scenario": scenario_id,
                    "id": str(party["id"]),
                    "who": str(party["who"]).strip(),
                    "consequence": str(party["consequence"]).strip(),
                    "note": str(party["note"]).strip() if party.get("note") else None,
                }
            )
    return out


def published(overlay: Overlay) -> dict[str, Any]:
    """The register as a published artefact body, alongside the constraint set it sits beside."""
    return {
        "constraints_pin": constraints.pin(),
        "org": overlay.org,
        "parties": register(overlay),
        "currency_note": (
            "named here, not priced — perspectival £ puts a non-contracting party's harm outside "
            "the currency by construction (twin/constraints.yaml: harms-to-non-contracting-"
            "parties). This register gives them no power; it refuses to let their absence look "
            "like their non-existence."
        ),
    }
