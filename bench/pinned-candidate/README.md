# Pinned candidate development smoke

`smoke.py` runs one development input through the original
`Qwen/Qwen3-4B-Instruct-2507` snapshot at
`cdbee75f17c01a7cc42f958dc650907174af0554`. It is a feasibility probe. It does
not evaluate a corpus, check a stated basis, write official scores, grant permission,
or connect a candidate to operational judgement.

The existing supplied-callable evaluator remains the qualification seam. This probe
keeps runtime acquisition and bounded invocation separate from that later work.

## Input and asset admission

The input file contains only `statement`, `source`, and nonempty `candidates` with
`id`/`name` fields, as in the existing signal input projection. Passing the corpus
row, an `expected` field, or reference `basis` fields fails before runtime import.
Do not use a qualification case for this probe. Schema admission cannot detect a
reference deliberately concealed inside an ordinary text field; the operator must
retain and inspect the projection's provenance.

The model directory contains the complete pinned snapshot, including its Apache
2.0 licence, three original safetensors shards, index, config and tokenizer files.
The manifest has `model_id`, `revision`, and `files` entries containing `path`,
`bytes`, and `sha256`. Verify the acquisition against the owner's pinned Git/LFS
metadata, then preserve the manifest independently. The probe rehashes every file
and refuses missing or unmanifested files. A user-supplied manifest alone does not
authenticate the publisher.

## Invocation cage

Run in a separate environment and cache; do not replace the project environment.
Retain exact package wheel hashes and installed runtime/build hashes. Python 3.12,
PyTorch 2.9.1, Transformers 4.57.1 and psutil 7.1.3 are the selected development route; a different
build is a different actor. The model is loaded explicitly on CPU in float32 with
eager attention. Its acquired BF16 tensors are cast in memory; original files are
unchanged. This dtype/casting/attention choice belongs to actor identity.

On macOS invoke through the kernel cage:

```sh
sandbox-exec -p '(version 1)(allow default)(deny network*)' \
  /isolated/venv/bin/python -u bench/pinned-candidate/smoke.py \
  --assets /isolated/model --manifest /evidence/model-manifest.json \
  --input /evidence/development-input.json --output /evidence/new-run
```

Use a clean environment: set `OMP_NUM_THREADS`, `MKL_NUM_THREADS`,
`OPENBLAS_NUM_THREADS`, `VECLIB_MAXIMUM_THREADS`, and `NUMEXPR_NUM_THREADS` to `2`;
`OMP_MAX_ACTIVE_LEVELS=1`; `TOKENIZERS_PARALLELISM=false`; `PYTHONNOUSERSITE=1`;
`HF_HUB_OFFLINE=1`; `TRANSFORMERS_OFFLINE=1`; and a new `HOME`/`HF_HOME` inside the
isolated cache. Supply no credentials. The runtime sets intraop threads to 2 and
interop threads to 1. Record actual thread CPU activity rather than inferring
parallelism from idle runtime thread counts.

The probe requires real TCP/UDP IPv4/IPv6 socket calls to fail with kernel `EPERM`
before importing the runtime. Offline flags alone do not pass. `--probe-only`
checks this control without loading a model. Kernel denial persists across imports
and child processes; the probe does not monkeypatch Python sockets.

Predeclare and check available memory/pressure and disk before loading. For this
route the experiment uses a 24 GiB RSS ceiling, at least 26 GiB free plus inactive
and speculative pages before load, and a 5 GiB disk reserve. The caller must run a
foreground supervisor that samples resource use and terminates only its own child
at the RSS bound; the probe itself does not enforce that RSS ceiling.
`supervise.py --output /evidence/observer --rss-cap-mib 24576 --timeout-seconds 900
-- <command...>` supplies this guard. Run it outside the model's network cage and
pass the sandboxed invocation above as its command. It samples total RSS of its
command and descendants before optional CPU/thread observations, refuses a denied
RSS observation, and cleans up its own command if its observer fails. Preserve
supervisor source, command, clean environment, resource samples, exit and
`/usr/bin/time -l` output. Allow one model process only. Its own alarm is 900 seconds;
input is capped at 1,024 tokens and greedy output at 96 new tokens.

The output directory must be new. It contains the exact prompt, rendered chat,
raw generated text (including special tokens), and actor capture with decoding,
chat-template hash, actual dtype/device, package/build identity, token IDs and
artifact hashes. Preserve failures separately; do not overwrite a prior run or
restart an active run because a tool poll timed out.

PyTorch/Transformers supply a portable CPU implementation route. The macOS wheel,
network cage and measured capture identify this local actor only. Linux execution,
existing hosted-runner capacity and semantic quality require their own evidence.

## Focused verification

```sh
python3 -m unittest discover -s bench/pinned-candidate -p 'test_*.py'
python3 -m mypy bench/pinned-candidate/smoke.py \
  bench/pinned-candidate/test_smoke.py --ignore-missing-imports
```

The tests exercise the same admission/invocation seam: hidden reference refusal,
modified weight refusal after a valid snapshot, real sandboxed versus
unsandboxed network controls, and termination of a small controlled child that
crosses the supervisor's RSS cap. They do not load a model or certify its competence.
The macOS kernel control test skips on other platforms; a skip is no Linux proof.

## Separate Linux kernel control

`linux_network.py --control` uses only the standard library and does not fetch or
load a model. Run it in a disposable unprivileged Linux x86_64 or aarch64 process.
It refuses pre-existing sockets/io_uring descriptors, effective capabilities and
runtime threads. It installs `no_new_privs` plus an architecture-checked seccomp
filter denying socket/socketpair creation, io_uring setup and pidfd descriptor
imports. The x86_64 filter also refuses x32 ABI aliases. Unknown platforms refuse.

Eight real socket/syscall controls must return kernel `EPERM`, both immediately
and after executing a fresh Python child. Pipes and ordinary file I/O remain
available. The existing Linux determinism runners execute this tiny control;
the macOS runner does not claim Linux coverage. No schedule, runner, provider or
model job is added. Source review or a Mac skip alone is not Linux execution proof.

Install the filter in the future dedicated runtime child before loading packages;
never install it in the parent supervisor or a shared process. It is irreversible
until that child exits. This is a network control, not general filesystem or
host isolation. It does not replace independent memory, disk, timeout, package,
model/source identity or semantic qualification controls. The old Mac smoke and
its resource bounds remain unchanged; no Linux model feasibility is claimed.

The filter uses the [kernel seccomp interface](https://www.kernel.org/doc/html/next/userspace-api/seccomp_filter.html)
and [no_new_privs](https://www.kernel.org/doc/html/latest/userspace-api/no_new_privs.html),
with constants from the Linux v6.16 [x86 syscall table](https://github.com/torvalds/linux/blob/v6.16/arch/x86/entry/syscalls/syscall_64.tbl)
and [generic syscall definitions](https://github.com/torvalds/linux/blob/v6.16/include/uapi/asm-generic/unistd.h).
