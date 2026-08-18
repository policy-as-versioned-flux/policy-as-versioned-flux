"""The three verbs of the walking skeleton: sense, run, score.

One dated signal binds to a component; one scenario executes and emits forecasts; a forecast is
scored against a recorded outcome. The loop closes before anything is deepened, because scoring
dictates what every other component must record (spec: "Scoring, first").

Every capability here sits at `partial`, which means **at least one** of its owning decision
ticket's acceptance criteria, not most of them. What is unchecked is visible in each artefact's
`depth` block rather than described in prose somewhere nobody reads.
"""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .artefact import Artefact, DERIVED, load as load_artefact
from .blob import BlobRef
from .canon import digest_of, sha256_hex
from .grades import Capabilities
from .model import ModelError, Overlay
from .repo import ModelRepo
from .schema import REGIMES, SIGNAL_BINDING_KINDS
from . import (
    admission as admission_mod,
    affected_parties as affected_parties_mod,
    blast as blast_mod,
    constraints,
    credibility as credibility_mod,
    evidence,
    options as options_mod,
    positions as positions_mod,
    pricing,
    primitives as primitives_mod,
    propagate as propagate_mod,
    regimes as regimes_mod,
    scoring,
)
from .pert import PertError, Triple
from .severity import Severity, SeverityError

CAPS_SENSE = ["domain-model", "provenance", "sense-move"]
# Added to `sense`'s set when a signal binds to a response rather than a component (build ticket
# 68). One capability rather than a set of its own: an enactment observation is the sensing
# capability's machinery pointed at a different subject, and only the corroborated grade is
# enactment's own work.
CAPS_ENACTMENT = ["enactment"]
CAPS_RUN = ["domain-model", "provenance", "scenario-engine"]
CAPS_SCORE = ["domain-model", "provenance", "sense-move"]
# The graph now carries causal edges and a Wardley map, so the causal layer is one of the
# capabilities that produced it and its depth travels with the artefact (build ticket 17).
CAPS_GRAPH = ["domain-model", "provenance", "causal-layer"]
CAPS_BLAST = ["causal-layer", "domain-model", "provenance"]
# Exposure reads the causal layer now: which impacts enter the £ is derived from a graded path to
# a declared cash flow, so the causal layer's depth travels with the figure (build ticket 29).
CAPS_EXPOSURE = ["causal-layer", "currency-regimes", "domain-model", "provenance"]
CAPS_PROPAGATE = ["causal-layer", "domain-model", "provenance"]
CAPS_OPTIONS = ["currency-regimes", "domain-model", "provenance"]
# The price is the causal layer multiplied by the currency, so both depths travel with it
# (build ticket 30). Neither capability alone produced this figure.
CAPS_PRICE = ["causal-layer", "currency-regimes", "domain-model", "provenance"]
# `do()` and `observe()` are the causal layer's intervention semantics (build ticket 22).
CAPS_QUERY = ["causal-layer", "domain-model", "provenance"]
# Rewind is the scenario engine's time primitive (build ticket 35), and it is a fact about the
# model repository, so provenance travels with it too.
CAPS_REWIND = ["domain-model", "provenance", "scenario-engine"]
# The information regimes are rewind's other half — decision ticket 13 Q2 defines a rewind as
# restoring the model under an information gate, and sense-move owns what counts as ingested.
CAPS_REGIMES = ["domain-model", "provenance", "scenario-engine", "sense-move"]
# The believed/rival/revealed deltas read a scenario's ensemble (scenario-engine) and score
# positions against an outcome (sense-move) — the same pair `run` and `score` each own, joined
# here rather than duplicated (build ticket 16).
CAPS_POSITIONS = ["domain-model", "provenance", "scenario-engine", "sense-move"]
# The credibility blend reads a world-layer prior against an org's overlay own-data (the
# world/overlay split, decision ticket 07 Q1b) to produce an evidence-adjacent £ figure
# (decision ticket 09) — build ticket 31.
CAPS_CREDIBILITY = ["currency-regimes", "domain-model", "provenance"]
# Rival causal accounts read the causal layer (each account is a claim about measured effect, the
# same vocabulary an `influences` edge asserts) over the domain model's graph — build ticket 32.
CAPS_CAUSAL_ACCOUNTS = ["causal-layer", "domain-model", "provenance"]
# The trade-off curve joins the causal layer's ensemble spread (32) to the £ (30, currency-regimes)
# — the same two capabilities `price` itself carries, because a curve across the ensemble is
# `pricing.price` run once per named account and nothing else — build ticket 33.
CAPS_TRADEOFF = ["causal-layer", "currency-regimes", "domain-model", "provenance"]

KIND_BOUND_SIGNAL = "bound-signal"
KIND_FORECAST_BUNDLE = "forecast-bundle"
KIND_SCORE_CARD = "score-card"
KIND_GRAPH = "graph"
KIND_BLAST_RADIUS = "blast-radius"
KIND_SCENARIO_EXPOSURE = "scenario-exposure"
KIND_PROPAGATION = "propagation"
KIND_PRICED_OPTIONS = "priced-option-set"
KIND_INTERVENTION = "intervention"
KIND_OBSERVATION = "observation"
KIND_REWOUND_MODEL = "rewound-model"
KIND_REGIME_GAP = "regime-gap"
KIND_PRICED_IMPACT = "priced-impact"
KIND_RELIABILITY_DIAGRAM = "reliability-diagram"
KIND_POSITION_DELTAS = "position-deltas"
KIND_CREDIBILITY_BLEND = "credibility-blend"
KIND_LOSS_EXCEEDANCE = "loss-exceedance-curve"
KIND_ANCHORED_LOSS_EXCEEDANCE = "anchored-loss-exceedance-curve"
KIND_CAUSAL_ACCOUNT_SPREAD = "causal-account-spread"
KIND_TRADE_OFF_CURVE = "trade-off-curve"
KIND_AFFECTED_PARTIES = "affected-parties-register"

