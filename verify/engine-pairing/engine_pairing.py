#!/usr/bin/env python3
"""engine_pairing.py -- eco-system ticket 148, hub ADR-0033 point 3: composition prices an
unsupported engine pairing, and never refuses it.

An adopter declares its engine in its own `gitops/engine/kyverno.yaml`. A composed policy line
supports exactly the engines its element of the platform's `distribution/versions.yaml` lists in
`tested_engines`, and the machinery the engines in `distribution/machinery.yaml`, both at the
platform tree the adopter composes against. On an engine a line does not support, its claims do
not count: every control it claims is a hole priced as ADR-0026 prices one, and the evidence
shows an `unsupported-engine` delta whose amount is the sum of those hole prices. No declaration
is priced the same way under `undeclared-engine`.

The check runs the COMPOSER THE ESTATE SERVES (`platform/compose/composition.py` in the estate
clone, the platform's origin/main on the runner) through its own CLI, the operation each
adopter's compose-check and cut-release run, on copies of the adopters' committed trees. It
derives every expected figure itself, never from the delta it grades:

  * a line's bodies are the admission objects the composer rendered into
    `composed/policies/v<version>/`, and the machinery's are the admission objects it rendered at
    the `composed/` root. A body's claims are read from the platform's own
    `oscal/component-definition.json` (`Check_Id`), in the tree composed against;
  * what a line supports is read from its `tested_engines` element by this check's own reading
    of ADR-0033 point 1: scope `every-served-body-v1` and a list of exact X.Y.Z versions. Any
    other value supports no engine;
  * a hole's price is its line on the regulator's partition (`prices[].holes[]` of a feed entry:
    the published weight times the triple), which a pairing does not move. A control with no line
    is a named absence, so a delta naming only such controls must carry `amount: null`.

What it grades:

  A. PLANTED, on a copy of a real adopter against the served composer and platform tree:
     1. the adopter's own declaration: no engine delta, the header records the declared engine;
     2. a declared engine the composed line does not list: one `unsupported-engine` delta naming
        the line and the engine, whose amount is the sum of the hole prices of the controls the
        line claims; the machinery gets one only where its own list lacks the engine;
     3. the same, with a planted platform claim of a WEIGHTED control on a line body, so the price
        is a number: the control is covered on the declared engine and a hole on the planted one,
        the delta's amount is that control's line, and the regime entry's open amount rises by it;
     4. no declaration: an `undeclared-engine` delta for the line and for the machinery, and the
        header records none;
     5. a declaration that does not read: the composition refuses as a missing instrument named
        `gitops/engine/kyverno.yaml`.
  B. FORWARD, each real adopter's committed tree composed now by the served composer against the
     served platform tree: what the adopter's artefact will say once its tools pin and its
     implementations pin move to a platform tag cut from this tree. Expected: no engine delta, and
     the header records the engine its file declares.
  C. SERVED, each real adopter's committed `composed/HEADER.yaml` and `composed/evidence.json`: the
     header's `declared-engine` equals the adopter's file, and the engine deltas are exactly the
     pairings the platform tree at the adopter's pinned implementations commit does not support.
     An artefact composed before ticket 148 carries no `declared-engine`: a could-not-look, because
     re-composing an adopter is a push its owner makes.

Grading: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    engine_pairing.py check        # the estate in .estate-clone/ (or PAVC_ESTATE_CLONE)
    engine_pairing.py selfcheck    # planted evidence: proves each grading rule bites
"""
from __future__ import annotations

import copy
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from _estate import ESTATE as DEFAULT_ESTATE  # type: ignore[import-not-found]  # noqa: E402

LINES: list[str] = []
ENGINE_FILE = "gitops/engine/kyverno.yaml"
ENGINE_KINDS = ("unsupported-engine", "undeclared-engine")
SCOPE = "every-served-body-v1"
ADMISSION_KINDS = {"ValidatingPolicy", "MutatingPolicy", "GeneratingPolicy"}
VERSION_SUFFIX = re.compile(r"-\d+-\d+-\d+$")
EXACT = re.compile(r"\d+\.\d+\.\d+")
ADOPTERS = ("driftwood", "tuppence", "ludlow")
PLANTED = "driftwood"
MACHINERY = "machinery"


