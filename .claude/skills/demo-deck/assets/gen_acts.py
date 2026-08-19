#!/usr/bin/env python3
"""Generate continuous-take audio for a narration.json script, chunked into
'acts' safely under the TTS backend's empirically-discovered generation cap.

Usage: python3 gen_acts.py <deck_dir> [--max-act-words 220]

Reads <deck_dir>/narration.json (list of {i, narration, ...}).
Writes <deck_dir>/acts.json (the chunking, so align_acts.py reuses the same
boundaries rather than redefining them) and <deck_dir>/audio/act<N>.wav.

Why chunked, not one giant call: a single request over roughly 550-600 words
was observed to truncate silently and reproducibly (same cutoff on repeat
runs with memory freed in between) -- this is a backend generation-length
cap, not a resource issue. 220 words/act default leaves a large safety
margin under that ceiling while keeping each act long enough that the voice
still flows naturally within it (most of the perceptible "flow" benefit of
one continuous take is within-act; the small gap between acts reads as a
natural paragraph break, not a jump cut).
"""
import json, pathlib, subprocess, sys, time, argparse, requests

TTS = 'http://localhost:7693'
VOICE = 'andy3'  # matches the cloned voice this project's pipeline has used throughout


def synth(text):
    last = None
    for attempt in range(5):
        try:
            r = requests.post(f'{TTS}/api/qwen3/generate', json={'text': text, 'mode': 'clone', 'voice_name': VOICE}, timeout=300)
            r.raise_for_status()
            audio_url = r.json()['audio_url']
            return requests.get(f'{TTS}{audio_url}', timeout=300).content
        except Exception as e:
            last = e
            time.sleep(3 * (attempt + 1))
    raise last


def dur(path):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nk=1:nw=1', str(path)], capture_output=True, text=True)
    return float(o.stdout.strip())


def chunk_into_acts(narr, max_words):
    """Greedily pack consecutive segments into acts, each under max_words."""
    acts, current, current_words = [], [], 0
    for seg in narr:
        w = len(seg['narration'].split())
        if current and current_words + w > max_words:
            acts.append(current)
            current, current_words = [], 0
        current.append(seg['i'])
        current_words += w
    if current:
        acts.append(current)
    return acts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('deck_dir')
    ap.add_argument('--max-act-words', type=int, default=220)
    args = ap.parse_args()

    here = pathlib.Path(args.deck_dir)
    narr = json.loads((here / 'narration.json').read_text())
    by_i = {seg['i']: seg for seg in narr}

    acts = chunk_into_acts(narr, args.max_act_words)
    (here / 'acts.json').write_text(json.dumps(acts, indent=2))
    print(f'{len(narr)} segments -> {len(acts)} acts (max {args.max_act_words} words/act)')

    aud_dir = here / 'audio'
    aud_dir.mkdir(exist_ok=True)
    total = 0.0
    for act_i, idxs in enumerate(acts):
        text = ' '.join(by_i[i]['narration'] for i in idxs)
        wc = len(text.split())
        print(f'act {act_i} (segments {idxs[0]}-{idxs[-1]}): {wc} words')
        audio = synth(text)
        wav = aud_dir / f'act{act_i}.wav'
        wav.write_bytes(audio)
        d = dur(wav)
        total += d
        print(f'  duration: {d:.1f}s ({wc / d:.2f} w/s)')
        time.sleep(0.3)

    print(f'\nTOTAL (sum of acts, before join gaps): {total:.1f}s -> {int(total // 60)}:{total % 60:04.1f}')
    print('Next: python3 align_acts.py', args.deck_dir)


if __name__ == '__main__':
    main()