# Calibration's own capability, decision ticket 11 — the same set `score` already carries, because
# a reliability diagram reads scores `score` produced and adds no domain of its own.
CAPS_RELIABILITY = CAPS_SCORE
# The FAIR engine's tail model is decision ticket 09's territory — the same £-currency decision
# that commits to TVaR over VaR (build ticket 24) — and it is standalone, so it carries no other
# capability's depth the way `price` carries the causal layer's.
CAPS_SEVERITY = ["currency-regimes"]

# Only an as-consumed execution produces a scoring-eligible forecast: the honest number is never
# contaminated by what we know now (spec story 40). Build ticket 36 turned the tag into a gate —
# the model is *loaded through* the regime, so a post-T fact is absent rather than screened.
SCORING_REGIME = regimes_mod.AS_CONSUMED

# Why a non-event carrying a graded mitigation claim scores unscoreable rather than as a miss
# (decision ticket 08 Q4, build ticket 81). Named beside the other `unscoreable` reasons above it.
MITIGATED_NON_EVENT = "mitigated-non-event"


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
    """One dated signal, and everything it binds to.

    **Build ticket 68 widened the subject, not the pipeline.** A signal binds to a component
    (`binding`) or to a response (`enactment`), and both walk this one loop. A declaration that a
    lever was pulled and a reconciler's report that it is running are ordinary signals with
    ordinary claims; there is no enactment ingest anywhere, and this function is the reason there
    does not need to be.

    **Build ticket 80 wired the primitives in.** A bound signal is an *observation* (decision
    ticket 11 Q4) — the same distinction `twin/primitives.py` already drew for `do()` — so a
    component binding's belief update propagates and the reach is published beside it, rather than
    stopping at the binding as if nothing followed from it.
    """
    from . import corroboration

    overlay = Overlay.load(repo, org)
    signal = overlay.signals.get(signal_id)
    if signal is None:
        known = ", ".join(sorted(overlay.signals)) or "none"
        raise VerbError(f"no signal {signal_id!r} in overlay {org!r} (have: {known})")

    # Built once and reused per binding below: the graph a component-binding's belief update
    # propagates through. Not needed for response bindings (corroboration), which never reach it.
    graph = overlay.graph()

    bindings = []
    responses: set[str] = set()
    for claim_id, claim in sorted(overlay.claims.items()):
        kind = str(claim.get("kind", ""))
        if kind not in SIGNAL_BINDING_KINDS or claim.get("signal") != signal_id:
            continue
        grade = int(claim.get("evidence_grade", 0))
        held = {
            "claim": claim_id,
            "kind": kind,
            "evidence_grade": grade,
            "claimed_by": claim.get("claimed_by"),
            "evidence": claim.get("evidence"),
        }
        if kind == corroboration.KIND:
            # The grade here is what one channel is worth alone, and the schema already refused a
            # claim that disagreed with the table. What the response is actually graded at is
            # computed below, across every channel that has observed it.
            response_id = str(claim["response"])
            responses.add(response_id)
            bindings.append({**held, "response": response_id, "channel": str(claim["channel"])})
            continue
        if grade != 5:
            # Skills sit upstream of this seam: their output is a committed grade-5 claim file,
            # and from the CLI's point of view it is just input.
            raise VerbError(
                f"claim {claim_id!r} binds a signal at evidence grade {grade}; hand-authored "
                "binding claims are grade 5 by construction"
            )
        component_id = str(claim.get("component", ""))
        overlay.component(component_id)  # resolved for the refusal, not for the value
        # Decision ticket 11 Q4: a bound signal is an observation, not a do() — belief updates
        # bidirectionally. Downstream is the same causal composition an intervention would also
        # produce (`twin/propagate.py`, shared with `_query()` below); upstream is what
        # distinguishes an observation from an intervention at all, so it runs through
        # `updated_beliefs()` and nowhere else — `severed()` is the intervention's function and
        # this is never called with a `Do`.
        downstream = propagate_mod.propagate(graph, component_id)
        upstream, traversal = primitives_mod.updated_beliefs(
            graph, primitives_mod.Observe(component_id)
        )
        bindings.append(
            {
                **held,
                "component": component_id,
                "component_layer": "overlay" if component_id in overlay.components else "world",
                "confidence": claim.get("confidence"),
                "propagation": {
                    "downstream": downstream,
                    "upstream": upstream,
                    "upstream_traversal": traversal,
                },
            }
        )
    if not bindings:
        raise VerbError(f"signal {signal_id!r} has no binding claim; an unbound signal does not sense")

    # The action state of every response this signal bears on, computed across *all* channels
    # rather than only this signal's — the answer to "was the recommendation acted upon?" is a
    # property of the response, and one channel's observation is never the whole of it.
    action_state = [corroboration.state(overlay, response_id) for response_id in sorted(responses)]

    return Artefact(
        kind=KIND_BOUND_SIGNAL,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(signal, f"signal {signal_id}")),
        # The enactment capability's depth travels with the artefact only when it produced part of
        # it. A signal that binds to components alone is the sensing capability's own output and
        # says so, rather than carrying a grade for work it did not do.
        depth=caps.depth_block(CAPS_SENSE + (CAPS_ENACTMENT if action_state else [])),
        body={
            "signal": signal,
            "bindings": bindings,
            "action_state": action_state,
            "channels": corroboration.published() if action_state else None,
        },
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


