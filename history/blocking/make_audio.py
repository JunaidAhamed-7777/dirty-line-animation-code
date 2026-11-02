# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""DIRTY LINE temporary mix using ONLY recorded CC0 sound sources.
Not authentic Audi Sport quattro S1 / Ford GT40 recordings: car identity unknown.
No synthesized engine/noise/impact layers. Source mapping written alongside mix.
"""
from pathlib import Path
import argparse,json,subprocess,wave
import numpy as np
from scipy.signal import butter,sosfilt,resample_poly
from scipy.io import wavfile
P=argparse.ArgumentParser();P.add_argument('--landing',type=float,default=12.);P.add_argument('--pass-time',type=float,default=17.7);args=P.parse_args()
ROOT=Path(__file__).resolve().parent;SRC=ROOT/'audio_sources';SR=48000;T=20.;N=int(SR*T);mix=np.zeros((N,2));edits=[];cache={}
def load(rel):
 if rel not in cache:
  rate,a=wavfile.read(SRC/rel)
  a=a.astype(np.float64)/(32768 if a.dtype==np.int16 else 2147483648)
  if a.ndim==1:a=np.column_stack((a,a))
  if rate!=SR:a=resample_poly(a,SR,rate,axis=0)
  cache[rel]=a
 return cache[rel]
def smooth(x):x=np.clip(x,0,1);return x*x*(3-2*x)
def put(rel,source_start,start,duration,gain=1,pan=0,rate=1,lowpass=None,highpass=None,fade=.08,role=''):
 a=load(rel);count=int(duration*SR);idx=(source_start*SR+np.arange(count)*rate)
 if idx[-1]>=len(a):raise ValueError(f'Not enough source {rel}, {idx[-1]/SR} sec')
 x=np.column_stack([np.interp(idx,np.arange(len(a)),a[:,c]) for c in (0,1)])
 # Preserve natural engine texture, modest clip normalization for a consistent mix.
 rms=np.sqrt(np.mean(x*x));x*=min(4,.12/max(rms,1e-6))*gain
 if lowpass:x=sosfilt(butter(2,lowpass,fs=SR,output='sos'),x,axis=0)
 if highpass:x=sosfilt(butter(2,highpass,btype='highpass',fs=SR,output='sos'),x,axis=0)
 tt=np.arange(count)/SR;env=smooth(tt/fade)*smooth((duration-tt)/fade);x*=env[:,None]
 if isinstance(pan,tuple):p=np.linspace(*pan,count)
 else:p=np.full(count,pan)
 # Preserve source stereo while moving the image smoothly with the screen action.
 x[:,0]*=np.sqrt(1-np.clip(p,-.95,.95));x[:,1]*=np.sqrt(1+np.clip(p,-.95,.95))
 j=int(start*SR);end=min(j+count,N);mix[j:end]+=x[:end-j]
 edits.append(dict(source=rel,source_start=source_start,timeline_start=start,duration=duration,gain=gain,pan=pan,playback_rate=rate,lowpass=lowpass,highpass=highpass,fade_seconds=fade,role=role))
def car(i):return f'mutedio/{i:03d}-performance-cars-mutedio.wav'
# Separate real field recordings give the two cars different voices.
put(car(35),2.2,0,3.45,.65,(-.45,.05),role='Hero chase, recorded performance car identity unspecified')
put(car(38),8.5,0,3.45,.43,(.4,.15),role='Rival chase, recorded performance car identity unspecified')
put(car(34),1.2,3.25,1.65,.38,-.15,rate=.94,role='Hero braking/downshift perspective')
put(car(39),1.1,3.3,1.8,.24,.5,role='Rival recedes around paved bend')
put(car(34),8.0,4.75,5.0,.72,(.15,-.15),rate=1.03,role='Hero accelerating through gravel slide')
put(car(38),15.2,4.75,4.9,.15,.55,lowpass=2300,role='Distant rival on circuit')
put(car(34),13.1,9.55,2.65,.28,(-.2,.2),lowpass=850,rate=.90,role='Flight subjective engine hush, real recording filtered')
put(car(38),21.3,9.55,2.6,.12,.45,lowpass=1800,role='Rival beneath the jump')
put(car(35),15.0,12.0,4.2,.74,(-.15,-.25),role='Hero landing recovery acceleration')
put(car(34),23.0,12.0,4.2,.48,(.3,.18),role='Rival side-by-side acceleration')
put(car(68),1.1,15.95,2.7,.9,(-.8,.85),rate=1.02,role='Hero fixed-camera finish pass')
put(car(67),5.0,16.1,2.7,.66,(-.65,.85),rate=.96,role='Rival fixed-camera finish pass')
put(car(15),7.0,18.45,2.2,.12,.85,lowpass=1800,role='Distant engine tail after finish')
# Real-recorded effects only. Foley source use is documented rather than mislabelled.
gravel='gravel_1117_joseph_sardin.wav';screech='tire_screech_2371_dorian_clair.wav';splash='splash_1521_joseph_sardin.wav'
put(screech,.2,3.45,1.05,.45,-.1,fade=.12,role='Brake tire chirp from recorded outdoor car skid')
put(screech,1.4,5.25,2.1,.20,.15,lowpass=4200,fade=.2,role='Brief traction scrub under gravel, not continuous asphalt squeal')
put(gravel,8.0,4.65,5.0,.55,(-.3,.3),rate=1.15,highpass=250,fade=.2,role='Gravel roost constructed from recorded gravel-footstep texture')
put(gravel,20.0,5.1,4.4,.3,(.35,-.1),rate=.85,highpass=600,fade=.2,role='Secondary recorded stones/debris layer')
# Selected recorded crunch pitched down supplies body weight, not a synthetic boom.
put(gravel,10.0,args.landing,.7,.68,-.15,rate=.58,lowpass=650,fade=.015,role='Landing weight from slowed/filtered real gravel impact')
put(splash,.05,args.landing+.02,1.8,.64,(-.15,.35),rate=1.1,highpass=180,fade=.015,role='Landing spray constructed from recorded stone/water splash')
put(splash,1.8,12.2,1.8,.18,.3,rate=1.0,highpass=700,fade=.15,role='Wet spray tail from water recording')
put(gravel,11.4,18.7,.35,.13,.45,rate=1.1,highpass=700,fade=.03,role='Final recorded pebble tick')
put(gravel,13.0,19.12,.4,.075,.6,rate=.9,highpass=900,fade=.03,role='Second recorded pebble tick')
rain=SRC/'rain_1290_joseph_sardin.wav'
if rain.exists():put(rain.name,10,0,20,.045,0,highpass=350,fade=.3,role='Quiet real rain-on-puddle bed')
# Short room-free reflections are delayed copies of recorded material, no generated audio.
for delay,level in [(int(.046*SR),.035),(int(.091*SR),.018)]:mix[delay:]+=mix[:-delay,::-1]*level
mix*=smooth(np.arange(N)/SR/.08)[:,None]*smooth((T-np.arange(N)/SR)/.15)[:,None]
peak=float(np.max(np.abs(mix)));mix*=min(1,.83/max(peak,1e-8))
def save(p,x):
 with wave.open(str(p),'wb') as w:
  w.setnchannels(2);w.setsampwidth(3);w.setframerate(SR)
  v=np.clip(x*8388607,-8388608,8388607).astype(np.int32).reshape(-1);b=np.empty((len(v),3),np.uint8);b[:,0]=v&255;b[:,1]=(v>>8)&255;b[:,2]=(v>>16)&255;w.writeframes(b.tobytes())
raw=ROOT/'DIRTY_LINE_RECORDED_TEMP_raw.wav';out=ROOT/'DIRTY_LINE_RECORDED_TEMP.wav';save(raw,mix)
def stats(stderr):return json.JSONDecoder().raw_decode(stderr[stderr.rfind('{'):])[0]
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','loudnorm=I=-18:TP=-1.8:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=stats(r.stderr)
params=f"loudnorm=I=-18:TP=-1.8:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
r=subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(raw),'-af',params,'-ar',str(SR),'-c:a','pcm_s24le',str(out)],capture_output=True,text=True,check=True)
report={'status':'TEMP: generic recorded performance-car engines, not verified Audi S1/GT40','duration_seconds':T,'sample_rate':SR,'channels':2,'bits':24,'only_recorded_sources':True,'loudness':stats(r.stderr),'edits':edits,'auditory_review':'Not claimed: verified decoding, source provenance, spectrum and levels; human listening review still recommended before final use.'}
(ROOT/'audio_edit_manifest_TEMP.json').write_text(json.dumps(report,indent=2))
subprocess.run(['ffmpeg','-v','error','-y','-i',str(out),'-c:a','libmp3lame','-b:a','192k',str(ROOT/'DIRTY_LINE_RECORDED_TEMP.mp3')],check=True)
print(out);print(json.dumps(report['loudness'],indent=2))
