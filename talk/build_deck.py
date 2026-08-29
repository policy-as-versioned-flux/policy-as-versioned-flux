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

Three statuses, and only three, on a beat:
  observed true / could not look / observed false   the gate's grade, from the
      capture's last line (the brief's contract: 'PASS: ', 'SKIP: ', 'FAIL: ').
  no check yet, owned by ticket NN                  generator-side. A step with
      no capture in this run. Never rendered as a gate grade.

  python3 talk/build_deck.py               write talk/deck.md
  python3 talk/build_deck.py --out PATH    write elsewhere (verify-demo.sh does)
  python3 talk/build_deck.py --check PATH  run the demo checks over a built deck
  python3 talk/build_deck.py --selfcheck   assert the four statuses render right
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALK = ROOT / "talk"
CAPDIR = TALK / "captures"
NARRATION = TALK / "narration.json"
TRUTHLOG = TALK / "truth.log"
ANSI = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

# The gate's grade word, keyed by the prefix its scripts put on their last line.
WORD = {"PASS": "observed true", "SKIP": "could not look", "FAIL": "observed false"}

# ponytail: build order. The deck is built from the captures on disk when the
# build runs. Inside a gate run, a script that sorts after verify/demo/ has not
# rewritten its capture yet, so its beat quotes the previous run's capture. That
# is why the deck says "built during run N" and not "run N produced every figure
# here", and why the scheduled workflow builds the committed deck AFTER
# verify-all.sh has finished rather than from inside it. Upgrade path: have
# verify-all.sh stamp its run id into each capture and assert it here.

# ponytail: the gate discards each script's exit code (it keeps only the
# capture), so the grade is read from the capture's last line, which the build
# brief makes the contract ("SKIP: <reason>" / "FAIL: <reason>"). If a script
# ever exits non-zero without saying so on its last line, the deck and the gate
# table disagree; verify-demo.sh catches that by cross-reading step 7's own
# verdict table, which is produced by a different script. Upgrade path: have
# verify-all.sh append its exit code to the capture, and read it here.


def slug(script):
    """The capture name verify-all.sh writes for a script path. Same rule."""
    s = script[2:] if script.startswith("./") else script
    return s.replace("/", "_")[:-3] if s.endswith(".sh") else s.replace("/", "_")


def capture_path(script):
    return CAPDIR / (slug(script) + ".out")


def capture_lines(script):
    txt = ANSI.sub("", capture_path(script).read_text(errors="replace"))
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


def hub_sha():
    try:
        return subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"],
                              capture_output=True, text=True, check=True).stdout.strip()
    except Exception:
        return "unknown"


def truth_tail():
    """The TRUTH line for THIS commit, or "" — never a stale one.

    2026-08-29 review: the headline quoted `run=5 hub=d4fcdb2 ... total=56` on a
    deck built at a different commit against 77 scripts, and said skip=0 while
    the deck itself showed two could-not-looks. The only assertion was that the
    quoted line existed somewhere in truth.log, so staleness was undetectable by
    construction. A number from another commit is not this deck's number.
    """
    if not TRUTHLOG.exists():
        return ""
    lines = [l.strip() for l in TRUTHLOG.read_text().splitlines() if l.strip().startswith("TRUTH ")]
    here = hub_sha()
    for line in reversed(lines):
        m = re.search(r"\bhub=(\S+)", line)
        if m and here != "unknown" and m.group(1).startswith(here[:7]):
            return line
    return ""


def run_id():
    """Which run this build belongs to. The scheduled CI run, or a local one."""
    r = os.environ.get("GITHUB_RUN_NUMBER", "").strip()
    return (r, True) if r else ("local", False)


def marker(**kw):
    return "<!-- beat " + " ".join(f"{k}={v}" for k, v in kw.items()) + " -->"


MARKER_RE = re.compile(r"<!-- beat (.*?) -->")


def beat_status(b, scheduled):
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
    cap = capture_path(b["script"])
    if not cap.exists():
        return ("NOCHECK", f"owned by ticket {b['ticket']}", [], False)
    rows = capture_lines(b["script"])
    tag, reason = grade(rows)
    if tag == "PASS" and b.get("scheduled_only") and not scheduled:
        reason = ("this step's capture is green here, but the number is quoted only from the "
                  "scheduled truth run, never from a presenter's laptop, and this is a local "
                  "build — so the deck does not show it green. The capture's own words: "
                  + reason)
        tag = "SKIP"
    return tag, reason, select(rows, grep=b.get("grep"), drop=b.get("drop"), limit=b.get("limit")), True


