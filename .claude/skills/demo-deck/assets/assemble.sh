#!/bin/bash
# Build <deck_dir>/output.mp4 from acts.json audio + segment_timing.json +
# slides/sNN.png -- one continuous audio track, slide changes at the real
# force-aligned per-segment start times.
#
# Usage: ./assemble.sh <deck_dir>
# Requires: gen_acts.py and align_acts.py already run (acts.json,
# segment_timing.json, audio/act*.wav, slides/*.png all present).
set -euo pipefail
DECK="$(cd "$1" && pwd)"
cd "$DECK"

N_ACTS=$(python3 -c "import json; print(len(json.load(open('acts.json'))))")
GAP=$(python3 -c "import json; print(json.load(open('segment_timing.json'))['gap'])")

python3 -c "
import subprocess
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','$GAP','audio/_gap.wav'], check=True)
"

: > /tmp/demo_deck_audio_concat.txt
for i in $(seq 0 $((N_ACTS - 1))); do
  echo "file '${DECK}/audio/act${i}.wav'" >> /tmp/demo_deck_audio_concat.txt
  if [ "$i" -lt $((N_ACTS - 1)) ]; then
    echo "file '${DECK}/audio/_gap.wav'" >> /tmp/demo_deck_audio_concat.txt
  fi
done
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/demo_deck_audio_concat.txt -c:a pcm_s16le -ar 48000 -ac 1 audio/full_continuous.wav
adur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 audio/full_continuous.wav)
echo "continuous audio: ${adur}s"

python3 << PYEOF
import json, pathlib
here = pathlib.Path('$DECK')
timing = json.load(open('segment_timing.json'))
segs = timing['segments']
total = timing['total_duration']
order = sorted(int(k) for k in segs.keys())
lines = []
for idx, i in enumerate(order):
    start = segs[str(i)]['global_start']
    nxt = segs[str(order[idx+1])]['global_start'] if idx+1 < len(order) else total
    d = max(nxt - start, 0.1)
    fname = str(here / 'slides' / f's{i+1:02d}.png')
    lines.append(f"file '{fname}'")
    lines.append(f"duration {d:.3f}")
lines.append(f"file '{lines[-2].split(chr(39))[1]}'")  # concat demuxer needs the last file repeated with no duration
open('/tmp/demo_deck_video_concat.txt', 'w').write('\n'.join(lines) + '\n')
print('video concat list written,', len(order), 'slides')
PYEOF

ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/demo_deck_video_concat.txt -vf "scale=1920:1080,setsar=1,format=yuv420p,fps=30" video_only.mp4
vdur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 video_only.mp4)
echo "video-only stream: ${vdur}s"

ffmpeg -y -loglevel error -i video_only.mp4 -i audio/full_continuous.wav -map 0:v -map 1:a \
  -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest output.mp4

fdur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 output.mp4)
awk -v d="$fdur" 'BEGIN{printf "BUILT output.mp4  %.1fs (%d:%05.2f)\n",d,int(d/60),d-60*int(d/60)}'
ls -lh output.mp4 | awk '{print $5}'
