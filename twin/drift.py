"""Flux drift measurement: the reduction, and the coverage that says what it is worth.

Build ticket 64, from spec story 85. **Instrument and wait.** Started near the front of the build
because it needs elapsed calendar time and nothing from the twin: the falsification verdict
(build ticket 65) cannot be honest without a measurement window, and starting the clock at the
verdict's natural dependency position would delay the answer by that window on top of everything
else.

The question, stated in `estate/driftwood/drift/window.yaml` before any sample existed: does the
state of a deployed control diverge from its declared state **between deploys**? If it does not,
a deploy-time attestation suffices and continuous reconciliation is a convenience rather than an
enabler — and the spec is amended.

**This module reduces; it does not conclude.** A drift event is a transition between two samples,
so no single sample can be one, and what the transitions *mean* is build ticket 65. `verdict` is
`None` here, with the reason, rather than absent.

## What a drift event is, and what it deliberately is not

A subject whose observed value changed between two consecutive samples **with no deploy between
them**. The Flux Kustomization's `lastAppliedRevision` is the deploy marker: a divergence that
follows a revision change is a deploy, and a deploy-time attestation would have caught it. Only
divergence *without* a deploy discriminates between the two designs, which is why the definition
was written down before the data arrived.

The "desired" state is the previous sample's observed value rather than a re-read of the git
tree. That is the same comparison stated in the window and it is the honest one: what matters is
whether the cluster moved on its own, and re-deriving desired state from a repository at report
time would compare today's git against yesterday's cluster.

## Coverage is not a footnote

An instrument whose silence reads as stability is worse than no instrument. So a probe that
cannot reach the cluster still writes a sample, and this module reports what fraction of the
declared window was actually observed, plus every gap wider than the declared cadence. "No drift
in 91 days" and "no drift in the eleven hours we were looking" are different claims, and only one
of them is falsifiable.
"""

from __future__ import annotations

import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from . import REPO_DIR

# mo-12 deleted the hub's committed estate/ tree; driftwood is a real repo now (mo-08), and
# clone-estate.sh fetches it into .estate-clone/ (git-ignored, disposable). Same repoint already
# applied to verify/party/party.py, verify/proportionality/render.py, verify/provenance/provenance.py.
_DRIFTWOOD = REPO_DIR / ".estate-clone" / "driftwood" / "drift"
WINDOW_PATH = _DRIFTWOOD / "window.yaml"
SAMPLES_PATH = _DRIFTWOOD / "samples.jsonl"
PRECONDITIONS_PATH = _DRIFTWOOD / "preconditions.yaml"
FORCED_CAMPAIGN_PATH = _DRIFTWOOD / "forced-campaign.yaml"

WINDOW_SCHEMA = "drift.window/v1"
FORCED_CAMPAIGN_SCHEMA = "drift.forced_campaign/v1"

# The fixed, named action set build ticket 78 requires — not an improvising agent choosing
# freely, which would itself carry model-prior bias about what "realistic" tampering looks like.
REQUIRED_FORCED_TRIALS = (
    "configmap-edit-outside-gitops",
    "scale-left-unreverted",
    "kustomization-suspended-left-suspended",
    "resource-deleted-outright",
)

# The value `forced-campaign.yaml`'s `configmap-edit-outside-gitops` trial writes
# (`forced-campaign.sh`'s first `run_trial` call) — never a value any declared subject legitimately
# holds. A timestamp-set intersection between the two logs misses a *misrouted* write (a broken
# `DRIFT_SAMPLES` override landing a forced sample in build ticket 64's own organic log rather than
# the campaign's), because a sample that never reached the forced log has no timestamp to
# intersect against. This marker is the second, independent check: it is unmistakably contamination
# wherever it turns up, regardless of which file the sample landed in.
FORCED_DRIFT_MARKER = "FORCED-DRIFT-TEST"

# The verdict is build ticket 65's, and naming it here rather than leaving the field absent is the
# same move as `model_residual.computed: false` in the regime gap — an absent conclusion reads as
# an oversight, a refused one reads as a boundary.
VERDICT_TICKET = "build ticket 65"


class DriftError(RuntimeError):
    """The window does not say what it must, or a sample is not a sample."""


