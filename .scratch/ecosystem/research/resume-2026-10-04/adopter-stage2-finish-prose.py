"""Correct historical absent-instrument prose without changing financial declarations."""
import json
from pathlib import Path

day = Path(__file__).resolve().parent
locator = json.loads((day / "adopter-stage2-isolated.json").read_text())
for org in ("tuppence", "ludlow"):
    repo = Path(locator["adopters"][org]["dir"])
    path = repo / "twin/VENDORED.md"
    text = path.read_text()
    text = text.replace("They reach no\nprice here, because nothing in this overlay reaches a price at all (below). Read every number in\nthat file as an authored prior.",
                        "The forward-intel producer does not read those authored priors: its money comes from the\ndeclared native filing, causal edge and response mechanisms. Read every number in that file as\nan authored prior, not an observed frequency.")
    start = text.index("## This overlay is COMPLETE and UNPRICED")
    end = text.index("## `forward-intel/payload.schema.json`", start)
    money = ("Tuppence's declared turnover and payment-fee share derive its native GBP cash flow.\nThe perspective reports in GBP too, so no FX conversion is needed."
             if org == "tuppence" else
             "Ludlow's declared USD turnover and service-fee share derive its native USD cash flow\nas at 2025-12-31. The GBP perspective requires the genuine signature-verified December 2025\nFX instrument: `fx/v2.0.0`, whose USD rate is 1.3126 units per GBP. An absent signature,\nrate or matching valuation month remains `CANNOT LOOK` (exit 3), never a guessed amount.")
    section = ("## The declared financial and evidence instruments\n\n" + money +
        "\n\nBoth the valuation and the loss mechanism retain evidence grade 3: published comparable\nwork, **not observed here**. The party explicitly declares `pricing_threshold: 3`, which\nadmits that grade without a regrade event. Grade-5 mitigation remains unpriced. The producer\nborrows the subscribed threat-register frequency explicitly; the comparable enforcement\nrecord is no claim that this institution experienced that event.\n\nThe first forward-intel v1 envelope is authored on 2026-10-04. Its ordinary publisher rule,\nbump and discovery declaration are reviewed with the source. Local emission is not an\nauthentic signed release, delivered application, or scheduled live observation.\n\n")
    text = text[:start] + section + text[end:]
    text = text.replace("It is vendored beside the (not yet emitted) feed for two reasons:",
                        "It is vendored beside the producer and its feed for two reasons:")
    old = ("driftwood ships a versioned `selection-policy` package and reads its rungs from it. This\nrepository ships none; authoring one is ticket 25's shape and not ticket 64's. So the rungs are\ndeclared in `ladder.yaml`, which records the platform release that published them")
    new = ("This repository also ships a versioned `selection-policy` package. Its forward-intel\nproducer reads its curve rungs from the separate `ladder.yaml` declaration; it does not select\na delivered tier. The ladder records the platform release that published the rungs")
    assert old in text
    text = text.replace(old, new)
    text = text.replace("the owner dispatches that workflow, `world_ref` is the only pin with bytes behind it and\n`PIN.yaml` carries `tag_cut: false`.",
                        "the owner dispatches that workflow, `PIN.yaml` carries `tag_cut: false`. Its full\n`hub_commit` pins genuinely published producer code, while `world_ref` pins the vendored\nworld bytes independently.")
    path.write_text(text)
    scenario = repo / f"twin/orgs/{org}/scenarios/penalty-published-2026.yaml"
    text = scenario.read_text()
    start = text.index("  And the honest other half:")
    end = text.index("affected_parties:", start)
    conversion = (" Its native GBP cash flow needs no conversion."
                  if org == "tuppence" else
                  " Its native USD cash flow reaches GBP only through the signed FX instrument\n  matching the 2025-12-31 valuation date; a missing dated rate is a missing instrument.")
    text = text[:start] + ("  The declared native filing and share derive the perspective's amount. Both valuation\n  and loss mechanism remain grade 3, admitted by this party's explicit pricing threshold 3.\n  The comparable regulatory record is not this institution's observed incident."
        + conversion + " Grade-5 mitigation remains\n  unpriced; publishing this standing question does not record a new enforcement event.\n") + text[end:]
    scenario.write_text(text)
    pin = repo / "twin/PIN.yaml"
    text = pin.read_text().replace("world_ref` in\n# orgs/<org>/meta.yaml is the only pin with bytes behind it.",
        "world_ref` in\n# orgs/<org>/meta.yaml pins the world bytes and hub_commit pins the published producer code.")
    pin.write_text(text)
print("Tuppence and Ludlow financial/grade prose corrected; numeric declarations unchanged")
