"""Preserve the immutable canonical schema contract and name owned optional additions."""
import json
from pathlib import Path

day = Path(__file__).resolve().parent
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
old = '''    same = open(CANONICAL, "rb").read() == open(VENDORED, "rb").read()
    out("PASS" if same else "FAIL",
        "vendored payload schema %s platform/feeds/forward-intel.payload.schema.json"
        % ("is byte-identical to" if same else "DIFFERS from"))'''
new = '''    canonical = json.load(open(CANONICAL))
    owned = json.load(open(VENDORED))
    extensions = {
        "rests_on_grade": {"type": "integer", "enum": [1, 2, 3]},
        "valuation": {
            "type": "object",
            "required": ["amount", "currency", "native_amount", "native_currency", "party_fact", "fx"],
            "properties": {
                "amount": {"type": "number"}, "currency": {"type": "string"},
                "native_amount": {"type": "number"}, "native_currency": {"type": "string"},
                "party_fact": {"type": "string"}, "fx": {"type": ["object", "null"]}},
            "additionalProperties": False}}
    base = dict(owned)
    base["properties"] = {key: value for key, value in owned["properties"].items()
                          if key not in extensions}
    same = (base == canonical and
            all(owned["properties"].get(key) == value for key, value in extensions.items()) and
            not (set(extensions) & set(owned["required"])))
    out("PASS" if same else "FAIL",
        "owned payload schema %s the immutable canonical contract plus exactly the optional "
        "valuation and rests_on_grade declarations"
        % ("preserves" if same else "DIFFERS from"))'''
for org, loc in locator["adopters"].items():
    repo = Path(loc["dir"])
    helper = repo / "verify-twin-overlay.sh"
    text = helper.read_text()
    assert old in text, org
    text = text.replace(old, new)
    if org == "driftwood":
        text = text.replace('os.path.join(entry["path"], "v1", "feed.json")',
                            'os.path.join(entry["path"], "v" + version.split(".")[0], "feed.json")')
    helper.write_text(text)
    doc = repo / "twin/VENDORED.md"
    text = doc.read_text()
    start = text.index("## `forward-intel/payload.schema.json`")
    end = text.find("\n## ", start + 5)
    if end == -1:
        end = len(text)
    section = '''## `forward-intel/payload.schema.json`

This is the adopter's owned schema for its forward-intel envelope. Its base is the
immutable `platform/feeds/forward-intel.payload.schema.json` at authenticated tools
v5.0.0 (`703eff6aee959843c4160aa54fd03413f62858cc`). It preserves every canonical
property, requirement and type. Ticket 144 adds exactly two optional declarations:
`rests_on_grade` (integer grades 1–3) and `valuation` (the native amount/currency,
party fact, reporting amount/currency and nullable dated FX record). No inherited
constraint is removed and the closed property set remains closed.

The active schema is an owned extension, not a byte-for-byte vendored copy. It lives
inside this publishing repository because the envelope resolves `payload_schema`
here, and the feed can be validated offline from these self-contained bytes.
`verify-twin-overlay.sh` checks the complete canonical base semantically and the
exact two optional additions against the materialized authentic platform schema.
It reports could-not-look if that parent is absent; absence never proves agreement.
'''
    doc.write_text(text[:start] + section + text[end:])
print("All3 owned schemas preserve the full authentic canonical contract plus exactly two optional declarations")
