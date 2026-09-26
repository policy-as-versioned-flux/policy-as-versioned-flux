#!/usr/bin/env python3
"""adopter_engines.py -- eco-system ticket 147, hub ADR-0033 point 2: each adopter declares its
engine in the file it installs from, the file agrees with the platform engine table, and adopters
that share a named cluster declare the same engine.

The served artefact is each adopter's `gitops/engine/kyverno.yaml`. Three operations read it:
the adopter's drift lane installs Kyverno from it (`drift-sample.yml`), its shift-left job
installs the offline CLI from it (`shift-left.yml`), and hub `talk/engine-up.sh <owner>`, which
`talk/up.sh` runs, installs a named cluster's Kyverno from the owner's copy. This module is the
reader `talk/engine-up.sh` uses, so the check grades the same parse the install acts on.

WHAT IS GRADED

 (a) The static check. Each adopter's file states an exact version, that release's install.yaml
     URL and sha256, and its linux_x86_64 CLI archive and sha256. Each figure must equal the row
     for that version in platform `engine/kyverno/engine-table.yaml`. The adopters are derived:
     every estate unit whose `party.yaml` claims the adopter role.
 (b) One engine per shared cluster. Which adopter uses which named cluster is derived from the
     scripts `talk/up.sh` runs. Each `step` names a unit's script, and the script names its
     cluster by `CTX="${CTX:-kind-<name>}"`, or by the `CLUSTER=<name>` of the lib.sh it sources.
     Adopters that use one cluster must declare the same engine. Today that is driftwood (its
     scripts/up.sh) and tuppence (its reset/up.sh) on kind-driftwood; nothing here names them.
 (c) talk/up.sh installs each engine from the owner's declaration. An adopter owns the cluster
     its own scripts create (`kind create cluster --name`). The platform's layers need an engine
     wherever they run, so each cluster a platform step targets must get one from
     `talk/engine-up.sh <owner>`, and no other cluster may get one (ticket 71, decision 17: this
     adds no engine to a cluster that has none). No step may run the platform's reference
     install, `engine/up.sh`.

WHAT IS NOT GRADED. That the bytes at each URL hash to the sha256: the lane and
`talk/engine-up.sh` check that when they download, and the table records where each figure came
from. That a cluster runs what was declared: the lane installs from the file, so a fact that
compared them could only read true (ADR-0033 point 2). Whether a line supports the declared
engine: composition prices that (ticket 148).

Usage:
    adopter_engines.py check [--hub DIR] [--estate DIR]
    adopter_engines.py selfcheck
    adopter_engines.py read <declaration>        version, install URL and sha256 on one line
    adopter_engines.py owned-cluster <adopter>   the kind cluster the adopter's scripts create
Exit 0 every assertion holds; 1 one does not, named; 3 no platform clone to read.
"""
from __future__ import annotations

import argparse
import copy
import re
import sys
import tempfile
from pathlib import Path

import yaml

HUB = Path(__file__).resolve().parents[2]
TABLE = "engine/kyverno/engine-table.yaml"
DECLARATION = "gitops/engine/kyverno.yaml"
ENGINE_UP = "talk/engine-up.sh"
REFERENCE_INSTALL = "engine/up.sh"
RELEASES = "https://github.com/kyverno/kyverno/releases/download"
KEYS = {"schema", "engine", "version", "install", "cli"}
FIELDS = ("install_url", "install_sha256", "cli_file", "cli_sha256")
_VERSION = re.compile(r"\d+\.\d+\.\d+")
_SHA = re.compile(r"[0-9a-f]{64}")
_STEP = re.compile(r'(?:^|[\s)])step\s+"[^"]*"\s+"(?P<script>[^"]+)"(?P<args>[^;#\n]*)')
_CTX = re.compile(r'^\s*CTX="\$\{CTX:-kind-(?P<name>[A-Za-z0-9][A-Za-z0-9-]*)\}"', re.M)
_SOURCES_LIB = re.compile(r'^\s*(?:source|\.)\s+"?\$\(dirname "\$\{BASH_SOURCE\[0\]\}"\)/lib\.sh"?\s*$', re.M)
_CLUSTER = re.compile(r'^CLUSTER=(?P<name>[A-Za-z0-9][A-Za-z0-9-]*)\s*$', re.M)
_CREATES = re.compile(r'kind create cluster --name "?\$\{?CLUSTER\}?"?')
# The check places a script by the cluster its own default names, and it reads `step` calls only.
# So talk/up.sh may not override CTX, and may not run an estate or hub script outside a step:
# either would move work to a cluster this check never reads, and it fails closed on both.
_SCRIPT = re.compile(r'\$\{?(?:CLONE|ROOT)\}?/[^"\s;)]+\.sh')
_CTX_SET = re.compile(r'(?:^|[\s;&|(])(?:export\s+|local\s+|declare\s+(?:-\w+\s+)?)?CTX=')
# Runs outside a step and targets no cluster: it clones the estate this check reads.
_BARE_ALLOWED = {"$ROOT/clone-estate.sh"}


