#!/usr/bin/env python3
"""feed_contract.py — ADR-0019 made checkable: every published feed is one envelope
(platform/feeds/schema.json) and every adopter subscription (inherits[]) resolves to a
publisher's publishes[] record and to a tag on the publisher's REAL remote.

Prints one line per check. Exit precedence: any FAIL -> 1; else any SKIP -> 3; else 0.
Needs jsonschema + pyyaml (hub .venv); verify-feed-contract.sh picks the interpreter.

Usage:
    feed_contract.py check                 # the whole estate
    feed_contract.py newest <party> <name> # one publisher's newest local envelope + its tag
    feed_contract.py selfcheck             # planted fixtures: proves each refusal bites
"""
from __future__ import annotations

import glob
from datetime import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

import yaml
from jsonschema import Draft7Validator

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
from _estate import ESTATE  # noqa: E402

REMOTE = "https://github.com/policy-as-versioned-{p}/{p}"
LINES: list[str] = []
SEEN = {"publishers": 0, "adopters": 0, "envelopes": 0}


def out(status, msg):
    LINES.append(status)
    print(f"{status}: {msg}")


def load_yaml(path):
    with open(path) as fh:
        return yaml.safe_load(fh) or {}


def load_json(path):
    with open(path) as fh:
        return json.load(fh)


def parties(estate):
    """{name: party.yaml dict} for every unit that has one."""
    found = {}
    for p in sorted(glob.glob(os.path.join(estate, "*", "party.yaml"))):
        found[os.path.basename(os.path.dirname(p))] = load_yaml(p)
    return found


def errors(schema, doc):
    return [e.message for e in Draft7Validator(schema).iter_errors(doc)]


def tag_forms(entry, version):
    """The tag shapes a publisher may sign this pin with. `<name>/vX.Y.Z` (feeds, and the
    platform's policy/vX.Y.Z line) or bare `vX.Y.Z` (single-feed repos: ico, nist). Both are
    tried and the PASS line says which one matched. A bare-major pin ('v1') resolves to ANY
    signed tag of that major (v1.x.y) -- no workflow cuts a literal 'v1'."""
    v = version.lstrip("v")
    ver = re.escape(v) if "." in v else rf"{re.escape(v)}\.\d+\.\d+"
    return re.compile(rf"^(?:{re.escape(entry['name'])}/)?v{ver}$")


def match_tag(entry, version, tags):
    """The highest remote tag that signs this pin, or None."""
    hits = [t for t in tags if tag_forms(entry, version).match(t)]
    return max(hits, key=lambda t: [int(x) for x in t.rsplit("v", 1)[1].split(".")]) if hits else None


def newest_tag_per_line(publisher, tags):
    """Ticket 76 item 3: the newest tag on each line a publisher's own publishes[] declares,
    in that line's own shape (`<name>/vX.Y.Z` or bare `vX.Y.Z`, the same two forms tag_forms
    admits) -- never a shape typed by the caller. `{name: tag or None}`; None means no tag of
    either shape exists in `tags`, which the caller reports as what was looked for and not found,
    not as an absence inferred from a pattern that could not match."""
    out = {}
    for entry in publisher.get("publishes") or []:
        shape = re.compile(rf"^(?:{re.escape(entry['name'])}/)?v\d+\.\d+\.\d+$")
        hits = [t for t in tags if shape.match(t)]
        out[entry["name"]] = (max(hits, key=lambda t: [int(x) for x in t.rsplit("v", 1)[1].split(".")])
                              if hits else None)
    return out


_TAGS: dict[str, set | None] = {}


def remote_tags(party):
    """Tags on the party's real remote; None if unreachable. Cached per run."""
    if party not in _TAGS:
        r = subprocess.run(["git", "ls-remote", "--tags", REMOTE.format(p=party)],
                           capture_output=True, text=True, timeout=60)
        _TAGS[party] = None if r.returncode else {
            l.split("refs/tags/")[1].removesuffix("^{}") for l in r.stdout.splitlines() if "refs/tags/" in l}
    return _TAGS[party]


