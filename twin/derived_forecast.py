"""A probability the twin DERIVES from signals, pre-registered on the served branch and scored
against the overlay's own outcome record (ecosystem ticket 93; ticket 75 Q10, owner-reasoned).

Until this module every probability the twin scored was a number read from YAML -- a world
model's `beliefs` -- and the package said so at run time. The owner decided (ticket 75 Q10) that
the twin may derive one with a model call, on the condition that the model runs inside Claude
Code on his machine: the local clock (`talk/local-clock.sh`, ticket 92) runs the
`/derive-probability` skill headlessly and the result lands as a pull request on the adopter's
own repository. This module is the pure-code half of that: the artefact, its validator, the
listing the model derives from, and the check that grades pre-registration and scoring.

**The artefact** is `twin.derived-forecast/v1`, one file per run at
`<adopter>/twin/forecasts/<date>-<slug>.forecast.yaml`. Not under `twin/orgs/<org>/`: the
overlay loader (`twin/model.py` `Overlay.load`) refuses any directory it does not read, so a
`forecasts/` collection there would fail every adopter's twin gate; the file sits beside
`twin/claims/` (the classify-and-judge precedent) and is joined to the overlay by proposition.
Every probability in it carries:

  * `perspective` and `currency` -- the seat it is a forecast for and the currency that seat
    prices in (`twin/currency.yaml`, checked against the perspective). It never prices itself:
    `price_eligible: false`, because a derivation is a model assertion (grade 5) and the ladder
    prices only grades inside `pricing_threshold` (2). `prices_through` names the path.
  * `basis: derived | recorded` -- item 4 of the ticket. A world model still carries a recorded
    belief where no signal exists, and the artefact says which of the two each probability is.
    A `recorded` probability is the world model's number UNCHANGED, with no signals. A `derived`
    one rests on at least one signal and states its reasoning.
  * the evidence grade the schema allows. `derived`: exactly `DERIVED_GRADE` (5, model
    assertion) -- and never stronger than the weakest signal it rests on, which is an ORDER
    STATISTIC on the ladder, not arithmetic (the ordinal ruling, reopened only this far: a
    comparison is allowed, a sum, a mean or a weight is not, and the validator refuses a
    `weight` or `score` on a signal). `recorded`: `null`, with `grade_absent_because`. The
    world-model schema (`twin/schema.py` `world-model`: `beliefs: mapping_of(probability)`)
    carries no source and no grade for a belief, and the ladder has no rung for an unsourced
    authored number. That is a finding the artefact records, not a schema this ticket loosens.
  * `recorded_belief` -- the world model's own number, kept beside the derivation the way an
    override keeps the position it answers (`answers`), so the disagreement is on the record.
  * `signals[]` -- for a derived probability, the feed observations it rested on: a market MOVE
    between two dated levels (`twin/market_signals.py`: the derivative, never the level; a
    signal carrying `probability` or `implied_probability` is refused) or a news event with
    its URL. Each names its envelope in `derived_from` shape, and the validator confirms the
    served envelope CARRIES that observation. A statement with no observation behind it is a
    scenario, not a signal.

**Pre-registration is git history, not a field.** `first_reached()` reads TWO first-parent
committer dates on the served ref (`refs/remotes/origin/main`): when the path ARRIVED, and when
it was LAST WRITTEN there. On GitHub the arrival is the merge, dated by GitHub. `pre_registered()`
keys on the last write and both dates are printed, because measuring the arrival alone measures
the PATH and not the CONTENT: a forecast rewritten after it landed -- in place, by delete and
re-add, or by a squash-add -- kept the original arrival date and was scored (review F1, measured:
re-added 2026-07-20 with `probability: 0.999` against an outcome on main since 2026-07-01,
`pre-registered: yes` at 2026-02-01, `brier=1e-06`, PASS). Under the last write, a number
rewritten after it landed is a NEW forecast and re-registers on the day of the rewrite. A RENAME
still costs a forecast its registration, which is the honest direction and is kept. A forecast
the twin dates early and a human merges late is not pre-registered, and a probability that was
not pre-registered is not scored (item 3).

**Scoring is `twin/scoring.py`, computed, never read.** The outcome is the overlay's own
`outcomes/` record (`twin/schema.py` `outcome`: `proposition, observed, resolved_on, source,
contamination, source_dated`), authored by a human, merged by a human, and it too must have
reached the served ref on or after the date it says it resolved. The answer key is immutable once
it is there: an outcome REWRITTEN on the served ref is refused by name, because editing it
silently rescores every forecast it resolves while the run goes on printing the original date
(review F2, measured: `observed: true` -> `false` moved brier 0.5329 -> 0.0729, both PASS). Two
outcomes resolving one proposition are refused too, rather than the first sorted one silently
winning. `check()` pairs each forecast with the outcome resolving its proposition and prints the
Brier and log scores it computes.

`ponytail:` hand-rolled rules, no jsonschema, for the same reason `validate_claim.py` gives:
the adopter-side python has pyyaml and not jsonschema. The claim kinds, the roles and the
pricing threshold are read off the twin itself, never copied.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path
from typing import Any, NamedTuple

import yaml

from . import market_signals, schema, scoring
from .evidence import threshold as pricing_threshold
from .feed_signal import EVIDENCE_GRADE as FEED_GRADE

SCHEMA = "twin.derived-forecast/v1"
SKILL = "derive-probability"
BASES = ("derived", "recorded")
SIGNAL_KINDS = ("market-move", "news-event")
FORECASTS_DIR = "twin/forecasts"
SUFFIX = ".forecast.yaml"
# The pool a derivation may rest on: the two feeds that carry DATED series. Read the way
# classify-and-judge reads them -- the served envelope, cited by its own name and version.
POOL_FEEDS = ("market-moves", "news")
PIN_FIELDS = ("party", "kind", "name", "version")

# A derivation is a model assertion: the ladder's weakest rung, the one feed_signal gives a
# lookup nobody read. Named once, beside the rung it equals, so a grep for the rung finds it.
DERIVED_GRADE = FEED_GRADE
GRADE_ABSENT_BECAUSE = (
    "twin/schema.py world-model: beliefs is mapping_of(probability) -- a recorded belief "
    "carries no source and no grade, and twin/evidence-ladder.yaml has no rung for an "
    "unsourced authored number (ecosystem ticket 93, a finding, not a schema change)"
)
# Keys that would make a grade or a level into a number something could do arithmetic on.
FORBIDDEN_SIGNAL_KEYS = ("weight", "score", "probability", "implied_probability")

# The pool served today is pinned by no adopter and tagged by no publisher; that is printed as
# a number on every check, and is why nothing derived from it is price-eligible (ticket 23).
PRICES_THROUGH = (
    "composition under the perspective, only through a causal path graded inside "
    "path_admission_threshold; this artefact itself never prices"
)


class DerivedForecastError(ValueError):
    pass


class CannotLook(RuntimeError):
    """A validator or check that could not read what it grades against. Never a pass."""


class StrictLoader(yaml.SafeLoader):
    """`yaml.SafeLoader`, with a duplicate mapping key REFUSED instead of silently resolved.

    PyYAML keeps the LAST of two identical keys, so a file whose visible `probability: 0.999`
    sits above a real `probability: 0.27` validates as 0.27: the file a human reviews in the
    pull request is not the file the validator read (review F4, measured -- the clock committed
    it). Every YAML this module reads goes through here.
    """

    def construct_mapping(self, node: Any, deep: bool = False) -> dict[Any, Any]:
        seen: set[Any] = set()
        for key_node, _ in node.value:
            key = self.construct_object(key_node, deep=deep)
            if key in seen:
                raise yaml.constructor.ConstructorError(
                    "while constructing a mapping", node.start_mark,
                    f"duplicate key {key!r}: PyYAML keeps the last, so the file a human reads is "
                    f"not the file this validator reads", key_node.start_mark)
            seen.add(key)
        return super().construct_mapping(node, deep=deep)


def load_yaml(text: str, where: str) -> Any:
    """`yaml.safe_load` with duplicate keys refused (StrictLoader), as a DerivedForecastError."""
    try:
        return yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise DerivedForecastError(f"{where} is not YAML this validator will read: {exc}") from exc


# --- the served envelopes ---------------------------------------------------------------------


def pin_key(pin: dict[str, Any]) -> tuple[str, ...]:
    return tuple(str(pin.get(field, "")) for field in PIN_FIELDS)


def feed_envelope(feeds_root: Path, name: str, version: str) -> dict[str, Any]:
    """The published envelope for `name` at `version`, read off the feeds checkout the way the
    feed contract lays it out (`<name>/v<MAJOR>/feed.json`). The envelope's own `version` must
    equal the one cited: a major directory is not a version."""
    major = str(version).lstrip("v").split(".", 1)[0]
    path = Path(feeds_root) / name / f"v{major}" / "feed.json"
    if not path.is_file():
        raise CannotLook(f"no envelope at {path} to confirm an observation against")
    envelope = json.loads(path.read_text(encoding="utf-8"))
    if envelope.get("kind") != "feed" or str(envelope.get("name")) != name:
        raise CannotLook(f"{path} is not the {name!r} feed envelope")
    if str(envelope.get("version")) != str(version):
        raise DerivedForecastError(
            f"{name} is served at version {envelope.get('version')!r}, not the cited {version!r}"
        )
    return envelope


def market_moves(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    """Every consecutive dated MOVE the served market-moves envelope carries, as
    `twin/market_signals.py` derives them. No level appears alone."""
    payload = envelope.get("payload") or {}
    observations = [
        market_signals.PriceObservation(str(mid), str(m["venue"]), str(p["date"]), float(p["price_level"]))
        for mid, m in (payload.get("markets") or {}).items()
        for p in m.get("observations", [])
    ]
    pin = {"party": str(envelope["published_by"]), "kind": "feed", "name": str(envelope["name"]),
           "version": str(envelope["version"])}
    out = []
    for move in market_signals.price_moves(observations):
        market = payload["markets"][move.question_id]
        out.append({
            "kind": "market-move",
            "market": move.question_id,
            "venue": move.venue,
            "question": str(market.get("question", "")),
            "from_date": move.from_date,
            "to_date": move.to_date,
            "from_level": move.from_level,
            "to_level": move.to_level,
            "statement": market_signals.move_statement(move),
            "from": pin,
        })
    return out


def news_events(envelope: dict[str, Any]) -> list[dict[str, Any]]:
    payload = envelope.get("payload") or {}
    pin = {"party": str(envelope["published_by"]), "kind": "feed", "name": str(envelope["name"]),
           "version": str(envelope["version"])}
    return [
        {
            "kind": "news-event",
            "event": str(e["id"]),
            "date": str(e["date"]),
            "source": str(e.get("source", "")),
            "statement": str(e["statement"]),
            "url": str((e.get("provenance") or {}).get("url", "")),
            "from": pin,
        }
        for e in payload.get("events", [])
    ]


def _close(a: Any, b: Any) -> bool:
    try:
        return abs(float(a) - float(b)) < 1e-9
    except (TypeError, ValueError):
        return False


def observation_missing(signal: dict[str, Any], feeds_root: Path) -> str | None:
    """Why the served envelope does NOT carry this signal's observation; None when it does."""
    pin = signal.get("from") or {}
    kind = signal.get("kind")
    envelope = feed_envelope(feeds_root, str(pin.get("name", "")), str(pin.get("version", "")))
    if kind == "market-move":
        for move in market_moves(envelope):
            if (move["market"] == signal.get("market") and move["venue"] == signal.get("venue")
                    and move["from_date"] == signal.get("from_date") and move["to_date"] == signal.get("to_date")
                    and _close(move["from_level"], signal.get("from_level"))
                    and _close(move["to_level"], signal.get("to_level"))):
                if signal.get("statement") != move["statement"]:
                    return (f"statement is not the move's own sentence; the feed's move reads: "
                            f"{move['statement']!r}")
                return None
        return (f"{pin.get('name')}@{pin.get('version')} does not carry a move of "
                f"{signal.get('market')!r} on {signal.get('venue')!r} from {signal.get('from_level')!r} "
                f"({signal.get('from_date')}) to {signal.get('to_level')!r} ({signal.get('to_date')}) "
                f"between consecutive observations")
    if kind == "news-event":
        for event in news_events(envelope):
            if event["event"] == signal.get("event"):
                if event["date"] != signal.get("date") or event["url"] != signal.get("url"):
                    return (f"event {event['event']!r} is dated {event['date']} with url {event['url']!r} "
                            f"in the served feed, not {signal.get('date')} / {signal.get('url')!r}")
                if signal.get("statement") != event["statement"]:
                    return f"statement is not the event's own; the feed reads: {event['statement']!r}"
                return None
        return f"{pin.get('name')}@{pin.get('version')} does not carry an event {signal.get('event')!r}"
    return f"signal kind {kind!r} is not one of {SIGNAL_KINDS}"


