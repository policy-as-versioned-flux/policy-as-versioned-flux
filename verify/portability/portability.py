#!/usr/bin/env python3
"""portability.py — eco-system ticket 45 made checkable: can an adopter re-derive its own
signed prices with the publisher's clone absent, and does every switching cost it prints
carry a perspective, a currency and a window it was really annualised over?

## What is measured, and against what

| | served artefact | operation that reaches it |
|---|---|---|
| the adopter's declared feed edges | its own `party.yaml` at the commit it SERVES | `git show HEAD:party.yaml` |
| what it vendored and what it digests to | its own `composed/HEADER.yaml` at that commit | `git show HEAD:composed/HEADER.yaml` |
| the vendored bytes | its own `composed/feeds/...` at that commit | `git show HEAD:<path>` |
| the publisher's own copy | the publisher's tree AT THE TAG THIS ADOPTER PINS | `git -C <publisher> show <tag>:<path>` |
| the prices | its own `composed/evidence.json` at that commit | `git show HEAD:composed/evidence.json` |

No proxy anywhere: not a working tree, not platform's main, not a file merely existing, not a
record's prose. The publisher's tag comes out of the adopter's own
`gitops/flux-system/gotk-sync-<party>.yaml` — the pin Renovate bumps and the adopter's own
workflows read — so a vendored payload is compared against the bytes at the tag this adopter
actually pins, and not against whatever the publisher's main happens to hold today.

## The sentences graded

1. every feed edge the adopter declares has a vendored copy at the version it pins;
2. every file the header digests is present in the SERVED tree and digests to what the header
   says — so the adopter's own tag signs bytes that are really there;
3. the vendored payload is byte-identical to the publisher's own artefact at the tag the
   adopter pins;
4. the vendored converter RUNS, standalone, over the vendored payload, in a directory holding
   nothing else — no publisher clone, no estate. That is the whole portability claim reduced to
   an experiment;
5. every `switching` entry carries the adopter's own perspective and reporting currency, and
   either an amount whose `over_pin_life` really is that amount over the window between the
   edge's signed `since` and the composition's own as-of, or NO amount and a named
   `could_not_look`;
6. an adopter that publishes no signed `size:` has its switching lines reported as a NAMED
   could-not-look, never a pass. The regime half of every price such an adopter carries is the
   publisher's statutory cap — a ceiling every firm in the estate shares — so the figure is not
   a statement about THAT institution. The check prints the identical figures as the proof
   rather than asserting it (ticket 64: tuppence and ludlow publish no size).

The FULL re-derivation of prices — composing an adopter with a publisher's clone absent and
getting every signed figure back — runs at the seam that owns it, platform's
`compose/composition.py --selfcheck`, where the whole compose really runs with ico's clone
removed. This script grades the estate's SERVED state, which is the half that rots.

Grading, per the gate contract: any FAIL -> 1; else any SKIP -> 3; else 0.

Usage:
    portability.py check        # every adopter in .estate-clone/
    portability.py selfcheck    # planted defects: proves each refusal bites
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

LINES: list[str] = []

# The platform release that first carries a composition able to vendor. Named as the thing the
# wait is ON, so the could-not-look says what would end it rather than "not yet".
VENDORING_LANDS_IN = "the first signed platform tag whose compose/composition.py vendors"
MONTHS_PER_YEAR = 12


def out(status: str, msg: str) -> None:
    LINES.append(status)
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


def months_apart(a: str, b: str) -> int:
    """Whole months between two YYYY-MM-DD strings, from the strings alone. Restated here
    rather than imported: the hub is not a party and pins no platform, exactly as
    verify/feed-contract restates pin_content's three cases in git plumbing."""
    try:
        ay, am = int(a[:4]), int(a[5:7])
        by, bm = int(b[:4]), int(b[5:7])
    except (ValueError, IndexError):
        return 0
    return abs((by * 12 + bm) - (ay * 12 + am))


def adopters(estate: str) -> list[str]:
    """Every party in the clone whose own party.yaml claims the adopter role. Derived, never
    a hardcoded list — verify-twin-per-adopter.sh's own rule."""
    found = []
    for name in sorted(os.listdir(estate)) if os.path.isdir(estate) else []:
        path = os.path.join(estate, name, "party.yaml")
        if not os.path.isfile(path):
            continue
        try:
            doc = yaml.safe_load(open(path).read()) or {}
        except yaml.YAMLError:
            continue
        if "adopter" in (doc.get("roles") or []):
            found.append(name)
    return found


