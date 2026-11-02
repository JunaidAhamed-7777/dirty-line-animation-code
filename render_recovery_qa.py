import bpy,os,sys
R=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene;s.render.engine='CYCLES';s.cycles.device='CPU';s.render.use_persistent_data=False;s.render.threads_mode='FIXED';s.render.threads=8;s.cycles.samples=24;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.1;s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=50
os.makedirs(R+'/previews',exist_ok=True)
frames=[int(x) for x in sys.argv[sys.argv.index('--')+1:]] if '--' in sys.argv else [104]
for fr in frames:
 s.frame_set(fr);s.render.filepath=R+'/previews/recovered-%04d.png'%fr;bpy.ops.render.render(write_still=True);print('RECOVERY_QA_FRAME',fr,flush=True)
