# 105 — Two adopter gates fetch their trust root over the network on every CI run

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

ludlow's gate verifies platform's real published evidence with a cold Sigstore TUF cache and every
route to the network blocked. driftwood's and tuppence's cannot. Both of them said they could.

Measured 2026-09-06 while building ticket 101, with the real binary against platform's real
committed bundle for policy 2.0.1 at tag `v2.0.1`:

    HOME=<empty> TUF_ROOT=<empty> HTTPS_PROXY=http://127.0.0.1:1 \
      cosign verify-blob --bundle=2.0.1.json.bundle \
        --certificate-identity-regexp=<that repository's own constant> ... 2.0.1.json

    driftwood  exit 1   tuf: failed to download 13.root.json ... connection refused
    ludlow     exit 0   (through its own gate, which pins its trust material)
    tuppence   exit 1   tuf: failed to download 13.root.json ... connection refused

The same invocation on a machine whose `~/.sigstore` cache is already warm returns `Verified OK`
in about a second, which is why nobody noticed: **the estate's evidence for "offline" was measured
on warm laptops.** A GitHub Actions runner is cold on every run, so every real `shift-left` run of
driftwood's and tuppence's gates reaches Sigstore's TUF CDN before it can check a signature.

## Why it matters, stated without inflation

It is not a correctness hole today: the fetched root is the genuine Sigstore root and the
verification that follows is real. It is three other things.

1. **An availability dependency in a required status check.** When the CDN is slow or unreachable,
   two adopters cannot merge a Renovate bump, and the failure reads as a signature problem.
2. **A trust-distribution difference nobody chose.** ludlow's root is a reviewed, committed file
   that changes only by pull request. The other two take whatever TUF serves at verification time.
   Which of those the estate wants is an architectural question; having both by accident is not an
   answer to it.
3. **It was written down as the opposite.** driftwood's gate said it "verifies the bundle's cosign
   signature offline"; tuppence's said verifying "needs no ambient credential and no network at
   all". Ticket 101 replaced both sentences with a number each harness prints on every run, but the
   underlying difference is still there.

## What ticket 101 already did, so this ticket does not redo it

* ludlow's gate pins the trust material for the legacy bundle shape platform actually publishes
  (`SIGSTORE_ROOT_FILE` / `SIGSTORE_REKOR_PUBLIC_KEY` / `SIGSTORE_CT_LOG_PUBLIC_KEY_FILE`, all
  written out of its one committed `trusted_root.json`, the per-log keys selected by the log
  identifiers the artefact itself names), with `TUF_ROOT` pointed at an empty directory so a warm
  cache cannot stand in for the pin. That code is the pattern this ticket copies.
* Every adopter's harness now prints its own cold-cache exit code on every run
  (ludlow Part E5, driftwood scenario G, tuppence scenario G), and the hub's
  `verify/real-signature/verify-a-real-signature-is-checked.sh` prints one line per adopter. So
  the day this ticket lands, four checks say so by themselves.

## Done

driftwood's and tuppence's gates verify platform's real published evidence with a cold TUF cache
and egress blocked, and the four measurements above print 0 instead of 1.

## What has to be decided, not just typed

1. **Whether each institution commits its own `trusted_root.json`, or whether that is the same
   file three times.** Copying ludlow's bytes into two more repositories is the smallest diff, and
   it also means three copies of a pin that must be refreshed together — with nothing grading that
   they agree. NORTH-STAR §2 says the publisher sets nothing inside an adopter's repository, so a
   platform-served root is not obviously right either. This is an architectural call under
   ADR-0025 and belongs in the ticket that makes it.
2. **What refreshing a pinned root costs.** ludlow's gate refuses BY NAME when the committed root
   carries no key for the log an artefact names, which is the correct failure and a real
   maintenance obligation: Sigstore rotating a CT or transparency log turns three required checks
   red until three pull requests land. A staleness report on the truth surface — "the committed
   root's newest log is N months old" — would turn that from a surprise into a schedule, and
   probably belongs with this work.
3. **Whether the publisher should move to new-format bundles anyway** (ticket 101 remedy 2). If
   platform re-signs, `--trusted-root` works directly and the per-log key selection ludlow needs
   becomes unnecessary for new tags — though already-published bundles on cut tags are immutable,
   so both shapes coexist until every pinned tag has moved. A tag is cut only by `cut-release.yml`
   and dispatched only by the owner, so this half waits on the owner whatever else is decided.