def render_beat(b, scheduled):
    tag, reason, rows, cited = beat_status(b, scheduled)
    cap = capture_path(b["script"])
    out = [marker(step=b["step"], status=tag, cited=("yes" if cited else "no"),
                  script=b["script"], capture=(str(cap.relative_to(ROOT)) if cited else "-")),
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


def build():
    narr = json.loads(NARRATION.read_text())
    run, scheduled = run_id()
    built = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
    tail = truth_tail()

    md = ["---", "marp: true", f"title: \"{narr['title']}\"", f"description: \"{narr['subtitle']}\"",
          "theme: default", "paginate: true",
          f"footer: \"generated by talk/build_deck.py · run={run} · hub={hub_sha()} · {built}\"",
          "style: |",
          "  section { font-size: 24px; }",
          "  section h1 { font-size: 44px; }",
          "  section h2 { font-size: 32px; }",
          "  pre { font-size: 13px; line-height: 1.35; }",
          "  code { font-size: 13px; }",
          "  img { max-height: 62vh; }",
          "---", "",
          "<!-- GENERATED FILE. Do not hand edit: talk/build_deck.py overwrites it from",
          "     talk/captures/ and talk/narration.json, and talk/verify-demo.sh grades the",
          "     deck it rebuilds, not the file you edited. Prose: talk/narration.json. -->", ""]

    # title slide
    md += [f"# {narr['title']}", "", f"### {narr['subtitle']}", "",
           f"built {built} during run **{run}** "
           f"({'a scheduled CI run' if scheduled else 'a local run, not the scheduled one'}) · hub `{hub_sha()}`. "
           "Each beat quotes the capture on disk for its own check, and carries the grade that capture gave.", ""]
    if tail:
        md += ["the truth surface's own recorded run at this commit, quoted from `talk/truth.log`:", "",
               "```text", tail, "```", ""]
    else:
        md += ["`talk/truth.log` records no run of the truth surface at this commit, so this deck "
               "quotes no headline number. The beats below carry their own grades, each read out "
               "of the capture named on the slide. An earlier run's line describes an earlier set "
               "of checks and is not comparable, so it is not shown.", ""]
    md += ["<!--", narr["opening"], "-->", ""]

    for s in narr["slides"]:
        md += ["---", ""]
        if s["kind"] == "prose":
            md += [f"## {s['title']}", ""] + s["body"] + ["", "<!--", s["narration"], "-->", ""]
        elif s["kind"] == "diagram":
            md += [f"## {s['title']}", "", f"![w:900]({s['image']})", "", s["caption"], "",
                   "<!--", s["narration"], "-->", ""]
        elif s["kind"] == "beat":
            md += render_beat(s, scheduled)
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
           re.compile(r"\brun[= ]\*{0,2}\S+?\*{0,2}(?=[ .·])"),
           re.compile(r"hub\s+`[0-9a-f]{7,40}`")]
BANNED = ["exemption", "hourglass", "admission gate", "deny gate"]


