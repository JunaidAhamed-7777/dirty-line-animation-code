#!/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
AUDIO="${1:-$ROOT/audio_work/DIRTY_LINE_V2_FINAL_AUDIO_RECOVERED.wav}"
# Actual 24fps frame quantization:536frames=22.333s; V2 contains engine and SFX only.
# The stylized title has its own animated tread masks and alpha fade.
ffmpeg -y -framerate 24 -start_number 1 -i "$ROOT/renders/frame_%04d.png" -i "$AUDIO" -i "$ROOT/title_work/DIRTY_LINE_title_alpha_1920.mov" \
-filter_complex "[0:v]fade=t=in:st=0:d=0.12,fade=t=out:st=21.95:d=0.383[bg];[2:v]fps=24,settb=1/24,setpts=N+494[title];[bg][title]overlay=0:0:eof_action=pass:repeatlast=0:shortest=0[composite];[composite]drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:text='Made By Junaid':fontsize=h*0.027:fontcolor=white@0.85:shadowcolor=black@0.8:shadowx=1:shadowy=1:x=w-tw-w*0.025:y=h-th-h*0.035[v];[1:a]apad=whole_dur=22.333333[a]" \
-map '[v]' -map '[a]' -c:v libx264 -preset slow -crf 17 -pix_fmt yuv420p -c:a aac -b:a 256k -ar 48000 -movflags +faststart -t 22.333333 "$ROOT/DIRTY_LINE_V2.mp4"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,nb_frames,sample_rate,channels -of json "$ROOT/DIRTY_LINE_V2.mp4" > "$ROOT/final_validation.json"
