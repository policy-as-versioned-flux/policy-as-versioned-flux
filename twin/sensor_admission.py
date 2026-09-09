#!/usr/bin/env python3
"""What a real adopter may sense for `bus-factor-key-person` (eco-system ticket 31).

The three adopter scenarios already carry the sentence this module makes checkable: *"A role,
never a person ... Sensing a real departure would need admission through the ethics gate, a DPIA
and the roles register, which is a separate ticket."* This is that separate ticket. The scenario
half was done; what was missing was the **admission rule** and something that grades it.

`twin/ethics_gate.py` already walks purpose, necessity and proportionality, already refuses a
sensor id that is not a row in `twin/sensors.yaml`, and already blocks a mandatory-but-incomplete
DPIA. It cannot do five things this scenario class needs, and each is a refusal here:

  a  it never looks at WHAT a sensor reads, so a payload whose fields are an employee id or a
     free-text note walks the same ladder as a commit count;
  b  its `dpia.complete` is a boolean the payload asserts about itself -- no record is read, no
     date, no accountable role and no retention period exists anywhere;
  c  its ladder RANKS intrusiveness but admits any pair a payload can justify, so a cohort or
     individual reading of a bus factor is admissible if the arithmetic works out;
  d  nothing anywhere asks whether the sensed party was told, though NORTH-STAR section 6
     excludes covert sensing permanently;
  e  `twin/roles.yaml` is the twin's own SIGNING register; the role a sensor senses lives in the
     adopter's `twin/orgs/<org>/people/` register, and nothing joined the two.

**The hard constraint, and how it is kept.** No design in this file can reach a real person.
The admissible set is one pair, structural/aggregate; the admissible fields are a closed list of
three counts and a component id; and refusal (a) is TERMINAL -- a record that names or identifies
an individual is refused before `ethics_gate.admit()` is called, so this module has no code path
that computes a proportionality ratio for a record that names a person. Putting a price on
sensing a named individual is exactly what ticket 31 must not build.

**What is out of scope, and why.** Ticket 82's named-individuals ruling is unanswered. Nothing
here needs it: this module refuses a named individual outright rather than deciding what may be
done with one, so it does not brush that ruling in either direction.

THE SERVED ARTEFACT. A record that is not on an adopter's `origin/main` is not served, so
`grade_estate()` reads every fact through `git show origin/main:<path>` in the fetched clone,
never the working tree. A worktree can carry an uncommitted admission that nobody has published.

    twin/sensor_admission.py <estate-dir>   # grade an estate; prints lines, exits 0/1/3
    twin/sensor_admission.py --selfcheck    # the rules and the served read, on planted material
"""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable

import yaml

from . import PACKAGE_DIR
from . import ethics_gate
from .sign import PERSONAL_FIELDS

RULE_PATH = PACKAGE_DIR / "sensor-admission.yaml"
SCHEMA = "twin.sensor-admission/v1"
RECORD_SCHEMA = "twin.sensor-admission-record/v1"
SCENARIO_CLASS = "bus-factor-key-person"

#: Where an adopter publishes an admission record and a DPIA, relative to its repository root.
ADMISSIONS_DIR = "twin/orgs/{org}/sensor-admissions"
PEOPLE_DIR = "twin/orgs/{org}/people"
SCENARIOS_DIR = "twin/orgs/{org}/scenarios"

#: Tokens in a FIELD OR KEY name that mean the thing read is an individual. `sign.PERSONAL_FIELDS`
#: is the register this estate already refuses a signature for; the rest are the shapes that list
#: does not spell. `committer`, `author` and `contributor` are deliberately absent: they name a
#: relation to a commit, and `distinct_committer_count` is the admissible aggregate reading.
INDIVIDUAL_NAME_TOKENS: tuple[str, ...] = tuple(sorted(set(PERSONAL_FIELDS) | {
    "employee", "staff", "payroll", "nino", "username", "handle", "phone", "mobile",
    "address", "photo", "biometric", "free", "text", "note", "comment", "message",
    "surname", "forename", "initials", "badge", "login", "worker",
}))

