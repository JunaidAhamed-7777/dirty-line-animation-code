# Historical authored revision; duplicate shared helpers and all assets are omitted.
import bpy,os,sys,json,math
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,R)
from timeline import pose,camera_pose
from atmosphere_grade import configure_atmosphere_grade
SCALES={"AUDI":4.24/4.4,"GT40":4.1783/4.09}
s=bpy.context.scene;s.unit_settings.system='METRIC';s.unit_settings.length_unit='METERS';s.unit_settings.scale_length=1
for prefix,k in SCALES.items():bpy.data.objects[prefix+'_ROOT'].scale=(k,k,k)
cam=s.camera;report=json.load(open(R+'/cars_prepared_report.json'))
for fr in range(1,537):
 t=(fr-1)/24
 for prefix,hero,key in [('AUDI',True,'Audi'),('GT40',False,'GT40')]:
  p=pose(t,hero);root=bpy.data.objects[prefix+'_ROOT'];body=bpy.data.objects[prefix+'_BODY'];root.location=p['position'];root.rotation_euler=(0,p['root_pitch'],p['yaw']);body.location.z=-p['compression']/SCALES[prefix];body.rotation_euler=(p['roll'],p['pitch'],0)
  root.keyframe_insert('location',frame=fr);root.keyframe_insert('rotation_euler',frame=fr);body.keyframe_insert('location',frame=fr);body.keyframe_insert('rotation_euler',frame=fr)
  for pos,w in report[key]['wheels'].items():
   steer=bpy.data.objects[w['steer']];spin=bpy.data.objects[w['spin']];steer.rotation_euler.z=p['steer'] if pos.startswith('F') else 0;spin.rotation_euler.y=p['distance']/(w['radius']*SCALES[prefix]);steer.keyframe_insert('rotation_euler',frame=fr);spin.keyframe_insert('rotation_euler',frame=fr)
 p,target,lens=camera_pose(t);cam.location=p;cam.rotation_euler=(target-p).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.data.dof.focus_distance=(target-p).length
 for prop in ['location','rotation_euler']:cam.keyframe_insert(prop,frame=fr)
 cam.data.keyframe_insert('lens',frame=fr);cam.data.dof.keyframe_insert('focus_distance',frame=fr)
cut_prev={math.ceil(t*24) for t in [.93,2.79,4.65,8.37,12.555,17.67]}
for db in [cam,cam.data]:
 for fc in db.animation_data.action.fcurves:
  for kp in fc.keyframe_points:kp.interpolation='CONSTANT' if int(kp.co.x) in cut_prev else 'LINEAR'
s.frame_set(150);bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE.blend',compress=True)
s.render.resolution_x=1280;s.render.resolution_y=720;s.render.resolution_percentage=50;s.cycles.samples=24
for fr in [292,296]:
 s.frame_set(fr);s.render.filepath=R+'/previews/grounded-contact-%04d.png'%fr;bpy.ops.render.render(write_still=True)
