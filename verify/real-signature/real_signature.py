#!/usr/bin/env python3
"""Eco-system ticket 101. Does every adopter gate really check a real signature?

Ticket 99 found that no adopter gate in the estate had ever been observed verifying a signature
platform actually published, and the first check that looked found ludlow's could not: with the
cosign version ludlow itself pins, its own invocation refused every bundle platform publishes
before it looked at the signature at all. That defect was LATENT for weeks -- a gate reaches its
signature check only when its composed member set moves -- and nothing in the estate graded the
one sentence that would have caught it.

THE SENTENCE GRADED HERE. Every adopter's own gate, run the way its own shift-left.yml runs it,
ACCEPTS platform's real published evidence for a version arriving in its window, and REFUSES the
same evidence when one byte of the publisher's own signature is changed.

Both halves matter and neither alone is enough. A gate that refuses everything passes the second
half and fails the first -- which is exactly what ludlow did. A gate that accepts everything
passes the first and fails the second, and would adopt a forged bump.

WHAT IS SERVED AND WHAT REACHES IT.

  served artefact   platform's own committed computed-semver/evidence/<version>.json[.bundle] at
                    a real tag, read out of a real clone. Nothing is signed here and no bundle,
                    certificate or signature is fabricated: the REFUSE half changes one byte of a
                    real signature, which is a corruption of the served artefact, not a fixture.
  operation         each adopter's own committed gate script, invoked through the flags its own
                    .github/workflows/shift-left.yml spells, under the identity constant that
                    repository itself holds. Read out of the workflow by
                    verify/fold-agreement/fold_agreement.py, whose argument whitelist this module
                    reuses rather than re-deriving -- one grader of "how does this repository
                    actually invoke its gate" is enough, and two would drift.

Only the MOVEMENT is planted (which versions the adopter's composed window names before and
after), because that is the thing a Renovate pull request changes.

ALSO REPORTED, NEVER GRADED: how offline each adopter's signature check is. ludlow pins its
Sigstore trust material and verifies with a cold TUF cache and no egress; driftwood and tuppence
pass cosign no trust root, so they fetch a trust root from Sigstore's TUF CDN on every CI run,
which is cold every time. That is a real difference between the three and it is printed as an
exit code per adopter rather than written down as a sentence -- eco-system ticket 101's own lesson
is that a sentence about what a check cannot do goes stale and nothing re-reads it. Closing the
difference is ticket 103.

Usage:
    real_signature.py <estate-dir>
    real_signature.py --selfcheck
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
FOLD = HERE.parent / "fold-agreement" / "fold_agreement.py"

# The planted movement: a version ARRIVES in the adopter's composed window, so the gate must look
# its evidence up and verify its signature. The pin moves between two real platform tags, because
# a gate whose pin does not move correctly does no work at all.
BASE_TAG = "v2.0.0"
HEAD_TAG = "v2.0.1"
STANDING = "2.0.0"


def _fold():
    spec = importlib.util.spec_from_file_location("fold_agreement", FOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# --------------------------------------------------------------------------------------------
# pure
# --------------------------------------------------------------------------------------------
def tamper_signature(bundle_text: str) -> str:
    """The same real bundle with exactly one base64 character of the publisher's own signature
    changed. Raises ValueError on a bundle shape whose signature this does not know how to reach
    -- silently returning the bundle unchanged would turn the REFUSE half of this check into an
    accidental second ACCEPT, and it would pass."""
    doc = json.loads(bundle_text)
    if not isinstance(doc, dict):
        raise ValueError("not a cosign bundle object")
    if "base64Signature" in doc:                       # the legacy shape platform publishes today
        original = doc["base64Signature"]
        doc["base64Signature"] = ("B" if original[:1] != "B" else "C") + original[1:]
    elif isinstance(doc.get("messageSignature"), dict):  # a new-format Sigstore bundle
        original = doc["messageSignature"].get("signature", "")
        if not original:
            raise ValueError("new-format bundle carries no messageSignature.signature")
        doc["messageSignature"]["signature"] = ("B" if original[:1] != "B" else "C") + original[1:]
    else:
        raise ValueError("neither a legacy base64Signature nor a new-format messageSignature")
    if json.dumps(doc, sort_keys=True) == json.dumps(json.loads(bundle_text), sort_keys=True):
        raise ValueError("tampering changed nothing")
    return json.dumps(doc)


def grade(observations: dict[str, dict]) -> tuple[str, list[tuple[str, str]]]:
    """observations: unit -> {"accept": result|None, "refuse": result|None, "reason": str,
    "version": str}, where a result is fold_agreement.run_gate's own dict.

    A unit whose gate could not be invoked at all is a could-not-look, never a pass: an
    uninvokable gate has not said that it checks a signature, and this check exists because
    something that was never observed was assumed for weeks."""
    lines: list[tuple[str, str]] = []
    bad, unknown = 0, 0
    for unit in sorted(observations):
        obs = observations[unit]
        version, accept, refuse = obs.get("version"), obs.get("accept"), obs.get("refuse")
        if accept is None or refuse is None:
            unknown += 1
            lines.append(("SKIP", f"{unit}'s own gate could not be invoked the way its own "
                                   f"shift-left.yml invokes it, so nothing was observed about "
                                   f"whether it checks a real signature: {obs.get('reason', '')}"))
            continue
        if accept["verdict"] != "adopt":
            bad += 1
            lines.append(("FAIL", f"{unit}'s gate did NOT accept platform's real published evidence "
                                   f"for policy {version} arriving in its window (exit "
                                   f"{accept['exit']}): {accept['output']}"))
        else:
            lines.append(("ok", f"{unit}: real cosign accepted platform's own published signature "
                                 f"for policy {version}, and the gate adopted"))
        if refuse["verdict"] != "refuse":
            bad += 1
            lines.append(("FAIL", f"{unit}'s gate ADOPTED the same evidence with one byte of "
                                   f"platform's own signature changed (exit {refuse['exit']}) -- it "
                                   f"is not checking the signature it says it checks"))
        elif "cosign" not in refuse["output"].lower() and "signature" not in refuse["output"].lower():
            bad += 1
            lines.append(("FAIL", f"{unit}'s gate refused the tampered evidence, but for a reason "
                                   f"that names neither cosign nor the signature -- a refusal about "
                                   f"something else is not evidence that the signature was checked: "
                                   f"{refuse['output']}"))
        else:
            lines.append(("ok", f"{unit}: the same bundle with one signature byte changed was "
                                 f"refused, naming the signature -- {refuse['output'][:120]}"))
    if bad:
        return "FAIL", lines + [("FAIL", f"{bad} half-check(s) observed false: an adopter gate that "
                                          f"did not verify platform's real published signature, or "
                                          f"did not refuse a corrupted one -- each named above")]
    if unknown and not lines:
        return "SKIP", lines
    if unknown:
        return "SKIP", lines + [("SKIP", f"{unknown} adopter gate(s) could not be invoked, so the "
                                          f"estate has not been observed whole")]
    return "PASS", lines


# --------------------------------------------------------------------------------------------
# the estate
# --------------------------------------------------------------------------------------------
def pick_version(platform_dir: Path) -> str | None:
    """A version platform really published a bundle for at HEAD_TAG whose OWN computed bump is
    below major -- so an ACCEPT is observable as an accept, instead of arriving through the
    designed composed-major refusal every adopter gate raises. Chosen from the tag's own tree on
    every run: hard-coding it is how a check ends up grading a version that has left the window."""
    root = platform_dir / "computed-semver" / "evidence"
    for doc in sorted(root.glob("*.json")):
        bundle = doc.with_name(doc.name + ".bundle")
        if not bundle.is_file() or doc.name[:-5] == STANDING:
            continue
        try:
            computed = json.loads(doc.read_text())["bump"]["computed"]
        except (json.JSONDecodeError, KeyError, OSError):
            continue
        if computed in ("none", "patch", "minor"):
            return doc.name[:-5]
    return None


def _clone(src: Path, dst: Path) -> None:
    subprocess.run(["git", "clone", "--local", "--quiet", str(src), str(dst)],
                   check=True, capture_output=True)


def offline_exit(fold, unit: str, unit_dir: Path, planted: dict, platform_dir: Path,
                 adopter_repo: Path, workdir: Path) -> int | None:
    """The number this check reports and does not grade: what THIS adopter's OWN gate, invoked
    exactly the way its own workflow invokes it, does against platform's real published evidence
    with a cold TUF cache and every proxy pointed at a closed port.

    It re-runs the accept half rather than calling cosign itself. An earlier draft here hand-rolled
    a flagless `cosign verify-blob`, which is a proxy for the gate and not the gate: it reported
    ludlow as network-dependent when ludlow's own gate, which pins its trust material, verifies
    offline. Naming the served artefact and the operation that reaches it is this whole ticket, and
    the first version of this function got the operation wrong.

    0 means the repository's signature check needs no network. Anything else means it fetches a
    Sigstore trust root, which a CI runner does on every single run, because a runner is cold every
    time."""
    cold_home, cold_tuf = workdir / "cold-home", workdir / "cold-tuf"
    cold_home.mkdir(parents=True, exist_ok=True)
    cold_tuf.mkdir(parents=True, exist_ok=True)
    cold = {"HOME": str(cold_home), "TUF_ROOT": str(cold_tuf),
            "HTTPS_PROXY": "http://127.0.0.1:1", "HTTP_PROXY": "http://127.0.0.1:1",
            "ALL_PROXY": "socks5://127.0.0.1:1"}
    restore = {k: os.environ.get(k) for k in cold}
    os.environ.update(cold)
    try:
        result, _ = fold.run_gate(unit, unit_dir, planted, platform_dir, adopter_repo, workdir)
    finally:
        for key, was in restore.items():
            if was is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = was
    return None if result is None else result["exit"]


SHA = 40


def _hermetic_git() -> dict[str, str]:
    """Every planted repository in this run is built with the operator's global and system git
    configuration switched off.

    Not tidiness. On 2026-09-06 this machine's global `core.hooksPath` hook stopped being able to
    run (an API quota), so `git commit` failed silently inside the planting -- and
    fold_agreement._commit returns `git rev-parse HEAD`'s stdout, which on a repository with no
    commits is the literal string "HEAD" with a non-zero exit nobody reads. Two of three gates then
    answered a question nobody had planted (ludlow saw an unchanged pin and adopted; only
    tuppence's gate, which refuses an unreadable ref, said so out loud) and the run would have
    reported the estate green. A grader that can be turned green by somebody's laptop hook is worse
    than no grader, so the planting is hermetic and the shas are checked below."""
    return {"GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_SYSTEM": os.devnull}


def _planted_or_none(planted: dict) -> str | None:
    """The reason this planting cannot be graded, or None. A sha that is not a sha means the
    commit did not happen, and every verdict downstream of it is about nothing."""
    for field in ("base_sha", "head_sha"):
        value = planted.get(field, "")
        if len(value) != SHA or not all(c in "0123456789abcdef" for c in value.lower()):
            return (f"the planted adopter repository could not be committed ({field} came back "
                     f"{value!r}, which is not a commit) -- nothing was planted, so nothing about "
                     f"any gate's answer would mean anything")
    return None


def run(estate: Path) -> tuple[str, list[tuple[str, str]]]:
    estate = estate.resolve()
    fold = _fold()

    spec = importlib.util.spec_from_file_location(
        "twin_per_adopter", HERE.parent / "twin-per-adopter" / "twin_per_adopter.py")
    tpa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tpa)
    units = [u for u in tpa.adopters(estate) if (estate / u).is_dir()]
    if not units:
        return "SKIP", [("SKIP", "no party in this estate claims the adopter role, so there is no "
                                  "adopter gate whose signature check could be observed")]
    platform_src = estate / "platform"
    if not (platform_src / ".git").is_dir():
        return "SKIP", [("SKIP", "this checkout carries no clone of platform, whose published "
                                  "signature is the only thing an adopter gate can be observed "
                                  "verifying")]
    if shutil.which("cosign") is None:
        return "SKIP", [("SKIP", "cosign is not installed, so no gate here can verify or refuse a "
                                  "real signature and nothing would be observed")]

    lines: list[tuple[str, str]] = []
    observations: dict[str, dict] = {}
    hermetic = _hermetic_git()
    restore_git = {k: os.environ.get(k) for k in hermetic}
    os.environ.update(hermetic)
    try:
        return _observe(estate, fold, units, platform_src, lines, observations)
    finally:
        for key, was in restore_git.items():
            if was is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = was


def _observe(estate: Path, fold, units: list[str], platform_src: Path,
             lines: list[tuple[str, str]],
             observations: dict[str, dict]) -> tuple[str, list[tuple[str, str]]]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        clean, corrupt = root / "platform", root / "platform-corrupt"
        _clone(platform_src, clean)
        tag_commits = {}
        for tag in (BASE_TAG, HEAD_TAG):
            resolved = fold._git(clean, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
            if resolved.returncode != 0:
                return "SKIP", [("SKIP", f"this checkout of platform has no tag object for {tag}, "
                                          f"which the planted movement pins")]
            tag_commits[tag] = resolved.stdout.strip()
        fold._git(clean, "checkout", "--quiet", HEAD_TAG)
        version = pick_version(clean)
        if version is None:
            return "SKIP", [("SKIP", f"platform at {HEAD_TAG} publishes no evidence document with a "
                                      f"committed bundle whose own computed bump is below major, so "
                                      f"an ACCEPT could not be told apart from the designed "
                                      f"composed-major refusal")]
        lines.append(("ok", f"platform checked out at {HEAD_TAG} ({tag_commits[HEAD_TAG][:12]}); the "
                             f"served artefact is its own published evidence for policy {version}"))

        # The corrupt estate: the SAME repository, the SAME tag, one byte of the publisher's own
        # signature changed, re-tagged so every gate's own pin check still passes and the only
        # thing left for a gate to notice is the signature.
        _clone(platform_src, corrupt)
        fold._git(corrupt, "checkout", "--quiet", HEAD_TAG)
        bundle = corrupt / "computed-semver" / "evidence" / f"{version}.json.bundle"
        try:
            bundle.write_text(tamper_signature(bundle.read_text()))
        except (ValueError, json.JSONDecodeError) as exc:
            return "SKIP", [("SKIP", f"platform's published bundle for {version} has a shape whose "
                                      f"signature this check cannot corrupt ({exc}), so the refuse "
                                      f"half could not be planted and half an observation is none")]
        corrupt_commit = fold._commit(corrupt, "one byte of the publisher's signature changed")
        fold._git(corrupt, "tag", "-f", HEAD_TAG)
        corrupt_tags = dict(tag_commits, **{HEAD_TAG: corrupt_commit})
        lines.append(("ok", f"the same tag re-cut with one base64 character of policy {version}'s "
                             f"real signature changed ({corrupt_commit[:12]}) -- nothing else moved, "
                             f"so a gate that adopts it adopted an unverified signature"))

        for unit in units:
            print(f"... {unit}", file=sys.stderr, flush=True)
            unit_dir = estate / unit
            obs: dict = {"version": version, "reason": ""}
            for half, platform_dir, tags in (("accept", clean, tag_commits),
                                             ("refuse", corrupt, corrupt_tags)):
                workdir = root / f"{unit}-{half}"
                workdir.mkdir(parents=True, exist_ok=True)
                planted = fold.plant(workdir / "adopter", ([STANDING], [STANDING, version],
                                                            BASE_TAG, HEAD_TAG), tags)
                unplanted = _planted_or_none(planted)
                if unplanted is not None:
                    obs[half], obs["reason"] = None, unplanted
                    continue
                result, reason = fold.run_gate(unit, unit_dir, planted, platform_dir,
                                               workdir / "adopter", workdir)
                obs[half] = result
                if result is None:
                    obs["reason"] = reason
            observations[unit] = obs

            cold_dir = root / f"{unit}-cold"
            cold_dir.mkdir(parents=True, exist_ok=True)
            cold_planted = fold.plant(cold_dir / "adopter", ([STANDING], [STANDING, version],
                                                             BASE_TAG, HEAD_TAG), tag_commits)
            cold = (None if _planted_or_none(cold_planted) is not None
                    else offline_exit(fold, unit, unit_dir, cold_planted, clean,
                                      cold_dir / "adopter", cold_dir))
            if cold is None:
                lines.append(("note", f"{unit}: the offline measurement could not be taken -- its "
                                       f"gate could not be invoked at all"))
            elif cold == 0:
                lines.append(("note", f"{unit}: its own gate verifies platform's real published "
                                       f"bundle with a cold TUF cache and every proxy pointed at a "
                                       f"closed port -- exit 0, no network needed"))
            else:
                lines.append(("note", f"{unit}: its own gate cannot verify platform's real published "
                                       f"bundle with a cold TUF cache and egress blocked -- exit "
                                       f"{cold}, so this repository's signature check fetches a "
                                       f"Sigstore trust root on every CI run, which is cold every "
                                       f"time (eco-system ticket 103)"))

    verdict, graded = grade(observations)
    return verdict, lines + graded


def selfcheck() -> int:
    """The rules, on planted inputs. A comparator only ever run against gates that behave has
    proved nothing about what it would say when one does not."""
    failures: list[str] = []

    def check(label: str, got, want) -> None:
        if got != want:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    legacy = json.dumps({"base64Signature": "AAAA", "cert": "x", "rekorBundle": {}})
    check("legacy tamper changes exactly the signature",
          json.loads(tamper_signature(legacy))["base64Signature"], "BAAA")
    check("legacy tamper leaves the certificate alone", json.loads(tamper_signature(legacy))["cert"], "x")
    new = json.dumps({"mediaType": "m", "verificationMaterial": {}, "messageSignature": {"signature": "BBBB"}})
    check("new-format tamper changes the signature",
          json.loads(tamper_signature(new))["messageSignature"]["signature"], "CBBB")
    for bad, why in ((json.dumps({"nothing": "here"}), "no signature field"),
                     (json.dumps(["not", "an", "object"]), "not an object"),
                     (json.dumps({"mediaType": "m", "messageSignature": {"signature": ""}}), "empty signature")):
        try:
            tamper_signature(bad)
            failures.append(f"tamper_signature accepted a bundle with {why} -- the refuse half "
                            f"would then be a second accept and would pass")
        except ValueError:
            pass

    adopt = {"verdict": "adopt", "composed": "none", "exit": 0, "argv": [], "output": "PASS"}
    refuse_sig = {"verdict": "refuse", "composed": None, "exit": 1, "argv": [],
                  "output": "cosign verify-blob refused the evidence signature"}
    refuse_flag = {"verdict": "refuse", "composed": None, "exit": 1, "argv": [],
                   "output": "Error: --trusted-root only supported with --new-bundle-format"}

    verdict, lines = grade({"a": {"version": "1.0.0", "accept": adopt, "refuse": refuse_sig}})
    check("a gate that accepts the real signature and refuses the corrupted one passes", verdict, "PASS")

    # The exact shape ludlow shipped: it refused BOTH halves. A check that graded only the refuse
    # half would have called that a pass, which is how the defect survived.
    verdict, lines = grade({"ludlow": {"version": "1.0.0", "accept": refuse_flag, "refuse": refuse_flag}})
    check("a gate that refuses the real signature too is false", verdict, "FAIL")
    check("and it is named", any("ludlow" in text and "did NOT accept" in text
                                 for level, text in lines if level == "FAIL"), True)

    verdict, lines = grade({"a": {"version": "1.0.0", "accept": adopt, "refuse": adopt}})
    check("a gate that adopts a corrupted signature is false", verdict, "FAIL")
    check("and it is named as adopting the tampered evidence",
          any("ADOPTED the same evidence" in text for level, text in lines if level == "FAIL"), True)

    # A refusal about something other than the signature is not evidence the signature was read.
    refuse_pin = {"verdict": "refuse", "composed": None, "exit": 1, "argv": [],
                  "output": "platform tag resolves to a different commit than the pin names"}
    verdict, _ = grade({"a": {"version": "1.0.0", "accept": adopt, "refuse": refuse_pin}})
    check("a refusal that names neither cosign nor the signature is false", verdict, "FAIL")

    verdict, lines = grade({"a": {"version": "1.0.0", "accept": None, "refuse": None,
                                   "reason": "no gate script"}})
    check("a gate that could not be invoked is a could-not-look, never a pass", verdict, "SKIP")

    verdict, _ = grade({"a": {"version": "1.0.0", "accept": adopt, "refuse": refuse_sig},
                        "b": {"version": "1.0.0", "accept": None, "refuse": None, "reason": "x"}})
    check("one unknown among the observed is still a could-not-look for the estate", verdict, "SKIP")

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("PASS: real_signature.py selfcheck -- the tamper touches exactly one signature and "
          "refuses a shape it cannot corrupt, a gate that refuses the real signature is false, a "
          "gate that adopts a corrupted one is false, a refusal naming neither cosign nor the "
          "signature is false, and a gate that could not be invoked is a could-not-look")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selfcheck":
        return selfcheck()
    if not argv:
        print("SKIP: no estate directory given")
        return 3
    verdict, lines = run(Path(argv[0]))
    for level, text in lines:
        print(f"{level}: {text}")
    if verdict == "PASS":
        print(f"SUMMARY: every adopter gate in this estate accepted platform's own published "
              f"signature and refused the same evidence with one byte of it changed, each through "
              f"its own workflow's own invocation and its own identity constant")
        return 0
    return 3 if verdict == "SKIP" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
