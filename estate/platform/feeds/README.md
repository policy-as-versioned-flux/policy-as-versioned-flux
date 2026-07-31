# policy-as-versioned-platform / feeds

**The reactive feeds** — institution threat register · CVE (trivy/GHSA-shaped) · EOL
(`endoflife.date`-shaped) — signed and versioned like the regulator feeds
(`nist` OSCAL, `ico` penalty schema), consumed by `platform/fair/fair.py` as
pinned deps. A feed change arrives as a reviewable diff (version bump) that
re-tunes the £ with **no edit to `fair.py`**. *(ticket 21)*

## What's here

```
threat-register/v1,v2/register.json(.sig)   institution -> headline threat -> lef
cve/v1,v2/cve-feed.json(.sig)               trivy/GHSA-shaped: cve -> cvss/severity/epss
eol/v1,v2/eol-feed.json(.sig)               endoflife.date-shaped: component -> eol_date + base rate
keys/feeds-signing-key(.pub).pem            shared ed25519 keypair (ponytail: repo-local demo key)
sign.sh / verify.sh                         offline sign / verify <feed> <version> <file>
to_fair_scenario.py                         feed entry -> fair.py scenario (unmodified fair.py consumes it)
verify-feeds.sh                             the whole beat: sign+verify, tamper rejection, £ moves on a
                                             bump, EOL ramps as a time-varying thread
```

Run `./verify-feeds.sh` (offline, no cluster) for the full beat.

## EOL as a time-varying thread

Unlike the other feeds, EOL risk isn't priced once at ingestion — it's a function
of *when you ask*. `to_fair_scenario.py eol <feed> <component> --as-of <date>`
computes `days_past_eol` and ramps loss-event-frequency linearly (+1x per year
past `eol_date`, capped at +4x — unpatched CVEs accumulate the longer a
component goes unmaintained, `eol_ramp()` in `to_fair_scenario.py`):

```mermaid
flowchart LR
    feed["eol-feed.json<br/>component -> eol_date + base_lef"] --> asof["--as-of date"]
    asof --> ramp{"days past eol_date?"}
    ramp -->|"before/at eol"| flat["ramp = 1.0x<br/>(still in support)"]
    ramp -->|"past eol"| grow["ramp = 1 + min(years_past, 4)<br/>(+1x per year, capped)"]
    flat --> lef["lef x ramp"]
    grow --> lef
    lef --> fair["fair.py summary<br/>-> ALE moves purely from<br/>elapsed time, no feed edit"]
```

So a policy version going unmaintained is priced like any other EOL risk — the
same `--as-of` clock the war-gamer (ticket 22) runs against, not a bespoke
sunset branch.

## Consumed by

`platform/fair/fair.py` (loss-event-frequency + loss-magnitude inputs, same
`(min,mode,max)` scenario shape as `estate/ico/schema/to_fair_scenario.py` and
`estate/platform/fair/scenarios/driftwood-cart-pii.json`). Institutions
(`driftwood`, `tuppence`, `ludlow`) and the war-gamer pin a feed version the
same way `driftwood/scripts/bump-nist-pin.sh` pins the `nist` catalog — a
version bump is a reviewable PR, verified offline via `verify.sh` before the
Flux/CI gate lets it in.
