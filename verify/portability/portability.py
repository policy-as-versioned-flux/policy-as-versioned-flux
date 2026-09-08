#!/usr/bin/env python3
"""portability.py — eco-system ticket 45 made checkable: can an adopter re-derive its own
signed prices with the publisher's clone absent, and does every switching cost it prints
carry a perspective, a currency and a window it was really annualised over?

## What is measured, and against what

| | served artefact | operation that reaches it |
|---|---|---|
| the adopter's declared feed edges | its own `party.yaml` at the commit it SERVES | `git fetch origin main`, then `git show origin/main:party.yaml` |
| what it vendored and what it digests to | its own `composed/HEADER.yaml` at that commit | `git show origin/main:composed/HEADER.yaml` |
| the vendored bytes and their record | its own `composed/feeds/...` at that commit, `PROVENANCE.json` included | `git show origin/main:<path>` |
| the publisher's own copy | the publisher's tree AT THE TAG THIS ADOPTER PINS | `git fetch origin <tag>`, then `git -C <publisher> show <tag>:<path>` |
| the prices | its own `composed/evidence.json` at that commit | `git show origin/main:composed/evidence.json` |

The served commit is `origin/main`, FETCHED before it is read (SERVED_REF — the rule
verify/map-surface applies, for the same reason). A clone under .estate-clone/ is a venue: its
HEAD is whatever a builder last checked out and its remote-tracking ref is whatever was last
fetched, and on 2026-09-08 every adopter clone here sat behind what GitHub served. Review F7
caught the first cut reading `HEAD` and calling it "the commit it serves". A unit whose fetch
fails is a could-not-look naming the reason, never a quiet read of the local ref. And it is a
COMMIT throughout, not a tag: `origin/main` is what the adopter serves, and whether a signed tag
also points at it is verify-branch-refs' question, not this one's.

No proxy anywhere: not a working tree, not platform's main, not a file merely existing, not a
record's prose. The publisher's tag comes out of the adopter's own
`gitops/flux-system/gotk-sync-<party>.yaml` — the pin Renovate bumps and the adopter's own
workflows read — so a vendored payload is compared against the bytes at the tag this adopter
actually pins, and not against whatever the publisher's main happens to hold today.

## The sentences graded

1. every feed edge the adopter declares has a vendored copy at the version it pins;
2. every file the header digests is present in the SERVED commit and digests to what the header
   says, and the tree's own `PROVENANCE.json` carries the same party, name, version, SHA and
   digests — so the commit the adopter serves carries the bytes its header signs, and the
   record that names the feed path, the converter and the invocation cannot describe a
   different tree than the one the header signed;
3. the vendored payload is byte-identical to the publisher's own artefact at the tag the
   adopter pins;
4. the vendored converter, REPLAYED with the exact invocation its `PROVENANCE.json` records, in
   a directory holding nothing but itself and the vendored payload — no publisher clone, no
   estate — returns a scenario digesting to what the record says it returned. Nothing about
   the command is guessed here: platform's `vendor_feed` writes the argv `_run_converter` really
   used and the sha256 of what came back, and this leg puts the payload in the place that argv
   expects and compares. A record with no invocation is a NAMED could-not-look and never a
   FAIL. Review F1: the first cut ran `<converter> --selfcheck`, which neither real converter
   accepts — ico's rewrites an unknown first token to `build` and exits 2 for missing
   arguments, the register's exits 2 for a missing `cmd` — and the leg was green only because
   the fixture converter special-cased the flag. On the day vendoring landed it would have been
   a false red for every real converter;
5. every `switching` entry carries the adopter's own perspective and reporting currency, and
   either an amount whose `over_pin_life` really is that amount over the window between the
   edge's signed `since` and the composition's own as-of, or NO amount and a named
   `could_not_look`. A window that runs BACKWARDS — as-of before since — FAILS naming both
   dates; it is not a pin's life of |N| months (review F3);
6. an adopter that publishes no signed `size:` has its switching lines reported as a NAMED
   could-not-look, never a pass. Which of its feed prices are the publisher's statutory cap is
   read off the served entry itself, never assumed from the missing size: ico's converter writes
   "Not sized to any subscriber: priced at the statutory cap." into the scenario it returns when
   it is given no turnover, and that note travels into the entry's `lef_basis` (CAP_NOTE). A
   capped line is a ceiling every firm in the estate shares, so it is not a statement about THAT
   institution; the check prints the identical figures across unsized adopters as the proof
   rather than asserting it (ticket 64: tuppence and ludlow publish no size). Two unsized
   adopters whose own notes both say "priced at the statutory cap" for the same feed and yet
   carry DIFFERENT amounts FAIL, naming both adopters and both amounts: a cap is one number
   (review F6). A feed whose note names no cap — the threat register prices each institution
   from its own entry — is neither called the cap nor compared: on the live estate ludlow and
   tuppence price it at 318,229.78 and 222,574.31 and that is two institutions, not a defect;
7. no string anywhere in `prices[]` carries an absolute path (review F2): composed/evidence.json
   is what the served commit carries, and a refusal that names the builder's home directory
   makes the served bytes depend on whose machine composed them.

What THIS adopter prices from publishers it could not re-read is printed per adopter, under its
own perspective and currency, and never totalled across adopters. It sums EXPOSURE kinds only
(`feed`, `twin`); a `premium` is a cost, is printed beside the figure by name, and is never added
to it (review F4: the first cut folded driftwood's 113,403.30 premium into a 1,920,138.92
"exposure" through a bare `+=`, the very line platform's `EXPOSURE_KINDS` refuses to cross).

The FULL re-derivation of prices — composing an adopter with a publisher's clone absent and
getting every signed figure back — runs at the seam that owns it, platform's
`compose/composition.py --selfcheck`: with ico's clone removed, every file driftwood RENDERS
comes back byte-identical and every price amount is equal; composed/evidence.json is written
from the document rather than rendered, and differs by the open publisher-clone-absent limit.
This script grades the estate's SERVED state, which is the half that rots.

Grading, per the gate contract: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    portability.py check        # every adopter in .estate-clone/
    portability.py selfcheck    # planted defects: proves each refusal bites
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

LINES: list[str] = []
MESSAGES: list[str] = []

# The commit each unit SERVES. Fetched before it is read, every run (review F7).
SERVED_REF = "origin/main"
# The platform release that first carries a composition able to vendor. Named as the thing the
# wait is ON, so the could-not-look says what would end it rather than "not yet".
VENDORING_LANDS_IN = "the first signed platform tag whose compose/composition.py vendors"
MONTHS_PER_YEAR = 12
# The price kinds that are EXPOSURE and may be summed into one figure under one perspective.
# Restated from platform's EXPOSURE_KINDS rather than imported (the hub pins no platform), and
# for the reason platform keeps it: a premium is a cost, and folding cover into the exposure it
# was priced from makes the premium an input to its own formula (review F4).
EXPOSURE_KINDS = ("feed", "twin")
PROVENANCE = "PROVENANCE.json"
# The publisher's own words for a price it computed at its statutory cap: ico's
# schema/to_fair_scenario.py appends this to the scenario note when it is given no turnover, and
# composition carries the note into the served entry's `lef_basis`. Read from the entry, so which
# lines are a cap is the publisher's statement and never this check's inference from a missing
# size (review F6, sharpened by the live estate: the threat register is priced per institution).
CAP_NOTE = "priced at the statutory cap"
# A slash-rooted path of two or more segments that is not the tail of a word, a URL scheme or a
# `./`: the shape of a builder's machine leaking into a signed artefact (review F2).
ABSOLUTE_PATH = re.compile(r"(?<![\w.:/])/[\w.-]+(?:/[\w.-]+)+")


def out(status: str, msg: str) -> None:
    LINES.append(status)
    MESSAGES.append(f"{status}: {msg}")
    print(f"{status}: {msg}")


def git(repo: str, *args: str) -> tuple[int, str]:
    r = subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True)
    return r.returncode, r.stdout


def show(repo: str, ref: str, path: str) -> str | None:
    """One blob out of a SERVED tree. None where the ref does not carry it — never a fallback
    to the working copy, which is the whole point of reading this way."""
    code, text = git(repo, "show", f"{ref}:{path}")
    return text if code == 0 else None


def digest(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()


# One fetch per (clone, refspec) per run. The served ref does not move while a run reads it,
# and eight units are fetched once each rather than once per edge.
_FETCHED: dict[tuple[str, str], str | None] = {}


def fetch(repo: str, refspec: str) -> str | None:
    """Fetch one refspec from `origin`. The reason it could not, or None.

    Fetching is part of the rule, not a convenience: `origin/main` in a local clone is only
    what GitHub serves if somebody fetched it, and a stale remote-tracking ref is the same
    venue-dependent reading as a working copy, one level down."""
    key = (repo, refspec)
    if key not in _FETCHED:
        r = subprocess.run(["git", "-C", repo, "fetch", "--quiet", "origin", refspec],
                           capture_output=True, text=True)
        _FETCHED[key] = None if r.returncode == 0 else \
            (r.stderr.strip().splitlines() or ["no reason given"])[-1]
    return _FETCHED[key]


def fetch_served(repo: str) -> str | None:
    return fetch(repo, f"+refs/heads/main:refs/remotes/{SERVED_REF}")


def fetch_tag(repo: str, tag: str) -> str | None:
    return fetch(repo, f"+refs/tags/{tag}:refs/tags/{tag}")


def months_apart(a: str, b: str) -> int:
    """Whole months from `a` to `b`, SIGNED, from the two YYYY-MM-DD strings alone. Restated
    here rather than imported: the hub is not a party and pins no platform, exactly as
    verify/feed-contract restates pin_content's three cases in git plumbing.

    Signed since review F3. It used to return abs(), so an as-of BEFORE the edge's own `since`
    graded as "the pin has stood N months". Negative means b precedes a, and the caller says
    what it does with that."""
    try:
        ay, am = int(a[:4]), int(a[5:7])
        by, bm = int(b[:4]), int(b[5:7])
    except (ValueError, IndexError):
        return 0
    return (by * 12 + bm) - (ay * 12 + am)


def adopters(estate: str) -> list[str]:
    """Every party in the clone whose own SERVED party.yaml claims the adopter role. Derived,
    never a hardcoded list — verify-twin-per-adopter.sh's own rule.

    Read at `origin/main` after a fetch, and never off disk or at HEAD. The directory listing is
    only how the candidate names are found; the role that decides whether a party is graded is
    a fact about the commit that party SERVES, so neither an uncommitted edit nor a builder's
    checkout can add an adopter to this run or remove one from it. A unit that cannot be
    fetched is named and left ungraded: it might be an adopter, and this run cannot see it."""
    found = []
    for name in sorted(os.listdir(estate)) if os.path.isdir(estate) else []:
        repo = os.path.join(estate, name)
        if not os.path.isdir(os.path.join(repo, ".git")):
            continue
        reason = fetch_served(repo)
        if reason:
            out("SKIP", f"could not fetch {SERVED_REF} for {name} ({reason}), so what this "
                        f"clone holds may be behind what GitHub serves and none of it is graded")
            continue
        text = show(repo, SERVED_REF, "party.yaml")
        if text is None:
            continue
        try:
            doc = yaml.safe_load(text) or {}
        except yaml.YAMLError:
            continue
        if "adopter" in (doc.get("roles") or []):
            found.append(name)
    return found


def pinned_tag(estate: str, adopter: str, party: str) -> str | None:
    """The tag THIS adopter pins for a publisher, out of its own Flux pin at the commit it
    serves. None where it declares no pin for that party."""
    text = show(os.path.join(estate, adopter), SERVED_REF,
                f"gitops/flux-system/gotk-sync-{party}.yaml")
    if text is None:
        return None
    for doc in yaml.safe_load_all(text):
        if isinstance(doc, dict) and doc.get("kind") == "GitRepository":
            tag = ((doc.get("spec") or {}).get("ref") or {}).get("tag")
            if tag:
                return str(tag)
    return None


def feed_edges(party_doc: dict) -> list[dict]:
    return [e for e in (party_doc.get("inherits") or [])
            if e.get("kind") in ("feed", "pricing", "threat")]


# --------------------------------------------------------------------------
# the per-adopter grade — pure over what was read, so selfcheck can plant
# --------------------------------------------------------------------------
def capped(entry: dict) -> bool:
    """Whether the publisher's own note on this served entry says it was priced at the cap."""
    return CAP_NOTE in str(entry.get("lef_basis") or "")


