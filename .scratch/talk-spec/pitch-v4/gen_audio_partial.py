import json, pathlib, subprocess, time, requests, sys
HERE=pathlib.Path(__file__).parent
AUD=HERE/'audio'; AUD.mkdir(exist_ok=True)
TTS='http://localhost:7693'
narr=json.loads((HERE/'narration.json').read_text())
targets=set(int(x) for x in sys.argv[1:])
def synth(t):
    last=None
    for attempt in range(5):
        try:
            r=requests.post(f'{TTS}/api/qwen3/generate',json={'text':t,'mode':'clone','voice_name':'andy3'},timeout=240)
            r.raise_for_status()
            return requests.get(f"{TTS}{r.json()['audio_url']}",timeout=240).content
        except Exception as e:
            last=e; time.sleep(3*(attempt+1))
    raise last
def dur(p):
    o=subprocess.run(['ffprobe','-v','error','-show_entries','format=duration','-of','default=nk=1:nw=1',str(p)],capture_output=True,text=True)
    try:return float(o.stdout.strip())
    except:return -1.0
for seg in narr:
    i=seg['i']
    if i not in targets: continue
    wav=AUD/f's{i:02d}.wav'; wav.write_bytes(synth(seg['narration']))
    d=dur(wav)
    print(f"s{i:02d} {len(seg['narration'].split()):>3}w {d:5.1f}s",flush=True)
    time.sleep(0.3)
total=sum(dur(AUD/f's{seg["i"]:02d}.wav') for seg in narr)
print('AUDIO TOTAL (all 18):', round(total,1),'s ->',f'{int(total//60)}:{total%60:04.1f}')
