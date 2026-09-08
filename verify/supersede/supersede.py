#!/usr/bin/env python3
"""supersede.py — eco-system ticket 84 made checkable: being behind costs something.

## What is measured, and against what

| | served artefact | operation that reaches it |
|---|---|---|
| the adopter's feed pins | its own `party.yaml` at the commit it SERVES | `git fetch origin main`, then `git show origin/main:party.yaml` |
| the prices it signs | its own `composed/evidence.json` at that commit | `git show origin/main:composed/evidence.json` |
| the composer that wrote them | platform's tree AT THE TAG THIS ADOPTER PINS | `gitops/platform/platform-pin.yaml` at that commit, then `git -C platform show <tag>:compose/composition.py` |
| what the publisher has published | the publisher's REAL remote tag namespace | `git ls-remote --tags` (feed_contract.remote_tags) |
| when the newer major was signed | the tag object, fetched read-only into the publisher clone | `git fetch origin tag <tag>`, then `for-each-ref --format=%(creatordate:short)` |
| the retirement proposals | the adopter's pull requests on `wargamer/retire-*` branches | `gh pr list --state all` |

Never HEAD, never a working tree, never platform's main (review F7 of ticket 45; the rule
verify/portability applies for the same reason). A unit that cannot be fetched, a remote that
cannot be reached, a tag that cannot be read, is a could-not-look naming the reason.

## The sentences graded, per adopter feed pin

1. BEHIND: the pin's major is older than the newest major the publisher's remote carries a tag
   for. Then the served evidence must carry one `supersede` line for that pin -- under the
   adopter's own perspective and reporting currency, `newer.tag` the tag the remote actually
   carries, `since` the day that tag was cut (read off the fetched tag object), `ramp` the EOL
   ramp from `since` to the entry's own `as_of` (restated here: 1 + min(years past, 4), never
   below 1.0 -- the hub is not a party and pins no platform, so the formula is restated as
   verify/priced-holes restates it, not imported), and `amount = base x (ramp - 1)` with `base`
   the feed line's own amount. A line missing or wrong is a FAIL -- unless the composer the
   adopter pins carries no supersede rule at all, which is a could-not-look naming the tag: no
   edit of the adopter's own could put the line there.
2. UNTAGGED: no tag of the pin's form on the remote. Counted here as a number ("untagged-feed
   holes carried: k of n"); the hole itself is graded by verify-untagged-pin-is-priced.sh, one
   grader per fact.
3. CURRENT: the pin is at the newest tagged major. Nothing to price; said by name.

The retirement proposals are COUNTED, never graded: opened is the clock's, merged is a human's,
and this check reads the number off GitHub and prints it (0/0 today). Whether a retirement PR
SHOULD exist waits on the clock having run after a composer that prices the supersede line.

## What it refuses to grade, said plainly

* whether a tag on the remote VERIFIES under the publisher's identity pins -- that is
  verify-untagged-pin-is-priced.sh's claim, with the identity-pinned verifier; here a tag on the
  remote is "tagged", in that word;
* the untagged hole's amount and shape (above);
* the eol feed's own time-varying price, which is composition's own selfcheck's seam.

Usage:
    supersede.py check        # every adopter in .estate-clone/ (PAVC_ESTATE_CLONE overrides)
    supersede.py selfcheck    # planted grades: proves each verdict bites
"""
from __future__ import annotations

import importlib.util
import json
import os
import re
import subprocess
import sys
from typing import Any

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
ESTATE = os.environ.get("PAVC_ESTATE_CLONE") or os.path.normpath(os.path.join(ROOT, ".estate-clone"))
SERVED_REF = "origin/main"
PLATFORM_PIN = "gitops/platform/platform-pin.yaml"
COMPOSER = "compose/composition.py"
RULE_TOKEN = "def price_supersede("
RETIRE_PREFIX = "wargamer/retire-"
SUPERSEDE_KIND = "supersede"
OPEN = ("new", "recorded")
LINES: list[str] = []
MESSAGES: list[str] = []