def affected_parties(repo: ModelRepo, caps: Capabilities, org: str, command: list[str]) -> Artefact:
    """Emit the affected-parties register: every outsider a scenario in this overlay named as
    bearing a modelled consequence (build ticket 61, decision ticket 15).

    A computed roll-up of what scenario authoring already declared — `twin/affected_parties.py`
    does the reading, this just wraps it as an artefact. No capability file tracks decision
    ticket 15 (build ticket 62's `twin/misuse.py` and build ticket 60's `twin/challenges.py` carry
    the identical note), so the depth block names no capability rather than fabricating one to
    fill the slot.
    """
    overlay = Overlay.load(repo, org)
    return Artefact(
        kind=KIND_AFFECTED_PARTIES,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth={
            "grade": None,
            "capabilities": {},
            "note": (
                "a computed roll-up of scenario-authored declarations; no capability file tracks "
                "decision ticket 15 (see build tickets 60 and 62's identical note)"
            ),
        },
        body=affected_parties_mod.published(overlay),
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


# -- propagate -----------------------------------------------------------------------------


def propagate(repo: ModelRepo, caps: Capabilities, org: str, origin: str, command: list[str]) -> Artefact:
    """Compose a shock through the causal layer by Monte-Carlo (build ticket 20).

    Three numbers per path, on purpose: the composed triple (exact, hand-checkable, unattenuated),
    the attenuated one, and the sampled spread. An attenuated figure whose un-attenuated form was
    never shown makes the attenuation unfalsifiable, and a product of modes is not the mode of a
    product — so all three are emitted and none of them stands in for the others.

    Structural edges do not appear here at all. A `needs` edge claims no mechanism, so nothing
    composes along it; that exposure is the unpriced blast radius and it stays unpriced.
    """
    overlay = Overlay.load(repo, org)
    # The closed body and the directional-magnitude refusal are enforced inside
    # `propagate_mod.propagate`, not here: build ticket 22 gave that body a second producer, and
    # a guard applied by one caller is a guard the other caller does not have.
    body = propagate_mod.propagate(overlay.graph(), origin)
    return Artefact(
        kind=KIND_PROPAGATION,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_PROPAGATE),
        body=body,
    )


# -- intervene and observe (build ticket 22) ------------------------------------------------


def _query(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    query: primitives_mod.Do | primitives_mod.Observe,
    command: list[str],
) -> Artefact:
    """One shock, two readings of it. The downstream half is identical; the upstream half is not.

    Emitting them through one function is deliberate: it is what makes "the downstream halves are
    the same" a property of the code rather than a claim about two implementations that could
    drift. The difference between doing and learning lives entirely above the causal composition,
    which is exactly what Pearl's `do()` says it should.
    """
    overlay = Overlay.load(repo, org)
    graph = overlay.graph()
    if query.component not in graph.components:
        raise VerbError(f"no component {query.component!r} in the graph of {org!r}")

    downstream = propagate_mod.propagate(graph, query.component)
    # Narrowed here rather than behind a boolean, because a boolean is what the type checker
    # cannot follow: with `is_intervention` in the way, `mypy` reported the union reaching both
    # `severed()` and `updated_beliefs()`. That refusal is the ticket's third criterion working.
    if isinstance(query, primitives_mod.Do):
        is_intervention, severed = True, primitives_mod.severed(graph, query)
        upstream: list[dict[str, Any]] = []
        traversal = primitives_mod.upstream_traversal(
            primitives_mod.UPSTREAM_MAX_DEPTH, truncated=False, ran=False
        )
    else:
        is_intervention, severed = False, []
        upstream, traversal = primitives_mod.updated_beliefs(graph, query)
    body: dict[str, Any] = {
        "operation": query.verb,
        "component": query.component,
        "semantics": {
            "propagates": "downstream only" if is_intervention else "downstream and upstream",
            "maps_to": "Pearl's do(x) — action" if is_intervention else "conditioning on an observation",
            "why": (
                "doing a thing does not rewrite its own causes, so an intervention severs the "
                "incoming edges and never updates belief about them"
                if is_intervention
                else "learning a fact is evidence about what produced it, so belief updates "
                "everywhere the graph connects — causes included"
            ),
            "upstream_carries_no_magnitude": (
                "an authored elasticity is d(target)/d(cause); inverting it into a diagnostic "
                "magnitude needs a prior over the causes that nothing in this model authors, so "
                "an updated ancestor is named, graded and located and carries no number"
            ),
        },
        "downstream": downstream,
        "severed": severed,
        "upstream": upstream,
        # Where the upstream walk stopped, published for the reason the propagation publishes
        # its own truncation: a walk that stopped early and said nothing is claiming a
        # completeness it has not got.
        "upstream_traversal": traversal,
    }
    primitives_mod.refuse_upstream_under_intervention(body)
    return Artefact(
        kind=KIND_INTERVENTION if is_intervention else KIND_OBSERVATION,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_QUERY),
        body=body,
    )


def intervene(
    repo: ModelRepo, caps: Capabilities, org: str, component: str, command: list[str]
) -> Artefact:
    """`do(component)`. Incoming causal edges cut, propagation downstream only."""
    return _query(repo, caps, org, primitives_mod.Do(component), command)


def observe(
    repo: ModelRepo, caps: Capabilities, org: str, component: str, command: list[str]
) -> Artefact:
    """`observe(component)`. Nothing cut, and belief updates about the causes too."""
    return _query(repo, caps, org, primitives_mod.Observe(component), command)


# -- rewind (build ticket 35) ---------------------------------------------------------------


