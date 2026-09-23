"""Eco-system ticket 120: the eighteen loophole candidates against ADR-0026, checked.

Ticket 115 ran three loophole rounds against ADR-0026, "a hole is priced, never refused", and
recorded 18 candidates in `bench/loophole/rounds/adr-0026/round-{1,2,3}/candidates.json`.
ADR-0030 says the tool is a pointer generator: test the place a candidate points at, never its
sentence, and count the survival rate on the candidates as stated. This file is that check.
Every candidate carries a verdict in `VERDICTS`, and each verdict names the test in this file
that holds the fact it rests on. No leg needs a kyverno engine: every place ADR-0026 governs is
in `compose/composition.py`, so every leg drives the platform's own composition.

Three candidates survived.

  1. **Implementing a control moves no price and no tier** (round 1 `overreach-6`). The
     candidate said a widening to controls no weight names earns no credit. The place is real
     and wider than it said: claiming every control the pinned regulator weights name leaves
     the regime entry, the exposure total and every proposed tier exactly where they were.
     The entry is a fixed partition of the regime exposure and a hole's status never reaches
     it. ADR-0026 point 2 and CONTEXT.md's **Hole** say implementing a control reduces the
     regime's price. The code does not.

  2. **The ungoverned ramp keys on a name the adopter chooses** (round 1 `loophole-2`). The
     candidate said an adopter can delay the first signed tag and run unpriced. That is false:
     the cluster runs only a signed tag, and a tag is cut only after `verify` re-renders a
     header that names the Namespace. The place was real: `since` was the first signed tag that
     named the Namespace by name. Renaming an aged ungoverned Namespace restarted its workloads
     at ramp 1.0, and the old name printed a `closed-ungoverned` delta that said it "now carries
     governed" when nothing was governed. Eco-system ticket 122 repaired it: `since` also follows
     the workloads, and a closed entry says whether it was governed or left the repo. The leg
     is now the regression test of that repair.

  3. **A regulator's withdrawal is booked as the adopter's removal** (round 3 `loophole-3`). The
     candidate said the withdrawn hole vanishes unpriced. That is false: it prints. ADR-0026's
     Consequences say a control the regulator withdraws "is not an adopter removal". The code
     cannot tell the two apart. It compares the selected set with the last signed one and books
     every control that left as a `removed-control` in the adopter's name. Until ticket 124 it
     refused; since ticket 124 it composes and prints the delta. Either way it named the
     adopter. Ticket 123 repaired it: a withdrawal now prints as a `withdrawn-control` delta that
     names the regulator's bump, and its leg is a regression test.

When a survivor's ticket repairs its place, the survivor leg here flips, and that ticket owns
the flip.

Counting rule (ticket 116's, applied unchanged): a candidate survives when checking the place it
points at finds a real defect that no earlier survivor or ticket already holds. Where several
candidates point at one place, the earliest by (round, key) is credited and the rest are echoes.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

import pytest
import yaml

HUB = Path(__file__).resolve().parent.parent
ESTATE = HUB / ".estate-clone"
PLATFORM = ESTATE / "platform"
ADOPTERS = ("driftwood", "ludlow", "tuppence")
ROUNDS = HUB / "bench" / "loophole" / "rounds" / "adr-0026"
ADR_0026 = HUB / "docs" / "adr" / "0026-a-hole-is-priced-never-refused-the-claim-keys-on-source-and-id.md"
ADR_0030 = (HUB / "docs" / "adr" /
            "0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md")
GOVERNED = "policy-as-versioned.dev/governed"
INSTITUTION = "policy-as-versioned.dev/institution"
TIER = "posture.acme.io/tier"
PARENTS = ("platform", "nist", "ico", "feeds", "insurer")

# (round, candidate) -> (verdict, the test that holds the fact, the fact in one line).
VERDICTS: dict[tuple[int, str], tuple[str, str, str]] = {
    (1, "loophole-1"): (
        "discard", "test_a_bespoke_hole_is_priced_on_its_own_line_and_moves_no_tier",
        "withdrawing a bespoke control prints a removed-control delta at its own scenario's "
        "residual; a bespoke hole's price reaches no tier, a limit ticket 38 D5 already named"),
    (1, "loophole-2"): (
        "survivor", "test_a_renamed_ungoverned_namespace_keeps_its_ramp_and_the_closed_delta_says_why",
        "delaying the tag is impossible, but since keys on the Namespace name, so a rename restarts "
        "the ramp"),
    (1, "loophole-3"): (
        "discard", "test_a_bespoke_id_never_covers_the_regulators_control_of_the_same_id",
        "(source, id) keeps the regulator's control a hole, and every record names the source"),
    (1, "overreach-4"): (
        "discard", "test_a_removal_composes_and_prints_as_priced_deltas",
        "true on 2026-09-23 and named by ADR-0026 as its known lag; ticket 124 built the priced "
        "removal"),
    (1, "overreach-5"): (
        "discard", "test_an_ungoverned_namespace_is_a_workload_share_while_it_exists_and_moves_no_tier",
        "priced only while its Namespace is in the repo, by its workload share, and it moves no tier"),
    (1, "overreach-6"): (
        "survivor", "test_implementing_every_weighted_control_moves_no_regime_price_and_no_tier",
        "no hole status reaches the regime entry, so implementing even a weighted control moves "
        "nothing"),
    (2, "loophole-1"): (
        "discard", "test_a_narrowing_prices_a_weighted_removal_and_names_each_unweighted_one",
        "an unweighted removal prints a named absence because no pinned weight prices it; a "
        "weighted one prints its price, and the regime entry is the pound either way"),
    (2, "loophole-2"): (
        "discard", "test_a_bespoke_id_never_covers_the_regulators_control_of_the_same_id",
        "a bespoke control never covers a regulator key, so the swap leaves the regulator's hole "
        "open and priced"),
    (2, "loophole-3"): (
        "discard", "test_a_renamed_ungoverned_namespace_keeps_its_ramp_and_the_closed_delta_says_why",
        "true, and the place is round 1 loophole-2's: an echo of that survivor"),
    (2, "overreach-4"): (
        "discard", "test_a_removal_composes_and_prints_as_priced_deltas",
        "a removal is priced as ADR-0026 point 5 chose, and no hole moves a tier, so there is no "
        "tier side effect"),
    (2, "overreach-5"): (
        "discard", "test_a_containment_namespace_is_governed_by_one_label_and_lands_isolated",
        "governing needs one label, no baseline, and an untiered governed Namespace lands isolated"),
    (2, "overreach-6"): (
        "discard", "test_a_mistranscribed_weight_moves_no_regime_price",
        "a wrong weight moves no regime price today; the partition only splits a fixed amount"),
    (3, "loophole-1"): (
        "discard", "test_a_bespoke_hole_is_priced_on_its_own_line_and_moves_no_tier",
        "same facts as round 1 loophole-1: the withdrawal prints, and a bespoke price reaches no "
        "tier"),
    (3, "loophole-2"): (
        "discard", "test_a_namespace_reaches_the_cluster_only_in_a_tag_whose_header_names_it",
        "a Namespace runs only from a signed tag whose verified header names it, so no delay exists"),
    (3, "loophole-3"): (
        "survivor", "test_a_regulator_withdrawal_prints_as_the_regulators_bump",
        "the withdrawn hole does not vanish: it was booked as the adopter's own removal until "
        "ticket 123, and now prints as the regulator's withdrawal"),
    (3, "overreach-4"): (
        "discard", "test_no_controls_parent_fires_only_when_none_is_declared",
        "`no-controls-parent` never fires on a rotted pin; a missing parent tree is ADR-0020's refusal"),
    (3, "overreach-5"): (
        "discard", "test_a_bespoke_id_never_covers_the_regulators_control_of_the_same_id",
        "(source, id) never collapses one id from two sources, so no merger dedup exists"),
    (3, "overreach-6"): (
        "discard", "test_an_ungoverned_namespace_is_a_workload_share_while_it_exists_and_moves_no_tier",
        "a directory is not a Namespace; a Namespace is priced only while it exists and moves no tier"),
}

# The matching across the three rounds. `place` is the code place the check tested; `reason` is
# the reason the candidate gives, read from its own text. Both are this ticket's reading, so a
# reader can disagree with one row rather than with a number. ADR-0030 point 2 measured overlap
# on ADR-0022 by reason; this is the second document.
MATCHING: dict[tuple[int, str], tuple[str, str]] = {
    (1, "loophole-1"): ("bespoke-scenario", "price a bespoke control low, withdraw it once it served"),
    (1, "loophole-2"): ("ramp-since", "delay the first signed tag so the ramp starts late"),
    (1, "loophole-3"): ("control-key", "a bespoke id shadows the regulator's id of the same name"),
    (1, "overreach-4"): ("removal", "an emergency removal is refused by code that lags the record"),
    (1, "overreach-5"): ("ungoverned-walk", "a short-lived Namespace is priced like a lasting one"),
    (1, "overreach-6"): ("hole-price", "hardening ahead of the regulator earns no credit"),
    (2, "loophole-1"): ("removal", "a mass removal of unweighted controls prints only absences"),
    (2, "loophole-2"): ("bespoke-scenario", "swap a regulator control for a cheap bespoke one"),
    (2, "loophole-3"): ("ramp-since", "rename Namespaces to keep resetting the ramp"),
    (2, "overreach-4"): ("removal", "an emergency removal is priced the same as a loosening"),
    (2, "overreach-5"): ("ungoverned-walk", "a containment Namespace is priced like sprawl"),
    (2, "overreach-6"): ("hole-price", "a wrong regulator weight has no adopter recourse"),
    (3, "loophole-1"): ("bespoke-scenario", "price a bespoke control low, withdraw it once it served"),
    (3, "loophole-2"): ("ramp-since", "delay the first signed tag so the ramp starts late"),
    (3, "loophole-3"): ("withdrawal", "a regulator withdrawal removes a hole with no price"),
    (3, "overreach-4"): ("controls-pin", "a rotted catalogue pin blocks an unrelated deploy"),
    (3, "overreach-5"): ("removal", "a merger's dedup narrows the selection and is priced"),
    (3, "overreach-6"): ("ungoverned-walk", "a short-lived Namespace is priced like a lasting one"),
}


# --------------------------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------------------------

def _composition() -> ModuleType:
    compose_dir = PLATFORM / "compose"
    # distribution/ carries cage_body, which the fixture platform's copied guard renderer imports.
    for extra in (compose_dir, PLATFORM / "distribution"):
        if str(extra) not in sys.path:
            sys.path.insert(0, str(extra))
    spec = importlib.util.spec_from_file_location("_t120_composition", compose_dir / "composition.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules["_t120_composition"] = module
    spec.loader.exec_module(module)
    return module


def _trees(**override: Path) -> dict[str, Path]:
    return {**{name: ESTATE / name for name in PARENTS}, **override}


def _tuppence(root: Path) -> Path:
    """A copy of tuppence's party artefact, its gitops tree and its workflows: what composition
    reads, with nothing committed yet, so the run is a first composition and no history moves
    a status."""
    work = root / "tuppence"
    work.mkdir(parents=True)
    src = ESTATE / "tuppence"
    shutil.copy(src / "party.yaml", work / "party.yaml")
    shutil.copytree(src / "gitops", work / "gitops")
    shutil.copytree(src / ".github", work / ".github")
    return work


def _edit_party(work: Path, edit: Any) -> None:
    doc = yaml.safe_load((work / "party.yaml").read_text())
    edit(doc)
    (work / "party.yaml").write_text(yaml.safe_dump(doc, sort_keys=False))


def _own_member(comp: ModuleType, name: str) -> dict[str, Any]:
    return {"version": "1.0.0", "manifest": {
        "apiVersion": "policies.kyverno.io/v1alpha1", "kind": "ValidatingPolicy",
        "metadata": {"name": f"{name}-1-0-0", "labels": {comp.LABEL_FAMILY: name}},
        "spec": {"validationActions": ["Audit"]}}}


def _regime_entry(doc: dict[str, Any]) -> dict[str, Any]:
    """The one regime entry that carries the regulator's weighted partition."""
    entries = [e for e in doc["prices"] if e.get("source") == "ico" and e.get("holes")]
    assert len(entries) == 1, [e.get("name") for e in doc["prices"]]
    return entries[0]


