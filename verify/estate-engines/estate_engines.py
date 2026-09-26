#!/usr/bin/env python3
"""estate_engines.py -- eco-system ticket 146 item 7, hub ADR-0033 point 5: the estate's own
engine pins name a supported engine of everything it serves.

A policy line supports exactly the engines in its `tested_engines` (ADR-0033 point 1), and the
machinery the composer renders supports exactly the engines in platform
`distribution/machinery.yaml`. The estate runs its own engine in five places. Each must name a
row of platform `engine/kyverno/engine-table.yaml`, carry that row's checksum where it carries
one, and be listed by every SERVED line and by the machinery:

  hub      .github/workflows/truth.yml          env KYVERNO_VERSION and KYVERNO_SHA256: the CLI
                                                the gate observes with (linux_x86_64 archive)
  platform .github/workflows/release.yml        the same pair: the CLI the release proof runs
  platform .github/workflows/cut-release.yml    the same pair: the CLI the publisher gate runs
  platform engine/kyverno/helmrelease.yaml      the HelmRelease's chart version, mapped to an
                                                engine through the table's `chart.version` column
  hub      tests/test_cage_ladder_holes.py      PINNED_KYVERNO, read with `ast`

A SERVED line is a cut element of platform `distribution/versions.yaml` (it carries `commit`, so
Flux can deliver its signed tag). An uncut candidate serves nothing yet, and its cut is graded by
the engine grader before the tag is signed. Whether a line PASSES on what it lists is the
grader's question (computed-semver/verify-cage-engine.sh); this check reads what is listed. An
adopter's own engine is out of scope: ticket 147 makes it the adopter's declared engine and
ticket 148 prices it.

Usage:
    estate_engines.py check [--hub DIR] [--estate DIR]
    estate_engines.py selfcheck
Exit 0 every pin holds; 1 one does not, named; 3 no platform clone to read.
"""
from __future__ import annotations

import argparse
import ast
import copy
import re
import sys
import tempfile
from pathlib import Path

import yaml

HUB = Path(__file__).resolve().parents[2]
TABLE = "engine/kyverno/engine-table.yaml"
ARCHIVE = "kyverno-cli_v${KYVERNO_VERSION}_linux_x86_64.tar.gz"
PINS = (
    ("hub truth.yml CLI", "hub", ".github/workflows/truth.yml", "workflow"),
    ("platform release.yml CLI", "platform", ".github/workflows/release.yml", "workflow"),
    ("platform cut-release.yml CLI", "platform", ".github/workflows/cut-release.yml", "workflow"),
    ("platform reference install (engine/kyverno/helmrelease.yaml chart)", "platform",
     "engine/kyverno/helmrelease.yaml", "chart"),
    ("hub test constant PINNED_KYVERNO (tests/test_cage_ladder_holes.py)", "hub",
     "tests/test_cage_ladder_holes.py", "constant"),
)


class CouldNotLook(Exception):
    pass


def read_table(platform: Path) -> dict[str, dict]:
    """version -> {sha256 (linux_x86_64 archive), chart}. Raises ValueError on a malformed table."""
    path = platform / TABLE
    doc = yaml.safe_load(path.read_text())
    rows = (doc or {}).get("versions") if isinstance(doc, dict) else None
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"{TABLE} lists no version")
    out: dict[str, dict] = {}
    for row in rows:
        v = str(row.get("version", ""))
        sha = ((row.get("cli") or {}).get("linux_x86_64") or {}).get("sha256")
        chart = (row.get("chart") or {}).get("version")
        if not re.fullmatch(r"\d+\.\d+\.\d+", v) or not re.fullmatch(r"[0-9a-f]{64}", str(sha or "")):
            raise ValueError(f"{TABLE}: row {v!r} has no exact version or no linux_x86_64 sha256")
        out[v] = {"sha256": sha, "chart": str(chart) if chart is not None else None}
    return out


def _listed(declaration) -> set[str] | None:
    if not isinstance(declaration, dict) or not isinstance(declaration.get("kyverno"), list):
        return None
    return {str(v) for v in declaration["kyverno"]}


def served_subjects(platform: Path) -> list[tuple[str, set[str] | None]]:
    """(subject, the engines it lists or None) for every cut line and for the machinery."""
    doc = yaml.safe_load((platform / "distribution/versions.yaml").read_text())
    elements = doc["spec"]["inputs"][0]["versions"]
    subjects = [(f"policy {e.get('version')}", _listed(e.get("tested_engines")))
                for e in elements if isinstance(e, dict) and e.get("commit")]
    machinery = platform / "distribution/machinery.yaml"
    declared = yaml.safe_load(machinery.read_text()) if machinery.is_file() else None
    subjects.append(("machinery", _listed((declared or {}).get("tested_engines")
                                          if isinstance(declared, dict) else None)))
    return subjects


