"""Do the three adopter gates answer the same question the same way?

Eco-system ticket 99. Three institutions carry three hand-written adopter gates, each implementing
ADR-0011's "computes that institution's own composed bump" in its own words. Nothing graded whether
they agreed. tuppence's gate folded its whole supported window where driftwood's and ludlow's folded
what the pull request moves, so a major standing in the window refused every pull request whatever
it changed: twelve consecutive red `shift-left` runs from 2026-08-28, found by a human reading a
workflow, not by a check. Three answers to one question is the underlying fault; this is the check
that names the next divergence on the day it appears.

WHAT IS MEASURED, AND AGAINST WHAT.

  The SERVED artefact is each adopter's own committed gate script -- `.github/scripts/
  adopter-gate.py`, or `adopter_gate.py` in ludlow -- in the estate checkout, the same bytes that
  repository's CI runs.

  The OPERATION that reaches it is that repository's own `shift-left.yml` step named `adopter
  gate ...`: this grader reads that step's command line out of the workflow, keeps its flags
  exactly as the workflow spells them, and substitutes only the VALUES (a planted repository, a
  planted commit, a temporary output path). Every token past the interpreter must be either a long
  flag this grader has a role for or a token it planted a value for; anything else -- a new flag,
  its value, a new positional, templated or plain literal alike -- stops the run with a named
  refusal (`resolve_argv`, narrowed 2026-09-05 after review). A planted case that no longer
  resembles the served operation would prove nothing about the estate.

  Nothing is faked. The evidence the gates verify is platform's own real committed evidence at a
  real tag, and `cosign verify-blob` really runs, really verifies a real Fulcio certificate, and is
  really allowed to refuse. What is planted is only the SUBJECT: a throwaway adopter repository
  whose composed window and platform pin move in a stated way between two real commits.

THE CASES. Each names the movement it plants and the verdict ADR-0011's reading gives it, and the
check requires both that the three gates agree and that they agree on that verdict. Agreement alone
would pass three gates that had broken in the same direction.

  standing    the window holds 4.0.0 at both ends and the pin does not move -- this pull request
              moves nothing, so it composes `none` and the gate adopts. This is the case that
              divided the estate for a fortnight.
  arrival     4.0.0 enters the window -- its own publisher-signed evidence records a major, so the
              composed bump is major and the gate refuses.
  quiet       2.0.1 enters the window -- its evidence records `none`, so an arrival is not a
              refusal by itself; the fold reads the evidence, never the version number.
  retirement  2.0.1 leaves the window -- a retirement reaches the institution as a major and the
              gate refuses.

WHAT THIS DOES NOT GRADE. Whether any one gate's verdict is RIGHT beyond these four planted
movements; each repository's own `verify-adopter-gate.sh` grades its own gate in depth, and this
check does not re-run them. It also does not read a gate's source to decide what it would do: every
line below is an exit code and an output file from a real subprocess.

    fold_agreement.py <estate-dir>   # plant, run the three real gates, grade; exits 0/1/3
    fold_agreement.py --selfcheck    # the pure rules, on planted inputs, no estate and no cosign
"""

from __future__ import annotations

import json
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path

import yaml

GATE_STEP_NAME_PREFIX = "adopter gate"
GATE_BASENAMES = ("adopter-gate.py", "adopter_gate.py")
SHELL_TAIL = {"|", "||", "&&", ";", ">", ">>", "2>&1", "&"}
NOT_THE_GATE = {"--matrix-row", "matrix-row", "--splice-body", "splice-body", "read-pin",
                "verify-commit", "wrap-section", "--print-only"}


class NoGateStep(Exception):
    """The workflow carries no step this grader can recognise as the adopter gate."""


class Unresolved(Exception):
    """The served operation carries an argument this grader has no planted value for."""


# ---------------------------------------------------------------- reading the served operation

def _logical_lines(run_text: str) -> list[str]:
    return [ln.strip() for ln in run_text.replace("\\\n", " ").splitlines() if ln.strip()]


def _tokens_of_gate_call(line: str, script_basename: str) -> list[str] | None:
    try:
        tokens = shlex.split(line, comments=True)
    except ValueError:
        return None
    if not any(t.endswith(script_basename) for t in tokens):
        return None
    cut = next((i for i, t in enumerate(tokens) if t in SHELL_TAIL), len(tokens))
    tokens = tokens[:cut]
    if any(t in NOT_THE_GATE for t in tokens):
        return None
    return tokens