def _tiers(doc: dict[str, Any]) -> list[tuple[str, str | None]]:
    return [(e["source"], e.get("proposed_tier")) for e in doc["prices"]]


def _exposure_total(rendered: dict[str, str]) -> float:
    return float(yaml.safe_load(rendered["composed/HEADER.yaml"])["exposure"]["total"])


def _fixture_estate(comp: ModuleType, root: Path) -> dict[str, Path]:
    """The composition selfcheck's own clean synthetic estate: fixture-nist with baselines
    SMALL {aa-1, aa-1.1, aa-2} and TINY {aa-1}, fixture-platform claiming aa-1."""
    comp._write_fixture_catalog(root / "fixture-nist")
    comp._write_fixture_platform(root / "fixture-platform", PLATFORM, claims=[("aa-1", "member-a")])
    return {"fixture-nist": root / "fixture-nist", "fixture-platform": root / "fixture-platform"}


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


def _namespaces(repo: Path, side: str) -> None:
    """A governed home Namespace with three Deployments and an ungoverned institution Namespace
    `side` with one, so `side` holds a quarter of the institution workloads."""
    apps = repo / "gitops" / "apps"
    apps.mkdir(parents=True, exist_ok=True)
    home = {"apiVersion": "v1", "kind": "Namespace",
            "metadata": {"name": "home", "labels": {INSTITUTION: "adopter", GOVERNED: "true"}}}
    other = {"apiVersion": "v1", "kind": "Namespace",
             "metadata": {"name": side, "labels": {INSTITUTION: "adopter"}}}
    (apps / "namespace.yaml").write_text(yaml.safe_dump_all([home, other]))
    for f in apps.glob("app-*.yaml"):
        f.unlink()
    for ns, count in (("home", 3), (side, 1)):
        deploys = [{"apiVersion": "apps/v1", "kind": "Deployment",
                    "metadata": {"name": f"app-{n}", "namespace": ns}, "spec": {}} for n in range(count)]
        (apps / f"app-{ns}.yaml").write_text(yaml.safe_dump_all(deploys))


def _signed_tag_naming(comp: ModuleType, repo: Path, tag: str, date: str, ungoverned: list[str]) -> None:
    """Commit a composed header naming `ungoverned` and cut an annotated tag on `date` whose
    body carries a signature block. `_signed_tags` reads the block's presence only; whether it
    verifies is verify/provenance's job, which is why a fixture block is enough here."""
    (repo / "composed").mkdir(exist_ok=True)
    (repo / "composed" / "HEADER.yaml").write_text(
        comp.HEADER_COMMENT + yaml.safe_dump({"ungoverned-namespaces": ungoverned}))
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", tag, date=date)
    _git(repo, "tag", "-a", tag, "-m",
         f"{tag}\n\n-----BEGIN FIXTURE SIGNATURE-----\nfixture\n-----END FIXTURE SIGNATURE-----",
         date=date)


# --------------------------------------------------------------------------------------------
# the survivors
# --------------------------------------------------------------------------------------------

