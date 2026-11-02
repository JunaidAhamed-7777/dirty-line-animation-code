#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AUDIO="${1:-$ROOT/DIRTY_LINE_RECORDED_TEMP.wav}"
# Temporary audio remains explicitly labelled until listening/model-source review.
# Watermark is composited AFTER the fade, so it remains visible throughout.
ffmpeg -y -framerate 24 -start_number 1 -i "$ROOT/renders/frame_%04d.png" -i "$AUDIO" \
-vf "fade=t=in:st=0:d=0.12,fade=t=out:st=19.6:d=0.4,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Made By Junaid':fontsize=h*0.027:fontcolor=white@0.85:shadowcolor=black@0.8:shadowx=1:shadowy=1:x=w-tw-w*0.025:y=h-th-h*0.035,drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:text='DIRTY LINE':fontsize=h*0.065:fontcolor=white:x=(w-tw)/2:y=h*0.40:enable='gte(t,18.8)'" \
-c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t 20 "$ROOT/DIRTY_LINE.mp4"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels -of json "$ROOT/DIRTY_LINE.mp4" > "$ROOT/final_validation.json"
