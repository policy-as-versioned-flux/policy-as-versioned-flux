"""Which majors is an institution carrying in its composed window?

THE NAME OF THIS DIRECTORY AND SCRIPT IS HISTORICAL, and narrower than what they grade. They are
named for the fact eco-system ticket 99 was about -- a major nobody reviewed -- but this check
CANNOT see a review and never asserts that one is absent. It looks for no acceptance record and
therefore says nothing about whether one exists: inventing a place to look would be inventing the
record, which is exactly what the ticket forbids. What it grades is what is CARRIED, which it
observes directly. Read "unreviewed" in the paths below as the ticket's
subject, never as this check's claim (delegated, ADR-0025, 2026-09-05, after review; renaming the
files would break the manifest row and the capture filenames the truth surface has already
published, and the sentence is cheaper to fix than the path).


Eco-system ticket 99. "An institution should not quietly carry a major nobody reviewed" is a real
property. tuppence's adopter gate held it as a per-pull-request refusal, by folding its whole
supported window instead of what the pull request moved, and that broke: once a major stood in the
window every pull request composed major and was refused, whatever it changed -- twelve consecutive
red runs from 2026-08-28 -- and the refusal named a remedy the gate had no input for. It was also
the wrong SHAPE. The fact does not depend on anyone opening a pull request, so a check that only
speaks on a pull request is the wrong place to say it. It is a standing report now: this one, which
the truth surface carries on every run, including on a day nobody proposes anything.

WHAT IS MEASURED, AND AGAINST WHAT.

  The SERVED artefact is two documents, and neither is an authoring copy:
    * each adopter's own `composed/evidence.json` -- the composed artefact ADR-0011 names as the
      adopter gate's subject, read at the commit the repository serves (`git show HEAD:...`), the
      same read its own gate makes with `--head-ref`;
    * platform's `computed-semver/evidence/<version>.json` and its cosign bundle, read AT THE TAG
      THAT ADOPTER'S OWN PIN NAMES -- never platform's `main`, and never a file lying in a working
      tree. Two adopters pinned to different tags are two different subjects, and this check reads
      each at its own.

  The OPERATION is the adopter's own verification: `cosign verify-blob`, offline, identity-pinned
  to the constant that repository itself holds -- in its `shift-left.yml` env block, or as a module
  constant in its own gate script. The constant is read out of the repository, never typed here. A
  bump is reported only from evidence that really verified under that constant, in this run.

WHAT IT DOES NOT DO. It records no review and invents none. Whether platform policy 4.0.0's major
is accepted for an institution is an authorisation, and ADR-0025 keeps those with the owner; this
check has no input for one and will keep naming the version until either the owner disposes of it
or the version leaves that institution's window. That is the point: an open authorisation is
visible every day rather than on the days somebody happens to open a pull request. The line it
prints is therefore about what is CARRIED, which is a fact this run observed -- never about what
was or was not reviewed, which it cannot see and does not claim to.

    unreviewed_major.py <estate-dir>   # grade the estate; prints lines, exits 0/1/3
    unreviewed_major.py --selfcheck    # the pure rules, on planted inputs, no estate and no cosign
"""

from __future__ import annotations

import ast
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

MAJOR = "major"


# ---------------------------------------------------------------- the served documents, parsed

def window_from_evidence(doc: dict) -> list[str]:
    """The policy versions an adopter's own composed evidence records as members. A
    platform-machinery member (the orphan guard, the governed-namespace guard) carries no
    `version` and is not one, exactly as every adopter's own gate already reads it."""
    return sorted({m["version"] for m in (doc.get("members") or [])
                   if isinstance(m, dict) and m.get("version") is not None})