def grade_switching(entries: list[dict], adopter: str, currency: str, sized: bool,
                    capped_feeds: set[str] | None = None) -> None:
    """Sentence 5, and the half of sentence 6 that is about an entry rather than the estate."""
    capped_feeds = capped_feeds or set()
    for entry in entries:
        who = f"{adopter}'s switching entry for {entry.get('source')}/{entry.get('name')}"
        if entry.get("perspective") != adopter or entry.get("currency") != currency:
            out("FAIL", f"{who} is priced under perspective {entry.get('perspective')!r} in "
                        f"{entry.get('currency')!r}, and {adopter} reports as {adopter!r} in "
                        f"{currency!r} — a price that is not this party's is not this party's")
            continue
        amount = entry.get("amount")
        if amount is None:
            if entry.get("could_not_look"):
                out("PASS", f"{who} could not be priced and says why, in the publisher's own "
                            f"words: {entry['could_not_look'][:160]}")
            else:
                out("FAIL", f"{who} carries no amount and no reason — an absent figure that "
                            f"names nothing is indistinguishable from a forgotten one")
            continue
        since, as_of = entry.get("since"), entry.get("as_of")
        if not since or not as_of:
            out("FAIL", f"{who} is annualised over a pin's life with no {'since' if not since else 'as_of'}"
                        f" — a window with one end")
            continue
        months = months_apart(str(since), str(as_of))
        if months < 0:
            out("FAIL", f"{who} is annualised over a window that runs backwards: the edge was "
                        f"signed since {since} and the composition's as-of is {as_of}, which is "
                        f"EARLIER — that is not a pin that has stood {-months} months, it is a "
                        f"composition that could not measure the pin's life (review F3)")
            continue
        if entry.get("pin_life_months") != months:
            out("FAIL", f"{who} says the pin has stood {entry.get('pin_life_months')} months, "
                        f"and {since} to {as_of} is {months}")
            continue
        expect = amount * months / MONTHS_PER_YEAR
        got = entry.get("over_pin_life")
        if not isinstance(got, (int, float)) or abs(got - expect) > 1e-6:
            out("FAIL", f"{who} carries over_pin_life {got}, and {amount} over {months} months "
                        f"is {expect}")
            continue
        if not sized and entry.get("name") in capped_feeds:
            # Never a pass. The amount is real arithmetic on the publisher's own statutory cap,
            # which is a ceiling every firm shares — so it is not a figure about this one.
            out("SKIP", f"{who} rests on a price computed at the publisher's statutory cap, "
                        f"because {adopter} publishes no signed size: — so the number is a "
                        f"ceiling every firm in this estate shares and says nothing about this "
                        f"institution (ticket 64)")
        elif not sized:
            # Also never a pass, for a stated reason that is policy rather than arithmetic: this
            # check grades no switching cost of an unsized adopter (ticket 64, decision 6). The
            # publisher's own note on this feed names no cap, so the amount may well be this
            # institution's; it stays unverified until a size is signed, and the line says so.
            out("SKIP", f"{who} is not graded: {adopter} publishes no signed size:, and this "
                        f"check grades no switching cost of an unsized adopter (ticket 64) — the "
                        f"publisher's own note on {entry.get('name')} names no cap, so the amount "
                        f"may be this institution's, and it stays unverified until a size is "
                        f"signed")
        else:
            out("PASS", f"{who} is {amount:.2f} {currency}/yr under {adopter}'s own perspective, "
                        f"carried over the {months} months the pin has stood since {since}")


