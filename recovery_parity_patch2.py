import bpy,sys,os,math
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,R)
from timeline import pose,main_y
# Two mast bases recovered by back-projecting surviving approved frame56.
# Remaining positions follow retained original course placement at V2 scale.
positions=[(-210,-32),(-176,16),(-136,-56),(-60,104),(60,104),(130,-64),(250,-70)]
def ordered(prefix,typ=None):
 return sorted([o for o in bpy.data.objects if o.name.startswith(prefix) and (not typ or o.type==typ)],key=lambda o:int(o.name.rsplit('.',1)[-1]) if '.' in o.name else 0)
masts=ordered('Floodlight mast');gantries=ordered('Light gantry');lights=ordered('Track floodlight','LIGHT')
for i,(x,y) in enumerate(positions):
 if i<len(masts):masts[i].location.x=x;masts[i].location.y=y
 if i<len(gantries):gantries[i].location.x=x;gantries[i].location.y=y
 for j,dx in enumerate((-1,1)):
  o=lights[2*i+j];o.location=(x+dx,y,10.6);o.rotation_euler=(Vector((x,main_y(x),0))-o.location).to_track_quat('-Z','Y').to_euler()
for label,extra in [('rear wheel roost',3),('lagged wake',7),('fine lingering cloud',6)]:
 o=next(o for o in bpy.data.objects if o.name=='V2 recovered dust | '+label)
 for fr in range(1,537):
  bpy.context.scene.frame_set(fr);p=pose((fr-1)/24,True);f=Vector((math.cos(p['yaw']),math.sin(p['yaw']),0));o.location-=f*extra;o.keyframe_insert('location',frame=fr)
for o in bpy.data.objects:
 if o.name.startswith('V2 recovered dust |') and o.animation_data:
  for fc in o.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
bpy.context.scene.frame_set(104);bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE.blend',compress=True)
