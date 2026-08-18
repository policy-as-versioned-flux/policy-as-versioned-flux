"""The demo slice's own rendered artefact (build ticket 91, decision ticket 22).

Decision ticket 22 asked for four things as a slice's own acceptance criteria: a one-sentence
thesis, subject + scenario selection with rationale, an explicit shown/stubbed/absent boundary,
and a mapping of the slice's own ACs back to the build tickets that realise them. Build ticket 77
built the *machinery* that makes the honest boundary structural (depth grades, the does-not-do
register, thesis sequencing) but deliberately did not build the artefact decision ticket 22 itself
asks for — that gap is this ticket's own work, and is why `demo-slice` opened this batch at `stub`
0/4 while every other capability had already reached `full`.

**Composed, not narrated.** Every piece below is either a literal constant lifted from the
decision/build tickets that resolved it (the thesis, the subject rationale, the AC-to-ticket
table) or a live read of machinery that already exists (`does_not_do.published()`,
`grades.Capabilities`) — the same "generated, never authored" discipline `does_not_do.py` states
for itself, applied here to the one part of it (which capabilities this *sequence* touches) that
is a fact about `twin/beat-*.sh`, not about the checklists alone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from . import does_not_do, enact, gameplay_lens, schedule, substrate_report, verbs
from .grades import Capabilities

if TYPE_CHECKING:  # pragma: no cover
    from .artefact import Artefact

KIND = "demo-slice-summary"

# AC 1 — decision ticket 22's own resolved thesis (Q1), verbatim.
THESIS = (
    "we can model an organisation's landscape, anticipate its movements, prove when we're wrong, "
    "and price the response wherever it lives"
)

# AC 2 — the Royal Mail / Netflix / Intel rationale, collected here as data rather than left to
# live only in decision ticket 22's own prose and the three beat scripts' header comments.
SUBJECTS: list[dict[str, Any]] = [
    {
        "org": "royal-mail",
        "beat": "royal-mail",
        "carries": "falsifiability (b), retrospective",
        "role": "proves the twin can be checked",
        "rationale": (
            "Netflix cannot carry this beat: its story is famous, so a twin \"anticipating\" it is "
            "indistinguishable from reciting it, which would undermine the very thesis the demo "
            "leads with. Royal Mail is low-contamination and unusually well-instrumented — the "
            "counterfactual sits inside its own audited filings (GLS reported line-by-line in the "
            "same segmental accounts), with six-plus dated checkpoints including a legally-liable "
            "IPO prospectus forecasting the very trend it then underinvested against."
        ),
        "build_tickets": ["71", "72"],
    },
    {
        "org": "netflix",
        "beat": "netflix",
        "carries": "versioned governance (c), concluding in the one-currency comparison (a)",
        "role": "shows the whole engine",
        "rationale": (
            "Rich, legible, fear and seize both on dated evidence, a deep behavioural substrate to "
            "synthesise, quarterly cadence. Carries the versioned-enactment claim and the "
            "concluding cross-domain comparison — deliberately last, because it is the most "
            "seductive claim and the least defensible standing alone."
        ),
        "build_tickets": ["73", "74"],
    },
    {
        "org": "intel",
        "beat": "intel",
        "carries": "falsifiability (b), live and forward",
        "role": "shows the twin will be checked next",
        "rationale": (
            "Nearly free, and the most honest thing in the demo: a genuine unresolved forecast, "
            "emitted, pinned, signed, where we do not know the answer either. It cannot be scored "
            "yet, and saying so on screen is the strongest demonstration of the falsifiability "
            "claim — a dated prediction someone can come back and check beats any retrospective."
        ),
        "build_tickets": ["75"],
    },
]

# Every capability an artefact-producing verb in `beat-royal-mail.sh`, `beat-netflix.sh` or
# `beat-intel.sh` actually calls, read from the same `CAPS_*` constants those verbs already carry
# — never retyped, so this cannot drift from what the beats really invoke without also changing
# the module that composes their output. `demo-slice` is added explicitly: every beat's own
# closing step grades it, but no `CAPS_*` list names it (the same reason `honest-build` is full
# but cited by no artefact's own depth block, per twin/README.md). `fixture`, `verify` and `grade`
# carry no capability of their own — they inspect or reproduce an artefact rather than producing
# one — so they contribute nothing here.
TOUCHED_CAPABILITIES: list[str] = sorted(
    set(
        verbs.CAPS_RUN
        + verbs.CAPS_SCORE
        + verbs.CAPS_REGIMES
        + verbs.CAPS_SENSE
        + verbs.CAPS_REWIND
        + verbs.CAPS_OPTIONS
        + verbs.CAPS_PRICE
        + verbs.CAPS_TRADEOFF
        + verbs.CAPS_PROPAGATE
        + gameplay_lens.CAPS_GAMEPLAY_SWEEP
        + schedule.CAPS_SWEEP
        + substrate_report.CAPS_SUBSTRATE
        + [enact.CAPABILITY, "demo-slice"]
    )
)

# AC 4 — this decision ticket's own four ACs, tied back to the build tickets that realise them.
ACCEPTANCE_CRITERIA: list[dict[str, Any]] = [
    {
        "index": 1,
        "text": "A single demonstrable thesis, stated in one sentence.",
        "build_tickets": ["77", "91"],
        "note": "77 sequenced the thesis structurally; 91 states it once, here, as data.",
    },
    {
        "index": 2,
        "text": "Subject + scenario selection, with rationale.",
        "build_tickets": ["71", "73", "75", "91"],
        "note": "71/73/75 built each subject's own answer key or spine; 91 collects the rationale "
        "already written for each into this artefact's own data.",
    },
    {
        "index": 3,
        "text": "An explicit shown/stubbed/absent boundary and how it is surfaced.",
        "build_tickets": ["77", "91"],
        "note": "77 built depth grades and the does-not-do register as structural mechanism; 91 "
        "scopes them to the capabilities this demo sequence actually touches.",
    },
    {
        "index": 4,
        "text": "Acceptance criteria for the slice, tied back to the owning tickets' criteria.",
        "build_tickets": ["91"],
        "note": "this table.",
    },
]


def boundary(caps: Capabilities | None = None) -> dict[str, Any]:
    """shown/stubbed/absent (decision ticket 22 Q3), scoped to this demo sequence.

    `shown` is every capability a beat script actually exercises. `stubbed` is the does-not-do
    register's own entries (build ticket 77), filtered to those capabilities — the unchecked
    acceptance criteria a viewer of *this* sequence could actually run into. `absent` is every
    other loaded capability: not shown as broken, simply never touched by anything in the
    sequence, which is a different and equally honest thing to say about it.
    """
    loaded = caps or Capabilities.load()
    published = does_not_do.published(loaded)
    touched = set(TOUCHED_CAPABILITIES)
    stubbed = [e for e in published["entries"] if e["id"].rsplit("-", 1)[0] in touched]
    absent = sorted(g.capability for g in loaded if g.capability not in touched)
    return {
        "shown": list(TOUCHED_CAPABILITIES),
        "stubbed": stubbed,
        "absent": absent,
        "depth": loaded.depth_block(TOUCHED_CAPABILITIES),
    }


def summary(caps: Capabilities | None = None) -> dict[str, Any]:
    """The four pieces decision ticket 22 asks for, composed into one structured body — a pure
    function of `Capabilities`, printable and emittable without any further lookup.
    """
    loaded = caps or Capabilities.load()
    return {
        "thesis": THESIS,
        "subjects": SUBJECTS,
        "boundary": boundary(loaded),
        "acceptance_criteria": ACCEPTANCE_CRITERIA,
    }


def artefact(
    command: list[str], caps: Capabilities | None = None, body: dict[str, Any] | None = None,
) -> "Artefact":
    """The demo slice summary as a derived artefact.

    `body` lets a caller that already computed `summary(caps)` (to print it, say) pass that same
    dict through rather than paying for the walk a second time — the same shape `does_not_do.py`
    settled on after build ticket 77's own performance-review finding.
    """
    from .artefact import DERIVED, Artefact

    loaded = caps or Capabilities.load()
    return Artefact(
        kind=KIND,
        mark=DERIVED,
        command=command,
        pins={"capabilities_digest": loaded.digest},
        depth=loaded.depth_block(TOUCHED_CAPABILITIES),
        body=body if body is not None else summary(loaded),
    )
