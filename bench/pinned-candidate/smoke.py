"""Development feasibility only; never evaluates or records a model permission."""
from __future__ import annotations

import json

MODEL = 'Qwen/Qwen3-4B-Instruct-2507'
REVISION = 'cdbee75f17c01a7cc42f958dc650907174af0554'

def make_prompt(value: dict) -> str:
    """Accept only the existing signal input projection, never the corpus row."""
    if set(value) != {'statement', 'source', 'candidates'}:
        raise ValueError('input-only signal projection required')
    if not all(isinstance(value[k], str) for k in ('statement', 'source')):
        raise ValueError('statement and source must be text')
    if not isinstance(value['candidates'], list) or not value['candidates']:
        raise ValueError('nonempty candidates required')
    for candidate in value['candidates']:
        if not isinstance(candidate, dict) or set(candidate) != {'id', 'name'}:
            raise ValueError('input-only candidate id/name required')
        if not all(isinstance(v, str) for v in candidate.values()):
            raise ValueError('candidate id/name must be text')
    return ('Classify this headline as social, technological, economic, environmental or political; '
            'choose the directly affected component from the candidates. '
            'Return a JSON object with steep, component (candidate id), and basis '
            '(brief reasoning grounded in the supplied statement).\nINPUT:\n' +
            json.dumps(value, ensure_ascii=False, sort_keys=True))

def verify_assets(root, manifest: dict) -> None:
    """Rehash the exact local snapshot before importing a model runtime."""
    import hashlib
    if manifest['model_id'] != MODEL or manifest['revision'] != REVISION:
        raise ValueError('foreign model revision')
    names = {item['path'] for item in manifest['files']}
    required = {'LICENSE', 'config.json', 'generation_config.json',
                'model.safetensors.index.json', 'tokenizer.json', 'tokenizer_config.json',
                'merges.txt', 'vocab.json',
                *(f'model-{i:05d}-of-00003.safetensors' for i in (1, 2, 3))}
    if not required <= names or names != {p.name for p in root.iterdir()}:
        raise ValueError('asset integrity: incomplete snapshot or unmanifested files')
    for item in manifest['files']:
        path = root / item['path']
        if path.is_symlink() or path.parent != root or not path.is_file():
            raise ValueError('asset integrity: local regular files required')
        digest = hashlib.sha256()
        with path.open('rb') as stream:
            while block := stream.read(4 * 1024 * 1024):
                digest.update(block)
        if path.stat().st_size != item['bytes'] or digest.hexdigest() != item['sha256']:
            raise ValueError(f'asset integrity: {item["path"]}')

def prove_network_denied() -> list[dict]:
    """Require kernel EPERM for real TCP/UDP IPv4/IPv6 calls, not a Python patch."""
    import errno
    import socket
    observations = []
    for family, address in ((socket.AF_INET, ('127.0.0.1', 9)),
                            (socket.AF_INET6, ('::1', 9))):
        for kind in (socket.SOCK_STREAM, socket.SOCK_DGRAM):
            with socket.socket(family, kind) as sock:
                sock.settimeout(1)
                try:
                    sock.connect(address)
                except OSError as exc:
                    if exc.errno != errno.EPERM:
                        raise RuntimeError('kernel network denial unproved') from exc
                    observations.append({'family': family.name, 'kind': kind.name,
                                         'result': 'EPERM', 'errno': exc.errno})
                else:
                    raise RuntimeError('network is available; refusing model import')
    return observations