#: Shapes in a VALUE that identify an individual whatever the field is called.
_EMAIL = re.compile(r"[^\s@,;]+@[^\s@,;]+\.[^\s@,;]+")
_NI_NUMBER = re.compile(r"\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]?\b")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_WORD = re.compile(r"[^a-z0-9]+")

REFUSAL_IDS = (
    "names-or-identifies-an-individual",
    "field-not-admissible",
    "kind-not-admissible",
    "no-dpia-record",
    "covert-sensing",
    "role-not-registered",
    "sensor-not-named",
)


class SensorAdmissionError(RuntimeError):
    """A malformed rule table, or an admission record that is not one at all."""


# -- the rule table -------------------------------------------------------------------------------

@lru_cache(maxsize=8)
def load_rule(path: Path | None = None) -> dict[str, Any]:
    """The closed rule table, validated on read -- the discipline `ethics_gate.load_sensors()`
    already applies to `sensors.yaml`. A table missing a refusal id the module can emit is
    refused here, so a sentence can never go missing and leave a refusal printing nothing."""
    source = path or RULE_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise SensorAdmissionError(f"{source}: not a {SCHEMA} document")
    for field in ("scenario_class", "admissible", "admissible_fields", "refusals", "requires"):
        if not doc.get(field):
            raise SensorAdmissionError(f"{source}: declares no {field}")
    declared = {str(r.get("id")) for r in doc["refusals"] if isinstance(r, dict)}
    missing = [r for r in REFUSAL_IDS if r not in declared]
    if missing:
        raise SensorAdmissionError(f"{source}: declares no sentence for {', '.join(missing)}")
    for row in doc["admissible"]:
        if row.get("kind") not in ("structural", "behavioural"):
            raise SensorAdmissionError(f"{source}: unknown kind {row.get('kind')!r}")
        if row.get("granularity") not in ("aggregate", "cohort", "individual"):
            raise SensorAdmissionError(f"{source}: unknown granularity {row.get('granularity')!r}")
    return doc


def admissible_pairs(rule: dict[str, Any]) -> tuple[tuple[str, str], ...]:
    return tuple((str(r["kind"]), str(r["granularity"])) for r in rule["admissible"])


def refusal(rule: dict[str, Any], rid: str, sensor: str, what: str, admissible: str = "") -> str:
    """The declared sentence, filled in. The sentence lives in the table so the words a reader is
    shown and the words the gate grades are the same bytes."""
    for row in rule["refusals"]:
        if str(row.get("id")) == rid:
            text = " ".join(str(row["sentence"]).split())
            return text.format(sensor=sensor or "(no sensor named)", what=what,
                               admissible=admissible)
    raise SensorAdmissionError(f"no declared sentence for refusal {rid!r}")


def is_terminal(rule: dict[str, Any], rid: str) -> bool:
    for row in rule["refusals"]:
        if str(row.get("id")) == rid:
            return bool(row.get("terminal"))
    return False


# -- individual shapes ----------------------------------------------------------------------------

def identifier_in_name(name: str) -> str | None:
    """The token that makes this field or key name an individual's, or None."""
    for token in _WORD.split(str(name).lower()):
        if token and token in INDIVIDUAL_NAME_TOKENS:
            return token
    return None


def identifier_in_value(value: str) -> str | None:
    """The shape that makes this value an individual's, whatever the field is called."""
    text = str(value)
    if _EMAIL.search(text):
        return "an email address"
    if _NI_NUMBER.search(text):
        return "a national insurance number"
    return None


def _walk(node: Any, path: str = "") -> Iterable[tuple[str, Any, Any]]:
    """(dotted path, key, value) for every leaf and every mapping key in a nested document."""
    if isinstance(node, dict):
        for key, value in node.items():
            here = f"{path}.{key}" if path else str(key)
            yield here, key, value
            yield from _walk(value, here)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            here = f"{path}[{index}]"
            yield here, None, value
            yield from _walk(value, here)