## What remedy 4 costs, measured during ticket 101's review — all three fail CLOSED

The pin ludlow now carries is strictly safer than a live fetch and strictly less available. Every
one of these refuses rather than admits, which is the right direction, and every one is a way
ludlow can go red on a day nothing is wrong with the signature.

1. **One CT key is pinned, and cosign errors on the FIRST SCT whose log is unpinned.** A Fulcio
   certificate carrying two SCTs — one from the pinned log, one from a log the committed root does
   not carry — is unverifiable by ludlow, even though a log it trusts did attest it. Platform's
   certificates carry one SCT today, so this is latent, exactly like the defect ticket 101 fixed.
   Selecting a key per SCT rather than one key for the certificate is the fix, and it belongs with
   whatever this ticket decides about roots.
2. **The root's second transparency-log key is not ECDSA, and the legacy path refuses it.**
   `cf1199…` (2025-09-23) is a non-ECDSA key; presented on the legacy path cosign answers
   `is not type ecdsa.PublicKey`. So a Rekor v2 bundle would be refused by ludlow for a KEY-TYPE
   reason — a refusal about a command line wearing the words of a refusal about a signature, which
   is the exact shape of the original ticket-101 defect. **This is the strongest argument for
   remedy 2 (platform re-signs in the new bundle format) sooner rather than later**, and it should
   be weighed here rather than left to be rediscovered.
3. **The env-var path honours no `validFor` window.** `trusted_root.json` carries validity windows
   per log; `SIGSTORE_CT_LOG_PUBLIC_KEY_FILE` does not read them. The retired 2021–22 CT key is
   therefore as "live" as the current one in ludlow's pin. Nothing is admitted that Sigstore would
   refuse on identity grounds, but a key the ecosystem has retired is still trusted here, and that
   is a property somebody chose by accident rather than on purpose.

## Notes

Charted 2026-09-06 from ticket 101's build. The finding is ticket 101's, not this ticket's: it is
recorded here because a finding that points at no ticket anyone can pick up is not reported, it is
mentioned.

## Answer

Built 2026-09-09. All three adopter gates now verify platform's real published evidence with a
cold TUF cache, an empty `TUF_ROOT` and every proxy pointed at a closed port, and the four
measurements ticket 101 left printing `1` print `0`. The three things the ticket said had to be
decided are decided below, each labelled, and one of them dissolved rather than being answered:
the door ludlow's ticket-101 pin used is the reason per-SCT key selection was needed at all.

### Decision 1 — three committed roots, one per institution, and each institution refreshes its own (`delegated`, ADR-0025)

Each adopter commits its own `.github/scripts/trusted_root.json`. Today all three files are
byte-identical (`sha256 6494e21ea73f…`) and nothing enforces that they stay so.

**Why not one platform-served root.** NORTH-STAR §2: the publisher sets nothing inside an
adopter's repository. A root served by platform would make the party being checked the supplier of
the ruler it is checked by, which is the sentence ADR-0011 exists to prevent and which every one
of these gates already refuses to do for the IDENTITY constant. Trust material is the same kind of
thing as an identity constant, and it gets the same treatment.

**Why not one shared file in the hub.** The hub is not in any adopter's dependency path at
verification time; a gate that reached out of its own repository for its trust root would be
fetching a root over a network again, with a different CDN.

**What that costs, said plainly.** Three copies of a pin that must be refreshed together, and
nothing enforces agreement. That is deliberate: during a Sigstore rotation one institution
refreshes before the others, and a check that graded byte-agreement would go red on a transient
and teach readers to ignore it. So agreement is PRINTED as a fact
(`the 3 adopters' committed roots are byte-identical (sha256 6494e21ea73f)`) and what is GRADED is
the thing that cannot go stale in the reassuring direction — decision 3.

**Who refreshes.** The adopter's own maintainers, by pull request: `cosign initialize`, then copy
`$HOME/.sigstore/root/*/targets/trusted_root.json` over the committed file. The instruction is in
each gate's own ticket-105 block, next to the code that reads it, not in a document somewhere
else. Nobody is told when it is due by a green line; they are told by the dates decision 3 prints.

### Decision 2 — per-SCT key selection is not built, because the door it was needed for is gone (`delegated`)