def _moment(stamp: str) -> datetime.datetime:
    text = str(stamp).strip().replace("Z", "+00:00")
    try:
        parsed = datetime.datetime.fromisoformat(text)
    except ValueError:
        raise DriftError(f"{stamp!r} is not an ISO 8601 instant") from None
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=datetime.timezone.utc)


def _day(stamp: str) -> datetime.datetime:
    return _moment(f"{stamp}T00:00:00+00:00")


@dataclass(frozen=True)
class Window:
    """The pre-registration. Loaded rather than trusted, for the reason the ladder is."""

    question: str
    opens: str
    closes: str
    cadence_minutes: int
    tolerance_minutes: int
    subjects: tuple[str, ...]
    falsifiers: tuple[str, ...]
    owner: str
    # The addendum's own words, carried on the object rather than left in the file, because build
    # ticket 65's verdict has to cite what this instrument could not see and a citation that means
    # re-opening the yaml is one an artefact quietly stops making. Empty when the window declares
    # no scope limit, and `verdict.decide` refuses to conclude on such a window rather than
    # inventing a limitation for it.
    does_not_measure: str = ""
    scope_consequence: str = ""

    @classmethod
    def load(cls, path: Path | None = None) -> "Window":
        source = path or WINDOW_PATH
        doc = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or doc.get("schema") != WINDOW_SCHEMA:
            raise DriftError(f"{source}: not a {WINDOW_SCHEMA} document")
        window, cadence = doc.get("window") or {}, doc.get("cadence") or {}
        subjects = tuple(str(s["id"]) for s in (doc.get("subjects") or []))
        if not subjects:
            raise DriftError(f"{source}: declares no subject, so it measures nothing")
        falsifiers = tuple(str(f) for f in (doc.get("outcomes_that_would_falsify_the_spec") or []))
        if not falsifiers:
            raise DriftError(
                f"{source}: names no outcome that would falsify the spec. A measurement that can "
                "only come back one way is a demonstration, and this one exists to be a test."
            )
        opens, closes = str(window.get("opens", "")), str(window.get("closes", ""))
        if not opens or not closes or _day(closes) <= _day(opens):
            raise DriftError(f"{source}: the window must declare `opens` before `closes`")
        owner = str((doc.get("operation") or {}).get("owner", "")).strip()
        if not owner:
            raise DriftError(
                f"{source}: names no operator. A probe nobody owns stops running and nobody notices, "
                "and a stopped probe is what produces a confident 'no drift'."
            )
        every = int(cadence.get("every_minutes", 0))
        if every <= 0:
            # Refused at load rather than defended against in every reader (build ticket 70). A
            # window declaring no cadence has no expected sample count, so coverage is undefined
            # and every downstream figure divides by it. `coverage`'s own `if window.cadence_minutes`
            # guard predates this and is now unreachable; it is left where it is rather than
            # removed, because deleting a guard is how one comes back.
            raise DriftError(
                f"{source}: declares a cadence of {every} minutes. Without one there is no expected "
                "sample count, so no coverage figure and no floor to reach."
            )
        scope = doc.get("scope_limit") or {}
        return cls(
            question=str(doc.get("question", "")).strip(),
            opens=opens,
            closes=closes,
            cadence_minutes=every,
            tolerance_minutes=int(cadence.get("tolerance_minutes", 0)),
            subjects=subjects,
            falsifiers=falsifiers,
            owner=owner,
            does_not_measure=str(scope.get("does_not_measure", "")).strip(),
            scope_consequence=str(scope.get("consequence_for_the_verdict", "")).strip(),
        )


