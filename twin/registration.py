"""What a `needs` edge may move, and when a resolution question is registered (ecosystem ticket 51).

Two questions, one module, because they are the same question asked twice: **what did this
actually derive?**

**1. The supply-constraint actor path.** Ticket 23 deferred whether
`nb-refining-capacity -> pq-cryptanalysis` is a twin `needs` edge whose propagation moves the
linked capability. `admits()` answers it structurally rather than by argument. A `needs` edge is
`schema.STRUCTURAL_EDGE`: `_refine_edge` refuses `sign`, `lag_days` and `elasticity` on one, so it
carries no direction of effect, no magnitude and no rate; the twin has no `velocity` field
anywhere and no `horizon` outside a scenario, so there is nothing to move a coordinate *by* and no
time to move it *over*. `twin/propagate.py` already walks `influences` and nothing else, and
`twin/blast.py` already follows `needs` backwards to an unpriced reachability set graded
`no-claimed-mechanism` -- and this module RUNS that traversal rather than describing it, because
the first round of this module reasoned about reachability by reading `blast.py` and got it wrong
twice (review F1: it refused `reachability` on a causal edge, though `radius()` walks `influences`
forwards into the blast radius; review F2: it called a two-hop dependency path "no dependency
between them, in either direction"). Reachability is transitive to `blast.MAX_DEPTH`, adjacency is
not, and `admits()` now says which of the two it measured. This module makes the ruling callable,
and extends it in the one direction neither module covers: **no edge of any type moves an
evolution coordinate.** The evolution axis is
an interpretive ordinal judgement (twin ticket 11 Q1), and the one operation ecosystem ticket 93
reopened the ordinal ruling to admit is an ORDER STATISTIC OVER EVIDENCE GRADES -- the weakest
grade among a derivation's signals -- and nothing else. A coordinate move is neither that operation
nor on that axis, so it stays refused, and a coordinate is moved only by a `position` or `override`
claim: an attributable claim with provenance, never a propagation.

**2. The resolution question and the pre-registration date.** Ticket 93 settled how
pre-registration is MEASURED for a forecast: `first_reached()` reads BOTH when a file arrived on
`origin/main` and when it was LAST WRITTEN there, and a file rewritten after it landed re-registers
on the day of the rewrite (review F1); an outcome is the answer key and is immutable once served
(F2). Nothing measured the QUESTION. A scenario-library entry carries the proposition, the horizon
and the words the question is asked in -- **edit any of the three after a forecast is pre-registered
against it and every score moves, with nothing on the record saying so.** So the same measurement
is applied here to the question and to an override, and `resolution_question()` refuses an entry
that names no date a forecast could ever be pre-registered before.

**An override is not scored on its coordinate.** Twin ticket 11 Q1 says an override "can be scored
later like any other forecast". Taken literally that would score `|asserted - revealed|` on the
evolution axis: arithmetic on an ordinal scale, against an answer key nobody publishes. So an
override is scoreable only THROUGH a falsifiable proposition -- a scenario in the same overlay that
names the component the override moves -- and an override that reaches no such scenario is
`unscoreable` with a reason, which is `twin/scoring.py`'s own first-class result and never a zero.

Its own module rather than more of `twin/derived_forecast.py`, for the reason `blast.py` is not
part of `model.py`: that module is the derivation and its artefact, this one is a ruling over the
graph and over git history. **Nothing it asserts is re-implemented here.** The git reads are
`derived_forecast`'s, the graph is `model.py`'s (`structural_edges`, `authored_edges`) and the
traversal is `blast.py`'s (`radius`), all imported -- a second implementation of "when did this
reach main", or of "what edges does this overlay have", is exactly how one of them goes on passing
after the other is fixed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from . import blast
from .derived_forecast import (
    Arrival,
    _date_of,
    _git,
    _read_yaml,
    _served_tree,
    adopters_in,
    first_reached,
    overlay_dir,
)
from .model import Graph, authored_edges, structural_edges, typed_graph
from .schema import CAUSAL_EDGE, STRUCTURAL_EDGE

# The ticket's own pair, kept here as data so the check measures it rather than asserting it.
SUPPLY_CONSTRAINT_PATH = ("nb-refining-capacity", "pq-cryptanalysis")

# What something could ask a relation between two components to move. A closed set, so a caller
# cannot invent a fifth thing and slip past the refusal -- the same move `blast.py`'s BODY_KEYS
# makes on its artefact.
MOVES = ("reachability", "magnitude", "evolution_position", "evidence_grade", "weight", "probability", "price")

# The verdicts `admits()` returns. Four, because "these are not in the model at all" and "they are
# both here and nothing connects them" are different answers and were being read as one.
PRICED_CAUSAL = "priced-causal"
UNPRICED_STRUCTURAL = "unpriced-structural"
# Reachability is TRANSITIVE and adjacency is not, so "nothing relates them" and "nothing relates
# them DIRECTLY" are different answers too. This module used to give the second and print the
# first, which made an absolute claim about a traversal it never ran (review F2).
REACHABLE_NOT_ADJACENT = "reachable-not-adjacent"
NO_RELATION = "no-relation-in-this-model"
NOT_IN_THIS_MODEL = "not-in-this-model"

# The three fields that MAKE a resolution question, and the four that make an override the claim
# it is. Rewriting one of these is the question changing; rewriting a `note` beside them is not.
# Ticket 93's review G2 said a refusal must name what moved rather than only that something did.
QUESTION_FIELDS = ("proposition", "horizon", "question")
OVERRIDE_FIELDS = ("component", "evolution_position", "claimed_by", "evidence_grade")

# Refused on EVERY relation, whatever its type. The first is ticket 51's own ruling; the rest are
# the reopened ordinal ruling (ecosystem ticket 93 on twin 08 Q1) read as what it says.
ALWAYS_REFUSED: dict[str, str] = {
    "evolution_position": (
        "the evolution axis is an interpretive ordinal judgement (twin 11 Q1), not a quantity an "
        "edge can move; a coordinate moves only by a 'position' or 'override' claim, which is "
        "attributable and carries provenance"
    ),
    "evidence_grade": (
        "a grade is a rung, not a number: the one operation the ordinal ruling was reopened to "
        "admit (ecosystem ticket 93) is an order statistic -- the weakest grade among a "
        "derivation's own signals -- and no sum, mean or weight on a grade is admitted"
    ),
    "weight": (
        "a weight on a relation is arithmetic on the ordinal axis wearing another name "
        "(twin/derived_forecast.py refuses `weight` on a signal for the same reason)"
    ),
    "probability": (
        "a probability is derived from signals against a proposition and pre-registered "
        "(ecosystem ticket 93); no edge emits one, and a market LEVEL is never read as one"
    ),
}


class RegistrationError(ValueError):
    """Something was asked to move that no relation in this model admits, or a question was asked
    that nothing could ever be registered against."""


# --- the model, read as plain YAML off a served tree ------------------------------------------


class Model(NamedTuple):
    """One adopter's overlay and the world layer under it, as plain dicts.

    Read the way `twin/derived_forecast.py` reads it -- straight off a materialised tree -- rather
    than through `twin/model.py`'s loader, because this runs over `git archive` of a ref and there
    is no `ModelRepo` there. The loader is what VALIDATES an overlay
    (`verify/twin-evals/verify-twin-evals.sh`); this reads one that already passed.
    """

    org: str
    root: Path
    components: dict[str, dict[str, Any]]
    world_components: dict[str, dict[str, Any]]
    edges: dict[str, dict[str, Any]]
    claims: dict[str, dict[str, Any]]
    scenarios: dict[str, dict[str, Any]]
    outcomes: dict[str, dict[str, Any]]
    propositions: dict[str, dict[str, Any]]
    # Keyed by (COLLECTION, id), never by id alone. An overlay's ids are unique inside a
    # collection and nothing makes them unique across collections, so a claim and a scenario
    # sharing an id would have made `repo_relative` hand git the wrong file -- and a registration
    # date read off the wrong file is exactly the class of defect this module exists to close.
    paths: dict[tuple[str, str], str]

    def component(self, ident: str) -> dict[str, Any] | None:
        """The overlay's own component, or the world layer's. Overlay first: an org may hold a
        component of the same name, and its own is the one its claims are about."""
        return self.components.get(ident) or self.world_components.get(ident)


def _collection(directory: Path, kind: str) -> tuple[dict[str, dict[str, Any]], dict[tuple[str, str], str]]:
    """Every `*.yaml` in one directory, keyed by its own `id`, with the file each came from --
    the file is what `first_reached()` is asked about later. The path key carries the COLLECTION
    as well as the id, because ids are unique inside a collection and across collections nothing
    makes them so."""
    out: dict[str, dict[str, Any]] = {}
    paths: dict[tuple[str, str], str] = {}
    if not directory.is_dir():
        return out, paths
    for path in sorted(directory.iterdir()):
        if path.suffix not in (".yaml", ".yml"):
            continue
        doc = _read_yaml(path)
        if isinstance(doc, dict) and "id" in doc:
            out[str(doc["id"])] = doc
            paths[(kind, str(doc["id"]))] = str(path)
    return out, paths


def read_model(adopter_root: Path, org: str) -> Model:
    """The overlay's collections and the world layer's components and propositions."""
    root = Path(adopter_root)
    org_dir = overlay_dir(root, org)
    world = root / "twin" / "world"
    components, cpaths = _collection(org_dir / "components", "components")
    world_components, _ = _collection(world / "components", "world-components")
    edges, epaths = _collection(org_dir / "edges", "edges")
    claims, clpaths = _collection(org_dir / "claims", "claims")
    scenarios, spaths = _collection(org_dir / "scenarios", "scenarios")
    outcomes, opaths = _collection(org_dir / "outcomes", "outcomes")
    propositions, _ = _collection(world / "propositions", "propositions")
    paths = {**cpaths, **epaths, **clpaths, **spaths, **opaths}
    return Model(org=org, root=root, components=components, world_components=world_components,
                 edges=edges, claims=claims, scenarios=scenarios, outcomes=outcomes,
                 propositions=propositions, paths=paths)


def repo_relative(model: Model, kind: str, ident: str) -> str | None:
    """The path an object of `kind` was read from, relative to the adopter checkout -- what git is
    asked about. None when the object is not one this model holds a file for."""
    absolute = model.paths.get((kind, ident))
    if absolute is None:
        return None
    try:
        return str(Path(absolute).relative_to(model.root))
    except ValueError:  # pragma: no cover - a path from outside the checkout is not ours to read
        return None


# --- 1. what a relation admits ------------------------------------------------------------------
#
# Everything this section says about DATES it derives from git. Everything it used to say about
# REACHABILITY it derived from reading `twin/blast.py` -- and a module that reasons about a
# traversal without running it will eventually describe one that no longer behaves that way (it
# did: review findings F1 and F2). So the traversal is RUN here, on the same model, and what
# `admits()` says about reachability is what `blast.radius()` returned.


class Reach(NamedTuple):
    """One end reached from the other by `twin/blast.py`'s own traversal, and how far away it is."""

    origin: str
    reached: str
    depth: int
    priced: bool
    reason: str | None
    detail: str | None

    def sentence(self) -> str:
        graded = "admitted to pricing" if self.priced else f"graded {self.reason!r}"
        return (f"twin/blast.py's traversal, run here, reaches {self.reached!r} from "
                f"{self.origin!r} at depth {self.depth}, {graded}")

    @property
    def all_causal(self) -> bool:
        """Every hop claims a mechanism. `blast.classify` grades a path with any structural hop
        `no-claimed-mechanism`, so anything else means the whole path is `influences` -- which is
        what `twin/propagate.py` composes a magnitude along, use-gated by grade."""
        return self.reason != blast.NO_MECHANISM