# --- the overlay side --------------------------------------------------------------------------


def _read_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    doc = load_yaml(path.read_text(encoding="utf-8"), str(path))
    return doc if isinstance(doc, dict) else None


def overlay_dir(adopter_root: Path, org: str) -> Path:
    return Path(adopter_root) / "twin" / "orgs" / org


def world_model_beliefs(adopter_root: Path, org: str, world_model: str) -> dict[str, float] | None:
    """The beliefs of a world model by id, from the overlay's own `world_models/` or the vendored
    world layer's. None when no such world model is in either place."""
    for base in (overlay_dir(adopter_root, org) / "world_models", Path(adopter_root) / "twin" / "world" / "world_models"):
        doc = _read_yaml(base / f"{world_model}.yaml")
        if doc is not None and str(doc.get("id")) == world_model:
            return {str(k): float(v) for k, v in (doc.get("beliefs") or {}).items()}
    return None


def currency_of(adopter_root: Path, perspective: str) -> str | None:
    doc = _read_yaml(Path(adopter_root) / "twin" / "currency.yaml")
    if doc is not None:
        value = (doc.get("perspectives") or {}).get(perspective)
        if value:
            return str(value)
    party = _read_yaml(Path(adopter_root) / "party.yaml")
    if party is not None and party.get("reporting_currency"):
        return str(party["reporting_currency"])
    return None