def individual_problems(document: Any, *, scan_names: bool = True) -> list[str]:
    """Every way this document names or identifies an individual, in document order.

    `scan_names=False` scans VALUES only -- used on a DPIA record, whose own keys legitimately
    talk about what is and is not sensed.
    """
    problems: list[str] = []
    for where, key, value in _walk(document):
        if scan_names and key is not None:
            token = identifier_in_name(str(key))
            if token is not None:
                problems.append(f"the key {where!r} (the word {token!r})")
        if isinstance(value, str):
            shape = identifier_in_value(value)
            if shape is not None:
                problems.append(f"the value at {where!r} ({shape})")
            elif scan_names and identifier_in_name(value) and where.startswith("fields["):
                problems.append(f"the field {value!r} (the word {identifier_in_name(value)!r})")
    return problems


# -- grading one record ---------------------------------------------------------------------------

def _missing_dpia(text: str | None, path: str, rule: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """What is wrong with the DPIA record at `path`, and whatever of it could be read."""
    if not path:
        return ["the record names no DPIA path at all"], {}
    if text is None:
        return [f"no DPIA record at {path}"], {}
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return [f"the DPIA record at {path} does not parse ({exc.__class__.__name__})"], {}
    if not isinstance(doc, dict):
        return [f"the DPIA record at {path} is not a mapping"], {}
    problems: list[str] = []
    for field in rule["requires"]["dpia_fields"]:
        if not str(doc.get(field, "")).strip():
            problems.append(f"the DPIA record at {path} carries no {field}")
    when = str(doc.get("completed_on", "")).strip()
    if when and not _DATE.match(when):
        problems.append(f"the DPIA record at {path} dates completed_on {when!r}, not YYYY-MM-DD")
    days = doc.get("retention_days")
    if days is not None and (not isinstance(days, int) or isinstance(days, bool) or days <= 0):
        problems.append(
            f"the DPIA record at {path} states retention_days {days!r}, not a positive whole "
            "number of days")
    for shape in individual_problems(doc, scan_names=False):
        problems.append(f"the DPIA record at {path} carries {shape}")
    return problems, doc


def grade_record(
    record: dict[str, Any],
    *,
    people: Iterable[str] = (),
    dpia_reader: Callable[[str], str | None] | None = None,
    rule: dict[str, Any] | None = None,
    sensors_path: Path | None = None,
) -> dict[str, Any]:
    """Grade one admission record. Returns `{"sensor", "admitted", "refusals", "terminal",
    "ladder"}`; never raises on a bad record, because a refusal a caller must handle is the
    product, not an exception a caller might not.

    Refusal (a) is terminal and is evaluated alone: when it fires, `ladder` is None and no other
    refusal is reported. Every other refusal is reported together, so an adopter fixing one
    learns of the rest in the same run instead of over four round trips.
    """
    rule = rule or load_rule()
    known_people = set(str(p) for p in people)
    sensor = str(record.get("sensor", "")).strip()
    admissible = admissible_pairs(rule)
    admissible_text = ", ".join(f"{k}/{g}" for k, g in admissible)

    # (a) terminal.
    named = individual_problems(record)
    if named:
        return {
            "sensor": sensor,
            "scenario_class": rule["scenario_class"],
            "refusals": [refusal(rule, "names-or-identifies-an-individual", sensor, named[0])],
            "terminal": True,
            "ladder": None,
            "admitted": False,
        }

    refusals: list[str] = []

    # sensor id: `sensors.yaml` stays the closed table, reported as a refusal rather than raised.
    known_sensors = ethics_gate.sensor_ids(sensors_path)
    sensor_named = sensor in known_sensors
    if not sensor_named:
        refusals.append(refusal(
            rule, "sensor-not-named", sensor,
            f"{sensor!r} is not a named sensor (have: {', '.join(known_sensors)})"))

    # (c) kind and granularity, declared and as the ladder walks them.
    kind, gran = str(record.get("kind", "")), str(record.get("granularity", ""))
    if (kind, gran) not in admissible:
        refusals.append(refusal(rule, "kind-not-admissible", sensor, f"{kind}/{gran}",
                                admissible_text))
    necessity = record.get("ladder", {}).get("necessity", {}) if isinstance(record.get("ladder"), dict) else {}
    walked = (str(necessity.get("kind", "")), str(necessity.get("level", "")))
    if walked != (kind, gran):
        refusals.append(refusal(
            rule, "kind-not-admissible", sensor,
            f"the record declares {kind}/{gran} and its ladder walks "
            f"{walked[0]}/{walked[1]}, so one of the two is not what runs",
            admissible_text))

    # the closed field set.
    fields = record.get("fields")
    if not isinstance(fields, list) or not fields:
        refusals.append(refusal(rule, "field-not-admissible", sensor,
                                "(the record declares no fields)", ", ".join(rule["admissible_fields"])))
    else:
        for field in fields:
            if str(field) not in rule["admissible_fields"]:
                refusals.append(refusal(rule, "field-not-admissible", sensor, str(field),
                                        ", ".join(rule["admissible_fields"])))

    # (d) covert sensing.
    notice = record.get("notice")
    if not isinstance(notice, dict) or not notice:
        refusals.append(refusal(rule, "covert-sensing", sensor,
                                "the record carries no notice, so the sensed party is not told"))
    else:
        for field in ("told", "published_at", "published_on"):
            if not str(notice.get(field, "")).strip():
                refusals.append(refusal(
                    rule, "covert-sensing", sensor,
                    f"the notice carries no {field}, so the sensed party is not told"))
        when = str(notice.get("published_on", "")).strip()
        if when and not _DATE.match(when):
            refusals.append(refusal(
                rule, "covert-sensing", sensor,
                f"the notice dates published_on {when!r}, not YYYY-MM-DD, so nothing says when "
                "anybody was told"))

    # (b) the DPIA record.
    dpia_path = str((record.get("dpia") or {}).get("record", "")).strip()
    text = dpia_reader(dpia_path) if (dpia_reader and dpia_path) else None
    dpia_problems, dpia_doc = _missing_dpia(text, dpia_path, rule)
    for problem in dpia_problems:
        refusals.append(refusal(rule, "no-dpia-record", sensor, problem))

    # (e) the roles register.
    senses = str(record.get("senses_role", "")).strip()
    if not senses:
        refusals.append(refusal(rule, "role-not-registered", sensor, "no sensed role at all"))
    elif senses not in known_people:
        refusals.append(refusal(rule, "role-not-registered", sensor, f"the sensed role {senses!r}"))
    signed_off = str(dpia_doc.get("completed_by", "")).strip()
    if signed_off and signed_off not in known_people:
        refusals.append(refusal(rule, "role-not-registered", sensor,
                                f"{signed_off!r} as the role accountable for the DPIA"))

    # the existing ladder, last, and only for a sensor the closed table names.
    ladder: dict[str, Any] | None = None
    if sensor_named and isinstance(record.get("ladder"), dict):
        payload = {"sensor": {"id": sensor, "name": sensor}, **record["ladder"]}
        try:
            ladder = ethics_gate.admit(payload)
        except ethics_gate.EthicsGateError as exc:
            refusals.append(refusal(rule, "sensor-not-named", sensor, str(exc)))

    admitted = not refusals and ladder is not None and bool(ladder["admitted"])
    return {
        "sensor": sensor,
        "scenario_class": rule["scenario_class"],
        "refusals": refusals,
        "terminal": False,
        "ladder": ladder,
        "admitted": admitted,
    }


# -- the served artefact --------------------------------------------------------------------------

def served(unit: Path, path: str) -> str | None:
    """The bytes GitHub serves at `origin/main:<path>`, or None. Never the working tree: an
    uncommitted admission record is not one an adopter has published."""
    out = subprocess.run(["git", "-C", str(unit), "show", f"origin/main:{path}"],
                         capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def served_paths(unit: Path) -> list[str]:
    out = subprocess.run(["git", "-C", str(unit), "ls-tree", "-r", "--name-only", "origin/main"],
                         capture_output=True, text=True)
    return out.stdout.splitlines() if out.returncode == 0 else []


def served_sha(unit: Path) -> str | None:
    out = subprocess.run(["git", "-C", str(unit), "rev-parse", "--short", "origin/main"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def adopters(estate: Path) -> list[str]:
    """Every unit whose SERVED party artefact claims the adopter role. Derived, never typed: a
    fourth adopter arrives here by publishing a party artefact."""
    found: list[str] = []
    if not estate.is_dir():
        return found
    for unit in sorted(p for p in estate.iterdir() if p.is_dir()):
        text = served(unit, "party.yaml")
        if not text:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict) and "adopter" in (doc.get("roles") or []):
            found.append(unit.name)
    return found


def people_register(estate: Path, org: str) -> dict[str, dict[str, Any]]:
    """The adopter's own roles register, read at `origin/main`."""
    prefix = PEOPLE_DIR.format(org=org) + "/"
    unit = estate / org
    register: dict[str, dict[str, Any]] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix) or not path.endswith(".yaml"):
            continue
        text = served(unit, path)
        if text is None:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict) and doc.get("id"):
            register[str(doc["id"])] = doc
    return register


def key_person_scenarios(estate: Path, org: str) -> dict[str, dict[str, Any]]:
    prefix = SCENARIOS_DIR.format(org=org) + "/"
    unit = estate / org
    out: dict[str, dict[str, Any]] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix) or not path.endswith(".yaml"):
            continue
        text = served(unit, path)
        if text is None:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        if isinstance(doc, dict) and doc.get("class") == SCENARIO_CLASS:
            out[path] = doc
    return out


