"""Recovery, not bit-exact restoration. Approved MP3 is the surviving bed.
No new engine performance design. Documented V2 final timing edits reconstructed.
"""
from pathlib import Path
import json,numpy as np,subprocess,wave,hashlib
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).resolve().parent;SR=48000;N=1072000;t=np.arange(N)/SR

def read(p):
 r,x=wavfile.read(p);assert r==SR;dt=x.dtype;x=x.astype(float)/(32768 if dt==np.int16 else 2147483648)
 return np.column_stack((x,x)) if x.ndim==1 else x

def save(p,x):
 with wave.open(str(p),'wb') as w:
  w.setnchannels(2);w.setsampwidth(3);w.setframerate(SR);v=np.clip(x*8388607,-8388608,8388607).astype(np.int32).reshape(-1);b=np.empty((len(v),3),np.uint8)
  for i in range(3):b[:,i]=(v>>(8*i))&255
  w.writeframes(b.tobytes())
x=read(P/'APPROVED_BED_DECODED_FROM_MP3.wav');x=np.pad(x,((0,max(0,N-len(x))),(0,0)))[:N]
def win(a,b):return np.clip((t-a)/.06,0,1)*np.clip((b-t)/.06,0,1)
# Surviving mix cannot separate engine and wind perspective; conservative combined gain.
env=10**((-3.5*win(2.2,4.2)-1.8*win(15.8,19.))/20)
env*=np.where(t<19.75,1,np.exp(-1.25*(t-19.75)));x*=env[:,None]
accent=np.zeros_like(x);edits=[]
def add(name,src,start,dur,peak,hp,lp,role):
 a=read(P/'sources'/name)[round(src*SR):round((src+dur)*SR)];tt=np.arange(len(a))/SR
 if hp:a=sosfilt(butter(2,hp,btype='highpass',fs=SR,output='sos'),a,axis=0)
 if lp:a=sosfilt(butter(2,lp,fs=SR,output='sos'),a,axis=0)
 if role=='traction':a*=(np.exp(-.5*((tt-.23)/.09)**2)+.5*np.exp(-.5*((tt-.46)/.065)**2))[:,None]
 a*=peak/max(abs(a).max(),1e-9);a*=np.minimum(tt/.003,1)[:,None]*np.minimum((dur-tt)/.07,1)[:,None];j=round(start*SR);accent[j:j+len(a)]+=a;edits.append({'source':name,'source_in':src,'timeline_in':start,'duration':dur,'role':role,'peak':peak})
add('heavy_metal.wav',1.134,12.09,.31,.36,80,3000,'chassis slam')
add('metal_debris.wav',.113,12.105,.38,.13,1700,9000,'spark skitter')
add('tire.wav',2.8,12.14,.70,.10,600,6000,'traction')
x+=accent;x*=min(1,.89/abs(x).max());x*=np.minimum((N-np.arange(N))/SR/.01,1)[:,None]
raw=P/'RECOVERED_FINAL_AUDIO_raw.wav';out=P/'DIRTY_LINE_V2_FINAL_AUDIO_RECOVERED.wav';save(raw,x)
def stats(s):return json.JSONDecoder().raw_decode(s[s.rfind('{'):])[0]
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(raw),'-af','loudnorm=I=-17:TP=-1.5:LRA=10:print_format=json','-f','null','-'],capture_output=True,text=True,check=True);m=stats(r.stderr)
f=f"loudnorm=I=-17:TP=-1.5:LRA=10:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true:print_format=json"
r=subprocess.run(['ffmpeg','-y','-hide_banner','-i',str(raw),'-af',f,'-ar',str(SR),'-c:a','pcm_s24le',str(out)],capture_output=True,text=True,check=True)
report={'status':'Reconstructed from approved320kbpsMP3, NOT bit-exact/lossless restoration','duration':N/SR,'approved_bed':'DIRTY_LINE_V2_CONTINUOUS_ENGINES.mp3','quality_gap':'MP3 compression already irreversible; original lossless V2 stems lost. Combined camera/finish gain approximates prior independent engine/wind attenuation; wind19.85 cannot independently recover, common recession19.75. No new engine take/pitch edits.','restored_edits':edits,'loudness':stats(r.stderr),'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'no_hearing_claim':True}
(P/'AUDIO_RECOVERY_MANIFEST.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
