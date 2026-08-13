"""Prediction-market price MOVES as dated world-layer signals — never price LEVELS as
probabilities (build ticket 59, decision ticket 21; research 17).

Research 17 S3.1 (Bürgi, Deng & Whelan 2026, "Makers or Takers: The Economics of the Kalshi
Prediction Market") is the load-bearing finding: Mincer–Zarnowitz regressions reject
unbiasedness **in every subsample tested**, and the bias is **worst in the low-price tail** —
exactly the region this system exists to price tail risk from. "Use only liquid markets" does
not fix it; liquidity-quintile and trade-size-quintile splits both reject the null in every
bucket. A price is a biased estimator of a probability with a known sign and an unmeasured scale
factor (S2.4, the Manski bound), so treating `price == P(event)` is wrong by construction. The
shape that survives that finding (S4): consume a market's **derivative and its disagreement**,
never its level — a price *change* is a dated, quantified, externally-authored event, which is
legitimate horizon-scanning input regardless of whether the level it moved between means
anything on its own.

This module is the "world-layer connector" research 17 S11.1 recommends, built the same way
build ticket 57 built the benchmark side of decision ticket 21: against a **caller-supplied
fixture price series**, because no live venue connection is reachable from this suite. Swapping
in a real Polymarket/Kalshi adapter changes nothing here — `price_moves` and `market_signal_run`
read `PriceObservation`/`PriceMove` values and do not care what produced them.

**The mechanism, not a comment.** `as_probability` exists and is called by nothing else in this
module or any other — its only job is to be the thing a future caller reaches for when tempted to
turn a price into a belief, and it refuses outright, every time, rather than warning and handing
back a number a warning can be silenced around.

**Signal source vs benchmark (decision ticket 21 Q1(b)).** `twin/benchmark.py` (build ticket 57)
quarantines a fixed set of question ids from ingestion, audited after the fact. This module is
the other half: the live signal-source path itself excludes a quarantined id **before**
`signal-classify` ever runs, so "the rest of the market universe may feed the twin freely" and
"never ingested... at any lag" hold in the one pipeline that actually ingests, not only in an
audit that assumes a pipeline agrees with it.

`ponytail:` no CLI verb — same reasoning `twin/ingest.py` (build ticket 53) and
`twin/benchmark.py` (build ticket 57) already gave: this is a typed function exercised at seam 2,
and a real venue adapter (a future ticket, not this one) is what would give a CLI invocation
something live to point at.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from .artefact import DERIVED, Artefact
from .canon import digest_of
from .grades import Capabilities
from .ingest import candidates_of
from .model import Overlay
from .repo import ModelRepo
from .signal_classify import SignalClassifyError, classify

KIND_MARKET_SIGNAL_RUN = "market-signal-run"

# The capability this module's artefacts declare (`twin/capabilities/forecast-book.yaml`, owning
# decision ticket 21) — the same list-of-one shape `twin/benchmark.py`'s CAPS_BENCHMARK uses.
CAPS_MARKET_SIGNALS = ["forecast-book"]

# Cited verbatim in every emitted artefact (acceptance criterion: "the bias evidence is cited in
# the artefact that consumes these signals") and in `as_probability`'s refusal message, so the
# same sentence travels with both the code path that respects the finding and the artefact a
# reader would otherwise have to go find the finding to understand.
BIAS_CITATION = (
    "favourite-longshot bias rejects unbiasedness in every subsample tested (Bürgi, Deng & "
    "Whelan 2026), worst in the low-price tail — research ticket 17 S3.1"
)


class MarketSignalError(RuntimeError):
    pass


class PriceLevelAsProbabilityError(RuntimeError):
    pass


@dataclass(frozen=True)
class PriceObservation:
    """One dated price reading from one venue. `price_level` is a raw market price in [0,1] —
    never a probability (see `as_probability`)."""

    question_id: str
    venue: str
    date: str  # YYYY-MM-DD
    price_level: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.price_level <= 1.0:
            raise MarketSignalError(
                f"{self.question_id}: price_level must be in [0,1], got {self.price_level}"
            )


@dataclass(frozen=True)
class PriceMove:
    """The derivative between two dated observations of the same question — never a level in
    isolation. No field here is named `probability` or `implied_probability`; the two levels a
    move was computed from are retained only as `from_level`/`to_level`, explicitly labelled, so
    a reader cannot mistake either one for a belief."""

    question_id: str
    venue: str
    from_date: str
    to_date: str
    from_level: float
    to_level: float

    @property
    def delta(self) -> float:
        return self.to_level - self.from_level

    @property
    def direction(self) -> str:
        if self.delta > 0:
            return "up"
        return "down" if self.delta < 0 else "flat"


def price_moves(observations: Iterable[PriceObservation]) -> list[PriceMove]:
    """Consecutive dated moves per question, sorted by date. A single observation for a question
    produces no move — there is nothing to derive a change from, and research 17 S4's value is
    the derivative, not the point, so that is the correct (not merely tolerated) outcome."""
    by_question: dict[str, list[PriceObservation]] = {}
    for obs in observations:
        by_question.setdefault(obs.question_id, []).append(obs)

    moves: list[PriceMove] = []
    for question_id in sorted(by_question):
        ordered = sorted(by_question[question_id], key=lambda o: o.date)
        for before, after in zip(ordered, ordered[1:]):
            moves.append(
                PriceMove(
                    question_id=question_id,
                    venue=after.venue,
                    from_date=before.date,
                    to_date=after.date,
                    from_level=before.price_level,
                    to_level=after.price_level,
                )
            )
    return moves


def as_probability(observation: PriceObservation) -> float:
    """Refused, always. There is no legitimate translation from a market price LEVEL to a
    probability in this codebase: the favourite-longshot bias means a price is a biased
    estimator of unknown scale (research 17 S2.4), worst exactly in the low-price tail this
    system prices tail risk from (S3.1). This fails outright rather than warning and returning a
    number anyway — a warning can be redirected to nowhere and a number would still flow
    downstream into a forecast (`price_levels_never_probabilities`, build ticket 59, decision
    ticket 21).
    """
    raise PriceLevelAsProbabilityError(
        f"{observation.question_id} ({observation.venue}, {observation.date}): a price LEVEL "
        f"({observation.price_level}) may never be read as a probability — "
        f"price_levels_never_probabilities. {BIAS_CITATION}."
    )


def move_statement(move: PriceMove) -> str:
    """The dated, sourced sentence a price move becomes before it reaches `signal-classify` —
    stating the change, never a level dressed as a belief."""
    return (
        f"{move.venue} price for {move.question_id!r} moved from {move.from_level:.2f} to "
        f"{move.to_level:.2f} ({move.direction}) between {move.from_date} and {move.to_date}"
    )


def market_signal_run(
    repo: ModelRepo,
    caps: Capabilities,
    org: str,
    moves: list[PriceMove],
    quarantined_ids: frozenset[str],
    command: list[str],
) -> Artefact:
    """Run `signal-classify`, unattended, over a set of price moves — the identical mechanism
    `twin/ingest.py` (build ticket 53) exercises over synthetic substrate, exercised here over
    prediction-market price moves instead (decision ticket 21; research 17's "world-layer
    connector").

    A quarantined question id (`twin/benchmark.py`, build ticket 57) is excluded **before**
    classification ever runs — proactive, not only auditable after the fact, so decision ticket
    21 Q1(b)'s "the rest of the market universe may feed the twin freely" and "never ingested...
    at any lag" hold for the pipeline that actually ingests.
    """
    if not moves:
        raise MarketSignalError("market_signal_run: no price moves to ingest")

    overlay = Overlay.load(repo, org)
    candidates = candidates_of(overlay)
    if not candidates:
        raise MarketSignalError(f"market_signal_run: overlay {org!r} declares no component to bind against")

    admitted = [m for m in moves if m.question_id not in quarantined_ids]
    excluded = [m for m in moves if m.question_id in quarantined_ids]

    items: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, move in enumerate(admitted):
        provenance = {
            "venue": move.venue,
            "question_id": move.question_id,
            "from_date": move.from_date,
            "to_date": move.to_date,
            # Explicitly labelled *level*, never *probability* — this is the field a reader (or
            # a careless future caller) would be tempted to rename, and the name is the guard.
            "price_level_from": move.from_level,
            "price_level_to": move.to_level,
            "bias_citation": BIAS_CITATION,
            "index": index,
        }
        try:
            result = classify(
                {"statement": move_statement(move), "source": f"market:{move.venue}", "candidates": candidates}
            )
        except SignalClassifyError as exc:
            failures.append({"index": index, "reason": str(exc), "provenance": provenance})
            continue
        items.append({**result, "provenance": provenance})

    return Artefact(
        kind=KIND_MARKET_SIGNAL_RUN,
        # No human gate: nothing here could carry a human's accountability
        # (`derived_never_human_signed`) — the same reasoning `twin/ingest.py` rests on.
        mark=DERIVED,
        command=command,
        pins={
            "model_repo": repo.pin.as_dict(),
            "overlay": overlay.ref.as_dict(),
            "world": overlay.world.ref.as_dict(),
            "org": overlay.org,
            "tool": {"name": "twin", "capabilities_digest": caps.digest},
            "moves_digest": digest_of(
                sorted((m.__dict__ for m in moves), key=lambda d: (d["question_id"], d["to_date"]))
            ),
            "quarantined_ids": sorted(quarantined_ids),
        },
        depth=caps.depth_block(CAPS_MARKET_SIGNALS),
        body={
            "items": items,
            "failures": failures,
            "excluded_quarantined": [
                {
                    "question_id": m.question_id, "venue": m.venue,
                    "from_date": m.from_date, "to_date": m.to_date,
                }
                for m in excluded
            ],
            "bias_evidence": BIAS_CITATION,
            "gate": (
                "price MOVES only, never LEVELS as probabilities (price_levels_never_probabilities, "
                "build ticket 59); no human gate at entry, binding trusted downstream as decision "
                "ticket 11 Q2 already decided for the sensing path this pipeline shares"
            ),
        },
    )