def _strings(value: object, at: str = "") -> list[tuple[str, str]]:
    """Every string inside a JSON value, with the key path it sits at."""
    if isinstance(value, str):
        return [(at, value)]
    if isinstance(value, dict):
        return [s for k, v in value.items() for s in _strings(v, f"{at}.{k}" if at else str(k))]
    if isinstance(value, list):
        return [s for i, v in enumerate(value) for s in _strings(v, f"{at}[{i}]")]
    return []


def grade_no_absolute_paths(prices: list[dict], adopter: str) -> None:
    """Sentence 7 (review F2). Every string in every entry, nested ones included: the threat
    entry's refusal and the unpriceable[] names are where a path travelled in the first cut."""
    for entry in prices:
        for at, text in _strings(entry):
            hit = ABSOLUTE_PATH.search(text)
            if hit:
                out("FAIL", f"{adopter}'s served prices[] entry {entry.get('kind')}/"
                            f"{entry.get('name')} carries an absolute path at `{at}`: "
                            f"{hit.group(0)} — composed/evidence.json is what the served commit "
                            f"carries, and a string naming the machine that composed it makes "
                            f"those bytes depend on whose machine that was (review F2)")


def provenance(repo: str, adopter: str, header_record: dict) -> dict | None:
    """The vendored tree's own PROVENANCE.json, read from the served commit and held to the
    header (sentence 2). The header carries the signed subset — party, name, version, path,
    SHA and the file digests; the record beside the files carries what the header does not:
    the feed path, the converter, the invocation that priced it and the digest of what it
    returned. The two must agree on every field they share, or the record is describing a
    tree other than the one the header signed. Returns the merged record, header winning."""
    path = f"{header_record['path']}/{PROVENANCE}"
    text = show(repo, SERVED_REF, path)
    if text is None:
        out("FAIL", f"{adopter}'s header names a vendored tree at {header_record['path']} and "
                    f"the served commit carries no {PROVENANCE} there — a tree with no record "
                    f"of what it is a copy of")
        return None
    try:
        record = json.loads(text)
    except json.JSONDecodeError as e:
        out("FAIL", f"{adopter}'s served {path} is not readable JSON: {e}")
        return None
    for key in ("party", "name", "version", "sha", "files"):
        if record.get(key) != header_record.get(key):
            out("FAIL", f"{adopter}'s served {path} says {key}={record.get(key)!r} and its own "
                        f"composed/HEADER.yaml signed {header_record.get(key)!r} — a record "
                        f"that disagrees with the header it rides under")
            return None
    return {**record, **header_record}


