#!/usr/bin/env python3
"""Is the twin three adopters, or one adopter and two promises?

Eco-system ticket 64. REGRILL answer 39 promised a twin overlay for driftwood, tuppence and
ludlow. Ticket 29 was resolved on 2026-08-29 claiming all three and built one -- and no check in
the gate could tell the difference, because every twin check in the estate was driftwood's own,
run against driftwood, and `verify/e2e/verify-e2e-step5-twin-forecasts.sh` hardcoded driftwood as
its adopter. A set of checks that only ever looks at the adopter that HAS the artefact cannot
report the two that do not.

So this grader asks the question about the estate rather than about an adopter:

  1. WHICH parties claim the adopter role, read off their own signed party artefacts -- never a
     list typed in here, or a fourth adopter would have to be remembered rather than discovered.
  2. WHICH of them carry a twin overlay at all. One that does not is NAMED, and the verdict is
     could-not-look. That is the line ticket 64 asks the gate to print until the overlays exist.
  3. Whether the vendored world layer is the same layer everywhere. `twin/model.py Overlay.load`
     resolves `world_ref` on the same ModelRepo, so each adopter vendors the layer into its own
     tree; the emitter's staging mirror commits `world/` alone first, so identical bytes stage to
     an identical content-addressed commit in every repository. Two adopters pinning different
     refs therefore means one of them vendored something else -- observed false, not unlooked-at.
  4. Whether each overlay carries the six standing scenarios (decision ticket 11 answer item 4)
     and an emitter.

What it deliberately does NOT do: price anything, run any adopter's emitter, or re-derive any
adopter's own verdict. Each adopter's own two checks (`verify-twin-overlay.sh`,
`twin/verify-twin-scenarios.sh`) are run by the gate in their own repositories and consumed by
step 5. Re-implementing half of them here is how a hub check comes to pass while the repository
that owns the artefact fails, which is the shape ticket 64 exists to end.

Pure over a directory, so the rules are tested at this seam in `tests/test_twin_per_adopter.py`
and the estate is graded by `verify-twin-per-adopter.sh` beside this file.

    twin_per_adopter.py <estate-dir>   # grade an estate; prints lines, exits 0/1/3
    twin_per_adopter.py --selfcheck    # the rules, on planted directories, no estate needed
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

ADOPTER_ROLE = "adopter"
STANDING_SCENARIOS = 6  # decision ticket 11 answer item 4


def adopters(estate: Path) -> list[str]:
    """Every unit in the estate whose signed party artefact claims the adopter role.

    Derived rather than declared: an estate that gains a fourth adopter gains it here by
    publishing a party artefact, which is the only place the role is signed. A directory with no
    readable party.yaml is not a party and is skipped in silence -- `.git`, a scratch directory
    and a nested worktree all land in that case, and none of them is a claim about anything.
    """
    found = []
    for unit in sorted(p for p in estate.iterdir() if p.is_dir()):
        artefact = unit / "party.yaml"
        if not artefact.is_file():
            continue
        try:
            doc = yaml.safe_load(artefact.read_text()) or {}
        except yaml.YAMLError:
            continue
        if not isinstance(doc, dict):
            continue
        if ADOPTER_ROLE in (doc.get("roles") or []):
            found.append(str(doc.get("party") or unit.name))
    return found


def survey(estate: Path, org: str) -> dict:
    """What this adopter's tree actually carries. Counts and reads; judges nothing."""
    twin = estate / org / "twin"
    overlay = twin / "orgs" / org
    meta = overlay / "meta.yaml"
    world_ref = None
    if meta.is_file():
        try:
            world_ref = (yaml.safe_load(meta.read_text()) or {}).get("world_ref")
        except yaml.YAMLError:
            world_ref = None
    world = twin / "world"
    return {
        "org": org,
        "has_overlay": overlay.is_dir(),
        "scenarios": len(list((overlay / "scenarios").glob("*.yaml"))) if overlay.is_dir() else 0,
        "world_files": len([p for p in world.rglob("*.yaml")]) if world.is_dir() else 0,
        "world_ref": str(world_ref) if world_ref else None,
        "has_emitter": (twin / "emit-forward-intel.py").is_file(),
    }


