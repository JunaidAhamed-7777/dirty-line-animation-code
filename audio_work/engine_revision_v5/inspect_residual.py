from pathlib import Path
import numpy as np,json
from scipy.io import wavfile
from scipy.signal import butter,sosfilt
P=Path(__file__).parent;r,eng=wavfile.read(P/'ENGINE_ONLY_V5.wav');_,fx=wavfile.read(P/'SFX_SPARSE_V5.wav');_,old=wavfile.read(P.parent/'engine_revision_v4/SFX_NO_GRAVEL_V4.wav');t=np.arange(len(eng))/r;outside=(t<12.09)|(t>=12.84)
for st in [5.2,7.1,9.3]:outside &= ~((t>=st)&(t<st+.055))
removed=old-fx
wavfile.write(P/'REMOVED_V4_NONENGINE_TEXTURE.wav',r,removed)
def rms(x):return float(20*np.log10(max(np.sqrt(np.mean(x.astype(float)**2)),1e-12)))
# Isolated-source numerical inspection, not auditory identification.
regions={}
for a,b in [(0,3),(5,9),(13,17),(19,20.5)]:
 z=eng[int(a*r):int(b*r)].astype(float);hi=sosfilt(butter(2,2200,btype='highpass',fs=r,output='sos'),z,axis=0);regions[f'{a}-{b}']={'engine_rms_dbfs':rms(z),'engine_above2200hz_rms_dbfs':rms(hi),'V4_nonengine_rms_dbfs':rms(old[int(a*r):int(b*r)]),'V5_nonengine_rms_dbfs':rms(fx[int(a*r):int(b*r)])}
q={'engine_byte_identical_to_V3':(P/'ENGINE_ONLY_V5.wav').read_bytes()==(P.parent/'engine_revision_v3/ENGINE_ONLY_V3.wav').read_bytes(),'nonengine_nonzero_samples_outside_allowed_events':int(np.count_nonzero(fx[outside])),'nonengine_max_abs_outside_allowed_events':float(abs(fx[outside]).max()),'landing_window':[12.09,12.84],'isolated_ticks':[[5.2,5.255],[7.1,7.155],[9.3,9.355]],'regions':regions,'verified_removed':'Continuous rain/rolling texture; all gravel; landing splash; metal skitter/debris. No non-engine samples outside landing and three isolated55ms ticks.','uncertainty':'Embedded broadband chatter in field-recorded engines is possible; numerical spectrum cannot identify perceived gravel. No listening tool available; no auditory claim. Engines left unchanged rather than blindly filtered.'};(P/'V5_RESIDUAL_AUDIT.json').write_text(json.dumps(q,indent=2));print(json.dumps(q,indent=2))