def rewind(repo: ModelRepo, caps: Capabilities, org: str, at: str, command: list[str]) -> Artefact:
    """The model state at a declared time, emitted so it can be read rather than described.

    The repository handed in is **already** rewound — `twin/primitives.py` resolves the time to a
    commit and opens it — so this verb is an ordinary read of an ordinary repository. That is the
    demonstration: nothing here knows it is looking at the past.

    It does check the time it was told, though, and that is not ceremony. Every other refusal for
    this verb lives in `ModelRepo.open_at_time`, which only the CLI calls; hand this function a
    repository at HEAD and a date in 1999 and it would otherwise emit an artefact claiming to be
    the model as it stood then. Cheap to check, because the pin already records when it was
    committed.
    """
    from .repo import RepoError

    try:
        moment = ModelRepo.parse_moment(at)
    except RepoError as exc:
        raise VerbError(str(exc)) from None
    committed = datetime.datetime.fromisoformat(repo.pin.committed)
    if committed > moment:
        raise VerbError(
            f"this repository is pinned at a commit dated {repo.pin.committed}, which is after "
            f"{at}. A rewind emits the model as it stood at the declared time, so a pin from "
            "after that time is a different model wearing the wrong date."
        )
    overlay = Overlay.load(repo, org)
    graph = overlay.graph()
    return Artefact(
        kind=KIND_REWOUND_MODEL,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_REWIND),
        body={
            "rewound_to": at,
            "resolved": {
                "commit": repo.pin.commit,
                "committed": repo.pin.committed,
                "tree": repo.pin.tree,
            },
            "abduction": (
                "Pearl's abduction step. A model state, not a filtered view: the graph below was "
                "loaded from the commit that was current at the declared time, so an elasticity "
                "recalibrated since reads here as it read then"
            ),
            "graph": graph.as_dict(),
            "rollups": graph.rollups(),
        },
    )


# -- options -------------------------------------------------------------------------------


def options(
    repo: ModelRepo, caps: Capabilities, org: str, perspective_id: str, command: list[str]
) -> Artefact:
    """The choice set after the constraint pre-filter, with the survivors costed (ticket 28).

    The pre-filter runs first and it never sees a cost, which is why no magnitude can bring an
    excluded option back. A removed option is absent from `priced` and its record carries no
    figure at all — a constraint is not a very large price, because a price can be outbid.
    """
    overlay = Overlay.load(repo, org)
    perspective = overlay.perspectives.get(perspective_id)
    if perspective is None:
        known = ", ".join(sorted(overlay.perspectives)) or "none"
        raise VerbError(f"no perspective {perspective_id!r} in overlay {org!r} (have: {known})")
    if not overlay.responses:
        raise VerbError(
            f"overlay {org!r} declares no candidate response, so there is no choice set to filter "
            "or to cost"
        )
    admitted = options_mod.prefilter(perspective, overlay.responses)
    return Artefact(
        kind=KIND_PRICED_OPTIONS,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_OPTIONS),
        body=admitted.priced(),
    )


# -- price (build ticket 30) -----------------------------------------------------------------


def price(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    origin: str,
    perspective_ids: list[str] | None,
    command: list[str],
) -> Artefact:
    """One shock, priced under each declared perspective, with the responses beside it (ticket 30).

    This is where the causal layer meets the £. Until now `twin propagate` composed elasticities
    and emitted no money, and `twin exposure` reported declared valuations and propagated nothing.
    A price here is the perspective's own declared valuation scaled by the propagated influence,
    and there is no severity slot anywhere — one authored magnitude per component per eye, so
    there is no second number an author could move the price through.

    **Nothing here picks a perspective.** With none named, every perspective in the overlay is
    priced and the spread between them is in the artefact — the same refusal `twin exposure`
    makes, because defaulting to the employer's is exactly the unstated firm's-£ the design
    rejects. Two eyes disagreeing about what a shock costs is the decision-relevant fact.
    """
    overlay = Overlay.load(repo, org)
    graph = overlay.graph()
    if not overlay.responses:
        raise VerbError(
            f"overlay {org!r} declares no candidate response, so there is nothing to price against "
            "the impact"
        )
    chosen = sorted(perspective_ids) if perspective_ids else sorted(overlay.perspectives)
    if not chosen:
        raise VerbError(
            f"overlay {org!r} declares no perspective. A price belongs to whoever pays to run the "
            "twin, so a shock cannot be priced until somebody says who they are."
        )

    entries = []
    for perspective_id in chosen:
        perspective = overlay.perspectives.get(perspective_id)
        if perspective is None:
            known = ", ".join(sorted(overlay.perspectives)) or "none"
            raise VerbError(f"no perspective {perspective_id!r} in overlay {org!r} (have: {known})")
        entries.append(pricing.price(graph, perspective, origin, overlay.responses, overlay))

    components = sorted({i["component"] for e in entries for i in e["impacts"]})
    return Artefact(
        kind=KIND_PRICED_IMPACT,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_PRICE),
        body={
            "origin": origin,
            "perspectives": entries,
            # Per component, per eye, and the width between them. A single organisational price
            # is the collapse this system refuses: there is no such thing.
            "attribution": [
                {
                    "component": component,
                    "priced": {
                        e["perspective"]: _price_at(e, component) for e in entries
                    },
                    "spread": pricing.spread([_price_at(e, component) for e in entries]),
                }
                for component in components
            ],
            "not_a_ranking": (
                "prices, costs and credits in one unit, in the order they were authored. Nothing "
                "marks one option best and nothing recommends one"
            ),
        },
    )


