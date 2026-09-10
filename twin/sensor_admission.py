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

import ast
import re
import shutil
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Iterable, NamedTuple

import yaml

from . import PACKAGE_DIR
from . import ethics_gate
from .sign import PERSONAL_FIELDS
from .strict_yaml import StrictLoader, duplicate_key

RULE_PATH = PACKAGE_DIR / "sensor-admission.yaml"
SCHEMA = "twin.sensor-admission/v1"
RECORD_SCHEMA = "twin.sensor-admission-record/v1"
SCENARIO_CLASS = "bus-factor-key-person"

#: Where an adopter publishes an admission record and a DPIA, relative to its repository root.
ADMISSIONS_DIR = "twin/orgs/{org}/sensor-admissions"
PEOPLE_DIR = "twin/orgs/{org}/people"
SCENARIOS_DIR = "twin/orgs/{org}/scenarios"
ORG_DIR = "twin/orgs/{org}"

#: Both spellings (round-6 F3). Reading only the long one dropped a record or a role file under
#: the short one in silence -- and the short one is what this estate uses for every workflow
#: file. Anything under a scanned directory that is neither is a NAMED row, not a third silent
#: class.
YAML_SUFFIXES = (".yaml", ".yml")

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
# R5-5 and round-6 F8: an adopter's own served bytes could deny the whole gate. A regular
# expression here backtracked quadratically -- 8 KiB 0.275s, 32 KiB 4.44s, 128 KiB 73s, 1 MiB
# about 75 minutes -- and neither the module nor the wrapper has a timeout, so in the gate that
# is a job that dies with no verdict. R5-5 returned early when the value had NO at-sign; F8
# measured that ONE at-sign, one character an adopter serves, restored it completely (24 KiB
# 2.4s, 128 KiB 73.5s), and R5-7 had just widened the scan to every readable party file, so the
# denial surface GREW. The pathological case was the pattern, not the input.
#
# So there is no pattern. `_looks_like_an_email` is a LINEAR scan: split on whitespace and the
# separators, then walk the at-signs within each chunk and test the part after each for an
# interior dot. No repetition operator, nothing to backtrack, cost strictly linear in the length
# of the value. The NI number is a bounded pattern and needs nothing.
#
# Round 7 (R7-1) repaired what the first cut of this scan LOST relative to the pattern -- an
# address at the end of a sentence, and a chunk carrying more than one at-sign -- without giving
# any of the speed back: 24 KiB went from 2.4s to 0.04ms, 128 KiB from 73.5s to 0.22ms, a
# megabyte takes 1.8ms. Every shape either root cause dropped is now a test.
_EMAIL_SEPARATORS = str.maketrans({",": " ", ";": " ", "|": " ", "/": " ", "<": " ", ">": " "})


def _has_an_interior_dot(domain: str) -> bool:
    """A dot with a label on each side, after any TRAILING dots are stripped.

    Round-7 finding R7-1, first root cause. This was `domain.rpartition('.')`, which takes the
    LAST dot: `example.com.` returned `('example.com', '.', '')`, the empty tail discarded the
    chunk, and **a full stop ending a sentence is the commonest way an address appears in prose**.
    The pattern this replaced searched from any offset and matched regardless.
    """
    trimmed = domain.rstrip(".")
    dot = trimmed.find(".")
    return 0 < dot < len(trimmed) - 1


def _looks_like_an_email(text: str) -> bool:
    if "@" not in text:
        return False
    for chunk in text.translate(_EMAIL_SEPARATORS).split():
        # Round-7 R7-1, second root cause: this was `if '@' in domain: continue`, which threw a
        # whole chunk away rather than trying the LATER at-signs in it, so a `mailto:` URL with a
        # cc and two addresses joined by a slash or a pipe were both invisible. Splitting once
        # and walking the adjacent pairs tries every at-sign and stays strictly linear: each
        # character of the chunk is visited once by `split` and once by the dot scan of the part
        # it lands in.
        parts = chunk.split("@")
        for index in range(len(parts) - 1):
            if parts[index] and _has_an_interior_dot(parts[index + 1]):
                return True
    return False
_NI_NUMBER = re.compile(r"\b[A-CEGHJ-PR-TW-Z]{2}\d{6}[A-D]?\b")
_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_WORD = re.compile(r"[^a-z0-9]+")

#: Every closed key set `closed_keys` must declare (review F1). A set the table forgets is a
#: refusal at load, never an open node.
_KEY_SETS = (
    "record", "notice", "dpia_ref", "ladder", "ladder_purpose", "ladder_necessity",
    "ladder_alternative", "ladder_proportionality", "ladder_dpia", "dpia_record", "people_file",
)

_TYPE_KINDS = ("bool", "number")

#: A refusal id, as this module's source spells one: lower case, at least one hyphen.
_ID_SHAPE = re.compile(r"^[a-z]+(?:-[a-z]+)+$")

#: The functions that build `(refusal id, what)` pairs rather than calling `out()` directly.
_PROBLEM_BUILDERS = ("closed_document_problems", "grade_record")

#: The function whose `out(...)` calls are the refusal emitter. Round-6: the walk matched by
#: NAME, so `grade_estate`'s `out` parameter -- the printer -- was conflated with it.
_EMITTER_FUNCTIONS = ("grade_record",)


def emitted_refusal_ids(source: Path | None = None) -> set[str]:
    """Every refusal id this module's own SOURCE can actually emit, read off the call sites.

    Round-5 finding R5-8: the two-way subset `load_rule()` enforced was between two
    DECLARATIONS -- the table and a hand-written `REFUSAL_IDS` -- not between a declaration and
    the CODE. An id added to BOTH loaded clean and appeared verbatim in the printed block.

    WHAT THIS PROVES, narrowed in round 6 to what the walk supports: every refusal id this
    module's source passes LITERALLY to the emitter. It does not prove reachability -- dead code
    behind a never-true condition still counts -- so the printed block says "the refusals it can
    EMIT are". The valuable direction is the fail-closed one, and it is total: a sentence the
    table declares for an id no call site spells is refused at load, and an id a call site
    spells with no sentence is refused too. `_EMITTER_FUNCTIONS` scopes the first pass so
    `grade_estate`'s `out` PARAMETER -- a printer that happens to share the name -- is not
    mistaken for the emitter.

    Two shapes, because the module emits in two ways: a literal first argument to `out(...)`
    anywhere, and the first element of the `(refusal id, what)` pairs that the two collectors
    named in `_PROBLEM_BUILDERS` construct. The tuple shape is scoped to those functions so an
    unrelated pair of hyphenated strings elsewhere in the file is not mistaken for an emission.
    """
    text = (source or Path(__file__)).read_text(encoding="utf-8")
    tree = ast.parse(text)
    found: set[str] = set()

    def add(node: ast.AST) -> None:
        if isinstance(node, ast.Constant) and isinstance(node.value, str) \
                and _ID_SHAPE.match(node.value):
            found.add(node.value)

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in _EMITTER_FUNCTIONS:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name) \
                    and inner.func.id == "out" and inner.args:
                first = inner.args[0]
                if isinstance(first, ast.Constant) and isinstance(first.value, str):
                    found.add(first.value)
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef) or node.name not in _PROBLEM_BUILDERS:
            continue
        for inner in ast.walk(node):
            if isinstance(inner, ast.Tuple) and len(inner.elts) == 2:
                add(inner.elts[0])
            elif isinstance(inner, ast.IfExp):
                add(inner.body)
                add(inner.orelse)
    return {i for i in found if _ID_SHAPE.match(i)}


#: The declaration slots earlier rounds' fixes rest on (round-6 F6): (table, set, keys, why).
_DECLARATIONS_FIXES_REST_ON = (
    ("non_empty", "ladder_necessity", ("alternatives",),
     "round-4 F7 rests on it: an empty alternatives list passes the necessity rung vacuously"),
    ("required_keys", "ladder_necessity", ("kind", "level", "alternatives"),
     "round-4 F7 and round-5 R3 rest on it: ethics_gate indexes those slots with []"),
    ("required_keys", "ladder_proportionality", ("intrusion_cost", "value_illuminated"),
     "round-5 R3 rests on it: ethics_gate indexes both with []"),
    ("required_keys", "record", ("schema",),
     "round-4 F9 rests on it: without it, deleting the key is a green admission"),
    ("fixed_values", "record", ("schema",),
     "round-4 F9 rests on it: it is what pins the record schema to RECORD_SCHEMA"),
    ("fixed_values", "dpia_record", ("schema",),
     "round-4 F6 rests on it: the DPIA's own schema was a slot a name lived in"),
    ("typed_keys", "ladder_purpose", ("will_act",),
     "round-4 G1b rests on it: the ladder only tests will_act for truthiness, so prose passed"),
    ("requires", "dpia_fields", ("completed_on", "completed_by", "retention_days"),
     "the DPIA gate rests on all three: a date, an accountable role and a retention period"),
)

#: The record fields a DPIA can be checked to agree with (F4). Anything else is a declaration
#: this module cannot resolve, and was a KeyError at grade time.
_DPIA_AGREES_ON = ("sensor", "scenario")

#: The refusals `grade_record()` evaluates BEFORE the ladder, and therefore the only ones the
#: table may mark terminal (R5-13). Anything else marked terminal would be decorative.
_TERMINAL_CAPABLE = ("names-or-identifies-an-individual", "key-not-declared",
                     "value-not-the-declared-shape", "duplicate-key", "required-key-missing")

#: The refusals the table MUST mark terminal (round-6 F5). R5-13 constrained which ids MAY be
#: terminal and nothing constrained which must be, so a one-word table edit -- or simply
#: dropping the key, since the guard defaults it to False -- made this module walk the ethics
#: gate for a record that names a person and return `admitted: True` with a proportionality
#: justification. That is a PRICE on sensing a named individual, which this module's own
#: docstring says it has no code path for. The whole purpose of the ticket rests on this row.
_TERMINAL_REQUIRED = ("names-or-identifies-an-individual",)