def out(status: str, msg: str) -> None:
    LINES.append(status)
    print(f"{status}: {msg}")


def close(a: float, b: float) -> bool:
    return abs(a - b) <= max(1e-6, 1e-9 * max(abs(a), abs(b)))


# --------------------------------------------------------------------------
# what is supported, read here rather than trusted from the composer
# --------------------------------------------------------------------------
def supported(value: object) -> list[str] | None:
    """ADR-0033 point 1: the exact versions a `tested_engines` value lists, or None when it
    supports none. Only scope `every-served-body-v1` with a non-empty list of distinct exact
    X.Y.Z strings is a support claim."""
    if not isinstance(value, dict) or value.get("scope") != SCOPE:
        return None
    listed = value.get("kyverno")
    if (not isinstance(listed, list) or not listed
            or not all(isinstance(v, str) and EXACT.fullmatch(v) for v in listed)
            or len(set(listed)) != len(listed)):
        return None
    return list(listed)


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _show(repo: Path, ref: str, path: str) -> str | None:
    got = _git(repo, "show", f"{ref}:{path}")
    return got.stdout if got.returncode == 0 else None


def _export(repo: Path, dest: Path) -> None:
    """The committed tree at HEAD, never the working tree."""
    data = subprocess.run(["git", "-C", str(repo), "archive", "HEAD"], capture_output=True,
                          check=True).stdout
    dest.mkdir(parents=True)
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        archive.extractall(dest, filter="data")


def table_rows(platform: Path) -> dict[str, dict]:
    doc = yaml.safe_load((platform / "engine" / "kyverno" / "engine-table.yaml").read_text())
    return {str(r["version"]): r for r in doc["versions"]}


def declaration(version: str, rows: dict[str, dict]) -> dict:
    """A well-formed declaration of `version`, every figure the engine table's row for it."""
    row = rows[version]
    return {"schema": 1, "engine": "kyverno", "version": version,
            "install": {"url": row["install"]["url"], "sha256": row["install"]["sha256"]},
            "cli": {"linux_x86_64": {"file": row["cli"]["linux_x86_64"]["file"],
                                     "sha256": row["cli"]["linux_x86_64"]["sha256"]}}}


def declared_version(text: str | None) -> str | None:
    if text is None:
        return None
    doc = yaml.safe_load(text)
    return doc.get("version") if isinstance(doc, dict) else None


# --------------------------------------------------------------------------
# the composer, run through its own CLI
# --------------------------------------------------------------------------
def compose(platform: Path, adopter: Path, estate: Path, work: Path) -> tuple[int, dict, dict, dict]:
    """(exit code, evidence document, header, rendered files) of the served composer's CLI run
    the way an adopter runs it: from the adopter root, `.` as the adopter, parents from `estate`."""
    out_dir = work / "out"
    if out_dir.exists():
        subprocess.run(["rm", "-rf", str(out_dir)], check=True)
    run = subprocess.run([sys.executable, str(platform / "compose" / "composition.py"), "compose",
                          ".", "--estate-clone", str(estate), "--out", str(out_dir)],
                         cwd=adopter, capture_output=True, text=True)
    try:
        doc = json.loads(run.stdout)
    except ValueError:
        doc = {"outcome": "unreadable", "stderr": run.stderr[-600:]}
    header, rendered = {}, {}
    if (out_dir / "composed" / "HEADER.yaml").exists():
        header = yaml.safe_load((out_dir / "composed" / "HEADER.yaml").read_text()) or {}
        for p in (out_dir / "composed").rglob("*.yaml"):
            rendered[str(p.relative_to(out_dir))] = p.read_text()
    return run.returncode, doc, header, rendered


def _names(text: str) -> set[str]:
    return {VERSION_SUFFIX.sub("", d["metadata"]["name"]) for d in yaml.safe_load_all(text)
            if isinstance(d, dict) and d.get("kind") in ADMISSION_KINDS}