def graph_of(model: Model) -> Graph:
    """`twin/model.py`'s own typed graph, over the plain dicts this module read off a served tree.

    The edges come from `model.structural_edges()` and `model.authored_edges()`, imported. Building
    them here would be a second answer to what this overlay's graph IS, and the whole point of
    running the traversal is that the answer is measured rather than restated -- the same reason
    `first_reached()` is imported rather than re-implemented.
    """
    components = {**model.world_components, **model.components}
    return typed_graph(
        org=model.org, components=components, people={},
        edges=structural_edges(components) + authored_edges(model.edges),
    )


def reachability(model: Model, origin: str, max_depth: int = blast.MAX_DEPTH) -> dict[str, Any]:
    """`twin/blast.py`'s blast radius from `origin`, over this model. The traversal itself, run."""
    return blast.radius(graph_of(model), origin, max_depth=max_depth)


def reached_set(model: Model, origin: str, max_depth: int = blast.MAX_DEPTH) -> tuple[tuple[str, int], ...]:
    """Every component the traversal reaches from `origin`, with its depth. Sorted, so a caller
    can assert on the SET rather than on a sentence about it."""
    artefact = reachability(model, origin, max_depth)
    return tuple(sorted(
        (str(r["component"]), int(r["depth"]))
        for r in artefact["admitted_to_pricing"] + artefact["unpriced"]
    ))


