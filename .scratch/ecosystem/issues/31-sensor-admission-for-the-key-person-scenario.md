# 31 — Sensor admission for the key-person scenario

Type: grilling (HITL)
Status: resolved
Blocked by: none (19 is `Status: resolved`; measured 2026-09-09)

## Question

What a real adopter may sense for `bus-factor-key-person`: ethics gate, roles register, DPIA, with covert sensing excluded.

## Notes

Graduated 2026-08-28 from ticket 11's resolution. Definition of done includes wiring its check into `talk/verify-all.sh`.

## Answer

**2026-09-09.** Built in the hub branch `ticket-31-sensor-admission`. The rule is a closed table,
the module that walks it reuses `twin/ethics_gate.py`, and the check grades what the three
adopters **serve** at `origin/main`.

### Stale claims corrected, each with the measurement

1. **`Blocked by: 19`.** Ticket 19 has read `Status: resolved` since 2026-08-28
   (`git show origin/main:.scratch/ecosystem/issues/19-misuse-and-portability.md | head -5`).
   The header above now reads `none`.
2. **"tuppence has no key-person scenario; driftwood and ludlow only."** False at the served
   artefact. All **three** adopters serve one:
   `git -C .estate-clone/<u> ls-tree -r --name-only origin/main | grep scenarios/` lists
   `twin/orgs/<u>/scenarios/key-person-2026.yaml` for driftwood (`08ca32e`), tuppence
   (`fbf952f`) and ludlow (`a2e9d02`), and all three carry the sentence *"A role, never a
   person … Sensing a real departure would need admission through the ethics gate, a DPIA and
   the roles register, which is a separate ticket"*. The scenario half was done for three, not
   two, and the check now grades the sentence rather than trusting it.
3. **"Definition of done includes wiring its check into `talk/verify-all.sh`."** `verify-all.sh`
   line 183 discovers scripts with
   `find -L .estate-clone verify -name 'verify*.sh' -not -path '*/.work/*' -not -path '*/.git/*'`,
   so nothing in that file is edited. What a new check needs is a row in
   `talk/verify-manifest.txt`, or the gate fails it for having no class. That row is added.
4. **"The substrate already exists: `twin/ethics_gate.py`, `twin/roles.yaml`,
   `twin/sensors.yaml`."** All three exist and were read before anything was built, and the
   substrate is **narrower than the ticket needs**. `ethics_gate.admit()` walks purpose,
   necessity and proportionality, refuses a sensor id that is not a row in `sensors.yaml`, and
   blocks a mandatory-but-incomplete DPIA. It cannot do any of the five things ticket 31 asks
   for: it never looks at **what** a sensor reads (`_check_necessity` compares a declared
   `kind`/`level` pair and nothing else); its `dpia.complete` is a **boolean the payload asserts
   about itself** — no record is read anywhere, and no date, accountable role or retention
   period exists in any file in this repository; it **ranks** intrusiveness but admits any pair
   whose arithmetic works out, so a cohort or individual bus-factor reading is admissible today;
   nothing anywhere asks whether the sensed party was told; and `twin/roles.yaml` is the twin's
   **signing** register (`model-steward`, `worksheet-author`, `constraint-owner`, `challenger`,
   `challenge-resolver`, `disparate-impact-respondent`) — it is not, and should not become, the
   register of an adopter's on-call roles.

### The decisions, each `delegated` (ADR-0025) with its reason

**D1 — Which sensor kinds are admissible: exactly one pair, `structural` / `aggregate`.**
Recorded in `twin/sensor-admission.yaml` `admissible:`, in `ethics_gate.py`'s own `_KIND_RANK`
and `_LEVEL_RANK` vocabulary rather than a second one. Reason, per exclusion:

- `individual` is out because the scenario's subject is a role file (`people/<role>.yaml`) that
  names nobody; an individual reading answers a question the scenario does not ask.
- `cohort` is out because **a bus factor of one means the cohort IS the person**. A
  cohort-granularity reading of "which components would lose their only committer" is an
  individual reading wearing a coarser word, and `_LEVEL_RANK` would rank it safer than it is.
  This is the single most important line in the ticket: the existing ladder would have admitted
  it.
- `behavioural` is out because the question is answered by commit-graph **structure**;
  `_check_necessity` would refuse a behavioural route anyway, and naming it here refuses it
  *before* the ladder rather than inside it.

`sensors.yaml` already carries exactly one row at that pair —
`bus-factor-structural-aggregate` — so the admissible set is not an invention: it is the sensor
the estate already names, and no new sensor row was added.

**D2 — What the ethics gate must be shown before a sensor is admitted.** Five facts, each a
fact on the served artefact rather than a promise, plus the existing ladder:

1. a sensor id that is a row in `twin/sensors.yaml` (the closed table stays closed);
2. a declared `kind`/`granularity` in the admissible set, **and a ladder whose `necessity` walks
   the same pair** — a record declaring structural/aggregate at the top and behavioural/
   individual in its ladder is refused, because one of the two is not what runs;
3. every declared field inside the closed `admissible_fields` set;
4. a **published, dated notice** (`told`, `published_at`, `published_on` as `YYYY-MM-DD`);
5. a **DPIA record** at a path in the adopter's own repository, and a **sensed role and a DPIA
   signatory that are both ids in the adopter's own people register**.

Only a record that survives all five reaches `ethics_gate.admit()`, unchanged.

**D3 — What the roles register must carry, and which register it is.** The register for this
rule is the **adopter's own** `twin/orgs/<org>/people/`, not the hub's `twin/roles.yaml`.
Reason: the role being sensed is the adopter's, it is the scenario's own declared subject, it is
signed under the adopter's tag, and putting an adopter's staffing into the twin's signing
register would make the hub carry a list of other organisations' roles. `twin/roles.yaml` is
**not bumped by this ticket** — a version bump changes `sign.register_pin()`'s digest and
therefore what every existing signature was made against, for no gain here. Each file in that
register must carry an `id`, a non-empty `role` sentence saying what it is accountable for, and
**no individual-shaped key or value**; the check grades all three across all three adopters.

**D4 — What the DPIA records and where it lives.** In the **adopter's own repository**, at the
path the admission record names (`twin/orgs/<org>/dpia/<sensor>.yaml` is the shape), carrying at
minimum `completed_on` (a `YYYY-MM-DD` date), `completed_by` (a role id in that adopter's people
register) and `retention_days` (a positive whole number). Reason: the adopter is the controller;
the hub is not, and a DPIA held by a party that is not the controller is a filing exercise. The
three required fields are the "disclosed limit is a printed number or a date" rule applied: a
DPIA with no date has not been done, and one with no retention period has not decided the thing
a DPIA exists to decide. The record's **values** are scanned for individual shapes too, so a
DPIA cannot smuggle in the person the admission record was refused for naming.

**D5 — What is refused outright, and the sentence that refuses it.** Seven refusal ids, each
with its sentence **declared in `twin/sensor-admission.yaml`** rather than formatted in the
module, so the words a reader is shown and the words the gate grades are the same bytes. The
five ticket 31 names, plus `field-not-admissible` (the closed field set) and `sensor-not-named`
(reported as a refusal instead of `ethics_gate`'s raise, because a refusal a caller must handle
is the product, not an exception a caller might swallow). `load_rule()` refuses a table that
declares no sentence for a refusal the module can emit, so a sentence cannot go missing and
leave a refusal printing nothing.

