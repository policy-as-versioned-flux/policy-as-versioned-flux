#!/bin/bash
# Assemble 20 slides x 20.0s (audio front-loaded, padded to 20s) into a 6:40 Pecha Kucha video.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p seg
: > concat.txt
for i in $(seq -w 1 20); do
  img="slides/s${i}.png"; wav="audio/s${i}.wav"; out="seg/seg${i}.mp4"
  vf="scale=1920:1080,setsar=1,format=yuv420p"
  # fade in on first slide, fade out on last
  if [ "$i" = "01" ]; then vf="$vf,fade=t=in:st=0:d=0.5"; fi
  if [ "$i" = "20" ]; then vf="$vf,fade=t=out:st=19.2:d=0.8"; fi
  ffmpeg -y -loglevel error -loop 1 -i "$img" -i "$wav" \
    -filter_complex "[1:a]apad,atrim=0:20,asetpts=PTS-STARTPTS[a]" \
    -map 0:v -map "[a]" -t 20 -r 30 \
    -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 "$out"
  echo "file 'seg/seg${i}.mp4'" >> concat.txt
  printf "seg %s ok\n" "$i"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i concat.txt -c copy pitch.mp4
dur=$(ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 pitch.mp4)
printf "\nBUILT pitch.mp4  duration=%.1fs  (target 400s / 6:40)\n" "$dur"
ls -lh pitch.mp4
