"""The constraint pre-filter, running before pricing (build ticket 28).

A constraint is not a very large price, because a price can be outbid. The tests here are all
versions of one claim: an excluded option never reaches a number, and no magnitude changes that.
"""

from __future__ import annotations

import json

import pytest

from twin import constraints, options, verbs
from twin.artefact import ArtefactError
from twin.canon import walk_keys
from twin.constraints import ConstraintError
from twin.grades import Capabilities
from twin.model import ModelError, Overlay
from twin.repo import ModelRepo
from twin.schema import SchemaError, validate

ORG = "netflix"
OPERATOR = "the-operator"
COUNCIL = "the-staff-council"
FLOOR_OPTION = "instrument-viewers-without-telling-them"
RUIN_OPTION = "stake-the-quarter-on-one-title"
SURVIVOR = "expand-the-delivery-network"


@pytest.fixture()
def overlay(repo: ModelRepo) -> Overlay:
    return Overlay.load(repo, ORG)


def _priced(overlay: Overlay, perspective_id: str = OPERATOR) -> dict:
    return options.prefilter(overlay.perspectives[perspective_id], overlay.responses).priced()


def test_an_excluded_option_is_absent_from_the_priced_set(overlay: Overlay) -> None:
    body = _priced(overlay)
    priced = {entry["option"] for entry in body["priced"]}

    assert priced == {SURVIVOR}, "only the option that crosses nothing is priced"
    assert FLOOR_OPTION not in priced
    assert RUIN_OPTION not in priced


def test_a_removed_option_carries_no_figure_anywhere(overlay: Overlay) -> None:
    """Absent from the choice set, not present with a large number."""
    from twin.canon import walk_values

    for record in _priced(overlay)["prefilter"]["removed"]:
        numbers = [v for _, v in walk_values(record) if isinstance(v, (int, float)) and not isinstance(v, bool)]
        assert numbers == [], f"{record['option']} carries {numbers}"


@pytest.mark.parametrize(
    "cost",
    [
        {"min": 0, "mode": 0, "max": 0},
        {"min": 1, "mode": 1, "max": 1},
        {"min": 1e12, "mode": 1e15, "max": 1e18},
    ],
)
def test_no_input_magnitude_brings_an_excluded_option_back(overlay: Overlay, cost: dict) -> None:
    """The pre-filter never reads a cost, so a cost cannot change what it does."""
    nudged = {
        ident: ({**doc, "cost": cost} if ident == RUIN_OPTION else doc)
        for ident, doc in overlay.responses.items()
    }
    body = options.prefilter(overlay.perspectives[OPERATOR], nudged).priced()
    assert RUIN_OPTION not in {entry["option"] for entry in body["priced"]}


def test_the_universal_floor_removes_an_option_under_every_perspective(overlay: Overlay) -> None:
    for perspective_id in (OPERATOR, COUNCIL):
        priced = {entry["option"] for entry in _priced(overlay, perspective_id)["priced"]}
        assert FLOOR_OPTION not in priced, f"the floor is negotiable under {perspective_id}"


def test_ruin_is_perspective_relative_so_the_filter_is_a_filter(overlay: Overlay) -> None:
    """A pre-filter that removed everything would pass every refusal and be useless."""
    operator = {entry["option"] for entry in _priced(overlay, OPERATOR)["priced"]}
    council = {entry["option"] for entry in _priced(overlay, COUNCIL)["priced"]}

    assert RUIN_OPTION not in operator, "insolvency is the operator's declared boundary"
    assert RUIN_OPTION in council, "the staff council declares a different boundary, so it survives"
    assert SURVIVOR in operator and SURVIVOR in council


