import bpy,os,json,hashlib
R=os.path.dirname(os.path.abspath(__file__));s=bpy.context.scene
# Snapshot all object and camera animation; not a single transform or time key is changed.
def fingerprint():
 rows=[]
 for action in bpy.data.actions:
  for fc in action.fcurves:
   if fc.data_path=='render.motion_blur_shutter':continue
   rows.append((action.name,fc.data_path,fc.array_index,[(tuple(k.co),tuple(k.handle_left),tuple(k.handle_right),k.interpolation) for k in fc.keyframe_points]))
 return hashlib.sha256(repr(rows).encode()).hexdigest()
before=fingerprint();original={}
shutter=next(fc for fc in s.animation_data.action.fcurves if fc.data_path=='render.motion_blur_shutter')
for fr in range(1,537):original[fr]=shutter.evaluate(fr)
for fr in range(463,480):
 if fr<467:v=.5+.4*(fr-463)/4
 elif fr<=475:v=.9
 else:v=.9-.4*(fr-475)/4
 s.render.motion_blur_shutter=v;s.render.keyframe_insert('motion_blur_shutter',frame=fr)
for fc in s.animation_data.action.fcurves:
 if fc.data_path=='render.motion_blur_shutter':
  for k in fc.keyframe_points:
   if 463<=k.co.x<=479:k.interpolation='CONSTANT'
after=fingerprint();assert before==after
new={}
for fr in range(1,537):
 new[fr]=shutter.evaluate(fr)
 if not 463<=fr<=479:assert abs(new[fr]-original[fr])<1e-7,(fr,new[fr],original[fr])
json.dump({'only_shutter_changed':True,'non_shutter_animation_sha256':before,'affected_frames':[463,479],'original':original,'patched':new},open(R+'/BLUR_ONLY_PATCH_REPORT.json','w'),indent=2)
s.frame_set(468);bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE_FINISH_BLUR_ONLY.blend',compress=True)
