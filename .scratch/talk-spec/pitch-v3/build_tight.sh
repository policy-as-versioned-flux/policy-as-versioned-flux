#!/bin/bash
# Retimed build: each slide lasts its (silence-trimmed) narration + 0.35s breath — no fixed 20s pad.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p seg audio_tight
: > concat_tight.txt
TRIM="silenceremove=start_periods=1:start_duration=0.03:start_threshold=-50dB,areverse,silenceremove=start_periods=1:start_duration=0.03:start_threshold=-50dB,areverse,apad=pad_dur=0.35"
for i in $(seq -w 1 20); do
  img="slides/s${i}.png"; raw="audio/s${i}.wav"; tw="audio_tight/s${i}.wav"; out="seg/seg${i}.mp4"
  ffmpeg -y -loglevel error -i "$raw" -af "$TRIM" "$tw"
  d=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$tw")
  raw_d=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 "$raw")
  vf="scale=1920:1080,setsar=1,format=yuv420p"
  if [ "$i" = "01" ]; then vf="$vf,fade=t=in:st=0:d=0.4"; fi
  if [ "$i" = "20" ]; then fo=$(awk -v d="$d" 'BEGIN{printf "%.2f", (d-0.7>0? d-0.7:0)}'); vf="$vf,fade=t=out:st=$fo:d=0.7"; fi
  ffmpeg -y -loglevel error -loop 1 -i "$img" -i "$tw" \
    -map 0:v -map 1:a -t "$d" -vf "$vf" -r 30 \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 "$out"
  echo "file 'seg/seg${i}.mp4'" >> concat_tight.txt
  printf "seg %s  raw %5.1fs -> tight %5.1fs\n" "$i" "$raw_d" "$d"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i concat_tight.txt -c copy pitch_tight.mp4
dur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 pitch_tight.mp4)
awk -v d="$dur" 'BEGIN{printf "\nBUILT pitch_tight.mp4  duration=%.1fs  (%d:%02d)\n", d, int(d/60), d%60}'
ls -lh pitch_tight.mp4 | awk '{print $5}'
