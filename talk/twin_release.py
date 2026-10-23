"""Initial twin package release; Git is the package and gitsign is its one signer.

No test mode, signature substitute or CI-result exception exists in this program.
Tests substitute only the external process/API boundaries in disposable fixtures.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

REPOSITORY = "policy-as-versioned-flux/policy-as-versioned-flux"
TAG = "twin/v0.1.0"
ISSUER = "https://token.actions.githubusercontent.com"
IDENTITY = (r"^https://github\.com/policy-as-versioned-flux/policy-as-versioned-flux/"
            r"\.github/workflows/cut-release\.yml@refs/heads/main$")


class Refusal(ValueError):
    """The observed release contract is not satisfied."""


def run(root: Path, *args: str) -> str:
    result = subprocess.run(args, cwd=root, text=True, capture_output=True, check=True, timeout=180)
    if args[0] == "gitsign":
        # Retain the genuine certificate/Rekor output for the hosted receipt.
        print(result.stdout, end="", flush=True)
        print(result.stderr, end="", file=sys.stderr, flush=True)
    return result.stdout.strip()


def remote_refs(root: Path) -> dict[str, str]:
    return {ref: oid for oid, ref in
            (line.split("\t") for line in run(root, "git", "ls-remote", "--heads", "--tags", "origin").splitlines())}


def prepare(root: Path, version: str, expected_commit: str) -> dict[str, Any]:
    if os.environ.get("GITSIGN_REKOR_MODE") != "offline":
        raise Refusal("persisted offline Rekor proof is required before signing")
    if version != "0.1.0" or (root / "twin/VERSION").read_text().strip() != version:
        raise Refusal("only the initial twin/VERSION 0.1.0 publication is defined")
    if not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        raise Refusal("expected commit must be a full lowercase SHA1")
    expected_workflow = f"{REPOSITORY}/.github/workflows/cut-release.yml@refs/heads/main"
    if (os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_WORKFLOW_REF") != expected_workflow):
        raise Refusal("cut must execute the canonical main workflow")
    if run(root, "git", "remote", "get-url", "origin").removesuffix(".git") != f"https://github.com/{REPOSITORY}":
        raise Refusal("origin is not the canonical publisher")
    if run(root, "git", "rev-parse", "HEAD") != expected_commit:
        raise Refusal("checkout differs from reviewed expected commit")
    if run(root, "git", "status", "--porcelain", "--untracked-files=all"):
        raise Refusal("release source is dirty")
    refs = remote_refs(root)
    if refs.get("refs/heads/main") != expected_commit:
        raise Refusal("canonical main advanced or differs from expected commit")
    if any(ref.startswith("refs/tags/twin/") for ref in refs) or run(root, "git", "tag", "--list", "twin/*"):
        raise Refusal("an initial twin tag already exists; never rewrite or retry it")
    if not run(root, "git", "ls-tree", "HEAD", "bin/twin").startswith("100755 blob "):
        raise Refusal("bin/twin is not the tracked executable entry point")
    return package_manifest(root, "HEAD", version, expected_commit)


def package_manifest(root: Path, ref: str, version: str, commit: str) -> dict[str, Any]:
    return {
        "schema": "twin-release/v1", "version": version, "tag": TAG,
        "repository": REPOSITORY, "source_commit": commit,
        "twin_tree": run(root, "git", "rev-parse", f"{ref}:twin"),
        "entrypoint_blob": run(root, "git", "rev-parse", f"{ref}:bin/twin"),
        "version_basis": "initial-publication-no-predecessor",
        "estate_green_claim": False,
        "claim_scope": "Versioned source package only; no actor attestation, measured forecast, financial credit or estate-green claim. Historical flux coverage remains unmeasured and its CI invariant remains red.",
    }


def verify_tag(root: Path, tag: str, expected_commit: str) -> dict[str, Any]:
    if tag != TAG or not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        raise Refusal("only twin/v0.1.0 at an exact expected commit is supported")
    if os.environ.get("GITSIGN_REKOR_MODE") != "offline":
        raise Refusal("persisted offline Rekor verification is required")
    ref = f"refs/tags/{tag}"
    if run(root, "git", "cat-file", "-t", ref) != "tag":
        raise Refusal("release requires an annotated signed tag object")
    run(root, "gitsign", "verify-tag", tag,
        "--certificate-identity-regexp=" + IDENTITY,
        "--certificate-oidc-issuer=" + ISSUER)
    if run(root, "git", "rev-parse", ref + "^{commit}") != expected_commit:
        raise Refusal("verified tag differs from expected source commit")
    if run(root, "git", "show", f"{ref}:twin/VERSION") != "0.1.0":
        raise Refusal("tagged package version differs from its tag")
    text = run(root, "git", "for-each-ref", "--format=%(contents)", ref)
    # gitsign appends its one signed-message block, as in the sibling release route.
    manifest = json.loads(text.split("\n-----BEGIN SIGNED MESSAGE-----", 1)[0])
    if not isinstance(manifest, dict) or not isinstance(manifest.get("message"), str) or not manifest["message"].strip():
        raise Refusal("tag annotation has no release message")
    actual = {key: value for key, value in manifest.items() if key != "message"}
    if json.dumps(actual, sort_keys=True) != json.dumps(package_manifest(root, ref, "0.1.0", expected_commit), sort_keys=True):
        raise Refusal("tag annotation does not bind the actual package source and scope")
    return manifest


def cut(root: Path, version: str, expected_commit: str, message: str) -> dict[str, Any]:
    manifest = prepare(root, version, expected_commit)
    if not message.strip():
        raise Refusal("a release message explaining the change is required")
    manifest["message"] = message
    with tempfile.TemporaryDirectory(prefix="twin-release-") as temporary:
        annotation = Path(temporary) / "annotation.json"
        annotation.write_text(json.dumps(manifest, sort_keys=True, indent=2) + "\n")
        run(root, "git", "-c", "gpg.format=x509", "-c", "gpg.x509.program=gitsign",
            "-c", "gitsign.rekorMode=offline", "-c", "user.name=twin release workflow",
            "-c", "user.email=releases@policy-as-versioned-flux.invalid",
            "tag", "-s", TAG, "-F", str(annotation), expected_commit)
    verified = verify_tag(root, TAG, expected_commit)
    if remote_refs(root).get("refs/heads/main") != expected_commit:
        raise Refusal("main advanced while signing; no tag was pushed")
    run(root, "git", "push", "--atomic", "origin", f"refs/tags/{TAG}:refs/tags/{TAG}")
    print(f"PUSHED {TAG} at {expected_commit}; dispatching separate verification/publication", flush=True)
    run(root, "gh", "workflow", "run", "release.yml", "--repo", REPOSITORY,
        "--ref", "main", "-f", f"tag={TAG}", "-f", f"expected_commit={expected_commit}")
    return verified


def publish(root: Path, tag: str, expected_commit: str) -> dict[str, Any]:
    allowed = {f"{REPOSITORY}/.github/workflows/release.yml@refs/heads/main",
               f"{REPOSITORY}/.github/workflows/release.yml@refs/tags/{TAG}"}
    if (os.environ.get("GITHUB_REPOSITORY") != REPOSITORY
            or os.environ.get("GITHUB_WORKFLOW_REF") not in allowed):
        raise Refusal("publication must execute the canonical release workflow")
    if tag != TAG or not re.fullmatch(r"[0-9a-f]{40}", expected_commit):
        raise Refusal("only the initial tag and an exact source commit are supported")
    if run(root, "git", "remote", "get-url", "origin").removesuffix(".git") != f"https://github.com/{REPOSITORY}":
        raise Refusal("origin is not the canonical publisher")
    # Refresh only the local verification copy: checkout may flatten annotated tags.
    # This never force-pushes or changes any remote object/ref.
    run(root, "git", "fetch", "--no-tags", "origin", f"+refs/tags/{tag}:refs/tags/{tag}")
    manifest = verify_tag(root, tag, expected_commit)
    refs = remote_refs(root)
    if (refs.get(f"refs/tags/{tag}^{{}}") != expected_commit
            or refs.get(f"refs/tags/{tag}") != run(root, "git", "rev-parse", f"refs/tags/{tag}")):
        raise Refusal("remote tag object/source changed; no release was published")
    with tempfile.TemporaryDirectory(prefix="twin-publication-") as temporary:
        notes = Path(temporary) / "notes.md"
        notes.write_text(
            f"# {tag}\n\nVerified gitsign tag at source `{expected_commit}`.\n\n"
            + manifest["claim_scope"] + "\n\n"
            + "Existing twin CI/invariants remain independently visible; publication is not an all-green CI claim.\n\n"
            + "```json\n" + json.dumps(manifest, sort_keys=True, indent=2) + "\n```\n")
        run(root, "gh", "release", "create", tag, "--repo", REPOSITORY, "--verify-tag",
            "--target", expected_commit, "--title", tag, "--notes-file", str(notes))
    return manifest


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["prepare", "cut", "publish"])
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--version", default="0.1.0")
    parser.add_argument("--tag", default=TAG)
    parser.add_argument("--expected-commit", required=True)
    parser.add_argument("--message", default="")
    args = parser.parse_args()
    try:
        if args.operation == "cut":
            result = cut(args.repo, args.version, args.expected_commit, args.message)
        elif args.operation == "publish":
            result = publish(args.repo, args.tag, args.expected_commit)
        else:
            result = prepare(args.repo, args.version, args.expected_commit)
        print(json.dumps(result, sort_keys=True, indent=2))
    except (Refusal, OSError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        if isinstance(error, subprocess.CalledProcessError):
            if error.stdout:
                print(error.stdout, end="", file=sys.stderr)
            if error.stderr:
                print(error.stderr, end="", file=sys.stderr)
        parser.exit(1, f"FAIL: {error}\n")


if __name__ == "__main__":
    main()