def pin_disagreement(tag: str, pinned: str, resolved: str | None) -> str | None:
    """ADR-0001's commit pin is load-bearing, not decorative, and every adopter gate checks it
    before it reads anything. This report reads evidence AT that tag, so it makes the same check
    first: a tag that resolves to a commit the pin does not name means the two documents this
    check reads disagree about which platform is being talked about, and the bump read out of it
    would be a bump for something else. Added 2026-09-05 after review, which caught this check
    reading the tag and discarding the commit beside it."""
    if resolved is None:
        return (f"pins platform tag {tag}, which this checkout of platform could not resolve to a "
                f"commit at all")
    # An abbreviated sha and an upper-case one are both valid git and both name the same commit;
    # reading either as a disagreement would be this check inventing a red out of a formatting
    # choice (R5-5, 2026-09-05). A prefix is accepted only when it is long enough to identify a
    # commit -- git's own shortest useful abbreviation -- so a stray fragment is still a mismatch.
    shortest = 7
    a, b = pinned.strip().lower(), resolved.strip().lower()
    same = a == b or (min(len(a), len(b)) >= shortest
                      and (a.startswith(b) or b.startswith(a)))
    if not same:
        return (f"pins platform tag {tag} at commit {pinned}, but that tag resolves to {resolved} "
                f"in this checkout -- the pin and the tag name different platforms, so any bump "
                f"read at that tag would be a bump for something this institution does not pin")
    return None


def pin_from_pin_yaml(text: str) -> tuple[str, str] | None:
    """The tag and commit the adopter's own platform pin names, off the GitRepository document of a
    real multi-document stream. None when the stream carries no such document."""
    try:
        docs = [d for d in yaml.safe_load_all(text) if isinstance(d, dict)]
    except yaml.YAMLError:
        return None
    for doc in docs:
        if doc.get("kind") != "GitRepository":
            continue
        ref = (doc.get("spec") or {}).get("ref") or {}
        if ref.get("tag") and ref.get("commit"):
            return str(ref["tag"]), str(ref["commit"])
    return None


# ------------------------------------------- the identity constant, where the repository holds it

def identity_from_workflow(text: str) -> tuple[str, str] | None:
    """Two of the three adopters wire their identity constant through their `shift-left.yml` env
    block, under names of their own choosing (`EVIDENCE_EXPECTED_IDENTITY_REGEXP`,
    `ADOPTER_GATE_IDENTITY_REGEXP`). Matched by suffix rather than by a list of names, so a fourth
    adopter naming it a fourth way is read rather than skipped."""
    try:
        doc = yaml.safe_load(text) or {}
    except yaml.YAMLError:
        return None
    if not isinstance(doc, dict):
        return None
    scopes = [doc.get("env") or {}]
    for job in (doc.get("jobs") or {}).values():
        if isinstance(job, dict):
            scopes.append(job.get("env") or {})
    flat: dict[str, str] = {}
    for scope in scopes:
        if isinstance(scope, dict):
            flat.update({str(k): str(v) for k, v in scope.items()})
    regexp = next((v for k, v in flat.items() if k.endswith("IDENTITY_REGEXP")), None)
    issuer = next((v for k, v in flat.items() if k.endswith("ISSUER")), None)
    return (regexp, issuer) if regexp and issuer else None


def identity_from_script(source: str) -> tuple[str, str] | None:
    """driftwood holds its constant in the gate script itself, as a parenthesised implicit
    concatenation. Read through `ast`, which resolves that to one string constant, rather than by a
    regular expression over source lines that would see two."""
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return None
    consts: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and isinstance(node.value, ast.Constant) \
                and isinstance(node.value.value, str):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    consts[target.id] = node.value.value
    regexp = next((v for k, v in consts.items() if k.endswith("IDENTITY_REGEXP")), None)
    issuer = next((v for k, v in consts.items() if k.endswith("ISSUER")), None)
    return (regexp, issuer) if regexp and issuer else None


