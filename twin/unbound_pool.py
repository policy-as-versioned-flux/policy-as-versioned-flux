"""The decaying unbound-signal pool (build ticket 54, decision ticket 11 Q3).

Decision ticket 11 Q3 decided unbound signals are **retained with decay**, not discarded: "by
construction the earliest, weakest signals are exactly the ones that bind to nothing *yet* —
discarding deletes what the system exists to catch." This module is the retention half. The
rescue half — a model change triggering a retrospective sweep that rebinds a decayed signal and
resets its decay, and the lead-time-to-recognition that sweep makes measurable — is build
ticket 55, not here.

**Retained, structurally.** Nothing in this codebase deletes a committed signal file, and this
module adds no deletion path: `pool()` reads every signal in an org's overlay that carries no
`binding` claim (the exact complement of what `twin/verbs.py`'s `sense()` refuses) and reports
every one of them, including ones long past the decay threshold — a signal that has decayed out
stays in the report with `decayed: true` and a computed `decayed_on` date, never dropped from the
list (Q3's "not silently deleted").

**The decay function is a published parameter**, `twin/decay.yaml`, read and validated the way
`twin/attenuation.yaml` and `twin/evidence-ladder.yaml` are — a versioned document a non-programmer
reader can audit, not a constant buried in this module.

**Pool size and age distribution are observable**, via `twin unbound-pool`: `pool_size` counts the
still-live pool (decayed-out signals excluded), and `age_distribution` bins live signals by
half-life multiple — a bin width derived from the published half-life rather than a second,
uncoordinated parameter, the same discipline `twin/benchmark.py`'s confidence histogram uses
against its own selection rule's bins.
"""

from __future__ import annotations

import datetime
import math
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from . import PACKAGE_DIR, TOOL_VERSION, verbs
from .artefact import Artefact, DERIVED
from .canon import digest_of
from .grades import Capabilities
from .model import Overlay
from .repo import ModelRepo

DECAY_PATH = PACKAGE_DIR / "decay.yaml"
SCHEMA = "twin.decay/v1"

KIND_UNBOUND_POOL = "unbound-signal-pool"

# Retention is decision ticket 11's own sense-move capability (AC5's first half); the promotion/
# rescue half is build ticket 55's. Reused rather than a capability of its own, the same choice
# `twin/ingest.py` made for the pipeline that runs `signal_classify` at volume.
CAPS_UNBOUND_POOL = verbs.CAPS_SENSE

# Age bins for the observable distribution, in half-life multiples rather than raw days: a bin
# width derived from the published half-life, not a second, uncoordinated parameter.
_AGE_BINS = ("0-1", "1-2", "2-3", "3-4", "4+")


class DecayError(RuntimeError):
    pass


@lru_cache(maxsize=8)
def decay_function(path: Path | None = None) -> dict[str, Any]:
    """The versioned decay parameter, validated on read.

    Validated rather than trusted, for the reason the attenuation schedule and the evidence
    ladder are: a decay file whose half-life has quietly gone non-positive, or whose threshold
    has drifted outside (0, 1), would decay nothing (or decay everything instantly) while still
    looking published.
    """
    source = path or DECAY_PATH
    doc = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("schema") != SCHEMA:
        raise DecayError(f"{source}: not a {SCHEMA} document")
    half_life = doc.get("half_life_days")
    if not isinstance(half_life, (int, float)) or isinstance(half_life, bool) or half_life <= 0:
        raise DecayError(f"{source}: half_life_days must be a positive number, got {half_life!r}")
    threshold = doc.get("decayed_out_threshold")
    if (
        not isinstance(threshold, (int, float))
        or isinstance(threshold, bool)
        or not (0.0 < threshold < 1.0)
    ):
        raise DecayError(
            f"{source}: decayed_out_threshold must be strictly between 0 and 1, got {threshold!r}"
        )
    return doc


def weight(age_days: float, path: Path | None = None) -> float:
    """Exponential decay: full weight (1.0) at age zero, halved every published half-life."""
    if age_days < 0:
        raise DecayError(f"age_days must not be negative, got {age_days!r}")
    half_life = float(decay_function(path)["half_life_days"])
    return 0.5 ** (age_days / half_life)


def is_decayed(w: float, path: Path | None = None) -> bool:
    return w < float(decay_function(path)["decayed_out_threshold"])