def _price_at(entry: dict[str, Any], component: str) -> float | None:
    """The attenuated modal price of a component under one eye, or nothing if it was refused.

    `None` rather than zero, for the reason the exposure attribution uses it: zero says "this
    shock costs them nothing", which is a different claim and usually a false one.
    """
    found = next((i for i in entry["impacts"] if i["component"] == component), None)
    return None if found is None else float(found["price"]["attenuated"]["mode"])


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

    **And a second gate, derived rather than declared** (build ticket 29). A well-graded valuation
    still enters the figure only if a causal path runs from the component to a cash flow this
    perspective declared. A perspective names where its money is; nobody names what is priceable.
    An impact with no such path is a register entry whose reason is falsifiable — "no evidenced
    causal path yet", never "we decided it does not count".

    What this is **not**: a modelled price. Nothing propagates into these figures — they are the
    perspective's own declared valuations of the components a scenario names, and the artefact says
    so in `basis` rather than implying otherwise. `twin price` is the verb that multiplies one of
    these valuations by a propagated influence (build ticket 30), and it is a different question:
    this asks what a scenario's components are worth to each eye, and that asks what one shock
    costs them. Neither is a substitute for the other.
    """
    overlay = Overlay.load(repo, org)
    graph = overlay.graph()
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
        # Derived first, and for every component in the scenario rather than only the valued ones:
        # whether an impact could enter the £ at all is a fact about the graph, not about whether
        # somebody happened to put a number on it.
        verdicts = [admission_mod.admit(graph, perspective, c) for c in components]
        admissible = {v["component"] for v in verdicts if v["admitted"]}
        basis_of = {v["component"]: v.get("basis") for v in verdicts}
        admitted: list[dict[str, Any]] = []
        register: list[dict[str, Any]] = []
        for component in components:
            valuation = declared.get(component)
            if valuation is None:
                continue
            grade = int(valuation["evidence_grade"])
            held = {"component": component, "evidence_grade": grade, "basis": valuation["basis"]}
            if not evidence.may_price(grade):
                # No figure, anywhere. The schema refuses one at this grade, so the register is a
                # list of names and reasons rather than a price with a null field.
                register.append(
                    {**held, "reason": (
                        f"evidence grade {grade} is outside the published threshold, so this is "
                        "reported beside the figure and never inside it"
                    )}
                )
            elif component not in admissible:
                # Well enough evidenced to carry a figure, and with nowhere for that figure to
                # reach. The two gates ask different questions, and this is the one the £ boundary
                # answers: no path, no price, and the reason is something somebody can falsify.
                register.append(
                    {**held, "reason": (
                        "no causal path at an adequate grade reaches a cash flow this perspective "
                        "declared, so the impact stays outside the currency — not because it does "
                        "not count, but because no evidenced path has been shown yet"
                    )}
                )
            else:
                # `admitted_because` travels with the figure. A component the perspective named
                # as its own cash flow enters with no path and no grade behind the path — that is
                # the one route to the £ that rests on a declaration, and a reader must be able to
                # see which figures took it (build ticket 29, the named limit in twin/admission.py).
                admitted.append(
                    {**held, "declared_value": float(valuation["amount"]),
                     "admitted_because": basis_of[component]}
                )
        entries.append(
            {
                "id": perspective_id,
                "name": perspective.get("name"),
                "party": perspective.get("party"),
                "pays": perspective.get("pays"),
                "constraint_set": constraints.resolve(perspective),
                "cash_flow": admission_mod.cash_flows(perspective),
                # The derived boundary, shown rather than applied silently. A refused impact
                # carries the unpriced structural blast radius, because "connected and
                # unpriceable" is the answer, not a gap (build ticket 29).
                "admission": [admission_mod.compact(v) for v in verdicts],
                "admitted": admitted,
                "register": register,
                "declared_exposure": sum(e["declared_value"] for e in admitted),
                # Split, never one figure. A declared cash flow enters on the perspective's word;
                # a graded path enters on evidence. Summing them into one number would hide which
                # half of the exposure rests on which, and that is the decision-relevant part.
                "exposure_by_basis": {
                    basis: sum(
                        e["declared_value"] for e in admitted if e["admitted_because"] == basis
                    )
                    for basis in sorted({e["admitted_because"] for e in admitted})
                },
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
                    "modelled price. `twin price` multiplies one of these by a propagated "
                    "influence (build ticket 30) and answers a different question: this says what "
                    "a scenario's components are worth to each eye, and that says what one shock "
                    "costs them. No severity distribution is sampled anywhere (24-25)"
                ),
            },
            "gating": evidence.published(),
            "prefilter": {
                "applied": False,
                "note": (
                    "the constraint pre-filter removes ruin-class and forbidden options before any "
                    "pricing, and it runs in `twin options` (build ticket 28). There is no choice "
                    "set here to filter: these are declared valuations of components, not "
                    "candidate responses. The constraint set each perspective resolves is "
                    "published beside the figures so a reader can see what would be filtered."
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
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    scenario_id: str,
    regime: str | None,
    command: list[str],
    at: str | None = None,
) -> Artefact:
    """Execute a scenario under a declared information regime. Emits forecasts, plural.

    `regime` has **no default** (build ticket 36, AC 1). It is positional and it is checked before
    anything else happens, because the one regime a default would pick is the one whose forecasts
    score — so an omitted flag would be a silent claim to have run under the honest gate.

    The gate is applied by **loading the model through it**: under `as-consumed` the overlay is
    read at the last commit on or before T and every fact dated after T is withheld, so the
    execution below has no post-T fact available to reference. Referencing one is not a mistake
    this function could make.
    """
    regime = regimes_mod.require(regime)
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")

    when = at or scenario.get("at")
    if not when:
        raise VerbError(f"scenario {scenario_id!r} declares no `at`; an execution happens at a declared time")

    # From here the model is whatever this regime admits. The scenario is re-resolved against it
    # rather than carried over: under `as-consumed` the repository is reopened at T, and a
    # scenario authored later did not exist then — which is an answer, not an inconvenience.
    ungated, history = regimes_mod.read_at(repo, org, regime, str(when), loaded=overlay)
    scenario = ungated.scenarios.get(scenario_id)
    if scenario is None:
        raise VerbError(
            f"scenario {scenario_id!r} does not exist in overlay {org!r} as it stood at {when} "
            f"under the {regime!r} regime. It was authored later, so there was no such question "
            "to ask at that time."
        )
    overlay, gate = regimes_mod.apply(ungated, regime, str(when), history)
    regimes_mod.refuse_redacted_subject(
        gate, ungated, [str(c) for c in scenario.get("components", []) or []],
        f"scenario {scenario_id!r}",
    )

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
                # No longer a tag with a promise attached (build ticket 36). The gate ran, and
                # what it withheld is in the artefact rather than described in prose somewhere.
                "gated": True,
                "gate": gate,
            },
            "forecasts": forecasts,
        },
    )


# -- regimes: the three-way gap (build ticket 36) --------------------------------------------


def regime_gap(
    repo: ModelRepo, caps: Capabilities, org: str, scenario_id: str, command: list[str],
    at: str | None = None,
) -> Artefact:
    """The same scenario under all three regimes, with the two gaps computed (build ticket 36).

    The gaps are the localisation diagnostic and they are **computed here**, not left for a reader
    to infer from three artefacts side by side: `as-consumed` versus `as-knowable` localises to
    sensing, `as-knowable` versus `with-hindsight` localises to interpretation. Wrong under all
    three localises to the model, and that third comparison is reported as *not computed* with the
    reason, because nothing here infers a probability from a fact yet.
    """
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")
    when = str(at or scenario.get("at") or "")
    if not when:
        raise VerbError(f"scenario {scenario_id!r} declares no `at`; a regime gate needs a time")

    reports = {}
    for regime in REGIMES:
        ungated, history = regimes_mod.read_at(repo, org, regime, when, loaded=overlay)
        _, report = regimes_mod.apply(ungated, regime, when, history)
        reports[regime] = report

    return Artefact(
        kind=KIND_REGIME_GAP,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(scenario, f"scenario {scenario_id}")),
        depth=caps.depth_block(CAPS_REGIMES),
        body={
            "scenario": {"id": scenario_id, "at": when, "question": scenario.get("question")},
            "regimes": [reports[regime] for regime in REGIMES],
            "localisation": regimes_mod.gap(reports),
            "scoring": (
                f"only {SCORING_REGIME!r} produces a scoring-eligible forecast; the other two "
                "exist to localise a failure, never to be scored against"
            ),
        },
    )


# -- positions: believed, rival, revealed (build ticket 16) ---------------------------------


def positions(
    repo: ModelRepo, caps: Capabilities, org: str, scenario_id: str, command: list[str]
) -> Artefact:
    """Every position a scenario's ensemble holds, the deltas between them, and each one scored
    against revealed truth where it has resolved.

    Reads the scenario's own `world_models` list — the identical ensemble `twin run` forecasts
    over — rather than inventing a second notion of which positions are "in play". Nothing here
    picks out the org's believed map or the twin's default reference as special: every id is
    resolved, delta'd and scored through the same call (`twin/positions.py`).
    """
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")
    proposition_id = str(scenario.get("proposition", ""))
    model_ids = [str(m) for m in scenario.get("world_models", []) or []]
    if not model_ids:
        raise VerbError(f"scenario {scenario_id!r} names no world models; there is nothing to delta")

    body = positions_mod.deltas(overlay, proposition_id, model_ids)
    return Artefact(
        kind=KIND_POSITION_DELTAS,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(scenario, f"scenario {scenario_id}")),
        depth=caps.depth_block(CAPS_POSITIONS),
        body={"scenario": {"id": scenario_id, "question": scenario.get("question")}, **body},
    )


# -- credibility: the world/overlay blend (build ticket 31) ---------------------------------


def credibility(
    repo: ModelRepo, caps: Capabilities, org: str, subject: str, command: list[str]
) -> Artefact:
    """The credibility-weighted blend of a world-layer prior with this org's own sparse data.

    An org with no `own_data` file for `subject` prices from the world-layer prior alone, and
    the artefact says so (`twin/credibility.py`): absence is the honest default, not an error.
    """
    overlay = Overlay.load(repo, org)
    prior = overlay.prior(subject)
    own = overlay.own_data_for(subject)
    raw_observations: list[Any] = own["observations"] if own else []
    observations = [float(v) for v in raw_observations]
    industry = Triple.of(prior["industry"])
    result = credibility_mod.blend(subject, industry, observations)

    return Artefact(
        kind=KIND_CREDIBILITY_BLEND,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_CREDIBILITY),
        body={
            "prior_id": prior["id"],
            "prior_basis": prior.get("basis"),
            "own_data_id": own["id"] if own else None,
            "own_data_basis": own.get("basis") if own else None,
            **result.as_dict(),
        },
    )


# -- causal accounts: rival causal accounts as ensemble spread (build ticket 32) ------------


def causal_accounts(
    repo: ModelRepo, caps: Capabilities, org: str, origin: str, account_ids: list[str], command: list[str]
) -> Artefact:
    """Every named rival causal account's own propagation from `origin`, and the spread between
    them — the causal-layer counterpart to `positions()`'s belief spread.

    Nothing here picks a favourite account: `twin/causal_accounts.py` reads every id identically,
    this overlay's own `edges` collection included as just another nameable account, and the
    spread across the named set — not any one account's figure — is the reported uncertainty.
    """
    from . import causal_accounts as causal_accounts_mod

    overlay = Overlay.load(repo, org)
    try:
        body = causal_accounts_mod.ensemble_spread(overlay, account_ids, origin)
    except causal_accounts_mod.CausalAccountError as exc:
        raise VerbError(str(exc)) from exc

    return Artefact(
        kind=KIND_CAUSAL_ACCOUNT_SPREAD,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_CAUSAL_ACCOUNTS),
        body=body,
    )


# -- trade-off curve: net cost of risk across the causal-account ensemble (build ticket 33) -


def trade_off(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    origin: str,
    perspective_id: str,
    account_ids: list[str],
    command: list[str],
) -> Artefact:
    """Every admitted response's net cost of risk, under every named rival causal account, with a
    marked default (build ticket 33).

    One eye's own curve: `twin price` already reports what a shock costs and what a response earns
    in credit, and `twin causal-accounts` already lets rival accounts disagree about how a shock
    propagates. This runs `pricing.price` once per named account, unmodified, and reports cost
    minus credit per account rather than picking one. Nothing here averages the ensemble away or
    ranks an option: the reader draws the trade-off, and the default is one marked point on it.
    """
    from . import tradeoff as tradeoff_mod

    overlay = Overlay.load(repo, org)
    perspective = overlay.perspectives.get(perspective_id)
    if perspective is None:
        known = ", ".join(sorted(overlay.perspectives)) or "none"
        raise VerbError(f"no perspective {perspective_id!r} in overlay {org!r} (have: {known})")
    if not overlay.responses:
        raise VerbError(
            f"overlay {org!r} declares no candidate response, so there is no curve to compare "
            "across the ensemble"
        )
    try:
        body = tradeoff_mod.curve(overlay, perspective, origin, overlay.responses, account_ids)
    except tradeoff_mod.TradeOffError as exc:
        raise VerbError(str(exc)) from exc

    return Artefact(
        kind=KIND_TRADE_OFF_CURVE,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_TRADEOFF),
        body=body,
    )


# -- score ---------------------------------------------------------------------------------


def score(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    forecast_path: str | Path,
    outcome_id: str,
    command: list[str],
    discount: dict[str, Any] | None = None,
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
    # Decision ticket 08 Q4, build ticket 81: the answer key may itself carry a mitigation claim
    # — "the event this forecast predicted did not happen because this evidenced intervention
    # prevented it" — reusing `response.mitigates`'s own schema and validator rather than a second
    # one, because it is the identical causal claim in a different place.
    mitigation_claim = outcome.get("mitigation")

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
        # The intervention-aware scoring rule (decision ticket 08 Q4, build ticket 81): a
        # mitigation credit is a causal claim like any other, so it is use-gated on the identical
        # threshold `pricing.py` already applies to £ credit — reused, not reinvented. Only a
        # non-event can be "prevented" at all, so this never touches a forecast the outcome
        # resolved true, and an ungraded or weakly-graded claim (3-5) earns no protection: the
        # forecast falls through and scores exactly as it would with no claim on record, which is
        # what "grades 4-5 earn NO calibration credit" means in code rather than in prose.
        if not observed and mitigation_claim is not None and evidence.may_price(
            int(mitigation_claim["evidence_grade"])
        ):
            unscoreable.append(
                {**entry, "reason": MITIGATED_NON_EVENT,
                 "detail": (
                     f"outcome {outcome_id!r} records observed=false with a mitigation claim at "
                     f"{mitigation_claim['component']!r}, evidenced at grade "
                     f"{mitigation_claim['evidence_grade']}. A prevented event counts only when "
                     "the prevention is evidenced at grade 1-2 (decision ticket 08 Q4), so this "
                     "forecast is excluded from the calibration record rather than scored as a "
                     "miss — the twin does not get to excuse a genuine miss with 'our warning "
                     "prevented it' unless the prevention itself carries the same evidence a "
                     "£ credit would need"
                 ),
                 "mitigation": {
                     "component": str(mitigation_claim["component"]),
                     "evidence_grade": int(mitigation_claim["evidence_grade"]),
                     "basis": str(mitigation_claim["basis"]),
                 }}
            )
            continue
        raw = scoring.score(probability, observed)
        entry = {
            **entry,
            "probability": probability,
            "observed": observed,
            "regime": str(regime),
            **raw,
            "pins": forecast["pins"],
        }
        if discount is not None:
            # Reported alongside the raw score, never in place of it (build ticket 40 AC): the
            # raw `brier`/`log_loss` above are untouched, and `adjusted_<rule>` is additive.
            entry["discount"] = discount["discount"]
            entry[f"adjusted_{discount['rule']}"] = scoring.quantise(raw[discount["rule"]] + discount["discount"])
        scores.append(entry)

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
                # Build ticket 41: explicit in the score card, not implicit in which outcome it
                # happens to be. False by omission, matching every answer key that makes no
                # hindsight-resistance claim.
                "hindsight_trap": bool(outcome.get("hindsight_trap", False)),
            },
            "rules": list(scoring.RULES),
            "orientation": "lower-is-better" if scoring.LOWER_IS_BETTER else "higher-is-better",
            "significant_digits": scoring.SIGNIFICANT_DIGITS,
            "scores": scores,
            "unscoreable": unscoreable,
            # Build ticket 40: `None` when no discount basis was supplied — an absent measurement,
            # never a zero, which is the same discipline `reliability_diagram`'s empty bins hold.
            "contamination_discount": discount,
        },
    )


# -- reliability diagram (build ticket 09), the discount (build ticket 40) -------------------


def load_score_card(path: str | Path) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load one score-card artefact, kind-checked, returning `(doc, its scores)`.

    The single place that knows what a score card's `body.scores` looks like from the outside —
    `reliability()` below and `cli.cmd_score`'s discount loading (build ticket 40) both pool
    scores from named cards, and shared the same read-and-validate loop until this was pulled out
    from under them.
    """
    doc = load_artefact(path)
    if doc["envelope"]["kind"] != KIND_SCORE_CARD:
        raise VerbError(f"{path} is a {doc['envelope']['kind']!r}, not a score card")
    return doc, doc["body"]["scores"]