def gate_argv(workflow_text: str, script_basename: str) -> list[str]:
    """The command line the workflow's own `adopter gate` step runs, tokenised.

    Anchored on the step's `name:` rather than on the script path, because every adopter invokes
    the same script for other work in the same workflow (`--matrix-row`, `read-pin`,
    `splice-body`), and grading the wrong invocation would grade the wrong question. The shell tail
    (`2>&1 | tee ...`) is not part of the operation that reaches the artefact and is cut.
    """
    doc = yaml.safe_load(workflow_text) or {}
    for job in (doc.get("jobs") or {}).values():
        for step in (job or {}).get("steps") or []:
            name = str(step.get("name") or "").strip().lower()
            if not name.startswith(GATE_STEP_NAME_PREFIX):
                continue
            for line in _logical_lines(str(step.get("run") or "")):
                tokens = _tokens_of_gate_call(line, script_basename)
                if tokens:
                    return tokens
    raise NoGateStep(
        f"no step named {GATE_STEP_NAME_PREFIX!r}... runs {script_basename} in this workflow")


def long_flags(tokens: list[str]) -> set[str]:
    return {t for t in tokens if t.startswith("--")}


def resolve_argv(tokens: list[str], mapping: dict[str, str],
                  value_flags: set[str] = None) -> list[str]:  # type: ignore[assignment]
    """The served operation's own tokens with planted values substituted, and NOTHING else
    reaching the real gate.

    Every token past the interpreter must be one of two things: a long flag this grader has a role
    for (`VALUE_FLAGS`), or a token it planted a value for. Anything else raises `Unresolved`.

    Narrowed 2026-09-05 after review. The first version raised only on a token the workflow
    templated (`${{ ... }}`) or expanded from a shell variable (`$old_pin`), which left the
    published guarantee false: a new long flag with a plain LITERAL value -- `--corpus-dir
    corpus/generated` -- was handed straight through to the real gate, and the run only went red
    because argparse happens to reject an unknown flag. A gate parsing with `parse_known_args`, or
    a flag the gate does accept (`--skip-cosign-verify` is in tuppence's gate and is not in
    `NOT_THE_GATE`), would have been carried silently into the planted run and the comparison would
    have graded something nobody planted. The flag list is the whitelist now, not the templating
    syntax.
    """
    flags = VALUE_FLAGS if value_flags is None else value_flags
    out: list[str] = []
    i = 0
    while i < len(tokens):
        token = tokens[i]
        if i == 0:  # the interpreter the workflow names
            out.append(token)
            i += 1
            continue
        if token.startswith("--"):
            if token not in flags:
                raise Unresolved(
                    f"{token} -- the served operation carries a long argument this grader has no "
                    f"role for, so it cannot plant a value for it; a planted case that is not the "
                    f"served operation grades nothing")
            out.append(token)
            if i + 1 < len(tokens) and not tokens[i + 1].startswith("--"):
                value = tokens[i + 1]
                if value not in mapping:
                    raise Unresolved(
                        f"{value} -- the value of {token} in the served operation, for which this "
                        f"grader planted nothing")
                out.append(str(mapping[value]))
                i += 2
                continue
            i += 1
            continue
        if token not in mapping:
            raise Unresolved(
                f"{token} -- a positional argument of the served operation for which this grader "
                f"planted nothing")
        out.append(str(mapping[token]))
        i += 1
    return out


# ---------------------------------------------------------------- reading a verdict back

BUMP_ROW = re.compile(r"^\|\s*bump\s*\|\s*\*\*(?P<declared>[^*]+)\*\*\s*\|\s*\*\*(?P<composed>[^*]+)\*\*\s*\|",
                       re.MULTILINE)


def composed_from_markdown(markdown: str) -> str | None:
    """ludlow writes no machine-readable summary; its composed bump reaches its reviewer (and its
    own workflow's pull-request body) through the rendered table, so that is where it is read."""
    m = BUMP_ROW.search(markdown)
    return m.group("composed").strip() if m else None


