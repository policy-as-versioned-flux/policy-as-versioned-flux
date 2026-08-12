"""Blind pinned emission, resolution scoring, and the narrow claim (build ticket 58, decision
ticket 21 Q1(c)/Q4/Q5).

`twin/benchmark.py` (build ticket 57) built the first half of decision ticket 21's external gate:
a mechanical, pre-registered question-selection rule and a quarantine that proves no benchmarked
question is ever ingested as a signal. This module builds the second half — **temporal
separation** — on the *same* selected questions: a forecast pinned and signed **before** its
question's resolution window opens, so "we forecast before we looked" is provable rather than
assured, and a resolution scored against that exact pinned emission once the question resolves.

**Nothing here is reinvented.** Signing and pinning reuse `twin/sign.py` and `twin/attest.py`
unchanged — `emit()` returns a `derived` `Artefact`, exactly the shape `attest.build()` already
signs with an agent signature and refuses a human one on (`derived_never_human_signed`), because a
forecast computed from its own pins is not a judgement anybody signs off on. Scoring reuses
`twin/scoring.py`'s proper scoring rules; `score_resolution()` never recomputes a Brier score by
hand.

**Blind, by construction rather than by review.** `emit()` refuses an emission timed at or after
its own question's declared resolution-window open — the same "gate, not an assurance" discipline
`twin/regimes.py`'s `as_consumed_admits_no_post_T_fact` uses for a different post-T leak.
`is_blind()` is the *same* function the refusal calls internally and an auditor can call again
later against nothing but the artefact's own recorded body, so nobody has to trust the refusal
fired — they can recompute it.

**Observe-only, by construction rather than by review (decision ticket 21 Q4).** This module
exposes exactly three functions — `emit`, `score_resolution`, `is_blind` — and none of them can
place a position: there is no function here that takes a stake, a side or an order. Harness guard
`forecast_book_is_blind_by_construction_and_observe_only` asserts the module's entire public
surface as an allow-list, the same discipline `prefilter_precedes_pricing` uses on
`twin/options.py`, so a differently-named position-placing function would still be caught.

**Co-registered, not merely same-named (decision ticket 21 Q2, RESOLVED).** `score_resolution()`
takes no question id or timestamp as a fresh parameter — both travel from the pinned emission's
own pins and body. A resolution can only ever be scored against the exact question and the exact
timestamps it was emitted against, never a same-id stand-in supplied out of step.

**The claim is narrow, and it travels with every result (decision ticket 21 Q5).** `CLAIM_SCOPE`
is carried in the body of both artefacts this module emits — what a clean score evidences, what it
explicitly does not (Wardley propagation, the causal elasticities, £ pricing, the org-specific
overlay), and the residual limit decision ticket 21 Q1 names: the quarantine proves no *direct*
ingestion, never that the twin's priors were unshaped by market-adjacent information arriving some
other way.
"""

from __future__ import annotations

import re
from typing import Any

from .artefact import Artefact, DERIVED
from .canon import digest_of
from .grades import Capabilities
from . import scoring

KIND_FORECAST_EMISSION = "forecast-emission"
KIND_RESOLUTION_SCORE = "resolution-score"

# The capability this module's artefacts declare (`twin/capabilities/forecast-book.yaml`, owning
# decision ticket 21) — a list because `caps.depth_block` takes one, not because a second
# capability is expected here.
CAPS_FORECAST_BOOK = ["forecast-book"]

# Fixed-width, UTC-only, always 'Z' — the same discipline `twin/regimes.py`'s `cutoff()` uses for
# its own dated cutoff, so blindness can be checked by plain string comparison rather than trusted
# to a lenient parser that would accept a shape that compares wrong.
_STAMP = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

CLAIM_SCOPE: dict[str, Any] = {
    "evidences": (
        "non-overconfidence in general world-forecasting, on a pre-registered, blind, "
        "co-registered question set, against an external adversarial baseline the twin cannot "
        "grade itself against"
    ),
    "does_not_evidence": [
        "Wardley propagation",
        "the causal elasticities",
        "£ pricing",
        "the org-specific overlay",
        "anything at organisational scale",
    ],
    "residual_limit": (
        "the quarantine (build ticket 57) proves no direct ingestion of a benchmarked question's "
        "id; it cannot prove the twin's priors were unshaped by market-adjacent information "
        "arriving some other way (decision ticket 21 Q1)"
    ),
}


class ForecastBookError(RuntimeError):
    pass