def identity_constants(unit_dir: Path, script: Path | None) -> tuple[str, str] | None:
    """Whichever of the two places this repository actually keeps it."""
    workflow = unit_dir / ".github" / "workflows" / "shift-left.yml"
    if workflow.is_file():
        found = identity_from_workflow(workflow.read_text())
        if found:
            return found
    if script is not None and script.is_file():
        return identity_from_script(script.read_text())
    return None


# ---------------------------------------------------------------- the report

def grade(findings: list[dict]) -> tuple[str, list[tuple[str, str]]]:
    """FAIL beats SKIP: a major that was actually observed standing in a window is not softened by
    something that could not be looked at -- neither by another adopter, NOR by another version in
    the same adopter's own window.

    The second half of that sentence was not true until 2026-09-05 (review finding R5-1). `look()`
    returned on the first version whose evidence the pinned tag does not carry, and this function
    read `skip` before `computed`, so appending one unrelated member to an adopter's
    composed/evidence.json turned an observed FAIL into a SKIP and the major disappeared from the
    report -- and `carries no signed evidence for policy version` is a DECLARED could-not-look, so
    the truth surface would have scored the masking as an expected skip. The state is reachable and
    has happened: ADR-0011's own 2026-09-03 note records platform's main carrying `4.0.0.json`
    without its bundle. Per-version could-not-looks now collect in `unread` and are named beside
    every major the run did observe.
    """
    if not findings:
        return "SKIP", [("SKIP", "no party in this estate claims the adopter role, so there is no "
                                  "composed window a major could be standing in")]
    lines: list[tuple[str, str]] = []
    majors = 0
    unlooked = 0
    for finding in findings:
        adopter = finding["adopter"]
        if finding.get("skip"):
            unlooked += 1
            lines.append(("SKIP", f"{adopter} {finding['skip']}"))
            continue
        if finding.get("fail"):
            majors += 1
            lines.append(("FAIL", f"{adopter} {finding['fail']}"))
            continue
        standing = [v for v in finding["window"] if finding["computed"].get(v) == MAJOR]
        unread = list(finding.get("unread") or [])
        for version, reason in unread:
            # Named on its own line, never as a reason to stop reading the rest of the window.
            unlooked += 1
            lines.append(("SKIP", f"{adopter} {reason}"))
        if standing:
            majors += 1
            for version in standing:
                lines.append(("FAIL", (
                    f"{adopter} carries policy version {version} in the composed window it serves, "
                    f"and platform's own signed evidence at the tag {adopter} pins "
                    f"({finding['tag']}) records bump.computed \"{MAJOR}\". Disposing of a major an "
                    f"institution carries is an authorisation the owner makes (ADR-0025); no gate "
                    f"can, and this line stands until the owner does or the version leaves the "
                    f"window")))
        elif unread:
            # No major among what could be read. The adopter's own status is a could-not-look, and
            # the line says what WAS verified rather than going quiet about the rest of the window.
            read = [v for v in finding["window"] if v in finding["computed"]]
            lines.append(("ok", (
                f"{adopter}: no major in the {len(read)} version(s) of its composed window that "
                f"could be read ({', '.join(read) or 'none'}), each verified at {finding['tag']} "
                f"under {adopter}'s own identity constant; {len(unread)} could not be read, named "
                f"above")))
        elif not finding["window"]:
            # Nothing was verified, because there was nothing to verify. Saying so is not the same
            # sentence as "every version verified", and a vacuous claim is still a claim.
            lines.append(("PASS", (
                f"{adopter}: the composed window it serves carries no policy version at all, so "
                f"there is no bump to read and no evidence was verified for it")))
        else:
            lines.append(("PASS", (
                f"{adopter}: no major in the {len(finding['window'])} version(s) its composed "
                f"window carries ({', '.join(finding['window'])}), each read from platform's "
                f"signed evidence at {finding['tag']} and verified under {adopter}'s own identity "
                f"constant")))
    if majors:
        return "FAIL", lines
    if unlooked:
        return "SKIP", lines
    return "PASS", lines