def pinned_pool_feeds(adopter_root: Path) -> dict[str, bool]:
    party = _read_yaml(Path(adopter_root) / "party.yaml") or {}
    pinned = {str(p.get("name", "")) for p in party.get("inherits") or [] if p.get("kind") == "feed"}
    return {name: name in pinned for name in POOL_FEEDS}


def inputs(adopter_root: Path, org: str, feeds_root: Path) -> dict[str, Any]:
    """What the model derives from: every scenario with its recorded beliefs, and the pool as
    dated moves and dated events. Deterministic, so two runs read the same listing; the model's
    judgement is the only thing that is not."""
    adopter_root, feeds_root = Path(adopter_root), Path(feeds_root)
    scenarios = []
    for path in sorted((overlay_dir(adopter_root, org) / "scenarios").glob("*.yaml")):
        doc = _read_yaml(path) or {}
        beliefs = {}
        for wm in doc.get("world_models") or []:
            known = world_model_beliefs(adopter_root, org, str(wm)) or {}
            if str(doc.get("proposition")) in known:
                beliefs[str(wm)] = known[str(doc["proposition"])]
        scenarios.append({
            "id": str(doc.get("id")),
            "proposition": str(doc.get("proposition")),
            "at": str(doc.get("at")),
            "horizon": str(doc.get("horizon")),
            "components": [str(c) for c in doc.get("components") or []],
            "world_models": [str(w) for w in doc.get("world_models") or []],
            "recorded_beliefs": beliefs,
        })
    pool: dict[str, Any] = {}
    for name in POOL_FEEDS:
        candidates = sorted((feeds_root / name).glob("v*/feed.json")) if (feeds_root / name).is_dir() else []
        if not candidates:
            pool[name] = {"served": False, "reason": f"no {name}/v*/feed.json under {feeds_root}"}
            continue
        envelope = json.loads(candidates[-1].read_text(encoding="utf-8"))
        entry: dict[str, Any] = {"served": True, "version": str(envelope.get("version")),
                                 "published_at": str(envelope.get("published_at"))}
        if name == "market-moves":
            entry["moves"] = market_moves(envelope)
        else:
            entry["events"] = news_events(envelope)
        pool[name] = entry
    perspectives = sorted(p.stem for p in (overlay_dir(adopter_root, org) / "perspectives").glob("*.yaml"))
    return {
        "org": org,
        "adopter_root": str(adopter_root),
        "feeds_root": str(feeds_root),
        "scenarios": scenarios,
        "perspectives": {p: currency_of(adopter_root, p) for p in perspectives},
        "pool": pool,
        "subscribed": pinned_pool_feeds(adopter_root),
        "note": ("a market LEVEL is never a probability (twin/market_signals.as_probability refuses); "
                 "a recorded belief is the number above, unchanged; a derived probability rests on at "
                 "least one move or event listed here and on nothing that is not"),
    }


# --- the validator -----------------------------------------------------------------------------


