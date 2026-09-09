"""The admission rule for `bus-factor-key-person` (eco-system ticket 31).

NOTHING IN THIS FILE NAMES A PERSON, real or invented. Every role is a role id out of an
adopter's own people register; every planted identifier is a KEY NAME, a FIELD NAME or a value on
the RFC 2606 reserved domain `example.invalid`. The review of 2026-09-09 demonstrated the F1 hole
with plants like `maintained_by: <a full name>`; every one of those plants is reproduced here
through its KEY alone, because after the fix it is the undeclared KEY that refuses the record and
the value is never reached. So the hole is closed and no name is written down.
"""

from __future__ import annotations

import copy
from typing import Any

import pytest

from twin import sensor_admission as sa

PEOPLE = ("platform-engineer", "data-protection-lead")

DPIA_TEXT = """
schema: twin.dpia/v1
sensor: bus-factor-structural-aggregate
scenario: key-person-2026
completed_on: '2026-09-09'
completed_by: data-protection-lead
retention_days: 90
lawful_basis: legitimate interests in the continuity of a service the organisation is accountable for
what_is_sensed: the number of distinct committers to a component in a window, per component
what_is_not_sensed: any individual, any message, any keystroke, any name, any identifier
"""

DPIA_PATH = "twin/orgs/driftwood/dpia/bus-factor-structural-aggregate.yaml"


def reader(text: str | None = DPIA_TEXT, at: str = DPIA_PATH) -> Any:
    def read(path: str) -> str | None:
        return text if path == at else None
    return read


def record(**over: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "schema": "twin.sensor-admission-record/v1",
        "sensor": "bus-factor-structural-aggregate",
        "scenario": "key-person-2026",
        "scenario_class": "bus-factor-key-person",
        "senses_role": "platform-engineer",
        "kind": "structural",
        "granularity": "aggregate",
        "fields": ["component", "distinct_committer_count", "window_days"],
        "notice": {
            "told": ["platform-engineer", "data-protection-lead"],
            "published_at": "docs/monitoring-notice.md",
            "published_on": "2026-09-09",
        },
        "dpia": {"record": DPIA_PATH},
        "ladder": {
            "purpose": {"scenario": "key-person-2026", "will_act": True},
            "necessity": {
                "kind": "structural",
                "level": "aggregate",
                "alternatives": [{"kind": "behavioural", "level": "individual"}],
            },
            "proportionality": {"intrusion_cost": 500.0, "value_illuminated": 50000.0},
            "dpia": {"channels": [], "profiling": False, "financial_loss_risk": False,
                     "complete": True},
        },
    }
    out = copy.deepcopy(base)
    out.update(copy.deepcopy(over))
    return out


def grade(rec: dict[str, Any], **kw: Any) -> dict[str, Any]:
    kw.setdefault("people", PEOPLE)
    kw.setdefault("scenarios", ("key-person-2026",))
    kw.setdefault("dpia_reader", reader())
    return sa.grade_record(rec, **kw)


def ids(result: dict[str, Any]) -> list[str]:
    return [r.split(":")[0].removeprefix("REFUSED ").strip() for r in result["refusals"]]


# -- the rule table itself -----------------------------------------------------------------------

def test_the_rule_table_loads_and_is_closed() -> None:
    rule = sa.load_rule()
    assert rule["scenario_class"] == "bus-factor-key-person"
    assert sa.admissible_pairs(rule) == (("structural", "aggregate"),)


def test_the_rule_table_is_refused_when_it_is_not_the_declared_schema(tmp_path) -> None:
    bad = tmp_path / "rule.yaml"
    bad.write_text("schema: something/else\nversion: 1\n", encoding="utf-8")
    with pytest.raises(sa.SensorAdmissionError):
        sa.load_rule(bad)


# -- green: the one admissible sensor -------------------------------------------------------------

def test_the_structural_aggregate_bus_factor_sensor_is_admitted() -> None:
    result = grade(record())
    assert result["refusals"] == []
    assert result["admitted"] is True


# -- (a) a sensor that names or identifies an individual ------------------------------------------

@pytest.mark.parametrize("field", [
    "employee_id", "work_email", "full_name", "person_handle", "free_text_note", "user",
])
def test_a_sensor_reading_a_field_that_identifies_an_individual_is_refused(field: str) -> None:
    result = grade(record(fields=["component", field]))
    assert "names-or-identifies-an-individual" in ids(result), (
        f"a sensor reading {field!r} must be refused by name, got {result['refusals']}"
    )
    assert result["admitted"] is False


