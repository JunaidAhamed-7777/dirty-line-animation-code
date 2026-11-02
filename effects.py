"""Deterministic original gravel and water-mist effects, no fluid bake required."""
import bpy,math,random
from mathutils import Vector
from timeline import pose,camera_pose
from car_model import material,mesh

def mist_material(name,color):
 m=material(name,color,0,1);m.surface_render_method='DITHERED';nt=m.node_tree;p=nt.nodes.get('Principled BSDF');p.inputs['Alpha'].default_value=.1
 tc=nt.nodes.new('ShaderNodeTexCoord');dist=nt.nodes.new('ShaderNodeVectorMath');dist.operation='DISTANCE';dist.inputs[1].default_value=(.5,.5,0);nt.links.new(tc.outputs['UV'],dist.inputs[0])
 ramp=nt.nodes.new('ShaderNodeMapRange');ramp.inputs['From Min'].default_value=.05;ramp.inputs['From Max'].default_value=.5;ramp.inputs['To Min'].default_value=1;ramp.inputs['To Max'].default_value=0;ramp.clamp=True;nt.links.new(dist.outputs['Value'],ramp.inputs['Value'])
 no=nt.nodes.new('ShaderNodeTexNoise');no.inputs['Scale'].default_value=6;no.inputs['Detail'].default_value=3;nt.links.new(tc.outputs['UV'],no.inputs['Vector'])
 mult=nt.nodes.new('ShaderNodeMath');mult.operation='MULTIPLY';nt.links.new(ramp.outputs['Result'],mult.inputs[0]);nt.links.new(no.outputs['Fac'],mult.inputs[1])
 info=nt.nodes.new('ShaderNodeObjectInfo');alpha=nt.nodes.new('ShaderNodeMath');alpha.operation='MULTIPLY';nt.links.new(mult.outputs[0],alpha.inputs[0]);nt.links.new(info.outputs['Alpha'],alpha.inputs[1]);nt.links.new(alpha.outputs[0],p.inputs['Alpha']);return m

def sprite(name,mat):
 o=mesh(name,[(-1,-1,0),(1,-1,0),(1,1,0),(-1,1,0)],[(0,1,2,3)],mat);uv=o.data.uv_layers.new(name='UVMap')
 for loop,co in zip(o.data.loops,[(0,0),(1,0),(1,1),(0,1)]):uv.data[loop.index].uv=co
 return o

def build_effects(fps=24,frames=536):
 rng=random.Random(902);dust=mist_material('Fine gravel dust',(.23,.18,.12));spray=mist_material('Backlit water mist',(.45,.58,.66));stone=material('Flying grit',(.13,.10,.065),0,.85)
 particles=[]
 # Particles use a fixed birth time, so every render is reproducible.
 for kind,count,t0,t1 in [('dust',280,4.65,10.95),('spray',180,12.09,20.6),('opening',130,0,3.1),('grit',90,4.8,10.8)]:
  for i in range(count):
   born=t0+(t1-t0)*i/count+rng.uniform(-.04,.04);p=pose(born,not(kind=='opening' and i%2));yaw=p['yaw'];fwd=Vector((math.cos(yaw),math.sin(yaw),0));side=Vector((-fwd.y,fwd.x,0));sgn=-1 if i%2 else 1
   origin=Vector(p['position'])-fwd*1.7+side*sgn*.75+Vector((0,0,.08));vel=fwd*(p['speed']*.22)+side*sgn*rng.uniform(.5,2.8)+Vector((0,0,rng.uniform(.5,2.2)))
   life=rng.uniform(.6,1.3) if kind!='grit' else rng.uniform(.25,.65)
   if kind=='grit':
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=rng.uniform(.018,.045));o=bpy.context.object;o.name='Gravel chip';o.data.materials.append(stone)
   else:o=sprite('Dust wisp' if kind=='dust' else 'Wheel spray wisp',dust if kind=='dust' else spray)
   particles.append((o,kind,born,life,origin,vel,rng.uniform(.15,.5)))
 for fr in range(1,frames+1):
  t=(fr-1)/fps;cam,_,_=camera_pose(t)
  for o,kind,born,life,origin,vel,size in particles:
   age=t-born;alive=0<=age<=life
   if not alive and fr not in {1,frames,max(1,int(born*fps)),min(frames,int((born+life)*fps)+2)}:continue
   if alive:
    gravity=9.81 if kind=='grit' else .5;pos=origin+vel*age+Vector((0,0,-.5*gravity*age*age));pos.z=max(.055,pos.z);o.location=pos
    if kind=='grit':o.scale=(1,1,1);o.rotation_euler=(age*14,age*9,age*17)
    else:
     grow=size+age*.75;o.scale=(grow*1.5,grow,1);o.rotation_euler=(cam-pos).to_track_quat('Z','Y').to_euler();o.color=(1,1,1,(.65 if kind=='dust' else .30)*math.sin(math.pi*age/life))
   else:o.scale=(0,0,0);o.color=(1,1,1,0)
   for prop in ('location','scale','rotation_euler','color'):o.keyframe_insert(prop,frame=fr)
 return particles
