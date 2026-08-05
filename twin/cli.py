"""The `twin` command — seam 1, the primary boundary.

A command takes a pinned model repository and emits a signed artefact to a declared output path.
Because attestation already requires determinism given the pins, this seam is golden-file
testable, and that property is itself the first test.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path

import yaml

from . import TOOL_VERSION, attest, fixtures, index, invariants, verbs
from .artefact import Artefact, ArtefactError
from .attest import AttestationError
from .blob import BlobRefError
from .grades import Capabilities, GradeError
from .index import IndexError_
from .invariants import FAIL, PASS, SKIP
from .invariants.harness import LIVE, MANIFEST_PATH, Suite, load_manifest
from .model import ModelError
from .reproduce import ReproduceError
from .repo import ModelRepo, RepoError
from .schema import SchemaError
from .scoring import ScoreError
from .verbs import VerbError


def _say(message: str) -> None:
    print(f"==> {message}")


def _emit(artefact: Artefact, out: str) -> int:
    path = artefact.write(out)
    sidecar = attest.write(artefact, path)
    depth = artefact.depth
    print(f"{artefact.kind} -> {path}")
    print(f"  attestation  {sidecar.name} (machine-attested, {attest.UNSIGNED})")
    print(f"  sha256       {artefact.digest()}")
    print(f"  depth        {depth['grade']}")
    for name, summary in sorted(depth.get("capabilities", {}).items()):
        unchecked = ", ".join(str(u["index"]) for u in summary["unchecked"]) or "-"
        print(
            f"    {name:<18} {summary['grade']:<8} {summary['checked']}/{summary['total']} "
            f"of decision ticket {summary['owning_ticket']}  unchecked: {unchecked}"
        )
    return 0


def _open(args: argparse.Namespace) -> tuple[ModelRepo, Capabilities, str]:
    repo = ModelRepo.open(args.repo, args.ref)
    caps = Capabilities.load()
    return repo, caps, verbs.resolve_org(repo, args.org)


# -- verbs ----------------------------------------------------------------------------------


def cmd_sense(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.sense(
        repo, caps, org, args.signal, verbs.command_for("sense", org=org, signal=args.signal)
    )
    return _emit(artefact, args.out)


def cmd_run(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    artefact = verbs.run(
        repo,
        caps,
        org,
        args.scenario,
        verbs.command_for("run", org=org, scenario=args.scenario, at=args.at),
        at=args.at,
    )
    return _emit(artefact, args.out)


def cmd_score(args: argparse.Namespace) -> int:
    from .artefact import digest_of_file

    repo, caps, org = _open(args)
    artefact = verbs.score(
        repo,
        caps,
        org,
        args.forecast,
        args.outcome,
        verbs.command_for(
            "score", org=org, outcome=args.outcome, forecast_sha256=digest_of_file(args.forecast)
        ),
    )
    return _emit(artefact, args.out)


def cmd_graph(args: argparse.Namespace) -> int:
    repo, caps, org = _open(args)
    return _emit(verbs.graph(repo, caps, org, verbs.command_for("graph", org=org)), args.out)


def cmd_validate(args: argparse.Namespace) -> int:
    """The gate an author or CI runs before committing. Nothing here writes model files, so
    "validated on write" means validated at the boundary the model crosses to get in."""
    from .model import BehaviouralOverlay, Overlay, World, orgs

    repo = ModelRepo.open(args.repo, args.ref)
    _say(f"validating {args.repo} at {repo.pin.commit[:12]}")
    World.load(repo)
    print("  ok   world layer")
    for org in orgs(repo):
        overlay = Overlay.load(repo, org)
        counts = {
            name: len(getattr(overlay, name))
            for name in ("components", "signals", "claims", "scenarios", "outcomes", "people", "edges")
        }
        print(f"  ok   overlay {org}: " + ", ".join(f"{v} {k}" for k, v in counts.items() if v))
        try:
            gated = BehaviouralOverlay.load(repo, org)
        except ModelError:
            print(f"       {org} has no behavioural overlay (the default, and the supported state)")
        else:
            print(
                f"  ok   {org} behavioural overlay: {len(gated.observations)} cohort observations, "
                f"DPIA {gated.meta['dpia']}, advisory only, {gated.meta['retention_days']}-day retention"
            )
    print("PASS: every object validates against its closed schema")
    return 0


def cmd_index(args: argparse.Namespace) -> int:
    repo = ModelRepo.open(args.repo, args.ref)
    out = index.write(repo, args.out)
    print(f"derived index -> {out}  ({index.read_digest(out)[:16]})")
    print("  derived, never authoritative: drop it and rebuild from the repository alone")
    return 0


def cmd_fixture(args: argparse.Namespace) -> int:
    root = fixtures.build(args.out)
    print(f"fixture model repository -> {root}")
    print("  deterministic: same content, same commit sha, on every machine")
    return 0


# -- grades ---------------------------------------------------------------------------------


def cmd_grade(args: argparse.Namespace) -> int:
    caps = Capabilities.load()
    for graded in caps:
        if args.capability and graded.capability != args.capability:
            continue
        checked = sum(1 for c in graded.criteria if c.checked)
        _say(
            f"{graded.capability}: {graded.grade}  ({checked}/{len(graded.criteria)} of "
            f"decision ticket {graded.owning_ticket})"
        )
        for c in graded.criteria:
            mark = "x" if c.checked else " "
            print(f"  [{mark}] {c.index}. {c.text}")
            if c.checked:
                print(f"        {c.ticked_by}: {c.evidence}")
    return 0


# -- the invariant suite ----------------------------------------------------------------------


def cmd_verify(args: argparse.Namespace) -> int:
    if args.artefact:
        return _reproduce(args.artefact, args.repo)
    if args.rehash:
        return _rehash(args.authorise)
    if args.bless_goldens:
        return _bless_goldens(args.authorise)

    suite = Suite()
    if args.list:
        for number, (name, is_invariant) in enumerate(suite.plan(), start=1):
            entry = next((e for e in suite.manifest if e.name == name), None)
            kind = "invariant" if is_invariant else "harness"
            state = f" [{entry.state}]" if entry else ""
            print(f"{number:>3}  {kind:<9} {name}{state}")
        return 0

    _say(f"twin invariant suite (tool {TOOL_VERSION})")
    results, ok = invariants.run(only=args.only or None)
    live = {e.name for e in suite.manifest if e.state == LIVE}

    for r in results:
        print(f"{r.number:>3}  {r.status:<4}  {r.name:<44}  {r.detail}")

    passed = sum(1 for r in results if r.status == PASS)
    failed = [r for r in results if r.status == FAIL]
    skipped = [r for r in results if r.status == SKIP]
    pending = [r for r in skipped if r.invariant and r.name not in live]
    honest = [r for r in skipped if r not in pending]

    print()
    print(
        f"RESULT: {passed} passed, {len(failed)} failed, {len(skipped)} skipped "
        f"({len(pending)} pending invariants, {len(honest)} skipped and not faked)"
    )
    if failed:
        for r in failed:
            print(f"  FAIL {r.name}: {r.detail}")
    return 0 if ok else 1


def _reproduce(artefact_path: str, repo_path: str | None) -> int:
    """`twin verify <artefact>` — recompute it from its pins and say whether it reproduces."""
    from .reproduce import reproduce

    if not repo_path:
        print(
            "twin verify <artefact> needs --repo: the pin records which model tree was read, "
            "not where that repository lives on this machine.",
            file=sys.stderr,
        )
        return 2
    report = reproduce(repo_path, artefact_path)
    _say(f"reproducing {artefact_path} from its pins")
    for link in report.chain:
        mark = "ok  " if link.reproduces else "FAIL"
        print(f"  {mark} {link.kind:<18} {link.actual[:16]} (recorded {link.expected[:16]})")
    mark = "ok  " if report.expected == report.actual else "FAIL"
    print(f"  {mark} {report.kind:<18} {report.actual[:16]} (recorded {report.expected[:16]})")
    print("  tolerance: none — byte identity. Scores carry a declared "
          f"{__import__('twin.scoring', fromlist=['x']).SIGNIFICANT_DIGITS}-significant-digit quantisation in the format.")
    if report.reproduces:
        print("\nREPRODUCES: the pins are sufficient to recompute this artefact exactly.")
        return 0
    if report.diff:
        print("\ndiverged:")
        print(report.diff)
    print("\nDIVERGES: the recorded pins do not recompute this artefact. The attestation is a claim, not a proof.")
    return 1


def _rehash(authorise: str | None) -> int:
    """Re-pin the check-body hashes. Deliberately awkward: it is how a refusal gets weakened."""
    from .invariants import body_hash, registry
    from .invariants.checks import module_hash

    checks = registry()
    wanted = {e.name: body_hash(checks[e.name]) for e in load_manifest() if e.state == LIVE}
    text = MANIFEST_PATH.read_text(encoding="utf-8")

    changed: list[str] = []
    head, blocks = _split_manifest(text)
    module_was = re.search(r"^checks_module_sha256:\s*(\S+)", "\n".join(head), re.M)
    if module_was and module_was.group(1) not in ("TBD", module_hash()):
        changed.append("checks_module_sha256")

    rewritten: list[list[str]] = []
    for block in blocks:
        name = _entry_name(block)
        if name not in wanted:
            rewritten.append(block)
            continue
        was = re.search(r"^\s*body_sha256:\s*(\S+)", "\n".join(block), re.M)
        if was and was.group(1) not in ("TBD", wanted[name]):
            changed.append(name)
        rewritten.append(_set_key(block, "body_sha256", wanted[name], after="state"))

    if changed and not _cites(authorise):
        print(
            "refusing to re-pin: "
            + ", ".join(sorted(set(changed)))
            + " already had a hash. Pass --authorise \"decision ticket NN — reason\".",
            file=sys.stderr,
        )
        return 1

    if changed:
        citation = json.dumps(authorise)
        rewritten = [
            _set_key(block, "authorised_by", citation, after="body_sha256")
            if _entry_name(block) in changed
            else block
            for block in rewritten
        ]
        if "checks_module_sha256" in changed:
            head = _set_top(head, "checks_module_authorised_by", citation)

    head = _set_top(head, "checks_module_sha256", module_hash())
    lines = head + [line for block in rewritten for line in block]
    MANIFEST_PATH.write_text("\n".join(lines).rstrip("\n") + "\n", encoding="utf-8")
    print(f"manifest re-pinned ({len(wanted)} live checks, module {module_hash()[:12]})")
    if changed:
        print(f"  authorised change to: {', '.join(sorted(set(changed)))}")
    return 0


def _split_manifest(text: str) -> tuple[list[str], list[list[str]]]:
    """Everything before the first entry, then one line-block per entry."""
    lines = text.splitlines()
    starts = [i for i, line in enumerate(lines) if re.match(r"\s*- name:\s*\S+", line)]
    if not starts:
        return lines, []
    bounds = starts + [len(lines)]
    return lines[: starts[0]], [lines[a:b] for a, b in zip(bounds, bounds[1:])]


def _drop_key(block: list[str], key: str) -> list[str]:
    """Remove `key:` and any continuation lines belonging to it (block scalars span lines)."""
    out: list[str] = []
    indent: int | None = None
    for line in block:
        match = re.match(rf"^(\s*){re.escape(key)}:", line)
        if match:
            indent = len(match.group(1))
            continue
        if indent is not None:
            if line.strip() and len(line) - len(line.lstrip()) > indent:
                continue
            indent = None
        out.append(line)
    return out


def _entry_name(block: list[str]) -> str:
    match = re.match(r"\s*- name:\s*(\S+)", block[0])
    return match.group(1) if match else ""


def _set_key(block: list[str], key: str, value: str, after: str) -> list[str]:
    block = _drop_key(block, key)
    out: list[str] = []
    placed = False
    for line in block:
        out.append(line)
        anchor = re.match(rf"^(\s*){re.escape(after)}:", line)
        if anchor and not placed:
            out.append(f"{anchor.group(1)}{key}: {value}")
            placed = True
    if not placed:  # no anchor line: append at the end of the block, at the entry's indent
        indent = " " * (len(block[0]) - len(block[0].lstrip()) + 2)
        out.append(f"{indent}{key}: {value}")
    return out


def _set_top(head: list[str], key: str, value: str) -> list[str]:
    """Set a top-level scalar, above `invariants:` — anything after it belongs to the list."""
    out = [line for line in head if not re.match(rf"^{re.escape(key)}:", line)]
    try:
        insert = next(i for i, line in enumerate(out) if re.match(r"^invariants:", line))
    except StopIteration:
        insert = len(out)
    out.insert(insert, f"{key}: {value}")
    return out


def _bless_goldens(authorise: str | None) -> int:
    """Re-record the committed artefact digests the cross-architecture check compares against.

    Gated like `--rehash`, and for the same reason: the goldens are the only thing that catches a
    change in what the engine computes, so re-blessing them is how a scoring rule or a
    serialisation gets quietly replaced. Recording them for the first time needs no citation.
    """
    from .invariants.checks import GOLDEN_PATH, golden_digests, recompute_digests
    from .invariants.harness import context

    with tempfile.TemporaryDirectory(prefix="twin-goldens-") as handle:
        ctx = context(Path(handle))
        digests = recompute_digests(ctx)
        capabilities_digest = ctx.caps.digest

    previous = golden_digests()
    moved = sorted(k for k in previous if previous[k] != digests.get(k))
    if moved and not _cites(authorise):
        print(
            f"refusing to re-bless: {', '.join(moved)} already had a golden digest. "
            'Pass --authorise "decision ticket NN — reason".',
            file=sys.stderr,
        )
        return 1
    GOLDEN_PATH.write_text(
        json.dumps(
            {
                "note": "Artefact digests from the fixture model repository. Byte-identity given "
                "the pins is the property; these are what a second architecture must reproduce.",
                "tool_version": TOOL_VERSION,
                "capabilities_digest": capabilities_digest,
                "authorised_by": authorise,
                "digests": digests,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"golden digests -> {GOLDEN_PATH.name} ({len(digests)} artefacts)")
    for kind, digest in sorted(digests.items()):
        print(f"  {kind:<18} {digest}")
    return 0


def _cites(text: str | None) -> bool:
    return bool(text and re.search(r"decision ticket\s+\d{1,2}", text, re.I))


# -- wiring -----------------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="twin", description=__doc__.splitlines()[0])
    parser.add_argument("--version", action="version", version=f"twin {TOOL_VERSION}")
    subs = parser.add_subparsers(dest="verb", required=True)

    def with_repo(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub.add_argument("--repo", required=True, help="path to the model repository")
        sub.add_argument("--ref", default="HEAD", help="git ref to pin (default HEAD)")
        return sub

    def with_org(sub: argparse.ArgumentParser) -> argparse.ArgumentParser:
        sub.add_argument("--org", default=None, help="which overlay; required when there is more than one")
        return sub

    sense = with_org(with_repo(subs.add_parser("sense", help="bind a dated signal to a component")))
    sense.add_argument("--signal", required=True)
    sense.add_argument("--out", required=True)
    sense.set_defaults(fn=cmd_sense)

    run = with_org(with_repo(subs.add_parser("run", help="execute a scenario; emits forecasts, plural")))
    run.add_argument("--scenario", required=True)
    run.add_argument("--at", default=None, help="override the scenario's declared time")
    run.add_argument("--out", required=True)
    run.set_defaults(fn=cmd_run)

    score = with_org(with_repo(subs.add_parser("score", help="score a forecast bundle against an outcome")))
    score.add_argument("--forecast", required=True, help="path to a forecast-bundle artefact")
    score.add_argument("--outcome", required=True)
    score.add_argument("--out", required=True)
    score.set_defaults(fn=cmd_score)

    graph = with_org(with_repo(subs.add_parser("graph", help="emit the typed knowledge graph")))
    graph.add_argument("--out", required=True)
    graph.set_defaults(fn=cmd_graph)

    validate = with_repo(subs.add_parser("validate", help="validate every object against its schema"))
    validate.set_defaults(fn=cmd_validate)

    idx = with_repo(subs.add_parser("index", help="build the derived index (never authoritative)"))
    idx.add_argument("--out", required=True)
    idx.set_defaults(fn=cmd_index)

    fixture = subs.add_parser("fixture", help="build the deterministic fixture model repository")
    fixture.add_argument("--out", required=True)
    fixture.set_defaults(fn=cmd_fixture)

    grade = subs.add_parser("grade", help="show computed depth grades")
    grade.add_argument("--capability", default=None)
    grade.set_defaults(fn=cmd_grade)

    verify = subs.add_parser("verify", help="run the invariant suite, or reproduce an artefact")
    verify.add_argument("artefact", nargs="?", help="an artefact to recompute from its pins")
    verify.add_argument("--repo", default=None, help="the model repository the pins refer to")
    verify.add_argument("--only", action="append", default=[], help="check name or number; repeatable")
    verify.add_argument("--list", action="store_true", help="list the checks without running them")
    verify.add_argument("--rehash", action="store_true", help="re-pin check-body hashes in the manifest")
    verify.add_argument("--authorise", default=None, help="decision ticket authorising a hash change")
    verify.add_argument(
        "--bless-goldens", action="store_true", help="re-record the committed artefact digests"
    )
    verify.set_defaults(fn=cmd_verify)

    return parser


REFUSALS = (
    RepoError,
    ModelError,
    VerbError,
    GradeError,
    ArtefactError,
    AttestationError,
    BlobRefError,
    IndexError_,
    ReproduceError,
    SchemaError,
    ScoreError,
    yaml.YAMLError,
    OSError,
    RecursionError,
)


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result: int = args.fn(args)
        return result
    except REFUSALS as exc:
        # A refusal is a sentence, not a traceback. A tool that sells honest refusal should not
        # answer malformed input with a stack dump.
        print(f"twin {args.verb}: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