class CouldNotLook(Exception):
    pass


class Refused(ValueError):
    """A file does not have the shape its readers rely on."""


def _need(cond: bool, msg: str) -> None:
    if not cond:
        raise Refused(msg)


# ------------------------------------------------------------------------------ the readers

def read_declaration(path: Path) -> dict[str, str]:
    """One adopter's declared engine, shape-checked the way its own engine_declaration.py does."""
    try:
        doc = yaml.safe_load(Path(path).read_text())
    except OSError as exc:
        raise Refused(f"{DECLARATION} is absent ({exc.strerror})") from exc
    except yaml.YAMLError as exc:
        raise Refused(f"{DECLARATION} is not YAML: {exc}") from exc
    _need(isinstance(doc, dict), f"{DECLARATION} is not a mapping")
    _need(set(doc) == KEYS, f"{DECLARATION} keys must be exactly {sorted(KEYS)}, not {sorted(doc)}")
    _need(doc["schema"] == 1 and doc["engine"] == "kyverno", f"{DECLARATION} must be schema 1, engine kyverno")
    version = doc["version"]
    _need(isinstance(version, str) and bool(_VERSION.fullmatch(version)),
          f"{DECLARATION} version {version!r} is not an exact X.Y.Z string")
    install = doc["install"] if isinstance(doc["install"], dict) else {}
    cli = ((doc["cli"] if isinstance(doc["cli"], dict) else {}).get("linux_x86_64")) or {}
    out = {"version": version, "install_url": str(install.get("url", "")),
           "install_sha256": str(install.get("sha256", "")), "cli_file": str(cli.get("file", "")),
           "cli_sha256": str(cli.get("sha256", ""))}
    _need(out["install_url"] == f"{RELEASES}/v{version}/install.yaml",
          f"{DECLARATION} install.url {out['install_url']!r} is not the install.yaml of {version}")
    _need(out["cli_file"] == f"kyverno-cli_v{version}_linux_x86_64.tar.gz",
          f"{DECLARATION} cli.linux_x86_64.file {out['cli_file']!r} is not the archive of {version}")
    for key in ("install_sha256", "cli_sha256"):
        _need(bool(_SHA.fullmatch(out[key])), f"{DECLARATION} {key} is not a 64-hex sha256")
    return out


def read_table(platform: Path) -> dict[str, dict[str, str]]:
    doc = yaml.safe_load((platform / TABLE).read_text())
    rows = doc.get("versions") if isinstance(doc, dict) else None
    _need(isinstance(rows, list) and bool(rows), f"{TABLE} lists no version")
    table = {}
    for row in rows:
        cli = ((row.get("cli") or {}).get("linux_x86_64")) or {}
        install = row.get("install") or {}
        table[str(row.get("version"))] = {
            "install_url": str(install.get("url", "")), "install_sha256": str(install.get("sha256", "")),
            "cli_file": str(cli.get("file", "")), "cli_sha256": str(cli.get("sha256", ""))}
    return table


def roles(unit: Path) -> set[str]:
    try:
        doc = yaml.safe_load((unit / "party.yaml").read_text())
    except (OSError, yaml.YAMLError):
        return set()
    return {str(r) for r in (doc or {}).get("roles") or []} if isinstance(doc, dict) else set()


