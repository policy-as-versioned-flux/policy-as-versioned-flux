#!/usr/bin/env python3
"""Build talk/deck.md — the demo deck — from the gate's own captures.

GENERATED, NOT AUTHORED. Hand editing talk/deck.md is not an option: the next
build overwrites it, and talk/verify-demo.sh grades the deck it rebuilds, never
the file you edited. Change the prose in talk/narration.json, change the
figures by re-running the gate.

Lifted from .scratch/talk-spec/pitch-v6/build_deck.py, which had the one
discipline worth keeping: every terminal line on a slide is read out of a
capture file at build time, so a slide cannot drift from the command that
produced it. What is new here is that the captures are the truth surface's own
(talk/verify-all.sh writes one talk/captures/<slug>.out per script), so a beat's
status tag is the gate's grade rather than a claim the deck makes.

A deck NAMES THE RUN IT DESCRIBES (ticket 66). The scheduled clock commits the
captures and the TRUTH line of each run in one lane commit, and never the deck
(talk/deck.md is outside the observation lane, ADR-0024). So the committed deck
is built from a RECORDED run: it carries `<!-- deck run=N hub=H source=recorded -->`,
quotes that run's TRUTH line, and every check of it reads that run's captures
out of the commit that recorded them -- never off the disk, where a local gate
run has left whatever it last produced. A deck built from the captures on disk
(`--out`, which verify-demo.sh does for its rebuild) names `source=disk`, and
may quote no TRUTH line: the truth surface has not recorded that run yet.

Three statuses, and only three, on a beat:
  observed true / could not look / observed false   the gate's grade, from the
      capture's last line (the brief's contract: 'PASS: ', 'SKIP: ', 'FAIL: ').
  no check yet, owned by ticket NN                  generator-side. A step with
      no capture in this run. Never rendered as a gate grade.

  python3 talk/build_deck.py               write talk/deck.md describing the newest recorded run
  python3 talk/build_deck.py --run N       ... describing recorded run N
  python3 talk/build_deck.py --out PATH    write a deck of the captures on disk (verify-demo.sh does)
  python3 talk/build_deck.py --run N --out PATH
  python3 talk/build_deck.py --name PATH   print the run a built deck describes and its commit
  python3 talk/build_deck.py --check PATH  run the demo checks over a built deck, against the run it names
  python3 talk/build_deck.py --selfcheck   assert the four statuses render right
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# The gate's grade word, keyed by the prefix its scripts put on their last line.
WORD = {"PASS": "observed true", "SKIP": "could not look", "FAIL": "observed false"}

# ponytail: build order. A deck of the captures ON DISK is built from whatever
# is there when the build runs. Inside a gate run, a script that sorts after
# verify/demo/ has not rewritten its capture yet, so its beat quotes the
# previous run's capture. That is why such a deck says "built during run N"
# and quotes no TRUTH line, and why the committed deck is built from a RECORDED
# run's captures out of git instead. Upgrade path: have verify-all.sh stamp its
# run id into each capture and assert it here.

# ponytail: the gate discards each script's exit code (it keeps only the
# capture), so the grade is read from the capture's last line, which the build
# brief makes the contract ("SKIP: <reason>" / "FAIL: <reason>"). If a script
# ever exits non-zero without saying so on its last line, the deck and the gate
# table disagree; verify-demo.sh catches that by cross-reading step 7's own
# verdict table, which is produced by a different script. Upgrade path: have
# verify-all.sh append its exit code to the capture, and read it here.


class CouldNotLook(Exception):
    """The deck names a recorded run whose recording commit this checkout cannot
    reach (a shallow clone, or a log line with no lane commit behind it). Not a
    grade: the check exits 3 and says why."""


def slug(script):
    """The capture name verify-all.sh writes for a script path. Same rule."""
    s = script[2:] if script.startswith("./") else script
    return s.replace("/", "_")[:-3] if s.endswith(".sh") else s.replace("/", "_")


def capture_path(script, capdir):
    return Path(capdir) / (slug(script) + ".out")


def capture_lines(script, capdir):
    txt = ANSI.sub("", capture_path(script, capdir).read_text(errors="replace"))
    return [r.rstrip() for r in txt.splitlines()]


def grade(rows):
    """(tag, reason) from a capture's last non-empty line. Never invents one."""
    last = ""
    for r in reversed(rows):
        if r.strip():
            last = r.strip()
            break
    for tag in WORD:
        if last.startswith(tag + ":"):
            return tag, last[len(tag) + 1:].strip()
    return "FAIL", "the capture's last line does not carry a PASS:, SKIP: or FAIL: verdict"