def _feed_contract() -> Any:
    spec = importlib.util.spec_from_file_location(
        "feed_contract", os.path.join(ROOT, "verify", "feed-contract", "feed_contract.py"))
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def out(status: str, msg: str) -> None:
    LINES.append(status)
    MESSAGES.append(msg)
    print(f"{status}: {msg}")


# --------------------------------------------------------------------------
# reads -- every one of a served ref, never a working tree
# --------------------------------------------------------------------------
def git(repo: str, *args: str) -> tuple[int, str]:
    done = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return done.returncode, (done.stdout if done.returncode == 0 else done.stderr).strip()


def show(repo: str, ref: str, path: str) -> str | None:
    rc, text = git(repo, "show", f"{ref}:{path}")
    return text if rc == 0 else None


def fetch(repo: str, refspec: str) -> str | None:
    done = subprocess.run(["git", "-C", repo, "fetch", "--quiet", "origin", refspec],
                          capture_output=True, text=True, timeout=120)
    return None if done.returncode == 0 else (done.stderr.strip().splitlines() or ["fetch failed"])[-1]


def fetch_served(repo: str) -> str | None:
    return fetch(repo, f"+refs/heads/main:refs/remotes/{SERVED_REF}")


def tag_date(repo: str, tag: str) -> str | None:
    """The day `tag` was cut, off the tag object fetched read-only into the publisher's clone.
    None where it cannot be fetched or is not an annotated tag object."""
    if fetch(repo, f"+refs/tags/{tag}:refs/tags/{tag}"):
        return None
    rc, text = git(repo, "for-each-ref", "--format=%(objecttype) %(creatordate:short)",
                   f"refs/tags/{tag}")
    if rc != 0 or not text:
        return None
    kind, date = (text.split() + ["", ""])[:2]
    return date if kind == "tag" and date else None


def served_yaml(repo: str, path: str) -> dict | None:
    text = show(repo, SERVED_REF, path)
    if text is None:
        return None
    doc = yaml.safe_load(text)
    return doc if isinstance(doc, dict) else None


def served_json(repo: str, path: str) -> dict | None:
    text = show(repo, SERVED_REF, path)
    if text is None:
        return None
    try:
        doc = json.loads(text)
    except ValueError:
        return None
    return doc if isinstance(doc, dict) else None


def served_platform_tag(repo: str) -> str | None:
    text = show(repo, SERVED_REF, PLATFORM_PIN)
    if text is None:
        return None
    for doc in yaml.safe_load_all(text):
        if isinstance(doc, dict) and doc.get("kind") == "GitRepository":
            tag = ((doc.get("spec") or {}).get("ref") or {}).get("tag")
            if tag:
                return str(tag)
    return None


def composer_carries_rule(estate: str, tag: str) -> bool | None:
    """Does platform's composer AT THE TAG THE ADOPTER PINS know the supersede rule? None
    where the tag cannot be read here."""
    platform = os.path.join(estate, "platform")
    text = show(platform, tag, COMPOSER)
    if text is None:
        if fetch(platform, f"+refs/tags/{tag}:refs/tags/{tag}"):
            return None
        text = show(platform, tag, COMPOSER)
    return None if text is None else RULE_TOKEN in text


def adopters(estate: str) -> list[str]:
    """Every unit whose SERVED party.yaml claims the adopter role; a unit that cannot be fetched
    is named and left ungraded."""
    found: list[str] = []
    for name in sorted(os.listdir(estate)) if os.path.isdir(estate) else []:
        repo = os.path.join(estate, name)
        if not os.path.exists(os.path.join(repo, ".git")):
            continue
        reason = fetch_served(repo)
        if reason:
            out("SKIP", f"could not fetch {SERVED_REF} for {name} ({reason}), so what it serves "
                        f"could not be read")
            continue
        doc = served_yaml(repo, "party.yaml")
        if doc and "adopter" in (doc.get("roles") or []):
            found.append(name)
    return found