def script_cluster(script: Path) -> str | None:
    """The kind cluster a script targets: its `CTX="${CTX:-kind-X}"` default, or the `CLUSTER=X`
    of the lib.sh beside it that it sources. None when neither spelling is there."""
    text = script.read_text()
    found = _CTX.search(text)
    if found:
        return found["name"]
    lib = script.parent / "lib.sh"
    if _SOURCES_LIB.search(text) and lib.is_file():
        found = _CLUSTER.search(lib.read_text())
        if found:
            return found["name"]
    return None


def owned_cluster(adopter: Path) -> str:
    """The one kind cluster the adopter's own scripts create. Refused when there is none or two."""
    owned = set()
    for script in sorted((adopter / "scripts").glob("*.sh")):
        if _CREATES.search(script.read_text()):
            name = script_cluster(script)
            _need(name is not None, f"{script} creates a cluster whose name this check cannot read")
            owned.add(name)
    _need(len(owned) == 1, f"{adopter.name}'s scripts create {len(owned)} kind cluster(s), "
                           f"{sorted(owned)}, and an owner must create exactly one")
    return owned.pop()


def steps(up_sh: Path) -> list[tuple[str, list[str]]]:
    """(script, args) for every `step` call in talk/up.sh, in every mode."""
    out = []
    for line in up_sh.read_text().splitlines():
        if line.lstrip().startswith("#"):
            continue
        for m in _STEP.finditer(line):
            out.append((m["script"], m["args"].split()))
    return out


