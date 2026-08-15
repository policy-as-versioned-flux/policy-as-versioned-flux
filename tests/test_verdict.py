"""The Flux falsification verdict (build ticket 65).

Seam 2: structural claims only — which branch resolves on which evidence, and which combinations
of evidence are refused. The point of testing this at all is that the failure mode is an
*argument*, not a wrong number: reading a null state-drift result as "therefore a deploy-time
attestation suffices" is a false dichotomy, and a false dichotomy written into a durable artefact
on the critical path is not caught by any arithmetic test. So the elimination path is closed in
code and these tests are what prove it stays closed.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from twin import drift, verdict
from twin.drift import Window
from twin.verdict import Protocol, VerdictError

PROTOCOL = """\
schema: drift.verdict_protocol/v1
version: 1
question: Does the risk basis require continuous proof of force?
risk_basis: A hop about an interval prices only on interval evidence.
evidence_ladder_version: 2
path_admission_threshold: 2
reading_gate: {minimum_coverage: 0.90, requires_window_closed: true, why: coverage is not a footnote}
branches:
  - {id: continuous-state, claim: c, settled_by: s, instrument: w, window_open: true}
  - {id: point-in-time, claim: c, settled_by: s, instrument: null, window_open: false,
     entailed_only_if_both_falsified: [continuous-state, continuous-action]}
  - {id: continuous-action, claim: c, settled_by: s, instrument: null, window_open: false,
     class_implementations: [Progent, AgentSpec, VIGIL]}
amendment_if_falsified: Story 81 drops the verification-substrate half.
operation: {owner: A Named Human}
"""

WINDOW = """\
schema: drift.window/v1
version: 1
question: Does a deployed control diverge between deploys?
window: {opens: '2026-01-01', closes: '2026-01-11', days: 10}
cadence: {every_minutes: 60, tolerance_minutes: 15}
subjects:
  - {id: live-version, repository: r, cluster: c, control: x, desired_from: a, observed_from: b}
outcomes_that_would_falsify_the_spec:
  - No drift event across the full window at coverage above 90%.
drift_event: {definition: d, deploy_marker: m, interval: i}
scope_limit:
  measures: STATE continuity only.
  does_not_measure: ACTION continuity. A control can hold its state while an action crosses it.
  consequence_for_the_verdict: A null result falsifies the STATE branch only.
