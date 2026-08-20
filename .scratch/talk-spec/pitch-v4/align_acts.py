import json, pathlib, subprocess, re, difflib

HERE = pathlib.Path(__file__).parent
narr = json.loads((HERE / 'narration.json').read_text())

ACTS = [
    list(range(0, 3)), list(range(3, 6)), list(range(6, 9)), list(range(9, 11)),
    list(range(11, 13)), list(range(13, 15)), list(range(15, 17)), list(range(17, 19)),
    list(range(19, 21)), list(range(21, 23)), list(range(23, 25)), list(range(25, 28)),
]

def norm(w):
    w = w.lower()
    w = re.sub(r"[^a-z0-9']", '', w)
    return w

def expected_tokens(idxs):
    # (token, segment_i) pairs, splitting hyphenated number-words so they
    # line up with how ASR will likely split them.
    toks = []
    for i in idxs:
        text = narr[i]['narration']
        for raw in text.split():
            for piece in raw.split('-'):
                t = norm(piece)
                if t:
                    toks.append((t, i))
    return toks

def dur(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nk=1:nw=1', str(p)], capture_output=True, text=True)
    return float(o.stdout.strip())

all_segment_times = {}  # i -> {'start': global_s, 'act': act_i}
act_offset = 0.0
GAP = 0.35  # small pause inserted between acts on concat

for act_i, idxs in enumerate(ACTS):
    wav = HERE / 'audio' / f'act{act_i}.wav'
    json_path = HERE / f'align_act{act_i}.json'
    if not json_path.exists():
        subprocess.run(['mw', 'transcribe', '--format', 'json', str(wav), '-o', str(json_path), '--overwrite'], check=True, capture_output=True)
    asr = json.loads(json_path.read_text())
    asr_words = []  # (norm_text, start_ms)
    for seg in asr['segments']:
        for w in seg['words']:
            t = norm(w['text'])
            if t:
                asr_words.append((t, w['start']))

    exp = expected_tokens(idxs)
    exp_tokens = [t for t, _ in exp]
    asr_tokens = [t for t, _ in asr_words]

    sm = difflib.SequenceMatcher(None, exp_tokens, asr_tokens, autojunk=False)
    # map exp index -> asr index (best-effort, from matching blocks)
    exp_to_asr = {}
    for block in sm.get_matching_blocks():
        for k in range(block.size):
            exp_to_asr[block.a + k] = block.b + k

    # for each segment, find first exp-token index, resolve to an asr time
    seen_segs = []
    for i in idxs:
        seen_segs.append(i)
    first_exp_idx_for_seg = {}
    for exp_idx, (_, seg_i) in enumerate(exp):
        if seg_i not in first_exp_idx_for_seg:
            first_exp_idx_for_seg[seg_i] = exp_idx

    act_duration = dur(wav)
    for seg_i in idxs:
        exp_idx = first_exp_idx_for_seg[seg_i]
        # search outward for a matched token if this exact one wasn't matched
        asr_idx = None
        for delta in range(0, 40):
            for cand in (exp_idx + delta, exp_idx - delta):
                if cand in exp_to_asr:
                    asr_idx = exp_to_asr[cand]
                    break
            if asr_idx is not None:
                break
        if asr_idx is not None and asr_idx < len(asr_words):
            local_start = asr_words[asr_idx][1] / 1000.0
        else:
            local_start = 0.0  # fallback: start of act
            print(f'  WARNING: no alignment match for segment {seg_i}, defaulting to act start')
        all_segment_times[seg_i] = {'act': act_i, 'local_start': local_start, 'global_start': act_offset + local_start}

    print(f'act {act_i}: duration {act_duration:.1f}s, offset {act_offset:.1f}s, matched {len(exp_to_asr)}/{len(exp_tokens)} tokens')
    act_offset += act_duration + GAP

total = act_offset - GAP
(HERE / 'segment_timing.json').write_text(json.dumps({'segments': all_segment_times, 'total_duration': total, 'gap': GAP}, indent=2))
print(f'\nTOTAL: {total:.1f}s -> {int(total//60)}:{total%60:04.1f}')
for i in sorted(all_segment_times):
    print(f"i={i:2d} act={all_segment_times[i]['act']} global_start={all_segment_times[i]['global_start']:6.1f}s")
