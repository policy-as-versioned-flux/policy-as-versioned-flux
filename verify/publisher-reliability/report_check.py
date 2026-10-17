#!/usr/bin/env python3
"""Observe NIST's signed binary report without asserting publisher-price quality.

Only a namespaced, identity-verified annotated tag supplies executable report
code. Mutable checkout files and bare catalogue tags are never report evidence.
The publisher's checker authenticates pairs and recomputes the full report;
this consumer additionally preserves the claim boundary and the empty-state wait.
"""
from __future__ import annotations

import argparse
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[2]
ORIGIN = "https://github.com/policy-as-versioned-nist/nist"
IDENTITY = (r"^https://github\.com/policy-as-versioned-nist/nist/\.github/"
            r"workflows/cut-release\.yml@refs/heads/main$")
ISSUER = "https://token.actions.githubusercontent.com"
TAG = re.compile(r"publisher-reliability/v(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
CLAIM = {"binary_forecast_scores_only": True, "publisher_price_accuracy": False,
         "price_eligible": False}
NO_TAG = "publisher reliability waits for NIST's signed publisher-reliability/v<semver> report tag"


class Rejected(ValueError):
    pass


class Unmeasured(RuntimeError):
    pass


def command(args: list[str], *, cwd: Path | None = None, timeout: int = 30,
            env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(args, cwd=cwd, text=True, capture_output=True,
                              timeout=timeout, env=env)
    except FileNotFoundError as error:
        raise Unmeasured("publisher reliability instrument missing: " + args[0]) from error
    except subprocess.TimeoutExpired as error:
        raise Rejected("publisher reliability instrument timed out: " + args[0]) from error


def git(repo: Path, *args: str) -> str:
    result = command(["git", "-C", str(repo), *args])
    if result.returncode:
        raise Rejected("cannot read NIST Git evidence: " + " ".join(args[:2]))
    return result.stdout.strip()


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise Rejected("duplicate report JSON key: " + key)
        result[key] = value
    return result


def load_report(path: Path) -> dict:
    try:
        report = json.loads(path.read_text(), object_pairs_hook=unique_object,
                            parse_constant=lambda value: (_ for _ in ()).throw(
                                Rejected("nonfinite report JSON value: " + value)))
    except (OSError, ValueError) as error:
        raise Rejected("cannot read committed publisher report: " + str(error)) from error
    if not isinstance(report, dict):
        raise Rejected("publisher report must be an envelope object")
    return report


def newest_tag(repo: Path) -> tuple[str, str]:
    origin = git(repo, "remote", "get-url", "origin").rstrip("/").removesuffix(".git")
    if origin != ORIGIN:
        raise Rejected("publisher report requires the canonical NIST origin")
    candidates: list[tuple[tuple[int, ...], str]] = []
    for name in git(repo, "tag", "--list", "publisher-reliability/*").splitlines():
        match = TAG.fullmatch(name)
        if not match:
            raise Rejected("malformed publisher report tag: " + name)
        candidates.append((tuple(int(value) for value in match.groups()), name))
    if not candidates:
        raise Unmeasured(NO_TAG)
    tag = max(candidates)[1]
    tag_object = git(repo, "rev-parse", "refs/tags/" + tag)
    if git(repo, "cat-file", "-t", tag_object) != "tag":
        raise Rejected("publisher report tag must be annotated and signed")
    headers = git(repo, "cat-file", "tag", tag_object).partition("\n\n")[0].splitlines()
    if [line.removeprefix("tag ") for line in headers if line.startswith("tag ")] != [tag]:
        raise Rejected("signed tag name differs from the namespaced report reference")
    commit = git(repo, "rev-parse", tag_object + "^{commit}")
    served = git(repo, "rev-parse", "refs/remotes/origin/main^{commit}")
    if commit not in git(repo, "rev-list", "--first-parent", served).splitlines():
        raise Rejected("publisher report tag is not on served NIST main's first-parent history")
    return tag, tag_object


def copy_tag(repo: Path, tag: str, tag_object: str, destination: Path) -> None:
    """Freeze the exact object in a regular private repo before name-only gitsign.

    gitsign0.17.1 resolves refs/tags/<argument>, not a raw object ID. A private
    object store and ref let it authenticate precisely the object later exported,
    independent of concurrent changes to the publisher checkout. No source ref,
    alternate, hardlink, public remote or signature is created here.
    """
    git(destination, "init", "--quiet")
    packed = subprocess.run(["git", "-C", str(repo), "pack-objects", "--revs", "--stdout"],
                            input=(tag_object + "\n").encode(), capture_output=True, timeout=30)
    if packed.returncode:
        raise Rejected("cannot copy captured publisher tag objects")
    unpacked = subprocess.run(["git", "-C", str(destination), "unpack-objects", "--strict"],
                              input=packed.stdout, capture_output=True, timeout=30)
    if unpacked.returncode:
        raise Rejected("captured publisher Git objects did not validate")
    git(destination, "update-ref", "refs/tags/" + tag, tag_object)


def verify_tag(repo: Path, tag: str) -> None:
    if shutil.which("gitsign") is None:
        raise Unmeasured("publisher reliability instrument missing: gitsign")
    result = command(["gitsign", "verify-tag", tag,
                      "--certificate-identity-regexp=" + IDENTITY,
                      "--certificate-oidc-issuer=" + ISSUER], cwd=repo, timeout=90,
                     env={**os.environ, "GITSIGN_REKOR_MODE": "offline"})
    # Exit status alone is insufficient: the real verifier emits all three facts.
    output = result.stdout + result.stderr
    facts = ("Good signature from", "Validated Git signature: true",
             "Validated Rekor entry: true", "Validated Certificate claims: true")
    if result.returncode or not all(fact in output for fact in facts):
        raise Rejected("publisher report tag failed pinned signature, Rekor or certificate verification")


def export(repo: Path, tag: str, destination: Path) -> None:
    result = subprocess.run(["git", "-C", str(repo), "archive", "--format=tar", tag],
                            capture_output=True, timeout=30)
    if result.returncode:
        raise Rejected("cannot read signed publisher report tree")
    with tarfile.open(fileobj=io.BytesIO(result.stdout)) as archive:
        for member in archive:
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts:
                raise Rejected("unsafe path in signed publisher tree")
            target = destination.joinpath(*path.parts)
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
            elif member.isfile():
                source = archive.extractfile(member)
                if source is None:
                    raise Rejected("unreadable signed publisher file")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read())
            else:
                raise Rejected("non-regular file in signed publisher tree")


def grade(report: dict, tag: str) -> tuple[int, str]:
    if (report.get("kind"), report.get("name"), report.get("published_by"), report.get("version")) != (
            "feed", "publisher-reliability", "nist", tag.rsplit("/v", 1)[1]):
        raise Rejected("signed report envelope does not match its NIST report tag")
    payload = report.get("payload")
    if not isinstance(payload, dict) or payload.get("schema") != "publisher-reliability/report-v1":
        raise Rejected("unknown publisher report schema")
    if payload.get("claim_scope") != CLAIM or any(type(payload["claim_scope"][key]) is not bool for key in CLAIM):
        raise Rejected("binary diagnostic report may not assert publisher-price accuracy or price eligibility")
    if payload.get("scorer") != "nist" or payload.get("as_of") != report.get("published_at"):
        raise Rejected("signed report scorer or observation time disagrees with its envelope")
    counts = payload.get("counts")
    if not isinstance(counts, dict) or any(type(counts.get(key)) is not int or counts[key] < 0
                                           for key in ("submitted", "eligible", "unscoreable")):
        raise Rejected("report counts must be nonnegative integers")
    if counts["submitted"] != counts["eligible"] + counts["unscoreable"]:
        raise Rejected("report population counts do not conserve submitted pairs")
    if counts["eligible"] == 0:
        if payload.get("status") != "unmeasured" or payload.get("losses") != {
                "lower_is_better": True, "brier": None, "log_loss": None}:
            raise Rejected("empty report must remain unmeasured with null losses")
        return 3, ("publisher reliability waits for eligible independent forecast/outcome pairs; "
                   f"signed {tag} has n=0, publisher-price accuracy remains unmeasured")
    if payload.get("status") != "measured":
        raise Rejected("nonempty binary report must name its measured status")
    return 0, (f"signed NIST binary diagnostic {tag} recomputes for n={counts['eligible']}; "
               "publisher-price accuracy and price eligibility are not established")


def observe(estate: Path) -> tuple[int, str]:
    repo = estate.resolve() / "nist"
    if not repo.is_dir():
        raise Unmeasured("publisher reliability instrument missing: NIST source checkout")
    tag, tag_object = newest_tag(repo)
    with tempfile.TemporaryDirectory(prefix="publisher-report-") as directory:
        snapshot = Path(directory)
        copy_tag(repo, tag, tag_object, snapshot)
        verify_tag(snapshot, tag)
        if git(snapshot, "rev-parse", "refs/tags/" + tag) != tag_object:
            raise Rejected("publisher report tag changed during signature verification")
        export(snapshot, tag_object, snapshot)
        feed = snapshot / "publisher-reliability/v1/feed.json"
        report = load_report(feed)
        checker = snapshot / "publisher-reliability/report.py"
        if not checker.is_file():
            raise Rejected("signed report has no native provenance/recomputation checker")
        checked = command([sys.executable, str(checker), "check", "--root", str(snapshot),
                           "--report", str(feed), "--sources", str(estate.resolve())],
                          cwd=snapshot, timeout=180)
        if checked.returncode == 3:
            raise Unmeasured("publisher reliability instrument unavailable in signed native checker")
        if checked.returncode:
            raise Rejected("signed native report provenance/recomputation check failed")
        return grade(report, tag)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--estate", type=Path, default=ROOT / ".estate-clone")
    args = parser.parse_args()
    try:
        code, message = observe(args.estate)
    except Unmeasured as error:
        code, message = 3, str(error)
    except (Rejected, OSError, tarfile.TarError, subprocess.TimeoutExpired) as error:
        code, message = 1, str(error)
    print(("PASS" if code == 0 else "SKIP" if code == 3 else "FAIL") + ": " + message)
    return code


if __name__ == "__main__":
    raise SystemExit(main())