def validate(doc: dict[str, Any], roles: set[str], headless: bool = False,
             adopter_root: Path | None = None, feeds_root: Path | None = None) -> list[str]:
    """Every reason `doc` is not a forecast file the twin can read; [] when it is. `headless` is
    the caller's fact (the local clock passes --headless). With `adopter_root` the scenario,
    perspective, currency and recorded belief are checked against the overlay; with `feeds_root`
    every signal is checked against the served envelope. Raises CannotLook when a root was given
    and cannot be read: a file nobody could check is not proposed, and not a pass."""
    bad: list[str] = []

    def need(condition: bool, message: str) -> None:
        if not condition:
            bad.append(message)

    need(doc.get("schema") == SCHEMA, f"schema is {doc.get('schema')!r}, not {SCHEMA!r}")
    org = str(doc.get("org") or "")
    need(bool(org), "no org: a forecast file belongs to one adopter")
    need(not doc.get("injected"),
         "injected: true -- this is a world-simulator rehearsal (talk/local-clock.sh --inject) and "
         "it is refused wherever it is presented")
    run = doc.get("run") or {}
    if headless:
        need(run.get("headless") is True,
             f"run.headless is {run.get('headless')!r}: this file was written by a headless run "
             f"(the local clock, nobody at the keyboard) and does not say so")
    need(run.get("skill") == SKILL, f"run.skill is {run.get('skill')!r}: this file names no skill that produced it")
    need(str(run.get("operator_role", "")) in roles,
         f"run.operator_role {run.get('operator_role')!r} is not a role in twin/roles.yaml")

    derived_from = doc.get("derived_from") or []
    need(bool(derived_from), "derived_from is empty: a forecast derived from nothing published is not evidence")
    for index, pin in enumerate(derived_from):
        for field in PIN_FIELDS:
            need(bool(pin.get(field)), f"derived_from[{index}] has no {field}")
        need(pin.get("kind") == "feed", f"derived_from[{index}] kind {pin.get('kind')!r} is not feed")
        need(str(pin.get("name")) in POOL_FEEDS,
             f"derived_from[{index}] names {pin.get('name')!r}, which carries no dated series; the pool is {POOL_FEEDS}")
    declared = {pin_key(p) for p in derived_from}
    cited: set[tuple[str, ...]] = set()

    forecasts = doc.get("forecasts") or []
    need(bool(forecasts), "no forecasts: an empty forecast file is not a proposal")
    ids = [f.get("id") for f in forecasts]
    need(len(set(ids)) == len(ids), f"duplicate forecast ids in {ids}")
    threshold = pricing_threshold()

    for f in forecasts:
        where = f"forecast {f.get('id')!r}"
        need(not f.get("injected"), f"{where}: injected: true -- a rehearsal forecast is refused")
        # SKILL.md 2 and this ticket's Answer both say EVERY forecast carries these. `reasoning`
        # says why the number is what it is; `prices_through` names the only path a number here
        # could ever reach money by; `recorded_belief` keeps the world model's own number beside
        # the derivation so the disagreement is on the record and both can be scored. All three
        # were promised and none of the last two was required (review F7, both measured ACCEPTED
        # when absent) -- a sentence claiming more than the run measured.
        for field in ("scenario", "proposition", "perspective", "reasoning", "prices_through"):
            need(bool(f.get(field)), f"{where}: no {field}")
        try:
            schema.probability(f.get("probability"), where)
        except schema.SchemaError as exc:
            bad.append(str(exc))
        try:
            schema.date(f.get("resolves_on"), f"{where}.resolves_on")
        except schema.SchemaError as exc:
            bad.append(str(exc))
        currency = str(f.get("currency") or "")
        need(len(currency) == 3 and currency.isalpha() and currency.isupper(),
             f"{where}: currency {f.get('currency')!r} is not an ISO code; a probability is a forecast "
             f"for a seat that prices in one currency")
        need(f.get("price_eligible") is False,
             f"{where}: price_eligible must be false -- a derivation is grade {DERIVED_GRADE} and the "
             f"ladder prices only inside pricing_threshold {threshold}; this artefact never prices")
        basis = f.get("basis")
        need(basis in BASES, f"{where}: basis {basis!r} is not one of {BASES}")
        signals = f.get("signals") or []
        belief = f.get("recorded_belief")
        need(belief is not None,
             f"{where}: no recorded_belief -- every forecast keeps the world model's own number "
             f"beside it, the way an override keeps the position it answers, so the disagreement "
             f"is on the record and both are scored (SKILL.md 2)")
        if belief is not None:
            need(isinstance(belief, dict) and bool(belief.get("world_model"))
                 and isinstance(belief.get("probability"), (int, float)),
                 f"{where}: recorded_belief must name a world_model and its probability")

        if basis == "derived":
            need(bool(signals), f"{where}: basis is derived and no signal is named -- a derivation rests on something")
            grades: list[int] = []
            for index, s in enumerate(signals):
                sw = f"{where}.signals[{index}]"
                need(s.get("kind") in SIGNAL_KINDS, f"{sw}: kind {s.get('kind')!r} is not one of {SIGNAL_KINDS}")
                for key in FORBIDDEN_SIGNAL_KEYS:
                    if key in s:
                        if key in ("probability", "implied_probability"):
                            bad.append(f"{sw}: carries {key!r} -- a market level is never a probability "
                                       f"(twin/market_signals.as_probability refuses) and a signal carries none")
                        else:
                            bad.append(f"{sw}: carries {key!r} -- no arithmetic on ordinal grades: a signal "
                                       f"is compared, never weighted or summed")
                need(s.get("evidence_grade") == FEED_GRADE,
                     f"{sw}: a feed observation read with nobody at the keyboard is grade 5, got {s.get('evidence_grade')!r}")
                if isinstance(s.get("evidence_grade"), int):
                    grades.append(int(s["evidence_grade"]))
                need(bool(s.get("statement")), f"{sw}: no statement")
                pin = s.get("from") or {}
                need(bool(pin), f"{sw}: names no envelope (from)")
                if pin:
                    cited.add(pin_key(pin))
                    need(pin_key(pin) in declared, f"{sw}: came from {pin_key(pin)}, which derived_from does not name")
                if feeds_root is not None and pin and s.get("kind") in SIGNAL_KINDS:
                    try:
                        missing = observation_missing(s, Path(feeds_root))
                    except DerivedForecastError as exc:
                        missing = str(exc)
                    need(missing is None, f"{sw}: {missing}")
            # The ordinal ruling, reopened this far and no further: a derivation is no stronger
            # than the weakest thing it rests on. max() over rung numbers is an order statistic
            # -- a comparison the ladder admits -- not a sum or a mean, which it does not.
            weakest = max(grades) if grades else DERIVED_GRADE
            need(f.get("evidence_grade") == weakest == DERIVED_GRADE,
                 f"{where}: evidence_grade {f.get('evidence_grade')!r} -- a derived probability carries the "
                 f"weakest grade among its signals ({weakest}), and a model's derivation is grade "
                 f"{DERIVED_GRADE} (model assertion); the grade is compared, never averaged")
        elif basis == "recorded":
            need(not signals, f"{where}: basis is recorded and signals are named -- a recorded belief rests on "
                              f"no signal; if a signal bore on it, the basis is derived")
            need(belief is not None, f"{where}: basis is recorded and no recorded_belief names the world model it was read from")
            need("evidence_grade" in f and f.get("evidence_grade") is None,
                 f"{where}: evidence_grade {f.get('evidence_grade')!r} on a recorded belief -- the world-model schema "
                 f"carries no grade for a belief and the ladder has no rung for it; the artefact says null, with the reason")
            need(bool(f.get("grade_absent_because")),
                 f"{where}: a recorded belief carries no grade and must say why (grade_absent_because)")
            if belief is not None and isinstance(belief.get("probability"), (int, float)):
                need(_close(belief["probability"], f.get("probability")),
                     f"{where}: a recorded belief is the world model's number unchanged: recorded_belief.probability "
                     f"{belief['probability']!r} != probability {f.get('probability')!r}")

        if adopter_root is not None and org:
            root = Path(adopter_root)
            if not overlay_dir(root, org).is_dir():
                raise CannotLook(f"no overlay at {overlay_dir(root, org)} to check {where} against")
            scenario = _read_yaml(overlay_dir(root, org) / "scenarios" / f"{f.get('scenario')}.yaml")
            need(scenario is not None, f"{where}: scenario {f.get('scenario')!r} is not in the overlay's scenarios/")
            if scenario is not None:
                need(str(scenario.get("proposition")) == str(f.get("proposition")),
                     f"{where}: proposition {f.get('proposition')!r} is not the scenario's ({scenario.get('proposition')!r})")
                need(str(scenario.get("horizon")) == str(f.get("resolves_on")),
                     f"{where}: resolves_on {f.get('resolves_on')!r} is not the scenario's horizon "
                     f"({scenario.get('horizon')!r}); the outcome date is the scenario's, not the forecast's to choose")
                if belief is not None and belief.get("world_model"):
                    need(str(belief["world_model"]) in [str(w) for w in scenario.get("world_models") or []],
                         f"{where}: recorded_belief names world model {belief['world_model']!r}, which the scenario does not list")
            perspective = str(f.get("perspective") or "")
            need((overlay_dir(root, org) / "perspectives" / f"{perspective}.yaml").is_file(),
                 f"{where}: perspective {perspective!r} is not in the overlay's perspectives/")
            declared_currency = currency_of(root, perspective)
            need(declared_currency is not None and declared_currency == currency,
                 f"{where}: currency {currency!r} is not what the perspective prices in ({declared_currency!r}, "
                 f"twin/currency.yaml or party.yaml reporting_currency)")
            if belief is not None and belief.get("world_model"):
                known = world_model_beliefs(root, org, str(belief["world_model"]))
                need(known is not None, f"{where}: world model {belief['world_model']!r} is in neither the overlay nor the vendored world layer")
                if known is not None:
                    have = known.get(str(f.get("proposition")))
                    need(have is not None and _close(have, belief.get("probability")),
                         f"{where}: recorded belief {belief.get('probability')!r} is not what world model "
                         f"{belief['world_model']} carries for {f.get('proposition')!r} ({have!r})")
            elif basis == "recorded":
                pass  # already refused above: a recorded belief names its world model

    for pin in declared - cited:
        bad.append(f"derived_from names {pin}, which no signal cites")
    return bad


