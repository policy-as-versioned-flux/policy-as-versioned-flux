#!/usr/bin/env python3
"""Parse the 20 `> ` narration lines from script.md, synthesize each via the local
Qwen3 TTS clone (andy3), save audio/sNN.wav, and report per-clip duration.
Flags any clip > 19.0s (would get truncated in a 20s Pecha Kucha slot)."""
import pathlib, subprocess, sys, requests

HERE = pathlib.Path(__file__).parent
AUD = HERE/"audio"; AUD.mkdir(exist_ok=True)
TTS = "http://localhost:7693"

def narration():
    lines = (HERE/"script.md").read_text().splitlines()
    return [ln[2:].strip() for ln in lines if ln.startswith("> ")]

def synth(text):
    r = requests.post(f"{TTS}/api/qwen3/generate",
                      json={"text": text, "mode": "clone", "voice_name": "andy3"}, timeout=120)
    r.raise_for_status()
    url = r.json()["audio_url"]
    return requests.get(f"{TTS}{url}", timeout=120).content

def dur(p):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                          "-of","default=nk=1:nw=1",str(p)], capture_output=True, text=True)
    try: return float(out.stdout.strip())
    except: return -1.0

def main():
    texts = narration()
    assert len(texts) == 20, f"expected 20 narration lines, got {len(texts)}"
    rows, over = [], []
    for i, t in enumerate(texts, 1):
        wav = AUD/f"s{i:02d}.wav"
        wav.write_bytes(synth(t))
        d = dur(wav); w = len(t.split())
        flag = "  <-- OVER 19s" if d > 19.0 else ("  (tight)" if d > 18.0 else "")
        rows.append(f"s{i:02d}  {w:>3}w  {d:5.1f}s{flag}")
        if d > 19.0: over.append((i, d, w))
        print(rows[-1], flush=True)
    total = sum(dur(AUD/f"s{i:02d}.wav") for i in range(1,21))
    summary = "\n".join(rows) + f"\n\nTOTAL narration audio: {total:.1f}s (video is fixed at 400s / 6:40)\n"
    summary += f"OVER-19s clips (need trimming): {[o[0] for o in over] or 'none'}\n"
    (HERE/"durations.txt").write_text(summary)
    print("\n"+summary)

if __name__ == "__main__":
    main()
