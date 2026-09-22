# bench/loophole: attack one norm document in three rounds

This is the procedure [ADR-0030](../../docs/adr/0030-loophole-runs-as-an-external-tool-in-rounds-and-the-estate-keeps-the-pointer.md)
decides. Read the ADR before you run anything. Eco-system ticket 115 wrote this page and moved
the harness here from `.scratch/laya-loophole/bench/`.

loophole is an adversarial agent loop by a third party. It reads a norm stated in prose and looks
for scenarios that are legal but wrong (loopholes) and wrong but legal to refuse (overreaches).
This estate's norm documents are its ADRs.

## What `bench/` is

`bench/` holds evaluation instruments that are **not gate checks**. Nothing here runs on a clock,
nothing here grades the truth surface, and no workflow calls it. `verify/` is the gate and
`tests/` holds the deterministic checks. What a loophole round finds only reaches the gate as a
deterministic test a survivor earns, behind a reviewed pull request (ADR-0030 point 8).

## What may never happen here

loophole carries **no licence**. All rights are reserved. So:

- never vendor it, fork it into the estate, or copy its source into this tree;
- never reimplement its prompts, and never commit its prompt text;
- never run it on a clock, and never make it a gate check.

The harness in this directory holds no loophole source and no loophole prompt. It imports a
clone you keep **outside** the project tree, through `LOOPHOLE_SRC`, and it refuses to start if
`LOOPHOLE_SRC` or `--full-log` points inside the tree.

## The files

| File | What it is |
|---|---|
| `loophole_round.py` | One round: two finders, one judge per candidate, 8 `claude -p` calls. Its guards fail the run (below). |
| `check_no_prompt_leak.py` | The prompt-leak check. Takes every 8-word run in loophole's `prompts.py` and looks for it in the files you name. |
| `rounds/<document>/` | Committed rounds. One `principles.md` per document, one `round-N/` per round. |
| `../../tests/test_loophole_round.py` | Holds the guards down with no clone and no model. |

## The budget

Measured on the three rounds against ADR-0022 (tickets 07 and 11), from their `calls.jsonl`:

| | One round | Three rounds |
|---|---|---|
| `claude -p` calls | 8 | 24 |
| Wall time | 173.5 s to 185.8 s | 539.0 s, about 9 minutes |
| List price | 0.4069 to 0.4197 USD | 1.2416 USD |

The subscription absorbs the list price. The owner ruled on 2026-09-21 that there is no paid
Anthropic API spend, which is why the transport is `claude -p` and not the API.

**That is the cheap half.** The real cost is the deterministic check. Three rounds give about 18
candidates. At the measured survival rate of 2 in 6, that is about 6 real defects. Checking 6
candidates took one whole ticket (Laya map ticket 08), so checking 18 costs roughly three times
that, about half a ticket per candidate. Budget the checking, not only the calls.

## Before the first round

1. **Clone loophole outside the tree.** Any scratch directory works. The three ADR-0022 rounds
   and the three ADR-0026 rounds ran at commit `129f7c0ee76a79600b8c3f9b35b9687c63b1f95c`.

   ```sh
   git clone https://github.com/brendanhogan/loophole.git <scratch>/loophole
   git -C <scratch>/loophole checkout 129f7c0ee76a79600b8c3f9b35b9687c63b1f95c
   export LOOPHOLE_SRC=<scratch>/loophole
   ```

   A newer commit is allowed. The summary records the one you ran, and the counter control below
   refuses a parser that stopped behaving the way the counters expect.

2. **Build a venv outside the tree.** The agents need `pydantic` only. The ADR-0026 rounds ran
   on Python 3.12.14 with `pydantic==2.12.5`, the version loophole's `uv.lock` names.

   ```sh
   python3.12 -m venv <scratch>/loophole-venv
   <scratch>/loophole-venv/bin/pip install 'pydantic==2.12.5'
   ```

3. **Log in to `claude`** with the subscription. Do not set `ANTHROPIC_API_KEY`.