def subjects(rendered: dict[str, str]) -> dict[str, set[str]]:
    """{line version or 'machinery': the body names the composer rendered for it}."""
    found: dict[str, set[str]] = {}
    for path, text in rendered.items():
        parts = path.split("/")
        if len(parts) == 4 and parts[1] == "policies" and parts[2].startswith("v"):
            found.setdefault(parts[2][1:], set()).update(_names(text))
        elif len(parts) == 2 and parts[1] not in ("HEADER.yaml", "kustomization.yaml"):
            found.setdefault(MACHINERY, set()).update(_names(text))
    return found


def claims(tree: Path) -> list[tuple[str, str, str]]:
    """(catalogue source, control id, claimed policy) for every Check_Id in the platform tree's
    own component-definition. The source is the catalogue party its `source` href names."""
    doc = json.loads((tree / "oscal" / "component-definition.json").read_text())
    found = []
    for comp in doc["component-definition"]["components"]:
        for ci in comp.get("control-implementations", []):
            segs = [s for s in re.split(r"[\\/]+", str(ci.get("source") or "")) if s not in ("", ".", "..")]
            source = segs[0] if segs else ""
            for ir in ci.get("implemented-requirements", []):
                for p in ir.get("props", []):
                    if p.get("name") == "Check_Id":
                        found.append((source, ir["control-id"], p["value"]))
    return found


def weighted_lines(doc: dict) -> dict[tuple[str, str], float]:
    """(source, id) -> amount, the regulator's partition on every feed entry that carries one."""
    lines: dict[tuple[str, str], float] = {}
    for e in doc.get("prices") or []:
        if e.get("kind") == "feed":
            for h in e.get("holes") or []:
                lines.setdefault((str(h["source"]), str(h["id"])), float(h["amount"]))
    return lines


def regime_open(doc: dict) -> float | None:
    amounts = [e["amount"] for e in doc.get("prices") or [] if e.get("kind") == "feed" and e.get("holes")]
    return float(amounts[0]) if amounts and amounts[0] is not None else None


def _selected(header: dict, baseline_source: str) -> set[tuple[str, str]]:
    return {tuple(c.split(":", 1)) if ":" in c else (baseline_source, c)  # type: ignore[misc]
            for c in header.get("selected-controls") or []}


# --------------------------------------------------------------------------
# the grading rule, a pure function so the selfcheck can plant against it
# --------------------------------------------------------------------------
def expected_deltas(engine: str | None, support: dict[str, list[str] | None],
                    claimed: dict[str, set[tuple[str, str]]], selected: set[tuple[str, str]],
                    lines: dict[tuple[str, str], float]) -> dict[str, dict]:
    """{subject line: {kind, controls, amount}} for every pairing that is not supported."""
    want = {}
    for line, listed in support.items():
        if engine is not None and listed is not None and engine in listed:
            continue
        controls = sorted(claimed.get(line, set()))
        priced = [lines[k] for k in controls if k in selected and k in lines]
        want[line] = {"kind": "undeclared-engine" if engine is None else "unsupported-engine",
                      "controls": controls, "amount": sum(priced) if priced else None}
    return want