def reliability(
    score_card_paths: list[str | Path], caps: Capabilities, command: list[str], bins: int = 10,
) -> Artefact:
    """A reliability diagram over a population of score cards, pooled.

    One score card is one execution's worth of scored forecasts. Nothing here re-derives a score:
    it reads the `scores` each named card already computed — already filtered to `as-consumed` by
    `score()` itself — and pools them into bins, so a thin bin is visible as a small count rather
    than a confident-looking bar (spec story 44).
    """
    if not score_card_paths:
        raise VerbError("no score card named; a reliability diagram over nothing is not a diagram")

    sources: list[dict[str, Any]] = []
    pooled: list[dict[str, Any]] = []
    for raw_path in score_card_paths:
        path = Path(raw_path)
        card_bytes = path.read_bytes()
        card, scores = load_score_card(path)
        sources.append(
            {"sha256": sha256_hex(card_bytes), "pins": card["envelope"]["pins"], "scored": len(scores)}
        )
        pooled.extend(scores)

    diagram = scoring.reliability_diagram(pooled, bins=bins)

    return Artefact(
        kind=KIND_RELIABILITY_DIAGRAM,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "score_cards": sources,
        },
        depth=caps.depth_block(CAPS_RELIABILITY),
        body={"bin_count": bins, "bins": diagram["bins"], "total_scored": diagram["total"]},
    )