def unread(up_sh: Path) -> list[str]:
    """Lines of talk/up.sh that could put work on a cluster this check does not read: a CTX
    override, or an estate or hub script run outside a `step` call."""
    out = []
    for n, line in enumerate(up_sh.read_text().splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        if _CTX_SET.search(line):
            out.append(f"line {n} sets CTX, which moves a script off the cluster its own default names")
        if not _STEP.search(line):
            for script in _SCRIPT.findall(line):
                if script not in _BARE_ALLOWED:
                    out.append(f"line {n} runs {script} outside a step call")
    return out


# ------------------------------------------------------------------------------ the grade

def grade(hub: Path, estate: Path) -> tuple[int, list[str]]:
    platform = estate / "platform"
    if not platform.is_dir():
        raise CouldNotLook(f"no platform clone at {platform} (run ./clone-estate.sh)")
    lines: list[str] = []
    fail = lambda msg: lines.append("FAIL: " + msg)  # noqa: E731
    try:
        table = read_table(platform)
    except (OSError, AttributeError, TypeError, yaml.YAMLError, Refused) as exc:
        return 1, [f"FAIL: the platform engine table is not readable, so no declaration can be held to it: {exc}"]
    units = sorted(p for p in estate.iterdir() if (p / "party.yaml").is_file())
    adopters = [u.name for u in units if "adopter" in roles(u)]
    platforms = {u.name for u in units if "platform" in roles(u)}
    if not adopters:
        return 1, ["FAIL: no estate unit claims the adopter role, so no declaration was read"]

    # (a) each declaration agrees with the table's row for its version
    declared: dict[str, dict[str, str]] = {}
    for name in adopters:
        try:
            engine = read_declaration(estate / name / DECLARATION)
        except Refused as exc:
            fail(f"{name} declares no readable engine: {exc}")
            continue
        declared[name] = engine
        row = table.get(engine["version"])
        if row is None:
            fail(f"{name} declares kyverno {engine['version']}, which is not a row of the platform "
                 f"engine table (rows: {', '.join(sorted(table))})")
            continue
        wrong = [f"its {k} is {engine[k]} where the table's is {row[k]}" for k in FIELDS if engine[k] != row[k]]
        if wrong:
            fail(f"{name} declares kyverno {engine['version']}, and " + "; ".join(wrong))
        else:
            lines.append(f"PASS: {name} declares kyverno {engine['version']}, and its install.yaml URL and "
                         "sha256 and its linux_x86_64 CLI archive and sha256 are the platform engine "
                         "table's row for that version")

    # derive who uses which named cluster, from the scripts talk/up.sh runs
    up_sh = hub / "talk" / "up.sh"
    users: dict[str, set[str]] = {}
    platform_clusters: set[str] = set()
    engines: dict[str, str] = {}
    try:
        called = steps(up_sh)
        hidden = unread(up_sh)
    except OSError as exc:
        return 1, lines + [f"FAIL: talk/up.sh is not readable ({exc.strerror}), so no cluster's engine can be traced"]
    for why in hidden:
        fail(f"talk/up.sh {why}, and this check reads each script's cluster from its default and "
             "reads step calls only, so it cannot show where that work runs")
    for script, args in called:
        if script.startswith("$ROOT/"):
            if script == f"$ROOT/{ENGINE_UP}":
                owner = args[0] if args else ""
                if owner not in adopters:
                    fail(f"talk/up.sh runs {ENGINE_UP} for {owner or 'no one'}, which is not an adopter")
                    continue
                try:
                    cluster = owned_cluster(estate / owner)
                except (OSError, Refused) as exc:
                    fail(f"talk/up.sh installs {owner}'s engine, and {exc}")
                    continue
                if cluster in engines:
                    fail(f"talk/up.sh installs an engine on kind-{cluster} twice ({engines[cluster]} and {owner})")
                engines[cluster] = owner
                # The owner runs its engine on the cluster, so it is one of the cluster's users even
                # when talk/up.sh does not run the owner's own bring-up script.
                users.setdefault(cluster, set()).add(owner)
            continue
        m = re.fullmatch(r"\$CLONE/(?P<unit>[^/]+)/(?P<rel>.+)", script)
        if not m:
            fail(f"talk/up.sh runs {script}, which this check cannot place in the estate or the hub")
            continue
        unit, rel = m["unit"], m["rel"]
        if unit in platforms and rel == REFERENCE_INSTALL:
            fail(f"talk/up.sh still runs the platform's reference install, {unit}/{rel}, on a named "
                 "cluster; a named cluster's engine comes from its owner's declaration")
            continue
        path = estate / unit / rel
        try:
            cluster = script_cluster(path)
        except OSError as exc:
            fail(f"talk/up.sh runs {unit}/{rel}, which is not readable ({exc.strerror})")
            continue
        if cluster is None:
            fail(f"talk/up.sh runs {unit}/{rel}, and this check cannot read which cluster it targets "
                 '(no CTX="${CTX:-kind-...}" and no CLUSTER= in a lib.sh it sources)')
            continue
        if unit in adopters:
            users.setdefault(cluster, set()).add(unit)
        if unit in platforms:
            platform_clusters.add(cluster)

    # (b) adopters on one cluster declare one engine
    used = "; ".join(f"kind-{c}: {', '.join(sorted(users[c]))}" for c in sorted(users))
    if not any(len(names) > 1 for names in users.values()):
        lines.append(f"PASS: no named cluster is used by more than one adopter ({used or 'no adopter step'}, "
                     "derived from the scripts talk/up.sh runs), so no two declarations have to agree")
    for cluster in sorted(users):
        names = sorted(users[cluster])
        if len(names) < 2:
            continue
        missing = [n for n in names if n not in declared]
        if missing:
            fail(f"kind-{cluster} is used by {', '.join(names)}, and no readable engine is declared by "
                 f"{', '.join(missing)}, so one engine for the cluster cannot be shown")
            continue
        seen = {n: tuple(declared[n][k] for k in ("version", *FIELDS)) for n in names}
        if len(set(seen.values())) > 1:
            fail(f"kind-{cluster} is used by {', '.join(names)}, and they declare different engines: "
                 + ", ".join(f"{n} kyverno {declared[n]['version']}" for n in names)
                 + ("" if len({declared[n]['version'] for n in names}) > 1 else " with different figures"))
        else:
            lines.append(f"PASS: kind-{cluster} is used by {', '.join(names)}, and all of them declare kyverno "
                         f"{declared[names[0]]['version']} with the same figures (derived from the scripts "
                         f"talk/up.sh runs: {used})")

    # (c) talk/up.sh installs each engine from the owner's declaration, and only where one runs
    for cluster in sorted(platform_clusters - set(engines)):
        fail(f"talk/up.sh puts platform layers on kind-{cluster} and installs no engine there from "
             f"its owner's declaration ({ENGINE_UP} <owner>)")
    for cluster, owner in sorted(engines.items()):
        if owner not in declared:
            fail(f"talk/up.sh installs kind-{cluster}'s engine from {owner}'s {DECLARATION}, and {owner} "
                 "declares no readable engine there")
    for cluster in sorted(set(engines) - platform_clusters):
        fail(f"talk/up.sh installs {engines[cluster]}'s engine on kind-{cluster}, where no platform "
             "layer runs: this adds an engine to a cluster that runs none (ticket 71, decision 17)")
    clusters = sorted(set(users) | platform_clusters | set(engines))
    held = sorted(set(engines) & platform_clusters)
    if held and not any(line.startswith("FAIL: talk/up.sh") for line in lines):
        bare = [c for c in clusters if c not in engines]
        lines.append("PASS: talk/up.sh installs " + ", ".join(
            f"kind-{c}'s engine from {engines[c]}'s own {DECLARATION}" for c in held)
            + (f", and no engine on {', '.join('kind-' + c for c in bare)}" if bare else "")
            + ", and runs no platform reference install")
    return (1 if any(line.startswith("FAIL:") for line in lines) else 0), lines


# ------------------------------------------------------------------------------ the selfcheck

_ROWS = {"1.18.2": ("a" * 64, "b" * 64), "1.19.1": ("c" * 64, "d" * 64)}


def _declaration(version: str, *, install_sha: str | None = None, cli_sha: str | None = None,
                 url_version: str | None = None) -> str:
    isha, csha = _ROWS.get(version, ("e" * 64, "f" * 64))
    return yaml.safe_dump({
        "schema": 1, "engine": "kyverno", "version": version,
        "install": {"url": f"{RELEASES}/v{url_version or version}/install.yaml", "sha256": install_sha or isha},
        "cli": {"linux_x86_64": {"file": f"kyverno-cli_v{version}_linux_x86_64.tar.gz", "sha256": cli_sha or csha}}})


UP_SH = """\
step() { :; }
step "driftwood: KinD + Flux" "$CLONE/driftwood/scripts/up.sh"
step "platform: identity substrate" "$CLONE/platform/identity/up.sh"
step "driftwood: Kyverno from driftwood's own declaration" "$ROOT/talk/engine-up.sh" driftwood
step "platform: posture" "$CLONE/platform/posture/up.sh"
step "tuppence: workload flagship" "$CLONE/tuppence/reset/up.sh"
case "$MODE" in
  tuppence)  step "tuppence: institution cluster" "$CLONE/tuppence/scripts/up.sh" ;;
  all)
    step "tuppence: institution cluster" "$CLONE/tuppence/scripts/up.sh"
    step "ludlow: institution cluster"   "$CLONE/ludlow/scripts/up.sh" ;;
esac
"""


def _plant(root: Path, *, versions=None, declarations=None, up_sh=UP_SH, extra=None, table=True):
    hub, estate = root / "hub", root / "estate"

    def put(base: Path, rel: str, text: str) -> None:
        (base / rel).parent.mkdir(parents=True, exist_ok=True)
        (base / rel).write_text(text)

    put(hub, "talk/up.sh", up_sh)
    if table:
        put(estate / "platform", TABLE, yaml.safe_dump({"schema": 1, "engine": "kyverno", "versions": [
            {"version": v, "cli": {"linux_x86_64": {"file": f"kyverno-cli_v{v}_linux_x86_64.tar.gz", "sha256": c}},
             "install": {"url": f"{RELEASES}/v{v}/install.yaml", "sha256": i}} for v, (i, c) in _ROWS.items()]}))
    put(estate / "platform", "party.yaml", "roles: [publisher, platform]\n")
    for rel in ("identity/up.sh", "posture/up.sh", REFERENCE_INSTALL):
        put(estate / "platform", rel, 'CTX="${CTX:-kind-driftwood}"\n')
    lib = 'source "$(dirname "${BASH_SOURCE[0]}")/lib.sh"\nkind create cluster --name "$CLUSTER" --wait 120s\n'
    for name in ("driftwood", "tuppence", "ludlow"):
        put(estate / name, "party.yaml", "roles: [risk-bearer, adopter, publisher]\n")
        put(estate / name, "scripts/lib.sh", f"CLUSTER={name}\nCTX=\"kind-${{CLUSTER}}\"\n")
        put(estate / name, "scripts/up.sh", lib)
    put(estate / "tuppence", "reset/up.sh", 'CTX="${CTX:-kind-driftwood}"\n')
    decl = {"driftwood": _declaration("1.18.2"), "tuppence": _declaration("1.18.2"),
            "ludlow": _declaration("1.18.2")}
    decl.update(declarations or {})
    for name, text in decl.items():
        if text is not None:
            put(estate / name, DECLARATION, text)
    for (unit, rel), text in (extra or {}).items():
        put(estate / unit, rel, text)
    return hub, estate


def selfcheck() -> int:
    up_all_ludlow_reset = UP_SH.replace(
        '    step "ludlow: institution cluster"',
        '    step "ludlow: a workload on tuppence\'s cluster" "$CLONE/ludlow/reset/up.sh"\n'
        '    step "ludlow: institution cluster"')
    cases = {
        "every adopter on the table's row, one engine on kind-driftwood": ({}, 0, None),
        "a declared version with no row in the table": (
            {"declarations": {"driftwood": _declaration("1.20.0")}}, 1, "not a row of the platform engine table"),
        "an install.yaml sha256 that is not the row's": (
            {"declarations": {"tuppence": _declaration("1.18.2", install_sha="9" * 64)}}, 1,
            "tuppence declares kyverno 1.18.2, and its install_sha256 is " + "9" * 64),
        "a CLI sha256 that is not the row's": (
            {"declarations": {"ludlow": _declaration("1.18.2", cli_sha="9" * 64)}}, 1,
            "ludlow declares kyverno 1.18.2, and its cli_sha256 is " + "9" * 64),
        "an install URL of another release": (
            {"declarations": {"driftwood": _declaration("1.18.2", url_version="1.19.1")}}, 1,
            "is not the install.yaml of 1.18.2"),
        "an adopter with no declaration": ({"declarations": {"ludlow": None}}, 1, "ludlow declares no readable engine"),
        "tuppence on another row while it shares kind-driftwood": (
            {"declarations": {"tuppence": _declaration("1.19.1")}}, 1,
            "kind-driftwood is used by driftwood, tuppence, and they declare different engines"),
        "ludlow on another row, sharing no cluster": ({"declarations": {"ludlow": _declaration("1.19.1")}}, 0, None),
        "a ludlow script on kind-tuppence, and the two disagree": (
            {"declarations": {"ludlow": _declaration("1.19.1")}, "up_sh": up_all_ludlow_reset,
             "extra": {("ludlow", "reset/up.sh"): 'CTX="${CTX:-kind-tuppence}"\n'}}, 1,
            "kind-tuppence is used by ludlow, tuppence, and they declare different engines"),
        "talk/up.sh still runs the platform's reference install": (
            {"up_sh": UP_SH.replace('"$ROOT/talk/engine-up.sh" driftwood', '"$CLONE/platform/engine/up.sh"')}, 1,
            "still runs the platform's reference install"),
        "no engine where the platform layers run": (
            {"up_sh": UP_SH.replace('step "driftwood: Kyverno from driftwood\'s own declaration" '
                                    '"$ROOT/talk/engine-up.sh" driftwood\n', "")}, 1,
            "puts platform layers on kind-driftwood and installs no engine there"),
        "an engine added to a cluster that runs none": (
            {"up_sh": UP_SH + 'step "ludlow: engine" "$ROOT/talk/engine-up.sh" ludlow\n'}, 1,
            "installs ludlow's engine on kind-ludlow, where no platform layer runs"),
        "a step whose cluster cannot be read": (
            {"extra": {("tuppence", "reset/up.sh"): "kubectl apply -f workloads.yaml\n"}}, 1,
            "cannot read which cluster it targets"),
        "no engine table": ({"table": False}, 1, "the platform engine table is not readable"),
        "the owner's own bring-up not in talk/up.sh, and tuppence on another engine": (
            {"declarations": {"tuppence": _declaration("1.19.1")},
             "up_sh": UP_SH.replace('step "driftwood: KinD + Flux" "$CLONE/driftwood/scripts/up.sh"\n', "")}, 1,
            "kind-driftwood is used by driftwood, tuppence, and they declare different engines"),
        "tuppence's workload moved to its own cluster, so nothing is shared": (
            {"declarations": {"tuppence": _declaration("1.19.1")},
             "extra": {("tuppence", "reset/up.sh"): 'CTX="${CTX:-kind-tuppence}"\n'}}, 0,
            "no named cluster is used by more than one adopter (kind-driftwood: driftwood; kind-ludlow: ludlow; "
            "kind-tuppence: tuppence"),
        "a CTX override moves the engine to another cluster": (
            {"up_sh": UP_SH.replace('step "driftwood: Kyverno', 'CTX=kind-tuppence step "driftwood: Kyverno')}, 1,
            "sets CTX, which moves a script off the cluster its own default names"),
        "a platform layer put on kind-ludlow by a CTX override": (
            {"up_sh": UP_SH + 'CTX=kind-ludlow step "platform: posture" "$CLONE/platform/posture/up.sh"\n'}, 1,
            "sets CTX"),
        "the reference install run outside a step": (
            {"up_sh": UP_SH + 'bash "$CLONE/platform/engine/up.sh"\n'}, 1,
            "runs $CLONE/platform/engine/up.sh outside a step call"),
        "an exported CTX": ({"up_sh": "export CTX=kind-ludlow\n" + UP_SH}, 1, "line 1 sets CTX"),
        "clone-estate.sh outside a step is allowed": (
            {"up_sh": 'bash "$ROOT/clone-estate.sh" || exit 1\n' + UP_SH}, 0, None),
        "the owner of an engine declares none": (
            {"declarations": {"driftwood": None}}, 1,
            "installs kind-driftwood's engine from driftwood's gitops/engine/kyverno.yaml, and driftwood "
            "declares no readable engine"),
    }
    bad = []
    for name, (plant, want, needle) in cases.items():
        with tempfile.TemporaryDirectory() as tmp:
            hub, estate = _plant(Path(tmp), **copy.deepcopy(plant))
            try:
                code, lines = grade(hub, estate)
            except Exception as exc:  # a crash is a selfcheck failure, named
                code, lines = 99, [f"crashed: {type(exc).__name__}: {exc}"]
        text = "\n".join(lines)
        if code != want or (needle and needle not in text):
            bad.append(f"{name}: exit {code}, wanted {want}" + (f" with {needle!r}" if needle else "")
                       + f"\n    {text}")
    if bad:
        print("FAIL: the selfcheck's planted estates did not grade as planted:\n  " + "\n  ".join(bad))
        return 1
    print(f"PASS: selfcheck: {len(cases)} planted estates grade as planted, among them tuppence on "
          "another engine while it shares kind-driftwood, and ludlow on another engine while it "
          "shares nothing")
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("mode", choices=("check", "selfcheck", "read", "owned-cluster"))
    parser.add_argument("path", nargs="?", type=Path)
    parser.add_argument("--hub", type=Path, default=HUB)
    parser.add_argument("--estate", type=Path, default=HUB / ".estate-clone")
    args = parser.parse_args(argv[1:])
    if args.mode == "selfcheck":
        return selfcheck()
    if args.mode in ("read", "owned-cluster"):
        if args.path is None:
            parser.error(f"{args.mode} needs a path")
        try:
            if args.mode == "read":
                e = read_declaration(args.path)
                print(e["version"], e["install_url"], e["install_sha256"])
            else:
                print(owned_cluster(args.path))
        except (OSError, Refused) as exc:
            print(f"REFUSED: {exc}", file=sys.stderr)
            return 1
        return 0
    try:
        code, lines = grade(args.hub, args.estate)
    except CouldNotLook as exc:
        print(f"SKIP: {exc}")
        return 3
    print("\n".join(lines))
    return code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