def composed_from_json(doc: dict) -> str | None:
    """tuppence's `--out` summary carries `composed`; driftwood's carries
    `result.composed_bump`. Both are that gate's own written answer, not a re-derivation."""
    if isinstance(doc.get("composed"), str):
        return doc["composed"]
    result = doc.get("result")
    if isinstance(result, dict) and isinstance(result.get("composed_bump"), str):
        return result["composed_bump"]
    return None


# ---------------------------------------------------------------- judging agreement

def divergences(case: str, results: dict[str, dict]) -> list[str]:
    """One line per gate whose answer differs from the answer the others gave. The answer is the
    pair (verdict, composed bump): two gates that both adopt while naming the movement differently
    still disagree about the number the reviewer reads.

    A gate that ran and refused without stating a composed bump at all has still ANSWERED -- its
    exit code is what its own `shift-left` job grades -- so it is compared, not excused. Its answer
    is (refuse, None), and the line below carries its last output so the reason it could not state
    a bump is visible rather than guessed at. Only a gate that could not be run at all is unknown,
    and `grade` treats that as a could-not-look.
    """
    answers = {unit: (r["verdict"], r["composed"]) for unit, r in results.items()}
    if len(set(answers.values())) <= 1:
        return []
    common = Counter(answers.values()).most_common()
    # `repr` as the tie-break key, not the tuple itself: an answer's composed bump may be None (a
    # gate that refused without stating one), and None does not order against a string.
    top = sorted((a for a, n in common if n == common[0][1]), key=repr)[0]
    agreeing = sorted(u for u, a in answers.items() if a == top)
    lines = []
    for unit in sorted(answers):
        if answers[unit] == top:
            continue
        verdict, composed = answers[unit]
        said = (f"composed {composed!r}" if composed is not None
                else "stating no composed bump at all: "
                     + str(results[unit].get("output", ""))[:160])
        lines.append(
            f"case {case!r}: {unit}'s gate answered {verdict} ({said}) where "
            f"{', '.join(agreeing)} answered {top[0]} (composed {top[1]!r}) -- one movement, more "
            f"than one answer, and only one of them can be the estate's")
    return lines


def grade(cases: dict[str, dict[str, dict | None]]) -> tuple[str, list[tuple[str, str]]]:
    """FAIL beats SKIP: a divergence that was actually observed is not softened by a gate that
    could not be run at all."""
    lines: list[tuple[str, str]] = []
    if not cases:
        return "SKIP", [("SKIP", "no case was planted, so no gate was run and nothing was compared")]
    bad = 0
    unlooked = 0
    for case in sorted(cases):
        results = cases[case]
        missing = sorted(u for u, r in results.items() if r is None)
        for unit in missing:
            unlooked += 1
            lines.append(("SKIP", f"case {case!r}: {unit}'s gate could not be run at all, so its "
                                   f"answer is unknown and agreement cannot be claimed"))
        ran = {u: r for u, r in results.items() if r is not None}
        found = divergences(case, ran)
        for line in found:
            lines.append(("FAIL", line))
        bad += len(found)
        if len(ran) < 2:
            # One gate agreeing with itself is not agreement. Before this guard an estate carrying
            # a single adopter -- or two whose gates could not be run -- reached a PASS line that
            # said "the three adopters' gates".
            unlooked += 1
            lines.append(("SKIP", f"case {case!r}: only {len(ran)} gate(s) answered "
                                   f"({', '.join(sorted(ran)) or 'none'}), and agreement between "
                                   f"fewer than two gates is not a thing this check can observe"))
        elif not found and not missing:
            answer = next(iter(ran.values()))
            lines.append(("PASS", f"case {case!r}: {len(ran)} gates ({', '.join(sorted(ran))}) each "
                                   f"answered {answer['verdict']} with composed bump "
                                   f"{answer['composed']!r}"))
    if bad:
        return "FAIL", lines
    if unlooked:
        return "SKIP", lines
    return "PASS", lines


# ---------------------------------------------------------------- planting and running