def local_version(estate, party, entry, version):
    """The envelope version queued on the branch for this pin (cut-release.yml cuts that
    exact vX.Y.Z), or None."""
    v = version.lstrip("v")
    major = v.split(".")[0]
    if entry["kind"] != "feed":
        return None  # ponytail: controls/implementations have no v<MAJOR>/feed.json; a tag is the only proof
    f = os.path.join(estate, party, entry["path"], f"v{major}", "feed.json")
    if not os.path.isfile(f):
        return None
    env_v = str(load_json(f).get("version", ""))
    # a bare major pin ('v1') matches any local vMAJOR envelope; full semver must match exactly
    return env_v if (env_v == v if "." in v else env_v.split(".")[0] == major) else None


def check_tag(estate, party, publisher, entry, version, label):
    tags = remote_tags(party)
    if tags is None:
        out("SKIP", f"{label}: could not reach {REMOTE.format(p=party)}"); return
    hit = match_tag(entry, version, tags)
    if hit:
        out("PASS", f"{label}: tag {hit} on {party}"); return
    queued = local_version(estate, party, entry, version)
    if queued:
        want = f"{entry['name']}/v{queued}" if len(publisher.get("publishes", [])) > 1 else f"v{queued}"
        out("SKIP", f"{label}: waiting for tag {want} on {party} (cut by cut-release.yml after merge)")
    else:
        out("FAIL", f"{label}: no tag for {version} on {party} and no local file for it")


def check_envelope(estate, party, entry, feed_file, envelope_schema):
    label = f"{party}/{os.path.relpath(feed_file, os.path.join(estate, party))}"
    try:
        doc = load_json(feed_file)
    except (OSError, ValueError) as e:
        out("FAIL", f"{label}: unreadable ({e})"); return None
    errs = errors(envelope_schema, doc)
    for k in ("kind", "name"):
        if doc.get(k) != entry.get(k):
            errs.append(f"{k} {doc.get(k)!r} != publishes[] {entry.get(k)!r}")
    if doc.get("published_by") != party:
        errs.append(f"published_by {doc.get('published_by')!r} != {party!r}")
    try:  # draft-07 `format` is advisory; the regex admits month 13
        datetime.fromisoformat(str(doc.get("published_at", "")).replace("Z", "+00:00"))
    except ValueError:
        errs.append(f"published_at {doc.get('published_at')!r} is not a real date-time")
    if errs:
        out("FAIL", f"{label}: envelope: " + "; ".join(errs)); return None
    out("PASS", f"{label}: envelope valid ({doc['kind']}/{doc['name']} {doc['version']})")
    ps = doc.get("payload_schema") or entry.get("payload_schema", "")  # the envelope names its own schema; an old major may predate the record's
    if re.match(r"^[a-z]+://", ps):
        out("SKIP", f"{label}: payload_schema is a URL ({ps}); not fetched offline")
    else:
        sp = os.path.join(estate, party, ps)
        if not os.path.isfile(sp):
            out("FAIL", f"{label}: payload_schema {ps} missing")
        else:
            perrs = errors(load_json(sp), doc.get("payload", {}))
            out("FAIL" if perrs else "PASS", f"{label}: payload vs {ps}" + ("; ".join([""] + perrs) if perrs else ""))
    d = os.path.join(estate, party, entry["path"])  # one location: <name>/rule.yaml, <name>/bump.yaml (the next-release bump is per feed, not per major)
    for side in ("rule.yaml", "bump.yaml"):
        sf = os.path.join(d, side)
        if not os.path.isfile(sf):
            out("FAIL", f"{label}: {entry['path']}/{side} missing"); continue
        if side == "bump.yaml":
            b = load_yaml(sf).get("bump")
            out("PASS" if b in ("major", "minor", "patch", "none") else "FAIL", f"{label}: bump.yaml bump={b}")
    return doc


