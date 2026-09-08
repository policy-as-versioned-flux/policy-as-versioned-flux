#!/usr/bin/env python3
"""Is every adopter's handbook a pure re-render of the artefact that adopter SERVES?

Eco-system ticket 34. ADR-0007's last-mile section, confirmed 2026-09-06 by ticket 80.
Review 2026-09-08 (F-06, F-08, F-09, F-10) narrowed what is read and what is claimed.

WHAT IS GRADED, AND AGAINST WHAT.

  The served artefact   each adopter's `composed/` tree at NAMED REFS of that adopter's own
                        repository, read with `git ls-tree` / `git show`. Never a working tree
                        and never a local branch: a working copy is not what anybody installs,
                        and a local `main` is whatever this checkout last had. Two refs are
                        graded for each adopter and both are printed: `origin/main`, and the
                        newest signed tag whose tree carries a page (when one exists). Grading
                        the tag alone would freeze this check on the first tag ever cut and
                        never look at the branch again.
  The operation         `render()` from the copy of `compose/handbook.py` that PLATFORM SERVES
                        at the tag the adopter's SERVED pin names, read with `git show` at the
                        graded ref; platform's `origin/main` otherwise, and the run says which.
                        The grader carries no renderer of its own: a hub copy would grade the
                        hub's idea of the render, not the estate's.
  The comparison        bytes. `git show <ref>:composed/HANDBOOK.md` against the re-render.

NO PROXIES. A file existing is not graded. A page that exists and does not re-render is exactly
the failure this check exists to catch, and it FAILs rather than skips. Three further properties
are proved on the real artefact every run, because a byte comparison alone could pass vacuously:

  purity        the same served bytes rendered again in a SEPARATE PROCESS -- environment
                emptied, a random PYTHONHASHSEED, a fresh working directory -- must produce
                identical output. An in-process second render shared HOME, the hostname, every
                module-level cache and the interpreter's hash seed with the first, so it could
                not see a renderer reading any of them (review F-06).
  source        the served renderer's code names none of `open`, `os`, `sys`, `socket`,
                `time`, `datetime`, `subprocess` (and the rest of FORBIDDEN_ROOTS) in module-level
                functions called by name from `render()`, and the module imports none of those
                modules at module level under any alias. This is a scan of the source text
                platform serves, and it is what the check TRUSTS beyond the process test: a
                renderer that reads `/etc/hosts` renders the same bytes in every process on one
                machine, so only reading its code catches it. It is a text scan and it does not
                see import-time bindings that need no import: `functools.partial(open, ...)` and
                a lambda in a module-level dict both escape it (round-2 review R2-02, measured
                in the selfcheck), and the PASS line says so.
  execution     a renderer platform serves at the ref that does not execute (ImportError,
                SyntaxError) is a FAIL, not a could-not-look: the artefact was read; the tool
                the estate publishes is what is broken (round-2 review R2-03).
  sensitivity   one field of the served artefact, changed in memory, must change the render.
                A renderer that ignored its input would pass every byte comparison forever.

DISCLOSED LIMITS ARE NUMBERS HERE, NOT SENTENCES. Three counts are printed on every run and none
of them is asserted:

  * how many adopters serve a handbook at `origin/main`;
  * how many ALSO serve one at a signed tag, graded as well -- "under the artefact's own tag" is
    the ticket's phrase, and until an adopter cuts such a tag this check has not seen one;
  * how many pin, at `origin/main`, a platform tag that already carries `compose/handbook.py` --
    until that pin moves, the page in the repository was produced by a human running the
    published tool, `composition.py verify` at that pin does not compare it, and
    `cut-release.yml` at that pin would sign a hand-edited page.

`signed_tags()` counts tag objects carrying a signature block; it verifies nothing (that is the
gitsign verifier's job and needs a network and trust material), and the count says so.

Exit 0 graded true; 1 graded false; 3 could not look, reason on the last line (ADR-0020).
"""
from __future__ import annotations

import ast
import copy
import importlib.util
import json
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

RENDERER = "compose/handbook.py"
PAGE = "composed/HANDBOOK.md"
PIN = "gitops/platform/platform-pin.yaml"
PLATFORM = "platform"
SERVED_BRANCH = "origin/main"