# The role each flag of the served operation plays, so that a planted value can be put where the
# workflow puts a real one. A flag with no role here and a templated value stops the run.
PLATFORM_DIR_FLAGS = {"--platform-dir"}
ADOPTER_DIR_FLAGS = {"--adopter-dir", "--ludlow-dir"}
BASE_REF_FLAGS = {"--base-ref", "--composed-base-ref", "--old-ref"}
HEAD_REF_FLAGS = {"--head-ref", "--composed-head-ref", "--new-ref"}
NEW_PIN_FLAGS = {"--new-pin-yaml"}
OLD_PIN_FLAGS = {"--old-pin-yaml"}
OUT_JSON_FLAGS = {"--out"}
OUT_MARKDOWN_FLAGS = {"--markdown-out", "--out-comment"}
IDENTITY_FLAGS = {"--identity-regexp"}
ISSUER_FLAGS = {"--issuer"}
VALUE_FLAGS = (PLATFORM_DIR_FLAGS | ADOPTER_DIR_FLAGS | BASE_REF_FLAGS | HEAD_REF_FLAGS
               | NEW_PIN_FLAGS | OLD_PIN_FLAGS | OUT_JSON_FLAGS | OUT_MARKDOWN_FLAGS
               | IDENTITY_FLAGS | ISSUER_FLAGS)

CASES = {
    # name: (base window, head window, base pin tag, head pin tag, verdict, composed)
    "standing": (["4.0.0"], ["4.0.0"], "v2.0.1", "v2.0.1", "adopt", "none"),
    "arrival": (["2.0.1"], ["2.0.1", "4.0.0"], "v2.0.0", "v2.0.1", "refuse", "major"),
    "quiet": (["2.0.0"], ["2.0.0", "2.0.1"], "v2.0.0", "v2.0.1", "adopt", "none"),
    "retirement": (["2.0.1", "4.0.0"], ["4.0.0"], "v2.0.0", "v2.0.1", "refuse", "major"),
}

PIN_TEMPLATE = """apiVersion: source.toolkit.fluxcd.io/v1
kind: GitRepository
metadata:
  name: platform
  namespace: flux-system
spec:
  interval: 1h
  url: https://github.com/policy-as-versioned-platform/platform
  ref:
    tag: {tag}
    commit: "{commit}"
---
apiVersion: kustomize.toolkit.fluxcd.io/v1
kind: Kustomization
metadata:
  name: platform-distribution
  namespace: flux-system
spec:
  interval: 1h
  path: ./distribution
"""


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _commit(repo: Path, message: str) -> str:
    _git(repo, "add", "-A")
    _git(repo, "-c", "user.name=fold-agreement", "-c", "user.email=fold@example.invalid",
         "-c", "commit.gpgsign=false", "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD").stdout.strip()


def _write_state(repo: Path, window: list[str], tag: str, commit: str) -> None:
    (repo / "gitops" / "platform").mkdir(parents=True, exist_ok=True)
    (repo / "gitops" / "platform" / "platform-pin.yaml").write_text(
        PIN_TEMPLATE.format(tag=tag, commit=commit))
    (repo / "composed").mkdir(parents=True, exist_ok=True)
    members = [{"name": f"policy-v{v}", "version": v} for v in window]
    members.append({"name": "policy-version-orphan-guard"})  # machinery, no version
    (repo / "composed" / "evidence.json").write_text(json.dumps({"members": members}, indent=2))


def plant(adopter_repo: Path, case: tuple, tag_commits: dict[str, str]) -> dict[str, str]:
    base_window, head_window, base_tag, head_tag = case[0], case[1], case[2], case[3]
    adopter_repo.mkdir(parents=True, exist_ok=True)
    _git(adopter_repo, "init", "-q", "-b", "main")
    _write_state(adopter_repo, base_window, base_tag, tag_commits[base_tag])
    base_sha = _commit(adopter_repo, "base")
    _write_state(adopter_repo, head_window, head_tag, tag_commits[head_tag])
    head_sha = _commit(adopter_repo, "head")
    return {"base_sha": base_sha, "head_sha": head_sha, "base_tag": base_tag, "head_tag": head_tag}