def grade(label: str, doc: dict, header: dict, engine: str | None, want: dict[str, dict],
          perspective: str) -> bool:
    """One composed document against the pairings derived for it. Prints one PASS or FAIL."""
    problems = []
    got_header = header.get("declared-engine", "absent")
    if got_header == "absent":
        problems.append("the header carries no declared-engine")
    elif engine is None and got_header is not None:
        problems.append(f"the header records {got_header!r} for an adopter that declares none")
    elif engine is not None and (not isinstance(got_header, dict) or got_header.get("version") != engine):
        problems.append(f"the header records {got_header!r}, and the adopter declares {engine}")
    deltas = [d for d in doc.get("deltas") or [] if isinstance(d, dict) and d.get("kind") in ENGINE_KINDS]
    got = {str(d.get("line")): d for d in deltas}
    if len(got) != len(deltas):
        problems.append("two engine deltas name one subject")
    if set(got) != set(want):
        problems.append(f"engine deltas name {sorted(got)}, and the unsupported pairings are {sorted(want)}")
    for line, w in want.items():
        d = got.get(line)
        if d is None:
            continue
        if d.get("kind") != w["kind"]:
            problems.append(f"{line}: kind {d.get('kind')}, want {w['kind']}")
        if d.get("perspective") != perspective:
            problems.append(f"{line}: perspective {d.get('perspective')!r}, not {perspective}")
        if w["kind"] == "unsupported-engine" and (d.get("engine") or {}).get("version") != engine:
            problems.append(f"{line}: names engine {d.get('engine')!r}, not {engine}")
        named = sorted((c.get("source"), c.get("control_id")) for c in d.get("controls") or [])
        if named != [tuple(k) for k in w["controls"]]:
            problems.append(f"{line}: names controls {named}, and the line claims {w['controls']}")
        amount = d.get("amount")
        if w["amount"] is None:
            if amount is not None:
                problems.append(f"{line}: amount {amount!r}, and no control it names carries a price")
        elif not isinstance(amount, (int, float)) or isinstance(amount, bool) or not close(amount, w["amount"]):
            problems.append(f"{line}: amount {amount!r}, and its controls' hole prices sum to {w['amount']:.2f}")
    open_holes = {(h.get("source"), h.get("control_id")): h for h in doc.get("holes") or []
                  if isinstance(h, dict) and h.get("status") != "closed"}
    for line, w in want.items():
        for k in w["controls"]:
            if k not in open_holes and w["amount"] is not None:
                problems.append(f"{line}: {k[0]}:{k[1]} is claimed on an unsupported pairing and is no open hole")
    if problems:
        out("FAIL", f"{label}: {'; '.join(problems[:4])}")
        return False
    summary = ", ".join(f"{w['kind']} {line} {'£%.2f' % w['amount'] if w['amount'] is not None else 'amount null'}"
                        for line, w in sorted(want.items())) or "no engine delta"
    out("PASS", f"{label}: {summary}; header declared-engine {got_header!r}")
    return True


# --------------------------------------------------------------------------
# the estate
# --------------------------------------------------------------------------
class Estate:
    def __init__(self, root: Path, work: Path):
        self.root, self.work = root, work
        self.platform = root / "platform"
        self.rows = table_rows(self.platform)
        self.commit = _git(self.platform, "rev-parse", "HEAD").stdout.strip()[:12] or "the working tree"

    def scratch(self, name: str, platform: Path | None = None) -> Path:
        """A scratch estate: every party a link to the real clone, platform optionally planted."""
        d = self.work / name
        d.mkdir(parents=True)
        for child in self.root.iterdir():
            if child.is_dir() and not child.name.startswith("."):
                (d / child.name).symlink_to(platform if (platform and child.name == "platform") else child)
        return d

    def adopter_copy(self, name: str, label: str) -> Path:
        dest = self.work / "adopters" / label / name
        _export(self.root / name, dest)
        return dest


def _support_at(platform: Path, ref: str | None, versions: list[str]) -> dict[str, list[str] | None]:
    """What each composed line and the machinery support, in the platform tree at `ref` (the
    working tree when None)."""
    def read(path: str) -> str | None:
        if ref is None:
            p = platform / path
            return p.read_text() if p.exists() else None
        return _show(platform, ref, path)
    array = yaml.safe_load(read("distribution/versions.yaml") or "{}") or {}
    elements = {str(e.get("version")): e for e in array.get("spec", {}).get("inputs", [{}])[0].get("versions", [])
                if isinstance(e, dict)}
    support = {v: supported((elements.get(v) or {}).get("tested_engines")) for v in versions}
    machinery = read("distribution/machinery.yaml")
    doc = yaml.safe_load(machinery) if machinery else None
    support[MACHINERY] = supported(doc.get("tested_engines") if isinstance(doc, dict) else None)
    return support


def _claimed(tree: Path, bodies: dict[str, set[str]]) -> dict[str, set[tuple[str, str]]]:
    found: dict[str, set[tuple[str, str]]] = {}
    for source, cid, policy in claims(tree):
        for line, names in bodies.items():
            if policy in names:
                found.setdefault(line, set()).add((source, cid))
    return found