def grade_adopter(estate: str, adopter: str, unsized: dict[str, dict] | None = None) -> None:
    repo = os.path.join(estate, adopter)
    party_text = show(repo, SERVED_REF, "party.yaml")
    if party_text is None:
        out("SKIP", f"{adopter} serves no party.yaml at {SERVED_REF}")
        return
    party_doc = yaml.safe_load(party_text) or {}
    currency = party_doc.get("reporting_currency") or "USD"
    sized = isinstance((party_doc.get("size") or {}).get("turnover"), dict)
    edges = feed_edges(party_doc)
    if not edges:
        out("PASS", f"{adopter} declares no feed parent, so it has nothing to be locked into")
        return

    evidence_text = show(repo, SERVED_REF, "composed/evidence.json")
    prices: list[dict] = []
    if evidence_text is None:
        out("SKIP", f"{adopter} serves no composed/evidence.json at {SERVED_REF}")
    else:
        try:
            prices = (json.loads(evidence_text) or {}).get("prices") or []
        except json.JSONDecodeError as e:
            out("FAIL", f"{adopter}'s served composed/evidence.json is not readable JSON: {e}")
            return

    header_text = show(repo, SERVED_REF, "composed/HEADER.yaml")
    header = yaml.safe_load(header_text) if header_text else None
    records = (header or {}).get("vendored-feeds") or []
    by_pin = {(r.get("party"), r.get("name"), str(r.get("version"))): r for r in records}

    switching = [e for e in prices if e.get("kind") == "switching"]
    feeds = [p for p in prices if p.get("kind") == "feed"]
    capped_feeds = {str(p.get("name")) for p in feeds if capped(p)}
    uncapped_feeds = sorted(str(p.get("name")) for p in feeds if not capped(p))
    grade_switching(switching, adopter, currency, sized, capped_feeds)
    grade_no_absolute_paths(prices, adopter)
    if not sized and unsized is not None:
        # Reported whether or not a switching entry exists yet, because the rule is about the
        # INPUT and the input is missing today. Which lines are the cap is the publisher's own
        # statement on the served entry (CAP_NOTE), never an inference from the missing size.
        # check() turns two unsized adopters carrying the IDENTICAL capped figure into the proof
        # of that, rather than asserting it in prose (ticket 64).
        unsized[adopter] = {p.get("name"): p.get("amount") for p in feeds if capped(p)}
        out("SKIP", f"{adopter} publishes no signed size:, so the feed prices its own served "
                    f"entries say were `{CAP_NOTE}` — {', '.join(sorted(capped_feeds)) or 'none'}"
                    f" — and every switching cost derived from one are the publisher's ceiling, "
                    f"not a figure about this institution (ticket 64); its other feed prices "
                    f"({', '.join(uncapped_feeds) or 'none'}) name no cap and are not graded "
                    f"either")

    # The standing figure this check exists to put somewhere: what THIS adopter prices from
    # publishers it could not re-read. One perspective, one currency, EXPOSURE kinds only, and
    # deliberately NOT totalled across adopters -- three adopters' exposures are three balance
    # sheets, and a sum that crosses a perspective is the one thing the £ seam refuses
    # (ADR-0020). A premium is a cost: named beside the figure, never added to it (review F4).
    exposure = 0.0
    costs: list[str] = []
    for edge in edges:
        party = str(edge.get("party") or "")
        name, version = edge.get("name"), str(edge.get("version"))
        tag = pinned_tag(estate, adopter, party)
        record = by_pin.get((party, name, version))
        if record is None:
            # The observation the estate had nowhere before: what this adopter prices from a
            # publisher it could not re-read if that publisher went away.
            priced = next((p for p in prices
                           if p.get("source") == party and p.get("name") == name), None)
            amount = priced.get("amount") if priced else None
            kind = priced.get("kind") if priced else None
            if not isinstance(amount, (int, float)):
                what = "an unpriced edge"
            elif kind in EXPOSURE_KINDS:
                exposure += amount
                what = f"{amount:.2f} {currency}/yr of exposure"
            else:
                costs.append(f"the {kind} {name} at {amount:.2f} {currency}/yr")
                what = f"a {kind} of {amount:.2f} {currency}/yr"
            out("SKIP", f"{adopter} carries no vendored copy of {party}'s {name}@{version} at "
                        f"{SERVED_REF}, so {what} it signed cannot be re-derived without "
                        f"{party}'s clone; it waits on {VENDORING_LANDS_IN} and on this "
                        f"adopter's platform pin moving to it "
                        f"(pinned publisher tag today: {tag or 'none declared'})")
            continue
        if not switching:
            out("FAIL", f"{adopter} vendored {party}/{name}@{version} but prints no switching "
                        f"entry for it — a copy nobody priced a switch against")
        # 2. the record beside the files, held to the header; then the digests the header signed
        record = provenance(repo, adopter, record)
        if record is None:
            continue
        broken = False
        for rel, want in (record.get("files") or {}).items():
            blob = show(repo, SERVED_REF, f"{record['path']}/{rel}")
            if blob is None:
                out("FAIL", f"{adopter}'s header digests {record['path']}/{rel} and the served "
                            f"commit does not carry it")
                broken = True
            elif digest(blob) != want:
                out("FAIL", f"{adopter}'s served {record['path']}/{rel} does not match the "
                            f"digest its own composed/HEADER.yaml signed")
                broken = True
        if broken:
            continue
        # 3. against the publisher's own bytes, at the tag THIS adopter pins
        publisher = os.path.join(estate, party)
        if tag is None:
            out("SKIP", f"{adopter} declares no Flux pin for {party}, so there is no tag to "
                        f"compare its vendored copy of {name}@{version} against")
        elif not os.path.isdir(os.path.join(publisher, ".git")):
            out("SKIP", f"{party}'s clone here has no {tag}:{record['feed_path']} to compare "
                        f"{adopter}'s vendored copy against — there is no clone of {party} here")
        else:
            reason = fetch_tag(publisher, tag)
            theirs = show(publisher, tag, record["feed_path"])
            if theirs is None:
                out("SKIP", f"{party}'s clone here has no {tag}:{record['feed_path']} to compare "
                            f"{adopter}'s vendored copy against"
                            + (f" (fetching the tag: {reason})" if reason else ""))
            elif theirs != show(repo, SERVED_REF, f"{record['path']}/{record['feed_path']}"):
                out("FAIL", f"{adopter}'s vendored {name}@{version} is not the payload {party} "
                            f"serves at {tag} — a copy that has drifted from the artefact it "
                            f"claims to be a copy of")
            else:
                out("PASS", f"{adopter}'s vendored {name}@{version} is byte-identical to what "
                            f"{party} serves at {tag}, the tag {adopter} itself pins")
        # 4. and the recorded invocation replays with nothing else on disk
        run_standalone(repo, adopter, record)
    if exposure or costs:
        beside = ""
        if costs:
            beside = (" Beside it, and never added to it: " + "; ".join(costs)
                      + " — a cost, not an exposure, and one array must not add them")
        out("SKIP", f"{adopter} prices {exposure:.2f} {currency}/yr of EXPOSURE (kinds "
                    f"{' and '.join(EXPOSURE_KINDS)} only), under its own perspective, from "
                    f"publishers whose clone it would need to re-derive any of it — no total is "
                    f"taken across adopters, because three adopters' exposures are three balance "
                    f"sheets.{beside}")