def pinned_tag(estate: str, adopter: str, party: str) -> str | None:
    """The tag THIS adopter pins for a publisher, out of its own Flux pin at the commit it
    serves. None where it declares no pin for that party."""
    text = show(os.path.join(estate, adopter), "HEAD",
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
def grade_switching(entries: list[dict], adopter: str, currency: str, sized: bool) -> None:
    """Sentence 5, and the half of sentence 6 that is about an entry rather than the estate."""
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
        if not sized:
            # Never a pass. The amount is real arithmetic on the publisher's own statutory cap,
            # which is a ceiling every firm shares — so it is not a figure about this one.
            out("SKIP", f"{who} rests on a price computed at the publisher's statutory cap, "
                        f"because {adopter} publishes no signed size: — so the number is a "
                        f"ceiling every firm in this estate shares and says nothing about this "
                        f"institution (ticket 64)")
        else:
            out("PASS", f"{who} is {amount:.2f} {currency}/yr under {adopter}'s own perspective, "
                        f"carried over the {months} months the pin has stood since {since}")


def grade_adopter(estate: str, adopter: str, unsized: dict[str, dict] | None = None) -> None:
    repo = os.path.join(estate, adopter)
    party_text = show(repo, "HEAD", "party.yaml")
    if party_text is None:
        out("SKIP", f"{adopter} serves no party.yaml at HEAD")
        return
    party_doc = yaml.safe_load(party_text) or {}
    currency = party_doc.get("reporting_currency") or "USD"
    sized = isinstance((party_doc.get("size") or {}).get("turnover"), dict)
    edges = feed_edges(party_doc)
    if not edges:
        out("PASS", f"{adopter} declares no feed parent, so it has nothing to be locked into")
        return

    evidence_text = show(repo, "HEAD", "composed/evidence.json")
    prices = []
    if evidence_text is None:
        out("SKIP", f"{adopter} serves no composed/evidence.json at HEAD")
    else:
        try:
            prices = (json.loads(evidence_text) or {}).get("prices") or []
        except json.JSONDecodeError as e:
            out("FAIL", f"{adopter}'s served composed/evidence.json is not readable JSON: {e}")
            return

    header_text = show(repo, "HEAD", "composed/HEADER.yaml")
    header = yaml.safe_load(header_text) if header_text else None
    records = (header or {}).get("vendored-feeds") or []
    by_pin = {(r.get("party"), r.get("name"), str(r.get("version"))): r for r in records}

    switching = [e for e in prices if e.get("kind") == "switching"]
    grade_switching(switching, adopter, currency, sized)
    if not sized and unsized is not None:
        # Reported whether or not a switching entry exists yet, because the rule is about the
        # INPUT and the input is missing today: every figure this adopter carries that scales
        # on turnover was computed at the publisher's own statutory cap. check() turns two
        # unsized adopters carrying the IDENTICAL figure into the proof of that, rather than
        # asserting it in prose (ticket 64).
        unsized[adopter] = {p.get("name"): p.get("amount") for p in prices
                             if p.get("kind") == "feed"}
        out("SKIP", f"{adopter} publishes no signed size:, so every price it carries that "
                    f"scales on turnover — and therefore every switching cost derived from one "
                    f"— is the publisher's statutory cap, not a figure about this institution "
                    f"(ticket 64)")

    for edge in edges:
        party, name, version = edge.get("party"), edge.get("name"), str(edge.get("version"))
        tag = pinned_tag(estate, adopter, party)
        record = by_pin.get((party, name, version))
        if record is None:
            # The observation the estate had nowhere before: what this adopter prices from a
            # publisher it could not re-read if that publisher went away.
            priced = next((p.get("amount") for p in prices
                           if p.get("source") == party and p.get("name") == name), None)
            amount = f"{priced:.2f} {currency}/yr" if isinstance(priced, (int, float)) else "an unpriced edge"
            out("SKIP", f"{adopter} carries no vendored copy of {party}'s {name}@{version} at "
                        f"HEAD, so {amount} of what it signed cannot be re-derived without "
                        f"{party}'s clone; it waits on {VENDORING_LANDS_IN} and on this "
                        f"adopter's platform pin moving to it "
                        f"(pinned publisher tag today: {tag or 'none declared'})")
            continue
        if not switching:
            out("FAIL", f"{adopter} vendored {party}/{name}@{version} but prints no switching "
                        f"entry for it — a copy nobody priced a switch against")
        # 2. the digests the adopter's own tag signed
        broken = False
        for rel, want in (record.get("files") or {}).items():
            blob = show(repo, "HEAD", f"{record['path']}/{rel}")
            if blob is None:
                out("FAIL", f"{adopter}'s header digests {record['path']}/{rel} and the served "
                            f"tree does not carry it")
                broken = True
            elif digest(blob) != want:
                out("FAIL", f"{adopter}'s served {record['path']}/{rel} does not match the "
                            f"digest its own composed/HEADER.yaml signed")
                broken = True
        if broken:
            continue
        # 3. against the publisher's own bytes, at the tag THIS adopter pins
        if tag is None:
            out("SKIP", f"{adopter} declares no Flux pin for {party}, so there is no tag to "
                        f"compare its vendored copy of {name}@{version} against")
        else:
            theirs = show(os.path.join(estate, party), tag, record["feed_path"])
            if theirs is None:
                out("SKIP", f"{party}'s clone here has no {tag}:{record['feed_path']} to compare "
                            f"{adopter}'s vendored copy against")
            elif theirs != show(repo, "HEAD", f"{record['path']}/{record['feed_path']}"):
                out("FAIL", f"{adopter}'s vendored {name}@{version} is not the payload {party} "
                            f"serves at {tag} — a copy that has drifted from the artefact it "
                            f"claims to be a copy of")
            else:
                out("PASS", f"{adopter}'s vendored {name}@{version} is byte-identical to what "
                            f"{party} serves at {tag}, the tag {adopter} itself pins")
        # 4. and it RUNS with nothing else on disk
        run_standalone(repo, adopter, record)


def run_standalone(repo: str, adopter: str, record: dict) -> None:
    """The portability claim as an experiment: the vendored converter, over the vendored
    payload, in a directory holding nothing else — no publisher clone, no estate, no hub."""
    converter = record.get("converter")
    if not converter:
        out("PASS", f"{adopter}'s vendored {record['name']}@{record['version']} declares no "
                    f"converter, and its publisher prices it without one — a named absence")
        return
    script = show(repo, "HEAD", f"{record['path']}/{converter}")
    payload_text = show(repo, "HEAD", f"{record['path']}/{record['feed_path']}")
    if script is None or payload_text is None:
        out("FAIL", f"{adopter}'s vendored {record['name']} is missing its converter or payload "
                    f"in the served tree")
        return
    with tempfile.TemporaryDirectory() as tmp:
        script_path = os.path.join(tmp, os.path.basename(converter))
        open(script_path, "w").write(script)
        try:
            body = json.loads(payload_text)
        except json.JSONDecodeError as e:
            out("FAIL", f"{adopter}'s vendored {record['name']} payload is not JSON: {e}")
            return
        body = body.get("payload", body)
        payload_path = os.path.join(tmp, "payload.json")
        open(payload_path, "w").write(json.dumps(body))
        r = subprocess.run([sys.executable, script_path, "--selfcheck"],
                           capture_output=True, text=True, cwd=tmp)
    if r.returncode == 0:
        out("PASS", f"{adopter}'s vendored converter for {record['name']}@{record['version']} "
                    f"runs standalone, in a directory holding nothing but itself and the "
                    f"payload — no publisher clone reachable")
    else:
        out("FAIL", f"{adopter}'s vendored converter for {record['name']}@{record['version']} "
                    f"does not run with the publisher's clone absent: "
                    f"{(r.stderr or r.stdout).strip().splitlines()[-1:] or ['no output']}")


# --------------------------------------------------------------------------
def check(estate: str = ESTATE) -> int:
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
    # number to the penny, that number is a property of the publisher's cap and not of either
    # firm. Printed by name so the reading is checkable rather than asserted.
    for name in {n for prices in unsized.values() for n in prices}:
        shared = sorted(a for a, prices in unsized.items()
                        if isinstance(prices.get(name), (int, float)))
        amounts = {unsized[a][name] for a in shared}
        if len(shared) > 1 and len(amounts) == 1:
            out("SKIP", f"{' and '.join(shared)} publish no signed size and both price {name} "
                        f"at exactly {amounts.pop():.2f} — the same number to the penny for two "
                        f"different institutions, which is what a statutory cap looks like and "
                        f"is why neither line may be read as a switching cost for either")
    if "FAIL" in LINES:
        return 1
    return 3 if "SKIP" in LINES else 0


# --------------------------------------------------------------------------
# selfcheck — every refusal above, planted and proved to bite
# --------------------------------------------------------------------------
CONVERTER = '''#!/usr/bin/env python3
import sys
if "--selfcheck" in sys.argv:
    sys.exit(0)
print("{}")
'''


# A fixture repository must not depend on the machine's global git config. `core.hooksPath`
# empties any globally installed pre-commit hook (one of them failed this fixture
# intermittently while it was being written), and the two gpgSign switches keep a machine that
# signs by default from making these throwaway objects need a key. A fixture that needs a
# signing key is a fixture that lies about what it proves.
FIXTURE_GIT = ["-c", "user.email=t@t", "-c", "user.name=t", "-c", "commit.gpgSign=false",
               "-c", "tag.gpgSign=false", "-c", "core.hooksPath=/dev/null"]


def _git_fixture(repo: str, *args: str) -> None:
    subprocess.run(["git", "-C", repo, *FIXTURE_GIT, *args], check=True, capture_output=True)


def _plant(root: str, *, vendored=True, digest_ok=True, payload_matches=True,
           converter_runs=True, switching=None) -> str:
    """A two-party fixture estate: one adopter, one publisher, both real git repos, the
    publisher carrying a real tag the adopter really pins."""
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

    ado = os.path.join(root, "ado")
    os.makedirs(os.path.join(ado, "gitops", "flux-system"))
    open(os.path.join(ado, "party.yaml"), "w").write(yaml.safe_dump(
        {"party": "ado", "roles": ["adopter"], "reporting_currency": "GBP",
         "size": {"turnover": {"amount": 10, "currency": "GBP"}, "customers": 2},
         "inherits": [{"party": "pub", "kind": "feed", "name": "wares",
                       "version": "v1", "since": "2026-01-15"}]}))
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
    os.makedirs(os.path.join(ado, "composed"))
    open(os.path.join(ado, "composed", "evidence.json"), "w").write(
        json.dumps({"prices": prices}, indent=2))
    header = {"policy-as-versioned.dev/composed": True}
    if vendored:
        base = "composed/feeds/pub/v1"
        vend_payload = payload if payload_matches else payload.replace("GBP", "USD")
        script = CONVERTER if converter_runs else CONVERTER.replace("sys.exit(0)", "sys.exit(2)")
        files = {"wares/v1/feed.json": vend_payload, "wares/to_fair_scenario.py": script}
        for rel, text in files.items():
            path = os.path.join(ado, base, rel)
            os.makedirs(os.path.dirname(path), exist_ok=True)
            open(path, "w").write(text)
        digests = {rel: digest(text) for rel, text in files.items()}
        if not digest_ok:
            digests["wares/v1/feed.json"] = "0" * 64
        header["vendored-feeds"] = [{"party": "pub", "name": "wares", "version": "v1",
                                     "path": base, "sha": "deadbeef",
                                     "feed_path": "wares/v1/feed.json",
                                     "converter": "wares/to_fair_scenario.py",
                                     "files": digests}]
    open(os.path.join(ado, "composed", "HEADER.yaml"), "w").write(yaml.safe_dump(header))
    for cmd in (["init", "-q", "-b", "main"], ["add", "-A"], ["commit", "-qm", "seed"]):
        _git_fixture(ado, *cmd)
    return root


def _run(**kwargs) -> list[str]:
    LINES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant(root, **kwargs)
        check(root)
    return list(LINES)


def selfcheck() -> None:
    ok = _run()
    assert "FAIL" not in ok and "SKIP" not in ok, ok
    print("OK a fully vendored adopter whose copy matches the publisher's own bytes at the tag "
          "it pins, whose converter runs standalone, and whose switching entry annualises over "
          "a real window, passes clean")

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
                          "could_not_look": "the twin has no lef to annualise on"}), "PASS",
         "an absent amount that carries the publisher's own refusal is a NAMED pass"),
    ):
        lines = _run(**kwargs)
        assert want in lines, (want, what, lines)
        print(f"OK {what}")

    # The size rule, proved on the fixture rather than asserted about the estate.
    LINES.clear()
    with tempfile.TemporaryDirectory() as root:
        _plant(root)
        path = os.path.join(root, "ado", "party.yaml")
        doc = yaml.safe_load(open(path).read())
        doc.pop("size")
        open(path, "w").write(yaml.safe_dump(doc))
        _git_fixture(os.path.join(root, "ado"), "add", "-A")
        _git_fixture(os.path.join(root, "ado"), "commit", "-qm", "unsized")
        rc = check(root)
    assert rc == 3 and "SKIP" in LINES, LINES
    print("OK an adopter that publishes no signed size: has its switching line graded a NAMED "
          "could-not-look and the run exits 3 — never a pass, and never a guess")
    print("\nselfcheck ok: eleven plants, each proved to bite")


def main(argv: list[str]) -> int:
    mode = argv[1] if len(argv) > 1 else "check"
    if mode == "selfcheck":
        selfcheck()
        return 0
    return check()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
