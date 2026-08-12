"""Causally-gated admission to the £: the pricing boundary, derived rather than declared.

Build ticket 29, from decision ticket 09 (Q4). An impact enters the currency only when a causal
path runs from the component to a **cash flow the perspective declared**, and every hop on that
path is graded at or inside the published admission threshold.

Two declarations, and the difference between them is the whole mechanism:

* a perspective **declares where its money is**. That is legitimate — it is their ledger, and
  nobody else can name it for them.
* nobody declares **what is priceable**. That is computed from the graph, so the £ is only ever as
  wide as the causal layer can justify.

The consequence is the property this exists for: the answer to *"why isn't morale in the £?"* is
never *"we decided it doesn't count"* but *"no evidenced causal path yet"* — a falsifiable claim
somebody can go and fix. Reputation and morale price through modelled churn, attrition and
grievance paths, or they do not price at all.

**A refusal is an answer, not a gap.** A refused impact comes back carrying the unpriced structural
blast radius, so "we know this is connected and cannot price it" is what the output actually says.

**The known limit, named rather than implied.** A component the perspective declares *as* its cash
flow is admitted with no path and no grade, because it is the ledger rather than a claim about the
ledger. That is the one route by which an author reaches the £ without evidence: name
`brand-goodwill` as a cash flow and a reputational figure enters with nothing behind it. The two
bases are therefore reported and subtotalled **separately** wherever a figure appears, so a
declared amount and a derived one are never summed into one indistinguishable number. Constraining
what may be called a cash flow is a modelling question this code does not answer.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import blast, evidence

if TYPE_CHECKING:  # pragma: no cover
    from .model import Graph

# Why an impact was admitted. Both are derived; neither can be authored.
IS_CASH_FLOW = "the-component-is-itself-a-declared-cash-flow"
GRADED_PATH = "a-graded-causal-path-reaches-a-declared-cash-flow"

# Why it was not.
NO_CASH_FLOW_DECLARED = "the-perspective-declares-no-cash-flow"
NO_GRADED_PATH = "no-graded-causal-path-to-any-declared-cash-flow"


def cash_flows(perspective: dict[str, Any]) -> list[str]:
    return sorted({str(c) for c in (perspective.get("cash_flow") or [])})


def compact(verdict: dict[str, Any]) -> dict[str, Any]:
    """The same verdict with the ladder published once instead of once per refusal.

    Only the duplicated `gating` blocks go. Every reached component, every path and every reason
    stays, because those are the answer — the refusal is supposed to be readable, not a stub.
    """
    radius = verdict.get("blast_radius")
    if radius is None:
        return verdict
    return {**verdict, "blast_radius": {k: v for k, v in radius.items() if k != "gating"}}


def admit(graph: "Graph", perspective: dict[str, Any], component: str) -> dict[str, Any]:
    """Does an impact at `component` enter this perspective's £, and on what evidence?"""
    from .model import ModelError

    if component not in graph.components:
        raise ModelError(f"no component {component!r} in the graph of {graph.org!r}")

    threshold = evidence.admission_threshold()
    declared = cash_flows(perspective)
    out: dict[str, Any] = {
        "component": component,
        "perspective": str(perspective["id"]),
        "cash_flow": declared,
        "gating": {"path_admission_threshold": threshold, "pin": evidence.pin()},
    }

    if component in declared:
        return {
            **out,
            "admitted": True,
            "basis": IS_CASH_FLOW,
            "path": [],
            "worst_evidence_grade": None,
            "reaches": component,
        }

    # The same traversal the blast radius runs, gated at the admission threshold rather than the
    # pricing one. One traversal, and the caller says which published number it is gating on.
    radius = blast.radius(graph, component, threshold=threshold)
    reached = {entry["component"]: entry for entry in radius["admitted_to_pricing"]}
    for target in declared:
        entry = reached.get(target)
        if entry is None:
            continue
        return {
            **out,
            "admitted": True,
            "basis": GRADED_PATH,
            "path": entry["path"],
            "worst_evidence_grade": entry["worst_evidence_grade"],
            "reaches": target,
        }

    return {
        **out,
        "admitted": False,
        "reason": NO_CASH_FLOW_DECLARED if not declared else NO_GRADED_PATH,
        "detail": (
            f"no causal path from {component!r} reaches a declared cash flow with every hop graded "
            f"at or inside {threshold}. The boundary is derived from the graph, so this is not a "
            "decision that it does not count — it is a claim somebody can falsify by evidencing a "
            "path."
        ),
        # The refusal carries the traversal, so the answer is "connected, and unpriceable" rather
        # than silence. This is the first-class output for an impact that cannot enter the £.
        "blast_radius": radius,
    }