def read_pin(kind: str, path: Path, table: dict[str, dict]) -> dict:
    """What one pin names: its engine version, and the checksum it carries if it carries one."""
    text = path.read_text()
    if kind == "workflow":
        env = (yaml.safe_load(text) or {}).get("env") or {}
        version, sha = env.get("KYVERNO_VERSION"), env.get("KYVERNO_SHA256")
        if version is None or sha is None:
            raise ValueError("carries no KYVERNO_VERSION and KYVERNO_SHA256 in its workflow env")
        if ARCHIVE not in text:
            raise ValueError(f"does not download {ARCHIVE}, so its checksum is not the table's "
                             "linux_x86_64 column")
        return {"version": str(version), "sha256": str(sha)}
    if kind == "chart":
        releases = [d for d in yaml.safe_load_all(text)
                    if isinstance(d, dict) and d.get("kind") == "HelmRelease"
                    and (d.get("metadata") or {}).get("name") == "kyverno"]
        if len(releases) != 1:
            raise ValueError("carries no single HelmRelease named kyverno")
        chart = str(releases[0]["spec"]["chart"]["spec"]["version"])
        rows = [v for v, r in table.items() if r["chart"] == chart]
        if len(rows) != 1:
            raise ValueError(f"names chart {chart}, which is not in the table's chart column")
        return {"version": rows[0], "chart": chart}
    for node in ast.walk(ast.parse(text)):
        if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "PINNED_KYVERNO"
                                                 for t in node.targets)
                and isinstance(node.value, ast.Constant) and isinstance(node.value.value, str)):
            return {"version": node.value.value}
    raise ValueError("assigns no string to PINNED_KYVERNO")


def grade(hub: Path, estate: Path) -> tuple[int, list[str]]:
    platform = estate / "platform"
    if not (platform / "distribution/versions.yaml").is_file():
        raise CouldNotLook(f"no platform clone at {platform} (run ./clone-estate.sh)")
    lines: list[str] = []
    try:
        table = read_table(platform)
    except (OSError, ValueError, AttributeError, yaml.YAMLError) as exc:
        return 1, [f"FAIL: the platform engine table is not readable, so no pin can name a row of it: {exc}"]
    try:
        subjects = served_subjects(platform)
    except (OSError, KeyError, IndexError, TypeError, yaml.YAMLError) as exc:
        return 1, [f"FAIL: the platform's served lines are not readable: {exc}"]
    code = 0
    for label, where, rel, kind in PINS:
        path = (hub if where == "hub" else platform) / rel
        try:
            pin = read_pin(kind, path, table)
        except (OSError, ValueError, KeyError, TypeError, SyntaxError, yaml.YAMLError) as exc:
            lines.append(f"FAIL: {label}: {exc}")
            code = 1
            continue
        v = pin["version"]
        faults = []
        if v not in table:
            faults.append(f"{v} is not a row of the engine table (rows: {', '.join(sorted(table))})")
        elif "sha256" in pin and pin["sha256"] != table[v]["sha256"]:
            faults.append(f"its sha256 {pin['sha256'][:12]}... is not the table's linux_x86_64 "
                          f"{table[v]['sha256'][:12]}... for {v}")
        for subject, listed in subjects:
            if listed is None:
                faults.append(f"{subject} lists no tested_engines, so it supports no engine")
            elif v not in listed:
                faults.append(f"{v} is not a supported engine of {subject} (it lists {', '.join(sorted(listed))})")
        if faults:
            lines.append(f"FAIL: {label} names kyverno {v}: " + "; ".join(faults))
            code = 1
        else:
            lines.append(f"PASS: {label} names kyverno {v}, a row of the engine table"
                         + (", with the row's checksum" if "sha256" in pin else "")
                         + (f" (chart {pin['chart']})" if "chart" in pin else "")
                         + f", listed by {', '.join(s for s, _ in subjects)}")
    return code, lines


# ------------------------------------------------------------------------------ the selfcheck

_SHA = {"1.18.2": "a" * 64, "1.19.1": "b" * 64}


