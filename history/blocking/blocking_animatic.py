# Historical authored revision; duplicate shared helpers and all assets are omitted.
import bpy,sys,os,math
from mathutils import Vector
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
from course import build_course
from car_model import material,cube
from timeline import pose,camera_pose
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);build_course()
s=bpy.context.scene;s.render.engine='BLENDER_WORKBENCH';s.render.resolution_x=640;s.render.resolution_y=360;s.render.resolution_percentage=100;s.render.fps=24;s.frame_start=1;s.frame_end=480;s.frame_step=4
s.display.shading.light='STUDIO';s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=True;s.display.shading.cavity_type='BOTH';s.display.shading.background_type='WORLD';s.world.color=(.08,.08,.08)
proxies=[]
for name,col in [('HERO PROXY - NOT FINAL CAR',(.9,.22,.03)),('RIVAL PROXY - NOT FINAL CAR',(.65,.7,.75))]:
 o=cube(name,(0,0,.5),(4.2,1.8,.9),material(name,col));proxies.append(o)
bpy.ops.object.camera_add();cam=bpy.context.object;s.camera=cam;cam.data.clip_end=1000
for f in range(1,481):
 t=(f-1)/24
 for i,o in enumerate(proxies):
  p=pose(t,i==0);o.location=Vector(p['position'])+Vector((0,0,.5));o.rotation_euler=(p['roll'],p['pitch'],p['yaw']);o.keyframe_insert('location',frame=f);o.keyframe_insert('rotation_euler',frame=f)
 pos,target,lens=camera_pose(t);cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.keyframe_insert('location',frame=f);cam.keyframe_insert('rotation_euler',frame=f);cam.data.keyframe_insert('lens',frame=f)
s.render.image_settings.file_format='PNG';s.render.filepath=ROOT+'/animatic/frame_';bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/BLOCKING_ONLY.blend');bpy.ops.render.render(animation=True)