def _path_between(model: Model, source: str, target: str,
                  max_depth: int = blast.MAX_DEPTH) -> tuple[Reach | None, bool]:
    """The best path the traversal finds between the two, in either direction, and whether either
    walk stopped at the depth cap.

    Either direction, because a structural dependency is the same unpriced exposure whichever end
    you name first -- and because `radius()` walks causal edges forwards and structural edges
    backwards from ONE origin, so asking from one end only would answer half the question.
    """
    truncated = False
    found: Reach | None = None
    for a, b in ((source, target), (target, source)):
        artefact = reachability(model, a, max_depth)
        truncated = truncated or bool(artefact["traversal"]["truncated"])
        if found is not None:
            continue
        for entry in artefact["admitted_to_pricing"] + artefact["unpriced"]:
            if str(entry["component"]) != b:
                continue
            found = Reach(origin=a, reached=b, depth=int(entry["depth"]),
                          priced="reason" not in entry, reason=entry.get("reason"),
                          detail=entry.get("detail"))
            break
    return found, truncated


def _no_path(source: str, target: str, max_depth: int, truncated: bool) -> str:
    """What "they are not connected" is allowed to say once the traversal has actually been run."""
    text = (f"twin/blast.py's traversal, run here from each of {source!r} and {target!r}, reaches "
            f"the other at no depth up to its max_depth of {max_depth}")
    if truncated:
        text += (", and one of those walks stopped at that cap, so a path longer than it is not "
                 "ruled out")
    return text


@dataclass(frozen=True)
class Admission:
    """What may move from `source` to `target`, and what may not, with the reason for each."""

    source: str
    target: str
    verdict: str
    reason: str
    admits: tuple[str, ...]
    refused: dict[str, str]

    def sentence(self) -> str:
        moves = ", ".join(self.admits) if self.admits else "nothing"
        return f"{self.source} -> {self.target}: {self.verdict} -- moves {moves}. {self.reason}"


def _needs_related(model: Model, source: str, target: str) -> str | None:
    """How `source` and `target` are structurally related, in this model's own words, or None.

    Both shapes of the same assertion are read: the `needs:` list on a component (build ticket 12's
    value chain) and a `type: needs` edge file. Direction is reported but not required -- a
    structural dependency in either direction is the same unpriced exposure.
    """
    for a, b in ((source, target), (target, source)):
        doc = model.component(a)
        if doc and b in [str(n) for n in (doc.get("needs") or [])]:
            return f"component {a!r} declares needs: [... {b} ...]"
    for ident, edge in sorted(model.edges.items()):
        if str(edge.get("type")) != STRUCTURAL_EDGE:
            continue
        ends = (str(edge.get("from")), str(edge.get("to")))
        if ends in ((source, target), (target, source)):
            return f"edge {ident!r} is a {STRUCTURAL_EDGE!r} edge between them"
    return None


def _causal_edge(model: Model, source: str, target: str) -> str | None:
    for ident, edge in sorted(model.edges.items()):
        if str(edge.get("type")) != CAUSAL_EDGE:
            continue
        if (str(edge.get("from")), str(edge.get("to"))) == (source, target):
            return ident
    return None


