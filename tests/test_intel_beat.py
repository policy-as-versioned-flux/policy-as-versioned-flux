"""The live, unresolved, pinned forecast (build ticket 75; decision tickets 06, 22; spec story 92).

The most honest artefact in the demo: a genuine forward forecast where the twin does not know the
answer either. Emitted through `twin sweep` — the scheduled production line, no scenario named at
run time — never hand-built. Pinned, signed, and explicitly unscoreable: no outcome exists for
this proposition, none will ever be authored by this fixture, and the artefact says so itself,
with the resolution window and the checking procedure, rather than a placeholder score.
"""

from __future__ import annotations

import io
import json
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from typing import Iterator

import pytest

from twin import fixtures, invariants, verbs
from twin.artefact import digest_of_file
from twin.attest import SUFFIX as ATTEST_SUFFIX
from twin.cli import main
from twin.grades import Capabilities
from twin.invariants import PASS
from twin.model import Overlay
from twin.repo import ModelRepo
from twin.verbs import CAPS_RUN

ORG = fixtures.INTEL_ORG
SCENARIO = "does-the-14a-bet-land-a-named-customer"
PROPOSITION = "a-leading-edge-foundry-node-lands-a-named-external-customer"

BEAT = Path(__file__).resolve().parents[1] / "twin" / "beat-intel.sh"


@pytest.fixture(scope="session")
def beat(
    tmp_path_factory: pytest.TempPathFactory, monkeypatch_session_signing_key: None,
) -> dict[str, Path]:
    """The beat's own artefacts, produced through the CLI exactly as the script produces them.

    Session-scoped: one fixture repository, one sweep, one standalone run. The script itself is
    run by CI rather than by pytest, the same reason `twin/demo.sh` and the other beat scripts are
    — a shell surface is checked by running it, and running it twice per suite buys nothing.
    """
    work = tmp_path_factory.mktemp("intel-beat")
    repo = fixtures.build_intel_org(work / "repo")
    out = work / "artefacts"
    out.mkdir()

    paths = {name: out / f"{name}.json" for name in ("sweep", "run")}
    assert main(["sweep", "--repo", str(repo), "--out", str(paths["sweep"])]) == 0
    assert main([
        "run", "--repo", str(repo), "--org", ORG, "--scenario", SCENARIO,
        "--regime", "as-consumed", "--out", str(paths["run"]),
    ]) == 0
    return {"repo": repo, **paths}


@pytest.fixture(scope="session")
def monkeypatch_session_signing_key(
    tmp_path_factory: pytest.TempPathFactory,
) -> Iterator[None]:
    """A session-scoped signing key. AC 1 asks for signed, not merely pinned.

    `pytest.MonkeyPatch` itself is function-scoped; this fixture uses its context-manager form so
    the key is set for the whole session's one `beat` build and undone after, the same lifetime the
    session-scoped `beat` fixture needs.
    """
    with pytest.MonkeyPatch.context() as mp:
        mp.setenv("TWIN_SIGNING_KEY", "intel-beat-test-key")
        yield


def _body(path: Path) -> dict:
    return json.loads(Path(path).read_bytes())["body"]


def _sidecar(path: Path) -> dict:
    return json.loads(Path(f"{path}{ATTEST_SUFFIX}").read_bytes())


# -- AC 1: pinned and signed, before any resolution -----------------------------------------------


def test_the_sweep_artefact_is_derived_pinned_and_agent_signed(beat: dict[str, Path]) -> None:
    sidecar = _sidecar(beat["sweep"])
    assert sidecar["mark"] == "derived"
    assert sidecar["signature_status"] is None, "signed: status is None exactly when signed"
    assert sidecar["agent_signature"], "no agent signature present"
    assert not sidecar["human_involvement"]["present"], "a derived artefact should carry no human signature"

    envelope = json.loads(beat["sweep"].read_bytes())["envelope"]
    assert envelope["pins"]["repos"], "the sweep artefact carries no pins"


def test_the_standalone_run_is_also_signed_and_reproduces_from_its_pins(beat: dict[str, Path]) -> None:
    sidecar = _sidecar(beat["run"])
    assert sidecar["signature_status"] is None
    assert sidecar["agent_signature"]

    out = io.StringIO()
    with redirect_stdout(out), redirect_stderr(out):
        code = main(["verify", str(beat["run"]), "--repo", str(beat["repo"])])
    assert code == 0, out.getvalue()
    assert "REPRODUCES" in out.getvalue()


# -- AC 4: emitted through the scheduled production line, not hand-made ---------------------------


def test_the_sweep_embedded_forecast_is_byte_identical_to_a_standalone_run(beat: dict[str, Path]) -> None:
    """Nothing here was hand-made for the demo.

    `twin sweep` names no scenario at run time; a standalone `twin run` on the identical scenario
    is the independent computation this test checks the scheduled one against, byte for byte.
    """
    sweep = _body(beat["sweep"])
    assert len(sweep["executions"]) == 1 and not sweep["failures"]
    execution = sweep["executions"][0]
    assert execution["org"] == ORG and execution["scenario"] == SCENARIO

    assert execution["forecast_bundle"]["sha256"] == digest_of_file(beat["run"])