def decayed_on(signal_date: str, path: Path | None = None) -> str:
    """The calendar date a signal's weight first crosses the published threshold — computed, so
    "when does this leave the live pool" is always answerable, whether or not that date has
    arrived yet."""
    doc = decay_function(path)
    half_life = float(doc["half_life_days"])
    threshold = float(doc["decayed_out_threshold"])
    half_lives_to_threshold = math.log(threshold) / math.log(0.5)
    days = math.ceil(half_life * half_lives_to_threshold)
    return (datetime.date.fromisoformat(signal_date) + datetime.timedelta(days=days)).isoformat()


def pin(path: Path | None = None) -> dict[str, Any]:
    """Which decay function a pool was computed against: its version, its parameters and its
    exact content — carried by every artefact that decays, the same reason the evidence ladder
    and the attenuation schedule pin themselves into what they gate."""
    doc = decay_function(path)
    return {
        "version": doc["version"],
        "half_life_days": doc["half_life_days"],
        "decayed_out_threshold": doc["decayed_out_threshold"],
        "digest": digest_of(doc),
    }


def unbound_ids(overlay: Overlay) -> set[str]:
    """Every signal in this overlay with no `binding` claim naming it — the exact complement of
    what `twin/verbs.py`'s `sense()` refuses to emit a bound-signal for."""
    bound = {str(c["signal"]) for c in overlay.claims.values() if c.get("kind") == "binding"}
    return set(overlay.signals) - bound


def pool(overlay: Overlay, at: str, path: Path | None = None) -> list[dict[str, Any]]:
    """Every unbound signal in this overlay, sorted by id, each carrying its age, weight, decay
    state and the date it does (or did) cross the threshold — never filtered out once decayed."""
    at_date = datetime.date.fromisoformat(at)
    entries: list[dict[str, Any]] = []
    for sid in sorted(unbound_ids(overlay)):
        signal = overlay.signals[sid]
        signal_date = str(signal["date"])
        age_days = (at_date - datetime.date.fromisoformat(signal_date)).days
        if age_days < 0:
            raise DecayError(
                f"signal {sid!r} is dated {signal_date}, after the declared time {at} — a "
                "signal's age cannot be computed from a time before it was observed"
            )
        w = weight(age_days, path)
        entries.append(
            {
                "id": sid,
                "date": signal_date,
                "steep": signal["steep"],
                "age_days": age_days,
                "weight": round(w, 6),
                "decayed": is_decayed(w, path),
                "decayed_on": decayed_on(signal_date, path),
            }
        )
    return entries


def age_distribution(entries: list[dict[str, Any]], path: Path | None = None) -> dict[str, int]:
    """A histogram over the live (non-decayed) pool, binned by half-life multiple. Every bin is
    present, zero included, the same discipline `twin/benchmark.py`'s `confidence_distribution`
    uses so an empty bin is visible rather than merely absent from the count."""
    half_life = float(decay_function(path)["half_life_days"])
    counts = {b: 0 for b in _AGE_BINS}
    for entry in entries:
        if entry["decayed"]:
            continue
        multiple = int(entry["age_days"] / half_life)
        counts[_AGE_BINS[min(multiple, len(_AGE_BINS) - 1)]] += 1
    return counts


def unbound_pool_artefact(
    repo: ModelRepo, caps: Capabilities, org: str, at: str, command: list[str]
) -> Artefact:
    """The pool, as a derived artefact: nothing here could carry a human's accountability
    (`derived_never_human_signed`) — the overlay's own signals and claims, and the published decay
    function, determine the output completely."""
    overlay = Overlay.load(repo, org)
    entries = pool(overlay, at)
    live = [e for e in entries if not e["decayed"]]

    return Artefact(
        kind=KIND_UNBOUND_POOL,
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "version": TOOL_VERSION, "capabilities_digest": caps.digest},
            "at": at,
            "decay": pin(),
        },
        depth=caps.depth_block(CAPS_UNBOUND_POOL),
        body={
            "as_of": at,
            "pool_size": len(live),
            "decayed_out_count": len(entries) - len(live),
            "age_distribution": age_distribution(entries),
            "signals": entries,
            "rescue": (
                "a model change triggering a retrospective sweep that rebinds a decayed signal "
                "and resets its decay is build ticket 55, not implemented here"
            ),
        },
    )