def admission_records(estate: Path, org: str) -> dict[str, dict[str, Any] | None]:
    prefix = ADMISSIONS_DIR.format(org=org) + "/"
    unit = estate / org
    out: dict[str, dict[str, Any] | None] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix) or not path.endswith(".yaml"):
            continue
        text = served(unit, path)
        if text is None:
            out[path] = None
            continue
        try:
            doc = yaml.safe_load(text)
        except yaml.YAMLError:
            doc = None
        out[path] = doc if isinstance(doc, dict) else None
    return out


NOTE_SENTENCE = "A role, never a person"


def grade_estate(estate: Path, out: Callable[[str], None] = print) -> int:
    """Grade every adopter's SERVED tree. 0 observed true, 1 observed false, 3 could not look.

    Three legs, each on `origin/main`:
      1. every `bus-factor-key-person` scenario says "A role, never a person" and names a role
         file that the served tree carries;
      2. every role file in the adopter's people register carries an id and a role and names no
         individual;
      3. every admission record grades through the rule above.

    Leg 3 is the one ticket 31 exists for and it is the one that cannot look today: nothing is
    admitted, because nobody has declared a sensor. That is printed as a COUNT, never as a pass.
    """
    if not estate.is_dir():
        out(f"SKIP: no estate clone at {estate}")
        return 3
    orgs = adopters(estate)
    if not orgs:
        out(f"SKIP: no party in {estate} serves a party.yaml claiming the adopter role at "
            "origin/main")
        return 3

    rule = load_rule()
    fail = 0
    scenarios_seen = 0
    records_seen = 0
    admitted_count = 0
    refused_count = 0
    shas: list[str] = []

    for org in orgs:
        unit = estate / org
        sha = served_sha(unit)
        shas.append(f"{org}={sha or 'unknown'}")
        register = people_register(estate, org)

        # leg 2: the register itself names nobody.
        for role_id, doc in sorted(register.items()):
            problems = individual_problems(doc)
            if problems:
                out(f"FAIL {org}: the role file for {role_id!r} carries {problems[0]}")
                fail += 1
            elif not str(doc.get("role", "")).strip():
                out(f"FAIL {org}: the role file for {role_id!r} says what it is accountable for "
                    "nowhere, so 'a role, never a person' rests on the id alone")
                fail += 1
        if not register:
            out(f"FAIL {org}: serves no people register at "
                f"{PEOPLE_DIR.format(org=org)}/, so no sensor could name a registered role")
            fail += 1

        # leg 1: the scenario keeps saying it.
        found = key_person_scenarios(estate, org)
        scenarios_seen += len(found)
        for path, doc in sorted(found.items()):
            note = " ".join(str(doc.get("note", "")).split())
            if NOTE_SENTENCE.lower() not in note.lower():
                out(f"FAIL {org}: {path} is a {SCENARIO_CLASS} scenario whose note no longer "
                    f"says {NOTE_SENTENCE!r}")
                fail += 1
            subject = re.search(r"`people/([a-z0-9-]+)\.yaml`", note)
            if subject is None:
                out(f"FAIL {org}: {path} names no `people/<role>.yaml` subject in its note")
                fail += 1
            elif subject.group(1) not in register:
                out(f"FAIL {org}: {path} names `people/{subject.group(1)}.yaml` as its subject "
                    f"and the served people register carries {sorted(register) or 'nothing'}")
                fail += 1

        # leg 3: the admission records, if any are served.
        records = admission_records(estate, org)

        def read_dpia(dpia_path: str, u: Path = unit) -> str | None:
            return served(u, dpia_path)

        for path, maybe in sorted(records.items()):
            records_seen += 1
            if maybe is None:
                out(f"FAIL {org}: {path} is not a readable admission record")
                fail += 1
                continue
            result = grade_record(maybe, people=register.keys(), rule=rule,
                                  dpia_reader=read_dpia)
            if result["admitted"]:
                admitted_count += 1
                out(f"PASS {org}: {path}: {result['sensor']} admitted -- "
                    f"{result['ladder']['claim']['evidence']}")
            else:
                refused_count += 1
                for line in result["refusals"]:
                    out(f"FAIL {org}: {path}: {line}")
                fail += 1

    units = " ".join(shas)
    if fail:
        out(f"FAIL: {fail} observed false across {len(orgs)} adopters at origin/main "
            f"[{units}]; {scenarios_seen} {SCENARIO_CLASS} scenarios, {records_seen} admission "
            f"records ({admitted_count} admitted, {refused_count} refused)")
        return 1
    if records_seen == 0:
        out(f"SKIP: {len(orgs)} adopters read at origin/main [{units}]; {scenarios_seen} carry a "
            f"{SCENARIO_CLASS} scenario and every one still says {NOTE_SENTENCE!r}; 0 declare a "
            f"sensor admission under twin/orgs/<org>/sensor-admissions/, so 0 admission decisions "
            f"could be graded")
        return 3
    out(f"PASS: {len(orgs)} adopters read at origin/main [{units}]; {scenarios_seen} "
        f"{SCENARIO_CLASS} scenarios still say {NOTE_SENTENCE!r}; {records_seen} admission "
        f"records graded, {admitted_count} admitted, {refused_count} refused")
    return 0


