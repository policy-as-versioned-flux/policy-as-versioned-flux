"""Which majors is an institution carrying in its composed window, and has it accepted each one?

THE NAME OF THIS DIRECTORY AND SCRIPT IS HISTORICAL. They are named for the fact eco-system ticket
99 was about, a major nobody reviewed. This check still cannot see a review. What it reads, since
ticket 129, is an ACCEPTANCE RECORD the institution carries in its own repository, and it grades a
carried major against that record: accepted, or not. It never says a review did or did not happen;
it says which record it read, or that it read none. Renaming the files would break the manifest row
and the capture filenames the truth surface has already published (delegated, ADR-0025,
2026-09-05), so the name stays and this sentence explains it.


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

THE ACCEPTANCE RECORD (eco-system ticket 129, delegated, ADR-0025). Accepting a major for an
institution is an authorisation, and ADR-0025 keeps those with the owner. The owner's decision
reaches this check as one file per accepted major, in the ADOPTER'S OWN repository, read at the
commit that repository serves (`git show HEAD:...`), the same read as its composed evidence:

    accepted-majors/<publisher>-<version>.yaml     # the file name is a convention, not a key

    kind: major-acceptance     # exactly this string
    party: driftwood           # the institution accepting; must be the adopter whose tree holds it
    publisher: platform        # whose policy version; this check reads platform's evidence only
    version: 5.0.0             # the exact version string the composed window carries
    accepted_by: <a name>      # who accepted it; any non-empty string
    accepted_on: 2026-09-23    # the day, an ISO date
    # any other key (a note, a pull-request link) is carried and ignored

A record counts for a carried major only when every one of those holds. A record for another
party, another publisher or another version counts for nothing, and neither does a record in a
working tree, on an unmerged branch, anywhere outside `accepted-majors/`, or in the hub. Accepting
one major accepts no other: 4.0.0 stays red beside an accepted 5.0.0 until it is accepted too or
leaves the window. Why here: the adopter is the risk-bearer (ADR-0015), the record lands only by the
same reviewed pull request that adopts anything in that repository (ADR-0002), and the tag that
signs its tree signs the record with it (ADR-0012). What this check does NOT verify: that the name
in `accepted_by` is the person who merged the record. The record's authority is the reviewed merge
that put it at the served commit, which this check does not re-grade.

ONE READER, FOUR COPIES (eco-system ticket 132). Each adopter's own gate reads the same records at
the head of the pull request it grades, and admits a composed major only when every major that pull
request adds is accepted. The format, the matching rule and the tree read are defined ONCE, in the
marked block below (`# >>> major-acceptance reader >>>`). Each gate carries that block byte for
byte. This check reads each gate script at the commit its repository serves and fails the adopter
whose copy differs, naming the first line that does. So the gate and this report cannot disagree
about what counts as an acceptance without this report saying so.

The line it prints for an unaccepted major is about what is CARRIED and what record it did or did
not find, both observed this run.

    unreviewed_major.py <estate-dir>   # grade the estate; prints lines, exits 0/1/3
    unreviewed_major.py --selfcheck    # the pure rules, on planted inputs, no estate and no cosign
"""

from __future__ import annotations

import ast
import datetime
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


# ---------------------------------------------------------------- the acceptance record

# >>> major-acceptance reader >>>
# Eco-system ticket 132. This block is the ONE definition of the major acceptance record: its
# format, the rule a record must meet to count, and how a record is read out of a tree. It is
# defined in the hub, in verify/unreviewed-major/unreviewed_major.py, and every adopter gate
# carries a byte-for-byte copy between these two marker lines. The hub check compares each served
# copy with this one on every run and fails the adopter whose copy differs. Change it here first,
# then copy it into each gate; never edit a copy alone.
RECORD_DIR = "accepted-majors"
RECORD_KIND = "major-acceptance"
PUBLISHER = "platform"