def select(rows, grep=None, drop=None, limit=None, drop_last=True):
    """Pull real text out of a capture. Never adds a line, never edits one."""
    rows = list(rows)
    if drop_last:
        while rows and not rows[-1].strip():
            rows.pop()
        if rows:
            rows.pop()
    if grep:
        rows = [r for r in rows if any(g in r for g in grep)]
    if drop:
        rows = [r for r in rows if not any(d in r for d in drop)]
    rows = [r for r in rows if r.strip()]
    return rows[:limit] if limit else rows


def wrap(rows, width):
    """Hard-wrap overflowing lines at spaces only, so no figure is ever split."""
    out = []
    for line in rows:
        if len(line) <= width:
            out.append(line)
            continue
        # Keep every run of spaces the capture had, so a wrapped table column
        # still lines up. Break only between words, so no figure is ever split.
        lead = line[:len(line) - len(line.lstrip())]
        cur = lead
        for part in re.findall(r"\S+\s*", line):
            if cur.strip() and len(cur) + len(part.rstrip()) > width:
                out.append(cur.rstrip())
                cur = lead + "  " + part
            else:
                cur += part
        if cur.strip():
            out.append(cur.rstrip())
    return out


def _git(root, *args, binary=False):
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True,
                          text=not binary, check=True).stdout


def hub_sha(root=ROOT):
    try:
        return _git(root, "rev-parse", "--short", "HEAD").strip()
    except Exception:
        return "unknown"


# ------------------------------------------------------- the run a deck names

def truth_lines(root=ROOT):
    p = Path(root) / "talk" / "truth.log"
    if not p.exists():
        return []
    return [l.strip() for l in p.read_text().splitlines() if l.strip().startswith("TRUTH ")]


def line_run(line):
    m = re.search(r"\brun=(\S+)", line)
    return m.group(1) if m else ""


def line_hub(line):
    m = re.search(r"\bhub=(\S+)", line)
    return m.group(1) if m else ""


def recorded_run(which, root=ROOT):
    """The TRUTH line of recorded run `which` ("newest" or a run number), or "".

    Only a NUMBERED run can be named. A local run writes `run=local` and its
    captures are throwaway scratch the lane never commits, so there is nothing
    a deck of it could be graded against tomorrow.
    """
    lines = [l for l in truth_lines(root) if line_run(l).isdigit()]
    if which == "newest":
        return lines[-1] if lines else ""
    for l in reversed(lines):
        if line_run(l) == str(which):
            return l
    return ""


def run_commit(run, root=ROOT):
    """The commit that recorded run N, or None if this checkout cannot reach it.

    The lane commit appends the TRUTH line and the captures together, so the
    commit wanted is the newest one touching talk/truth.log at which the log's
    LAST line is run N. Not `git log -S`: on a shallow clone the boundary
    commit "adds" the whole file, and -S would name it for every run it
    contains, pairing run N's line with a later run's captures.
    """
    try:
        shas = _git(root, "log", "--format=%H", "--", "talk/truth.log").split()
    except Exception:
        return None
    for sha in shas:
        try:
            txt = _git(root, "show", f"{sha}:talk/truth.log")
        except Exception:
            continue
        tail = [l for l in txt.splitlines() if l.startswith("TRUTH ")]
        if tail and line_run(tail[-1]) == str(run):
            return sha
    return None


def export_captures(sha, dest, root=ROOT):
    """talk/captures as committed at `sha`, unpacked under `dest`. Read out of
    git and never off the disk: the captures on disk are whatever the last
    local gate run left there, which is not the run the deck names."""
    dest = Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    blob = _git(root, "archive", sha, "talk/captures", binary=True)
    with tarfile.open(fileobj=io.BytesIO(blob)) as tar:
        try:
            tar.extractall(dest, filter="data")
        except TypeError:   # python < 3.12 has no extraction filter
            tar.extractall(dest)
    return dest / "talk" / "captures"