**D6 — Refusal (a) is terminal and is evaluated alone.** A record that names or identifies an
individual is refused **before** `ethics_gate.admit()` is called; `ladder` comes back `None` and
no other refusal is reported. Reason: computing a proportionality ratio for such a record would
**put a price on sensing a named person**, which is the thing NORTH-STAR §6 excludes outright,
and this module must have no code path that does it. It is the same structural argument
`walk_ladder()` already makes for a failed purpose rung ("asking that question anyway would
dignify a sensor that should never have been proposed"), applied one rung earlier. The other
six refusals are reported **together**, so an adopter fixing one learns of the rest in one run.

**D7 — No admission record is planted into any adopter, so the check cannot pass today.** A
DPIA record and a monitoring notice are records of acts a controller performed. Writing them
into driftwood, tuppence or ludlow would be a faked observation, which is the rule that does not
bend. The honest outcome is a could-not-look with a printed count. What would turn it green: an
adopter publishing `twin/orgs/<org>/sensor-admissions/<sensor>.yaml` and the DPIA it names.

**D8 — The three scenario notes are not edited.** They say sensing "would need admission
through the ethics gate, a DPIA and the roles register, which is a separate ticket". That
remains true of every adopter: none declares an admission. Rewording three signed adopter trees
to say the same thing costs three pull requests and measures nothing. The check now **grades**
the sentence instead, so it cannot quietly disappear.

**D9 — The rule and the module live in `twin/`, the check in `verify/`.** `verify/*.py` does not
import `twin`, by the convention `verify/_estate.py` records; `verify/misuse/verify-misuse.sh`
is the precedent for a shell check in `verify/` driving a module in `twin/`, and this follows it
exactly. `mypy twin` therefore covers the new module.

### Red first, at the five seams

Tests were written against a first-cut module that loaded the table and walked the ladder and
did nothing else. `.venv/bin/python -m pytest tests/test_sensor_admission.py -n0 -q` →
**25 failed, 4 passed**. The exact lines, one per seam:

| seam | red line | green line |
|---|---|---|
| (a) names or identifies an individual | `AssertionError: a sensor reading 'employee_id' must be refused by name, got []` (and `work_email`, `full_name`, `person_handle`, `free_text_note`, `user`) | `REFUSED names-or-identifies-an-individual: bus-factor-structural-aggregate: the field 'employee_id' (the word 'employee') names or identifies an individual. A bus-factor-key-person sensor senses a role, never a person, and this record is refused before its proportionality is computed.` |
| (b) admitted without a DPIA record | `AssertionError: a sensor with no DPIA record must be refused by name, got []` | `REFUSED no-dpia-record: bus-factor-structural-aggregate: no DPIA record at twin/orgs/planted/dpia/bus-factor-structural-aggregate.yaml. A sensor of people is admitted only against a completed DPIA in the adopter's own repository, carrying a date, an accountable role and a retention period in days.` |
| (c) kind not in the admissible list | `AssertionError: structural/cohort is not in the admissible set and must be refused by name, got []` | `REFUSED kind-not-admissible: bus-factor-structural-aggregate: structural/cohort is not admissible for bus-factor-key-person; the admissible set is structural/aggregate.` |
| (d) covert sensing | `AssertionError: a sensor the sensed party is not told about must be refused by name, got []` | `REFUSED covert-sensing: bus-factor-structural-aggregate: the record carries no notice, so the sensed party is not told. Covert sensing is permanently excluded (NORTH-STAR section 6), so a sensor with no published, dated notice is refused before its ladder is walked.` |
| (e) role with no entry in the roles register | `AssertionError: a sensed role absent from the people register must be refused by name, got []` | `REFUSED role-not-registered: bus-factor-structural-aggregate: it names the sensed role 'unregistered-role', which the adopter's people register does not carry. A sensor may sense only a role somebody has registered, and a DPIA may be signed off only by one.` |

Then green: **30 passed**.

### What the check grades, and what it prints today

`verify/sensor-admission/verify-sensor-admission.sh`, discovered by `talk/verify-all.sh`'s glob,
with a row in `talk/verify-manifest.txt` classed `estate-observation`.

- **Leg 1, the instrument**, on planted material that says it is planted: ten planted records
  (each of the seven refusals red, then the one admissible sensor green) and **four planted
  single-unit estates whose served ref is a real `refs/remotes/origin/main`** — one that grades
  PASS, one whose record names an individual and grades FAIL, one that serves no
  `bus-factor-key-person` scenario at all and grades FAIL, and one with no admission record that
  grades SKIP with a count. The fixture's own git runs with `core.hooksPath` pointed at an empty
  directory, so the owner's global ggshield hook cannot make a fixture commit a load intermittent.
- **Leg 2, the estate, at the SERVED artefact.** Every fact is read with
  `git show origin/main:<path>` in the fetched clone, never the working tree: an uncommitted
  admission record is not one an adopter has published, and grading a worktree would let an
  uncommitted edit change the verdict. Three sub-legs: every adopter serves a `bus-factor-key-person`
  scenario, it still says "A role, never a person", and it names a `people/<role>.yaml` the
  served tree carries — an adopter that stopped serving one is observed **false**, not skipped
  past, because otherwise the printed count could fall from 3 to 0 with nothing going red;
  every role file carries an id, a role sentence and no individual-shaped key or value; every
  admission record grades through the rule.

Today, verbatim:

```
SKIP: 3 adopters read at origin/main [driftwood=08ca32e ludlow=a2e9d02 tuppence=fbf952f]; 3 carry
a bus-factor-key-person scenario and every one still says 'A role, never a person'; 0 declare a
sensor admission under twin/orgs/<org>/sensor-admissions/, so 0 admission decisions could be
graded
```

**3 adopters, 3 scenarios, 0 admission records, 0 admission decisions graded.** That is a named
could-not-look with a printed count, declared `waits:` in the manifest — the day an adopter
publishes one, this script grades it and can pass, which is why it is not `never:`.

### No real person anywhere

- Nothing built here senses anything. There is no sensing substrate in this estate and this
  ticket built none: the rule decides what *would* be admissible, and the only sensor it admits
  reads a component id and three counts.
- The one admissible sensor's field set is closed to `component`, `distinct_committer_count`,
  `commits_in_window`, `window_days`. Every other field is refused by name.
- Refusal (a) is terminal, so no code path in `twin/sensor_admission.py` prices, ladders or
  scores a record that names an individual.
- `INDIVIDUAL_NAME_TOKENS` extends `twin/sign.py`'s existing `PERSONAL_FIELDS` — the list this
  estate already refuses a signature for — rather than starting a second one. `committer`,
  `author` and `contributor` are deliberately **not** in it: they name a relation to a commit,
  and `distinct_committer_count` is the admissible aggregate reading.
- Values are scanned for an email address and a national-insurance-number shape wherever they
  appear in an admission record or a DPIA record, so an identifier under an innocent field name
  is still refused.
- **In the fixtures and in this ticket, no human name appears anywhere.** Every role is a role
  id out of an adopter's own people register (`platform-engineer`, `platform-lead`,
  `data-protection-lead`); the one planted email is `someone@example.invalid` and the one
  planted git author is `selfcheck@example.invalid`, both on the RFC 2606 reserved domain; the
  planted identifiers are field *names* (`employee_id`, `work_email`, `full_name`,
  `person_handle`, `free_text_note`, `user`), never values that could be a person.
