#!/usr/bin/env python3
"""Eco-system ticket 105. The committed trust roots are dated, and they carry what is served.

Ticket 101 pinned ludlow's Sigstore trust material in one committed trusted_root.json; ticket 105
put the same pin in driftwood and tuppence, so every adopter gate now verifies platform's evidence
with a cold TUF cache and no egress. The price of a pin is that it goes stale: a root that lacks a
key for the log an artefact names REFUSES BY NAME, which is the right failure and a real
maintenance obligation -- Sigstore rotating a log turns three required checks red until three
pull requests land. This check turns that from a surprise into a schedule.

WHAT IS PRINTED, AS NUMBERS AND DATES, NEVER GRADED: per adopter, the sha256 of the committed
root, the date it was committed and how many days ago, the date the newest log key in it starts
and how many days ago, and every key's validity window against today (current / retired N days
ago / not yet valid). Whether the adopters' copies are byte-identical is printed as a fact, not
graded: during a rotation one institution refreshes before the others, and that is a transient,
not a defect. Any sentence of the form "the root is fresh" would go stale the day it is written,
so none is printed.

WHAT IS GRADED, BECAUSE IT CANNOT GO STALE IN THE REASSURING DIRECTION:

  served artefact   platform's own committed computed-semver/evidence/<version>.json.bundle at the
                    tag THAT ADOPTER pins -- the Fulcio certificate's own embedded SCT log ids and
                    timestamps, read out of the DER, and the Rekor log id and integrated time out
                    of the bundle's own rekorBundle. Read at the tag, never from a working tree.
  operation         the adopter's own committed .github/scripts/trusted_root.json at its HEAD --
                    the file its gate hands cosign through --trusted-root -- read with `git show`,
                    never from a working tree.

The sentence: every log platform's evidence at that adopter's pin names is carried by that
adopter's committed root, by key id, with the artefact's own timestamp inside that key's validFor
window. The day it is false the adopter's gate refuses by name, so this line is red before a
Renovate pull request is. A root that is absent is a could-not-look BY NAME, never a pass.

Usage:
    trust_root.py <estate-dir>
    trust_root.py --selfcheck
"""
from __future__ import annotations

import base64
import binascii
import hashlib
import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

import yaml

HERE = Path(__file__).resolve().parent
ROOT_PATH = ".github/scripts/trusted_root.json"
PIN_PATH = "gitops/platform/platform-pin.yaml"
EVIDENCE_DIR = "computed-semver/evidence"

# 1.3.6.1.4.1.11129.2.4.2 -- RFC 6962's SignedCertificateTimestampList extension, as it appears in
# DER: the OID, then the extnValue OCTET STRING. The same bytes ludlow's gate keyed on in ticket 101.
SCT_EXTENSION_OID_DER = bytes.fromhex("060a2b06010401d679020402")


# --------------------------------------------------------------------------------------------
# pure
# --------------------------------------------------------------------------------------------
class LogKey(NamedTuple):
    kind: str            # "ctlog", "tlog" or "ca"
    name: str            # the log's baseUrl, or the CA's uri
    key_id: str          # lowercase hex of the log id (sha256 of the key's DER); "" for a CA
    key_type: str        # keyDetails as the root states it; "" for a CA
    start: datetime | None
    end: datetime | None


def _parse_time(text: str | None) -> datetime | None:
    if not text:
        return None
    text = text.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)


def _read_der_octet_string(data: bytes, pos: int) -> bytes:
    if pos >= len(data) or data[pos] != 0x04:
        raise ValueError("expected a DER OCTET STRING")
    n = data[pos + 1]
    pos += 2
    if n & 0x80:
        k = n & 0x7F
        n = int.from_bytes(data[pos:pos + k], "big")
        pos += k
    return data[pos:pos + n]


