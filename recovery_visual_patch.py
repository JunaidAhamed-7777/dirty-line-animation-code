"""Targeted recovery parity fixes, based on surviving approved native frames."""
import bpy,sys,os,math
from mathutils import Vector
R=os.path.dirname(os.path.abspath(__file__));sys.path.insert(0,R)
from timeline import main_y
from camera_v2 import camera_pose
for o in bpy.data.objects:
 if o.type=='LIGHT' and o.name.startswith('Track floodlight'):
  target=Vector((o.location.x,main_y(o.location.x),0));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
for o in bpy.data.objects:
 if o.name.startswith('Layered eroded ridgeline'):o.location.y+=40;o.scale.z*=.65
# Restore forest density over the longer V2 course, keeping original mesh variants.
col=bpy.data.collections.get('Distant irregular treeline')
if col:
 for o in list(col.objects):bpy.data.objects.remove(o,do_unlink=True)
 bpy.data.collections.remove(col)
from distant_treeline import build_distant_treeline
build_distant_treeline(count=500)
# The distant moon is self-visible, not dependent on ground light attenuation.
moon=bpy.data.objects.get('V2 Sky Grass | HALF MOON');m=moon.data.materials[0];n=m.node_tree.nodes;l=m.node_tree.links;n.clear()
out=n.new('ShaderNodeOutputMaterial');em=n.new('ShaderNodeEmission');em.inputs['Color'].default_value=(.40,.45,.50,1);l.new(em.outputs[0],out.inputs['Surface'])
pos,target,lens=camera_pose(103/24);view=(Vector(pos)-moon.location).normalized();right=(Vector(target)-Vector(pos)).normalized().cross(Vector((0,0,1))).normalized();sun=-right
geo=n.new('ShaderNodeNewGeometry');dot=n.new('ShaderNodeVectorMath');dot.operation='DOT_PRODUCT';dot.inputs[1].default_value=sun;l.new(geo.outputs['Normal'],dot.inputs[0]);ramp=n.new('ShaderNodeMapRange');ramp.clamp=True;ramp.inputs['From Min'].default_value=-.03;ramp.inputs['From Max'].default_value=.6;ramp.inputs['To Min'].default_value=.01;ramp.inputs['To Max'].default_value=.7;l.new(dot.outputs['Value'],ramp.inputs['Value']);l.new(ramp.outputs['Result'],em.inputs['Strength'])
# Keep a huge wake, but let the rear wheel and livery remain readable.
for m in bpy.data.materials:
 if m.name.startswith('V2 recovered dust |') and 'finish tire' not in m.name and m.node_tree and m.node_tree.animation_data:
  for fc in m.node_tree.animation_data.action.fcurves:
   if 'Dust envelope' in fc.data_path:
    for k in fc.keyframe_points:k.co.y*=.65;k.handle_left.y*=.65;k.handle_right.y*=.65
s=bpy.context.scene;s['Recovery visual revision']='road-centered pools, half-moon visibility, lower distant ridges, denser forest, readable large dust wake'
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE.blend',compress=True)
