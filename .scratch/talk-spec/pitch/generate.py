#!/usr/bin/env python3
"""Pitch audio generator + length harness.
Narration is the source of truth here. TTS is non-deterministic in length, so:
  python generate.py all           # generate audio/s01..s20.wav once
  python generate.py measure       # measure existing wavs
  python generate.py reps N i ...   # regen slides i.. N times, report min/mean/max
Target: audio 17.5-19.3s per slide (each video slide is a fixed 20.0s).
"""
import subprocess, sys, os, statistics, pathlib

HERE = pathlib.Path(__file__).parent
TTS = HERE / ".." / ".." / ".." / "tts.py"
AUDIO = HERE / "audio"; AUDIO.mkdir(exist_ok=True)

# 20 slides. Keep TTS-clean: words not symbols, commas for pauses, no em-dash.
LINES = {
 1: "What does a breach actually cost you? Not a red, amber, green dot on a dashboard, and not a compliance checkbox either. An actual number, in pounds. Because that one honest number is the only real place to start every security decision that you, and your board, will ever make.",
 2: "Here's the uncomfortable truth. Most governance today is theatre. Compliant, or not compliant. A single green tick that means nothing really moved, nobody priced the risk, and nobody can tell you what changed when the world did. It is, quite simply, a binary lie.",
 3: "So here is the idea I want to build. Governance is not a checkbox. It is a proportionate, informed, continuously re-tuned response to quantified risk. Version that entire chain, from appetite to evidence, and proportionality stays honest and current as the world keeps moving.",
 4: "Start with a reframe your engineers already trust. A policy is just a dependency. A lint pack. You pin it, you sign it, you adopt it by pull request. Suddenly, governance becomes something every developer in the building already knows exactly how to consume.",
 5: "The shape of it is an hourglass. Risk appetite, in pounds, sets the tone at the very top. It funnels down through principles, controls, and one single enforcement decision. Then evidence flows back up into one defensible number. Versioned, top to bottom, end to end.",
 6: "Now the moment that makes the whole thesis land. Two institutions. A retailer, and a hospital. Same shared platform, same rule, the same engine underneath. One control: encrypt the data at rest. Watch carefully what proportionality actually does to that identical rule.",
 7: "In the retailer, that control merely audits. In the hospital, the very same control blocks the deployment. Why? Because a health breach costs roughly eight times a retail one. Same rule, opposite verdict, purely because the pounds say so. That is proportionality you can see.",
 8: "Those pounds are real. A lightweight actuarial engine takes calibrated estimates, runs a Monte Carlo simulation, and returns your expected loss and the tail, the genuinely bad year your board actually lies awake fearing. This is the insurance industry's own maths, not a vibe.",
 9: "Best of all, this number is not static, it moves in real time. Tighten a control, and the pounds fall. Accept a risky condition, and they quietly rise. A new threat lands, and they jump. Two runs, one single input changed, and you watch the true cost of a decision, live on screen.",
 10: "Next, we kill the ugliest word in all of governance: exemption. No carve-outs, no special favours. Instead: you may do this, if you meet these conditions. Uniform, versioned, and priced. Every single allowance now carries its own honest, visible line of accepted risk.",
 11: "Failures move left, where they belong. The cluster advertises which policy versions it supports. Your pipeline runs the very same check the cluster will, offline, before you ever merge. A deploy-time surprise becomes almost unheard of, and the compliant path becomes the easy one.",
 12: "Then the whole estate comes alive. It war-games itself. Threat feeds, fresh vulnerabilities, end-of-life dates, regulator penalties, and market intelligence all pour in. An agent continuously stress-tests your controls and asks one question: is this still proportionate, or has the world quietly moved again?",
 13: "When it drifts, the agent does exactly one thing. It opens a pull request. It proposes, it never disposes. A human reviews, the gate checks, and only then does it ship. The scary capability is safe precisely because it rides the same rails you already trust.",
 14: "Every actor, human or machine, signs their own work. Cryptographically signed, publicly logged, verifiable from end to end. You can prove which actor proposed what, when, and from exactly what evidence. For an A.I.-enabled organisation, that is precisely how you learn to trust the machine.",
 15: "None of this is slideware. Six real organisations. A shared platform, three live institutions, two regulators publishing real controls and real fines as code. A separate cluster for each. The heart of this talk runs live, on real clusters, not faked in a diagram.",
 16: "Which lets us close exactly where no security talk ever closes: on the balance sheet. Residual risk becomes economic capital. An underwriter would price the very same controls we enforce. Technological risk finally becomes a single line your board can read, defend, and actually act upon.",
 17: "Here is precisely why this is ours to build. Flux is not a logo on a slide. It is genuinely load-bearing, doing six real jobs: distribution, provenance, pruning, healing, ordering, and events. This work puts Flux at the dead centre of the entire risk-governance story.",
 18: "So what do you actually get for the spend? A flagship conference talk that tours the circuit. A reusable demonstration estate our teams can put in front of literally any prospect. And clear ownership of a narrative that nobody else in this entire market is telling yet.",
 19: "So here is my commitment to you. Nothing is a nice-to-have. Six organisations, built fresh, fully live. The risk engine, the living loop, the provenance, the balance sheet. All of it real, all of it versioned, nothing faked, nothing hinted. I build the whole thing.",
 20: "So here is the ask. Fund it. End to end, all the way through to the flagship talk. Give me the runway, and I will hand you the estate that proves governance can finally be proportionate, honest, and alive. Let's put technological risk on the balance sheet.",
}

