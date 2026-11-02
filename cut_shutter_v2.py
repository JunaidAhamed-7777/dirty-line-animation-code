import bpy,math
from camera_v2 import CUTS
def apply_cut_shutter():
 s=bpy.context.scene;affected=sorted({f for t in CUTS for f in (math.ceil(t*24),math.ceil(t*24)+1)});values={}
 for fr in range(1,537):s.frame_set(fr);values[fr]=s.render.motion_blur_shutter
 for fr in range(1,537):
  s.render.motion_blur_shutter=0.0 if fr in affected else values[fr];s.render.keyframe_insert('motion_blur_shutter',frame=fr)
 for fc in s.animation_data.action.fcurves:
  if fc.data_path=='render.motion_blur_shutter':
   for kp in fc.keyframe_points:kp.interpolation='CONSTANT'
 return affected