def admits(model: Model, source: str, target: str,
           max_depth: int = blast.MAX_DEPTH) -> Admission:
    """What, if anything, moves from `source` to `target` in this model.

    Five verdicts, and the ones that read alike are kept apart on purpose:

    * components that are not in this model at all cannot be connected by anything;
    * components that ARE both here with an edge between them are adjacent;
    * components that are both here, are not adjacent, but which the traversal REACHES one from
      the other are a dependency path of more than one hop -- reachability is transitive to
      `blast.MAX_DEPTH` and adjacency is not, and answering the first with the second is how a
      component two hops downstream gets called unrelated (review F2);
    * components that are both here and that nothing reaches from the other are a modelling gap
      somebody could close.

    Reading "not in this model" as "nothing between them" is how a pair that exists in another
    repository's JSON gets discussed as an edge, and reading "not adjacent" as "not connected" is
    how an exposure that `twin/blast.py` prints every day gets denied in a sentence.

    Whatever the verdict, what it says about REACHABILITY is what the traversal returned: the walk
    is run here, not read about.
    """
    missing = [ident for ident in (source, target) if model.component(ident) is None]
    if missing:
        absent = (f"{' and '.join(repr(m) for m in missing)} "
                  f"{'is' if len(missing) == 1 else 'are'} not a component of overlay "
                  f"{model.org!r} or of the world layer under it")
        refused = dict(ALWAYS_REFUSED)
        refused["reachability"] = (
            f"{absent}, so twin/blast.py has no node to start or finish a traversal on -- this is "
            "not a claim that nothing connects them somewhere else, only that this model has no "
            "end to walk from"
        )
        refused["magnitude"] = f"{absent}, so there is no edge here to compose anything along"
        refused["price"] = f"{absent}, so there is nothing here to price"
        return Admission(
            source=source, target=target, verdict=NOT_IN_THIS_MODEL,
            reason=f"{absent}, so there is no relation here to propagate along",
            admits=(), refused=refused,
        )

    # The traversal, RUN, before any verdict is chosen. Everything below that mentions
    # reachability quotes this measurement.
    reach, truncated = _path_between(model, source, target, max_depth)

    causal = _causal_edge(model, source, target)
    if causal is not None:
        refused = dict(ALWAYS_REFUSED)
        return Admission(
            source=source, target=target, verdict=PRICED_CAUSAL,
            reason=(
                f"edge {causal!r} is an {CAUSAL_EDGE!r} edge asserting sign, lag and a calibrated "
                f"elasticity, so twin/propagate.py composes a MAGNITUDE along it, use-gated by "
                f"evidence grade. It is a dependency path as well as a priced one -- "
                f"twin/blast.py walks {CAUSAL_EDGE!r} edges FORWARDS into the blast radius, and "
                f"{reach.sentence() if reach else _no_path(source, target, max_depth, truncated)}. "
                f"It still moves no coordinate"
            ),
            admits=("reachability", "magnitude"), refused=refused,
        )

    structural = _needs_related(model, source, target)
    if structural is not None:
        refused = dict(ALWAYS_REFUSED)
        refused["magnitude"] = (
            f"a {STRUCTURAL_EDGE!r} edge claims no mechanism: twin/schema.py refuses sign, lag_days "
            "and elasticity on one, so there is nothing to compose. twin/propagate.py walks "
            f"{CAUSAL_EDGE!r} edges and nothing else"
        )
        refused["price"] = (
            "twin/blast.py grades a structural hop 'no-claimed-mechanism' and the blast-radius "
            "artefact has no key a price could be written into"
        )
        return Admission(
            source=source, target=target, verdict=UNPRICED_STRUCTURAL,
            reason=(
                f"{structural}. A structural dependency propagates REACHABILITY -- 'this is "
                "downstream and exposed, and nobody has claimed a mechanism' -- which is a "
                f"first-class answer (twin 08 Q3), not a gap: "
                f"{reach.sentence() if reach else _no_path(source, target, max_depth, truncated)}"
            ),
            admits=("reachability",), refused=refused,
        )

    if reach is not None:
        refused = dict(ALWAYS_REFUSED)
        admitted = ("reachability", "magnitude") if reach.all_causal else ("reachability",)
        if not reach.all_causal:
            refused["magnitude"] = (
                f"{reach.detail or 'at least one hop is structural'}, so twin/propagate.py "
                f"composes nothing along this path: it walks {CAUSAL_EDGE!r} edges and nothing else"
            )
        refused["price"] = (
            "twin/blast.py grades this path "
            f"{reach.reason!r} and the blast-radius artefact has no key a price could be written "
            "into" if not reach.priced else
            "a price is the estate's own gate to compute from a magnitude, not something a "
            "relation hands over"
        )
        return Admission(
            source=source, target=target, verdict=REACHABLE_NOT_ADJACENT,
            reason=(
                f"nothing in overlay {model.org!r} relates them DIRECTLY -- no {CAUSAL_EDGE!r} "
                f"edge, no {STRUCTURAL_EDGE!r} edge and no needs: entry -- but reachability is "
                f"transitive and adjacency is not: {reach.sentence()}"
            ),
            admits=admitted, refused=refused,
        )

    refused = dict(ALWAYS_REFUSED)
    refused["magnitude"] = "there is no edge between them to compose anything along"
    refused["reachability"] = _no_path(source, target, max_depth, truncated)
    refused["price"] = "there is no edge between them to price"
    return Admission(
        source=source, target=target, verdict=NO_RELATION,
        reason=(
            f"both are components of this model, nothing in overlay {model.org!r} relates them "
            f"directly -- no {CAUSAL_EDGE!r} edge, no {STRUCTURAL_EDGE!r} edge and no needs: "
            f"entry -- and {_no_path(source, target, max_depth, truncated)}"
        ),
        admits=(), refused=refused,
    )


def grade_admission(model: Model, source: str, target: str,
                    max_depth: int = blast.MAX_DEPTH) -> list[str]:
    """The ruling GRADED rather than printed, and its reachability claim checked against the walk.

    Two things are observed, both falsifiable:

    1. every move in `ALWAYS_REFUSED` is refused, on whatever verdict this pair returns -- that is
       the ruling itself, and a run that only printed the verdict would not notice it changing;
    2. what the admission SAYS about reachability is what `twin/blast.py` actually returns for the
       pair. The module's one affirmative claim was asserted and never observed until now, which
       is exactly how it came to be wrong about a causal edge (review F1) and about a two-hop path
       (review F2).
    """
    admission = admits(model, source, target, max_depth)
    failures: list[str] = []
    for asked in sorted(ALWAYS_REFUSED):
        try:
            refuse_move(admission, asked)
        except RegistrationError:
            continue
        failures.append(
            f"a {admission.verdict} relation between {source!r} and {target!r} was admitted to "
            f"move {asked!r}: no relation of any type moves it (ecosystem ticket 51, Decision 1)"
        )
    if admission.verdict == NOT_IN_THIS_MODEL:
        return failures
    reach, _ = _path_between(model, source, target, max_depth)
    says = "reachability" in admission.admits
    if says != (reach is not None):
        failures.append(
            f"admits({source!r}, {target!r}) says it "
            f"{'moves' if says else 'does not move'} reachability, and twin/blast.py's traversal "
            f"{'found no path' if reach is None else 'reached it at depth ' + str(reach.depth)}: "
            "the ruling and the traversal it cites disagree"
        )
    return failures