def identity_constants(unit_dir: Path, script: Path) -> tuple[str, str] | None:
    """Each adopter holds its own identity constant, and each holds it in a different place: two in
    their `shift-left.yml` env block, one as a module constant in the gate script itself. Read
    from whichever of those the repository actually has, never from a value typed in here."""
    workflow = unit_dir / ".github" / "workflows" / "shift-left.yml"
    if workflow.is_file():
        env = yaml.safe_load(workflow.read_text()) or {}
        flat: dict[str, str] = {}
        for scope in [env.get("env") or {}] + [
                (job or {}).get("env") or {} for job in (env.get("jobs") or {}).values()]:
            flat.update({str(k): str(v) for k, v in scope.items()})
        regexp = next((v for k, v in flat.items() if k.endswith("IDENTITY_REGEXP")), None)
        issuer = next((v for k, v in flat.items() if k.endswith("ISSUER")), None)
        if regexp and issuer:
            return regexp, issuer
    import ast
    tree = ast.parse(script.read_text())
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


def build_mapping(tokens: list[str], script: Path, planted: dict, platform_dir: Path,
                   adopter_repo: Path, out_json: Path, out_markdown: Path,
                   identity: tuple[str, str]) -> dict[str, str]:
    """Map the served operation's own value tokens onto the planted case, by the ROLE of the flag
    that introduces them. Positional arguments (driftwood's `compose <platform> <old> <new>`) are
    mapped by position after the subcommand."""
    mapping: dict[str, str] = {}
    for token in tokens:
        if token.endswith(GATE_BASENAMES[0]) or token.endswith(GATE_BASENAMES[1]):
            mapping[token] = str(script)
    positionals: list[str] = []
    i = 1  # token 0 is the interpreter
    while i < len(tokens):
        token = tokens[i]
        if token.startswith("--"):
            if token in VALUE_FLAGS and i + 1 < len(tokens):
                value = tokens[i + 1]
                if token in PLATFORM_DIR_FLAGS:
                    mapping[value] = str(platform_dir)
                elif token in ADOPTER_DIR_FLAGS:
                    mapping[value] = str(adopter_repo)
                elif token in BASE_REF_FLAGS:
                    mapping[value] = planted["base_sha"]
                elif token in HEAD_REF_FLAGS:
                    mapping[value] = planted["head_sha"]
                elif token in NEW_PIN_FLAGS:
                    mapping[value] = str(adopter_repo / "gitops" / "platform" / "platform-pin.yaml")
                elif token in OLD_PIN_FLAGS:
                    mapping[value] = str(out_json.parent / "old-platform-pin.yaml")
                elif token in OUT_JSON_FLAGS:
                    mapping[value] = str(out_json)
                elif token in OUT_MARKDOWN_FLAGS:
                    mapping[value] = str(out_markdown)
                elif token in IDENTITY_FLAGS:
                    mapping[value] = identity[0]
                elif token in ISSUER_FLAGS:
                    mapping[value] = identity[1]
                i += 2
                continue
            i += 1
            continue
        if i > 1 and not tokens[i - 1].startswith("--"):
            positionals.append(token)
        elif i == 1:
            pass
        i += 1
    # driftwood: `compose <platform_dir> <old_tag> <new_tag>`; the subcommand word is first. The
    # subcommand maps to itself -- a planted value, deliberately identical -- so that resolve_argv
    # can require EVERY token past the interpreter to be planted and still let it through. A
    # positional this grader has no role for stays unmapped and stops the run there.
    if positionals and positionals[0] == "compose":
        mapping[positionals[0]] = positionals[0]
        roles = [str(platform_dir), planted["base_tag"], planted["head_tag"]]
        for value, planted_value in zip(positionals[1:], roles):
            mapping[value] = planted_value
    return mapping


