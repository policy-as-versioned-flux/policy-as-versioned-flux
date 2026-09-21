# 02 — Laya runs offline, pinned, and measured here

Type: task (AFK)
Status: open
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