def check_publisher(estate, party, doc, envelope_schema, party_schema):
    perrs = errors(party_schema, doc)
    out("FAIL" if perrs else "PASS", f"{party}/party.yaml vs party schema" + ("; ".join([""] + perrs) if perrs else ""))
    pubs = doc.get("publishes") or []
    if not pubs:
        out("FAIL", f"{party}: role publisher but publishes[] is empty")
    for entry in pubs:
        path = os.path.join(estate, party, entry.get("path", ""))
        if entry.get("kind") != "feed":
            out("PASS" if os.path.exists(path) else "FAIL", f"{party}: publishes {entry.get('kind')} at {entry.get('path')}")
            continue
        if entry.get("payload_schema", "") is None:
            # A feed record that declares NO payload schema is a section of this party's own
            # signed artefact rather than an ADR-0019 envelope -- the adopter's `exposure`, which
            # composition renders into composed/HEADER.yaml and the party's own tag signs. There
            # is no v*/feed.json to validate; what is checkable is that the section is really
            # there, which is what a consumer pinning it is pinning.
            section = os.path.join(path, "HEADER.yaml")
            present = os.path.isfile(section) and \
                isinstance((load_yaml(section) or {}).get(entry.get("name")), (dict, list))
            out("PASS" if present else "FAIL",
                f"{party}: publishes {entry.get('name')} as a section of {entry.get('path')}/"
                f"HEADER.yaml, signed by this party's own tag and not an envelope of its own"
                + ("" if present else " -- and HEADER.yaml carries no such section"))
            continue
        files = sorted(glob.glob(os.path.join(path, "v*", "feed.json")))
        if not files:
            # a declared feed with nothing published yet (insurer/quote until ticket 36): could not look, never PASS
            out("SKIP" if os.path.isdir(path) else "FAIL",
                f"{party}: feed {entry.get('name')} has no {entry.get('path')}/v*/feed.json yet")
        for f in files:
            SEEN["envelopes"] += 1
            check_envelope(estate, party, entry, f, envelope_schema)


def resolve(all_parties, inh):
    pub = all_parties.get(inh.get("party"), {})
    if "publisher" not in (pub.get("roles") or []):
        return pub, None
    for e in pub.get("publishes") or []:
        if e.get("kind") == inh.get("kind") and (inh.get("kind") != "feed" or e.get("name") == inh.get("name")):
            return pub, e
    return pub, None


def check_adopter(estate, party, doc, all_parties):
    for inh in doc.get("inherits") or []:
        label = f"{party} pins {inh.get('party')}/{inh.get('kind')}" + (f"/{inh['name']}" if inh.get("name") else "") + f"@{inh.get('version')}"
        pub, entry = resolve(all_parties, inh)
        if entry is None:
            out("FAIL", f"{label}: no matching publishes[] record on {inh.get('party')}/party.yaml"); continue
        if str(inh.get("version")).lstrip("v") in [str(r).lstrip("v") for r in entry.get("revoked") or []]:
            out("PASS", f"{label}: revoked by publisher (a priced hole, never a refusal)")
        check_tag(estate, inh["party"], pub, entry, str(inh["version"]), label)


def run(estate):
    env_path = os.path.join(estate, "platform", "feeds", "schema.json")
    party_path = os.path.join(estate, "platform", "party", "schema.json")
    for p in (env_path, party_path):
        if not os.path.isfile(p):
            out("FAIL", f"{p} missing"); return
    for k in SEEN:
        SEEN[k] = 0
    envelope_schema, party_schema = load_json(env_path), load_json(party_path)
    all_parties = parties(estate)
    for name, doc in all_parties.items():
        if "publisher" in (doc.get("roles") or []):
            SEEN["publishers"] += 1
            check_publisher(estate, name, doc, envelope_schema, party_schema)
    for name, doc in all_parties.items():
        if "adopter" in (doc.get("roles") or []):
            SEEN["adopters"] += 1
    # Every party that pins anything, not only the ones whose roles say "adopter". The insurer's
    # roles are [publisher, insurer], so its four pins were never resolved by anything: it pinned
    # an `exposure` feed at a version no adopter had ever published, and 65 PASS/SKIP lines went
    # by without one of them naming an insurer pin (found 2026-08-29). A pin nobody resolves is
    # not a pass, it is an unvisited line.
    for name, doc in all_parties.items():
        if doc.get("inherits"):
            check_adopter(estate, name, doc, all_parties)
    for k, n in SEEN.items():
        if not n:
            out("FAIL", f"no {k} observed under {estate}: absence is not a pass")


