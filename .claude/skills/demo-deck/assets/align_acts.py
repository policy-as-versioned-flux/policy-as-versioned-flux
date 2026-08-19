#!/usr/bin/env python3
"""Force-align each act's audio to its known script text, via MacWhisper
(`mw`) word-level ASR + sequence matching -- not the TTS server's own
/api/tts/align-words endpoint, which was found unreliable (503 on every
call across two independent runs). Whisper's transcript won't always match
the script verbatim (homophones, number formatting), so segment boundaries
are found by aligning token sequences with difflib rather than trusting
exact text equality.

Usage: python3 align_acts.py <deck_dir>

Reads <deck_dir>/narration.json and <deck_dir>/acts.json (written by
gen_acts.py -- run that first). Writes <deck_dir>/segment_timing.json:
{"segments": {"<i>": {"act": N, "local_start": s, "global_start": s}, ...},
 "total_duration": s, "gap": s}
"""
import json, pathlib, subprocess, re, difflib, sys, argparse

GAP = 0.35  # small pause inserted between acts on concat; must match assemble.sh


def norm(w):
    return re.sub(r"[^a-z0-9']", '', w.lower())


def expected_tokens(narr, idxs):
    """(token, segment_i) pairs, splitting hyphenated number-words so they
    line up with how ASR is likely to split them (e.g. 'twenty-one' -> two
    tokens)."""
    toks = []
    by_i = {seg['i']: seg for seg in narr}
    for i in idxs:
        for raw in by_i[i]['narration'].split():
            for piece in raw.split('-'):
                t = norm(piece)
                if t:
                    toks.append((t, i))
    return toks


def dur(path):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nk=1:nw=1', str(path)], capture_output=True, text=True)
    return float(o.stdout.strip())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck_dir')
    args = ap.parse_args()
    here = pathlib.Path(args.deck_dir)

    narr = json.loads((here / 'narration.json').read_text())
    acts = json.loads((here / 'acts.json').read_text())

    all_times = {}
    act_offset = 0.0

    for act_i, idxs in enumerate(acts):
        wav = here / 'audio' / f'act{act_i}.wav'
        json_path = here / f'align_act{act_i}.json'
        if not json_path.exists():
            subprocess.run(['mw', 'transcribe', '--format', 'json', str(wav), '-o', str(json_path), '--overwrite'], check=True, capture_output=True)
        asr = json.loads(json_path.read_text())
        asr_words = []
        for seg in asr['segments']:
            for w in seg['words']:
                t = norm(w['text'])
                if t:
                    asr_words.append((t, w['start']))

        exp = expected_tokens(narr, idxs)
        exp_tokens = [t for t, _ in exp]
        asr_tokens = [t for t, _ in asr_words]

        sm = difflib.SequenceMatcher(None, exp_tokens, asr_tokens, autojunk=False)
        exp_to_asr = {}
        for block in sm.get_matching_blocks():
            for k in range(block.size):
                exp_to_asr[block.a + k] = block.b + k

        first_exp_idx_for_seg = {}
        for exp_idx, (_, seg_i) in enumerate(exp):
            if seg_i not in first_exp_idx_for_seg:
                first_exp_idx_for_seg[seg_i] = exp_idx

        act_duration = dur(wav)
        for seg_i in idxs:
            exp_idx = first_exp_idx_for_seg[seg_i]
            asr_idx = None
            for delta in range(0, 40):
                for cand in (exp_idx + delta, exp_idx - delta):
                    if cand in exp_to_asr:
                        asr_idx = exp_to_asr[cand]
                        break
                if asr_idx is not None:
                    break
            local_start = (asr_words[asr_idx][1] / 1000.0) if (asr_idx is not None and asr_idx < len(asr_words)) else 0.0
            if asr_idx is None:
                print(f'  WARNING: no alignment match for segment {seg_i}, defaulting to act start -- spot-check this slide\'s timing')
            all_times[seg_i] = {'act': act_i, 'local_start': local_start, 'global_start': act_offset + local_start}

        match_rate = len(exp_to_asr) / max(len(exp_tokens), 1)
        print(f'act {act_i}: duration {act_duration:.1f}s, offset {act_offset:.1f}s, matched {match_rate:.0%} of tokens')
        if match_rate < 0.6:
            print(f'  WARNING: low match rate for act {act_i} -- spot-check its slides\' timing before delivering')
        act_offset += act_duration + GAP

    total = act_offset - GAP
    (here / 'segment_timing.json').write_text(json.dumps({'segments': all_times, 'total_duration': total, 'gap': GAP}, indent=2))
    print(f'\nTOTAL: {total:.1f}s -> {int(total // 60)}:{total % 60:04.1f}')
    print('Next: run render.js to screenshot slides, then assemble.sh')


if __name__ == '__main__':
    main()
