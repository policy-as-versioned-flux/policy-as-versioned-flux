"""The constraint pre-filter, and the only door to pricing behind it.

Build ticket 28, from decision tickets 09 and 15. **A constraint is not a very large price.** A
price can be outbid: with enough upside an optimiser finds the number that buys a monstrous
option, and a very large penalty still asserts that a number exists. So an excluded option is
removed from the choice set **before anything prices anything**, and the removal record carries no
figure at all.

That ordering is asserted structurally rather than by convention, in two locks:

* `Admitted` is the only thing that can be priced, and `prefilter` is the only thing that produces
  one. Constructing an `Admitted` any other way is refused.
* pricing is a **method on `Admitted`**, not a free function. There is no callable anywhere in
  this module that takes an unfiltered option and returns a number.

The pre-filter has no constraint list of its own. It reads the set the perspective resolves —
the universal floor plus that perspective's declared red lines — so what is excluded is exactly
what was published, and changing one changes the other.

Ruin is perspective-relative by design: insolvency for a firm, loss of livelihood for a person. An
option that crosses one perspective's ruin boundary and not another's is removed for the first and
survives for the second, and the artefact says which constraints were not in force rather than
implying the option was never checked.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import constraints, pert
from .artefact import ArtefactError
from .canon import walk_keys, walk_values
from .constraints import ConstraintError
from .pert import Triple

# The seed and draw count are part of the format, recorded in every priced set so a reader can
# reproduce the sample rather than trust it.
SEED = "twin-option-pricing-v1"
DRAWS = 2000

# The one lock on construction. `Admitted` is what pricing accepts and `prefilter` is what makes
# one; a module-private sentinel is what makes that a fact rather than a docstring.
#
# `ponytail:` a lock, not a proof. Python has no private constructor, so somebody who reaches for
# this module's underscore-prefixed name can still build one by hand. It stops the accidental
# reordering and the innocent refactor, which is what the invariant is actually defending against;
# a determined author who wants to price an excluded option has to write down that they did.
_FROM_THE_PREFILTER = object()

# A **removal record** is closed separately and much harder, because a flat whole-body key set
# cannot make the guarantee: the priced half legitimately needs `cost`, `mean`, `min` and the
# rest, so a single set containing them would let an excluded option carry `cost: "GBP 5m"` and
# still pass. These nine keys are the ones the pre-filter writes, all of them strings, and the
# assertion `price_shaped & REMOVAL_KEYS == set()` is then available and true — the same
# assertion the blast radius can make about its own body.
REMOVAL_KEYS = frozenset(
    {"option", "name", "addresses", "constraint", "class", "tier", "forbids", "because",
     "not_in_force_here"}
)

# The rest of the body, closed. Same move as the blast radius and Article 9.
BODY_KEYS = frozenset(
    {
        "perspective", "prefilter", "calibration", "sampler", "priced", "not_a_ranking",
        "ran_before_pricing", "rule", "known_limit", "constraint_set", "considered", "removed",
        "admitted",
        "pin", "version", "digest", "constraints", "floor_is_negotiable",
        "id", "source", "note",
        "document", "sha256", "interval", "steps",
        "engine", "seed", "draws", "seeded_by", "reproducible_within", "significant_digits",
        "cost", "sampled", "min", "mode", "max", "mean", "variance", "degenerate",
        "p05", "p50", "p95",
    }
    | REMOVAL_KEYS
)


@dataclass(frozen=True)
class Option:
    """A candidate response. It carries a cost range and never a rank."""

    id: str
    name: str
    addresses: str
    cost: Triple
    crosses: dict[str, str]

    @classmethod
    def of(cls, doc: dict[str, Any]) -> "Option":
        return cls(
            id=str(doc["id"]),
            name=str(doc["name"]),
            addresses=str(doc["addresses"]),
            cost=Triple.of(doc["cost"]),
            crosses={str(k): str(v).strip() for k, v in (doc.get("crosses") or {}).items()},
        )


@dataclass(frozen=True)
class Admitted:
    """What survived the pre-filter. The only input pricing accepts."""

    perspective: str
    options: tuple[Option, ...]
    removed: tuple[dict[str, str], ...]
    considered: tuple[str, ...]
    constraint_set: dict[str, Any]
    made_by: Any = None

    def __post_init__(self) -> None:
        if self.made_by is not _FROM_THE_PREFILTER:
            raise ConstraintError(
                "an Admitted set was built without running the constraint pre-filter. Pricing "
                "accepts nothing else, and the pre-filter is the only thing that produces one — "
                "otherwise `prefilter_precedes_pricing` would be an ordering convention."
            )

    def _refuse_a_broken_partition(self) -> None:
        """Re-derive the filter from the constraint set, and refuse if the answer disagrees.

        This is the lock that actually holds. The construction sentinel is a dataclass **field**,
        so `dataclasses.replace()` carries it through and rebuilds an `Admitted` around any option
        list at all — the ordinary way to derive a frozen dataclass, and therefore exactly the
        "innocent refactor" the sentinel claimed to stop.

        So the decision is recomputed here, from the constraint set the object carries, rather
        than trusted. A copy cannot carry a wrong answer past this, because the answer is not what
        is being checked — the inputs are.
        """
        in_force = {str(entry["id"]) for entry in (self.constraint_set.get("constraints") or [])}
        crossing = sorted(o.id for o in self.options if set(o.crosses) & in_force)
        if crossing:
            raise ConstraintError(
                f"{', '.join(crossing)} would be priced while crossing a constraint in force for "
                f"{self.perspective!r}. The pre-filter's answer disagrees with the constraint set "
                "this object carries, so it was not the pre-filter that produced it."
            )

        priced = {option.id for option in self.options}
        excluded = {str(entry["option"]) for entry in self.removed}
        considered = set(self.considered)
        if priced & excluded:
            raise ConstraintError(
                f"{', '.join(sorted(priced & excluded))} is both removed and admitted. An excluded "
                "option is absent from the choice set, not present with a number beside it."
            )
        if priced | excluded != considered:
            raise ConstraintError(
                "the choice set does not account for what it considered: considered "
                f"{sorted(considered)}, priced {sorted(priced)}, removed {sorted(excluded)}. "
                "Pricing accepts only what the pre-filter produced, and an option that appears "
                "without having been filtered — or a removal record that has gone missing — is "
                "how `prefilter_precedes_pricing` stops being true."
            )

    def priced(self, seed: str = SEED, draws: int = DRAWS) -> dict[str, Any]:
        """Cost every surviving option. An excluded one is not here, at any magnitude.

        Pricing is a method rather than a free function on purpose: there is then no callable that
        could be handed an unfiltered list. The partition check below is what makes that hold
        against a copy of this object rather than only against a fresh one.
        """
        self._refuse_a_broken_partition()
        body = {
            "perspective": self.perspective,
            "prefilter": {
                "ran_before_pricing": True,
                "rule": (
                    "an option that crosses a constraint in force for this perspective is removed "
                    "from the choice set before any pricing runs, and its record carries no figure "
                    "— a constraint is not a very large price, because a price can be outbid"
                ),
                "known_limit": (
                    "an option declares the constraints it crosses; nothing derives them. The "
                    "magnitude leg is airtight — a cost is not an input to this decision — but the "
                    "identification leg is self-reported, so an option that crosses a red line and "
                    "does not say so is priced. A net, not a proof."
                ),
                "constraint_set": self.constraint_set,
                "considered": list(self.considered),
                "removed": [dict(entry) for entry in self.removed],
                "admitted": [option.id for option in self.options],
            },
            "calibration": pert.procedure(),
            "sampler": pert.sampler(seed, draws, "perspective and option, never draw order"),
            "priced": [
                {
                    "option": option.id,
                    "name": option.name,
                    "addresses": option.addresses,
                    "cost": option.cost.moments(),
                    "sampled": _sample(option, seed, draws),
                }
                for option in self.options
            ],
            "not_a_ranking": (
                "these are costs, in the order the options were authored. Nothing here marks one "
                "cheapest and nothing recommends one — the reader draws the trade-off, never the "
                "artefact"
            ),
        }
        refuse_undeclared_keys(body)
        refuse_priced_removals(body)
        return body


def _sample(option: Option, seed: str, draws: int) -> dict[str, Any]:
    stream = pert.stream(f"{seed}:{option.id}")
    return pert.summarise([option.cost.sample(stream) for _ in range(draws)])


def prefilter(perspective: dict[str, Any], responses: dict[str, dict[str, Any]]) -> Admitted:
    """Remove what the constraint set forbids, before anything is priced.

    Reads `constraints.resolve` and nothing else: this function holds no list of its own, so what
    it removes is exactly what was published.

    It never looks at a cost. That is why no input magnitude can make an excluded option reappear —
    the magnitude is not an input to this decision.
    """
    resolved = constraints.resolve(perspective)
    in_force = {str(entry["id"]): entry for entry in resolved["constraints"]}

    survivors: list[Option] = []
    removed: list[dict[str, str]] = []
    considered: list[str] = []
    for ident, doc in sorted(responses.items()):
        option = Option.of(doc)
        considered.append(ident)
        crossed = sorted(set(option.crosses) & set(in_force))
        if not crossed:
            survivors.append(option)
            continue
        for constraint_id in crossed:
            entry = in_force[constraint_id]
            # Strings only. There is no cost in this record, and the body-key closure above means
            # there is nowhere to put one.
            removed.append(
                {
                    "option": option.id,
                    "name": option.name,
                    "addresses": option.addresses,
                    "constraint": constraint_id,
                    "class": str(entry["class"]),
                    "tier": str(entry["tier"]),
                    "forbids": str(entry["forbids"]),
                    "because": option.crosses[constraint_id],
                    # Named rather than implied: ruin is perspective-relative, so an option removed
                    # here may legitimately survive under another eye.
                    "not_in_force_here": ", ".join(sorted(set(option.crosses) - set(in_force))) or "none",
                }
            )
    return Admitted(
        perspective=str(perspective["id"]),
        options=tuple(survivors),
        removed=tuple(removed),
        considered=tuple(considered),
        constraint_set=resolved,
        made_by=_FROM_THE_PREFILTER,
    )


def refuse_undeclared_keys(body: dict[str, Any]) -> None:
    """The priced-option body is closed. A key nobody declared does not serialise."""
    stray = sorted(set(walk_keys(body)) - BODY_KEYS)
    if stray:
        raise ArtefactError(
            f"a priced option set carries undeclared field(s) {', '.join(stray)}. This body is "
            "closed: adding a slot beside a removed option needs an authorising decision ticket."
        )


def refuse_priced_removals(body: dict[str, Any]) -> None:
    """A removed option carries no figure — not as a number, and not as a number in words.

    This is `ruin_class_absent_not_priced` at the point of emission. An excluded option absent from
    `priced` but carrying a figure in its removal record would be a price by another name, and the
    comparison it enables is the whole thing the pre-filter exists to prevent.

    Both halves matter. The **key closure** is the guarantee: `REMOVAL_KEYS` holds no price-shaped
    name, so `"cost": "GBP 5,000,000"` has nowhere to go even as a string. The **type screen** is
    the belt: it catches a figure smuggled into a key that is legitimately there.
    """
    removed = body.get("prefilter", {}).get("removed", [])
    priced = {entry["option"] for entry in body.get("priced", [])}
    for record in removed:
        if record["option"] in priced:
            raise ArtefactError(
                f"option {record['option']!r} was removed by the pre-filter and is priced anyway. "
                "An excluded option is absent from the choice set, not present with a number."
            )
        stray = sorted(set(walk_keys(record)) - REMOVAL_KEYS)
        if stray:
            raise ArtefactError(
                f"the removal record for {record['option']!r} carries undeclared field(s) "
                f"{', '.join(stray)}. This record is closed to the nine fields the pre-filter "
                "writes, so an excluded option has nowhere to put a figure — in a number or in "
                "words — and adding a slot needs an authorising decision ticket."
            )
        numbers = [
            f"{key}={value}"
            for key, value in walk_values(record)
            if isinstance(value, (int, float)) and not isinstance(value, bool)
        ]
        if numbers:
            raise ArtefactError(
                f"the removal record for {record['option']!r} carries {', '.join(numbers)}. A "
                "removed option carries no figure: a number beside it is a price by another name."
            )