# What the source scan refuses to see reachable from render(): a bare name, or the root of an
# attribute chain. `os` covers os.environ, os.getcwd, os.path and every other read of the machine.
FORBIDDEN_NAMES = {"open", "input", "__import__", "exec", "eval"}
FORBIDDEN_ROOTS = {"os", "sys", "socket", "time", "datetime", "subprocess", "random", "pathlib",
                   "Path", "importlib", "urllib", "http", "requests", "shutil", "glob", "io"}


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
    """A party that composes for itself: at its SERVED branch it carries `composed/` and pins
    platform. Discovered from `origin/main`, never from the working tree (review F-08), and
    never listed -- a fourth adopter is graded the day it exists."""
    found = []
    for child in sorted(estate.iterdir()):
        if not (child / ".git").exists() or not resolves(child, SERVED_BRANCH):
            continue
        if has_path(child, SERVED_BRANCH, "composed") and has_path(child, SERVED_BRANCH, PIN):
            found.append(child)
    return found


def pinned_platform_tag(adopter: Path, ref: str) -> str | None:
    """The platform tag the pin file SERVED at `ref` names. Read out of `git show`, not a
    working copy, so the count of pins carrying the renderer is about what is served."""
    try:
        import yaml
        text = show(adopter, ref, PIN)
    except Exception:
        return None
    for doc in yaml.safe_load_all(text):
        if not isinstance(doc, dict):
            continue
        tag = ((doc.get("spec") or {}).get("ref") or {}).get("tag")
        if tag:
            return str(tag)
    return None


def served_refs(adopter: Path, override: str | None) -> tuple[list[tuple[str, str, bool]], str]:
    """The refs of this adopter to grade, each with why and whether it is a signed tag.

    `origin/main` always, when it carries a page; plus the newest signed tag carrying one, so a
    tag once cut does not stop the branch being read (review F-10). No local `main`, no `HEAD`
    (review F-08). An override names exactly one ref and replaces both."""
    if override:
        if not resolves(adopter, override):
            return [], f"PAVC_HANDBOOK_REFS names {override}, which does not resolve"
        if not has_path(adopter, override, PAGE):
            return [], f"PAVC_HANDBOOK_REFS names {override}, which serves no {PAGE}"
        return [(override, "named by PAVC_HANDBOOK_REFS", override in signed_tags(adopter))], ""
    refs: list[tuple[str, str, bool]] = []
    if not resolves(adopter, SERVED_BRANCH):
        return [], f"this checkout has no {SERVED_BRANCH} to read the served artefact at"
    if has_path(adopter, SERVED_BRANCH, PAGE):
        refs.append((SERVED_BRANCH, f"the served branch {SERVED_BRANCH}", False))
    for tag in reversed(signed_tags(adopter)):
        if has_path(adopter, tag, PAGE):
            refs.append((tag, "the newest signed tag carrying a handbook", True))
            break
    if not refs:
        return [], f"neither {SERVED_BRANCH} nor any signed tag of this repository carries {PAGE}"
    return refs, ""


def renderer_ref(platform: Path, pinned: str | None) -> tuple[str | None, str, bool]:
    """The ref of PLATFORM to take the renderer from, why, and whether it is the adopter's pin.

    The pin first, because that is what the adopter actually runs. Platform's served branch is
    the only fallback (review F-08), named as such, so this check keeps grading while the pin
    catches up."""
    if pinned and resolves(platform, pinned) and has_path(platform, pinned, RENDERER):
        return pinned, f"the platform tag this adopter pins ({pinned})", True
    # PAVC_HANDBOOK_PLATFORM_REF grades a platform BRANCH before it merges. Never set by the gate,
    # and it can never make a run look better than it is: the returned flag stays False, so the
    # "pinned tag already carries the renderer" count does not move for it.
    branch = os.environ.get("PAVC_HANDBOOK_PLATFORM_REF")
    if branch and resolves(platform, branch) and has_path(platform, branch, RENDERER):
        return branch, f"platform {branch}, named by PAVC_HANDBOOK_PLATFORM_REF", False
    if resolves(platform, SERVED_BRANCH) and has_path(platform, SERVED_BRANCH, RENDERER):
        why = f"platform {SERVED_BRANCH}" + (
            f"; the pinned tag {pinned} does not carry {RENDERER}" if pinned else "")
        return SERVED_BRANCH, why, False
    return None, f"neither the pinned tag nor platform {SERVED_BRANCH} carries {RENDERER}", False