def test_a_record_that_identifies_an_individual_is_refused_before_its_ladder_is_walked() -> None:
    result = grade(record(fields=["component", "employee_id"]))
    assert result["terminal"] is True
    assert result["ladder"] is None, (
        "a record naming an individual must never be priced: computing its proportionality "
        f"puts a price on sensing a named person, got {result['ladder']}"
    )
    assert len(result["refusals"]) == 1


def test_an_individual_shaped_value_anywhere_in_the_record_is_refused() -> None:
    result = grade(record(senses_role="platform-engineer",
                          notice={"told": ["someone@example.invalid"],
                                  "published_at": "docs/monitoring-notice.md",
                                  "published_on": "2026-09-09"}))
    assert "names-or-identifies-an-individual" in ids(result)


# -- (b) a sensor admitted without a DPIA record --------------------------------------------------

def test_a_sensor_with_no_dpia_record_at_the_path_it_names_is_refused() -> None:
    result = grade(record(), dpia_reader=reader(text=None))
    assert "no-dpia-record" in ids(result), (
        f"a sensor with no DPIA record must be refused by name, got {result['refusals']}")
    assert result["admitted"] is False


def test_a_dpia_record_missing_its_retention_period_is_not_a_dpia_record() -> None:
    text = DPIA_TEXT.replace("retention_days: 90\n", "")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "no-dpia-record" in ids(result), (
        f"a DPIA record with no retention period must be refused by name, got {result['refusals']}")
    assert "retention_days" in " ".join(result["refusals"])


def test_a_dpia_record_naming_no_date_is_not_a_dpia_record() -> None:
    text = DPIA_TEXT.replace("completed_on: '2026-09-09'\n", "")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "no-dpia-record" in ids(result), (
        f"a DPIA record with no date must be refused by name, got {result['refusals']}")


def test_the_admission_record_naming_no_dpia_path_at_all_is_refused() -> None:
    result = grade(record(dpia={}))
    assert "no-dpia-record" in ids(result), (
        f"a record naming no DPIA path must be refused by name, got {result['refusals']}")


# -- (c) a sensor whose kind is not in the admissible list ----------------------------------------

@pytest.mark.parametrize("kind,gran", [
    ("behavioural", "aggregate"),
    ("structural", "cohort"),
    ("structural", "individual"),
    ("behavioural", "individual"),
])
def test_a_kind_or_granularity_outside_the_admissible_set_is_refused(kind: str, gran: str) -> None:
    result = grade(record(kind=kind, granularity=gran,
                          ladder={**record()["ladder"],
                                  "necessity": {"kind": kind, "level": gran, "alternatives": []}}))
    assert "kind-not-admissible" in ids(result), (
        f"{kind}/{gran} is not in the admissible set and must be refused by name, got "
        f"{result['refusals']}")
    assert result["admitted"] is False


def test_a_record_whose_ladder_walks_a_different_pair_than_it_declares_is_refused() -> None:
    ladder = copy.deepcopy(record()["ladder"])
    ladder["necessity"] = {"kind": "behavioural", "level": "individual", "alternatives": []}
    result = grade(record(ladder=ladder))
    assert "kind-not-admissible" in ids(result), (
        f"a record declaring structural/aggregate whose ladder walks behavioural/individual must "
        f"be refused by name, got {result['refusals']}")
    assert "is not what runs" in " ".join(result["refusals"])


def test_a_field_outside_the_closed_admissible_set_is_refused() -> None:
    result = grade(record(fields=["component", "lines_of_code"]))
    assert "field-not-admissible" in ids(result), (
        f"a field outside the closed set must be refused by name, got {result['refusals']}")
    assert result["admitted"] is False


# -- (d) covert sensing ---------------------------------------------------------------------------

def test_a_sensor_the_sensed_party_is_not_told_about_is_refused() -> None:
    result = grade(record(notice={}))
    assert "covert-sensing" in ids(result), (
        f"a sensor the sensed party is not told about must be refused by name, got "
        f"{result['refusals']}")
    assert result["admitted"] is False


def test_a_notice_with_no_publication_date_has_told_nobody() -> None:
    result = grade(record(notice={"told": ["platform-engineer"],
                                  "published_at": "docs/monitoring-notice.md"}))
    assert "covert-sensing" in ids(result), (
        f"a notice with no publication date must be refused by name, got {result['refusals']}")
    assert "published_on" in " ".join(result["refusals"])


