import bpy,os,time,json
R=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
s.render.use_persistent_data=False;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=100;s.cycles.samples=32;s.cycles.adaptive_min_samples=8;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.10;s.render.threads_mode='FIXED';s.render.threads=4
s.cycles.use_auto_tile=True;s.cycles.tile_size=256
s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.image_settings.color_depth='8';s.render.image_settings.compression=25
os.makedirs(R+'/native',exist_ok=True)
for fr in range(463,480):
 path=R+'/native/frame_%04d.png'%fr
 if os.path.exists(path):continue
 s.frame_set(fr);s.render.filepath=path;t=time.time();bpy.ops.render.render(write_still=True)
 rec={'frame':fr,'seconds':time.time()-t,'bytes':os.path.getsize(path)}
 with open(R+'/native_progress.jsonl','a') as f:f.write(json.dumps(rec)+'\n')
 print('NATIVE_BLUR_COMPLETE',json.dumps(rec),flush=True)
print('ALL_17_BLUR_FRAMES_COMPLETE',flush=True)