def newest(estate, party, name):
    """One publisher's highest local v<MAJOR>/feed.json: envelope valid + tag on the real remote."""
    all_parties = parties(estate)
    pub = all_parties.get(party)
    entry = next((e for e in (pub or {}).get("publishes") or [] if e.get("name") == name), None)
    if entry is None:
        out("FAIL", f"{party}/party.yaml has no publishes[] entry named {name}"); return
    files = glob.glob(os.path.join(estate, party, entry["path"], "v*", "feed.json"))
    if not files:
        out("FAIL", f"{party}: no {entry['path']}/v*/feed.json"); return
    f = max(files, key=lambda p: int(re.sub(r"\D", "", os.path.basename(os.path.dirname(p))) or 0))
    env_path = os.path.join(estate, "platform", "feeds", "schema.json")
    if not os.path.isfile(env_path):
        out("FAIL", f"{env_path} missing"); return
    doc = check_envelope(estate, party, entry, f, load_json(env_path))
    if doc:
        check_tag(estate, party, pub, entry, str(doc["version"]), f"{party}/{name}@{doc['version']}")


def exit_code():
    return 1 if "FAIL" in LINES else 3 if "SKIP" in LINES else 0


def selfcheck():
    """Plant a two-party estate in a temp dir and prove the refusals bite. Offline: the remote
    lookup is stubbed."""
    global _TAGS
    envelope = {"type": "object", "additionalProperties": False,
                "required": ["kind", "name", "version", "published_by", "published_at", "payload_schema", "payload"],
                "properties": {"kind": {"enum": ["feed", "controls", "implementations"]}, "name": {"type": "string"},
                               "version": {"type": "string", "pattern": r"^\d+\.\d+\.\d+$"}, "published_by": {"type": "string"},
                               "published_at": {"type": "string"}, "payload_schema": {"type": "string"}, "payload": {"type": "object"}}}
    party_schema = {"type": "object"}
    with tempfile.TemporaryDirectory() as tmp:
        def w(rel, obj, as_yaml=False):
            p = os.path.join(tmp, rel); os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as fh:
                (yaml.safe_dump if as_yaml else json.dump)(obj, fh)
        w("platform/feeds/schema.json", envelope); w("platform/party/schema.json", party_schema)
        w("ico/party.yaml", {"party": "ico", "roles": ["publisher"], "publishes": [
            {"kind": "feed", "name": "penalty-schema", "path": "penalty-schema", "payload_schema": "penalty-schema/payload.schema.json"}]}, True)
        w("ico/penalty-schema/payload.schema.json", {"type": "object", "required": ["fine"]})
        w("ico/penalty-schema/v1/feed.json", {"kind": "feed", "name": "penalty-schema", "version": "1.0.0", "published_by": "ico",
                                              "published_at": "2026-08-28T00:00:00Z", "payload_schema": "penalty-schema/payload.schema.json", "payload": {"fine": 1}})
        w("ico/penalty-schema/rule.yaml", {"changed": "any"}, True); w("ico/penalty-schema/bump.yaml", {"bump": "none"}, True)
        w("platform/party.yaml", {"party": "platform", "roles": ["publisher"], "publishes": [
            {"kind": "implementations", "name": "policy", "path": "feeds"}]}, True)
        w("ico/penalty-schema/v2/feed.json", {"kind": "feed", "name": "penalty-schema", "version": "2.0.0", "published_by": "ico",
                                              "published_at": "2026-08-28T00:00:00Z", "payload_schema": "penalty-schema/payload.schema.json", "payload": {"fine": 2}})
        w("driftwood/party.yaml", {"party": "driftwood", "roles": ["adopter"], "inherits": [
            {"party": "ico", "kind": "feed", "name": "penalty-schema", "version": "v1"},   # bare major -> v1.0.0 tagged
            {"party": "platform", "kind": "implementations", "version": "3.0.0"},         # policy/v3.0.0 tagged
            {"party": "platform", "kind": "implementations", "version": "4.0.0"},         # no tag, no local file -> FAIL
            {"party": "ico", "kind": "feed", "name": "penalty-schema", "version": "2.0.0"},  # local only -> queued
            {"party": "ico", "kind": "feed", "name": "penalty-schema", "version": "9.0.0"},  # nowhere -> FAIL
            {"party": "ico", "kind": "feed", "name": "nope", "version": "1.0.0"}]}, True)   # no record -> FAIL
        _TAGS = {"ico": {"v1.0.0"}, "platform": {"policy/v3.0.0", "v1.1.1"}}
        run(tmp)
        assert LINES.count("FAIL") == 3 and "SKIP" in LINES, LINES
        assert match_tag({"name": "penalty-schema"}, "v1", {"v1.0.0", "v1.2.0", "v2.0.0"}) == "v1.2.0"
        # ticket 76 item 3: each published line's newest tag, in that line's own shape. feeds'
        # threat-register/v2.0.0 is what `git tag -l 'v*.*.*'` could never match.
        feeds = {"publishes": [{"name": "threat-register"}, {"name": "cve"}]}
        assert newest_tag_per_line(feeds, {"threat-register/v1.0.0", "threat-register/v2.0.0"}) \
            == {"threat-register": "threat-register/v2.0.0", "cve": None}
        assert newest_tag_per_line({"publishes": [{"name": "policy"}, {"name": "identity-substrate"}]},
                                   {"v1.0.0", "v2.0.1", "v2.0.0"}) \
            == {"policy": "v2.0.1", "identity-substrate": "v2.0.1"}, "a bare tag signs every line"
        assert newest_tag_per_line({"publishes": [{"name": "x"}]}, {"x/v1.0.0", "y/v9.9.9", "v1"}) \
            == {"x": "x/v1.0.0"}, "another line's tag and a bare major are not this line's"
        # an empty estate is not a pass
        LINES.clear()
        os.makedirs(os.path.join(tmp, "empty", "platform"))
        w("empty/platform/feeds/schema.json", envelope); w("empty/platform/party/schema.json", party_schema)
        run(os.path.join(tmp, "empty"))
        assert LINES and set(LINES) == {"FAIL"}, LINES
        # a bad envelope bites
        LINES.clear()
        w("ico/penalty-schema/v2/feed.json", {"kind": "feed", "name": "penalty-schema", "version": "2.0.0", "published_by": "ico",
                                              "published_at": "x", "payload_schema": "penalty-schema/payload.schema.json", "payload": {}, "signature": "no"})
        newest(tmp, "ico", "penalty-schema")
        assert LINES == ["FAIL"], LINES
        # unreachable remote -> SKIP, never PASS
        LINES.clear(); _TAGS = {"ico": None}
        check_tag(tmp, "ico", load_yaml(os.path.join(tmp, "ico/party.yaml")), {"kind": "feed", "name": "penalty-schema", "path": "penalty-schema"}, "v1", "x")
        assert LINES == ["SKIP"], LINES
    LINES.clear()
    print("ok  selfcheck: envelope, payload, sidecars, unresolved record, missing tag, bare-major and policy/ tags, queued tag, unreachable remote, empty estate all graded")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "check"
    if cmd == "selfcheck":
        selfcheck(); sys.exit(0)
    if cmd == "newest":
        newest(ESTATE, sys.argv[2], sys.argv[3])
    else:
        run(ESTATE)
    sys.exit(exit_code())