# -- heavy-tailed severity: TVaR and the loss-exceedance curve (build ticket 24) -------------


def severity_curve(
    mu: float, sigma: float, threshold: float, xi: float, beta: float, alphas: list[float],
    caps: Capabilities, command: list[str],
) -> Artefact:
    """A loss-exceedance curve over a declared lognormal-body/GPD-tail severity.

    Standalone — no organisation, no component, no `ModelRepo` — the same shape `reliability`
    already is: a derived artefact over authored parameters rather than a graph read. This is
    deliberate: `twin/pricing.py` prices a component from the perspective's declared valuation
    and carries no severity slot on purpose (see its docstring), so the FAIR engine's tail model
    is not a field the schema makes room for either. Anchoring these five parameters to real
    evidence is build ticket 25's job, separated because the implementation and the empirical
    work are different jobs.
    """
    if not alphas:
        raise VerbError("no confidence level named; a loss-exceedance curve over nothing is not a curve")
    try:
        distribution = Severity(mu=mu, sigma=sigma, threshold=threshold, xi=xi, beta=beta)
        curve = distribution.loss_exceedance_curve(alphas)
    except (SeverityError, PertError) as exc:
        # `quantise()` is `pert`'s, reused rather than reinvented, and it raises `PertError` on an
        # overflowing figure — a severity-shaped refusal wearing the sibling module's name.
        raise VerbError(str(exc)) from exc

    return Artefact(
        kind=KIND_LOSS_EXCEEDANCE,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "severity": distribution.as_dict(),
        },
        depth=caps.depth_block(CAPS_SEVERITY),
        body={"curve": curve},
    )