def wav_dur(p):
    out = subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
                          "-of","default=nk=1:nw=1",str(p)],capture_output=True,text=True)
    try: return float(out.stdout.strip())
    except: return 0.0

def gen(i, out=None):
    out = out or AUDIO / f"s{i:02d}.wav"
    r = subprocess.run(["python3",str(TTS)],input=LINES[i].encode(),
                       stdout=open(out,"wb"),stderr=subprocess.DEVNULL,timeout=180)
    return out

def flag(d):
    return "  <-- LONG" if d>19.4 else ("  <-- short" if d<16.8 else "")

def reroll(i, lo=17.0, hi=19.2, K=5, cap=19.35):
    """Keep sNN.wav if already in-window; else re-roll up to K, keep best (<=cap, closest to centre)."""
    import shutil
    final = AUDIO/f"s{i:02d}.wav"; tmp = AUDIO/f"_try{i:02d}.wav"; ctr=(lo+hi)/2
    if final.exists() and lo<=wav_dur(final)<=hi:
        return wav_dur(final), 0
    best=None; bestscore=1e9
    for k in range(K):
        gen(i, out=tmp); d=wav_dur(tmp)
        if lo<=d<=hi:
            shutil.copy(tmp, final); tmp.unlink(missing_ok=True); return d, k+1
        if d<=cap:
            s=abs(d-ctr)
            if s<bestscore: bestscore=s; best=d; shutil.copy(tmp, final)
    tmp.unlink(missing_ok=True)
    return (best if best is not None else wav_dur(final)), K

if __name__=="__main__":
    cmd = sys.argv[1] if len(sys.argv)>1 else "all"
    if cmd=="fix":
        lo=float(sys.argv[2]) if len(sys.argv)>2 else 17.0
        hi=float(sys.argv[3]) if len(sys.argv)>3 else 19.2
        tot=0
        for i in sorted(LINES):
            d,n=reroll(i,lo,hi); tot+=d
            print(f"s{i:02d}: {d:5.2f}s  ({n} re-rolls){flag(d)}",flush=True)
        print(f"TOTAL audio {tot:.1f}s")
        sys.exit(0)
    if cmd=="measure":
        tot=0
        for i in sorted(LINES):
            p=AUDIO/f"s{i:02d}.wav"; d=wav_dur(p) if p.exists() else 0; tot+=d
            print(f"s{i:02d}: {len(LINES[i].split()):2d}w  {d:5.2f}s{flag(d)}")
        print(f"TOTAL audio {tot:.1f}s  (video = 20x20 = 400s)")
    elif cmd=="reps":
        N=int(sys.argv[2]); ids=[int(x) for x in sys.argv[3:]] or sorted(LINES)
        for i in ids:
            ds=[wav_dur(gen(i, AUDIO/f"_rep{i}_{k}.wav")) for k in range(N)]
            print(f"s{i:02d}: {len(LINES[i].split())}w  n={N}  min {min(ds):.2f}  mean {statistics.mean(ds):.2f}  max {max(ds):.2f}")
    else:
        tot=0
        for i in sorted(LINES):
            d=wav_dur(gen(i)); tot+=d
            print(f"s{i:02d}: {len(LINES[i].split()):2d}w  {d:5.2f}s{flag(d)}",flush=True)
        print(f"TOTAL audio {tot:.1f}s")
