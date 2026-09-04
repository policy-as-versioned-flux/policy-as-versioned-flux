#!/usr/bin/env python3
"""branch_refs.py — eco-system tickets 62 and 77 made checkable: no unit checks another
organisation out at a branch, and every cross-organisation checkout names a tag one of the
consuming repository's OWN pin records declares.

NORTH-STAR §2 says a parent is "consumed only through a pinned, signed dependency". Until
2026-09-04 that was true of the policy artefact and of almost nothing else: twelve checkouts in
tuppence and ludlow named `ecosystem/thin-slice`, a branch ticket 57 had deleted, so their
propose-tier, shift-left and cut-release clocks died at fetch; nine more in driftwood named
`main`; and ico, feeds and insurer checked the platform out with no `ref:` at all. A signature
lives on a tag. A branch has none, and it can be moved or deleted under the consumer, which is
what happened.

What this grades, for every `actions/checkout` step in every `.github/workflows/*.yml` under the
estate clone whose `repository:` names a DIFFERENT policy-as-versioned organisation:

  no `ref:` at all           FAIL -- the checkout is the publisher's default branch.
  a literal that is a tag
  on the publisher's clone   PASS -- pinned to a signed tag.
  a literal that is not      FAIL -- a branch, or a tag that does not exist on the publisher.
  a ${{ }} expression        the consuming repository must DECLARE which version of that
                             publisher it is on, in a GitRepository pin file under gitops/
                             whose spec.url is the publisher's, or in a `<PUBLISHER>_TAG:`
                             env constant in the same workflow. PASS when the declared tag
                             exists on the publisher's clone; FAIL when nothing declares it,
                             or when what is declared is not a tag the publisher has cut.

  a publisher with NO tags   SKIP. There is no tag to pin to, so the consumer cannot be asked
                             for one; the reason names the publisher. Today that is the hub
                             (driftwood's twin-sweep.yml), which ticket 64 owns.
  a publisher this checkout
  does not carry             SKIP -- the clone cannot be looked at, never a pass.

The rule deliberately does NOT try to follow a `${{ steps.x.outputs.y }}` back to the step that
set it: a workflow expression is evaluated by GitHub and not by this script, and pretending to
resolve it would be a guess. What is checkable offline is the fact the expression must be built
from -- a pin, in this repository, naming a tag that exists -- and that is what is graded. The
commit half of each {tag, commit} pair is asserted on the runner by each unit's own
.github/scripts/verify-pinned-checkouts.py, which is where the runner's real HEAD can be read.

Prints one line per check. Exit precedence: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    branch_refs.py check        # the estate under .estate-clone (or $PAVC_ESTATE_CLONE)
    branch_refs.py selfcheck    # planted fixtures: proves each refusal bites
"""
from __future__ import annotations

import glob
import os
import re
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

LINES: list[str] = []
MSGS: list[str] = []
ORG = re.compile(r"^policy-as-versioned-([a-z-]+)/([A-Za-z0-9._-]+)$")
EXPR = re.compile(r"\$\{\{.*\}\}")
SEEN = {"workflows": 0, "cross-org checkouts": 0}


def out(status: str, msg: str) -> None:
    LINES.append(status)
    MSGS.append(f"{status}: {msg}")
    print(f"{status}: {msg}")


# --------------------------------------------------------------------------
# what a unit repository DECLARES about a publisher
# --------------------------------------------------------------------------
def pinned_tags(unit_dir: str) -> dict[str, set[str]]:
    """{publisher: tags this repository's own GitRepository pin files name}. The pin files are
    the estate's one declared shape for "which signed version of X am I on" -- platform-pin.yaml,
    gotk-sync-nist.yaml and, since ticket 62, gotk-sync-{ico,feeds,insurer}.yaml."""
    found: dict[str, set[str]] = {}
    for path in sorted(glob.glob(os.path.join(unit_dir, "gitops", "**", "*.yaml"), recursive=True)):
        try:
            with open(path) as fh:
                docs = [d for d in yaml.safe_load_all(fh) if isinstance(d, dict)]
        except (OSError, yaml.YAMLError):
            continue
        for doc in docs:
            if doc.get("kind") != "GitRepository":
                continue
            ref = (doc.get("spec") or {}).get("ref") or {}
            m = ORG.match(str((doc.get("spec") or {}).get("url", "")).removeprefix("https://github.com/"))
            if m and ref.get("tag"):
                found.setdefault(m.group(1), set()).add(str(ref["tag"]))
    return found