def refuse_move(admission: Admission, what: str) -> None:
    """Raise unless `what` is one of the things this admission actually admits.

    The refusal names what was asked for and why it is refused, because a refusal that says only
    "not allowed" leaves the reader to guess which ruling it came from.
    """
    if what not in MOVES:
        raise RegistrationError(
            f"{admission.source} -> {admission.target}: {what!r} is not one of the things a relation "
            f"could move ({', '.join(MOVES)}). A move nobody named is not admitted by omission"
        )
    if what in admission.admits:
        return
    why = admission.refused.get(what, admission.reason)
    raise RegistrationError(
        f"{admission.source} -> {admission.target}: a {admission.verdict} relation does not move "
        f"{what!r} -- {why}"
    )


# --- 2. the resolution question -----------------------------------------------------------------


def resolution_question(model: Model, scenario_id: str) -> dict[str, Any]:
    """What a scenario-library entry resolves on, and the last day a forecast could register.

    Refused, by name:

    * an entry with no `horizon` -- `horizon` is optional on `twin/schema.py`'s scenario, and an
      entry without one is a standing question, not a resolvable one: there is no date for an
      outcome to fall on and none for a registration to be strictly before;
    * an entry whose `horizon` is not strictly after its own `at` -- nothing that names it could
      EVER be pre-registered, because registration is strictly before the outcome date and the
      entry itself was authored on or after it;
    * an entry whose `proposition` the world layer does not carry, which would resolve against an
      answer key for a question nobody wrote down.
    """
    scenario = model.scenarios.get(scenario_id)
    if scenario is None:
        raise RegistrationError(f"no scenario {scenario_id!r} in overlay {model.org!r}")
    horizon = scenario.get("horizon")
    if not horizon:
        raise RegistrationError(
            f"scenario {scenario_id!r} declares no horizon, so it names no date an outcome falls on "
            "and no date a forecast could be registered strictly before: it is a standing question, "
            "not a resolvable one"
        )
    at, resolves_on = str(scenario.get("at")), str(horizon)
    if dt.date.fromisoformat(resolves_on) <= dt.date.fromisoformat(at):
        raise RegistrationError(
            f"scenario {scenario_id!r}: horizon {resolves_on} is not after its own at {at}. "
            "Pre-registration is strictly before the outcome date (ecosystem ticket 93), and this "
            "entry was authored on or after its own, so nothing could ever be registered against it"
        )
    proposition = str(scenario.get("proposition"))
    if proposition not in model.propositions:
        raise RegistrationError(
            f"scenario {scenario_id!r} resolves on proposition {proposition!r}, which the world "
            f"layer under overlay {model.org!r} does not carry"
        )
    matching = sorted(
        ident for ident, outcome in model.outcomes.items()
        if str(outcome.get("proposition")) == proposition
    )
    return {
        "scenario": scenario_id,
        "question": str(scenario.get("question", "")).strip(),
        "proposition": proposition,
        "resolves_on": resolves_on,
        "authored_at": at,
        "register_before": str(dt.date.fromisoformat(resolves_on) - dt.timedelta(days=1)),
        "resolved_by": (
            f"an outcome record in twin/orgs/{model.org}/outcomes resolving {proposition!r}, merged "
            f"onto the served ref on or after {resolves_on} and immutable once there"
        ),
        "outcomes": matching,
        "scored_by": (
            "twin/scoring.py's Brier and log loss, on a probability registered before "
            f"{resolves_on}; a probability that was not is not scored"
        ),
        "never_scored_on": (
            "the entry's own words: a question is not a forecast and carries no probability, so "
            "the entry pre-registers nothing by existing"
        ),
    }


def override_resolution(model: Model, claim_id: str) -> dict[str, Any]:
    """What an `override` claim resolves on -- and what it never resolves on.

    An override asserts an `evolution_position`: a point on an interpretive ordinal axis, against
    which nobody publishes an answer key. Scoring it directly would be `|asserted - revealed|` on
    an ordinal scale, which twin 11 Q1 refuses and which ecosystem ticket 93's reopening does not
    reach (that admits an order statistic over evidence GRADES and nothing else). So an override is
    scoreable only THROUGH a falsifiable proposition: a scenario in the same overlay that names the
    component the override moves. An override that reaches none is `unscoreable` WITH A REASON --
    `twin/scoring.py`'s own first-class result -- and never a zero, because a zero reads as a
    confident claim that was wrong.
    """
    claim = model.claims.get(claim_id)
    if claim is None:
        raise RegistrationError(f"no claim {claim_id!r} in overlay {model.org!r}")
    if str(claim.get("kind")) != "override":
        raise RegistrationError(
            f"claim {claim_id!r} is a {claim.get('kind')!r} claim, not an override; only an override "
            "asserts a corrected coordinate a human answers for"
        )
    component = str(claim.get("component"))
    if model.component(component) is None:
        raise RegistrationError(
            f"override {claim_id!r} moves component {component!r}, which is not in overlay "
            f"{model.org!r} or the world layer under it"
        )
    through = []
    for ident in sorted(model.scenarios):
        scenario = model.scenarios[ident]
        if component not in [str(c) for c in (scenario.get("components") or [])]:
            continue
        try:
            question = resolution_question(model, ident)
        except RegistrationError as exc:
            through.append({"scenario": ident, "unresolvable": str(exc)})
            continue
        through.append({
            "scenario": ident,
            "proposition": question["proposition"],
            "resolves_on": question["resolves_on"],
            "register_before": question["register_before"],
        })
    scoreable = [entry for entry in through if "proposition" in entry]
    return {
        "override": claim_id,
        "component": component,
        "claimed_by": str(claim.get("claimed_by")),
        "evidence_grade": claim.get("evidence_grade"),
        "asserts": {"evolution_position": claim.get("evolution_position")},
        "scoreable": bool(scoreable),
        "through": through,
        "unscoreable_because": None if scoreable else (
            f"no scenario in overlay {model.org!r} names component {component!r}, so this override "
            "moves a coordinate no resolvable question depends on. Recorded and arguable, never "
            "counted: an unscoreable claim is a first-class result with a reason, not a zero"
        ),
        "never_scored_on": (
            "the evolution_position itself -- an interpretive ordinal coordinate with no published "
            "answer key. Scoring |asserted - revealed| on it is arithmetic on an ordinal scale "
            "(twin 11 Q1), which ecosystem ticket 93's reopening does not admit"
        ),
    }