def summary(doc: dict[str, Any]) -> str:
    forecasts = doc.get("forecasts") or []
    derived = sum(1 for f in forecasts if f.get("basis") == "derived")
    recorded = len(forecasts) - derived
    signals = sum(len(f.get("signals") or []) for f in forecasts)
    return (f"{len(forecasts)} probabilit{'y' if len(forecasts) == 1 else 'ies'}: {derived} derived "
            f"(grade {DERIVED_GRADE}, resting on {signals} served observation(s)), {recorded} recorded "
            f"(no grade: the world-model schema carries none), every one under a perspective and a "
            f"currency, none price-eligible; {len(doc.get('derived_from') or [])} envelope(s) cited")


# --- git history: pre-registration ------------------------------------------------------------


def _git(repo: Path, *args: str) -> str | None:
    try:
        run = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    return run.stdout if run.returncode == 0 else None


class Arrival(NamedTuple):
    """When a path ARRIVED on the served ref, and when it was last WRITTEN there.

    Both are first-parent committer dates on the served ref. They differ whenever the file was
    rewritten after it landed -- edited in place, deleted and re-added, or squashed in again --
    and that difference is the whole of review F1: measuring pre-registration on the path's
    first add measures the PATH, not the CONTENT, so a number rewritten once the answer was
    already on main still reported `pre-registered: yes` at the original date and was scored
    (measured: re-added 2026-07-20 with `probability: 0.999` against an outcome on main since
    2026-07-01, `brier=1e-06`, PASS).
    """

    added: str
    added_sha: str
    last: str
    last_sha: str

    @property
    def rewritten(self) -> bool:
        return self.added_sha != self.last_sha

    def where(self, ref: str) -> str:
        """The sentence both dates are printed in, so the limit stays a number on every run."""
        text = f"reached {ref} {self.added} in {self.added_sha[:7]}"
        if self.rewritten:
            text += f", last written there {self.last} in {self.last_sha[:7]} (rewritten after it landed)"
        else:
            text += f", never rewritten there since"
        return text


def first_reached(repo: Path, path: str, ref: str = "refs/remotes/origin/main") -> Arrival | None:
    """When `path` arrived on `ref` and when it was last written there, both read off FIRST-PARENT
    history. On the served branch the arrival is the merge commit, dated by whoever performed the
    merge -- for a pull request merged through GitHub, GitHub's clock. None when the path is not
    on the ref.

    Two reads, not one. `--diff-filter=A --reverse | head -1` answers "when did this PATH first
    appear", which is not "when was this CONTENT registered": a rewrite in place, a delete and
    re-add, or a squash-add leaves the first add exactly where it was. `pre_registered()` keys on
    the LAST write, so a forecast rewritten after it landed is a NEW forecast and re-registers on
    the day of the rewrite. A RENAME still costs a forecast its registration -- the new path's
    first add is the rename commit -- which is the honest direction and is kept.
    """
    added = _git(repo, "log", "--first-parent", "--diff-filter=A", "--format=%cI %H", "--reverse", ref, "--", path)
    if not added or not added.strip():
        return None
    add_stamp, add_sha = added.strip().splitlines()[0].split(" ", 1)
    last = _git(repo, "log", "--first-parent", "-1", "--format=%cI %H", ref, "--", path)
    if not last or not last.strip():  # unreachable while the add is readable; never guess
        return None
    last_stamp, last_sha = last.strip().splitlines()[0].split(" ", 1)
    return Arrival(add_stamp, add_sha, last_stamp, last_sha)


def committed_before_its_parent(repo: Path, sha: str) -> bool | None:
    """True when `sha`'s committer date is EARLIER than its own first parent's -- the cheap tell
    that a committer date was chosen rather than taken (review F10).

    The pre-registration date is a committer date. Merged through GitHub it is GitHub's clock; a
    fast-forward push from a laptop carries the laptop's, and `GIT_COMMITTER_DATE` carries
    whatever was typed. This check cannot tell those apart offline -- that limit stands. But a
    commit dated BEFORE the commit it sits on is not a clock disagreement, it is an impossibility,
    and it is free to count. None when there is no parent to compare against.
    """
    here = _git(repo, "log", "-1", "--format=%cI", sha)
    parent = _git(repo, "log", "-1", "--format=%cI", f"{sha}^")
    if not here or not parent or not here.strip() or not parent.strip():
        return None
    return _stamp(here.strip()) < _stamp(parent.strip())


