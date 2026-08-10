"""The typed schema for everything in a model repository.

Formalises what the walking skeleton seeded (build ticket 12). Two properties do the work:

**The schemas are closed.** A key that is not declared is rejected. That is what makes
"special-category data has **no schema slot**" true rather than aspirational — Article 9 compliance
is an impossibility of representation, not a validation rule someone could later relax. The named
Article 9 denylist below exists only to give a *specific* error instead of a generic one; the
closure is the guard.

**Validation happens where the model enters the system.** Nothing in this tool writes model files —
authors write text and commit it — so "validated on write" means validated at load, and `twin
validate` is the gate an author or CI runs before the commit.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Any, Callable

from .wardley import WardleyError, band

_CAMEL = re.compile(r"([a-z0-9])([A-Z])")
IDENT = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

COMPONENT_KINDS = ("capability", "activity", "practice", "data")
EVOLUTION = ("genesis", "custom-built", "product", "commodity")
STEEP = ("social", "technological", "economic", "environmental", "political")
EDGE_TYPES = ("needs", "maintains", "knows", "owns", "influences")
STRUCTURAL_EDGE, PERSON_EDGES = "needs", ("maintains", "knows", "owns")
# The structural/causal distinction, made in the type rather than in a comment (decision ticket
# 07, AC 3). `needs` says the value chain would break; `influences` says a change here moves
# something there, by this much, in this direction, after this long.
CAUSAL_EDGE = "influences"
SIGNS = ("positive", "negative")
EVIDENCE_GRADES = (1, 2, 3, 4, 5)
REGIMES = ("as-consumed", "as-knowable", "with-hindsight")
CONTAMINATION = ("low", "high", "control")

# Which collections hold a **dated fact about the world**, and which field carries the date
# (build ticket 36). Declared here rather than derived from the schemas, for the reason the
# invariant manifest declares its refused field names: a gate that works out its own subject
# from the thing it is gating is a tautology, and deleting a line would silently shrink it.
#
# A regrade is deliberately absent. It is the twin's own record-keeping about how strong a claim
# is, not a fact it ingested about the world, and the information regimes gate the second. The
# limit is real and named in `twin/regimes.py`: a regrade dated after T still moves a grade under
# `as-knowable`, and only the rewind leg removes it.
DATED_FACTS = {"signals": "date", "outcomes": "resolved_on"}
# Who a perspective belongs to. Enumerated so that "a non-employer party can instantiate one" is
# checkable rather than asserted — and deliberately flat: nothing anywhere ranks these, and there
# is no field by which one could (build ticket 26).
PARTIES = (
    "employer", "employee-body", "union", "regulator", "customer-body", "supplier", "other",
)

# UK GDPR Article 9.
#
# Two different jobs, and only one of them is a guarantee:
#
# * As **field names**, this list only improves the error message. The guarantee is the closed
#   schema above it — there is no slot, so there is nothing to name.
# * As **values**, this list is a **net, not a proof**. `cohort` and `metric` are free
#   identifiers, so `staff-on-long-term-sickness` is an Article 9 record whatever it is called,
#   and no enumeration of words can be complete. The everyday synonyms are here because the
#   obvious phrasings are the ones that get typed; a determined author can still describe a
#   protected group in words nobody listed. That limit is stated rather than papered over.
SPECIAL_CATEGORY = (
    "biometric", "biometric_data", "church", "disability", "disabled", "ethnic_origin", "ethnicity",
    "faith", "genetic", "genetic_data", "health", "health_condition", "health_status", "hiv",
    "illness", "medical", "mosque", "philosophical_belief", "political_opinion", "politics",
    "pregnancy", "pregnant", "race", "racial_origin", "religion", "religious_belief", "sex_life",
    "sexual_orientation", "sexuality", "sick_leave", "sickness", "synagogue", "trade_union",
    "trade_union_membership", "union_member", "union_membership",
)


class SchemaError(ValueError):
    pass


class SpecialCategoryError(SchemaError):
    """An attempt to author Article 9 data. There is nowhere to put it."""


class RollUpError(SchemaError):
    """An attempt to author an aggregate. Roll-ups are computed from constituents on read."""


# Field names that would hold an authored aggregate (build ticket 13). Like the Article 9 list,
# this is a net rather than the guarantee: the guarantee is that the schemas are closed and no
# roll-up is declared in any of them, so an aggregate has no home. The list exists to give a
# specific error inside the one place a closed schema cannot see — a free-form mapping.
# Deliberately narrow: `count` and `summary` are ordinary words in provenance prose.
ROLLUP_FIELDS = ("aggregate", "aggregates", "roll_up", "rollup", "rollups", "subtotal", "total", "totals")


Validator = Callable[[Any, str], None]


def ident(value: Any, where: str) -> None:
    if not isinstance(value, str) or not IDENT.match(value):
        raise SchemaError(f"{where}: {value!r} is not an identifier (lower-case, digits, hyphens)")


def text(value: Any, where: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise SchemaError(f"{where}: expected non-empty text")


def date(value: Any, where: str) -> None:
    if not isinstance(value, str) or not ISO_DATE.match(value):
        raise SchemaError(f"{where}: expected a date of the form YYYY-MM-DD, got {value!r}")


def boolean(value: Any, where: str) -> None:
    if not isinstance(value, bool):
        raise SchemaError(f"{where}: expected true or false, got {value!r}")


def whole(value: Any, where: str) -> None:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise SchemaError(f"{where}: expected a whole number, got {value!r}")


def unit_interval(value: Any, where: str) -> None:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0.0 <= float(value) <= 1.0:
        raise SchemaError(f"{where}: expected a number between 0 and 1, got {value!r}")


def probability(value: Any, where: str) -> None:
    """Strictly between 0 and 1.

    A forecast of certainty is not a forecast: it carries an infinite penalty under the log score,
    which is not representable and would make the artefact unserialisable. Refusing it here is
    cheaper than discovering it at scoring time.
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SchemaError(f"{where}: expected a probability, got {value!r}")
    if not 0.0 < float(value) < 1.0:
        raise SchemaError(
            f"{where}: probability must be strictly between 0 and 1, got {value!r} — a claim of "
            "certainty carries an infinite log-score penalty and is not a forecast"
        )