def grade(surveys: list[dict]) -> tuple[str, list[tuple[str, str]]]:
    """The verdict and the lines behind it.

    FAIL beats SKIP beats PASS, the same precedence every check in this estate uses: an observed
    falsehood is the answer even when something else could not be looked at.
    """
    lines: list[tuple[str, str]] = []
    if not surveys:
        lines.append(("SKIP", "no party in this estate claims the adopter role, so there is no "
                              "adopter whose twin overlay could be looked at"))
        return "SKIP", lines

    present = [s for s in surveys if s["has_overlay"]]
    absent = [s["org"] for s in surveys if not s["has_overlay"]]

    for s in sorted(present, key=lambda s: s["org"]):
        org = s["org"]
        problems = []
        if s["scenarios"] != STANDING_SCENARIOS:
            problems.append("carries %d scenario files, not the six standing scenarios "
                            "decision ticket 11 answer item 4 asks for" % s["scenarios"])
        if not s["has_emitter"]:
            problems.append("has no twin/emit-forward-intel.py emitter")
        if not s["world_files"]:
            problems.append("vendors no world layer under twin/world/")
        if not s["world_ref"]:
            problems.append("pins no world_ref in its overlay meta.yaml")
        lines.append(("FAIL" if problems else "PASS",
                      "%s: an overlay with %d scenarios, %d vendored world files and world_ref %s"
                      % (org, s["scenarios"], s["world_files"], s["world_ref"])
                      + ("; " + "; ".join(problems) if problems else "")))

    refs = {s["world_ref"] for s in present if s["world_ref"]}
    if len(refs) > 1:
        lines.append(("FAIL",
                      "the adopters that carry an overlay pin %d different world_ref values (%s). "
                      "The vendored bytes are identical by construction and stage to one "
                      "content-addressed commit, so more than one means one of them vendored "
                      "something else" % (len(refs), ", ".join(sorted(refs)))))
    elif len(refs) == 1 and len(present) > 1:
        lines.append(("PASS",
                      "every one of the %d overlays vendors the same world layer, pinned at the "
                      "same content-addressed world_ref %s" % (len(present), refs.pop())))

    if absent:
        lines.append(("SKIP",
                      "%d of %d adopters carry no twin overlay and are named rather than omitted: "
                      "%s. REGRILL answer 39 promises one each; until they exist this check "
                      "cannot look at them, and it does not pass over the ones that are there"
                      % (len(absent), len(surveys), ", ".join(sorted(absent)))))
    else:
        lines.append(("PASS",
                      "%d of %d parties claiming the adopter role carry a twin overlay of their "
                      "own" % (len(present), len(surveys))))

    statuses = [s for s, _ in lines]
    return ("FAIL" if "FAIL" in statuses else "SKIP" if "SKIP" in statuses else "PASS"), lines


# -- the selfcheck ------------------------------------------------------------------------------


def _plant(root: Path, org: str, roles: list[str], **overlay) -> None:
    unit = root / org
    unit.mkdir(parents=True, exist_ok=True)
    (unit / "party.yaml").write_text("party: %s\nroles: [%s]\n" % (org, ", ".join(roles)))
    if not overlay:
        return
    twin = unit / "twin"
    (twin / "world").mkdir(parents=True, exist_ok=True)
    for i in range(int(overlay.get("world", 30))):
        (twin / "world" / ("w%d.yaml" % i)).write_text("id: w%d\n" % i)
    org_dir = twin / "orgs" / org
    (org_dir / "scenarios").mkdir(parents=True, exist_ok=True)
    for i in range(int(overlay.get("scenarios", STANDING_SCENARIOS))):
        (org_dir / "scenarios" / ("s%d.yaml" % i)).write_text("id: s%d\n" % i)
    (org_dir / "meta.yaml").write_text("world_ref: %s\n" % overlay.get("ref", "c2d0733"))
    if overlay.get("emitter", True):
        (twin / "emit-forward-intel.py").write_text("# emitter\n")


