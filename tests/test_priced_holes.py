"""verify/priced-holes — the pure arithmetic and the since rule, at the grader's own seam.

The grader re-derives what composition.py computes (ticket 38): the EOL ramp from `since` to
`as_of`, the workload share of the uncaged residual bounded at the whole residual, and the rule
that `since` is read off the first signed tag naming the namespace and survives a reopen. These
tests pin those down so a change to either side shows up here before the gate.
"""

from __future__ import annotations

import importlib.util
import math
import os
import subprocess
from pathlib import Path
from types import ModuleType

import pytest
import yaml

GRADER = Path(__file__).resolve().parent.parent / "verify" / "priced-holes" / "priced_holes.py"


@pytest.fixture(scope="module")
def grader() -> ModuleType:
    spec = importlib.util.spec_from_file_location("priced_holes", GRADER)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# -- the ramp ----------------------------------------------------------------------------------


def test_ramp_is_one_up_to_since_and_where_a_date_is_unknown(grader: ModuleType) -> None:
    assert grader.expected_ramp("2026-08-25", "2026-08-25") == 1.0
    assert grader.expected_ramp("2026-08-25", "2026-08-01") == 1.0
    assert grader.expected_ramp(None, "2026-08-28") == 1.0
    assert grader.expected_ramp("2026-08-25", None) == 1.0


def test_ramp_grows_one_x_per_year_and_caps_at_four(grader: ModuleType) -> None:
    three_days = grader.expected_ramp("2026-08-25", "2026-08-28")
    assert math.isclose(three_days, 1.0 + 3 / 365.0)
    one_year = grader.expected_ramp("2025-10-31", "2026-10-31")
    two_years = grader.expected_ramp("2025-10-31", "2027-10-31")
    assert 1.0 < three_days < one_year < two_years
    assert grader.expected_ramp("2020-01-01", "2030-01-01") == 5.0


# -- the share and the bound -------------------------------------------------------------------


def test_amount_is_the_workload_share_of_the_residual(grader: ModuleType) -> None:
    assert grader.expected_amount(1000.0, 1, 4, 1.0) == (250.0, False)
    assert grader.expected_amount(1000.0, 4, 4, 1.0) == (1000.0, False)


def test_amount_is_bounded_at_the_whole_residual(grader: ModuleType) -> None:
    amount, bounded = grader.expected_amount(1000.0, 3, 4, 2.0)   # 1500 raw
    assert amount == 1000.0 and bounded is True


def test_nothing_inside_and_no_residual_price_nothing(grader: ModuleType) -> None:
    assert grader.expected_amount(1000.0, 0, 0, 3.0) == (0.0, False)
    assert grader.expected_amount(None, 2, 4, 1.0) == (None, False)


# -- since-preservation and the document checks -------------------------------------------------


def _lines(grader: ModuleType, doc: dict, ctx: dict) -> list[str]:
    grader.LINES.clear()
    grader.check_doc(doc, ctx)
    return list(grader.LINES)


