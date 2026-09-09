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
  (each of the seven refusals red, then the one admissible sensor green) and **three planted
  single-unit estates whose served ref is a real `refs/remotes/origin/main`** — one that grades
  PASS, one whose record names an individual and grades FAIL, one with no admission record that
  grades SKIP with a count. The fixture's own git runs with `core.hooksPath` pointed at an empty
  directory, so the owner's global ggshield hook cannot make a fixture commit a load intermittent.
- **Leg 2, the estate, at the SERVED artefact.** Every fact is read with
  `git show origin/main:<path>` in the fetched clone, never the working tree: an uncommitted
  admission record is not one an adopter has published, and grading a worktree would let an
  uncommitted edit change the verdict. Three sub-legs: every `bus-factor-key-person` scenario
  still says "A role, never a person" and names a `people/<role>.yaml` the served tree carries;
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
- The three adopters' own people registers were read at `origin/main` and each names a role and
  nobody: `driftwood` `platform-engineer` + `data-protection-lead`, `tuppence`
  `payments-engineer` + `financial-crime-lead`, `ludlow` `platform-engineer` +
  `privacy-officer`. The check now refuses the day one of them gains a name.

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
