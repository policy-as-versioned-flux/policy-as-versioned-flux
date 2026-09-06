#!/usr/bin/env python3
"""Is every adopter's handbook a pure re-render of the artefact that adopter SERVES?

Eco-system ticket 34. ADR-0007's last-mile section, confirmed 2026-09-06 by ticket 80.

WHAT IS GRADED, AND AGAINST WHAT.

  The served artefact   each adopter's `composed/` tree at ONE named ref of that adopter's own
                        repository, read with `git ls-tree` / `git show`. Never a working tree:
                        a working copy is not what anybody installs. The ref is chosen and
                        PRINTED -- the newest signed tag whose tree carries a handbook, else
                        `origin/main` -- so a reader can see which bytes were graded.
  The operation         `handbook.py render <dir> --ref <ref>`, run from the copy of
                        `compose/handbook.py` that PLATFORM SERVES at the tag the adopter pins
                        (falling back to platform's `origin/main` and saying so). The grader
                        carries no renderer of its own. A hub copy would grade the hub's idea of
                        the render, not the estate's.
  The comparison        bytes. `git show <ref>:composed/HANDBOOK.md` against the re-render.

NO PROXIES. A file existing is not graded. A page that exists and does not re-render is exactly
the failure this check exists to catch, and it FAILs rather than skips. Two further properties are
proved on the real artefact every run, because a byte comparison alone could pass vacuously:

  purity        the same served bytes rendered twice, from a different working directory and
                under a scrambled environment, must produce identical output. If they do not,
                the render is not a function of the artefact and the comparison means nothing.
  sensitivity   one field of the served artefact, changed in memory, must change the render.
                A renderer that ignored its input would pass every byte comparison forever.

DISCLOSED LIMITS ARE NUMBERS HERE, NOT SENTENCES. Three counts are printed on every run and none
of them is asserted:

  * how many adopters serve a handbook at all;
  * how many are graded at a SIGNED TAG rather than at a branch tip -- "under the artefact's own
    tag" is the ticket's phrase, and until an adopter cuts a tag carrying a page, this check has
    not seen one, and says so with a number rather than a claim;
  * how many pin a platform tag that already carries `compose/handbook.py` -- until that pin
    moves, the page in the repository was produced by a human running the published tool rather
    than by the compose step itself.

Each of those heals itself: the day a tag is cut or a pin moves, the number moves with no edit
here. None of them is a pass condition, because none of them is this check's claim.

Exit 0 graded true; 1 graded false; 3 could not look, reason on the last line (ADR-0020).
"""
from __future__ import annotations

import copy
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RENDERER = "compose/handbook.py"
PAGE = "composed/HANDBOOK.md"
PLATFORM = "platform"


# ---------------------------------------------------------------- git plumbing


def git(repo: Path, *args: str) -> tuple[int, str]:
    done = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    return done.returncode, done.stdout


def has_path(repo: Path, ref: str, path: str) -> bool:
    return git(repo, "cat-file", "-e", f"{ref}:{path}")[0] == 0


def show(repo: Path, ref: str, path: str) -> str:
    rc, out = git(repo, "show", f"{ref}:{path}")
    if rc != 0:
        raise FileNotFoundError(f"{ref}:{path}")
    return out


def resolves(repo: Path, ref: str) -> bool:
    return git(repo, "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}")[0] == 0


def signed_tags(repo: Path) -> list[str]:
    """Tags that are annotated objects carrying a signature block. Newest tagger date last.

    This never claims a signature VERIFIES -- that is the gitsign verifier's job and it needs a
    network and trust material. It claims only that the tag object carries one, which is all this
    check reports (as a count)."""
    rc, out = git(repo, "for-each-ref", "refs/tags", "--sort=taggerdate",
                  "--format=%(refname:short) %(objecttype)")
    if rc != 0:
        return []
    found = []
    for line in out.splitlines():
        parts = line.split()
        if len(parts) != 2 or parts[1] != "tag":
            continue
        body = git(repo, "cat-file", "tag", parts[0])[1]
        if "-----BEGIN" in body:
            found.append(parts[0])
    return found


# ---------------------------------------------------------------- the estate