# ---------------------------------------------------------------- looking at the estate

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def look(estate: Path, unit: str, platform_dir: Path) -> dict:
    """One adopter, measured. Every read below is of a served document: the adopter's composed
    evidence at the commit it serves, and platform's evidence at the tag that adopter pins."""
    finding: dict = {"adopter": unit, "tag": None, "window": [], "computed": {}, "skip": None,
                      "unread": []}
    unit_dir = estate / unit

    pin_text = _git(unit_dir, "show", "HEAD:gitops/platform/platform-pin.yaml")
    if pin_text.returncode != 0:
        finding["skip"] = ("serves no gitops/platform/platform-pin.yaml at HEAD, so there is no "
                            "tag to read a publisher's evidence at")
        return finding
    pin = pin_from_pin_yaml(pin_text.stdout)
    if pin is None:
        finding["skip"] = ("serves a platform pin with no GitRepository document naming a tag and "
                            "a commit")
        return finding
    tag, pinned_commit = pin
    finding["tag"] = tag

    composed = _git(unit_dir, "show", "HEAD:composed/evidence.json")
    if composed.returncode != 0:
        finding["skip"] = "serves no composed/evidence.json at HEAD, so it declares no window"
        return finding
    try:
        finding["window"] = window_from_evidence(json.loads(composed.stdout))
    except (json.JSONDecodeError, KeyError, TypeError):
        finding["skip"] = "serves a composed/evidence.json at HEAD that is not a readable member set"
        return finding

    resolve = _git(platform_dir, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
    if resolve.returncode != 0:
        finding["skip"] = (f"pins platform tag {tag}, which this checkout of platform has no tag "
                            f"object for, so its evidence could not be read at the pin")
        return finding
    disagreement = pin_disagreement(tag, pinned_commit, resolve.stdout.strip())
    if disagreement:
        finding["fail"] = disagreement
        return finding

    script = next((unit_dir / ".github" / "scripts" / b
                   for b in ("adopter-gate.py", "adopter_gate.py")
                   if (unit_dir / ".github" / "scripts" / b).is_file()), None)
    identity = identity_constants(unit_dir, script)
    if identity is None:
        finding["skip"] = ("holds no identity constant this check could find, in its shift-left.yml "
                            "env or in its own gate script, so nothing could be verified as its own "
                            "publisher's")
        return finding
    regexp, issuer = identity

    with tempfile.TemporaryDirectory() as td:
        work = Path(td)
        for version in finding["window"]:
            base = f"computed-semver/evidence/{version}.json"
            doc_text = _git(platform_dir, "show", f"{tag}:{base}")
            bundle_text = _git(platform_dir, "show", f"{tag}:{base}.bundle")
            if doc_text.returncode != 0 or bundle_text.returncode != 0:
                # R5-1: named and carried, never a reason to stop reading the rest of the window.
                # Returning here let one unreadable version silence a major already observed.
                finding["unread"].append((version, (
                    f"pins platform {tag}, whose tree carries no signed evidence for policy "
                    f"version {version} that it declares in its window")))
                continue
            doc_path, bundle_path = work / f"{version}.json", work / f"{version}.json.bundle"
            doc_path.write_text(doc_text.stdout)
            bundle_path.write_text(bundle_text.stdout)
            verified = subprocess.run(
                ["cosign", "verify-blob", f"--bundle={bundle_path}",
                 f"--certificate-identity-regexp={regexp}",
                 f"--certificate-oidc-issuer={issuer}", str(doc_path)],
                capture_output=True, text=True)
            if verified.returncode != 0:
                finding["fail"] = (
                    f"carries policy version {version}, and platform's evidence for it at {tag} did "
                    f"NOT verify under the identity constant {unit} itself holds: "
                    f"{(verified.stderr or verified.stdout).strip().splitlines()[-1][:160]}")
                return finding
            try:
                finding["computed"][version] = json.loads(doc_text.stdout)["bump"]["computed"]
            except (json.JSONDecodeError, KeyError, TypeError):
                finding["unread"].append((version, (
                    f"pins platform {tag}, whose verified evidence for {version} records no "
                    f"bump.computed to read")))
                continue
    return finding


def run(estate: Path) -> tuple[str, list[tuple[str, str]]]:
    estate = estate.resolve()
    tpa_path = Path(__file__).resolve().parent.parent / "twin-per-adopter" / "twin_per_adopter.py"
    spec = importlib.util.spec_from_file_location("twin_per_adopter", tpa_path)
    tpa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tpa)

    units = [u for u in tpa.adopters(estate) if (estate / u).is_dir()]
    if not units:
        return grade([])
    platform_dir = estate / "platform"
    if not (platform_dir / ".git").exists():
        return "SKIP", [("SKIP", "this checkout carries no clone of platform, whose signed evidence "
                                  "records the bump every adopter's window is read against")]
    if shutil.which("cosign") is None:
        return "SKIP", [("SKIP", "cosign is not installed, and a bump read out of an unverified "
                                  "evidence document is not a fact this report will carry")]
    return grade([look(estate, unit, platform_dir) for unit in units])