def _stamp(stamp: str) -> dt.datetime:
    parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    return parsed.replace(tzinfo=dt.timezone.utc) if parsed.tzinfo is None else parsed


def _date_of(stamp: str) -> dt.date:
    """The UTC calendar date of an ISO-8601 committer stamp."""
    parsed = dt.datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc).date()


def pre_registered(reached: str, resolves_on: str) -> bool:
    """True only when the forecast was LAST WRITTEN onto the served ref on a UTC date strictly
    before the outcome date. Strictly: a forecast merged on the day the question resolves could
    have seen the answer. Callers pass `Arrival.last`, never `Arrival.added` -- a number rewritten
    after it landed is registered on the day of the rewrite (review F1)."""
    return _date_of(reached) < dt.date.fromisoformat(str(resolves_on))


def signed_feed_tags(feeds_repo: Path) -> tuple[list[str], list[str]]:
    """(every tag naming a pool feed, those of them carrying a signature block).

    `git tag --list` counts NAMES: two unsigned annotated tags satisfied it and the run printed
    "2 signed tag(s)" (review F3, measured). Ticket 84's verify/supersede reads the tag OBJECT
    and requires the armour block, and so does this. A lightweight tag has no object to read --
    `git cat-file tag` refuses it -- and counts as unsigned, which is what it is.
    """
    listed = [t for t in (_git(feeds_repo, "tag", "--list", *(f"{name}/*" for name in POOL_FEEDS)) or "").split() if t]
    signed = []
    for tag in listed:
        body = _git(feeds_repo, "cat-file", "tag", tag)
        if body and "SIGNATURE-----" in body:
            signed.append(tag)
    return listed, signed


def score(forecast: dict[str, Any], outcome: dict[str, Any]) -> dict[str, float]:
    """`twin/scoring.py`'s proper rules on the forecast's probability and the outcome's observed
    truth. Never a second implementation."""
    if str(outcome.get("proposition")) != str(forecast.get("proposition")):
        raise DerivedForecastError(
            f"outcome {outcome.get('id')!r} resolves {outcome.get('proposition')!r}, not the forecast's "
            f"{forecast.get('proposition')!r}"
        )
    return scoring.score(float(forecast["probability"]), bool(outcome["observed"]))


# --- the check ---------------------------------------------------------------------------------


def _served_tree(repo: Path, ref: str, into: Path, paths: tuple[str, ...] = ("twin", "party.yaml")) -> Path | None:
    """Materialise those of `paths` that `ref` carries under `into`, read off the ref's committed
    tree and never the working tree. None when the ref cannot be read or carries none of them."""
    present = [p for p in paths if _git(repo, "cat-file", "-e", f"{ref}:{p}") is not None]
    if not present:
        return None
    try:
        run = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", ref, *present],
                             capture_output=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if run.returncode != 0:
        return None
    into.mkdir(parents=True, exist_ok=True)
    import io
    with tarfile.open(fileobj=io.BytesIO(run.stdout)) as tar:
        tar.extractall(into, filter="data")
    return into


def _ref_age_hours(repo: Path, ref: str, now: dt.datetime) -> float | None:
    """How long since the ref file (or packed-refs, or FETCH_HEAD) was last written: the age of
    what this check calls 'the served branch'."""
    git_dir = _git(repo, "rev-parse", "--git-common-dir")
    if not git_dir:
        return None
    base = Path(git_dir.strip())
    if not base.is_absolute():
        base = repo / base
    stamps = []
    for candidate in (base / ref, base / "packed-refs", base / "FETCH_HEAD"):
        if candidate.is_file():
            stamps.append(candidate.stat().st_mtime)
    if not stamps:
        return None
    newest = dt.datetime.fromtimestamp(max(stamps), tz=dt.timezone.utc)
    return max(0.0, (now - newest).total_seconds() / 3600)


def adopters_in(estate: Path) -> list[str]:
    """Units whose served ref carries a twin overlay named after them."""
    out = []
    for unit in sorted(p for p in Path(estate).iterdir() if (p / ".git").exists()):
        if _git(unit, "cat-file", "-e", f"refs/remotes/origin/main:twin/orgs/{unit.name}/meta.yaml") is not None:
            out.append(unit.name)
    return out