def test_the_prefilter_reads_the_published_constraint_set_and_holds_no_list(overlay: Overlay) -> None:
    """Both directions. A subset check alone can only catch an *invented* constraint.

    The failure this criterion actually names is the opposite one — the filter ignoring a
    published constraint — and a subset assertion is structurally blind to it.
    """
    body = _priced(overlay)
    in_force = {str(c["id"]) for c in body["prefilter"]["constraint_set"]["constraints"]}
    removed = {record["option"] for record in body["prefilter"]["removed"]}

    assert constraints.floor_ids() <= in_force
    filtered_on = {record["constraint"] for record in body["prefilter"]["removed"]}
    assert filtered_on <= in_force, "the filter removed on an id nobody published"

    # The converse: for every option considered, crossing an in-force constraint and being
    # removed are the same thing.
    for ident, doc in sorted(overlay.responses.items()):
        crosses_something = bool(set(doc.get("crosses") or {}) & in_force)
        assert crosses_something == (ident in removed), (
            f"{ident} crosses {sorted(set(doc.get('crosses') or {}) & in_force)} and "
            f"{'was not' if crosses_something else 'was'} removed"
        )


def test_pricing_cannot_be_reached_without_the_prefilter(overlay: Overlay) -> None:
    """Structural, not an ordering convention: there is nothing to call in the wrong order."""
    with pytest.raises(ConstraintError, match="without running the constraint pre-filter"):
        options.Admitted(
            perspective=OPERATOR, options=(), removed=(), considered=(), constraint_set={}
        )
    # An allow-list, not a name blacklist: a free function that prices an unfiltered option
    # reopens the ordering whatever it is called, and `tally` gives nothing away.
    import inspect

    public = {
        name
        for name, value in vars(options).items()
        if not name.startswith("_") and inspect.isfunction(value)
        and getattr(value, "__module__", "") == options.__name__
    }
    assert public == {"prefilter", "refuse_undeclared_keys", "refuse_priced_removals"}
    assert callable(options.Admitted.priced)


def test_an_option_crossing_two_red_lines_is_removed_once_per_line(overlay: Overlay) -> None:
    """Untested until now, and three layers count `removed` differently because of it."""
    doubled = {
        **overlay.responses,
        RUIN_OPTION: {
            **overlay.responses[RUIN_OPTION],
            "crosses": {
                "insolvency": "A real chance the organisation cannot meet its obligations.",
                "no-covert-sensing": "It only works if nobody is told it is running.",
            },
        },
    }
    body = options.prefilter(overlay.perspectives[OPERATOR], doubled).priced()
    records = [r for r in body["prefilter"]["removed"] if r["option"] == RUIN_OPTION]

    assert {r["constraint"] for r in records} == {"insolvency", "no-covert-sensing"}
    assert {r["tier"] for r in records} == {"perspective", "universal"}
    assert RUIN_OPTION not in {e["option"] for e in body["priced"]}
    # Every record, not just the first: a dict keyed by option id would hide the second one.
    for record in records:
        assert not set(walk_keys(record)) - options.REMOVAL_KEYS


def test_survivors_and_removals_partition_what_was_considered(overlay: Overlay) -> None:
    pre = _priced(overlay)["prefilter"]
    considered = set(pre["considered"])
    survived = set(pre["admitted"])
    excluded = {record["option"] for record in pre["removed"]}

    assert survived | excluded == considered
    assert not survived & excluded


def test_a_removal_record_has_no_slot_for_a_figure_even_in_words(overlay: Overlay) -> None:
    """The key closure is the guarantee; the type screen is the belt.

    A whole-body key set cannot make this claim, because the priced half legitimately needs
    `cost` and `mean`. So the removal record is closed separately, and a figure written as a
    string has nowhere to go either.
    """
    assert not options.REMOVAL_KEYS & {"cost", "mean", "min", "max", "price", "amount"}

    body = _priced(overlay)
    body["prefilter"]["removed"][0]["cost"] = "GBP 5,000,000"
    with pytest.raises(ArtefactError, match="undeclared field"):
        options.refuse_priced_removals(body)