def acceptance_from_text(text: str) -> dict | str:
    """One record, parsed to the five fields that make it one; or the reason it is not a record."""
    try:
        doc = yaml.safe_load(text)
    except yaml.YAMLError as err:
        return f"is not readable YAML ({str(err).splitlines()[0][:80]})"
    if not isinstance(doc, dict):
        return "is not a YAML mapping"
    if doc.get("kind") != RECORD_KIND:
        return f"carries kind {doc.get('kind')!r}, not {RECORD_KIND!r}"
    got: dict = {}
    for key in ("party", "publisher", "version", "accepted_by"):
        value = doc.get(key)
        if value is None or not str(value).strip():
            return f"carries no {key}"
        got[key] = str(value).strip()
    on = doc.get("accepted_on")
    if isinstance(on, datetime.datetime):
        on = on.date()
    if isinstance(on, datetime.date):
        got["accepted_on"] = on.isoformat()
    else:
        try:
            got["accepted_on"] = datetime.date.fromisoformat(str(on).strip()).isoformat()
        except ValueError:
            return f"carries accepted_on {on!r}, which is not an ISO date"
    return {k: got[k] for k in ("party", "publisher", "version", "accepted_by", "accepted_on")}


def acceptance_for(records: list[tuple[str, str]], adopter: str, version: str,
                   publisher: str = PUBLISHER) -> tuple[tuple[str, dict] | None, list[str]]:
    """The first record in this adopter's own tree that accepts this version of this publisher's
    policy for this adopter, and a reason for every record that names the version but does not
    count, so a near miss is named rather than silently read as no record at all."""
    near: list[str] = []
    for path, text in records:
        parsed = acceptance_from_text(text)
        if isinstance(parsed, str):
            near.append(f"{path} {parsed}")
            continue
        if parsed["version"] != version:
            continue
        if parsed["party"] != adopter:
            near.append(f"{path} accepts {version} for {parsed['party']}, not for {adopter}")
            continue
        if parsed["publisher"] != publisher:
            near.append(f"{path} accepts {parsed['publisher']}'s {version}, not {publisher}'s")
            continue
        return (path, parsed), near
    return None, near


def acceptance_records_at(repo: Path, ref: str) -> list[tuple[str, str]]:
    """Every file under accepted-majors/ in `repo`'s tree at `ref`, as (path, text), sorted by
    path. Only a committed tree is read: a working-tree or staged file is not a record. A ref that
    does not resolve raises ValueError, because an unreadable tree is not an empty directory."""
    listed = subprocess.run(["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref, "--",
                             f"{RECORD_DIR}/"], capture_output=True, text=True)
    if listed.returncode != 0:
        raise ValueError(f"could not list {RECORD_DIR}/ at {ref[:12]} in {repo}: "
                         f"{listed.stderr.strip()[:160]}")
    records: list[tuple[str, str]] = []
    for path in sorted(p for p in listed.stdout.splitlines() if p.strip()):
        shown = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{path}"],
                               capture_output=True, text=True)
        if shown.returncode != 0:
            raise ValueError(f"could not read {path} at {ref[:12]} in {repo}: "
                             f"{shown.stderr.strip()[:160]}")
        records.append((path, shown.stdout))
    return records
# <<< major-acceptance reader <<<


READER_BEGIN = "# >>> major-acceptance reader >>>"
READER_END = "# <<< major-acceptance reader <<<"


def reader_block(source: str) -> str | None:
    """The marked reader block in a source file, marker lines included, or None when the file
    does not carry exactly one complete block."""
    lines = source.splitlines(keepends=True)
    begins = [i for i, line in enumerate(lines) if line.rstrip("\n") == READER_BEGIN]
    ends = [i for i, line in enumerate(lines) if line.rstrip("\n") == READER_END]
    if len(begins) != 1 or len(ends) != 1 or ends[0] < begins[0]:
        return None
    block = "".join(lines[begins[0]:ends[0] + 1])
    return block if block.endswith("\n") else block + "\n"


def reader_drift(gate_source: str) -> str | None:
    """None when an adopter gate carries this module's reader block byte for byte; otherwise why
    it does not, naming the first line that differs."""
    own = reader_block(Path(__file__).read_text())
    if own is None:
        return "cannot be compared, because the hub module itself carries no complete reader block"
    theirs = reader_block(gate_source)
    if theirs is None:
        return (f"carries no complete major-acceptance reader block (one {READER_BEGIN!r} line and "
                f"one {READER_END!r} line)")
    if theirs == own:
        return None
    mine, its = own.splitlines(), theirs.splitlines()
    for n, (a, b) in enumerate(zip(mine, its), start=1):
        if a != b:
            return (f"carries a major-acceptance reader that differs from the hub's at block line "
                    f"{n}: the gate has {b.strip()[:100]!r} where the hub has {a.strip()[:100]!r}")
    return (f"carries a major-acceptance reader that differs from the hub's in length: "
            f"{len(its)} lines against the hub's {len(mine)}")