def selfcheck() -> int:
    """The rules, on planted directories. No estate, no network, no adopter's own script."""
    import tempfile

    cases = []
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)

        whole = root / "whole"
        for org in ("driftwood", "tuppence", "ludlow"):
            _plant(whole, org, ["adopter"], scenarios=6)
        _plant(whole, "platform", ["publisher"])
        cases.append(("three complete overlays and one publisher", whole, "PASS", "3 of 3"))

        one = root / "one"
        _plant(one, "driftwood", ["adopter"], scenarios=6)
        _plant(one, "tuppence", ["adopter"])
        _plant(one, "ludlow", ["adopter"])
        cases.append(("the state ticket 64 found: one overlay, two adopters without one",
                      one, "SKIP", "ludlow, tuppence"))

        split = root / "split"
        _plant(split, "driftwood", ["adopter"], ref="c2d0733")
        _plant(split, "tuppence", ["adopter"], ref="deadbee")
        cases.append(("two overlays vendoring different world layers", split, "FAIL", "world_ref"))

        thin = root / "thin"
        _plant(thin, "ludlow", ["adopter"], scenarios=4)
        cases.append(("an overlay short of the six standing scenarios", thin, "FAIL", "six"))

        naked = root / "naked"
        _plant(naked, "platform", ["publisher"])
        cases.append(("an estate with no adopter at all", naked, "SKIP", "adopter role"))

        bad = 0
        for label, estate, want, phrase in cases:
            status, lines = grade([survey(estate, o) for o in adopters(estate)])
            body = " | ".join(m for _, m in lines)
            ok = status == want and phrase in body
            print("%s: %s -> %s%s" % ("ok " if ok else "BAD", label, status,
                                      "" if ok else " (wanted %s containing %r)" % (want, phrase)))
            bad += 0 if ok else 1
    if bad:
        print("FAIL: %d selfcheck case(s) did not grade as written" % bad)
        return 1
    print("OK: twin_per_adopter selfcheck (pure rules on planted directories, no estate read)")
    return 0


def main(argv: list[str]) -> int:
    if "--selfcheck" in argv:
        return selfcheck()
    # `--list`: the adopter names, one per line and nothing else, so that
    # verify/e2e/verify-e2e-step5-twin-forecasts.sh can `mapfile` them instead of hardcoding
    # `driftwood` the way it did until 2026-09-04. Exit 3 when there is no adopter to list: an
    # empty list is a could-not-look, and a caller that read it as "no work to do" would print a
    # green line over an estate it never looked at.
    if argv[:1] == ["--list"]:
        if len(argv) != 2:
            print("usage: twin_per_adopter.py --list <estate-dir>")
            return 2
        estate = Path(argv[1])
        if not estate.is_dir():
            return 3
        names = adopters(estate)
        for name in names:
            print(name)
        return 0 if names else 3
    if len(argv) != 1:
        print("usage: twin_per_adopter.py <estate-dir> | --list <estate-dir> | --selfcheck")
        return 2
    estate = Path(argv[0])
    if not estate.is_dir():
        print("SKIP: %s is not a directory, so no estate could be read" % estate)
        return 3
    status, lines = grade([survey(estate, o) for o in adopters(estate)])
    for kind, message in lines:
        print("%s: %s" % (kind, message))
    print("TOTAL: %d pass, %d fail, %d could-not-look"
          % (sum(1 for k, _ in lines if k == "PASS"),
             sum(1 for k, _ in lines if k == "FAIL"),
             sum(1 for k, _ in lines if k == "SKIP")))
    return {"PASS": 0, "FAIL": 1, "SKIP": 3}[status]


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