def run_standalone(repo: str, adopter: str, record: dict) -> None:
    """Sentence 4 as an experiment: the vendored converter is written into a directory holding
    nothing but itself and the vendored payload — no publisher clone, no estate, no hub — and
    RUN with the exact argv its PROVENANCE.json records, the payload in the place that argv
    expects (platform's `_run_converter` puts it second: `<converter> <cmd> <payload> <rest>`,
    and the record is written by the same code that ran it). The scenario it prints must digest
    to what the record says the priced run returned. That is what proves the copy carries no
    hidden dependency on the repository it came from AND re-derives the price, not merely that
    it starts.

    Nothing is guessed. A record with no invocation is a NAMED could-not-look, never a FAIL,
    and never a flag this check made up (review F1). The one liberty platform's load_feed_payload
    takes with a payload — filling the converter's version key from the envelope when the body
    lacks it — is restated from the record's own `payload_version_key`, not from platform."""
    name, version = record["name"], record["version"]
    converter = record.get("converter")
    if not converter:
        out("PASS", f"{adopter}'s vendored {name}@{version} declares no converter, and its "
                    f"publisher prices it without one — a named absence")
        return
    who = f"{adopter}'s vendored converter for {name}@{version}"
    invocation, want = record.get("invocation"), record.get("scenario_sha256")
    if not isinstance(invocation, list) or not invocation or not isinstance(want, str):
        out("SKIP", f"no vendored converter records an invocation: {who} carries no "
                    f"`invocation` and `scenario_sha256` in its {PROVENANCE}, so there is no "
                    f"command to replay and nothing to hold its output to; it waits on a "
                    f"platform tag whose vendor_feed records both, and this check will not "
                    f"guess a flag (review F1)")
        return
    script = show(repo, SERVED_REF, f"{record['path']}/{converter}")
    payload_text = show(repo, SERVED_REF, f"{record['path']}/{record['feed_path']}")
    if script is None or payload_text is None:
        out("FAIL", f"{who} is missing its converter or payload in the served commit")
        return
    try:
        envelope = json.loads(payload_text)
    except json.JSONDecodeError as e:
        out("FAIL", f"{adopter}'s vendored {name} payload is not JSON: {e}")
        return
    body = envelope.get("payload", envelope) if isinstance(envelope, dict) else envelope
    key = record.get("payload_version_key")
    if key and isinstance(body, dict):
        body = dict(body)
        body.setdefault(key, str(version))
    argv = [str(a) for a in invocation]
    shown = f"{os.path.basename(converter)} {argv[0]} <payload> {' '.join(argv[1:])}".rstrip()
    with tempfile.TemporaryDirectory() as bare:
        script_path = os.path.join(bare, os.path.basename(converter))
        open(script_path, "w").write(script)
        payload_path = os.path.join(bare, "payload.json")
        open(payload_path, "w").write(json.dumps(body))
        r = subprocess.run([sys.executable, script_path, argv[0], payload_path, *argv[1:]],
                           capture_output=True, text=True, cwd=bare)
    if r.returncode != 0:
        out("FAIL", f"{who} does not run with the publisher's clone absent: `{shown}` exited "
                    f"{r.returncode}: "
                    f"{(r.stderr or r.stdout).strip().splitlines()[-1:] or ['no output']}")
        return
    try:
        got = digest(json.dumps(json.loads(r.stdout), sort_keys=True))
    except json.JSONDecodeError as e:
        out("FAIL", f"{who} ran `{shown}` and printed something that is not a scenario: {e}")
        return
    if got != want:
        out("FAIL", f"{who} replayed `{shown}` standalone and returned a scenario digesting to "
                    f"{got[:12]}, and the record it was vendored with says {want[:12]} — the "
                    f"same command over the same payload gave a different answer, so what this "
                    f"copy re-derives is not what was priced")
        return
    out("PASS", f"{who} replays its recorded invocation `{shown}` in a directory holding "
                f"nothing but itself and the vendored payload — no publisher clone, no estate — "
                f"and returns the very scenario it was priced from (sha256 {want[:12]}), so "
                f"{adopter} can re-derive that price with {record['party']}'s clone absent")


