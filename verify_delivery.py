"""Post-render technical verification; run after finish_video.sh."""
from pathlib import Path
import hashlib,json,subprocess
from PIL import Image,ImageStat,ImageDraw
R=Path(__file__).resolve().parent
checks=[]
for n in range(1,537):
 p=R/'renders'/f'frame_{n:04d}.png'
 with Image.open(p) as im:
  im.load();assert im.size==(1920,1080),(n,im.size)
  extrema=im.convert('L').getextrema();assert extrema[1]>20,(n,'unexpected black image')
 checks.append({'frame':n,'bytes':p.stat().st_size})
p=R/'DIRTY_LINE_V2.mp4'
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',str(p)]))
v=next(s for s in probe['streams'] if s['codec_type']=='video');a=next(s for s in probe['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'])==(1920,1080)
assert v['r_frame_rate']=='24/1' and int(v['nb_read_frames'])==536
assert a['channels']==2 and a['sample_rate']=='48000'
assert abs(float(probe['format']['duration'])-536/24)<.1
r=subprocess.run(['ffmpeg','-v','error','-i',str(p),'-f','null','-'],capture_output=True,text=True)
assert r.returncode==0 and not r.stderr.strip(),r.stderr
selected=[1,24,67,90,120,170,230,276,292,350,430,469,480,500,514,529]
sheet=Image.new('RGB',(1280,4*200),(12,15,20));d=ImageDraw.Draw(sheet)
for i,n in enumerate(selected):
 t=(n-1)/24;out=R/'previews'/f'final_encoded_{n:04d}.png'
 subprocess.run(['ffmpeg','-v','error','-y','-ss',str(t),'-i',str(p),'-frames:v','1',str(out)],check=True)
 with Image.open(out) as im:sheet.paste(im.resize((320,180)),((i%4)*320,(i//4)*200))
 d.text(((i%4)*320+8,(i//4)*200+183),f'Frame {n} / {t:.3f}s',fill='white')
sheet.save(R/'previews'/'FINAL_ENCODED_CONTACT_SHEET.jpg',quality=95)
report={'png_frames_fully_decoded':len(checks),'video_frames':int(v['nb_read_frames']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'duration':probe['format']['duration'],'audio_sample_rate':a['sample_rate'],'audio_channels':a['channels'],'ffmpeg_full_decode':'passed','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'visual_review':'contact sheet and selected actual encoded images must be reviewed separately; no listening claim'}
(R/'FINAL_DELIVERY_QA.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