def named_run(run, root=ROOT):
    """(TRUTH line, recording commit) for run `run`. Refuses a run the log does
    not record; raises CouldNotLook when the commit is unreachable."""
    line = recorded_run(run, root)
    if not line:
        raise SystemExit(f"talk/truth.log records no numbered run {run!r}; a deck can only "
                         "describe a run the truth surface recorded and committed the captures of")
    sha = run_commit(line_run(line), root)
    if sha is None:
        raise CouldNotLook(named_run_reason(line))
    return line, sha


def named_run_reason(line):
    n = line_run(line)
    return (f"the truth surface recorded run {n} at hub={line_hub(line)}, but the commit that "
            f"recorded it (the lane commit whose newest TRUTH line is run {n}) is not reachable "
            "from this checkout; a shallow clone, or a line appended with no captures committed "
            "beside it")


NAME_RE = re.compile(r"<!-- deck (.*?) -->")


def deck_name(md):
    """The run a built deck says it describes, from its own marker, or {}."""
    m = NAME_RE.search(md)
    return dict(p.split("=", 1) for p in m.group(1).split(" ")) if m else {}


def marker(**kw):
    return "<!-- beat " + " ".join(f"{k}={v}" for k, v in kw.items()) + " -->"


MARKER_RE = re.compile(r"<!-- beat (.*?) -->")


def beat_status(b, scheduled, capdir):
    """(tag, reason, rows, cited) for one beat. The only place status is decided.

    The capture is read FIRST. `scheduled_only` (D4: a reader is not shown a
    rehearsal) may only downgrade a PASS to could-not-look — it may never hide
    an observed-false, and it may never substitute a procedural excuse for a
    reason the check gave in its own words. Before 2026-08-29 it returned
    could-not-look before the capture was ever opened, so a step the gate had
    graded FAIL rendered amber and the deck's own checker agreed; and step 4's
    real reason (two named live defects) was replaced by "this build is a local
    one", contradicting step 7's table on the same deck.
    """
    cap = capture_path(b["script"], capdir)
    if not cap.exists():
        return ("NOCHECK", f"owned by ticket {b['ticket']}", [], False)
    rows = capture_lines(b["script"], capdir)
    tag, reason = grade(rows)
    if tag == "PASS" and b.get("scheduled_only") and not scheduled:
        reason = ("this step's capture is green here, but the number is quoted only from the "
                  "scheduled truth run, never from a presenter's laptop, and this is a local "
                  "build — so the deck does not show it green. The capture's own words: "
                  + reason)
        tag = "SKIP"
    return tag, reason, select(rows, grep=b.get("grep"), drop=b.get("drop"), limit=b.get("limit")), True


def render_beat(b, scheduled, capdir):
    tag, reason, rows, cited = beat_status(b, scheduled, capdir)
    # The capture is NAMED by its path in the repository, whichever directory
    # it was read from: that is the file the run committed, and what a reader
    # can open.
    cap = "talk/captures/" + slug(b["script"]) + ".out"
    out = [marker(step=b["step"], status=tag, cited=("yes" if cited else "no"),
                  script=b["script"], capture=(cap if cited else "-")),
           "", f"## {b['step']} · {b['title']}", ""]
    if tag == "NOCHECK":
        out += [f"**no check yet, {reason}** — this step has no capture in this run, so the deck "
                "shows no result for it. That is the generator saying so, not the gate.", ""]
    else:
        out += [f"**{WORD[tag]}** — {reason}", ""]
    if rows:
        out += ["```text", f"$ bash {b['script']}"] + wrap(rows, b.get("width", 104)) + ["```", ""]
    out += ["<!--", b["narration"], "-->", ""]
    return out


def build(run=None, root=ROOT):
    """The deck as text. `run` names a recorded run ("newest" or N) and reads
    that run's captures out of its recording commit; None reads the captures on
    disk as this, unrecorded, run."""
    root = Path(root)
    narr = json.loads((root / "talk" / "narration.json").read_text())
    built = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    with tempfile.TemporaryDirectory() as tmp:
        if run is None:
            r = os.environ.get("GITHUB_RUN_NUMBER", "").strip()
            name = {"run": r or "local", "hub": hub_sha(root), "source": "disk"}
            scheduled, tail = bool(r), ""
            capdir = root / "talk" / "captures"
        else:
            tail, sha = named_run(run, root)
            name = {"run": line_run(tail), "hub": line_hub(tail), "source": "recorded"}
            scheduled = True   # every numbered run is the scheduled clock's
            capdir = export_captures(sha, Path(tmp), root)
        return _render(narr, name, scheduled, tail, capdir, built)