# --------------------------------------------------------------------------
def check(estate: str = ESTATE) -> int:
    _FETCHED.clear()
    if not os.path.isdir(estate):
        out("SKIP", "no .estate-clone (run clone-estate.sh)")
        return 3
    names = adopters(estate)
    if not names:
        out("SKIP", "no party in this estate claims the adopter role")
        return 3
    unsized: dict[str, dict] = {}
    for adopter in names:
        grade_adopter(estate, adopter, unsized)
    # The proof, not the claim: where two unsized adopters price the same feed at the SAME
    # number to the penny, and each entry's own note says it was priced at the cap, that number
    # is a property of the publisher's cap and not of either firm. Printed by name so the
    # reading is checkable rather than asserted. Two DIFFERENT numbers under two cap notes are
    # not two caps (review F6): at least one of those lines was priced at something other than
    # the cap, and this check cannot say which, so it says both. Only capped entries are here:
    # a feed priced per institution differs between institutions, and that is not a finding.
    for name in sorted({n for prices in unsized.values() for n in prices}):
        shared = sorted(a for a, prices in unsized.items()
                        if isinstance(prices.get(name), (int, float)))
        amounts = {unsized[a][name] for a in shared}
        if len(shared) > 1 and len(amounts) == 1:
            out("SKIP", f"{' and '.join(shared)} publish no signed size and both price {name} "
                        f"at exactly {amounts.pop():.2f} — the same number to the penny for two "
                        f"different institutions, which is what a statutory cap looks like and "
                        f"is why neither line may be read as a switching cost for either")
        elif len(shared) > 1:
            out("FAIL", f"{' and '.join(shared)} publish no signed size, each one's own served "
                        f"entry for {name} says it was `{CAP_NOTE}`, and they price it at "
                        f"DIFFERENT amounts — "
                        + ", ".join(f"{a} at {unsized[a][name]!r}" for a in shared)
                        + " — a statutory cap is one number, so two numbers mean at least one "
                        f"of these lines was not priced at the cap, and this check cannot say "
                        f"which (review F6)")
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck — every refusal above, planted and proved to bite
# --------------------------------------------------------------------------
# Shaped like the estate's real two converters, so a leg that guesses at a command goes red here
# the way it would on the day vendoring lands: an argparse SUBCOMMAND takes the payload path,
# and a bare `--selfcheck` is not something it accepts (exit 2) -- exactly what ico's
# schema/to_fair_scenario.py and platform's feeds/to_fair_scenario.py do. It reads the version
# key load_feed_payload fills, so the replay's one liberty is exercised too.
CONVERTER = '''#!/usr/bin/env python3
import argparse, json, sys
p = argparse.ArgumentParser()
sub = p.add_subparsers(dest="cmd", required=True)
b = sub.add_parser("build")
b.add_argument("payload")
b.add_argument("regime")
args = p.parse_args()
body = json.load(open(args.payload))
print(json.dumps({"name": "wares:%s %s" % (body.get("feed_version"), args.regime),
                  "currency": body["currency"]}))
'''
# What the fixture converter returns for the vendored payload under the recorded invocation --
# stated by the plant, not computed by running it, so the digest the check is held to is an
# independent statement of the expected scenario.
SCENARIO = {"name": "wares:v1 uk", "currency": "GBP"}
INVOCATION = ["build", "uk"]


# A fixture repository must not depend on the machine's global git config. `core.hooksPath`
# empties any globally installed pre-commit hook (one of them failed this fixture
# intermittently while it was being written), and the two gpgSign switches keep a machine that
# signs by default from making these throwaway objects need a key. A fixture that needs a
# signing key is a fixture that lies about what it proves.
FIXTURE_GIT = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgSign=false",
               "-c", "tag.gpgSign=false", "-c", "core.hooksPath=/dev/null"]


def _git_fixture(repo: str, *args: str) -> None:
    subprocess.run(["git", "-C", repo, *FIXTURE_GIT, *args], check=True, capture_output=True)


def _serve(repo: str) -> None:
    """Give a fixture repository a real `origin` to fetch from: a bare clone beside it, holding
    what the repository has PUSHED. The check reads what origin serves, so a later local commit
    that is never pushed must be invisible to it (review F7)."""
    bare = repo + ".git"
    subprocess.run(["git", *FIXTURE_GIT, "clone", "--quiet", "--bare", repo, bare],
                   check=True, capture_output=True)
    _git_fixture(repo, "remote", "add", "origin", bare)


def _plant(root: str, *, vendored=True, digest_ok=True, payload_matches=True,
           converter_runs=True, invocation_recorded=True, scenario_digest_ok=True,
           provenance="present", premium=False, switching=None) -> str:
    """A two-party fixture estate: one adopter, one publisher, both real git repos with a real
    origin, the publisher carrying a real tag the adopter really pins."""
    pub = os.path.join(root, "pub")
    os.makedirs(os.path.join(pub, "wares", "v1"))
    payload = json.dumps({"name": "wares", "payload": {"currency": "GBP"}}, indent=2)
    open(os.path.join(pub, "wares", "v1", "feed.json"), "w").write(payload)
    open(os.path.join(pub, "party.yaml"), "w").write(yaml.safe_dump(
        {"party": "pub", "roles": ["publisher"],
         "publishes": [{"kind": "feed", "name": "wares", "path": "wares"}]}))
    for cmd in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "seed"],
                ["tag", "v1.0.0"]):
        _git_fixture(pub, *cmd)
    _serve(pub)

    ado = os.path.join(root, "ado")
    os.makedirs(os.path.join(ado, "gitops", "flux-system"))
    edges = [{"party": "pub", "kind": "feed", "name": "wares", "version": "v1",
              "since": "2026-01-15"}]
    if premium:
        edges.append({"party": "ins", "kind": "feed", "name": "quote-ado", "version": "v1",
                      "since": "2026-01-15"})
    open(os.path.join(ado, "party.yaml"), "w").write(yaml.safe_dump(
        {"party": "ado", "roles": ["adopter"], "reporting_currency": "GBP",
         "size": {"turnover": {"amount": 10, "currency": "GBP"}, "customers": 2},
         "inherits": edges}))
    open(os.path.join(ado, "gitops", "flux-system", "gotk-sync-pub.yaml"), "w").write(
        yaml.safe_dump({"apiVersion": "source.toolkit.fluxcd.io/v1", "kind": "GitRepository",
                        "spec": {"ref": {"tag": "v1.0.0"}}}))
    entry = switching if switching is not None else {
        "source": "pub", "kind": "switching", "perspective": "ado", "currency": "GBP",
        "amount": 100.0, "name": "wares", "version": "v1", "since": "2026-01-15",
        "as_of": "2026-07-15", "pin_life_months": 6, "over_pin_life": 50.0,
        "could_not_look": None}
    prices = [{"source": "pub", "kind": "feed", "name": "wares", "perspective": "ado",
               "currency": "GBP", "amount": 100.0}] + ([entry] if entry else [])
    if premium:
        prices.append({"source": "ins", "kind": "premium", "name": "quote-ado",
                       "perspective": "ado", "currency": "GBP", "amount": 7.0})
    os.makedirs(os.path.join(ado, "composed"))
    open(os.path.join(ado, "composed", "evidence.json"), "w").write(
        json.dumps({"prices": prices}, indent=2))
    header: dict = {"policy-as-versioned.dev/composed": True}
    if vendored:
        base = "composed/feeds/pub/v1"
        vend_payload = payload if payload_matches else payload.replace("GBP", "USD")
        script = CONVERTER if converter_runs else \
            CONVERTER.replace("body = json.load", "sys.exit(2)\nbody = json.load")
        files = {"wares/v1/feed.json": vend_payload, "wares/to_fair_scenario.py": script}
        digests = {rel: digest(text) for rel, text in files.items()}
        if not digest_ok:
            digests["wares/v1/feed.json"] = "0" * 64
        signed = {"party": "pub", "name": "wares", "version": "v1", "sha": "deadbeef",
                  "files": digests}
        record = {**signed, "kind": "feed", "feed_path": "wares/v1/feed.json",
                  "party_artefact": None, "converter": "wares/to_fair_scenario.py",
                  "converter_from": "pub", "published_at": "2026-01-15",
                  "payload_version_key": "feed_version",
                  "invocation": INVOCATION if invocation_recorded else None,
                  "scenario_sha256": (digest(json.dumps(SCENARIO, sort_keys=True))
                                      if scenario_digest_ok else "0" * 64)
                  if invocation_recorded else None}
        if provenance == "disagrees":
            record["sha"] = "cafebabe"
        if provenance != "missing":
            files[PROVENANCE] = json.dumps(record, indent=2, sort_keys=True) + "\n"
        for rel, text in files.items():
            path = os.path.join(ado, base, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").write(text)
        header["vendored-feeds"] = [{**signed, "path": base}]
    open(os.path.join(ado, "composed", "HEADER.yaml"), "w").write(yaml.safe_dump(header))
    for cmd in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "seed"]):
        _git_fixture(ado, *cmd)
    _serve(ado)
    return root