def env_tags(workflow_text: str) -> dict[str, str]:
    """{publisher: tag} from `<PUBLISHER>_TAG:` constants in a workflow's own env block -- the
    shape ico's and feeds' release.yml use, beside GITSIGN_VERSION, because neither repository
    runs a cluster or carries a renovate.json for a pin file to be worth."""
    return {m.group(1).lower().replace("_", "-"): m.group(2)
            for m in re.finditer(r"^\s*([A-Z][A-Z0-9_]*)_TAG:\s*(\S+)\s*$", workflow_text, re.M)}


# --------------------------------------------------------------------------
# what a publisher has actually signed
# --------------------------------------------------------------------------
_TAGS: dict[str, set[str] | None] = {}
# The hub is a ninth repository and clone-estate.sh does not clone it into the estate: it IS the
# checkout the gate runs from. driftwood's twin-sweep.yml consumes it, so it is graded like any
# other publisher, off this working copy's own tags.
HUB = os.path.normpath(os.path.join(HERE, "..", ".."))


def clone_tags(estate: str, party: str) -> set[str] | None:
    """Tags in the estate checkout of the publisher; None when this checkout has no clone of
    it at all. Local, because clone-estate.sh fetches tags on purpose (see its own comment on
    --depth 1) and a check that shells out to the network per checkout would be minutes long."""
    if party not in _TAGS:
        repo = HUB if party == "flux" else os.path.join(estate, party)
        # `git tag`, not a test for a .git DIRECTORY: a builder's estate is symlinked at nested
        # worktrees whose .git is a file, and testing for the directory made every unit look
        # unclonable and turned the whole run into could-not-look.
        if not os.path.isdir(repo):
            _TAGS[party] = None
        else:
            r = subprocess.run(["git", "-C", repo, "tag"], capture_output=True, text=True, timeout=60)
            _TAGS[party] = set(r.stdout.split()) if r.returncode == 0 else None
    return _TAGS[party]


# --------------------------------------------------------------------------
# reading the checkouts out of a workflow
# --------------------------------------------------------------------------
def checkouts(doc: dict) -> list[dict]:
    """Every actions/checkout step's `with:` mapping in a parsed workflow."""
    steps = []
    for job in (doc.get("jobs") or {}).values():
        if not isinstance(job, dict):
            continue
        for step in job.get("steps") or []:
            if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/checkout@"):
                steps.append(step.get("with") or {})
    return steps


def grade(estate: str, unit: str, wf_name: str, with_: dict, declared: dict[str, set[str]],
          env: dict[str, str]) -> None:
    repo = str(with_.get("repository", ""))
    m = ORG.match(repo)
    if not m or m.group(1) == unit:
        return  # this repository's own checkout, or a third-party action's
    party = m.group(1)
    SEEN["cross-org checkouts"] += 1
    label = f"{unit}/{wf_name} checks out {repo}"
    tags = clone_tags(estate, party)
    if tags is None:
        out("SKIP", f"{label}: this checkout carries no clone of {party}, so what it pins "
                    f"cannot be looked at"); return
    if not tags:
        out("SKIP", f"{label}: {party} has cut no tag at all, so there is no signed version to "
                    f"pin to -- the consumer is not at fault and this is not a pass"); return

    ref = with_.get("ref")
    if ref is None:
        out("FAIL", f"{label} with no `ref:` -- that is {party}'s default branch, which carries "
                    f"no signature and can move under this consumer"); return
    ref = str(ref)
    if not EXPR.search(ref):
        if ref in tags:
            out("PASS", f"{label} at the literal tag {ref}")
        else:
            out("FAIL", f"{label} at {ref!r}, which is not a tag {party} has signed -- a branch "
                        f"is not a pinned, signed dependency")
        return
    names = declared.get(party, set()) | ({env[party]} if party in env else set())
    if not names:
        out("FAIL", f"{label} at a computed ref, and nothing in {unit} declares which version of "
                    f"{party} it is on -- no GitRepository pin under gitops/ and no "
                    f"{party.upper()}_TAG in this workflow"); return
    unsigned = sorted(n for n in names if n not in tags)
    if unsigned:
        out("FAIL", f"{label} at a computed ref, and {unit} pins {party} at "
                    f"{', '.join(unsigned)}, which {party} has not signed")
    else:
        out("PASS", f"{label} at the tag {unit} pins it to ({', '.join(sorted(names))})")


