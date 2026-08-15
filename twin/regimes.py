"""The three information regimes, and the gate that makes `as-consumed` mean something.

Build ticket 36, from decision tickets 11, 13 (Q2, Q2b) and 19. Three regimes, and the gaps
between them are the reason there are three rather than one honest one:

* **`as-consumed`** — only what the twin had ingested by T. Two filters, because there are two
  ways a post-T fact can arrive: the repository is read **as it stood at T** (a fact committed
  later is not there at all), and any fact that survives that but is *dated* after T is withheld.
* **`as-knowable`** — everything dated on or before T, whenever it was ingested. This is what a
  perfect sensing apparatus would have had.
* **`with-hindsight`** — unrestricted.

The two differences localise a failure, which is the whole point:

* `as-consumed` versus `as-knowable` is a **sensing** failure — it was there to be found and we
  did not have it.
* `as-knowable` versus `with-hindsight` is an **interpretation** failure — nothing dated by T
  said it, so reading it as foreseeable is hindsight.
* wrong under all three is the **model**.

**The gate is by construction, not by review.** A withheld fact is *absent from the overlay the
execution reads*: there is no post-T fact to include, so including one is not a mistake somebody
could make. And a withheld fact that the execution could still have **reached** — one bound by a
claim to a component the scenario names — is a refusal rather than a silent removal, because
running a scenario whose own subject matter has been redacted answers a different question from
the one that was asked.

## Two named limits

**The rewind leg needs a repository that existed at T.** A retrospective subject is dated 2011
and the model repository holding it was created this year, so there is no commit at 2011 to read
and the ingestion-history filter cannot constrain anything. The date filter always applies; the
history filter reports itself as `unavailable` with the reason, rather than being quietly skipped
so that `as-consumed` looks stronger than it was.

**A regrade is not gated.** `schema.DATED_FACTS` covers facts about the world — signals and
outcomes. A regrade is the twin's own record of how strong a claim is, and a regrade dated after
T still moves a grade under `as-knowable`. Under `as-consumed` the rewind removes it when the
repository history reaches back that far, and does not when it does not.
"""

from __future__ import annotations

import dataclasses
import re
from typing import Any

from .model import Overlay
from .repo import ModelRepo, RepoError
from .schema import DATED_FACTS, REGIMES

AS_CONSUMED, AS_KNOWABLE, WITH_HINDSIGHT = REGIMES

# What each regime filters on. Read from here rather than from a chain of `if`s, so the three
# regimes are visibly a table with two independent switches rather than three special cases.
FILTERS: dict[str, dict[str, bool]] = {
    AS_CONSUMED: {"by_ingestion": True, "by_date": True},
    AS_KNOWABLE: {"by_ingestion": False, "by_date": True},
    WITH_HINDSIGHT: {"by_ingestion": False, "by_date": False},
}

SENSING, INTERPRETATION = "sensing", "interpretation"

WITHHELD_POST_T = "dated after the execution time"

# The cutoff is compared against fact dates as a **string**, which is exact for `YYYY-MM-DD` and
# quietly wrong for anything else: `'2011-09-01' > '20110712'` is `False`, so a post-T fact would
# be admitted. `datetime.fromisoformat` accepts the basic form, so the rewind's own parser is not
# a guard against this — the same shape of defect as an unparseable rewind time answering a
# question about the past with today's model.
_DAY = re.compile(r"^\d{4}-\d{2}-\d{2}$")


class RegimeError(RuntimeError):
    """A regime that does not exist, an execution with no regime, or a redacted subject."""


def cutoff(at: str) -> str:
    """The execution time as a day the date filter can compare against, or a refusal.

    Every dated fact in this system is a `YYYY-MM-DD` day, because that is what the schema admits.
    A cutoff in any other shape is refused rather than coerced: truncating `2011-07-12T09:00:00Z`
    to its date would silently answer a question about a moment with an answer about a day.
    """
    stamp = str(at).strip()
    if not _DAY.match(stamp):
        raise RegimeError(
            f"{stamp!r} is not an execution date of the form YYYY-MM-DD. Every dated fact in this "
            "model is a day, and the gate compares them as text — so a cutoff in another shape "
            "compares wrong rather than failing, and admits facts it should withhold."
        )
    return stamp


def require(regime: str | None) -> str:
    """The regime, or a refusal. **There is no default, and that is the whole of AC 1.**

    Defaulting would make the gate bypassable by *omission* rather than by assertion: an author
    who left the flag off would inherit whichever regime the code happened to prefer, and the one
    the code would prefer is the one that scores.
    """
    if regime is None or not str(regime).strip():
        raise RegimeError(
            "an execution declares its information regime; there is no default. Choose one of "
            f"{', '.join(REGIMES)} — only {AS_CONSUMED!r} produces a scoring-eligible forecast, "
            "and defaulting to it would let the gate be bypassed by leaving the flag off."
        )
    name = str(regime).strip()
    if name not in FILTERS:
        raise RegimeError(f"unknown information regime {name!r}; this system has {', '.join(REGIMES)}")
    return name