def check(estate: str, hub: str, adopters: list[str] | None = None, now: str | None = None,
          ref: str = "refs/remotes/origin/main") -> int:
    """Grade the SERVED artefact: every `twin/forecasts/*.forecast.yaml` on origin/main of every
    adopter, validated against the served overlay and the served feeds, its arrival read off
    first-parent history, paired with the overlay's own outcome, and scored here. Prints one line
    per fact and one verdict last. 0 true, 1 false, 3 could not look."""
    estate_path, hub_path = Path(estate), Path(hub)
    moment = dt.datetime.fromisoformat(now.replace("Z", "+00:00")) if now else dt.datetime.now(dt.timezone.utc)
    register = yaml.safe_load((hub_path / "twin" / "roles.yaml").read_text(encoding="utf-8"))
    roles = {str(r["id"]) for r in register["roles"]}
    feeds_repo = estate_path / "feeds"
    if not (feeds_repo / ".git").exists():
        print(f"SKIP: no feeds checkout at {feeds_repo} (run clone-estate.sh): the observations a derivation cites cannot be confirmed")
        return 3
    names = adopters if adopters is not None else adopters_in(estate_path)
    if not names:
        print(f"SKIP: no unit under {estate_path} carries a twin overlay on {ref}; there is no adopter to read a forecast from")
        return 3

    fails: list[str] = []
    waits: list[str] = []
    scored = 0
    derived_total = recorded_total = late_total = 0
    earliest_pending: str | None = None
    pinned = 0
    # Review F9: every signal's grade is FORCED to 5 by validate() before `weakest = max(grades)`,
    # so the reopened ordinal comparison is a TAUTOLOGY today -- it is built for the day a signal
    # at another rung exists, and until then the run says how many distinct grades it saw.
    # Review F10: how many registering commits are dated before their own first parent.
    grades_seen: set[int] = set()
    impossible_dates: set[str] = set()
    with tempfile.TemporaryDirectory() as tmp:
        feeds_tree = _served_tree(feeds_repo, ref, Path(tmp) / "feeds", POOL_FEEDS + ("party.yaml",))
        if feeds_tree is None:
            print(f"SKIP: could not read {ref} of {feeds_repo}: the served pool cannot be confirmed")
            return 3
        feeds_root = feeds_tree
        feed_tags, signed_tags = signed_feed_tags(feeds_repo)
        for adopter in names:
            repo = estate_path / adopter
            tree = _served_tree(repo, ref, Path(tmp) / adopter)
            if tree is None:
                print(f"    {adopter}: could not read {ref} (no checkout, or no origin/main fetched)")
                waits.append(f"could not read {ref} of {adopter}")
                continue
            age = _ref_age_hours(repo, ref, moment)
            age_text = f"{age:.0f}h ago" if age is not None else "unknown"
            if pinned_pool_feeds(tree).get("market-moves") or pinned_pool_feeds(tree).get("news"):
                pinned += 1
            files = sorted(str(p.relative_to(tree)) for p in (tree / "twin" / "forecasts").glob(f"*{SUFFIX}")) \
                if (tree / "twin" / "forecasts").is_dir() else []
            outcomes = []
            for path in sorted((tree / "twin" / "orgs" / adopter / "outcomes").glob("*.yaml")) \
                    if (tree / "twin" / "orgs" / adopter / "outcomes").is_dir() else []:
                try:
                    doc = _read_yaml(path) or {}
                except DerivedForecastError as exc:
                    fails.append(f"{adopter}: outcome {path.name}: {exc}")
                    continue
                try:
                    schema.validate("outcome", doc, f"{adopter}:{path.name}")
                except schema.SchemaError as exc:
                    fails.append(f"{adopter}: outcome {path.name} is not a twin outcome: {exc}")
                    continue
                rel = str(path.relative_to(tree))
                reached = first_reached(repo, rel, ref)
                if reached is None:
                    fails.append(f"{adopter}: outcome {rel} is on the tree but not in {ref}'s first-parent history")
                    continue
                # The answer key is immutable once it is on the served ref. An outcome edited
                # afterwards silently rescores every forecast it resolves while the run goes on
                # printing the ORIGINAL date (review F2, measured: `observed: true` -> `false`
                # committed 2026-07-25 moved brier 0.5329 -> 0.0729, both PASS). A correction is
                # a new record, and it arrives with its own date where anyone can see it.
                if reached.rewritten:
                    fails.append(f"{adopter}: outcome {doc['id']} reached {ref} on {_date_of(reached.added)} in "
                                 f"{reached.added_sha[:7]} and was rewritten there on {_date_of(reached.last)} in "
                                 f"{reached.last_sha[:7]} -- an answer key edited after it landed rescores every "
                                 f"forecast it resolves, and nothing on the record would say so")
                    continue
                if _date_of(reached.added) < dt.date.fromisoformat(str(doc["resolved_on"])):
                    fails.append(f"{adopter}: outcome {doc['id']} reached {ref} on {_date_of(reached.added)}, before the "
                                 f"date it says it resolved ({doc['resolved_on']}) -- an answer recorded before the question closed")
                    continue
                outcomes.append((doc, reached))
            # Two answer keys for one question: `matching[0]` silently took whichever sorted
            # first and the run PASSed with no word that they disagree (review F2, measured).
            by_proposition: dict[str, list[str]] = {}
            for doc, _ in outcomes:
                by_proposition.setdefault(str(doc.get("proposition")), []).append(str(doc.get("id")))
            for proposition, ids in sorted(by_proposition.items()):
                if len(ids) > 1:
                    fails.append(f"{adopter}: {len(ids)} outcomes resolve {proposition!r} ({', '.join(sorted(ids))}) "
                                 f"-- two answer keys for one question; the check will not pick one, and a forecast "
                                 f"on that proposition is not scored until one of them is withdrawn")
            print(f"    {adopter}: {len(files)} *{SUFFIX} on {ref} (ref last updated {age_text}); "
                  f"{len(outcomes)} outcome(s) in twin/orgs/{adopter}/outcomes")
            for rel in files:
                try:
                    fdoc = _read_yaml(tree / rel)
                except DerivedForecastError as exc:
                    fails.append(f"{adopter}: {rel}: {exc}")
                    continue
                if fdoc is None:
                    fails.append(f"{adopter}: {rel} is not a YAML mapping")
                    continue
                try:
                    bad = validate(fdoc, roles, headless=bool((fdoc.get("run") or {}).get("headless")),
                                   adopter_root=tree, feeds_root=feeds_root)
                except CannotLook as exc:
                    waits.append(f"{adopter}: {rel}: could not look: {exc}")
                    continue
                except DerivedForecastError as exc:
                    fails.append(f"{adopter}: {rel}: {exc}")
                    continue
                if bad:
                    for reason in bad:
                        print(f"    not ok  {adopter}: {rel}: {reason}")
                    fails.append(f"{adopter}: {rel} is not a forecast file the twin can read ({len(bad)} reason(s))")
                    continue
                reached = first_reached(repo, rel, ref)
                if reached is None:
                    fails.append(f"{adopter}: {rel} is on the tree but not in {ref}'s first-parent history")
                    continue
                for f in fdoc["forecasts"]:
                    basis = f["basis"]
                    if basis == "derived":
                        derived_total += 1
                    else:
                        recorded_total += 1
                    matching = [o for o in outcomes if str(o[0].get("proposition")) == str(f["proposition"])]
                    if len(matching) > 1:
                        # already failed above, by proposition. Say so on the forecast's own line
                        # rather than dropping it out of the listing: a forecast that vanishes
                        # from the record is a gap a reader has to notice.
                        print(f"    forecast {f['id']}: p={f['probability']} basis={basis} -- not read: "
                              f"{len(matching)} outcomes resolve {f['proposition']!r} and the check picks neither")
                        continue
                    closes = str(f["resolves_on"])
                    if matching:
                        closes = min(closes, str(matching[0][0]["resolved_on"]))
                    # The LAST write onto the served ref, not the first add. Both are printed.
                    pre = pre_registered(reached.last, closes)
                    for s_grade in (s.get("evidence_grade") for s in f.get("signals") or []):
                        if isinstance(s_grade, int):
                            grades_seen.add(s_grade)
                    # by COMMIT, not by forecast: one file can carry several probabilities
                    if committed_before_its_parent(repo, reached.last_sha):
                        impossible_dates.add(reached.last_sha)
                    signals = ", ".join(
                        f"{s['kind']} {s.get('market') or s.get('event')} ({s['from']['name']}@{s['from']['version']})"
                        for s in f.get("signals") or []) or "none (recorded belief)"
                    grade = f"grade {f['evidence_grade']}" if f.get("evidence_grade") is not None \
                        else "carries no grade (the world-model schema carries none for a recorded belief)"
                    print(f"    forecast {f['id']}: p={f['probability']} basis={basis} {grade} perspective={f['perspective']} "
                          f"currency={f['currency']} signals: {signals}; {reached.where(ref)}, "
                          f"outcome date {closes}: pre-registered: {'yes' if pre else 'no'} "
                          f"(registered {_date_of(reached.last)}, added {_date_of(reached.added)})")
                    if not pre:
                        late_total += 1
                        rewrite = (f" (added {_date_of(reached.added)} and rewritten there in {reached.last_sha[:7]}: "
                                   f"a number rewritten after it landed is registered on the day of the rewrite)"
                                   if reached.rewritten else "")
                        fails.append(f"{adopter}: forecast {f['id']} was last written onto {ref} on "
                                     f"{_date_of(reached.last)}{rewrite}, not before its outcome date {closes}: "
                                     f"not pre-registered, not scored")
                        continue
                    if dt.date.fromisoformat(str(f["resolves_on"])) > moment.date() and not matching:
                        if earliest_pending is None or str(f["resolves_on"]) < earliest_pending:
                            earliest_pending = str(f["resolves_on"])
                        continue
                    if not matching:
                        waits.append(f"{adopter}: forecast {f['id']} passed its outcome date {f['resolves_on']} and no "
                                     f"outcome in twin/orgs/{adopter}/outcomes resolves {f['proposition']!r} yet")
                        continue
                    outcome, o_reached = matching[0]
                    if _date_of(o_reached.added) <= _date_of(reached.last):
                        fails.append(f"{adopter}: outcome {outcome['id']} reached {ref} ({o_reached.added}) no later than "
                                     f"forecast {f['id']} was last written there ({reached.last}): the answer was on main "
                                     f"before the forecast")
                        continue
                    result = score(f, outcome)
                    scored += 1 if basis == "derived" else 0
                    print(f"    scored   {f['id']} against outcome {outcome['id']} (observed={outcome['observed']}, "
                          f"reached {o_reached.added}, never rewritten there): " + " ".join(f"{k}={v}" for k, v in result.items())
                          + f" (lower is better; computed now, {moment.date()}, by twin/scoring.py; {basis})")
        print(f"    note: {pinned} of {len(names)} adopter(s) pin news or market-moves in party.yaml inherits[]; "
              f"the feeds publisher has {len(feed_tags)} tag(s) naming either, {len(signed_tags)} of them carrying a "
              f"signature block (read with `git cat-file tag`, ticket 84's rule; a lightweight tag has no object to "
              f"read and counts as unsigned) -- the pool is served unpinned and untagged, so nothing derived from it "
              f"is price-eligible (ticket 23)")
    print(f"    totals: {derived_total} derived, {recorded_total} recorded (carrying no grade), {late_total} late, "
          f"{scored} derived and scored")
    tautology = ("" if len(grades_seen) > 1 else
                 " -- until that is more than one, 'no stronger than its weakest signal' is a "
                 "comparison with nothing to compare, and it is built for the day a signal at "
                 "another rung exists")
    print(f"    limits: {len(grades_seen)} distinct evidence grade(s) across every signal read "
          f"({', '.join(str(g) for g in sorted(grades_seen)) or 'no signal read'}){tautology}; "
          f"{len(impossible_dates)} registering commit(s) dated before their own first parent. A "
          f"committer date merged through GitHub is GitHub's; a fast-forward push from a laptop "
          f"carries the laptop's, and this check cannot tell those two apart offline")
    if fails:
        for line in fails:
            print(f"    FAIL: {line}")
        print(f"FAIL: {len(fails)} derived-forecast fact(s) observed false on {ref} of {', '.join(names)}")
        return 1
    if scored:
        print(f"PASS: {scored} derived, pre-registered probabilit{'y' if scored == 1 else 'ies'} scored by twin/scoring.py "
              f"against the overlay's own outcome, each resting on an observation the served feed carries, "
              f"pre-registration read off {ref}'s first-parent history ({derived_total} derived, {recorded_total} recorded)")
        return 0
    if waits:
        print(f"SKIP: {waits[0]}" + (f" (+{len(waits) - 1} more)" if len(waits) > 1 else ""))
        return 3
    if derived_total == 0 and recorded_total == 0:
        print(f"SKIP: no *{SUFFIX} has reached {ref} of any adopter ({', '.join(names)}): the derive step of "
              f"talk/local-clock.sh has not run and been merged")
        return 3
    if derived_total == 0:
        print(f"SKIP: {recorded_total} recorded belief(s) and 0 derived on {ref}: no served observation bore on any scenario yet")
        return 3
    print(f"SKIP: {derived_total} derived probabilit{'y' if derived_total == 1 else 'ies'} pre-registered on {ref}; "
          f"none has passed its outcome date (earliest {earliest_pending}) -- the score waits on the date")
    return 3


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    i = sub.add_parser("inputs", help="the deterministic listing the model derives from")
    i.add_argument("--adopter", required=True, help="the adopter checkout (the clock's worktree)")
    i.add_argument("--org", required=True)
    i.add_argument("--feeds", required=True, help="the feeds publisher's checkout")
    c = sub.add_parser("check", help="grade the served forecasts of every adopter")
    c.add_argument("--estate", required=True)
    c.add_argument("--hub", required=True)
    c.add_argument("--adopter", action="append", default=None)
    c.add_argument("--now", default=None)
    args = parser.parse_args(argv)
    if args.cmd == "inputs":
        print(yaml.safe_dump(inputs(Path(args.adopter), args.org, Path(args.feeds)), sort_keys=False, width=100))
        return 0
    return check(args.estate, args.hub, adopters=args.adopter, now=args.now)


if __name__ == "__main__":
    sys.exit(main())