def adopters(estate: Path) -> list[Path]:
    """A party that composes for itself: it carries `composed/` and pins platform. Discovered,
    never listed -- a fourth adopter is graded the day it exists."""
    found = []
    for child in sorted(estate.iterdir()):
        if not (child / ".git").exists():
            continue
        if (child / "composed").is_dir() and (child / "gitops/platform/platform-pin.yaml").is_file():
            found.append(child)
    return found


def pinned_platform_tag(adopter: Path) -> str | None:
    """The platform tag this adopter's own pin file names. Read out of the pin, not guessed."""
    try:
        import yaml
        text = (adopter / "gitops/platform/platform-pin.yaml").read_text()
    except Exception:
        return None
    for doc in yaml.safe_load_all(text):
        if not isinstance(doc, dict):
            continue
        tag = ((doc.get("spec") or {}).get("ref") or {}).get("tag")
        if tag:
            return str(tag)
    return None


def served_ref(adopter: Path, override: str | None) -> tuple[str | None, str]:
    """Which ref of this adopter carries the page this check should grade, and how it was chosen.

    Newest signed tag that carries one wins: that is the ticket's "under the artefact's own tag".
    A branch tip is the honest fallback while no tag carries one, and the caller prints which."""
    if override:
        return (override, "named by PAVC_HANDBOOK_REFS") if resolves(adopter, override) else \
               (None, f"PAVC_HANDBOOK_REFS names {override}, which does not resolve")
    for tag in reversed(signed_tags(adopter)):
        if has_path(adopter, tag, PAGE):
            return tag, "the newest signed tag carrying a handbook"
    for ref in ("origin/main", "main", "HEAD"):
        if resolves(adopter, ref) and has_path(adopter, ref, PAGE):
            return ref, f"no signed tag carries a handbook; {ref} does"
    return None, "no signed tag and no branch tip of this repository carries composed/HANDBOOK.md"


def renderer_ref(platform: Path, pinned: str | None) -> tuple[str | None, str, bool]:
    """The ref of PLATFORM to take the renderer from, why, and whether it is the adopter's pin.

    The pin first, because that is what the adopter actually runs. Platform's own branch tip is
    the fallback, named as such, so this check keeps grading while the pin catches up."""
    if pinned and resolves(platform, pinned) and has_path(platform, pinned, RENDERER):
        return pinned, f"the platform tag this adopter pins ({pinned})", True
    # PAVC_HANDBOOK_PLATFORM_REF grades a platform BRANCH before it merges. Never set by the gate,
    # and it can never make a run look better than it is: the returned flag stays False, so the
    # "pinned tag already carries the renderer" count does not move for it.
    branch = os.environ.get("PAVC_HANDBOOK_PLATFORM_REF")
    if branch and resolves(platform, branch) and has_path(platform, branch, RENDERER):
        return branch, f"platform {branch}, named by PAVC_HANDBOOK_PLATFORM_REF", False
    for ref in ("origin/main", "main", "HEAD"):
        if resolves(platform, ref) and has_path(platform, ref, RENDERER):
            why = f"platform {ref}" + (
                f"; the pinned tag {pinned} does not carry {RENDERER} yet" if pinned else "")
            return ref, why, False
    return None, f"no ref of platform carries {RENDERER}", False