The ticket asked whether to select a certificate-transparency key per SCT, since ticket 101's
review measured that cosign errors on the FIRST embedded SCT whose log the pin does not carry, so
a two-SCT Fulcio certificate is unverifiable under a single-key pin.

**That is a property of the LEGACY verification path, not of pinning.** ludlow's ticket-101 pin
fed `SIGSTORE_ROOT_FILE` / `SIGSTORE_REKOR_PUBLIC_KEY` / `SIGSTORE_CT_LOG_PUBLIC_KEY_FILE`,
because cosign v3.1.3 refuses `--trusted-root` for the legacy bundle shape platform publishes.
Those variables take ONE key per role and cosign demands a key for every SCT it finds. So this
build took the other door instead: **a legacy bundle is re-encoded, locally, into the v0.1
Sigstore bundle `--trusted-root` reads**, and the whole committed root verifies it.

Nothing is signed and nothing is trusted that the served bundle does not carry: the certificate,
the signature, the Rekor entry body, its log id, its log index, its integrated time and its signed
entry timestamp are copied across, and **the only computed field is the artefact's own sha256** —
which cosign checks against the artefact it is handed anyway. A re-encoding that is wrong is a
refusal, never an acceptance; the selfcheck grades the mapping field by field on bytes it lays
down itself, and a legacy bundle missing any of those fields refuses by name before cosign is
called. The DER parsing and per-role key selection ludlow carried are **deleted**.

What that buys, each measured on this build rather than argued:

| ticket 101's measured cost of the pin | on the `--trusted-root` door |
|---|---|
| cosign demands a key for EVERY embedded SCT, so a two-log certificate is unverifiable | sigstore-go applies a THRESHOLD: `only able to verify 0 SCT entries; unable to meet threshold of 1` is what the wrong-CT-key attack prints on every harness run — a threshold of one, not a key per SCT |
| the env-var path honours no `validFor` window, so the retired 2021–22 CT key is as live as the current one | windows are honoured: the `ct-window-closed` attack (the current CT key given an `end` before the artefact was signed) REFUSES on all three, cold and warm |
| the root's second transparency-log key is not ECDSA, so a Rekor v2 bundle would be refused for a KEY-TYPE reason | that refusal lived on the legacy door and is gone with it; the root's `PKIX_ED25519` key loads |

The third row matters beyond itself: ticket 101 called it **"the strongest argument for remedy 2
sooner rather than later"**. That argument no longer exists, which is why decision 4 weighs remedy
2 lower than ticket 101 did.

### Decision 3 — the staleness report is graded on the served artefact, not on a date (`delegated`)

`verify/trust-root/verify-the-committed-trust-root-is-dated.sh` (+ `trust_root.py`, manifest row,
`tests/test_trust_root.py`, 15 cases).

**PRINTED, never graded**, per adopter: the committed root's sha256, the date it was committed and
how many days ago, the date its newest log key starts and how many days ago, and every key's
validity window against today as `current since <date> (<n> days)` / `retired <date> (<n> days
ago)` / `not yet valid (starts <date>, in <n> days)`. Today, all three adopters:

    committed trust root sha256 6494e21ea73f, committed 2026-09-09 (0 days ago)   [ludlow: 2026-08-24 (15 days ago)]
    newest log key starts 2025-09-23 (351 days ago); pins platform v2.0.1
      tlog  https://rekor.sigstore.dev       key c0d23d6ad406973f PKIX_ECDSA_P256_SHA_256: current since 2021-01-12 (2065 days)
      tlog  https://log2025-1.rekor.sigstore.dev key cf1199155bddd051 PKIX_ED25519:        current since 2025-09-23 (351 days)
      ctlog https://ctfe.sigstore.dev/test   key 086092f02852ff68 PKIX_ECDSA_P256_SHA_256: retired 2022-10-31 (1408 days ago)
      ctlog https://ctfe.sigstore.dev/2022   key dd3d306ac6c71132 PKIX_ECDSA_P256_SHA_256: current since 2022-10-20 (1420 days)
      ca    https://fulcio.sigstore.dev: retired 2022-12-31 (1347 days ago)
      ca    https://fulcio.sigstore.dev: current since 2022-04-13 (1609 days)
    the 3 adopters' committed roots are byte-identical (sha256 6494e21ea73f)

**No sentence of the form "the root is fresh" is printed**, because that sentence goes stale the
day it is written — this ticket's parent lesson.

