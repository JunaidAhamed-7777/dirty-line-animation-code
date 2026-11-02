import numpy as np
from scipy.io import wavfile
from scipy.signal import welch
from pathlib import Path
for p in sorted((Path(__file__).parent/'sources').glob('*mutedio.wav')):
 r,x=wavfile.read(p);x=x.astype(float)/(2**31);x=x.mean(axis=1)
 print(p.name,'duration',len(x)/r)
 for st in range(0,int(len(x)/r)-2,2):
  y=x[st*r:(st+2)*r];f,s=welch(y,fs=r,nperseg=8192);band=(f>90)&(f<1400);peak=f[band][np.argmax(s[band])];rms=20*np.log10(np.sqrt(np.mean(y*y))+1e-12);cent=(f[band]*s[band]).sum()/s[band].sum()
  print(st,round(rms,1),round(peak),round(cent))