def _expect(tree: Path, engine: str | None, doc: dict, header: dict, rendered: dict,
            baseline_source: str, support_ref: str | None = None) -> dict[str, dict]:
    bodies = subjects(rendered)
    support = _support_at(tree, support_ref, [v for v in bodies if v != MACHINERY])
    return expected_deltas(engine, support, _claimed(tree, bodies), _selected(header, baseline_source),
                           weighted_lines(doc))


def _baseline_source(party: dict) -> str:
    return next((e["party"] for e in party.get("inherits") or []
                 if e.get("kind") == "controls" and e.get("party") != party.get("party")), "")


def planted_and_forward(estate: Estate) -> None:
    served = estate.scratch("served")
    where = f"platform {estate.commit}'s composer and tree"
    # B. FORWARD: every real adopter, as it will compose once both its pins move to this tree.
    for name in ADOPTERS:
        if not (estate.root / name).is_dir():
            out("SKIP", f"{name}: no clone in the estate, so its forward composition could not be looked at")
            continue
        copy_dir = estate.adopter_copy(name, "forward")
        party = yaml.safe_load((copy_dir / "party.yaml").read_text())
        engine = declared_version((copy_dir / ENGINE_FILE).read_text() if (copy_dir / ENGINE_FILE).exists() else None)
        rc, doc, header, rendered = compose(estate.platform, copy_dir, served, estate.work / f"fwd-{name}")
        if rc != 0 or doc.get("outcome") != "composed":
            out("FAIL", f"{name} (forward, {where}): the composition did not compose: "
                        f"{doc.get('refusals') or doc.get('party_artefact_errors') or doc.get('stderr')}")
            continue
        if "engine" not in doc:
            out("FAIL", f"{name} (forward, {where}): the evidence carries no engine section, so the "
                        f"served composer predates ticket 148 and prices no pairing")
            continue
        grade(f"{name} (forward: its committed tree composed by {where}, declaring {engine})", doc, header,
              engine, _expect(estate.platform, engine, doc, header, rendered, _baseline_source(party)), name)

    # A. PLANTED, on a copy of driftwood.
    if not (estate.root / PLANTED).is_dir():
        out("SKIP", f"no {PLANTED} clone to plant a declaration on")
        return
    base = estate.adopter_copy(PLANTED, "control")
    party = yaml.safe_load((base / "party.yaml").read_text())
    bsrc = _baseline_source(party)
    own = declared_version((base / ENGINE_FILE).read_text()) if (base / ENGINE_FILE).exists() else None
    rc, control, c_header, rendered = compose(estate.platform, base, served, estate.work / "control")
    if rc != 0 or "engine" not in control:
        out("FAIL", f"planted: the control composition of {PLANTED} did not compose with an engine section")
        return
    bodies = subjects(rendered)
    lines_v = sorted(v for v in bodies if v != MACHINERY)
    support = _support_at(estate.platform, None, lines_v)
    # 2. an engine the composed line does not list: a row of the engine table, never invented.
    unlisted = sorted(v for v in estate.rows if all(v not in (support[l] or []) for l in lines_v))
    if not unlisted:
        out("SKIP", "planted: every row of the engine table is listed by every composed line, so no "
                    "unsupported engine can be planted from the table")
        return
    planted = unlisted[-1]

    def with_declaration(label: str, doc_or_text) -> Path:
        d = estate.adopter_copy(PLANTED, label)
        f = d / ENGINE_FILE
        if doc_or_text is None:
            f.unlink(missing_ok=True)
        else:
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text(doc_or_text if isinstance(doc_or_text, str) else yaml.safe_dump(doc_or_text))
        return d

    grade(f"planted 1, {PLANTED} declaring its own {own} on {where}", control, c_header, own,
          _expect(estate.platform, own, control, c_header, rendered, bsrc), PLANTED)
    d = with_declaration("unsupported", declaration(planted, estate.rows))
    rc, doc, header, rend = compose(estate.platform, d, served, estate.work / "unsupported")
    if rc != 0:
        out("FAIL", f"planted 2: declaring {planted} refused: {doc.get('refusals')}")
    else:
        want = _expect(estate.platform, planted, doc, header, rend, bsrc)
        grade(f"planted 2, {PLANTED} declaring {planted}, which composed line(s) {lines_v} do not list", doc,
              header, planted, want, PLANTED)
        if not any(w["controls"] for w in want.values()):
            out("FAIL", f"planted 2: no unsupported line claims a control, so the price has nothing to grade")

    # 3. a planted WEIGHTED claim on a line body, so the price is a number that moves.
    lines = weighted_lines(control)
    selected = _selected(c_header, bsrc)
    target = next((k for k in sorted(lines) if k in selected), None)
    body = next((b for b in sorted(bodies.get(lines_v[0], set()))), None) if lines_v else None
    if target is None or body is None:
        out("SKIP", "planted 3: the regulator's partition names no selected control, or the line has no body, "
                    "so no weighted claim can be planted")
    else:
        tree = estate.work / "platform-planted"
        _export(estate.platform, tree)
        comp_path = tree / "oscal" / "component-definition.json"
        comp = json.loads(comp_path.read_text())
        ci = comp["component-definition"]["components"][0]["control-implementations"][0]
        ci["implemented-requirements"].append(
            {"control-id": target[1], "props": [{"name": "Check_Id", "value": body}]})
        comp_path.write_text(json.dumps(comp, indent=2))
        planted_estate = estate.scratch("planted-claim", platform=tree)
        on = with_declaration("claim-supported", declaration(own, estate.rows)) if own else None
        off = with_declaration("claim-unsupported", declaration(planted, estate.rows))
        if on is None:
            out("SKIP", f"planted 3: {PLANTED} declares no engine to compare the planted claim against")
        else:
            rc1, doc1, h1, _r1 = compose(tree, on, planted_estate, estate.work / "claim-on")
            rc2, doc2, h2, r2 = compose(tree, off, planted_estate, estate.work / "claim-off")
            h_on = {(h.get("source"), h.get("control_id")): h for h in doc1.get("holes") or []}
            h_off = {(h.get("source"), h.get("control_id")): h for h in doc2.get("holes") or []}
            want = _expect(tree, planted, doc2, h2, r2, bsrc)
            ok = grade(f"planted 3, a planted claim of {target[0]}:{target[1]} on {body} ({lines_v[0]}), "
                       f"{PLANTED} declaring {planted}", doc2, h2, planted, want, PLANTED)
            moved_by = lines[target]
            problems = []
            if rc1 or rc2:
                problems.append(f"exit codes {rc1}, {rc2}")
            if target in h_on and h_on[target].get("status") != "closed":
                problems.append(f"{target[1]} is still an open hole on the declared {own}")
            hole = h_off.get(target) or {}
            if hole.get("status") in (None, "closed") or not close(hole.get("amount") or 0.0, moved_by):
                problems.append(f"{target[1]} on {planted} is {hole!r}, not an open hole of {moved_by:.2f}")
            r_on, r_off = regime_open(doc1), regime_open(doc2)
            if r_on is None or r_off is None or not close(r_off - r_on, moved_by):
                problems.append(f"the regime entry's open amount moved {r_on} -> {r_off}, not by {moved_by:.2f}")
            if weighted_lines(doc1) != weighted_lines(doc2):
                problems.append("the regulator's partition changed with the engine")
            if problems:
                out("FAIL", f"planted 3: {'; '.join(problems)}")
            elif ok:
                out("PASS", f"planted 3: {target[1]} is covered on {own} and a hole of £{moved_by:.2f} on "
                            f"{planted}, and the regime entry's open amount rises from £{r_on:.2f} to "
                            f"£{r_off:.2f}, by exactly that hole (ADR-0026)")

    # 4. no declaration.
    d = with_declaration("undeclared", None)
    rc, doc, header, rend = compose(estate.platform, d, served, estate.work / "undeclared")
    if rc != 0:
        out("FAIL", f"planted 4: no declaration refused: {doc.get('refusals')}")
    else:
        grade(f"planted 4, {PLANTED} with no {ENGINE_FILE}", doc, header, None,
              _expect(estate.platform, None, doc, header, rend, bsrc), PLANTED)

    # 5. a declaration that does not read.
    bad = declaration(planted, estate.rows)
    bad["version"] = ">=1.18"
    d = with_declaration("malformed", bad)
    rc, doc, header, _ = compose(estate.platform, d, served, estate.work / "malformed")
    named = [r for r in doc.get("refusals") or [] if r.get("kind") == "missing-instrument"
             and r.get("subject") == ENGINE_FILE]
    if rc == 1 and doc.get("outcome") == "refused" and named:
        out("PASS", f"planted 5, a declaration of version '>=1.18': refused as a missing instrument naming "
                    f"{ENGINE_FILE}")
    else:
        out("FAIL", f"planted 5: a malformed declaration gave exit {rc}, outcome {doc.get('outcome')!r}, "
                    f"refusals {doc.get('refusals')!r}")


