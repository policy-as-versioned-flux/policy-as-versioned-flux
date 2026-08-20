# 16 — Make the party model explicit and machine-checked

Type: task
Status: open
Blocked by: 03

## Question

The glossary settled in *Settle what "organisation" means* is prose in `CONTEXT.md`, and nothing
validates it. Make the party model data, and check it.

**1. A `roles:` declaration per party.** Three roles, composable: `publisher`, `risk-bearer`,
`adopter`. Today's holdings — `platform`: publisher + risk-bearer + adopter (it pins `nist`);
`nist`, `ico`: publisher; `driftwood`, `tuppence`, `ludlow`: risk-bearer + adopter.

**2. Consolidate the split appetite store.** `platform` carries a strict £10k band in
`estate/platform/honesty/scenarios/platform-appetite.json`, separate from
`estate/platform/risk/appetite.json`, and `reflexive.py:56` works around `tolerance_for()`'s hard-exit
by passing an override path. That workaround is why nobody noticed the platform is a risk-bearer.

Merge it into the shared store **with the entry marked**, so `tolerance_for("platform")` stops being a
special case and the £10k band becomes discoverable — but a naive `for org in orgs` cannot sweep the
apparatus in as a fourth institution and quietly wrong every count the demo quotes. Verify the counts
that currently read three still read three.

**3. A guard that actually bites.** This is the point of the ticket, and the reason it was split out
rather than done during the glossary work: a `roles:` field nothing validates would be the estate's
**fourth** assertion that cannot fail. The guard must refuse a party whose declared roles contradict
the filesystem — a `risk-bearer` with no appetite entry, a `publisher` that ships no signed versioned
artefact, an `adopter` that pins nothing. Prove it bites by planting each violation and watching it
fail, the way `verify-posture-projection.sh` and the twin's harness guards do.

Consider whether this lands before or after the split: after, each party declares its own roles in its
own repo and the guard runs cross-org; before, it is one file and one loop. Cheaper before, more
honest after.