GATE_BASENAMES = ("adopter-gate.py", "adopter_gate.py")


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
    drifted = 0
    for finding in findings:
        adopter = finding["adopter"]
        if finding.get("reader_drift"):
            # Ticket 132: a gate that reads the record differently from this check can admit what
            # this check calls unaccepted, or refuse what it calls accepted. Observed, so FAIL.
            drifted += 1
            lines.append(("FAIL", (
                f"{adopter}'s adopter gate {finding['reader_drift']}. The hub module "
                f"verify/unreviewed-major/unreviewed_major.py defines the reader; the gate must "
                f"carry it byte for byte")))
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
        served = str(finding.get("served") or "")[:12] or "an unresolved commit"
        records = list(finding.get("records") or [])
        for version, reason in unread:
            # Named on its own line, never as a reason to stop reading the rest of the window.
            unlooked += 1
            lines.append(("SKIP", f"{adopter} {reason}"))
        accepted: list[str] = []
        unaccepted: list[str] = []
        for version in standing:
            match, near = acceptance_for(records, adopter, version)
            if match is not None:
                path, rec = match
                accepted.append(version)
                lines.append(("PASS", (
                    f"{adopter} carries policy version {version}, which platform's signed evidence "
                    f"at {finding['tag']} records as \"{MAJOR}\", and accepts it: {path} at the "
                    f"commit {adopter} serves ({served}) records it accepted by "
                    f"{rec['accepted_by']} on {rec['accepted_on']}")))
                continue
            unaccepted.append(version)
            nearly = ("; records that name it and do not count: " + "; ".join(near)) if near else ""
            lines.append(("FAIL", (
                f"{adopter} carries policy version {version} in the composed window it serves, "
                f"and platform's own signed evidence at the tag {adopter} pins "
                f"({finding['tag']}) records bump.computed \"{MAJOR}\". {adopter}'s own tree at "
                f"the commit it serves ({served}) carries no {RECORD_DIR}/ record accepting it"
                f"{nearly}. Accepting a major is an authorisation the owner makes (ADR-0025), "
                f"recorded in {adopter}'s own repository; this line stands until that record is "
                f"served or the version leaves the window")))
        if unaccepted:
            majors += 1
        elif unread:
            # No unaccepted major among what could be read. The adopter's own status is a
            # could-not-look, and the line says what WAS verified rather than going quiet.
            read = [v for v in finding["window"] if v in finding["computed"]]
            lines.append(("ok", (
                f"{adopter}: no unaccepted major in the {len(read)} version(s) of its composed "
                f"window that could be read ({', '.join(read) or 'none'}), each verified at "
                f"{finding['tag']} under {adopter}'s own identity constant; {len(unread)} could "
                f"not be read, named above")))
        elif not finding["window"]:
            # Nothing was verified, because there was nothing to verify. Saying so is not the same
            # sentence as "every version verified", and a vacuous claim is still a claim.
            lines.append(("PASS", (
                f"{adopter}: the composed window it serves carries no policy version at all, so "
                f"there is no bump to read and no evidence was verified for it")))
        elif accepted:
            lines.append(("PASS", (
                f"{adopter}: no unaccepted major in the {len(finding['window'])} version(s) its "
                f"composed window carries ({', '.join(finding['window'])}), each read from "
                f"platform's signed evidence at {finding['tag']} and verified under {adopter}'s "
                f"own identity constant; {len(accepted)} major(s) accepted, named above")))
        else:
            lines.append(("PASS", (
                f"{adopter}: no major in the {len(finding['window'])} version(s) its composed "
                f"window carries ({', '.join(finding['window'])}), each read from platform's "
                f"signed evidence at {finding['tag']} and verified under {adopter}'s own identity "
                f"constant")))
    if majors or drifted:
        return "FAIL", lines
    if unlooked:
        return "SKIP", lines
    return "PASS", lines


# ---------------------------------------------------------------- looking at the estate