4. **Run both negative controls.** No model call is made.

   ```sh
   <scratch>/loophole-venv/bin/python bench/loophole/loophole_round.py --controls-only
   ```

   It must print `counter control: 5/5` and `leak control: 1287/1287` (or whatever count the
   clone's `prompts.py` gives, with both sides equal). Exit 3 means a control did not fire. Stop.

## Choosing the document

Pick an ADR this estate wrote that states a norm in prose. Hold it fixed: it must be committed,
and the harness records its commit and refuses a file with uncommitted changes. Write
`rounds/<document>/principles.md`: the estate's own normative claims the document serves, each
quoted or paraphrased from `NORTH-STAR.md`, `CONTEXT.md` or an ADR, with the sources named at the
top. Invent nothing. Commit it before the first round.

Attacked so far: ADR-0022 (three rounds, in `.scratch/laya-loophole/research/`) and ADR-0026
(three rounds, in `rounds/adr-0026/`). The next document is named in eco-system ticket 115's
build record.

## A round

Run the three rounds **one after another**, never in parallel, each into an empty directory:

```sh
<scratch>/loophole-venv/bin/python bench/loophole/loophole_round.py \
  --code        docs/adr/<the ADR>.md \
  --principles  bench/loophole/rounds/<document>/principles.md \
  --domain      "<one line naming what the document governs>" \
  --out         bench/loophole/rounds/<document>/round-1 \
  --ticket      <the ticket you run under> \
  --round       1 \
  --full-log    <scratch>/<document>-round-1.jsonl
```

`--full-log` is optional. It holds loophole's prompt text verbatim, so it must sit outside the
tree, and the harness refuses it otherwise. Never pass `--bare` to `claude`.

Exit codes: **0** a clean round; **1** a round ran and is not clean, and `summary.json` says why
under `failures`; **2** a guard refused; **3** a negative control did not fire. Only a clean
round is committed. Re-run a round that exits 1 into a fresh directory and keep the failed one
out of the tree.

## The guards, and why each fails the run

- **`--bare` never reaches `claude -p`.** `claude -p --bare` never reads the login. With no API
  key it exits 0 and returns "Not logged in" as its result. The parser finds no scenarios and
  loophole would print that the code appears robust. The harness refuses the flag, and it also
  refuses the failure shape (`is_error: true`, a non-zero exit, or a reply that is not JSON)
  whatever flag caused it.
- **Two counters at zero.** `parse_failures` counts scenario tags the parser did not take.
  `under_production` counts scenarios asked for and never opened. A model that abandons the
  format opens no tag, so the first counter reads 0; only the second sees it. The harness checks
  both against loophole's own parser before any call is spent, and fails the round if either
  is above zero.
- **A judge reply with no verdict tag fails the round.** The upstream judge reads a missing
  `<verdict>` as "unresolvable" with no warning (ADR-0030 point 5).
- **The prompt-leak check runs over the round's own files** before the harness returns, and a
  hit fails the round.

## After the round, before `git add`

Run the leak check yourself over every file you are about to commit, even though the harness ran
it. Files can change between the run and the commit.

```sh
LOOPHOLE_SRC=<scratch>/loophole python bench/loophole/check_no_prompt_leak.py \
  bench/loophole/rounds/<document>
```

It must end `total leaked runs: 0` and exit 0. Then stage the round's three files by name:
`calls.jsonl`, `candidates.json`, `summary.json`.

## What a round writes down

`summary.json` carries what ADR-0030 point 9 lists: `target` (path, commit, sha256), `harness`
(its sha256 and the leak check's), `model_served`, `model_calls`, `wall_time_s`,
`list_price_usd`, `counters` (both counters and the judge's missing verdicts), `candidates`,
`prompt_digests`, and `ticket` from `--ticket`. `candidates.json` holds every candidate with the
judge's verdict. `calls.jsonl` holds every response and a sha256 and length for each prompt,
never the prompt.

## What to do with the candidates

The judge's verdict is not a filter. It called 17 of 18 ADR-0022 candidates resolvable. **Every
candidate goes to a deterministic check against the code, whatever the judge said.** Test the
place the candidate points at, never the sentence it wrote. Count the survival rate on the
candidates as stated. Chart the checking as its own ticket; a round does not check itself.