def run(estate: str) -> None:
    for k in SEEN:
        SEEN[k] = 0
    _TAGS.clear()
    units = sorted(os.path.basename(p) for p in glob.glob(os.path.join(estate, "*"))
                   if os.path.isdir(p))
    if not units:
        out("FAIL", f"no unit under {estate}: absence is not a pass"); return
    for unit in units:
        declared = pinned_tags(os.path.join(estate, unit))
        for wf in sorted(glob.glob(os.path.join(estate, unit, ".github", "workflows", "*.yml"))):
            try:
                with open(wf) as fh:
                    text = fh.read()
                doc = yaml.safe_load(text)
            except (OSError, yaml.YAMLError) as e:
                out("FAIL", f"{unit}/{os.path.basename(wf)}: unreadable ({e})"); continue
            if not isinstance(doc, dict):
                continue
            SEEN["workflows"] += 1
            env = env_tags(text)
            for with_ in checkouts(doc):
                grade(estate, unit, os.path.basename(wf), with_, declared, env)
    for k, n in SEEN.items():
        if not n:
            out("FAIL", f"no {k} observed under {estate}: absence is not a pass")


def exit_code() -> int:
    return 1 if "FAIL" in LINES else 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
def selfcheck() -> None:
    """Plant an estate of workflow fixtures and prove each refusal bites."""
    def wf(steps):
        return "name: x\non: push\njobs:\n  j:\n    steps:\n" + steps

    with tempfile.TemporaryDirectory() as tmp:
        def unit(name, tags):
            d = os.path.join(tmp, name)
            os.makedirs(os.path.join(d, ".github", "workflows"), exist_ok=True)
            subprocess.run(["git", "init", "-q", "-b", "main", d], check=True)
            for cfg in (["user.email", "s@e"], ["user.name", "s"]):
                subprocess.run(["git", "-C", d, "config"] + cfg, check=True)
            open(os.path.join(d, "seed"), "w").write("x")
            subprocess.run(["git", "-C", d, "add", "seed"], check=True)
            subprocess.run(["git", "-C", d, "commit", "-qm", "seed"], check=True)
            for t in tags:
                subprocess.run(["git", "-C", d, "-c", "tag.gpgSign=false", "tag", "-a", "-m", t, t], check=True)
            return d

        ico = unit("ico", ["v3.0.0"])
        hub = unit("hub", [])
        adopter = unit("driftwood", ["v1.1.0"])
        os.makedirs(os.path.join(adopter, "gitops", "flux-system"))
        open(os.path.join(adopter, "gitops", "flux-system", "gotk-sync-ico.yaml"), "w").write(
            "apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\n"
            "metadata: {name: ico}\nspec:\n"
            "  url: https://github.com/policy-as-versioned-ico/ico\n"
            "  ref:\n    tag: v3.0.0\n    commit: " + "a" * 40 + "\n")
        step = ("      - uses: actions/checkout@v4\n        with:\n"
                "          repository: policy-as-versioned-{p}/{p}\n{ref}")
        def w(name, body):
            open(os.path.join(adopter, ".github", "workflows", name), "w").write(wf(body))

        w("a-pinned-expression.yml", step.format(
            p="ico", ref="          ref: ${{ steps.pins.outputs.ico_tag }}\n"))
        w("b-branch.yml", step.format(p="ico", ref="          ref: main\n"))
        w("c-no-ref.yml", step.format(p="ico", ref=""))
        w("d-literal-tag.yml", step.format(p="ico", ref="          ref: v3.0.0\n"))
        w("e-untagged-publisher.yml", step.format(p="hub", ref="          ref: main\n"))
        w("f-own-repo.yml", step.format(p="driftwood", ref="          ref: main\n"))
        w("g-no-clone.yml", step.format(p="nowhere", ref="          ref: main\n"))

        LINES.clear(); MSGS.clear()
        run(tmp)
        by_file = {}
        for line in MSGS:
            m = re.search(r"(?:^|\s)driftwood/([a-z-]+\.yml)", line)
            if m:
                by_file[m.group(1)] = line
        want = {"a-pinned-expression.yml": "PASS", "b-branch.yml": "FAIL", "c-no-ref.yml": "FAIL",
                "d-literal-tag.yml": "PASS", "e-untagged-publisher.yml": "SKIP",
                "g-no-clone.yml": "SKIP"}
        for name, status in want.items():
            assert name in by_file, f"{name} was never graded: {MSGS}"
            assert by_file[name].startswith(status), f"{name}: {by_file[name]}"
        assert "f-own-repo.yml" not in by_file, "a repository's own checkout is not cross-org"
        assert "no `ref:`" in by_file["c-no-ref.yml"]
        assert "not a tag" in by_file["b-branch.yml"]
        assert "cut no tag at all" in by_file["e-untagged-publisher.yml"]
        assert exit_code() == 1, LINES

        # an expression with NO pin behind it, and a pin naming a tag the publisher never cut
        for name in list(os.listdir(os.path.join(adopter, ".github", "workflows"))):
            os.remove(os.path.join(adopter, ".github", "workflows", name))
        w("h-undeclared.yml", step.format(
            p="hub", ref="          ref: ${{ steps.pins.outputs.hub_tag }}\n"))
        subprocess.run(["git", "-C", hub, "-c", "tag.gpgSign=false", "tag", "-a", "-m", "t", "v9.0.0"], check=True)
        LINES.clear(); MSGS.clear(); run(tmp)
        assert any("nothing in driftwood declares which version of hub" in m for m in MSGS), MSGS

        pin = os.path.join(adopter, "gitops", "flux-system", "gotk-sync-ico.yaml")
        moved = open(pin).read().replace("tag: v3.0.0", "tag: v4.0.0")
        open(pin, "w").write(moved)
        for name in os.listdir(os.path.join(adopter, ".github", "workflows")):
            os.remove(os.path.join(adopter, ".github", "workflows", name))
        w("i-pin-not-signed.yml", step.format(
            p="ico", ref="          ref: ${{ steps.pins.outputs.ico_tag }}\n"))
        LINES.clear(); MSGS.clear(); run(tmp)
        assert any("pins ico at v4.0.0, which ico has not signed" in m for m in MSGS), MSGS

        # an empty estate is not a pass
        LINES.clear(); MSGS.clear()
        empty = os.path.join(tmp, "empty"); os.makedirs(empty)
        run(empty)
        assert LINES and set(LINES) == {"FAIL"}, LINES

        # an env constant declares the pin where a repository carries no gitops/ pin file
        assert env_tags("env:\n  PLATFORM_TAG: v2.0.1\n  GITSIGN_VERSION: 1\n") == {"platform": "v2.0.1"}

    LINES.clear(); MSGS.clear()
    print("ok  selfcheck: a computed ref backed by a pin and a literal tag pass; a branch, a "
          "missing ref, an undeclared computed ref and a pin naming an unsigned tag all refuse; "
          "an untagged publisher, a missing clone and an empty estate are never a pass")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck(); sys.exit(0)
    run(os.environ.get("PAVC_ESTATE_CLONE") or ESTATE)
    sys.exit(exit_code())