def test_the_covert_refusal_cites_the_rule_that_refuses_it() -> None:
    result = grade(record(notice={}))
    line = [r for r in result["refusals"] if "covert-sensing" in r][0]
    assert "NORTH-STAR section 6" in line


# -- (e) a role with no entry in the roles register -----------------------------------------------

def test_a_sensed_role_absent_from_the_people_register_is_refused() -> None:
    result = grade(record(senses_role="unregistered-role"))
    assert "role-not-registered" in ids(result), (
        f"a sensed role absent from the people register must be refused by name, got "
        f"{result['refusals']}")
    assert result["admitted"] is False


def test_a_dpia_signed_off_by_a_role_absent_from_the_people_register_is_refused() -> None:
    text = DPIA_TEXT.replace("completed_by: data-protection-lead",
                             "completed_by: unregistered-role")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "role-not-registered" in ids(result), (
        f"a DPIA signed off by an unregistered role must be refused by name, got "
        f"{result['refusals']}")



# -- F1: the record's KEY set is closed ----------------------------------------------------------
# Every plant below is one the 2026-09-09 review measured as ADMITTED with a green PASS before
# the key set was closed. Each is reproduced by its key alone; no value here is a name.

@pytest.mark.parametrize("key", [
    "maintained_by", "escalation_contact", "github", "owner", "stakeholders", "context",
    "reviewed_by", "held_by",
])
def test_a_top_level_key_the_table_does_not_declare_is_refused(key: str) -> None:
    result = grade(record(**{key: "<a value this test never reads>"}))
    assert "key-not-declared" in ids(result), (
        f"an undeclared key {key!r} must be refused by name, got {result['refusals']}")
    assert result["terminal"] is True
    assert result["ladder"] is None
    assert result["admitted"] is False


@pytest.mark.parametrize("key", ["\u0435mployee_id", "e\u200bmployee_id", "employe\u0435"])
def test_a_homoglyph_or_zero_width_key_is_refused_by_the_closed_set(key: str) -> None:
    """The name scanner splits on [^a-z0-9]+, so a Cyrillic e or a zero-width space evades it.
    A closed key set does not care: the key is simply not one the table declares."""
    assert sa.identifier_in_name(key) is None, "this plant only tests the closed set"
    result = grade(record(**{key: 1}))
    assert "key-not-declared" in ids(result), (
        f"a homoglyph key {key!r} must be refused by the closed set, got {result['refusals']}")


def test_an_undeclared_key_inside_the_notice_is_refused() -> None:
    result = grade(record(notice={"told": ["platform-engineer"], "published_at": "docs/n.md",
                                  "published_on": "2026-09-09", "contact": "x"}))
    assert "key-not-declared" in ids(result), (
        f"an undeclared key inside the notice must be refused, got {result['refusals']}")
    assert "notice.contact" in " ".join(result["refusals"])


def test_an_undeclared_key_inside_the_ladder_is_refused() -> None:
    ladder = copy.deepcopy(record()["ladder"])
    ladder["purpose"]["raised_by"] = "x"
    result = grade(record(ladder=ladder))
    assert "key-not-declared" in ids(result), (
        f"an undeclared key inside the ladder must be refused, got {result['refusals']}")
    assert "ladder.purpose.raised_by" in " ".join(result["refusals"])


def test_an_undeclared_key_inside_the_dpia_record_is_refused() -> None:
    text = DPIA_TEXT + "reviewed_by: <a value this test never reads>\n"
    result = grade(record(), dpia_reader=reader(text=text))
    assert "key-not-declared" in ids(result), (
        f"an undeclared key in the DPIA record must be refused, got {result['refusals']}")
    assert result["terminal"] is True


def test_the_notice_must_name_the_roles_told_as_role_ids_not_prose() -> None:
    """After G1 the document closure reaches this first and refuses it TERMINALLY, which is
    stricter than the covert-sensing refusal that used to catch it: prose in a slot the table
    declares as a list of role ids is where a name arrives."""
    result = grade(record(notice={"told": "the whole team was told in person",
                                  "published_at": "docs/n.md", "published_on": "2026-09-09"}))
    assert "key-not-declared" in ids(result), (
        f"a prose notice must be refused by name, got {result['refusals']}")
    assert "notice.told" in " ".join(result["refusals"])
    assert result["terminal"] is True and result["ladder"] is None