def _commit_and_push(repo: str, message: str) -> None:
    _git_fixture(repo, "add", "-A")
    _git_fixture(repo, "commit", "-qm", message)
    _git_fixture(repo, "push", "-q", "origin", "main")


def _unsize(repo: str, name: str, amount: float, cap_note: bool = True) -> None:
    """Strip the signed size from a fixture adopter and set its one feed price, carrying the
    publisher's own cap note on the entry as ico's converter would (or not, as the register's)."""
    path = os.path.join(repo, "party.yaml")
    doc = yaml.safe_load(open(path).read())
    doc.pop("size")
    doc["party"] = name
    open(path, "w").write(yaml.safe_dump(doc))
    evidence = os.path.join(repo, "composed", "evidence.json")
    ev = json.loads(open(evidence).read())
    for p in ev["prices"]:
        p["perspective"] = name
        if p["kind"] == "feed":
            p["amount"] = amount
            if cap_note:
                p["lef_basis"] = "lm sourced from the publisher's own fines. Not sized to any " \
                                 "subscriber: priced at the statutory cap."
    open(evidence, "w").write(json.dumps(ev, indent=2))


def _plant_unsized_pair(root: str, first: float, second: float, cap_note: bool = True) -> str:
    """Two unsized adopters pinning the same publisher feed, priced at `first` and `second`."""
    _plant(root)
    ado = os.path.join(root, "ado")
    bdo = os.path.join(root, "bdo")
    shutil.copytree(ado, bdo)
    _git_fixture(bdo, "remote", "remove", "origin")
    _serve(bdo)
    for repo, name, amount in ((ado, "ado", first), (bdo, "bdo", second)):
        _unsize(repo, name, amount, cap_note)
        _commit_and_push(repo, "unsized")
    return root


def _run(**kwargs) -> list[str]:
    LINES.clear()
    MESSAGES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant(root, **kwargs)
        check(root)
    return list(LINES)