@dataclass(frozen=True)
class ForcedCampaign:
    """The forced-drift latency campaign's pre-registration (build ticket 78).

    A companion instrument to `Window`, not a replacement for it. `Window` waits on organic
    behaviour to answer a base-rate question; this forces four named, scripted, reversible
    actions against the same real cluster and answers a *mechanism* question instead — when a
    plausible change happens, do Flux and the probe catch it, and how fast? Loaded rather than
    trusted, for the same reason `Window.load` is: a file that can declare anything is not a
    declaration until something refuses the ones that don't hold their own guardrails.
    """

    question: str
    not_organic_drift_evidence: str
    trials: tuple[str, ...]
    sample_every_seconds: int
    window_minutes: int
    samples_path: Path
    owner: str

    @classmethod
    def load(cls, path: Path | None = None) -> "ForcedCampaign":
        source = path or FORCED_CAMPAIGN_PATH
        doc = yaml.safe_load(source.read_text(encoding="utf-8"))
        if not isinstance(doc, dict) or doc.get("schema") != FORCED_CAMPAIGN_SCHEMA:
            raise DriftError(f"{source}: not a {FORCED_CAMPAIGN_SCHEMA} document")

        trial_docs = doc.get("trials") or []
        ids = tuple(str(t.get("id", "")) for t in trial_docs)
        if set(ids) != set(REQUIRED_FORCED_TRIALS) or len(ids) != len(REQUIRED_FORCED_TRIALS):
            raise DriftError(
                f"{source}: declares {sorted(ids)}, not exactly the four trials build ticket 78 "
                f"names: {sorted(REQUIRED_FORCED_TRIALS)}"
            )
        for trial in trial_docs:
            if not str(trial.get("action", "")).strip():
                raise DriftError(f"{source}: trial {trial.get('id')!r} names no action")
            if not str(trial.get("undo", "")).strip():
                raise DriftError(
                    f"{source}: trial {trial.get('id')!r} names no undo step — every action needs "
                    "a companion, pre-recorded undo (build ticket 78)"
                )

        resolution = doc.get("resolution") or {}
        sample_every_seconds = int(resolution.get("sample_every_seconds", 0))
        window_minutes = int(resolution.get("window_minutes", 0))
        if sample_every_seconds <= 0 or window_minutes <= 0:
            raise DriftError(
                f"{source}: `resolution` must declare a positive sample_every_seconds and "
                "window_minutes"
            )

        samples = str((doc.get("samples") or {}).get("path", "")).strip()
        if not samples:
            raise DriftError(f"{source}: names no samples path")
        samples_path = (source.parent / samples).resolve()
        if samples_path.name == SAMPLES_PATH.name:
            raise DriftError(
                f"{source}: samples path must not be build ticket 64's organic log "
                f"({SAMPLES_PATH}) — forcing the very thing the organic measurement counts would "
                "contaminate it"
            )

        not_organic = str(doc.get("not_organic_drift_evidence", "")).strip()
        if "65" not in not_organic:
            raise DriftError(
                f"{source}: `not_organic_drift_evidence` must state explicitly, citing build "
                "ticket 65, that this campaign is not evidence for the organic-drift verdict"
            )

        owner = str((doc.get("operation") or {}).get("owner", "")).strip()
        if not owner:
            raise DriftError(f"{source}: names no operator")

        return cls(
            question=str(doc.get("question", "")).strip(),
            not_organic_drift_evidence=not_organic,
            trials=ids,
            sample_every_seconds=sample_every_seconds,
            window_minutes=window_minutes,
            samples_path=samples_path,
            owner=owner,
        )


def load_samples(path: Path | None = None) -> list[dict[str, Any]]:
    """Every probe sample, oldest first. A missing log is empty, never an error.

    The window opens before the first sample by construction, so "no samples yet" is the ordinary
    state at the start of a measurement rather than a fault.
    """
    source = path or SAMPLES_PATH
    if not source.is_file():
        return []
    samples = []
    for number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            doc = json.loads(line)
        except json.JSONDecodeError:
            raise DriftError(f"{source}:{number}: not a JSON object") from None
        if "ts" not in doc or "reachable" not in doc:
            raise DriftError(f"{source}:{number}: a sample declares `ts` and `reachable`")
        samples.append(doc)
    return sorted(samples, key=lambda s: _moment(s["ts"]))