def evidence_grade(value: Any, where: str) -> None:
    """The evidence ladder, 1 to 5. The ladder itself is build ticket 18; the slot is here.

    Integers only, and `bool` excluded explicitly. `True == 1` and `3.0 == 3` in Python, so
    without both guards `evidence_grade: true` would pass as the weakest grade and `3.0` would
    reach the artefact as `3.0` — a rung on a five-rung ladder written as if it were continuous.
    """
    if not isinstance(value, int) or isinstance(value, bool) or value not in EVIDENCE_GRADES:
        raise SchemaError(f"{where}: expected an evidence grade 1-5, got {value!r}")


def amount(value: Any, where: str) -> None:
    """A declared money figure. Non-negative, finite, and never a bool.

    Deliberately unitless in the schema: the unit belongs to the perspective that declared it,
    and a perspective prices in its own terms (decision ticket 09, Q1).
    """
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise SchemaError(f"{where}: expected a number, got {value!r}")
    if not math.isfinite(float(value)):
        raise SchemaError(f"{where}: expected a finite number, got {value!r}")
    if float(value) < 0:
        raise SchemaError(f"{where}: expected a non-negative number, got {value!r}")


def valuation(value: Any, where: str) -> None:
    """What a perspective says a component is worth to it, and what backs that claim.

    Closed like everything else, and **graded**: the £ boundary is the same use-gate the causal
    layer runs on. Only a valuation evidenced at the published threshold carries an `amount`;
    anything weaker is a register entry with no figure at all, reported beside the number and
    never inside it (decision ticket 09, Q4). That is what stops reputation becoming
    "reputation damage = £X" — the rejected shadow price.
    """
    if not isinstance(value, dict):
        raise SchemaError(f"{where}: expected a valuation mapping, got {value!r}")
    unknown = sorted((set(value) - {"amount", "evidence_grade", "basis"}), key=str)
    if unknown:
        raise SchemaError(
            f"{where}: unknown field(s) {', '.join(str(u) for u in unknown)}; a valuation is "
            "amount, evidence_grade and basis"
        )
    missing = sorted({"evidence_grade", "basis"} - set(value))
    if missing:
        raise SchemaError(
            f"{where}: missing {', '.join(missing)}. A figure with no grade behind it is exactly "
            "the shadow price decision ticket 09 refuses."
        )
    evidence_grade(value["evidence_grade"], f"{where}.evidence_grade")
    text(value["basis"], f"{where}.basis")

    # Imported here rather than at module scope: `twin.evidence` reads this module's grade tuple,
    # so importing it eagerly would close a cycle.
    from .evidence import may_price

    grade = int(value["evidence_grade"])
    if may_price(grade) and "amount" not in value:
        raise SchemaError(
            f"{where}: evidence grade {grade} admits a figure and none is declared. A valuation "
            "inside the threshold and carrying no amount is a gap, not a register entry."
        )
    if not may_price(grade) and "amount" in value:
        raise SchemaError(
            f"{where}: evidence grade {grade} is outside the pricing threshold, so this valuation "
            "may not carry an amount. It is a register entry — reported beside the number, never "
            "inside it — because inventing comparability the evidence does not support is the "
            "move decision ticket 09 rejected."
        )
    if "amount" in value:
        amount(value["amount"], f"{where}.amount")


