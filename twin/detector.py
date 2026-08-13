"""`detector` (build ticket 52, decision ticket 12 AC 4, Q2): the blind half of the
planter/detector/scorer split.

Decision ticket 12 Q2: "a detector agent runs with no access to [ground truth] and no shared
context." Enforced here structurally, not by convention: this module imports nothing from
`twin.planter`, never constructs or reads a `planter.Plant` or `planter.PlantedWorld`, and
`detect()` reads only a batch's `channels` — the exact shape `planter.PlantedWorld.public` hands
onward, with its own `plants` key already gone.
`twin/invariants/harness.py`'s `planter_detector_scorer_are_structurally_separated_and_...` guard
proves both properties on the real code: an AST scan finds no import naming `planter`, and
`detect()` returns byte-identical output whether or not a caller's input dict happens to carry a
`plants` key at all — the function does not even look, so ground truth spliced back in by a
careless caller still cannot leak through.

`ponytail:` the anomaly heuristic below is the same "shares little vocabulary with its
surroundings" signature `substrate_eval.plant_difficulty` measures, computed here for the opposite
purpose and with no ground truth: flag the most lexically foreign line per channel as the
suspected plant, rather than score a known plant's own difficulty after the fact. It has no claim
to be a good anomaly detector — what is being proven is the structural blindness, not detection
quality, the same "stand-in for judgement" shape `signal_classify.py`'s own docstring names.
Upgrade path: swap `detect`'s body for a model call; nothing about its signature, or the blindness
the harness guard checks, has to change.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

_STOPWORDS = frozenset(
    ("a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "is", "it", "no", "of", "on",
     "or", "reason", "that", "the", "this", "to", "with", "after", "again")
)
_FOCUS_PREFIX = re.compile(r"^\[[^\]]*\]\s*")


def _tokens(text: str) -> set[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return {w for w in words if len(w) >= 2 and w not in _STOPWORDS}


@dataclass(frozen=True)
class Detection:
    """A candidate plant location and nothing else — no field on this class, or anywhere in this
    module, is capable of naming an actionability horizon; that concept does not exist here."""

    channel: str
    index: int
    line: str
    outlier_score: float  # 0.0 = shares no vocabulary with its channel's other lines


def detect(public: dict[str, Any]) -> tuple[Detection, ...]:
    """The detector. Reads only `public["channels"]` — never a `plants` key, never anything from
    `twin.planter` — and flags, per channel, the single line sharing the least vocabulary with the
    rest of that channel's own lines. A channel with fewer than two lines flags nothing: there is
    no "rest" for a line to be foreign against.

    Always proposes its single best candidate per eligible channel, the same "max is still a
    choice" honesty `signal_classify._bind` documents — a channel with no real plant still gets a
    guess, and it is `twin/scorer.py`'s job, working from ground truth this function never sees,
    to say whether that guess was right.
    """
    channels = public.get("channels", {})
    detections: list[Detection] = []
    for channel, lines in channels.items():
        if len(lines) < 2:
            continue
        best_index: int | None = None
        best_score: float | None = None
        for i, line in enumerate(lines):
            own = _tokens(_FOCUS_PREFIX.sub("", line))
            other: set[str] = set()
            for j, other_line in enumerate(lines):
                if j != i:
                    other |= _tokens(_FOCUS_PREFIX.sub("", other_line))
            score = len(own & other) / len(own) if own else 1.0
            if best_score is None or score < best_score:
                best_index, best_score = i, score
        assert best_index is not None and best_score is not None  # len(lines) >= 2 guarantees a choice
        detections.append(
            Detection(channel=channel, index=best_index, line=lines[best_index], outlier_score=best_score)
        )
    return tuple(detections)
