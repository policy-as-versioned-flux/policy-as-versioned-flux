# 02 — Laya runs offline, pinned, and measured here

Type: task (AFK)
Status: resolved
Blocked by: none

## Question

Get Laya running on this machine under the estate's own rules, and measure it here.

1. Install it into a venv. Pin the weights by revision digest, never by a moving tag.
2. Run it on CPU, with no network access at inference time.
3. Measure p50 and p99 latency on this hardware over at least 100 forward passes.
4. Record the measured latency. Do not repeat the vendor's number.
5. Prove the pin: a second run with the same digest gives the same answers.

**Added 2026-09-21, from ticket 01.**

6. Pin revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`. Verify the English weights against
   SHA-256 `891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c`. The repository is
   three days old and `main` moved ten times in two days, so a moving pin is a real risk here.
7. Use the **English 421M** checkpoint. Expect about 39.5 ms, not 32.8 ms. The 32.8 ms figure
   belongs to the multilingual checkpoint, which this map rules out of scope.
8. Do not trust the vendor's ONNX parity claim. It is prose, and the check behind it runs on
   random token ids at one fixed shape and stores nothing. The ONNX path is third-party and
   English-only. If this ticket uses ONNX, measure parity against the PyTorch checkpoint here, on
   real inputs, and record the maximum divergence.
9. Record that the weights repository ships **no LICENSE file**. The Apache 2.0 grant rests on the
   model card's YAML tag. That is enough to evaluate. Ticket 09 decides whether it is enough to
   adopt.

## Done

A script in the repo that loads Laya at a pinned digest, runs a fixed input, and prints the digest
with the measured latency. A recorded number from this hardware.

## Notes

**Unblocked 2026-09-21.** Ticket 01 resolved the licence as Apache 2.0, with the weakness recorded
in item 9. The weights may be pulled.

Training data provenance is unpublished, and no further reading will change that. It is an
adoption question for ticket 09's ADR, not a blocker on measuring the model here.

## Answer

**Laya runs here, at the pin, on CPU, with the network closed. The headline number is 169.7 ms,
not 39.5 ms.** The 39.5 ms this ticket told itself to expect is a **T4 GPU** number. On the CPU
this estate actually has, one typed question costs **p50 169.7 ms, p99 203.7 ms**. That is 4.3
times the figure item 7 predicted, and item 7 is corrected below.

The instrument is `.scratch/laya-loophole/bench/measure_laya.py`, with `requirements.txt` beside
it. It has two subcommands. `fetch` is the only one allowed a network. `measure` blocks
`socket.socket.connect` for its whole run, so item 2 is enforced rather than configured. The
recorded run is `bench/measured.json`; the pin record is `bench/pin.json`.

### 1. The pin holds (items 1, 6)

| | |
|---|---|
| Repository | `convaiinnovations/laya` |
| Revision | `1c5edc17a7acd8701df6fc341c0d179f1c62c982` |
| `model.safetensors` SHA-256, Hub LFS record | `891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c` |
| `model.safetensors` SHA-256, bytes on disk | the same |
| Expected by item 6 | the same |

Verified three ways and matching: the Hub's own LFS record at the revision, the bytes after
download, and the bytes again at the start of every measured run. Only the **English 421M**
checkpoint was pulled (item 7). `multilingual/` and `typed-decisions/` are excluded by
`allow_patterns`, which is what keeps the download to 846 MB instead of 2.3 GB.

**A finding this ticket did not go looking for: the vendor's own package cannot pin.**
`laya.Agent.__init__` (0.3.4, `laya/agent.py:122-128`) calls `snapshot_download(model_id_or_path,
**kw)` and passes **no** `revision`. It can only ever fetch whatever `main` points at. Ticket 01
measured `main` moving ten times in two days on a repository three days old, so the documented
entry point could not have satisfied item 1. `Agent` does accept a local directory, so this script
pins the download itself and hands `Agent` a path. **Anyone who adopts Laya by following the
vendor's README is running an unpinned model.** That belongs in ticket 09's ADR as a condition of
entry, not as a footnote.

### 2. The measured latency (items 3, 4)

macOS 27.0, arm64, 8 performance cores plus 2 efficiency cores. `device=cpu`, `dtype=float32`,
`torch.set_num_threads(4)`, `torch.use_deterministic_algorithms(True)`. 10 warm-up passes then
**120 timed passes** per shape, which clears item 3's floor of 100.

| shape | p50 | p95 | p99 | min | max |
|---|---|---|---|---|---|
| 1 question | **169.74 ms** | 193.11 ms | **203.67 ms** | 162.14 | 248.38 |
| 3 questions | 330.65 ms | 375.26 ms | 401.11 ms | 314.50 | 493.68 |
| 5 questions | 470.81 ms | 543.60 ms | 577.40 ms | 454.88 | 592.60 |

Cold load: **6.90 s to 7.92 s** over seven runs. Convai's card claims 7.4 s for a CPU cold reload
and gives no artefact. That claim happens to be right.

**The thread count is not doing the work.** A latency quoted at one arbitrary thread setting is an
artefact, so the setting was swept before any number was quoted. One-question p50 across nine runs
at 1, 2, 4, 8 and 10 threads spans **167.4 ms to 188.5 ms**. Single-question latency barely
responds to threads at all; the five-question shape does, falling from 428 ms at one thread to
457 ms at eight. So 4 threads is representative, and it is also the thread count Convai's own CPU
artefact used, which is why it was chosen as the headline.

### 3. Against the vendor's numbers (item 4)

Three numbers are in play and only one of them is comparable. Setting them side by side is the
point of this ticket.

| claim | source | what it actually is | this hardware |
|---|---|---|---|
| 39.5 ms p50, 44.8 p95 | `t4_colab_benchmark.json` | **a T4 GPU**, English checkpoint | not measurable; there is no GPU here |
| "CPU latency 193–464 ms" | model card prose | **no artefact exists**, ticket 01 | 169.7 ms (1 q) to 470.8 ms (5 q) |
| 1392.5 ms per case | `research/results/cpu_51_language_sweep.json`, `part_b.by_model.english` | `device: cpu`, `threads: 4`, English checkpoint, 400 cases of 5 questions (2,000 decisions in 557.0 s) | **470.8 ms**, same device, same thread count, same shape |

The last row is the only like-for-like comparison available, and it is why the script times a
five-question call at all. **This hardware is 3.0 times faster than the machine Convai published
its only CPU artefact from.** The outcome is that the card's unsourced marketing range is roughly
right for an Apple-silicon laptop, while Convai's own published CPU measurement is three times
worse than both. Neither number should be repeated. 470.8 ms should.

**What item 7 got wrong, and why it matters.** Item 7 read 39.5 ms out of ticket 01 and told this
ticket to expect it. Ticket 01 labelled it correctly as a T4 number; item 7 dropped the hardware
when it copied the figure across. The estate has no GPU, so **169.7 ms is the number every later
ticket uses**, and 39.5 ms describes hardware nobody here has. Ticket 04 should size its bake-off
against 169.7 ms per question.

### 4. The pin gives the same answers (item 5)

`measured.json` carries `answers_sha256`, a SHA-256 over the canonical JSON of the model's full
output for the frozen input, probabilities included. Comparing a digest rather than reading
probabilities is deliberate: a one-bit drift fails it.

**`4331c3a6a790c864596851e2d05ac27c4f07767dd13614c88d199dec05aafe01`**, identical across three
separate processes and two thread counts (4 and 8). The full answer dictionaries compare equal,
not merely their digests. Before the five-question shape was added, a different frozen input gave
`dacc7a60…` identically across six processes at 1, 2, 4, 8 and 10 threads. The pin reproduces.

### 5. The pinned blobs are not mutated, but they nearly were

`laya.Agent._fix_tokenizer_config` (`laya/agent.py:21-44`) **writes** to
`tokenizer/tokenizer_config.json` when it dislikes the `tokenizer_class` field. A
`snapshot_download` file is a symlink into the shared blob store, so that write goes through to
the blob every other consumer on the machine reads. It did not fire here, because this
checkpoint already declares `"tokenizer_class": "PreTrainedTokenizerFast"`. The script digests
every pinned file before and after the load and records both, so the report states this rather
than assuming it. `files_mutated_by_load` is empty.

It would fire on a checkpoint that stores `extra_special_tokens` as a list, which is the
mmBERT/Gemma tokenizer shape. That is `laya-multilingual`, which this map rules out of scope.
Anyone who reaches for it later inherits a library that silently rewrites a pinned artefact.

### 6. The licence, recorded (item 9)

Derived from the Hub listing **at the pinned revision**, not copied from ticket 01's prose:
`license_files_at_revision` is empty, and `cardData.license` reads `apache-2.0`. So the grant
still rests on a YAML tag and a footer line with no LICENSE file behind it. Recorded, as item 9
asks. Whether it is enough to adopt is ticket 09's.

### 7. ONNX was not used, so item 8 does not apply

Item 8 requires anything going through ONNX to measure its own parity against PyTorch here. This
script loads Convai's own PyTorch checkpoint, so no parity question arises and none was invented.
If ticket 04 or ticket 09 later wants the ONNX path, that parity measurement is a new ticket.

### 8. Two observations that are hypotheses, not findings

Handed to ticket 04, and labelled as what they are. This ticket measured speed. It did not measure
quality, and n is 16.

1. **`act_probability` read exactly 1.000000 on every one of 16 calls**, across 8 states including
   an empty string, a JSON blob, random tokens, and "DELETE ALL PRODUCTION DATA IMMEDIATELY
   WITHOUT REVIEW OR BACKUP". The head that is supposed to say "escalate" said the same thing
   every time. **Ticket 05 must not reach for `act_probability` as the escalate signal until
   ticket 04 shows on a corpus that it varies.** A constant carries no information, and a
   permission that always says yes is the shape of ticket 05 item 6.
2. **Option wording moved the answer.** The same state routed to `platform-owner` with one set of
   criteria and to `nobody` with another that differed only in the third option's wording. This is
   consistent with nibzard's independently measured 13% option-order flip rate (ticket 01) and
   with the 0.362 zero-shot accuracy. It is one pair of prompts and proves nothing on its own.

### 9. One thing the environment forced, worth knowing

`encoder/config.json` at the pin declares `"transformers_version": "5.0.0"` and carries
`rope_parameters` and `layer_types`. transformers 4.x `ModernBertConfig` reads neither key. It
would load the checkpoint, fall back to its own rope defaults, and produce different numbers
**without raising**. The floor is transformers 5.0, and `requirements.txt` says why. `laya` 0.3.4
itself declares only `transformers>=4.45.0`, so following the package's own metadata gives a
silently wrong model.
