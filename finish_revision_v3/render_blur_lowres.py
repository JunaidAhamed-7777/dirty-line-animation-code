import bpy,os,time,json,gc
R=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
s.render.engine='CYCLES';s.cycles.device='CPU';s.render.threads_mode='FIXED';s.render.threads=4;s.render.use_persistent_data=False;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.render.image_settings.file_format='PNG';s.render.image_settings.color_mode='RGB';s.render.resolution_percentage=100
s.render.resolution_x=480;s.render.resolution_y=270;s.cycles.samples=8;s.cycles.adaptive_min_samples=4;s.cycles.adaptive_threshold=.18
os.makedirs(R+'/blur_only_preview',exist_ok=True)
for fr in range(463,480):
 s.frame_set(fr);s.render.filepath=R+'/blur_only_preview/%04d.png'%fr;t=time.time();bpy.ops.render.render(write_still=True);print('BLUR_PREVIEW',fr,time.time()-t,flush=True);gc.collect()