def test_implementing_every_weighted_control_moves_no_regime_price_and_no_tier(tmp_path):
    """Survivor 1, round 1 `overreach-6`. tuppence is composed twice against its real pinned
    parents: as it is, and with its own claim on every control the pinned regulator weights
    name. The claims land: every weighted line turns `covered`. Nothing else moves. The regime
    entry, the exposure total and every proposed tier are the same numbers. ADR-0026 point 2
    says implementing a control reduces the regime's price; this leg says it does not, and
    flips when it does."""
    comp = _composition()
    before, before_rendered = comp.compose(_tuppence(tmp_path / "before"), _trees())
    assert before["outcome"] == "composed", before["refusals"]
    entry = _regime_entry(before)
    weighted = sorted(h["id"] for h in entry["holes"])
    assert weighted and all(h["status"] != "covered" for h in entry["holes"]), entry["holes"]

    work = _tuppence(tmp_path / "after")
    _edit_party(work, lambda d: d.setdefault("overlay", {}).setdefault("add", []).append(
        _own_member(comp, "own-hardening")))
    comp._write_component_definition(work / comp.ADOPTER_CLAIMS_FILE,
                                     [(cid, "own-hardening") for cid in weighted],
                                     source="../nist/catalog/NIST_SP-800-53_rev5.2.0_catalog.json")
    after, after_rendered = comp.compose(work, _trees())
    assert after["outcome"] == "composed", after["refusals"]
    after_entry = _regime_entry(after)
    assert {h["id"]: h["status"] for h in after_entry["holes"]} == {cid: "covered" for cid in weighted}

    assert after_entry["amount"] == entry["amount"], (entry["amount"], after_entry["amount"])
    assert _exposure_total(after_rendered) == _exposure_total(before_rendered)
    assert _tiers(after) == _tiers(before)
    adr = ADR_0026.read_text(encoding="utf-8")
    assert "so implementing a control reduces the regime's price" in adr


def test_a_renamed_ungoverned_namespace_keeps_its_ramp_and_the_closed_delta_says_why(tmp_path):
    """Survivor 2, round 1 `loophole-2` (round 2 `loophole-3` and round 3 `loophole-2` are
    echoes), repaired by eco-system ticket 122. Until then `since` was the date of the first
    signed tag whose header named the Namespace, read by name: a Namespace named in a tag two
    years old ramped at 3.0, and renamed with its workloads it ramped at 1.0. The old name
    printed a `closed-ungoverned` delta saying it now carried governed: "true", which no
    Namespace did. Now `since` is the earliest signed tag that names the Namespace, or names as
    ungoverned a Namespace that then held a workload this one holds now and that no longer
    holds it as an ungoverned Namespace. A rename keeps its ramp, a governed shadow of the old
    name does not drop it (the review round), and a closed entry says whether it was governed or
    left the repo."""
    comp = _composition()
    repo = tmp_path / "adopter"
    repo.mkdir()
    _git(repo, "init", "-q")
    _namespaces(repo, "side")
    _signed_tag_naming(comp, repo, "v1.0.0", "2024-09-01", ["side"])
    as_of, base = "2026-09-01", 10_000.0

    aged = comp.compute_ungoverned({"side"}, {"side"}, governed={"home"})
    comp.price_ungoverned(aged, repo, "adopter", "GBP", base, as_of)
    assert aged[0]["price"]["since"] == "2024-09-01" and aged[0]["price"]["ramp"] == 3.0, aged
    assert aged[0]["price"]["share"] == 0.25 and aged[0]["price"]["amount"] == base * 0.25 * 3.0, aged
    assert aged[0]["price"]["since_by"] == "v1.0.0 names side", aged

    _namespaces(repo, "side-2")     # same workload, new name
    _signed_tag_naming(comp, repo, "v1.1.0", "2026-09-01", ["side-2"])
    renamed = comp.compute_ungoverned({"side-2"}, {"side"}, governed={"home"})
    comp.price_ungoverned(renamed, repo, "adopter", "GBP", base, as_of)
    by_name = {e["namespace"]: e for e in renamed}
    assert by_name["side"] == {"namespace": "side", "status": "closed", "closed_by": "left-repo"}, by_name
    kept = by_name["side-2"]["price"]
    assert kept["since"] == "2024-09-01" and kept["ramp"] == 3.0, kept
    assert kept["since_by"] == "v1.0.0 names side ungoverned, where Deployment/app-0 sat", kept
    assert kept["workloads"] == aged[0]["price"]["workloads"] == 1, kept
    assert kept["amount"] == aged[0]["price"]["amount"], (kept, aged)

    deltas = comp.compute_deltas([], renamed, None, "adopter", "GBP")
    closed = [d for d in deltas if d["kind"] == "closed-ungoverned-namespace"]
    assert len(closed) == 1 and "left the adopter's repo" in closed[0]["detail"], closed
    assert "governed" not in closed[0]["detail"].replace("ungoverned", ""), closed
    opened = [d for d in deltas if d["kind"] == "new-ungoverned-namespace"]
    assert len(opened) == 1 and "since 2024-09-01" in opened[0]["detail"], opened
    assert comp.governed_namespaces(repo) == ["home"], "the renamed Namespace was not governed"

    # Review round: re-declaring the old name as a governed Namespace that holds inert manifests
    # of the same kind and name does not drop the carried age. A governed Namespace pays no
    # ramp, so it cannot be the place the workload still sits.
    dummy_ns = {"apiVersion": "v1", "kind": "Namespace",
                "metadata": {"name": "side", "labels": {INSTITUTION: "adopter", GOVERNED: "true"}}}
    dummy = repo / "gitops" / "apps" / "dummy.yaml"
    dummy.write_text(yaml.safe_dump_all([dummy_ns, {"apiVersion": "apps/v1", "kind": "Deployment",
                                                    "metadata": {"name": "app-0", "namespace": "side"}}]))
    _signed_tag_naming(comp, repo, "v1.2.0", "2026-09-02", ["side-2"])
    shadowed = comp.compute_ungoverned({"side-2"}, {"side-2"}, governed={"home", "side"})
    comp.price_ungoverned(shadowed, repo, "adopter", "GBP", base, as_of)
    held = shadowed[0]["price"]
    assert held["since"] == "2024-09-01" and held["ramp"] == 3.0, held
    dummy.unlink()

    # The same shadow cut in one step, with no signed tag between the rename and the dummy.
    once = tmp_path / "once"
    once.mkdir()
    _git(once, "init", "-q")
    _namespaces(once, "side")
    _signed_tag_naming(comp, once, "v1.0.0", "2024-09-01", ["side"])
    _namespaces(once, "side-2")
    (once / "gitops" / "apps" / "dummy.yaml").write_text(yaml.safe_dump_all(
        [dummy_ns, {"apiVersion": "apps/v1", "kind": "Deployment",
                    "metadata": {"name": "app-0", "namespace": "side"}}]))
    one_step = comp.compute_ungoverned({"side-2"}, {"side"}, governed={"home", "side"})
    comp.price_ungoverned(one_step, once, "adopter", "GBP", base, as_of)
    assert next(e for e in one_step if e["namespace"] == "side-2")["price"]["since"] == "2024-09-01", one_step

    # Governing it is the close that says governed.
    ns_file = repo / "gitops" / "apps" / "namespace.yaml"
    docs = list(yaml.safe_load_all(ns_file.read_text()))
    for doc in docs:
        doc["metadata"]["labels"][GOVERNED] = "true"
    ns_file.write_text(yaml.safe_dump_all(docs))
    assert comp.governed_namespaces(repo) == ["home", "side-2"], comp.governed_namespaces(repo)
    governed = comp.compute_ungoverned(set(comp.ungoverned_namespaces(repo)), {"side-2"},
                                       governed=set(comp.governed_namespaces(repo)))
    assert governed == [{"namespace": "side-2", "status": "closed", "closed_by": "governed"}], governed
    [delta] = comp.compute_deltas([], governed, None, "adopter", "GBP")
    assert 'now carries governed: "true"' in delta["detail"], delta

    # A copy is not a move: a new Namespace running a workload of the same kind and name while
    # the aged one still holds it starts its own ramp.
    copy = tmp_path / "copy"
    copy.mkdir()
    _git(copy, "init", "-q")
    _namespaces(copy, "side")
    _signed_tag_naming(comp, copy, "v1.0.0", "2024-09-01", ["side"])
    (copy / "gitops" / "apps" / "copy.yaml").write_text(yaml.safe_dump(
        {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "app-0", "namespace": "other"}}))
    both = comp.compute_ungoverned({"side", "other"}, {"side"}, governed={"home"})
    comp.price_ungoverned(both, copy, "adopter", "GBP", base, as_of)
    other = next(e for e in both if e["namespace"] == "other")["price"]
    assert other["since"] is None and other["ramp"] == 1.0, other

    # The residual, named in ticket 122: rename every workload with the Namespace and the ramp
    # restarts, because a workload's kind and name are also the adopter's to choose.
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    _git(fresh, "init", "-q")
    _namespaces(fresh, "side")
    _signed_tag_naming(comp, fresh, "v1.0.0", "2024-09-01", ["side"])
    _namespaces(fresh, "side-2")
    (fresh / "gitops" / "apps" / "app-side-2.yaml").write_text(yaml.safe_dump(
        {"apiVersion": "apps/v1", "kind": "Deployment", "metadata": {"name": "renamed", "namespace": "side-2"}}))
    restarted = comp.compute_ungoverned({"side-2"}, {"side"}, governed={"home"})
    comp.price_ungoverned(restarted, fresh, "adopter", "GBP", base, as_of)
    again = next(e for e in restarted if e["namespace"] == "side-2")["price"]
    assert again["since"] is None and again["ramp"] == 1.0, again