# -- selfcheck ------------------------------------------------------------------------------------

_GOOD_DPIA = """schema: twin.dpia/v1
sensor: bus-factor-structural-aggregate
scenario: key-person-2026
completed_on: '2026-09-09'
completed_by: platform-lead
retention_days: 90
lawful_basis: legitimate interests in the continuity of a service the organisation runs
what_is_sensed: the number of distinct committers to a component in a window, per component
what_is_not_sensed: any individual, any message, any keystroke, any identifier
"""

_GOOD_RECORD = """schema: twin.sensor-admission-record/v1
sensor: bus-factor-structural-aggregate
scenario: key-person-2026
scenario_class: bus-factor-key-person
senses_role: platform-engineer
kind: structural
granularity: aggregate
fields: [component, distinct_committer_count, window_days]
notice:
  told: every holder of a role in the people register, before the sensor first runs
  published_at: docs/monitoring-notice.md
  published_on: '2026-09-09'
dpia:
  record: twin/orgs/planted/dpia/bus-factor-structural-aggregate.yaml
ladder:
  purpose: {scenario: key-person-2026, will_act: true}
  necessity:
    kind: structural
    level: aggregate
    alternatives: [{kind: behavioural, level: individual}]
  proportionality: {intrusion_cost: 500.0, value_illuminated: 50000.0}
  dpia: {channels: [], profiling: false, financial_loss_risk: false, complete: true}
"""

