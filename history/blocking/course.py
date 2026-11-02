# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""Closed fictional mixed-surface night course. Asset-independent scene module."""
import bpy,math,random
from mathutils import Vector
from car_model import material,mesh,cube,cylinder
random.seed(127)
ROAD_CONTROLS=[(-140,-22),(-110,-22),(-80,-18),(-55,-8),(-45,0),(-40,16),(-27,35),(0,45),(27,35),(40,16),(45,0),(55,-8),(80,-18),(110,-22),(150,-22)]
GRAVEL_CONTROLS=[(-45,0),(-30,4),(-10,6),(10,5),(30,2),(45,0)]
def spline(ctrl,sub=12):
 out=[];pts=[ctrl[0]]+ctrl+[ctrl[-1]]
 for i in range(1,len(pts)-2):
  p0,p1,p2,p3=[Vector(p) for p in pts[i-1:i+3]]
  for k in range(sub):
   t=k/sub;q=.5*((2*p1)+(-p0+p2)*t+(2*p0-5*p1+4*p2-p3)*t*t+(-p0+3*p1-3*p2+p3)*t*t*t);out.append(q)
 out.append(Vector(ctrl[-1]));return out
ROAD=spline(ROAD_CONTROLS,20);GRAVEL=spline(GRAVEL_CONTROLS,20)
def profile_height(x,y,gravel=False):
 # A modest compacted crest and a clear ballistic landing, no giant stunt ramp.
 return .03+( .62*math.exp(-((x-24)/4.2)**2) if gravel else 0)
def strip(name,points,width,mat,height=.03):
 verts=[];faces=[]
 for i,p in enumerate(points):
  tangent=(points[min(i+1,len(points)-1)]-points[max(0,i-1)]).normalized();normal=Vector((-tangent.y,tangent.x))
  for side in (-1,1):
   q=p+normal*width*.5*side;z=profile_height(q.x,q.y,True) if name=='Gravel shortcut' else height;verts.append((q.x,q.y,z))
 for i in range(len(points)-1):faces.append((2*i,2*i+1,2*i+3,2*i+2))
 return mesh(name,verts,faces,mat)
def texture(mat,scale,bump,roughlo,roughhi):
 nt=mat.node_tree;p=nt.nodes.get('Principled BSDF');noise=nt.nodes.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=scale;noise.inputs['Detail'].default_value=3
 geo=nt.nodes.new('ShaderNodeNewGeometry');nt.links.new(geo.outputs['Position'],noise.inputs['Vector'])
 col=nt.nodes.new('ShaderNodeValToRGB');base=p.inputs['Base Color'].default_value[:3];col.color_ramp.elements[0].color=tuple(c*.55 for c in base)+(1,);col.color_ramp.elements[1].color=tuple(c*1.4 for c in base)+(1,);nt.links.new(noise.outputs['Fac'],col.inputs[0]);nt.links.new(col.outputs[0],p.inputs['Base Color'])
 b=nt.nodes.new('ShaderNodeBump');b.inputs['Strength'].default_value=bump;b.inputs['Distance'].default_value=.025;nt.links.new(noise.outputs['Fac'],b.inputs['Height']);nt.links.new(b.outputs['Normal'],p.inputs['Normal'])
 ramp=nt.nodes.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].color=(roughlo,roughlo,roughlo,1);ramp.color_ramp.elements[1].color=(roughhi,roughhi,roughhi,1);nt.links.new(noise.outputs['Fac'],ramp.inputs[0]);nt.links.new(ramp.outputs[0],p.inputs['Roughness'])
