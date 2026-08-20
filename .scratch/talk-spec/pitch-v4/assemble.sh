#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

GAP=0.35
python3 -c "
import subprocess
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','lavfi','-i','anullsrc=r=48000:cl=mono','-t','$GAP','audio/_gap.wav'], check=True)
"

HERE="$(pwd)"
# concat all 10 acts with a small gap between, into one continuous track
: > /tmp/audio_concat.txt
for i in $(seq 0 11); do
  echo "file '${HERE}/audio/act${i}.wav'" >> /tmp/audio_concat.txt
  if [ "$i" -lt 11 ]; then
    echo "file '${HERE}/audio/_gap.wav'" >> /tmp/audio_concat.txt
  fi
done
ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/audio_concat.txt -c:a pcm_s16le -ar 48000 -ac 1 audio/full_continuous.wav
dur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 audio/full_continuous.wav)
echo "continuous audio: ${dur}s"

# build the video-only stream: each slide image held for its real duration
python3 << 'PYEOF'
import json, pathlib
here = pathlib.Path('.').resolve()
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
lines.append(f"file '{lines[-2].split(chr(39))[1]}'")  # repeat last image per concat demuxer requirement
open('/tmp/video_concat.txt', 'w').write('\n'.join(lines) + '\n')
print('video concat list written,', len(order), 'slides')
PYEOF

ffmpeg -y -loglevel error -f concat -safe 0 -i /tmp/video_concat.txt -vf "scale=1920:1080,setsar=1,format=yuv420p,fps=30" video_only.mp4
vdur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 video_only.mp4)
echo "video-only stream: ${vdur}s"

ffmpeg -y -loglevel error -i video_only.mp4 -i audio/full_continuous.wav -map 0:v -map 1:a -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 -shortest pitch-v5.mp4

fdur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 pitch-v5.mp4)
awk -v d="$fdur" 'BEGIN{printf "BUILT pitch-v5.mp4  %.1fs (%d:%05.2f)\n",d,int(d/60),d-60*int(d/60)}'
ls -lh pitch-v5.mp4 | awk '{print $5}'