def run_gate(unit: str, unit_dir: Path, planted: dict, platform_dir: Path, adopter_repo: Path,
             workdir: Path) -> tuple[dict | None, str]:
    """Run this adopter's REAL gate, through its own workflow's own flags. Returns (None, reason)
    when the gate could not be run at all: its answer is then unknown, and unknown is never read as
    agreement."""
    script = next((unit_dir / ".github" / "scripts" / b for b in GATE_BASENAMES
                   if (unit_dir / ".github" / "scripts" / b).is_file()), None)
    workflow = unit_dir / ".github" / "workflows" / "shift-left.yml"
    if script is None:
        return None, f"{unit} carries no adopter gate script at .github/scripts/{GATE_BASENAMES[0]}"
    if not workflow.is_file():
        return None, f"{unit} carries no .github/workflows/shift-left.yml to read the gate's own operation from"
    tokens = gate_argv(workflow.read_text(), script.name)
    identity = identity_constants(unit_dir, script)
    if identity is None:
        return None, (f"{unit} holds no identity constant this grader could find, in its "
                       f"shift-left.yml env or in {script.name}, so its gate cannot be run "
                       f"identity-pinned the way its own CI runs it")
    out_json = workdir / "summary.json"
    out_markdown = workdir / "comment.md"
    # The pull request BASE's copy of the pin, which two of the three workflows hand the gate as a
    # file read out of their own git history. Planted the same way, from the base commit.
    (workdir / "old-platform-pin.yaml").write_text(
        _git(adopter_repo, "show", f"{planted['base_sha']}:gitops/platform/platform-pin.yaml").stdout)
    mapping = build_mapping(tokens, script, planted, platform_dir, adopter_repo, out_json,
                             out_markdown, identity)
    argv = resolve_argv(tokens, mapping)
    try:
        proc = subprocess.run(argv, capture_output=True, text=True, cwd=str(workdir))
    except OSError as exc:
        # The interpreter the workflow names is not on this runner (`python3` on a machine that has
        # only `python`, say). Nothing was observed, so nothing is claimed: this is a could-not-look
        # naming the command, not a crash that leaves the wrapper reporting "0 movements differed".
        return None, (f"{unit}'s gate could not be started at all on this runner: {argv[0]!r} "
                       f"({type(exc).__name__}: {exc})")
    composed = None
    if out_json.is_file():
        try:
            composed = composed_from_json(json.loads(out_json.read_text()))
        except json.JSONDecodeError:
            composed = None
    if composed is None and out_markdown.is_file():
        composed = composed_from_markdown(out_markdown.read_text())
    tail = ((proc.stdout + proc.stderr).strip().splitlines() or [""])[-1]
    # A gate that stated no composed bump has still answered -- its exit code is the thing its own
    # required check grades -- so `composed` is None here and compared as part of the answer,
    # never quietly dropped.
    return {"verdict": "adopt" if proc.returncode == 0 else "refuse", "composed": composed,
            "exit": proc.returncode, "argv": argv, "output": tail}, ""