def test_an_empty_told_list_is_still_covert_sensing() -> None:
    result = grade(record(notice={"told": [], "published_at": "docs/n.md",
                                  "published_on": "2026-09-09"}))
    assert "covert-sensing" in ids(result), (
        f"a notice telling nobody must be refused by name, got {result['refusals']}")
    assert "role ids" in " ".join(result["refusals"])


def test_a_notice_naming_a_role_the_register_does_not_carry_is_refused() -> None:
    result = grade(record(notice={"told": ["platform-engineer", "unregistered-role"],
                                  "published_at": "docs/n.md", "published_on": "2026-09-09"}))
    assert "role-not-registered" in ids(result), (
        f"a notice naming an unregistered role must be refused, got {result['refusals']}")


def test_a_dpia_filed_under_a_basename_that_is_not_the_sensor_id_is_refused() -> None:
    path = "twin/orgs/driftwood/dpia/whoever-signed-it.yaml"
    result = grade(record(dpia={"record": path}), dpia_reader=reader(at=path))
    assert "no-dpia-record" in ids(result), (
        f"a DPIA filed under a name that is not the sensor id must be refused, got "
        f"{result['refusals']}")
    assert "basename" in " ".join(result["refusals"])


# -- F5: the record is graded by the table that rules its own class ------------------------------

def test_a_record_declaring_another_scenario_class_is_refused() -> None:
    result = grade(record(scenario_class="support-ticket-volume"))
    assert "not-this-scenario-class" in ids(result), (
        f"a record of another class must be refused by name, got {result['refusals']}")
    assert result["scenario_class"] == "support-ticket-volume", (
        "the result must report the class the RECORD declared, never stamp the table's on it")


def test_a_record_naming_a_scenario_this_adopter_does_not_serve_is_refused() -> None:
    result = grade(record(scenario="not-a-served-scenario",
                          ladder={**copy.deepcopy(record()["ladder"]),
                                  "purpose": {"scenario": "not-a-served-scenario",
                                              "will_act": True}}))
    assert "scenario-not-served" in ids(result), (
        f"a scenario the adopter does not serve must be refused by name, got "
        f"{result['refusals']}")


def test_the_ladders_purpose_scenario_must_be_the_one_the_record_names() -> None:
    ladder = copy.deepcopy(record()["ladder"])
    ladder["purpose"] = {"scenario": "eol-date-passes-2026", "will_act": True}
    result = grade(record(ladder=ladder))
    assert "scenario-not-served" in ids(result), result["refusals"]
    assert "is not what runs" in " ".join(result["refusals"])


# -- F3: every declared refusal carries a usable sentence ----------------------------------------

def test_a_refusal_row_with_no_sentence_is_refused_at_load(tmp_path) -> None:
    import yaml
    doc = yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))
    doc["refusals"][0].pop("sentence")
    bad = tmp_path / "no-sentence.yaml"
    bad.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(sa.SensorAdmissionError, match="sentence"):
        sa.load_rule(bad)


def test_a_refusal_row_with_a_blank_sentence_is_refused_at_load(tmp_path) -> None:
    import yaml
    doc = yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))
    doc["refusals"][0]["sentence"] = "   "
    bad = tmp_path / "blank-sentence.yaml"
    bad.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(sa.SensorAdmissionError, match="sentence"):
        sa.load_rule(bad)


def test_a_refusal_sentence_that_names_no_placeholder_is_refused_at_load(tmp_path) -> None:
    import yaml
    doc = yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))
    rid = doc["refusals"][0]["id"]
    doc["refusals"][0]["sentence"] = f"REFUSED {rid}: something went wrong."
    bad = tmp_path / "no-placeholder.yaml"
    bad.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(sa.SensorAdmissionError, match="sensor|what"):
        sa.load_rule(bad)


def test_a_refusal_sentence_that_does_not_open_with_its_own_id_is_refused_at_load(tmp_path) -> None:
    import yaml
    doc = yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))
    doc["refusals"][0]["sentence"] = "{sensor} was refused because of {what}."
    bad = tmp_path / "bad-opening.yaml"
    bad.write_text(yaml.safe_dump(doc), encoding="utf-8")
    with pytest.raises(sa.SensorAdmissionError, match="REFUSED"):
        sa.load_rule(bad)


# -- F4: terminality is read from the table, not hardcoded ---------------------------------------

