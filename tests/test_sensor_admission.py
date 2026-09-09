"""The admission rule for `bus-factor-key-person` (eco-system ticket 31).

Nothing in this file names or senses a real person. Every role is a role id out of an adopter's
own people register, every planted identifier is a FIELD NAME or a value at `example.invalid`,
and the one place a value shape is asserted uses a reserved-by-RFC-2606 domain and a zeroed id.
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
            "told": "every holder of a role in the people register, before the sensor first runs",
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
                          notice={"told": "someone@example.invalid",
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
    result = grade(record(notice={"told": "every holder of a role in the people register",
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
