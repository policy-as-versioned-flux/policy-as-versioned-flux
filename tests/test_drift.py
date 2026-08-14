"""The Flux drift reduction (build ticket 64).

Seam 2: the claims here are numerical and structural — which transitions are drift, what the
interval is, and what coverage a sparse log supports. The instrument itself is a shell probe
against a live cluster and is not simulated: what is tested is the arithmetic that turns its log
into an answer, because that is where a wrong number would look right.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from twin import drift
from twin.drift import DriftError, ForcedCampaign, Window

WINDOW = """\
schema: drift.window/v1
version: 1
question: Does a deployed control diverge between deploys?
window: {opens: '2026-01-01', closes: '2026-01-11', days: 10}
cadence: {every_minutes: 60, tolerance_minutes: 15}
subjects:
  - {id: live-version, repository: r, cluster: c, control: x, desired_from: a, observed_from: b}
  - {id: nist-pin, repository: r, cluster: c, control: y, desired_from: a, observed_from: b}
outcomes_that_would_falsify_the_spec:
  - No drift event across the full window at coverage above 90%.
drift_event: {definition: d, deploy_marker: m, interval: i}
operation: {owner: A Named Human, runner: cron}
"""


@pytest.fixture()
def window(tmp_path: Path) -> Window:
    path = tmp_path / "window.yaml"
    path.write_text(WINDOW, encoding="utf-8")
    return Window.load(path)


def _log(tmp_path: Path, *samples: dict) -> list[dict]:
    path = tmp_path / "samples.jsonl"
    path.write_text("".join(json.dumps(s) + "\n" for s in samples), encoding="utf-8")
    return drift.load_samples(path)


def _sample(ts: str, revision: str = "r1", **subjects: str) -> dict:
    return {"ts": ts, "reachable": True, "revision": revision,
            "subjects": {"live-version": "1.0.0", "nist-pin": "1.0.0", **subjects}}


# -- what counts as drift --------------------------------------------------------------------


def test_a_change_with_no_deploy_between_is_a_drift_event(window: Window, tmp_path: Path) -> None:
    samples = _log(
        tmp_path,
        _sample("2026-01-02T00:00:00Z", "r0"),
        _sample("2026-01-02T01:00:00Z", "r1"),                       # a deploy
        _sample("2026-01-02T02:00:00Z", "r1"),
        _sample("2026-01-02T03:00:00Z", "r1", **{"live-version": "9.9.9"}),
    )
    found = drift.events(window, samples)
    assert [(e["subject"], e["from"], e["to"]) for e in found] == [("live-version", "1.0.0", "9.9.9")]
    # Two hours from the deploy that preceded it, which is the number the whole ticket exists for.
    assert found[0]["since_deploy_seconds"] == 7200
    assert found[0]["last_deploy"] == "2026-01-02T01:00:00Z"


def test_a_change_that_arrives_with_a_deploy_is_a_deploy(window: Window, tmp_path: Path) -> None:
    """The distinction the spec's claim rests on: a deploy-time attestation would catch this."""
    samples = _log(
        tmp_path,
        _sample("2026-01-02T00:00:00Z", "r1"),
        _sample("2026-01-02T01:00:00Z", "r2", **{"live-version": "2.0.0"}),
    )
    assert drift.events(window, samples) == []


def test_a_deleted_control_is_total_drift_not_an_unchanged_one(window: Window, tmp_path: Path) -> None:
    samples = _log(
        tmp_path,
        _sample("2026-01-02T00:00:00Z"),
        _sample("2026-01-02T01:00:00Z", **{"nist-pin": ""}),
    )
    found = drift.events(window, samples)
    assert [(e["subject"], e["deleted"]) for e in found] == [("nist-pin", True)]


def test_a_change_across_an_unobserved_gap_is_not_counted_as_drift(window: Window, tmp_path: Path) -> None:
    """A deploy could have happened and been reverted inside the gap, so this is coverage."""
    samples = _log(
        tmp_path,
        _sample("2026-01-02T00:00:00Z"),
        _sample("2026-01-04T00:00:00Z", **{"live-version": "9.9.9"}),
    )
    assert drift.events(window, samples) == []
    holes = drift.coverage(window, samples, "2026-01-05T00:00:00Z")["gaps_wider_than_the_cadence"]
    assert any(hole["hours"] == 48.0 for hole in holes)