def _render(narr, name, scheduled, tail, capdir, built):
    run, hub = name["run"], name["hub"]
    md = ["---", "marp: true", f"title: \"{narr['title']}\"", f"description: \"{narr['subtitle']}\"",
          "theme: default", "paginate: true",
          f"footer: \"generated by talk/build_deck.py · run={run} · hub={hub} · {built}\"",
          "style: |",
          "  section { font-size: 24px; }",
          "  section h1 { font-size: 44px; }",
          "  section h2 { font-size: 32px; }",
          "  pre { font-size: 13px; line-height: 1.35; }",
          "  code { font-size: 13px; }",
          "  img { max-height: 62vh; }",
          "---", "",
          "<!-- GENERATED FILE. Do not hand edit: talk/build_deck.py overwrites it from",
          "     the named run's captures and talk/narration.json, and talk/verify-demo.sh",
          "     grades it against that run, not the file you edited. Prose: talk/narration.json. -->",
          "<!-- deck " + " ".join(f"{k}={v}" for k, v in name.items()) + " -->", ""]

    # title slide
    md += [f"# {narr['title']}", "", f"### {narr['subtitle']}", ""]
    if tail:
        m = re.match(r"TRUTH (\S+)", tail)
        when = m.group(1) if m else "an unknown time"
        md += [f"built {built} from the captures the truth surface committed for run **{run}**, "
               f"a scheduled run recorded {when} at hub `{hub}`. Each beat quotes that run's "
               "capture for its own check, and carries the grade that capture gave.", "",
               "the run this deck describes, as the truth surface recorded it in `talk/truth.log`:", "",
               "```text", tail, "```", ""]
    else:
        md += [f"built {built} during run **{run}** "
               f"({'a scheduled CI run' if scheduled else 'a local run, not the scheduled one'}) · hub `{hub}`. "
               "Each beat quotes the capture on disk for its own check, and carries the grade that capture gave.", "",
               "`talk/truth.log` has not recorded this run: the deck was built from the captures on "
               "disk while, or before, the truth surface wrote its line. So it quotes no headline "
               "number. The beats below carry their own grades, each read out of the capture named "
               "on the slide. An earlier run's line describes an earlier run and is not this deck's "
               "number, so it is not shown.", ""]
    md += ["<!--", narr["opening"], "-->", ""]

    for s in narr["slides"]:
        md += ["---", ""]
        if s["kind"] == "prose":
            md += [f"## {s['title']}", ""] + s["body"] + ["", "<!--", s["narration"], "-->", ""]
        elif s["kind"] == "diagram":
            md += [f"## {s['title']}", "", f"![w:900]({s['image']})", "", s["caption"], "",
                   "<!--", s["narration"], "-->", ""]
        elif s["kind"] == "beat":
            md += render_beat(s, scheduled, capdir)
        else:
            raise SystemExit(f"unknown slide kind: {s['kind']}")

    return "\n".join(md).rstrip() + "\n"


# ---------------------------------------------------------------- the checks

FIG = re.compile(r"£?\d[\d,]*(?:\.\d+)?%?")
# Named ceiling: headers, dates, tags, step numbers, ticket and ADR references
# are outside the figure check. Everything else in a beat body is checked.
OUTSIDE = [re.compile(r"\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}Z?)?"),
           re.compile(r"\b\d{2}:\d{2}\b"),
           re.compile(r"\bsteps?[\s=]*\d+(\s*(-|to|and)\s*\d+)?", re.I),
           re.compile(r"\btickets?\s+\d+((\s*,\s*|\s+and\s+)\d+)*", re.I),
           re.compile(r"\bADR-\d{4}\b"),
           re.compile(r"§\s*\d+"),
           re.compile(r"\b[QDH]\d+\b"),
           # the deck's own provenance stamp: `run=N` and the hub commit sha
           re.compile(r"\brun[= ]\*{0,2}\S+?\*{0,2}(?=[ .,·])"),
           re.compile(r"hub\s+`[0-9a-f]{7,40}`")]
BANNED = ["exemption", "hourglass", "admission gate", "deny gate"]


