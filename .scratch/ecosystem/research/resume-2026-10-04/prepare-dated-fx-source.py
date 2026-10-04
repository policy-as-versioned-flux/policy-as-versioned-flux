"""Prepare only the approved isolated FX2 source from captured official primary bytes."""
from __future__ import annotations

import datetime as dt
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

day = Path(__file__).resolve().parent
hub = day.parents[3]
feeds = hub / ".estate-publish/feeds"
base = "974e73514e0d8d4cad2e6906acf51d1cc27028b3"
assert subprocess.check_output(["git", "-C", str(feeds), "rev-parse", "HEAD"], text=True).strip() == base
assert not subprocess.check_output(["git", "-C", str(feeds), "status", "--porcelain"], text=True).strip()
sys.path.insert(0, str(feeds / "fetch"))
import fx
import lib

def digest(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


old = json.loads((feeds / "fx/v1/feed.json").read_text())
frozen = {str(p.relative_to(feeds)): digest(p.read_bytes())
          for p in feeds.glob("*/v*/feed.json") if p.is_file()}
default_replay = digest((feeds / "fetch/source/fx.json").read_bytes())
proof = {"schema": 1, "authority": "HM Revenue & Customs",
         "units": "currency units per GBP1", "base": "GBP",
         "captured_at": dt.datetime.now(dt.timezone.utc).isoformat(),
         "scope": "captured official public data; source preparation only, no signed release claim",
         "normalizer": "fetch/fx.py parse", "normalizer_sha256": digest((feeds / "fetch/fx.py").read_bytes()),
         "periods": {}, "preserved_published_baseline": {"tag": "fx/v1.1.0", "commit": base,
             "envelope": "fx/v1/feed.json", "envelope_sha256": digest((feeds / "fx/v1/feed.json").read_bytes())}}
monthly = feeds / "fetch/source/hmrc"
monthly.mkdir(parents=True)
payloads = {}
for period, name in (("2025-12", "2025-12"), ("2026-08", "2026-08")):
    raw = (day / f"hmrc-monthly-{name}.csv").read_bytes()
    year, month = period.split("-")
    url = fx.UPSTREAM.format(year=year, month=int(month))
    payload = fx.parse(raw, period, url)
    payloads[period] = payload
    relative = f"fetch/source/hmrc/{period}.csv"
    (feeds / relative).write_bytes(raw)
    proof["periods"][period] = {"source_url": url, "raw_csv": relative,
        "raw_sha256": digest(raw), "raw_bytes": len(raw),
        "normalized_payload_sha256": digest(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()),
        "unique_currency_count": len(payload["rates"]), "USD_units_per_GBP1": payload["rates"]["USD"]}
assert payloads["2026-08"] == old["payload"], "Actual August source must reproduce immutable1.1 bytes"
assert proof["periods"]["2026-08"]["raw_sha256"] == "8da9e83a830282c94cbcb31779cbeb93d7a2a739d1bb898cbec62182b7b29fad"
payload = payloads["2025-12"]
verdict = lib.bump_engine.compute(old, {**old, "payload": payload}, lib.load_rule("fx"))
assert verdict == "major"
version = lib.next_version(old["version"], verdict)
assert version == "2.0.0"
envelope = {**old, "version": version, "published_at": "2026-10-04T00:00:00Z", "payload": payload}
envelope_path = feeds / "fx/v2/feed.json"
envelope_path.parent.mkdir(parents=True)
envelope_path.write_text(json.dumps(envelope, indent=2) + "\n")
dated = feeds / "fetch/source/periods/2025-12/fx.json"
dated.parent.mkdir(parents=True)
dated.write_text(json.dumps(payload, indent=2) + "\n")
proof["periods"]["2025-12"]["offline_replay_payload"] = str(dated.relative_to(feeds))
proof["periods"]["2025-12"]["offline_replay_payload_sha256"] = digest(dated.read_bytes())
proof["periods"]["2025-12"]["prepared_envelope"] = str(envelope_path.relative_to(feeds))
proof["periods"]["2025-12"]["prepared_envelope_sha256"] = digest(envelope_path.read_bytes())
proof["computed_bump"] = verdict
proof["prospective_version"] = version
proof["removed_currency_codes"] = sorted(set(old["payload"]["rates"]) - set(payload["rates"]))
proof["added_currency_codes"] = sorted(set(payload["rates"]) - set(old["payload"]["rates"]))
(monthly / "PROVENANCE.json").write_text(json.dumps(proof, indent=2) + "\n")
bump_path = feeds / "fx/bump.yaml"
text = bump_path.read_text()
assert text.count("bump: minor") == 1
bump_path.write_text(text.replace("bump: minor", "bump: major"))
assert all(digest((feeds / name).read_bytes()) == expected for name, expected in frozen.items())
assert digest((feeds / "fetch/source/fx.json").read_bytes()) == default_replay
(day / "fx2-source-preparation.json").write_text(json.dumps({"base": base,
    "branch": subprocess.check_output(["git", "-C", str(feeds), "branch", "--show-current"], text=True).strip(),
    "computed_bump": verdict, "prospective_version": version, "frozen_major_payloads": frozen,
    "all_frozen_major_payloads_byte_exact": True, "default_august_replay_byte_exact": True,
    "provenance": proof, "external_mutations": False}, indent=2) + "\n")
print(json.dumps({"base": base, "computed_bump": verdict, "version": version,
                  "frozen_payload_count": len(frozen), "all_frozen_byte_exact": True}, indent=2))
