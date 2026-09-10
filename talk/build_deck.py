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

Beats are the seven NORTH-STAR section 4 steps and nothing else. An ASIDE is the other kind
of capture-reading slide (eco-system ticket 48): a read the demo makes that is not one of the seven
steps -- the Monte Carlo the pound rests on, the clocks that refresh it, the priced cage, the local
clock the twin's model call runs on. An aside is graded exactly as a beat is (its status is the
run's own grade for its script, every figure on it must be in its capture), and it is outside the
step ordering. Where a beat with no capture reads "no check yet", an aside with no capture reads
COULD NOT LOOK and NAMES the capture file the run did not write, so a reader is never shown a blank
where a number was, and never yesterday's number. The demo check exits 3 -- could not look -- when
an aside's capture is missing, and never 0.

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

# The split and the ceiling are read off the quoted line, never re-derived here: one counter,
# in talk/truth_manifest.py, for the gate and the deck alike (eco-system ticket 83). Imported by
# path because talk/ is not a package and this file is run as a script from anywhere.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from truth_manifest import measured                                          # noqa: E402

# The gate's grade word, keyed by the prefix its scripts put on their last line.
WORD = {"PASS": "observed true", "SKIP": "could not look", "FAIL": "observed false"}
# What grade() says when a capture's last line is not a verdict at all. Named, because
# resolved_grade() has to tell "the last line disagrees with the run" from "there is no last-line
# opinion to disagree with", and 30 of run 186's 120 captures are the second kind (16 of them
# specifically the wrapped-verdict shape; run 184 is 30 of 119).
# Hyphens, en and em dashes and slashes join words a phrase lint must read as separate ones.
JOINERS = re.compile(r"[-\u2010-\u2015/]+")
# The row count the record states about its own table, e.g. "**There are 5 rows below**".
# Bold is allowed on either side of the digits, because that is how the record writes it.
DECLARED_ROWS = re.compile(r"[Tt]here (?:is|are) \*{0,2}(\d+)\*{0,2} rows? below")
NO_VERDICT = "the capture's last line does not carry a PASS:, SKIP: or FAIL: verdict"

# A run that recorded no grade for a script is a COULD-NOT-LOOK, and it says which of the two
# shapes it is. It is not a grade, so it never appears in WORD, and the deck may not render it as
# one. Ticket 48 review F1: before this, the absent table fell back to the capture's last line --
# the very proxy the grade table exists to replace -- and a script whose verdict wraps then
# rendered `observed false` with the whole check green. A table can also lack a row for one
# script, which six of run 186's own 120 captures do, so the fallback is reachable on a run
# that has a table. The dated census is in ticket 48; this instrument needs no moving count.
UNGRADED = "UNGRADED"
NO_TABLE = ("this run committed no `talk/captures/_grades.tsv`, so it recorded no grade for "
            "`{script}` and this deck will not read one off the capture's last line")
NO_ROW = ("this run's `talk/captures/_grades.tsv` carries no row for `{script}`, so the run "
          "recorded no grade for it and this deck will not read one off the capture's last line")

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
    return "FAIL", NO_VERDICT


def grades_table(capdir):
    """{script: PASS|SKIP|FAIL} as the RUN graded it, out of talk/captures/_grades.tsv.

    The gate grades a script by its EXIT CODE and keeps only the capture, so reading a grade off a
    capture's LAST LINE is a proxy -- and a wrong one for every script whose verdict wraps. Run
    184: `.estate-clone/platform/fair/verify-fair-tail.sh` exited 0 and its capture's last line is
    the second half of a two-line `PASS:` sentence, so the last-line reading says FAIL. That is the
    Monte Carlo aside's own capture. verify-all.sh has written this per-script table inside the
    observation lane since ticket 59, so the deck reads what the run recorded.

    {} for a run that committed no table. A run with no table, and
    a run whose table has no row for one script, mean the same thing -- this run recorded no grade
    for it. Six of run 186's own 120 captures have no row. resolved_grade() says so by name rather
    than falling back to the capture's last line.
    """
    p = Path(capdir) / "_grades.tsv"
    if not p.exists():
        return {}
    out = {}
    for row in p.read_text(errors="replace").splitlines():
        if row.startswith("#") or not row.strip():
            continue
        cells = row.split("\t")
        if len(cells) >= 2 and cells[1] in WORD:
            out[cells[0]] = cells[1]
    return out


