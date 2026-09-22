"""Laya/loophole ticket 08: the two loophole candidates that survived, as checks.

`loophole` is non-deterministic, so under "derive what you assert" its output is a hypothesis and
never a finding. Ticket 07 ran one round against ADR-0022 and produced six candidates. This file
is what two of them became: the candidate was the pointer, the check is the finding. The other
four are recorded as discards in the ticket, with a reason each.

Neither survivor reproduces the wording of the scenario that pointed at it. Both were measured
and both came back with a different mechanism from the one the model named, which is the whole
reason the ticket refuses to catalogue a candidate unread.

  A. **`infra` is read by no served cage-tier body.** Measured 2026-09-21 as a hole; repaired and
     decided 2026-09-22 by eco-system ticket 113, so leg A is now that repair's regression test.
     ADR-0022 gives a `platform`-role party the right to declare a Namespace at `infra`, and
     `platform/engine/namespaces.yaml` declares kube-system, flux-system and kyverno that way.
     Ticket 113 decided `infra` is a ROLE declaration and not a rung: no served body reads it,
     and that is now asserted as a decision rather than reported as a surprise. What protects
     the substrate is measured here instead. An UNCLAIMED pod there is outside every served
     cage-tier body by its `claims-a-policy-version` matchCondition, with the declaration or
     without it. A CLAIMING pod there takes the body's ungoverned else-branch: `isolated` under
     5.0.0 and graded, `baseline` -- the loosest rung -- under 4.0.0, which all three adopters
     still serve. `distribution/verify-infra-declaration.sh` was re-aimed at those two facts:
     its proof 3 guards the claim gate and the substrate's ungoverned state (the hazard a
     planted body shows is real), and its proof 4 names every delivered body that still cages a
     claiming substrate pod looser than `isolated`. The legs below hold the engine and that
     offline script to the same answer.

  B. **A second governed Namespace document silences the hub's binding walk, at exit 0.**
     `platform/shift-left/tier_binding.py` returns 3 -- could-not-look -- when a party declares
     two governed Namespaces, because which one carries the party's tier is not the check's guess
     to make (ADR-0020). The adopter's own `shift-left.yml` turns that 3 into a failed pull
     request. The hub's estate walk, `verify/tier-binding/tier_binding_estate.py`, printed the
     party's SKIP line, CONTINUED, and exited 0 while any other party was bound, and
     `verify-all.sh` grades a script by its exit code, so the gate read PASS for an estate in which
     one party's cage was unobserved. Repaired 2026-09-22 by eco-system ticket 114: a party owed an
     observation that cannot be looked at now holds the walk at exit 3, outside the manifest's
     declared `waits:`, so leg B is that repair's regression test.

The `infra` legs that need an engine run under the version the release workflows pin, 1.18.2.
A different CLI is a could-not-look and says so: 1.19.1 refuses to compile the served body at all
(`expected type 'string' but found 'dyn'`), and grading that as a passing fixture would be this
file asserting a property it never looked at.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

HUB = Path(__file__).resolve().parent.parent
ESTATE = HUB / ".estate-clone"
PLATFORM = ESTATE / "platform"
ADOPTERS = ("driftwood", "ludlow", "tuppence")
PINNED_KYVERNO = "1.18.2"
TRIPWIRE = Path("distribution") / "verify-infra-declaration.sh"
CLAIM = "policy-as-versioned.dev/policy-version"
SUBSTRATE = {"platform.acme.io/plane": "engine", "posture.acme.io/tier": "infra"}

# The rungs `variables.tier`'s membership test admits. `infra` is deliberately not among them
# (wargamer.LADDER says so too, and ticket 113 decided it stays that way), which is exactly why
# the else branch is what an `infra` Namespace gets.
SELECTABLE = ("baseline", "restricted", "quarantine", "isolated")


def _every_cage_tier_body() -> list[Path]:
    """Every copy of cage-tier anyone holds: the hub's released trees (retired ones included),
    the authoring tree, and each adopter's composed copy. `.work/` is a builder's scratch tree
    and vselfcheck is a fixture; neither is held by anyone."""
    found: list[Path] = []
    for pattern in ("distribution/policies/v*/cage-tier.yaml", "graded/policies/cage-tier.yaml"):
        found += [p for p in PLATFORM.glob(pattern)
                  if ".work" not in p.parts and "vselfcheck" not in p.parts]
    for adopter in ADOPTERS:
        found += sorted((ESTATE / adopter).glob("composed/policies/v*/cage-tier.yaml"))
    return sorted(found)


def _declared_versions() -> list[str]:
    """The lines `distribution/versions.yaml` declares, read with a real YAML parser -- the
    tripwire reads the same array with a regex, so the two readings check each other."""
    doc = yaml.safe_load((PLATFORM / "distribution" / "versions.yaml").read_text())
    return [v["version"] for block in doc["spec"]["inputs"] for v in block["versions"]]


def _delivered_bodies() -> list[Path]:
    """What reaches a cluster: each DECLARED line, the graded authoring copy the next line is cut
    from, and each adopter's composed copy. The set the tripwire's proofs 3 and 4 read."""
    found = [PLATFORM / "distribution" / "policies" / f"v{v}" / "cage-tier.yaml"
             for v in _declared_versions()]
    found.append(PLATFORM / "graded" / "policies" / "cage-tier.yaml")
    for adopter in ADOPTERS:
        found += sorted((ESTATE / adopter).glob("composed/policies/v*/cage-tier.yaml"))
    missing = [p for p in found if not p.is_file()]
    assert not missing, f"a delivered body is absent from the estate: {missing}"
    return found


def _without_comments(body: Path) -> str:
    """The policy BODY, with the prose stripped. `verify-infra-declaration.sh` had to learn the
    same lesson on 2026-09-04: its own changelog comment quoted the shape it had replaced, and
    the check read the prose and reported an already-flipped body as unflipped."""
    return "\n".join(re.sub(r"#.*$", "", line) for line in body.read_text(encoding="utf-8").splitlines())


def _claim(body: Path) -> str:
    """The claim that selects this body. A released or composed body self-scopes to its own
    version label; the graded authoring copy carries none and matches any non-empty claim."""
    doc = yaml.safe_load(body.read_text(encoding="utf-8"))
    return doc["metadata"].get("labels", {}).get(CLAIM, "graded")


def _kyverno() -> str:
    """The pinned CLI, or a named could-not-look. Never another version: 1.19.1 does not compile
    the served body, so a skip here is the honest verdict and a pass would be a lie."""
    exe = shutil.which("kyverno")
    if exe is None:
        pytest.skip("no kyverno CLI on PATH -- the served cage body needs an engine to render")
    out = subprocess.run([exe, "version"], capture_output=True, text=True).stdout
    if PINNED_KYVERNO not in out:
        pytest.skip(f"kyverno on PATH is not the pinned {PINNED_KYVERNO} that release.yml "
                    f"installs -- {out.splitlines()[0] if out else 'no version line'}")
    return exe


def _render(tmp: Path, exe: str, body: Path, namespace_labels: dict, pod_labels: dict) -> dict:
    """One pod through one served cage-tier body, against one Namespace. Returns the mutated pod,
    or {} when the policy skipped it."""
    values = {"apiVersion": "cli.kyverno.io/v1alpha1", "kind": "Values",
              "namespaces": [{"apiVersion": "v1", "kind": "Namespace",
                              "metadata": {"name": "substrate", "labels": namespace_labels}}]}
    pod = {"apiVersion": "v1", "kind": "Pod",
           "metadata": {"name": "probe", "namespace": "substrate", "labels": pod_labels},
           "spec": {"containers": [{"name": "app", "image": "nginx"}]}}
    (tmp / "values.yaml").write_text(yaml.safe_dump(values))
    (tmp / "pod.yaml").write_text(yaml.safe_dump(pod))
    run = subprocess.run([exe, "apply", str(body), "--resource", str(tmp / "pod.yaml"),
                          "--values-file", str(tmp / "values.yaml")],
                         capture_output=True, text=True, cwd=tmp)
    assert "error: 0" in run.stdout, f"the engine refused the served body:\n{run.stdout}{run.stderr}"
    return _mutated_pod(run.stdout, pod)


def _mutated_pod(stdout: str, sent: dict) -> dict:
    """The pod as some policy in the file CHANGED it, or {} when none did. The engine's own
    words are not enough on either side. It prints `applied to` with the pod unchanged when a
    body skips it (4.0.0 does), and a file with two policies can print `skipped mutate policy`
    for one while the other cages the pod. Until the second review of PR 28 (2026-09-22) the
    skip line alone was read as "outside the cage", so a shadow policy caging CoreDNS at
    `isolated` read as skipped. So: compare what came back with what was sent."""
    # The engine prints `policy <name> applied to <ns>/Pod/<name>:` and then the object.
    blocks = re.split(r"^policy .* applied to .*:$", stdout, flags=re.M)
    for block in blocks[1:]:
        # Only the first document after the header is the object; the engine's own prose
        # (`Mutation: ...`) follows the `---` and is not YAML.
        doc = yaml.safe_load(re.split(r"(?m)^---\s*$", block)[0])
        if isinstance(doc, dict) and doc.get("kind") == "Pod" and doc != sent:
            return doc
    if len(blocks) > 1 or "skipped mutate policy" in stdout:
        return {}
    raise AssertionError(f"the engine neither applied nor skipped a policy:\n{stdout}")


def _rung(tmp: Path, exe: str, body: Path, namespace_labels: dict) -> str:
    """The rung a CLAIMING pod gets from `body` in a Namespace carrying `namespace_labels`."""
    pod = _render(tmp, exe, body, namespace_labels, {CLAIM: _claim(body)})
    assert pod, f"{body}: a claiming pod was skipped -- the body does not self-scope as assumed"
    return pod["metadata"]["labels"]["posture.acme.io/tier"]


def _tripwire(platform: Path) -> subprocess.CompletedProcess:
    """`verify-infra-declaration.sh` as the gate calls it: no arguments, so its selfcheck runs
    first. It derives the estate from its own location, so a planted platform is planted beside
    whatever adopters its parent directory holds."""
    return subprocess.run(["bash", str(platform / TRIPWIRE)], capture_output=True, text=True)


def _plant_platform(root: Path, graded_body: str | None = None, namespaces: str | None = None,
                    declared: tuple[str, ...] = ("5.0.0",)) -> Path:
    """A platform checkout the tripwire can run over, built from the REAL files, with one thing
    changed. The estate beside it holds no adopter, so only the platform's own bodies count."""
    plat = root / "estate" / "platform"
    (plat / "distribution").mkdir(parents=True)
    shutil.copy(PLATFORM / TRIPWIRE, plat / TRIPWIRE)
    shutil.copy(PLATFORM / "party.yaml", plat / "party.yaml")
    (plat / "engine").mkdir()
    (plat / "engine" / "namespaces.yaml").write_text(
        namespaces if namespaces is not None
        else (PLATFORM / "engine" / "namespaces.yaml").read_text())
    (plat / "distribution" / "versions.yaml").write_text(
        "spec:\n  inputs:\n    - versions:\n"
        + "".join(f'        - {{ version: "{v}", tag: "policy/v{v}" }}\n' for v in declared))
    for v in declared:
        (plat / "distribution" / "policies" / f"v{v}").mkdir(parents=True)
        shutil.copy(PLATFORM / "distribution" / "policies" / f"v{v}" / "cage-tier.yaml",
                    plat / "distribution" / "policies" / f"v{v}" / "cage-tier.yaml")
    (plat / "graded" / "policies").mkdir(parents=True)
    (plat / "graded" / "policies" / "cage-tier.yaml").write_text(
        graded_body if graded_body is not None
        else (PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text())
    return plat


CLAIM_GATE_EXPR = "object.metadata.?labels['policy-as-versioned.dev/policy-version'].orValue('') != ''"

# Each way a served body's claim gate can be edited so an UNCLAIMED pod passes it. `true` drops
# the gate; the `|| true` shapes keep the real gate as a PREFIX and loosen it after, which a
# prefix match reads as the gate (review of PR 28, 2026-09-22). The last one breaks the line.
LOOSENINGS = {
    "dropped": lambda gate: "true",
    "or-true": lambda gate: f"{gate} || true",
    "or-true-next-line": lambda gate: f"{gate}\n        || true",
}


GATE_ENTRY = ("    - name: claims-a-policy-version\n      expression: >-\n"
              f"        {CLAIM_GATE_EXPR}\n")
ANY_POD = "    - name: any-pod\n      expression: 'true'\n"


def _second_policy_document(graded: str) -> str:
    """The real body, then `---` and a copy named `cage-tier-shadow` whose one matchCondition
    every pod passes. The gate is still in the file, word for word."""
    shadow = graded.replace("  name: cage-tier\n", "  name: cage-tier-shadow\n", 1)
    return graded + "\n---\n" + shadow.replace(GATE_ENTRY, ANY_POD, 1)


def _gate_as_annotation_text(graded: str) -> str:
    """The real matchCondition swapped for one every pod passes, and the gate entry parked
    verbatim in an annotation string, where a text search still finds it."""
    note = "".join("      " + line + "\n" for line in GATE_ENTRY.splitlines())
    return graded.replace(GATE_ENTRY, ANY_POD, 1).replace(
        "metadata:\n  name: cage-tier\n",
        "metadata:\n  name: cage-tier\n  annotations:\n    note: |\n" + note, 1)


# Each way the gate's text can stay in the file while it stops being the one policy's own
# matchCondition (second review of PR 28, 2026-09-22). The engine cages an unclaimed pod under
# both; a whole-file search read both as gated.
MISPLACEMENTS = {
    "second-policy-document": _second_policy_document,
    "gate-as-annotation-text": _gate_as_annotation_text,
}


def _without_claim_gate(body: str, loosen: str = "dropped") -> str:
    """A served body with its `claims-a-policy-version` matchCondition swapped for one every pod
    passes. The one edit proof 3 exists to catch, in each shape `LOOSENINGS` names."""
    assert CLAIM_GATE_EXPR in body, "the body's claim gate moved -- re-read it before planting"
    gated = body.replace(CLAIM_GATE_EXPR, LOOSENINGS[loosen](CLAIM_GATE_EXPR), 1)
    assert gated != body
    return gated


# --------------------------------------------------------------------------------------------
# A. `infra` is a role declaration, and the substrate is protected by what really protects it
# --------------------------------------------------------------------------------------------

def test_the_platform_declares_three_namespaces_at_infra_and_governs_none_of_them():
    """The premise every leg below rests on, read rather than assumed."""
    docs = list(yaml.safe_load_all((PLATFORM / "engine" / "namespaces.yaml").read_text()))
    declared = {d["metadata"]["name"]: d["metadata"].get("labels", {}) for d in docs if d}
    assert set(declared) == {"kyverno", "flux-system", "kube-system"}
    for name, labels in declared.items():
        assert labels.get("posture.acme.io/tier") == "infra", name
        assert "policy-as-versioned.dev/governed" not in labels, \
            f"{name} is governed after all -- leg A's else branch is the UNGOVERNED one"


def test_infra_stays_out_of_every_cage_tier_body_by_decision():
    """Ticket 113 decided `infra` is not a rung: any dial row for it would repeat `isolated` or be
    looser, and looser is an exemption bought by choosing a Namespace. Read as text, over every
    copy anyone holds. A body that starts reading the word needs a new decision, and the
    tripwire's proof 4 fails on it by name until one is made."""
    bodies = _every_cage_tier_body()
    assert len(bodies) >= 4, f"only {len(bodies)} cage-tier bodies found -- the scan is blind"
    carrying = [str(p.relative_to(HUB)) for p in bodies if "infra" in _without_comments(p)]
    assert carrying == [], f"a body reads `infra` -- ticket 113's decision needs revisiting: {carrying}"


def test_a_claiming_substrate_pod_falls_closed_under_the_newest_line_and_graded(tmp_path):
    """The repair, where the platform can make it: the newest declared line and the authoring copy
    the next line is cut from both cage a claiming pod in an `infra` Namespace at `isolated`."""
    exe = _kyverno()
    newest = max(_declared_versions(), key=lambda v: tuple(int(x) for x in v.split(".")))
    for body in (PLATFORM / "distribution" / "policies" / f"v{newest}" / "cage-tier.yaml",
                 PLATFORM / "graded" / "policies" / "cage-tier.yaml"):
        tier = _rung(tmp_path, exe, body, SUBSTRATE)
        assert tier == "isolated", f"{body.relative_to(ESTATE)}: a claiming substrate pod got {tier!r}"


def test_the_tripwire_names_exactly_the_bodies_the_engine_cages_loosely(tmp_path):
    """Fact 2, as the gate now sees it. The engine renders a claiming substrate pod under every
    delivered body; the offline tripwire reads the same bodies with regexes. They must name the
    same offenders, and the tripwire must FAIL while there are any. The only offenders allowed
    are 4.0.0 bodies, which are signed and frozen: the exposure closes when the adopters serve
    5.0.0 and 4.0.0 leaves versions.yaml, and a NEW offender is a regression."""
    exe = _kyverno()
    loose = {}
    for body in _delivered_bodies():
        tier = _rung(tmp_path, exe, body, SUBSTRATE)
        assert tier in SELECTABLE, f"{body}: rendered {tier!r}, which is not a rung"
        if tier != "isolated":
            loose[str(body.relative_to(ESTATE))] = tier
    for rel, tier in loose.items():
        assert "/v4.0.0/" in rel and tier == "baseline", (
            f"{rel} cages a claiming substrate pod at {tier!r}: only the frozen 4.0.0 bodies may "
            f"still do that")
    run = _tripwire(PLATFORM)
    out = run.stdout + run.stderr
    if not loose:
        assert run.returncode == 0 and "PASS:" in out, out
        return
    assert run.returncode == 1, out
    fail = next(line for line in out.splitlines() if line.startswith("FAIL:"))
    assert "claims a policy version in kube-system" in fail, fail
    named = dict(re.findall(r"(\S+/cage-tier\.yaml)=(\w+)", fail))
    assert named == loose, f"the tripwire and the engine disagree:\n  tripwire {named}\n  engine   {loose}"


def test_an_unclaimed_substrate_pod_is_outside_every_delivered_body(tmp_path):
    """Fact 3, now the property proof 3 guards. CoreDNS claims no policy version, so every
    delivered cage-tier body skips it -- with the `infra` declaration and without it. The
    declaration is not what keeps the substrate running; the claim gate is."""
    exe = _kyverno()
    for body in _delivered_bodies():
        with_label = _render(tmp_path, exe, body, SUBSTRATE, {})
        without_label = _render(tmp_path, exe, body, {"platform.acme.io/plane": "engine"}, {})
        assert with_label == {} == without_label, (
            f"{body.relative_to(ESTATE)}: an unclaimed substrate pod was caged -- CoreDNS would "
            f"stop")


@pytest.mark.parametrize("loosen", sorted(LOOSENINGS))
def test_the_hazard_proof_3_guards_is_real(loosen, tmp_path):
    """The tripwire must guard a configuration that does happen. Drop or loosen the claim gate in
    the graded body and the engine puts an unclaimed substrate pod -- CoreDNS -- on `isolated`:
    no ingress, no egress, first eviction."""
    exe = _kyverno()
    body = tmp_path / "ungated.yaml"
    body.write_text(_without_claim_gate(
        (PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text(), loosen))
    pod = _render(tmp_path, exe, body, SUBSTRATE, {})
    assert pod and pod["metadata"]["labels"]["posture.acme.io/tier"] == "isolated", pod


@pytest.mark.parametrize("misplace", sorted(MISPLACEMENTS))
def test_the_hazard_a_misplaced_gate_hides_is_real(misplace, tmp_path):
    """The gate's words are still in the file, and the engine still cages CoreDNS at
    `isolated`. This is also the engine-side leg's own check: `_render` must see the caging
    policy even when another policy in the same file printed a skip."""
    exe = _kyverno()
    graded = (PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text()
    assert GATE_ENTRY in graded, "the graded body's gate entry moved -- re-read it before planting"
    body = tmp_path / "misplaced.yaml"
    body.write_text(MISPLACEMENTS[misplace](graded))
    pod = _render(tmp_path, exe, body, SUBSTRATE, {})
    assert pod and pod["metadata"]["labels"]["posture.acme.io/tier"] == "isolated", pod


def test_a_mutation_outranks_a_skip_line_in_the_engine_output():
    """`_render`'s reading of kyverno's stdout, pinned without an engine. The shapes are the
    ones kyverno 1.18.2 printed: 4.0.0 prints `applied to` with the pod unchanged and then a skip
    line for an unclaimed pod, and the two-policy plant prints a skip for one policy while the
    other cages the pod."""
    sent = {"apiVersion": "v1", "kind": "Pod", "metadata": {"name": "coredns", "labels": {}}}
    unchanged = ("policy cage-tier applied to substrate/Pod/coredns:\n"
                 "apiVersion: v1\nkind: Pod\nmetadata:\n  name: coredns\n  labels: {}\n---\n")
    caged = ("policy cage-tier-shadow applied to substrate/Pod/coredns:\n"
             "apiVersion: v1\nkind: Pod\nmetadata:\n  name: coredns\n  labels:\n"
             "    posture.acme.io/tier: isolated\n---\n")
    skip = "skipped mutate policy cage-tier -> resource substrate/Pod/coredns\n"
    assert _mutated_pod(unchanged + caged + skip, sent)["metadata"]["labels"] == \
        {"posture.acme.io/tier": "isolated"}, "a caging policy beside a skipping one cages"
    assert _mutated_pod(unchanged + skip, sent) == {}, "an unchanged pod plus a skip is a skip"
    assert _mutated_pod(skip, sent) == {}


@pytest.mark.parametrize("misplace", sorted(MISPLACEMENTS))
def test_the_tripwire_fires_when_the_gate_is_not_the_policys_own(misplace, tmp_path):
    graded = (PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text()
    run = _tripwire(_plant_platform(tmp_path, graded_body=MISPLACEMENTS[misplace](graded)))
    out = run.stdout + run.stderr
    assert run.returncode == 1, out
    assert "without the claims-a-policy-version gate: platform/graded/policies/cage-tier.yaml" in out, out


def test_the_tripwire_fires_on_a_duplicated_matchconditions_key(tmp_path):
    """A second `matchConditions:` key under spec. The pinned CLI loads no policy from such a
    file (`Applying 0 policy rule(s)`), so what a cluster would do is not observed here; the
    tripwire refuses to vouch for a gate it cannot read as one list."""
    graded = (PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text()
    body = graded.replace("  variables:\n", "  matchConditions:\n" + ANY_POD + "  variables:\n", 1)
    assert body != graded
    run = _tripwire(_plant_platform(tmp_path, graded_body=body))
    out = run.stdout + run.stderr
    assert run.returncode == 1 and "2 spec.matchConditions keys" in out, out


def test_the_tripwire_passes_a_platform_that_serves_only_the_fixed_line(tmp_path):
    """The control. Without it, the FAIL legs below could be the tripwire failing everything."""
    run = _tripwire(_plant_platform(tmp_path))
    assert run.returncode == 0 and "PASS:" in run.stdout, run.stdout + run.stderr


@pytest.mark.parametrize("loosen", sorted(LOOSENINGS))
def test_the_tripwire_fires_when_a_served_body_drops_the_claim_gate(loosen, tmp_path):
    """The authoring copy, where the gate is a block scalar."""
    body = _without_claim_gate((PLATFORM / "graded" / "policies" / "cage-tier.yaml").read_text(), loosen)
    run = _tripwire(_plant_platform(tmp_path, graded_body=body))
    out = run.stdout + run.stderr
    assert run.returncode == 1, out
    assert "without the claims-a-policy-version gate: platform/graded/policies/cage-tier.yaml" in out, out


@pytest.mark.parametrize("loosen", sorted(LOOSENINGS))
def test_the_tripwire_fires_when_a_declared_line_loosens_the_claim_gate(loosen, tmp_path):
    """A rendered line, where the gate is a one-line plain scalar."""
    plat = _plant_platform(tmp_path)
    served = plat / "distribution" / "policies" / "v5.0.0" / "cage-tier.yaml"
    served.write_text(_without_claim_gate(served.read_text(), loosen))
    run = _tripwire(plat)
    out = run.stdout + run.stderr
    assert run.returncode == 1, out
    assert ("without the claims-a-policy-version gate: "
            "platform/distribution/policies/v5.0.0/cage-tier.yaml") in out, out


def test_the_tripwire_fires_when_a_substrate_namespace_is_governed(tmp_path):
    ns = (PLATFORM / "engine" / "namespaces.yaml").read_text().replace(
        "name: kube-system\n  labels: { platform.acme.io/plane: engine,",
        'name: kube-system\n  labels: { policy-as-versioned.dev/governed: "true", '
        "platform.acme.io/plane: engine,")
    assert "governed" in ns, "the kube-system manifest moved -- re-read it before planting"
    run = _tripwire(_plant_platform(tmp_path, namespaces=ns))
    out = run.stdout + run.stderr
    assert run.returncode == 1 and "governed" in out and "kube-system" in out, out


def test_the_tripwire_fires_on_a_declared_line_that_cages_the_substrate_loosely(tmp_path):
    """Fact 2 planted on the platform alone: declare 4.0.0 beside 5.0.0 and proof 4 names it."""
    run = _tripwire(_plant_platform(tmp_path, declared=("4.0.0", "5.0.0")))
    out = run.stdout + run.stderr
    assert run.returncode == 1, out
    assert "platform/distribution/policies/v4.0.0/cage-tier.yaml=baseline" in out, out
    assert "v5.0.0/cage-tier.yaml=" not in out.split("FAIL:")[-1], out


@pytest.mark.parametrize("entitled", [True, False])
def test_a_governed_namespace_declaring_infra_renders_isolated_under_every_delivered_body(entitled, tmp_path):
    """Ticket 113 item 4. `tier_binding.py` grades an `infra` declaration `bound` because
    `isolated`, what it renders, is the tightest rung a price selects. That is only safe if the
    cage really renders `isolated` for it, under every body anyone is delivered, whoever wrote
    it -- admission cannot read a party's roles, so `entitled` changes nothing the engine sees and
    the parameter is here to say so."""
    exe = _kyverno()
    labels = {"policy-as-versioned.dev/governed": "true", "posture.acme.io/tier": "infra"}
    if entitled:
        labels["platform.acme.io/plane"] = "engine"
    for body in _delivered_bodies():
        tier = _rung(tmp_path, exe, body, labels)
        assert tier == "isolated", f"{body.relative_to(ESTATE)}: a governed `infra` rendered {tier!r}"


def test_tier_binding_grades_infra_as_the_isolated_it_renders(tmp_path):
    """The binding check's verdict names the rung the cage delivers, not a rung no cage has."""
    adopter = tmp_path / "adopter"
    (adopter / "gitops" / "apps").mkdir(parents=True)
    (adopter / "gitops" / "apps" / "namespace.yaml").write_text(
        "apiVersion: v1\nkind: Namespace\nmetadata:\n  name: x\n  labels:\n"
        '    policy-as-versioned.dev/governed: "true"\n    posture.acme.io/tier: "infra"\n')
    (tmp_path / "evidence.json").write_text(json.dumps({"prices": [
        {"source": "ico", "kind": "feed", "proposed_tier": "isolated", "changed": False}]}))
    run = subprocess.run(["python3", str(PLATFORM / "shift-left" / "tier_binding.py"), "check",
                          "--evidence", str(tmp_path / "evidence.json"),
                          "--adopter-dir", str(adopter)], capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "declares 'infra' (renders 'isolated'" in run.stdout, run.stdout



# --------------------------------------------------------------------------------------------
# B. a second governed Namespace document silenced the hub's walk at exit 0 (repaired, ticket 114)
# --------------------------------------------------------------------------------------------

NAMESPACE = """\
apiVersion: v1
kind: Namespace
metadata:
  name: {name}
  labels:
    policy-as-versioned.dev/governed: "true"
    posture.acme.io/tier: "{tier}"
"""
PRICE = {"source": "feeds", "kind": "feed", "name": "threat-register",
         "proposed_tier": "isolated", "changed": False}
WALK = HUB / "verify" / "tier-binding" / "tier_binding_estate.py"
WRAPPER = HUB / "verify" / "tier-binding" / "verify-tier-binding.sh"


def _plant(root: Path, ambiguous: str | tuple[str, ...] | None,
           parties: tuple[str, ...] = ("driftwood", "ludlow")) -> Path:
    """Bound parties against the REAL platform checkout. `ambiguous` names the party (or
    parties) that also declare a second governed Namespace."""
    named = (ambiguous,) if isinstance(ambiguous, str) else (ambiguous or ())
    estate = root / "estate"
    estate.mkdir()
    (estate / "platform").symlink_to(PLATFORM)
    for party in parties:
        apps = estate / party / "gitops" / "apps"
        apps.mkdir(parents=True)
        body = NAMESPACE.format(name=party, tier="isolated")
        if party in named:
            body += "---\n" + NAMESPACE.format(name=f"{party}-second", tier="baseline")
        (apps / "namespace.yaml").write_text(body)
        (estate / party / "composed").mkdir()
        (estate / party / "composed" / "evidence.json").write_text(json.dumps({"prices": [PRICE]}))
    return estate


def _walk(estate: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["python3", str(WALK), "check", "--estate-clone", str(estate)],
                          capture_output=True, text=True)


def _gate_reads(script: str, last_line: str) -> tuple[bool, str]:
    """What `talk/verify-all.sh` makes of an exit 3 from `script`: (declared?, why), judged by
    the gate's own manifest reader against the gate's own manifest."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("_t114_truth_manifest",
                                                  HUB / "talk" / "truth_manifest.py")
    assert spec is not None and spec.loader is not None
    tm = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = tm          # @dataclass resolves its module through sys.modules
    spec.loader.exec_module(tm)
    entries = tm.load_manifest(str(HUB / "talk" / "verify-manifest.txt"))
    declared, why = tm.judge(entries, script, last_line)
    return declared, why


def _last(run: subprocess.CompletedProcess) -> str:
    return run.stdout.strip().splitlines()[-1]


def test_the_hub_walk_passes_a_clean_planted_estate(tmp_path):
    """The control. Without it, leg B's exit 3 could be the walk refusing everything."""
    run = _walk(_plant(tmp_path, ambiguous=None))
    assert run.returncode == 0, run.stdout + run.stderr
    assert len(re.findall(r"^PASS: ", run.stdout, re.M)) == 2, run.stdout
    # platform is walked too, has nothing composed and claims no adopter role: it owes no
    # observation, so its SKIP line is named and does not hold the walk back
    assert re.search(r"^SKIP: platform: ", run.stdout, re.M), run.stdout


def test_a_second_governed_namespace_document_leaves_the_walk_could_not_look(tmp_path):
    """The finding, repaired. driftwood's binding goes unobserved while ludlow's passes. The
    walk used to exit 0 here, which `talk/verify-all.sh` grades PASS; it now exits 3 and its
    last line names driftwood."""
    run = _walk(_plant(tmp_path, ambiguous="driftwood"))
    assert "SKIP: driftwood: 2 governed Namespace declarations" in run.stdout, run.stdout
    assert re.search(r"^PASS: ludlow: ", run.stdout, re.M), run.stdout
    assert run.returncode == 3, run.stdout + run.stderr
    assert "driftwood" in _last(run) and "has not observed the estate whole" in _last(run), run.stdout


def test_the_gate_reads_the_unobserved_party_red_not_waits(tmp_path):
    """Exit 3 alone is not enough: the gate grades an exit 3 whose last line matches the
    manifest's declared `waits:` pattern as the estate not having arrived yet. An adopter that
    silences its own observation is not that, so the wrapper's last line must fall outside it."""
    estate = _plant(tmp_path, ambiguous="driftwood")
    import os
    run = subprocess.run(["bash", str(WRAPPER)], capture_output=True, text=True,
                         env={**os.environ, "ESTATE_CLONE": str(estate)})
    # the walk looked (a could-not-look for a missing instrument would also exit 3)
    assert re.search(r"^PASS: ludlow: ", run.stdout, re.M), run.stdout + run.stderr
    assert run.returncode == 3, run.stdout + run.stderr
    declared, why = _gate_reads("verify/tier-binding/verify-tier-binding.sh", _last(run))
    assert not declared, (why, _last(run))


def test_every_party_unobserved_is_not_the_declared_nothing_composed_skip(tmp_path):
    """Before ticket 114, when EVERY party was ambiguous the walk fell through to its 'no party
    has both' line, which the manifest declares as `waits:`. Both parties do have both."""
    run = _walk(_plant(tmp_path, ambiguous=("driftwood", "ludlow")))
    assert run.returncode == 3, run.stdout + run.stderr
    assert "no party in this estate has both" not in _last(run), run.stdout
    declared, why = _gate_reads("verify/tier-binding/verify-tier-binding.sh", _last(run))
    assert not declared, (why, _last(run))


def test_an_adopter_that_composes_nothing_is_still_owed_an_observation(tmp_path):
    """The other way out of the walk: an adopter-role party that drops its composed evidence.
    Its signed party.yaml still claims the adopter role, so it is owed an observation."""
    estate = _plant(tmp_path, ambiguous=None)
    shutil.rmtree(estate / "driftwood" / "composed")
    (estate / "driftwood" / "party.yaml").write_text(
        "party: driftwood\nroles: [risk-bearer, adopter, publisher]\n")
    run = _walk(estate)
    assert run.returncode == 3, run.stdout + run.stderr
    assert "driftwood" in _last(run), run.stdout


def test_a_fourth_adopter_outside_the_named_parties_is_walked(tmp_path):
    """The walk used to iterate a fixed tuple, so an adopter it did not name was never looked
    at. The role is signed in party.yaml, so it is read from there."""
    estate = _plant(tmp_path, ambiguous="newcomer", parties=("driftwood", "ludlow", "newcomer"))
    (estate / "newcomer" / "party.yaml").write_text("party: newcomer\nroles:\n  - adopter\n")
    run = _walk(estate)
    assert "SKIP: newcomer: 2 governed Namespace declarations" in run.stdout, run.stdout
    assert run.returncode == 3, run.stdout + run.stderr


def test_the_walk_selfcheck_plants_the_ambiguous_estate():
    """Item 2: the selfcheck holds the repair, so it cannot regress without the gate's own
    wrapper going red."""
    src = WALK.read_text(encoding="utf-8")
    body = src[src.index("def selfcheck"):]
    assert "second governed Namespace" in body, "no ambiguous-estate leg in the selfcheck"
    run = subprocess.run(["python3", str(WALK), "selfcheck", "--estate-clone", str(ESTATE)],
                         capture_output=True, text=True)
    assert run.returncode == 0, run.stdout + run.stderr
    assert "unobserved" in run.stdout, run.stdout


def test_verify_all_grades_a_script_by_its_exit_code_alone():
    """Why leg B's exit code is the whole finding: the gate never reads the per-party SKIP line."""
    gate = (HUB / "talk" / "verify-all.sh").read_text(encoding="utf-8")
    assert "exit 3" in gate and "SKIP" in gate
    walk = WALK.read_text(encoding="utf-8")
    assert "return 1 if failed else 0" not in walk, \
        "the walk folds per-party verdicts into 1-or-0 again -- a skipped party is lost"