def served_artefacts(estate: Estate) -> None:
    """C. Each adopter's committed artefact, against the platform tree at its pinned commit."""
    for name in ADOPTERS:
        repo = estate.root / name
        if not repo.is_dir():
            out("SKIP", f"{name}: no clone in the estate, so its composed artefact could not be looked at")
            continue
        header = yaml.safe_load(_show(repo, "HEAD", "composed/HEADER.yaml") or "{}") or {}
        evidence = _show(repo, "HEAD", "composed/evidence.json")
        if "declared-engine" not in header or evidence is None:
            out("SKIP", f"{name}: its committed composed/HEADER.yaml carries no declared-engine, so it was "
                        f"composed by a composer from before ticket 148; re-composing is the adopter's push")
            continue
        doc = json.loads(evidence)
        engine = declared_version(_show(repo, "HEAD", ENGINE_FILE))
        pin = yaml.safe_load(_show(repo, "HEAD", "gitops/platform/platform-pin.yaml") or "{}") or {}
        commit = ((pin.get("spec") or {}).get("ref") or {}).get("commit")
        if not commit or _git(estate.platform, "cat-file", "-e", f"{commit}^{{commit}}").returncode:
            out("SKIP", f"{name}: the platform clone carries no commit {commit!r} that its implementations pin names")
            continue
        rendered = {}
        listing = _git(repo, "ls-tree", "-r", "--name-only", "HEAD", "composed/").stdout.split()
        for path in listing:
            if path.endswith(".yaml"):
                rendered[path] = _show(repo, "HEAD", path) or ""
        party = yaml.safe_load(_show(repo, "HEAD", "party.yaml") or "{}") or {}
        tree = estate.work / f"pinned-{name}"
        if not tree.exists():
            tree.mkdir(parents=True)
            data = subprocess.run(["git", "-C", str(estate.platform), "archive", commit, "oscal"],
                                  capture_output=True, check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(data)) as archive:
                archive.extractall(tree, filter="data")
        bodies = subjects(rendered)
        support = _support_at(estate.platform, commit, [v for v in bodies if v != MACHINERY])
        want = expected_deltas(engine, support, _claimed(tree, bodies), _selected(header, _baseline_source(party)),
                               weighted_lines(doc))
        grade(f"{name} (served: its committed composed/ against platform {commit[:12]}, its implementations pin)",
              doc, header, engine, want, name)