- The three adopters' own people registers were read at `origin/main`: `driftwood`
  `platform-engineer` + `data-protection-lead`, `tuppence` `payments-engineer` +
  `financial-crime-lead`, `ludlow` `platform-engineer` + `privacy-officer`. Six served role
  files, each carrying an `id`, a `role` and no third key, and no identifier-shaped filename,
  id, key or value. **That is the measurement, and it is narrower than "names nobody"** (review
  F2): a role id that is simply a person's name in plain words matches no token and no value
  shape, and no rule here reads English.

### Files changed

| repo | file | what |
|---|---|---|
| hub | `twin/sensor-admission.yaml` | new: the closed rule table and the seven refusal sentences |
| hub | `twin/sensor_admission.py` | new: the rule, the served read, `--selfcheck` |
| hub | `tests/test_sensor_admission.py` | new: 30 tests, the five seams red first |
| hub | `verify/sensor-admission/verify-sensor-admission.sh` | new: the gate check |
| hub | `talk/verify-manifest.txt` | one row, `estate-observation`, two declared `waits:` |
| hub | `.scratch/ecosystem/map.md` | the map line, in number order |
| hub | `.scratch/ecosystem/issues/31-*.md` | this file |

No unit repository is changed by this ticket (D7, D8).

Map line: 31 built: one admissible pair (structural/aggregate; cohort refused because a bus factor of one means the cohort IS the person) and a closed four-field set; a published dated notice, a DPIA in the adopter's own repo with a date, an accountable role and a retention period in days, and a sensed role in the adopter's own `people/` register, all before the ethics gate's ladder; naming an individual is a terminal refusal evaluated alone; `verify/sensor-admission/` grades three adopters at origin/main and prints 3/3/0 today, a could-not-look with counts, never a pass.

## Review round 1 — 2026-09-09, request-changes, one high finding

The reviewer's F1 was right and the fix is theirs: **close the record's KEY set the way
`admissible_fields` closes the field set**, which is what this rule table already argued for two
blocks above the hole ("a deny-list refuses the identifiers somebody thought of"). Head is now
`ec4dfbb`.

### F1 (high) — the record document was open, so a served record could name a person and be admitted

Only `fields:` was closed. The record DOCUMENT had no closed key set, and `identifier_in_value`
recognises exactly two shapes. The reviewer measured, end to end at a real served ref, that a
record carrying `maintained_by`, `escalation_contact`, `github`, `owner`, `stakeholders`, a
nested `context.escalation.to`, a prose `notice.told`, a person-shaped `scenario:` id, or a DPIA
`reviewed_by` key came back `exit 0, 1 admission records graded, 1 admitted, 0 refused`. A
homoglyph key (`еmployee_id`, a zero-width space, `employeе`) evaded `identifier_in_name`
for the same reason: `_WORD` splits on `[^a-z0-9]+`, so a Cyrillic e is a separator.

**Fixed, and `identifier_in_value` was NOT lengthened.** `twin/sensor-admission.yaml` gains
`closed_keys:` with eleven sets — `record`, `notice`, `dpia_ref`, `ladder`, the four ladder rung
sets, `ladder_alternative`, `dpia_record` and `people_file` — and a key at any level that the
table does not declare is a **terminal** refusal, `key-not-declared`. That closes the homoglyph
gap for free: a homoglyph key is by definition not in a closed set. Three further closures came
out of the same plants: `notice.told` is now a **list of role ids** out of the adopter's own
register rather than prose; the record's `scenario` must be one the adopter **serves** for this
class and must equal the ladder's own purpose rung; and the DPIA's **basename must be the
sensor's id**, so a DPIA cannot be filed under anybody's name.

**Red first, one line per plant the review measured.** Every plant is reproduced through its KEY
alone, because after the fix it is the undeclared key that refuses the record and the value is
never reached — so the hole is closed and no name is written down anywhere in this repository.