def test_terminality_is_read_from_the_table_at_the_branch(tmp_path) -> None:
    """`is_terminal()` was defined and never called: `terminal: true` in the table was
    decorative. It is now the branch condition, so a table that says a refusal is not terminal
    reports it beside the others instead of alone."""
    import yaml
    doc = yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))
    for row in doc["refusals"]:
        if row["id"] == "names-or-identifies-an-individual":
            row["terminal"] = False
    loosened = tmp_path / "loosened.yaml"
    loosened.write_text(yaml.safe_dump(doc), encoding="utf-8")
    rule = sa.load_rule(loosened)
    result = grade(record(fields=["component", "employee_id"]), rule=rule)
    assert result["terminal"] is False
    assert result["ladder"] is not None, "the module must have read the table, not its own mind"
    assert "names-or-identifies-an-individual" in ids(result)
    # and the shipped table still says terminal
    assert sa.is_terminal(sa.load_rule(), "names-or-identifies-an-individual") is True


def test_the_terminal_sentence_says_nothing_else_was_evaluated() -> None:
    result = grade(record(fields=["component", "employee_id"]))
    assert result["refusals"][-1].endswith("No refusal beyond these was evaluated.")


# -- F2: the people register, widened -------------------------------------------------------------

def test_a_role_file_with_a_key_the_table_does_not_declare_is_a_problem() -> None:
    problems = sa.people_file_problems("platform-engineer.yaml",
                                       {"id": "platform-engineer", "role": "On call.",
                                        "held_by": "<a value this test never reads>"},
                                       sa.load_rule())
    assert any("held_by" in p for p in problems), problems


def test_a_role_file_whose_id_or_filename_is_identifier_shaped_is_a_problem() -> None:
    by_id = sa.people_file_problems("user-account.yaml",
                                    {"id": "user-account", "role": "On call."}, sa.load_rule())
    assert any("user" in p for p in by_id), by_id
    by_name = sa.people_file_problems("employee-of-the-month.yaml",
                                      {"id": "on-call", "role": "On call."}, sa.load_rule())
    assert any("employee" in p for p in by_name), by_name


def test_a_clean_role_file_has_no_problem() -> None:
    assert sa.people_file_problems(
        "platform-engineer.yaml",
        {"id": "platform-engineer", "role": "On call for the checkout namespace."},
        sa.load_rule()) == []



# -- G1: the DOCUMENT is closed, not eleven enumerated paths --------------------------------------
# The enumerated walk visited exactly eleven positions, so a mapping sitting under a DECLARED key
# that has no closed set of its own was never reached. Both plants below were measured by the
# 2026-09-09 re-check at a real served ref as `exit 0, 1 admitted, 0 refused`.

def test_a_mapping_under_a_declared_scalar_key_is_refused() -> None:
    result = grade(record(notice={"told": ["platform-engineer"],
                                  "published_at": {"holder": "<a value this test never reads>"},
                                  "published_on": "2026-09-09"}))
    assert "key-not-declared" in ids(result), (
        "a mapping under notice.published_at must be refused by name, got "
        f"{result['refusals']}")
    assert "notice.published_at" in " ".join(result["refusals"])
    assert result["terminal"] is True
    assert result["ladder"] is None
    assert result["admitted"] is False


def test_a_prose_value_in_a_boolean_slot_is_refused() -> None:
    """`will_act` is a boolean the ladder only tests for truthiness, so any non-empty string
    passed `_check_purpose` — a boolean slot accepting arbitrary prose."""
    ladder = copy.deepcopy(record()["ladder"])
    ladder["purpose"]["will_act"] = "agreed with the on-call rota"
    result = grade(record(ladder=ladder))
    assert "value-not-the-declared-shape" in ids(result), (
        "prose in the boolean ladder.purpose.will_act must be refused by name, got "
        f"{result['refusals']}")
    assert "ladder.purpose.will_act" in " ".join(result["refusals"])
    assert result["terminal"] is True
    assert result["ladder"] is None


@pytest.mark.parametrize("where,value", [
    ("schema", {"a": 1}),
    ("sensor", {"a": 1}),
    ("kind", {"a": 1}),
    ("granularity", ["structural"]),
    ("senses_role", {"a": 1}),
])
def test_a_mapping_or_list_under_any_other_declared_scalar_key_is_refused(where, value) -> None:
    result = grade(record(**{where: value}))
    assert "key-not-declared" in ids(result), (
        f"a non-scalar under the declared key {where!r} must be refused by name, got "
        f"{result['refusals']}")