# --- 3. when it registered ----------------------------------------------------------------------


def _blob(repo: Path, sha: str, path: str) -> dict[str, Any] | None:
    """One committed blob, parsed. None when git cannot show it or it is not a mapping."""
    text = _git(Path(repo), "show", f"{sha}:{path}")
    if text is None:
        return None
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError:
        return None
    return doc if isinstance(doc, dict) else None


def fields_moved(repo: Path, arrival: Arrival, path: str,
                 fields: tuple[str, ...]) -> list[str] | None:
    """Which of `fields` differ between the blob that ARRIVED on the ref and the blob there now.

    `[]` when the rewrite moved none of them, `None` when either blob cannot be read. The
    counterpart of `twin/derived_forecast.py::probabilities_moved`, and it exists for the same
    reason review G2 gave there: the registration rule is blob identity, so a rewrite is a rewrite
    whatever changed -- but a report that says only "rewritten" cannot tell an appended note from
    a changed question, and those are not the same event to anyone reading it.
    """
    before = _blob(repo, arrival.added_sha, path)
    after = _blob(repo, arrival.last_sha, path)
    if before is None or after is None:
        return None
    return [f"{field}: {before.get(field)!r} -> {after.get(field)!r}"
            for field in fields if before.get(field) != after.get(field)]


def question_moved(repo: Path, arrival: Arrival, path: str) -> list[str] | None:
    """Which of a scenario entry's `proposition`, `horizon` and `question` moved since it landed.

    Those three are the question: the thing resolved on, the day it resolves, and the words it is
    asked in. A `note` beside them can be appended without the question changing -- and the
    override PR this ticket writes does exactly that, so the distinction is not hypothetical.
    """
    return fields_moved(repo, arrival, path, QUESTION_FIELDS)


def override_moved(repo: Path, arrival: Arrival, path: str) -> list[str] | None:
    """Which of an override's `component`, `evolution_position`, `claimed_by` and `evidence_grade`
    moved since it landed -- the coordinate it asserts, whose it is, and at what rung."""
    return fields_moved(repo, arrival, path, OVERRIDE_FIELDS)


def _moved_sentence(moved: list[str] | None, fields: tuple[str, ...]) -> str:
    """What a rewrite is allowed to say it moved."""
    if moved is None:
        return "what moved could not be read: the blob that arrived is no longer readable here"
    if not moved:
        return (f"none of {', '.join(fields)} moved -- the rewrite was to another field (a note, a "
                "comment or whitespace), and it re-registers the file all the same")
    return "; ".join(moved)


def registered_on(repo: Path, path: str, before: str | None = None,
                  ref: str = "refs/remotes/origin/main",
                  moved_fields: tuple[str, ...] | None = None) -> dict[str, Any]:
    """When the CONTENT at `path` was registered on the served ref, measured ticket 93's way.

    `first_reached()` is imported, never re-implemented: it returns BOTH first-parent dates, when
    the path arrived and when it was LAST WRITTEN there, and the registration is the last write. A
    file rewritten after it landed is a new file and re-registers on the day of the rewrite --
    which is the whole of review F1, applied here to the QUESTION and to the OVERRIDE rather than
    to the forecast. `before`, when given, is the date the registration must be strictly earlier
    than (a scenario's own horizon, or the horizon of a scenario an override is scored through).
    `moved_fields`, when given, says WHAT moved in a rewrite as well as that one happened -- the
    distinction ticket 93's review G2 insisted on for a forecast's numbers.
    """
    arrival: Arrival | None = first_reached(Path(repo), path, ref=ref)
    if arrival is None:
        return {
            "path": path, "on_ref": False,
            "sentence": f"{path} is not on {ref}: nothing is registered until it is merged there",
        }
    registers_on = str(_date_of(arrival.last))
    out: dict[str, Any] = {
        "path": path, "on_ref": True,
        "arrived": str(_date_of(arrival.added)),
        "registers_on": registers_on,
        "rewritten": arrival.rewritten,
        "sentence": arrival.where(ref),
    }
    if moved_fields is not None and arrival.rewritten:
        moved = fields_moved(Path(repo), arrival, path, moved_fields)
        out["moved"] = moved
        out["moved_sentence"] = _moved_sentence(moved, moved_fields)
        out["sentence"] += f" -- {out['moved_sentence']}"
    if before is not None:
        out["before"] = before
        out["in_time"] = dt.date.fromisoformat(registers_on) < dt.date.fromisoformat(str(before))
    return out


# --- the check ----------------------------------------------------------------------------------


