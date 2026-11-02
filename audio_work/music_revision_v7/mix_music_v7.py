from pathlib import Path
import numpy as np,json,subprocess,hashlib,argparse
from scipy.io import wavfile
P=Path(__file__).parent;SR=48000;N=1072000;t=np.arange(N)/SR

def read(name):
 r,z=wavfile.read(P/name);d=z.dtype;assert r==SR;return z.astype(float)/(2**(8*d.itemsize-1) if d.kind=='i' else 1)
def save(name,z):wavfile.write(P/name,SR,z.astype(np.float32))
# Supply licensed music and its required attribution separately; no music assets are distributed.
parser=argparse.ArgumentParser(description='Mix locally supplied licensed Racket and Bang by TeknoAXE.')
parser.add_argument('--music-source',type=Path,required=True,help='Local 48 kHz stereo WAV, obtained separately under the applicable license.')
parser.add_argument('--music-credit-file',type=Path,required=True,help='Text file containing the required music attribution.')
args=parser.parse_args()
start=0.;delay=.042;src=read(args.music_source.resolve());music=np.pad(src,((round(delay*SR),0),(0,0)))[:N].copy();gain=.14/np.sqrt(np.mean(music*music));music*=gain
fade=np.minimum(t/.30,1)*np.clip((N/SR-t)/1.15,0,1)
# Grounded landing: a short 6dB music dip, with gentle entry/release.
duck=np.interp(t,[0,12.015,12.05,12.09,12.22,12.40,22.334],[1,1,.5,.5,.5,1,1]);music*=fade[:,None]*duck[:,None]
save('MUSIC_EDIT_PRIVATE_V7.wav',music);engine=read('../engine_revision_v5/ENGINE_ONLY_V5.wav')*10**(-9/20);save('ENGINE_LOW_V7.wav',engine);wind=read('../music_revision_v6/CLEAN_AERO_WIND_V6.wav');fx=read('../music_revision_v6/SPARSE_FX_SLAM_V6.wav');raw=music+engine+wind+fx;save('RAW_V7.wav',raw)
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'RAW_V7.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=12:print_format=json','-f','null','-'],capture_output=True,text=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
f=f"loudnorm=I=-16:TP=-1.5:LRA=12:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'RAW_V7.wav'),'-af',f,'-ar','48000','-c:a','pcm_s24le',str(P/'DIRTY_LINE_V7_RACKET_AND_BANG.wav')],capture_output=True,check=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'DIRTY_LINE_V7_RACKET_AND_BANG.wav'),'-c:a','libmp3lame','-b:a','320k',str(P/'DIRTY_LINE_V7_RACKET_AND_BANG.mp3')],capture_output=True,check=True)
credits=args.music_credit_file.read_text().strip()
(P/'MUSIC_CREDIT_REQUIRED.txt').write_text(credits+'\n')
def rms(z):return float(20*np.log10(max(np.sqrt(np.mean(z*z)),1e-12)))
report={'duration':N/SR,'music':{'title':'Racket and Bang','artist':'TeknoAXE','license':'CC-BY4.0','source':'https://teknoaxe.com/Link_Code_3.php?genre=Drum_and_Bass&q=2375','source_in':start,'source_out':N/SR-delay,'timeline_delay':delay,'changes':'Continuous excerpt,300ms entrance,1.15s closing fade,6dB landingduck12.05–12.40. No tempo change.','selection_evidence':'Original opening builds at6s and12s source; measured onset12.048 maps to12.090 landing with42ms opening offset. Source19.552 onset maps19.594 nearfinish. Measured pulse intervals about375ms; not an asserted meter. Numerical analysis, not hearing.','credit':credits,'content_id':'No verified artist-specific ContentID policy; no claim-free guarantee. Source/edit stems kept private, excluded from public code repo.'},'engine_gain_db':-9,'engine_change_from_V6_db':3,'wind':'Synthetic smooth90–2200Hz aerodynamicnoise, no rain/rolling/gravel','landing':'Additional clean metallicbody+attack at12.09,240ms maximum,70ms exponentialdecay; musicduck. No debris/rattle tail.','sparse_ticks':[5.2,7.1,9.3],'rms_dbfs':{'music':rms(music[:int(19.5*SR)]),'engine':rms(engine[:int(19.5*SR)]),'wind':rms(wind[:int(19.5*SR)])},'source_stems_preserved':True,'subjective_listening':False}
(P/'V7_MANIFEST.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['rms_dbfs']));print('READY')