def sct_entries(cert_der: bytes) -> list[tuple[str, datetime]]:
    """Every embedded SCT's log id (lowercase hex) and timestamp, read out of the certificate's own
    DER -- the artefact names its own ruler, and nothing the publisher supplies at verification
    time is consulted. [] when the certificate carries no SCT extension."""
    i = cert_der.find(SCT_EXTENSION_OID_DER)
    if i < 0:
        return []
    try:
        inner = _read_der_octet_string(_read_der_octet_string(cert_der, i + len(SCT_EXTENSION_OID_DER)), 0)
        total = int.from_bytes(inner[:2], "big")
        pos, end, out = 2, 2 + total, []
        while pos < end:
            n = int.from_bytes(inner[pos:pos + 2], "big")
            sct = inner[pos + 2:pos + 2 + n]
            pos += 2 + n
            if len(sct) >= 41:
                millis = int.from_bytes(sct[33:41], "big")
                out.append((sct[1:33].hex(), datetime.fromtimestamp(millis / 1000, tz=timezone.utc)))
        return out
    except (ValueError, IndexError, OverflowError):
        return []


def _hex_id(key_id_b64: str) -> str:
    try:
        return base64.b64decode(key_id_b64).hex()
    except (ValueError, binascii.Error):
        return ""


def root_keys(root_doc: dict) -> list[LogKey]:
    """Every key the committed root carries, with the window the root itself states for it."""
    keys: list[LogKey] = []
    for kind, field in (("tlog", "tlogs"), ("ctlog", "ctlogs")):
        for entry in root_doc.get(field) or []:
            public = entry.get("publicKey") or {}
            window = public.get("validFor") or {}
            keys.append(LogKey(kind, entry.get("baseUrl") or "?", _hex_id(((entry.get("logId") or {}).get("keyId")) or ""),
                               public.get("keyDetails") or "", _parse_time(window.get("start")), _parse_time(window.get("end"))))
    for ca in root_doc.get("certificateAuthorities") or []:
        window = ca.get("validFor") or {}
        keys.append(LogKey("ca", ca.get("uri") or "?", "", "", _parse_time(window.get("start")), _parse_time(window.get("end"))))
    return keys


def _day(at: datetime) -> str:
    return at.date().isoformat()


def window_status(start: datetime | None, end: datetime | None, at: datetime) -> str:
    """A date and a number, never an adjective on its own."""
    if start is not None and at < start:
        return f"not yet valid (starts {_day(start)}, in {(start - at).days} days)"
    if end is not None and at > end:
        return f"retired {_day(end)} ({(at - end).days} days ago)"
    since = f" since {_day(start)} ({(at - start).days} days)" if start is not None else ""
    return f"current{since}" + (f", until {_day(end)}" if end is not None else "")


def carries(keys: list[LogKey], kind: str, key_id: str, at: datetime) -> LogKey | None:
    """The key of this kind and id whose window covers `at`, or None. A key outside its window is
    not carried for this artefact: sigstore-go skips it, and so does this."""
    for key in keys:
        if key.kind != kind or key.key_id != key_id:
            continue
        if key.start is not None and at < key.start:
            continue
        if key.end is not None and at > key.end:
            continue
        return key
    return None


def newest_start(keys: list[LogKey]) -> datetime | None:
    starts = [k.start for k in keys if k.kind in ("tlog", "ctlog") and k.start is not None]
    return max(starts) if starts else None


