import bpy,math
from mathutils import Vector
from timeline import hero_y,derivative,ramp_height
from car_model import mesh,material
def build_ramp_earthworks():
 # Copy the scanned opaque gravel, never the feathered ribbon material.
 source=bpy.data.materials.get('Compacted ochre gravel')
 if source and source.use_nodes:
  mat=source.copy();mat.name='Compacted ramp earth shoulders'
  nt=mat.node_tree
  bs=next((node for node in nt.nodes if node.type=='BSDF_PRINCIPLED'),None)
  out=next((node for node in nt.nodes if node.type=='OUTPUT_MATERIAL'),None)
  if bs:
   for link in list(bs.inputs['Alpha'].links):nt.links.remove(link)
   bs.inputs['Alpha'].default_value=1.0
   # Direct opaque surface avoids inherited boundary/ribbon transparent mixing.
   if out:nt.links.new(bs.outputs['BSDF'],out.inputs['Surface'])
 else:
  mat=material('Compacted ramp earth shoulders',(.18,.105,.048),0,.94)
 for side in (-1,1):
  v=[];f=[]
  for i in range(89):
   x=88+i*.5;y=hero_y(x);dy=derivative(hero_y,x);n=Vector((-dy,1)).normalized();h=ramp_height(x)
   for w,z in [(3.35,h-.005),(4.4,max(.025,h*.5)),(6.2,.025)]:
    q=Vector((x,y))+n*w*side;v.append((q.x,q.y,z))
  for i in range(88):
   for j in range(2):k=i*3+j;f.append((k,k+1,k+4,k+3))
  mesh('Graded ramp shoulder',v,f,mat)