def _plant_estate(root: Path, *, table=None, versions=None, machinery=None, truth=None,
                  release=None, cut=None, chart="3.8.2", constant="1.18.2") -> tuple[Path, Path]:
    hub, platform = root / "hub", root / "estate/platform"

    def put(base: Path, rel: str, text: str) -> None:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)

    rows = table if table is not None else [
        {"version": v, "cli": {"linux_x86_64": {"sha256": s}}, "chart": {"version": c}}
        for (v, s), c in zip(_SHA.items(), ("3.8.2", "3.9.1"))]
    put(platform, TABLE, yaml.safe_dump({"schema": 1, "engine": "kyverno", "versions": rows}))
    elements = versions if versions is not None else [
        {"version": "5.0.0", "commit": "5" * 40, "tested_engines": {"kyverno": ["1.18.2"]}}]
    put(platform, "distribution/versions.yaml",
        yaml.safe_dump({"spec": {"inputs": [{"versions": elements}]}}))
    if machinery != "absent":
        put(platform, "distribution/machinery.yaml",
            yaml.safe_dump({"tested_engines": machinery or {"kyverno": ["1.18.2"]}}))

    def workflow(pair):
        v, s = pair or ("1.18.2", _SHA["1.18.2"])
        return (f"env:\n  KYVERNO_VERSION: {v}\n  KYVERNO_SHA256: {s}\njobs:\n  x:\n    steps:\n"
                f"    - run: curl -o k.tgz \"https://example.invalid/{ARCHIVE}\"\n")
    put(hub, ".github/workflows/truth.yml", workflow(truth))
    put(platform, ".github/workflows/release.yml", workflow(release))
    put(platform, ".github/workflows/cut-release.yml",
        cut if isinstance(cut, str) else workflow(cut))
    put(platform, "engine/kyverno/helmrelease.yaml", yaml.safe_dump_all([
        {"kind": "HelmRepository", "metadata": {"name": "kyverno"}},
        {"kind": "HelmRelease", "metadata": {"name": "kyverno"},
         "spec": {"chart": {"spec": {"chart": "kyverno", "version": chart}}}}]))
    put(hub, "tests/test_cage_ladder_holes.py", f'PINNED_KYVERNO = "{constant}"\n')
    return hub, root / "estate"


def selfcheck() -> int:
    cases = {
        "every pin on a supported row": ({}, 0, None),
        "the gate's CLI on a version with no row": ({"truth": ("1.20.0", "c" * 64)}, 1, "not a row"),
        "the gate's CLI on a row no served line supports": (
            {"truth": ("1.19.1", _SHA["1.19.1"])}, 1, "not a supported engine of policy 5.0.0"),
        "a release CLI whose checksum is not the row's": ({"release": ("1.18.2", "d" * 64)}, 1, "is not the table's"),
        "a reference install on a chart no line supports": ({"chart": "3.9.1"}, 1, "not a supported engine"),
        "a reference install on a chart the table does not list": ({"chart": "9.9.9"}, 1, "chart column"),
        "the test constant on an unsupported row": ({"constant": "1.19.1"}, 1, "PINNED_KYVERNO"),
        "a machinery that does not list the engine": (
            {"machinery": {"kyverno": ["1.19.1"]}}, 1, "not a supported engine of machinery"),
        "a machinery with no declaration": ({"machinery": "absent"}, 1, "machinery lists no tested_engines"),
        "a served line with no tested_engines": (
            {"versions": [{"version": "5.0.0", "commit": "5" * 40}]}, 1, "policy 5.0.0 lists no tested_engines"),
        "a cut-release that installs install.yaml, not the CLI archive": (
            {"cut": "env:\n  KYVERNO_VERSION: 1.18.2\n  KYVERNO_SHA256: " + _SHA["1.18.2"] + "\n"}, 1,
            "does not download"),
    }
    uncut_only = {"versions": [
        {"version": "5.0.0", "commit": "5" * 40, "tested_engines": {"kyverno": ["1.18.2"]}},
        {"version": "6.0.0", "tested_engines": {"kyverno": ["1.19.1"]}}]}
    cases["an uncut candidate serves nothing, so it does not bind the pins"] = (uncut_only, 0, None)
    bad = []
    for name, (plant, want, needle) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            hub, estate = _plant_estate(Path(tmp), **copy.deepcopy(plant))
            code, lines = grade(hub, estate)
        text = "\n".join(lines)
        if code != want or (needle and needle not in text):
            bad.append(f"{name}: exit {code}, wanted {want}" + (f" with {needle!r}" if needle else "")
                       + f"\n    {text}")
    if bad:
        print("FAIL: the selfcheck's planted pins did not grade as planted:\n  " + "\n  ".join(bad))
        return 1
    print(f"PASS: selfcheck: {len(cases)} planted estates grade as planted, including a pin on a "
          "row of the table that no served line supports")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("check", "selfcheck"))
    parser.add_argument("--hub", type=Path, default=HUB)
    parser.add_argument("--estate", type=Path, default=HUB / ".estate-clone")
    args = parser.parse_args(argv[1:])
    if args.mode == "selfcheck":
        return selfcheck()
    try:
        code, lines = grade(args.hub, args.estate)
    except CouldNotLook as exc:
        print(f"SKIP: {exc}")
        return 3
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