def _withdraw(nist: Path, cid: str, *, from_catalogue: bool, baselines: tuple[str, ...]) -> None:
    """The regulator's next catalogue, in place: `cid` leaves every named baseline profile in
    `baselines` and, with `from_catalogue`, leaves the catalogue too. The adopter's own tree is
    not touched."""
    catalog = nist / "catalog"
    meta = json.loads((catalog / "BASELINE_VERSIONS.json").read_text())
    for name in baselines:
        path = catalog / meta["baselines"][name]["file"]
        profile = json.loads(path.read_text())
        for imp in profile["profile"]["imports"]:
            for inc in imp.get("include-controls", []):
                if cid in inc.get("with-ids", []):
                    inc["with-ids"].remove(cid)
        path.write_text(json.dumps(profile))
    if from_catalogue:
        path = catalog / json.loads((catalog / "CATALOG_VERSION.json").read_text())["file"]
        doc = json.loads(path.read_text())

        def drop(items: list[dict[str, Any]]) -> list[dict[str, Any]]:
            return [dict(c, controls=drop(c.get("controls", []))) if c.get("controls") else c
                    for c in items if c["id"] != cid]

        for group in doc["catalog"].get("groups", []):
            group["controls"] = drop(group.get("controls", []))
        path.write_text(json.dumps(doc))


def _catalogue_controls(nist: Path) -> tuple[Path, dict[str, Any]]:
    catalog = nist / "catalog"
    path = catalog / json.loads((catalog / "CATALOG_VERSION.json").read_text())["file"]
    return path, json.loads(path.read_text())


def _walk(items: list[dict[str, Any]]) -> Any:
    for c in items:
        yield c
        yield from _walk(c.get("controls", []))


def _status(nist: Path, cid: str) -> str | None:
    """The `status` prop the catalogue in `nist` gives `cid`, or None."""
    _path, doc = _catalogue_controls(nist)
    for group in doc["catalog"].get("groups", []):
        for c in _walk(group.get("controls", [])):
            if c["id"] == cid:
                return next((p["value"] for p in c.get("props", []) if p.get("name") == "status"), None)
    raise AssertionError(f"{cid} is not in {nist}'s catalogue")


def _mark_withdrawn(nist: Path, cid: str) -> None:
    """The regulator's next catalogue keeps `cid` under `status: withdrawn`, the way NIST
    marks the controls it withdrew."""
    path, doc = _catalogue_controls(nist)
    for group in doc["catalog"].get("groups", []):
        for c in _walk(group.get("controls", [])):
            if c["id"] == cid:
                c["props"] = [p for p in c.get("props", []) if p.get("name") != "status"]
                c["props"].append({"name": "status", "value": "withdrawn"})
    path.write_text(json.dumps(doc))


def _move_nist_pin(work: Path, before_pin: dict[str, Any]) -> None:
    """The bump reaches tuppence the only way one can: its nist pin moves to a new tag."""
    pin = work / "gitops" / "flux-system" / "gotk-sync-nist.yaml"
    pin.write_text(pin.read_text().replace(f"tag: v{before_pin['version']}", "tag: v9.0.0")
                   .replace(before_pin["sha"], "9" * 40))
    _edit_party(work, lambda doc: [e.update(version="9.0.0") for e in doc["inherits"]
                                   if e["party"] == "nist" and e["kind"] == "controls"])


def _parent(rendered: dict[str, str], party: str) -> dict[str, Any]:
    header = yaml.safe_load(rendered["composed/HEADER.yaml"])
    return next(p for p in header["parents"] if p["party"] == party and p["kind"] == "controls")


def test_a_regulator_withdrawal_prints_as_the_regulators_bump(tmp_path):
    """Survivor 3, round 3 `loophole-3`, repaired by eco-system ticket 123. The adopter keeps
    its baseline name and changes nothing. The regulator's next catalogue withdraws aa-2 and
    drops it from SMALL. The composition composes and prints one `withdrawn-control` delta. It
    names the regulator and its catalogue on both sides of the bump, and it never names the
    adopter as the one who removed it. No `removed-control` delta prints. The perspective stays
    the adopter's: it says whose pound the amount is, not who acted. Until ticket 124 this
    refused; from ticket 124 to ticket 123 it printed a `removed-control` in the adopter's name."""
    comp = _composition()
    trees = _fixture_estate(comp, tmp_path)
    work = tmp_path / "fixture-adopter14"
    comp._write_fixture_adopter(work, "SMALL")
    first, rendered = comp.compose(work, trees)
    assert first["outcome"] == "composed", first["refusals"]
    comp._commit_header(work, rendered)

    _withdraw(trees["fixture-nist"], "aa-2", from_catalogue=True, baselines=("SMALL", "BIG"))
    party_before = (work / "party.yaml").read_text()
    second, second_rendered = comp.compose(work, trees)
    assert (work / "party.yaml").read_text() == party_before, "the adopter changed nothing"
    assert second["outcome"] == "composed", second["refusals"]

    assert [d for d in second["deltas"] if d["kind"] in ("removed-control", "baseline-narrowing")] == []
    withdrawn = [d for d in second["deltas"] if d["kind"] == "withdrawn-control"]
    assert [(d["source"], d["control_id"]) for d in withdrawn] == [("fixture-nist", "aa-2")], second["deltas"]
    d = withdrawn[0]
    assert d["withdrawn_by"] == "fixture-nist" and d["reason"] == "catalogue", d
    before, after = _parent(rendered, "fixture-nist"), _parent(second_rendered, "fixture-nist")
    assert before["sha"] != after["sha"], "the regulator's tree moved"
    assert d["catalogue"] == {"from": f"{before['version']}@{before['sha'][:12]}",
                              "to": f"{after['version']}@{after['sha'][:12]}"}, d
    assert d["catalogue"]["from"] in d["detail"] and d["catalogue"]["to"] in d["detail"], d
    assert "fixture-adopter14" not in d["detail"], d
    assert d["perspective"] == "fixture-adopter14" and d["currency"] == "GBP", d
    assert d["amount"] is None and d["priced_by"] is None, d
    header = yaml.safe_load(second_rendered["composed/HEADER.yaml"])
    assert header["selected-controls"] == ["aa-1", "aa-1.1"], header

    record = " ".join(ADR_0026.read_text(encoding="utf-8").split())
    assert "A control the regulator withdraws from its catalogue** is not an adopter removal" in record
    assert "Eco-system ticket 123 built the withdrawal" in record


def test_a_baseline_the_regulator_narrows_under_the_same_name_is_its_withdrawal(tmp_path):
    """Ticket 123's second shape. The regulator keeps aa-1.1 in its catalogue and drops it from
    SMALL. The adopter's last header records what its own overlay selected (nothing), so aa-1.1
    left with the regulator's baseline, not with the adopter."""
    comp = _composition()
    trees = _fixture_estate(comp, tmp_path)
    work = tmp_path / "fixture-adopter14"
    comp._write_fixture_adopter(work, "SMALL")
    first, rendered = comp.compose(work, trees)
    assert first["outcome"] == "composed", first["refusals"]
    assert yaml.safe_load(rendered["composed/HEADER.yaml"])["overlay-controls"] == []
    comp._commit_header(work, rendered)

    _withdraw(trees["fixture-nist"], "aa-1.1", from_catalogue=False, baselines=("SMALL",))
    second, _ = comp.compose(work, trees)
    assert second["outcome"] == "composed", second["refusals"]
    assert [d["kind"] for d in second["deltas"]] == ["withdrawn-control"], second["deltas"]
    d = second["deltas"][0]
    assert (d["control_id"], d["reason"], d["withdrawn_by"]) == ("aa-1.1", "baseline", "fixture-nist"), d
    assert "SMALL" in d["detail"] and "fixture-adopter14" not in d["detail"], d