# --------------------------------------------------------------------------
# pure pieces, so selfcheck can plant
# --------------------------------------------------------------------------
def pinned_major(version: str) -> int | None:
    digits = re.match(r"v?(\d+)", str(version or ""))
    return int(digits.group(1)) if digits else None


def newest_tagged_major(name: str, tags: set[str]) -> tuple[int | None, str | None]:
    """(major, tag) of the highest tag of this feed's form on the remote: `<name>/vX.Y.Z` or bare
    `vX.Y.Z`, the two shapes feed_contract.tag_forms admits. (None, None) where none exists."""
    shape = re.compile(rf"^(?:{re.escape(name)}/)?v(\d+)\.(\d+)\.(\d+)$")
    hits = [(tuple(int(g) for g in m.groups()), t) for t in tags for m in [shape.match(t)] if m]
    if not hits:
        return None, None
    key, tag = max(hits)
    return key[0], tag


def eol_ramp(since: str, as_of: str) -> float:
    """platform/feeds/to_fair_scenario.py's ramp, restated: 1.0 up to `since`, then +1x per
    year, capped at +4x. Whole days off the two YYYY-MM-DD strings."""
    import datetime as dt
    days = (dt.date.fromisoformat(as_of) - dt.date.fromisoformat(since)).days
    return 1.0 if days <= 0 else 1.0 + min(days / 365.0, 4.0)


def close(a: float, b: float) -> bool:
    return abs(a - b) <= 1e-6 * max(1.0, abs(a), abs(b))


def edge_entry(evidence: dict | None, party: str, name: str) -> dict | None:
    for e in (evidence or {}).get("prices") or []:
        if e.get("kind") in ("feed", "premium") and e.get("source") == party and e.get("name") == name:
            return e
    return None


def supersede_line(evidence: dict | None, party: str, name: str) -> dict | None:
    for e in (evidence or {}).get("prices") or []:
        if e.get("kind") == SUPERSEDE_KIND and e.get("source") == party and e.get("name") == name:
            return e
    return None


def grade_behind(*, adopter: str, currency: str, party: str, name: str, version: str,
                 newest_major: int, newest_tag: str, tagged: str | None, line: dict | None,
                 entry: dict | None, rule: bool | None, platform_tag: str | None) -> tuple[str, str]:
    """One (status, message) for a pin that is BEHIND a newer tagged major."""
    label = (f"{adopter} pins {party}/feed/{name}@{version}, behind v{newest_major} "
             f"({newest_tag} on {party}'s real remote)")
    if line is None:
        if rule is False:
            return "SKIP", (f"{label}: composed under platform {platform_tag}, which carries no "
                            f"supersede rule, so no edit of {adopter}'s own could put the line "
                            f"there -- it waits on a platform tag carrying the rule and a pin bump")
        if rule is None:
            return "SKIP", (f"{label}: could not read platform tag {platform_tag!r} here, so whether "
                            f"the composer that wrote this evidence carries the supersede rule is "
                            f"unobserved")
        return "FAIL", (f"{label}: the composer it pins ({platform_tag}) carries the supersede rule "
                        f"and the served evidence carries no supersede line for it -- being behind "
                        f"is priced, never free (ticket 84, ticket 13 D5)")
    problems: list[str] = []
    if line.get("perspective") != adopter or line.get("currency") != currency:
        problems.append(f"under {line.get('perspective')}/{line.get('currency')}, not {adopter}/{currency}")
    newer = line.get("newer") or {}
    if newer.get("tag") != newest_tag:
        problems.append(f"names newer tag {newer.get('tag')!r}, the remote's newest is {newest_tag}")
    if tagged is None:
        return "SKIP", f"{label}: could not fetch tag {newest_tag} from {party} to read the day it was cut"
    if line.get("since") != tagged or newer.get("tagged") != tagged:
        problems.append(f"since {line.get('since')!r} is not the day {newest_tag} was cut ({tagged})")
    as_of = line.get("as_of")
    try:
        want_ramp = eol_ramp(tagged, str(as_of)) if as_of else 1.0
    except ValueError:
        want_ramp = -1.0
    base, amount, ramp = line.get("base"), line.get("amount"), line.get("ramp")
    numeric = all(isinstance(x, (int, float)) and not isinstance(x, bool) for x in (base, amount, ramp))
    if not numeric:
        problems.append(f"carries base {base!r}, ramp {ramp!r}, amount {amount!r}: not a priced line")
    else:
        assert isinstance(base, (int, float)) and isinstance(amount, (int, float)) and isinstance(ramp, (int, float))
        if want_ramp < 0 or not close(float(ramp), want_ramp):
            problems.append(f"ramp {ramp} is not eol_ramp({tagged}, {as_of}) = {want_ramp:.6f}")
        if not close(float(amount), float(base) * (float(ramp) - 1.0)):
            problems.append(f"amount {amount} is not base {base} x (ramp {ramp} - 1)")
        if entry is not None and isinstance(entry.get("amount"), (int, float)) \
                and not close(float(base), float(entry["amount"])):
            problems.append(f"base {base} is not the feed line's own amount {entry['amount']}")
    if problems:
        return "FAIL", f"{label}: the supersede line " + "; ".join(problems)
    assert isinstance(amount, (int, float)) and isinstance(ramp, (int, float)) \
        and isinstance(base, (int, float))
    return "PASS", (f"{label}: priced {amount:,.2f} {currency} under {adopter}'s own perspective "
                    f"as of {as_of} (ramp {ramp:.4f} since {tagged}, the day {newest_tag} was cut, "
                    f"on the line's own {float(base):,.2f})")


