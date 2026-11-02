import bpy
from mathutils import Vector
from timeline import pose,ease
def add_fight_fill():
 d=bpy.data.lights.new('Fight soft track fill','AREA');d.energy=1800;d.color=(.55,.7,1);d.shape='DISK';d.size=13;o=bpy.data.objects.new('Fight soft track fill',d);bpy.context.collection.objects.link(o)
 for fr in range(1,537):
  t=(fr-1)/24;mid=(Vector(pose(t)['position'])+Vector(pose(t,False)['position']))*.5;o.location=mid+Vector((-2,-7,8));o.rotation_euler=(mid-o.location).to_track_quat('-Z','Y').to_euler();o.keyframe_insert('location',frame=fr);o.keyframe_insert('rotation_euler',frame=fr);d.energy=1800*ease((t-15.2)/.6)*(1-ease((t-19)/.5));d.keyframe_insert('energy',frame=fr)