def test_an_adopters_own_removal_stays_a_removal_beside_a_withdrawal(tmp_path):
    """The repair must not launder an adopter's act as the regulator's. The adopter selects aa-3
    through its overlay, and the regulator drops aa-1.1 from SMALL. In one run the adopter takes
    aa-3 out of its overlay and the regulator's bump lands. aa-3 prints as the adopter's
    `removed-control`; aa-1.1 prints as the regulator's `withdrawn-control`."""
    comp = _composition()
    trees = _fixture_estate(comp, tmp_path)
    work = tmp_path / "fixture-adopter14"
    comp._write_fixture_adopter(work, "SMALL", controls_add=["aa-3"])
    first, rendered = comp.compose(work, trees)
    assert first["outcome"] == "composed", first["refusals"]
    assert yaml.safe_load(rendered["composed/HEADER.yaml"])["overlay-controls"] == ["aa-3"]
    comp._commit_header(work, rendered)

    _withdraw(trees["fixture-nist"], "aa-1.1", from_catalogue=False, baselines=("SMALL",))
    _edit_party(work, lambda doc: doc["overlay"].update(controls=[]))
    second, _ = comp.compose(work, trees)
    assert second["outcome"] == "composed", second["refusals"]
    kinds = {d["control_id"]: d["kind"] for d in second["deltas"] if "control_id" in d}
    assert kinds == {"aa-3": "removed-control", "aa-1.1": "withdrawn-control"}, second["deltas"]


# NIST keeps ac-2.10 under `status: withdrawn`, and an overlay can still select it (the gap the
# ticket-123 build recorded). The review of ticket 123 found the adopter's own removal of it was
# booked as the regulator's withdrawal.
OWN_WITHDRAWN_STATUS = "ac-2.10"


@pytest.mark.parametrize("legacy_header", [False, True], ids=["overlay-recorded", "legacy-header"])
def test_an_adopters_own_removal_of_a_withdrawn_status_control_stays_its_removal(tmp_path, legacy_header):
    """Ticket 123, review round. tuppence selects ac-2.10 through its overlay. NIST's pinned
    catalogue keeps ac-2.10 under `status: withdrawn`, and the composition selects it all the
    same. The adopter alone then takes it out of its overlay; the nist pin does not move. That
    is the adopter's `removed-control`, never a `withdrawn-control` naming a bump that did not
    happen. A last header with no `overlay-controls` must not change the answer."""
    assert _status(ESTATE / "nist", OWN_WITHDRAWN_STATUS) == "withdrawn"
    comp = _composition()
    work = _tuppence(tmp_path / "tuppence")
    _edit_party(work, lambda doc: doc.setdefault("overlay", {}).update(controls=[OWN_WITHDRAWN_STATUS]))
    first, rendered = comp.compose(work, _trees())
    assert first["outcome"] == "composed", first["refusals"]
    header = yaml.safe_load(rendered["composed/HEADER.yaml"])
    assert OWN_WITHDRAWN_STATUS in header["selected-controls"], header["selected-controls"]
    if legacy_header:
        header.pop("overlay-controls")
        header.pop("comparison-inputs", None)
        rendered = dict(rendered)
        rendered["composed/HEADER.yaml"] = comp.HEADER_COMMENT + yaml.safe_dump(header, **comp.YAML_KWARGS)
    comp._commit_header(work, rendered)

    _edit_party(work, lambda doc: doc["overlay"].update(controls=[]))
    second, second_rendered = comp.compose(work, _trees())
    assert second["outcome"] == "composed", second["refusals"]
    assert _parent(rendered, "nist") == _parent(second_rendered, "nist"), "the regulator did nothing"
    moved = [d for d in second["deltas"] if d.get("control_id") == OWN_WITHDRAWN_STATUS]
    assert [d["kind"] for d in moved] == ["removed-control"], second["deltas"]
    assert [d for d in second["deltas"] if d["kind"] == "withdrawn-control"] == [], second["deltas"]


def test_an_adopters_own_removal_of_a_withdrawn_status_control_beside_a_real_bump(tmp_path):
    """Ticket 123, review round, the same-run shape. tuppence's overlay selects ac-2.10, which
    NIST already keeps under `status: withdrawn`. In one run NIST's next tag withdraws another
    selected control and tuppence takes ac-2.10 out of its overlay. The nist pin moves, so a
    real bump lands, but the adopter's last overlay would still select ac-2.10 against the new
    catalogue. ac-2.10 is the adopter's `removed-control`; the other control is NIST's
    `withdrawn-control`."""
    comp = _composition()
    work = _tuppence(tmp_path / "tuppence")
    _edit_party(work, lambda doc: doc.setdefault("overlay", {}).update(controls=[OWN_WITHDRAWN_STATUS]))
    first, rendered = comp.compose(work, _trees())
    assert first["outcome"] == "composed", first["refusals"]
    selected = yaml.safe_load(rendered["composed/HEADER.yaml"])["selected-controls"]
    other = next(c for c in selected if c != OWN_WITHDRAWN_STATUS)
    comp._commit_header(work, rendered)

    nist = tmp_path / "nist"
    shutil.copytree(ESTATE / "nist", nist, ignore=shutil.ignore_patterns(".git"))
    _withdraw(nist, other, from_catalogue=False, baselines=("LOW", "MODERATE", "HIGH"))
    _mark_withdrawn(nist, other)
    _move_nist_pin(work, _parent(rendered, "nist"))
    _edit_party(work, lambda doc: doc["overlay"].update(controls=[]))
    second, _ = comp.compose(work, _trees(nist=nist))
    assert second["outcome"] == "composed", second["refusals"]
    kinds = {d["control_id"]: d["kind"] for d in second["deltas"]
             if d.get("control_id") in (OWN_WITHDRAWN_STATUS, other)}
    assert kinds == {OWN_WITHDRAWN_STATUS: "removed-control", other: "withdrawn-control"}, second["deltas"]


def test_a_weights_feed_that_names_a_withdrawn_control_keeps_its_price_on_the_withdrawal(tmp_path):
    """Ticket 123 item 2, against tuppence's real pinned parents. NIST withdraws a control the
    way its catalogue already marks 182 of them: the control stays in the catalogue with
    `status: withdrawn` and leaves every baseline. The pinned ico weights still name it. That is
    the feed's own fact to fix in its next version (ADR-0026). The composition does not refuse
    and does not re-partition: the regime entry keeps its amount, its line for the control reads
    `withdrawn`, and the `withdrawn-control` delta carries the price the hole carried."""
    comp = _composition()
    work = _tuppence(tmp_path / "tuppence")
    first, rendered = comp.compose(work, _trees())
    assert first["outcome"] == "composed", first["refusals"]
    entry = _regime_entry(first)
    selected = set(yaml.safe_load(rendered["composed/HEADER.yaml"])["selected-controls"])
    line = next(h for h in entry["holes"] if h["id"] in selected)
    comp._commit_header(work, rendered)

    nist = tmp_path / "nist"
    shutil.copytree(ESTATE / "nist", nist, ignore=shutil.ignore_patterns(".git"))
    _withdraw(nist, line["id"], from_catalogue=False, baselines=("LOW", "MODERATE", "HIGH"))
    _mark_withdrawn(nist, line["id"])
    before_pin = _parent(rendered, "nist")
    _move_nist_pin(work, before_pin)
    second, _ = comp.compose(work, _trees(nist=nist))
    assert second["outcome"] == "composed", second["refusals"]
    moved = [d for d in second["deltas"] if d.get("control_id") == line["id"]]
    assert [d["kind"] for d in moved] == ["withdrawn-control"], second["deltas"]
    assert moved[0]["amount"] == line["amount"] and moved[0]["priced_by"], moved
    assert moved[0]["reason"] == "catalogue" and moved[0]["withdrawn_by"] == "nist", moved
    assert moved[0]["catalogue"] == {"from": f"{before_pin['version']}@{before_pin['sha'][:12]}",
                                     "to": "9.0.0@" + "9" * 12}, moved
    assert "tuppence" not in moved[0]["detail"], moved
    after = _regime_entry(second)
    assert after["amount"] == entry["amount"], (entry["amount"], after["amount"])
    after_line = next(h for h in after["holes"] if h["id"] == line["id"])
    assert after_line["status"] == "withdrawn" and after_line["amount"] == line["amount"], after_line