| plant (the review's, by key) | red line | green line |
|---|---|---|
| `maintained_by` | `AssertionError: an undeclared key 'maintained_by' must be refused by name, got []` | `REFUSED key-not-declared: bus-factor-structural-aggregate: 'maintained_by' (the record keys are: dpia, fields, granularity, kind, ladder, notice, scenario, scenario_class, schema, senses_role, sensor) is not one this table declares … No other refusal on this record was evaluated.` |
| `escalation_contact` | `AssertionError: an undeclared key 'escalation_contact' must be refused by name, got []` | same sentence, `'escalation_contact'` |
| `github` | `AssertionError: an undeclared key 'github' must be refused by name, got []` | same sentence, `'github'` |
| `owner` | `AssertionError: an undeclared key 'owner' must be refused by name, got []` | same sentence, `'owner'` |
| `stakeholders` | `AssertionError: an undeclared key 'stakeholders' must be refused by name, got []` | same sentence, `'stakeholders'` |
| `context` (the nested `context.escalation.to` case) | `AssertionError: an undeclared key 'context' must be refused by name, got []` | same sentence, `'context'` |
| `held_by` | `AssertionError: an undeclared key 'held_by' must be refused by name, got []` | same sentence, `'held_by'` |
| DPIA `reviewed_by` | `AssertionError: an undeclared key in the DPIA record must be refused, got []` | `REFUSED key-not-declared: bus-factor-structural-aggregate: the DPIA record's key 'reviewed_by' (the dpia_record keys are: …) is not one this table declares …` |
| homoglyph `еmployee_id` | `AssertionError: a homoglyph key 'еmployee_id' must be refused by the closed set, got []` | `REFUSED key-not-declared: … 'еmployee_id' …` (the test first asserts `identifier_in_name` cannot see it) |
| zero-width `e​mployee_id` | `AssertionError: a homoglyph key 'e\u200bmployee_id' must be refused by the closed set, got []` | same |
| `notice.contact` | `AssertionError: an undeclared key inside the notice must be refused, got []` | `REFUSED key-not-declared: … 'notice.contact' (the notice keys are: published_at, published_on, told) …` |
| `ladder.purpose.raised_by` | `AssertionError: an undeclared key inside the ladder must be refused, got []` | `REFUSED key-not-declared: … 'ladder.purpose.raised_by' (the ladder_purpose keys are: scenario, will_act) …` |
| prose `notice.told` | `AssertionError: a prose notice must be refused by name, got []` | `REFUSED covert-sensing: bus-factor-structural-aggregate: the notice names who is told as str rather than a list of role ids, and prose is where a personal name arrives. …` |
| `notice.told` naming an unregistered role | `AssertionError: a notice naming an unregistered role must be refused, got []` | `REFUSED role-not-registered: bus-factor-structural-aggregate: it names 'unregistered-role' among the roles the notice says it told, which the adopter's people register does not carry. …` |
| a DPIA filed under any other basename | `AssertionError: a DPIA filed under a name that is not the sensor id must be refused, got []` | `REFUSED no-dpia-record: … the DPIA record at twin/orgs/driftwood/dpia/whoever-signed-it.yaml has a basename that is not bus-factor-structural-aggregate.yaml — a DPIA is filed under the sensor it is about, never under anything else. …` |

**End to end at a real served ref**, two new planted estates: a served record carrying
`maintained_by` grades **FAIL** with `key-not-declared` (it graded PASS before), and a served
role file carrying `held_by` under the filename `employee-of-the-month.yaml` produces two
findings and grades **FAIL**.

The reviewer's good news is kept and is why `committer`/`author`/`contributor` stay out of the
token list: **the SENSOR still cannot read a person under any spelling**, because what binds the
read is the closed `admissible_fields` set, not the token list.

### F2 (medium) — the register sentences were wider than the measurement

Both fixed by **widening the measurement and narrowing the sentence**, since widening alone
cannot close it. Widened: `people_file_problems()` now reads the role file's served
**filename**, its `id`, its **closed key set** (`id`, `role`) and its values, where before only
keys and values were scanned against the token list — so `held_by: <a name>` and
`people/employee-of-the-month.yaml` are both findings. `people_files()` keys the register by
**path** rather than by id, because reading it into an id-keyed dict is what threw the filename
away.

Narrowed, because a role id that is simply a person's name in plain words matches no token and
no value shape and no rule proposed would catch it: the map line and the ticket now say **"no
undeclared key and no identifier-shaped filename, id, key or value"**, and the script prints
five `LIMIT:` lines on every run naming exactly what is not refused — a personal name in plain
words, in a DPIA's `lawful_basis`, `what_is_sensed` or `what_is_not_sensed`, in a notice path, or
as a role id. That residual belongs to the adopter's own register review.

### F3 (medium) — a refusal could have no sentence

`load_rule()` validated the refusal **id** only. A row with no `sentence:` loaded and raised an
uncaught `KeyError` at emit; `sentence: ''` loaded and emitted `refusals=['']`, a blank FAIL line
with no reason. `load_rule()` now refuses a row whose sentence is absent or blank, does not carry
both `{sensor}` and `{what}`, or does not open `REFUSED <id>:` so the gate can read the id off
the line. Four tests, red first (`Failed: DID NOT RAISE <class
'twin.sensor_admission.SensorAdmissionError'>` on each).

### F4 — **changed.** `is_terminal()` is called at the branch

It was defined and never called; `terminal: true` was decorative. The terminal set is now built
from the table (`terminal = [line for line in terminal if is_terminal(rule, id_of(line))]`), and
`test_terminality_is_read_from_the_table_at_the_branch` loosens a copy of the shipped table to
`terminal: false` and asserts the module then reports the refusal beside the others **with a
ladder**, then asserts the shipped table still says terminal.

### F5 — **changed.** A record of another class is refused, and the result reports its own class

`grade_record` stamped the table's `scenario_class` onto every result, so a record declaring
`support-ticket-volume` came back asserting it was `bus-factor-key-person`. The result now
carries the class **the record declared**, and a mismatch is the refusal
`not-this-scenario-class`.

### F6 — **changed.** The cohort reason is scoped to a bus factor of one

D1's cohort reason ("the cohort IS the person") holds at n=1; nothing derives n, and the
adopters carry it only as unread prose in `proposition:`. `bus_factor_scope: one` is now in the
table with a comment saying the **outcome** is right at every n and the **reason** is not, that
no run could tell the two cases apart because nothing derives n, and that a later ticket wanting
cohort must first make n a derived fact rather than loosening this on the grounds that the
reason fails at n=3.

### F7 — **recorded, no change.** Leg 1's sentence check is a substring test

`"It is not true that: A role, never a person"` would pass it. Left as is, with the reason: the
five real evasions planted are each caught distinctly, and a rule that tried to read the
surrounding English would be the "record that describes intent, not code" trap. The sentence's
presence is a tripwire against silent deletion, not a proof that the note means it.

### The optional clause, taken

Both terminal sentences now end **"No other refusal on this record was evaluated."**

### Kept, as the reviewer asked

The printed `origin/main` sha per adopter is derived from what was actually read, so a stale
clone shows in the verdict line rather than grading stale bytes silently.

### Battery, re-run after the fixes

- `pytest tests/test_sensor_admission.py -n0 -q` → **59 passed** (54 failed first).
- `pytest tests/test_sensor_admission.py tests/test_ethics_gate.py -n0 -q` → 98 passed.
- `verify/sensor-admission/verify-sensor-admission.sh` → exit 3, **24 planted records and six
  planted served estates grade as planted**, then the same 3 / 3 / 0 line on the real estate.
- `mypy twin tests conftest.py` → Success, 186 source files.

## Review round 2 — 2026-09-09, request-changes, one new medium finding

Head is now the branch tip after rebase onto current `origin/main`.

### G1 (medium) — the walk was a whitelist of eleven PATHS, not a closure of the DOCUMENT

`undeclared_keys()` visited exactly eleven positions, so any mapping sitting under a **declared**
key that had no closed set of its own — `published_at`, `schema`, `sensor`, `kind`,
`granularity`, `will_act`, `intrusion_cost`, `completed_by` — was never walked. The reviewer
measured both at a real served ref as `exit 0, PASS planted: … admitted, 1 admitted, 0 refused`.

**Fixed as a recursion, not a longer enumeration.** `closed_document_problems()` replaces
`undeclared_keys()`/`_undeclared()`. Three new tables make the shape declarable rather than
hand-written: `nested_maps` (a key holding a mapping ruled by a named set), `nested_lists` (a key
holding a list of such mappings), `scalar_lists` (a key holding a list of scalars) — and the
**default is SCALAR**, which is the case the enumeration missed. A mapping or list reached
anywhere else is `key-not-declared`. `typed_keys` adds the type check the reviewer asked for:
`will_act`, `profiling`, `financial_loss_risk` and `complete` must be booleans, `intrusion_cost`
and `value_illuminated` numbers, under the new terminal refusal `value-not-the-declared-shape`.
`load_rule()` also refuses a table whose `nested_maps`/`nested_lists` point at a key set
`closed_keys` does not declare, because that would silently stop the recursion at the node it
names — G1 again by another route.

**Red first, the two lines the re-check asked for:**

| plant | red line | green line |
|---|---|---|
| `notice.published_at: {holder: …}` | `AssertionError: a mapping under notice.published_at must be refused by name, got []` | `REFUSED key-not-declared: bus-factor-structural-aggregate: the key 'notice.published_at' holds a dict, and the table declares no key set for it. The key set is closed, because an undeclared key — or a mapping under a declared one — is where a person arrives, and no deny-list of identifier shapes can be longer than the names somebody can think of. No refusal beyond these was evaluated.` |
| `ladder.purpose.will_act: 'agreed with …'` | `AssertionError: prose in the boolean ladder.purpose.will_act must be refused by name, got []` | `REFUSED value-not-the-declared-shape: bus-factor-structural-aggregate: the key 'ladder.purpose.will_act' holds 'agreed with the on-call rota', and the table declares a boolean. A slot the table types is checked for its type, because a value of the wrong shape is read by something downstream that was never told, and prose in a slot nobody reads as prose is where a person arrives. No refusal beyond these was evaluated.` |

Both are also planted **end to end at a real served ref** (two new planted estates), where each
now grades FAIL. Eight further plants cover the same family: a mapping or list under `schema`,
`sensor`, `kind`, `granularity` and `senses_role`, a mapping inside the `fields` scalar list, a
mapping at `ladder.necessity.alternatives[0].level`, and a mapping under the DPIA's
`completed_by`.

**One knock-on, recorded because it makes a refusal stricter.** A prose `notice.told` is now
reached by the closure first and refused **terminally** as `key-not-declared`, where before it
was the non-terminal `covert-sensing`. That is the safer direction and the test says so; the
`covert-sensing` branch still owns an empty or missing `told`, and a new test pins that.

### G2 (low) — a type-confused record crashed the estate run

`grade_record` raised an uncaught `AttributeError` on `dpia:` as a list, contradicting its own
docstring, and one adopter's malformed record aborted the grading of the other two. Fixed in the
same change by running the closure **before** any `.get()` chain, and by reading the DPIA path
only through an `isinstance` guard. `closed_document_problems` calls `.get()` on nothing it has
not first shown to be a mapping. Nine plants: `dpia` as a list, a string, an int and `None`,
`notice` and `ladder` as lists, and a record that is not a mapping at all — every one now a
refusal, none a crash.

### G3 (cosmetic) — the clause printed several times per run

The clause is out of both terminal sentences and is appended **once**, to the last line of the
batch, from a new `terminal_batch_clause:` in the table: *"No refusal beyond these was
evaluated."* A test asserts it appears exactly once in a three-refusal batch.

### Not touched, as instructed

**`verify/map-surface/verify-map-surface.sh` line 90 runs `clone-estate.sh`, so the check
RE-FETCHES the estate it then grades.** In a clone-of-a-clone whose `origin` points at the shared
`.estate-clone`, that resets each unit's `origin/main` back to the stale sha immediately after it
was set correctly, and at the stale sha platform's `fetch.yml` serves the old four-path
observation lane while tuppence's and nist's serve their old declarations — twelve declarations,
twelve findings, exactly the `lane-not-owned x12` the round-1 reviewer saw and the mid-run ref
drift it could not attribute. So that check **mutates the estate it grades**, and its rule-4
verdict follows a remote URL rather than the estate's content. Not this ticket's to fix; recorded
so the next reader does not re-derive it.

### Battery, re-run after the fixes

- `pytest tests/test_sensor_admission.py -n0 -q` → **78 passed** (24 failed first, including the
  three `AttributeError`s G2 names).
- `verify/sensor-admission/verify-sensor-admission.sh` → exit 3, **28 planted records and eight
  planted served estates grade as planted**, then the same 3 / 3 / 0 line on the real estate.
- `mypy twin tests conftest.py` → Success, 186 source files.

### Measured on the real runner, on this exact tree

`truth` run 205, dispatched on `a70e9d2` because the workflow's push filter is
`talk/…`, `clone-estate.sh`, `verify/**` and `.github/workflows/truth.yml`, and the last commit
touches only `twin/`, `tests/` and this file. Quoted **from the Actions log and NOT citable** — a
branch run records nothing (ticket 100), and the run's own gate printed `CAN_RECORD: no`:

```
TRUTH 2026-09-09T16:32Z run=205 hub=a70e9d2 enact=development units=[driftwood=08ca32e@main
feeds=ca40396@main ico=9653fd9@main insurer=61fba9d@main ludlow=a2e9d02@main nist=f83126f@main
platform=8da250d@main tuppence=fbf952f@main] pass=77 [observed=23 self=41 simulated=4 meta=9]
fail=8 skip=31 [never=9 waits=22] excluded=8 total=124 ceiling=105
```

The gate graded this check `SKIP (waits)` with the intended line, against the real fetched estate.
None of the eight fails is this check: they are `verify/branch-refs`, `verify/deny-is-not-a-rung`,
`verify/derived-status`, `verify/handbook`, `verify/schedules`,
`verify/unreviewed-major` and two in `.estate-clone/`. `verify/derived-status`'s single fault
names **ticket 34**, not this one; ticket 31 falls in its "7 rest only on checks that could not
look", which it counts and does not fault. That check is red byte-identically on pristine
`origin/main` in this clone.

One number moved between the branch run on `867075c` and the one above, one fail becoming one
pass. It is **not** this branch: `platform`'s served sha moved from `2998571` to `8da250d`
between the two, and the pass that arrived is in the `self` class, which this branch does not add
to. This branch's own row is `SKIP (waits)` in both. Neither figure is quoted here as a citable
number, because neither branch run wrote a line to `talk/truth.log`; `verify/cited-truth`
refused an earlier draft of this paragraph for pairing a run number with a figure the log does
not record, which is the correct refusal.

## Re-check round 3 — 2026-09-09, request-changes on R1 and R2

### R1 (high) — the closure closed the PARSED document, not the SERVED BYTES

`yaml.safe_load` silently discards a repeated mapping key, last one wins. So a served record
reading

```
senses_role: <a person's name> <an email address>
senses_role: platform-engineer
```

was **admitted with a green PASS**: the parser threw the first line away before
`identifier_in_value` — whose whole job is that email shape — ever saw it. Pre-existing rather
than a regression, but it is the G1 class exactly and it defeats the commit sentence "the
document is closed".

**Fixed with the loader that already exists, not a new one.** `StrictLoader` was written by
ticket 93 for the same reason in the clock (a visible `probability: 0.999` above a real
`probability: 0.27` validated as `0.27`). Ticket 102's rule is no fork, so it is **lifted** to
`twin/strict_yaml.py` and both modules import it; `twin/derived_forecast.py` keeps the name
bound, and its 47 tests still pass. `load_served()` is now the only way this check parses
adopter-served bytes, and it is used at **every** one: `adopters()`, `people_files()`,
`key_person_scenarios()`, `admission_records()` and both DPIA reads. A duplicate is the new
terminal refusal `duplicate-key`, which names the key the parser would have discarded.

**Red first:**

| | |
|---|---|
| red | `AttributeError: module 'twin.sensor_admission' has no attribute 'load_served'` |
| green | `duplicate key 'senses_role' in the served bytes: PyYAML keeps the last, so the document a reader sees is not the document a parser builds` |

The loop the re-check asked for is closed by an assertion, not by prose:
`test_the_bytes_are_what_was_graded_not_the_parsed_dict` asserts that `yaml.safe_load` of the
same bytes returns a clean dict with `senses_role == 'platform-engineer'` and that
`individual_problems()` finds nothing in it — **and** that `load_served` refuses those bytes and
names `senses_role`. A duplicated `notice:` block is planted the same way, and the whole thing
again **end to end at a real served ref** in the selfcheck.

### R2 (medium, and new in the previous commit, which is why it blocked)

`load_rule()` validated nothing about `typed_keys`. `bool` mistyped as `boolean` **loaded
clean** and made the type check a silent no-op, because the recursion computes `wrong` as a
disjunction over the names it knows. The `nested_maps`/`nested_lists` guard written in the same
commit was not extended to the declaration added beside it.

Now refused at load, for `typed_keys`, `scalar_lists`, `required_keys` and `fixed_values` alike:
a set name `closed_keys` does not declare, a key that set's closed list does not declare, and —
for `typed_keys` — a type name outside `("bool", "number")`. Red first, each
`Failed: DID NOT RAISE <class 'twin.sensor_admission.SensorAdmissionError'>`; green, e.g.
`typed_keys.ladder_purpose.will_act declares the type 'boolean', which this module does not know
(have: bool, number) — an unknown name makes the check a silent no-op`. A further test asserts
the plant the mistyped name silenced is still refused with the table as shipped.

### R5 (low) — membership is not usability

`child not in closed_keys` passed a set **declared as null**, which then raised an uncaught
`TypeError` at grade time. Every guard now tests `not doc["closed_keys"].get(name)`. Red first
on both a null `closed_keys` entry and a `nested_maps` child pointing at one.

### R3 and R4 (medium, pre-existing, the G2 class alive by another route)

**R3.** The closure graded the shape of keys that were **present** and never that a **required**
one was there, and `ethics_gate` indexes those slots with `[]`. `required_keys:` now declares
them — `ladder_necessity [kind, level]`, `ladder_alternative [kind, level]`,
`ladder_proportionality [intrusion_cost, value_illuminated]` — and a missing one is the new
terminal refusal `required-key-missing`. Only slots something downstream **indexes** are listed;
a key read with `.get()` is not, because refusing it would displace a refusal that already has
better words (a notice with no `told` is covert sensing). The four measured crashes
(`KeyError: 'level'`, `'kind'` twice, `'intrusion_cost'`) are red first and now refusals.

**R4.** `RecursionError` is not a `yaml.YAMLError`, so a `fields:` nested 500 deep propagated out
of the reader. `load_served()` catches **broadly**, and `grade_estate` wraps the per-record grade
so a bad file is a FAIL row for **that file** while the other adopters are still graded. A
planted estate carries a malformed record **beside** a good one and asserts both: the bad one is
named, the good one is still admitted.

### R6 (low) — the doubled wording

Both callers assumed `what` was a bare key path. `people_file_problems()` printed *"carries the
undeclared key the key 'id' holds a dict…"* and `grade_record()` *"the DPIA record's key the key
'schema' holds a dict…"*. Fixed, with a test for each.

### R7 and R9 — four of the five surviving slots are CLOSED, and the block is derived

The re-check planted a real name into `record.schema`, the DPIA's `sensor:` and `scenario:`, and
`ladder.dpia.channels[]`, and watched each graded green. Rather than only documenting them, four
are now **closed by deriving the value**, under `value-not-the-declared-shape`:

- `record.schema` must equal the value the table declares — the plant landed because
  `RECORD_SCHEMA` was defined and used nowhere. **Round 4 F9 corrected this record**: at that
  point the constant was still unused, because the value lived a second time as a literal in the
  table with nothing asserting the two agreed. `load_rule()` now refuses a table whose
  `fixed_values.record.schema` differs from `RECORD_SCHEMA`, and `schema` is in
  `required_keys.record`, so deleting the key is a refusal too. Only now is "closed by use"
  true;
- the DPIA must name the **same** `sensor` and `scenario` as the record it is filed against, or
  it is a DPIA about something else;
- `ladder.dpia.channels[]` must be empty: the one admissible sensor for this class reads a
  commit graph, not a channel.

The printed LIMIT block is **generated from the table** by `limits()`. **Round 4 F5 and F6
corrected the claim that it therefore cannot go stale**: it could still grow to advertise a
refusal id no code path emits, it could name a DPIA field that does not exist, and its list of
residual slots was missing at least four. All three are now closed — see round 4 below — and the
honest sentence is that the block cannot drift from the table, and the table is now validated in
both directions. It names every refusal id the table declares, says the loader refuses
a duplicate key, and lists what a plain-words name still survives in: a DPIA's `lawful_basis`,
`what_is_sensed` and `what_is_not_sensed`, a notice's `published_at` path, and a role id or a
role file's own `role:` prose. Those five are the residual, and the adopter's own register review
is where they live.

### R8 — the knock-on, measured

The promotion to terminal is not confined to `notice.told`: **every** mapping or list under a
declared scalar key, every typed- or fixed-slot error, every undeclared key, every missing
required key and a duplicate key are terminal, and each pre-empts the whole non-terminal battery
for that record. Measured here, first-hand, on one record carrying five independent problems (a
prose `notice.told`, an unregistered `senses_role`, `behavioural`/`individual`, a field outside
the closed set, and no DPIA path):

- at `867075c`: `refusals=5 classes=5 terminal=False admitted=False`
- now: `refusals=1 classes=1 terminal=True admitted=False`

The verdict is unchanged — refused either way, exit 1 either way — and nothing became less safe.
What changes is that an adopter is told one thing at a time once a terminal problem is present.
That is the intended trade and it is recorded here rather than left to be rediscovered.

### The limit that became a line about the loader

Recorded, as the re-check asked: a duplicate key in a served document **used to be** discarded by
the parser before any rule saw it, and was a limit this check printed nowhere. It is now a
refusal, so the LIMIT block carries a line about what the loader does instead.

### Battery, re-run after the fixes

- `pytest tests/test_sensor_admission.py -n0 -q` → **102 passed** (21 failed first, including the
  three `KeyError`s R3 names).
- `pytest tests/test_derived_forecast.py -n0 -q` → 47 passed, with `StrictLoader` imported from
  its new home.
- `verify/sensor-admission/verify-sensor-admission.sh` → exit 3, **32 planted records and eleven
  planted served estates grade as planted**.
- `mypy twin tests conftest.py` → Success, 187 source files.

## Re-check round 4 — 2026-09-09, request-changes on F1

### F1 (high, blocking) — a regression the R1 fix caused: an adopter VANISHED

`adopters()` parsed `party.yaml` through `load_served`, got an `Unreadable`, failed the
`isinstance(doc, dict)` test and `continue`d **with no output at all**. Every fact that adopter
served went ungraded and a red estate printed green. The previous cut worked by accident: it used
`yaml.safe_load` inside `try/except yaml.YAMLError: continue`, so a duplicate-keyed `party.yaml`
parsed fine and the adopter WAS graded. The R1 fix widened the silent-skip class from
"unparseable" to "unparseable or duplicate-keyed".

**Red first**, on the re-check's own two-adopter plant at real served refs — `alpha` serves a
`party.yaml` with a duplicated `roles:` **and** a record reading `fields: [component,
employee_id]`; `bravo` is clean:

> **red** — `AssertionError: an adopter whose party.yaml cannot be read must be NAMED, not
> silently dropped; the run said: … PASS bravo: … bus-factor-structural-aggregate admitted …
> PASS: 1 adopters read at origin/main [bravo=46e3bbe]; 1 bus-factor-key-person scenarios still
> say 'A role, never a person'; 1 admission records graded, 1 admitted, 0 refused`
>
> **green** — `FAIL alpha: alpha/party.yaml: duplicate key 'roles' in the served bytes: PyYAML
> keeps the last, so the document a reader sees is not the document a parser builds`, and the run
> ends `FAIL:` at exit 1 with `alpha`'s record refused by name.

`adopters()` now returns the units it could **not** read alongside the ones it could, and
`grade_estate` prints a FAIL row per unreadable party artefact and counts it — the treatment the
other four readers already had. The pre-existing half is closed in the same change: an
**unparseable** `party.yaml`, and one that parses to something that is not a mapping, are FAIL
rows too. The silent skip that REMAINS is the correct one, and a test pins it: a directory that
serves no `party.yaml` at all is not a party.

### F2 (high, pre-existing) — a fifth way to abort the run, in the layer above

`served()` decoded git output with `text=True`, so a served file that is not valid UTF-8 raised
an uncaught `UnicodeDecodeError` inside `subprocess` — outside `grade_estate`'s per-record try,
so it aborted every other adopter, and its traceback went to **stderr**, which the verify
script's `tee` never captured, so the operator was shown a LIMIT line as the reason for the
failure. `served()` now reads **bytes** and returns the `Unreadable` shape its callers already
handle; `served_paths()` decodes with `surrogateescape` so a non-UTF-8 filename round-trips to
git rather than raising. The wrapper now merges stderr into its log and takes its last line from
a `^(PASS|FAIL|SKIP): ` match, refusing outright if the module printed no verdict line at all.
Planted end to end: a binary role file beside a clean adopter is a FAIL row naming
`binary.yaml`, and the clean adopter is still graded.

### F3, F4 and F5 — R2's own lesson, applied to the four declarations added beside it

- **F3.** The falsiness guard reached the top level and `closed_keys`, not the derived tables'
  **sub-entries**. `typed_keys.ladder_purpose: null`, `fixed_values.record: null` and
  `required_keys.ladder_necessity: null` each loaded clean and silently disabled the check they
  name — two of them readmitting plants closed the round before. One line in the loop: an empty
  sub-entry is refused at load.
- **F4.** `dpia_must_agree`, `requires.dpia_fields` and `admissible_channels` were indexed with
  no guard. Now: each must be a list of the type the module indexes; `dpia_must_agree` may name
  only a field the module can resolve against the record; `requires.dpia_fields` and
  `free_prose_fields` must name keys the `dpia_record` set declares. `admissible_channels` gets
  a **presence-and-type** check, not a truthiness one, because its correct value is `[]`.
- **F5.** The subset was enforced in one direction only, so a well-formed but **unreachable**
  refusal id loaded clean and the generated block grew to advertise it. Both directions now.

### F6 — two more slots closed, and the block's scope made honest

Closed: the **DPIA's own `schema:`** is now a fixed value like the record's; and the **whole
`dpia.record` path** is derived against `dpia_path_pattern`
(`^twin/orgs/[a-z0-9-]+/dpia/{sensor}\.yaml$`) rather than only its basename, which had left the
directory part free text.

Not closed, and now stated instead of implied: a served **scenario file** and **party.yaml** have
no closed key set. Both are now run through the **value** scan, which is what closes the
falsification the re-check found (they admitted an email address). They are deliberately **not**
run through the key-token scan: `note:` is a legitimate key in a scenario file, and the token
list was written for a closed field set. The block now says exactly that — five documents, keys
and values in three of them, values only in the other two — and lists the residual slots
including "any other prose in a served scenario file or a party.yaml".

### F7 — the right test is slot by slot, not "is it indexed"

`ladder.necessity.alternatives` is read with `.get()` and has **no** better-worded refusal behind
it: deleting the line gave a green admission with a vacuously passed necessity rung ("no less
intrusive alternative among 0 considered"). It is now in `required_keys`, and a new `non_empty:`
table refuses an explicitly empty one for the same reason. The ticket's earlier rule — "only
indexed slots are required" — is **corrected here**: the test is slot by slot, does this `.get()`
slot have a refusal with better words.

### F8 — the joke, and it landed

The one YAML this check still read with `yaml.safe_load` on a real path was **its own rule
table**, so a second `typed_keys:` block appended to it loaded clean and silently dropped two of
the three typed sets. `load_rule()` now uses the `StrictLoader` this ticket had just imported.

### F9 — R9 was recorded as closed and was not

`grep -rn RECORD_SCHEMA` returned the definition and a ticket sentence claiming use. Fixed by
making the claim true: `load_rule()` refuses a table whose `fixed_values.record.schema` differs
from the constant, and `schema` is in `required_keys.record` so deleting it is a refusal. The
sentence in round 3's section above is corrected rather than left standing.

### F10 to F13 — all four fixed

- **F10.** `StrictLoader` refused **every** merge key, duplicate or not, because it constructed
  the `<<` key node before `flatten_mapping` removed it — and said the bytes were not YAML when
  they are. It now skips the merge tag. Two tests: one merge key, and two in one mapping.
- **F11.** A record could be counted FAIL with **no line saying why**, when the ladder stopped
  and nothing else had anything to add. A record that is not admitted now always carries at
  least one refusal.
- **F12.** Any `EthicsGateError` was reported as `sensor-not-named`, so a ladder missing a whole
  rung was refused with words saying the sensor id is not registered, when it is. New refusal
  `ladder-could-not-walk`, in its own words.
- **F13.** A complex key raised `TypeError` from the loader's own membership test, surfacing as
  "not YAML this check will read (TypeError)" and refusing a complex key carrying no duplicate.
  Keys are compared by a hashable rendering now.

### Battery, re-run after the fixes

- `pytest tests/test_sensor_admission.py -n0 -q` → **128 passed** (24 failed first).
- `pytest tests/test_derived_forecast.py -n0 -q` → 47 passed, loader unchanged for ticket 93.
- `verify/sensor-admission/verify-sensor-admission.sh` → exit 3, **34 planted records and
  thirteen planted served estates grade as planted**.
- `mypy twin tests conftest.py` → Success, 187 source files.

## Re-check round 5 — 2026-09-10, request-changes on R5-1 and R5-2

The reviewer named the pattern for the third round running, and it is the right one to record:
the record is closed against every plant five rounds have thrown at the **document**, and every
remaining hole is one level **out** — in how the check decides which BYTES to look at, and in how
it trusts its own table.

### R5-1 (blocking) — a path git QUOTES made an artefact vanish

`git ls-tree --name-only` **C-quotes** any path carrying a non-ASCII byte, so `served_paths()`
returned `'"twin/orgs/alpha/people/rota-na\303\257ve.yaml"'` — quotes and backslashes included —
and `served()` on that string returned `None`. Every such artefact was **silently dropped** from
legs 2 and 3. The surrogate-escape decode did not help and could not: git quotes before Python
sees the bytes.

**Red first**, on the reviewer's own measurement:

> **red** — `AssertionError: a served path with one non-ASCII byte must round-trip, got [...]` /
> `assert 'twin/orgs/alpha/people/rota-naïve.yaml' in [..., '"twin/orgs/alpha/people/rota-na\303\257ve.yaml"', ...]`
> and, end to end, `AssertionError: a byte-identical record one directory over must not give exit
> 3 and '0 declare a sensor admission': assert 3 == 1`
>
> **green** — `git ls-tree -r -z --name-only` and a split on the null byte; the path round-trips,
> `served()` reads it back, and the same record at the accented path is refused
> `REFUSED names-or-identifies-an-individual: … the field 'employee_id' …` at exit 1.

Both plants are in the tests and in the selfcheck. The `served()` docstring and the round-4 F2
sentence in this ticket, both of which claimed the round-trip worked, are corrected in place.

### R5-2 (blocking, pre-existing) — a damaged repository vanished the same way

`adopters()` read a `None` from `served()` as "serves no party file", which is also what it
returns when the directory is not a git repository, or is one whose remote-tracking main has
gone. With the plant adopter's git directory removed the estate gave `PASS: 1 adopters read` at
exit 0 with the record naming an individual unmentioned.

> **red** — `AssertionError: a unit whose repository cannot be read must be named, not dropped: …`
> `assert 0 == 1`
>
> **green** — `FAIL alpha: alpha: origin/main does not resolve in this unit: the repository or
> its remote-tracking main cannot be read, so nothing it serves was graded`, exit 1.

`ref_resolves()` runs `rev-parse --verify -q origin/main` first, and a unit that looks like a unit
(a `.git`, a `party.yaml` or a `twin/` tree on disk) whose ref does not resolve is its own named
row, distinct from a tree that serves no party file. A bare scratch directory is still the
correct silent skip, and a test pins it. The `adopters()` docstring — which asserted the old,
wrong boundary — is corrected in the same change.

### R5-3 and R5-4 (major) — and R5-3 silently disabled round 4's own fix

`dpia_path_pattern` was read and validated by nothing: `^.*$` loaded clean and readmitted a DPIA
filed under a directory named after a person, which is exactly what round 4's F6 closed; an
invalid pattern loaded clean and raised at grade time. It must now contain the literal
`{sensor}` and compile. `admissible_fields` was truthiness-checked only, so declared as a
**scalar** — one missing list dash — it loaded clean and turned the closed field set into a
**substring test**: `fields: [com, pone]` was admitted, the exact opposite of the table's own
stated reasoning. It joins the list-and-type group.

### R5-5 (major) — an adopter's own bytes could deny the gate

The email pattern backtracked quadratically on a value with **no at-sign**: 8 KiB 0.275s, 32 KiB
4.44s, 128 KiB 73s, 1 MiB about 75 minutes. Neither the module nor the wrapper has a timeout, so
in the gate that is a job that dies with no verdict. One line: `identifier_in_value` returns early
unless the value contains an at-sign, which is precisely the pathological case. A test asserts
24 KiB with no at-sign is under half a second — 24 KiB and not a megabyte, so a **red** run still
finishes — and a second asserts the shape is still found in a long value. The NI pattern is
bounded and is untouched.

### R5-6 (moderate) — THE RULE, in my own new code

The F11 fallback read `stopped_at` off the **top** level of the gate's result, where that key does
not exist; it lives one level down, which the very next line already reached into. So every ladder
refusal read *"the ethics gate stopped at the DPIA gate"* whatever actually stopped it. It reaches
one level down now, and two tests assert a proportionality stop names proportionality and a
purpose stop names purpose.

### R5-7 and R5-8 (moderate) — two generated sentences that overstated the code

**R5-7.** The block said every party file is value-scanned and the scan ran only inside the
adopter-role branch, so five of the eight real units were never scanned. The scan is cheap and
there was no reason to scope it: it now runs on **every readable** party file, and the sentence is
true rather than narrowed.

**R5-8.** The two-way subset was between two **declarations** — the table and a hand-written
`REFUSAL_IDS` — not between a declaration and the **code**. `emitted_refusal_ids()` now walks this
module's own AST for the ids it passes to `out()` and the ids in the `(refusal id, what)` pairs
its two collectors build, `load_rule()` compares the table against **that**, and the printed block
lists **that**. The sentence is true by construction now, not by inspection.

### R5-9 (moderate) — three comments asserting what the code does not do

All three corrected in place: the `scan_names` docstring (its false setting is used by the party
and scenario readers, never on a DPIA, which is scanned **with** its keys), the `adopters()`
docstring (R5-2), and the `served()` docstring plus this ticket's round-4 F2 sentence (R5-1).

### R5-10 to R5-14 (minor) — all fixed

- **R5-10.** The estate grader collapsed the new `Unreadable` back to a null, so a served DPIA
  that is not UTF-8 was reported as *"no DPIA record"* when the DPIA **is** served. It says what
  it is now, and the missing-record branch is skipped so the two claims cannot both print.
- **R5-11.** Four mistyped declaration tables crashed out of load; they refuse now, and
  `nested_maps`/`nested_lists` joined the same guard.
- **R5-12.** A refusal sentence with an unknown placeholder loaded clean and raised at emit; only
  `{sensor}`, `{what}` and `{admissible}` are accepted.
- **R5-13.** `terminal` was never validated as a boolean and is consulted only over the
  pre-ladder batch, so it was decorative on nine refusals. It must be a boolean, and the table
  may mark terminal only what `_TERMINAL_CAPABLE` names — the five the code actually evaluates
  before the ladder. Marking `covert-sensing` terminal is now a refusal at load.
- **R5-14.** `version` must be a whole number and `bus_factor_scope` must read `one`, both
  checked at load, so the table's own bump instruction is no longer an instruction nothing
  enforces. The `requires:` sentences are stated in the table as prose for a reader, with
  `requires.dpia_fields` the one that is validated.

### Battery, re-run after the fixes

- `pytest tests/test_sensor_admission.py -n0 -q` → **153 passed** (21 failed first).
- `verify/sensor-admission/verify-sensor-admission.sh` → exit 3, **34 planted records and fifteen
  planted served estates grade as planted**.
- `mypy twin tests conftest.py` → Success, 189 source files.

## Waits on the owner

**Nothing.** Ticket 82's named-individuals ruling (its "Waits on the owner" item 3) is still
unanswered, and nothing designed here brushes it: that ruling is about whether the twin's own
corpus may keep the names of four living executives in the Intel scenario. This ticket never
decides what may be done with a named individual — it refuses one outright, in either direction
of that ruling. If the owner rules **B** (remove the names), nothing here changes; if the owner
rules **A** (keep them), nothing here changes either, because the corpus is public-record
citation and this rule governs **sensing**, which the corpus does not do.

## Not done

- **No adopter can pass this check** until one publishes an admission record and the DPIA it
  names (D7). The gate says so with a count rather than a green.
- **Nothing observes a sensor running.** There is no sensing substrate anywhere in this estate;
  the rule is graded, the sensing is not, and the manifest row prints that limit on every run.
- **The notice itself is not graded.** The check reads the notice's `published_at` as a string
  and does not open it: an adopter's notice document does not exist to open, and inventing a
  path for it would be a proxy for a notice rather than the notice. The day an adopter publishes
  one, resolving `published_at` against its served tree is a one-line addition.
- **`twin/roles.yaml` gains no sensor-admission role** (D3). If a later ticket wants the twin
  itself to sign an admission, that is a register bump and a re-pin of every signature's
  `role_register` digest, and it belongs with the ticket that needs it.