# -- empirical severity anchoring (build ticket 25) ------------------------------------------


def anchored_severity_curve(
    subject_id: str, alphas: list[float], caps: Capabilities, command: list[str],
    sensitivity_grid: list[float] | None = None,
) -> Artefact:
    """A loss-exceedance curve fit from `twin/severity-anchors.yaml`'s cited quantiles, rather
    than from raw parameters named on the command line (`twin severity`'s own path, untouched).

    Every parameter travels with whether it is anchored (cited, or fit from cited quantiles) or
    not, so a reader sees which numbers in the curve below are defensible and which are
    illustrative rather than having to trust the module that produced them. `sensitivity_grid`,
    when given, sweeps the unanchored `xi` at the highest requested alpha and reports how far the
    headline TVaR moves — the anchoring's own honesty about what it does not pin, made visible in
    the artefact rather than only in the YAML.
    """
    from . import anchoring

    if not alphas:
        raise VerbError("no confidence level named; a loss-exceedance curve over nothing is not a curve")
    try:
        result = anchoring.anchored(subject_id)
        curve = result.severity.loss_exceedance_curve(alphas)
        sensitivity_report = (
            anchoring.sensitivity(subject_id, max(alphas), sensitivity_grid) if sensitivity_grid else None
        )
    except (anchoring.AnchoringError, SeverityError, PertError) as exc:
        raise VerbError(str(exc)) from exc

    return Artefact(
        kind=KIND_ANCHORED_LOSS_EXCEEDANCE,
        mark=DERIVED,
        command=command,
        pins={
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "anchors": anchoring.pin(),
        },
        depth=caps.depth_block(CAPS_SEVERITY),
        body={"anchoring": result.as_dict(), "curve": curve, "sensitivity": sensitivity_report},
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
