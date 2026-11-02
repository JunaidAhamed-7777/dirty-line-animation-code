# Historical authored revision; duplicate shared helpers and all assets are omitted.
"""Original low-cost ragged conifer silhouettes for the distant verge.
Only generated mesh geometry; no external vegetation assets or texture cards.
"""
import bpy, math, random
from car_model import material, mesh

def _tree_mesh(index,rng,leafmats,bark):
 verts=[];faces=[];slots=[]
 # Slightly bent thin trunk, with a narrow root flare rather than a straight pole.
 for row,z in enumerate((0.,.46,1.)):
  radius=(.020,.012,.003)[row];cx=.013*math.sin(z*2+index);cy=.009*math.sin(z*3+index)
  for j in range(6):
   a=j*math.tau/6;verts.append((cx+radius*math.cos(a),cy+radius*math.sin(a),z))
 for row in range(2):
  for j in range(6):faces.append((row*6+j,row*6+(j+1)%6,(row+1)*6+(j+1)%6,(row+1)*6+j));slots.append(3)
 # Overlapping jagged branch skirts, with alternating long/short tips and
 # asymmetric centers. These are faceted branch masses, not smooth cones.
 tiers=rng.randint(7,9)
 for tier in range(tiers):
  z=.15+tier*.79/(tiers-1);r=.19*(1-z)**.72*rng.uniform(.8,1.14)
  cx=.018*math.sin(tier*1.5+index);cy=.014*math.cos(tier*1.8+index)
  count=12;base=len(verts);rotation=rng.random()*math.tau
  # Upper branch attachment ring and uneven lower rim form a crumpled skirt.
  for j in range(count):
   a=rotation+j*math.tau/count;rr=r*(rng.uniform(.6,.9) if j%2 else rng.uniform(.95,1.22));zz=z+rng.uniform(-.055,.015)
   verts.append((cx+rr*math.cos(a),cy+rr*math.sin(a),zz))
  peak=len(verts);verts.append((cx+rng.uniform(-.015,.015),cy+rng.uniform(-.015,.015),min(1.035,z+.17)))
  hub=len(verts);verts.append((cx,cy,z-.01))
  for j in range(count):
   faces.append((base+j,base+(j+1)%count,peak));slots.append((tier+j//4)%3)
   faces.append((base+(j+1)%count,base+j,hub));slots.append((tier+1)%3)
 ob=mesh('Ragged conifer prototype %02d'%index,verts,faces,leafmats[0]);me=ob.data
 for m in leafmats[1:]+[bark]:me.materials.append(m)
 for p,slot in zip(me.polygons,slots):p.material_index=slot;p.use_smooth=False
 bpy.data.objects.remove(ob,do_unlink=True);return me

def build_distant_treeline(seed=78143,count=208):
 """Create a shallow y58–69m forest edge with sparse clusters/open gaps.
 Trees are 4–9.5m nominal height, max actual mesh tip <10m. Root z=.025m.
 Does not touch existing scene geometry or save any files.
 """
 name='Distant irregular treeline'
 if name in bpy.data.collections:raise RuntimeError('Treeline already exists; duplicate refused')
 rng=random.Random(seed);col=bpy.data.collections.new(name);bpy.context.scene.collection.children.link(col)
 leaves=[material('Wet conifer foliage %d'%i,c,0,.82) for i,c in enumerate([(.014,.026,.024),(.019,.033,.029),(.025,.039,.035)])]
 bark=material('Distant conifer bark',(.028,.024,.020),0,.91)
 variants=[_tree_mesh(i,rng,leaves,bark) for i in range(9)]
 # Deliberate uneven groups, plus a few isolated sentinels. Clear gaps remain.
 clusters=[(-196,10),(-155,12),(-119,7),(-76,11),(-26,13),(24,8),(62,11),(112,15),(162,9)]
 positions=[];attempts=0
 while len(positions)<count and attempts<count*40:
  attempts+=1
  if rng.random()<.90:
   center,spread=rng.choice(clusters);x=max(-220,min(180,rng.gauss(center,spread)))
  else:x=rng.uniform(-220,180)
  y=rng.uniform(59,68.8)
  # Avoid artificial one-dimensional rows and near-identical overlapping trunks.
  if any((x-px)**2+(y-py)**2<1.25**2 for px,py in positions):continue
  positions.append((x,y))
  me=rng.choice(variants);o=bpy.data.objects.new('Ragged distant conifer',me);col.objects.link(o)
  height=rng.uniform(4,9.5);width=height*rng.uniform(.72,1.13);o.scale=(width,width*rng.uniform(.85,1.1),height);o.location=(x,y,.025)
  o.rotation_euler=(rng.uniform(-.025,.025),rng.uniform(-.025,.025),rng.random()*math.tau)
 col['seed']=seed;col['tree_count']=len(positions);col['shared_meshes']=len(variants);col['purpose']='Layered forest silhouette ahead of distant hills; original generated geometry.'
 return {'collection':col,'tree_count':len(positions),'shared_meshes':len(variants),'max_faces_per_variant':max(len(v.polygons) for v in variants),'x_bounds':(min(x for x,y in positions),max(x for x,y in positions)),'y_bounds':(min(y for x,y in positions),max(y for x,y in positions))}
