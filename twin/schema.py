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

import re
from dataclasses import dataclass, field
from typing import Any, Callable

_CAMEL = re.compile(r"([a-z0-9])([A-Z])")
IDENT = re.compile(r"^[a-z0-9][a-z0-9-]{1,63}$")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

COMPONENT_KINDS = ("capability", "activity", "practice", "data")
EVOLUTION = ("genesis", "custom-built", "product", "commodity")
STEEP = ("social", "technological", "economic", "environmental", "political")
EDGE_TYPES = ("needs", "maintains", "knows", "owns")
STRUCTURAL_EDGE, PERSON_EDGES = "needs", ("maintains", "knows", "owns")
REGIMES = ("as-consumed", "as-knowable", "with-hindsight")
CONTAMINATION = ("low", "high", "control")

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
        known = set(self.required) | set(self.optional)
        unknown = sorted(set(doc) - known)
        if unknown:
            raise SchemaError(
                f"{where}: unknown field(s) {', '.join(unknown)}. The schema is closed — "
                f"it accepts {', '.join(sorted(known))} and nothing else."
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
    "claim": Schema(
        required={
            "id": ident,
            "kind": one_of("binding"),
            "signal": ident,
            "component": ident,
            "evidence_grade": whole,
            "claimed_by": text,
            "evidence": text,
        },
        optional={"confidence": unit_interval},
    ),
    "scenario": Schema(
        required={
            "id": ident,
            "question": text,
            "proposition": ident,
            "at": date,
            "components": list_of(ident),
            "world_models": list_of(ident),
        },
        optional={"horizon": date, "substrate": text, "regime": one_of(*REGIMES)},
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
    "edge": Schema(
        required={"id": ident, "type": one_of(*EDGE_TYPES), "from": ident, "to": ident},
        optional={"note": text},
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
}


def validate(kind: str, doc: dict[str, Any], where: str) -> None:
    schema = SCHEMAS.get(kind)
    if schema is None:
        raise SchemaError(f"{where}: no schema for {kind!r}")
    schema.validate(doc, where)


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
    "observations": "observation",
}