operation: {owner: A Named Human, runner: cron}
"""


def _protocol(tmp_path: Path, text: str = PROTOCOL) -> Protocol:
    path = tmp_path / "verdict.yaml"
    path.write_text(text, encoding="utf-8")
    return Protocol.load(path)


@pytest.fixture()
def protocol(tmp_path: Path) -> Protocol:
    return _protocol(tmp_path)


@pytest.fixture()
def window(tmp_path: Path) -> Window:
    path = tmp_path / "window.yaml"
    path.write_text(WINDOW, encoding="utf-8")
    return Window.load(path)


def _full_coverage_log(tmp_path: Path, *, drifts: bool) -> list[dict]:
    """Ten days of hourly samples, so the reading gate actually opens."""
    lines = []
    for hour in range(10 * 24):
        day, at = 1 + hour // 24, hour % 24
        value = "2.0.0" if drifts and hour > 100 else "1.0.0"
        lines.append(
            {
                "ts": f"2026-01-{day:02d}T{at:02d}:00:00Z",
                "reachable": True,
                "revision": "r1",
                "subjects": {"live-version": value},
            }
        )
    path = tmp_path / "samples.jsonl"
    path.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
    return drift.load_samples(path)


# -- the pre-registration refuses what would make it unfalsifiable ----------------------------


def test_a_protocol_declaring_two_branches_does_not_load(tmp_path: Path) -> None:
    """The original pair looked exhaustive. That is the defect, so it is a load error."""
    text = PROTOCOL.replace(
        "  - {id: continuous-action, claim: c, settled_by: s, instrument: null, window_open: false,\n"
        "     class_implementations: [Progent, AgentSpec, VIGIL]}\n",
        "",
    )
    with pytest.raises(VerdictError, match="three branches"):
        _protocol(tmp_path, text)


def test_a_protocol_with_no_drafted_amendment_does_not_load(tmp_path: Path) -> None:
    text = PROTOCOL.replace("amendment_if_falsified: Story 81 drops the verification-substrate half.", "")
    with pytest.raises(VerdictError, match="negative result changes nothing"):
        _protocol(tmp_path, text)


def test_the_action_branch_resting_on_one_product_does_not_load(tmp_path: Path) -> None:
    """Judge the class, not the product — build ticket 65 says so, and one name is a product."""
    text = PROTOCOL.replace("[Progent, AgentSpec, VIGIL]", "[AWS Dogwood]")
    with pytest.raises(VerdictError, match="class"):
        _protocol(tmp_path, text)


def test_a_protocol_disagreeing_with_the_live_ladder_does_not_load(tmp_path: Path) -> None:
    """The risk basis cites a threshold. A statement that can rot away from its gate is prose."""
    text = PROTOCOL.replace("path_admission_threshold: 2", "path_admission_threshold: 4")
    with pytest.raises(VerdictError, match="path_admission_threshold"):
        _protocol(tmp_path, text)


def test_a_protocol_naming_no_owner_does_not_load(tmp_path: Path) -> None:
    text = PROTOCOL.replace("operation: {owner: A Named Human}", "operation: {}")
    with pytest.raises(VerdictError, match="owner"):
        _protocol(tmp_path, text)


def test_a_coverage_floor_of_zero_does_not_load(tmp_path: Path) -> None:
    text = PROTOCOL.replace("minimum_coverage: 0.90", "minimum_coverage: 0")
    with pytest.raises(VerdictError, match="minimum_coverage"):
        _protocol(tmp_path, text)


def test_a_coverage_floor_of_one_does_not_load(tmp_path: Path) -> None:
    """The gate asks for coverage *above* the floor, so a floor of 1 can never be cleared.

    Found by build ticket 70's review of its own reachability guard: a floor of 1 loaded fine and
    made `floor_reachable` report the floor permanently out of reach on a window that had not even
    opened. The unsatisfiable protocol is the defect, not the guard reading it.
    """
    text = PROTOCOL.replace("minimum_coverage: 0.90", "minimum_coverage: 1.0")
    with pytest.raises(VerdictError, match="minimum_coverage"):
        _protocol(tmp_path, text)


def test_a_window_declaring_no_cadence_does_not_load(tmp_path: Path) -> None:
    """Without a cadence there is no expected sample count, so coverage divides by nothing."""
    path = tmp_path / "no-cadence.yaml"
    path.write_text(WINDOW.replace("every_minutes: 60", "every_minutes: 0"), encoding="utf-8")
    with pytest.raises(drift.DriftError, match="cadence"):
        Window.load(path)


# -- the branches resolve separately, and only on their own evidence ---------------------------


def test_below_the_coverage_floor_no_branch_resolves(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """A closed window with nothing in it. 'No drift observed' here is not a result.

    Read after the close deliberately, so the coverage gate is what bites rather than the
    window-still-open gate — an unsampled window that ran its full length is the shape build ticket
    64 already came within three days of producing, and it must not read as a falsifier.
    """
    samples = drift.load_samples(tmp_path / "nothing.jsonl")
    decided = verdict.decide(protocol, window, samples, "2026-01-12T00:00:00Z")
    state = decided["branches"]["continuous-state"]
    assert state["state"] == verdict.PENDING
    assert "coverage" in state["why"]
    assert decided["verdict"] is None


def test_the_window_still_open_holds_the_verdict_even_at_full_coverage(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-06T00:00:00Z")
    assert decided["branches"]["continuous-state"]["state"] == verdict.PENDING
    assert "has not closed" in decided["branches"]["continuous-state"]["why"]


def test_no_drift_at_full_coverage_over_a_closed_window_falsifies_the_state_branch(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert decided["branches"]["continuous-state"]["state"] == verdict.FALSIFIED
    assert decided["amendment_if_falsified"] == protocol.amendment_if_falsified


def test_a_drift_event_at_full_coverage_holds_the_state_branch(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    samples = _full_coverage_log(tmp_path, drifts=True)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert decided["branches"]["continuous-state"]["state"] == verdict.HELD


def test_the_action_branch_is_unmeasured_and_says_no_window_is_open(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """Recorded as absent rather than inferred to be unnecessary."""
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    action = decided["branches"]["continuous-action"]
    assert action["state"] == verdict.UNMEASURED
    assert "no pre-registered window" in action["why"]


# -- the false dichotomy is closed in code, not warned against ---------------------------------


def test_a_falsified_state_branch_never_concludes_the_point_in_time_branch(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """The defect build ticket 65 exists to prevent, asserted directly.

    Full coverage, a closed window, not one drift event — the strongest null result the state
    instrument can produce — and the residual branch still does not resolve, because the third
    branch is unmeasured.
    """
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert decided["branches"]["continuous-state"]["state"] == verdict.FALSIFIED
    assert decided["branches"]["point-in-time"]["state"] == verdict.PENDING
    assert "elimination" in decided["branches"]["point-in-time"]["why"]
    assert decided["verdict"] is None


def test_a_held_state_branch_earns_a_verdict_in_its_own_right(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """The one direction readable without the action window.

    A branch that HOLDS answers the question positively and needs no elimination: observed drift
    means continuous state proof is required, whatever an action-boundary window would later show.
    The residual branch is never reached, and the verdict says what Flux is evidence *of*.
    """
    samples = _full_coverage_log(tmp_path, drifts=True)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert decided["verdict"] is not None
    assert "continuous-state" in decided["verdict"]
    assert "not evidence that no action crossed" in decided["verdict"]
    assert decided["branches"]["point-in-time"]["state"] == verdict.PENDING


def test_a_protocol_that_drops_the_elimination_rule_does_not_load(tmp_path: Path) -> None:
    """The rule is enforced from code; deleting it from the file must not open the door.

    Reading the guard out of the yaml would mean one deleted key re-opened the elimination path —
    the exact defect this module exists to refuse, reachable by editing a data file.
    """
    text = PROTOCOL.replace(
        "     entailed_only_if_both_falsified: [continuous-state, continuous-action]", "     x: y"
    )
    with pytest.raises(VerdictError, match="entailed by"):
        _protocol(tmp_path, text)


def test_the_elimination_rule_is_not_read_from_the_file(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """Belt and braces: even a loaded protocol whose rule was mutated after load cannot open it."""
    protocol.branches[verdict.RESIDUAL]["entailed_only_if_both_falsified"] = []
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert decided["branches"]["point-in-time"]["state"] == verdict.PENDING
    assert decided["verdict"] is None


def test_a_window_whose_scope_limit_states_no_consequence_yields_no_verdict(
    tmp_path: Path
) -> None:
    """Naming the limitation without naming what it does to the reading is half a citation."""
    path = tmp_path / "half.yaml"
    path.write_text(
        WINDOW.replace("  consequence_for_the_verdict: A null result falsifies the STATE branch only.\n", ""),
        encoding="utf-8",
    )
    with pytest.raises(VerdictError, match="scope_limit"):
        verdict.decide(_protocol(tmp_path), Window.load(path), [], "2026-01-11T00:00:00Z")


def test_exactly_the_floor_is_not_above_the_floor(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    """The window's falsifier says coverage *above* 90%, so 90.0% exactly does not meet it."""
    lines = []
    for hour in range(10 * 24):
        if hour % 10 == 0:  # drop one sample in ten, landing at 90% coverage exactly
            continue
        day, at = 1 + hour // 24, hour % 24
        lines.append(
            {
                "ts": f"2026-01-{day:02d}T{at:02d}:00:00Z",
                "reachable": True,
                "revision": "r1",
                "subjects": {"live-version": "1.0.0"},
            }
        )
    path = tmp_path / "ninety.jsonl"
    path.write_text("".join(json.dumps(line) + "\n" for line in lines), encoding="utf-8")
    decided = verdict.decide(protocol, window, drift.load_samples(path), "2026-01-11T00:00:00Z")
    branch = decided["branches"]["continuous-state"]
    assert branch["evidence"]["sampled_fraction"] == 0.9
    assert branch["state"] == verdict.PENDING
    assert "at or below" in branch["why"]