def grade(observations: dict[str, dict], today: datetime) -> tuple[str, list[tuple[str, str]]]:
    """observations: unit -> {"pin": tag, "root": None | {"sha", "committed", "keys"}, "reason",
    "artefacts": [{"version", "logs": [{"kind", "id", "at"}]}]}."""
    lines: list[tuple[str, str]] = []
    bad = unknown = 0
    shas: dict[str, str] = {}
    for unit in sorted(observations):
        obs = observations[unit]
        root = obs.get("root")
        if root is None:
            unknown += 1
            lines.append(("SKIP", f"{unit}: could not look -- {obs.get('reason') or 'no committed trust root'}"))
            continue
        shas[unit] = root["sha"]
        keys: list[LogKey] = root["keys"]
        committed = root.get("committed")
        age = (f"committed {_day(committed)} ({(today - committed).days} days ago)" if committed is not None
               else "commit date unknown")
        newest = newest_start(keys)
        newest_text = (f"newest log key starts {_day(newest)} ({(today - newest).days} days ago)" if newest is not None
                       else "no log key states a start date")
        lines.append(("note", f"{unit}: committed trust root sha256 {root['sha'][:12]}, {age}; {newest_text}; "
                              f"pins platform {obs.get('pin') or '?'}"))
        for key in keys:
            ident = f" key {key.key_id[:16]}" if key.key_id else ""
            kind = f" {key.key_type}" if key.key_type else ""
            lines.append(("note", f"{unit}:   {key.kind} {key.name}{ident}{kind}: "
                                  f"{window_status(key.start, key.end, today)}"))
        for artefact in obs.get("artefacts") or []:
            logs = artefact.get("logs")
            if logs is None:
                bad += 1
                lines.append(("FAIL", f"{unit}: platform's evidence bundle for policy {artefact.get('version')} at "
                                      f"{obs.get('pin')} could not be read as a bundle of either shape, so the logs "
                                      f"it names could not be derived -- an unreadable served artefact is not a pass, "
                                      f"and this adopter's gate refuses it by name too"))
                continue
            if not logs:
                bad += 1
                lines.append(("FAIL", f"{unit}: platform's evidence for policy {artefact.get('version')} at "
                                      f"{obs.get('pin')} names no transparency log and no certificate-transparency "
                                      f"log at all, so there is nothing for the committed root to carry and "
                                      f"nothing a pin could verify"))
                continue
            for log in logs:
                carried = carries(keys, log["kind"], log["id"], log["at"])
                if carried is not None:
                    lines.append(("ok", f"{unit}: policy {artefact.get('version')} names {log['kind']} "
                                        f"{log['id'][:16]} at {log['at'].isoformat(timespec='seconds')}; the "
                                        f"committed root carries it ({carried.name}), inside its window"))
                    continue
                bad += 1
                pinned = [k for k in keys if k.kind == log["kind"] and k.key_id == log["id"]]
                if pinned:
                    k = pinned[0]
                    lines.append(("FAIL", f"{unit}: platform's evidence for policy {artefact.get('version')} names "
                                          f"{log['kind']} {log['id'][:16]} at {log['at'].isoformat(timespec='seconds')}, "
                                          f"and the committed root carries that key ({k.name}) but its validFor window "
                                          f"({_day(k.start) if k.start else '?'} .. {_day(k.end) if k.end else 'open'}) "
                                          f"does not cover the artefact's timestamp {_day(log['at'])} -- the gate will "
                                          f"refuse this evidence"))
                else:
                    lines.append(("FAIL", f"{unit}: platform's evidence for policy {artefact.get('version')} names "
                                          f"{log['kind']} {log['id'][:16]} and the committed root carries no key for it "
                                          f"-- the pinned trust root has gone stale for the artefact this adopter "
                                          f"pins, and the gate will refuse by name until {ROOT_PATH} is refreshed"))
    if len(shas) >= 2:
        if len(set(shas.values())) == 1:
            lines.append(("note", f"the {len(shas)} adopters' committed roots are byte-identical "
                                  f"(sha256 {next(iter(shas.values()))[:12]})"))
        else:
            lines.append(("note", "the committed roots differ: "
                                  + ", ".join(f"{u} {s[:12]}" for u, s in sorted(shas.items()))
                                  + " -- a fact, not a failure: a rotation lands one institution at a time"))
    if bad:
        return "FAIL", lines + [("FAIL", f"{bad} named log(s) that platform's evidence at an adopter's pin names "
                                          f"and that adopter's committed trust root does not carry inside the "
                                          f"key's window -- each named above")]
    if unknown:
        return "SKIP", lines + [("SKIP", f"{unknown} adopter(s) could not be looked at -- each named above -- so "
                                          f"the estate has not been observed whole")]
    return "PASS", lines


# --------------------------------------------------------------------------------------------
# the estate
# --------------------------------------------------------------------------------------------
def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)


