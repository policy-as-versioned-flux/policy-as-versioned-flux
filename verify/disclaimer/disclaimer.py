#!/usr/bin/env python3
"""disclaimer.py — ticket 82: the legal realism of nine public repositories, machine-checked
(pure stdlib plus pyyaml, offline).

The estate's two regulators carry the names of the real bodies whose figures they repackage
(ico's signed feed says `authority: ICO (Information Commissioner's Office)`; nist redistributes
the genuine SP 800-53 catalogue). Nothing said, on any README or party artefact, that the party
is a demonstration and not the regulator. This module refuses an estate where that is still so:

    party.yaml   -> carries DISCLAIMER as a `#` comment line. A comment, not a key: the
                    artefact is signed under the unit's tag and validated against
                    platform/party/schema.json (additionalProperties: false), so a key would
                    change every signed artefact and need a platform tag first. A later ticket
                    that wants it machine-readable edits schema.json and this check together.
    README.md    -> carries DISCLAIMER, anywhere.
    ico, nist    -> DISCLAIMER.md exists and carries DISCLAIMER (the two parties that name a
                    real authority get the long form).
    nist/NOTICE  -> attributes the catalogue and the three baselines to NIST as a US Government
                    work, and cites the SAME upstream URL and sha256 values catalog/*.json
                    record, so the notice cannot drift from the artefact it attributes.
    hub          -> LICENSE is Apache-2.0 and README says so (the hub was the one repository of
                    nine with no licence at all).

Usage:
    disclaimer.py check       # refuse (non-zero, lists why) any unit missing a line
    disclaimer.py selfcheck   # + prove the guard bites (plants each violation) + the counts
    disclaimer.py notice DIR  # print the NOTICE text rendered from DIR/catalog/*.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from typing import Any, Callable, Sequence

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))  # verify/, for _estate
from _estate import ESTATE  # noqa: E402

HUB = os.path.normpath(os.path.join(HERE, "..", ".."))
ROLES = os.path.join(os.path.dirname(HERE), "party", "roles.json")

# The one line. Under 100 characters so it fits a party.yaml comment without wrapping, and the
# same bytes in every README, every party artefact and both DISCLAIMER.md files, so one grep
# finds it everywhere and a paraphrase is a refusal, not a variant.
DISCLAIMER = ("A demonstration party, not affiliated with, endorsed by or speaking for any real "
              "authority it names.")
REGULATORS = ("ico", "nist")

_COMMENT = re.compile(r"^\s*#\s*" + re.escape(DISCLAIMER) + r"\s*$", re.M)


def _read(path: str) -> str | None:
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except OSError:
        return None


def party_yaml_problems(path: str | os.PathLike[str]) -> list[str]:
    """The artefact carries the line as a comment, and still parses as the signed shape."""
    path = os.fspath(path)
    rel = os.path.join(os.path.basename(os.path.dirname(path)), "party.yaml")
    text = _read(path)
    if text is None:
        return [f"{rel}: missing"]
    problems = []
    if not _COMMENT.search(text):
        if DISCLAIMER in text:
            problems.append(f"{rel}: the disclaimer is present but not as a `#` comment line "
                            "(a key changes the signed artefact and needs schema.json first)")
        else:
            problems.append(f"{rel}: no disclaimer comment line; expected `# {DISCLAIMER}`")
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        return problems + [f"{rel}: does not parse as YAML ({exc.__class__.__name__})"]
    if not isinstance(doc, dict) or not doc.get("party"):
        problems.append(f"{rel}: parses, but not to a party artefact (no `party:` key)")
    return problems


def readme_problems(path: str | os.PathLike[str]) -> list[str]:
    path = os.fspath(path)
    rel = os.path.join(os.path.basename(os.path.dirname(path)), "README.md")
    text = _read(path)
    if text is None:
        return [f"{rel}: missing"]
    if DISCLAIMER not in text:
        return [f"{rel}: does not carry the disclaimer line"]
    return []


def disclaimer_md_problems(unit_dir: str | os.PathLike[str]) -> list[str]:
    unit_dir = os.fspath(unit_dir)
    rel = os.path.join(os.path.basename(unit_dir), "DISCLAIMER.md")
    text = _read(os.path.join(unit_dir, "DISCLAIMER.md"))
    if text is None:
        return [f"{rel}: missing"]
    if DISCLAIMER not in text:
        return [f"{rel}: does not carry the disclaimer line"]
    return []


def _provenance(unit_dir: str) -> tuple[dict[str, Any], dict[str, Any]]:
    cat = json.loads(_read(os.path.join(unit_dir, "catalog", "CATALOG_VERSION.json")) or "{}")
    base = json.loads(_read(os.path.join(unit_dir, "catalog", "BASELINE_VERSIONS.json")) or "{}")
    return cat, base


def notice_facts(unit_dir: str | os.PathLike[str]) -> list[tuple[str, str]]:
    """(label, value) pairs a NOTICE must quote verbatim: the upstream URL and every sha256 the
    catalogue and baseline manifests record. Read from the manifests, never hard-coded, so a
    catalogue bump that forgets the NOTICE is a refusal."""
    unit_dir = os.fspath(unit_dir)
    cat, base = _provenance(unit_dir)
    facts: list[tuple[str, str]] = []
    if cat.get("source", {}).get("url"):
        facts.append(("catalogue upstream url", cat["source"]["url"]))
    if cat.get("sha256"):
        facts.append((f"catalogue sha256 ({cat.get('file', '?')})", cat["sha256"]))
    for name, entry in sorted((base.get("baselines") or {}).items()):
        if entry.get("sha256"):
            facts.append((f"{name} baseline sha256 ({entry.get('file', '?')})", entry["sha256"]))
    return facts


def notice_problems(unit_dir: str | os.PathLike[str]) -> list[str]:
    unit_dir = os.fspath(unit_dir)
    rel = os.path.join(os.path.basename(unit_dir), "NOTICE")
    text = _read(os.path.join(unit_dir, "NOTICE"))
    if text is None:
        return [f"{rel}: missing"]
    problems = []
    facts = notice_facts(unit_dir)
    if not any("catalogue" in label for label, _ in facts):
        problems.append(f"{rel}: catalog/CATALOG_VERSION.json records no url or sha256 to cite")
    if not any("baseline sha256" in label for label, _ in facts):
        # The NOTICE attributes the three baselines; an unreadable manifest must not become a
        # pass for that half of the attribution.
        problems.append(f"{rel}: catalog/BASELINE_VERSIONS.json records no baseline sha256 to "
                        "cite (missing, unreadable or empty)")
    for label, value in facts:
        if value not in text:
            problems.append(f"{rel}: does not cite the {label} the manifest records: {value}")
    for phrase in ("public domain", "17 U.S.C.", "National Institute of Standards and Technology"):
        if phrase not in text:
            problems.append(f"{rel}: does not say '{phrase}'")
    return problems


def render_notice(unit_dir: str | os.PathLike[str]) -> str:
    """The NOTICE text for nist, rendered from its own provenance manifests."""
    unit_dir = os.fspath(unit_dir)
    cat, base = _provenance(unit_dir)
    src = cat.get("source", {})
    lines = [
        "policy-as-versioned-nist",
        "",
        "This repository redistributes, verbatim, the following works of the",
        "National Institute of Standards and Technology (NIST), an agency of the United States",
        "Department of Commerce:",
        "",
        f"  {src.get('nistCatalogTitle', 'NIST SP 800-53 OSCAL catalogue')}",
        f"  (SP 800-53 revision {src.get('nistMetadataVersion', '?')}, OSCAL {src.get('oscalVersion', '?')})",
        f"  and its LOW, MODERATE and HIGH baseline profiles.",
        "",
        "Works of the United States Government are not subject to copyright protection in the",
        "United States (17 U.S.C. section 105) and are in the public domain there. NIST asks that",
        "the source be credited; no endorsement by NIST is claimed or implied. The catalogue and",
        "the baselines are NOT licensed under this repository's Apache-2.0 LICENSE, which covers",
        "only the wrapper this party adds around them: party.yaml, the scripts, the version and",
        "provenance manifests, and the README.",
        "",
        f"Source: {src.get('upstream', '?')}",
        f"  {src.get('url', '?')}",
    ]
    if base.get("source", {}).get("urlTemplate"):
        lines.append(f"  {base['source']['urlTemplate']}")
    lines += [
        "",
        "The exact bytes redistributed, as recorded in catalog/CATALOG_VERSION.json and",
        "catalog/BASELINE_VERSIONS.json (verify/disclaimer in the hub refuses a NOTICE that",
        "disagrees with either manifest):",
        "",
    ]
    for label, value in notice_facts(unit_dir):
        if "sha256" in label:  # the url is already cited under Source: above
            lines.append(f"  {value}  {label}")
    lines += [
        "",
        f"Fetched {src.get('fetchedAt', '?')} (catalogue), "
        f"{base.get('source', {}).get('fetchedAt', '?')} (baselines).",
        "",
        DISCLAIMER,
        "",
    ]
    return "\n".join(lines)


def hub_problems(hub_root: str | os.PathLike[str]) -> list[str]:
    hub_root = os.fspath(hub_root)
    problems = []
    lic = _read(os.path.join(hub_root, "LICENSE"))
    if lic is None:
        problems.append("hub LICENSE: missing")
    elif "Apache License" not in lic or "Version 2.0" not in lic:
        problems.append("hub LICENSE: present but not the Apache License, Version 2.0")
    readme = _read(os.path.join(hub_root, "README.md"))
    if readme is None or "Apache-2.0" not in readme or "LICENSE" not in readme:
        problems.append("hub README.md: does not name the Apache-2.0 LICENSE")
    return problems


def load_parties(roles_path: str = ROLES) -> list[str]:
    with open(roles_path) as fh:
        return sorted(json.load(fh)["parties"])


def check_all(parties: Sequence[str], estate_dir: str | os.PathLike[str] = ESTATE,
              hub_root: str | os.PathLike[str] = HUB) -> list[str]:
    estate_dir = os.fspath(estate_dir)
    problems: list[str] = []
    for party in parties:
        unit = os.path.join(estate_dir, party)
        problems += party_yaml_problems(os.path.join(unit, "party.yaml"))
        problems += readme_problems(os.path.join(unit, "README.md"))
        if party in REGULATORS:
            problems += disclaimer_md_problems(unit)
        if party == "nist":
            problems += notice_problems(unit)
    problems += hub_problems(hub_root)
    return problems


# --- commands -------------------------------------------------------------
def cmd_check(_args: argparse.Namespace) -> None:
    if not os.path.isdir(os.path.join(ESTATE, "platform")):
        print("SKIP: no .estate-clone/ -- run ./clone-estate.sh first")
        sys.exit(3)
    parties = load_parties()
    problems = check_all(parties)
    if problems:
        sys.exit("REFUSED — the estate does not say what it is:\n" +
                 "\n".join(f"  - {p}" for p in problems))
    print(f"ok  {len(parties)} parties: every party.yaml and README carries the disclaimer line, "
          f"{'/'.join(REGULATORS)} carry DISCLAIMER.md, nist/NOTICE cites the catalogue it "
          "attributes, the hub is Apache-2.0")


def _plant(tmp: str, name: str, mutate: Callable[[str], None]) -> None:
    """Copy the real unit's checked files into tmp/<name>, then break one thing."""
    src = os.path.join(ESTATE, name)
    dst = os.path.join(tmp, name)
    os.makedirs(os.path.join(dst, "catalog"), exist_ok=True)
    for f in ("party.yaml", "README.md", "DISCLAIMER.md", "NOTICE"):
        if os.path.isfile(os.path.join(src, f)):
            shutil.copy(os.path.join(src, f), os.path.join(dst, f))
    for f in ("CATALOG_VERSION.json", "BASELINE_VERSIONS.json"):
        if os.path.isfile(os.path.join(src, "catalog", f)):
            shutil.copy(os.path.join(src, "catalog", f), os.path.join(dst, "catalog", f))
    mutate(dst)


