# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""DIRTY LINE: supplied classic cars, original course/camera/animation, user music.
No model scripts are executed; source collections are appended as data only.
"""
import bpy,sys,os,math,json
from mathutils import Vector,Matrix
ROOT=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,ROOT)
from course import build_course
from track_details import build_track_details
from roadside_detail import build_roadside_detail,build_gravel_verge
from distant_treeline import build_distant_treeline
from lighting import configure_scene
from effects import build_effects
from timeline import pose,camera_pose,ease
from car_model import material
from lamp_glass import refine_lamp_glass
from fix_actual_rims import fix_actual_rims
from atmosphere_grade import configure_atmosphere_grade
SCALES={"AUDI":4.24/4.4,"GT40":4.1783/4.09}
bpy.ops.wm.read_factory_settings(use_empty=True)
# Append actual user-supplied meshes, rebuilt in Blender4.3 with reusable wheel rigs.
with bpy.data.libraries.load(ROOT+'/CARS_CLOUD.blend',link=False) as (src,dst):dst.collections=['CAR_AUDI','CAR_GT40']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
with bpy.data.libraries.load(ROOT+'/driver_work/driver_prepared.blend',link=False) as (src,dst):dst.collections=['DRIVER_AUDI']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
driver=bpy.data.objects['DRIVER_AUDI_ROOT'];driver.parent=bpy.data.objects['AUDI_BODY'];driver.matrix_parent_inverse=Matrix.Identity(4);driver.location=(0,0,0);driver.rotation_euler=(0,0,0);driver.scale=(1,1,1)
with bpy.data.libraries.load(ROOT+'/driver_work/driver_gt40_prepared.blend',link=False) as (src,dst):dst.collections=['DRIVER_GT40']
for c in dst.collections:bpy.context.scene.collection.children.link(c)
driverg=bpy.data.objects['DRIVER_GT40_ROOT'];driverg.parent=bpy.data.objects['GT40_BODY'];driverg.matrix_parent_inverse=Matrix.Identity(4);driverg.location=(0,0,0);driverg.rotation_euler=(0,0,0);driverg.scale=(1,1,1)
# Film-ready glass and paint: preserve livery textures and actual body geometry.
for m in bpy.data.materials:
 if not m.use_nodes:continue
 p=next((n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
 if not p:continue
 n=m.name.lower()
 if 'windowglass' in n or ('gt40' in n and 'glass' in n):
  p.inputs['Roughness'].default_value=.028;p.inputs['Transmission Weight'].default_value=1;p.inputs['Base Color'].default_value=(.8,.9,1,1);p.inputs['Metallic'].default_value=0
 if m.name in ['GT40_Headlight3','GT40_Headlight1']:
  p.inputs['Transmission Weight'].default_value=1;p.inputs['Roughness'].default_value=.025;p.inputs['Metallic'].default_value=0;p.inputs['Base Color'].default_value=(.9,.95,1,1)
 if m.name in ['GT40_Headlight4','GT40_Headlight5']:
  p.inputs['Emission Color'].default_value=(.7,.85,1,1);p.inputs['Emission Strength'].default_value=2
 if 'paintblack' in n:
  p.inputs['Base Color'].default_value=(.045,.10,.15,1);p.inputs['Roughness'].default_value=.19;p.inputs['Coat Weight'].default_value=.8
 if 'carpaint' in n:
  p.inputs['Roughness'].default_value=.21;p.inputs['Coat Weight'].default_value=.85
  # Local-space low-body dirt accumulates during the gravel sequence, never floats in world space.
  nt=m.node_tree;tc=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(tc.outputs['Object'],sep.inputs[0]);height=nt.nodes.new('ShaderNodeMapRange');height.inputs['From Min'].default_value=.2;height.inputs['From Max'].default_value=.72;height.inputs['To Min'].default_value=.65;height.inputs['To Max'].default_value=0;height.clamp=True;nt.links.new(sep.outputs['Z'],height.inputs['Value'])
  noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=18;noise.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['Object'],noise.inputs['Vector']);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';nt.links.new(height.outputs['Result'],mul.inputs[0]);nt.links.new(noise.outputs['Fac'],mul.inputs[1]);progress=nt.nodes.new('ShaderNodeValue');progress.name='Mud accumulation';progress.outputs[0].default_value=0;progress.outputs[0].keyframe_insert('default_value',frame=112);progress.outputs[0].default_value=1;progress.outputs[0].keyframe_insert('default_value',frame=230)
  mul2=nt.nodes.new('ShaderNodeMath');mul2.operation='MULTIPLY';nt.links.new(mul.outputs[0],mul2.inputs[0]);nt.links.new(progress.outputs[0],mul2.inputs[1]);mix=nt.nodes.new('ShaderNodeMixRGB');mix.blend_type='MIX';mix.inputs[2].default_value=(.065,.04,.018,1)
  if p.inputs['Base Color'].links:nt.links.new(p.inputs['Base Color'].links[0].from_socket,mix.inputs[1])
  else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
  nt.links.new(mul2.outputs[0],mix.inputs[0]);nt.links.new(mix.outputs[0],p.inputs['Base Color'])
for prefix,k in SCALES.items():bpy.data.objects[prefix+'_ROOT'].scale=(k,k,k)
fix_actual_rims()
# Functioning lights on the actual front lamp lens faces, not invisible illumination.
headmat=material('Audi warm halogen lenses',(1,.68,.28),.1,.15,1.7)
for name in ['AUDI_Object_19','AUDI_Object_20']:
 o=bpy.data.objects.get(name)
 if o:
  idx=len(o.data.materials);o.data.materials.append(headmat)
  for poly in o.data.polygons:
   if poly.center.x>1.9 and poly.normal.x>.22:poly.material_index=idx
for prefix,col,energy in [('AUDI',(1,.72,.36),1200),('GT40',(.65,.82,1),1000)]:
 root=bpy.data.objects[prefix+'_ROOT']
 for sy in (-1,1):
  d=bpy.data.lights.new(prefix+' working headlight','SPOT');d.energy=energy;d.color=col;d.spot_size=.7;d.spot_blend=.65;d.shadow_soft_size=.06
  o=bpy.data.objects.new(prefix+' working headlight',d);bpy.context.collection.objects.link(o);o.parent=root;o.location=(2.25 if prefix=='AUDI' else 2.13,sy*.58,.63 if prefix=='AUDI' else .47);o.rotation_euler=Vector((1,0,-.08)).to_track_quat('-Z','Y').to_euler()
refine_lamp_glass()
# Dashboard fill makes supplied helmet subtly visible through the glass, not a bright mannequin.
d=bpy.data.lights.new('Audi instrument glow','POINT');d.energy=1.6;d.color=(.25,.48,.7);d.shadow_soft_size=.15;o=bpy.data.objects.new('Audi instrument glow',d);bpy.context.collection.objects.link(o);o.parent=bpy.data.objects['AUDI_BODY'];o.location=(.4,.28,.85)
build_course();build_track_details();build_roadside_detail();build_gravel_verge();build_distant_treeline();s=configure_scene(1280,720,24)
s.render.engine='CYCLES';s.cycles.device='CPU';s.cycles.samples=48;s.cycles.use_denoising=True;s.cycles.use_adaptive_sampling=True;s.cycles.adaptive_threshold=.05;s.cycles.max_bounces=6;s.cycles.diffuse_bounces=2;s.cycles.glossy_bounces=3;s.cycles.transmission_bounces=4;s.cycles.volume_bounces=1;s.cycles.transparent_max_bounces=64;s.cycles.sample_clamp_indirect=3
configure_atmosphere_grade();s.unit_settings.system='METRIC';s.unit_settings.length_unit='METERS';s.unit_settings.scale_length=1
bpy.ops.object.camera_add();cam=bpy.context.object;cam.name='DIRTY LINE | authored camera';s.camera=cam;cam.data.clip_end=1000;cam.data.lens=43;cam.data.dof.use_dof=True;cam.data.dof.aperture_fstop=5.6
s.render.use_motion_blur=True;s.render.motion_blur_shutter=.3;s.render.motion_blur_position='START'
for f,shutter in [(1,.3),(462,.3),(467,.08),(475,.08),(480,.3),(536,.3)]:
 s.render.motion_blur_shutter=shutter;s.render.keyframe_insert('motion_blur_shutter',frame=f)
# Physical rigs use roots for road contact, BODY for suspension, wheel angle for distance.
report=json.load(open(ROOT+'/cars_prepared_report.json'))
for fr in range(1,537):
 t=(fr-1)/24
 for prefix,hero,key in [('AUDI',True,'Audi'),('GT40',False,'GT40')]:
  p=pose(t,hero);root=bpy.data.objects[prefix+'_ROOT'];body=bpy.data.objects[prefix+'_BODY'];root.location=p['position'];root.rotation_euler=(0,p['root_pitch'],p['yaw']);body.location.z=-p['compression']/SCALES[prefix];body.rotation_euler=(p['roll'],p['pitch'],0)
  root.keyframe_insert('location',frame=fr);root.keyframe_insert('rotation_euler',frame=fr);body.keyframe_insert('location',frame=fr);body.keyframe_insert('rotation_euler',frame=fr)
  for pos,w in report[key]['wheels'].items():
   steer=bpy.data.objects[w['steer']];spin=bpy.data.objects[w['spin']];steer.rotation_euler.z=p['steer'] if pos.startswith('F') else 0;spin.rotation_euler.y=p['distance']/(w['radius']*SCALES[prefix]);steer.keyframe_insert('rotation_euler',frame=fr);spin.keyframe_insert('rotation_euler',frame=fr)
 pos,target,lens=camera_pose(t);cam.location=pos;cam.rotation_euler=(target-pos).to_track_quat('-Z','Y').to_euler();cam.data.lens=lens;cam.keyframe_insert('location',frame=fr);cam.keyframe_insert('rotation_euler',frame=fr);cam.data.keyframe_insert('lens',frame=fr);cam.data.dof.focus_distance=(target-pos).length;cam.data.dof.keyframe_insert('focus_distance',frame=fr)

# Deterministic effects can be skipped for quick geometry/camera inspection.
if '--no-fx' not in sys.argv:build_effects(frames=536)
for ob in bpy.data.objects:
 if ob.animation_data and ob.animation_data.action:
  for fc in ob.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='LINEAR'
# Hold camera transform up to each cut; START shutter never samples the preceding shot.
cut_prev={math.ceil(t*24) for t in [.93,2.79,4.65,8.37,12.555,17.67]}
for datablock in [cam,cam.data]:
 if datablock.animation_data and datablock.animation_data.action:
  for fc in datablock.animation_data.action.fcurves:
   for kp in fc.keyframe_points:kp.interpolation='CONSTANT' if int(kp.co.x) in cut_prev else 'LINEAR'
s['Title']='DIRTY LINE';s['Creator']='Junaid Ahamed';s['Source assets']='User supplied GT40.blend, audi_quattro_race_car.glb, driver_80.glb. Original course, camera, animation and effects. AI-assisted production under human oversight.';s['Music']='User supplied Drowning.mp3; confirmed rights to parent. Edited cue22.32s.';s['Submission status']='Offline production only; not registered or submitted.'
s.render.filepath=ROOT+'/renders/frame_';s.frame_set(150)
for screen in bpy.data.screens:
 for area in screen.areas:
  if area.type=='VIEW_3D':area.spaces.active.region_3d.view_perspective='CAMERA';area.spaces.active.clip_end=1000
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=ROOT+'/DIRTY_LINE.blend',compress=True)
print('FILM_SCENE_READY',len(bpy.data.objects))
if '--test' in sys.argv:
 s.render.resolution_percentage=50;s.cycles.samples=24
 for frame in ([20,470] if '--quick' in sys.argv else [30,150,276,320,470]):
  s.frame_set(frame);s.render.filepath=ROOT+'/previews/film-test-%04d.png'%frame;bpy.ops.render.render(write_still=True)