def mitigation(value: Any, where: str) -> None:
    """What a response claims it removes from an impact, and what backs that claim.

    Build ticket 30. **Mitigation credit is a causal claim like any other**, so it carries a grade
    and is use-gated on the same rule. That closes the classic unfalsifiability loophole: "the
    incident did not happen *because* of our control" asserts a counterfactual, and asserting it
    is free unless something forces the evidence to travel with it.

    The gate is at credit time rather than here, and the asymmetry with `valuation` is deliberate.
    A weakly-graded valuation may not carry an **amount**, because an amount at grade 5 *is* the
    shadow price. A weakly-graded reduction is a **claim**, not a figure — it becomes money only
    when something multiplies it by a priced impact, and that is where it earns nothing.
    """
    if not isinstance(value, dict):
        raise SchemaError(f"{where}: expected a mitigation mapping, got {value!r}")
    fields = {"component", "reduction", "evidence_grade", "basis"}
    unknown = sorted((set(value) - fields), key=str)
    if unknown:
        raise SchemaError(
            f"{where}: unknown field(s) {', '.join(str(u) for u in unknown)}; a mitigation claim "
            "is component, reduction, evidence_grade and basis"
        )
    missing = sorted(fields - set(value))
    if missing:
        raise SchemaError(
            f"{where}: missing {', '.join(missing)}. A reduction with no grade behind it would "
            "take default credit, and 'the incident did not happen because of our control' is a "
            "causal claim that has to carry its evidence like any other."
        )
    ident(value["component"], f"{where}.component")
    # A unit-interval triple, never a scalar: a control that removes "half" of an impact knows
    # that no better than an elasticity knows its own point, and the range is the honest form.
    pert(value["reduction"], f"{where}.reduction")
    evidence_grade(value["evidence_grade"], f"{where}.evidence_grade")
    text(value["basis"], f"{where}.basis")