def cmd_selfcheck(_args: argparse.Namespace) -> None:
    if not os.path.isdir(os.path.join(ESTATE, "platform")):
        print("SKIP: no .estate-clone/ -- run ./clone-estate.sh first")
        sys.exit(3)
    # 1. The real estate is clean.
    parties = load_parties()
    problems = check_all(parties)
    assert not problems, "\n".join(problems)

    # 2. The guard bites: plant each violation in isolation (never touching the real committed
    #    files) and watch check_all refuse it, then watch the restored copy pass.
    with tempfile.TemporaryDirectory() as tmp:
        def strip_comment(d: str) -> None:
            p = os.path.join(d, "party.yaml")
            with open(p) as fh:
                text = fh.read()
            with open(p, "w") as fh:
                fh.write(_COMMENT.sub("", text))

        def as_key(d: str) -> None:
            p = os.path.join(d, "party.yaml")
            with open(p) as fh:
                text = fh.read()
            with open(p, "w") as fh:
                fh.write(_COMMENT.sub(f"disclaimer: {DISCLAIMER}", text))

        def strip_readme(d: str) -> None:
            p = os.path.join(d, "README.md")
            with open(p) as fh:
                text = fh.read()
            with open(p, "w") as fh:
                fh.write(text.replace(DISCLAIMER, "a README that says nothing about being a demo"))

        def drift_notice(d: str) -> None:
            p = os.path.join(d, "NOTICE")
            cat = json.loads(open(os.path.join(d, "catalog", "CATALOG_VERSION.json")).read())
            with open(p) as fh:
                text = fh.read()
            with open(p, "w") as fh:
                fh.write(text.replace(cat["sha256"], "0" * 64))

        def drop_disclaimer_md(d: str) -> None:
            os.remove(os.path.join(d, "DISCLAIMER.md"))

        def untouched(_d: str) -> None:
            pass

        plants: list[tuple[str, Callable[[str], None], str]] = [
            ("driftwood", strip_comment, "no disclaimer comment"),
            ("platform", as_key, "not as a `#` comment"),
            ("feeds", strip_readme, "README.md: does not carry"),
            ("nist", drift_notice, "NOTICE: does not cite the catalogue sha256"),
            ("ico", drop_disclaimer_md, "DISCLAIMER.md: missing"),
        ]
        for name, mutate, expect in plants:
            _plant(tmp, name, mutate)
            got = check_all([name], estate_dir=tmp, hub_root=HUB)
            assert got and any(expect in g for g in got), f"planted {name}/{mutate.__name__} not refused: {got}"
            _plant(tmp, name, untouched)
            got = check_all([name], estate_dir=tmp, hub_root=HUB)
            assert not got, f"restored {name} must pass: {got}"

        # the hub without its LICENSE is refused too
        hub = os.path.join(tmp, "hub")
        os.makedirs(hub)
        shutil.copy(os.path.join(HUB, "README.md"), os.path.join(hub, "README.md"))
        got = hub_problems(hub)
        assert got and "LICENSE: missing" in got[0], got

    print("ok  guard bites: a party.yaml without the comment, the line as a key, a bare README, a "
          "drifted NOTICE sha256, a missing DISCLAIMER.md and a hub without LICENSE are each refused "
          "when planted, cleared once restored")
    print(f"ok  real estate: {len(parties)} parties carry the line on party.yaml and README | "
          f"DISCLAIMER.md on {', '.join(REGULATORS)} | nist/NOTICE cites {len(notice_facts(os.path.join(ESTATE, 'nist')))} "
          "provenance facts | hub LICENSE Apache-2.0")


def cmd_notice(args: argparse.Namespace) -> None:
    sys.stdout.write(render_notice(args.dir))


def main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="ticket 82: disclaimers, NOTICE and licence, checked.")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check", help="refuse any unit missing its line").set_defaults(func=cmd_check)
    sub.add_parser("selfcheck", help="check + prove the guard bites").set_defaults(func=cmd_selfcheck)
    n = sub.add_parser("notice", help="render nist's NOTICE from its provenance manifests")
    n.add_argument("dir")
    n.set_defaults(func=cmd_notice)
    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