_SCENARIO = """id: key-person-2026
class: bus-factor-key-person
note: >-
  A role, never a person: `people/platform-engineer.yaml` is the subject and it names no
  individual.
"""


def _git(repo: Path, *args: str, hooks: Path) -> None:
    subprocess.run(["git", "-c", f"core.hooksPath={hooks}", "-C", str(repo), *args],
                   check=True, capture_output=True, text=True)


def _plant(root: Path, hooks: Path, record: str | None) -> Path:
    """A one-unit estate whose SERVED ref is a real `refs/remotes/origin/main`."""
    estate = root / "estate"
    unit = estate / "planted"
    org = "planted"
    (unit / f"twin/orgs/{org}/people").mkdir(parents=True, exist_ok=True)
    (unit / f"twin/orgs/{org}/scenarios").mkdir(parents=True, exist_ok=True)
    (unit / f"twin/orgs/{org}/dpia").mkdir(parents=True, exist_ok=True)
    (unit / "party.yaml").write_text("party: planted\nroles: [adopter]\n", encoding="utf-8")
    (unit / f"twin/orgs/{org}/people/platform-engineer.yaml").write_text(
        "id: platform-engineer\nrole: On call for the planted namespace.\n", encoding="utf-8")
    (unit / f"twin/orgs/{org}/people/platform-lead.yaml").write_text(
        "id: platform-lead\nrole: Accountable for the planted DPIA.\n", encoding="utf-8")
    (unit / f"twin/orgs/{org}/scenarios/key-person-2026.yaml").write_text(_SCENARIO, encoding="utf-8")
    (unit / f"twin/orgs/{org}/dpia/bus-factor-structural-aggregate.yaml").write_text(
        _GOOD_DPIA, encoding="utf-8")
    admissions = unit / f"twin/orgs/{org}/sensor-admissions"
    if record is not None:
        admissions.mkdir(parents=True, exist_ok=True)
        (admissions / "bus-factor-structural-aggregate.yaml").write_text(record, encoding="utf-8")
    _git(unit, "init", "-q", "-b", "main", hooks=hooks)
    _git(unit, "config", "user.email", "selfcheck@example.invalid", hooks=hooks)
    _git(unit, "config", "user.name", "selfcheck", hooks=hooks)
    _git(unit, "add", "-A", hooks=hooks)
    _git(unit, "commit", "-q", "-m", "planted", hooks=hooks)
    _git(unit, "update-ref", "refs/remotes/origin/main", "HEAD", hooks=hooks)
    return estate