# ---------------------------------------------------------------- selfcheck

def selfcheck() -> int:
    bad = 0

    def check(label: str, got, want) -> None:
        nonlocal bad
        ok = got == want
        print(f"{'ok ' if ok else 'BAD'}: {label}" + ("" if ok else f" -> {got!r}, wanted {want!r}"))
        bad += 0 if ok else 1

    check("the window is the member versions, deduplicated, machinery excluded",
          window_from_evidence({"members": [{"name": "a", "version": "4.0.0"},
                                            {"name": "b", "version": "4.0.0"},
                                            {"name": "guard"},
                                            {"name": "c", "version": "2.0.1"}]}),
          ["2.0.1", "4.0.0"])
    pin = ("kind: GitRepository\nspec:\n  ref:\n    tag: v2.0.1\n    commit: \"" + "d" * 40 + "\"\n"
           "---\nkind: Kustomization\nspec:\n  path: x\n")
    check("the pinned tag comes off the GitRepository document of a real stream",
          pin_from_pin_yaml(pin), ("v2.0.1", "d" * 40))
    check("a stream with no GitRepository names no tag", pin_from_pin_yaml("kind: Kustomization\n"), None)
    check("a tag resolving to the commit the pin names is no disagreement",
          pin_disagreement("v2.0.1", "a" * 40, "a" * 40), None)
    check("a tag resolving to a different commit than the pin names is observed false, and both are named",
          all(s in (pin_disagreement("v2.0.1", "a" * 40, "b" * 40) or "")
              for s in ("v2.0.1", "a" * 40, "b" * 40)), True)
    check("a tag that resolves to nothing at all is named too",
          "could not resolve" in (pin_disagreement("v2.0.1", "a" * 40, None) or ""), True)
    check("an abbreviated or upper-case sha in the pin is not a disagreement",
          (pin_disagreement("v2.0.1", ("a" * 40).upper(), "a" * 40),
           pin_disagreement("v2.0.1", "a" * 12, "a" * 40)), (None, None))
    check("a fragment too short to name a commit still is one",
          pin_disagreement("v2.0.1", "aaa", "a" * 40) is not None, True)
    check("an identity constant in a workflow env block is read",
          identity_from_workflow("env:\n  X_IDENTITY_REGEXP: ^a$\n  X_ISSUER: https://i\n"),
          ("^a$", "https://i"))
    check("an identity constant in the gate script is read, implicit concatenation and all",
          identity_from_script('P_IDENTITY_REGEXP = (\n    r"^a"\n    r"b$"\n)\nP_ISSUER = "https://i"\n'),
          ("^ab$", "https://i"))
    check("a repository holding neither yields nothing rather than a default",
          (identity_from_workflow("env:\n  FOO: bar\n"), identity_from_script("X = 1\n")), (None, None))

    clean = {"adopter": "driftwood", "tag": "v2.0.1", "window": ["2.0.1"],
             "computed": {"2.0.1": "none"}, "skip": None}
    carried = {"adopter": "tuppence", "tag": "v2.0.1", "window": ["4.0.0"],
               "computed": {"4.0.0": "major"}, "skip": None}
    unlooked = {"adopter": "ludlow", "tag": None, "window": [], "computed": {},
                "skip": "pins platform tag v9.9.9, which this checkout of platform has no tag object for"}
    check("a window with no major is the pass", grade([clean])[0], "PASS")
    empty = {"adopter": "nist", "tag": "v2.0.1", "window": [], "computed": {}, "skip": None}
    status_empty, lines_empty = grade([empty])
    check("an empty window passes without claiming anything was verified for it",
          (status_empty, "no evidence was verified" in lines_empty[0][1]), ("PASS", True))
    status, lines = grade([carried])
    check("a major standing in a window is named, with its adopter and the tag it was read at",
          (status, all(s in " ".join(m for _, m in lines) for s in ("tuppence", "4.0.0", "v2.0.1"))),
          ("FAIL", True))
    check("an adopter that could not be looked at makes the report a could-not-look",
          grade([clean, unlooked])[0], "SKIP")
    check("a major that WAS observed outranks an adopter that was not",
          grade([carried, unlooked])[0], "FAIL")
    # R5-1: and it outranks an unreadable version in its OWN window, which used to silence it.
    masked = dict(carried, window=["1.9.9", "4.0.0"],
                  unread=[("1.9.9", "pins platform v2.0.1, whose tree carries no signed evidence "
                                     "for policy version 1.9.9 that it declares in its window")])
    status_masked, lines_masked = grade([masked])
    check("one unreadable version does not silence a major already observed in the same window",
          (status_masked,
           any(k == "FAIL" and "4.0.0" in m for k, m in lines_masked),
           any(k == "SKIP" and "1.9.9" in m for k, m in lines_masked)),
          ("FAIL", True, True))
    only_unread = {"adopter": "ludlow", "tag": "v2.0.1", "window": ["1.9.9", "2.0.1"],
                   "computed": {"2.0.1": "none"}, "skip": None,
                   "unread": [("1.9.9", "pins platform v2.0.1, whose tree carries no signed "
                                         "evidence for policy version 1.9.9")]}
    status_unread, lines_unread = grade([only_unread])
    check("a window with an unreadable version and no major is a could-not-look that still says "
          "what it read",
          (status_unread, any("2.0.1" in m for _, m in lines_unread)), ("SKIP", True))
    check("no adopter at all is a could-not-look", grade([])[0], "SKIP")
    check("evidence that does not verify is observed false, never a shrug",
          grade([{"adopter": "driftwood", "tag": "v2.0.1", "window": ["4.0.0"], "computed": {},
                  "skip": None, "fail": "did NOT verify"}])[0], "FAIL")

    if bad:
        print(f"FAIL: {bad} selfcheck case(s) did not grade as written")
        return 1
    print("OK: unreviewed_major selfcheck (the window, the pin, both identity-constant readers and "
          "the report's arithmetic, on planted inputs; no estate read, no cosign run)")
    return 0


def main(argv: list[str]) -> int:
    if "--selfcheck" in argv:
        return selfcheck()
    if len(argv) != 1:
        print("usage: unreviewed_major.py <estate-dir> | --selfcheck")
        return 2
    estate = Path(argv[0])
    if not estate.is_dir():
        print(f"SKIP: {estate} is not a directory, so no estate could be read")
        return 3
    status, lines = run(estate)
    for kind, message in lines:
        print(f"{kind}: {message}")
    return {"PASS": 0, "FAIL": 1, "SKIP": 3}[status]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