def _platform_intel_pair(estate: Path, pair: tuple[str, str]) -> tuple[str, str | None]:
    """What the two ids the ticket names actually ARE, measured on the platform's served intel.

    Returns the sentence to print and, when the measurement contradicts the finding it was taken
    for, the failure to grade on.

    Decision 1's factual half is that the pair is two rows of platform's Wardley intel that both
    point at a FAIR RISK and never at each other. That is a claim about somebody else's file,
    which somebody else can edit -- so it is graded and not only printed (review F5). A
    could-not-look stays a could-not-look and is never graded green.
    """
    repo = estate / "platform"
    if not (repo / ".git").exists():
        return "could not look: no platform checkout to read wardley/intel/market-intel.json from", None
    with tempfile.TemporaryDirectory() as tmp:
        tree = _served_tree(repo, "refs/remotes/origin/main", Path(tmp), paths=("wardley",))
        if tree is None:
            return "could not look: platform's refs/remotes/origin/main carries no wardley/ tree", None
        intel = tree / "wardley" / "intel" / "market-intel.json"
        if not intel.is_file():
            return "could not look: no wardley/intel/market-intel.json on platform's served ref", None
        doc = json.loads(intel.read_text(encoding="utf-8"))
    rows = {str(c.get("id")): c for c in doc.get("components", []) if str(c.get("id")) in pair}
    if len(rows) != len(pair):
        absent = [ident for ident in pair if ident not in rows]
        return f"platform's served intel carries no row for {', '.join(absent)}", None
    described = "; ".join(
        f"{ident} actor={rows[ident].get('actor')!r} evolution={rows[ident].get('evolution')} "
        f"velocity={rows[ident].get('velocity')} links_risk={rows[ident].get('links_risk')!r}"
        for ident in pair
    )
    # The graded half: does either row point at the OTHER id? That is the shape ticket 23 recorded
    # as "the links_risk edge to the capability it constrains", and finding it would mean the
    # premise this decision rests on had stopped being true.
    points_at_each_other = [
        f"platform's intel row {ident!r} names links_risk {rows[ident].get('links_risk')!r}, which "
        f"is the OTHER id in the pair. Ecosystem ticket 51's Decision 1 rests on neither row "
        f"pointing at the other; it now does, and the decision needs re-reading, not re-asserting"
        for ident in pair if str(rows[ident].get("links_risk")) in pair
    ]
    targets = {str(rows[ident].get("links_risk")) for ident in pair}
    shared = (
        f"both name the same links_risk ({sorted(targets)[0]!r}), which is a FAIR risk id and not "
        "a component, so neither row points at the other"
    ) if len(targets) == 1 else f"they name different links_risk targets ({sorted(targets)})"
    return f"{described} -- {shared}", (points_at_each_other[0] if points_at_each_other else None)