def test_a_number_in_a_declared_field_of_a_removal_record_is_refused(overlay: Overlay) -> None:
    body = _priced(overlay)
    body["prefilter"]["removed"][0]["because"] = 5000000
    with pytest.raises(ArtefactError, match="carries because=5000000"):
        options.refuse_priced_removals(body)


def test_a_copy_of_an_admitted_set_cannot_price_an_excluded_option(overlay: Overlay) -> None:
    """`dataclasses.replace` carries the construction sentinel through. The partition does not.

    This is the bypass the sentinel alone did not stop: deriving a frozen dataclass with
    `replace()` is the ordinary refactor, and it rebuilt an `Admitted` around any option list at
    all. Re-deriving the partition inside `priced()` is what actually holds.
    """
    import dataclasses

    admitted = options.prefilter(overlay.perspectives[OPERATOR], overlay.responses)
    banned = options.Option.of(overlay.responses[RUIN_OPTION])

    # The decision is recomputed from the constraint set the object carries, so a copy cannot
    # carry a wrong answer past it — the answer is not what is checked, the inputs are.
    forged = dataclasses.replace(admitted, options=(banned,), removed=(), considered=(RUIN_OPTION,))
    with pytest.raises(ConstraintError, match="crossing a constraint in force"):
        forged.priced()

    both = dataclasses.replace(admitted, options=admitted.options + (banned,))
    with pytest.raises(ConstraintError, match="crossing a constraint in force"):
        both.priced()

    # And the partition itself: a removal record quietly dropped is also refused.
    thinned = dataclasses.replace(admitted, removed=admitted.removed[:1])
    with pytest.raises(ConstraintError, match="does not account for what it considered"):
        thinned.priced()


def test_the_priced_body_is_closed(overlay: Overlay) -> None:
    with pytest.raises(ArtefactError, match="undeclared field"):
        options.refuse_undeclared_keys({**_priced(overlay), "cheapest": SURVIVOR})


def test_a_response_naming_a_red_line_nobody_declared_is_refused(scratch_repo) -> None:
    """A `crosses` id that matches nothing would silently never filter."""
    from twin import fixtures

    path = scratch_repo / "orgs" / "netflix" / "responses" / "expand-the-delivery-network.yaml"
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "note: >-", "crosses:\n  no-such-red-line: A constraint nobody declared.\nnote: >-"
        ),
        encoding="utf-8",
    )
    fixtures.git(scratch_repo, "add", "-A")
    fixtures.git(scratch_repo, "commit", "-q", "-m", "cross a constraint nobody declared")

    with pytest.raises(ModelError, match="no universal constraint and no perspective"):
        Overlay.load(ModelRepo.open(scratch_repo), ORG)


def test_a_cost_triple_is_a_triple_and_is_ordered() -> None:
    base = {"id": "probe", "name": "Probe", "addresses": "a-component"}
    validate("response", {**base, "cost": {"min": 1, "mode": 2, "max": 3}}, "probe")
    with pytest.raises(SchemaError, match="min <= mode <= max"):
        validate("response", {**base, "cost": {"min": 3, "mode": 2, "max": 1}}, "probe")
    with pytest.raises(SchemaError, match="missing max"):
        validate("response", {**base, "cost": {"min": 1, "mode": 2}}, "probe")
    with pytest.raises(SchemaError, match="non-negative"):
        validate("response", {**base, "cost": {"min": -1, "mode": 2, "max": 3}}, "probe")


def test_the_emitted_choice_set_is_derived_and_depth_graded(repo: ModelRepo, caps: Capabilities) -> None:
    artefact = verbs.options(
        repo, caps, ORG, OPERATOR, verbs.command_for("options", org=ORG, perspective=OPERATOR)
    )
    doc = json.loads(artefact.to_bytes())
    assert doc["envelope"]["mark"] == "derived"
    assert doc["envelope"]["depth"]["capabilities"]
    assert doc["body"]["prefilter"]["ran_before_pricing"] is True
