"""Reconstructed brief skidplate contact sparks; no persistent flame jets."""
import bpy,math,random
from mathutils import Vector
from timeline import pose
from car_model import mesh
def add_landing_sparks():
 rng=random.Random(29317);mat=bpy.data.materials.new('V2 hot skidplate sparks');mat.use_nodes=True;nt=mat.node_tree;nt.nodes.clear();e=nt.nodes.new('ShaderNodeEmission');e.inputs[0].default_value=(1,.62,.18,1);e.inputs[1].default_value=12;out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(e.outputs[0],out.inputs['Surface'])
 for j in range(70):
  birth=12.09+rng.uniform(0,.07);life=rng.uniform(.14,.28);p=pose(birth);yaw=p.get('path_yaw',p['yaw']);f=Vector((math.cos(yaw),math.sin(yaw),0));n=Vector((-f.y,f.x,0));origin=Vector(p['position'])-f*.7+n*rng.uniform(-.5,.5);origin.z=.09
  v=f*p['speed']*rng.uniform(.45,.8)+n*rng.uniform(-4,4)+Vector((0,0,rng.uniform(.6,3.4)))
  ob=mesh('V2 skidplate spark',[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,1),(0,0,-1)],[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)],mat);length=rng.uniform(.018,.05)
  for fr in range(1,537):
   t=(fr-1)/24;age=t-birth;alive=0<=age<=life
   if alive:
    ob.location=origin+v*age+Vector((0,0,-4.905*age*age));vel=v+Vector((0,0,-9.81*age));ob.rotation_euler=vel.to_track_quat('X','Z').to_euler();ob.scale=(length,.0025,.0025)
   else:ob.scale=(0,0,0)
   ob.keyframe_insert('location',frame=fr);ob.keyframe_insert('rotation_euler',frame=fr);ob.keyframe_insert('scale',frame=fr)
