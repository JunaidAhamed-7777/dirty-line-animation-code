import bpy,os,sys,time,json,hashlib,struct
R=os.path.dirname(os.path.abspath(__file__));folder=R+'/motion_preview_frames';os.makedirs(folder,exist_ok=True);s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.render.use_persistent_data=False;s.render.threads_mode='FIXED';s.render.threads=8;s.cycles.samples=8;s.cycles.adaptive_min_samples=4;s.cycles.adaptive_threshold=.18;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.render.resolution_x=480;s.render.resolution_y=270;s.render.resolution_percentage=100;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.compression=15
manifest={'source_sha256':hashlib.sha256(open(R+'/DIRTY_LINE.blend','rb').read()).hexdigest(),'size':[480,270],'samples':8,'frames':536,'fps':24};mp=folder+'/manifest.json'
if os.path.exists(mp) and json.load(open(mp))!=manifest:raise RuntimeError('Preview revision mismatch, do not mix frames')
json.dump(manifest,open(mp,'w'),indent=2)
for fr in range(1,537):
 path=folder+'/%04d.png'%fr
 if os.path.exists(path):continue
 s.frame_set(fr);s.render.filepath=folder+'/pending.png';start=time.time();bpy.ops.render.render(write_still=True);os.replace(folder+'/pending.png',path)
 with open(folder+'/progress.jsonl','a') as f:f.write(json.dumps({'frame':fr,'seconds':time.time()-start})+'\n')
 print('MOTION_PREVIEW_FRAME',fr,flush=True)
print('MOTION_PREVIEW_COMPLETE',flush=True)
