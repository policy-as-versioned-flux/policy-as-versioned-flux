import json, pathlib, subprocess, requests, time

HERE = pathlib.Path(__file__).parent
TTS = 'http://localhost:7693'
AUD = HERE / 'audio'; AUD.mkdir(exist_ok=True)
narr = json.loads((HERE / 'narration.json').read_text())

# Group segment indices into acts, each well under the ~560-word cap.
ACTS = [
    list(range(0, 3)),    # 0-2
    list(range(3, 6)),    # 3-5
    list(range(6, 9)),    # 6-8
    list(range(9, 11)),   # 9,10   calibration + reflexive
    list(range(11, 13)),  # 11,12  AI-OS thesis + senses
    list(range(13, 15)),  # 13,14  reasons + knows-when-to-shut-up
    list(range(15, 17)),  # 15,16  never-acts-alone + the headline
    list(range(17, 19)),  # 17,18  maps it + refuses to panic
    list(range(19, 21)),  # 19,20  the paper + the money moves
    list(range(21, 23)),  # 21,22  provenance + honest red
    list(range(23, 25)),  # 23,24  scale + why now
    list(range(25, 28)),  # 25,26,27  vision + what's left + close
]

def synth(text):
    last = None
    for attempt in range(5):
        try:
            r = requests.post(f'{TTS}/api/qwen3/generate', json={'text': text, 'mode': 'clone', 'voice_name': 'andy3'}, timeout=300)
            r.raise_for_status()
            audio_url = r.json()['audio_url']
            audio = requests.get(f'{TTS}{audio_url}', timeout=300).content
            return audio, audio_url
        except Exception as e:
            last = e; time.sleep(3 * (attempt + 1))
    raise last

def align(text, audio_url):
    last = None
    for attempt in range(5):
        try:
            a = requests.post(f'{TTS}/api/tts/align-words', json={'text': text, 'audio_url': audio_url, 'language': 'en'}, timeout=300)
            a.raise_for_status()
            return a.json()
        except Exception as e:
            last = e; time.sleep(4 * (attempt + 1))
    print(f'  ALIGNMENT FAILED after retries: {last}')
    return None

def dur(p):
    o = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nk=1:nw=1', str(p)], capture_output=True, text=True)
    return float(o.stdout.strip())

results = []
for act_i, idxs in enumerate(ACTS):
    text = ' '.join(narr[i]['narration'] for i in idxs)
    wc = len(text.split())
    print(f'act {act_i} (segments {idxs[0]}-{idxs[-1]}): {wc} words', flush=True)
    audio, audio_url = synth(text)
    wav = AUD / f'act{act_i}.wav'
    wav.write_bytes(audio)
    d = dur(wav)
    print(f'  duration: {d:.1f}s ({wc/d:.2f} w/s)', flush=True)
    results.append({'act': act_i, 'segments': idxs, 'words': wc, 'duration': d})
    time.sleep(0.5)

(HERE / 'acts_summary.json').write_text(json.dumps(results, indent=2))
total = sum(r['duration'] for r in results)
print(f'\nTOTAL (sum of acts, before any join padding): {total:.1f}s -> {int(total//60)}:{total%60:04.1f}')