**GRADED, because it cannot go stale in the reassuring direction:** every log the SERVED artefact
names is carried by THAT adopter's committed root, by key id, with the artefact's own timestamp
inside that key's `validFor` window. The served artefact is platform's own committed
`computed-semver/evidence/<version>.json.bundle` at the tag THAT ADOPTER pins, read with
`git show` at the tag; the logs are the SCT log ids and timestamps out of the Fulcio certificate's
own DER and the Rekor log id and integrated time out of the bundle's own `rekorBundle`. The
operation is the adopter's committed root at HEAD, read with `git show`. The day this is false the
adopter's gate refuses by name, so **this line is red before a Renovate pull request is**. A root
that is absent, an adopter that pins no tag, a tag this platform clone lacks, or a bundle that
cannot be read is a could-not-look BY NAME, never a pass.

Today it grades 8 log names per adopter, 24 in all, all carried, all inside window.

### Decision 4 — remedy 2 stays the follow-on, and it is worth less than ticket 101 thought (`delegated`)

Remedy 2 is platform re-signing its evidence in the new bundle format. It still waits on the
owner: a tag is cut only by `cut-release.yml` and dispatched only by the owner, and nothing here
fakes one.

**What it would remove:** `sigstore_bundle()` and its selfcheck in three gates — about 45 lines
each — for tags cut after it lands.

**What it would NOT remove, which is the part ticket 101 did not have to weigh:** the pin itself,
the three committed roots, the refresh obligation, decision 3's check, or the re-encoding, because
bundles on already-cut tags are immutable and every adopter pins `v2.0.1` today. Both shapes
coexist until every pinned tag has moved, so `sigstore_bundle()` has to stay after remedy 2 lands
and stays exercised by the selfcheck.

**So it is a tidying, not a fix.** Ticket 101 rated it urgent on the strength of the non-ECDSA
Rekor key refusing on a key-type ground — a refusal about a key type wearing the words of a
refusal about a signature. That refusal lived on the legacy env-var door, and this build removed
the door.

### Is anything now LESS safe?

Asked first, because two gates that failed closed on a cold cache now accept, and one gate's
verification path changed shape entirely.

**Availability: yes, deliberately, and that is the whole trade.** A stale or wrong root now
refuses where a live fetch used to paper over it. Decision 3 turns that into a schedule.

**Correctness: measured no, on every axis this estate can reach.** Each of these was run against
platform's real published bundle for policy 2.0.1 at `v2.0.1`, cold `HOME`, empty `TUF_ROOT`,
every proxy at a closed port with `NO_PROXY`/`no_proxy` cleared:

* one changed signature byte → refused by all three, naming the signature
  (`failed to verify log inclusion: transparency log signature does not match`);
* **one changed byte of the ARTEFACT — new here, because the re-encoding computes the artefact's
  digest itself and a check that computed it from a tampered artefact would verify a lie** →
  refused by all three: `transparency log hashedrekord entry digest f9dd3389… does not match
  artifact 858a9472…`. driftwood and tuppence read the served evidence from platform's working
  tree and ludlow reads it out of git at the pinned tag, so the tamper was planted in both places;
* a foreign identity constant → refused (harness E/E4/E2);
* a wrong Rekor key, a corrupt Rekor key, a wrong CT key, a wrong Fulcio CA, a CT key whose window
  closed before the artefact, and an absent root → refused on all three, cold AND warm, on the
  trust material and never on the network (12 cases per adopter);
* an unplaceable bundle shape → refused BY NAME before cosign is invoked.

**One refusal IS removed, and it is named rather than left to be found.** Under ticket 101's
env-var pin, an SCT from a log the committed root does not carry was FATAL. Under `--trusted-root`
it is skipped and the threshold is one verified SCT. So a Fulcio certificate carrying one SCT from
a pinned log and one from an unpinned log is ACCEPTED here where ludlow refused it three days ago.
That is Sigstore's own policy and it is exactly what makes ticket 101's cost 1 go away, but it is
a refusal removed and it is recorded as one. Nothing platform has published carries two SCTs:
decision 3's check reads the DER of every bundle at every adopter's pin and names exactly one
ctlog per artefact.