def test_an_unreachable_sample_is_not_a_comparison(window: Window, tmp_path: Path) -> None:
    """The cluster said nothing. Bridging across it would let a deploy hide inside the outage."""
    samples = _log(
        tmp_path,
        _sample("2026-01-02T00:00:00Z"),
        {"ts": "2026-01-02T00:30:00Z", "reachable": False, "reason": "no cluster", "subjects": {}},
        _sample("2026-01-02T01:00:00Z", **{"live-version": "9.9.9"}),
    )
    found = drift.events(window, samples)
    assert [e["subject"] for e in found] == ["live-version"]
    assert drift.coverage(window, samples, "2026-01-02T02:00:00Z")["samples_reachable"] == 2


# -- coverage, which is what the answer is worth ---------------------------------------------


def test_an_instrument_that_stopped_shows_up_as_a_gap(window: Window, tmp_path: Path) -> None:
    """The failure this module exists to refuse: silence reading as a stable estate."""
    samples = _log(tmp_path, _sample("2026-01-01T01:00:00Z"), _sample("2026-01-01T02:00:00Z"))
    cover = drift.coverage(window, samples, "2026-01-06T00:00:00Z")
    assert cover["sampled_fraction"] < 0.02
    assert cover["gaps_wider_than_the_cadence"][-1]["hours"] == pytest.approx(118.0)


def test_an_entirely_unsampled_window_is_one_long_gap(window: Window, tmp_path: Path) -> None:
    cover = drift.coverage(window, _log(tmp_path), "2026-01-03T00:00:00Z")
    assert cover["samples_taken"] == 0 and cover["sampled_fraction"] == 0.0
    assert cover["gaps_wider_than_the_cadence"] == [
        {"from": "2026-01-01T00:00:00+00:00", "to": "2026-01-03T00:00:00+00:00", "hours": 48.0}
    ]


def test_coverage_does_not_run_past_the_declared_close(window: Window, tmp_path: Path) -> None:
    """The window closes when it said it would, whatever the clock says afterwards."""
    cover = drift.coverage(window, _log(tmp_path), "2027-01-01T00:00:00Z")
    assert cover["window_elapsed_fraction"] == 1.0


# -- the pre-registration refuses to be a demonstration ---------------------------------------


def test_a_window_naming_no_falsifier_does_not_load(tmp_path: Path) -> None:
    path = tmp_path / "window.yaml"
    path.write_text(WINDOW.replace("outcomes_that_would_falsify_the_spec:", "unused:"), encoding="utf-8")
    with pytest.raises(DriftError, match="falsify"):
        Window.load(path)


def test_a_window_naming_no_owner_does_not_load(tmp_path: Path) -> None:
    path = tmp_path / "window.yaml"
    path.write_text(WINDOW.replace("owner: A Named Human", "note: nobody"), encoding="utf-8")
    with pytest.raises(DriftError, match="names no operator"):
        Window.load(path)


def test_the_committed_window_and_preconditions_load(tmp_path: Path) -> None:
    """The real pre-registration, not a fixture of one."""
    committed = Window.load()
    assert committed.subjects and committed.falsifiers and committed.owner
    body = drift.report("2026-08-07T12:00:00Z")
    assert body["verdict"] is None and body["verdict_lands_at"] == "build ticket 65"
    assert [p["id"] for p in body["open_preconditions"]] == ["org-actions-may-not-create-prs"]


# -- the forced-drift latency campaign (build ticket 78) --------------------------------------

FORCED_CAMPAIGN = """\
schema: drift.forced_campaign/v1
version: 1
question: How fast do Flux and the probe catch a forced, plausible operator action?
not_organic_drift_evidence: >-
  Excluded from build ticket 65's organic-drift tally by construction: written to a separate log.
resolution: {sample_every_seconds: 15, window_minutes: 30}
samples: {path: forced-campaign-samples.jsonl}
trials:
  - id: configmap-edit-outside-gitops
    action: kubectl patch cm x
    undo: kubectl patch cm x back
  - id: scale-left-unreverted
    action: kubectl scale deploy x --replicas=0
    undo: kubectl scale deploy x --replicas=1
  - id: kustomization-suspended-left-suspended
    action: kubectl patch kustomization x suspend=true
    undo: kubectl patch kustomization x suspend=false
  - id: resource-deleted-outright
    action: kubectl delete cm y
    undo: wait for Flux to recreate it
operation: {owner: A Named Human}
"""