def test_a_mapping_inside_a_declared_scalar_list_is_refused() -> None:
    result = grade(record(fields=["component", {"holder": "x"}]))
    assert "key-not-declared" in ids(result), result["refusals"]
    assert "fields[1]" in " ".join(result["refusals"])


def test_a_deeply_nested_mapping_under_a_declared_scalar_key_is_refused() -> None:
    ladder = copy.deepcopy(record()["ladder"])
    ladder["necessity"]["alternatives"][0]["level"] = {"holder": "x"}
    result = grade(record(ladder=ladder))
    assert "key-not-declared" in ids(result), result["refusals"]
    assert "ladder.necessity.alternatives[0].level" in " ".join(result["refusals"])


def test_a_mapping_under_a_declared_scalar_key_of_the_dpia_record_is_refused() -> None:
    text = DPIA_TEXT.replace("completed_by: data-protection-lead",
                             "completed_by: {holder: <never read>}")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "key-not-declared" in ids(result), result["refusals"]
    assert "completed_by" in " ".join(result["refusals"])


# -- G2: a type-confused record is refused, never a crash -----------------------------------------

@pytest.mark.parametrize("value", [["twin/orgs/x/dpia/y.yaml"], "a string", 7, None])
def test_a_type_confused_dpia_block_is_refused_and_never_raises(value) -> None:
    result = grade(record(dpia=value))
    assert result["admitted"] is False
    assert result["refusals"], "a type-confused dpia block must produce a refusal, not a crash"


@pytest.mark.parametrize("key", ["notice", "ladder"])
def test_a_type_confused_mapping_key_is_refused_and_never_raises(key) -> None:
    result = grade(record(**{key: ["not", "a", "mapping"]}))
    assert result["admitted"] is False
    assert result["refusals"]


def test_a_record_that_is_not_a_mapping_at_all_is_refused_and_never_raises() -> None:
    result = grade(["not", "a", "record"])  # type: ignore[arg-type]
    assert result["admitted"] is False
    assert result["refusals"]


# -- G3: the clause is printed once, on the last terminal line ------------------------------------

def test_the_terminal_clause_is_printed_once_at_the_end_of_the_batch() -> None:
    result = grade(record(fields=["component", "employee_id"], owner="x", github="y"))
    joined = " ".join(result["refusals"])
    assert joined.count("No refusal beyond these was evaluated") == 1
    assert result["refusals"][-1].endswith("No refusal beyond these was evaluated.")
    assert len(result["refusals"]) >= 3



# -- R1: the closure closes the SERVED BYTES, not the parsed dict ---------------------------------
# `yaml.safe_load` silently discards a repeated mapping key, last one wins. The re-check's plant
# carried a name AND an email past every rule to a green PASS on a real served ref, because the
# parser threw the first line away before `identifier_in_value` — whose whole job is that email
# shape — ever saw it. The plant is reproduced here with the identifier shapes and no name.

DUPLICATED_SENSES_ROLE = """schema: twin.sensor-admission-record/v1
sensor: bus-factor-structural-aggregate
senses_role: someone@example.invalid
senses_role: platform-engineer
"""


def test_the_plain_parser_hides_the_duplicate_this_check_must_refuse() -> None:
    """The premise, asserted rather than assumed: `safe_load` returns a clean document, so a
    closure over the PARSED dict cannot see the line the served bytes carry."""
    import yaml
    parsed = yaml.safe_load(DUPLICATED_SENSES_ROLE)
    assert parsed["senses_role"] == "platform-engineer"
    assert sa.individual_problems(parsed) == []


def test_a_duplicate_key_in_served_bytes_is_refused() -> None:
    problems = sa.load_served("twin/orgs/x/sensor-admissions/y.yaml", DUPLICATED_SENSES_ROLE)
    assert isinstance(problems, sa.Unreadable), (
        f"served bytes with a duplicated key must be unreadable, got {problems!r}")
    assert "duplicate key" in problems.why, problems.why
    assert "senses_role" in problems.why, problems.why


def test_the_bytes_are_what_was_graded_not_the_parsed_dict() -> None:
    """Closing the loop the re-check asked for: the same bytes that `safe_load` reads as clean
    are refused, and the refusal names the key the parser discarded."""
    import yaml
    assert isinstance(yaml.safe_load(DUPLICATED_SENSES_ROLE), dict)
    result = sa.load_served("p.yaml", DUPLICATED_SENSES_ROLE)
    assert isinstance(result, sa.Unreadable) and "senses_role" in result.why