# --------------------------------------------------------------------------------------------
# the discards, each with the fact that decides it
# --------------------------------------------------------------------------------------------

def test_a_removal_composes_and_prints_as_priced_deltas(tmp_path):
    """Round 1 `overreach-4` and round 2 `overreach-4`. ADR-0026 point 5: a removal is priced,
    never refused. Until ticket 124 this leg held the known lag: a narrowing from SMALL to TINY
    refused `removed-control`. It is now the regression test of the build. The narrowing
    composes. Each control that left prints one `removed-control` delta under the adopter's
    perspective, and one `baseline-narrowing` delta summarises the change. No pinned weight names
    a fixture control, so every amount is a named absence. The next header selects only aa-1."""
    comp = _composition()
    trees = _fixture_estate(comp, tmp_path)
    work = tmp_path / "fixture-adopter14"
    comp._write_fixture_adopter(work, "SMALL")
    first, rendered = comp.compose(work, trees)
    assert first["outcome"] == "composed", first["refusals"]
    comp._commit_header(work, rendered)
    _edit_party(work, lambda d: d.update(baseline="TINY"))
    comp._write_baseline_configmap(work, "TINY")
    narrowed, narrowed_rendered = comp.compose(work, trees)
    assert narrowed["outcome"] == "composed", narrowed["refusals"]
    assert not [r for r in narrowed["refusals"] if r["kind"] == "removed-control"], narrowed["refusals"]

    removed = [d for d in narrowed["deltas"] if d["kind"] == "removed-control"]
    assert [d["control_id"] for d in removed] == ["aa-1.1", "aa-2"], narrowed["deltas"]
    for d in removed:
        assert d["source"] == "fixture-nist" and d["perspective"] == "fixture-adopter14", d
        assert d["currency"] == "GBP" and d["amount"] is None and d["priced_by"] is None, d
    narrowing = [d for d in narrowed["deltas"] if d["kind"] == "baseline-narrowing"]
    assert len(narrowing) == 1, narrowed["deltas"]
    assert narrowing[0]["subject"] == "SMALL -> TINY", narrowing
    assert (narrowing[0]["dropped"], narrowing[0]["priced"], narrowing[0]["amount"]) == (2, 0, None), narrowing
    assert [h["control_id"] for h in narrowed["holes"]] == [], narrowed["holes"]
    header = yaml.safe_load(narrowed_rendered["composed/HEADER.yaml"])
    assert header["selected-controls"] == ["aa-1"], header

    record = " ".join(ADR_0026.read_text(encoding="utf-8").split())
    assert record.count("Its `check_selected_set` still refuses `removed-control`") == 0
    assert "Eco-system ticket 124 built the priced removal" in record


def test_a_narrowing_prices_a_weighted_removal_and_names_each_unweighted_one(tmp_path):
    """Round 2 `loophole-1`: a mass removal of unweighted controls prints only absences. True,
    and it is what ADR-0026 says: no pinned weight prices those controls, so the pound they
    carry is nothing any regulator named. The weighted pound is the regime entry, and a removal
    does not move it. tuppence narrows from MODERATE to LOW against a nist copy whose LOW also
    drops the weighted `ra-3`. The one weighted removal prints the price its hole carried; every
    other removal is a named absence; the summary delta counts both; the regime entry and its
    `ra-3` line keep their amounts, and the line reads `unselected`."""
    comp = _composition()
    nist = tmp_path / "nist"
    shutil.copytree(ESTATE / "nist", nist, ignore=shutil.ignore_patterns(".git"))
    low = nist / "catalog" / "NIST_SP-800-53_rev5.2.0_LOW-baseline_profile.json"
    profile = json.loads(low.read_text())
    for imp in profile["profile"]["imports"]:
        for inc in imp.get("include-controls", []):
            if "ra-3" in inc.get("with-ids", []):
                inc["with-ids"].remove("ra-3")
    low.write_text(json.dumps(profile))
    trees = _trees(nist=nist)

    work = _tuppence(tmp_path / "tuppence")
    first, rendered = comp.compose(work, trees)
    assert first["outcome"] == "composed", first["refusals"]
    ra3 = next(h for h in _regime_entry(first)["holes"] if h["id"] == "ra-3")
    comp._commit_header(work, rendered)
    before = set(yaml.safe_load(rendered["composed/HEADER.yaml"])["selected-controls"])

    _edit_party(work, lambda d: d.update(baseline="LOW"))
    pin = work / "gitops" / "apps" / "nist-pin-configmap.yaml"
    pin.write_text(pin.read_text().replace("MODERATE", "LOW"))
    second, second_rendered = comp.compose(work, trees)
    assert second["outcome"] == "composed", second["refusals"]
    after = set(yaml.safe_load(second_rendered["composed/HEADER.yaml"])["selected-controls"])

    removed = {d["control_id"]: d for d in second["deltas"] if d["kind"] == "removed-control"}
    assert sorted(removed) == sorted(before - after) and "ra-3" in removed, sorted(removed)
    assert removed["ra-3"]["amount"] == ra3["amount"] and removed["ra-3"]["priced_by"], removed["ra-3"]
    assert all(d["amount"] is None and d["priced_by"] is None
               for cid, d in removed.items() if cid != "ra-3")
    narrowing = next(d for d in second["deltas"] if d["kind"] == "baseline-narrowing")
    assert narrowing["subject"] == "MODERATE -> LOW", narrowing
    assert (narrowing["dropped"], narrowing["priced"], narrowing["amount"]) == (len(removed), 1, ra3["amount"])

    entry = _regime_entry(second)
    assert entry["amount"] == _regime_entry(first)["amount"]
    line = next(h for h in entry["holes"] if h["id"] == "ra-3")
    assert line["status"] == "unselected" and line["amount"] == ra3["amount"], line


def test_a_bespoke_hole_is_priced_on_its_own_line_and_moves_no_tier(tmp_path):
    """Round 1 `loophole-1`, round 3 `loophole-1`. Both need a bespoke control's price to move
    something that a later removal or a cheaper replacement could move back. A bespoke hole is
    priced, on its own line, by the adopter's own scenario, and nothing reads that line: the
    regime entry, the exposure total and every tier match the composition without it. Ticket
    38 D5 named this limit ("priced but not yet tiered"), so the place is already held. The
    withdrawal both candidates need composes since ticket 124 and prints a `removed-control`
    delta at the scenario's own residual, so the withdrawn pound is on the record."""
    comp = _composition()
    plain, plain_rendered = comp.compose(_tuppence(tmp_path / "plain"), _trees())

    work = _tuppence(tmp_path / "bespoke")
    _edit_party(work, lambda d: (d["inherits"].append({"party": "tuppence", "kind": "controls", "version": "1.0.0"}),
                                 d.setdefault("overlay", {}).update(controls=["tuppence:vendor-review"])))
    comp._write_small_catalog(work, {"vendor-review": {"scenario": "scenarios/vendor-review.json"}})
    (work / "scenarios").mkdir()
    shutil.copy(PLATFORM / "policy" / "scenarios" / "driftwood-root-residual.json",
                work / "scenarios" / "vendor-review.json")
    bespoke, bespoke_rendered = comp.compose(work, _trees())
    assert bespoke["outcome"] == "composed", bespoke["refusals"]
    hole = next(h for h in bespoke["holes"] if h["source"] == "tuppence")
    assert hole["control_id"] == "vendor-review" and hole["amount"] > 0, hole

    assert _regime_entry(bespoke)["amount"] == _regime_entry(plain)["amount"]
    assert _exposure_total(bespoke_rendered) == _exposure_total(plain_rendered)
    assert _tiers(bespoke) == _tiers(plain)

    comp._commit_header(work, bespoke_rendered)
    _edit_party(work, lambda d: d["overlay"].update(controls=[]))
    withdrawn, _ = comp.compose(work, _trees())
    assert withdrawn["outcome"] == "composed", withdrawn["refusals"]
    removed = [d for d in withdrawn["deltas"] if d["kind"] == "removed-control"]
    assert [(d["source"], d["control_id"]) for d in removed] == [("tuppence", "vendor-review")], removed
    assert removed[0]["amount"] == hole["amount"], (removed, hole)
    assert removed[0]["priced_by"] == "tuppence scenario scenarios/vendor-review.json", removed
    readme = (PLATFORM / "compose" / "README.md").read_text(encoding="utf-8")
    assert "so it is priced but not yet tiered" in readme