def run(estate: Path) -> tuple[str, list[tuple[str, str]]]:
    # Absolute: every gate below runs with its cwd inside a temporary directory, the way its own
    # workflow runs it from the runner's workspace root, so a relative estate path would resolve
    # to nothing there and the run would report "no answer" for a gate that was never invoked.
    estate = estate.resolve()
    import importlib.util
    tpa_path = Path(__file__).resolve().parent.parent / "twin-per-adopter" / "twin_per_adopter.py"
    spec = importlib.util.spec_from_file_location("twin_per_adopter", tpa_path)
    tpa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tpa)

    units = [u for u in tpa.adopters(estate) if (estate / u).is_dir()]
    if not units:
        return "SKIP", [("SKIP", "no party in this estate claims the adopter role, so there is no "
                                  "adopter gate to compare against another")]
    platform_src = estate / "platform"
    if not (platform_src / ".git").is_dir():
        return "SKIP", [("SKIP", "this checkout carries no clone of platform, whose signed evidence "
                                  "every adopter gate verifies before it composes anything")]
    if shutil.which("cosign") is None:
        return "SKIP", [("SKIP", "cosign is not installed, and a gate whose signature verification "
                                  "cannot run has not answered the question this check compares")]

    lines: list[tuple[str, str]] = []
    cases: dict[str, dict[str, dict | None]] = {}
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        platform_dir = root / "platform"
        subprocess.run(["git", "clone", "--local", "--quiet", str(platform_src), str(platform_dir)],
                        check=True, capture_output=True)
        tags = sorted({t for case in CASES.values() for t in (case[2], case[3])})
        tag_commits = {}
        for tag in tags:
            resolved = _git(platform_dir, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}")
            if resolved.returncode != 0:
                return "SKIP", [("SKIP", f"this checkout of platform has no tag object for {tag}, "
                                          f"which every planted case pins")]
            tag_commits[tag] = resolved.stdout.strip()
        head_tag = CASES["standing"][3]
        _git(platform_dir, "checkout", "--quiet", head_tag)
        lines.append(("ok", f"platform checked out at {head_tag} ({tag_commits[head_tag][:12]}), "
                             f"the tag every planted pin names as the head"))

        for name, case in CASES.items():
            cases[name] = {}
            for unit in units:
                workdir = root / name / unit
                workdir.mkdir(parents=True)
                adopter_repo = workdir / "repo"
                planted = plant(adopter_repo, case, tag_commits)
                _git(platform_dir, "checkout", "--quiet", head_tag)
                try:
                    result, reason = run_gate(unit, estate / unit, planted, platform_dir,
                                               adopter_repo, workdir)
                except (NoGateStep, Unresolved) as exc:
                    lines.append(("FAIL", f"{unit}: this grader could not reproduce the operation "
                                           f"its own shift-left.yml runs -- {type(exc).__name__}: "
                                           f"{exc}"))
                    cases[name][unit] = None
                    continue
                cases[name][unit] = result
                if result is None:
                    lines.append(("SKIP", f"case {name!r}: {reason}"))
                else:
                    lines.append(("ok", f"case {name!r} {unit}: exit {result['exit']}, composed "
                                         f"{result['composed']!r} -- {result['output'][:120]}"))

    status, judged = grade(cases)
    lines.extend(judged)
    expected = [(name, case[4], case[5]) for name, case in CASES.items()]
    if status == "PASS":
        wrong = []
        for name, want_verdict, want_composed in expected:
            answer = next(r for r in cases[name].values() if r is not None)
            if answer["verdict"] != want_verdict or answer["composed"] != want_composed:
                wrong.append(f"case {name!r}: all three answered {answer['verdict']} "
                             f"(composed {answer['composed']!r}) where ADR-0011's reading of the "
                             f"movement is {want_verdict} (composed {want_composed!r})")
        for line in wrong:
            lines.append(("FAIL", line))
        if wrong:
            status = "FAIL"
    if any(kind == "FAIL" for kind, _ in lines):
        status = "FAIL"
    if status == "PASS":
        # The wrapper quotes this rather than hard-coding "the three adopters": however many gates
        # answered is what the PASS line is allowed to say.
        answered = sorted({u for case in cases.values() for u, r in case.items() if r is not None})
        lines.append(("SUMMARY", (
            f"on {len(CASES)} planted movements of a composed window ({', '.join(sorted(CASES))}), "
            f"the {len(answered)} adopter gates that answered ({', '.join(answered)}) -- each run "
            f"through the flag shape its own shift-left.yml uses, against platform's real signed "
            f"evidence with real cosign -- returned the same verdict and the same composed bump, "
            f"and each was the verdict ADR-0011's reading gives that movement")))
    return status, lines


# ---------------------------------------------------------------- selfcheck

SELFCHECK_WORKFLOW = """
jobs:
  gate:
    steps:
      - name: adopter gate -- compose this institution's own bump
        run: |
          python3 unit/.github/scripts/adopter-gate.py \\
            --platform-dir platform --adopter-dir unit \\
            --base-ref "${{ github.event.pull_request.base.sha }}" --head-ref HEAD \\
            --out summary.json 2>&1 | tee out.txt
      - name: fill the matrix row
        run: python3 unit/.github/scripts/adopter-gate.py --matrix-row --platform-dir platform
"""


