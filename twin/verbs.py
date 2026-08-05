"""The three verbs of the walking skeleton: sense, run, score.

One dated signal binds to a component; one scenario executes and emits forecasts; a forecast is
scored against a recorded outcome. The loop closes before anything is deepened, because scoring
dictates what every other component must record (spec: "Scoring, first").

Everything here is stub depth. What is unchecked is visible in each artefact's `depth` block
rather than described in prose somewhere nobody reads.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from . import TOOL_VERSION
from .artefact import Artefact, DERIVED, load as load_artefact
from .blob import BlobRef
from .canon import digest_of, sha256_hex
from .grades import Capabilities
from .model import ModelError, Overlay
from .repo import ModelRepo

CAPS_SENSE = ["domain-model", "provenance", "sense-move"]
CAPS_RUN = ["domain-model", "provenance", "scenario-engine"]
CAPS_SCORE = ["domain-model", "provenance", "sense-move"]

KIND_BOUND_SIGNAL = "bound-signal"
KIND_FORECAST_BUNDLE = "forecast-bundle"
KIND_SCORE_CARD = "score-card"


class VerbError(RuntimeError):
    pass


def command_for(verb: str, **parts: str | None) -> list[str]:
    """The command as recorded in an artefact.

    Deliberately not `sys.argv`: the repository path and the output path are where the work
    happened, not inputs to the derivation, and a machine path in the envelope would break
    `identical_pins_identical_bytes` across machines. A forecast being scored is named by its
    digest here for the same reason — by pin, never by path.
    """
    out = ["twin", verb]
    for key, value in sorted(parts.items()):
        if value is not None:
            out += [f"--{key.replace('_', '-')}", str(value)]
    return out


def _pins(repo: ModelRepo, overlay: Overlay, caps: Capabilities, substrate: str | None) -> dict[str, Any]:
    """Model repo ref, world ref, overlay ref, and the tool's own version.

    The tool is a pin too: identical bytes is only a meaningful claim pin-for-pin, and a change
    to the depth-grade checklists changes what an artefact says about itself.
    """
    return {
        "model_repo": repo.pin.as_dict(),
        "overlay": overlay.ref.as_dict(),
        "world": overlay.world.ref.as_dict(),
        "org": overlay.org,
        "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
        # Bulk substrate is addressed by content hash rather than held inline. Null until the
        # substrate track lands; the reference form round-trips through here regardless.
        "substrate": substrate,
    }


def _substrate_ref(doc: dict[str, Any], where: str) -> str | None:
    raw = doc.get("substrate")
    if raw is None:
        return None
    try:
        return str(BlobRef.parse(str(raw)))  # parse then re-serialise: the round-trip
    except ValueError as exc:
        raise VerbError(f"{where}: {exc}") from exc


# -- sense ---------------------------------------------------------------------------------


STEEP = ("social", "technological", "economic", "environmental", "political")
ISO_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def validate_signal(signal_id: str, signal: dict[str, Any]) -> None:
    """A signal is dated, STEEP-classed and provenanced, or it is not a signal.

    Enforced rather than conventional: without this the schema is whatever the last author
    happened to type, and "a dated signal binds to a component" would be a description of the
    fixture rather than a property of the system.
    """
    date = str(signal.get("date", ""))
    if not ISO_DATE.match(date):
        raise VerbError(f"signal {signal_id!r} needs a `date` of the form YYYY-MM-DD, got {date!r}")
    steep = str(signal.get("steep", "")).lower()
    if steep not in STEEP:
        raise VerbError(f"signal {signal_id!r} needs a `steep` class from {STEEP}, got {steep!r}")
    if not str(signal.get("statement", "")).strip():
        raise VerbError(f"signal {signal_id!r} needs a `statement` — what was observed")
    if not str(signal.get("source", "")).strip():
        raise VerbError(f"signal {signal_id!r} needs a `source` — where it was observed")
    provenance = signal.get("provenance")
    if not isinstance(provenance, dict) or not provenance:
        raise VerbError(f"signal {signal_id!r} needs a non-empty `provenance` mapping")


def sense(repo: ModelRepo, caps: Capabilities, org: str, signal_id: str, command: list[str]) -> Artefact:
    overlay = Overlay.load(repo, org)
    signal = overlay.signals.get(signal_id)
    if signal is None:
        known = ", ".join(sorted(overlay.signals)) or "none"
        raise VerbError(f"no signal {signal_id!r} in overlay {org!r} (have: {known})")
    validate_signal(signal_id, signal)

    bindings = []
    for claim_id, claim in sorted(overlay.claims.items()):
        if claim.get("kind") != "binding" or claim.get("signal") != signal_id:
            continue
        grade = int(claim.get("evidence_grade", 0))
        if grade != 5:
            # Skills sit upstream of this seam: their output is a committed grade-5 claim file,
            # and from the CLI's point of view it is just input.
            raise VerbError(
                f"claim {claim_id!r} binds a signal at evidence grade {grade}; hand-authored "
                "binding claims are grade 5 by construction"
            )
        component_id = str(claim.get("component", ""))
        component = overlay.component(component_id)
        bindings.append(
            {
                "claim": claim_id,
                "component": component_id,
                "component_layer": "overlay" if component_id in overlay.components else "world",
                "evidence_grade": grade,
                "claimed_by": claim.get("claimed_by"),
                "evidence": claim.get("evidence"),
                "confidence": claim.get("confidence"),
            }
        )
    if not bindings:
        raise VerbError(f"signal {signal_id!r} has no binding claim; an unbound signal does not sense")

    return Artefact(
        kind=KIND_BOUND_SIGNAL,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, _substrate_ref(signal, f"signal {signal_id}")),
        depth=caps.depth_block(CAPS_SENSE),
        body={"signal": signal, "bindings": bindings},
    )


# -- run -----------------------------------------------------------------------------------


def run(
    repo: ModelRepo, caps: Capabilities, org: str, scenario_id: str, command: list[str], at: str | None = None
) -> Artefact:
    overlay = Overlay.load(repo, org)
    scenario = overlay.scenarios.get(scenario_id)
    if scenario is None:
        known = ", ".join(sorted(overlay.scenarios)) or "none"
        raise VerbError(f"no scenario {scenario_id!r} in overlay {org!r} (have: {known})")

    when = at or scenario.get("at")
    if not when:
        raise VerbError(f"scenario {scenario_id!r} declares no `at`; an execution happens at a declared time")

    proposition_id = str(scenario.get("proposition", ""))
    proposition = overlay.proposition(proposition_id)

    components = [str(c) for c in scenario.get("components", []) or []]
    if not components:
        raise VerbError(f"scenario {scenario_id!r} references no components")
    for component_id in components:
        overlay.component(component_id)

    model_ids = [str(m) for m in scenario.get("world_models", []) or []]
    if not model_ids:
        raise VerbError(f"scenario {scenario_id!r} names no world models; a forecast is always relative to one")

    pins = _pins(repo, overlay, caps, _substrate_ref(scenario, f"scenario {scenario_id}"))
    # A forecast travels on its own, so it carries the whole pin — including the command that
    # produced it, not just the refs it read (build ticket 06).
    forecast_pins = {**pins, "command": list(command)}

    # Forecasts, plural, always. There is no code path anywhere that collapses this list, and
    # there never will be: the ability to collapse would be used.
    forecasts: list[dict[str, Any]] = []
    for model_id in model_ids:
        world_model = overlay.world_model(model_id)
        beliefs = world_model.get("beliefs", {}) or {}
        if proposition_id not in beliefs:
            raise VerbError(
                f"world model {model_id!r} holds no belief about {proposition_id!r}; it cannot "
                "forecast a proposition it has not considered"
            )
        forecast = {
            "scenario": scenario_id,
            "world_model": model_id,
            "world_model_credence": world_model.get("credence"),
            "world_model_layer": "overlay" if model_id in overlay.world_models else "world",
            "proposition": proposition_id,
            "proposition_text": proposition.get("text"),
            "probability": float(beliefs[proposition_id]),
            "at": when,
            "horizon": scenario.get("horizon"),
            "components": components,
            "pins": forecast_pins,
        }
        forecast["id"] = digest_of(forecast)[:16]
        forecasts.append(forecast)

    return Artefact(
        kind=KIND_FORECAST_BUNDLE,
        mark=DERIVED,
        command=command,
        pins=pins,
        depth=caps.depth_block(CAPS_RUN),
        body={
            "scenario": {
                "id": scenario_id,
                "at": when,
                "components": components,
                "world_models": model_ids,
                "proposition": proposition_id,
                "horizon": scenario.get("horizon"),
                "question": scenario.get("question"),
            },
            "forecasts": forecasts,
        },
    )


# -- score ---------------------------------------------------------------------------------


def score(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    forecast_path: str | Path,
    outcome_id: str,
    command: list[str],
) -> Artefact:
    overlay = Overlay.load(repo, org)
    outcome = overlay.outcomes.get(outcome_id)
    if outcome is None:
        known = ", ".join(sorted(overlay.outcomes)) or "none"
        raise VerbError(f"no outcome {outcome_id!r} in overlay {org!r} (have: {known})")

    bundle_bytes = Path(forecast_path).read_bytes()
    bundle = load_artefact(forecast_path)
    if bundle["envelope"]["kind"] != KIND_FORECAST_BUNDLE:
        raise VerbError(f"{forecast_path} is a {bundle['envelope']['kind']!r}, not a forecast bundle")

    observed = outcome.get("observed")
    if not isinstance(observed, bool):
        raise VerbError(f"outcome {outcome_id!r} must record `observed: true|false`")
    proposition_id = str(outcome.get("proposition", ""))
    overlay.proposition(proposition_id)

    scores = []
    for forecast in bundle["body"]["forecasts"]:
        if forecast.get("proposition") != proposition_id:
            continue
        probability = float(forecast["probability"])
        scores.append(
            {
                # By pin, not by path: the forecast is named by what it is, not by where it sat.
                "forecast_id": forecast["id"],
                "world_model": forecast["world_model"],
                "probability": probability,
                "observed": observed,
                "brier": (probability - (1.0 if observed else 0.0)) ** 2,
                "pins": forecast["pins"],
            }
        )
    if not scores:
        raise VerbError(
            f"no forecast in {forecast_path} addresses proposition {proposition_id!r}; nothing to score"
        )

    return Artefact(
        kind=KIND_SCORE_CARD,
        mark=DERIVED,
        command=command,
        pins=_pins(repo, overlay, caps, None),
        depth=caps.depth_block(CAPS_SCORE),
        body={
            "subject": {
                "kind": KIND_FORECAST_BUNDLE,
                "sha256": sha256_hex(bundle_bytes),
                "produced_by": bundle["envelope"]["produced_by"],
                "pins": bundle["envelope"]["pins"],
            },
            "outcome": {
                "id": outcome_id,
                "proposition": proposition_id,
                "observed": observed,
                "resolved_on": outcome.get("resolved_on"),
                "source": outcome.get("source"),
            },
            "rule": "brier",
            "scores": scores,
        },
    )


def resolve_org(repo: ModelRepo, org: str | None) -> str:
    from .model import orgs as list_orgs

    available = list_orgs(repo)
    if org:
        if org not in available:
            raise ModelError(f"no overlay for org {org!r} (have: {', '.join(available) or 'none'})")
        return org
    if len(available) == 1:
        return available[0]
    raise ModelError(f"--org is required; this repository has overlays for: {', '.join(available) or 'none'}")
