#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p seg; : > concat.txt
TRIM="silenceremove=start_periods=1:start_duration=0.03:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_duration=0.03:start_threshold=-50dB,areverse,apad=pad_dur=0.4"
for f in $(ls slides/s*.png | sort); do
  i=$(basename "$f" .png | sed 's/^s//')
  raw="audio/s${i}.wav"; tw="audio/tight-s${i}.wav"; out="seg/seg${i}.mp4"
  [ -f "$raw" ] || { echo "!! missing $raw — skipping"; continue; }
  ffmpeg -y -loglevel error -i "$raw" -af "$TRIM" "$tw"
  d=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$tw")
  ffmpeg -y -loglevel error -loop 1 -i "$f" -i "$tw" -map 0:v -map 1:a -t "$d" \
    -vf "scale=1920:1080,setsar=1,format=yuv420p" -r 30 -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p -c:a aac -b:a 192k -ar 48000 "$out"
  echo "file 'seg/seg${i}.mp4'" >> concat.txt
done
ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt -c copy demo-video.mp4
dur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 demo-video.mp4)
awk -v d="$dur" 'BEGIN{printf "BUILT demo-video.mp4  %.0fs (%d:%02d)\n",d,int(d/60),d%60}'
ls -lh demo-video.mp4 | awk '{print $5}'