def test_a_protocol_that_does_not_require_a_closed_window_reads_one_early(
    window: Window, tmp_path: Path
) -> None:
    """The gate has two halves and both are pre-registered, so both are exercised.

    Nothing sets this false today. The test exists because an untested branch of a reading gate is
    how a gate comes to be relaxed without anyone noticing it was ever tight.
    """
    relaxed = _protocol(tmp_path, PROTOCOL.replace("requires_window_closed: true", "requires_window_closed: false"))
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(relaxed, window, samples, "2026-01-06T00:00:00Z")
    assert decided["branches"]["continuous-state"]["state"] == verdict.FALSIFIED


# -- what the instrument could not see travels with the verdict -------------------------------


def test_the_verdict_cites_what_the_instrument_could_not_measure(
    protocol: Protocol, window: Window, tmp_path: Path
) -> None:
    samples = _full_coverage_log(tmp_path, drifts=False)
    decided = verdict.decide(protocol, window, samples, "2026-01-11T00:00:00Z")
    assert "ACTION continuity" in decided["scope_limit"]["does_not_measure"]


def test_a_window_with_no_scope_limit_yields_no_verdict(tmp_path: Path) -> None:
    """A verdict that cannot state what its instrument could not see is the false dichotomy."""
    path = tmp_path / "bare.yaml"
    path.write_text(re.sub(r"scope_limit:.*?(?=operation:)", "", WINDOW, flags=re.S), encoding="utf-8")
    bare = Window.load(path)
    with pytest.raises(VerdictError, match="scope_limit"):
        verdict.decide(_protocol(tmp_path), bare, [], "2026-01-11T00:00:00Z")