def _show(repo: Path, ref: str, path: str) -> str | None:
    proc = _git(repo, "show", f"{ref}:{path}")
    return proc.stdout if proc.returncode == 0 else None


def _pinned_tag(pin_text: str) -> str | None:
    try:
        for doc in yaml.safe_load_all(pin_text):
            if isinstance(doc, dict) and doc.get("kind") == "GitRepository":
                return ((doc.get("spec") or {}).get("ref") or {}).get("tag")
    except yaml.YAMLError:
        return None
    return None


def _cert_der(bundle: dict) -> bytes | None:
    raw = bundle.get("cert")
    if raw is None:
        material = bundle.get("verificationMaterial") or {}
        chain = (material.get("x509CertificateChain") or {}).get("certificates") or []
        raw = (material.get("certificate") or {}).get("rawBytes") or (chain[0].get("rawBytes") if chain else None)
    if not raw:
        return None
    try:
        der = base64.b64decode(raw)
        if der.lstrip().startswith(b"-----BEGIN"):
            der = base64.b64decode("".join(l for l in der.decode().splitlines() if "-----" not in l))
        return der
    except (ValueError, binascii.Error, UnicodeDecodeError):
        return None


def artefact_logs(bundle_text: str) -> list[dict] | None:
    """The logs a published bundle names, of either shape. None when the bundle cannot be read."""
    try:
        bundle = json.loads(bundle_text)
    except json.JSONDecodeError:
        return None
    if not isinstance(bundle, dict):
        return None
    der = _cert_der(bundle)
    if der is None:
        return None
    logs = [{"kind": "ctlog", "id": log_id, "at": at} for log_id, at in sct_entries(der)]
    payload = (bundle.get("rekorBundle") or {}).get("Payload") or {}
    if payload.get("logID") and payload.get("integratedTime"):
        logs.append({"kind": "tlog", "id": str(payload["logID"]).lower(),
                     "at": datetime.fromtimestamp(int(payload["integratedTime"]), tz=timezone.utc)})
    for entry in ((bundle.get("verificationMaterial") or {}).get("tlogEntries") or []):
        key_id = ((entry.get("logId") or {}).get("keyId")) or ""
        if key_id and entry.get("integratedTime"):
            logs.append({"kind": "tlog", "id": _hex_id(key_id),
                         "at": datetime.fromtimestamp(int(entry["integratedTime"]), tz=timezone.utc)})
    return logs


def observe(estate: Path, units: list[str]) -> dict[str, dict]:
    platform = estate / "platform"
    observations: dict[str, dict] = {}
    for unit in units:
        unit_dir = estate / unit
        obs: dict = {"pin": None, "root": None, "reason": "", "artefacts": []}
        observations[unit] = obs
        root_text = _show(unit_dir, "HEAD", ROOT_PATH)
        if root_text is None:
            obs["reason"] = f"{unit} commits no {ROOT_PATH} at HEAD, so there is no pinned trust root to date"
            continue
        try:
            root_doc = json.loads(root_text)
            if not isinstance(root_doc, dict):
                raise ValueError("not an object")
        except (json.JSONDecodeError, ValueError) as exc:
            obs["reason"] = f"{unit}'s committed {ROOT_PATH} is not a readable trusted root ({exc})"
            continue
        when = _git(unit_dir, "log", "-1", "--format=%cI", "--", ROOT_PATH).stdout.strip()
        obs["root"] = {"sha": hashlib.sha256(root_text.encode()).hexdigest(),
                       "committed": _parse_time(when) if when else None, "keys": root_keys(root_doc)}
        pin_text = _show(unit_dir, "HEAD", PIN_PATH)
        tag = _pinned_tag(pin_text) if pin_text is not None else None
        if not tag:
            obs["root"], obs["reason"] = None, (f"{unit} pins no platform tag in {PIN_PATH} at HEAD, so there is "
                                                f"no served artefact to hold its committed root against")
            continue
        obs["pin"] = tag
        if _git(platform, "rev-parse", "-q", "--verify", f"refs/tags/{tag}^{{commit}}").returncode != 0:
            obs["root"], obs["reason"] = None, (f"this checkout of platform has no tag object for {tag}, the tag "
                                                f"{unit} pins, so the artefact it serves could not be read")
            continue
        listing = _git(platform, "ls-tree", "--name-only", f"refs/tags/{tag}", f"{EVIDENCE_DIR}/").stdout.split()
        bundles = sorted(p for p in listing if p.endswith(".json.bundle"))
        if not bundles:
            obs["root"], obs["reason"] = None, (f"platform at {tag} publishes no evidence bundle under "
                                                f"{EVIDENCE_DIR}/, so there is no served artefact naming a log")
            continue
        for path in bundles:
            version = path.rsplit("/", 1)[-1][:-len(".json.bundle")]
            text = _show(platform, f"refs/tags/{tag}", path) or ""
            logs = artefact_logs(text)
            obs["artefacts"].append({"version": version, "logs": logs})
    return observations


