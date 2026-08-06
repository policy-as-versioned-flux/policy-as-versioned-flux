"""The three verbs of the walking skeleton: sense, run, score.

One dated signal binds to a component; one scenario executes and emits forecasts; a forecast is
scored against a recorded outcome. The loop closes before anything is deepened, because scoring
dictates what every other component must record (spec: "Scoring, first").

Every capability here sits at `partial`, which means **at least one** of its owning decision
ticket's acceptance criteria, not most of them. What is unchecked is visible in each artefact's
`depth` block rather than described in prose somewhere nobody reads.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .artefact import Artefact, DERIVED, load as load_artefact
from .blob import BlobRef
from .canon import digest_of, sha256_hex
from .grades import Capabilities
from .model import ModelError, Overlay
from .repo import ModelRepo
from .schema import REGIMES
from . import blast as blast_mod, constraints, evidence, scoring

CAPS_SENSE = ["domain-model", "provenance", "sense-move"]
CAPS_RUN = ["domain-model", "provenance", "scenario-engine"]
CAPS_SCORE = ["domain-model", "provenance", "sense-move"]
# The graph now carries causal edges and a Wardley map, so the causal layer is one of the
# capabilities that produced it and its depth travels with the artefact (build ticket 17).
CAPS_GRAPH = ["domain-model", "provenance", "causal-layer"]
CAPS_BLAST = ["causal-layer", "domain-model", "provenance"]
CAPS_EXPOSURE = ["currency-regimes", "domain-model", "provenance"]

KIND_BOUND_SIGNAL = "bound-signal"
KIND_FORECAST_BUNDLE = "forecast-bundle"
KIND_SCORE_CARD = "score-card"
KIND_GRAPH = "graph"
KIND_BLAST_RADIUS = "blast-radius"
KIND_SCENARIO_EXPOSURE = "scenario-exposure"

# Only an as-consumed execution produces a scoring-eligible forecast: the honest number is never
# contaminated by what we know now (spec story 40). The *tag* lands here; the *gating* — refusing
# a fact dated after T — is build ticket 36, and the artefact says so rather than implying it.
SCORING_REGIME = "as-consumed"
REGIME_GATING_TICKET = "build ticket 36"


class VerbError(RuntimeError):
    pass


def command_for(verb: str, **parts: str | None) -> list[str]:
    """The command as recorded in an artefact.

    Deliberately not `sys.argv`: the repository path and the output path are where the work
    happened, not inputs to the derivation, and a machine path in the envelope would break
    `identical_pins_identical_bytes` across machines. A forecast being scored is named by its
    digest here for the same reason — by pin, never by path.
    """
    out = ["twin", verb]
    for key, value in sorted(parts.items()):
        if value is not None:
            out += [f"--{key.replace('_', '-')}", str(value)]
    return out


def _pins(repo: ModelRepo, overlay: Overlay, caps: Capabilities, substrate: str | None) -> dict[str, Any]:
    """Model repo ref, world ref, overlay ref, and the tool's own version.

    The tool is a pin too: identical bytes is only a meaningful claim pin-for-pin, and a change
    to the depth-grade checklists changes what an artefact says about itself.
    """
    return {
        "model_repo": repo.pin.as_dict(),
        "overlay": overlay.ref.as_dict(),
        "world": overlay.world.ref.as_dict(),
        "org": overlay.org,
        "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
        # Bulk substrate is addressed by content hash rather than held inline. Null until the
        # substrate track lands; the reference form round-trips through here regardless.
        "substrate": substrate,
    }


def _substrate_ref(doc: dict[str, Any], where: str) -> str | None:
    raw = doc.get("substrate")
    if raw is None:
        return None
    try:
        return str(BlobRef.parse(str(raw)))  # parse then re-serialise: the round-trip
    except ValueError as exc:
        raise VerbError(f"{where}: {exc}") from exc


# -- sense ---------------------------------------------------------------------------------


def sense(repo: ModelRepo, caps: Capabilities, org: str, signal_id: str, command: list[str]) -> Artefact:
    overlay = Overlay.load(repo, org)
    signal = overlay.signals.get(signal_id)
    if signal is None:
        known = ", ".join(sorted(overlay.signals)) or "none"
        raise VerbError(f"no signal {signal_id!r} in overlay {org!r} (have: {known})")

    bindings = []
    for claim_id, claim in sorted(overlay.claims.items()):
        if claim.get("kind") != "binding" or claim.get("signal") != signal_id:
            continue
        grade = int(claim.get("evidence_grade", 0))
        if grade != 5:
            # Skills sit upstream of this seam: their output is a committed grade-5 claim file,
            # and from the CLI's point of view it is just input.
            raise VerbError(
                f"claim {claim_id!r} binds a signal at evidence grade {grade}; hand-authored "
                "binding claims are grade 5 by construction"
            )
        component_id = str(claim.get("component", ""))
        component = overlay.component(component_id)
        bindings.append(
            {
                "claim": claim_id,
                "component": component_id,
                "component_layer": "overlay" if component_id in overlay.components else "world",
                "evidence_grade": grade,
                "claimed_by": claim.get("claimed_by"),
                "evidence": claim.get("evidence"),
                "confidence": claim.get("confidence"),
            }
        )
    if not bindings:
        raise VerbError(f"signal {signal_id!r} has no binding claim; an unbound signal does not sense")

    return Artefact(
        kind=KIND_BOUND_SIGNAL,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(signal, f"signal {signal_id}")),
        depth=caps.depth_block(CAPS_SENSE),
        body={"signal": signal, "bindings": bindings},
    )


# -- graph ---------------------------------------------------------------------------------


def graph(repo: ModelRepo, caps: Capabilities, org: str, command: list[str]) -> Artefact:
    """Emit the typed knowledge graph as an artefact.

    Generated, never committed: downstream tracks test against a live contract rather than a
    fossil (build ticket 12). Behavioural observations are absent by construction — they are a
    separately gated unit and the graph has no route to them.
    """
    overlay = Overlay.load(repo, org)
    built = overlay.graph()
    body = built.as_dict()
    body["bus_factor"] = {
        component: holders
        for component in sorted(built.components)
        if (holders := built.bus_factor(component))
    }
    # Both derived on read from the components and edges above, in the same pass that emitted
    # them: the map has no authoring step (build ticket 14) and the roll-ups have no authored
    # form (build ticket 13).
    body["wardley"] = built.wardley()
    body["rollups"] = built.rollups()
    return Artefact(
        kind=KIND_GRAPH,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_GRAPH),
        body=body,
    )


# -- blast ---------------------------------------------------------------------------------


def blast(repo: ModelRepo, caps: Capabilities, org: str, origin: str, command: list[str]) -> Artefact:
    """The unpriced structural blast radius, and what may be priced beside it (build ticket 19).

    One traversal, two outputs. A path prices only when every hop claims a mechanism *and* every
    mechanism is evidenced at or inside the published threshold; everything else is reported as
    connected-but-unpriceable, which is an answer rather than a gap. A scenario whose only causal
    path runs through a grade-5 model assertion therefore emits a blast radius and never a price.
    """
    overlay = Overlay.load(repo, org)
    body = blast_mod.radius(overlay.graph(), origin)
    blast_mod.refuse_undeclared_keys(body)
    return Artefact(
        kind=KIND_BLAST_RADIUS,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_BLAST),
        body=body,
    )


# -- exposure ------------------------------------------------------------------------------


def exposure(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    scenario_id: str,
    perspective_ids: list[str] | None,
    command: list[str],
) -> Artefact:
    """The same scenario, under each declared perspective (build ticket 26).

    The £ belongs to whoever pays to run the twin, so a scenario has no single figure — it has one
    per eye, and the difference between them is attributable component by component. Nothing here
    picks a perspective: with none named, **every** perspective in the overlay is reported, because
    defaulting to the operator's would be exactly the unstated firm's-£ the design refuses.

    **The use-gate reaches here too** (build ticket 19, decision ticket 09 Q4 — one rule, three
    jobs). A valuation carries its own evidence grade, and only a valuation inside the published
    threshold enters the figure. Anything weaker is a **register entry**: named beside the number,
    carrying no amount at all, because the schema refuses one. That is what stops a perspective
    declaring "reputation damage = £X", which is the shadow price decision ticket 09 rejected.

    What this is **not**: a modelled price. Nothing propagates yet (build ticket 20), no severity
    is sampled (23-25) and the constraint pre-filter that must run before any pricing is build
    ticket 28. The admitted figures are the perspective's own declared valuations and the artefact
    says so in `basis` rather than implying otherwise.
    """
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")

    chosen = sorted(perspective_ids) if perspective_ids else sorted(overlay.perspectives)
    if not chosen:
        raise VerbError(
            f"overlay {org!r} declares no perspective. The £ belongs to whoever pays to run the "
            "twin, so a scenario cannot be valued until somebody says who they are."
        )
    # A repeated component is one component: it would otherwise be valued twice and appear twice
    # in the attribution, which reads as two different things worth the same.
    components = list(dict.fromkeys(str(c) for c in scenario.get("components", []) or []))

    entries: list[dict[str, Any]] = []
    for perspective_id in chosen:
        perspective = overlay.perspectives.get(perspective_id)
        if perspective is None:
            known = ", ".join(sorted(overlay.perspectives)) or "none"
            raise VerbError(f"no perspective {perspective_id!r} in overlay {org!r} (have: {known})")
        declared = {str(k): v for k, v in (perspective.get("values") or {}).items()}
        admitted: list[dict[str, Any]] = []
        register: list[dict[str, Any]] = []
        for component in components:
            valuation = declared.get(component)
            if valuation is None:
                continue
            grade = int(valuation["evidence_grade"])
            if evidence.may_price(grade):
                admitted.append(
                    {"component": component, "declared_value": float(valuation["amount"]),
                     "evidence_grade": grade, "basis": valuation["basis"]}
                )
            else:
                # No figure, anywhere. The schema refuses one at this grade, so the register is a
                # list of names and reasons rather than a price with a null field.
                register.append(
                    {"component": component, "evidence_grade": grade, "basis": valuation["basis"],
                     "reason": (
                         f"evidence grade {grade} is outside the published threshold, so this is "
                         "reported beside the figure and never inside it"
                     )}
                )
        entries.append(
            {
                "id": perspective_id,
                "name": perspective.get("name"),
                "party": perspective.get("party"),
                "pays": perspective.get("pays"),
                "constraint_set": constraints.resolve(perspective),
                "admitted": admitted,
                "register": register,
                "declared_exposure": sum(e["declared_value"] for e in admitted),
                # A component this perspective never valued at all — distinct from one it valued
                # too weakly to price, which is in the register above.
                "unvalued": [c for c in components if c not in declared],
            }
        )

    return Artefact(
        kind=KIND_SCENARIO_EXPOSURE,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(scenario, f"scenario {scenario_id}")),
        depth=caps.depth_block(CAPS_EXPOSURE),
        body={
            "scenario": {
                "id": scenario_id,
                "at": scenario.get("at"),
                "question": scenario.get("question"),
                "components": components,
            },
            "basis": {
                "kind": "declared-valuation",
                "propagated": False,
                "severity_sampled": False,
                "note": (
                    "each figure is a valuation the perspective declared for a component, not a "
                    "modelled price: nothing propagates yet (build ticket 20), no severity "
                    "distribution is sampled (23-25) and no causal path has been priced (30)"
                ),
            },
            "gating": evidence.published(),
            "prefilter": {
                "applied": False,
                "lands_at": "build ticket 28",
                "note": (
                    "the constraint pre-filter that removes ruin-class and forbidden options "
                    "before any pricing has not been built, so no figure here has been compared "
                    "against a red line — and the constraint set each perspective resolves is "
                    "published beside it so a reader can see what it will filter on"
                ),
            },
            "perspectives": entries,
            "declared_exposure": {e["id"]: e["declared_exposure"] for e in entries},
            "exposure_spread": _spread([e["declared_exposure"] for e in entries]),
            "attribution": [
                {
                    "component": component,
                    # `null` for a perspective that admitted no figure — because it never valued
                    # this component, or because it valued it too weakly to price. Zero would say
                    # "worth nothing to them", which is a different claim and usually a false one.
                    "declared_value": {e["id"]: _admitted(e, component) for e in entries},
                    "spread": _spread([_admitted(e, component) for e in entries]),
                }
                for component in components
            ],
        },
    )


def _admitted(entry: dict[str, Any], component: str) -> float | None:
    return next((e["declared_value"] for e in entry["admitted"] if e["component"] == component), None)


def _spread(values: list[Any]) -> float | None:
    """The width between the widest and narrowest figure, or nothing if there is only one eye.

    A spread, never a chosen number: two perspectives disagreeing about what a component is worth
    is the decision-relevant fact, and any single figure here would destroy it.
    """
    numbers = [float(v) for v in values if v is not None]
    return max(numbers) - min(numbers) if len(numbers) > 1 else None


# -- run -----------------------------------------------------------------------------------


def run(
    repo: ModelRepo, caps: Capabilities, org: str, scenario_id: str, command: list[str], at: str | None = None
) -> Artefact:
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")

    when = at or scenario.get("at")
    if not when:
        raise VerbError(f"scenario {scenario_id!r} declares no `at`; an execution happens at a declared time")

    proposition_id = str(scenario.get("proposition", ""))
    proposition = overlay.proposition(proposition_id)

    components = [str(c) for c in scenario.get("components", []) or []]
    if not components:
        raise VerbError(f"scenario {scenario_id!r} references no components")
    for component_id in components:
        overlay.component(component_id)

    model_ids = [str(m) for m in scenario.get("world_models", []) or []]
    if not model_ids:
        raise VerbError(f"scenario {scenario_id!r} names no world models; a forecast is always relative to one")

    regime = str(scenario.get("regime", SCORING_REGIME))
    if regime not in REGIMES:
        raise VerbError(f"scenario {scenario_id!r}: unknown information regime {regime!r}")

    pins = _pins(repo, overlay, caps, _substrate_ref(scenario, f"scenario {scenario_id}"))
    # A forecast travels on its own, so it carries the whole pin — including the command that
    # produced it, not just the refs it read (build ticket 06).
    forecast_pins = {**pins, "command": list(command)}

    # Forecasts, plural, always. There is no code path anywhere that collapses this list, and
    # there never will be: the ability to collapse would be used.
    forecasts: list[dict[str, Any]] = []
    for model_id in model_ids:
        world_model = overlay.world_model(model_id)
        beliefs = world_model.get("beliefs", {}) or {}
        if proposition_id not in beliefs:
            raise VerbError(
                f"world model {model_id!r} holds no belief about {proposition_id!r}; it cannot "
                "forecast a proposition it has not considered"
            )
        forecast = {
            "scenario": scenario_id,
            "world_model": model_id,
            "world_model_credence": world_model.get("credence"),
            "world_model_layer": "overlay" if model_id in overlay.world_models else "world",
            "proposition": proposition_id,
            "proposition_text": proposition.get("text"),
            "probability": float(beliefs[proposition_id]),
            "at": when,
            "horizon": scenario.get("horizon"),
            "components": components,
            "regime": regime,
            "pins": forecast_pins,
        }
        forecast["id"] = digest_of(forecast)[:16]
        forecasts.append(forecast)

    return Artefact(
        kind=KIND_FORECAST_BUNDLE,
        mark=DERIVED,
        command=command,
        pins=pins,
        depth=caps.depth_block(CAPS_RUN),
        body={
            "scenario": {
                "id": scenario_id,
                "at": when,
                "components": components,
                "world_models": model_ids,
                "proposition": proposition_id,
                "horizon": scenario.get("horizon"),
                "question": scenario.get("question"),
            },
            "regime": {
                "declared": regime,
                "scoring_eligible": regime == SCORING_REGIME,
                "gated": False,
                "gating_lands_at": REGIME_GATING_TICKET,
            },
            "forecasts": forecasts,
        },
    )


# -- score ---------------------------------------------------------------------------------


def score(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    forecast_path: str | Path,
    outcome_id: str,
    command: list[str],
) -> Artefact:
    overlay = Overlay.load(repo, org)
    outcome = overlay.outcomes.get(outcome_id)
    if outcome is None:
        known = ", ".join(sorted(overlay.outcomes)) or "none"
        raise VerbError(f"no outcome {outcome_id!r} in overlay {org!r} (have: {known})")

    bundle_bytes = Path(forecast_path).read_bytes()
    bundle = load_artefact(forecast_path)
    if bundle["envelope"]["kind"] != KIND_FORECAST_BUNDLE:
        raise VerbError(f"{forecast_path} is a {bundle['envelope']['kind']!r}, not a forecast bundle")
    bundle_org = bundle["envelope"]["pins"].get("org")
    if bundle_org != org:
        # Propositions live in the shared world layer, so a proposition match is not a tenancy
        # check. Without this, one tenant's probabilities land verbatim in another's artefact.
        raise VerbError(
            f"that forecast bundle belongs to {bundle_org!r}, not {org!r}; a score card never "
            "crosses a tenant boundary"
        )

    observed = outcome.get("observed")
    if not isinstance(observed, bool):
        raise VerbError(f"outcome {outcome_id!r} must record `observed: true|false`")
    proposition_id = str(outcome.get("proposition", ""))
    overlay.proposition(proposition_id)

    # The execution's own declaration is read back, not just the per-forecast tag: a bundle that
    # says `scoring_eligible: false` at the top must not score whatever its forecasts claim.
    declared = bundle["body"].get("regime") or {}
    declared_regime = declared.get("declared")
    if declared_regime is not None and not declared.get("scoring_eligible", declared_regime == SCORING_REGIME):
        declared_regime = str(declared_regime)

    scores: list[dict[str, Any]] = []
    unscoreable: list[dict[str, Any]] = []
    for forecast in bundle["body"]["forecasts"]:
        entry = {"forecast_id": forecast["id"], "world_model": forecast["world_model"]}
        # No default. Defaulting an untagged forecast to the one regime that scores would let the
        # invariant be bypassed by *deleting* the tag rather than changing it, and would have the
        # card invent a claim the bundle never made.
        regime = forecast.get("regime")
        if regime is None:
            unscoreable.append(
                {**entry, "reason": "regime-untagged",
                 "detail": "the forecast declares no information regime, so it is not scoring-eligible"}
            )
            continue
        if declared_regime is not None and regime != declared_regime:
            unscoreable.append(
                {**entry, "reason": "regime-disagrees-with-execution",
                 "detail": f"forecast says {regime!r}, the execution declared {declared_regime!r}"}
            )
            continue
        if forecast.get("proposition") != proposition_id:
            # Explicit, and never a zero: a forecast nobody can resolve is not a bad forecast.
            unscoreable.append(
                {**entry, "reason": "no-resolvable-outcome",
                 "detail": f"forecasts {forecast.get('proposition')!r}, outcome resolves {proposition_id!r}"}
            )
            continue
        if regime != SCORING_REGIME:
            unscoreable.append(
                {**entry, "reason": "regime-not-as-consumed",
                 "detail": f"executed {regime!r}; only {SCORING_REGIME!r} produces a scoring-eligible forecast"}
            )
            continue
        probability = float(forecast["probability"])
        if not 0.0 < probability < 1.0:
            unscoreable.append(
                {**entry, "reason": "not-a-probability",
                 "detail": f"{probability} is not strictly between 0 and 1"}
            )
            continue
        scores.append(
            {
                **entry,
                "probability": probability,
                "observed": observed,
                "regime": str(regime),
                **scoring.score(probability, observed),
                "pins": forecast["pins"],
            }
        )

    return Artefact(
        kind=KIND_SCORE_CARD,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_SCORE),
        body={
            "subject": {
                "kind": KIND_FORECAST_BUNDLE,
                "sha256": sha256_hex(bundle_bytes),
                "produced_by": bundle["envelope"]["produced_by"],
                "pins": bundle["envelope"]["pins"],
            },
            "answer_key": {
                "id": outcome_id,
                "proposition": proposition_id,
                "observed": observed,
                "resolved_on": outcome.get("resolved_on"),
                "source": outcome.get("source"),
                "contamination": outcome.get("contamination"),
                "source_dated": outcome.get("source_dated"),
            },
            "rules": list(scoring.RULES),
            "orientation": "lower-is-better" if scoring.LOWER_IS_BETTER else "higher-is-better",
            "significant_digits": scoring.SIGNIFICANT_DIGITS,
            "scores": scores,
            "unscoreable": unscoreable,
        },
    )


def resolve_org(repo: ModelRepo, org: str | None) -> str:
    from .model import orgs as list_orgs

    available = list_orgs(repo)
    if org:
        if org not in available:
            raise ModelError(f"no overlay for org {org!r} (have: {', '.join(available) or 'none'})")
        return org
    if len(available) == 1:
        return available[0]
    raise ModelError(f"--org is required; this repository has overlays for: {', '.join(available) or 'none'}")