def test_the_forecast_is_plural_and_the_ensemble_genuinely_disagrees(beat: dict[str, Path]) -> None:
    forecasts = _body(beat["run"])["forecasts"]
    assert len(forecasts) >= 2, "no ensemble to spread across"
    distinct = {f["probability"] for f in forecasts}
    assert len(distinct) >= 2, f"all {len(forecasts)} forecasts agree: {distinct}"


# -- AC 2 + AC 3: explicitly unscoreable, with the resolution date and checking procedure ----------


def test_the_emitted_body_names_its_own_unscoreability_and_checking_procedure(
    beat: dict[str, Path],
) -> None:
    """Published in the artefact's own body, never only in the fixture source or a script's prose.

    Build ticket 74's own review found prose that explained a caveat only in a script's `echo`
    lines, never reaching the artefact that gets read, shared and attested. This reads the
    statement back out of the emitted `forecast-bundle`'s own `scenario.question`.
    """
    question = _body(beat["run"])["scenario"]["question"].lower()
    for needle in ("unscoreable", "second half of 2026", "first half of 2027", "twin score"):
        assert needle in question, f"{needle!r} missing from the emitted question"


def test_the_proposition_declares_a_resolution_date(beat: dict[str, Path]) -> None:
    overlay = Overlay.load(ModelRepo.open(beat["repo"]), ORG)
    proposition = overlay.proposition(PROPOSITION)
    assert proposition["resolves_on"] == "2027-06-30"


def test_the_resolution_date_is_published_in_the_emitted_artefact_too(
    beat: dict[str, Path],
) -> None:
    """Held to the same standard as the unscoreability check above: read back from the emitted
    body, not only from the source overlay a reader holding just the artefact cannot see.

    `verbs.run` already copies the scenario's `horizon` into `body.scenario.horizon` for every
    fixture in this file — unmodified by this ticket — so the date the scenario declares and the
    date a reader of the artefact sees are asserted to be the identical string, not merely both
    present somewhere.
    """
    assert _body(beat["run"])["scenario"]["horizon"] == "2027-06-30"


def test_no_outcome_is_authored_and_score_refuses_and_names_the_absence(
    beat: dict[str, Path],
) -> None:
    """The permanent half of AC 2 — structural, not narrated.

    Unlike Netflix (no outcome because the story is over and scoring it would be recital), this
    org carries no outcome because the story has not happened yet. `twin score` refuses either way,
    identically, and the reason each carries is different — this fixture's own scenario says so.
    """
    overlay = Overlay.load(ModelRepo.open(beat["repo"]), ORG)
    assert not overlay.outcomes

    out = io.StringIO()
    # Written outside the fixture repository: a path inside it would dirty the working tree of the
    # very model this test reads, on the day `twin score` stops refusing.
    with redirect_stdout(out), redirect_stderr(out):
        code = main([
            "score", "--repo", str(beat["repo"]), "--org", ORG, "--forecast", str(beat["run"]),
            "--outcome", "any-outcome-at-all", "--out", str(beat["repo"].parent / "never.json"),
        ])
    assert code != 0
    assert "any-outcome-at-all" in out.getvalue()
    assert "have: none" in out.getvalue()
    assert not (beat["repo"].parent / "never.json").exists(), "a score card was written despite refusing"


# -- AC 6: depth grade declared as a computed checklist --------------------------------------------


def test_the_forecast_carries_a_computed_depth_grade(beat: dict[str, Path]) -> None:
    depth = json.loads(beat["run"].read_bytes())["envelope"]["depth"]
    expected = Capabilities.load().depth_block(CAPS_RUN)
    assert depth == expected


# -- decision ticket 08 AC 5: the real causal claim, exercised (build ticket 81) -------------------


def test_the_real_euv_causal_edge_composes_to_a_priced_elasticity(
    beat: dict[str, Path], caps: Capabilities
) -> None:
    """EUV delay -> process-node slip, on the real spine — the Intel half of decision ticket 08
    AC 5, exercised the same way as the Netflix co-flagship's Qwikster->churn edge: a real
    propagation, not a description of one. See `twin/fixtures.py`'s own `_INTEL_BASE` for the
    dated, cited evidence a grade-2 elasticity rests on."""
    repo = ModelRepo.open(beat["repo"])
    artefact = verbs.propagate(
        repo, caps, ORG, "euv-lithography",
        verbs.command_for("propagate", org=ORG, origin="euv-lithography"),
    )
    reached = {r["component"]: r for r in artefact.body["reached"]}
    assert "leading-edge-foundry-node" in reached, "the causal edge did not compose at all"
    primary = next(p for p in reached["leading-edge-foundry-node"]["paths"] if p["primary"])
    assert primary["sign"] == "negative"
    assert primary["worst_evidence_grade"] == 2
    assert not primary["directional_only"], (
        "grade 2 is inside the pricing threshold — a real elasticity, not a direction-only claim"
    )


# -- AC 5: extends the invariant suite, and the new guard passes live ------------------------------


def test_the_new_harness_guard_passes(tmp_path: Path) -> None:
    results, ok = invariants.run(
        only=["intel_forecast_is_pinned_signed_and_names_its_own_unscoreability"], tmp=tmp_path,
    )
    assert len(results) == 1
    assert results[0].status == PASS, results[0].detail
    assert ok