def test_a_duplicated_notice_block_is_refused() -> None:
    body = ("schema: twin.sensor-admission-record/v1\n"
            "notice:\n  holder: someone@example.invalid\n"
            "notice:\n  told: [platform-engineer]\n")
    result = sa.load_served("p.yaml", body)
    assert isinstance(result, sa.Unreadable) and "notice" in result.why


def test_a_readable_document_comes_back_as_itself() -> None:
    assert sa.load_served("p.yaml", "a: 1\n") == {"a": 1}


def test_unparseable_served_bytes_are_unreadable_not_a_crash() -> None:
    assert isinstance(sa.load_served("p.yaml", "a: [1, 2\n"), sa.Unreadable)


def test_served_bytes_that_blow_the_parser_stack_are_unreadable_not_a_crash() -> None:
    """R4: `admission_records()` caught only `yaml.YAMLError`, so a deeply nested document's
    `RecursionError` propagated out of the reader and aborted the whole estate run."""
    deep = "fields: " + "[" * 500 + "]" * 500 + "\n"
    assert isinstance(sa.load_served("p.yaml", deep), sa.Unreadable)


# -- R2: the declarations added in the last commit are validated ----------------------------------

def _rule_doc():
    import yaml
    return yaml.safe_load(sa.RULE_PATH.read_text(encoding="utf-8"))


def _write(tmp_path, doc, name="rule.yaml"):
    import yaml
    path = tmp_path / name
    path.write_text(yaml.safe_dump(doc), encoding="utf-8")
    return path


def test_a_typed_keys_type_name_the_module_does_not_know_is_refused_at_load(tmp_path) -> None:
    """The re-check's own plant: `bool` mistyped as `boolean` loaded clean and made the check a
    silent no-op, because the recursion computes `wrong` as a disjunction over known names."""
    doc = _rule_doc()
    doc["typed_keys"]["ladder_purpose"]["will_act"] = "boolean"
    with pytest.raises(sa.SensorAdmissionError, match="boolean"):
        sa.load_rule(_write(tmp_path, doc))


def test_a_typed_keys_set_that_closed_keys_does_not_declare_is_refused_at_load(tmp_path) -> None:
    doc = _rule_doc()
    doc["typed_keys"]["no_such_set"] = {"a": "bool"}
    with pytest.raises(sa.SensorAdmissionError, match="no_such_set"):
        sa.load_rule(_write(tmp_path, doc))


def test_a_typed_keys_key_its_own_set_does_not_declare_is_refused_at_load(tmp_path) -> None:
    doc = _rule_doc()
    doc["typed_keys"]["ladder_purpose"]["not_a_key"] = "bool"
    with pytest.raises(sa.SensorAdmissionError, match="not_a_key"):
        sa.load_rule(_write(tmp_path, doc))


def test_a_scalar_lists_set_or_key_the_table_does_not_declare_is_refused_at_load(tmp_path) -> None:
    doc = _rule_doc()
    doc["scalar_lists"]["no_such_set"] = ["a"]
    with pytest.raises(sa.SensorAdmissionError, match="no_such_set"):
        sa.load_rule(_write(tmp_path, doc))
    doc = _rule_doc()
    doc["scalar_lists"]["record"] = ["not_a_key"]
    with pytest.raises(sa.SensorAdmissionError, match="not_a_key"):
        sa.load_rule(_write(tmp_path, doc))


def test_the_typed_check_still_bites_after_the_guard(tmp_path) -> None:
    """The plant the mistyped name silenced, still refused with the table as shipped."""
    ladder = copy.deepcopy(record()["ladder"])
    ladder["purpose"]["will_act"] = "agreed with the on-call rota"
    assert "value-not-the-declared-shape" in ids(grade(record(ladder=ladder)))


# -- R5: a declared-but-null key set is refused, not merely a missing one --------------------------

def test_a_closed_key_set_declared_null_is_refused_at_load(tmp_path) -> None:
    """Membership is not usability: `child not in closed_keys` passed a null entry, which then
    raised an uncaught TypeError at grade time."""
    doc = _rule_doc()
    doc["closed_keys"]["notice"] = None
    with pytest.raises(sa.SensorAdmissionError, match="notice"):
        sa.load_rule(_write(tmp_path, doc))


