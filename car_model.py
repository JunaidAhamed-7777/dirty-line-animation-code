"""Original unbranded endurance prototype: all geometry generated in Blender."""
import bpy, math
from mathutils import Vector
from math import sin,cos,pi

def material(name,color,metal=0,rough=.35,emit=0):
 m=bpy.data.materials.new(name);m.diffuse_color=(*color,1);m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(*color,1);p.inputs['Metallic'].default_value=metal;p.inputs['Roughness'].default_value=rough;p.inputs['Emission Color'].default_value=(*color,1);p.inputs['Emission Strength'].default_value=emit
 return m

def mesh(name,verts,faces,mat,parent=None):
 me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.update();o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o);o.data.materials.append(mat);o.parent=parent
 for p in me.polygons:p.use_smooth=True
 return o

def cube(name,loc,scale,mat,parent=None,bevel=.03):
 bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale;bpy.ops.object.transform_apply(location=False,rotation=False,scale=True);o.parent=parent;o.data.materials.append(mat)
 if bevel:b=o.modifiers.new('Edge radii','BEVEL');b.width=bevel;b.segments=3;o.modifiers.new('Normals','WEIGHTED_NORMAL')
 return o

def cylinder(name,loc,r,depth,mat,parent=None,axis='Y',vertices=48):
 bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=loc,rotation=(pi/2,0,0) if axis=='Y' else (0,0,0));o=bpy.context.object;o.name=name;o.data.materials.append(mat);o.parent=parent
 for p in o.data.polygons:p.use_smooth=True
 b=o.modifiers.new('Fine edge','BEVEL');b.width=.008;b.segments=2;o.modifiers.new('Normals','WEIGHTED_NORMAL');return o

def loft(name,sections,mat,parent,segments=24):
 # sections: longitudinal x, halfwidth, bottom, top. Rounded-square section.
 v=[];f=[]
 for x,w,bot,top in sections:
  for i in range(segments):
   a=2*pi*i/segments;y=w*math.copysign(abs(cos(a))**.65,cos(a));z=(top+bot)/2+(top-bot)/2*math.copysign(abs(sin(a))**.8,sin(a));v.append((x,y,z))
 for j in range(len(sections)-1):
  for i in range(segments):f.append((j*segments+i,j*segments+(i+1)%segments,(j+1)*segments+(i+1)%segments,(j+1)*segments+i))
 f+=[tuple(reversed(range(segments))),tuple((len(sections)-1)*segments+i for i in range(segments))]
 return mesh(name,v,f,mat,parent)

