import json, pathlib, subprocess, time, requests
HERE=pathlib.Path(__file__).parent
AUD=HERE/'audio'; AUD.mkdir(exist_ok=True)
TTS='http://localhost:7693'
narr=json.loads((HERE/'narration.json').read_text())
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
for i,seg in enumerate(narr,1):
    wav=AUD/f's{i:02d}.wav'; wav.write_bytes(synth(seg['narration']))
    print(f"s{i:02d} {len(seg['narration'].split()):>3}w {dur(wav):5.1f}s",flush=True)
    time.sleep(0.4)
print('AUDIO DONE:',len(narr),'clips, total',round(sum(dur(AUD/f's{i:02d}.wav') for i in range(1,len(narr)+1)),1),'s')
