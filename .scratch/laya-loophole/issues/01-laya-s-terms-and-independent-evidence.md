# 01 — Laya's terms and independent evidence

Type: research (AFK)
Status: resolved
Blocked by: none

## Question

Every number this estate has on Laya today comes from the vendor. Find the primary sources, and
name the claims that no primary source supports.

Answer these:

1. What licence covers the weights? What licence covers the inference code? What is known about
   the training data and its provenance?
2. Who is Convai Innovations? Does any evaluation of Laya exist that the vendor did not publish?
3. What is "Jev", the model Laya compares itself against? Is the comparison fair, and who chose
   the benchmark?
4. What does "specialise" mean in practice? Find the documented fine-tune recipe. Report how many
   labelled items per question type it uses.
5. Does the ONNX export produce the same answers as the PyTorch checkpoint? Find the evidence, or
   record that none exists.
6. What exactly does the typed-decisions API accept, and what does it return? Report the shape.
7. Is there a pinnable artefact digest for the weights?

## Done

A research note under `.scratch/laya-loophole/research/`. Every claim carries a primary-source URL.
The note ends with an explicit list of claims that no primary source supports.

## Notes

The vendor claims already on file: 421M parameters, ModernBERT-large backbone, Apache 2.0, CPU
latency 193 to 464 ms, GPU p50 32.8 ms, 0.766 accuracy on typed decisions against Jev's 0.727,
0.362 zero-shot, calibration error 0.466 raw and 0.081 after a per-question-type temperature fit.
Confirm or refute each against a primary source.

## Answer (2026-09-21)

Full note, every claim carrying a primary-source URL:
[`../research/01-laya-terms-and-evidence.md`](../research/01-laya-terms-and-evidence.md).

1. **Licence.** Apache 2.0 for both, unevenly. The code has a real Apache LICENSE file on
   GitHub and an SPDX declaration on PyPI. The weights repo has **no LICENSE file** — the grant
   rests on card metadata. Backbone `ModernBERT-large` is Apache 2.0. **Training data: no provenance published at all** — no corpus, size, method or
   licence anywhere. Ticket 02 is unblocked on licence, never on provenance.
2. **Independent evaluation of Laya: none exists.** The two benchmark repos Convai cites
   (AbdelStark, nibzard) measure only Jev; the reproductions tracker is a catalogue; the one
   third-party fork republishes Convai's table without running it. Every quality number the estate
   holds is Convai measuring Convai.
3. **Jev** is TypeSafe AI's closed System-One model; the $0.042/1M price is TypeSafe's own
   published figure. The benchmark was **not** chosen by Convai — `LocalLLaMA/typed-decisions` is
   authored by `codelion`, who measured Jev at 0.727 himself. The comparison is **unfair, and that
   card says so in advance**: it warns that a specialist fitted on the train split must not be set
   beside a generalist, and that scoring above 0.75 means learning the teacher's quirks. Laya's
   headline does exactly both. AG News was also in Laya's training mix, per Convai's own raw file.
4. **Specialise** = fine-tune on the benchmark's own train split. Counted from the dataset directly:
   **6,000 labelled decisions — 1,800 `choice`, 1,800 `noul`, 2,400 `score` — across 20 question
   schemas at 300 labelled items each.** The estate's six twin skills hold 42 items in total.
5. **ONNX parity: no real evidence.** The "≈1e-5" is prose; the check uses random token ids at one
   shape and stores nothing. The 4-dp end-to-end test covers one example and skips in CI.
6. **API shape** is a clone of Jev's `system_one`. Three answer types documented in the note; it
   throws rather than degrades when options exceed `head_max_len`.
7. **Digests exist.** Revision `1c5edc17a7acd8701df6fc341c0d179f1c62c982`; English weights SHA-256
   `891102d372688fc2a094dac56a384bc537b87c63f21f9f3dac0be2b7cbc8d86c`. Pin both — `main` moved ten
   times in two days.

**Corrections to the numbers on file.** 32.8 ms is the *multilingual* checkpoint; the 421M English
one is 39.5 ms. 0.466 → 0.081 is a mean over 49 suites dominated by multilingual ones; for
typed-decisions alone the same file records 0.207 → 0.129. 421M and 0.362 are confirmed exactly.

**14 claims have no primary source**, listed in §9 of the note.