def test_a_bespoke_id_never_covers_the_regulators_control_of_the_same_id(tmp_path):
    """Round 1 `loophole-3`, round 2 `loophole-2`, round 3 `overreach-5`. tuppence publishes a
    bespoke `pl-2`, one of the regulator's weighted ids, and claims it. The claim covers
    `tuppence:pl-2` only. The regulator's `pl-2` stays a hole and its weighted line is not
    `covered`. The header lists both keys, one bare and one with its source, so one id from two
    sources is two selected controls: nothing collapses them."""
    comp = _composition()
    work = _tuppence(tmp_path)

    def edit(doc: dict[str, Any]) -> None:
        doc["inherits"].append({"party": "tuppence", "kind": "controls", "version": "1.0.0"})
        overlay = doc.setdefault("overlay", {})
        overlay["controls"] = ["tuppence:pl-2"]
        overlay.setdefault("add", []).append(_own_member(comp, "own-plan"))

    _edit_party(work, edit)
    comp._write_small_catalog(work, {"pl-2": {"scenario": "scenarios/pl-2.json"}})
    comp._write_component_definition(work / comp.ADOPTER_CLAIMS_FILE, [("pl-2", "own-plan")],
                                     source="catalog/catalog.json")
    doc, rendered = comp.compose(work, _trees())
    assert doc["outcome"] == "composed", doc["refusals"]
    holes = {(h["source"], h["control_id"]) for h in doc["holes"]}
    assert ("nist", "pl-2") in holes and ("tuppence", "pl-2") not in holes, sorted(holes)[:5]
    line = next(h for h in _regime_entry(doc)["holes"] if h["id"] == "pl-2")
    assert line["source"] == "nist" and line["status"] == "recorded", line
    header = yaml.safe_load(rendered["composed/HEADER.yaml"])
    assert {"pl-2", "tuppence:pl-2"} <= set(header["selected-controls"])
    assert "pl-2" in header["holes"] and "tuppence:pl-2" not in header["holes"]


def test_an_ungoverned_namespace_is_a_workload_share_while_it_exists_and_moves_no_tier(tmp_path):
    """Round 1 `overreach-5`, round 3 `overreach-6`. A directory of manifests is not a
    Namespace: the walk reads `kind: Namespace` documents and the Namespace a workload names.
    Since ticket 119 a scratch Job that names a Namespace makes it an ungoverned Namespace, as
    the candidates say, because silence buys no exemption and neither does intent. An ungoverned
    Namespace with no workload prices at zero. One that is deleted closes and carries no price.
    One with workloads is priced, and that price moves no tier and no exposure total."""
    comp = _composition()
    scratch = tmp_path / "scratch-dir"
    (scratch / "gitops" / "scratch").mkdir(parents=True)
    (scratch / "gitops" / "scratch" / "notes.yaml").write_text(yaml.safe_dump(
        {"apiVersion": "v1", "kind": "ConfigMap", "metadata": {"name": "grant"}}))
    assert comp.ungoverned_namespaces(scratch) == [], "a directory was read as a Namespace"
    (scratch / "gitops" / "scratch" / "job.yaml").write_text(yaml.safe_dump(
        {"apiVersion": "batch/v1", "kind": "Job", "metadata": {"name": "grant", "namespace": "scratch"}}))
    assert comp.ungoverned_namespaces(scratch) == ["scratch"], "a Namespace a workload names went unpriced"

    empty = [{"namespace": "side", "status": "new"}]
    repo = tmp_path / "empty"
    (repo / "gitops").mkdir(parents=True)
    (repo / "gitops" / "ns.yaml").write_text(yaml.safe_dump(
        {"apiVersion": "v1", "kind": "Namespace", "metadata": {"name": "side", "labels": {INSTITUTION: "x"}}}))
    comp.price_ungoverned(empty, repo, "adopter", "GBP", 10_000.0, "2026-09-01")
    assert empty[0]["price"]["amount"] == 0.0, empty

    deleted = comp.compute_ungoverned(set(), {"side"})
    comp.price_ungoverned(deleted, repo, "adopter", "GBP", 10_000.0, "2026-09-01")
    assert deleted == [{"namespace": "side", "status": "closed"}], deleted

    plain, plain_rendered = comp.compose(_tuppence(tmp_path / "plain"), _trees())
    work = _tuppence(tmp_path / "sprawl")
    _namespaces(work, "sprawl")
    sprawl, sprawl_rendered = comp.compose(work, _trees())
    priced = next(e for e in sprawl["ungoverned"] if e["namespace"] == "sprawl")
    assert priced["price"]["amount"] and priced["price"]["amount"] > 0, priced
    assert _tiers(sprawl) == _tiers(plain)
    assert _exposure_total(sprawl_rendered) == _exposure_total(plain_rendered)


def test_a_containment_namespace_is_governed_by_one_label_and_lands_isolated(tmp_path):
    """Round 2 `overreach-5`. Governing a Namespace needs one label and no baseline. The walk
    then lists it as governed and not ungoverned, and the binding check reads a governed
    Namespace with no tier as `isolated`, the tightest rung below `infra`."""
    comp = _composition()
    repo = tmp_path / "adopter"
    (repo / "gitops").mkdir(parents=True)
    ns = {"apiVersion": "v1", "kind": "Namespace",
          "metadata": {"name": "quarantine", "labels": {INSTITUTION: "adopter", GOVERNED: "true"}}}
    (repo / "gitops" / "namespace.yaml").write_text(yaml.safe_dump(ns))
    assert comp.governed_namespaces(repo) == ["quarantine"] and comp.ungoverned_namespaces(repo) == []
    (tmp_path / "evidence.json").write_text(json.dumps({"prices": [
        {"source": "feeds", "kind": "feed", "name": "threat-register", "proposed_tier": "isolated",
         "changed": False}]}))
    run = subprocess.run(["python3", str(PLATFORM / "shift-left" / "tier_binding.py"), "check",
                          "--evidence", str(tmp_path / "evidence.json"), "--adopter-dir", str(repo)],
                         capture_output=True, text=True)
    assert run.returncode == 0 and "isolated by default" in run.stdout, run.stdout + run.stderr