def selfcheck() -> int:
    bad = 0

    def check(label: str, got, want) -> None:
        nonlocal bad
        ok = got == want
        print(f"{'ok ' if ok else 'BAD'}: {label}" + ("" if ok else f" -> {got!r}, wanted {want!r}"))
        bad += 0 if ok else 1

    argv = gate_argv(SELFCHECK_WORKFLOW, "adopter-gate.py")
    check("the gate step's own command is read, and the shell tail is not part of it",
          argv[-2:] + [t for t in argv if t in SHELL_TAIL], ["--out", "summary.json"])
    check("the matrix-row invocation of the same script is not mistaken for the gate",
          "--matrix-row" in argv, False)
    check("the flags are the workflow's own",
          long_flags(argv), {"--platform-dir", "--adopter-dir", "--base-ref", "--head-ref", "--out"})
    try:
        gate_argv("jobs:\n  x:\n    steps:\n      - name: build\n        run: make\n", "adopter-gate.py")
        check("a workflow with no gate step refuses", "returned", "raised NoGateStep")
    except NoGateStep:
        check("a workflow with no gate step refuses", "raised", "raised")
    try:
        resolve_argv(argv, {})
        check("an unmapped templated argument refuses", "returned", "raised Unresolved")
    except Unresolved:
        check("an unmapped templated argument refuses", "raised", "raised")

    # The narrowing this check exists for (review, 2026-09-05): a NEW long flag carrying a plain
    # literal value must stop the run too. Before this, `--corpus-dir corpus/generated` was handed
    # straight to the real gate and the run only went red because argparse happens to refuse an
    # unknown flag -- a gate using parse_known_args, or a flag the gate accepts, would have carried
    # it into the planted run in silence.
    planted = {"g.py": "/plant/gate.py", "platform": "/plant/platform", "HEAD": "abc123"}
    grown = ["python3", "g.py", "--platform-dir", "platform", "--corpus-dir", "corpus/generated"]
    try:
        resolve_argv(grown, dict(planted, **{"corpus/generated": "/plant/corpus"}))
        check("a new long flag with a plain literal value refuses", "returned", "raised Unresolved")
    except Unresolved as exc:
        check("a new long flag with a plain literal value refuses, naming it",
              "--corpus-dir" in str(exc), True)
    try:
        resolve_argv(["python3", "g.py", "--platform-dir", "somewhere-else"], planted)
        check("a known flag whose value was not planted refuses", "returned", "raised Unresolved")
    except Unresolved as exc:
        check("a known flag whose value was not planted refuses, naming it",
              "somewhere-else" in str(exc), True)
    try:
        resolve_argv(["python3", "g.py", "compose", "platform"], planted)
        check("a positional nobody planted refuses", "returned", "raised Unresolved")
    except Unresolved as exc:
        check("a positional nobody planted refuses, naming it", "compose" in str(exc), True)
    check("and the whole served shape resolves when every token is planted",
          resolve_argv(["python3", "g.py", "--platform-dir", "platform", "--head-ref", "HEAD"],
                        planted),
          ["python3", "/plant/gate.py", "--platform-dir", "/plant/platform", "--head-ref", "abc123"])

    check("the composed bump is read out of a rendered comment table",
          composed_from_markdown("| bump | **patch** | **none** |\n"), "none")
    check("and out of either machine-readable summary shape",
          (composed_from_json({"composed": "major"}),
           composed_from_json({"result": {"composed_bump": "patch"}})), ("major", "patch"))

    agree = {"driftwood": {"verdict": "adopt", "composed": "none"},
             "ludlow": {"verdict": "adopt", "composed": "none"},
             "tuppence": {"verdict": "adopt", "composed": "none"}}
    check("three gates that answer alike diverge on nothing", divergences("standing", agree), [])
    split = dict(agree, tuppence={"verdict": "refuse", "composed": "major"})
    found = divergences("standing", split)
    check("the fortnight-long divergence is named, with both answers",
          (len(found), "tuppence" in found[0], "refuse" in found[0], "adopt" in found[0]),
          (1, True, True, True))
    check("a divergence fails the grade", grade({"standing": split})[0], "FAIL")
    mute = dict(agree, ludlow={"verdict": "refuse", "composed": None, "output": "cosign errored"})
    found_mute = divergences("quiet", mute)
    check("a gate that refused without stating a bump is compared, with the reason it printed",
          (len(found_mute), "ludlow" in found_mute[0], "cosign errored" in found_mute[0]),
          (1, True, True))
    check("a gate that could not be run is a could-not-look, never an agreement",
          grade({"standing": dict(agree, ludlow=None)})[0], "SKIP")
    check("agreement on every case is the pass", grade({"standing": agree})[0], "PASS")
    only_one = {"driftwood": {"verdict": "adopt", "composed": "none"}}
    status_one, lines_one = grade({"standing": only_one})
    check("one gate agreeing with itself is not agreement",
          (status_one, any("fewer than two" in m for _, m in lines_one)), ("SKIP", True))

    if bad:
        print(f"FAIL: {bad} selfcheck case(s) did not grade as written")
        return 1
    print("OK: fold_agreement selfcheck (the workflow reader, the resolver and the comparator, "
          "on planted inputs; no estate read, no gate run)")
    return 0


def main(argv: list[str]) -> int:
    if "--selfcheck" in argv:
        return selfcheck()
    if len(argv) != 1:
        print("usage: fold_agreement.py <estate-dir> | --selfcheck")
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
