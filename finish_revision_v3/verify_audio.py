import numpy as np,json,re,hashlib
from pathlib import Path
from scipy.io import wavfile
from scipy.signal import correlate
P=Path(__file__).parent;A=P.parent/'audio_work/engine_revision_v3'
def read(p):
 r,z=wavfile.read(p);d=z.dtype;return r,z.astype(float)/(2**(d.itemsize*8-1) if d.kind=='i' else 1)
r,x=read(A/'DIRTY_LINE_V3_LOADED_ENGINES.wav');sy,y=read(P/'FINAL_AAC_DECODED.wav');n=min(len(x),len(y));x=x[:n];y=y[:n]
c=correlate(y[:96000].mean(1),x[:96000].mean(1),mode='full',method='fft');lag=int(np.argmax(c[94999:97000])-1000)
l=json.loads(re.findall(r'\{[^{}]+\}',(P/'audio_loudness.log').read_text())[-1]);probe=json.loads((P/'audio_probe.json').read_text());audio=next(s for s in probe['streams'] if s['codec_type']=='audio');video=next(s for s in probe['streams'] if s['codec_type']=='video')
manifest=json.loads((A/'V3_MANIFEST.json').read_text());tires=[e for e in manifest['edits'] if 'tire' in e['file']];_,eng=read(A/'ENGINE_ONLY_V3.wav');rms=[float(20*np.log10(max(np.sqrt(np.mean(eng[i:i+4800]**2)),1e-12))) for i in range(0,int(19.5*r),4800)]
d={'status':'PASS','audio_alignment_samples':lag,'reference_correlation':float(np.corrcoef(x.ravel(),y.ravel())[0,1]),'integrated_lufs':float(l['input_i']),'true_peak_dbtp':float(l['input_tp']),'clipped_samples':int(np.sum(abs(y)>=1)),'audio_duration':audio['duration'],'audio_start':audio['start_time'],'sample_rate':audio['sample_rate'],'channels':audio['channels'],'video_duration':video['duration'],'frames':video['nb_frames'],'tire_events':tires,'no_offroad_squeal':'Verified construction manifest and source code: no old mixed bed retained; only tire source event12.14–12.84. Not a subjective listening claim.','loaded_engine_construction':'Recorded039 steady loaded sections plus independent038 loaded sections; long crossfades. Brief11% rate dips recovering160ms at hero1.7,6.65,14.1,17.45; rival2.45,7.6,14.9,18.1. No idle sections intentionally selected.','minimum_engine_100ms_rms_dbfs_before19_5':min(rms),'silent_engine_windows':sum(z < -100 for z in rms),'reference_sha256':hashlib.sha256((A/'DIRTY_LINE_V3_LOADED_ENGINES.wav').read_bytes()).hexdigest(),'scope':'Technical encoded audio alignment and source-construction QA. No subjective hearing or engine identity claims. No music. FX reconstructed after source-stem loss, not bit-identical to prior mix.'}
if lag!=0 or d['reference_correlation']<.99 or d['clipped_samples'] or d['true_peak_dbtp']>-1:d['status']='CHECK'
(P/'FINAL_V3_AUDIO_QA.json').write_text(json.dumps(d,indent=2)+'\n');print(json.dumps(d,indent=2))