REFUSAL_IDS = (
    "names-or-identifies-an-individual",
    "key-not-declared",
    "value-not-the-declared-shape",
    "duplicate-key",
    "required-key-missing",
    "ladder-could-not-walk",
    "not-this-scenario-class",
    "scenario-not-served",
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
    # F8: the one YAML this check read with `safe_load` on a real path was its own rule table,
    # so a second `typed_keys:` block appended to it loaded CLEAN and silently dropped two of the
    # three typed sets.
    doc = load_served(str(source), source.read_text(encoding="utf-8"))
    if isinstance(doc, Unreadable):
        raise SensorAdmissionError(f"{source}: {doc.why}")
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise SensorAdmissionError(f"{source}: not a {SCHEMA} document")
    for field in ("scenario_class", "admissible", "admissible_fields", "refusals", "requires",
                  "closed_keys", "free_prose_fields", "nested_maps", "nested_lists",
                  "scalar_lists", "typed_keys", "terminal_batch_clause", "required_keys",
                  "fixed_values", "dpia_must_agree", "dpia_path_pattern", "non_empty"):
        if not doc.get(field):
            raise SensorAdmissionError(f"{source}: declares no {field}")
    for name in _KEY_SETS:
        if not doc["closed_keys"].get(name):
            raise SensorAdmissionError(f"{source}: closed_keys declares no {name} set")
    # A nested set the table points at but never declares would silently stop the recursion at
    # the node it names, which is the G1 hole again by another route.
    for parent, children in {**doc["nested_maps"], **doc["nested_lists"]}.items():
        for key, child in (children or {}).items():
            # Re-check R5: membership is not usability. `child not in closed_keys` passed a set
            # DECLARED AS NULL, which then raised an uncaught TypeError at grade time.
            if not doc["closed_keys"].get(child):
                raise SensorAdmissionError(
                    f"{source}: {parent}.{key} points at the key set {child!r}, which "
                    "closed_keys does not declare, or declares empty")
    # Re-check R2: the declarations added by the G1 fix were validated by nothing. `bool`
    # mistyped as `boolean` loaded clean and made the type check a silent no-op, because the
    # recursion computes `wrong` as a disjunction over the names it knows.
    for table, what in (("typed_keys", "type"), ("scalar_lists", "scalar list"),
                        ("required_keys", "required key"), ("fixed_values", "fixed value"),
                        ("non_empty", "non-empty key"), ("nested_maps", "nested mapping"),
                        ("nested_lists", "nested list")):
        # R5-11: a mistyped table crashed out of load with an AttributeError rather than
        # refusing.
        if not isinstance(doc.get(table), dict):
            raise SensorAdmissionError(
                f"{source}: {table} is {doc.get(table)!r} and this module reads it as a mapping "
                f"of key set to {what}s")
        for set_name, entry in (doc.get(table) or {}).items():
            # F3: the falsiness guard reached the top level and `closed_keys`, not these tables'
            # SUB-ENTRIES. Nulling one loaded clean and silently disabled the check it names --
            # `typed_keys.ladder_purpose: null` readmitted the prose-in-a-boolean plant, and
            # `required_keys.ladder_necessity: null` brought back `KeyError: 'kind'`.
            if not entry:
                raise SensorAdmissionError(
                    f"{source}: {table}.{set_name} is declared empty, which silently disables "
                    f"the {what} check it names")
            declared = doc["closed_keys"].get(set_name)
            if not declared:
                raise SensorAdmissionError(
                    f"{source}: {table} names the key set {set_name!r}, which closed_keys does "
                    "not declare, or declares empty")
            keys = entry if isinstance(entry, (list, tuple)) else list(entry or {})
            for key in keys:
                if str(key) not in {str(k) for k in declared}:
                    raise SensorAdmissionError(
                        f"{source}: {table}.{set_name} names the {what} {key!r}, which the "
                        f"{set_name} key set does not declare")
            if table == "typed_keys":
                for key, kind in (entry or {}).items():
                    if str(kind) not in _TYPE_KINDS:
                        raise SensorAdmissionError(
                            f"{source}: typed_keys.{set_name}.{key} declares the type "
                            f"{kind!r}, which this module does not know (have: "
                            f"{', '.join(_TYPE_KINDS)}) — an unknown name makes the check a "
                            "silent no-op")
    # F4: three declarations the module INDEXES had no load guard at all, each a KeyError at
    # grade time. `admissible_channels` needs a presence-and-type check and not a truthiness
    # one, because its correct value is an empty list.
    # R5-4: `admissible_fields` was truthiness-checked only, so declared as a SCALAR (one
    # missing list dash) it loaded clean and turned the closed field set into a SUBSTRING test:
    # `fields: [com, pone]` was admitted.
    for field in ("dpia_must_agree", "admissible_channels", "free_prose_fields",
                  "admissible_fields"):
        if not isinstance(doc.get(field), list):
            raise SensorAdmissionError(
                f"{source}: {field} is {doc.get(field)!r}, and this module indexes it as a list")
    for field in doc["dpia_must_agree"]:
        if str(field) not in _DPIA_AGREES_ON:
            raise SensorAdmissionError(
                f"{source}: dpia_must_agree names {field!r}, which this module cannot resolve "
                f"against the record (have: {', '.join(sorted(_DPIA_AGREES_ON))})")
    dpia_keys = {str(k) for k in doc["closed_keys"]["dpia_record"]}
    if not doc.get("requires", {}).get("dpia_fields"):
        raise SensorAdmissionError(f"{source}: requires declares no dpia_fields")
    for field in list(doc["requires"]["dpia_fields"]) + list(doc["free_prose_fields"]):
        if str(field) not in dpia_keys:
            raise SensorAdmissionError(
                f"{source}: {field!r} is named as a DPIA field and the dpia_record key set does "
                "not declare it")
    declared_ids = {str(r.get("id")) for r in doc["refusals"] if isinstance(r, dict)}
    declared = declared_ids
    # F5: the subset was enforced in one direction only, so a well-formed but UNREACHABLE
    # refusal id loaded clean and the generated limits block grew to include it.
    emitted = emitted_refusal_ids()
    for extra in sorted(declared_ids - emitted):
        raise SensorAdmissionError(
            f"{source}: declares the refusal {extra!r}, which no `out(...)` call site in this "
            "module emits — a generated limits block would advertise a refusal that cannot "
            "happen")
    for unlisted in sorted(emitted - declared_ids):
        raise SensorAdmissionError(
            f"{source}: this module emits {unlisted!r} and the table declares no sentence for it")
    # R5-3: `dpia_path_pattern` was read and validated by nothing. `^.*$` loaded clean and
    # readmitted a DPIA filed under a directory named after a person, which is what round 4's F6
    # closed; an invalid pattern loaded clean and raised at grade time.
    pattern = doc.get("dpia_path_pattern")
    if not isinstance(pattern, str) or "{sensor}" not in pattern:
        raise SensorAdmissionError(
            f"{source}: dpia_path_pattern is {pattern!r} and must be a string naming "
            "{sensor}, or it does not derive the path against the sensor at all")
    try:
        re.compile(pattern.replace("{sensor}", "x"))
    except re.error as exc:
        raise SensorAdmissionError(
            f"{source}: dpia_path_pattern is not a compilable regular expression ({exc})"
        ) from exc
    # Round-6 F6: three earlier fixes could be re-opened by a mis-authoring that loads clean.
    # Each slot a fix RESTS ON is asserted by name, so narrowing it is a refusal rather than a
    # silently readmitted plant.
    for table, set_name, keys, why in _DECLARATIONS_FIXES_REST_ON:
        rests_on = {str(k) for k in ((doc.get(table) or {}).get(set_name) or [])}
        for key in keys:
            if key not in rests_on:
                raise SensorAdmissionError(
                    f"{source}: {table}.{set_name} does not declare {key!r}, and {why}")
    if not pattern.startswith("^") or not pattern.endswith("$"):
        raise SensorAdmissionError(
            f"{source}: dpia_path_pattern {pattern!r} is not anchored at both ends, so a "
            "trivially permissive form naming {sensor} passes and the directory part is free "
            "text again")
    # R5-14: read rather than left as prose nothing checks.
    if not isinstance(doc.get("version"), int) or isinstance(doc.get("version"), bool):
        raise SensorAdmissionError(
            f"{source}: version is {doc.get('version')!r} and must be a whole number, since the "
            "table's own instruction is to bump it")
    for row in doc["admissible"]:
        if doc.get("bus_factor_scope") == "one" and row.get("granularity") != "aggregate":
            raise SensorAdmissionError(
                f"{source}: admissible declares {row.get('kind')}/{row.get('granularity')} while "
                "bus_factor_scope reads one. At a bus factor of one a cohort IS the person, and "
                "the table's own comment forbids loosening this without deriving n first")
    if doc.get("bus_factor_scope") != "one":
        raise SensorAdmissionError(
            f"{source}: bus_factor_scope is {doc.get('bus_factor_scope')!r}; the cohort "
            "exclusion's stated reason holds at one, and this module states it at one")
    # F9: the record schema lives here AND as a module constant. Nothing asserted they agree.
    declared_schema = (doc["fixed_values"].get("record") or {}).get("schema")
    if declared_schema != RECORD_SCHEMA:
        raise SensorAdmissionError(
            f"{source}: fixed_values.record.schema is {declared_schema!r} and RECORD_SCHEMA is "
            f"{RECORD_SCHEMA!r}; the two are the same fact and must not drift")
    missing = [r for r in REFUSAL_IDS if r not in declared]
    if missing:
        raise SensorAdmissionError(f"{source}: declares no sentence for {', '.join(missing)}")
    # A row that declares an id and no usable sentence used to load and then either raise an
    # uncaught KeyError at emit or print a blank FAIL line with no reason (review F3).
    for row in doc["refusals"]:
        rid = str(row.get("id"))
        sentence = " ".join(str(row.get("sentence") or "").split())
        if not sentence:
            raise SensorAdmissionError(f"{source}: refusal {rid!r} declares no sentence")
        for placeholder in ("{sensor}", "{what}"):
            if placeholder not in sentence:
                raise SensorAdmissionError(
                    f"{source}: refusal {rid!r} declares a sentence with no {placeholder} — it "
                    "would refuse without saying what it refused")
        for placeholder in re.findall(r"\{([a-z_]*)\}", sentence):
            if placeholder not in ("sensor", "what", "admissible"):
                raise SensorAdmissionError(
                    f"{source}: refusal {rid!r} declares the placeholder {{{placeholder}}}, "
                    "which nothing fills — it loads clean and raises at emit")
        if not isinstance(row.get("terminal", False), bool):
            raise SensorAdmissionError(
                f"{source}: refusal {rid!r} declares terminal {row.get('terminal')!r}, which is "
                "not a boolean")
        # R5-13: only the PRE-LADDER batch consults the flag, so marking anything else terminal
        # was decorative on nine of the refusals. The table may only mark terminal what the code
        # actually evaluates terminally.
        if row.get("terminal") and rid not in _TERMINAL_CAPABLE:
            raise SensorAdmissionError(
                f"{source}: refusal {rid!r} is marked terminal and this module never evaluates "
                f"it before the ladder (those that are: {', '.join(_TERMINAL_CAPABLE)}), so the "
                "flag would be decorative")
        if rid in _TERMINAL_REQUIRED and not row.get("terminal"):
            raise SensorAdmissionError(
                f"{source}: refusal {rid!r} is not marked terminal. It must be: without it this "
                "module walks the ethics gate for a record that names a person and computes a "
                "proportionality ratio for it, which is a PRICE on sensing a named individual "
                "and the one thing ticket 31 must never build")
        if not sentence.startswith(f"REFUSED {rid}:"):
            raise SensorAdmissionError(
                f"{source}: refusal {rid!r} declares a sentence that does not open "
                f"'REFUSED {rid}:', so the gate could not read the id off the line")
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
    if _looks_like_an_email(text):
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

    `scan_names=False` scans VALUES only. Round-5 finding R5-9: this used to say it was used on
    a DPIA record, and no caller does that -- the DPIA is scanned WITH its keys, like the
    admission record and every role file. The two callers that pass it are the party-artefact
    reader and the scenario reader, whose documents have no closed key set and where `note:` is
    a legitimate key.
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



# -- the closed key sets (review F1) --------------------------------------------------------------

class Unreadable(NamedTuple):
    """Served bytes this check will not read, and why. Never a silent None: a document the
    parser could not be trusted with is a FAIL row for that file, not an absence."""

    path: str
    why: str


def load_served(path: str, text: str) -> Any:
    """Parse bytes an adopter SERVES, refusing a duplicate mapping key.

    Re-check R1. `yaml.safe_load` silently discards a repeated key, last one wins, so the closed
    key sets closed the PARSED document and not the served bytes the whole design rests on. A
    served record reading

        senses_role: <a person's name> <an email address>
        senses_role: platform-engineer

    was ADMITTED with a green PASS: the parser threw the first line away before
    `identifier_in_value` — whose whole job is that email shape — ever saw it. `StrictLoader`
    (`twin/strict_yaml.py`, lifted from ticket 93's clock rather than forked) refuses it.

    Re-check R4: the exception is caught BROADLY, not as `yaml.YAMLError` alone. A `fields:`
    nested 500 deep blows the parser's stack, and `RecursionError` is not a YAMLError, so it
    propagated out of the reader and aborted the grading of every other adopter.
    """
    try:
        return yaml.load(text, Loader=StrictLoader)
    except Exception as exc:  # noqa: BLE001 -- see R4 above; a reader must not abort the run
        key = duplicate_key(exc)
        if key is not None:
            return Unreadable(path, f"duplicate key {key} in the served bytes: PyYAML keeps the "
                                    "last, so the document a reader sees is not the document a "
                                    "parser builds")
        return Unreadable(path, f"the served bytes are not YAML this check will read "
                                f"({exc.__class__.__name__})")


_SCALAR = (str, int, float, bool, type(None))
_TYPE_NAMES = {"bool": "a boolean", "number": "a number"}


def closed_document_problems(node: Any, rule: dict[str, Any], set_name: str = "record",
                             where: str = "") -> list[tuple[str, str]]:
    """`(refusal id, what)` for every way this document is not the shape the table declares.

    Re-check G1, 2026-09-09. The first cut walked a hand-enumerated list of ELEVEN PATHS, so any
    mapping sitting under a DECLARED key that had no closed set of its own was never reached:
    `notice.published_at: {holder: <a name>}` and `ladder.purpose.will_act: 'agreed with <a
    name>'` were both ADMITTED with a green PASS at a real served ref, the second because
    `ethics_gate._check_purpose` only tests `will_act` for truthiness. A whitelist of paths is
    not a closure of a document.

    This is the closure. Every key a set declares is a nested mapping, a list of nested
    mappings, a list of scalars, or -- the default the enumeration missed -- a SCALAR, and a
    typed slot is checked for its type. It is also total: it never calls `.get()` on anything it
    has not first shown to be a mapping, so a type-confused record (`dpia:` as a list) comes back
    as a refusal instead of the `AttributeError` that used to abort the whole estate run at one
    adopter's malformed file (re-check G2).

    YAML anchors and merge keys need no case of their own: `yaml.safe_load` expands `<<:` into
    real keys before this ever runs, so a merged-in key is caught as undeclared like any other.
    """
    out: list[tuple[str, str]] = []
    if not isinstance(node, dict):
        out.append(("key-not-declared",
                    f"{where or 'the record'} is a {type(node).__name__} where the table declares "
                    f"a {set_name} mapping"))
        return out
    allowed = {str(k) for k in rule["closed_keys"][set_name]}
    maps = rule["nested_maps"].get(set_name) or {}
    lists_ = rule["nested_lists"].get(set_name) or {}
    scalar_lists = set(rule["scalar_lists"].get(set_name) or [])
    typed = rule["typed_keys"].get(set_name) or {}
    fixed = (rule.get("fixed_values") or {}).get(set_name) or {}
    listed = ", ".join(sorted(allowed))
    # Re-check R3: the closure graded the shape of keys that were PRESENT and never that a
    # required one was there, and `ethics_gate` indexes these slots with `[]`.
    here = (where + ".") if where else ""
    for required in (rule.get("required_keys") or {}).get(set_name) or []:
        if str(required) not in {str(k) for k in node}:
            out.append(("required-key-missing",
                        f"{here}{required} is not there, and the {set_name} set declares it "
                        "required"))
    for wanted in (rule.get("non_empty") or {}).get(set_name) or []:
        if str(wanted) in {str(k) for k in node} and not node[wanted]:
            out.append(("required-key-missing",
                        f"{here}{wanted} is empty, and the {set_name} set declares it required "
                        "and non-empty: an empty one passes the rung it feeds vacuously"))
    for key, value in node.items():
        name = str(key)
        path = f"{where}.{name}" if where else name
        if name not in allowed:
            out.append(("key-not-declared",
                        f"the key {path!r} is not one this table declares "
                        f"(the {set_name} keys are: {listed})"))
            continue
        if name in maps:
            out += closed_document_problems(value, rule, maps[name], path)
        elif name in lists_:
            if not isinstance(value, list):
                out.append(("key-not-declared",
                            f"the key {path!r} holds a {type(value).__name__} where the table "
                            f"declares a list of {lists_[name]} mappings"))
            else:
                for index, item in enumerate(value):
                    out += closed_document_problems(item, rule, lists_[name], f"{path}[{index}]")
        elif name in scalar_lists:
            if not isinstance(value, list):
                out.append(("key-not-declared",
                            f"the key {path!r} holds a {type(value).__name__} where the table "
                            "declares a list of scalars"))
            else:
                for index, item in enumerate(value):
                    if not isinstance(item, _SCALAR):
                        out.append(("key-not-declared",
                                    f"the item at {path}[{index}] holds a "
                                    f"{type(item).__name__}, and the table declares no key set "
                                    "for it"))
        elif not isinstance(value, _SCALAR):
            out.append(("key-not-declared",
                        f"the key {path!r} holds a {type(value).__name__}, and the table declares "
                        "no key set for it"))
        elif name in fixed:
            if value != fixed[name]:
                out.append(("value-not-the-declared-shape",
                            f"the key {path!r} holds {value!r}, and the table fixes it at "
                            f"{fixed[name]!r}"))
        elif name in typed:
            want = str(typed[name])
            wrong = (want == "bool" and not isinstance(value, bool)) or (
                want == "number" and (isinstance(value, bool)
                                      or not isinstance(value, (int, float))))
            if wrong:
                out.append(("value-not-the-declared-shape",
                            f"the key {path!r} holds {value!r}, and the table declares "
                            f"{_TYPE_NAMES.get(want, want)}"))
    return out


def people_file_problems(filename: str, doc: Any, rule: dict[str, Any]) -> list[str]:
    """What is wrong with one role file in an adopter's people register.

    Review F2, 2026-09-09: leg 2 used to scan the document's keys and values for the token list
    only, so `held_by: <a full name>` passed, and a register replaced with `people/<a person's
    name>.yaml` carrying that as its `id` passed too — neither the filename nor the id was ever
    read. All three are read here, and the key set is closed the way the record's now is.

    NAMED LIMIT, and it is why this function's callers must not claim more: a role id that is
    simply a person's name in plain words matches no token and no value shape. No rule here reads
    English. What this refuses is an undeclared key, an identifier-SHAPED id, filename, key or
    value, and a role file that says nothing about what it is accountable for.
    """
    if not isinstance(doc, dict):
        return [f"{filename}: is not a mapping, so it is not a role file"]
    problems = [f"{filename}: {what}"
                for _rid, what in closed_document_problems(doc, rule, "people_file", "")]
    stem = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    token = identifier_in_name(stem)
    if token is not None:
        problems.append(f"{filename}: is named after {token!r}, which names an individual")
    role_id = str(doc.get("id", "")).strip()
    if not role_id:
        problems.append(f"{filename}: declares no id")
    else:
        token = identifier_in_name(role_id)
        if token is not None:
            problems.append(f"{filename}: declares the id {role_id!r} (the word {token!r}), "
                            "which names an individual")
    for shape in individual_problems(doc):
        problems.append(f"{filename}: carries {shape}")
    if not str(doc.get("role", "")).strip():
        problems.append(f"{filename}: says what it is accountable for nowhere, so "
                        "'a role, never a person' rests on the id alone")
    return problems


# -- grading one record ---------------------------------------------------------------------------

def _missing_dpia(text: str | None, path: str, sensor: str,
                  rule: dict[str, Any]) -> tuple[list[str], dict[str, Any]]:
    """What is wrong with the DPIA record at `path`, and whatever of it could be read."""
    if not path:
        return ["the record names no DPIA path at all"], {}
    if text is None:
        return [f"no DPIA record at {path}"], {}
    doc = load_served(path, text)
    if isinstance(doc, Unreadable):
        return [f"the DPIA record at {path}: {doc.why}"], {}
    if not isinstance(doc, dict):
        return [f"the DPIA record at {path} is not a mapping"], {}
    problems: list[str] = []
    # Review F1: a DPIA filed under somebody's name is a DPIA about a person. The basename is the
    # sensor's own id, which is a row in a closed table, so there is nothing to name it after.
    if sensor:
        pattern = str(rule["dpia_path_pattern"]).replace("{sensor}", re.escape(sensor))
        if not re.match(pattern, path):
            problems.append(
                f"the DPIA record at {path} is not filed at {pattern} — round-4 F6: deriving "
                "only the BASENAME left the directory part free text, which is a place a name "
                "can live")
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
    return problems, doc


def grade_record(
    record: dict[str, Any],
    *,
    people: Iterable[str],
    scenarios: Iterable[str],
    dpia_reader: Callable[[str], str | "Unreadable" | None] | None = None,
    rule: dict[str, Any] | None = None,
    sensors_path: Path | None = None,
) -> dict[str, Any]:
    """Grade one admission record. Returns `{"sensor", "scenario_class", "admitted", "refusals",
    "terminal", "ladder"}`; never raises on a bad record, because a refusal a caller must handle
    is the product, not an exception a caller might not.

    `people` is the adopter's own people register and `scenarios` the ids of the scenarios it
    SERVES for this class. Both are required keyword arguments, with no default: a default of
    "not checked" is how a refusal comes to be silently skipped.

    A TERMINAL refusal is reported alone, and `ladder` comes back None. Which refusals are
    terminal is read from the table at the branch (`is_terminal()`), not decided here — review
    F4 found the field decorative because the branch was hardcoded. Two are terminal today:
    a record that names or identifies an individual, and a record carrying a key the table does
    not declare. Computing a proportionality ratio for either would put a price on sensing a
    named person, and an undeclared key is exactly where a person arrives.
    """
    rule = rule or load_rule()
    known_people = {str(p) for p in people}
    served_scenarios = {str(s) for s in scenarios}
    safe: dict[str, Any] = record if isinstance(record, dict) else {}
    sensor = str(safe.get("sensor", "")).strip() if isinstance(safe.get("sensor"), _SCALAR) else ""
    declared_class = str(safe.get("scenario_class", "")).strip()

    def out(rid: str, what: str, admissible_list: str = "") -> str:
        return refusal(rule, rid, sensor, what, admissible_list)

    # -- the document's own shape, FIRST -----------------------------------------------------
    # Re-check G2: this runs before any `.get()` chain, so a type-confused record (`dpia:` as a
    # list) is refused rather than aborting the whole estate run with an AttributeError at one
    # adopter's malformed file. `closed_document_problems` calls `.get()` on nothing it has not
    # first shown to be a mapping.
    shape: list[tuple[str, str]] = closed_document_problems(record, rule)
    dpia_block = safe.get("dpia")
    dpia_path = ""
    if isinstance(dpia_block, dict) and isinstance(dpia_block.get("record"), str):
        dpia_path = dpia_block["record"].strip()
    read = dpia_reader(dpia_path) if (dpia_reader and dpia_path) else None
    dpia_text: str | None = read if isinstance(read, str) else None
    dpia_doc: dict[str, Any] = {}
    if isinstance(read, Unreadable):
        shape.append(("duplicate-key" if "duplicate key" in read.why else "no-dpia-record",
                      f"the DPIA record at {dpia_path} is served and {read.why}"))
    elif dpia_text is not None:
        loaded = load_served(dpia_path, dpia_text)
        if isinstance(loaded, Unreadable):
            shape.append(("duplicate-key" if "duplicate key" in loaded.why else "no-dpia-record",
                          f"the DPIA record at {dpia_path}: {loaded.why}"))
        elif isinstance(loaded, dict):
            dpia_doc = loaded
            shape += [(rid, f"in the DPIA record, {what}")
                      for rid, what in closed_document_problems(dpia_doc, rule, "dpia_record")]

    problems: list[tuple[str, str]] = (
        [("names-or-identifies-an-individual", w) for w in individual_problems(safe)]
        + [("names-or-identifies-an-individual",
            f"the DPIA record at {dpia_path} carries {w}") for w in individual_problems(dpia_doc)]
        + shape
    )
    listed = {"key-not-declared": ", ".join(rule["closed_keys"]["record"])}
    terminal = [out(rid, what, listed.get(rid, "")) for rid, what in problems
                if is_terminal(rule, rid)]
    if terminal:
        # Re-check G3: the clause is appended ONCE, to the batch, instead of ending every
        # sentence in it.
        clause = " ".join(str(rule["terminal_batch_clause"]).split())
        terminal[-1] = f"{terminal[-1]} {clause}"
        return {
            "sensor": sensor,
            "scenario_class": declared_class or rule["scenario_class"],
            "refusals": terminal,
            "terminal": True,
            "ladder": None,
            "admitted": False,
        }

    refusals: list[str] = [out(rid, what, listed.get(rid, "")) for rid, what in problems]
    admissible = admissible_pairs(rule)
    admissible_text = ", ".join(f"{k}/{g}" for k, g in admissible)

    # this table rules one class, and says which one it graded (review F5).
    if declared_class != rule["scenario_class"]:
        refusals.append(out("not-this-scenario-class", declared_class or "(none)",
                            rule["scenario_class"]))

    # sensor id: `sensors.yaml` stays the closed table, reported as a refusal rather than raised.
    known_sensors = ethics_gate.sensor_ids(sensors_path)
    sensor_named = sensor in known_sensors
    if not sensor_named:
        refusals.append(out("sensor-not-named",
                            f"{sensor!r} is not a named sensor "
                            f"(have: {', '.join(known_sensors)})"))

    # the scenario this sensor feeds is one the adopter serves, and the ladder walks the same one.
    scenario = str(safe.get("scenario", "")).strip()
    served_text = ", ".join(sorted(served_scenarios)) or "none"
    if scenario not in served_scenarios:
        refusals.append(out("scenario-not-served", repr(scenario or "(none)"), served_text))
    raw_ladder = safe.get("ladder")
    ladder_doc: dict[str, Any] = raw_ladder if isinstance(raw_ladder, dict) else {}
    purpose_scenario = str((ladder_doc.get("purpose") or {}).get("scenario", "")).strip()
    if purpose_scenario != scenario:
        refusals.append(out(
            "scenario-not-served",
            f"{scenario!r} while its ladder's purpose rung walks {purpose_scenario!r}, so one of "
            "the two is not what runs", served_text))

    # (c) kind and granularity, declared and as the ladder walks them.
    kind, gran = str(safe.get("kind", "")), str(safe.get("granularity", ""))
    if (kind, gran) not in admissible:
        refusals.append(out("kind-not-admissible", f"{kind}/{gran}", admissible_text))
    necessity = ladder_doc.get("necessity") or {}
    walked = (str(necessity.get("kind", "")), str(necessity.get("level", "")))
    if walked != (kind, gran):
        refusals.append(out(
            "kind-not-admissible",
            f"the record declares {kind}/{gran} and its ladder walks "
            f"{walked[0]}/{walked[1]}, so one of the two is not what runs", admissible_text))

    # the closed field set.
    fields = safe.get("fields")
    if not isinstance(fields, list) or not fields:
        refusals.append(out("field-not-admissible", "(the record declares no fields)",
                            ", ".join(rule["admissible_fields"])))
    else:
        for field in fields:
            if str(field) not in rule["admissible_fields"]:
                refusals.append(out("field-not-admissible", str(field),
                                    ", ".join(rule["admissible_fields"])))

    # (d) covert sensing. `told` is a LIST OF ROLE IDS, never prose (review F1).
    notice = safe.get("notice")
    if not isinstance(notice, dict) or not notice:
        refusals.append(out("covert-sensing",
                            "the record carries no notice, so the sensed party is not told"))
    else:
        told = notice.get("told")
        if not isinstance(told, list) or not told:
            refusals.append(out(
                "covert-sensing",
                "the notice names who is told as "
                f"{type(told).__name__ if told is not None else 'nothing'} rather than a non-empty "
                "list of role ids, and prose is where a personal name arrives"))
        else:
            for role in told:
                if str(role) not in known_people:
                    refusals.append(out("role-not-registered",
                                        f"{str(role)!r} among the roles the notice says it told"))
        for field in ("published_at", "published_on"):
            if not str(notice.get(field, "")).strip():
                refusals.append(out(
                    "covert-sensing",
                    f"the notice carries no {field}, so the sensed party is not told"))
        when = str(notice.get("published_on", "")).strip()
        if when and not _DATE.match(when):
            refusals.append(out(
                "covert-sensing",
                f"the notice dates published_on {when!r}, not YYYY-MM-DD, so nothing says when "
                "anybody was told"))

    # Re-check R7/R9: two more slots a plain-words name survived in, each closed by deriving
    # rather than by scanning. A DPIA that names another sensor or another scenario is a DPIA
    # about something else.
    for field in rule["dpia_must_agree"]:
        if not dpia_doc:
            break
        mine = {"sensor": sensor, "scenario": str(safe.get("scenario", "")).strip()}[field]
        theirs = str(dpia_doc.get(field, "")).strip()
        if theirs != mine:
            refusals.append(out(
                "value-not-the-declared-shape",
                f"the DPIA record at {dpia_path} is filed for {field} {theirs!r} and this record "
                f"names {mine!r}, so it is a DPIA about something else"))
    # The one admissible sensor for this class reads a commit graph, so it declares NO
    # monitoring channel; a channel is free prose the ICO triage would then act on.
    channels = (ladder_doc.get("dpia") or {}).get("channels") if isinstance(
        ladder_doc.get("dpia"), dict) else None
    for channel in channels or []:
        if str(channel) not in [str(c) for c in rule["admissible_channels"]]:
            refusals.append(out(
                "value-not-the-declared-shape",
                f"its ladder declares the monitoring channel {str(channel)!r}, and this class "
                f"declares {rule['admissible_channels'] or 'none'}"))

    # (b) the DPIA record. Skipped when the bytes were served but could not be read: that is
    # already reported above, and "no DPIA record at ..." would be a different, false claim
    # (R5-10).
    if not isinstance(read, Unreadable):
        dpia_problems, _ = _missing_dpia(dpia_text, dpia_path, sensor, rule)
        for problem in dpia_problems:
            refusals.append(out("no-dpia-record", problem))

    # (e) the roles register.
    senses = str(safe.get("senses_role", "")).strip()
    if not senses:
        refusals.append(out("role-not-registered", "no sensed role at all"))
    elif senses not in known_people:
        refusals.append(out("role-not-registered", f"the sensed role {senses!r}"))
    signed_off = str(dpia_doc.get("completed_by", "")).strip()
    if signed_off and signed_off not in known_people:
        refusals.append(out("role-not-registered",
                            f"{signed_off!r} as the role accountable for the DPIA"))

    # the existing ladder, last, and only for a sensor the closed table names.
    ladder: dict[str, Any] | None = None
    if sensor_named and ladder_doc:
        payload = {"sensor": {"id": sensor, "name": sensor}, **ladder_doc}
        try:
            ladder = ethics_gate.admit(payload)
        except ethics_gate.EthicsGateError as exc:
            # F12: this was reported as `sensor-not-named` whatever it was about, so a ladder
            # missing a whole rung was refused with words saying the sensor id is not
            # registered, when it is.
            refusals.append(out("ladder-could-not-walk", str(exc)))

    admitted = not refusals and ladder is not None and bool(ladder["admitted"])
    if not admitted and not refusals:
        # F11: a record could be counted FAIL with no line saying why, when the ladder stopped
        # and nothing else had anything to add.
        # R5-6: this read `stopped_at` off the TOP level of the gate's result, where the key
        # does not exist -- it lives one level down, which the very next line already reached
        # into -- so every ladder refusal read "stopped at the DPIA gate" whatever stopped it.
        raw_rungs = (ladder or {}).get("ladder") or {}
        ladder_result: dict[str, Any] = raw_rungs if isinstance(raw_rungs, dict) else {}
        stopped = ladder_result.get("stopped_at")
        rungs = ladder_result.get("rungs")
        detail = rungs[-1]["justification"] if rungs else "the ethics gate did not admit it"
        where_it_stopped = (f"the {stopped} rung" if stopped
                            else "the DPIA gate, the ladder having passed")
        refusals.append(out(
            "ladder-could-not-walk", f"the ethics gate stopped at {where_it_stopped}: {detail}"))
    return {
        "sensor": sensor,
        "scenario_class": declared_class or rule["scenario_class"],
        "refusals": refusals,
        "terminal": False,
        "ladder": ladder,
        "admitted": admitted,
    }


def limits(rule: dict[str, Any] | None = None) -> list[str]:
    """What this check refuses and what it does NOT, derived from the table rather than typed.

    Re-check R7: the printed block was stale in BOTH directions. It never mentioned
    `value-not-the-declared-shape` or a mapping under a declared key, both new and terminal, and
    its list of places a plain-words name survives was incomplete — the re-check planted one into
    `record.schema`, the DPIA's `sensor:` and `scenario:` and `ladder.dpia.channels[]` and
    watched each graded green. Four of those five are now CLOSED by deriving the value instead of
    scanning it, so this block is generated from the same table that closes them and cannot drift
    from it again.
    """
    rule = rule or load_rule()
    # R5-8, narrowed in round 6: read off the CALL SITES, not the table. It establishes that a
    # literal call site exists, not that the id is reachable, so the sentence says EMIT.
    refuses = ", ".join(sorted(emitted_refusal_ids()))
    survives = [f"a DPIA's {f}" for f in rule["free_prose_fields"]]
    survives += ["a notice's published_at path", "a role id or a role file's own role: prose",
                 "any other prose in a served scenario file or a party.yaml"]
    return [
        "this run grades the RULE and any admission record an adopter serves. Nothing here "
        "observes a sensor running or a person; no sensing substrate exists in this estate.",
        f"the refusals it can emit are: {refuses}. That list is read off this module's own call "
        "sites, so a refusal the table declares and no call site spells is refused at load; it "
        "does not prove every one of them is reachable.",
        "served bytes are parsed with a loader that refuses a DUPLICATE mapping key, so the "
        "document this check grades is the document a reader sees, not the one PyYAML builds "
        "by keeping the last of two identical keys.",
        f"the three scanned directories -- people, scenarios and sensor-admissions -- read both "
        f"{' and '.join(YAML_SUFFIXES)}, and anything else under them is a named row. The DPIA "
        "path pattern accepts only .yaml, so a DPIA served under the short spelling is refused "
        "as missing: fail-closed, and named here because the asymmetry is real.",
        "the identifier scan covers FIVE served documents and no others: the admission record, "
        "the DPIA record it names and every role file in the people register are scanned for "
        "identifier-shaped KEYS AND VALUES; every "
        f"{SCENARIO_CLASS} scenario file and every readable party.yaml, whatever roles it "
        "claims, are scanned for identifier-shaped "
        "VALUES only, because their shape is not closed and `note:` is a legitimate key there. "
        "Within those it refuses a key the "
        "table does not declare, a mapping or list under a declared key, a slot whose type or "
        "fixed value the table declares, a required or non-empty key that is absent, an "
        "identifier-SHAPED filename, id, key or value, an email address and a UK national "
        "insurance number.",
        "no rule here reads English, so within those documents a personal name written in plain "
        "words survives in " + "; ".join(survives) + ", and is refused by nothing.",
    ]


# -- the served artefact --------------------------------------------------------------------------

def display(path: str) -> str:
    """A path rendered so printing it cannot kill the run (round-6 F4).

    A genuinely non-UTF-8 path decodes with `surrogateescape`, is read and graded correctly, and
    was then killed on the way OUT when the estate grader printed it -- outside every guard the
    earlier rounds installed, and reopening round-4 F2 at the path layer. The run went red rather
    than green, so nothing was hidden, but it measured nothing.
    """
    return str(path).encode("utf-8", "surrogateescape").decode("utf-8", "replace")


def served(unit: Path, path: str) -> str | Unreadable | None:
    """The bytes GitHub serves at `origin/main:<path>`. Never the working tree: an uncommitted
    admission record is not one an adopter has published.

    Three outcomes, and the middle one is round-4 finding F2: `None` when `origin/main` serves
    nothing at that path, an `Unreadable` when it serves bytes that are not UTF-8, and the text
    otherwise. This used to decode with `text=True`, so a served file of
    `b'id: \xff\xfe\x00binary\nrole: x\n'` raised an uncaught `UnicodeDecodeError` inside
    `subprocess` — in the layer ABOVE the per-record guard, so it aborted the grading of every
    other adopter, and its traceback went to stderr where the verify script's `tee` never saw it.
    """
    out = subprocess.run(["git", "-C", str(unit), "show", f"origin/main:{path}"],
                         capture_output=True)
    if out.returncode != 0:
        return None
    try:
        return out.stdout.decode("utf-8")
    except UnicodeDecodeError as exc:
        return Unreadable(path, f"the served bytes are not UTF-8 ({exc})")


def served_paths(unit: Path) -> list[str]:
    """Every path `origin/main` serves.

    Round-5 finding R5-1, and it is one level OUT from the document again. `git ls-tree
    --name-only` **C-quotes** any path carrying a non-ASCII byte, so this handed back
    `'"twin/orgs/alpha/people/rota-na\\303\\257ve.yaml"'` — quotes and backslashes included — and
    `served()` on that string returned None. Every such artefact was SILENTLY DROPPED from legs 2
    and 3: a role file whose id was an email refused at an ASCII name and passed green at an
    accented one, and a byte-identical admission record one directory over turned an exit 1 into
    `exit 3, 0 declare a sensor admission`. The surrogate-escape decode did not help and the
    docstring that said it did was wrong: git quotes before Python sees the bytes.

    `-z` is the fix, because git never quotes under the null-separated form. The
    surrogate-escape decode stays for the genuinely non-UTF-8 name, which it does handle.
    """
    out = subprocess.run(
        ["git", "-C", str(unit), "ls-tree", "-r", "-z", "--name-only", "origin/main"],
        capture_output=True)
    if out.returncode != 0:
        return []
    text = out.stdout.decode("utf-8", errors="surrogateescape")
    return [name for name in text.split("\0") if name]


def ref_resolves(unit: Path) -> bool:
    """Whether `origin/main` resolves in this unit at all (R5-2).

    `served()` returns None both for "this tree carries no such file" and for "this is not a
    repository, or its remote-tracking main is gone". Reading the second as the first is how a
    unit whose repository was damaged came to be dropped in silence, beside a real adopter.
    """
    # Round-6 F1: `rev-parse --verify -q origin/main` proves a ref PARSES, not that it POINTS
    # AT ANYTHING. For a pruned clone, a ref naming a sha the repository never had, or a ref
    # that is a blob, it printed a sha while `ls-tree` said "not a tree object" -- and the unit
    # landed in exactly the silent skip R5-2 was written to close. Peeling to a commit is what
    # actually asks the question.
    out = subprocess.run(
        ["git", "-C", str(unit), "rev-parse", "--verify", "-q", "origin/main^{commit}"],
        capture_output=True)
    return out.returncode == 0


def served_sha(unit: Path) -> str | None:
    out = subprocess.run(["git", "-C", str(unit), "rev-parse", "--short", "origin/main"],
                         capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def adopters(estate: Path,
             unreadable: dict[str, Unreadable] | None = None) -> list[str]:
    """Every unit whose SERVED party artefact claims the adopter role, and — in `unreadable` —
    every unit that SERVES a party artefact this check could not read.

    Round-4 finding F1, a regression the strict loader caused. This used to `continue` in
    silence on anything that was not a dict, so an adopter whose `party.yaml` carried a
    duplicated key VANISHED from the run: its scenario note, its people register and a record
    naming an individual all went ungraded, and a red estate printed `PASS: 1 adopters read`
    with the dropped adopter named nowhere. The pre-existing half was the same shape
    (`except yaml.YAMLError: continue`).

    Round-5 finding R5-2 closed the other half: a unit whose `origin/main` does not resolve --
    a directory that is not a git repository, or one whose remote-tracking main is gone -- used
    to land in the same silent skip, so a DAMAGED real unit vanished beside a healthy one. The
    ref is resolved first, and such a unit is its own named row.

    The silent skip that REMAINS is the correct one, and it is now narrower than the earlier
    docstring claimed: a directory with no git repository in it at all, and a repository that
    serves no `party.yaml`, are not parties. A scratch directory lands in the first.
    """
    found: list[str] = []
    unreadable = {} if unreadable is None else unreadable
    if not estate.is_dir():
        return found
    for unit in sorted(p for p in estate.iterdir() if p.is_dir()):
        where = f"{unit.name}/party.yaml"
        # R5-2: a unit whose REF does not resolve is a damaged repository, not a directory that
        # happens to carry no party file. The ref is resolved first so the two are distinct.
        if not ref_resolves(unit):
            # A unit that carries a party artefact or a twin overlay ON DISK but whose ref does
            # not resolve is a DAMAGED repository, not an empty directory: it is named. A bare
            # scratch directory carries neither and stays the correct silent skip.
            looks_like_a_unit = (unit / ".git").exists() or (unit / "party.yaml").exists() \
                or (unit / "twin").is_dir()
            if looks_like_a_unit:
                unreadable[unit.name] = Unreadable(
                    f"{unit.name}", "origin/main does not resolve in this unit: the repository "
                    "or its remote-tracking main cannot be read, so nothing it serves was graded")
            continue
        paths = served_paths(unit)
        if not paths:
            # F1, belt and braces: the ref resolved and nothing came back.
            unreadable[unit.name] = Unreadable(
                unit.name, "origin/main resolves and its tree came back empty, so nothing this "
                           "unit serves could be read")
            continue
        text = served(unit, "party.yaml")
        if text is None:
            # F2: a unit that SERVES an org tree and no readable adopter claim used to vanish
            # with all of it -- register, key-person scenario and admission record. Leg 1 states
            # the opposite principle for the scenario, and for the same reason: if it can vanish,
            # the count moves and nothing goes red. A repository serving no org tree at all stays
            # the correct silent skip.
            org_prefix = "twin/orgs/"
            if any(p.startswith(org_prefix) for p in paths):
                served_orgs = sorted({p.split("/")[2] for p in paths
                                      if p.startswith(org_prefix) and p.count("/") >= 2})
                unreadable[unit.name] = Unreadable(
                    unit.name, f"serves a twin org tree ({', '.join(served_orgs)}) and no "
                               "readable party.yaml, so it stopped saying it is a party while "
                               "still serving everything this check grades")
            continue
        if isinstance(text, Unreadable):
            unreadable[unit.name] = Unreadable(where, text.why)
            continue
        doc = load_served(where, text)
        if isinstance(doc, Unreadable):
            unreadable[unit.name] = doc
            continue
        if not isinstance(doc, dict):
            unreadable[unit.name] = Unreadable(
                where, f"the served party artefact is a {type(doc).__name__}, not a mapping")
            continue
        # R5-7: the value scan used to run only inside the adopter branch, so five of the eight
        # real units were never scanned and the generated block's "every party file" was false.
        # It is cheap and there is no reason to scope it.
        for problem in individual_problems(doc, scan_names=False):
            unreadable[f"{unit.name}::{len(unreadable)}"] = Unreadable(
                where, f"carries {problem}")
        if "adopter" in (doc.get("roles") or []):
            found.append(unit.name)
    return found


def people_files(estate: Path, org: str) -> dict[str, Any]:
    """Every role file in the adopter's people register, BY SERVED PATH.

    By path and not by id, because review F2 found that reading the register into an id-keyed
    dict threw away the filename — and a register replaced with a file named after a person,
    carrying that as its id, was invisible to every rule the check had.
    """
    prefix = PEOPLE_DIR.format(org=org) + "/"
    unit = estate / org
    files: dict[str, Any] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix):
            continue
        if not path.endswith(YAML_SUFFIXES):
            files[path] = Unreadable(path, "is under the people register and is neither "
                                           f"{' nor '.join(YAML_SUFFIXES)}, so nothing read it")
            continue
        text = served(unit, path)
        if text is None:
            continue
        files[path] = text if isinstance(text, Unreadable) else load_served(path, text)
    return files


def people_register(estate: Path, org: str) -> dict[str, dict[str, Any]]:
    """The adopter's own roles register, keyed by role id, read at `origin/main`."""
    register: dict[str, dict[str, Any]] = {}
    for doc in people_files(estate, org).values():
        if isinstance(doc, dict) and doc.get("id"):
            register[str(doc["id"])] = doc
    return register


def key_person_scenarios(estate: Path, org: str,
                         unreadable: dict[str, Unreadable] | None = None
                         ) -> dict[str, dict[str, Any]]:
    prefix = SCENARIOS_DIR.format(org=org) + "/"
    unit = estate / org
    unreadable = {} if unreadable is None else unreadable
    out: dict[str, dict[str, Any]] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix):
            continue
        if not path.endswith(YAML_SUFFIXES):
            unreadable[path] = Unreadable(path, "is under the scenarios directory and is neither "
                                                f"{' nor '.join(YAML_SUFFIXES)}")
            continue
        text = served(unit, path)
        if text is None:
            continue
        doc = text if isinstance(text, Unreadable) else load_served(path, text)
        if isinstance(doc, Unreadable):
            unreadable[path] = doc
            continue
        if isinstance(doc, dict) and doc.get("class") == SCENARIO_CLASS:
            # F6: a served scenario file has no closed key set, so an EMAIL ADDRESS lived in it
            # unrefused and falsified the limits block's own sentence. Its shape is ticket 11's
            # and varies, so it is not closed; the VALUE scan is run over it (`scan_names=False`,
            # because `note:` is a legitimate key here and the token list was written for a
            # closed field set), and the limits block says exactly that.
            for problem in individual_problems(doc, scan_names=False):
                unreadable[f"{path}::{len(unreadable)}"] = Unreadable(path, f"carries {problem}")
            out[path] = doc
    return out