def run(estate_root: Path) -> None:
    if not (estate_root / "platform" / "compose" / "composition.py").exists():
        out("SKIP", f"no {estate_root}/platform clone to compose with")
        return
    with tempfile.TemporaryDirectory() as tmp:
        estate = Estate(estate_root, Path(tmp))
        planted_and_forward(estate)
        served_artefacts(estate)


def exit_code() -> int:
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck: planted evidence, each defect must grade FAIL
# --------------------------------------------------------------------------
def selfcheck() -> int:
    lines = {("nist", "pl-2"): 100.0, ("nist", "ra-3"): 50.0}
    selected = {("nist", "ac-6"), ("nist", "cm-6"), ("nist", "pl-2"), ("nist", "ra-3")}
    claimed = {"5.0.0": {("nist", "ac-6"), ("nist", "pl-2")}, MACHINERY: {("nist", "cm-6")}}
    support = {"5.0.0": ["1.18.2"], MACHINERY: ["1.18.2", "1.19.1"]}
    want = expected_deltas("1.19.1", support, claimed, selected, lines)
    assert set(want) == {"5.0.0"} and want["5.0.0"]["amount"] == 100.0, want
    assert expected_deltas("1.18.2", support, claimed, selected, lines) == {}
    undeclared = expected_deltas(None, support, claimed, selected, lines)
    assert set(undeclared) == {"5.0.0", MACHINERY} and undeclared[MACHINERY]["amount"] is None, undeclared
    assert supported({"scope": "published-cage-fixtures-v1", "kyverno": ["1.18.2"]}) is None
    assert supported({"scope": SCOPE, "kyverno": [">=1.18"]}) is None
    assert supported({"scope": SCOPE, "kyverno": ["1.18.2", "1.18.2"]}) is None

    good_doc = {
        "deltas": [{"kind": "unsupported-engine", "line": "5.0.0", "perspective": "a",
                    "engine": {"engine": "kyverno", "version": "1.19.1"},
                    "controls": [{"source": "nist", "control_id": "ac-6"},
                                 {"source": "nist", "control_id": "pl-2"}], "amount": 100.0}],
        "holes": [{"source": "nist", "control_id": "ac-6", "status": "new"},
                  {"source": "nist", "control_id": "pl-2", "status": "new"}],
    }
    good_header = {"declared-engine": {"engine": "kyverno", "version": "1.19.1"}}
    plants = {
        "the delta's amount is not the sum": lambda d, h: d["deltas"][0].__setitem__("amount", 150.0),
        "a zero where nothing priced": lambda d, h: None,
        "the delta is missing": lambda d, h: d.__setitem__("deltas", []),
        "an engine delta on a supported pairing": lambda d, h: d["deltas"].append(
            dict(d["deltas"][0], line=MACHINERY, controls=[{"source": "nist", "control_id": "cm-6"}], amount=None)),
        "the delta names another engine": lambda d, h: d["deltas"][0].__setitem__(
            "engine", {"engine": "kyverno", "version": "1.18.2"}),
        "the delta names too few controls": lambda d, h: d["deltas"][0].__setitem__(
            "controls", [{"source": "nist", "control_id": "pl-2"}]),
        "the header records another engine": lambda d, h: h.__setitem__(
            "declared-engine", {"engine": "kyverno", "version": "1.18.2"}),
        "the header records no engine": lambda d, h: h.pop("declared-engine"),
        "a priced control is no open hole": lambda d, h: d["holes"][1].__setitem__("status", "closed"),
        "the kind is undeclared on a declared engine": lambda d, h: d["deltas"][0].__setitem__(
            "kind", "undeclared-engine"),
        "another party's perspective": lambda d, h: d["deltas"][0].__setitem__("perspective", "b"),
    }
    LINES.clear()
    assert grade("good", copy.deepcopy(good_doc), copy.deepcopy(good_header), "1.19.1", want, "a"), LINES
    missed = []
    for name, plant in plants.items():
        doc, header = copy.deepcopy(good_doc), copy.deepcopy(good_header)
        wanted = copy.deepcopy(want)
        if name == "a zero where nothing priced":
            wanted["5.0.0"]["amount"] = None
            doc["deltas"][0]["amount"] = 0.0
        else:
            plant(doc, header)
        LINES.clear()
        if grade(name, doc, header, "1.19.1", wanted, "a"):
            missed.append(name)
    LINES.clear()
    if missed:
        print(f"FAIL: selfcheck: the grader passed {missed}")
        return 1
    print(f"PASS: selfcheck: the expected pairings derive as planted, and each of {len(plants)} planted "
          f"defects in a delta, a hole or the header grades FAIL")
    return 0


def main(argv: list[str]) -> int:
    if argv[1:] == ["selfcheck"]:
        return selfcheck()
    if argv[1:] == ["check"]:
        root = Path(os.environ.get("PAVC_ESTATE_CLONE") or DEFAULT_ESTATE)
        run(root)
        return exit_code()
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