def verdict(rows, tag):
    """The WHOLE verdict sentence for `tag`: from the last line opening `TAG:` to the end of the
    capture. A one-line verdict reads exactly as grade() read it; a wrapped one is not cut off
    mid-clause, which is what quoting the last line alone would put on a slide."""
    idx = None
    for i, r in enumerate(rows):
        if r.strip().startswith(tag + ":"):
            idx = i
    if idx is None:
        return ""
    parts = [rows[idx].strip()[len(tag) + 1:].strip()]
    parts += [r.strip() for r in rows[idx + 1:] if r.strip()]
    return " ".join(p for p in parts if p)


def resolved_grade(script, rows, capdir):
    """(tag, reason, disagreement) for one script in one run.

    The tag is the run's own grade where the run recorded one, because that is the exit code the
    gate actually observed. `disagreement` is set only when the capture's last line carries a
    verdict of its OWN and it differs -- a capture that ends mid-sentence has no opinion to
    disagree with, and reading one out of it is the proxy this function exists to stop.
    """
    last_tag, last_reason = grade(rows)
    table = grades_table(capdir)
    if script not in table:
        # Never the last-line proxy. The run recorded no grade, the deck says which shape of
        # nothing that is, and check() puts it on the could-not-look list (exit 3).
        shape = NO_TABLE if not table else NO_ROW
        return UNGRADED, shape.format(script=script), None
    tag = table[script]
    reason = verdict(rows, tag) or last_reason
    bad = None
    if last_reason != NO_VERDICT and last_tag != tag:
        bad = (f"the capture's own last line says {last_tag} and the run's grade table "
               f"(talk/captures/_grades.tsv) says {tag}")
    return tag, reason, bad


def select(rows, grep=None, drop=None, limit=None, drop_last=True):
    """Pull real text out of a capture. Never adds a line, never edits one."""
    rows = list(rows)
    if drop_last:
        while rows and not rows[-1].strip():
            rows.pop()
        # The verdict goes above the fence, in its own words, so it is dropped from the quoted
        # body. It used to be ONE popped line, which left the first half of a two-line `PASS:`
        # sentence quoted as if it were output (the Monte Carlo capture is exactly that shape).
        start = None
        for i, r in enumerate(rows):
            if any(r.strip().startswith(tag + ":") for tag in WORD):
                start = i
        if start is not None and start == len(rows) - 1:
            rows.pop()
        elif start is not None:
            rows = rows[:start]
        elif rows:
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
    tag, reason, _ = resolved_grade(b["script"], rows, capdir)
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
    elif tag == UNGRADED:
        out += [f"**could not look** — {reason}.", ""]
    else:
        out += [f"**{WORD[tag]}** — {reason}", ""]
    if rows:
        out += ["```text", f"$ bash {b['script']}"] + wrap(rows, b.get("width", 104)) + ["```", ""]
    out += ["<!--", b["narration"], "-->", ""]
    return out


ASIDE_RE = re.compile(r"<!-- aside (.*?) -->")


def aside_status(a, capdir):
    """(tag, reason, rows, cited) for one aside. ABSENT is not a grade and never renders as one:
    it is the deck saying, by name, that the run wrote no capture for this read."""
    cap = capture_path(a["script"], capdir)
    if not cap.exists():
        return ("ABSENT", a["absent"], [], False)
    rows = capture_lines(a["script"], capdir)
    tag, reason, _ = resolved_grade(a["script"], rows, capdir)
    return tag, reason, select(rows, grep=a.get("grep"), drop=a.get("drop"), limit=a.get("limit")), True


def render_aside(a, capdir):
    tag, reason, rows, cited = aside_status(a, capdir)
    want = "talk/captures/" + slug(a["script"]) + ".out"
    out = ["<!-- aside " + " ".join(f"{k}={v}" for k, v in
                                    (("name", a["name"]), ("status", tag),
                                     ("cited", "yes" if cited else "no"),
                                     ("script", a["script"]),
                                     ("capture", want if cited else "-"),
                                     ("wanted", want))) + " -->",
           "", f"## {a['title']}", ""]
    if tag == "ABSENT":
        out += [f"**could not look** — this run wrote no `{want}`, so this slide has nothing to "
                f"show and shows nothing. {reason}", ""]
    elif tag == UNGRADED:
        out += [f"**could not look** — {reason}.", ""]
    else:
        out += [f"**{WORD[tag]}** — {reason}", ""]
    if rows:
        out += ["```text", f"$ bash {a['script']}"] + wrap(rows, a.get("width", 104)) + ["```", ""]
    out += ["<!--", a["narration"], "-->", ""]
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
               "```text", tail, "```", "",
               # The bare count cannot tell a loosely coupled eco-system from one party testing
               # itself, so the deck says what the passes rest on and how many of the scripts
               # could ever pass on that runner. Computed from the quoted line, so the deck
               # cannot state a split the line does not carry (eco-system ticket 83).
               measured(tail), ""]
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
        elif s["kind"] == "aside":
            md += render_aside(s, capdir)
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
REFUSED_HEADING = "## Words a slide may not use"
EMPHASIS = re.compile(r"[*_`]")
SPACES = re.compile(r"\s+")


