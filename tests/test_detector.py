"""`detector` (build ticket 52, decision ticket 12 AC 4, Q2): the blind half of the
planter/detector/scorer split — "a detector agent runs with no access to [ground truth] and no
shared context." Structural blindness is checked here directly, not only in the harness guard:
this module imports nothing from `twin.planter`, and `detect()` is indifferent to a ground-truth
key even when one is spliced into its input.
"""

from __future__ import annotations

import ast
import inspect

from twin import detector
from twin.detector import Detection, detect


def test_detector_module_imports_nothing_naming_planter() -> None:
    tree = ast.parse(inspect.getsource(detector))
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [a.name for a in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module or ""] + [a.name for a in node.names]
        else:
            continue
        assert not any("planter" in n for n in names), names


def test_detect_flags_the_most_lexically_foreign_line_per_channel() -> None:
    public = {
        "channels": {
            "events": [
                "[atlas] Lunch order chat about sandwiches.",
                "[atlas] Lunch order chat about sandwiches again.",
                "[atlas] a completely unrelated cryptic anomaly appears",
                "[atlas] Lunch order chat about sandwiches once more.",
            ]
        }
    }
    detections = detect(public)
    assert len(detections) == 1
    d = detections[0]
    assert d.channel == "events"
    assert d.index == 2
    assert d.outlier_score < 0.3


def test_detect_flags_nothing_in_a_channel_with_fewer_than_two_lines() -> None:
    public = {"channels": {"hr": ["[atlas] only one line here"], "events": []}}
    assert detect(public) == ()


def test_detect_returns_one_detection_per_eligible_channel() -> None:
    public = {
        "channels": {
            "events": ["[a] one", "[a] two", "[a] three"],
            "hr": ["[a] four", "[a] five"],
        }
    }
    detections = detect(public)
    assert {d.channel for d in detections} == {"events", "hr"}


def test_detect_is_deterministic() -> None:
    public = {"channels": {"events": ["[a] one thing happens", "[a] another thing happens", "[a] a third thing happens"]}}
    assert detect(public) == detect(public)


def test_detect_is_indifferent_to_a_spliced_in_ground_truth_key() -> None:
    """The behavioural half of structural blindness: `detect()` does not even look at a `plants`
    key, whether it is absent (the honest shape `planter.PlantedWorld.public` hands over) or
    present with a decoy (what a careless caller might splice back in)."""
    public = {"channels": {"events": ["[a] one thing happens", "[a] another thing happens", "[a] a third thing happens"]}}
    tampered = {**public, "plants": [{"channel": "events", "index": 0, "signal": "not the real ground truth"}]}
    assert detect(public) == detect(tampered)


def test_detect_reads_only_the_channels_key() -> None:
    """No other input shape is consulted — `detect`'s own signature takes the whole public batch
    but only ever reaches into `["channels"]`, and never names `ground_truth` or `horizon`."""
    params = list(inspect.signature(detect).parameters)
    assert params == ["public"]
    assert not any("ground_truth" in p.lower() or "horizon" in p.lower() for p in params)


def test_detection_is_a_plain_dataclass_with_no_reference_to_ground_truth() -> None:
    fields = {f for f in Detection.__dataclass_fields__}
    assert fields == {"channel", "index", "line", "outlier_score"}