def _fact_date(collection: str, doc: dict[str, Any]) -> str:
    return str(doc[DATED_FACTS[collection]])


def _withhold(collection: str, ident: str, doc: dict[str, Any], reason: str) -> dict[str, Any]:
    """A withheld fact, named and dated. Named rather than counted: a redaction nobody can see
    is indistinguishable from a fact that never existed."""
    return {
        "collection": collection,
        "id": ident,
        "dated": _fact_date(collection, doc),
        "reason": reason,
    }


def _dated_facts(overlay: Overlay) -> dict[str, dict[str, dict[str, Any]]]:
    return {name: dict(getattr(overlay, name)) for name in DATED_FACTS}


def ingestion_history(repo: ModelRepo, at: str) -> dict[str, Any]:
    """Whether the repository can be read as it stood at T, and what it means when it cannot.

    Reported rather than silently skipped. An `as-consumed` run against a repository whose first
    commit postdates T is gated on fact dates alone, which is genuinely weaker, and an artefact
    that did not say so would be claiming an ingestion history it never had.

    The refusal's own text is deliberately **not** carried through: it names the resolved path on
    disk, and a machine path in an artefact breaks `identical_pins_identical_bytes` on the first
    machine that checks out somewhere else. The fact worth recording is that there was no commit
    to read, not where the checkout happened to be.
    """
    try:
        rewound = ModelRepo.open_at_time(repo.model_root, at)
    except RepoError:
        return {
            "available": False,
            "reason": "this repository holds no commit at or before the execution time",
            "consequence": (
                "the ingestion-history filter did not run: this repository has no commit at or "
                "before the execution time, so `as-consumed` here rests on fact dates alone. A "
                "fact ingested late but dated early is not detectable from this repository."
            ),
        }
    return {
        "available": True,
        "commit": rewound.pin.commit,
        "committed": rewound.pin.committed,
        "consequence": (
            "the overlay was read at the last commit on or before the execution time, so a fact "
            "committed later is absent rather than filtered"
        ),
    }


def read_at(
    repo: ModelRepo, org: str, regime: str, at: str, loaded: Overlay | None = None
) -> tuple[Overlay, dict[str, Any]]:
    """Load `org` under `regime`, and say what the ingestion-history leg did.

    The rewind is a **repository open**, not a filter over today's tree — a filtered view can
    hide a row added since, and it cannot restore an elasticity that was later recalibrated
    (build ticket 35). So `as-consumed` reads a real past model state wherever there is one.

    `loaded` is the caller's already-open overlay at HEAD. Reused where no rewind is needed,
    because the caller had to read the scenario to know what T is before it could ask for a
    regime at all — and reading it twice would cost a git process per file for no answer.
    """
    at = cutoff(at)
    history = {"available": False, "reason": "this regime does not filter by ingestion history",
               "consequence": "every fact in the repository today was visible to this execution"}
    if not FILTERS[require(regime)]["by_ingestion"]:
        return loaded or Overlay.load(repo, org), history

    history = ingestion_history(repo, at)
    if not history["available"]:
        return loaded or Overlay.load(repo, org), history
    return Overlay.load(ModelRepo.open_at_time(repo.model_root, at), org), history


def apply(overlay: Overlay, regime: str, at: str, history: dict[str, Any]) -> tuple[Overlay, dict[str, Any]]:
    """Withhold every fact this regime may not see, and report what was withheld and why.

    The withheld facts are **removed from the overlay**, not flagged on it. That is what "gated by
    construction" buys: an execution reading this overlay has no post-T fact available to
    reference, so referencing one is not an error it could make.

    A claim binds a signal. A claim whose signal was withheld goes with it — a reading of a
    document the twin did not have is not a claim the twin held.
    """
    name = require(regime)
    at = cutoff(at)
    filters = FILTERS[name]
    facts = _dated_facts(overlay)

    withheld: list[dict[str, Any]] = []
    kept: dict[str, dict[str, dict[str, Any]]] = {}
    for collection, docs in sorted(facts.items()):
        surviving = {}
        for ident, doc in sorted(docs.items()):
            if filters["by_date"] and _fact_date(collection, doc) > at:
                withheld.append(_withhold(collection, ident, doc, WITHHELD_POST_T))
                continue
            surviving[ident] = doc
        kept[collection] = surviving

    # A fact the **rewind** removed is not in `facts` at all — it was never loaded, which is the
    # stronger form of withholding and the reason this is a repository open rather than a filter.
    # It shows up as a difference between regimes rather than as an entry here, which is what
    # `gap()` computes and `twin regimes` reports.
    dropped_signals = {w["id"] for w in withheld if w["collection"] == "signals"}
    claims = {
        ident: doc
        for ident, doc in overlay.claims.items()
        if str(doc.get("signal")) not in dropped_signals
    }
    orphaned = sorted(set(overlay.claims) - set(claims))

    # Table-driven rather than a field per collection: `DATED_FACTS` is the declaration, so a
    # collection added there is gated without anybody remembering to add a line here.
    changes: dict[str, Any] = {"claims": claims, **kept}
    gated = dataclasses.replace(overlay, **changes)
    report = {
        "regime": name,
        "at": at,
        "filters": dict(filters),
        "ingestion_history": history,
        "withheld": withheld,
        "claims_withheld_with_their_signal": orphaned,
        "admitted": {
            collection: sorted(kept.get(collection, {})) for collection in sorted(DATED_FACTS)
        },
        "gated_by": (
            "construction: a withheld fact is absent from the overlay this execution read, so "
            "there is no post-T fact available to reference"
        ),
        "known_limits": [
            "a regrade is the twin's own record of a claim's strength, not a fact about the "
            "world, so it is not date-gated; only the rewind removes one dated after T",
            history.get("consequence", ""),
        ],
    }
    return gated, report


