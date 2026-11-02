"""Motivated closed-course architecture and surface details; original geometry."""
import bpy,math,random
from mathutils import Vector
from car_model import material,cube,cylinder,mesh
from course import ROAD

def line(name,points,radius,mat):
 cu=bpy.data.curves.new(name,'CURVE');cu.dimensions='3D';cu.resolution_u=1;cu.bevel_depth=radius;cu.bevel_resolution=2;sp=cu.splines.new('POLY');sp.points.add(len(points)-1)
 for p,co in zip(sp.points,points):p.co=(*co,1)
 o=bpy.data.objects.new(name,cu);bpy.context.collection.objects.link(o);o.data.materials.append(mat);return o

def build_track_details():
 steel=material('Weathered safety steel',(.10,.13,.16),.75,.36);concrete=material('Concrete wall',(.11,.13,.14),.05,.8);paint=material('Worn enamel',(.44,.48,.46),.25,.5);dark=material('Drain iron',(.009,.013,.017),.7,.38);window=material('Warm operations windows',(.6,.27,.055),.1,.22,2);red=material('Reflective warning red',(.55,.025,.008),.2,.32);white=material('Reflective white panels',(.7,.76,.75),.15,.3);lamp=material('Lamp face',(.65,.8,1),0,.2,5)
 # Continuous outer Armco follows real road geometry, with regularly spaced support posts.
 outer=[]
 for i,p in enumerate(ROAD):
  tan=(ROAD[min(i+1,len(ROAD)-1)]-ROAD[max(i-1,0)]).normalized();q=p+Vector((-tan.y,tan.x))*5.2;outer.append((q.x,q.y,.58))
 line('Armco upper rail',[(x,y,z+.2) for x,y,z in outer],.065,steel);line('Armco lower rail',[(x,y,z-.12) for x,y,z in outer],.06,steel)
 for i in range(0,len(outer),5):
  x,y,z=outer[i];cube('Armco support',(x,y,.41),(.12,.12,.82),steel,None,.01)
 # Irregular shallow puddles catch motivated light, avoiding uniformly plastic asphalt.
 rng=random.Random(81);water=material('Thin standing water',(.012,.02,.028),.25,.055)
 for k in range(0):
  i=rng.randrange(3,len(ROAD)-3);p=ROAD[i];tan=(ROAD[i+1]-ROAD[i-1]).normalized();nor=Vector((-tan.y,tan.x));center=p+nor*rng.choice([-1,1])*rng.uniform(1.8,3.0);length=rng.uniform(.7,2.8);width=rng.uniform(.18,.65);verts=[]
  for j in range(18):
   a=2*math.pi*j/18;r=rng.uniform(.8,1.1);q=center+tan*(length*math.cos(a)*r)+nor*(width*math.sin(a)*r);verts.append((q.x,q.y,.035))
  mesh('Shallow road puddle',verts,[tuple(range(18))],water)
 # Operations building establishes a real venue beyond the final straight.
 cube('Pit operations building',(104,9,2.2),(25,7,4.4),concrete,None,.07)
 cube('Overhanging pit roof',(104,8.8,4.55),(26,8,.25),steel,None,.04)
 for x in range(94,116,3):
  cube('Lit pit window',(x,5.48,2.9),(2.1,.025,1.05),window,None,.015)
  cube('Pit garage door',(x,5.43,1.03),(2.15,.04,1.9),dark,None,.01)
  for z in (.3,.6,.9,1.2,1.5,1.8):cube('Garage door seam',(x,5.395,z),(2.1,.015,.012),steel,None,0)
 cube('Timing tower base',(84,12,4),(5,5,8),concrete,None,.06)
 cube('Timing room',(84,12,8.7),(6,6,1.6),dark,None,.04)
 for side in (-1,1):cube('Timing room glazing',(84,12+side*3.01,8.7),(5.5,.025,1.15),window,None,.02)
 cube('Timing room roof',(84,12,9.65),(6.5,6.5,.25),steel,None,.03)
 # Small overhead finish gantry; deliberately unbranded.
 for y in (-28,-16):cube('Finish gantry upright',(123,y,3.1),(.24,.24,6.2),steel,None,.02)
 for z in (5.5,6.1):cube('Finish gantry beam',(123,-22,z),(.25,12.3,.15),steel,None,.02)
 for j in range(12):
  y=-27.5+j;o=cube('Finish truss diagonal',(123,y,5.8),(.09,1.12,.09),steel,None,.008);o.rotation_euler.x=(1 if j%2 else -1)*.52
 cube('Finish sign board',(123,-22,5.8),(.08,4,.65),dark,None,.02)
 # Two modest gantry lamps light the line, not a flat global camera key.
 for y in (-25,-19):
  cube('Gantry luminaire',(123,y,5.34),(.4,.65,.1),lamp,None,.015)
  d=bpy.data.lights.new('Finish light','AREA');d.energy=1000;d.color=(.72,.82,1);d.size=2;o=bpy.data.objects.new('Finish light',d);bpy.context.collection.objects.link(o);o.location=(123,y,5.2)
 # Drainage channels and actual grate bars beside the wet merge.
 for x,y in [(48,-3.4),(54,-8.1),(100,-25.3),(109,-25.7),(119,-25.7)]:
  cube('Drain recess',(x,y,.035),(1.6,.38,.025),dark,None,.005)
  for k in range(12):cube('Drain grate bar',(x-.72+k*.13,y,.055),(.035,.36,.035),steel,None,.005)
 # Reflection-producing pits light from the building, with warm/cool separation.
 for x in (96,105,114):
  d=bpy.data.lights.new('Pit wall pool','AREA');d.energy=350;d.color=(1,.55,.22);d.shape='DISK';d.size=3;o=bpy.data.objects.new('Pit wall pool',d);bpy.context.collection.objects.link(o);o.location=(x,4.9,3.8);o.rotation_euler=(Vector((x,-5,0))-o.location).to_track_quat('-Z','Y').to_euler()
 # Chevron board beyond the main bend provides direction rather than decorative clutter.
 for x,y in [(-35,30),(35,30)]:
  cube('Chevron backing',(x,y,1.4),(.1,2,1),dark,None,.02)
  for k in (-.5,.5):
   ob=cube('Chevron stripe',(x-.06,y+k,1.4),(.025,.65,.16),white,None,.01);ob.rotation_euler.x=-.65 if k<0 else .65