def _body(sl):
    # Outside the figure check: the beat and deck markers (tags), headings, the
    # fence rules, the "$ bash <script>" line that names the command, and the
    # marp front matter / narrator comments a reader never sees on the slide.
    return "\n".join(l for l in sl.splitlines()
                     if not l.startswith("<!-- beat ") and not l.startswith("<!-- deck ")
                     and not l.startswith("#")
                     and not l.strip().startswith("```") and not l.startswith("$ ")
                     and not l.strip().startswith("TRUTH ")
                     # markdown image directives: `![w:900](path)` is layout, not a figure
                     and not l.strip().startswith("!["))


def parse(md):
    """Split a built deck into ([beats], [non-beat slide bodies])."""
    slides = md.split("\n---\n")
    # slides[0] is the marp front matter (theme, paginate, the CSS font sizes).
    # It is machine configuration, never rendered as a slide, so it is outside
    # the figure check the same way a heading is.
    beats, prose = [], []
    for sl in slides[1:]:
        m = MARKER_RE.search(sl)
        if not m:
            prose.append(_body(sl))
            continue
        kv = dict(p.split("=", 1) for p in m.group(1).split(" "))
        beats.append((kv, _body(sl)))
    return beats, prose


def figures(body):
    t = body
    for rx in OUTSIDE:
        t = rx.sub(" ", t)
    return [f for f in FIG.findall(t) if any(c.isdigit() for c in f)]