**The refusal TEXTS changed, because the door changed.** Ticket 101's negative proofs quoted the
legacy path's wording — `rekor log public key not found for payload`, `P256 point not on curve`,
`ctfe public key not found for payload`, `x509: certificate signed by unknown authority`. Those
strings are cosign's legacy-path messages and none of them appears now. The ATTACKS all still
refuse; sigstore-go words them differently, and in each case more specifically:

| attack | refusal, measured on this build, all three adopters |
|---|---|
| wrong Rekor key | `failed to verify log inclusion: not enough verified log entries from transparency log: 0 < 1` |
| corrupt Rekor key | `setting trusted material: loading trusted root: failed to parse public key for tlog: https://rekor.sigstore.dev asn1: …` |
| wrong CT key | `failed to verify signed certificate timestamp: only able to verify 0 SCT entries; unable to meet threshold of 1` |
| wrong Fulcio root | `failed to verify leaf certificate: leaf certificate verification failed` |
| CT key window closed before the artefact | same as wrong CT key — the key is not carried for this artefact |
| absent pins, empty `TUF_ROOT`, egress blocked | `tuf: failed to download 13.root.json` (the contrast each harness measures on every run) |
| pinned-but-wrong, WARM `~/.sigstore` | still refused, identically — the env beats the cache |

No script anywhere in the estate still asserts the old strings; they were quoted only in ticket
101's own record, which is history and stays as written.

### The zero-connections proof

Exit codes say a run did not SUCCEED at reaching the network; they do not say it did not TRY. So
the gates were run again through a proxy that logs every connection attempt and serves none
(`127.0.0.1:18443`, one line per request), with `HTTPS_PROXY`/`HTTP_PROXY`/`ALL_PROXY` and their
lowercase spellings all pointed at it, `NO_PROXY` and `no_proxy` cleared, a fresh empty `HOME` and
a fresh empty `TUF_ROOT` per run, each gate's own `verify_evidence()` against platform's real
published evidence for policy 2.0.1:

    contrast: cosign verify-blob with NO trust root   exit 1, 2 connections logged
                                                      CONNECT tuf-repo-cdn.sigstore.dev:443
                                                      CONNECT tuf-repo-cdn.sigstore.dev:443
    driftwood's own gate                              VERIFIED 2.0.1, exit 0, 0 connections
    tuppence's own gate                               VERIFIED 2.0.1, exit 0, 0 connections
    ludlow's own gate                                 VERIFIED 2.0.1, exit 0, 0 connections

The contrast is what makes the zero mean something: the same proxy, on the same machine, in the
same minute, logged the unpinned invocation twice.

### Red before green, exactly

`G` is the scenario each adopter's harness prints on every run. Before this ticket, on the same
machine, same command, same real bundle:

    driftwood scenario G   exit 1   tuf: failed to download 13.root.json ... connection refused
    tuppence  scenario G   exit 1   tuf: failed to download 13.root.json ... connection refused
    ludlow    Part E5      exit 1   (the contrast: the same bytes with the pin removed)

    driftwood scenario G   exit 0   and GRADED, not merely printed
    tuppence  scenario G   exit 0   and GRADED, not merely printed
    ludlow    E2           exit 0   unchanged, E5 still prints the contrast's exit 1

And the hub's own three notes, which read `driftwood 1 / ludlow 0 / tuppence 1` on main:

    note: driftwood: its own gate verifies platform's real published bundle with a cold TUF cache
          and every proxy pointed at a closed port -- exit 0, no network needed
    note: ludlow:    ... exit 0, no network needed
    note: tuppence:  ... exit 0, no network needed

`trust_root.py`'s two newest rules were written red: `a bundle that could not be read is false`
and `and says so, rather than saying the artefact named no log` both failed against the grader as
it stood — it called an unreadable served bundle "names no transparency log at all", which is a
different fact — before the FAIL branch that distinguishes them was written.

### Ticket 101 review item R2-1, fixed while here

