from pathlib import Path
import numpy as np,json
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
from scipy.ndimage import gaussian_filter1d
P=Path(__file__).parent;A=P.parent;SR=48000;N=1072000;t=np.arange(N)/SR

def read(p):
 r,z=wavfile.read(p);d=z.dtype;assert r==SR;z=z.astype(float)/(2**(8*d.itemsize-1) if d.kind=='i' else 1);return np.column_stack((z,z)) if z.ndim==1 else z
def save(name,z):wavfile.write(P/name,SR,z.astype(np.float32))
def band(z,lo,hi):return sosfilt(butter(2,[lo,hi],btype='bandpass',fs=SR,output='sos'),z,axis=0)
engine=read(A/'engine_revision_v5/ENGINE_ONLY_V5.wav')*10**(-12/20)
fx=read(A/'engine_revision_v5/SFX_SPARSE_V5.wav').copy()
# Existing subtle160ms thud is retained; add clean single metallic attack/body, no debris tail.
src=read(A/'sources/heavy_metal.wav');a=src[round(1.134*SR):round((1.134+.24)*SR)]
body=band(a,55,500);attack=band(a,700,4200);body*=.50/max(abs(body).max(),1e-9);attack*=.27/max(abs(attack).max(),1e-9)
tt=np.arange(len(a))/SR;env=np.minimum(tt/.0015,1)*np.exp(-tt/0.070)*np.minimum((.24-tt)/.018,1)
hit=(body+attack)*env[:,None];j=round(12.09*SR);fx[j:j+len(hit)]+=hit
save('ENGINE_LOW_V6.wav',engine);save('SPARSE_FX_SLAM_V6.wav',fx)
# Smooth aerodynamic noise, explicitly synthesized per latest authorization. No rain/gravel/rolling sample.
rng=np.random.default_rng(61209);noise=rng.normal(0,1,(N,2));wind=band(noise,90,2200)
wind/=np.sqrt(np.mean(wind*wind));base=np.interp(t,[0,.35,.85,2.2,4.2,8.6,10.55,11.04,12.09,12.5,15.8,19,19.53,19.85,20.7,22.333],[.028,.045,.034,.020,.039,.036,.041,.026,.026,.040,.037,.024,.052,.034,.006,0])
base=gaussian_filter1d(base[::240],7);base=np.interp(np.arange(N),np.arange(len(base))*240,base)
# Broad slowly changing energy, not granular transients.
wind*=base[:,None];wind*=np.minimum(t/.09,1)[:,None]*np.minimum((N/SR-t)/.20,1)[:,None]
save('CLEAN_AERO_WIND_V6.wav',wind)
report={'duration':N/SR,'engine_gain_db':-12,'engine_source':'exact V5 engine stem, unchanged pitch/timing','wind':'New deterministic synthetic90–2200Hz smooth aerodynamic noise. No recorded rain/road/gravel texture. Allowed latest user request.','fx':'Preserved V5 three55ms metal ticks and landing squeal. Added single240ms maximum heavy_metal body55–500Hz+attack700–4200Hz,70ms exponentialdecay at12.09. No debris tails.','music_pending':True,'no_subjective_listening':True}
(P/'V6_BEDS_MANIFEST.json').write_text(json.dumps(report,indent=2));print('BEDS READY')
