"""`ethics-gate` (build ticket 47, decision ticket 15) — the sixth and last of the six skills seam
3 (build ticket 42, `twin/skills.py`) exists to evaluate.

Decision ticket 15 Q1: sensor admission is a **ladder**, walked in order — **purpose, then
necessity, then proportionality** — reconciling total-scope ambition ("model the mechanism
universally") with data minimisation ("sense sparingly"). A sensor that fails a rung is refused
before the later rungs are even considered: failing purpose says nothing about whether a less
intrusive route exists, and asking that question anyway would dignify a sensor that should never
have been proposed. `walk_ladder()` below stops there, structurally rather than by convention.

Decision ticket 15 Q2 supplies two more judgements, both operationalised here for the first time
(the position itself was already stated in the decision ticket's own prose; no code realised it
before this ticket). **(b) the design rule** — prefer a sensor whose gaming *is* the desired
behaviour (Goodhart-proof by construction), and mark the rest rather than trust vigilance to catch
them. **(c) the backstop** — a metric improving faster than the underlying reality is grounds for
suspicion, never a verdict: `flag_fast_improvement()` never emits an adverse finding on its own,
and the only way one exists is a human's own `adjudicate_fast_improvement()`, attributable to a
registered role — the same "inferred/flagged first, human second" shape
`twin/evolution_judge.py` already established for evolution positions.

The **DPIA triage** (research 05 Part B.2, the ICO's 2023 monitoring guidance) is the "concrete
DPIA workflow" decision ticket 15 itself named as carried forward: `dpia_triage()` names the
monitoring cases the ICO lists as DPIA-mandatory — email/message, keystroke, biometric monitoring,
profiling, or a risk of financial loss to the worker — and `admit()` combines it with the ladder
into the **operational gate** decision ticket 15's own resolution describes: "admission requires
passing the ladder + a DPIA... reuse re-triggers both." The other half of that resolution — the
behavioural overlay's own detachability — is build ticket 07's, structural and unchanged here.

`ponytail:` `classify_gameability()`'s keyword match is fitted to decision ticket 15 Q2(b)'s own
worked example (bus-factor: gaming it means genuinely spreading knowledge) — the same honest move
`signal_classify.py` and `evolution_judge.py` make: the point being proven is the preference rule
and the backstop's structure, not classifier quality. Upgrade path: swap the body for a model
call; nothing else in this module, its tests or its harness guard changes, because `evaluate()`
(`twin/skills.py`) reads `skill_fn` as a bare callable.

No sensor fixture exists anywhere in `twin/fixtures.py` — decision ticket 15's own resolution
carries the sensor set itself forward as a build-time artefact, not decided here — so
`labelled_corpus()` below is hand-authored sensor proposals with known ladder outcomes, the same
shape `twin/skills.py`'s own `TOY_SKILL_CORPUS` is, rather than derived from an existing org.

**AC 2, "the sensor set + granularity decision" (build ticket 82)**: `sensors.yaml` is that
artefact — a versioned, closed table naming each sensor, what it observes and its coarsest-safe
granularity, mirroring `enactment-channels.yaml`'s shape. `load_sensors()` refuses an entry
missing a declared `kind` or `granularity`; `admit()` refuses a payload whose sensor id is not a
row in that table, before the ladder is even walked. Every id the table names is one a real caller
already proposes: `labelled_corpus()`'s five and `payroll-record`, the one enactment channel that
observes people at all.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR
from .sign import role_ids

SKILL = "ethics-gate"

GOODHART_PROOF = "goodhart-proof"
MARKED = "marked"

_RUNGS = ("purpose", "necessity", "proportionality")

# Necessity rung intrusiveness ranking, least intrusive first — decision ticket 15 Q1 rung 2's own
# words: "prefer structural over behavioural, aggregate over individual, cohort over person."
_KIND_RANK = {"structural": 0, "behavioural": 1}
_LEVEL_RANK = {"aggregate": 0, "cohort": 1, "individual": 2}

# A round, stated suspicion threshold for the fast-improvement backstop — 50% improvement in one
# reporting period — not a fitted number (decision ticket 15 Q2c).
_DEFAULT_FAST_IMPROVEMENT_RATE = 0.5

# Fitted to decision ticket 15 Q2(b)'s own worked example: gaming a bus-factor score means
# genuinely spreading knowledge, which is exactly what the sensor wants. See module docstring.
_GOODHART_PROOF_KEYWORDS = ("bus-factor", "bus factor", "knowledge spread", "spread knowledge")


class EthicsGateError(RuntimeError):
    """A malformed payload, an out-of-order call, or an adjudication with no flag or role."""


# -- the named sensor set (decision ticket 15 AC2, build ticket 82) -----------------------------

SENSOR_TABLE_PATH = PACKAGE_DIR / "sensors.yaml"
SENSOR_SCHEMA = "twin.sensors/v1"
SENSOR_REQUIRED = ("sensor", "name", "kind", "granularity", "observes")


@lru_cache(maxsize=8)
def load_sensors(path: Path | None = None) -> dict[str, Any]:
    """The versioned, closed sensor table, validated on read — the same discipline
    `corroboration.table()` applies to `enactment-channels.yaml`. A row missing a declared
    `kind` or `granularity` is refused rather than silently admitted with an assumed one.

    `ponytail:` cached per path, the same ceiling `corroboration.table()` carries and for the
    same reason — a test rewriting a table file in place sees the first version; write a new
    temp file instead.
    """
    source = path or SENSOR_TABLE_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SENSOR_SCHEMA:
        raise EthicsGateError(f"{source}: not a {SENSOR_SCHEMA} document")
    sensors = doc.get("sensors")
    if not isinstance(sensors, list) or not sensors:
        raise EthicsGateError(f"{source}: names no sensor")
    seen: set[str] = set()
    for row in sensors:
        if not isinstance(row, dict):
            raise EthicsGateError(f"{source}: a sensor entry is not a mapping")
        missing = [f for f in SENSOR_REQUIRED if not str(row.get(f, "")).strip()]
        if missing:
            raise EthicsGateError(
                f"{source}: sensor {row.get('sensor')!r} declares no {', '.join(missing)}"
            )
        sid = str(row["sensor"])
        if sid in seen:
            raise EthicsGateError(f"{source}: sensor {sid!r} is declared twice")
        seen.add(sid)
        if row["kind"] not in _KIND_RANK:
            raise EthicsGateError(f"{source}: sensor {sid!r} declares unknown kind {row['kind']!r}")
        if row["granularity"] not in _LEVEL_RANK:
            raise EthicsGateError(
                f"{source}: sensor {sid!r} declares unknown granularity {row['granularity']!r}"
            )
    return doc


def sensor_ids(path: Path | None = None) -> tuple[str, ...]:
    """Every named sensor id, in table order."""
    return tuple(str(row["sensor"]) for row in load_sensors(path)["sensors"])


# -- the admission ladder (decision ticket 15 Q1) -----------------------------------------------


def _intrusiveness(kind: str, level: str) -> tuple[int, int]:
    if kind not in _KIND_RANK:
        raise EthicsGateError(f"{SKILL}: unknown sensor kind {kind!r} (have: {sorted(_KIND_RANK)})")
    if level not in _LEVEL_RANK:
        raise EthicsGateError(f"{SKILL}: unknown sensor level {level!r} (have: {sorted(_LEVEL_RANK)})")
    return (_KIND_RANK[kind], _LEVEL_RANK[level])


def _check_purpose(rung: dict[str, Any]) -> tuple[bool, str]:
    scenario = str(rung.get("scenario") or "").strip()
    will_act = bool(rung.get("will_act"))
    if not scenario:
        return False, "no named scenario consumes this sensor — a sensor feeding nothing is surveillance for its own sake"
    if not will_act:
        return False, f"a scenario ({scenario!r}) is named but nobody will act on what this sensor feeds it"
    return True, f"scenario {scenario!r} consumes this sensor and will be acted on"


def _check_necessity(rung: dict[str, Any]) -> tuple[bool, str]:
    chosen_kind, chosen_level = str(rung["kind"]), str(rung["level"])
    chosen = _intrusiveness(chosen_kind, chosen_level)
    alternatives = rung.get("alternatives") or []
    for alt in alternatives:
        alt_kind, alt_level = str(alt["kind"]), str(alt["level"])
        if _intrusiveness(alt_kind, alt_level) < chosen:
            return False, (
                f"a less intrusive route exists ({alt_kind}/{alt_level}) that answers the same "
                f"question as {chosen_kind}/{chosen_level} — prefer structural over behavioural, "
                "aggregate over individual, cohort over person"
            )
    return True, (
        f"no less intrusive alternative among {len(alternatives)} considered outranks "
        f"{chosen_kind}/{chosen_level}"
    )


def _check_proportionality(rung: dict[str, Any]) -> tuple[bool, str]:
    cost, value = float(rung["intrusion_cost"]), float(rung["value_illuminated"])
    if value <= cost:
        return False, f"the illuminated value ({value}) does not outweigh the intrusion imposed ({cost})"
    return True, f"the illuminated value ({value}) outweighs the intrusion imposed ({cost})"


_RUNG_CHECKS = {"purpose": _check_purpose, "necessity": _check_necessity, "proportionality": _check_proportionality}


def walk_ladder(payload: dict[str, Any]) -> dict[str, Any]:
    """The ladder itself. `payload` is `{"purpose": {...}, "necessity": {...}, "proportionality":
    {...}}` — one dict per rung, in `_RUNGS` order.

    Walked strictly in order, and a failing rung **stops the process**: the loop breaks before the
    next rung's check function is even called, so a later rung's payload is never read once an
    earlier one has failed — structural, not merely a return value a caller could ignore. Returns
    `{"admitted", "stopped_at", "rungs"}`, where `rungs` holds only the rungs actually evaluated,
    each carrying a non-empty `justification` — the recorded reason this ticket's own checklist
    asks for, on both a pass and a fail.
    """
    missing = [f for f in _RUNGS if f not in payload]
    if missing:
        raise EthicsGateError(f"{SKILL}: payload declares no {', '.join(missing)}")
    rungs: list[dict[str, Any]] = []
    for rung in _RUNGS:
        passed, justification = _RUNG_CHECKS[rung](payload[rung])
        rungs.append({"rung": rung, "passed": passed, "justification": justification})
        if not passed:
            break
    admitted = len(rungs) == len(_RUNGS) and all(r["passed"] for r in rungs)
    return {"admitted": admitted, "stopped_at": None if admitted else rungs[-1]["rung"], "rungs": tuple(rungs)}


# -- the DPIA triage (research 05 Part B.2, the ICO's 2023 monitoring guidance) -----------------

# The ICO's own list of monitoring cases that trigger a mandatory DPIA (research 05 Part B.2):
# email/message monitoring, keystroke monitoring, biometric data, and (separately) any profiling
# or any monitoring likely to cause the worker financial loss.
_DPIA_CHANNEL_TRIGGERS = ("email", "messages", "keystroke", "biometric")


def dpia_triage(payload: dict[str, Any]) -> dict[str, Any]:
    """`payload` is `{"channels": [...], "profiling": bool, "financial_loss_risk": bool}`.

    Returns `{"mandatory", "triggers", "citation"}` — never a judgement about whether the DPIA has
    actually been *done*; `admit()` below is where a mandatory-but-incomplete DPIA blocks
    admission. Triage names why a DPIA is mandatory; it is not the DPIA itself.
    """
    channels = {str(c) for c in (payload.get("channels") or [])}
    triggers = sorted(channels & set(_DPIA_CHANNEL_TRIGGERS))
    if payload.get("profiling"):
        triggers.append("profiling")
    if payload.get("financial_loss_risk"):
        triggers.append("financial_loss_risk")
    return {
        "mandatory": bool(triggers),
        "triggers": sorted(set(triggers)),
        "citation": (
            "ICO Employment Practices guidance, Monitoring workers (2023); UK GDPR Art. 35; "
            "DPA 2018 — research 05 Part B.2"
        ),
    }


# -- the full skill: ladder + DPIA gate together (decision ticket 15's own "operational gate") --


def admit(payload: dict[str, Any]) -> dict[str, Any]:
    """The skill. `payload` is `{"sensor": {"id", "name"}, "purpose": {...}, "necessity": {...},
    "proportionality": {...}, "dpia": {"channels", "profiling", "financial_loss_risk", "complete"}}`.

    `payload["sensor"]["id"]` must name a row in `sensors.yaml` — decision ticket 15 AC2's closed
    table, checked here rather than left as any string a caller happens to pass (build ticket 82).
    An unnamed sensor is refused before the ladder is even walked.

    A sensor is admitted only when the ladder is admitted **and** any mandatory DPIA is recorded
    complete — decision ticket 15's own resolution of AC 5: "admission requires passing the ladder
    + a DPIA." Detachment of the behavioural overlay itself (the resolution's other half) is
    build ticket 07's structural mechanism and is untouched by this module.

    Returns a grade-5 claim-shaped dict (`kind`, `component`, `evidence_grade`, `claimed_by`,
    `evidence`), the same shape `signal_classify.classify()`/`evolution_judge.judge()` return —
    `evidence_grade` is a literal `5`, no parameter here can set it to anything else. `kind` is
    `'sensor-admission'`, not (yet) one of `schema.py`'s closed `claim.kind` values: no acceptance
    criterion here asks for this to be committed into a model repository, the same limit
    `gameplay_lens.propose()`'s own claim-shaped output states.
    """
    missing = [f for f in ("sensor", *_RUNGS, "dpia") if f not in payload]
    if missing:
        raise EthicsGateError(f"{SKILL}: payload declares no {', '.join(missing)}")
    sensor_id = str(payload["sensor"]["id"])
    known = sensor_ids()
    if sensor_id not in known:
        raise EthicsGateError(
            f"{SKILL}: {sensor_id!r} is not a named sensor (have: {', '.join(known)}) — "
            f"{SENSOR_TABLE_PATH.name} is the closed table, not any string a payload proposes"
        )
    ladder = walk_ladder({rung: payload[rung] for rung in _RUNGS})
    triage = dpia_triage(payload["dpia"])
    dpia_complete = bool(payload["dpia"].get("complete"))
    dpia_satisfied = (not triage["mandatory"]) or dpia_complete
    admitted = ladder["admitted"] and dpia_satisfied

    if not ladder["admitted"]:
        reason = f"stopped at the {ladder['stopped_at']} rung: {ladder['rungs'][-1]['justification']}"
    elif not dpia_satisfied:
        reason = (
            f"the ladder passed but a DPIA is mandatory ({', '.join(triage['triggers'])}) and is "
            "not recorded complete"
        )
    else:
        reason = "the ladder passed and no outstanding DPIA gate blocks admission"

    return {
        "admitted": admitted,
        "ladder": ladder,
        "dpia": {**triage, "complete": dpia_complete, "satisfied": dpia_satisfied},
        "claim": {
            "kind": "sensor-admission",
            "component": payload["sensor"]["id"],
            "evidence_grade": 5,
            "claimed_by": f"{SKILL} (skill)",
            "evidence": reason,
        },
    }


def scorer(actual: Any, expected: Any) -> bool:
    """A pass needs both the overall admission decision and where the ladder itself stopped —
    `stopped_at` distinguishes 'the ladder never passed' from 'the ladder passed but the DPIA
    gate blocked it' (both report `admitted: False`), which is the distinction this skill exists
    to get right."""
    return (
        actual.get("admitted") == expected["admitted"]
        and actual.get("ladder", {}).get("stopped_at") == expected.get("stopped_at")
    )


# -- gameability marking and the preference rule (decision ticket 15 Q2(b)) ---------------------


def classify_gameability(payload: dict[str, Any]) -> dict[str, Any]:
    """`payload` is `{"sensor": {"id", ...}, "metric_description": str}`.

    `marked` is the safe default — decision ticket 15 Q2(b): "where none exists, mark
    gameability explicitly" — `goodhart-proof` requires positive evidence that gaming the metric
    requires doing the genuinely desired thing.
    """
    missing = [f for f in ("sensor", "metric_description") if f not in payload]
    if missing:
        raise EthicsGateError(f"{SKILL}: payload declares no {', '.join(missing)}")
    text = str(payload["metric_description"]).lower()
    if any(k in text for k in _GOODHART_PROOF_KEYWORDS):
        marking = GOODHART_PROOF
        reason = "gaming this metric requires doing the genuinely desired thing (decision ticket 15 Q2b)"
    else:
        marking = MARKED
        reason = "no evidence gaming this metric requires the desired behaviour; marked rather than preferred"
    return {"sensor": payload["sensor"]["id"], "gameability": marking, "reason": reason}


def prefer(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """The preference rule itself, applied and recorded — decision ticket 15 Q2(b), "prefer
    sensors where gaming the metric IS the desired behaviour." Every candidate is classified, and
    every goodhart-proof one is preferred over every merely-marked one; where none is
    goodhart-proof, that is recorded too rather than silently picking one."""
    if not candidates:
        raise EthicsGateError(f"{SKILL}: prefer() needs at least one candidate sensor to choose among")
    marked = [classify_gameability(c) for c in candidates]
    preferred = [m["sensor"] for m in marked if m["gameability"] == GOODHART_PROOF]
    reason = (
        f"{', '.join(preferred)} preferred: gaming the metric is the desired behaviour"
        if preferred
        else "no candidate is goodhart-proof; none preferred on gameability grounds alone"
    )
    return {"candidates": marked, "preferred": preferred, "reason": reason}


# -- fast improvement: suspicion, never a verdict (decision ticket 15 Q2(c)) ---------------------


def flag_fast_improvement(payload: dict[str, Any]) -> dict[str, Any]:
    """`payload` is `{"sensor": {"id", ...}, "baseline": float, "current": float,
    "rate_threshold": float?}`.

    Never carries an adverse finding, a verdict, or a recommendation — checked directly by the
    harness guard against `twin/invariants`'s own banned-word scan, the same one
    `no_recommended_action_field` runs. `flagged` says only that the improvement is fast enough to
    be *worth a human looking*; nothing here concludes gaming occurred.
    """
    missing = [f for f in ("sensor", "baseline", "current") if f not in payload]
    if missing:
        raise EthicsGateError(f"{SKILL}: payload declares no {', '.join(missing)}")
    sensor_id = payload["sensor"]["id"]
    baseline, current = float(payload["baseline"]), float(payload["current"])
    threshold = float(payload.get("rate_threshold", _DEFAULT_FAST_IMPROVEMENT_RATE))
    if baseline == 0:
        rate = 0.0 if current == 0 else float("inf")
    else:
        rate = (current - baseline) / abs(baseline)
    flagged = rate >= threshold
    statement = (
        f"improved at a rate of {rate:.2f}, at or above the suspicion threshold {threshold:.2f} — "
        "flagged for human adjudication; this is grounds for suspicion, never an automatic finding"
        if flagged
        else f"improved at a rate of {rate:.2f}, below the suspicion threshold {threshold:.2f} — no flag raised"
    )
    return {
        "sensor": sensor_id,
        "rate": rate,
        "threshold": threshold,
        "flagged": flagged,
        "requires_human_adjudication": flagged,
        "statement": statement,
    }


def adjudicate_fast_improvement(flag: dict[str, Any], role: str, finding: str, reason: str) -> dict[str, Any]:
    """The only way a fast-improvement flag becomes an actual finding: a human, holding a
    registered role (`twin/roles.yaml`), states one. Refuses to run against a flag that was never
    raised — structurally, so "adjudicate" cannot be called into existence on nothing — and
    refuses an unregistered role, the same discipline `evolution_judge.override()` applies.
    """
    if not flag.get("flagged"):
        raise EthicsGateError(f"{SKILL}: adjudicate_fast_improvement() needs a raised flag, not a clear one")
    if role not in role_ids():
        raise EthicsGateError(f"{SKILL}: {role!r} is not in the role register — adjudication attaches to a registered role")
    if not finding.strip():
        raise EthicsGateError(f"{SKILL}: a finding with no statement is not an adjudication")
    return {
        "kind": "fast-improvement-adjudication",
        "sensor": flag["sensor"],
        "claimed_by": role,
        "finding": finding.strip(),
        "evidence": reason,
        "evidence_grade": 4,
    }


# -- the labelled corpus: hand-authored sensor proposals with known ladder outcomes -------------


def labelled_corpus() -> list[dict[str, Any]]:
    """Five sensor proposals with known outcomes, spanning every way `admit()` can refuse and the
    one way it admits — no sensor fixture exists in `twin/fixtures.py` to derive this from (see
    module docstring), so this is hand-authored, the same shape `skills.TOY_SKILL_CORPUS` is.
    """
    no_dpia = {"channels": [], "profiling": False, "financial_loss_risk": False, "complete": False}
    items: list[dict[str, Any]] = [
        {
            "id": "bus-factor-structural-aggregate",
            "input": {
                "sensor": {"id": "bus-factor-structural-aggregate", "name": "Commit-structure bus-factor, aggregated"},
                "purpose": {"scenario": "key-person-succession-planning", "will_act": True},
                "necessity": {
                    "kind": "structural", "level": "aggregate",
                    "alternatives": [{"kind": "behavioural", "level": "individual"}],
                },
                "proportionality": {"intrusion_cost": 500.0, "value_illuminated": 50000.0},
                "dpia": no_dpia,
            },
            "expected": {"admitted": True, "stopped_at": None},
        },
        {
            "id": "mood-sensor-no-scenario",
            "input": {
                "sensor": {"id": "mood-sensor-no-scenario", "name": "Ambient sentiment sensor"},
                "purpose": {"scenario": "", "will_act": False},
                "necessity": {"kind": "structural", "level": "aggregate", "alternatives": []},
                "proportionality": {"intrusion_cost": 100.0, "value_illuminated": 1000.0},
                "dpia": no_dpia,
            },
            "expected": {"admitted": False, "stopped_at": "purpose"},
        },
        {
            "id": "individual-email-content-when-aggregate-suffices",
            "input": {
                "sensor": {"id": "individual-email-content-when-aggregate-suffices", "name": "Per-person email content scan"},
                "purpose": {"scenario": "insider-risk-monitoring", "will_act": True},
                "necessity": {
                    "kind": "behavioural", "level": "individual",
                    "alternatives": [{"kind": "structural", "level": "aggregate"}],
                },
                "proportionality": {"intrusion_cost": 1000.0, "value_illuminated": 100000.0},
                "dpia": {**no_dpia, "channels": ["email"]},
            },
            "expected": {"admitted": False, "stopped_at": "necessity"},
        },
        {
            "id": "expensive-surveillance-low-value",
            "input": {
                "sensor": {"id": "expensive-surveillance-low-value", "name": "Full-team activity dashboard"},
                "purpose": {"scenario": "attrition-risk-monitoring", "will_act": True},
                "necessity": {"kind": "structural", "level": "aggregate", "alternatives": []},
                "proportionality": {"intrusion_cost": 100000.0, "value_illuminated": 1000.0},
                "dpia": no_dpia,
            },
            "expected": {"admitted": False, "stopped_at": "proportionality"},
        },
        {
            "id": "keystroke-monitoring-no-dpia",
            "input": {
                "sensor": {"id": "keystroke-monitoring-no-dpia", "name": "Keystroke-cadence monitor"},
                "purpose": {"scenario": "insider-risk-monitoring", "will_act": True},
                "necessity": {"kind": "structural", "level": "aggregate", "alternatives": []},
                "proportionality": {"intrusion_cost": 1000.0, "value_illuminated": 50000.0},
                "dpia": {"channels": ["keystroke"], "profiling": False, "financial_loss_risk": False, "complete": False},
            },
            "expected": {"admitted": False, "stopped_at": None},
        },
    ]
    return items