def _timestamp(value: Any, field: str) -> str:
    stamp = str(value).strip()
    if not _STAMP.match(stamp):
        raise ForecastBookError(
            f"{field} {stamp!r} is not a UTC timestamp of the form YYYY-MM-DDTHH:MM:SSZ — fixed "
            "width and always 'Z', so blindness is checked by plain string comparison rather than "
            "trusted to a parser lenient enough to compare wrong"
        )
    return stamp


def is_blind(emitted_at: str, resolution_window_opens_at: str) -> bool:
    """True only when the emission's own recorded timestamp is strictly before its own recorded
    resolution-window open — checked against the two recorded strings themselves, the same
    "checked against the artefact's own body rather than asserted in prose" discipline
    `BenchmarkSet.spans_full_confidence_range()` uses. An auditor holding only the artefact, not
    the code that built it, can re-run this exact check.
    """
    return _timestamp(emitted_at, "emitted_at") < _timestamp(resolution_window_opens_at, "resolution_window_opens_at")


def emit(
    caps: Capabilities,
    question: dict[str, Any],
    world_model: str,
    probability: float,
    emitted_at: str,
    command: list[str],
) -> Artefact:
    """A forecast, pinned and signed before its question's resolution window opens.

    Refused structurally, not by review: an emission at or after the question's own declared
    window-open is refused here rather than merely discouraged, and the refusal calls the same
    `is_blind()` an auditor can call again later against nothing but the emitted artefact's body.
    """
    qid = str(question["id"])
    opens = _timestamp(question["resolution_window_opens_at"], "resolution_window_opens_at")
    stamped = _timestamp(emitted_at, "emitted_at")
    if not 0.0 < float(probability) < 1.0:
        raise ForecastBookError(
            f"a forecast must be strictly between 0 and 1, got {probability} — a claim of "
            "certainty is not a forecast (twin/scoring.py's own refusal, reasserted at emission)"
        )
    if not is_blind(stamped, opens):
        raise ForecastBookError(
            f"emission at {stamped} is not strictly before question {qid!r}'s resolution window "
            f"opens at {opens} — blind emission requires strictly-before, refused here rather "
            "than merely reviewed"
        )
    return Artefact(
        kind=KIND_FORECAST_EMISSION,
        mark=DERIVED,
        command=command,
        pins={
            "question": {"id": qid, "digest": digest_of(question)},
            "world_model": str(world_model),
            "tool": {"capabilities_digest": caps.digest},
        },
        depth=caps.depth_block(CAPS_FORECAST_BOOK),
        body={
            "probability": float(probability),
            "emitted_at": stamped,
            "resolution_window_opens_at": opens,
            "observe_only": True,
            "position_placed": False,
            "claim_scope": CLAIM_SCOPE,
        },
    )


def score_resolution(
    caps: Capabilities,
    emission_doc: dict[str, Any],
    emission_sha256: str,
    observed: bool,
    command: list[str],
) -> Artefact:
    """Score a pinned, signed emission once its question resolves — via `twin/scoring.py`'s
    proper scoring rules, never a second implementation.

    Co-registered: the question id and both timestamps travel from the emission artefact's own
    pins and body, never as fresh parameters a caller could supply out of step, so a resolution can
    only ever be scored against the exact question and the exact emission it was pinned to.
    """
    kind = emission_doc.get("envelope", {}).get("kind")
    if kind != KIND_FORECAST_EMISSION:
        raise ForecastBookError(f"{kind!r} is not a {KIND_FORECAST_EMISSION!r} artefact")
    body = emission_doc["body"]
    if not is_blind(body["emitted_at"], body["resolution_window_opens_at"]):
        raise ForecastBookError(
            "the presented emission does not attest blindness against its own recorded "
            "timestamps — refusing to score it as though it were forecast before the window opened"
        )
    probability = float(body["probability"])
    raw = scoring.score(probability, observed)
    return Artefact(
        kind=KIND_RESOLUTION_SCORE,
        mark=DERIVED,
        command=command,
        pins={
            "emission": {
                "sha256": str(emission_sha256),
                "question": emission_doc["envelope"]["pins"]["question"],
            },
            "tool": {"capabilities_digest": caps.digest},
        },
        depth=caps.depth_block(CAPS_FORECAST_BOOK),
        body={
            "probability": probability,
            "observed": bool(observed),
            "emitted_at": body["emitted_at"],
            "resolution_window_opens_at": body["resolution_window_opens_at"],
            **raw,
            "rules": list(scoring.RULES),
            "claim_scope": CLAIM_SCOPE,
        },
    )
