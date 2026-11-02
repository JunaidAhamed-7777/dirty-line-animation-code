from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import resample_poly,butter,sosfilt
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).parent; S=P/'sources';SR=48000;N=1072000;t=np.arange(N)/SR
manifest=[]
def read(p):
 r,z=wavfile.read(p);d=z.dtype;z=z.astype(float)/(2**(8*d.itemsize-1) if d.kind=='i' else 1)
 if z.ndim==1:z=np.column_stack([z,z])
 if r!=SR:z=resample_poly(z,SR,r,axis=0)
 return z

def save(name,z):wavfile.write(P/name,SR,z.astype(np.float32))
def filt(z,hp,lp):return sosfilt(butter(2,[hp,lp],btype='bandpass',fs=SR,output='sos'),z,axis=0)
def level(z,target):
 # Slow gain leveling, retaining the recorded texture rather than rev-envelope.
 energy=gaussian_filter1d(np.mean(z*z,axis=1)[::240],55); rms=np.sqrt(np.interp(np.arange(len(z)),np.arange(len(energy))*240,energy)+1e-8)
 return z*np.clip(target/rms,.2,5)[:,None]
def engine(file,sections,rate,shifts,pan,target):
 src=read(S/file);out=np.zeros((N,2));weight=np.zeros(N)
 for start,a,b in sections:
  st=int(start*SR);duration=(b-a)/rate;num=min(N-st,int(duration*SR));tt=np.arange(num)/SR
  rr=np.ones(num)*rate
  for shift in shifts:rr*=1-.11*np.exp(-np.maximum(tt+start-shift,0)/.16)*(tt+start>=shift)
  idx=a*SR+np.cumsum(rr);z=np.column_stack([np.interp(idx,np.arange(len(src)),src[:,c]) for c in range(2)])
  z=level(filt(z,80,6500),target)
  w=np.minimum(tt/.55,1)*np.minimum((duration-tt)/.55,1)
  if st==0:w=np.minimum((duration-tt)/.55,1)
  out[st:st+num]+=z*w[:,None];weight[st:st+num]+=w
  manifest.append({'role':'loaded engine','file':file,'source':[a,b],'timeline_in':start,'playback_rate_base':rate,'crossfade_seconds':.55})
 out/=np.maximum(weight,.001)[:,None]
 # Perspective and power remain continuous, only brief torque release at shifts.
 env=np.ones(N)
 for shift in shifts:env*=1-.12*np.exp(-np.maximum(t-shift,0)/.10)*(t>=shift)
 env*=1-.24*np.exp(-((t-11.55)/.5)**6)
 env*=np.where(t<19.53,1,np.exp(-2.5*(t-19.53)))
 env*=np.minimum((22.333333-t)/.3,1)
 p=pan+.30*np.tanh((t-19.53)*5)
 out[:,0]*=np.sqrt((1-p)/2);out[:,1]*=np.sqrt((1+p)/2)
 return out*env[:,None]
hero=engine('039-performance-cars-mutedio.wav',[(0,2,21.5),(14.5,4.1,16)],1.15,[1.7,6.65,14.1,17.45],-.22,.125)
rival=engine('038-performance-cars-mutedio.wav',[(0,10.25,16.8),(5.0,10.7,16.6),(9.7,10.15,16.8),(14.85,10.65,16.9),(19.4,10.2,15.5)],1.02,[2.45,7.6,14.9,18.1],.28,.080)
fx=np.zeros((N,2))
def event(path,src,start,dur,peak,hp=100,lp=9000,role='FX',shape=None):
 z=read(path);idx=(src+np.arange(round(dur*SR))/SR)*SR
 a=np.column_stack([np.interp(idx,np.arange(len(z)),z[:,c]) for c in range(2)]);a=filt(a,hp,lp);tt=np.arange(len(a))/SR
 if shape=='traction':a*=(np.exp(-.5*((tt-.23)/.09)**2)+.5*np.exp(-.5*((tt-.46)/.065)**2))[:,None]
 a*=peak/max(abs(a).max(),1e-9);a*=np.minimum(tt/.003,1)[:,None]*np.minimum((dur-tt)/.07,1)[:,None];i=round(start*SR);n=min(len(a),N-i);fx[i:i+n]+=a[:n]
 manifest.append({'role':role,'file':str(path.name),'source_in':src,'timeline_in':start,'duration':dur})
# Rebuild recorded rolling/wind-like wet-road texture; no old mixed bed, no offroad squeal.
road=read(S/'rain_1290_joseph_sardin.wav'); idx=np.arange(N)%len(road);road=filt(road[idx],350,6500);road=level(road,.018)
env=np.where((t>=4.65)&(t<12.09),.23,1.0);env*=np.where(t<19.75,1,np.exp(-1.8*(t-19.75)));road*=env[:,None];fx+=road
for st,source,dur in [(4.65,.4,3.7),(7.8,1.2,3.25)]:event(S/'gravel_1117_joseph_sardin.wav',source,st,dur,.11,180,8000,'gravel roost, recorded gravel foley')
event(S/'splash_1521_joseph_sardin.wav',.1,12.09,.65,.13,150,9000,'wet landing spray')
event(P.parent/'sources/heavy_metal.wav',1.134,12.09,.31,.36,80,3000,'chassis slam, unchanged recipe')
event(P.parent/'sources/metal_debris.wav',.113,12.105,.38,.13,1700,9000,'spark skitter, unchanged recipe')
event(P.parent/'sources/tire.wav',2.8,12.14,.70,.10,600,6000,'ONLY tire squeal after landing','traction')
eng=hero+rival;save('ENGINE_ONLY_V3.wav',eng);save('SFX_REBUILT_V3.wav',fx);save('RAW_V3.wav',eng+fx)
# Two-pass loudness normalisation.
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'RAW_V3.wav'),'-af','loudnorm=I=-17:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
f=f"loudnorm=I=-17:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'RAW_V3.wav'),'-af',f,'-ar','48000','-c:a','pcm_s24le',str(P/'DIRTY_LINE_V3_LOADED_ENGINES.wav')],capture_output=True,check=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'DIRTY_LINE_V3_LOADED_ENGINES.wav'),'-c:a','libmp3lame','-b:a','320k',str(P/'DIRTY_LINE_V3_LOADED_ENGINES.mp3')],capture_output=True,check=True)
report={'duration':N/SR,'edits':manifest,'important':'Original separate SFX stems lost. FX reconstructed from original CC0 recordings, NOT bit-identical. No residual old mixed bed. No music. No offroad or title tire squeal. Only traction squeal12.14–12.84. Engine model/cylinder identities unknown. No subjective listening claim.','engine_design':'039 steady loaded section and independently recorded038 loaded sections, long irregular source selections and crossfades, 11 percent brief upshift rate dips with160ms recovery; no idle sections.', 'source_license':'muted.io performance cars CC0; BigSoundBank Joseph Sardin/Dorian Clair CC0, provenance in handoff archive and prior recovery manifest'}
(P/'V3_MANIFEST.json').write_text(json.dumps(report,indent=2));print('DONE')