def refuse_redacted_subject(
    report: dict[str, Any], overlay: Overlay, components: list[str], where: str
) -> None:
    """A withheld fact the execution could still have reached is a refusal, not a removal.

    This is AC 3, and it is the difference between a gate and a redaction. A post-T fact bound by
    a claim to a component this scenario names is *about the subject matter being forecast*, so
    silently running without it answers a different question from the one that was asked — and it
    would answer it under the one regime whose forecasts score.

    The claims are read from the **pre-filter** overlay on purpose — the one `read_at` returned,
    after any rewind and before the date filter. `apply` has already dropped the claim along with
    its signal, so asking the gated copy what was reachable would ask the redaction what it was
    missing.
    """
    if report["regime"] != AS_CONSUMED:
        return
    withheld = {w["id"]: w for w in report["withheld"] if w["collection"] == "signals"}
    if not withheld:
        return
    # The subject is resolved through `Overlay.forecast_subject`, never read off the claim. Build
    # ticket 68 added a claim kind whose subject is a response, and `claim['component']` would have
    # covered it by accident — silently, in the direction of under-refusing. Whether an enactment
    # is about the subject matter is a decision, and it is taken in one place with its reason.
    named = sorted(
        {
            f"{claim['signal']} (dated {withheld[str(claim['signal'])]['dated']}, bound to "
            f"{overlay.forecast_subject(claim)} by {ident})"
            for ident, claim in overlay.claims.items()
            if str(claim.get("signal")) in withheld and overlay.forecast_subject(claim) in components
        }
    )
    if named:
        raise RegimeError(
            f"{where}: an {AS_CONSUMED} execution at {report['at']} cannot run — "
            f"{'; '.join(named)} is dated after the execution time and is bound to a component "
            "this scenario forecasts. Withholding it would answer a different question from the "
            "one asked, under the one regime whose forecasts score. Run this scenario "
            f"{WITH_HINDSIGHT!r}, or move the execution time past the fact."
        )


def gap(reports: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The three-way gap, computed rather than left for a reader to infer (AC 4).

    Each regime's admitted fact set is a set of ids; the differences between them are the two
    diagnostics. The **model** residual is deliberately not a number here: nothing in this system
    infers a probability from a fact yet — a forecast reads a world model's declared belief — so a
    difference in scored accuracy across regimes would currently be identically zero and would
    read as "sensing is perfect" rather than as "nothing consumes a signal". That is stated, not
    computed, and it is the honest state until the sense→move loop closes.
    """
    admitted = {
        regime: {f"{c}/{i}" for c, ids in report["admitted"].items() for i in ids}
        for regime, report in reports.items()
    }
    consumed, knowable, hindsight = (
        admitted[AS_CONSUMED], admitted[AS_KNOWABLE], admitted[WITH_HINDSIGHT]
    )
    return {
        "admitted_counts": {regime: len(facts) for regime, facts in sorted(admitted.items())},
        "gaps": [
            {
                "between": [AS_CONSUMED, AS_KNOWABLE],
                "localises": SENSING,
                "facts": sorted(knowable - consumed),
                "reading": (
                    "dated on or before the execution time and not in the model repository then. "
                    "It was there to be found and the twin did not have it, so a miss here is a "
                    "sensing failure rather than a modelling one."
                ),
            },
            {
                "between": [AS_KNOWABLE, WITH_HINDSIGHT],
                "localises": INTERPRETATION,
                "facts": sorted(hindsight - knowable),
                "reading": (
                    "dated after the execution time. Nothing knowable by then said it, so reading "
                    "the outcome as foreseeable from these is hindsight rather than interpretation."
                ),
            },
        ],
        "model_residual": {
            "computed": False,
            "why": (
                "wrong under all three regimes localises to the model, and that comparison needs a "
                "forecast that moves when the fact base moves. A forecast here reads a world "
                "model's declared belief and nothing infers it from a signal, so the three "
                "probabilities are identical by construction and a computed residual of zero "
                "would read as 'the model is fine' rather than as 'nothing consumes a signal'."
            ),
        },
    }