def selfcheck(out: Callable[[str], None] = print) -> int:
    """The rules and the served read, on planted material. A grader only ever run against
    material that passes it proves nothing, so every refusal is planted red first here."""
    rule = load_rule()
    people = ("platform-engineer", "platform-lead")
    good = yaml.safe_load(_GOOD_RECORD)
    failures = 0

    def reader(text: str | None) -> Callable[[str], str | None]:
        return lambda path: text if path.endswith("bus-factor-structural-aggregate.yaml") else None

    def expect(what: str, record: dict[str, Any], rid: str | None,
               dpia: str | None = _GOOD_DPIA) -> None:
        nonlocal failures
        result = grade_record(record, people=people, rule=rule, dpia_reader=reader(dpia))
        got = [line.split(":")[0].removeprefix("REFUSED ").strip() for line in result["refusals"]]
        if rid is None:
            if result["admitted"] and not got:
                out(f"PASS: selfcheck: {what}")
                return
            out(f"FAIL: selfcheck: {what} -- expected an admission, got {result['refusals']}")
        else:
            if rid in got and not result["admitted"]:
                out(f"PASS: selfcheck: {what} ({[line for line in result['refusals'] if rid in line][0][:150]})")
                return
            out(f"FAIL: selfcheck: {what} -- expected {rid}, got {got or 'an admission'}")
        failures += 1

    import copy
    def variant(**over: Any) -> dict[str, Any]:
        rec = copy.deepcopy(good)
        rec.update(copy.deepcopy(over))
        return rec

    expect("a sensor reading an employee id is refused by name",
           variant(fields=["component", "employee_id"]), "names-or-identifies-an-individual")
    expect("a sensor with no DPIA record is refused", variant(), "no-dpia-record", dpia=None)
    expect("a DPIA record with no retention period is refused", variant(), "no-dpia-record",
           dpia=_GOOD_DPIA.replace("retention_days: 90\n", ""))
    ladder = copy.deepcopy(good["ladder"])
    ladder["necessity"] = {"kind": "behavioural", "level": "individual", "alternatives": []}
    expect("a behavioural/individual reading is refused",
           variant(kind="behavioural", granularity="individual", ladder=ladder),
           "kind-not-admissible")
    expect("a cohort reading is refused", variant(granularity="cohort"), "kind-not-admissible")
    expect("a sensor the sensed party is not told about is refused", variant(notice={}),
           "covert-sensing")
    expect("a sensed role absent from the people register is refused",
           variant(senses_role="unregistered-role"), "role-not-registered")
    expect("a sensor id absent from sensors.yaml is refused",
           variant(sensor="not-a-named-sensor"), "sensor-not-named")
    expect("a field outside the closed set is refused",
           variant(fields=["component", "lines_of_code"]), "field-not-admissible")
    expect("the one admissible sensor is admitted", variant(), None)

    # and the served read itself, on a real git repository.
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        hooks = root / "nohooks"
        hooks.mkdir()
        lines: list[str] = []
        estate = _plant(root / "green", hooks, _GOOD_RECORD)
        rc = grade_estate(estate, out=lines.append)
        if rc == 0 and any("1 admission records graded, 1 admitted" in ln for ln in lines):
            out(f"PASS: selfcheck: a planted served admission grades PASS ({lines[-1][:150]})")
        else:
            out(f"FAIL: selfcheck: a planted served admission should grade PASS, got exit {rc}: "
                f"{lines[-1] if lines else 'nothing'}")
            failures += 1

        lines = []
        estate = _plant(root / "red", hooks, _GOOD_RECORD.replace(
            "fields: [component, distinct_committer_count, window_days]",
            "fields: [component, employee_id]"))
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("names-or-identifies-an-individual" in ln for ln in lines):
            out(f"PASS: selfcheck: a planted served admission naming an individual grades FAIL "
                f"({lines[-1][:150]})")
        else:
            out(f"FAIL: selfcheck: a planted served admission naming an individual should grade "
                f"FAIL, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        lines = []
        estate = _plant(root / "skip", hooks, None)
        rc = grade_estate(estate, out=lines.append)
        if rc == 3 and any("0 declare a sensor admission" in ln for ln in lines):
            out(f"PASS: selfcheck: an adopter declaring no sensor is a could-not-look with a "
                f"count ({lines[-1][:150]})")
        else:
            out(f"FAIL: selfcheck: an adopter declaring no sensor should be a could-not-look "
                f"with a count, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

    if failures:
        out(f"FAIL: selfcheck: {failures} planted case(s) did not grade as planted")
        return 1
    out("PASS: selfcheck: ten planted records and three planted served estates grade as planted")
    return 0


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    if argv[0] == "--selfcheck":
        return selfcheck()
    return grade_estate(Path(argv[0]))


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
