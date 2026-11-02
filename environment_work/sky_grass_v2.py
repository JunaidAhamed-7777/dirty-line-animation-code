"""Reconstructed V2 grass/halfmoon. No clouds. Not byte-identical original.
build_sky_grass(ROAD, GRAVEL, max_clumps=45000); no save/render side effects.
"""
import bpy,math,random,bisect
from collections import defaultdict
PREFIX='V2 Sky Grass | '
def build_sky_grass(road,gravel,max_clumps=45000):
 rng=random.Random(28573)
 routes=[[(float(p[0]),float(p[1])) for p in route] for route in (road,gravel)]
 if any(len(r)<2 for r in routes):raise ValueError('Need sampled road and gravel centerlines')
 for o in list(bpy.data.objects):
  if o.name.startswith(PREFIX):bpy.data.objects.remove(o,do_unlink=True)
 collection=bpy.data.collections.get('V2 Sky Grass')
 if not collection:collection=bpy.data.collections.new('V2 Sky Grass');bpy.context.scene.collection.children.link(collection)
 # Spatial hash of dense centerline samples, generous extra margin for intersample gaps.
 cells=[];cell_size=6.0
 for route in routes:
  grid=defaultdict(list)
  for a,b in zip(route,route[1:]):
   length=math.hypot(b[0]-a[0],b[1]-a[1]);steps=max(1,math.ceil(length/.5))
   for k in range(steps):
    t=k/steps;x=a[0]+(b[0]-a[0])*t;y=a[1]+(b[1]-a[1])*t;grid[(math.floor(x/cell_size),math.floor(y/cell_size))].append((x,y))
  cells.append(grid)
 def clear(x,y):
  gx=math.floor(x/cell_size);gy=math.floor(y/cell_size)
  for grid,margin in zip(cells,(4.5,4.1)):
   rr=(margin+.08)**2
   for dx in (-1,0,1):
    for dy in (-1,0,1):
     for px,py in grid.get((gx+dx,gy+dy),()):
      if (x-px)**2+(y-py)**2<rr:return False
  return True
 lengths=[]
 for route in routes:
  cumulative=[0.0]
  for a,b in zip(route,route[1:]):cumulative.append(cumulative[-1]+math.hypot(b[0]-a[0],b[1]-a[1]))
  lengths.append(cumulative)
 def sample(route_index):
  route=routes[route_index];cum=lengths[route_index];s=rng.uniform(0,cum[-1]);i=min(len(route)-2,bisect.bisect_right(cum,s)-1);a,b=route[i:i+2];t=(s-cum[i])/max(1e-9,cum[i+1]-cum[i]);dx=b[0]-a[0];dy=b[1]-a[1];d=math.hypot(dx,dy)
  return a[0]+dx*t,a[1]+dy*t,-dy/d,dx/d
 mats=[]
 for i,col in enumerate(((.055,.082,.021,1),(.082,.105,.033,1),(.105,.12,.044,1),(.033,.061,.019,1),(.15,.14,.065,1))):
  m=bpy.data.materials.get(PREFIX+'grass '+str(i)) or bpy.data.materials.new(PREFIX+'grass '+str(i));m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=col;p.inputs['Roughness'].default_value=.88;p.inputs['Specular IOR Level'].default_value=.18;mats.append(m)
 verts=[];faces=[];mi=[];batch=0;counts={'verge':0,'infield':0}
 def flush():
  nonlocal verts,faces,mi,batch
  if not verts:return
  me=bpy.data.meshes.new(PREFIX+f'grass batch {batch:03d}');me.from_pydata(verts,[],faces);me.update();ob=bpy.data.objects.new(me.name,me);collection.objects.link(ob)
  for m in mats:me.materials.append(m)
  for p,idx in zip(me.polygons,mi):p.material_index=idx;p.use_smooth=True
  verts=[];faces=[];mi=[];batch+=1
 def clump(x,y):
  # Terrain top is near0.025m. Root tuck avoids floating grass.
  h=rng.uniform(.08,.22);shade=rng.randrange(len(mats));base_angle=rng.random()*math.tau
  for blade in range(rng.randint(3,5)):
   angle=base_angle+blade*2.4+rng.uniform(-.4,.4);wx=math.cos(angle);wy=math.sin(angle);bend=rng.uniform(.018,.065);height=h*rng.uniform(.75,1.1);width=rng.uniform(.004,.010);bx=x+rng.uniform(-.035,.035);by=y+rng.uniform(-.035,.035);start=len(verts)
   for j in range(5):
    t=j/5;cx=bx+wy*bend*t*t;cy=by-wx*bend*t*t;w=width*(1-.85*t)
    verts.extend(((cx-wx*w,cy-wy*w,.018+height*t),(cx+wx*w,cy+wy*w,.018+height*t)))
   verts.append((bx+wy*bend,by-wx*bend,.018+height))
   for j in range(4):faces.append((start+j*2,start+j*2+1,start+j*2+3,start+j*2+2));mi.append(shade)
   faces.append((start+8,start+9,start+10));mi.append(shade)
 def patch_accept(x,y):
  # Broad sparse patches rather than uniform carpet or individually placed objects.
  value=.62+.18*math.sin(x*.19+y*.13)+.12*math.sin(x*.073-y*.23)
  return rng.random()<value
 attempts=0
 while counts['verge']<max_clumps and attempts<max_clumps*18:
  attempts+=1;ri=0 if rng.random()<lengths[0][-1]/sum(c[-1] for c in lengths) else 1;x,y,nx,ny=sample(ri);offset=rng.uniform(4.65 if ri==0 else 4.25,12.5)*(1 if rng.random()<.5 else -1);x+=nx*offset;y+=ny*offset
  if not clear(x,y) or not patch_accept(x,y):continue
  clump(x,y);counts['verge']+=1
  if counts['verge']%2500==0:flush()
 # Field between branch centerlines; ROAD/GRAVEL monotonic X in this film.
 sr=sorted(routes[0]);sg=sorted(routes[1]);rx=[p[0] for p in sr];gx=[p[0] for p in sg]
 def at(route,xs,x):
  i=max(0,min(len(route)-2,bisect.bisect_right(xs,x)-1));a,b=route[i:i+2];return a[1]+(b[1]-a[1])*(x-a[0])/max(1e-9,b[0]-a[0])
 target=round(max_clumps/3);attempts=0
 while counts['infield']<target and attempts<target*25:
  attempts+=1;x=rng.uniform(max(rx[0],gx[0]),min(rx[-1],gx[-1]));a=at(sr,rx,x);b=at(sg,gx,x)
  if abs(a-b)<11:continue
  y=rng.uniform(min(a,b)+4.5,max(a,b)-4.5)
  if not clear(x,y) or not patch_accept(x,y):continue
  clump(x,y);counts['infield']+=1
  if counts['infield']%2500==0:flush()
 flush()
 # Existing scene SUN supplies phase/shading; no emissive disk or extra light.
 bpy.ops.mesh.primitive_uv_sphere_add(segments=64,ring_count=32,radius=10,location=(300,850,125));moon=bpy.context.object;moon.name=PREFIX+'HALF MOON'
 for c in list(moon.users_collection):c.objects.unlink(moon)
 collection.objects.link(moon)
 m=bpy.data.materials.get(PREFIX+'moon grey') or bpy.data.materials.new(PREFIX+'moon grey');m.use_nodes=True;p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Base Color'].default_value=(.38,.39,.41,1);p.inputs['Roughness'].default_value=1;p.inputs['Specular IOR Level'].default_value=.08;moon.data.materials.append(m)
 for p in moon.data.polygons:p.use_smooth=True
 moon['phase_note']='Grey sphere phase depends on existing SUN direction; inspect rendered half-phase.'
 bpy.context.scene['V2_grass_recovery']=str(counts);return counts