def calibration(value: Any, where: str) -> None:
    """Authoring-time provenance for a calibrated range: who estimated it, when, against what
    reference class (build ticket 23, `twin/calibration.md` steps
    `record-the-estimator-and-the-date` and `name-the-reference-class`).

    Optional beside a triple, not required of one. Every triple is still representable without
    this — a wide, honestly-uncertain range is not a worse citizen than a well-provenanced one —
    but without the slot, "the procedure was used" could never be more than assumed. With it, at
    least one triple in the repository can carry proof that it went through the five steps rather
    than being authored as a spreadsheet guess with two decorations either side.

    Not to be confused with the *other* `"calibration"` key this codebase emits — `pert.procedure()`
    in `twin/options.py` and `twin/propagate.py`, the pinned digest of the discipline itself. That
    one names which document was in force for a whole artefact; this one names who followed it for
    one triple. The two never appear in the same body.
    """
    if not isinstance(value, dict):
        raise SchemaError(f"{where}: expected a calibration mapping, got {value!r}")
    fields = {"estimator", "date", "reference_class"}
    unknown = sorted((set(value) - fields), key=str)
    if unknown:
        raise SchemaError(
            f"{where}: unknown field(s) {', '.join(str(u) for u in unknown)}; a calibration record "
            "is estimator, date and reference_class"
        )
    missing = sorted(fields - set(value))
    if missing:
        raise SchemaError(
            f"{where}: missing {', '.join(missing)}. An estimate with no date cannot be checked "
            "against what happened next, and one with no named reference class is a grade 4 or 5 "
            "claim wearing a calibrated range's clothes."
        )
    text(value["estimator"], f"{where}.estimator")
    date(value["date"], f"{where}.date")
    text(value["reference_class"], f"{where}.reference_class")


def _triple(value: Any, where: str, point: Validator, noun: str) -> None:
    """The shape every min/mode/max triple has. Only the point validator differs."""
    if not isinstance(value, dict):
        raise SchemaError(f"{where}: expected a min/mode/max mapping, got {value!r}")
    unknown = sorted(set(value) - {"min", "mode", "max"})
    if unknown:
        raise SchemaError(f"{where}: unknown field(s) {', '.join(unknown)}; {noun} is min, mode, max")
    missing = sorted({"min", "mode", "max"} - set(value))
    if missing:
        raise SchemaError(f"{where}: missing {', '.join(missing)}; a range needs all three points")
    for key in ("min", "mode", "max"):
        point(value[key], f"{where}.{key}")
    low, mode, high = (float(value["min"]), float(value["mode"]), float(value["max"]))
    if not low <= mode <= high:
        raise SchemaError(f"{where}: expected min <= mode <= max, got {low} / {mode} / {high}")


def pert(value: Any, where: str) -> None:
    """A calibrated range as a min/mode/max triple.

    Closed like everything else: exactly these three keys. A triple is how an elasticity states
    its own uncertainty, and a single number cannot — which is why there is no scalar form.
    """
    _triple(value, where, unit_interval, "a PERT triple")


def money_pert(value: Any, where: str) -> None:
    """A calibrated cost range: the same triple, unbounded above.

    Separate from `pert` because the domains are different and conflating them would be a real
    error: an elasticity is a magnitude in the unit interval, and a cost is not.
    """
    _triple(value, where, amount, "a cost triple")


def degenerate(triple: dict[str, Any]) -> bool:
    """A triple with no width. Permitted, and flagged wherever it is read (build ticket 17).

    Not refused: an elasticity genuinely known to a point is representable. But a point estimate
    wearing a range's clothes is false precision, so it is never allowed to look like a range.
    """
    return float(triple["min"]) == float(triple["mode"]) == float(triple["max"])


def one_of(*allowed: str) -> Validator:
    def check(value: Any, where: str) -> None:
        if value not in allowed:
            raise SchemaError(f"{where}: expected one of {', '.join(allowed)}, got {value!r}")

    return check


def list_of(inner: Validator) -> Validator:
    def check(value: Any, where: str) -> None:
        if not isinstance(value, list) or not value:
            raise SchemaError(f"{where}: expected a non-empty list")
        for i, item in enumerate(value):
            inner(item, f"{where}[{i}]")

    return check


def mapping_of(inner: Validator) -> Validator:
    def check(value: Any, where: str) -> None:
        if not isinstance(value, dict) or not value:
            raise SchemaError(f"{where}: expected a non-empty mapping")
        for key, item in value.items():
            ident(key, f"{where} key")
            inner(item, f"{where}.{key}")

    return check


def free_mapping(value: Any, where: str) -> None:
    if not isinstance(value, dict) or not value:
        raise SchemaError(f"{where}: expected a non-empty mapping")