def _exec(path: Path, name: str) -> Any:
    """Execute a python file and hand back the module. A spec or loader that comes back None is a
    real, reachable state -- an unreadable or non-importable path -- so it is raised by name rather
    than left to fail three lines later as an AttributeError nobody can read."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"{path} is not importable as python")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_renderer(platform: Path, ref: str, into: Path) -> Path:
    """The SERVED renderer's bytes, as platform publishes them at that ref, written to a file
    for the in-process exec and the separate-process render. Reading is one step and executing
    is another (review R2-03): a ref that cannot be read is a could-not-look, a renderer that
    is read and does not execute is a red."""
    target = into / "handbook.py"
    target.write_text(show(platform, ref, RENDERER))
    return target


def read_served(adopter: Path, ref: str) -> tuple[dict[str, str], dict]:
    """Every file of `composed/` at that ref, plus the parsed evidence document."""
    rc, out = git(adopter, "ls-tree", "-r", "--name-only", ref, "composed/")
    if rc != 0:
        raise FileNotFoundError(f"{ref}:composed/")
    files = {p: show(adopter, ref, p) for p in sorted(out.split()) if p.strip()}
    return files, json.loads(files["composed/evidence.json"])


# ---------------------------------------------------------------- the three legs


def render_elsewhere(renderer: Path, files: dict[str, str], work: Path) -> tuple[int, str, str]:
    """`handbook.py render <dir>` in a separate process: environment emptied but for a random
    hash seed and a C locale, cwd a fresh directory, the artefact written to disk exactly as
    served. Returns (exit code, stdout, stderr)."""
    root = work / "elsewhere-artefact"
    cwd = work / "elsewhere-cwd"
    for d in (root, cwd):
        if d.exists():
            for p in sorted(d.rglob("*"), reverse=True):
                p.unlink() if p.is_file() else p.rmdir()
            d.rmdir()
    cwd.mkdir(parents=True)
    for rel, text in files.items():
        (root / rel).parent.mkdir(parents=True, exist_ok=True)
        (root / rel).write_text(text)
    done = subprocess.run(
        [sys.executable, str(renderer), "render", str(root)],
        env={"PYTHONHASHSEED": str(random.randint(1, 2 ** 31)), "LC_ALL": "C"},
        cwd=str(cwd), capture_output=True, text=True)
    return done.returncode, done.stdout, done.stderr


def impure_reads(source: str) -> list[str]:
    """Names the served renderer's code reachable from `render()` must not touch, found by a
    static walk of its module-level functions. Returns `function: name` strings; empty is clean.

    Two walks. The first is every statement that runs at IMPORT time -- module level, class
    bodies, `if`/`try` blocks -- and refuses any `import`/`from ... import` of a FORBIDDEN_ROOTS
    module under any alias (`import datetime as dt`, `from socket import gethostname as _g`),
    because an aliased name or a module-level binding (`_HOST = socket.gethostname()`) is
    invisible to the second walk (round-2 review R2-02). The second follows calls by name from
    `render()` through module-level functions.

    This trusts the text: a renderer that hides a read behind `getattr(__builtins__, ...)` or an
    imported helper module is not seen, and neither is an import-time binding that needs no
    import -- `functools.partial(open, ...)` or a lambda in a module-level dict -- and the PASS
    line says the scan is a scan that does not see import-time bindings."""
    tree = ast.parse(source)
    found: list[str] = []
    for node in _import_time(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[0] in FORBIDDEN_ROOTS:
                    found.append(f"module: import {alias.name}"
                                 + (f" as {alias.asname}" if alias.asname else ""))
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in FORBIDDEN_ROOTS:
                names = ", ".join(a.name + (f" as {a.asname}" if a.asname else "")
                                  for a in node.names)
                found.append(f"module: from {node.module} import {names}")
    funcs = {n.name: n for n in tree.body if isinstance(n, ast.FunctionDef)}
    if "render" not in funcs:
        return sorted(set(found)) + ["render: not defined at module level"]
    seen, todo = set(), ["render"]
    while todo:
        name = todo.pop()
        if name in seen or name not in funcs:
            continue
        seen.add(name)
        for node in ast.walk(funcs[name]):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in funcs:
                todo.append(node.func.id)
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_NAMES:
                found.append(f"{name}: {node.id}")
            if isinstance(node, ast.Name) and node.id in FORBIDDEN_ROOTS:
                found.append(f"{name}: {node.id}")
            if isinstance(node, ast.Attribute):
                root: ast.expr = node
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in FORBIDDEN_ROOTS:
                    found.append(f"{name}: {ast.unparse(node)}")
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                found.append(f"{name}: import inside the function")
    return sorted(set(found))


def _import_time(tree: ast.Module):
    """Every node that executes when the module is imported: the walk descends into class
    bodies and `if`/`try`/`with` blocks but never into a function or lambda body, which runs
    only when called, nor into `if __name__ == "__main__":`, which does not run under
    `exec_module` (the module is executed as `served_handbook`) -- so a name bound only there
    is not a hidden read but a NameError the byte leg would already have caught."""
    todo: list[ast.AST] = list(tree.body)
    while todo:
        node = todo.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
            continue
        if isinstance(node, ast.If) and _is_main_guard(node.test):
            continue
        yield node
        todo.extend(ast.iter_child_nodes(node))


def _is_main_guard(test: ast.expr) -> bool:
    return (isinstance(test, ast.Compare) and isinstance(test.left, ast.Name)
            and test.left.id == "__name__" and len(test.ops) == 1
            and isinstance(test.ops[0], ast.Eq) and len(test.comparators) == 1
            and isinstance(test.comparators[0], ast.Constant)
            and test.comparators[0].value == "__main__")


def _mutate(files: dict[str, str], evidence: dict) -> tuple[tuple | None, str]:
    """One graded field of the served artefact, changed. Returns the mutated inputs and its name."""
    f2, e2 = copy.deepcopy(dict(files)), copy.deepcopy(evidence)
    prices = e2.get("prices") or []
    priced = [p for p in prices if isinstance(p.get("amount"), (int, float))]
    if priced:
        priced[0]["amount"] = priced[0]["amount"] + 4242.42
        return (f2, e2), f"prices[{prices.index(priced[0])}].amount (+4242.42)"
    limits = e2.get("limits") or []
    if limits:
        limits[0]["status"] = "moved-by-the-grader"
        return (f2, e2), "limits[0].status"
    return None, ""


# ---------------------------------------------------------------- the grading


def grade_ref(adopter: Path, platform: Path, ref: str, why_ref: str, tag_graded: bool,
              work: Path) -> dict:
    """One adopter at one ref, one verdict. `state` is one of pass / fail / skip."""
    name = adopter.name
    pinned = pinned_platform_tag(adopter, ref)
    rref, why_renderer, on_pin = renderer_ref(platform, pinned)
    common = {"name": name, "ref": ref, "why_ref": why_ref, "renderer_ref": rref,
              "why_renderer": why_renderer, "on_pin": on_pin, "tag_graded": tag_graded}
    if rref is None:
        return {**common, "state": "skip", "line": f"{name}@{ref}: {why_renderer}"}

    try:
        renderer_path = read_renderer(platform, rref, work)
        files, evidence = read_served(adopter, ref)
    except Exception as exc:                                    # noqa: BLE001
        return {**common, "state": "skip",
                "line": f"{name}@{ref}: could not read the served artefact or renderer at "
                        f"{ref}/{rref}: {exc}"}
    # Read is not executed. A renderer platform serves that cannot be executed is the estate's
    # published tool being broken, which is a red, not a could-not-look (review R2-03).
    try:
        module = _exec(renderer_path, "served_handbook")
    except Exception as exc:                                    # noqa: BLE001
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the renderer platform serves at {rref} does not "
                        f"execute: {type(exc).__name__}: {exc}"}

    served = files.get(PAGE)
    if served is None:
        return {**common, "state": "skip", "line": f"{name}@{ref}: serves no {PAGE}"}
    nbytes = len(served.encode())

    try:
        rendered = module.render(dict(files), evidence)
    except Exception as exc:                                    # noqa: BLE001
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the served artefact does not render: {exc}"}

    if rendered != served:
        n = sum(1 for a, b in zip(rendered.splitlines(), served.splitlines()) if a != b)
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: {PAGE} is NOT what its own served artefact renders to "
                        f"({n} line(s) differ, {nbytes} bytes served vs "
                        f"{len(rendered.encode())} re-rendered) -- the page says something the "
                        f"artefact does not"}

    # PURITY, in a separate process under an emptied environment (review F-06).
    rc, again, err = render_elsewhere(renderer_path, files, work)
    if rc != 0 or again != rendered:
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the render is not a pure function of the artefact -- the "
                        "same served bytes rendered differently from a separate process under an "
                        "emptied environment, a random PYTHONHASHSEED and a fresh cwd"
                        + (f" (exit {rc}: {err.strip().splitlines()[-1] if err.strip() else ''})"
                           if rc != 0 else "") + ", so the byte comparison above proves nothing"}

    # SOURCE: what the process test cannot see on one machine.
    reads = impure_reads(show(platform, rref, RENDERER))
    if reads:
        return {**common, "state": "fail",
                "line": f"{name}@{ref}: the served renderer at platform {rref} reaches, from "
                        f"render() or at import time, {', '.join(reads)} -- a read outside the "
                        "artefact, so the byte comparison above proves nothing"}

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
            "line": f"{name}@{ref}: {nbytes} bytes, byte-identical to a re-render of the "
                    f"artefact served at the same ref; the same bytes again from a separate "
                    f"process under an emptied environment; the served renderer names none of "
                    f"open/os/sys/socket/time/datetime/subprocess in module-level functions "
                    f"called by name from render(), and imports none of those modules at module "
                    f"level under any alias (a text scan that does not see import-time "
                    f"bindings); moving {what} moves the page"}


# ---------------------------------------------------------------- entry points


def run(estate: Path, overrides: dict[str, str]) -> int:
    platform = estate / PLATFORM
    if not (platform / ".git").exists():
        print(f"SKIP: {estate}/{PLATFORM} is not a git checkout, so the served renderer "
              f"({RENDERER}) cannot be read from any ref")
        return 3
    found = adopters(estate)
    if not found:
        print(f"SKIP: no party under {estate} carries both composed/ and a platform pin at "
              f"{SERVED_BRANCH}, so there is no adopter artefact to grade a handbook against")
        return 3

    results = []
    with tempfile.TemporaryDirectory() as td:
        for adopter in found:
            refs, why_none = served_refs(adopter, overrides.get(adopter.name))
            if not refs:
                r = {"name": adopter.name, "state": "skip", "line": f"{adopter.name}: {why_none}"}
                results.append(r)
                print(f"  ??   {r['line']}")
                continue
            for ref, why_ref, tag_graded in refs:
                r = grade_ref(adopter, platform, ref, why_ref, tag_graded, Path(td))
                results.append(r)
                mark = {"pass": "  ok  ", "fail": "FAIL: ", "skip": "  ??  "}[r["state"]]
                print(f"{mark} {r['line']}")
                if r["state"] != "skip":
                    print(f"         ref: {r['why_ref']}; renderer from {r['why_renderer']}")

    passes = [r for r in results if r["state"] == "pass"]
    fails = [r for r in results if r["state"] == "fail"]
    graded = passes + fails
    on_branch = sorted({r["name"] for r in graded if not r.get("tag_graded")})
    at_tag = sorted({r["name"] for r in graded if r.get("tag_graded")})
    on_pin = sorted({r["name"] for r in graded if r.get("on_pin")})
    # An override names a branch other than the served one; the count says which it read.
    branch_label = SERVED_BRANCH if not overrides else "a branch ref named by PAVC_HANDBOOK_REFS"

    # The three disclosed limits, as numbers, every run, whatever the verdict.
    print(f"COUNTS: {len(on_branch)} of {len(found)} adopter(s) serve a handbook at "
          f"{branch_label} this check could read; {len(at_tag)} of {len(found)} also serve one "
          f"at a signed tag, graded as well; {len(on_pin)} of {len(found)} pin a platform tag "
          f"that already carries {RENDERER}.")

    if fails:
        print(f"FAILED: {len(fails)} graded ref(s): "
              + ", ".join(f"{r['name']}@{r['ref']}" for r in fails))
        return 1
    if not passes:
        print(f"SKIP: no adopter of the {len(found)} in this estate serves a handbook this check "
              f"could read, so nothing was compared -- {'; '.join(r['line'] for r in results)}")
        return 3
    print(f"SUMMARY: {len(passes)} served ref(s) across {len({r['name'] for r in passes})} "
          f"adopter(s) ({', '.join(f'{r['name']}@{r['ref']}' for r in passes)}) each serve a "
          f"composed/HANDBOOK.md byte-identical to a re-render of the artefact served at the same "
          f"ref by the renderer platform serves; the same bytes again from a separate process "
          f"under an emptied environment; the served renderer names none of "
          f"open/os/sys/socket/time/datetime/subprocess in module-level functions called by name "
          f"from render() and imports none of those modules at module level under any alias (a "
          f"text scan that does not see import-time bindings, which is what this check trusts); "
          f"the page moves when the artefact moves; {len(at_tag)} adopter(s) graded at a signed "
          f"tag as well; {len(on_pin)} pin a platform tag carrying {RENDERER}")
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
    pin = adopter / PIN
    pin.parent.mkdir(parents=True, exist_ok=True)
    pin.write_text("apiVersion: source.toolkit.fluxcd.io/v1\nkind: GitRepository\n"
                   "spec:\n  ref:\n    tag: planted-platform-v1\n")
    _repo(adopter, "the artefact and its render")
    return estate


def _repo(path: Path, message: str) -> None:
    """A repository whose refs exist, with an `origin/main` because that is the only branch ref
    this check reads. The runner's own git configuration is deliberately not inherited: a
    machine that force-signs every tag or runs a global pre-commit hook has nothing to do with
    what is graded here."""
    subprocess.run(["git", "-C", str(path), "init", "-q", "-b", "main"], check=True)
    hooks = path / ".nohooks"
    hooks.mkdir()
    for k, v in (("core.hooksPath", str(hooks)), ("commit.gpgsign", "false"),
                 ("tag.gpgSign", "false"), ("tag.forceSignAnnotated", "false"),
                 ("user.name", "t"), ("user.email", "t@t.invalid")):
        subprocess.run(["git", "-C", str(path), "config", k, v], check=True)
    _commit(path, message)


def _commit(path: Path, message: str) -> None:
    subprocess.run(["git", "-C", str(path), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", message], check=True)
    # The planted remote-tracking ref moves with the planted branch: this check reads
    # origin/main and nothing else, so the plant must serve one.
    subprocess.run(["git", "-C", str(path), "update-ref", "refs/remotes/origin/main", "HEAD"],
                   check=True)


def _replace_render(plat: Path, body: str, prefix: str = "") -> str:
    """Swap the planted renderer's render() for one whose body is `body` (which may call the
    real one, renamed _real_render), with `prefix` inserted at MODULE level just before it.
    Returns the original source for restoring."""
    src = (plat / RENDERER).read_text()
    head = "def render(files: Mapping[str, str], evidence: Mapping[str, Any]) -> str:"
    assert src.count(head) == 1, "the served renderer's render() signature moved"
    (plat / RENDERER).write_text(src.replace(
        head, f"{prefix}\n\n{head}\n{body}\n\n\ndef _real_render(files: Mapping[str, str], "
              "evidence: Mapping[str, Any]) -> str:", 1))
    return src


def selfcheck(renderer_src: Path) -> int:
    """The grader's rules, on planted inputs. A grader only ever run against artefacts that agree
    has proved nothing about what it does when they do not."""
    ok = 0

    def check(claim: str, cond: bool, detail: str = "") -> None:
        """`detail` is the graded run's own output; its FAIL / ?? lines are printed under the
        claim so a red on the FIRST case says what the served renderer did, not only that the
        rules no longer grade (a renderer refused by the source scan looks like broken rules
        otherwise -- round 2, 2026-09-08)."""
        nonlocal ok
        if not cond:
            print(f"FAIL: selfcheck: {claim}")
            for line in detail.splitlines():
                if line.startswith(("FAIL", "  ??", "SKIP")):
                    print(f"      {line}")
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
        plat = estate / PLATFORM

        rc, out = graded(estate)
        check("a page that re-renders from its own served artefact grades 0",
              rc == 0 and "SUMMARY:" in out, out)
        check("the counts are printed even on a pass", "COUNTS:" in out)
        check("the served branch is graded and no signed tag is counted",
              f"planted@{SERVED_BRANCH}:" in out and "0 of 1 also serve one at a signed tag" in out)
        check("the pin is read from the served ref and does not carry the renderer",
              "0 of 1 pin a platform tag" in out and "planted-platform-v1 does not carry" in out)

        # F-08: a local branch that is AHEAD of origin/main is not what is graded
        page = adopter / PAGE
        keep = page.read_text()
        page.write_text(keep + "\nhand-edited on a local branch only\n")
        subprocess.run(["git", "-C", str(adopter), "add", "-A"], check=True)
        subprocess.run(["git", "-C", str(adopter), "commit", "-qm", "local only"], check=True)
        rc, out = graded(estate)
        check("a hand-edit committed on the local branch but not on origin/main is not graded "
              "(the served branch is origin/main, never local main or HEAD)", rc == 0)
        subprocess.run(["git", "-C", str(adopter), "reset", "-q", "--hard", "origin/main"],
                       check=True)

        # a hand-edited page, served
        page.write_text(keep + "\nThe estate has no holes and everything is fine.\n")
        _commit(adopter, "hand-edit the page")
        rc, out = graded(estate)
        check("a sentence added to the page by hand grades 1",
              rc == 1 and "is NOT what its own served artefact renders to" in out)
        check("the byte count in the FAIL line is bytes, not characters",
              f"{len((keep + chr(10) + 'The estate has no holes and everything is fine.' + chr(10)).encode())} bytes served" in out)

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
        subprocess.run(["git", "-C", str(adopter), "checkout", "-q", "HEAD~2", "--",
                        "composed/evidence.json"], check=True)
        _commit(adopter, "back to the artefact the page was rendered from")
        rc, out = graded(estate)
        check("...and with the artefact back, the same page grades 0 again", rc == 0)

        # A renderer that IGNORES its input and returns a constant equal to the committed page.
        # The byte comparison passes -- that is the point -- so only the sensitivity leg can catch
        # it.
        src = _replace_render(plat, "    return " + repr(keep))
        _commit(plat, "a renderer that ignores its input")
        rc, out = graded(estate)
        check("a renderer that ignores its input is caught by the sensitivity leg, not the byte "
              "comparison", rc == 1 and "did NOT change the render" in out)
        (plat / RENDERER).write_text(src)
        _commit(plat, "restore the renderer")

        # F-06 plant 1: a renderer that reads HOME. Every in-process render on this machine sees
        # the same HOME, so the page committed by it re-renders byte-identically here and an
        # in-process purity test passes; only a separate process with the environment emptied
        # sees the difference. The page is committed by the plant so the byte leg passes first.
        src = _replace_render(
            plat, "    import os as _os\n"
                  "    return _real_render(files, evidence) + _os.environ.get('HOME', '')")
        _commit(plat, "a renderer that reads HOME")
        hb_home = _exec(plat / RENDERER, "hb_home")
        files, evidence = hb_home._fixture()
        files[hb_home.EVIDENCE_PATH] = (adopter / "composed/evidence.json").read_text()
        page.write_text(hb_home.render(files, json.loads(files[hb_home.EVIDENCE_PATH])))
        _commit(adopter, "the page a HOME-reading renderer produced")
        rc, out = graded(estate)
        check("a renderer that appends $HOME re-renders byte-identically in this process and is "
              "caught only by the separate emptied-environment process",
              rc == 1 and "from a separate process under an emptied environment" in out
              and "is NOT what" not in out)
        page.write_text(keep)
        (plat / RENDERER).write_text(src)
        _commit(plat, "restore the renderer")
        _commit(adopter, "restore the page")

        # F-06 plant 2: a renderer that reads /etc/hosts renders the same bytes in every process
        # on this machine, so the process test passes; only reading its code catches it.
        src = _replace_render(
            plat, "    _hosts = open('/etc/hosts').read()\n"
                  "    return _real_render(files, evidence) + ('' if _hosts else '')")
        _commit(plat, "a renderer that reads /etc/hosts")
        rc, out = graded(estate)
        check("a renderer that reads /etc/hosts renders identically in every process and is "
              "caught by the source scan of the served renderer",
              rc == 1 and "reaches, from render() or at import time, render: open" in out)
        (plat / RENDERER).write_text(src)
        _commit(plat, "restore the renderer")
        rc, out = graded(estate)
        check("...and with the real renderer back, the same artefact grades 0 again", rc == 0)

        # R2-02: six ways a read can sit OUTSIDE a module-level function called from render(),
        # none of them moving the bytes (each appends '' whatever it read), so the byte and
        # purity legs pass and only the source scan can see them. Measured red first on
        # 2026-09-08: all six graded 0 under the reviewed scan. Four are caught now by the
        # import-time walk; two need no import and still escape, and the PASS line says the
        # scan does not see import-time bindings.
        tail = "\n    return _real_render(files, evidence) + ('' if _x else '')"
        caught = [
            ("an aliased from-import (from socket import gethostname as _g)",
             "from socket import gethostname as _g\n", "    _x = _g()" + tail,
             "module: from socket import gethostname as _g"),
            ("an aliased import (import datetime as dt)",
             "import datetime as dt\n", "    _x = dt.date.today()" + tail,
             "module: import datetime as dt"),
            ("a module-level binding (_HOST = socket.gethostname())",
             "import socket\n_HOST = socket.gethostname()\n", "    _x = _HOST" + tail,
             "module: import socket"),
            ("a @staticmethod on a module-level class reading time.time()",
             "import time\nclass _Clock:\n    @staticmethod\n    def now():\n"
             "        return time.time()\n", "    _x = _Clock.now()" + tail,
             "module: import time"),
        ]
        for claim, prefix, body, expect in caught:
            src = _replace_render(plat, body, prefix)
            _commit(plat, claim)
            rc, out = graded(estate)
            check(f"{claim} is caught by the import-time walk of the source scan",
                  rc == 1 and expect in out and "at import time" in out)
            (plat / RENDERER).write_text(src)
            _commit(plat, "restore the renderer")
        escapes = [
            ("functools.partial(open, '/etc/hosts') bound at module level",
             "import functools\n_rd = functools.partial(open, '/etc/hosts')\n",
             "    _x = _rd().read()" + tail),
            ("a lambda in a module-level dict calling open()",
             "_F = {'hosts': lambda: open('/etc/hosts').read()}\n",
             "    _x = _F['hosts']()" + tail),
        ]
        for claim, prefix, body in escapes:
            src = _replace_render(plat, body, prefix)
            _commit(plat, claim)
            rc, out = graded(estate)
            check(f"{claim} ESCAPES the source scan (measured: grades 0), which is why the PASS "
                  "line says the scan does not see import-time bindings",
                  rc == 0 and "does not see import-time bindings" in out)
            (plat / RENDERER).write_text(src)
            _commit(plat, "restore the renderer")

        # R2-03: a renderer that platform serves at the ref but that does not EXECUTE. Measured
        # red first on 2026-09-08: it graded 3 (a declared could-not-look, so the gate row went
        # NOTE) under the reviewed check. The artefact was read; the published tool is broken.
        src = _replace_render(plat, "    return _real_render(files, evidence)",
                              "import hb_helpers\n")
        _commit(plat, "a renderer that imports a helper module platform does not serve")
        rc, out = graded(estate)
        check("a served renderer that does not execute (import hb_helpers -> ImportError) "
              "grades 1, not 3: the artefact was read, the published tool is what is broken",
              rc == 1 and "does not execute: ModuleNotFoundError" in out)
        (plat / RENDERER).write_text(src)
        _commit(plat, "restore the renderer")
        rc, out = graded(estate)
        check("...and with the real renderer back, the same artefact grades 0 again", rc == 0)

        # F-10: a signed tag carrying a page is graded AS WELL AS origin/main, never instead.
        # The tag body carries a signature block that signs nothing -- which is exactly what
        # signed_tags() counts and its docstring says it never verifies.
        subprocess.run(["git", "-C", str(adopter), "tag", "-a", "planted-signed-v1", "-m",
                        "planted\n-----BEGIN PGP SIGNATURE-----\nnot a signature\n"
                        "-----END PGP SIGNATURE-----\n"], check=True)
        rc, out = graded(estate)
        check("a signed tag carrying a page is graded as well as origin/main, and both are counted",
              rc == 0 and "planted@planted-signed-v1:" in out
              and f"planted@{SERVED_BRANCH}:" in out
              and "1 of 1 also serve one at a signed tag" in out)
        page.write_text(keep + "\nhand-edited after the tag\n")
        _commit(adopter, "hand-edit the page after the tag")
        rc, out = graded(estate)
        check("a hand-edit on origin/main AFTER the tag still grades 1 -- the tag does not "
              "freeze the check on itself",
              rc == 1 and f"planted@{SERVED_BRANCH}: {PAGE} is NOT" in out
              and "planted@planted-signed-v1:" in out)
        page.write_text(keep)
        _commit(adopter, "restore the page")

        # nothing serves a page
        subprocess.run(["git", "-C", str(adopter), "tag", "-d", "planted-signed-v1"],
                       check=True, capture_output=True)
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

    print(f"PASS: selfcheck: {ok} planted cases -- a fresh page passes, a local-only edit is not "
          "graded, a hand-edited page fails, an artefact that moved under an unmoved page fails, "
          "a renderer that ignores its input is caught by sensitivity, one that reads $HOME by the "
          "separate emptied-environment process, one that reads /etc/hosts by the source scan, "
          "four import-time reads (aliased imports, a module-level binding, a staticmethod) by "
          "its import-time walk while two that need no import (functools.partial(open), a "
          "lambda in a dict) are measured to escape it, a served renderer that does not execute "
          "is red rather than a skip, a signed tag is graded beside origin/main and never "
          "instead of it, and both a missing page and a missing renderer exit 3 rather than 0")
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
