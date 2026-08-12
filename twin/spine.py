"""Spine anchoring and free-running (build ticket 50, decision ticket 12 Q3, spec story 57).

RESOLVED 2026-08-05: "the spine is authoritative and immutable; the substrate may never
contradict a dated public fact, but is free wherever the record is silent — which is almost
everywhere." Two failure modes named there, both real. **Over-anchoring**
(generate-everything-from-the-spine) is "actively dangerous": if nothing but the plants were left
un-derived from the public record, diffing the substrate against the spine would recover the
plants directly — a rigged test dressed as a rigorous one. **Silent drift** — never checking at
all — lets an authored substrate quietly say something the record contradicts, which is the
failure `reconcile()` below exists to catch rather than assume away.

**The spine is not invented for this module — it is the org's own real, dated `signal`
documents**, already committed for every backtest fixture (build tickets 38-41: Carillion, NMC
Health, Wirecard, Enron). `Spine.from_overlay()` reads them directly rather than authoring a
second, parallel "spine fact" format: `DATED_FACTS["signals"] == "date"` (`twin/schema.py`) is
already the field `twin/regimes.py` gates `as-consumed`/`as-knowable` on, so a spine built this way
carries knowability dates the regime gate already understands, by construction rather than by a
second parser agreeing with the first today. `Spine.at()` reuses `regimes.cutoff()` itself for
exactly that reason — genuine reuse, checked in `tests/test_spine.py` by asserting a malformed
checkpoint fails with `regimes.RegimeError`, not merely a look-alike error string.

`anchor()` inserts every fact knowable by a checkpoint into a generated substrate batch
(`twin/substrate_generator.py`'s own output shape), verbatim; `reconcile()` checks a batch
actually carries every fact it should and names what is missing rather than reporting a silent
gap; `reconcile_at_every_checkpoint()` runs that check once per distinct spine date — AC 1's "at
every dated checkpoint", not only the last one. `diff_against_spine()` is the attack surface
named directly: the split a reader computing "batch minus spine" would see. The free-running half
— everything not anchored, mundane content and any planted signal alike — has to stay large
relative to the anchored half, or the diff recovers the plants; `tests/test_spine.py` demonstrates
the split on the real Carillion fixture rather than asserting the property in prose.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import regimes
from .canon import digest_of
from .model import Overlay


class SpineError(RuntimeError):
    """A spine fact malformed, a spine with nothing in it, or a substrate that has silently
    drifted from a fact it must never contradict."""


@dataclass(frozen=True)
class SpineFact:
    """One real, dated, public fact the substrate may never contradict. Carries the identical
    field name (`date`) `DATED_FACTS["signals"]` already names, not a look-alike."""

    id: str
    date: str
    statement: str
    source: str

    def as_dict(self) -> dict[str, Any]:
        return {"id": self.id, "date": self.date, "statement": self.statement, "source": self.source}


@dataclass(frozen=True)
class Spine:
    """The immutable public spine for one org: its own real, dated signals — never generated,
    never authored a second time. Small by construction, the same way a causal-account is meant
    to stay sparse: most of the record is not disputed, and the spine only names what is knowable.
    """

    facts: tuple[SpineFact, ...]

    def __post_init__(self) -> None:
        if not self.facts:
            raise SpineError("a spine carries no facts — there is nothing to anchor to")
        ids = [f.id for f in self.facts]
        if len(ids) != len(set(ids)):
            raise SpineError("a spine declares a fact id twice")

    @classmethod
    def from_overlay(cls, overlay: Overlay) -> "Spine":
        """The org's own real dated signals, unmodified. Reading `overlay.signals` directly is
        the seam AC 1 asks to be defined: the spine is not a separate authored artefact, it is the
        set of dated facts the org overlay already carries."""
        return cls(
            facts=tuple(
                SpineFact(
                    id=ident, date=str(doc["date"]), statement=str(doc["statement"]), source=str(doc["source"])
                )
                for ident, doc in sorted(overlay.signals.items())
            )
        )

    def pin(self) -> dict[str, Any]:
        return {"digest": digest_of([f.as_dict() for f in self.facts])}

    def at(self, checkpoint: str) -> tuple[SpineFact, ...]:
        """Every fact knowable on or before `checkpoint` — reusing `regimes.cutoff`'s own
        validation and day-string comparison, the identical gate `as-knowable` runs over signals,
        so a spine fact is gated by the regime machinery rather than a parallel copy of it."""
        at = regimes.cutoff(checkpoint)
        return tuple(f for f in self.facts if f.date <= at)


def anchor(batch: dict[str, Any], spine: Spine, checkpoint: str, channel: str = "events") -> dict[str, Any]:
    """Insert every spine fact knowable by `checkpoint`, verbatim, into `batch[channel]` — the
    anchoring half. Additive only: nothing already in `batch` is touched, so free-running content
    (mundane lines, any planted signal) stays exactly as free as it was — anchoring does not
    overwrite or relocate it.

    Returns a new batch; `batch` itself is not mutated, the discipline `regimes.apply` follows.
    """
    channels = batch.get("channels", {})
    if channel not in channels:
        raise SpineError(f"batch carries no channel {channel!r} to anchor the spine into")
    known = spine.at(checkpoint)
    updated = {c: list(lines) for c, lines in channels.items()}
    updated[channel] = updated[channel] + [f.statement for f in known]
    return {
        **batch,
        "channels": updated,
        "anchored": [f.as_dict() for f in known],
        "spine_checkpoint": regimes.cutoff(checkpoint),
    }


def reconcile(batch: dict[str, Any], spine: Spine, checkpoint: str) -> dict[str, Any]:
    """Every spine fact knowable by `checkpoint` is present, verbatim, somewhere in `batch` —
    checked against the actual substrate, not assumed from having called `anchor()` earlier.
    Refuses, naming what is missing, rather than reporting a silent gap (AC: "reconciles with the
    public spine at every dated checkpoint").
    """
    known = spine.at(checkpoint)
    present = {line for lines in batch.get("channels", {}).values() for line in lines}
    missing = [f for f in known if f.statement not in present]
    if missing:
        raise SpineError(
            f"at checkpoint {checkpoint}: {len(missing)} spine fact(s) knowable by then are "
            f"absent from the substrate ({', '.join(f.id for f in missing)}) — the substrate has "
            "silently drifted from a record it must never contradict by omission"
        )
    return {
        "checkpoint": regimes.cutoff(checkpoint),
        "reconciled": [f.id for f in known],
        "consequence": "every spine fact knowable by this checkpoint is present, verbatim, in the substrate",
    }


def reconcile_at_every_checkpoint(batch: dict[str, Any], spine: Spine) -> list[dict[str, Any]]:
    """`reconcile()`, run once per distinct fact date in `spine` — AC 1's "at every dated
    checkpoint", not only the last one."""
    checkpoints = sorted({f.date for f in spine.facts})
    return [reconcile(batch, spine, cp) for cp in checkpoints]


def diff_against_spine(batch: dict[str, Any], spine: Spine) -> dict[str, list[str]]:
    """What a reader computing "the substrate minus the spine" sees: every line split into
    `anchored` (identical to a spine fact's own statement) and `free_running` (everything else).

    This is the attack surface decision ticket 12 Q3 names directly: if `free_running` reduced to
    exactly the planted signals, this diff alone would locate every plant. It does not here,
    because free-running mundane content dominates by construction
    (`twin/substrate_generator.py`'s own `MIN_MUNDANE_FRACTION`) — a plant sits inside a residual
    much larger than itself, not standing alone as the only unanchored thing.
    """
    statements = {f.statement for f in spine.facts}
    anchored: list[str] = []
    free_running: list[str] = []
    for lines in batch.get("channels", {}).values():
        for line in lines:
            (anchored if line in statements else free_running).append(line)
    return {"anchored": sorted(anchored), "free_running": sorted(free_running)}