@dataclass(frozen=True)
class Schema:
    """Closed by construction: `required | optional` is the whole vocabulary."""

    required: dict[str, Validator]
    optional: dict[str, Validator] = field(default_factory=dict)

    def validate(self, doc: dict[str, Any], where: str) -> None:
        refuse_special_category(doc, where)
        refuse_authored_rollups(doc, where)
        known = set(self.required) | set(self.optional)
        # Sorted and rendered by `str`: YAML 1.1 reads a bare `on:` or `yes:` as a *boolean* key,
        # so an untrusted model file can hand us a key set that is not all strings — and a
        # refusal that raises a TypeError while formatting its own message is not a refusal.
        unknown = sorted((set(doc) - known), key=str)
        if unknown:
            raise SchemaError(
                f"{where}: unknown field(s) {', '.join(str(u) for u in unknown)}. The schema is "
                f"closed — it accepts {', '.join(sorted(known))} and nothing else."
            )
        missing = sorted(set(self.required) - set(doc))
        if missing:
            raise SchemaError(f"{where}: missing required field(s) {', '.join(missing)}")
        for name, check in {**self.required, **self.optional}.items():
            if name in doc:
                check(doc[name], f"{where}.{name}")


def _article_nine(text_value: str) -> str | None:
    """Which Article 9 category this string names, if any.

    Matched on word-ish boundaries after normalising separators, so `health-status`,
    `Health Status`, `healthStatus` and `staff_on_long_term_sickness_religion` all resolve.
    Substring matching is deliberate and deliberately blunt: a false positive costs an author one
    rename, a false negative puts an Article 9 record in the repository.
    """
    flattened = re.sub(r"[^a-z0-9]+", "_", _CAMEL.sub(r"\1_\2", str(text_value)).lower())
    words = set(flattened.split("_"))
    for category in SPECIAL_CATEGORY:
        parts = category.split("_")
        if all(part in words for part in parts):
            return category
    return None