# -- the committed files, read as committed ----------------------------------------------------


def test_the_committed_protocol_loads() -> None:
    live = Protocol.load()
    assert set(live.branches) == set(verdict.BRANCHES)
    assert live.minimum_coverage == 0.90
    assert "65" in live.amendment_if_falsified or "81" in live.amendment_if_falsified


def test_the_coverage_floor_matches_the_windows_own_falsifier() -> None:
    """The floor is the window's number, not this file's.

    Restating it lower in the verdict protocol would retune the measurement through the back door,
    which is the exact move `drift_window_was_declared_before_it_was_measured` exists to catch on
    the window itself.
    """
    declared = Window.load()
    percentages = {
        int(match) for falsifier in declared.falsifiers for match in re.findall(r"(\d+)%", falsifier)
    }
    assert percentages, "the window's falsifiers name no coverage figure to match against"
    assert Protocol.load().minimum_coverage * 100 == min(percentages)


def test_the_live_verdict_is_pending_because_the_window_is_open() -> None:
    """Not a placeholder assertion: this is the honest state of build ticket 65 today."""
    decided = verdict.decide(Protocol.load(), Window.load(), drift.load_samples(), "2026-08-15T00:00:00Z")
    assert decided["verdict"] is None
    assert decided["branches"]["continuous-state"]["state"] == verdict.PENDING


# -- can the floor still be reached at all? (build ticket 70) ---------------------------------
#
# The composition build ticket 70's audit found unguarded. Ticket 64 built the instrument and said
# in its own guard's docstring that "coverage is ticket 65's problem"; ticket 65 pre-registered a
# 90% floor and never asked whether the instrument could deliver it. Both are green apart and the
# pair cannot produce a reading.


def test_an_empty_window_that_has_only_just_opened_can_still_reach_the_floor(window: Window) -> None:
    reach = drift.floor_reachable(window, [], "2026-01-01T00:00:00Z", 0.90)
    assert reach["reachable"] is True
    assert reach["ceiling"] == 1.0
    assert reach["latest_start"] == "2026-01-01T23:00:00+00:00"


def test_a_window_left_unsampled_past_its_latest_start_can_never_reach_the_floor(
    window: Window,
) -> None:
    """Two days of silence in a ten-day window at 90% is already unrecoverable."""
    reach = drift.floor_reachable(window, [], "2026-01-03T00:00:00Z", 0.90)
    assert reach["reachable"] is False
    assert reach["ceiling"] < 0.90
    assert reach["latest_start"] is None
    assert reach["samples_needed"] == 217  # floor(0.9 * 240) + 1 — *above* the floor, not at it


