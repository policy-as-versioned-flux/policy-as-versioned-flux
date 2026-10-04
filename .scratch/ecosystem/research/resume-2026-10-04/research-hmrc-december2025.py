"""Read-only primary HMRC table normalization and actual published FX rule assessment."""
from __future__ import annotations

import csv
from decimal import Decimal
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys

day = Path(__file__).resolve().parent
feeds = day.parents[3] / ".estate-publish/feeds"
raw = (day / "hmrc-monthly-2025-12.csv").read_bytes()
assert raw == (day / "hmrc-monthly-2025-12-confirmed.csv").read_bytes()
url = "https://www.trade-tariff.service.gov.uk/api/v2/exchange_rates/files/monthly_csv_2025-12.csv"
sys.path.insert(0, str(feeds / "fetch"))
spec = importlib.util.spec_from_file_location("primary_hmrc_fx", feeds / "fetch/fx.py")
assert spec and spec.loader
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
payload = source.parse(raw, "2025-12", url)
table = list(csv.DictReader(io.StringIO(raw.decode("utf-8-sig"))))
assert all(row["Start date"] == "01/12/2025" and row["End date"] == "31/12/2025" for row in table)
usd = [row for row in table if row["Country/Territories"] == "USA"]
assert len(usd) == 1 and usd[0]["Currency Code"] == "USD"
assert Decimal(usd[0]["Currency Units per £1"]) == Decimal("1.3126")
assert payload["rates"]["USD"] == 1.3126
(day / "hmrc-december2025-normalized-payload.json").write_text(json.dumps(payload, indent=2) + "\n")
(day / "hmrc-december2025-full-row-table.json").write_text(json.dumps(table, indent=2, ensure_ascii=False) + "\n")
release = subprocess.check_output(["git", "-C", str(feeds), "rev-parse", "fx/v1.1.0^{}"], text=True).strip()
assert release == "974e73514e0d8d4cad2e6906acf51d1cc27028b3"
old = json.loads(subprocess.check_output(["git", "-C", str(feeds), "show", release + ":fx/v1/feed.json"]))
rule_path = feeds / "fx/rule.yaml"
spec = importlib.util.spec_from_file_location("published_feed_bump", feeds / "bump.py")
assert spec and spec.loader
bump = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bump)
rule = bump.load_rule(rule_path)
measured = bump.compute(old, {**old, "payload": payload}, rule)
deleted = sorted(set(old["payload"]["rates"]) - set(payload["rates"]))
added = sorted(set(payload["rates"]) - set(old["payload"]["rates"]))
native = Decimal("8475000000")
result = {"source_url": url,
    "official_month_page": "https://www.trade-tariff.service.gov.uk/exchange_rates/view/2025-12",
    "raw_sha256": hashlib.sha256(raw).hexdigest(), "raw_bytes": len(raw),
    "raw_byte_confirmation": "two official CSV GETs byte exact",
    "full_row_count": len(table), "unique_currency_count": len(payload["rates"]),
    "all_row_start_date": "2025-12-01", "all_row_end_date": "2025-12-31",
    "usd_row": usd[0], "units": "currency units per GBP1", "GBP_base_rate": 1,
    "normalization": "actual published fetch/fx.py parse(raw, 2025-12, officialURL), no inferred rates",
    "normalized_payload_sha256": hashlib.sha256((day / "hmrc-december2025-normalized-payload.json").read_bytes()).hexdigest(),
    "immutable_august_baseline": {"tag": "fx/v1.1.0", "commit": release,
        "tag_object": subprocess.check_output(["git", "-C", str(feeds), "rev-parse", "fx/v1.1.0"], text=True).strip(),
        "period": old["payload"]["period"], "USD": old["payload"]["rates"]["USD"]},
    "actual_published_rule_bump": measured, "removed_currency_codes": deleted, "added_currency_codes": added,
    "prospective_ordinary_namespace_release": "fx/v2.0.0" if measured == "major" else "fx/v1.2.0",
    "prospective_only": True, "candidate_feed_envelope_saved": False,
    "existing_converter_and_emitter_major_paths": "tag major parsed to fx/vMAJOR/feed.json; namespace already accepts fx2",
    "illustrative_arithmetic_only_until_signed_snapshot": {
        "native_USD": str(native), "date": "2025-12-31", "official_USD_per_GBP": "1.3126",
        "GBP_formula": "native_USD / USD_per_GBP", "GBP": str(native / Decimal("1.3126")),
        "not_a_current_served_or_signed_price": True},
    "no_repo_mutations": "research files only; no feed/adopter source or tags changed",
    "actual_matching_signed_feed_available": False,
    "current_Ludlow_result": "MissingInstrument -> CANNOT LOOK exit3 until authentic matching signed feed exists"}
(day / "hmrc-december2025-primary-research.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