def refuse_special_category(node: Any, where: str) -> None:
    """No slot, anywhere, at any depth — as a key **or as a value**.

    Checking keys alone would leave the representation intact and only close the spelling: a
    cohort called `staff-on-long-term-sickness` with a metric called `health-status` is a health
    record however tidy the field names are, and the gated behavioural unit is exactly where such
    a thing would land.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            _refuse_scalar(key, f"{where} key {key!r}")
            refuse_special_category(value, f"{where}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            refuse_special_category(value, f"{where}[{i}]")
    elif isinstance(node, str):
        _refuse_scalar(node, where)


def refuse_authored_rollups(node: Any, where: str) -> None:
    """No object may author an aggregate, at any depth (build ticket 13).

    A stored roll-up is a second copy of a fact, and a second copy is a thing that can drift from
    the first. Every aggregate in this system is computed from its constituents on read, so
    changing a constituent changes the roll-up with no separate step and no chance to disagree.
    """
    if isinstance(node, dict):
        for key, value in node.items():
            if str(key).lower().replace("-", "_") in ROLLUP_FIELDS:
                raise RollUpError(
                    f"{where}: {key!r} authors an aggregate. Roll-ups are derived — computed from "
                    "their constituents on read — so there is no authored form to write here."
                )
            refuse_authored_rollups(value, f"{where}.{key}")
    elif isinstance(node, list):
        for i, value in enumerate(node):
            refuse_authored_rollups(value, f"{where}[{i}]")


def _refuse_scalar(value: Any, where: str) -> None:
    category = _article_nine(value) if isinstance(value, str) else None
    if category:
        raise SpecialCategoryError(
            f"{where}: {value!r} names {category!r}, a special category under Article 9, which has "
            "no representation in this model. Compliance here is an impossibility, not a rule."
        )


SCHEMAS: dict[str, Schema] = {
    "world-meta": Schema(
        required={"id": ident, "unit": one_of("world")},
        optional={"name": text, "description": text},
    ),
    "overlay-meta": Schema(
        required={"id": ident, "unit": one_of("overlay"), "org": ident, "world_ref": text},
        optional={"name": text, "description": text},
    ),
    "component": Schema(
        required={"id": ident, "name": text, "kind": one_of(*COMPONENT_KINDS)},
        optional={
            "evolution": one_of(*EVOLUTION),
            # The axis position itself, finer than the stage. Optional because a stage is
            # already a position: absent, the band midpoint is derived (build ticket 14).
            "evolution_position": unit_interval,
            "visibility": unit_interval,
            "needs": list_of(ident),
            "description": text,
        },
    ),
    "proposition": Schema(required={"id": ident, "text": text}, optional={"resolves_on": date}),
    "world-model": Schema(
        required={"id": ident, "name": text, "beliefs": mapping_of(probability)},
        optional={"credence": unit_interval, "note": text},
    ),
    "signal": Schema(
        required={
            "id": ident,
            "date": date,
            "steep": one_of(*STEEP),
            "source": text,
            "statement": text,
            "provenance": free_mapping,
        },
        optional={"substrate": text},
    ),
    # `evidence_grade` is the ladder's rung, not any whole number: the grade travels with the
    # claim, so an off-ladder value would be a claim whose strength nothing can read (ticket 18).
    "claim": Schema(
        required={
            "id": ident,
            "kind": one_of("binding"),
            "signal": ident,
            "component": ident,
            "evidence_grade": evidence_grade,
            "claimed_by": text,
            "evidence": text,
        },
        optional={"confidence": unit_interval},
    ),
    # A grade is immutable without one of these (build ticket 18). It records who moved it, when,
    # from what, to what and why — and the direction is *derived* from the two grades rather than
    # authored, because a record that lets you type the direction lets you type the wrong one.
    "regrade": Schema(
        required={
            "id": ident,
            "subject": ident,
            "from_grade": evidence_grade,
            "to_grade": evidence_grade,
            "regraded_on": date,
            "by_role": ident,
            "reason": text,
            "evidence": text,
        },
        optional={"note": text},
    ),
    # Whose £ this is (build ticket 26). There is no field here that ranks one perspective above
    # another and none that removes a universal constraint, which is what "a perspective may add
    # to the floor and never override it" means when it is structural.
    "perspective": Schema(
        required={
            "id": ident,
            "name": text,
            "party": one_of(*PARTIES),
            "pays": text,
            "values": mapping_of(valuation),
            # Required, not optional. Ruin is perspective-relative — insolvency for a firm,
            # livelihood for a person — so a perspective that declares no boundary has silently
            # inherited somebody else's.
            "ruin": mapping_of(text),
            # Where this perspective's money actually moves (build ticket 29). Required for the
            # same reason `ruin` is: the £ boundary is derived from a causal path to a cash flow,
            # and a perspective that names no cash flow has silently inherited somebody else's
            # ledger. Declaring where the money is is legitimate; declaring what is priceable is
            # not, and this field cannot do the second — admission is computed from the graph.
            "cash_flow": list_of(ident),
        },
        optional={"forbidden": mapping_of(text), "note": text},
    ),
    # A candidate response (build ticket 28). It carries a cost range and the red lines it crosses,
    # and it never carries a verdict: nothing here ranks one option above another, and the
    # pre-filter that removes an excluded one runs before anything prices the rest.
    #
    # `crosses` names constraints, never magnitudes. A constraint is not a very large price, so
    # there is no field here by which a big enough number could buy an excluded option.
    # `mitigates` is optional, and its absence is the honest default (build ticket 30). A response
    # that claims nothing earns nothing — the alternative is a default credit, which is exactly
    # the unfalsifiable claim the grade exists to stop.
    "response": Schema(
        required={"id": ident, "name": text, "addresses": ident, "cost": money_pert},
        optional={
            "crosses": mapping_of(text), "note": text, "mitigates": mitigation,
            "calibration": calibration,
        },
    ),
    # A scenario carries **no regime** (build ticket 36). The regime is a required parameter of
    # the execution, and a scenario-level field would be a default in everything but name: an
    # author who omitted the flag would silently inherit whichever regime the file happened to
    # declare, and a file that declared none would silently inherit the one that scores. The
    # regime is a property of *this run's* information gate, not of the question being asked, and
    # the same scenario is meant to be run under all three.
    "scenario": Schema(
        required={
            "id": ident,
            "question": text,
            "proposition": ident,
            "at": date,
            "components": list_of(ident),
            "world_models": list_of(ident),
        },
        optional={"horizon": date, "substrate": text},
    ),
    # The answer-key format (build ticket 08): the boundary fixture the answer-key track tests
    # against. `contamination` is the slot the Enron control fills at build ticket 40.
    "outcome": Schema(
        required={
            "id": ident,
            "proposition": ident,
            "observed": boolean,
            "resolved_on": date,
            "source": text,
            # Required, not optional: the contamination discount (build ticket 40) is computed
            # from this, and an answer key that does not declare its class silently becomes
            # "assume it is clean" — which is the assumption the discount exists to refuse.
            "contamination": one_of(*CONTAMINATION),
            "source_dated": boolean,
        },
        optional={"note": text},
    ),
    "person": Schema(required={"id": ident}, optional={"role": text}),
    # One schema, two edge families. Which fields are required depends on the type, and
    # `_refine_edge` below is what enforces that — a causal edge without an elasticity is not a
    # causal edge, and a person edge carrying one is asserting something it cannot know.
    "edge": Schema(
        required={"id": ident, "type": one_of(*EDGE_TYPES), "from": ident, "to": ident},
        optional={
            "note": text,
            "sign": one_of(*SIGNS),
            "lag_days": whole,
            "elasticity": pert,
            "evidence_grade": evidence_grade,
            "confidence": unit_interval,
            "calibration": calibration,
        },
    ),
    # The gated unit. Cohort-level by construction — there is no `person` field, which is what
    # "aggregate over individual, cohort over person" means when it is structural rather than a
    # guideline (decision ticket 15).
    "behavioural-meta": Schema(
        required={
            "id": ident,
            "unit": one_of("behavioural"),
            "org": ident,
            "dpia": text,
            "lawful_basis": text,
            "retention_days": whole,
            "advisory_only": boolean,
        },
        optional={"note": text},
    ),
    "observation": Schema(
        required={"id": ident, "cohort": ident, "metric": ident, "value": unit_interval, "observed_on": date},
        optional={"sensor": text, "gameability": one_of("low", "medium", "high"), "note": text},
    ),
    # The industry prior, authored in the world layer (build ticket 31, decision ticket 07 Q1b —
    # the world/overlay split IS the credibility-theory structure). `subject` is a free identifier
    # naming whatever this estimates; nothing here ties it to a component, because the blend is a
    # generic mechanism, not a pricing one.
    "prior": Schema(
        required={"id": ident, "subject": ident, "industry": money_pert, "basis": text},
    ),
    # An org's own sparse observations for a subject a world-layer prior names (build ticket 31).
    # Absence of this file for a subject is the honest default — the org prices from the world
    # prior alone — so `observations` is required non-empty rather than optional-and-empty: a file
    # that exists but claims no data is a different, confusing way to say the same thing.
    "own-data": Schema(
        required={"id": ident, "subject": ident, "observations": list_of(amount), "basis": text},
    ),
}


# A causal edge must assert all four; a fifth, `calibration`, may accompany one but is never
# required — an uncalibrated-but-honest range is still a legal claim (build ticket 23).
CAUSAL_FIELDS = ("sign", "lag_days", "elasticity", "evidence_grade")
CAUSAL_ONLY_OPTIONAL = ("calibration",)


def _refine_component(doc: dict[str, Any], where: str) -> None:
    """Positions are first-class, so a half-position is refused (build ticket 14).

    A component with a stage and no visibility has no place on the map, and a reader who sees
    one axis populated will assume the other was considered. Both, or neither.
    """
    from .wardley import WardleyError, band

    has_stage, has_visibility = "evolution" in doc, "visibility" in doc
    if has_stage != has_visibility:
        missing = "visibility" if has_stage else "evolution"
        raise SchemaError(
            f"{where}: declares one map axis and not the other (missing {missing}). A component "
            "is positioned on both axes or on neither — a half-position reads as a whole one."
        )
    if "evolution_position" not in doc:
        return
    if not has_stage:
        raise SchemaError(f"{where}: declares evolution_position without the evolution stage it refines")
    try:
        low, high = band(str(doc["evolution"]))
    except WardleyError as exc:
        raise SchemaError(f"{where}: {exc}") from None
    value = float(doc["evolution_position"])
    if not low <= value < high and not (high == 1.0 and value == 1.0):
        raise SchemaError(
            f"{where}: evolution_position {value} is outside the {doc['evolution']!r} band "
            f"[{low}, {high}) — the stage and the position must be the same claim"
        )


def _refine_edge(doc: dict[str, Any], where: str) -> None:
    """A causal edge asserts sign, lag and elasticity; a structural or person edge asserts none.

    Propagation that runs on directional hand-waving is what this refuses (build ticket 17): an
    `influences` edge with no elasticity would still be traversable, and would quietly become a
    "some effect, unknown size" that a Monte-Carlo cannot honestly use.
    """
    causal = doc.get("type") == CAUSAL_EDGE
    present = [f for f in CAUSAL_FIELDS + CAUSAL_ONLY_OPTIONAL if f in doc]
    if causal:
        missing = [f for f in CAUSAL_FIELDS if f not in doc]
        if missing:
            raise SchemaError(
                f"{where}: a {CAUSAL_EDGE!r} edge must declare {', '.join(missing)} — a causal "
                "claim without sign, lag and a calibrated elasticity is a direction, not a quantity"
            )
    elif present:
        raise SchemaError(
            f"{where}: a {doc.get('type')!r} edge carries {', '.join(present)}, which only a "
            f"{CAUSAL_EDGE!r} edge may assert. A structural dependency is not a measured effect."
        )


def _refine_regrade(doc: dict[str, Any], where: str) -> None:
    """A regrade moves a grade, and somebody in a registered role stands behind the move."""
    from .sign import SignatureError, role_ids

    if int(doc["from_grade"]) == int(doc["to_grade"]):
        raise SchemaError(
            f"{where}: regrades {doc['subject']!r} from grade {doc['from_grade']} to the same "
            "grade. A regrade that changes nothing is not a regrade."
        )
    try:
        known = role_ids()
    except SignatureError as exc:  # pragma: no cover - a broken register is its own error
        raise SchemaError(f"{where}: {exc}") from None
    if str(doc["by_role"]) not in known:
        raise SchemaError(
            f"{where}: by_role {doc['by_role']!r} is not in the register (have: {', '.join(known)}). "
            "A regrade records who moved a grade, and a role nobody holds records nobody."
        )


def _refine_perspective(doc: dict[str, Any], where: str) -> None:
    """A perspective may add constraints to the universal floor and may never override it."""
    from .constraints import ConstraintError, refuse_floor_override

    try:
        refuse_floor_override(doc)
    except ConstraintError as exc:
        raise SchemaError(f"{where}: {exc}") from None


REFINEMENTS: dict[str, Callable[[dict[str, Any], str], None]] = {
    "component": _refine_component,
    "edge": _refine_edge,
    "regrade": _refine_regrade,
    "perspective": _refine_perspective,
}


def validate(kind: str, doc: dict[str, Any], where: str) -> None:
    schema = SCHEMAS.get(kind)
    if schema is None:
        raise SchemaError(f"{where}: no schema for {kind!r}")
    schema.validate(doc, where)
    refine = REFINEMENTS.get(kind)
    if refine is not None:
        refine(doc, where)


# Which schema a file gets, by the collection directory it sits in.
COLLECTION_KINDS: dict[str, str] = {
    "components": "component",
    "propositions": "proposition",
    "world_models": "world-model",
    "signals": "signal",
    "claims": "claim",
    "scenarios": "scenario",
    "outcomes": "outcome",
    "people": "person",
    "edges": "edge",
    "regrades": "regrade",
    "perspectives": "perspective",
    "responses": "response",
    "observations": "observation",
    "priors": "prior",
    "own_data": "own-data",
}