def run(estate: Path, today: datetime) -> tuple[str, list[tuple[str, str]]]:
    estate = estate.resolve()
    spec = importlib.util.spec_from_file_location("twin_per_adopter", HERE.parent / "twin-per-adopter" / "twin_per_adopter.py")
    assert spec is not None and spec.loader is not None, "cannot load twin_per_adopter.py"
    tpa = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tpa)
    units = [u for u in tpa.adopters(estate) if (estate / u).is_dir()]
    if not units:
        return "SKIP", [("SKIP", "no party in this estate claims the adopter role, so there is no adopter gate "
                                  "whose trust root could be dated")]
    if not (estate / "platform" / ".git").is_dir():
        return "SKIP", [("SKIP", "this checkout carries no clone of platform, whose published evidence is the only "
                                  "artefact a committed trust root can be held against")]
    return grade(observe(estate, units), today)


def selfcheck() -> int:
    failures: list[str] = []

    def check(label: str, got: object, want: object) -> None:
        if got != want:
            failures.append(f"{label}: got {got!r}, want {want!r}")

    today = datetime(2026, 9, 9, tzinfo=timezone.utc)
    stamp = datetime(2026, 8, 25, 16, 31, 21, tzinfo=timezone.utc)
    sct = bytes([0]) + bytes.fromhex("dd" * 32) + int(stamp.timestamp() * 1000).to_bytes(8, "big") + b"\x00\x00"
    inner = (len(sct) + 2).to_bytes(2, "big") + len(sct).to_bytes(2, "big") + sct
    der = b"\x30\x82\x00\x10" + SCT_EXTENSION_OID_DER + b"\x04" + bytes([len(inner) + 2]) + b"\x04" + bytes([len(inner)]) + inner
    got = sct_entries(der)
    check("the SCT log id is read out of the DER", [g[0] for g in got], ["dd" * 32])
    check("and its timestamp", got[0][1] if got else None, stamp)
    check("a certificate without the extension names no log", sct_entries(b"\x30\x82\x00\x10x"), [])

    def key(kind: str, hex_id: str, start: str, end: str | None = None) -> dict:
        return {"baseUrl": f"https://{kind}.example", "logId": {"keyId": base64.b64encode(bytes.fromhex(hex_id)).decode()},
                "publicKey": {"rawBytes": "QQ==", "keyDetails": "PKIX_ECDSA_P256_SHA_256",
                              "validFor": {"start": start, **({"end": end} if end else {})}}}
    root = {"tlogs": [key("rekor", "c0" * 32, "2021-01-12T11:53:27Z")],
            "ctlogs": [key("ctfe", "dd" * 32, "2022-10-20T00:00:00Z"), key("ctfe", "08" * 32, "2021-03-14T00:00:00Z", "2022-10-31T23:59:59.999Z")],
            "certificateAuthorities": [{"uri": "https://fulcio.example", "validFor": {"start": "2022-04-13T20:06:15Z"}, "certChain": {"certificates": []}}]}
    keys = root_keys(root)
    check("a retired key is retired, dated, counted", window_status(keys[2].start, keys[2].end, today), "retired 2022-10-31 (1408 days ago)")
    check("a current key is current, dated, counted", window_status(keys[1].start, None, today), "current since 2022-10-20 (1420 days)")
    check("a retired key is not carried for a 2026 artefact", carries(keys, "ctlog", "08" * 32, stamp), None)
    check("a current key is", carries(keys, "ctlog", "dd" * 32, stamp) is not None, True)

    UNSET: list[dict] = []

    def obs(root_doc: dict | None, logs: list[dict] | None = UNSET, sha: str = "a" * 64) -> dict:
        if logs is UNSET:
            logs = [{"kind": "ctlog", "id": "dd" * 32, "at": stamp}, {"kind": "tlog", "id": "c0" * 32, "at": stamp}]
        return {"pin": "v2.0.1", "reason": "x commits no root",
                "root": None if root_doc is None else {"sha": sha, "committed": datetime(2026, 8, 24, tzinfo=timezone.utc), "keys": root_keys(root_doc)},
                "artefacts": [{"version": "2.0.1", "logs": logs}]}
    verdict, lines = grade({"a": obs(root)}, today)
    check("a root carrying every named log inside its window passes", verdict, "PASS")
    check("and the age is printed as a number", any("16 days ago" in t for _, t in lines), True)
    stale = dict(root, ctlogs=[key("ctfe", "ab" * 32, "2022-10-20T00:00:00Z")])
    verdict, lines = grade({"a": obs(stale)}, today)
    check("a log the root does not carry is false", verdict, "FAIL")
    check("and it is named", any("carries no key" in t and "dd" * 8 in t for lvl, t in lines if lvl == "FAIL"), True)
    closed = dict(root, ctlogs=[key("ctfe", "dd" * 32, "2022-10-20T00:00:00Z", "2026-01-01T00:00:00Z")])
    verdict, lines = grade({"a": obs(closed)}, today)
    check("a key whose window closed before the artefact is false", verdict, "FAIL")
    check("and the window is dated", any("2026-01-01" in t for lvl, t in lines if lvl == "FAIL"), True)
    check("an absent root is a could-not-look", grade({"a": obs(None)}, today)[0], "SKIP")
    check("an absent root beside a stale one is false", grade({"a": obs(None), "b": obs(stale)}, today)[0], "FAIL")
    check("an artefact naming no log is false", grade({"a": obs(root, logs=[])}, today)[0], "FAIL")
    verdict, unreadable = grade({"a": obs(root, logs=None)}, today)
    check("a bundle that could not be read is false", verdict, "FAIL")
    check("and says so, rather than saying the artefact named no log",
          any("could not be read as a bundle" in text for level, text in unreadable if level == "FAIL"), True)
    _, lines = grade({"a": obs(root, sha="a" * 64), "b": obs(root, sha="b" * 64)}, today)
    check("differing copies are a note, not a fail", any(lvl == "note" and "differ" in t for lvl, t in lines), True)

    for failure in failures:
        print(f"FAIL: {failure}")
    if failures:
        return 1
    print("PASS: trust_root.py selfcheck -- the SCT log id and timestamp are read out of the DER, every window "
          "is a date and a number, a log the root does not carry is false by name, a key outside its window "
          "is false by date, an unreadable served bundle is false and says so rather than saying the artefact "
          "named no log, an absent root is a could-not-look, and differing copies are a fact")
    return 0


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selfcheck":
        return selfcheck()
    if not argv:
        print("SKIP: no estate directory given")
        return 3
    verdict, lines = run(Path(argv[0]), datetime.now(timezone.utc))
    for level, text in lines:
        print(f"{level}: {text}")
    if verdict == "PASS":
        print("SUMMARY: every log platform's evidence names at each adopter's pin is carried by that adopter's own "
              "committed trust root inside the key's validFor window -- the ages above are printed, not graded")
        return 0
    return 3 if verdict == "SKIP" else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