def check(estate: str, hub: str, adopters: list[str] | None = None,
          ref: str = "refs/remotes/origin/main") -> int:
    """Grade the SERVED artefact: every scenario-library entry and every override claim on
    `origin/main` of every adopter carrying a twin overlay, read off the ref's committed tree with
    `git archive`. 0 observed true, 1 observed false, 3 could not look."""
    estate_path, hub_path = Path(estate), Path(hub)
    if not (hub_path / "twin" / "VERSION").is_file():
        print(f"SKIP: no twin/VERSION under {hub_path}: this is not a checkout of the hub")
        return 3
    names = adopters if adopters is not None else adopters_in(estate_path)
    if not names:
        print(f"SKIP: no unit under {estate_path} carries a twin overlay on {ref}; there is no "
              "scenario library or override to read")
        return 3

    fails: list[str] = []
    scenarios_read = resolvable = overrides_read = scoreable = registered = rewritten = 0
    traversed = reaching = 0
    horizons: set[str] = set()
    admissions: list[str] = []
    with tempfile.TemporaryDirectory() as tmp:
        for name in names:
            repo = estate_path / name
            tree = _served_tree(repo, ref, Path(tmp) / name)
            if tree is None:
                fails.append(f"{name}: could not read {ref} (no checkout, or the ref carries no twin/ tree)")
                continue
            model = read_model(tree, name)
            print(f"    {name}: {len(model.scenarios)} scenario(s), {len(model.claims)} claim(s), "
                  f"{len(model.outcomes)} outcome(s) on {ref}")
            for scenario_id in sorted(model.scenarios):
                scenarios_read += 1
                try:
                    question = resolution_question(model, scenario_id)
                except RegistrationError as exc:
                    fails.append(f"{name}: {exc}")
                    continue
                resolvable += 1
                horizons.add(question["resolves_on"])
                path = repo_relative(model, "scenarios", scenario_id)
                if path is None:  # pragma: no cover - every scenario came from a file
                    continue
                mark = registered_on(repo, path, before=question["resolves_on"], ref=ref,
                                     moved_fields=QUESTION_FIELDS)
                if mark["on_ref"]:
                    registered += 1
                    if mark["rewritten"]:
                        rewritten += 1
                    if not mark["in_time"]:
                        fails.append(
                            f"{name}: the resolution question of scenario {scenario_id!r} registered "
                            f"on {mark['registers_on']}, which is not before its own horizon "
                            f"{question['resolves_on']}: {mark['sentence']}. A question rewritten "
                            "after the answer was knowable moves every score taken against it, and "
                            "re-registers on the day of the rewrite (ecosystem ticket 93, F1)"
                        )
                print(f"      scenario {scenario_id}: resolves {question['proposition']} on "
                      f"{question['resolves_on']}, register before {question['register_before']}; "
                      f"{mark['sentence']}")
            for claim_id in sorted(model.claims):
                if str(model.claims[claim_id].get("kind")) != "override":
                    continue
                overrides_read += 1
                try:
                    resolution = override_resolution(model, claim_id)
                except RegistrationError as exc:
                    fails.append(f"{name}: {exc}")
                    continue
                path = repo_relative(model, "claims", claim_id)
                # The EARLIEST horizon among the questions this override is scored through, not
                # whichever came first alphabetically: the strictest deadline is the one that
                # binds, and an entry in `through` that names an unresolvable scenario carries no
                # date at all.
                dated = [e for e in resolution["through"] if "resolves_on" in e]
                first = min(dated, key=lambda e: str(e["resolves_on"])) if dated else None
                mark = registered_on(repo, path, before=first["resolves_on"] if first else None,
                                     ref=ref, moved_fields=OVERRIDE_FIELDS) \
                    if path else {"on_ref": False, "sentence": "no file"}
                if resolution["scoreable"]:
                    scoreable += 1
                    if mark["on_ref"] and not mark.get("in_time", True):
                        fails.append(
                            f"{name}: override {claim_id!r} registered on {mark['registers_on']}, "
                            f"not before {first['resolves_on'] if first else '?'}: {mark['sentence']}"
                        )
                print(f"      override {claim_id}: moves {resolution['component']}, "
                      f"{'scoreable through ' + ', '.join(str(e['scenario']) for e in resolution['through'] if 'proposition' in e) if resolution['scoreable'] else 'UNSCOREABLE -- ' + str(resolution['unscoreable_because'])}; "
                      f"{mark['sentence']}")
            # The traversal over THIS adopter's real graph, on the components its own questions
            # name. The ticket's pair is in no real model, so grading only that pair would leave
            # the real-estate half deriving its dates from git and its reachability from nothing --
            # which is the asymmetry review F4 was about, and it does not stop being one because
            # the fixture half closed it.
            asked_about = sorted({
                str(c) for scenario in model.scenarios.values()
                for c in (scenario.get("components") or [])
                if model.component(str(c)) is not None
            })
            for ident in asked_about:
                downstream = reached_set(model, ident)
                traversed += 1
                reaching += 1 if downstream else 0
                admissions.append(
                    f"{name}: twin/blast.py's traversal from {ident!r}, a component this overlay's "
                    f"own questions name, reaches "
                    + (", ".join(f"{c} (depth {d})" for c, d in downstream) if downstream
                       else "nothing: nothing in this overlay declares it as a need")
                )
            admission = admits(model, *SUPPLY_CONSTRAINT_PATH)
            admissions.append(f"{name}: {admission.sentence()}")
            # The ruling, GRADED. Printing a verdict tells a reader what the module thinks;
            # grading it is what notices the day it stops being true (review F5).
            fails.extend(grade_admission(model, *SUPPLY_CONSTRAINT_PATH))
            # And the traversal itself, RUN over this adopter's own graph, so the module's one
            # affirmative claim is a measurement on every run rather than a citation (review F4).
            for origin in SUPPLY_CONSTRAINT_PATH:
                if model.component(origin) is None:
                    continue
                reached = reached_set(model, origin)
                admissions.append(
                    f"{name}: twin/blast.py's traversal from {origin!r} reaches "
                    + (", ".join(f"{c} (depth {d})" for c, d in reached) if reached else "nothing")
                )

    for line in admissions:
        print(f"    {line}")
    intel_sentence, intel_finding = _platform_intel_pair(estate_path, SUPPLY_CONSTRAINT_PATH)
    print(f"    the ticket's pair on platform's served intel: {intel_sentence}")
    if intel_finding is not None:
        fails.append(intel_finding)
    print(f"    ruling, graded on every adopter above rather than printed: no relation of any type "
          f"moves an evolution_position, an evidence_grade, a weight or a probability -- "
          f"{len(ALWAYS_REFUSED)} refusals that hold on every verdict, and what each admission says "
          f"about reachability is checked against twin/blast.py's traversal of that same model")
    print(f"    limits: {scenarios_read} scenario(s) read, {resolvable} resolvable, "
          f"{registered} registered on {ref} ({rewritten} rewritten since they arrived); "
          f"{overrides_read} override(s), {scoreable} scoreable through a proposition; "
          f"horizons {', '.join(sorted(horizons)) if horizons else 'none'}; "
          f"twin/blast.py's traversal run over {traversed} component(s) the questions name, "
          f"{reaching} of which reach anything at all")

    if fails:
        for line in fails:
            print(f"    FAIL: {line}")
        print(f"FAIL: {len(fails)} registration fact(s) observed false on {ref} of {', '.join(names)}")
        return 1
    if scenarios_read == 0:
        print(f"SKIP: no scenario-library entry has reached {ref} of any adopter ({', '.join(names)})")
        return 3
    if overrides_read == 0:
        print(f"SKIP: {resolvable} of {scenarios_read} scenario-library entries on {ref} carry a "
              f"resolution question and a registration date, and 0 override claim has reached "
              f"{ref} of any adopter ({', '.join(names)}): the headline skill's override PR "
              "(ecosystem ticket 23) has not been merged")
        return 3
    print(f"PASS: {resolvable} of {scenarios_read} scenario-library entries on {ref} name a "
          f"resolution question -- a proposition the world layer carries, a horizon after their own "
          f"authoring date, and a registration date read off first-parent history -- and "
          f"{scoreable} of {overrides_read} override(s) are scoreable through one of them, none on "
          "its own coordinate; the ruling was graded on every adopter and its reachability claim "
          "checked against twin/blast.py's own traversal, not against a reading of it")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="grade the served scenario library and overrides")
    c.add_argument("--estate", required=True)
    c.add_argument("--hub", required=True)
    c.add_argument("--adopter", action="append", default=None)
    a = sub.add_parser("admits", help="what moves between two components of one overlay")
    a.add_argument("--adopter", required=True, help="the adopter checkout")
    a.add_argument("--org", required=True)
    a.add_argument("source")
    a.add_argument("target")
    q = sub.add_parser("question", help="the resolution question of one scenario-library entry")
    q.add_argument("--adopter", required=True)
    q.add_argument("--org", required=True)
    q.add_argument("scenario")
    o = sub.add_parser("override", help="what an override claim is scoreable through")
    o.add_argument("--adopter", required=True)
    o.add_argument("--org", required=True)
    o.add_argument("claim")
    args = parser.parse_args(argv)
    if args.cmd == "check":
        return check(args.estate, args.hub, adopters=args.adopter)
    model = read_model(Path(args.adopter), args.org)
    try:
        if args.cmd == "admits":
            admission = admits(model, args.source, args.target)
            print(yaml.safe_dump({
                "source": admission.source, "target": admission.target, "verdict": admission.verdict,
                "reason": admission.reason, "admits": list(admission.admits),
                "refused": admission.refused,
            }, sort_keys=False, width=100))
        elif args.cmd == "question":
            print(yaml.safe_dump(resolution_question(model, args.scenario), sort_keys=False, width=100))
        else:
            print(yaml.safe_dump(override_resolution(model, args.claim), sort_keys=False, width=100))
    except RegistrationError as exc:
        print(f"refused: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
