"""Finite native publisher gates, retained historical bytes and primary dated FX replay."""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

day = Path(__file__).resolve().parent
hub = day.parents[3]
feeds = hub / ".estate-publish/feeds"
platform = hub / ".estate-publish/platform"
baseline = json.loads((day / "fx2-source-preparation.json").read_text())
results = {"platform_schema_tag": "v2.0.1", "platform_schema_commit": "533dccb0a823001b396fd60ab08014bf75065a37",
           "no_external_mutations": True, "checks": {}}

with tempfile.TemporaryDirectory(prefix="pavf-fx2-pinned-schema-") as temporary:
    schemas = Path(temporary)
    for rel in ["feeds/schema.json", "feeds/forward-intel.payload.schema.json"]:
        target = schemas / rel
        target.parent.mkdir(exist_ok=True, parents=True)
        target.write_bytes(subprocess.check_output(["git", "-C", str(platform), "show",
            results["platform_schema_commit"] + ":" + rel]))
    env = {**os.environ, "PLATFORM_DIR": str(schemas)}
    env.pop("GITHUB_OUTPUT", None)
    for name in ["verify-feeds.sh", "verify-market-and-news.sh"]:
        proc = subprocess.run(["bash", name], cwd=feeds, env=env, capture_output=True, text=True, timeout=120)
        (day / f"fx2-{name}.log").write_text(proc.stdout + proc.stderr)
        results["checks"][name] = {"exit": proc.returncode, "final_line": proc.stdout.rstrip().splitlines()[-1] if proc.stdout else proc.stderr}
        (day / "fx2-source-checks.json").write_text(json.dumps(results, indent=2) + "\n")
        assert proc.returncode == 0, (name, proc.stdout, proc.stderr)
        print(name + ": PASS")
    for name, argv in [
        ("fx-native-selfcheck", [sys.executable, "converters/fx.py", "selfcheck"]),
        ("december-date-conversion", [sys.executable, "converters/fx.py", "convert", "8475000000", "USD", "GBP", "2025-12-31"]),
        ("august-date-preserved", [sys.executable, "converters/fx.py", "convert", "1000", "GBP", "USD", "2026-08-14"]),
        ("original-to-december-normal-rule", [sys.executable, "bump.py", "fx/v1/feed.json", "fx/v2/feed.json", "fx/rule.yaml"]),
    ]:
        proc = subprocess.run(argv, cwd=feeds, env=env, capture_output=True, text=True, timeout=60)
        assert proc.returncode == 0, (name, proc.stdout, proc.stderr)
        if name == "original-to-december-normal-rule":
            assert proc.stdout.strip() == "major"
        results["checks"][name] = {"exit": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}
        print(name + ": PASS")
    replay_env = {**env, "FEEDS_SOURCE_DIR": str(feeds / "fetch/source/periods/2025-12"), "FEEDS_FX_PERIOD": "2025-12"}
    proc = subprocess.run([sys.executable, "fetch/fx.py", "--dry-run"], cwd=feeds, env=replay_env,
                          capture_output=True, text=True, timeout=60)
    assert proc.returncode == 0 and "-> none" in proc.stdout, (proc.stdout, proc.stderr)
    results["checks"]["december-offline-primary-replay"] = {"exit": proc.returncode,
        "stdout": proc.stdout, "scope": "dry run against captured primary December payload; no observation lane write, no new upstream clock claim"}
    for bad in ["2025-11-30", "2026-01-01"]:
        proc = subprocess.run([sys.executable, "converters/fx.py", "convert", "1000", "USD", "GBP", bad],
                              cwd=feeds, env=env, capture_output=True, text=True, timeout=60)
        assert proc.returncode == 4 and "MISSING INSTRUMENT" in proc.stderr, (bad, proc.stdout, proc.stderr)
        results["checks"]["missing-month-" + bad] = {"exit": proc.returncode, "stderr": proc.stderr,
                                                    "observed_honest_absence": True}

sys.path.insert(0, str(feeds / "fetch"))
import fx
provenance = json.loads((feeds / "fetch/source/hmrc/PROVENANCE.json").read_text())
for period, row in provenance["periods"].items():
    raw = (feeds / row["raw_csv"]).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == row["raw_sha256"]
    parsed = fx.parse(raw, period, row["source_url"])
    envelope = json.loads((feeds / ("fx/v2/feed.json" if period == "2025-12" else "fx/v1/feed.json")).read_text())
    assert parsed == envelope["payload"]
    results["checks"]["primary-replay-" + period] = {"complete_official_table_matches_envelope": True,
        "raw_sha256": row["raw_sha256"], "unique_currency_count": len(parsed["rates"])}
assert all(hashlib.sha256((feeds / path).read_bytes()).hexdigest() == expected
           for path, expected in baseline["frozen_major_payloads"].items())
results["checks"]["frozen-major-preservation"] = {"byte_exact_count": len(baseline["frozen_major_payloads"]), "PASS": True}
subprocess.run(["git", "-C", str(feeds), "diff", "--check"], check=True, capture_output=True)
(day / "fx2-source-checks.json").write_text(json.dumps(results, indent=2) + "\n")
print("all native gates, dated raw replays, missing-month refusals and12frozen envelopes: PASS")