def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def records_at_served_ref(unit_dir: Path) -> tuple[str | None, list[tuple[str, str]]]:
    """The commit this repository serves, and every file under accepted-majors/ in its tree at
    that commit. A working-tree or staged file is not served and is not read."""
    head = _git(unit_dir, "rev-parse", "-q", "--verify", "HEAD^{commit}")
    if head.returncode != 0:
        return None, []
    served = head.stdout.strip()
    try:
        return served, acceptance_records_at(unit_dir, served)
    except ValueError:
        return served, []


def gate_reader_drift(unit_dir: Path) -> str | None:
    """Ticket 132: whether the adopter gate this repository serves reads the acceptance record the
    way this check does. Read at HEAD, like everything else here. A repository serving no gate
    script has no reader to drift, and says nothing here."""
    for basename in GATE_BASENAMES:
        shown = _git(unit_dir, "show", f"HEAD:.github/scripts/{basename}")
        if shown.returncode == 0:
            drift = reader_drift(shown.stdout)
            return None if drift is None else f".github/scripts/{basename} {drift}"
    return None


def look(estate: Path, unit: str, platform_dir: Path) -> dict:
    """One adopter, measured. Every read below is of a served document: the adopter's composed
    evidence at the commit it serves, and platform's evidence at the tag that adopter pins."""
    finding: dict = {"adopter": unit, "tag": None, "window": [], "computed": {}, "skip": None,
                      "unread": [], "served": None, "records": [], "reader_drift": None}
    unit_dir = estate / unit
    # Ticket 129: the acceptance records, read at the same served commit as everything else here.
    finding["served"], finding["records"] = records_at_served_ref(unit_dir)
    finding["reader_drift"] = gate_reader_drift(unit_dir)

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
                   for b in GATE_BASENAMES
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

    # Ticket 129: the acceptance record. Planted records only; none of them is a real acceptance.
    def rec(party: str = "driftwood", version: str = "5.0.0", publisher: str = "platform",
            by: str = "Example Owner") -> str:
        return (f"kind: major-acceptance\nparty: {party}\npublisher: {publisher}\n"
                f"version: {version}\naccepted_by: {by}\naccepted_on: 2026-09-23\n")

    def carrying(window: list[str], records: list[tuple[str, str]]) -> dict:
        return {"adopter": "driftwood", "tag": "v3.2.0", "window": window,
                "computed": {v: "major" for v in window}, "skip": None,
                "served": "c" * 40, "records": records}

    here = "accepted-majors/platform-5.0.0.yaml"
    check("a well-formed record parses to its five fields",
          acceptance_from_text(rec()),
          {"party": "driftwood", "publisher": "platform", "version": "5.0.0",
           "accepted_by": "Example Owner", "accepted_on": "2026-09-23"})
    check("a record with no accepted_by is not a record",
          isinstance(acceptance_from_text(rec(by="''")), str), True)
    check("a carried major with a record accepting it for this adopter is the pass",
          grade([carrying(["5.0.0"], [(here, rec())])])[0], "PASS")
    check("a record for another institution accepts nothing here",
          grade([carrying(["5.0.0"], [(here, rec(party="tuppence"))])])[0], "FAIL")
    check("a record for another version accepts nothing here",
          grade([carrying(["5.0.0"], [(here, rec(version="4.0.0"))])])[0], "FAIL")
    check("a record for another publisher accepts nothing here",
          grade([carrying(["5.0.0"], [(here, rec(publisher="nist"))])])[0], "FAIL")
    check("the hub's own reader block has not drifted from itself",
          reader_drift(Path(__file__).read_text()), None)
    check("a gate with no reader block has drifted",
          (reader_drift("def main():\n    pass\n") or "").startswith("carries no"), True)
    status_mixed, lines_mixed = grade([carrying(["4.0.0", "5.0.0"], [(here, rec())])])
    check("an accepted 5.0.0 does not accept the 4.0.0 still in the window",
          (status_mixed, [k for k, m in lines_mixed if "4.0.0 in the composed" in m]),
          ("FAIL", ["FAIL"]))

    if bad:
        print(f"FAIL: {bad} selfcheck case(s) did not grade as written")
        return 1
    print("OK: unreviewed_major selfcheck (the window, the pin, both identity-constant readers, the "
          "acceptance record and the report's arithmetic, on planted inputs; no estate read, no "
          "cosign run)")
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