def test_a_reopened_namespace_keeps_the_since_the_first_signed_tag_carries(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["status"] = "new"
    doc["deltas"].append({"kind": "new-ungoverned-namespace", "namespace": "reset",
                          "perspective": "driftwood", "currency": "GBP",
                          "amount": doc["ungoverned"][0]["price"]["amount"], "detail": ""})
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_a_since_no_signed_tag_carries_is_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["price"]["since"] = "2026-08-01"
    assert "FAIL" in _lines(grader, doc, ctx)


def test_a_null_since_needs_its_limit_named(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    price = doc["ungoverned"][0]["price"]
    price.update(since=None, ramp=1.0, amount=150.0, limits=[])
    ctx["since"] = {"reset": None}
    assert "FAIL" in _lines(grader, doc, ctx)
    price["limits"] = ["no signed composed artefact names reset: ramp held at 1.0"]
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_an_amount_above_the_residual_is_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["ungoverned"][0]["price"]["amount"] = 301.0
    assert "FAIL" in _lines(grader, doc, ctx)


def test_the_deleted_refusals_are_observed_false_and_the_old_shape_is_a_skip(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["refusals"] = [{"kind": "baseline-widening", "subject": "MODERATE -> HIGH"}]
    assert "FAIL" in _lines(grader, doc, ctx)
    doc, ctx = grader._good()
    doc.pop("deltas")
    lines = _lines(grader, doc, ctx)
    assert "SKIP" in lines and "FAIL" not in lines


@pytest.mark.parametrize("kind", ["new-untagged-pin", "closed-untagged-pin"])
def test_an_untagged_pin_delta_is_a_kind_this_check_admits(grader: ModuleType, kind: str) -> None:
    """Ticket 69's own deltas. DELTA_KINDS is a whitelist, so the moment an
    adopter composed an untagged pin this check failed on the delta reporting
    it -- the gate going red on the rule it was built to grade."""
    doc, ctx = grader._good()
    doc["deltas"].append({"kind": kind, "source": "insurer", "name": "quote-driftwood",
                          "version": "v2", "perspective": "driftwood", "currency": "GBP",
                          "amount": 113403.3, "priced_by": "the premium the pin books",
                          "detail": ""})
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_a_kind_the_whitelist_does_not_name_is_still_observed_false(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    doc["deltas"].append({"kind": "reopened-untagged-pin", "source": "insurer",
                          "perspective": "driftwood", "currency": "GBP", "amount": 1.0,
                          "detail": ""})
    assert "FAIL" in _lines(grader, doc, ctx)


@pytest.mark.parametrize("kind", ["removed-control", "baseline-narrowing", "withdrawn-control"])
def test_a_priced_removal_delta_is_a_kind_this_check_admits(grader: ModuleType, kind: str) -> None:
    """Eco-system ticket 124: ADR-0026 point 5 prices a removal as a
    `removed-control` delta beside one `baseline-narrowing` summary. An
    adopter that narrows must not fail this check on the deltas that report
    it. Eco-system ticket 123 adds `withdrawn-control`: the regulator's
    withdrawal, which is not the adopter's removal."""
    doc, ctx = grader._good()
    doc["deltas"].append({"kind": kind, "source": "nist", "control_id": "ac-11",
                          "subject": "MODERATE -> LOW", "perspective": "driftwood",
                          "currency": "GBP", "amount": None, "priced_by": None, "detail": ""})
    assert "FAIL" not in _lines(grader, doc, ctx)


def test_a_source_that_still_refuses_a_removal_fails(grader: ModuleType) -> None:
    """Eco-system ticket 124 adds `removed-control` to the gone set: a refusal
    literal of that kind fails, a delta literal of the same kind passes."""
    base = ('{"kind": "missing-instrument", "needs_composition": True}\n'
            'def compute_deltas\ndeltas\ndef ungoverned_price\neol_ramp\n')
    grader.LINES.clear()
    grader.check_source(base + '{"kind": "removed-control", "needs_composition": True}\n')
    assert "FAIL" in grader.LINES, grader.LINES
    grader.LINES.clear()
    grader.check_source(base + 'deltas.append({"kind": "removed-control", "source": s})\n')
    assert "FAIL" not in grader.LINES, grader.LINES
    grader.LINES.clear()


def test_a_schema_that_still_says_a_removal_refuses_fails(grader: ModuleType) -> None:
    """The party schema's `overlay.controls` sentence is rewritten by ticket
    124. The ticket 38 sentence it kept ("May only grow ... an exemption by
    another name") fails; the priced one passes."""
    lead = "bare or `party:id`; an addition is a priced hole, never refused. "
    grader.LINES.clear()
    grader.check_schema({"properties": {"overlay": {"properties": {"controls": {
        "description": lead + "May only grow: a composition still refuses on any id that "
                              "leaves the set, because a removal is an exemption by another name."}}}}})
    assert "FAIL" in grader.LINES, grader.LINES
    grader.LINES.clear()
    grader.check_schema({"properties": {"overlay": {"properties": {"controls": {
        "description": lead + "A removal is priced, never refused: an id that leaves the set "
                              "prints as a `removed-control` delta."}}}}})
    assert "FAIL" not in grader.LINES, grader.LINES
    grader.LINES.clear()

# -- eco-system ticket 119: silence buys no exemption from the price ----------------------------


def _write(path: Path, *docs: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump_all(list(docs)))


def test_the_recount_prices_an_unlabelled_namespace_and_skips_only_the_platform_substrate(
        grader: ModuleType, tmp_path: Path) -> None:
    """The grader's own walk follows the rule composition.py follows since ticket 119. A Namespace
    with no label, or one only a workload names, is ungoverned. The substrate is what the
    platform declares `infra` in its own tree. An adopter's copy of that label buys nothing."""
    ns = lambda name, labels: {"apiVersion": "v1", "kind": "Namespace",  # noqa: E731
                               "metadata": {"name": name, "labels": labels}}
    job = lambda name, where: {"apiVersion": "batch/v1", "kind": "Job",  # noqa: E731
                               "metadata": {"name": name, "namespace": where}}
    estate = tmp_path / "estate"
    _write(estate / "platform" / "engine" / "namespaces.yaml",
           ns("kube-system", {"posture.acme.io/tier": "infra"}),
           ns("flux-system", {"posture.acme.io/tier": "infra"}), ns("access", {}))
    assert grader._substrate(str(estate)) == {"kube-system", "flux-system"}
    repo = estate / "adopter"
    _write(repo / "gitops" / "ns.yaml",
           ns("home", {"policy-as-versioned.dev/institution": "a", "policy-as-versioned.dev/governed": "true"}),
           ns("side", {}), ns("mine", {"posture.acme.io/tier": "infra"}))
    _write(repo / "gitops" / "jobs.yaml", job("a", "home"), job("b", "side"), job("c", "elsewhere"),
           job("d", "flux-system"))
    institution, workloads, ungoverned = grader._namespace_facts(str(repo), {"kube-system", "flux-system"})
    assert institution == {"home", "side", "mine", "elsewhere"}, institution
    assert workloads == {"home": 1, "side": 1, "elsewhere": 1, "flux-system": 1}, workloads
    assert ungoverned == {"side", "mine", "elsewhere"}, ungoverned


def test_the_substrate_is_unknown_without_the_platform_declaration(grader: ModuleType, tmp_path: Path) -> None:
    assert grader._substrate(str(tmp_path)) is None


def test_an_ungoverned_namespace_the_evidence_leaves_unpriced_is_observed_false(
        grader: ModuleType, capsys: pytest.CaptureFixture[str]) -> None:
    """tuppence's shape: the repo walk finds `openbao` ungoverned, and the committed evidence,
    composed before ticket 119, prices only `tuppence-reset`."""
    doc, ctx = grader._good()
    ctx["ungoverned"] = {"reset"}
    assert "FAIL" not in _lines(grader, doc, ctx)
    capsys.readouterr()
    ctx["ungoverned"] = {"reset", "openbao"}
    assert "FAIL" in _lines(grader, doc, ctx)
    printed = [line for line in capsys.readouterr().out.splitlines() if line.startswith("FAIL:")]
    assert len(printed) == 1 and "openbao" in printed[0], printed


def test_a_regime_line_the_catalogue_withdrew_reads_withdrawn(grader: ModuleType) -> None:
    """Eco-system ticket 123 item 2: a weight that still names a control the pinned
    catalogue withdrew keeps its line, and the line reads `withdrawn`."""
    doc, ctx = grader._good()
    entry = next(e for e in doc["prices"] if e.get("holes"))
    entry["holes"][1]["status"] = "withdrawn"
    assert "FAIL" not in _lines(grader, doc, ctx)
    entry["holes"][1]["status"] = "retired"
    assert "FAIL" in _lines(grader, doc, ctx)


# -- eco-system ticket 122: the age follows the workloads, and a close says why ------------------


def _repo(tmp_path: Path, name: str) -> Path:
    """A throwaway adopter repo. Its git runs no hooks, so the fixture calls no network."""
    repo = tmp_path / name
    repo.mkdir()
    _git(repo, "init", "-q")
    return repo


def _git(repo: Path, *args: str, date: str | None = None) -> None:
    hooks = repo.parent / "no-hooks"
    hooks.mkdir(exist_ok=True)
    env = {**os.environ, "GIT_AUTHOR_NAME": "fixture", "GIT_AUTHOR_EMAIL": "fixture@example.invalid",
           "GIT_COMMITTER_NAME": "fixture", "GIT_COMMITTER_EMAIL": "fixture@example.invalid"}
    if date:
        env["GIT_COMMITTER_DATE"] = env["GIT_AUTHOR_DATE"] = f"{date}T12:00:00+00:00"
    subprocess.run(["git", "-c", f"core.hooksPath={hooks}", "-c", "commit.gpgSign=false",
                    "-c", "tag.gpgSign=false", "-C", str(repo), *args],
                   check=True, capture_output=True, env=env)


def _deploy(name: str, where: str) -> dict:
    return {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": name, "namespace": where}}


def _cut(repo: Path, tag: str, date: str, ungoverned: list[str]) -> None:
    """Commit a composed header naming `ungoverned` and cut an annotated tag on `date` whose body
    carries a FIXTURE block, the shape the grader reads. It claims no signature."""
    (repo / "composed").mkdir(exist_ok=True)
    (repo / "composed" / "HEADER.yaml").write_text(
        "# advisory header -- policy-as-versioned.dev/composed\n"
        + yaml.safe_dump({"ungoverned-namespaces": ungoverned}))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", tag, date=date)
    _git(repo, "tag", "-a", tag, "-m", f"{tag}\n\n-----BEGIN FIXTURE BLOCK-----\n", date=date)


def test_since_follows_a_workload_that_left_an_aged_namespace(grader: ModuleType, tmp_path: Path) -> None:
    """The grader re-derives ticket 122's rule from the clone's own tags, not from the evidence:
    a Namespace's since is the first signed tag naming it, or naming as ungoverned a Namespace
    that held a workload this one holds now and no longer holds it."""
    repo = _repo(tmp_path, "renamed")
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    _cut(repo, "v1.0.0", "2024-09-01", ["side"])
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side-2"))
    _cut(repo, "v1.1.0", "2026-09-01", ["side-2"])
    assert grader._signed_since(str(repo), ["side-2"]) == {"side-2": "2024-09-01"}

    fresh = _repo(tmp_path, "fresh")
    _write(fresh / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    _cut(fresh, "v1.0.0", "2024-09-01", ["side"])
    _write(fresh / "gitops" / "apps.yaml", _deploy("renamed", "side-2"))
    _cut(fresh, "v1.1.0", "2026-09-01", ["side-2"])
    assert grader._signed_since(str(fresh), ["side-2"]) == {"side-2": "2026-09-01"}


def test_a_copy_beside_the_original_keeps_no_carried_since(grader: ModuleType, tmp_path: Path) -> None:
    repo = _repo(tmp_path, "copy")
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    _cut(repo, "v1.0.0", "2024-09-01", ["side"])
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side"), _deploy("app-0", "other"))
    assert grader._signed_since(str(repo), ["side", "other"]) == {"side": "2024-09-01", "other": None}


def test_a_closed_namespace_must_say_why_and_agree_with_the_recount(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    ctx["institution"] = {"reset", "driftwood", "gone-home"}
    ctx["ungoverned"] = {"reset"}
    closed = {"namespace": "gone-home", "status": "closed", "closed_by": "governed"}
    doc["ungoverned"].append(closed)
    doc["deltas"].append({"kind": "closed-ungoverned-namespace", "namespace": "gone-home",
                          "perspective": "driftwood", "currency": "GBP", "amount": None, "detail": "x"})
    assert "FAIL" not in _lines(grader, doc, ctx)
    closed["closed_by"] = "left-repo"
    assert "FAIL" in _lines(grader, doc, ctx), "left-repo for a Namespace the repo still declares governed"
    ctx["institution"] = {"reset", "driftwood"}
    assert "FAIL" not in _lines(grader, doc, ctx)
    closed["closed_by"] = "governed"
    assert "FAIL" in _lines(grader, doc, ctx), "governed for a Namespace that left the repo"
    closed.pop("closed_by")
    assert "FAIL" in _lines(grader, doc, ctx), "a close that does not say why"


def _governed_dummy(repo: Path, name: str, *workloads: str) -> None:
    """Declare `name` governed and give it inert Deployments of the given names."""
    _write(repo / "gitops" / "dummy.yaml",
           {"apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": name, "labels": {"policy-as-versioned.dev/governed": "true"}}},
           *[_deploy(w, name) for w in workloads])


def test_a_governed_shadow_of_the_old_name_keeps_the_carried_since(grader: ModuleType, tmp_path: Path) -> None:
    """Review round of ticket 122: re-declaring the old name governed, with inert manifests of
    the same kind and name, does not drop the age the rename carried. A governed Namespace pays
    no ramp, so it is not where the workload still sits. The grader needs the recount's
    ungoverned set to say so, as the composer does."""
    repo = _repo(tmp_path, "shadow")
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    _cut(repo, "v1.0.0", "2024-09-01", ["side"])
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side-2"))
    _cut(repo, "v1.1.0", "2026-09-01", ["side-2"])
    _governed_dummy(repo, "side", "app-0")
    _cut(repo, "v1.2.0", "2026-09-02", ["side-2"])
    ungoverned = grader._namespace_facts(str(repo), set())[2]
    assert ungoverned == {"side-2"}, ungoverned
    assert grader._signed_since(str(repo), ["side-2"], ungoverned) == {"side-2": "2024-09-01"}

    once = _repo(tmp_path, "once")
    _write(once / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    _cut(once, "v1.0.0", "2024-09-01", ["side"])
    _write(once / "gitops" / "apps.yaml", _deploy("app-0", "side-2"))
    _governed_dummy(once, "side", "app-0")
    assert grader._signed_since(str(once), ["side-2"], {"side-2"}) == {"side-2": "2024-09-01"}


def test_a_tagged_blob_that_is_not_utf8_is_skipped_as_the_composer_skips_it(
        grader: ModuleType, tmp_path: Path) -> None:
    repo = _repo(tmp_path, "binary")
    _write(repo / "gitops" / "apps.yaml", _deploy("app-0", "side"))
    (repo / "gitops" / "x.yaml").write_bytes(b"kind: Deployment\nmetadata: {name: \xff}\n")
    _cut(repo, "v1.0.0", "2024-09-01", ["side"])
    assert grader._workloads_at(str(repo), "v1.0.0") == {"side": {"Deployment/app-0"}}


def test_a_close_the_recount_cannot_check_leaves_a_skip_line(grader: ModuleType) -> None:
    doc, ctx = grader._good()
    for key in ("institution", "ungoverned"):
        ctx.pop(key)
    doc["ungoverned"].append({"namespace": "gone-home", "status": "closed", "closed_by": "governed"})
    doc["deltas"].append({"kind": "closed-ungoverned-namespace", "namespace": "gone-home",
                          "perspective": "driftwood", "currency": "GBP", "amount": None, "detail": "x"})
    lines = _lines(grader, doc, ctx)
    assert "FAIL" not in lines and "SKIP" in lines, lines