def step7_table(capdir, script="verify/e2e/verify-e2e-step7-honesty.sh"):
    """Steps' verdicts as a different script recorded them. Breaks the circle."""
    p = capture_path(script, capdir)
    if not p.exists():
        return {}
    out = {}
    for line in capture_lines(script, capdir):
        m = re.match(r"\s{2,}(\d)\s{2,}\S.*?\s(PASS|SKIP|FAIL)\s", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def check(path, root=ROOT):
    """(bad, review, beats). Grades the deck against the run IT NAMES: a
    recorded run's captures come out of its recording commit; a disk deck is
    read against talk/captures/. Raises CouldNotLook when the named run's
    commit is unreachable, which is a could-not-look and not a grade."""
    root = Path(root)
    md = Path(path).read_text()
    bad, review = [], []
    beats, prose = parse(md)
    quoted = [l.strip() for l in md.splitlines() if l.strip().startswith("TRUTH ")]

    with tempfile.TemporaryDirectory() as tmp:
        name = deck_name(md)
        if not name:
            bad.append("the deck carries no `<!-- deck run=... -->` marker, so it names no run and "
                       "nothing can be read against it")
            run_word, capdir = "this run", root / "talk" / "captures"
        elif name.get("source") == "recorded":
            n = name.get("run", "?")
            run_word = f"run {n}"
            line = recorded_run(n, root)
            if not line:
                bad.append(f"the deck describes run {n}, but talk/truth.log records no numbered run {n}")
                capdir = root / "talk" / "captures"
            else:
                if line_hub(line) != name.get("hub"):
                    bad.append(f"the deck says run {n} was recorded at hub={name.get('hub')}, the "
                               f"TRUTH line says hub={line_hub(line)}")
                if quoted != [line]:
                    bad.append(f"the quoted TRUTH line is not the line that recorded run {n}, the run "
                               "this deck describes: a number from another run is not this deck's number")
                sha = run_commit(n, root)
                if sha is None:
                    raise CouldNotLook(named_run_reason(line))
                capdir = export_captures(sha, Path(tmp), root)
        else:
            run_word, capdir = "this run", root / "talk" / "captures"
            if quoted:
                bad.append("a deck built from the captures on disk describes a run the truth surface "
                           "has not recorded, so it may quote no TRUTH line; the one quoted is "
                           "another run's number")

        steps = [int(kv["step"]) for kv, _ in beats]
        if steps != sorted(steps) or steps != list(range(1, 8)):
            bad.append(f"beats are not the seven NORTH-STAR section 4 steps in order: {steps}")

        table = step7_table(capdir)
        for kv, body in beats:
            step = int(kv["step"])
            if kv["cited"] == "yes":
                cap = capture_path(kv["script"], capdir)
                if kv["capture"] != "talk/captures/" + cap.name:
                    bad.append(f"step {step}: cites {kv['capture']}, which is not the capture of "
                               f"{kv['script']}")
                if not cap.exists():
                    bad.append(f"step {step}: cites a capture that is not in {run_word}: {kv['capture']}")
                    continue
                tag, _ = grade(capture_lines(kv["script"], capdir))
                if tag != kv["status"]:
                    bad.append(f"step {step}: deck says {kv['status']}, the capture of {run_word} says {tag}")
                if table.get(step) and table[step] != kv["status"]:
                    bad.append(f"step {step}: deck says {kv['status']}, the run's own honesty table says {table[step]}")
                # Set membership, not substring: '8,269.23' is a substring of the
                # capture's '58,269.23' and used to pass as a figure that appears
                # nowhere as a value. Any short run of digits was free the same way.
                captured = set(figures(cap.read_text(errors="replace")))
                for f in figures(body):
                    if f not in captured:
                        bad.append(f"step {step}: figure '{f}' is on the slide but not in its capture")
            else:
                if kv["capture"] != "-":
                    bad.append(f"step {step}: uncited beat still names a capture")
                for f in figures(body):
                    bad.append(f"step {step}: figure '{f}' on a beat with no capture behind it")
                if kv["status"] not in ("SKIP", "NOCHECK"):
                    bad.append(f"step {step}: a beat with no capture claims {kv['status']}")
                # Absence is not "no check yet": a step whose script is on disk but
                # whose capture the run failed to produce reads as "the check does
                # not exist" to a reader. It is a missing observation, and red.
                if kv["status"] == "NOCHECK" and (root / kv["script"]).exists():
                    bad.append(f"step {step}: {kv['script']} exists on disk but {run_word} wrote no "
                               f"capture for it — that is a missing observation, not a missing check")

    # Every figure on a NON-beat slide. The prose deliberately spells numbers
    # out as words, so the small rule is the right one: a figure off a beat has
    # no capture behind it and cannot be checked, so it may not be there at all.
    for body in prose:
        for f in figures(body):
            bad.append(f"a non-beat slide carries the figure '{f}'; only a beat slide may carry a "
                       "figure, because only a beat has a capture to check it against")

    low = md.lower()
    for phrase in BANNED:
        if phrase in low:
            bad.append(f"phrase lint: '{phrase}' is refused vocabulary")
    for i, line in enumerate(md.splitlines(), 1):
        if "gate" in line.lower() and not any(p in line.lower() for p in BANNED):
            review.append(f"  line {i}: {line.strip()[:110]}")

    for s in quoted:
        if s not in truth_lines(root):
            bad.append("a quoted TRUTH line is not a line in talk/truth.log")

    return bad, review, beats


def selfcheck():
    assert slug("verify/e2e/verify-e2e-step7-honesty.sh") == "verify_e2e_verify-e2e-step7-honesty"
    assert slug(".estate-clone/ico/verify-penalty-feed.sh") == ".estate-clone_ico_verify-penalty-feed"
    assert grade(["x", "SKIP: waiting for tag v3.0.0"]) == ("SKIP", "waiting for tag v3.0.0")
    assert grade(["PASS: fine", ""]) == ("PASS", "fine")
    assert grade(["FAIL: nope"])[0] == "FAIL"
    assert grade(["no verdict at all"])[0] == "FAIL"
    assert select(["a", "b", "PASS: x"]) == ["a", "b"]
    assert wrap(["  aaa 326,139.13 bbb"], 12) == ["  aaa", "    326,139.13", "    bbb"]

    with tempfile.TemporaryDirectory() as tmp:
        capdir = Path(tmp)
        # a step with no capture renders generator-side, never as a gate grade
        b = {"step": 9, "title": "t", "script": "verify/none/verify-nothing-here.sh",
             "ticket": "42", "narration": "n"}
        tag, reason, rows, cited = beat_status(b, True, capdir)
        assert (tag, reason, rows, cited) == ("NOCHECK", "owned by ticket 42", [], False)
        md = "\n".join(render_beat(b, True, capdir))
        assert "no check yet, owned by ticket 42" in md and "capture=-" in md
        body = "\n".join(l for l in md.splitlines()
                         if not l.startswith("<!-- beat ") and not l.startswith("#"))
        assert figures(body) == [], figures(body)

        # scheduled_only may downgrade a PASS and NOTHING else. A capture the gate
        # graded FAIL renders FAIL on a local build, cited, with its own reason.
        b4 = {"step": 4, "title": "t", "script": "verify/selfcheck/verify-scheduled-only-probe.sh",
              "ticket": "16", "narration": "n", "scheduled_only": True}
        probe = capture_path(b4["script"], capdir)
        probe.write_text("looked at a cluster\nFAIL: the cage is NOT in force\n")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("FAIL", True), (tag, cited)
        assert reason == "the cage is NOT in force", reason
        probe.write_text("looked at a cluster\nSKIP: no Running pod to carry the cage\n")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("SKIP", True) and reason == "no Running pod to carry the cage"
        probe.write_text("looked at a cluster\nPASS: reconciled at the pinned revision\n")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("SKIP", True), (tag, cited)
        assert "reconciled at the pinned revision" in reason and "local build" in reason
        assert beat_status(b4, True, capdir)[0] == "PASS"

    # the figure check is set membership, not substring: 8,269.23 is inside
    # 58,269.23 and must not pass as a figure the capture carries
    assert "8,269.23" not in set(figures("residual 58,269.23"))

    # the figure check: a hand-typed figure with no capture behind it is caught
    assert figures("residual 58,269.23 and 40,000 GBP") == ["58,269.23", "40,000"]
    assert figures("built 2026-08-29 · step 4 · ticket 47 · ADR-0021 · Q2") == []
    # the deck's own name is outside the figure check; the sha is not a figure
    assert figures("for run **22**, a scheduled run recorded 2026-09-03T10:24Z at hub `14cc731`.") == []

    # the run a deck names: only a numbered run, newest by default, never local
    tl = ["TRUTH 2026-09-01T00:00Z run=local hub=aaaaaaa pass=1 fail=0 skip=0 excluded=0 total=1",
          "TRUTH 2026-09-02T00:00Z run=21 hub=bbbbbbb pass=1 fail=0 skip=0 excluded=0 total=1",
          "TRUTH 2026-09-03T00:00Z run=22 hub=ccccccc pass=1 fail=0 skip=0 excluded=0 total=1"]
    assert (line_run(tl[2]), line_hub(tl[2])) == ("22", "ccccccc")
    assert deck_name("x\n<!-- deck run=22 hub=ccccccc source=recorded -->\ny") == {
        "run": "22", "hub": "ccccccc", "source": "recorded"}
    assert deck_name("no marker") == {}
    print("selfcheck ok")


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", help="the recorded run to describe: a run number, or 'newest'")
    ap.add_argument("--out", help="write here instead of talk/deck.md")
    ap.add_argument("--name", metavar="PATH", help="print the run a built deck describes")
    ap.add_argument("--check", metavar="PATH", help="run the demo checks over a built deck")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)

    if a.selfcheck:
        selfcheck()
        return 0
    if a.name:
        name = deck_name(Path(a.name).read_text())
        if name.get("source") != "recorded":
            print(f"{a.name} describes no recorded run: " + (
                f"it was built from the captures on disk during run {name['run']}" if name
                else "it carries no deck marker"))
            return 1
        try:
            line, sha = named_run(name["run"])
        except CouldNotLook as e:
            print(f"could not look: {e}")
            return 3
        print(f"run={line_run(line)} hub={line_hub(line)} commit={sha[:7]}")
        return 0
    if a.check:
        try:
            bad, review, beats = check(a.check)
        except CouldNotLook as e:
            print(f"could not look: {e}")
            return 3
        if review:
            print(f"review, not a lint failure: the word gate appears on {len(review)} lines; "
                  "every use outside the four refused phrases is a human review item:")
            for r in review[:8]:
                print(r)
        for b in bad:
            print("  bad  " + b)
        print(f"checked {len(beats)} beats in {a.check}")
        return 1 if bad else 0

    # a build. talk/deck.md always describes a recorded run (the newest unless
    # --run says which); an --out deck describes the captures on disk unless
    # --run names a run.
    run = a.run
    if run is None and not a.out:
        run = "newest"
    out = Path(a.out) if a.out else ROOT / "talk" / "deck.md"
    try:
        text = build(run)
    except CouldNotLook as e:
        print(f"could not look: {e}")
        return 3
    out.write_text(text)
    name = deck_name(text)
    src = (f"run {name['run']}'s committed captures" if name["source"] == "recorded"
           else f"{len(list((ROOT / 'talk' / 'captures').glob('*.out')))} captures on disk")
    print(f"{out}: {len(text.splitlines())} lines from {src}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