def flatten(s):
    """Slide text as a phrase lint should see it: lower case, markdown emphasis removed, runs of
    whitespace (newlines included) collapsed to one space.

    Not a nicety. `Deny is the *bottom* rung` is how the phrase last shipped on a slide
    (talk/deck-2026-07-31-superseded.md:149), and a literal substring list would have walked
    straight past it -- as would a phrase broken over two lines by the wrapper.

    Hyphens, dashes and slashes are whitespace here too (ticket 48 review F6). `deny-gate` is the
    same phrase as `deny gate` and is the next wrapper the refused phrase would plausibly wear;
    before this it passed as a review item rather than a red. Both sides are flattened, the slide
    text and the table's phrase cell, so the rule stays symmetric.
    """
    return SPACES.sub(" ", JOINERS.sub(" ", EMPHASIS.sub("", s.lower()))).strip()


def refused_phrases(root=ROOT):
    """The phrases a slide may not use, read out of CONTEXT.md's `## Words a slide may not use`
    table: [{phrase, instead, why}]. [] when the record carries no such table, which check()
    treats as a fault -- a lint with no list is not a lint.

    THE LIST LIVES IN THE RECORD, NOT HERE. Four phrases were hard-coded in this file from ticket
    47 until ticket 48, derived from nothing a reader could check and answerable to no decision;
    that is the defect class every review of this estate has found. Now the vocabulary record
    carries them with the entry or dated decision that refuses each one, and the checker follows
    the record. Adding a word to the lint is an edit to CONTEXT.md.
    """
    return _phrase_table(root)[0]


def _phrase_table(root=ROOT):
    """(rows, problems, declared) -- ONE parse of the table, three views of it.

    `problems` is ticket 48 review F3. A row that does not parse to three non-empty cells used to
    be SKIPPED in silence, so one stray `|` inside a row's own prose dropped that phrase from the
    lint while the table still read complete to a human -- a failure mode the python literal this
    replaced did not have, because a list in code cannot be truncated by punctuation. Measured:
    `| `deny gate` | the bottom rung | of the cage ladder, `isolated` |` left `deny gate` unlinted
    and a slide carrying it exited 0. Now the malformed line is named and red.

    `declared` is the row count the record states in its own prose, or None. Comparing it with the
    rows found makes DELETING a row a deliberate two-place edit rather than a silent one.
    """
    path = Path(root) / "CONTEXT.md"
    if not path.exists():
        return [], [], None
    rows, problems, declared, inside, fenced = [], [], None, False, False
    declarations = []
    for line in path.read_text(errors="replace").splitlines():
        if line.startswith("## "):
            if inside and fenced:
                problems.append("unclosed backtick fence in refused-vocabulary section")
            fenced = False
            inside = line.startswith(REFUSED_HEADING)
            continue
        if not inside:
            continue
        # A fenced block is quoted material and a `|` line is the table itself. The count is a
        # sentence a reader reads, so neither may set it (ticket 48 review R6): without this the
        # first match wins and a fenced example, or prose inside a cell, silently becomes the
        # declaration. Of the remaining matches NONE may silently win over another: comments,
        # quotations, tilde fences and indented examples count as ambiguous declarations too
        # (ticket 109). This conservative refusal avoids a second Markdown parser.
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced:
            continue
        if not line.lstrip().startswith("|"):
            declarations.extend(int(m.group(1)) for m in DECLARED_ROWS.finditer(line))
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        # The separator row is every cell made of nothing but `-` and `:`. It is not a row and is
        # not malformed. The header names its own columns and is skipped by name.
        if cells and all(c and set(c) <= set("-:") for c in cells):
            continue
        if len(cells) != 3 or not flatten(cells[0]):
            problems.append(line.strip())
            continue
        phrase = flatten(cells[0])
        if phrase == "refused on a slide":
            continue
        rows.append({"phrase": phrase, "instead": cells[1], "why": cells[2]})
    if inside and fenced:
        problems.append("unclosed backtick fence in refused-vocabulary section")
    if len(declarations) > 1:
        problems.append("multiple row-count declarations in refused-vocabulary section: "
                        + ", ".join(map(str, declarations)))
    if declarations:
        declared = declarations[0]
    return rows, problems, declared