def build_car(name,color):
 root=bpy.data.objects.new(name,None);bpy.context.collection.objects.link(root)
 paint=material(name+' | lacquer',color,.65,.22);carbon=material(name+' | exposed carbon',(.012,.018,.023),.45,.32);rubber=material(name+' | tire rubber',(.009,.011,.014),0,.48);metal=material(name+' | forged alloy',(.27,.31,.35),.9,.24);glass=material(name+' | smoked glass',(.014,.032,.045),.65,.12);white=material(name+' | LED white',(.65,.83,1),.1,.2,7);red=material(name+' | rear LED',(.7,.004,.002),.1,.2,5);orange=material(name+' | brake disc',(.32,.15,.06),.85,.35)
 body=loft(name+' sculpted body',[(-2.28,.76,.24,.51),(-2.05,.94,.2,.65),(-1.45,.98,.18,.78),(-.7,.85,.18,.68),(.5,.83,.18,.64),(1.35,.97,.18,.70),(1.95,.93,.22,.59),(2.35,.72,.3,.40)],paint,root)
 # Real wheel arches cut through the body, not intersecting toy wheels.
 for x in (-1.45,1.45):
  bpy.ops.mesh.primitive_cylinder_add(vertices=64,radius=.465,depth=3,location=(x,0,.39),rotation=(pi/2,0,0));cut=bpy.context.object
  mod=body.modifiers.new('Open wheel arch','BOOLEAN');mod.operation='DIFFERENCE';mod.object=cut;bpy.context.view_layer.objects.active=body;bpy.ops.object.modifier_apply(modifier=mod.name);bpy.data.objects.remove(cut,do_unlink=True)
 b=body.modifiers.new('Body edge radii','BEVEL');b.width=.025;b.segments=3;body.modifiers.new('Body normals','WEIGHTED_NORMAL')
 # Canopy smoothly narrows into a long dorsal engine cover.
 canopy=loft(name+' canopy',[(-1.1,.18,.62,.72),(-.85,.39,.61,1.02),(-.45,.46,.60,1.23),(.10,.43,.61,1.26),(.55,.35,.60,1.10),(.94,.16,.59,.70)],glass,root)
 sub=canopy.modifiers.new('Canopy curvature','SUBSURF');sub.levels=2
 roof=loft(name+' roof spine',[(-1.05,.055,.7,.75),(-.78,.065,1,1.08),(-.4,.07,1.21,1.26),(.1,.065,1.24,1.28),(.5,.055,1.08,1.13),(.9,.04,.66,.71)],paint,root,12)
 # Front splitter, nose center keel, rear diffuser and vented side pods.
 cube(name+' front splitter',(2.12,0,.21),(.62,2.03,.055),carbon,root,.035)
 cube(name+' side sill left',(-.02,-.91,.22),(2.1,.12,.12),carbon,root)
 cube(name+' side sill right',(-.02,.91,.22),(2.1,.12,.12),carbon,root)
 cube(name+' diffuser',(-2.12,0,.21),(.55,1.7,.08),carbon,root)
 for y in (-.7,-.35,0,.35,.7):cube(name+' diffuser fin',(-2.15,y,.23),(.5,.025,.17),carbon,root,.005)
 for sy in (-1,1):
  # Headlight housings and three thin functional LED strips.
  housing=cube(name+' front light housing',(1.95,sy*.72,.56),(.43,.29,.10),carbon,root,.055);housing.rotation_euler.y=-.12
  for j in range(3):cube(name+' white light blade',(2.08-j*.07,sy*.72,.615),(.025,.23,.018),white,root,.008)
  cube(name+' rear light',(-2.29,sy*.52,.51),(.025,.58,.025),red,root,.009)
  # Side intake black inset with internal vanes.
  cube(name+' side intake',(-.22,sy*.855,.48),(.72,.035,.23),carbon,root,.055)
  for j in range(5):cube(name+' intake vane',(-.48+j*.13,sy*.88,.47),(.026,.04,.19),metal,root,.006)
  # Fenders over each wheel carry fine louvers rather than flat blocks.
  for x in (-1.45,1.45):
   for j in range(5):cube(name+' fender louver',(x-.22+j*.1,sy*.72,.77),(.035,.26,.015),carbon,root,.005)
  cube(name+' mirror stalk',(.3,sy*.53,.94),(.16,.25,.035),carbon,root,.012)
  cube(name+' mirror',(.32,sy*.69,.96),(.24,.12,.10),paint,root,.045)
 # Twin supports, thin cambered rear wing and endplates.
 for y in (-.43,.43):cube(name+' wing upright',(-1.92,y,.88),(.11,.055,.68),carbon,root,.012)
 wing=cube(name+' rear wing',(-2.02,0,1.2),(.52,2.12,.07),carbon,root,.035);wing.rotation_euler.y=.07
 for sy in (-1,1):cube(name+' wing endplate',(-2.02,sy*1.04,1.2),(.57,.035,.23),paint,root,.02)
 # Wheels: separate steering pivots, tire barrel, rim lips, spokes and brake discs.
 wheels=[]
 for x in (-1.45,1.45):
  for sy in (-1,1):
   pivot=bpy.data.objects.new(name+' steering pivot',None);bpy.context.collection.objects.link(pivot);pivot.parent=root;pivot.location=(x,sy*.91,.39)
   spin=bpy.data.objects.new(name+' rotating wheel',None);bpy.context.collection.objects.link(spin);spin.parent=pivot
   tire=cylinder(name+' tire',(0,0,0),.39,.30,rubber,spin)
   # Surface circumferential grooves and molded sidewall rings.
   for yy in (-.105,0,.105):
    bpy.ops.mesh.primitive_torus_add(major_segments=48,minor_segments=6,major_radius=.387,minor_radius=.006,location=(0,yy,0),rotation=(pi/2,0,0));o=bpy.context.object;o.name=name+' tire groove';o.parent=spin;o.data.materials.append(carbon)
   outer=sy*.157
   cylinder(name+' brake rotor',(0,sy*.10,0),.245,.018,orange,spin)
   cylinder(name+' rim barrel',(0,outer,0),.29,.025,metal,spin)
   cylinder(name+' dark rim well',(0,outer+sy*.016,0),.255,.025,carbon,spin)
   for j in range(10):
    a=2*pi*j/10;sp=cube(name+' forged spoke',(.14*cos(a),outer+sy*.035,.14*sin(a)),(.235,.035,.027),metal,spin,.009);sp.rotation_euler.y=-a
   cylinder(name+' centerlock',(0,outer+sy*.06,0),.065,.04,metal,spin)
   wheels.append((pivot,spin,x,sy))
 # Functioning headlight cones mounted low, aimed down the road.
 for sy in (-1,1):
  d=bpy.data.lights.new(name+' headlight','SPOT');d.energy=700;d.color=(.73,.85,1);d.spot_size=.65;d.spot_blend=.55;d.shadow_soft_size=.08
  o=bpy.data.objects.new(name+' headlight',d);bpy.context.collection.objects.link(o);o.parent=root;o.location=(2.18,sy*.71,.58);o.rotation_euler=Vector((1,0,-.065)).to_track_quat('-Z','Y').to_euler()
 return root,wheels
