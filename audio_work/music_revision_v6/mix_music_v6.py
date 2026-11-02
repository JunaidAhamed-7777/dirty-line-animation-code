from pathlib import Path
import numpy as np,json,subprocess,hashlib,argparse
from scipy.io import wavfile
P=Path(__file__).parent;SR=48000;N=1072000;t=np.arange(N)/SR

def read(name):
 r,z=wavfile.read(P/name);d=z.dtype;assert r==SR;return z.astype(float)/(2**(8*d.itemsize-1) if d.kind=='i' else 1)
def save(name,z):wavfile.write(P/name,SR,z.astype(np.float32))
# Supply your own licensed 48 kHz stereo WAV; no music is included in this repository.
parser=argparse.ArgumentParser(description='Mix the film using a locally supplied licensed Catalyst recording by Scott Buckley.')
parser.add_argument('--music-source',type=Path,required=True,help='Local 48 kHz stereo WAV of Catalyst; obtain separately and follow its attribution terms.')
args=parser.parse_args()
start=72.374;src=read(args.music_source.resolve());music=src[round(start*SR):round(start*SR)+N].copy();gain=.14/np.sqrt(np.mean(music*music));music*=gain
fade=np.minimum(t/.30,1)*np.clip((N/SR-t)/1.15,0,1)
# Grounded landing: a short 6dB music dip, with gentle entry/release.
duck=np.interp(t,[0,12.015,12.05,12.09,12.22,12.40,22.334],[1,1,.5,.5,.5,1,1]);music*=fade[:,None]*duck[:,None]
save('MUSIC_EDIT_PRIVATE_V6.wav',music);engine=read('ENGINE_LOW_V6.wav');wind=read('CLEAN_AERO_WIND_V6.wav');fx=read('SPARSE_FX_SLAM_V6.wav');raw=music+engine+wind+fx;save('RAW_V6.wav',raw)
r=subprocess.run(['ffmpeg','-hide_banner','-i',str(P/'RAW_V6.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=12:print_format=json','-f','null','-'],capture_output=True,text=True);m=json.JSONDecoder().raw_decode(r.stderr[r.stderr.rfind('{'):])[0]
f=f"loudnorm=I=-16:TP=-1.5:LRA=12:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true"
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'RAW_V6.wav'),'-af',f,'-ar','48000','-c:a','pcm_s24le',str(P/'DIRTY_LINE_V6_MUSIC_WIND.wav')],capture_output=True,check=True)
subprocess.run(['ffmpeg','-hide_banner','-y','-i',str(P/'DIRTY_LINE_V6_MUSIC_WIND.wav'),'-c:a','libmp3lame','-b:a','320k',str(P/'DIRTY_LINE_V6_MUSIC_WIND.mp3')],capture_output=True,check=True)
credits='“Catalyst” by Scott Buckley — released under CC-BY 4.0. www.scottbuckley.com.au\nhttps://www.scottbuckley.com.au/library/catalyst/\nhttps://creativecommons.org/licenses/by/4.0/\nEdited excerpt; trimmed, faded and ducked for this film.'
(P/'MUSIC_CREDIT_REQUIRED.txt').write_text(credits+'\n')
def rms(z):return float(20*np.log10(max(np.sqrt(np.mean(z*z)),1e-12)))
report={'duration':N/SR,'music':{'title':'Catalyst','artist':'Scott Buckley','license':'CC-BY4.0','source':'https://www.scottbuckley.com.au/library/catalyst/','source_in':start,'source_out':start+N/SR,'changes':'Continuous excerpt,300ms entrance,1.15s closing fade,6dB landingduck12.05–12.40. No tempo change.','selection_evidence':'Waveform energy rises approaching84s source; strong measured onset84.464 maps to12.09 landing. Numerical cue selection, not auditory audition.','credit':credits,'content_id':'Artist SmartContentID checks attribution; no claim-free guarantee. Track/source/edit stems kept private, not for public source repo.'},'engine_gain_db':-12,'wind':'Synthetic smooth90–2200Hz aerodynamicnoise, no rain/rolling/gravel','landing':'Additional clean metallicbody+attack at12.09,240ms maximum,70ms exponentialdecay; musicduck. No debris/rattle tail.','sparse_ticks':[5.2,7.1,9.3],'rms_dbfs':{'music':rms(music[:int(19.5*SR)]),'engine':rms(engine[:int(19.5*SR)]),'wind':rms(wind[:int(19.5*SR)])},'source_stems_preserved':True,'subjective_listening':False}
(P/'V6_MANIFEST.json').write_text(json.dumps(report,indent=2));print(json.dumps(report['rms_dbfs']));print('READY')
