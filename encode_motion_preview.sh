#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
ffmpeg -y -hide_banner -loglevel warning -framerate 24 -start_number 1 -i "$ROOT/motion_preview_frames/%04d.png" -i "$ROOT/audio_work/DIRTY_LINE_V2_FINAL_AUDIO_RECOVERED.wav" -i "$ROOT/title_work/DIRTY_LINE_title_alpha_1920.mov" -filter_complex "[2:v]scale=480:270,fps=24,settb=1/24,setpts=N+494[title];[0:v][title]overlay=0:0:eof_action=pass:repeatlast=0[bg];[bg]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Made By Junaid':fontsize=8:fontcolor=white@0.85:shadowcolor=black:shadowx=1:shadowy=1:x=w-tw-12:y=h-th-10[v]" -map '[v]' -map 1:a -c:v libx264 -preset fast -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -t 22.333333 -movflags +faststart "$ROOT/DIRTY_LINE_V2_RECOVERY_MOTION_PREVIEW.mp4"
ffmpeg -v error -i "$ROOT/DIRTY_LINE_V2_RECOVERY_MOTION_PREVIEW.mp4" -f null -
