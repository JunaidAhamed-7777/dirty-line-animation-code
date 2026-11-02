from pathlib import Path
import numpy as np,json,subprocess
from scipy.io import wavfile
from scipy.signal import resample_poly,butter,sosfilt
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).parent; S=P.parent/'engine_revision_v3/sources';SR=48000;N=1072000;t=np.arange(N)/SR
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
# Copy approved engine stem byte-for-byte: no engine resynthesis.
import shutil,hashlib
shutil.copy2(P.parent/'engine_revision_v3/ENGINE_ONLY_V3.wav',P/'ENGINE_ONLY_V5.wav')
eng=read(P/'ENGINE_ONLY_V5.wav')
fx=np.zeros((N,2))
def event(path,src,start,dur,peak,hp=100,lp=9000,role='FX',shape=None):
 z=read(path);idx=(src+np.arange(round(dur*SR))/SR)*SR
 a=np.column_stack([np.interp(idx,np.arange(len(z)),z[:,c]) for c in range(2)]);a=filt(a,hp,lp);tt=np.arange(len(a))/SR
 if shape=='traction':a*=(np.exp(-.5*((tt-.23)/.09)**2)+.5*np.exp(-.5*((tt-.46)/.065)**2))[:,None]
 a*=peak/max(abs(a).max(),1e-9);a*=np.minimum(tt/.003,1)[:,None]*np.minimum((dur-tt)/.07,1)[:,None];i=round(start*SR);n=min(len(a),N-i);fx[i:i+n]+=a[:n]
 manifest.append({'role':role,'file':str(path.name),'source_in':src,'timeline_in':start,'duration':dur})
# No continuous road, rain, gravel or rolling texture; no offroad squeal.
# Three isolated recorded metal pings, not a gravel/rolling bed.
for when,source in [(5.2,.113),(7.1,.145),(9.3,.181)]:
 event(P.parent/'sources/metal_debris.wav',source,when,.055,.035,900,6500,'isolated rock-on-metal proxy tick')
event(P.parent/'sources/heavy_metal.wav',1.134,12.09,.16,.30,65,650,'brief low-passed landing thud')
event(P.parent/'sources/tire.wav',2.8,12.14,.70,.10,600,6000,'ONLY tire squeal after landing','traction')
save('SFX_SPARSE_V5.wav',fx);save('RAW_V5.wav',eng+fx)
# Two-pass loudness normalisation.
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'RAW_V5.wav'),'-af','loudnorm=I=-17:TP=-1.5:LRA=11:print_format=json','-f','null','-'],capture_output=True,text=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
f=f"loudnorm=I=-17:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'RAW_V5.wav'),'-af',f,'-ar','48000','-c:a','pcm_s24le',str(P/'DIRTY_LINE_V5_MINIMAL.wav')],capture_output=True,check=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'DIRTY_LINE_V5_MINIMAL.wav'),'-c:a','libmp3lame','-b:a','320k',str(P/'DIRTY_LINE_V5_MINIMAL.mp3')],capture_output=True,check=True)
report={'duration':N/SR,'edits':manifest,'removed':'ALL rain/rolling/wet-road/gravel/splash/skitter/debris layers removed. Exact engine stem plus short low-passed thud, landing squeal, and three55ms quiet metal ticks at5.2/7.1/9.3 remain. No continuous non-engine texture.','engine_stem_sha256':hashlib.sha256((P/'ENGINE_ONLY_V5.wav').read_bytes()).hexdigest(),'engine_stem_byte_identical':(P/'ENGINE_ONLY_V5.wav').read_bytes()==(P.parent/'engine_revision_v3/ENGINE_ONLY_V3.wav').read_bytes(),'important':'Original separate SFX stems lost. FX reconstructed from original CC0 recordings, NOT bit-identical. No residual old mixed bed. No music. No offroad or title tire squeal. Only traction squeal12.14–12.84. Engine model/cylinder identities unknown. No subjective listening claim.','engine_design':'039 steady loaded section and independently recorded038 loaded sections, long irregular source selections and crossfades, 11 percent brief upshift rate dips with160ms recovery; no idle sections.', 'source_license':'muted.io performance cars CC0; BigSoundBank Joseph Sardin/Dorian Clair CC0, provenance in handoff archive and prior recovery manifest'}
(P/'V5_MANIFEST.json').write_text(json.dumps(report,indent=2));print('DONE')