def _body(sl):
    # Outside the figure check: the beat and deck markers (tags), headings, the
    # fence rules, the "$ bash <script>" line that names the command, and the
    # marp front matter / narrator comments a reader never sees on the slide.
    return "\n".join(l for l in sl.splitlines()
                     if not l.startswith("<!-- beat ") and not l.startswith("<!-- deck ")
                     and not l.startswith("<!-- aside ")
                     and not l.startswith("#")
                     and not l.strip().startswith("```") and not l.startswith("$ ")
                     and not l.strip().startswith("TRUTH ")
                     # `measured: ...` is the quoted TRUTH line read back through
                     # truth_manifest.measured(); check() requires it to equal that line's own
                     # split and ceiling exactly, which is a stronger rule than the figure
                     # check, and its figures come from the line, not from a presenter.
                     and not l.strip().startswith("measured: ")
                     # markdown image directives: `![w:900](path)` is layout, not a figure
                     and not l.strip().startswith("!["))


def parse(md):
    """Split a built deck into ([beats], [asides], [slide bodies with no capture behind them])."""
    slides = md.split("\n---\n")
    # slides[0] is the marp front matter (theme, paginate, the CSS font sizes).
    # It is machine configuration, never rendered as a slide, so it is outside
    # the figure check the same way a heading is.
    beats, asides, prose = [], [], []
    for sl in slides[1:]:
        m = MARKER_RE.search(sl)
        if m:
            beats.append((dict(p.split("=", 1) for p in m.group(1).split(" ")), _body(sl)))
            continue
        m = ASIDE_RE.search(sl)
        if m:
            asides.append((dict(p.split("=", 1) for p in m.group(1).split(" ")), _body(sl)))
            continue
        prose.append(_body(sl))
    return beats, asides, prose


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
    """(bad, review, cannot, beats, asides). Grades the deck against the run IT NAMES: a
    recorded run's captures come out of its recording commit; a disk deck is
    read against talk/captures/. Raises CouldNotLook when the named run's
    commit is unreachable, which is a could-not-look and not a grade.

    `cannot` is the second could-not-look, and the reason it is a list rather than an exception:
    an aside whose capture the run did not write is not a fault in the deck and not a fault in the
    estate, so it may not be red -- and it may not be green either, because a slide with nothing
    behind it went on the deck. The demo check exits 3 and prints these."""
    root = Path(root)
    md = Path(path).read_text()
    bad, review, cannot = [], [], []
    beats, asides, prose = parse(md)
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
                elif measured(line) not in md:
                    # Ticket 83: quoting the bare count is the thing the manifest exists to stop.
                    # The sentence is computed from the quoted line, so a deck that states a
                    # split the line does not carry, or states none at all, is caught here.
                    bad.append("the deck quotes the TRUTH line but not what it measured; the "
                               f"line's own split and ceiling read: {measured(line)}")
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
                # The same reading the renderer uses: the run's own grade where it recorded one.
                # These two used to be different readings of the same thing (the renderer moved to
                # the grade table in ticket 48 and this did not), which would have reddened every
                # beat whose capture ends mid-verdict.
                tag, _r, disagreement = resolved_grade(kv["script"], capture_lines(kv["script"], capdir), capdir)
                if tag != kv["status"]:
                    bad.append(f"step {step}: deck says {kv['status']}, {run_word} graded "
                               f"{kv['script']} {tag}")
                if disagreement:
                    bad.append(f"step {step}: {disagreement}")
                if tag == UNGRADED:
                    cannot.append(f"step {step}: {run_word} recorded no grade for {kv['script']}, "
                                  "so this check may not say the deck is whole")
                if kv["status"] in WORD and table.get(step) and table[step] != kv["status"]:
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

        # The asides (ticket 48). Graded exactly as a beat is -- the run's own grade, every
        # figure in its capture, the capture it names being the capture of the script it names --
        # and outside the seven-step ordering, because an aside is a read the demo makes and not
        # one of the seven steps the estate promises.
        for kv, body in asides:
            nm = kv.get("name", "?")
            if kv["cited"] == "yes":
                cap = capture_path(kv["script"], capdir)
                if kv["capture"] != "talk/captures/" + cap.name:
                    bad.append(f"aside {nm}: cites {kv['capture']}, which is not the capture of "
                               f"{kv['script']}")
                if not cap.exists():
                    bad.append(f"aside {nm}: cites a capture that is not in {run_word}: "
                               f"{kv['capture']}")
                    continue
                rows = capture_lines(kv["script"], capdir)
                tag, _r, disagreement = resolved_grade(kv["script"], rows, capdir)
                if tag != kv["status"]:
                    bad.append(f"aside {nm}: deck says {kv['status']}, {run_word} graded "
                               f"{kv['script']} {tag}")
                if disagreement:
                    bad.append(f"aside {nm}: {disagreement}")
                if tag == UNGRADED:
                    cannot.append(f"aside {nm}: {run_word} recorded no grade for {kv['script']}, "
                                  "so this check may not say the deck is whole")
                captured = set(figures(cap.read_text(errors="replace")))
                for f in figures(body):
                    if f not in captured:
                        bad.append(f"aside {nm}: figure '{f}' is on the slide but not in its capture")
            else:
                # No capture. The slide may claim nothing, may carry no figure, and must NAME the
                # file it wanted -- a blank space where a number was is the thing this forbids.
                if kv["status"] != "ABSENT":
                    bad.append(f"aside {nm}: a slide with no capture behind it claims {kv['status']}")
                if kv["capture"] != "-":
                    bad.append(f"aside {nm}: uncited slide still names a capture")
                for f in figures(body):
                    bad.append(f"aside {nm}: figure '{f}' on a slide with no capture behind it")
                want = kv.get("wanted", "")
                if not want or want not in body:
                    bad.append(f"aside {nm}: could not look, and does not name the capture it "
                               f"wanted ({want or 'the marker names none'}); a reader is owed the "
                               "file name, not a blank")
                else:
                    cannot.append(f"aside {nm}: {run_word} wrote no {want}, so the slide says it "
                                  "could not look and this check may not say the deck is whole")

    # Every figure on a NON-beat slide. The prose deliberately spells numbers
    # out as words, so the small rule is the right one: a figure off a beat has
    # no capture behind it and cannot be checked, so it may not be there at all.
    for body in prose:
        for f in figures(body):
            bad.append(f"a non-beat slide carries the figure '{f}'; only a beat slide may carry a "
                       "figure, because only a beat has a capture to check it against")

    refused, problems, declared = _phrase_table(root)
    for line in problems:
        if line.startswith(("multiple row-count declarations", "unclosed backtick fence")):
            bad.append("CONTEXT.md: " + line)
            continue
        bad.append("CONTEXT.md's `" + REFUSED_HEADING + "` table carries a row that does not parse "
                   "to three non-empty cells, so the phrase it names is not linted while the table "
                   f"still reads complete: {line}")
    # Both only when there IS a table. A record carrying no table at all gets the one fault
    # below, which says the whole thing; three messages for one absence would read as three
    # problems.
    if refused or problems:
        if declared is None:
            bad.append("CONTEXT.md's `" + REFUSED_HEADING + "` section states no row count, so a "
                       "deleted row would be a one-place edit nothing notices")
        elif declared != len(refused):
            bad.append(f"CONTEXT.md's `{REFUSED_HEADING}` section says it carries {declared} "
                       f"row(s) and the table parses to {len(refused)}")
    if not refused:
        bad.append("CONTEXT.md carries no `" + REFUSED_HEADING + "` table, so the phrase lint has "
                   "no list to apply; a lint whose list is derived from nothing is not a lint")
    flat = flatten(md)
    for row in refused:
        if row["phrase"] in flat:
            bad.append(f"phrase lint: '{row['phrase']}' is refused vocabulary — say instead: "
                       f"{row['instead']} (CONTEXT.md refuses it: {row['why']})")
    # The word `gate` on its own is a human review item and never a failure: the truth surface
    # keeps the name (ticket 03), ADR-0011 keeps `release gate`, and no word lint can tell which
    # sense a line means. Which senses ARE refused is the record's list above.
    for i, line in enumerate(md.splitlines(), 1):
        n = flatten(line)
        if "gate" in n and not any(r["phrase"] in n for r in refused):
            review.append(f"  line {i}: {line.strip()[:110]}")

    for s in quoted:
        if s not in truth_lines(root):
            bad.append("a quoted TRUTH line is not a line in talk/truth.log")

    return bad, review, cannot, beats, asides


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

        def observed(tag, line):
            """The run graded this script `tag` and wrote this capture. Both, together: a probe
            with a capture and no row in the run's grade table is UNGRADED, not graded off its
            last line, so a fixture that writes only the capture would be testing the fallback
            this file no longer has (ticket 48 review F1)."""
            probe.write_text(f"looked at a cluster\n{line}\n")
            (capdir / "_grades.tsv").write_text(f"{b4['script']}\t{tag}\t{line}\n")

        observed("FAIL", "FAIL: the cage is NOT in force")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("FAIL", True), (tag, cited)
        assert reason == "the cage is NOT in force", reason
        observed("SKIP", "SKIP: no Running pod to carry the cage")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("SKIP", True) and reason == "no Running pod to carry the cage"
        observed("PASS", "PASS: reconciled at the pinned revision")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == ("SKIP", True), (tag, cited)
        assert "reconciled at the pinned revision" in reason and "local build" in reason

        # ...and the same probe with its ROW taken away is a could-not-look that names the
        # script, never a grade read off the capture's last line. Both shapes: no table at all,
        # and a table with no row for this script.
        (capdir / "_grades.tsv").unlink()
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == (UNGRADED, True), (tag, cited)
        assert reason == NO_TABLE.format(script=b4["script"]), reason
        assert "**could not look**" in "\n".join(render_beat(b4, False, capdir))
        (capdir / "_grades.tsv").write_text("verify/somewhere/verify-else.sh\tPASS\tfine\n")
        tag, reason, _rows, cited = beat_status(b4, False, capdir)
        assert (tag, cited) == (UNGRADED, True), (tag, cited)
        assert reason == NO_ROW.format(script=b4["script"]), reason
        # ...and on a scheduled run, with the run's own PASS row back, the downgrade is gone.
        observed("PASS", "PASS: reconciled at the pinned revision")
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
    # ticket 96 put `enact=<mode>` between hub= and units=. The deck neither names nor grades
    # the mode -- it names a run and a hub -- so all that is asserted here is that the field
    # passes through the two readers the deck's provenance check compares against the marker.
    withmode = ("TRUTH 2026-09-06T00:00Z run=23 hub=eeeeeee enact=other-hand units=[] "
                "pass=1 fail=0 skip=0 excluded=0 total=1")
    assert (line_run(withmode), line_hub(withmode)) == ("23", "eeeeeee")

    # what the line measured (ticket 83): the sentence comes from the line, and its figures are
    # outside the figure check because check() pins them to the line exactly
    split = ("TRUTH 2026-09-05T00:00Z run=25 hub=ddddddd units=[] pass=2 [observed=1 self=1 "
             "simulated=0 meta=0] fail=0 skip=1 [never=1 waits=0] excluded=0 total=3 ceiling=2")
    assert "observed 1 + self 1" in measured(split) and "ceiling of 2 of 3" in measured(split)
    assert "carries no split" in measured(tl[2])
    assert figures(_body("measured: " + measured(split))) == []

    # --------------------------------------------------- the three seams of ticket 48
    # Each one is a defect this deck could carry and a reader could not see: a figure with no
    # capture behind it, a slide with nothing behind it at all, and a refused phrase. All three
    # are asserted end to end through check(), over a deck built by hand, because asserting the
    # helpers alone is how a checker passes while the file a reader opens is wrong (review
    # 2026-08-29, the same lesson).
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "talk" / "captures").mkdir(parents=True)
        def record(rows, count="There are 2 rows below."):
            (root / "CONTEXT.md").write_text(
                "# c\n\n" + REFUSED_HEADING + "\n\n" + count + "\n\n"
                "| refused on a slide | say instead | refused by |\n"
                "| --- | --- | --- |\n" + rows + "\n"
                "## Another section\n\n| this | is not | a refusal |\n")

        GOOD = ("| `deny is the bottom rung` | `isolated` is the bottom rung | ticket 89 |\n"
                "| `admission gate` | the mutating admission controller | ticket 75 Q5 |\n")
        record(GOOD)
        capdir = root / "talk" / "captures"
        (capdir / "verify_fx_verify-fx.out").write_text(
            "ok  priced 58,269.23 GBP\nPASS: two lines of verdict,\nand the second one.\n")
        (capdir / "_grades.tsv").write_text(
            "# a comment row\nverify/fx/verify-fx.sh\tPASS\tand the second one.\n")

        # the list comes off the record, in the record's order, and stops at the next heading
        assert [r["phrase"] for r in refused_phrases(root)] == ["deny is the bottom rung",
                                                               "admission gate"]
        assert refused_phrases(Path(tmp) / "nowhere") == []
        assert _phrase_table(root)[1:] == ([], 2)

        # F3, both halves. A row broken by one stray `|` inside its own prose is NAMED, not
        # dropped: before this it left the phrase unlinted while the table read complete.
        record("| `deny is the bottom rung` | `isolated` is the bottom rung of the cage | "
               "ladder | ticket 89 |\n"
               "| `admission gate` | the controller | ticket 75 Q5 |\n")
        rows, problems, _n = _phrase_table(root)
        assert [r["phrase"] for r in rows] == ["admission gate"], rows
        assert len(problems) == 1 and "deny is the bottom rung" in problems[0], problems
        # ...and an emptied phrase cell is the same fault.
        record("|  | `isolated` is the bottom rung | ticket 89 |\n" + GOOD)
        assert len(_phrase_table(root)[1]) == 1
        # A deleted row disagrees with the count the record states about itself.
        record("| `admission gate` | the mutating admission controller | ticket 75 Q5 |\n")
        rows, problems, declared = _phrase_table(root)
        assert (len(rows), problems, declared) == (1, [], 2)
        # A record that states no count at all is a fault of its own.
        record(GOOD, count="")
        assert _phrase_table(root)[2] is None
        record(GOOD)

        # F6: a hyphen is whitespace to the lint, so the refused phrase cannot wear one.
        assert flatten("This is the deny-gate for every workload.") == \
            "this is the deny gate for every workload."
        assert flatten("`deny gate`") == "deny gate"

        # the run's own grade, not the capture's last line. This capture is the Monte Carlo
        # capture's shape: a script that exited 0 whose last line is the second half of its
        # verdict, so the last-line reading calls it FAIL.
        rows = capture_lines("verify/fx/verify-fx.sh", capdir)
        assert grade(rows) == ("FAIL", NO_VERDICT)
        assert resolved_grade("verify/fx/verify-fx.sh", rows, capdir) == (
            "PASS", "two lines of verdict, and the second one.", None)
        # ... and the whole verdict block leaves the quoted body, not just its last line
        assert select(rows) == ["ok  priced 58,269.23 GBP"]
        # a disagreement is only reported when the last line has a verdict of its own to disagree
        (capdir / "verify_fx_verify-fx.out").write_text("ok  x\nFAIL: it did not\n")
        assert resolved_grade("verify/fx/verify-fx.sh",
                              capture_lines("verify/fx/verify-fx.sh", capdir), capdir)[2] \
            == ("the capture's own last line says FAIL and the run's grade table "
                "(talk/captures/_grades.tsv) says PASS")
        (capdir / "verify_fx_verify-fx.out").write_text(
            "ok  priced 58,269.23 GBP\nPASS: two lines of verdict,\nand the second one.\n")

        # the RENDERER's side of the same seam: an aside whose capture is not there renders as
        # could-not-look, names the file it wanted, claims nothing and cites nothing. Asserted
        # here as well as through check(), because a generator that emits a confident marker and
        # a checker that believes markers agree with each other and lie to the reader.
        a_gone = {"name": "clock", "title": "t", "script": "verify/gone/verify-gone.sh",
                  "absent": "nobody has run it here.", "narration": "n"}
        assert aside_status(a_gone, capdir) == ("ABSENT", "nobody has run it here.", [], False)
        rendered = "\n".join(render_aside(a_gone, capdir))
        assert "status=ABSENT cited=no" in rendered and "capture=- " in rendered
        assert "wanted=talk/captures/verify_gone_verify-gone.out" in rendered
        assert "could not look" in rendered and "nobody has run it here." in rendered
        assert "`talk/captures/verify_gone_verify-gone.out`" in rendered
        assert figures(_body(rendered)) == []
        # and one whose capture IS there carries the run's grade, not the last line's
        a_fx = {"name": "fx", "title": "t", "script": "verify/fx/verify-fx.sh",
                "absent": "no.", "narration": "n"}
        assert aside_status(a_fx, capdir)[:2] == ("PASS", "two lines of verdict, and the second one.")
        assert "status=PASS cited=yes" in "\n".join(render_aside(a_fx, capdir))

        deck = root / "d.md"

        def graded(*slides):
            steps = "".join(
                f"\n---\n\n<!-- beat step={i} status=NOCHECK cited=no "
                f"script=verify/e2e/verify-e2e-step{i}-x.sh capture=- -->\n\n"
                f"## {i} · x\n\n**no check yet, owned by ticket 1** — nothing\n"
                for i in range(1, 8))
            deck.write_text("---\nmarp: true\n---\n\n<!-- deck run=local hub=aaa source=disk -->"
                            "\n\n# t\n" + steps + "".join(slides))
            return check(deck, root)

        FX = ("<!-- aside name=fx status=PASS cited=yes script=verify/fx/verify-fx.sh "
              "capture=talk/captures/verify_fx_verify-fx.out "
              "wanted=talk/captures/verify_fx_verify-fx.out -->\n\n## fx\n\n"
              "**observed true** — two lines of verdict, and the second one.\n\n"
              "```text\nok  priced {}\n```\n")

        # (a) a figure on a slide that its capture does not carry
        bad, review, cannot, beats, asides = graded("\n---\n\n" + FX.format("58,269.23 GBP"))
        assert (bad, cannot, len(beats), len(asides)) == ([], [], 7, 1), (bad, cannot)
        bad, _r, cannot, _b, _a = graded("\n---\n\n" + FX.format("99,999.99 GBP"))
        assert bad == ["aside fx: figure '99,999.99' is on the slide but not in its capture"], bad
        assert cannot == []

        # (b) a slide whose capture the run did not write: named, never blank, never a pass, and
        # never red either -- an extra read the run did not produce is not a fault in the deck
        GONE = ("<!-- aside name=clock status={} cited=no script=verify/gone/verify-gone.sh "
                "capture=- wanted=talk/captures/verify_gone_verify-gone.out -->\n\n## clock\n\n"
                "**could not look** — this run wrote no `{}`, so nothing is shown.\n")
        bad, _r, cannot, _b, _a = graded(
            "\n---\n\n" + GONE.format("ABSENT", "talk/captures/verify_gone_verify-gone.out"))
        assert bad == [], bad
        assert cannot == ["aside clock: this run wrote no talk/captures/verify_gone_verify-gone.out"
                          ", so the slide says it could not look and this check may not say the "
                          "deck is whole"], cannot
        # ... and it may not quietly claim a grade, and may not leave the file unnamed
        bad, _r, _c, _b, _a = graded(
            "\n---\n\n" + GONE.format("PASS", "talk/captures/verify_gone_verify-gone.out"))
        assert bad == ["aside clock: a slide with no capture behind it claims PASS"], bad
        bad, _r, _c, _b, _a = graded("\n---\n\n" + GONE.format("ABSENT", "some other file"))
        assert bad == ["aside clock: could not look, and does not name the capture it wanted "
                       "(talk/captures/verify_gone_verify-gone.out); a reader is owed the file "
                       "name, not a blank"], bad

        # (c) the phrase lint, off the record, with emphasis stripped -- and the phrases the
        # decision ADMITS staying admitted
        bad, _r, _c, _b, _a = graded("\n---\n\n## x\n\nDeny is the *bottom* rung.\n")
        assert bad == ["phrase lint: 'deny is the bottom rung' is refused vocabulary — say "
                       "instead: `isolated` is the bottom rung (CONTEXT.md refuses it: "
                       "ticket 89)"], bad
        bad, review, _c, _b, _a = graded("\n---\n\n## x\n\nThe release gate and the honesty "
                                         "gate keep their names.\n")
        assert bad == [], bad
        assert len(review) == 1 and "release gate" in review[0], review
        # a record with no table at all is a fault: a lint derived from nothing is not a lint
        (root / "CONTEXT.md").write_text("# c\n\n## Nothing here\n")
        bad, _r, _c, _b, _a = graded("\n---\n\n" + FX.format("58,269.23 GBP"))
        assert bad == ["CONTEXT.md carries no `" + REFUSED_HEADING + "` table, so the phrase lint "
                       "has no list to apply; a lint whose list is derived from nothing is not a "
                       "lint"], bad

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
            bad, review, cannot, beats, asides = check(a.check)
        except CouldNotLook as e:
            print(f"could not look: {e}")
            return 3
        if review:
            n = len(refused_phrases())
            print(f"review, not a lint failure: the word gate appears on {len(review)} lines; "
                  f"every use outside the {n} phrases CONTEXT.md refuses is a human review item:")
            for r in review[:8]:
                print(r)
        for b in bad:
            print("  bad  " + b)
        for c in cannot:
            print("  could not look  " + c)
        print(f"checked {len(beats)} beats and {len(asides)} asides in {a.check}")
        # A fault outranks a could-not-look: a deck that is wrong is wrong whether or not another
        # slide had nothing to read.
        return 1 if bad else (3 if cannot else 0)

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