def build_course():
 asphalt=material('Rain-black asphalt',(.024,.032,.043),.18,.23);texture(asphalt,36,.32,.12,.38)
 gravel=material('Compacted ochre gravel',(.13,.095,.065),.05,.8);texture(gravel,14,.75,.6,.95)
 land=material('Midnight wet earth',(.016,.027,.020),0,.9);texture(land,1.6,.5,.75,1)
 white=material('Road paint',(.65,.67,.62),.1,.35);red=material('Curb red',(.32,.025,.012),.1,.5);metal=material('Barrier galvanized',(.11,.14,.17),.8,.38);black=material('Rubber posts',(.015,.02,.024),0,.8);amber=material('Reflector amber',(1,.24,.018),.2,.25,1.5)
 cube('Terrain',(0,0,-.12),(600,500,.2),land,None,0)
 strip('Paved race course',ROAD,8,asphalt);strip('Gravel shortcut',GRAVEL,6,gravel)
 # Edge lines follow actual road curvature; gaps at gravel entry and exit remain clear.
 for side in (-1,1):
  edge=[]
  for i,p in enumerate(ROAD):
   tangent=(ROAD[min(i+1,len(ROAD)-1)]-ROAD[max(i-1,0)]).normalized();q=p+Vector((-tangent.y,tangent.x))*side*3.65;edge.append(q)
  strip('White road edge',edge,.09,white,.038)
 # Red/white kerb blocks on the paved corner, unmistakable geography in the wide shot.
 for i in range(85,201,3):
  p=ROAD[i];tan=(ROAD[i+1]-ROAD[i-1]).normalized();normal=Vector((-tan.y,tan.x));q=p+normal*4.1
  o=cube('Corner curb',(q.x,q.y,.06),(1.25,.48,.1),red if (i//3)%2 else white,None,.02);o.rotation_euler.z=math.atan2(tan.y,tan.x)
 # Sparse reflectors define the gravel route without blocking the action.
 for i in range(8,len(GRAVEL)-8,13):
  p=GRAVEL[i];tan=(GRAVEL[i+1]-GRAVEL[i-1]).normalized();nor=Vector((-tan.y,tan.x))
  for side in (-1,1):
   q=p+nor*side*3.5;cube('Gravel marker',(q.x,q.y,.38),(.12,.12,.75),white,None,.015);cube('Marker reflector',(q.x,q.y-.067,.61),(.09,.015,.12),amber,None,.005)
 # Finish line is actual painted geometry, not an editing claim.
 for j in range(16):
  for k in range(2):cube('Finish chequer',(112+k*.42,-25.8+j*.48,.043),(.42,.48,.012),white if (j+k)%2 else black,None,0)
 # Small irregular stones soften the manufactured-looking edge of the gravel cut.
 bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1);proto=bpy.context.object;proto.name='Gravel edge stone';proto.data.materials.append(gravel)
 for i in range(450):
  j=random.randrange(1,len(GRAVEL)-1);p=GRAVEL[j];tan=(GRAVEL[j+1]-GRAVEL[j-1]).normalized();nor=Vector((-tan.y,tan.x));q=p+nor*random.uniform(-3.4,3.4)
  o=proto if i==0 else bpy.data.objects.new('Scattered gravel',proto.data)
  if i:bpy.context.collection.objects.link(o)
  o.location=(q.x,q.y,profile_height(q.x,q.y,True)+.015);r=random.uniform(.015,.075);o.scale=(r*1.5,r,r*.6);o.rotation_euler=(random.random(),random.random(),random.random()*6.28)
 # Far silhouetted low hills, seeded and original.
 for k in range(14):
  x=-220+k*34;y=105+random.uniform(-10,30);bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2,radius=1,location=(x,y,-2));o=bpy.context.object;o.name='Distant landscape';o.scale=(random.uniform(35,65),random.uniform(35,65),random.uniform(10,24));o.data.materials.append(land)
  for face in o.data.polygons:face.use_smooth=True
  sub=o.modifiers.new('Eroded silhouette','SUBSURF');sub.levels=2
 # Floodlights give broad physically motivated pools and wet reflections.
 for x,y in [(-68,-28),(-30,52),(30,52),(65,-32),(112,-35)]:
  cylinder('Floodlight mast',(x,y,5.5),.075,11,metal,None,'Z',12)
  cube('Light gantry',(x,y,10.8),(3,.25,.25),metal,None,.04)
  for dx in (-1,1):
   d=bpy.data.lights.new('Track floodlight','AREA');d.energy=2600;d.color=(.58,.73,1);d.shape='DISK';d.size=3;o=bpy.data.objects.new('Track floodlight',d);bpy.context.collection.objects.link(o);o.location=(x+dx,y,10.6);target=Vector((x,y+12 if y<0 else y-12,0));o.rotation_euler=(target-o.location).to_track_quat('-Z','Y').to_euler()
 return ROAD,GRAVEL