def retirement_prs(unit: str) -> tuple[int, int] | None:
    """(opened, merged) retirement proposals on the unit's real repository, or None when gh
    could not answer. Opened counts every PR ever on a wargamer/retire-* branch, merged the
    subset a human merged."""
    repo = f"policy-as-versioned-{unit}/{unit}"
    try:
        done = subprocess.run(["gh", "pr", "list", "--repo", repo, "--state", "all", "--limit", "100",
                               "--json", "number,headRefName,mergedAt"],
                              capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    if done.returncode != 0:
        return None
    try:
        prs = json.loads(done.stdout or "[]")
    except ValueError:
        return None
    retire = [p for p in prs if str(p.get("headRefName", "")).startswith(RETIRE_PREFIX)]
    return len(retire), sum(1 for p in retire if p.get("mergedAt"))


# --------------------------------------------------------------------------
# the estate
# --------------------------------------------------------------------------
def check(estate: str = ESTATE) -> int:
    fc = _feed_contract()
    if not os.path.isdir(estate):
        out("SKIP", f"no estate at {estate} (run clone-estate.sh)")
        return exit_code()
    behind = 0
    carried = 0
    untagged = 0
    holes = 0
    pins = 0
    opened_total = merged_total = 0
    pr_unknown: list[str] = []
    names = adopters(estate)
    if not names:
        out("FAIL", "no party in this estate claims the adopter role at its served commit -- a "
                    "check that grades nothing and exits green is the failure the gate exists to catch")
        return exit_code()
    for adopter in names:
        repo = os.path.join(estate, adopter)
        party = served_yaml(repo, "party.yaml") or {}
        currency = str(party.get("reporting_currency") or "GBP")
        evidence = served_json(repo, "composed/evidence.json")
        platform_tag = served_platform_tag(repo)
        rule = composer_carries_rule(estate, platform_tag) if platform_tag else None
        if evidence is None:
            out("SKIP", f"{adopter} serves no composed/evidence.json at {SERVED_REF}, so nothing it prices can be read")
        if platform_tag is None:
            out("SKIP", f"{adopter} declares no platform pin at {SERVED_REF} ({PLATFORM_PIN}), so which composer wrote its evidence is unobserved")
        for edge in (party.get("inherits") or []):
            if edge.get("kind") != "feed":
                continue
            pins += 1
            publisher, name, version = str(edge["party"]), str(edge.get("name")), str(edge.get("version"))
            tags = fc.remote_tags(publisher)
            if tags is None:
                out("SKIP", f"{adopter} pins {publisher}/feed/{name}@{version}: could not reach "
                            f"{fc.REMOTE.format(p=publisher)} to read its tags")
                continue
            newest_major, newest_tag = newest_tagged_major(name, tags)
            mine = pinned_major(version)
            entry = edge_entry(evidence, publisher, name)
            if fc.match_tag({"name": name}, version, tags) is None:
                untagged += 1
                hole = (entry or {}).get("hole")
                if isinstance(hole, dict) and hole.get("status") in OPEN:
                    holes += 1
                out("NOTE", f"{adopter} pins {publisher}/feed/{name}@{version}: untagged on the remote; "
                            f"hole carried in the served evidence: {'yes' if isinstance(hole, dict) and hole.get('status') in OPEN else 'no'} "
                            f"(graded by verify-untagged-pin-is-priced.sh)")
                continue
            if newest_major is None or mine is None or newest_major <= mine:
                out("PASS", f"{adopter} pins {publisher}/feed/{name}@{version}: at the newest tagged "
                            f"major on {publisher}'s real remote ({newest_tag}); nothing to price, said by name")
                continue
            behind += 1
            line = supersede_line(evidence, publisher, name)
            if line is not None:
                carried += 1
            assert newest_tag is not None
            tagged = tag_date(os.path.join(estate, publisher), newest_tag) if os.path.isdir(os.path.join(estate, publisher)) else None
            status, msg = grade_behind(adopter=adopter, currency=currency, party=publisher, name=name,
                                       version=version, newest_major=newest_major, newest_tag=newest_tag,
                                       tagged=tagged, line=line, entry=entry, rule=rule,
                                       platform_tag=platform_tag)
            out(status, msg)
        counts = retirement_prs(adopter)
        if counts is None:
            pr_unknown.append(adopter)
        else:
            opened_total += counts[0]
            merged_total += counts[1]
    if pins == 0:
        out("FAIL", "no adopter declares a feed pin at its served commit -- nothing was graded")
    out("NOTE", f"adopters behind a newer tagged major: {behind} pin(s) across {len(names)} adopter(s); "
                f"supersede lines carried in served evidence: {carried} of {behind}")
    out("NOTE", f"untagged-feed pins: {untagged} of {pins}; holes carried: {holes} of {untagged}")
    out("NOTE", f"retirement PRs opened/merged: {opened_total}/{merged_total}"
                + (f" (could not list for {', '.join(pr_unknown)})" if pr_unknown else ""))
    return exit_code()


def exit_code() -> int:
    if "FAIL" in LINES:
        return 1
    if "SKIP" in LINES:
        return 3
    return 0


# --------------------------------------------------------------------------
# selfcheck -- pure grades, planted
# --------------------------------------------------------------------------
def selfcheck() -> None:
    plants = 0

    def line(**over: Any) -> dict[str, Any]:
        ramp = eol_ramp("2026-09-01", "2026-09-08")
        base: dict[str, Any] = {
            "source": "pub", "kind": SUPERSEDE_KIND, "name": "wares", "version": "v1",
            "perspective": "ado", "currency": "GBP",
            "newer": {"version": "v2", "tag": "wares/v2.0.0", "tagged": "2026-09-01"},
            "since": "2026-09-01", "as_of": "2026-09-08", "ramp": ramp, "base": 1000.0,
            "amount": 1000.0 * (ramp - 1.0)}
        base.update(over)
        return base

    def grade(**over: Any) -> tuple[str, str]:
        kw: dict[str, Any] = dict(adopter="ado", currency="GBP", party="pub", name="wares",
                                  version="v1", newest_major=2, newest_tag="wares/v2.0.0",
                                  tagged="2026-09-01", line=line(), entry={"amount": 1000.0},
                                  rule=True, platform_tag="v9.9.9")
        kw.update(over)
        return grade_behind(**kw)

    # the ramp restated matches the feeds module's own numbers
    assert eol_ramp("2025-10-31", "2025-01-01") == 1.0 and eol_ramp("2025-10-31", "2025-10-31") == 1.0
    assert abs(eol_ramp("2025-10-31", "2026-10-31") - 2.0) < 1e-9 and eol_ramp("2025-10-31", "2035-10-31") == 5.0
    # the newest tagged major of a form family, and a pin's major
    assert newest_tagged_major("wares", {"wares/v1.0.0", "wares/v2.0.0", "other/v3.0.0", "v1.9.9"}) == (2, "wares/v2.0.0")
    assert newest_tagged_major("q", {"v1.0.0", "v3.1.0", "v3.0.9"}) == (3, "v3.1.0")
    assert newest_tagged_major("q", {"z/v9.0.0"}) == (None, None)
    assert pinned_major("v2") == 2 and pinned_major("2.1.0") == 2 and pinned_major("x") is None

    cases = [
        ("behind, carried, right", grade(), "PASS"),
        ("behind, composer without the rule", grade(line=None, rule=False), "SKIP"),
        ("behind, composer unreadable", grade(line=None, rule=None), "SKIP"),
        ("behind, rule present, no line", grade(line=None), "FAIL"),
        ("behind, tag date unreadable", grade(tagged=None), "SKIP"),
        ("wrong perspective", grade(line=line(perspective="other")), "FAIL"),
        ("wrong currency", grade(line=line(currency="USD")), "FAIL"),
        ("names a tag the remote does not have", grade(line=line(newer={"version": "v2", "tag": "wares/v2.0.1", "tagged": "2026-09-01"})), "FAIL"),
        ("since is not the tag date", grade(line=line(since="2026-08-01")), "FAIL"),
        ("ramp not the eol ramp", grade(line=line(ramp=1.5)), "FAIL"),
        ("amount not base x (ramp-1)", grade(line=line(amount=999.0)), "FAIL"),
        ("base not the feed line's amount", grade(line=line(), entry={"amount": 5.0}), "FAIL"),
        ("unpriced line", grade(line=line(amount=None)), "FAIL"),
        ("zero on the signing day is a PASS with both dates", grade(line=line(as_of="2026-09-01", ramp=1.0, amount=0.0)), "PASS"),
    ]
    for label, (status, msg), want in cases:
        assert status == want, (label, status, msg)
        plants += 1
    _, msg = grade(line=None, rule=False)
    assert "v9.9.9" in msg and "carries no supersede rule" in msg, msg
    _, msg = grade(line=line(as_of="2026-09-01", ramp=1.0, amount=0.0))
    assert "0.00 GBP" in msg and "2026-09-01" in msg, msg
    _, msg = grade(line=None)
    assert "never free" in msg, msg
    # the lookups
    ev = {"prices": [{"kind": "feed", "source": "pub", "name": "wares", "amount": 7.0, "hole": {"status": "new"}},
                     line()]}
    assert edge_entry(ev, "pub", "wares") is ev["prices"][0] and edge_entry(ev, "pub", "x") is None
    assert supersede_line(ev, "pub", "wares") is ev["prices"][1] and supersede_line(None, "pub", "wares") is None
    print(f"OK {plants} planted grades bite: a pin behind a newer tagged major PASSes only with a "
          f"supersede line under the adopter's own perspective and currency naming the remote's "
          f"tag, its cut date, the eol ramp to its own as-of and base x (ramp - 1); a composer "
          f"without the rule is a could-not-look naming the tag; the ramp and the majors read as "
          f"platform's do")


def main(argv: list[str]) -> int:
    cmd = argv[1] if len(argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck()
        return 0
    if cmd == "check":
        return check()
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
