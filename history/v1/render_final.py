# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""Resumable final rendering. Run with official Blender4.3.2 in background."""
import bpy,os,time,json,hashlib
R=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.adaptive_min_samples=8;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.10;s.render.threads_mode='FIXED';s.render.threads=8
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=25
os.makedirs(R+'/renders',exist_ok=True)
source_hash=hashlib.sha256(open(R+'/DIRTY_LINE.blend','rb').read()).hexdigest()
manifest_path=R+'/render_manifest.json'
manifest={'source_sha256':source_hash,'resolution':[1920,1080],'fps':24,'frames':536,'samples':32,'adaptive_min_samples':8,'adaptive_threshold':.10}
if os.path.exists(manifest_path):
 old=json.load(open(manifest_path))
 if old!=manifest and any(n.startswith('frame_') for n in os.listdir(R+'/renders')):raise RuntimeError('Source/settings changed: archive invalidated frames before resuming, do not mix revisions')
json.dump(manifest,open(manifest_path,'w'),indent=2)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE_FINAL.blend',compress=True)
records=[];start=time.time()
for fr in range(1,537):
 if os.path.exists(R+'/STOP_RENDER'):
  print('RENDER_STOP_REQUESTED_AT_FRAME',fr,flush=True);break
 path=R+'/renders/frame_%04d.png'%fr
 # Blender output is checked by signature/IHDR here; final full decode is separate.
 valid=False
 if os.path.exists(path):
  import struct
  with open(path,'rb') as f:
   header=f.read(24);f.seek(-12,2);tail=f.read(12)
  valid=tail==b'\x00\x00\x00\x00IEND\xaeB`\x82' and len(header)==24 and header[:8]==b'\x89PNG\r\n\x1a\n' and struct.unpack('>II',header[16:24])==(1920,1080) and os.path.getsize(path)>10000
 if valid:continue
 s.frame_set(fr);s.render.filepath=path;t=time.time();bpy.ops.render.render(write_still=True);elapsed=time.time()-t
 rec={'frame':fr,'seconds':elapsed,'elapsed_run_seconds':time.time()-start,'bytes':os.path.getsize(path)};records.append(rec)
 with open(R+'/render_progress.jsonl','a') as f:f.write(json.dumps(rec)+'\n')
 print('FINAL_FRAME_COMPLETE',json.dumps(rec),flush=True)
else:print('FINAL_RENDER_COMPLETE',flush=True)