def test_a_mistranscribed_weight_moves_no_regime_price(tmp_path):
    """Round 2 `overreach-6`. A clone of the regulator's repo carries a wrong partition: 0.7 on
    one lower-tier control and 0.1 on the others. tuppence composed against it prices the regime
    entry, the exposure and every tier exactly as against the published weights. A weight only
    splits a fixed amount, so today it cannot misprice anything. The recourse the candidate asks
    for is the pin the adopter already holds and a pull request to the publisher's repo."""
    comp = _composition()
    right, right_rendered = comp.compose(_tuppence(tmp_path / "right"), _trees())
    ico = tmp_path / "ico"
    subprocess.run(["git", "clone", "-q", str(ESTATE / "ico"), str(ico)], check=True, capture_output=True)
    feed = ico / "penalty-schema" / "v3" / "feed.json"
    doc = json.loads(feed.read_text())
    lower = (doc.get("payload") or doc)["control_weights"]["uk-gdpr"]["lower-tier"]
    for i, w in enumerate(lower):
        w["weight"] = 0.7 if i == 0 else round(0.3 / (len(lower) - 1), 10)
    feed.write_text(json.dumps(doc, indent=2))
    wrong, wrong_rendered = comp.compose(_tuppence(tmp_path / "wrong"), _trees(ico=ico))
    assert wrong["outcome"] == "composed", wrong["refusals"]
    moved = {h["id"]: h["weight"] for h in _regime_entry(wrong)["holes"]}
    assert moved[lower[0]["id"]] == 0.7, moved
    assert _regime_entry(wrong)["amount"] == _regime_entry(right)["amount"]
    assert _exposure_total(wrong_rendered) == _exposure_total(right_rendered)
    assert _tiers(wrong) == _tiers(right)


def test_a_namespace_reaches_the_cluster_only_in_a_tag_whose_header_names_it(tmp_path):
    """Round 3 `loophole-2` (and the mechanism round 1 `loophole-2` named). Each adopter's
    cluster syncs its own repo at a pinned tag and commit, never a branch. Its release workflow
    runs `verify`, a byte-for-byte re-render, before it cuts the tag. A Namespace added to the
    repo without the header that names it fails `verify`. So the first signed tag that can
    carry a Namespace to the cluster is the first one that names it, and no delay exists."""
    comp = _composition()
    for adopter in ADOPTERS:
        sync = ESTATE / adopter / "gitops" / "flux-system" / "gotk-sync.yaml"
        repo_doc = next(d for d in yaml.safe_load_all(sync.read_text()) if d and d.get("kind") == "GitRepository")
        assert set(repo_doc["spec"]["ref"]) == {"tag", "commit"}, (adopter, repo_doc["spec"]["ref"])
        workflow = (ESTATE / adopter / ".github" / "workflows" / "cut-release.yml").read_text()
        assert workflow.index(" verify . ") < workflow.index("create the signed annotated tag"), adopter

    trees = _fixture_estate(comp, tmp_path)
    work = tmp_path / "fixture-adopter14"
    comp._write_fixture_adopter(work, "SMALL")
    _, rendered = comp.compose(work, trees)
    for rel, content in rendered.items():
        (work / rel).parent.mkdir(parents=True, exist_ok=True)
        (work / rel).write_text(content)
    assert comp.verify(work, trees)[0], "the control: a freshly composed tree verifies"
    comp._write_namespace(work, "late", institution=True, governed=False)
    comp._write_workload(work, "late", "app")
    ok, mismatches = comp.verify(work, trees)
    assert not ok and mismatches, "a Namespace the committed artefact does not know verified"


def test_no_controls_parent_fires_only_when_none_is_declared(tmp_path):
    """Round 3 `overreach-4`. `no-controls-parent` fires when a party declares no controls
    parent. A controls parent whose tree cannot be read is a different refusal, a missing
    parent tree, before any hole is looked at. That refusal is ADR-0020's decided line, a
    missing instrument refuses, and the candidate's recourse, a re-pin by pull request, is the
    path principle 12 names."""
    comp = _composition()
    trees = _fixture_estate(comp, tmp_path)
    missing = tmp_path / "missing"
    comp._write_fixture_adopter(missing, "SMALL")
    doc, _ = comp.compose(missing, {k: v for k, v in trees.items() if k != "fixture-nist"})
    assert doc["outcome"] == "refused" and doc["refusals"] == [], doc["refusals"]
    assert any("no parent tree provided" in e for e in doc["party_artefact_errors"]), doc["party_artefact_errors"]

    undeclared = tmp_path / "undeclared"
    comp._write_fixture_adopter(undeclared, "SMALL")
    _edit_party(undeclared, lambda d: d.update(inherits=[e for e in d["inherits"] if e["kind"] != "controls"]))
    doc, _ = comp.compose(undeclared, trees)
    assert [r["kind"] for r in doc["refusals"] if r["kind"] == "no-controls-parent"] == ["no-controls-parent"], \
        doc["refusals"]


# --------------------------------------------------------------------------------------------
# the record: every candidate has a verdict, the rate is computed, the matching is counted
# --------------------------------------------------------------------------------------------

def _candidates() -> set[tuple[int, str]]:
    found = set()
    for rnd in (1, 2, 3):
        for case in json.loads((ROUNDS / f"round-{rnd}" / "candidates.json").read_text()):
            found.add((rnd, case["key"]))
    return found


def test_every_candidate_carries_a_verdict_and_a_matching_row():
    assert set(VERDICTS) == set(MATCHING) == _candidates() and len(VERDICTS) == 18
    here = {name for name in globals() if name.startswith("test_")}
    for key, (verdict, test, fact) in VERDICTS.items():
        assert verdict in {"survivor", "discard"} and fact.strip(), key
        assert test in here, f"{key}: no test named {test}"


def test_the_judge_verdicts_are_counted_and_not_used():
    """ADR-0030 point 5: the judge's verdict is not a filter. It called 11 of 18 resolvable.
    Of the three survivors it called one unresolvable."""
    judged = {}
    for rnd in (1, 2, 3):
        for case in json.loads((ROUNDS / f"round-{rnd}" / "candidates.json").read_text()):
            judged[(rnd, case["key"])] = case["judge_resolvable"]
    assert sum(judged.values()) == 11
    survivors = [k for k, (v, _, _) in VERDICTS.items() if v == "survivor"]
    assert sorted(judged[k] for k in survivors) == [False, True, True]


def test_the_survival_rate_is_derived_from_the_verdicts():
    """Three of eighteen on ADR-0026, by round 2, 0 and 1. ADR-0022 gave three of eighteen too,
    so two documents give six of thirty-six. ADR-0030's 2026-09-23 note states both."""
    survived = sorted(k for k, (v, _, _) in VERDICTS.items() if v == "survivor")
    assert len(survived) == 3 and len(VERDICTS) == 18
    by_round = [sum(1 for r, _ in survived if r == n) for n in (1, 2, 3)]
    assert by_round == [2, 0, 1]
    adr = ADR_0030.read_text(encoding="utf-8")
    assert "3 of 18 candidates against ADR-0026 survived" in adr
    assert "6 of 36" in adr


def _overlap(a: int, b: int, key: Any) -> int:
    """A one-to-one matching between two rounds on `key`: for each label, the smaller of the
    two rounds' counts."""
    left = [key(v) for (r, _), v in MATCHING.items() if r == a]
    right = [key(v) for (r, _), v in MATCHING.items() if r == b]
    return sum(min(left.count(label), right.count(label)) for label in set(left))


def test_the_overlap_between_rounds_is_counted_by_place_and_by_reason():
    """ADR-0030 point 2 measured, on ADR-0022, a pairwise overlap of 2, 1 and 3 by reason. On
    ADR-0026 it is 0, 3 and 0 by reason, and 5, 4 and 4 by place. All three rounds share four
    places and no reason. The tool repeats its place and varies its reason, as on ADR-0022."""
    pairs = ((1, 2), (1, 3), (2, 3))
    assert [_overlap(a, b, lambda v: v) for a, b in pairs] == [0, 3, 0]
    assert [_overlap(a, b, lambda v: v[0]) for a, b in pairs] == [5, 4, 4]
    places = [{v[0] for (r, _), v in MATCHING.items() if r == n} for n in (1, 2, 3)]
    assert places[0] & places[1] & places[2] == {"bespoke-scenario", "ramp-since", "removal", "ungoverned-walk"}
    reasons = [{v for (r, _), v in MATCHING.items() if r == n} for n in (1, 2, 3)]
    assert reasons[0] & reasons[1] & reasons[2] == set()
    distinct = {v for v in MATCHING.values()}
    assert len(distinct) == 15 and len({v[0] for v in distinct}) == 8