def admission_records(estate: Path, org: str) -> dict[str, Any]:
    prefix = ADMISSIONS_DIR.format(org=org) + "/"
    unit = estate / org
    out: dict[str, Any] = {}
    for path in served_paths(unit):
        if not path.startswith(prefix):
            continue
        if not path.endswith(YAML_SUFFIXES):
            out[path] = Unreadable(path, "is under the sensor-admissions directory and is "
                                         f"neither {' nor '.join(YAML_SUFFIXES)}")
            continue
        text = served(unit, path)
        if text is None:
            out[path] = Unreadable(path, "origin/main serves no bytes at this path")
            continue
        doc = text if isinstance(text, Unreadable) else load_served(path, text)
        out[path] = doc if isinstance(doc, (dict, Unreadable)) else Unreadable(
            path, f"the served bytes are a {type(doc).__name__}, not an admission record")
    return out


NOTE_SENTENCE = "A role, never a person"


def grade_estate(estate: Path, out: Callable[[str], None] = print) -> int:
    """Grade every adopter's SERVED tree. 0 observed true, 1 observed false, 3 could not look.

    Three legs, each on `origin/main`:
      1. every adopter serves a `bus-factor-key-person` scenario, it says "A role, never a
         person", and it names a role file that the served tree carries;
      2. every role file in the adopter's people register carries an id and a role, carries no
         key the table does not declare, and has no identifier-shaped filename, id, key or
         value;
      3. every admission record grades through the rule above.

    Leg 3 is the one ticket 31 exists for and it is the one that cannot look today: nothing is
    admitted, because nobody has declared a sensor. That is printed as a COUNT, never as a pass.
    """
    # Round-6 F4: one wrapper, so no print site anywhere below can kill the run on a path that
    # decoded with surrogates. `display()` is still applied where a path is embedded, so the
    # message reads sensibly; this is the belt that makes the guarantee total.
    plain = out

    def say(line: str) -> None:
        plain(display(line))

    for line in limits():
        say(f"  LIMIT: {line}")
    if not estate.is_dir():
        say(f"SKIP: no estate clone at {estate}")
        return 3
    unreadable_parties: dict[str, Unreadable] = {}
    orgs = adopters(estate, unreadable_parties)
    fail_parties = 0
    for name, why in sorted(unreadable_parties.items()):
        print_ = f"FAIL {name.split('::')[0]}: {why.path}: {why.why}"
        say(print_)
        fail_parties += 1
    if not orgs and not unreadable_parties:
        say(f"SKIP: no party in {estate} serves a party.yaml claiming the adopter role at "
            "origin/main")
        return 3

    rule = load_rule()
    fail = fail_parties
    scenarios_seen = 0
    records_seen = 0
    admitted_count = 0
    refused_count = 0
    shas: list[str] = []

    for org in orgs:
        unit = estate / org
        sha = served_sha(unit)
        shas.append(f"{org}={sha or 'unknown'}")
        files = people_files(estate, org)
        register = {str(d["id"]): d for d in files.values()
                    if isinstance(d, dict) and d.get("id")}

        # leg 2: the register itself. Widened after review F2: the file's NAME, its `id`, its
        # keys (closed set) and its values, not the keys and values alone.
        for path, doc in sorted(files.items()):
            if isinstance(doc, Unreadable):
                say(f"FAIL {org}: {path}: {doc.why}")
                fail += 1
                continue
            for problem in people_file_problems(path, doc, rule):
                say(f"FAIL {org}: {problem}")
                fail += 1
        if not register:
            say(f"FAIL {org}: serves no people register at "
                f"{PEOPLE_DIR.format(org=org)}/, so no sensor could name a registered role")
            fail += 1

        # leg 1: the scenario keeps saying it.
        #
        # An adopter serving NO scenario of this class is observed FALSE, not skipped past. All
        # three serve one today, and the note on it is this estate's only published statement
        # that a departure is sensed as a role and never as a person. If it could vanish and
        # leave this script printing "0 carry a bus-factor-key-person scenario" as a
        # could-not-look, the count would move and nothing would go red.
        unreadable_scenarios: dict[str, Unreadable] = {}
        found = key_person_scenarios(estate, org, unreadable_scenarios)
        for path, why in sorted(unreadable_scenarios.items()):
            say(f"FAIL {org}: {path}: {why.why}")
            fail += 1
        scenarios_seen += len(found)
        if not found:
            say(f"FAIL {org}: serves no {SCENARIO_CLASS} scenario under "
                f"{SCENARIOS_DIR.format(org=org)}/, so the sentence this check grades -- "
                f"{NOTE_SENTENCE!r} -- is published nowhere for this adopter")
            fail += 1
        for path, doc in sorted(found.items()):
            note = " ".join(str(doc.get("note", "")).split())
            if NOTE_SENTENCE.lower() not in note.lower():
                say(f"FAIL {org}: {path} is a {SCENARIO_CLASS} scenario whose note no longer "
                    f"says {NOTE_SENTENCE!r}")
                fail += 1
            subject = re.search(r"`people/([a-z0-9-]+)\.yaml`", note)
            if subject is None:
                say(f"FAIL {org}: {path} names no `people/<role>.yaml` subject in its note")
                fail += 1
            elif subject.group(1) not in register:
                say(f"FAIL {org}: {path} names `people/{subject.group(1)}.yaml` as its subject "
                    f"and the served people register carries {sorted(register) or 'nothing'}")
                fail += 1

        # leg 3: the admission records, if any are served.
        records = admission_records(estate, org)

        def read_dpia(dpia_path: str, u: Path = unit) -> str | Unreadable | None:
            # R5-10: this collapsed the Unreadable shape back to a null, so a DPIA that IS
            # served but is not UTF-8 was reported as "no DPIA record at ...", which is a
            # different claim.
            return served(u, dpia_path)

        for path, maybe in sorted(records.items()):
            records_seen += 1
            if isinstance(maybe, Unreadable):
                say(f"FAIL {org}: {path}: {maybe.why}")
                refused_count += 1
                fail += 1
                continue
            # Re-check R4: one adopter's malformed record used to abort the grading of the whole
            # estate. The refusals above make each measured crash a refusal instead, and this
            # belt holds for anything neither the closure nor the loader anticipated: a bad file
            # is a FAIL row for that file and the other adopters are still graded.
            try:
                result = grade_record(
                    maybe, people=register.keys(),
                    scenarios=[str(s.get("id", "")) for s in found.values()
                               if isinstance(s, dict)],
                    rule=rule, dpia_reader=read_dpia)
            except Exception as exc:  # noqa: BLE001 -- see R4 above
                say(f"FAIL {org}: {path}: grading it raised {exc.__class__.__name__}: {exc}. "
                    "That is a defect in this check, not a pass for the record")
                refused_count += 1
                fail += 1
                continue
            if result["admitted"]:
                admitted_count += 1
                say(f"PASS {org}: {path}: {result['sensor']} admitted -- "
                    f"{result['ladder']['claim']['evidence']}")
            else:
                refused_count += 1
                for line in result["refusals"]:
                    say(f"FAIL {org}: {path}: {line}")
                fail += 1

    units = " ".join(shas)
    if fail:
        say(f"FAIL: {fail} observed false across {len(orgs)} adopters at origin/main "
            f"[{units}]; {scenarios_seen} {SCENARIO_CLASS} scenarios, {records_seen} admission "
            f"records ({admitted_count} admitted, {refused_count} refused)")
        return 1
    if records_seen == 0:
        say(f"SKIP: {len(orgs)} adopters read at origin/main [{units}]; {scenarios_seen} carry a "
            f"{SCENARIO_CLASS} scenario and every one still says {NOTE_SENTENCE!r}; 0 declare a "
            f"sensor admission under twin/orgs/<org>/sensor-admissions/, so 0 admission decisions "
            f"could be graded")
        return 3
    say(f"PASS: {len(orgs)} adopters read at origin/main [{units}]; {scenarios_seen} "
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
  told: [platform-engineer, platform-lead]
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
    """Git for synthetic served-ref fixtures only; never use a developer's signing key."""
    subprocess.run(["git", "-c", f"core.hooksPath={hooks}", "-c", "commit.gpgsign=false",
                    "-C", str(repo), *args],
                   check=True, capture_output=True, text=True)


def _plant(root: Path, hooks: Path, record: str | None, scenario: bool = True,
           extra_role_file: tuple[str, str] | None = None,
           extra_record: tuple[str, str] | None = None,
           org: str = "planted", party: str | None = None,
           extra_bytes: tuple[str, bytes] | None = None) -> Path:
    """A planted unit whose SERVED ref is a real `refs/remotes/origin/main`.

    `org` names the unit, so several can be planted into one estate directory; `party` overrides
    the served `party.yaml` bytes, and `extra_bytes` writes a file that is not text at all.
    """
    estate = root / "estate"
    unit = estate / org
    (unit / f"twin/orgs/{org}/people").mkdir(parents=True, exist_ok=True)
    (unit / f"twin/orgs/{org}/scenarios").mkdir(parents=True, exist_ok=True)
    (unit / f"twin/orgs/{org}/dpia").mkdir(parents=True, exist_ok=True)
    (unit / "party.yaml").write_text(
        party if party is not None else f"party: {org}\nroles: [adopter]\n", encoding="utf-8")
    (unit / f"twin/orgs/{org}/people/platform-engineer.yaml").write_text(
        "id: platform-engineer\nrole: On call for the planted namespace.\n", encoding="utf-8")
    (unit / f"twin/orgs/{org}/people/platform-lead.yaml").write_text(
        "id: platform-lead\nrole: Accountable for the planted DPIA.\n", encoding="utf-8")
    if scenario:
        (unit / f"twin/orgs/{org}/scenarios/key-person-2026.yaml").write_text(
            _SCENARIO, encoding="utf-8")
    (unit / f"twin/orgs/{org}/dpia/bus-factor-structural-aggregate.yaml").write_text(
        _GOOD_DPIA.replace("planted", org), encoding="utf-8")
    if extra_role_file is not None:
        name, body = extra_role_file
        (unit / f"twin/orgs/{org}/people/{name}").write_text(body, encoding="utf-8")
    admissions = unit / f"twin/orgs/{org}/sensor-admissions"
    if record is not None:
        admissions.mkdir(parents=True, exist_ok=True)
        (admissions / "bus-factor-structural-aggregate.yaml").write_text(record, encoding="utf-8")
    if extra_record is not None:
        admissions.mkdir(parents=True, exist_ok=True)
        (admissions / extra_record[0]).write_text(extra_record[1], encoding="utf-8")
    if extra_bytes is not None:
        target = unit / extra_bytes[0]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(extra_bytes[1])
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
    planted = 0

    def reader(text: str | None) -> Callable[[str], str | None]:
        return lambda path: text if path.endswith("bus-factor-structural-aggregate.yaml") else None

    def expect(what: str, record: dict[str, Any], rid: str | None,
               dpia: str | None = _GOOD_DPIA) -> None:
        nonlocal failures, planted
        planted += 1
        result = grade_record(record, people=people, scenarios=("key-person-2026",),
                              rule=rule, dpia_reader=reader(dpia))
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
    ladder["necessity"] = {"kind": "behavioural", "level": "individual",
                           "alternatives": [{"kind": "structural", "level": "aggregate"}]}
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
    # Review F1, 2026-09-09. Each of these was ADMITTED with a green PASS before the record's key
    # set was closed. The plants are the KEYS the review used; no value here is a name.
    for key in ("maintained_by", "escalation_contact", "github", "owner", "stakeholders",
                "context", "held_by"):
        expect(f"an undeclared record key {key!r} is refused terminally",
               variant(**{key: "<a value the grader never reads>"}), "key-not-declared")
    for key in ("\u0435mployee_id", "e\u200bmployee_id"):
        expect("a homoglyph key the name scanner cannot see is refused by the closed set",
               variant(**{key: 1}), "key-not-declared")
    expect("an undeclared key in the DPIA record is refused terminally", variant(),
           "key-not-declared", dpia=_GOOD_DPIA + "reviewed_by: <never read>\n")
    notice = copy.deepcopy(good["notice"])
    expect("a notice naming who was told in prose rather than role ids is refused terminally",
           variant(notice={**notice, "told": "the whole team was told in person"}),
           "key-not-declared")
    expect("a notice telling nobody is refused",
           variant(notice={**notice, "told": []}), "covert-sensing")
    # Re-check G1, 2026-09-09: a mapping under a DECLARED key with no closed set of its own was
    # never reached by the enumerated walk, and both of these were admitted with a green PASS.
    expect("a mapping under the declared scalar notice.published_at is refused",
           variant(notice={**notice, "published_at": {"holder": "<never read>"}}),
           "key-not-declared")
    prose_ladder = copy.deepcopy(good["ladder"])
    prose_ladder["purpose"]["will_act"] = "agreed with the on-call rota"
    expect("prose in the boolean ladder.purpose.will_act is refused",
           variant(ladder=prose_ladder), "value-not-the-declared-shape")
    # Re-check G2: a type-confused record must be a refusal, never an AttributeError that aborts
    # the whole estate run at one adopter's malformed file.
    expect("a dpia block that is a list is refused rather than raising",
           variant(dpia=["twin/orgs/planted/dpia/bus-factor-structural-aggregate.yaml"]),
           "key-not-declared")
    expect("a notice naming an unregistered role is refused",
           variant(notice={**notice, "told": ["unregistered-role"]}), "role-not-registered")
    expect("a record of another scenario class is refused",
           variant(scenario_class="support-ticket-volume"), "not-this-scenario-class")
    expect("a scenario this adopter does not serve is refused",
           variant(scenario="not-a-served-scenario"), "scenario-not-served")
    expect("a record of the wrong schema is refused",
           variant(schema="something else"), "value-not-the-declared-shape")
    missing = copy.deepcopy(good["ladder"])
    missing["necessity"].pop("kind")
    expect("a ladder rung with no kind is refused rather than indexed",
           variant(ladder=missing), "required-key-missing")
    channels = copy.deepcopy(good["ladder"])
    channels["dpia"]["channels"] = ["a channel this class never reads"]
    expect("a ladder declaring a monitoring channel is refused",
           variant(ladder=channels), "value-not-the-declared-shape")
    expect("a DPIA filed for another sensor is refused", variant(),
           "value-not-the-declared-shape",
           dpia=_GOOD_DPIA.replace("sensor: bus-factor-structural-aggregate",
                                   "sensor: payroll-record"))
    empty_alt = copy.deepcopy(good["ladder"])
    empty_alt["necessity"]["alternatives"] = []
    expect("a necessity rung with no alternatives considered is refused",
           variant(ladder=empty_alt), "required-key-missing")
    expect("a DPIA of the wrong schema is refused", variant(), "value-not-the-declared-shape",
           dpia=_GOOD_DPIA.replace("schema: twin.dpia/v1", "schema: whatever you like"))
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

        # Review F1, end to end at a real served ref: this exact record was ADMITTED with a
        # green PASS before the key set was closed.
        lines = []
        estate = _plant(root / "openkey", hooks, _GOOD_RECORD
                        + "maintained_by: <a value the grader never reads>\n")
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("key-not-declared" in ln for ln in lines):
            out(f"PASS: selfcheck: a served record carrying an undeclared key grades FAIL "
                f"({lines[-1][:150]})")
        else:
            out(f"FAIL: selfcheck: a served record carrying an undeclared key should grade FAIL, "
                f"got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Re-check G1, end to end at a real served ref: both of these were ADMITTED with a green
        # PASS before the document was closed, because the walk was eleven enumerated paths.
        lines = []
        estate = _plant(root / "opennested", hooks, _GOOD_RECORD.replace(
            "  published_at: docs/monitoring-notice.md\n",
            "  published_at: {holder: <a value the grader never reads>}\n"))
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("notice.published_at" in ln for ln in lines):
            out(f"PASS: selfcheck: a served record with a mapping under a declared scalar key "
                f"grades FAIL ({lines[-1][:130]})")
        else:
            out(f"FAIL: selfcheck: a served record with a mapping under a declared scalar key "
                f"should grade FAIL, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        lines = []
        estate = _plant(root / "prosebool", hooks, _GOOD_RECORD.replace(
            "  purpose: {scenario: key-person-2026, will_act: true}",
            "  purpose: {scenario: key-person-2026, will_act: agreed with the on-call rota}"))
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("will_act" in ln for ln in lines):
            out(f"PASS: selfcheck: a served record with prose in the boolean will_act grades "
                f"FAIL ({lines[-1][:130]})")
        else:
            out(f"FAIL: selfcheck: a served record with prose in the boolean will_act should "
                f"grade FAIL, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Re-check R1, end to end at a real served ref, with the re-check's own plant: a
        # DUPLICATED key carrying an email shape past a closure that reads the parsed document.
        lines = []
        estate = _plant(root / "dupkey", hooks, _GOOD_RECORD.replace(
            "senses_role: platform-engineer\n",
            "senses_role: someone@example.invalid\nsenses_role: platform-engineer\n"))
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("duplicate key" in ln and "senses_role" in ln for ln in lines):
            out(f"PASS: selfcheck: a served record with a duplicated key grades FAIL and names "
                f"the key the parser would have discarded ({lines[-1][:120]})")
        else:
            out(f"FAIL: selfcheck: a served record with a duplicated key should grade FAIL, got "
                f"exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Re-check R3 and R4: four served records used to raise an uncaught KeyError, and a
        # deeply nested one a RecursionError, each aborting the grading of every other adopter.
        # Here the malformed record sits BESIDE a good one: the bad file must be its own FAIL row
        # and the good one must still be graded.
        lines = []
        estate = _plant(root / "malformed", hooks, _GOOD_RECORD, extra_record=(
            "payroll-record.yaml", "fields: " + "[" * 400 + "]" * 400 + "\n"))
        rc = grade_estate(estate, out=lines.append)
        good_still_graded = any("admitted" in ln and "PASS" in ln for ln in lines)
        bad_named = any("payroll-record.yaml" in ln and "FAIL" in ln for ln in lines)
        if rc == 1 and good_still_graded and bad_named:
            out("PASS: selfcheck: one adopter's unreadable record is its own FAIL row and the "
                "record beside it is still graded")
        else:
            out(f"FAIL: selfcheck: an unreadable record must not abort the run; got exit {rc}, "
                f"good-graded={good_still_graded}, bad-named={bad_named}")
            failures += 1

        lines = []
        broken = _GOOD_RECORD.replace(
            "    alternatives: [{kind: behavioural, level: individual}]",
            "    alternatives: [{kind: behavioural}]")
        estate = _plant(root / "missingkey", hooks, broken)
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("required-key-missing" in ln and "level" in ln for ln in lines):
            out("PASS: selfcheck: a ladder alternative with no `level` is refused by name rather "
                "than indexed with [] downstream")
        else:
            out(f"FAIL: selfcheck: a ladder alternative with no `level` should be refused by "
                f"name, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-4 F1, the blocking regression, end to end at real served refs: an adopter whose
        # party.yaml cannot be read used to VANISH, taking a record naming an individual with it,
        # and the estate printed PASS.
        lines = []
        bad = _GOOD_RECORD.replace("planted", "alpha").replace(
            "fields: [component, distinct_committer_count, window_days]",
            "fields: [component, employee_id]")
        root4 = root / "twoadopters"
        _plant(root4, hooks, bad, org="alpha",
               party="party: alpha\nroles: [adopter]\nroles: [adopter]\n")
        estate = _plant(root4, hooks, _GOOD_RECORD.replace("planted", "bravo"), org="bravo")
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "alpha" in joined and "duplicate key" in joined:
            out("PASS: selfcheck: an adopter whose party.yaml cannot be read is NAMED and the "
                "estate stays red, rather than vanishing from the count")
        else:
            out(f"FAIL: selfcheck: an unreadable party.yaml must be a FAIL row naming the "
                f"adopter, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-5 R5-1, end to end: `git ls-tree --name-only` C-quotes a path with a non-ASCII
        # byte, so the artefact at it was dropped from legs 2 and 3 in silence.
        lines = []
        root6 = root / "quotedpath"
        estate = _plant(root6, hooks, None, org="alpha", extra_record=(
            "bus-factor-structural-aggregate-na\u00efve.yaml",
            _GOOD_RECORD.replace("planted", "alpha").replace(
                "fields: [component, distinct_committer_count, window_days]",
                "fields: [component, employee_id]")))
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "names-or-identifies-an-individual" in joined:
            out("PASS: selfcheck: a record at a path git would quote is still graded, where it "
                "used to give exit 3 and '0 declare a sensor admission'")
        else:
            out(f"FAIL: selfcheck: a record at a quoted path must still be graded, got exit "
                f"{rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-5 R5-2: a unit whose ref does not resolve is a damaged repository, not an empty
        # directory, and used to vanish beside a healthy adopter.
        lines = []
        root7 = root / "brokenref"
        _plant(root7, hooks, _GOOD_RECORD.replace("planted", "alpha"), org="alpha")
        estate = _plant(root7, hooks, _GOOD_RECORD.replace("planted", "bravo"), org="bravo")
        subprocess.run(["git", "-C", str(estate / "alpha"), "update-ref", "-d",
                        "refs/remotes/origin/main"], check=True, capture_output=True)
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "alpha" in joined and "does not resolve" in joined:
            out("PASS: selfcheck: a unit whose origin/main does not resolve is a named row, not "
                "a silent drop")
        else:
            out(f"FAIL: selfcheck: a unit whose ref does not resolve must be named, got exit "
                f"{rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-6 F1: `rev-parse --verify -q origin/main` proves a ref PARSES, not that it
        # POINTS AT ANYTHING; a pruned object store resolved and `ls-tree` said "not a tree
        # object", so the unit landed in the silent skip R5-2 was written to close.
        lines = []
        root8 = root / "prunedref"
        bad_alpha = _GOOD_RECORD.replace("planted", "alpha").replace(
            "fields: [component, distinct_committer_count, window_days]",
            "fields: [component, employee_id]")
        _plant(root8, hooks, bad_alpha, org="alpha")
        estate = _plant(root8, hooks, _GOOD_RECORD.replace("planted", "bravo"), org="bravo")
        objects = estate / "alpha" / ".git" / "objects"
        shutil.rmtree(objects)
        objects.mkdir()
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "alpha" in joined and "bravo" in joined:
            out("PASS: selfcheck: a ref that parses but points at no tree is a named row, and "
                "the healthy unit beside it is still graded")
        else:
            out(f"FAIL: selfcheck: a ref that parses but points at no tree must be named, got "
                f"exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-6 F2: a unit that SERVES the whole org tree and stops serving its adopter claim
        # vanished with all of it, unnamed.
        lines = []
        root9 = root / "noclaim"
        _plant(root9, hooks, bad_alpha, org="alpha")
        estate = _plant(root9, hooks, _GOOD_RECORD.replace("planted", "bravo"), org="bravo")
        unit = estate / "alpha"
        _git(unit, "rm", "-q", "--cached", "party.yaml", hooks=hooks)
        _git(unit, "commit", "-q", "-m", "stop claiming", hooks=hooks)
        _git(unit, "update-ref", "refs/remotes/origin/main", "HEAD", hooks=hooks)
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "stopped saying it is a party" in joined:
            out("PASS: selfcheck: a unit serving an org tree with no readable adopter claim is "
                "a named row, not a silent drop")
        else:
            out(f"FAIL: selfcheck: a unit serving an org tree with no adopter claim must be "
                f"named, got exit {rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-6 F3: only one spelling of the extension was read, and the short one is what
        # this estate uses for every workflow file.
        lines = []
        estate = _plant(root / "shortext", hooks, None, org="alpha", extra_record=(
            "bus-factor-structural-aggregate.yml", bad_alpha))
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "names-or-identifies-an-individual" in joined:
            out("PASS: selfcheck: a record under the short extension is still graded")
        else:
            out(f"FAIL: selfcheck: a record under the short extension must be graded, got exit "
                f"{rc}: {lines[-1] if lines else 'nothing'}")
            failures += 1

        # Round-4 F2: a served file that is not UTF-8 aborted the run from the layer above the
        # per-record guard, and its traceback went to stderr where the wrapper never saw it.
        lines = []
        root5 = root / "notutf8"
        _plant(root5, hooks, _GOOD_RECORD.replace("planted", "alpha"), org="alpha",
               extra_bytes=("twin/orgs/alpha/people/binary.yaml",
                            b"id: \xff\xfe\x00binary\nrole: x\n"))
        estate = _plant(root5, hooks, _GOOD_RECORD.replace("planted", "bravo"), org="bravo")
        rc = grade_estate(estate, out=lines.append)
        joined = "\n".join(lines)
        if rc == 1 and "binary.yaml" in joined and "bravo" in joined:
            out("PASS: selfcheck: a served file that is not UTF-8 is a FAIL row and the other "
                "adopter is still graded")
        else:
            out(f"FAIL: selfcheck: a non-UTF-8 served file must be a FAIL row, got exit {rc}: "
                f"{lines[-1] if lines else 'nothing'}")
            failures += 1

        # Review F2, end to end: a role file carrying an undeclared key, and one named after
        # something that is not a role.
        lines = []
        estate = _plant(root / "openrole", hooks, None, extra_role_file=(
            "employee-of-the-month.yaml",
            "id: on-call-secondary\nrole: Second on call.\nheld_by: <never read>\n"))
        rc = grade_estate(estate, out=lines.append)
        named = [ln for ln in lines if "held_by" in ln or "employee" in ln]
        if rc == 1 and len(named) >= 2:
            out(f"PASS: selfcheck: a served role file with an undeclared key and a filename that "
                f"is not a role grades FAIL ({named[0][:120]})")
        else:
            out(f"FAIL: selfcheck: a served role file with an undeclared key and a filename that "
                f"is not a role should grade FAIL, got exit {rc} and {len(named)} finding(s)")
            failures += 1

        lines = []
        estate = _plant(root / "noscenario", hooks, None, scenario=False)
        rc = grade_estate(estate, out=lines.append)
        if rc == 1 and any("serves no bus-factor-key-person scenario" in ln for ln in lines):
            out(f"PASS: selfcheck: an adopter that stopped serving the key-person scenario "
                f"grades FAIL ({lines[-1][:150]})")
        else:
            out(f"FAIL: selfcheck: an adopter that stopped serving the key-person scenario "
                f"should grade FAIL, got exit {rc}: {lines[-1] if lines else 'nothing'}")
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
    out(f"PASS: selfcheck: {planted} planted records and eighteen planted served "
        "estates grade as planted")
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