def selfcheck() -> None:
    plants = 0
    ok = _run()
    assert "FAIL" not in ok and "SKIP" not in ok, ok
    plants += 1
    print("OK a fully vendored adopter whose copy matches the publisher's own bytes at the tag "
          "it pins, whose converter replays its recorded invocation to the recorded digest, and "
          "whose switching entry annualises over a real window, passes clean")

    # The fixture converter is faithful to the real two on the one point that matters: the
    # flag the first cut guessed is not something it accepts.
    with tempfile.TemporaryDirectory() as bare:
        script = os.path.join(bare, "to_fair_scenario.py")
        open(script, "w").write(CONVERTER)
        r = subprocess.run([sys.executable, script, "--selfcheck"], capture_output=True,
                           text=True, cwd=bare)
    assert r.returncode == 2, (r.returncode, r.stderr[-200:])
    plants += 1
    print("OK the fixture converter exits 2 on `--selfcheck`, as ico's and platform's real "
          "converters do -- so the leg that passed on that flag would go red here too")

    for kwargs, want, what in (
        (dict(vendored=False), "SKIP",
         "an adopter with no vendored copy could-not-looks, naming what it cannot re-derive"),
        (dict(digest_ok=False), "FAIL",
         "a vendored file that does not match the digest its own header signed FAILS"),
        (dict(payload_matches=False), "FAIL",
         "a vendored payload that has drifted from the publisher's own bytes at the pinned tag "
         "FAILS"),
        (dict(converter_runs=False), "FAIL",
         "a vendored converter that will not run with the publisher absent FAILS"),
        (dict(scenario_digest_ok=False), "FAIL",
         "a converter that runs but returns a scenario other than the one the record says was "
         "priced FAILS"),
        (dict(provenance="missing"), "FAIL",
         "a vendored tree the header names with no PROVENANCE.json in the served commit FAILS"),
        (dict(provenance="disagrees"), "FAIL",
         "a PROVENANCE.json that disagrees with the header it rides under FAILS"),
        (dict(switching={"source": "pub", "kind": "switching", "perspective": "pub",
                          "currency": "GBP", "amount": 1.0, "name": "wares"}), "FAIL",
         "a switching entry priced under somebody else's perspective FAILS"),
        (dict(switching={"source": "pub", "kind": "switching", "perspective": "ado",
                          "currency": "GBP", "amount": None, "name": "wares",
                          "could_not_look": None}), "FAIL",
         "an absent amount that names no reason FAILS"),
        (dict(switching={"source": "pub", "kind": "switching", "perspective": "ado",
                          "currency": "GBP", "amount": 100.0, "name": "wares",
                          "since": "2026-01-15", "as_of": "2026-07-15",
                          "pin_life_months": 6, "over_pin_life": 999.0}), "FAIL",
         "an over_pin_life that is not the amount over the window it names FAILS"),
        (dict(switching={"source": "pub", "kind": "switching", "perspective": "ado",
                          "currency": "GBP", "amount": None, "name": "wares",
                          "could_not_look": "missing instrument: twin/forward-intel/v1/feed.json "
                                            "carries no lef to annualise on"}), "PASS",
         "an absent amount that carries the publisher's own refusal, naming a path RELATIVE to "
         "the adopter, is a NAMED pass"),
    ):
        lines = _run(**kwargs)
        assert want in lines, (want, what, lines)
        plants += 1
        print(f"OK {what}")

    # Review F1: a record with no invocation is a named could-not-look, never a FAIL.
    lines = _run(invocation_recorded=False)
    assert "FAIL" not in lines and "SKIP" in lines, lines
    assert any("no vendored converter records an invocation" in m for m in MESSAGES), MESSAGES
    plants += 1
    print("OK a vendored converter whose record names no invocation is a NAMED could-not-look "
          "(`no vendored converter records an invocation`), never a FAIL and never a guessed "
          "flag")

    # Review F3: a window that runs backwards FAILS naming both dates.
    lines = _run(switching={"source": "pub", "kind": "switching", "perspective": "ado",
                            "currency": "GBP", "amount": 100.0, "name": "wares",
                            "since": "2026-08-28", "as_of": "2026-05-15",
                            "pin_life_months": 3, "over_pin_life": 25.0})
    assert "FAIL" in lines, lines
    assert any("runs backwards" in m and "2026-08-28" in m and "2026-05-15" in m
               for m in MESSAGES), MESSAGES
    assert months_apart("2026-08-28", "2026-05-15") == -3
    plants += 1
    print("OK a switching entry whose as-of is EARLIER than its signed since FAILS naming both "
          "dates -- never `the pin has stood 3 months`")

    # Review F2: an absolute path anywhere in prices[] FAILS.
    lines = _run(switching={"source": "pub", "kind": "switching", "perspective": "ado",
                            "currency": "GBP", "amount": None, "name": "wares",
                            "could_not_look": "missing instrument: no file at /Users/someone/"
                                              "estate/driftwood/twin/forward-intel/v1/feed.json"})
    assert "FAIL" in lines, lines
    assert any("absolute path" in m and "/Users/someone/" in m for m in MESSAGES), MESSAGES
    plants += 1
    print("OK a prices[] string carrying the builder's absolute path FAILS, and the relative "
          "`twin/forward-intel/v1/feed.json` two plants up did not")

    # Review F4: the per-adopter figure sums exposure kinds only; the premium is named beside.
    lines = _run(vendored=False, premium=True)
    figure = next(m for m in MESSAGES if "of EXPOSURE" in m)
    assert "100.00 GBP/yr of EXPOSURE" in figure and "the premium quote-ado at 7.00" in figure \
        and "107.00" not in figure, figure
    plants += 1
    print("OK the per-adopter unre-derivable figure sums `feed` and `twin` only -- 100.00, not "
          "107.00 -- and names the 7.00 premium beside it rather than folding it in")

    # Review F7: the check reads what origin SERVES, not the clone's HEAD.
    LINES.clear()
    MESSAGES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant(root)
        ado = os.path.join(root, "ado")
        path = os.path.join(ado, "party.yaml")
        doc = yaml.safe_load(open(path).read())
        doc["inherits"] = []
        open(path, "w").write(yaml.safe_dump(doc))
        _git_fixture(ado, "add", "-A")
        _git_fixture(ado, "commit", "-qm", "local only: drop every edge, push nothing")
        rc = check(root)
    assert rc == 0 and not any("declares no feed parent" in m for m in MESSAGES), MESSAGES
    plants += 1
    print("OK a commit at the clone's HEAD that origin does not serve changes nothing: the "
          "check fetched and read origin/main, not HEAD")

    # The size rule, proved on the fixture rather than asserted about the estate.
    LINES.clear()
    MESSAGES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant(root)
        ado = os.path.join(root, "ado")
        _unsize(ado, "ado", 100.0)
        _commit_and_push(ado, "unsized")
        rc = check(root)
    assert rc == 3 and "SKIP" in LINES, LINES
    plants += 1
    print("OK an adopter that publishes no signed size: has its switching line graded a NAMED "
          "could-not-look and the run exits 3 -- never a pass, and never a guess")

    # Review F6: two unsized adopters at the SAME number are the cap; at DIFFERENT numbers,
    # at least one is not, and the check says both.
    for first, second, want in ((9039791.01976426, 9039791.01976426, "SKIP"),
                                (9039791.01976426, 9039791.02976426, "FAIL")):
        LINES.clear()
        MESSAGES.clear()
        with tempfile.TemporaryDirectory() as root:
            _plant_unsized_pair(root, first, second)
            rc = check(root)
        if want == "SKIP":
            assert rc == 3 and any("both price wares at exactly" in m for m in MESSAGES), MESSAGES
        else:
            assert rc == 1 and any("DIFFERENT amounts" in m and "ado at 9039791.01976426" in m
                                   and "bdo at 9039791.02976426" in m for m in MESSAGES), MESSAGES
        plants += 1
    print("OK two unsized adopters whose own entries say `priced at the statutory cap` and price "
          "one feed at the same number to the penny are the proof of a cap (SKIP), and at two "
          "different numbers FAIL naming both adopters and both amounts")
    # ...and a feed whose note names no cap is priced per institution: two numbers, no finding.
    LINES.clear()
    MESSAGES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant_unsized_pair(root, 318229.7785850087, 222574.31190283748, cap_note=False)
        rc = check(root)
    assert rc == 3 and "FAIL" not in LINES, MESSAGES
    assert any("is not graded" in m and "names no cap" in m for m in MESSAGES), MESSAGES
    plants += 1
    print("OK two unsized adopters pricing a feed whose own note names NO cap at different "
          "amounts are two institutions, not a defect: no FAIL, and each switching line is a "
          "named could-not-look that says the amount is ungraded rather than a cap")
    print(f"\nselfcheck ok: {plants} plants, each proved to bite")


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "check"
    if mode == "selfcheck":
        selfcheck()
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