def _exec(path: Path, name: str):
    """Execute a python file and hand back the module. A spec or loader that comes back None is a
    real, reachable state -- an unreadable or non-importable path -- so it is raised by name rather
    than left to fail three lines later as an AttributeError nobody can read."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"{path} is not importable as python")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_renderer(platform: Path, ref: str, into: Path):
    """The SERVED renderer, executed from the bytes platform publishes at that ref."""
    target = into / "handbook.py"
    target.write_text(show(platform, ref, RENDERER))
    return _exec(target, "served_handbook")


def read_served(adopter: Path, ref: str) -> tuple[dict[str, str], dict]:
    """Every file of `composed/` at that ref, plus the parsed evidence document."""
    rc, out = git(adopter, "ls-tree", "-r", "--name-only", ref, "composed/")
    if rc != 0:
        raise FileNotFoundError(f"{ref}:composed/")
    files = {p: show(adopter, ref, p) for p in sorted(out.split()) if p.strip()}
    return files, json.loads(files["composed/evidence.json"])


# ---------------------------------------------------------------- the grading


def grade_one(adopter: Path, platform: Path, override: str | None, work: Path) -> dict:
    """One adopter, one verdict. `state` is one of pass / fail / skip."""
    name = adopter.name
    ref, why_ref = served_ref(adopter, override)
    if ref is None:
        return {"name": name, "state": "skip", "line": f"{name}: {why_ref}"}

    pinned = pinned_platform_tag(adopter)
    rref, why_renderer, on_pin = renderer_ref(platform, pinned)
    if rref is None:
        return {"name": name, "state": "skip", "line": f"{name}: {why_renderer}"}

    try:
        module = load_renderer(platform, rref, work)
        files, evidence = read_served(adopter, ref)
    except Exception as exc:                                    # noqa: BLE001
        return {"name": name, "state": "skip",
                "line": f"{name}: could not read the served artefact or renderer at "
                        f"{ref}/{rref}: {exc}"}

    tag_graded = ref in signed_tags(adopter)
    common = {"name": name, "ref": ref, "why_ref": why_ref, "renderer_ref": rref,
              "why_renderer": why_renderer, "on_pin": on_pin, "tag_graded": tag_graded}

    try:
        rendered = module.render(dict(files), evidence)
    except Exception as exc:                                    # noqa: BLE001
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the served artefact does not render: {exc}"}

    served = files.get(PAGE)
    if served is None:
        return {**common, "state": "skip", "line": f"{name}@{ref}: serves no {PAGE}"}

    if rendered != served:
        n = sum(1 for a, b in zip(rendered.splitlines(), served.splitlines()) if a != b)
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: {PAGE} is NOT what its own served artefact renders to "
                        f"({n} line(s) differ, {len(served)} bytes served vs {len(rendered)} "
                        f"re-rendered) -- the page says something the artefact does not"}

    # PURITY. Same bytes in, same bytes out, from elsewhere and under another environment.
    saved_env, saved_cwd = dict(os.environ), os.getcwd()
    try:
        os.chdir(work)
        os.environ.update({"TZ": "Pacific/Kiritimati", "LANG": "C", "PAVC_NOISE": "1"})
        again = module.render(copy.deepcopy(dict(files)), copy.deepcopy(evidence))
    finally:
        os.chdir(saved_cwd)
        os.environ.clear()
        os.environ.update(saved_env)
    if again != rendered:
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the render is not a pure function of the artefact -- the "
                        "same served bytes rendered differently from another directory under "
                        "another environment, so the byte comparison above proves nothing"}

    # SENSITIVITY. A renderer that ignored its input would pass every comparison forever.
    moved, what = _mutate(files, evidence)
    if moved is None:
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: this artefact carries no field the grader knows how to "
                        "move, so the byte comparison could not be shown to bite"}
    if module.render(*moved) == rendered:
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: changing {what} in the served artefact did NOT change the "
                        "render, so the page is not derived from the artefact it sits beside"}

    return {**common, "state": "pass",
            "line": f"{name}@{ref}: {len(served)} bytes, byte-identical to a re-render of the "
                    f"artefact served at the same ref; pure across cwd and environment; moving "
                    f"{what} moves the page"}


def _mutate(files: dict[str, str], evidence: dict) -> tuple[tuple | None, str]:
    """One graded field of the served artefact, changed. Returns the mutated inputs and its name."""
    f2, e2 = copy.deepcopy(dict(files)), copy.deepcopy(evidence)
    prices = e2.get("prices") or []
    if prices and isinstance(prices[0].get("amount"), (int, float)):
        prices[0]["amount"] = prices[0]["amount"] + 4242.42
        return (f2, e2), f"prices[0].amount (+4242.42)"
    limits = e2.get("limits") or []
    if limits:
        limits[0]["status"] = "moved-by-the-grader"
        return (f2, e2), "limits[0].status"
    return None, ""


# ---------------------------------------------------------------- entry points


def run(estate: Path, overrides: dict[str, str]) -> int:
    platform = estate / PLATFORM
    if not (platform / ".git").exists():
        print(f"SKIP: {estate}/{PLATFORM} is not a git checkout, so the served renderer "
              f"({RENDERER}) cannot be read from any ref")
        return 3
    found = adopters(estate)
    if not found:
        print(f"SKIP: no party under {estate} carries both composed/ and a platform pin, so there "
              "is no adopter artefact to grade a handbook against")
        return 3

    results = []
    with tempfile.TemporaryDirectory() as td:
        for adopter in found:
            r = grade_one(adopter, platform, overrides.get(adopter.name), Path(td))
            results.append(r)
            mark = {"pass": "  ok  ", "fail": "FAIL: ", "skip": "  ??  "}[r["state"]]
            print(f"{mark} {r['line']}")
            if r["state"] != "skip" and r.get("why_ref"):
                print(f"         ref chosen: {r['why_ref']}; renderer from {r['why_renderer']}")

    passes = [r for r in results if r["state"] == "pass"]
    fails = [r for r in results if r["state"] == "fail"]
    graded = passes + fails
    tagged = [r for r in graded if r.get("tag_graded")]
    on_pin = [r for r in graded if r.get("on_pin")]

    # The three disclosed limits, as numbers, every run, whatever the verdict.
    print(f"COUNTS: {len(graded)} of {len(found)} adopter(s) serve a handbook this check could "
          f"read; {len(tagged)} of {len(graded)} graded at a signed tag rather than a branch tip; "
          f"{len(on_pin)} of {len(graded)} pin a platform tag that already carries {RENDERER}.")

    if fails:
        print(f"FAILED: {len(fails)} adopter(s): " + ", ".join(r["name"] for r in fails))
        return 1
    if not passes:
        print(f"SKIP: no adopter of the {len(found)} in this estate serves a handbook this check "
              f"could read, so nothing was compared -- {'; '.join(r['line'] for r in results)}")
        return 3
    print(f"SUMMARY: {len(passes)} adopter(s) ({', '.join(r['name'] for r in passes)}) each serve "
          f"a composed/HANDBOOK.md that is byte-identical to a re-render of the artefact served at "
          f"the same ref, by the renderer platform serves; the render is pure across directory and "
          f"environment and moves when the artefact moves; {len(tagged)} of them graded at a signed "
          f"tag; {len(on_pin)} of them pin a platform tag carrying {RENDERER}")
    return 0


# ---------------------------------------------------------------- selfcheck


def _plant(root: Path, renderer_src: Path) -> Path:
    """A throwaway estate: one platform carrying the real renderer, one adopter carrying a real
    artefact and its render. Nothing here is the estate; this is the grader's own ruler."""
    estate = root / "estate"
    plat = estate / PLATFORM
    (plat / "compose").mkdir(parents=True)
    (plat / RENDERER).write_text(renderer_src.read_text())
    _repo(plat, "the renderer")

    hb = _exec(plat / RENDERER, "hb_fixture")
    files, evidence = hb._fixture()
    files[hb.EVIDENCE_PATH] = json.dumps(evidence, indent=2)

    adopter = estate / "planted"
    for rel, text in files.items():
        p = adopter / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    (adopter / PAGE).write_text(hb.render(files, evidence))
    pin = adopter / "gitops/platform/platform-pin.yaml"
    pin.parent.mkdir(parents=True, exist_ok=True)
    pin.write_text("apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\n"
                   "spec:\n  ref:\n    tag: planted-platform-v1\n")
    _repo(adopter, "the artefact and its render")
    return estate