def test_the_sample_target_is_the_one_the_verdict_would_actually_accept(window: Window) -> None:
    """The target is checked against `decide`'s own comparison, not assumed from the arithmetic.

    `int(floor * total) + 1` is one short whenever the product lands just under an integer in
    binary. `0.29 * 240` is 69.6 and safe, but the same expression on a 100-interval window gives
    28.999999999999996, so the target computes as 29 and 29/100 is *not* above 0.29. Asserted
    directly against the rule `verdict.decide` applies, on a floor chosen because it is inexact.
    """
    for floor in (0.29, 0.58, 0.87, 0.90):
        reach = drift.floor_reachable(window, [], "2026-01-01T00:00:00Z", floor)
        needed, total = reach["samples_needed"], reach["samples_expected_over_window"]
        assert needed / total > floor, f"floor {floor}: {needed}/{total} does not clear it"
        assert (needed - 1) / total <= floor, f"floor {floor}: {needed} is more than the minimum"


def test_the_latest_start_is_exactly_the_moment_the_floor_slips_away(window: Window) -> None:
    """The deadline is a real boundary, not an estimate: one minute either side of it decides."""
    on_time = drift.floor_reachable(window, [], "2026-01-01T23:00:00Z", 0.90)
    too_late = drift.floor_reachable(window, [], "2026-01-01T23:01:00Z", 0.90)
    assert on_time["reachable"] is True
    assert too_late["reachable"] is False


def test_samples_already_taken_count_towards_the_floor(window: Window, tmp_path: Path) -> None:
    """The deadline moves later as samples land — otherwise it is a countdown, not a measurement."""
    samples = _full_coverage_log(tmp_path, drifts=False)[:48]
    with_samples = drift.floor_reachable(window, samples, "2026-01-03T00:00:00Z", 0.90)
    without = drift.floor_reachable(window, [], "2026-01-03T00:00:00Z", 0.90)
    assert with_samples["samples_reachable"] == 48
    assert with_samples["ceiling"] > without["ceiling"]


def test_an_unreachable_probe_writes_a_sample_but_it_does_not_count(
    window: Window, tmp_path: Path
) -> None:
    """`coverage` counts only reachable samples, and so does this — a probe that could not see the
    cluster observed nothing, however faithfully it recorded that."""
    path = tmp_path / "unreachable.jsonl"
    path.write_text(
        "".join(
            json.dumps({"ts": f"2026-01-01T{at:02d}:00:00Z", "reachable": False, "subjects": {}}) + "\n"
            for at in range(24)
        ),
        encoding="utf-8",
    )
    reach = drift.floor_reachable(window, drift.load_samples(path), "2026-01-02T00:00:00Z", 0.90)
    assert reach["samples_reachable"] == 0
    assert reach["reachable"] is False


def test_the_live_instrument_cannot_reach_the_live_protocols_floor() -> None:
    """**The finding build ticket 70's audit exists to surface, pinned to a fixed clock.**

    Not a hypothetical. The committed window opened 2026-08-07 declaring an hourly cadence; the
    committed log holds three samples against the 211 that cadence owed by 2026-08-15, because
    `window.yaml`'s `operation.crontab` is a documented line nobody installed. From
    2026-08-16T05:00Z onward no probing schedule can bring the continuous-state branch above its
    own pre-registered floor, so build ticket 65's primary branch closes `unmeasured` whatever
    happens next.

    Pinned to a fixed `now` so it records the finding permanently rather than re-deciding it
    against the wall clock. The wall-clock half is the harness guard
    `flux_coverage_floor_is_still_reachable`, which is where a live estate gets told in time.
    """
    live_window, live_floor = Window.load(), Protocol.load().minimum_coverage
    samples = drift.load_samples()

    before = drift.floor_reachable(live_window, samples, "2026-08-16T05:00:00Z", live_floor)
    after = drift.floor_reachable(live_window, samples, "2026-08-16T06:00:00Z", live_floor)
    assert before["reachable"] is True, "the finding is dated from the wrong side of the deadline"
    assert after["reachable"] is False
    assert after["ceiling"] < live_floor
