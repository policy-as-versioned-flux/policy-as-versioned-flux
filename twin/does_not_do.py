"""The does-not-do register (build ticket 77, decision tickets 15 and 22).

Decision ticket 15 built the published-scope-exclusions device (`twin/constraints.py`'s
`scope_exclusions`) so strategic non-modelling would be visible rather than deniable. This is the
same primitive turned on the demo itself: what a viewer is shown is a slice of each capability's
owning decision ticket, never the whole of it, and the gap has to be as visible as an exclusion is.

**Generated, never authored.** `constraints.yaml`'s exclusions are hand-written because they name a
choice a human made about what the twin was asked to model. This register names a fact about the
code instead: which acceptance criteria are still unchecked. There is no YAML file behind it and
no field through which an entry could be typed — `register()` is a pure function of
`grades.Capabilities`, so the register can never drift from the checklists it reads. Drift between
a demo's narrated honesty and its actual state is exactly the failure build ticket 77 exists to
make structural instead of narrated (decision ticket 22 Q3).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from .grades import Capabilities

if TYPE_CHECKING:  # pragma: no cover
    from .artefact import Artefact

KIND = "does-not-do-register"


def register(caps: Capabilities | None = None) -> list[dict[str, Any]]:
    """One entry per unchecked acceptance criterion, across every loaded capability.

    A capability graded `full` contributes nothing — there is nothing left to disclose. Ordered by
    capability name then criterion index, so the register is deterministic given the same
    checklists: an unordered walk would fail `identical_pins_identical_bytes` on iteration order
    alone rather than on anything that actually changed.
    """
    loaded = caps or Capabilities.load()
    entries: list[dict[str, Any]] = []
    for graded in loaded:
        for criterion in graded.unchecked:
            entries.append(
                {
                    "id": f"{graded.capability}-{criterion.index}",
                    "does_not_do": criterion.text,
                    "because": (
                        f"decision ticket {graded.owning_ticket} AC {criterion.index} is not yet "
                        f"realised; {graded.capability} is graded {graded.grade!r}"
                    ),
                    "source": f"decision ticket {graded.owning_ticket}, capability {graded.capability!r}",
                }
            )
    return entries


def published(caps: Capabilities | None = None) -> dict[str, Any]:
    """The register as a publishable body, with the totals it is counted against."""
    loaded = caps or Capabilities.load()
    checked, total = loaded.aggregate()
    return {
        "capabilities_surveyed": len(list(loaded)),
        "criteria_checked": checked,
        "criteria_total": total,
        "entries": register(loaded),
    }


def artefact(
    command: list[str], caps: Capabilities | None = None, body: dict[str, Any] | None = None,
) -> "Artefact":
    """The register as a derived artefact.

    Derived, not authored: nothing here is a human's choice at publication time, only a read of
    checklists that already exist. The depth block names every capability the register surveyed —
    the same capabilities whose gaps it is disclosing.

    `body` lets a caller that already computed `published(caps)` (to print it, say) pass that same
    dict through rather than paying for `register()`'s walk over every capability a second time.
    """
    from .artefact import DERIVED, Artefact

    loaded = caps or Capabilities.load()
    names = sorted(g.capability for g in loaded)
    return Artefact(
        kind=KIND,
        mark=DERIVED,
        command=command,
        pins={"capabilities_digest": loaded.digest},
        depth=loaded.depth_block(names),
        body=body if body is not None else published(loaded),
    )
