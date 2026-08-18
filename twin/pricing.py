"""Response pricing, mitigation credit, and the join of the causal layer to the £.

Build ticket 30, from decision ticket 09. Until now the two halves of this system did not touch:
`twin propagate` composed elasticities and emitted no money, and `twin exposure` reported declared
valuations and propagated nothing. This is the multiplication between them, and it is gated three
times over rather than once.

## What a price is here

    price at C = the perspective's declared valuation of C  x  the propagated influence at C

**There is no severity slot, and that is a decision rather than an omission.** A separate authored
severity would give every component two authored magnitudes under one eye, with nothing
reconciling them and an author free to move the price through whichever number is watched less.
The perspective's declared valuation is the magnitude, so there is exactly one, it is already
evidence-graded, and the £ stays perspectival right down into the price: the operator and the
staff council price the same shock differently because they always did value the component
differently.

## Three gates, and they ask different questions

1. **The path** must be graded inside the pricing threshold. A grade-3 mechanism may not carry a
   number, so a shock that reaches a component only through one produces an unpriced structural
   blast radius. This is the gate the pocket org's `shared-database` origin fails.
2. **The valuation** must be graded inside the same threshold — the schema refuses an amount
   otherwise, so this one is already true at the source.
3. **Admission** must hold: a graded causal path has to reach a cash flow the perspective
   declared (build ticket 29).

A component that fails any of them is a **register entry**, named with its reason and carrying no
figure at all. Not a zero: zero is a price, and "we cannot price this" is not.

## Mitigation credit is a causal claim, and is gated like one

A response may declare what it removes from an impact. That claim carries an evidence grade and is
use-gated on exactly the rule above, which closes the classic unfalsifiability loophole — "the
incident did not happen *because* of our control" asserts a counterfactual, and asserting it is
free unless the evidence has to travel with it.

**An ungraded claim earns nothing rather than a default.** Two shapes, both handled: a response
that declares no `mitigates` block claims nothing and gets no credit field; a response whose claim
is graded outside the threshold gets a register entry naming the grade. Neither gets a number.

**Build ticket 86 closes decision ticket 08's action-state loop at this join.** A well-evidenced
mitigation claim is still only half of "the incident did not happen because of our control" — the
other half is that the control was actually put in place, which `twin/corroboration.py` (build
ticket 68) already answers from the ordinary model. `_credit()` reads it: an option whose response
carries no corroborated enactment is refused credit with a named reason, even when its own
mitigation claim is evidenced well enough to price. A claim and an enactment are two different
causal assertions — "this removes part of the impact" and "this was done" — and crediting one
without the other would let an unenacted control price exactly as a real one does.

## The ordering lock survives

Pricing a response still runs through `options.prefilter(...).priced()` and nothing here ever sees
a raw response. That is why this module can exist without reopening `prefilter_precedes_pricing`:
there is no callable here that takes an unfiltered option and returns a figure, and the invariant
asserts that as an allow-list on this module's public surface as well as on `options.py`'s.

## What this is not

Not a ranking, and not a recommendation. Cost and credit are reported in the same unit so that an
HR lever and a security control are directly comparable, and the reader draws the trade-off. There
is no field here that marks one option best, and build ticket 33's curve across the ensemble is
where a marked default lands.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import admission, corroboration, evidence, options as options_mod, propagate as propagate_mod
from .artefact import ArtefactError
from .canon import walk_keys
from .pert import Triple, quantise

if TYPE_CHECKING:  # pragma: no cover
    from .model import Graph, Overlay

# Why an impact could not be priced. Each is falsifiable by somebody: evidence a path, evidence a
# valuation, or show a route to the money.
PATH_TOO_WEAK = "the-causal-path-is-graded-outside-the-pricing-threshold"
NO_VALUATION = "this-perspective-declares-no-valuation-for-this-component"
VALUATION_TOO_WEAK = "the-valuation-is-graded-outside-the-pricing-threshold"
NOT_ADMITTED = "no-graded-causal-path-reaches-a-declared-cash-flow"
DIRECTIONAL_ONLY = "the-path-carries-a-direction-and-no-magnitude"

# Why a response earned no credit.
CLAIMS_NONE = "this-response-claims-no-mitigation"
CLAIM_TOO_WEAK = "the-mitigation-claim-is-graded-outside-the-pricing-threshold"
NOT_ENACTED = "the-option-this-claims-to-credit-has-no-corroborated-enactment"
NOTHING_PRICED_THERE = "the-impact-this-claims-to-reduce-was-not-priced"

BODY_KEYS = options_mod.BODY_KEYS | frozenset(
    {
        "origin", "impacts", "register", "responses", "comparison", "basis", "kind", "note",
        "valuation", "influence", "price", "depth", "worst_evidence_grade", "admitted_because",
        "reason", "detail", "evidence_grade", "component", "mitigation", "credit", "reduction",
        "claims", "reduces", "no_severity_slot",
        "traversal", "follows", "max_depth", "max_paths", "truncated", "known_limits",
        "truncated_by_depth", "truncated_by_path_count", "gated_at_grade",
        "structural_edges_do_not_propagate", "paths_are_not_aggregated",
        "gating", "pin", "version", "pricing_threshold", "path_admission_threshold", "rule",
        "admission_rule", "grades", "grade", "name", "admits", "example", "may_price", "digest",
        "attenuation", "attenuated", "composed", "factor", "amount", "basis", "sign",
    }
)

# The keys that may carry a **figure** in this body, named rather than derived. Everything else
# with a number in it is a grade, a depth or a count — and a price appearing anywhere outside this
# set is the failure `grade_5_only_path_never_prices` exists to catch.
PRICE_BEARING = frozenset({"price", "cost", "sampled", "credit", "valuation", "reduction"})


def _priced_triple(amount: float, influence: dict[str, Any]) -> dict[str, Any]:
    """A declared magnitude scaled by an influence triple, with the analytic moments beside it.

    Point-wise, and exact: an elasticity triple is non-negative and the magnitude is a scalar, so
    scaling is the one composition that needs no sampling. `twin propagate` already reports the
    sampled spread of the influence itself, and re-sampling it here would report the same
    uncertainty twice under a different name.
    """
    return Triple(
        float(amount) * float(influence["min"]),
        float(amount) * float(influence["mode"]),
        float(amount) * float(influence["max"]),
    ).moments()


def _register(component: str, reason: str, detail: str, **extra: Any) -> dict[str, Any]:
    """A refusal, named and reasoned, carrying no figure. Never a zero — zero is a price."""
    return {"component": component, "reason": reason, "detail": detail, **extra}


def impacts(
    graph: "Graph", perspective: dict[str, Any], origin: str
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    """Price every impact a shock at `origin` causes, under one perspective's eye.

    Returns the priced impacts, the register of refusals, and the traversal that produced both.
    Both lists come back: a refusal is an answer, so an impact that cannot be priced is reported
    with the reason rather than dropped.
    """
    threshold = evidence.threshold()
    propagation = propagate_mod.propagate(graph, origin, threshold=threshold)
    declared = {str(k): v for k, v in (perspective.get("values") or {}).items()}

    priced: list[dict[str, Any]] = []
    register: list[dict[str, Any]] = []
    for reached in propagation["reached"]:
        component = str(reached["component"])
        path = next((p for p in reached["paths"] if p["primary"]), None)
        if path is None:
            continue
        verdict = admission.admit(graph, perspective, component)

        if path["directional_only"]:
            register.append(_register(
                component, DIRECTIONAL_ONLY,
                "past the attenuation boundary a path carries a direction and no magnitude, so "
                "there is nothing to multiply a valuation by",
                depth=path["depth"],
            ))
            continue
        grade = path["worst_evidence_grade"]
        if grade is None or not evidence.may_price(int(grade)):
            register.append(_register(
                component, PATH_TOO_WEAK,
                f"the weakest hop on this path is graded {grade}, outside the published pricing "
                "threshold. The mechanism may be real; that it operates here is not evidenced, "
                "and a number resting on it would be false precision",
                depth=path["depth"], worst_evidence_grade=grade,
            ))
            continue
        valuation = declared.get(component)
        if valuation is None:
            register.append(_register(
                component, NO_VALUATION,
                "the path is evidenced and this perspective has not said what the component is "
                "worth to it. A price needs both, and inventing the second is the shadow price "
                "decision ticket 09 rejected",
                depth=path["depth"], worst_evidence_grade=grade,
            ))
            continue
        valuation_grade = int(valuation["evidence_grade"])
        if not evidence.may_price(valuation_grade) or "amount" not in valuation:
            register.append(_register(
                component, VALUATION_TOO_WEAK,
                f"the valuation is graded {valuation_grade}, so the schema refuses it an amount. "
                "There is nothing to scale",
                depth=path["depth"], evidence_grade=valuation_grade,
            ))
            continue
        if not verdict["admitted"]:
            register.append(_register(
                component, NOT_ADMITTED,
                "the path is evidenced and the valuation is evidenced, and no graded causal path "
                "reaches a cash flow this perspective declared. Connected and unpriceable is the "
                "answer, not a gap",
                depth=path["depth"], worst_evidence_grade=grade,
            ))
            continue

        amount = float(valuation["amount"])
        priced.append(
            {
                "component": component,
                "depth": path["depth"],
                "worst_evidence_grade": grade,
                "sign": path["sign"],
                "admitted_because": verdict["basis"],
                "valuation": {
                    "amount": amount,
                    "evidence_grade": valuation_grade,
                    "basis": str(valuation["basis"]),
                },
                # Both, for the reason `twin propagate` emits both: an attenuated figure whose
                # un-attenuated form was never shown makes the attenuation unfalsifiable.
                "influence": {
                    "composed": path["composed"],
                    "attenuated": path["attenuated"],
                    "attenuation": path["attenuation"],
                },
                "price": {
                    "composed": _priced_triple(amount, path["composed"]),
                    "attenuated": _priced_triple(amount, path["attenuated"]),
                },
            }
        )
    return priced, register, propagation["traversal"]


def _credit(
    option: dict[str, Any], claim: dict[str, Any] | None, priced: list[dict[str, Any]],
    overlay: "Overlay",
) -> dict[str, Any]:
    """What a response earns, or why it earns nothing. Never a default.

    The absent-claim branch is first on purpose: a response that says nothing is the common case,
    and reading silence as an average reduction is the exact unfalsifiability this gate exists to
    stop.
    """
    if not claim:
        return {"claims": False, "reason": CLAIMS_NONE,
                "detail": "this response declares no mitigation, so it earns no credit. Silence "
                          "is not an average reduction"}
    reduces = str(claim["component"])
    grade = int(claim["evidence_grade"])
    held = {"claims": True, "reduces": reduces, "evidence_grade": grade,
            "reduction": Triple.of(claim["reduction"]).moments(), "basis": str(claim["basis"])}
    if not evidence.may_price(grade):
        return {**held, "reason": CLAIM_TOO_WEAK,
                "detail": f"the claim that this removes part of the impact at {reduces!r} is "
                          f"graded {grade}, outside the published pricing threshold. 'The incident "
                          "did not happen because of our control' is a causal claim like any "
                          "other, and an unevidenced one earns nothing rather than a default"}
    option_id = str(option["option"])
    action_state = corroboration.state(overlay, option_id)
    if not action_state["may_price"]:
        return {**held, "reason": NOT_ENACTED,
                "detail": f"the claim that this removes part of the impact at {reduces!r} is "
                          f"evidenced well enough to price, but {option_id!r} itself has no "
                          f"corroborated enactment: {action_state['why']} 'The incident did not "
                          "happen because of our control' needs the control to have actually been "
                          "put in place, evidenced like everything else here — a mitigation claim "
                          "does not earn credit for a control nobody has seen enacted"}
    impact = next((i for i in priced if i["component"] == reduces), None)
    if impact is None:
        return {**held, "reason": NOTHING_PRICED_THERE,
                "detail": f"no priced impact at {reduces!r} in this shock, so there is nothing for "
                          "the reduction to be a fraction of"}
    reduction = Triple.of(claim["reduction"])
    return {
        **held,
        # Point-wise against the attenuated price, which is the figure the published schedule
        # says is the impact. Scaling the un-attenuated one would credit a control for removing
        # part of a number this system does not report as the impact.
        "credit": Triple(
            float(impact["price"]["attenuated"]["min"]) * reduction.low,
            float(impact["price"]["attenuated"]["mode"]) * reduction.mode,
            float(impact["price"]["attenuated"]["max"]) * reduction.high,
        ).moments(),
    }


def price(graph: "Graph", perspective: dict[str, Any], origin: str,
          responses: dict[str, dict[str, Any]], overlay: "Overlay") -> dict[str, Any]:
    """One shock, one eye: the impacts it prices, and what each admissible response costs and buys.

    The response half runs through the constraint pre-filter first and reads its product, never
    the raw responses — so an excluded option is absent here at any magnitude, exactly as it is
    absent from `twin options`.

    `overlay` is required, not defaulted: mitigation credit is gated on corroborated enactment
    (build ticket 86) via `corroboration.state(overlay, ...)`, and a parameter free to be omitted
    would be a silent way to skip the gate — exactly the default this module's own culture refuses
    everywhere else.
    """
    priced, register, traversal = impacts(graph, perspective, origin)
    admitted = options_mod.prefilter(perspective, responses)
    choice_set = admitted.priced()
    for entry in choice_set["priced"]:
        claim = (responses.get(entry["option"]) or {}).get("mitigates")
        entry["mitigation"] = _credit(entry, claim, priced, overlay)

    body = {
        "origin": origin,
        "perspective": str(perspective["id"]),
        "basis": {
            "kind": "declared-valuation-scaled-by-propagated-influence",
            "no_severity_slot": (
                "there is no authored severity anywhere in this system. The magnitude a price "
                "scales is the perspective's own declared valuation, so a component carries one "
                "authored figure under one eye rather than two that nothing reconciles — and the "
                "£ stays perspectival right down into the price"
            ),
            "note": (
                "the composed and attenuated prices are both reported, because an attenuated "
                "figure whose un-attenuated form was never shown makes the attenuation "
                "unfalsifiable. Neither is sampled: `twin propagate` reports the influence's own "
                "sampled spread, and re-sampling it here would report one uncertainty twice"
            ),
        },
        "gating": evidence.published(),
        "traversal": traversal,
        "impacts": priced,
        # A refusal is an answer. Every reached component appears in one list or the other, and
        # the register carries reasons rather than zeros.
        "register": register,
        "responses": choice_set,
        "comparison": (
            "cost and credit are in the same unit, so a non-technical lever and a technical "
            "control are directly comparable. Nothing here marks one best and nothing recommends "
            "one: the reader draws the trade-off, and the curve across the ensemble is build "
            "ticket 33"
        ),
    }
    refuse_undeclared_keys(body)
    refuse_unpriced_figures(body)
    options_mod.refuse_priced_removals(choice_set)
    return body


def refuse_undeclared_keys(body: dict[str, Any]) -> None:
    """The priced-impact body is closed. A key nobody declared does not serialise."""
    stray = sorted(set(walk_keys(body)) - BODY_KEYS)
    if stray:
        raise ArtefactError(
            f"a priced impact carries undeclared field(s) {', '.join(stray)}. This body is "
            "closed: adding a slot beside a refused impact needs an authorising decision ticket."
        )


def refuse_unpriced_figures(body: dict[str, Any]) -> None:
    """A register entry and an uncredited response carry no money. Not even a zero.

    Zero is a price, and it is the wrong one: "this impact cannot be priced" and "this impact is
    worth nothing" are different claims, and the second is usually false. Asserted at emission
    rather than trusted to hold because the branches were written the right way round.
    """
    for entry in body.get("register", []):
        stray = sorted(set(entry) - {"component", "reason", "detail", "depth",
                                     "worst_evidence_grade", "evidence_grade"})
        if stray:
            raise ArtefactError(
                f"the register entry for {entry['component']!r} carries undeclared field(s) "
                f"{', '.join(stray)}. A refused impact has nowhere to put a figure."
            )
    for entry in body.get("responses", {}).get("priced", []):
        mitigation = entry.get("mitigation") or {}
        if "credit" in mitigation and "reason" in mitigation:
            raise ArtefactError(
                f"the mitigation for {entry['option']!r} carries both a credit and a reason it "
                "earned none. A claim is credited or it is not."
            )
        if "reason" in mitigation and "credit" in walk_keys(mitigation):
            raise ArtefactError(
                f"the mitigation for {entry['option']!r} was refused credit and carries one "
                "anyway. An unevidenced claim earns nothing rather than a default."
            )


def spread(figures: list[float | None]) -> float | None:
    """The width between the widest and narrowest price, or nothing if there is only one eye."""
    numbers = [float(f) for f in figures if f is not None]
    return quantise(max(numbers) - min(numbers)) if len(numbers) > 1 else None
