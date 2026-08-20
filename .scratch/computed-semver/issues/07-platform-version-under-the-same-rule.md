# 07 — Bind the platform's own version to the rule it distributes

Type: task
Status: open
Blocked by: 05

## Question

`CONTEXT.md` defines the rule for "the whole policy body". But `platform` ships a versioned artefact
that institutions pin, and a platform bump edits the version array — which changes which policies are
installed, which changes verdicts. Settled at charting: **the same rule binds it.**

**The job:** make a platform release compute its bump the same way a policy release does. A platform
change that adds a version to the array, retires one, or alters the orphan-guard's allow-list can flip
a workload's admission outcome, and the version number must say so.

Note this is the reflexive argument the estate already makes elsewhere — the apparatus prices its own
risk against its own £10k band and passes its own test. Exempting the distribution layer from the
versioning rule the distribution layer enforces would be precisely the self-exemption
`honesty/reflexive.py` exists to refuse.

Watch for the case where retiring a version is the *whole* change: a workload pinned to the retired
version is matched by nothing afterwards. Whether that is major (its verdict changed) or out of scope
(it was already unsupported) is exactly the sort of edge the verdict-semantics ticket should have
settled — check that it did, and raise it back there if not.