def main() -> None:
    import argparse
    import hashlib
    import importlib.metadata
    import os
    from pathlib import Path
    import platform
    import signal
    import sys
    import time

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--probe-only', action='store_true')
    parser.add_argument('--assets', type=Path)
    parser.add_argument('--manifest', type=Path)
    parser.add_argument('--input', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    network = prove_network_denied()
    print(json.dumps({'network_probe': network}), flush=True)
    if args.probe_only:
        return
    if not all((args.assets, args.manifest, args.input, args.output)):
        parser.error('assets, manifest, input and output required')
    signal.alarm(900)
    args.output.mkdir(exist_ok=False)
    started = time.monotonic()
    verify_assets(args.assets, json.loads(args.manifest.read_text()))
    prompt = make_prompt(json.loads(args.input.read_text()))
    (args.output / 'prompt.txt').write_text(prompt)
    for key in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
                'VECLIB_MAXIMUM_THREADS', 'NUMEXPR_NUM_THREADS'):
        if os.environ.get(key) != '2':
            raise RuntimeError(f'{key} must be explicitly 2')
    if os.environ.get('TOKENIZERS_PARALLELISM') != 'false':
        raise RuntimeError('parallel tokenization forbidden')

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    torch.manual_seed(0)
    tokenizer = AutoTokenizer.from_pretrained(args.assets, local_files_only=True,
                                               trust_remote_code=False)
    text = tokenizer.apply_chat_template([{'role': 'user', 'content': prompt}],
                                         tokenize=False, add_generation_prompt=True)
    (args.output / 'rendered-chat.txt').write_text(text)
    encoded = tokenizer(text, return_tensors='pt', add_special_tokens=False)
    count = encoded['input_ids'].shape[-1]
    if count > 1024:
        raise ValueError('input exceeds predeclared 1024 token bound')
    print(json.dumps({'stage': 'load', 'input_tokens': count, 'pid': os.getpid()}), flush=True)
    with torch.device('cpu'):
        model = AutoModelForCausalLM.from_pretrained(
            args.assets, local_files_only=True, trust_remote_code=False,
            use_safetensors=True, torch_dtype=torch.float32, device_map=None,
            low_cpu_mem_usage=True, attn_implementation='eager')
    model.eval()
    dtypes = sorted({str(p.dtype) for p in model.parameters()})
    devices = sorted({str(p.device) for p in model.parameters()})
    if dtypes != ['torch.float32'] or devices != ['cpu']:
        raise RuntimeError('actual actor is not explicit CPU float32')
    loaded = time.monotonic()
    print(json.dumps({'stage': 'generate', 'load_seconds': loaded-started,
                      'dtypes': dtypes, 'devices': devices}), flush=True)
    with torch.inference_mode():
        ids = model.generate(**encoded, max_new_tokens=96, do_sample=False,
                             num_beams=1, use_cache=True)
    generated = ids[0, count:].tolist()
    raw = tokenizer.decode(generated, skip_special_tokens=False)
    (args.output / 'raw-output.txt').write_text(raw)
    actor = {
        'purpose': 'development feasibility only; no qualification or permission',
        'model': MODEL, 'revision': REVISION, 'os': platform.platform(),
        'machine': platform.machine(), 'python': sys.version,
        'python_executable_sha256': hashlib.sha256(Path(sys.executable).read_bytes()).hexdigest(),
        'packages': {name: importlib.metadata.version(name) for name in
                     ('torch', 'transformers', 'tokenizers', 'safetensors', 'numpy')},
        'torch_git_version': torch.version.git_version,
        'torch_build': torch.__config__.show(), 'dtypes': dtypes, 'devices': devices,
        'threads': torch.get_num_threads(), 'interop_threads': torch.get_num_interop_threads(),
        'attention': 'eager', 'max_input_tokens': 1024, 'max_new_tokens': 96,
        'timeout_seconds': 900, 'do_sample': False, 'num_beams': 1, 'seed': 0,
        'input_tokens': count, 'output_tokens': len(generated), 'output_token_ids': generated,
        'input_sha256': hashlib.sha256(args.input.read_bytes()).hexdigest(),
        'manifest_sha256': hashlib.sha256(args.manifest.read_bytes()).hexdigest(),
        'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'chat_template_sha256': hashlib.sha256(tokenizer.chat_template.encode()).hexdigest(),
        'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
        'rendered_chat_sha256': hashlib.sha256(text.encode()).hexdigest(),
        'raw_output_sha256': hashlib.sha256(raw.encode()).hexdigest(),
        'network_control': 'inherited macOS sandbox-exec deny network*; no monkeypatch',
        'network_probe': network, 'load_seconds': loaded-started,
        'generate_seconds': time.monotonic()-loaded, 'wall_seconds': time.monotonic()-started,
    }
    (args.output / 'actor.json').write_text(json.dumps(actor, indent=2)+'\n')
    print(json.dumps({'stage': 'complete', 'output_tokens': len(generated),
                      'wall_seconds': actor['wall_seconds']}), flush=True)

if __name__ == '__main__':
    main()
