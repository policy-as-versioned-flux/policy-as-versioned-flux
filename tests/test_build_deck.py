"""talk/build_deck.py names the run it describes and is graded against that run
(eco-system ticket 66).

The deck used to be graded against "this run": whatever talk/captures/ held when
the check ran. The scheduled clock never rebuilds the deck (talk/deck.md is
outside the observation lane), so every scheduled run whose grades moved called
the committed deck stale. Now a deck names a recorded run, and its checks read
that run's captures out of the commit that recorded it, never off the disk.

The hub root is a parameter throughout, so these tests run against a throwaway
git repository with two recorded runs and never against the real truth.log.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import tempfile
from pathlib import Path

import pytest

_SPEC = importlib.util.spec_from_file_location(
    "build_deck", Path(__file__).resolve().parent.parent / "talk" / "build_deck.py")
assert _SPEC is not None and _SPEC.loader is not None
bd = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(bd)

STEP = "verify/e2e/verify-e2e-step{n}-x.sh"
HONESTY = "verify/e2e/verify-e2e-step7-honesty.sh"
ASIDE = "verify/tail/verify-tail-x.sh"
RUN1 = ("TRUTH 2026-09-01T09:41Z run=1 hub=aaaaaaa units=[driftwood=1111111] "
        "pass=5 fail=0 skip=2 excluded=0 total=7")
# run 2 carries ticket 96's `enact=` between hub= and units=, and run 1 does not: the deck is
# built and checked over a log holding both shapes, so the field cannot break the run the deck
# names and its absence cannot break the run before it.
RUN2 = ("TRUTH 2026-09-02T09:41Z run=2 hub=bbbbbbb enact=other-hand units=[driftwood=2222222] "
        "pass=4 fail=1 skip=2 excluded=0 total=7")
LOCAL = ("TRUTH 2026-09-02T12:00Z run=local hub=ccccccc units=[driftwood=2222222] "
         "pass=4 fail=1 skip=2 excluded=0 total=7")


# The fixture's own git runs with NO hooks. The owner's global config points core.hooksPath at a
# ggshield secret scan, which is a rate-limited network call on every commit; when its quota ran
# out on 2026-09-06 every commit here raised CalledProcessError and ten tests errored on the
# fixture rather than on anything under test (ticket 92 round 5, R2, which set this rule for every
# fixture and grader in the estate). The thing under test still reads the real global config:
# GIT_CONFIG_GLOBAL is never set, so a check that snapshots config still sees the truth.
_NO_HOOKS = tempfile.mkdtemp(prefix="build-deck-no-hooks-")


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t",
                           "-c", f"core.hooksPath={_NO_HOOKS}", *args],
                          capture_output=True, text=True, check=True).stdout.strip()


def _narration() -> dict:
    slides: list[dict] = [{"kind": "prose", "title": "How to read", "body": ["no figures here"],
                           "narration": "n"}]
    for n in range(1, 8):
        script = HONESTY if n == 7 else STEP.format(n=n)
        slides.append({"kind": "beat", "step": n, "title": f"step {n}", "script": script,
                       "ticket": "66", "narration": "n", "scheduled_only": n == 4})
        if n == 2:
            # eco-system ticket 48: a capture-reading slide that is not one of the seven steps,
            # so it sits between two of them and never in the step ordering
            slides.append({"kind": "aside", "name": "tail", "title": "the tail",
                           "script": ASIDE, "narration": "n",
                           "absent": "no run has looked at the tail here."})
    return {"title": "A deck", "subtitle": "of a named run", "opening": "o", "slides": slides}


def _captures(root: Path, grades: dict[int, str], residual: str) -> None:
    cap = root / "talk" / "captures"
    cap.mkdir(parents=True, exist_ok=True)
    rows = ["  #   step   verdict   why", "  --- ------ --------- ---"]
    for n in range(1, 8):
        script = HONESTY if n == 7 else STEP.format(n=n)
        tag = grades[n]
        body = f"residual {residual}\n{tag}: step {n} says so\n"
        (cap / (bd.slug(script) + ".out")).write_text(body)
        rows.append(f"  {n}   s{n}     {tag}      because")
    honesty = ("\n".join(rows)
               + f"\nresidual {residual}\n{grades[7]}: steps 1-6 each report one honest verdict\n")
    (cap / (bd.slug(HONESTY) + ".out")).write_text(honesty)
    # The aside's capture ends in the CONTINUATION of a two-line verdict, which is the shape that
    # made the last-line reading a proxy: the run graded this script PASS and the last line reads
    # back FAIL. 30 of run 186's 120 real captures have it.
    (cap / (bd.slug(ASIDE) + ".out")).write_text(
        f"residual {residual}\nPASS: the tail is named,\nand the sentence wraps.\n")
    table = ["# talk/captures/_grades.tsv", "# " + "x"]
    for n in range(1, 8):
        script = HONESTY if n == 7 else STEP.format(n=n)
        table.append(f"{script}\t{grades[n]}\tlast line")
    table.append(f"{ASIDE}\tPASS\tand the sentence wraps.")
    (cap / "_grades.tsv").write_text("\n".join(table) + "\n")


def _record(root: Path, line: str, grades: dict[int, str], residual: str) -> str:
    """One lane commit: a TRUTH line appended beside the captures of that run."""
    _captures(root, grades, residual)
    with (root / "talk" / "truth.log").open("a") as fh:
        fh.write(line + "\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", f"truth: record {bd.line_run(line)}")
    return _git(root, "rev-parse", "HEAD")


GRADES1 = {1: "PASS", 2: "PASS", 3: "PASS", 4: "PASS", 5: "SKIP", 6: "SKIP", 7: "PASS"}
GRADES2 = {1: "FAIL", 2: "PASS", 3: "PASS", 4: "PASS", 5: "SKIP", 6: "SKIP", 7: "PASS"}


@pytest.fixture()
def hub(tmp_path: Path) -> dict:
    root = tmp_path / "hub"
    (root / "talk").mkdir(parents=True)
    _git(root, "init", "-q")
    (root / "talk" / "narration.json").write_text(json.dumps(_narration()))
    # The refused-phrase list lives in the vocabulary record and the checker reads it there
    # (eco-system ticket 48), so a hub with no record has no lint and check() says so.
    (root / "CONTEXT.md").write_text(
        "# c\n\n" + bd.REFUSED_HEADING + "\n\n"
        "| refused on a slide | say instead | refused by |\n| --- | --- | --- |\n"
        "| `deny is the bottom rung` | `isolated` is the bottom rung | ticket 89 |\n")
    (root / "talk" / "truth.log").write_text("")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "narration")
    lane1 = _record(root, RUN1, GRADES1, "40,000")
    lane2 = _record(root, RUN2, GRADES2, "58,269.23")
    # a local run's line is recorded too, and must never be nameable: its
    # captures were never committed
    with (root / "talk" / "truth.log").open("a") as fh:
        fh.write(LOCAL + "\n")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "a local line, no captures")
    # HEAD is not a lane commit, and the disk captures are NOT any recorded run's:
    # exactly the state a laptop is in after a local gate run
    _captures(root, {n: "SKIP" for n in range(1, 8)}, "1")
    return {"root": root, "lane1": lane1, "lane2": lane2}


def test_the_newest_recorded_run_is_the_newest_numbered_line(hub: dict) -> None:
    assert bd.recorded_run("newest", hub["root"]) == RUN2
    assert bd.recorded_run("1", hub["root"]) == RUN1
    assert bd.recorded_run(2, hub["root"]) == RUN2
    assert bd.recorded_run("local", hub["root"]) == ""
    assert bd.recorded_run("9", hub["root"]) == ""


def test_run_commit_is_the_lane_commit_whose_newest_line_is_that_run(hub: dict) -> None:
    assert bd.run_commit(1, hub["root"]) == hub["lane1"]
    assert bd.run_commit(2, hub["root"]) == hub["lane2"]
    assert bd.run_commit(9, hub["root"]) is None


def test_captures_are_read_from_the_recording_commit_not_the_disk(hub: dict, tmp_path: Path) -> None:
    capdir = bd.export_captures(hub["lane1"], tmp_path / "x", hub["root"])
    step1 = (capdir / (bd.slug(STEP.format(n=1)) + ".out")).read_text()
    assert "PASS: step 1" in step1 and "40,000" in step1
    on_disk = (hub["root"] / "talk" / "captures" / (bd.slug(STEP.format(n=1)) + ".out")).read_text()
    assert "SKIP: step 1" in on_disk


def test_a_named_deck_carries_that_runs_grades_line_and_hub(hub: dict) -> None:
    md = bd.build(run="newest", root=hub["root"])
    name = bd.deck_name(md)
    assert name == {"run": "2", "hub": "bbbbbbb", "source": "recorded"}
    assert RUN2 in md and RUN1 not in md
    beats, asides, _prose = bd.parse(md)
    assert [kv["status"] for kv, _ in beats] == [GRADES2[n] for n in range(1, 8)]
    # the aside carries the run's own grade for its script, out of that run's grade table, and
    # NOT the FAIL its capture's last line reads back
    assert [(kv["name"], kv["status"], kv["cited"]) for kv, _ in asides] == [("tail", "PASS", "yes")]
    assert "the tail is named, and the sentence wraps." in md
    # a recorded run is the scheduled run, so scheduled_only never downgrades it
    assert "58,269.23" in md and "residual 1\n" not in md


def test_a_disk_deck_names_no_recorded_run_and_quotes_no_line(hub: dict, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_RUN_NUMBER", raising=False)
    md = bd.build(root=hub["root"])
    assert bd.deck_name(md)["source"] == "disk" and bd.deck_name(md)["run"] == "local"
    assert "TRUTH " not in md
    beats, asides, _prose = bd.parse(md)
    # what the disk holds is a local run's SKIPs, all seven of them
    assert [kv["status"] for kv, _ in beats] == ["SKIP"] * 7
    assert [kv["status"] for kv, _ in asides] == ["PASS"]


def test_the_check_grades_the_run_the_deck_names_not_the_disk(hub: dict, tmp_path: Path) -> None:
    # run 1 is older than HEAD's newest line, and the disk holds neither run:
    # the false red the ticket exists to remove
    p = tmp_path / "deck1.md"
    p.write_text(bd.build(run=1, root=hub["root"]))
    bad, _review, cannot, beats, asides = bd.check(p, root=hub["root"])
    assert bad == [] and cannot == [] and len(beats) == 7 and len(asides) == 1
    p2 = tmp_path / "deck2.md"
    p2.write_text(bd.build(run=2, root=hub["root"]))
    assert bd.check(p2, root=hub["root"])[0] == []


def test_a_hand_edited_status_or_figure_is_refused_against_the_named_run(hub: dict, tmp_path: Path) -> None:
    md = bd.build(run=2, root=hub["root"])
    p = tmp_path / "deck.md"
    p.write_text(md.replace("beat step=1 status=FAIL", "beat step=1 status=PASS", 1)
                 .replace("**observed false** — step 1 says so", "**observed true** — step 1 says so", 1))
    bad = bd.check(p, root=hub["root"])[0]
    assert any("step 1: deck says PASS" in b and "run 2" in b for b in bad), bad
    p.write_text(md.replace("residual 58,269.23", "residual 99,999.99", 1))
    bad = bd.check(p, root=hub["root"])[0]
    assert any("99,999.99" in b for b in bad), bad


def test_a_deck_naming_a_run_the_log_does_not_record_is_refused(hub: dict, tmp_path: Path) -> None:
    md = bd.build(run=2, root=hub["root"])
    p = tmp_path / "deck.md"
    p.write_text(md.replace("<!-- deck run=2 hub=bbbbbbb", "<!-- deck run=9 hub=bbbbbbb", 1))
    bad = bd.check(p, root=hub["root"])[0]
    assert any("run 9" in b and "records no" in b for b in bad), bad
    # a quoted line from another run than the named one
    p.write_text(md.replace(RUN2, RUN1, 1))
    bad = bd.check(p, root=hub["root"])[0]
    assert any("quoted TRUTH line" in b for b in bad), bad
    # a disk deck may quote nothing
    disk = bd.build(root=hub["root"]).replace("<!--\no\n-->", f"```text\n{RUN2}\n```\n<!--\no\n-->", 1)
    p.write_text(disk)
    bad = bd.check(p, root=hub["root"])[0]
    assert any("not recorded" in b for b in bad), bad


def test_an_unreachable_recording_commit_is_a_could_not_look(hub: dict, tmp_path: Path) -> None:
    root = hub["root"]
    line3 = RUN2.replace("run=2", "run=3").replace("hub=bbbbbbb", "hub=ddddddd")
    with (root / "talk" / "truth.log").open("a") as fh:
        fh.write(line3 + "\n")   # recorded in the log, but no commit carries it
    with pytest.raises(bd.CouldNotLook, match="run 3"):
        bd.build(run=3, root=root)
    md = bd.build(run=2, root=root)
    p = tmp_path / "deck.md"
    p.write_text(md.replace("<!-- deck run=2 hub=bbbbbbb", "<!-- deck run=3 hub=ddddddd", 1)
                 .replace(RUN2, line3, 1))
    with pytest.raises(bd.CouldNotLook, match="run 3"):
        bd.check(p, root=root)
    bd.recorded_run("newest", root) == line3


def test_a_recorded_run_cannot_be_local(hub: dict) -> None:
    with pytest.raises(SystemExit):
        bd.build(run="local", root=hub["root"])


def test_an_aside_whose_capture_the_run_never_wrote_is_a_could_not_look(
        hub: dict, tmp_path: Path) -> None:
    """Eco-system ticket 48. The seven steps are what the estate promises and a missing capture
    for one is red. An aside is an extra read: the slide names the file the run did not write,
    claims nothing, carries no figure, and the check may say neither pass nor fail about it."""
    root = hub["root"]
    narr = json.loads((root / "talk" / "narration.json").read_text())
    for slide in narr["slides"]:
        if slide.get("kind") == "aside":
            slide["script"] = "verify/nowhere/verify-nowhere-x.sh"
    (root / "talk" / "narration.json").write_text(json.dumps(narr))

    md = bd.build(run=2, root=root)
    want = "talk/captures/" + bd.slug("verify/nowhere/verify-nowhere-x.sh") + ".out"
    assert "status=ABSENT cited=no" in md and f"wanted={want}" in md
    assert "could not look" in md and f"`{want}`" in md
    assert "no run has looked at the tail here." in md

    p = tmp_path / "deck.md"
    p.write_text(md)
    bad, _review, cannot, beats, asides = bd.check(p, root=root)
    assert bad == [], bad
    assert len(beats) == 7 and len(asides) == 1
    assert cannot == [f"aside tail: run 2 wrote no {want}, so the slide says it could not look "
                      "and this check may not say the deck is whole"], cannot


def test_a_hub_whose_record_carries_no_refused_table_has_no_lint(hub: dict, tmp_path: Path) -> None:
    """The phrase list is read from CONTEXT.md and lives nowhere else, so a record without the
    table is a fault rather than a silently empty lint (eco-system ticket 48)."""
    root = hub["root"]
    assert [r["phrase"] for r in bd.refused_phrases(root)] == ["deny is the bottom rung"]
    p = tmp_path / "deck.md"
    p.write_text(bd.build(run=2, root=root))
    assert bd.check(p, root=root)[0] == []

    # the phrase itself, in the shape it last shipped in: emphasis is stripped before matching
    p.write_text(bd.build(run=2, root=root) + "\n---\n\n## x\n\nDeny is the *bottom* rung.\n")
    bad = bd.check(p, root=root)[0]
    assert any("'deny is the bottom rung' is refused vocabulary" in b
               and "`isolated` is the bottom rung" in b for b in bad), bad

    (root / "CONTEXT.md").write_text("# c\n\n## No table here\n")
    p.write_text(bd.build(run=2, root=root))
    bad = bd.check(p, root=root)[0]
    assert bad == [f"CONTEXT.md carries no `{bd.REFUSED_HEADING}` table, so the phrase lint has "
                   "no list to apply; a lint whose list is derived from nothing is not a lint"], bad