def _write_campaign(tmp_path: Path, text: str = FORCED_CAMPAIGN) -> Path:
    path = tmp_path / "forced-campaign.yaml"
    path.write_text(text, encoding="utf-8")
    return path


def test_a_forced_campaign_with_all_four_trials_loads(tmp_path: Path) -> None:
    campaign = ForcedCampaign.load(_write_campaign(tmp_path))
    assert campaign.trials == (
        "configmap-edit-outside-gitops",
        "scale-left-unreverted",
        "kustomization-suspended-left-suspended",
        "resource-deleted-outright",
    )
    assert campaign.sample_every_seconds == 15
    assert campaign.window_minutes == 30
    assert campaign.samples_path.name == "forced-campaign-samples.jsonl"
    assert campaign.owner == "A Named Human"


def test_a_forced_campaign_missing_a_trial_does_not_load(tmp_path: Path) -> None:
    text = FORCED_CAMPAIGN.replace(
        "  - id: resource-deleted-outright\n"
        "    action: kubectl delete cm y\n"
        "    undo: wait for Flux to recreate it\n",
        "",
    )
    with pytest.raises(DriftError, match="exactly the four trials"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_a_trial_with_no_undo_does_not_load(tmp_path: Path) -> None:
    text = FORCED_CAMPAIGN.replace("    undo: kubectl patch cm x back\n", "")
    with pytest.raises(DriftError, match="no undo step"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_a_trial_with_no_action_does_not_load(tmp_path: Path) -> None:
    text = FORCED_CAMPAIGN.replace("    action: kubectl patch cm x\n", "")
    with pytest.raises(DriftError, match="names no action"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_a_campaign_naming_no_owner_does_not_load(tmp_path: Path) -> None:
    text = FORCED_CAMPAIGN.replace("operation: {owner: A Named Human}", "operation: {}")
    with pytest.raises(DriftError, match="names no operator"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_a_campaign_silent_on_organic_evidence_does_not_load(tmp_path: Path) -> None:
    text = FORCED_CAMPAIGN.replace(
        "not_organic_drift_evidence: >-\n"
        "  Excluded from build ticket 65's organic-drift tally by construction: written to a "
        "separate log.\n",
        "",
    )
    with pytest.raises(DriftError, match="not evidence for the organic-drift verdict"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_a_campaign_reusing_the_organic_samples_path_does_not_load(tmp_path: Path) -> None:
    """Forcing the very thing build ticket 64 counts must never land in its own log."""
    text = FORCED_CAMPAIGN.replace(
        "samples: {path: forced-campaign-samples.jsonl}", "samples: {path: samples.jsonl}"
    )
    with pytest.raises(DriftError, match="organic log"):
        ForcedCampaign.load(_write_campaign(tmp_path, text))


def test_the_committed_forced_campaign_loads(tmp_path: Path) -> None:
    """The real pre-registration, not a fixture of one."""
    committed = ForcedCampaign.load()
    assert len(committed.trials) == 4
    assert committed.owner and committed.not_organic_drift_evidence
    assert committed.samples_path != drift.SAMPLES_PATH


def test_the_orchestrator_script_runs_exactly_the_declared_trials() -> None:
    """`forced-campaign.sh` is the executable form of the pre-registration; the two must agree.

    Bash cannot parse YAML without a new dependency, so the script hardcodes its own trial
    definitions — this is the regression test that catches the two silently drifting apart,
    standing in for the parser this repository deliberately does not add.
    """
    script = (drift.FORCED_CAMPAIGN_PATH.parent / "forced-campaign.sh").read_text(encoding="utf-8")
    for trial_id in drift.REQUIRED_FORCED_TRIALS:
        assert f'run_trial "{trial_id}"' in script, f"forced-campaign.sh never runs {trial_id!r}"