def events(window: Window, samples: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every observed drift event: a change with no deploy between the two samples.

    Walks consecutive **reachable** pairs. An unreachable sample is not a comparison — the cluster
    said nothing, so nothing changed as far as this instrument can tell — but the gap it leaves is
    coverage, and `coverage()` reports it. Silently bridging across an outage would let a deploy
    hide inside the gap and turn a deploy into a drift event.
    """
    found: list[dict[str, Any]] = []
    last_deploy: str | None = None
    reachable = [s for s in samples if s.get("reachable")]
    for earlier, later in zip(reachable, reachable[1:]):
        if str(earlier.get("revision")) != str(later.get("revision")):
            last_deploy = str(later["ts"])
            continue
        if _moment(later["ts"]) - _moment(earlier["ts"]) > _gap_limit(window):
            # The two samples are further apart than the declared cadence allows, so a deploy
            # could have happened and been reverted between them. Not a drift event, and the hole
            # is in `coverage`.
            continue
        for subject in window.subjects:
            was, now = str(earlier.get("subjects", {}).get(subject, "")), str(
                later.get("subjects", {}).get(subject, "")
            )
            if was == now:
                continue
            found.append(
                {
                    "subject": subject,
                    "from": was,
                    "to": now,
                    "observed_at": str(later["ts"]),
                    "revision": str(later.get("revision")),
                    "last_deploy": last_deploy,
                    "since_deploy_seconds": (
                        None if last_deploy is None
                        else int((_moment(later["ts"]) - _moment(last_deploy)).total_seconds())
                    ),
                    # An upper bound, declared in the window and repeated here so a reader of the
                    # number alone cannot mistake it for the moment of divergence.
                    "interval_is": (
                        "an upper bound: the probe samples on a cadence, so the divergence began "
                        f"somewhere in the {window.cadence_minutes} minutes before this sample"
                    ),
                    "deleted": now == "",
                }
            )
    return found


def _gap_limit(window: Window) -> datetime.timedelta:
    return datetime.timedelta(minutes=window.cadence_minutes + window.tolerance_minutes)


def coverage(window: Window, samples: list[dict[str, Any]], now: str) -> dict[str, Any]:
    """How much of the declared window was actually observed, and where the holes are.

    `now` is passed in rather than read from the clock, so a report is a function of its inputs
    and two runs over the same log agree. The caller supplies it; the CLI supplies the wall clock
    and says so.
    """
    opens, closes, moment = _day(window.opens), _day(window.closes), _moment(now)
    elapsed = max(0.0, (min(moment, closes) - opens).total_seconds())
    reachable = [s for s in samples if s.get("reachable")]
    expected = elapsed / (window.cadence_minutes * 60) if window.cadence_minutes else 0.0

    holes = []
    limit = _gap_limit(window)
    # Bounded by the window at both ends, so an unsampled opening and a probe that stopped last
    # week are both holes. Without the trailing bound a dead instrument reports no gaps at all,
    # which is the exact failure this module exists to refuse.
    marks = [opens] + [_moment(s["ts"]) for s in reachable] + [min(moment, closes)]
    for earlier, later in zip(marks, marks[1:]):
        if later - earlier > limit:
            holes.append(
                {
                    "from": earlier.isoformat(),
                    "to": later.isoformat(),
                    "hours": round((later - earlier).total_seconds() / 3600, 2),
                }
            )
    return {
        "window_opens": window.opens,
        "window_closes": window.closes,
        "as_at": now,
        "window_elapsed_fraction": round(elapsed / (closes - opens).total_seconds(), 4),
        "samples_taken": len(samples),
        "samples_reachable": len(reachable),
        "samples_expected_by_now": int(expected),
        "sampled_fraction": round(len(reachable) / expected, 4) if expected >= 1 else 0.0,
        "gaps_wider_than_the_cadence": holes,
        "why_this_matters": (
            "'no drift in 91 days' and 'no drift in the hours we were looking' are different "
            "claims, and an unsampled window supports neither. An unreachable probe still writes "
            "a sample, so a stopped instrument shows up here rather than as a stable estate."
        ),
    }


def floor_reachable(
    window: Window, samples: list[dict[str, Any]], now: str, floor: float
) -> dict[str, Any]:
    """Can a coverage floor still be reached at the declared cadence, and by when (ticket 70).

    `coverage` reports what has been observed. This reports what *can still be* observed, which is
    the question nobody asked: an instrument sampling at 1% of its cadence is not merely behind,
    it is spending a budget that does not refill. Every hour of silence inside the window is an
    hour of coverage nothing later can buy back, so a floor stops being reachable at a computable
    moment, and after that moment the reading is settled whatever the probe does next.

    Build ticket 70's audit found this unguarded. Both tickets recorded that the probe was behind —
    ticket 64 as "NOT MEASURING", ticket 65 as "1% coverage" — and neither computed the deadline
    that shortfall implied, because ticket 64's guard asks about the last day and ticket 65 reads
    coverage only after the window has closed. "Behind" and "irrecoverable" are different facts.

    `now` is a parameter for the same reason `coverage`'s is: the arithmetic is a function of its
    inputs. The wall clock belongs to the caller, and the harness guard is the caller that has one.

    **Counts raw reachable samples, exactly as `coverage` does, and so inherits its gameability**:
    1966 hand-runs in one afternoon would read as a met floor, though no sensible reading of the
    window would call that coverage. Deliberate rather than overlooked. This figure has to agree
    with the one `verdict.decide` actually gates on, and a stricter count here would report a floor
    as out of reach that the verdict would then accept. Fix it in `coverage` or not at all.
    """
    opens, closes, moment = _day(window.opens), _day(window.closes), _moment(now)
    cadence = datetime.timedelta(minutes=window.cadence_minutes)  # `Window.load` refuses a zero
    total = (closes - opens) / cadence
    # Strictly above the floor, matching the window's own falsifier ("coverage above 90%") and
    # `verdict.decide`'s `<=` test. At exactly the floor the branch does not resolve, so a target
    # of exactly the floor would compute a deadline for an outcome that reads as pending.
    #
    # The second line is not belt-and-braces. `int(floor * total) + 1` is one short whenever the
    # product lands just under an integer in binary: `0.29 * 100` is 28.999999999999996, so the
    # target computes as 29, and 29/100 is *not* above 0.29. Rather than reason about which floors
    # are exact, the target is checked against `decide`'s own comparison and nudged if it fails.
    needed = int(floor * total) + 1
    if needed / total <= floor:
        needed += 1
    reachable_samples = [s for s in samples if s.get("reachable")]
    outstanding = needed - len(reachable_samples)

    # Whole cadence intervals only: a probe started part-way through an interval does not observe
    # that interval, and rounding the part up is how a deadline that has already passed reads as
    # ten minutes of slack. `total` stays fractional, because it is a window length rather than a
    # count of opportunities somebody still has.
    remaining_slots = max(0, int((closes - moment) / cadence))
    ceiling = min(1.0, (len(reachable_samples) + remaining_slots) / total)
    # The last moment a probe could start and still take `outstanding` samples before the window
    # closes. `None` once the floor is either already met or already gone: there is no deadline
    # for something that needs no action, and none for something no action can reach.
    latest_start = closes - outstanding * cadence
    return {
        "floor": floor,
        "window_closes": window.closes,
        "as_at": now,
        "cadence_minutes": window.cadence_minutes,
        "samples_reachable": len(reachable_samples),
        "samples_expected_over_window": int(total),
        "samples_needed": needed,
        "ceiling": round(ceiling, 4),
        "reachable": ceiling > floor,
        "latest_start": (
            None if outstanding <= 0 or latest_start < moment else latest_start.isoformat()
        ),
        "why_this_matters": (
            "an unsampled hour inside the window cannot be sampled later, so a coverage floor "
            "stops being reachable at a computable moment. After it, 'no drift observed' is "
            "unreadable against the pre-registration however diligently the probe runs."
        ),
    }


def report(
    now: str,
    window_path: Path | None = None,
    samples_path: Path | None = None,
    preconditions_path: Path | None = None,
) -> dict[str, Any]:
    """The measurement so far. A reduction, never a verdict."""
    window = Window.load(window_path)
    samples = load_samples(samples_path)
    source = preconditions_path or PRECONDITIONS_PATH
    preconditions = (
        (yaml.safe_load(source.read_text(encoding="utf-8")) or {}).get("preconditions") or []
        if source.is_file()
        else []
    )
    return {
        "question": window.question,
        "owner": window.owner,
        "would_falsify_the_spec": list(window.falsifiers),
        "coverage": coverage(window, samples, now),
        "drift_events": events(window, samples),
        "open_preconditions": [
            {"id": p["id"], "blocks": p.get("blocks"), "owner": p.get("owner")}
            for p in preconditions
            if str(p.get("state")) == "open"
        ],
        "verdict": None,
        "verdict_lands_at": VERDICT_TICKET,
        "why_no_verdict": (
            "this is the instrument. Whether drift between deploys justifies continuous "
            f"proof-of-force is {VERDICT_TICKET}, and it reads this data — writing the conclusion "
            "into the instrument is how a measurement becomes a demonstration."
        ),
    }