def _repo(path: Path, message: str) -> None:
    """A repository whose refs exist. The runner's own git configuration is deliberately not
    inherited: a machine that force-signs every tag or runs a global pre-commit hook has nothing
    to do with what is graded here."""
    subprocess.run(["git", "-C", str(path), "init", "-q", "-b", "main"], check=True)
    hooks = path / ".nohooks"
    hooks.mkdir()
    for k, v in (("core.hooksPath", str(hooks)), ("commit.gpgsign", "false"),
                 ("tag.gpgSign", "false"), ("tag.forceSignAnnotated", "false"),
                 ("user.name", "t"), ("user.email", "t@t.invalid")):
        subprocess.run(["git", "-C", str(path), "config", k, v], check=True)
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", message], check=True)


def _commit(path: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", message], check=True)


def selfcheck(renderer_src: Path) -> int:
    """The grader's rules, on planted inputs. A grader only ever run against artefacts that agree
    has proved nothing about what it does when they do not."""
    ok = 0

    def check(claim: str, cond: bool) -> None:
        nonlocal ok
        if not cond:
            print(f"FAIL: selfcheck: {claim}")
            raise SystemExit(1)
        ok += 1
        print(f"  ok   {claim}")

    import io
    import contextlib

    def graded(estate: Path, overrides=None) -> tuple[int, str]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = run(estate, overrides or {})
        return rc, buf.getvalue()

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        estate = _plant(root, renderer_src)
        adopter = estate / "planted"

        rc, out = graded(estate)
        check("a page that re-renders from its own served artefact grades 0",
              rc == 0 and "SUMMARY:" in out)
        check("the counts are printed even on a pass", "COUNTS:" in out)
        check("a branch tip, not a tag, is named as such",
              "0 of 1 graded at a signed tag" in out)

        # a hand-edited page
        page = adopter / PAGE
        keep = page.read_text()
        page.write_text(keep + "\nThe estate has no holes and everything is fine.\n")
        _commit(adopter, "hand-edit the page")
        rc, out = graded(estate)
        check("a sentence added to the page by hand grades 1",
              rc == 1 and "is NOT what its own served artefact renders to" in out)

        # a moved artefact under an unmoved page
        page.write_text(keep)
        ev = adopter / "composed/evidence.json"
        doc = json.loads(ev.read_text())
        doc["prices"][0]["amount"] = 999999.0
        ev.write_text(json.dumps(doc, indent=2))
        _commit(adopter, "move the price, leave the page")
        rc, out = graded(estate)
        check("a price that moved under an unmoved page grades 1",
              rc == 1 and "is NOT what its own served artefact renders to" in out)

        # A renderer that IGNORES its input and returns a constant equal to the committed page.
        # The byte comparison passes -- that is the point -- so only the sensitivity leg can catch
        # it. Put back the artefact the page was rendered from first, so the comparison really
        # does pass and the red that follows can only have come from sensitivity.
        subprocess.run(["git", "-C", str(adopter), "checkout", "-q", "HEAD~2", "--",
                        "composed/evidence.json"], check=True)
        _commit(adopter, "back to the artefact the page was rendered from")
        plat = estate / PLATFORM
        src = (plat / RENDERER).read_text()
        (plat / RENDERER).write_text(
            src.replace("def render(files: Mapping[str, str], evidence: Mapping[str, Any]) -> str:",
                        "_CONSTANT = " + repr(keep) + "\n\n\n"
                        "def render(files: Mapping[str, str], evidence: Mapping[str, Any]) -> str:\n"
                        "    return _CONSTANT\n\n\n"
                        "def _unused(files: Mapping[str, str], evidence: Mapping[str, Any]) -> str:",
                        1))
        _commit(plat, "a renderer that ignores its input")
        rc, out = graded(estate)
        check("a renderer that ignores its input is caught by the sensitivity leg, not the byte "
              "comparison", rc == 1 and "did NOT change the render" in out)
        (plat / RENDERER).write_text(src)
        _commit(plat, "restore the renderer")
        rc, out = graded(estate)
        check("...and with the real renderer back, the same artefact grades 0 again", rc == 0)

        # nothing serves a page
        subprocess.run(["git", "-C", str(adopter), "rm", "-q", PAGE], check=True)
        _commit(adopter, "no page here")
        rc, out = graded(estate)
        check("an estate where nothing serves a page grades 3, never 0",
              rc == 3 and out.strip().splitlines()[-1].startswith("SKIP:"))

        # no renderer anywhere
        (plat / RENDERER).unlink()
        _commit(plat, "no renderer")
        rc, out = graded(estate)
        check("an estate whose platform serves no renderer grades 3, never 0",
              rc == 3 and "SKIP:" in out)

    print(f"PASS: selfcheck: {ok} planted cases -- a fresh page passes, a hand-edited page fails, "
          "an artefact that moved under an unmoved page fails, a renderer that ignores its input "
          "is caught by sensitivity rather than by the byte comparison, and both a missing page "
          "and a missing renderer exit 3 rather than 0")
    return 0


def main(argv: list[str]) -> int:
    if "--selfcheck" in argv:
        i = argv.index("--selfcheck")
        return selfcheck(Path(argv[i + 1]))
    estate = Path(argv[1])
    overrides = {}
    for pair in (os.environ.get("PAVC_HANDBOOK_REFS") or "").split(","):
        if "=" in pair:
            unit, _, ref = pair.partition("=")
            overrides[unit.strip()] = ref.strip()
    return run(estate, overrides)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