def test_a_nested_map_pointing_at_a_null_key_set_is_refused_at_load(tmp_path) -> None:
    doc = _rule_doc()
    doc["closed_keys"]["spare_set"] = None
    doc["nested_maps"]["record"]["notice"] = "spare_set"
    with pytest.raises(sa.SensorAdmissionError, match="spare_set"):
        sa.load_rule(_write(tmp_path, doc))


# -- R3: a required key that is absent is refused, never indexed by the ladder --------------------

@pytest.mark.parametrize("mutate,missing", [
    (lambda l: l["necessity"]["alternatives"][0].pop("level"), "level"),
    (lambda l: l["necessity"].pop("kind"), "kind"),
    (lambda l: l["necessity"].clear(), "kind"),
    (lambda l: l["proportionality"].pop("intrusion_cost"), "intrusion_cost"),
])
def test_a_missing_required_ladder_key_is_refused_rather_than_indexed(mutate, missing) -> None:
    ladder = copy.deepcopy(record()["ladder"])
    mutate(ladder)
    result = grade(record(ladder=ladder))
    assert "required-key-missing" in ids(result), (
        f"a ladder rung with no {missing!r} must be refused by name rather than indexed with [], "
        f"got {result['refusals']}")
    assert missing in " ".join(result["refusals"])
    assert result["admitted"] is False


# -- R6: the callers do not double the wording ----------------------------------------------------

def test_the_people_file_problem_is_not_doubled() -> None:
    problems = sa.people_file_problems("p.yaml", {"id": {"a": 1}, "role": "x"}, sa.load_rule())
    assert problems and "the undeclared key the key" not in problems[0], problems


def test_the_dpia_key_problem_is_not_doubled() -> None:
    text = DPIA_TEXT.replace("schema: twin.dpia/v1", "schema: {a: 1}")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "the DPIA record's key the key" not in " ".join(result["refusals"]), result["refusals"]


# -- R7/R9: four of the five slots a plain-words name survived in are closed ----------------------

def test_a_record_whose_schema_is_not_the_declared_one_is_refused() -> None:
    result = grade(record(schema="something else"))
    assert "value-not-the-declared-shape" in ids(result), result["refusals"]


def test_a_dpia_naming_another_sensor_or_scenario_is_refused() -> None:
    text = DPIA_TEXT.replace("sensor: bus-factor-structural-aggregate", "sensor: payroll-record")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "value-not-the-declared-shape" in ids(result), result["refusals"]
    text = DPIA_TEXT.replace("scenario: key-person-2026", "scenario: something-else-2026")
    result = grade(record(), dpia_reader=reader(text=text))
    assert "value-not-the-declared-shape" in ids(result), result["refusals"]


def test_a_ladder_declaring_any_dpia_channel_is_refused() -> None:
    ladder = copy.deepcopy(record()["ladder"])
    ladder["dpia"]["channels"] = ["a channel this class never reads"]
    result = grade(record(ladder=ladder))
    assert "value-not-the-declared-shape" in ids(result), result["refusals"]


def test_the_limits_are_derived_from_the_table_and_name_both_new_refusals() -> None:
    text = " ".join(sa.limits(sa.load_rule()))
    for expected in ("value-not-the-declared-shape", "key-not-declared", "duplicate",
                     "lawful_basis", "published_at", "role id"):
        assert expected in text, f"the printed limits do not mention {expected!r}: {text}"


# -- the sensor table stays closed ----------------------------------------------------------------

def test_a_sensor_id_that_is_not_in_sensors_yaml_is_refused_rather_than_raising() -> None:
    result = grade(record(sensor="not-a-named-sensor"))
    assert "sensor-not-named" in ids(result), (
        f"a sensor id absent from sensors.yaml must be refused by name, got {result['refusals']}")
    assert result["admitted"] is False


def test_the_admissible_sensor_is_the_one_sensors_yaml_already_carries() -> None:
    from twin import ethics_gate
    assert "bus-factor-structural-aggregate" in ethics_gate.sensor_ids()


# -- nothing this rule admits can reach a person --------------------------------------------------

def test_every_admissible_field_is_a_count_or_a_component_id() -> None:
    rule = sa.load_rule()
    assert set(rule["admissible_fields"]) == {
        "component", "distinct_committer_count", "commits_in_window", "window_days"}


def test_no_admissible_pair_is_individual_or_cohort_granularity() -> None:
    for _kind, gran in sa.admissible_pairs(sa.load_rule()):
        assert gran == "aggregate"
