"""Closed fictional mixed-surface night course. Asset-independent scene module."""
import bpy,math,random
from mathutils import Vector
from car_model import material,mesh,cube,cylinder
random.seed(127)
from timeline import ROAD as _R,GRAVEL as _G,profile_height,FINISH_X,FINISH_Y,main_y
ROAD=[Vector(p) for p in _R];GRAVEL=[Vector(p) for p in _G]
def strip(name,points,width,mat,height=.03):
 verts=[];faces=[]
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();normal=Vector((-tangent.y,tangent.x))
  for side in (-1,1):
   q=p+normal*width*.5*side;z=profile_height(q.x,q.y,True)+.006 if name.startswith('Gravel') else height;verts.append((q.x,q.y,z))
 for i in range(len(points)-1):faces.append((2*i,2*i+1,2*i+3,2*i+2))
 ob=mesh(name,verts,faces,mat)
 uv=ob.data.uv_layers.new(name='Ribbon UV')
 for poly in ob.data.polygons:
  for li in poly.loop_indices:
   vi=ob.data.loops[li].vertex_index;uv.data[li].uv=(vi%2,(vi//2)/(len(points)-1))
 return ob
def texture(mat,scale,bump,roughlo,roughhi):
 nt=mat.node_tree;p=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
 geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
 col=nt.nodes.new('ShaderNodeValToRGB');base=p.inputs['Base Color'].default_value[:3];col.color_ramp.elements[0].color=tuple(c*.55 for c in base)+(1,);col.color_ramp.elements[1].color=tuple(c*1.4 for c in base)+(1,);nt.links.new(noise.outputs['Fac'],col.inputs[0]);nt.links.new(col.outputs[0],p.inputs['Base Color'])
 b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump;b.inputs['Distance'].default_value=.025;nt.links.new(noise.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(roughlo,roughlo,roughlo,1);ramp.color_ramp.elements[1].color=(roughhi,roughhi,roughhi,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Roughness'])
def build_course():
 asphalt=material('Rain-black asphalt',(.024,.032,.043),.18,.23);texture(asphalt,36,.32,.12,.38)
 gravel=material('Compacted ochre gravel',(.13,.095,.065),.05,.8);texture(gravel,14,.75,.6,.95)
 land=material('Midnight wet earth',(.035,.043,.026),0,.9);texture(land,1.6,.5,.75,1)
 white=material('Road paint',(.65,.67,.62),.1,.35);red=material('Curb red',(.32,.025,.012),.1,.5);metal=material('Barrier galvanized',(.11,.14,.17),.8,.38);black=material('Rubber posts',(.015,.02,.024),0,.8);amber=material('Reflector amber',(1,.24,.018),.2,.25,1.5)
 cube('Terrain',(60,0,-.075),(1300,650,.2),land,None,0)
 # Macro wetness is independent of asphalt grain: patchy rough areas and shallow wet hollows.
 nt=asphalt.node_tree;bs=nt.nodes.get('Principled BSDF');geo=nt.nodes.new('ShaderNodeNewGeometry');wet=nt.nodes.new('ShaderNodeTexNoise');wet.inputs['Scale'].default_value=.30;wet.inputs['Detail'].default_value=4;wet.inputs['Roughness'].default_value=.7;nt.links.new(geo.outputs['Position'],wet.inputs['Vector']);r=nt.nodes.new('ShaderNodeValToRGB');r.color_ramp.elements[0].position=.25;r.color_ramp.elements[0].color=(.14,.14,.14,1);r.color_ramp.elements[1].position=.78;r.color_ramp.elements[1].color=(.43,.43,.43,1);nt.links.new(wet.outputs['Fac'],r.inputs[0]);nt.links.new(r.outputs[0],bs.inputs['Roughness'])
 # Feather gravel into the earth with a noisy boundary, not a raised rectangular carpet.
 nt=gravel.node_tree;bs=nt.nodes.get('Principled BSDF');uv=nt.nodes.new('ShaderNodeTexCoord');sep=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(uv.outputs['UV'],sep.inputs[0]);sub=nt.nodes.new('ShaderNodeMath');sub.operation='SUBTRACT';sub.inputs[1].default_value=.5;nt.links.new(sep.outputs['X'],sub.inputs[0]);ab=nt.nodes.new('ShaderNodeMath');ab.operation='ABSOLUTE';nt.links.new(sub.outputs[0],ab.inputs[0]);geo=nt.nodes.new('ShaderNodeNewGeometry');n=nt.nodes.new('ShaderNodeTexNoise');n.inputs['Scale'].default_value=3;nt.links.new(geo.outputs['Position'],n.inputs['Vector']);mul=nt.nodes.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.10;nt.links.new(n.outputs['Fac'],mul.inputs[0]);add=nt.nodes.new('ShaderNodeMath');add.operation='ADD';nt.links.new(ab.outputs[0],add.inputs[0]);nt.links.new(mul.outputs[0],add.inputs[1]);fade=nt.nodes.new('ShaderNodeMapRange');fade.inputs['From Min'].default_value=.37;fade.inputs['From Max'].default_value=.49;fade.inputs['To Min'].default_value=1;fade.inputs['To Max'].default_value=0;fade.clamp=True;nt.links.new(add.outputs[0],fade.inputs[0]);nt.links.new(fade.outputs['Result'],bs.inputs['Alpha'])
 strip('Paved race course',ROAD,8,asphalt);strip('Gravel shortcut',GRAVEL,7,gravel)
 rut=material('Damp compressed tire ruts',(.055,.043,.027),0,.65);texture(rut,22,.2,.45,.85)
 for side in (-1,1):
  pts=[]
  for i,p in enumerate(GRAVEL):
   tangent=(GRAVEL[min(i+1,len(GRAVEL)-1)]-GRAVEL[max(i-1,0)]).normalized();q=p+Vector((-tangent.y,tangent.x))*(side*.72+.24*math.sin(i*.055));pts.append(q)
  ob=strip('Gravel compacted wheel track',pts,.20,rut);ob.location.z=.001

 # Edge lines follow actual road curvature; gaps at gravel entry and exit remain clear.
 for side in (-1,1):
  edge=[]
  for i,p in enumerate(ROAD):
   tangent=(ROAD[min(i+1,len(ROAD)-1)]-ROAD[max(i-1,0)]).normalized();q=p+Vector((-tangent.y,tangent.x))*side*3.65;edge.append(q)
  strip('White road edge',edge,.09,white,.038)
 # Red/white kerb blocks on the paved corner, unmistakable geography in the wide shot.
 for i in range(520,1160,6):
  p=ROAD[i];tan=(ROAD[i+1]-ROAD[i-1]).normalized();normal=Vector((-tan.y,tan.x));q=p+normal*4.1
  o=cube('Corner curb',(q.x,q.y,.06),(1.25,.48,.1),red if (i//6)%2 else white,None,.02);o.rotation_euler.z=math.atan2(tan.y,tan.x)
 # Sparse reflectors define the gravel route without blocking the action.
 for i in range(8,len(GRAVEL)-8,16):
  p=GRAVEL[i];tan=(GRAVEL[i+1]-GRAVEL[i-1]).normalized();nor=Vector((-tan.y,tan.x))
  for side in (-1,1):
   q=p+nor*side*3.5;cube('Gravel marker',(q.x,q.y,.38),(.12,.12,.75),white,None,.015);cube('Marker reflector',(q.x,q.y-.067,.61),(.09,.015,.12),amber,None,.005)
 # Finish line is actual painted geometry, not an editing claim.
 for j in range(16):
  for k in range(2):cube('Finish chequer',(FINISH_X+k*.42,FINISH_Y-3.8+j*.48,.043),(.42,.48,.012),white if (j+k)%2 else black,None,0)
 # Small irregular stones soften the manufactured-looking edge of the gravel cut.
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);proto=bpy.context.object;proto.name='Gravel edge stone';proto.data.materials.append(gravel)
 for i in range(450):
  j=random.randrange(1,len(GRAVEL)-1);p=GRAVEL[j];tan=(GRAVEL[j+1]-GRAVEL[j-1]).normalized();nor=Vector((-tan.y,tan.x));q=p+nor*random.uniform(-3.4,3.4)
  o=proto if i==0 else bpy.data.objects.new('Scattered gravel',proto.data)
  if i:bpy.context.collection.objects.link(o)
  o.location=(q.x,q.y,profile_height(q.x,q.y,True)+.015);r=random.uniform(.015,.075);o.scale=(r*1.5,r,r*.6);o.rotation_euler=(random.random(),random.random(),random.random()*6.28)
 # Continuous irregular ridgelines rather than repeated round hill primitives.
 for layer in range(3):
  verts=[];faces=[];nx=150;ny=18
  hillmat=material('Atmospheric ridge '+str(layer),(.025+layer*.012,.039+layer*.015,.046+layer*.02),0,1)
  for j in range(ny):
   y=70+layer*55+j*7
   for i in range(nx):
    x=-500+i*8;envelope=math.sin(math.pi*j/(ny-1))**.7
    h=(12+layer*5+7*math.sin(x*.021+layer*2)+4*math.sin(x*.067+layer)+2*math.sin(x*.139+y*.06))*envelope
    verts.append((x,y,max(.02,h)))
  for j in range(ny-1):
   for i in range(nx-1):
    k=j*nx+i;faces.append((k,k+1,k+1+nx,k+nx))
  ob=mesh('Layered eroded ridgeline',verts,faces,hillmat)
  for face in ob.data.polygons:face.use_smooth=True
 # Floodlights give broad physically motivated pools and wet reflections.
 for x,y in [(x,main_y(x)+(18 if i%2 else -18)) for i,x in enumerate([-300,-220,-120,0,120,240,390])]:
  cylinder('Floodlight mast',(x,y,5.5),.075,11,metal,None,'Z',12)
  cube('Light gantry',(x,y,10.8),(3,.25,.25),metal,None,.04)
  for dx in (-1,1):
   d=bpy.data.lights.new('Track floodlight','AREA');d.energy=2600;d.color=(.58,.73,1);d.shape='DISK';d.size=3;o=bpy.data.objects.new('Track floodlight',d);bpy.context.collection.objects.link(o);o.location=(x+dx,y,10.6);target=Vector((x,main_y(x),0));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 return ROAD,GRAVEL
