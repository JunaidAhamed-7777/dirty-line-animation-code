import numpy as np, json, re, hashlib
from scipy.io import wavfile
class sf:
 @staticmethod
 def read(path):
  rate,z=wavfile.read(path)
  if z.dtype.kind=="i": z=z.astype(float)/float(2**(z.dtype.itemsize*8-1))
  return z,rate
from pathlib import Path
from scipy.signal import correlate
p=Path(__file__).parent
x,sr=sf.read(p/'DIRTY_LINE_V2_FINAL_AUDIO_RECOVERED.wav'); y,sy=sf.read(p/'FINAL_ENCODED_DECODED.wav')
n=min(len(x),len(y)); a=x[:n]; b=y[:n]
# Check audio timing with cross correlation over first 2s, +-1000 samples.
c=correlate(b[:96000].mean(1),a[:96000].mean(1),mode='full',method='fft'); mid=95999; lag=int(np.argmax(c[mid-1000:mid+1001])-1000)
probe=json.loads((p/'final_encoded_probe.json').read_text()); v=next(s for s in probe['streams'] if s['codec_type']=='video'); au=next(s for s in probe['streams'] if s['codec_type']=='audio')
log=(p/'final_encoded_loudness.log').read_text(); loud=json.loads(re.findall(r'\{[^{}]+\}',log)[-1])
def rms(z): return float(20*np.log10(max(np.sqrt(np.mean(z*z)),1e-12)))
w=int(.1*sr); windows=[rms(b[i:i+w]) for i in range(0,int(20.6*sr)-w+1,w)]
events={}
for key,lo,hi in [('approach',10,11.04),('airborne',11.04,12.09),('precontact',11.99,12.08),('contact',12.09,12.16),('traction',12.14,12.84),('finish',19.3,19.7),('recession',20.2,20.8),('ending',21.8,22.3)]:
 z=b[int(lo*sr):int(hi*sr)];events[key]={'interval_seconds':[lo,hi],'rms_dbfs':rms(z),'peak_dbfs':float(20*np.log10(max(np.max(abs(z)),1e-12)))}
result={'video':{'codec':v['codec_name'],'width':v['width'],'height':v['height'],'frames':v.get('nb_frames'),'fps':v['avg_frame_rate'],'duration':v['duration']},'audio':{'codec':au['codec_name'],'sample_rate':sy,'channels':au['channels'],'stream_duration':au['duration'],'stream_start':au.get('start_time'),'decoded_samples':len(y),'reference_samples':len(x),'aac_padding_samples':len(y)-len(x)},'comparison':{'lag_samples':lag,'correlation':float(np.corrcoef(a.ravel(),b.ravel())[0,1]),'error_rms_dbfs':rms(b-a),'reference_sha256':hashlib.sha256((p/'DIRTY_LINE_V2_FINAL_AUDIO_RECOVERED.wav').read_bytes()).hexdigest()},'levels':{'integrated_lufs':float(loud['input_i']),'true_peak_dbtp':float(loud['input_tp']),'lra':float(loud['input_lra']),'clipped_samples':int(np.sum(abs(b)>=1)),'minimum_100ms_rms_before_20_6_dbfs':min(windows),'silent_100ms_windows_before_20_6':sum(z < -100 for z in windows)},'event_windows':events,'scope':'Technical decoded-AAC QA, no subjective listening claim. Native picture timing previously inspected. No music or gratuitous edits applied.'}
result['pass']=lag==0 and result['comparison']['correlation']>.99 and result['levels']['clipped_samples']==0 and result['levels']['true_peak_dbtp']<=-1 and result['levels']['silent_100ms_windows_before_20_6']==0
(p/'FINAL_ENCODED_AUDIO_QA.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