The hub's offline note derived the words "fetches a Sigstore trust root" from a non-zero exit
alone. That is true of a gate with no pin and false of a gate refusing a wrong one — and after
this ticket every gate is the second kind, so the wrong sentence would have been printed at the
first stale root. `offline_note()` now greps the gate's own output for `tuf|dial tcp|connection
refused` before saying anything about the network, and otherwise prints
`exit N ... for a reason that is not the network -- its output names no TUF fetch and no refused
connection: <last line>`.

### The defect this build's own review found

tuppence's `scripts/verify-adopter-gate.sh` defines its own shell function named `cut` (the
release helper, line ~459). Scenario H's `echo "... -- $(echo "$tail_line" | cut -c1-150)"` ran
THAT — four real release scripts, twelve times — and printed their last line,
`no evidence changes to commit (no policy tags in this dispatch)`, as the refusal text of every
doctored-root case. The grading was correct throughout (it greps the gate's captured output for
the case's own refusal); every printed REASON was another command's output. Fixed by making the
printed line the line graded — the case's own needle, matched in the gate's output, truncated by
parameter expansion rather than by a command the file shadows. **A green whose evidence sentence
is another program's stdout is the same defect class as a green that never measured anything**,
and it was invisible in an exit code.

### Files

* driftwood `.github/scripts/adopter-gate.py`, `.github/scripts/trusted_root.json` (new),
  `scripts/verify-adopter-gate.sh` (G graded, I added).
* tuppence `.github/scripts/adopter-gate.py`, `.github/scripts/trusted_root.json` (new),
  `scripts/verify-adopter-gate.sh` (G graded, H added, D2 rewritten).
* ludlow `.github/scripts/adopter_gate.py` (net −132 lines: the DER parser and per-role selection
  out, the re-encoding in), `verify-adopter-gate.sh` (E6 added).
* hub `verify/trust-root/` (new), `tests/test_trust_root.py` (new),
  `verify/real-signature/real_signature.py` + its script (R2-1), `tests/test_real_signature.py`,
  `talk/verify-manifest.txt` (one new row, three rewritten).

No workflow file is touched in any repository, so no `workflows` grant is needed for any of the
four pull requests.

### How it is graded

* `verify/trust-root/verify-the-committed-trust-root-is-dated.sh` — decision 3's sentence.
* `verify/real-signature/verify-a-real-signature-is-checked.sh` — unchanged sentence, three
  notes now reading 0, and the R2-1 wording.
* `verify/fold-agreement/verify-fold-agreement.sh` — still green on all four planted movements.
* `driftwood/scripts/verify-adopter-gate.sh` A–I, `tuppence/scripts/verify-adopter-gate.sh` A–H,
  `ludlow/verify-adopter-gate.sh` Parts A–E6.
* each gate's own `--selfcheck`; `tests/test_trust_root.py` (15), `tests/test_real_signature.py`
  (25).

**What the unit CI does NOT say, repeated from ticket 101 because it is still true.** No unit CI
job runs `--selfcheck` or a harness. `shift-left` reaches `verify_evidence()` only when the
composed member set moves. Everything that grades this ticket ran locally and in the hub gate.

## Waits on the owner

1. **Re-signing platform's evidence in the new bundle format** (ticket 101 remedy 2). A tag is cut
   only by `cut-release.yml` and dispatched only by the owner. Decision 4 says what it removes and
   what it does not; nothing here is blocked on it.
2. **Whether platform policy 4.0.0's major is accepted for driftwood, for ludlow and for
   tuppence.** Unchanged from tickets 99 and 101, untouched here, and still the whole of
   `verify-unreviewed-major-in-window.sh`'s remaining red.
3. Nothing else.

Map line: Ticket 105 (2026-09-09): driftwood's and tuppence's gates stopped fetching a Sigstore
trust root over the network on every CI run -- all three adopters now commit their own
`trusted_root.json` (byte-identical today, and nobody serves one to anybody, because the party
being checked does not supply the ruler) and hand it to cosign whole through `--trusted-root`,
with a legacy bundle re-encoded locally into the v0.1 Sigstore shape that door reads and the
artefact's own sha256 as the only computed field; that dissolved rather than answered the per-SCT
key question -- sigstore-go applies a threshold of one verified SCT where the legacy env-var path
ludlow used demanded a key for every one -- and it honours `validFor` windows and loads the
non-ECDSA Rekor key, which removes the argument ticket 101 called the strongest case for the
publisher re-signing; measured through a logging proxy the three gates made 0 connections where
the unpinned contrast made 2, a changed signature byte and a changed artefact byte are both
refused, and 12 doctored-root attacks per adopter refuse on the trust material and never on the
network, cold and warm; `verify/trust-root/` prints each committed root's age and every key's
validity window as dates and numbers and grades only what cannot go stale reassuringly -- that
every log the served bundle at that adopter's pin names is carried by that adopter's own root
inside the key's window.