def _body(sl):
    # Outside the figure check: the beat marker (a tag), headings, the fence
    # rules, the "$ bash <script>" line that names the command, and the marp
    # front matter / narrator comments a reader never sees on the slide.
    return "\n".join(l for l in sl.splitlines()
                     if not l.startswith("<!-- beat ") and not l.startswith("#")
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


def step7_table(script="verify/e2e/verify-e2e-step7-honesty.sh"):
    """Steps' verdicts as a different script recorded them. Breaks the circle."""
    p = capture_path(script)
    if not p.exists():
        return {}
    out = {}
    for line in capture_lines(script):
        m = re.match(r"\s{2,}(\d)\s{2,}\S.*?\s(PASS|SKIP|FAIL)\s", line)
        if m:
            out[int(m.group(1))] = m.group(2)
    return out


def check(path):
    md = Path(path).read_text()
    bad, review = [], []
    beats, prose = parse(md)

    steps = [int(kv["step"]) for kv, _ in beats]
    if steps != sorted(steps) or steps != list(range(1, 8)):
        bad.append(f"beats are not the seven NORTH-STAR section 4 steps in order: {steps}")

    table = step7_table()
    for kv, body in beats:
        step = int(kv["step"])
        if kv["cited"] == "yes":
            cap = ROOT / kv["capture"]
            if not cap.exists():
                bad.append(f"step {step}: cites a capture that is not in this run: {kv['capture']}")
                continue
            tag, _ = grade(capture_lines(kv["script"]))
            if tag != kv["status"]:
                bad.append(f"step {step}: deck says {kv['status']}, this run's capture says {tag}")
            if table.get(step) and table[step] != kv["status"]:
                bad.append(f"step {step}: deck says {kv['status']}, the run's own honesty table says {table[step]}")
            # Set membership, not substring: '8,269.23' is a substring of the
            # capture's '58,269.23' and used to pass as a figure that appears
            # nowhere as a value. Any short run of digits was free the same way.
            captured = set(figures(capture_path(kv["script"]).read_text(errors="replace")))
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
            if kv["status"] == "NOCHECK" and (ROOT / kv["script"]).exists():
                bad.append(f"step {step}: {kv['script']} exists on disk but this run wrote no "
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

    here = hub_sha()
    for line in md.splitlines():
        s = line.strip()
        if not s.startswith("TRUTH "):
            continue
        if s not in TRUTHLOG.read_text():
            bad.append("a quoted TRUTH line is not a line in talk/truth.log")
        m = re.search(r"\bhub=(\S+)", s)
        if here != "unknown" and not (m and m.group(1).startswith(here[:7])):
            bad.append(f"a quoted TRUTH line was recorded at hub={m.group(1) if m else '?'}, not at "
                       f"this deck's own commit {here}: it counts a different set of checks and is "
                       "not this deck's number")

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

    # a step with no capture renders generator-side, never as a gate grade
    b = {"step": 9, "title": "t", "script": "verify/none/verify-nothing-here.sh",
         "ticket": "42", "narration": "n"}
    tag, reason, rows, cited = beat_status(b, True)
    assert (tag, reason, rows, cited) == ("NOCHECK", "owned by ticket 42", [], False)
    md = "\n".join(render_beat(b, True))
    assert "no check yet, owned by ticket 42" in md and "capture=-" in md
    body = "\n".join(l for l in md.splitlines()
                     if not l.startswith("<!-- beat ") and not l.startswith("#"))
    assert figures(body) == [], figures(body)

    # scheduled_only may downgrade a PASS and NOTHING else. A capture the gate
    # graded FAIL renders FAIL on a local build, cited, with its own reason.
    b4 = {"step": 4, "title": "t", "script": "verify/selfcheck/verify-scheduled-only-probe.sh",
          "ticket": "16", "narration": "n", "scheduled_only": True}
    probe = capture_path(b4["script"])
    probe.parent.mkdir(parents=True, exist_ok=True)
    try:
        probe.write_text("looked at a cluster\nFAIL: the cage is NOT in force\n")
        tag, reason, _rows, cited = beat_status(b4, False)
        assert (tag, cited) == ("FAIL", True), (tag, cited)
        assert reason == "the cage is NOT in force", reason
        probe.write_text("looked at a cluster\nSKIP: no Running pod to carry the cage\n")
        tag, reason, _rows, cited = beat_status(b4, False)
        assert (tag, cited) == ("SKIP", True) and reason == "no Running pod to carry the cage"
        probe.write_text("looked at a cluster\nPASS: reconciled at the pinned revision\n")
        tag, reason, _rows, cited = beat_status(b4, False)
        assert (tag, cited) == ("SKIP", True), (tag, cited)
        assert "reconciled at the pinned revision" in reason and "local build" in reason
        assert beat_status(b4, True)[0] == "PASS"
    finally:
        probe.unlink(missing_ok=True)

    # the figure check is set membership, not substring: 8,269.23 is inside
    # 58,269.23 and must not pass as a figure the capture carries
    assert "8,269.23" not in set(figures("residual 58,269.23"))

    # the figure check: a hand-typed figure with no capture behind it is caught
    assert figures("residual 58,269.23 and 40,000 GBP") == ["58,269.23", "40,000"]
    assert figures("built 2026-08-29 · step 4 · ticket 47 · ADR-0021 · Q2") == []
    print("selfcheck ok")


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--selfcheck":
        selfcheck()
    elif a and a[0] == "--check":
        bad, review, beats = check(a[1])
        if review:
            print(f"review, not a lint failure: the word gate appears on {len(review)} lines; "
                  "every use outside the four refused phrases is a human review item:")
            for r in review[:8]:
                print(r)
        for b in bad:
            print("  bad  " + b)
        print(f"checked {len(beats)} beats in {a[1]}")
        sys.exit(1 if bad else 0)
    else:
        out = Path(a[1]) if len(a) > 1 and a[0] == "--out" else TALK / "deck.md"
        text = build()
        out.write_text(text)
        print(f"{out}: {len(text.splitlines())} lines, {len(list(CAPDIR.glob('*.out')))} captures on disk")
