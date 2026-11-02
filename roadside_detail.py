"""Seeded, low-cost natural roadside detail for DIRTY LINE.
Original linked-mesh tufts and pebbles; no image/model assets, no animation.
Safe to call after build_course(). Does not load or save a production scene.
"""
import bpy, math, random, bisect
from course import ROAD, GRAVEL
from car_model import material, mesh

def _segments(points):
 return [(float(a.x),float(a.y),float(b.x-a.x),float(b.y-a.y)) for a,b in zip(points,points[1:])]

def _distance_sq(x,y,segments):
 best=1e30
 for ax,ay,dx,dy in segments:
  q=max(0.,min(1.,((x-ax)*dx+(y-ay)*dy)/(dx*dx+dy*dy)))
  best=min(best,(x-ax-q*dx)**2+(y-ay-q*dy)**2)
 return best

def _tuft_data(index,rng,mats):
 verts=[];faces=[];slots=[]
 for blade in range(rng.randint(8,12)):
  angle=rng.random()*math.tau;dx,dy=math.cos(angle),math.sin(angle);sx,sy=-dy,dx
  bx,by=rng.uniform(-.035,.035),rng.uniform(-.035,.035)
  height=rng.uniform(.07,.19);bend=rng.uniform(.025,.085);width=rng.uniform(.004,.012)
  base=len(verts)
  for row in range(5):
   t=row/5;cx=bx+dx*bend*t*t;cy=by+dy*bend*t*t;z=height*(t-.12*t*t)
   w=width*(1-t)**.75
   verts.extend([(cx-sx*w,cy-sy*w,z),(cx,cy,z+.0025*(1-t)),(cx+sx*w,cy+sy*w,z)])
  tip=len(verts);verts.append((bx+dx*bend,by+dy*bend,height*.88))
  for row in range(4):
   a=base+row*3;b=a+3;faces.extend([(a,b,b+1,a+1),(a+1,b+1,b+2,a+2)]);slots.extend([blade%len(mats)]*2)
  faces.extend([(base+12,tip,base+13),(base+13,tip,base+14)]);slots.extend([blade%len(mats)]*2)
 ob=mesh('Roadside grass prototype %02d'%index,verts,faces,mats[0]);me=ob.data
 for m in mats[1:]:me.materials.append(m)
 for p,slot in zip(me.polygons,slots):p.material_index=slot;p.use_smooth=True
 bpy.data.objects.remove(ob,do_unlink=True)
 return me

def _stone_data(index,rng,mat):
 # Squashed irregular octahedra: small real geometry rather than billboard spots.
 verts=[(1,0,0),(-1,0,0),(0,1,0),(0,-1,0),(0,0,.65),(0,0,-.40)]
 verts=[(x*rng.uniform(.8,1.2),y*rng.uniform(.8,1.2),z*rng.uniform(.8,1.2)) for x,y,z in verts]
 faces=[(0,2,4),(2,1,4),(1,3,4),(3,0,4),(2,0,5),(1,2,5),(3,1,5),(0,3,5)]
 ob=mesh('Roadside pebble prototype %02d'%index,verts,faces,mat);me=ob.data
 for p in me.polygons:p.use_smooth=False
 bpy.data.objects.remove(ob,do_unlink=True);return me

def build_roadside_detail(seed=64271,grass_count=1120,pebble_count=220):
 """Return collection and measured counts; all instances avoid both driving paths.
 8 shared tuft meshes +4 shared pebble meshes. Ground surface is z=.025m.
 Patchiness, gaps, irregular height and rotation deliberately avoid hedge rows.
 """
 if 'Roadside natural detail' in bpy.data.collections:
  raise RuntimeError('Roadside detail already exists; refusing duplicate placement')
 rng=random.Random(seed);col=bpy.data.collections.new('Roadside natural detail');bpy.context.scene.collection.children.link(col)
 mats=[material('Wet verge grass %d'%i,c,0,.52) for i,c in enumerate([(.025,.037,.016),(.037,.045,.020),(.052,.045,.022)])]
 for m in mats:
  p=m.node_tree.nodes.get('Principled BSDF');p.inputs['Coat Weight'].default_value=.10;p.inputs['Coat Roughness'].default_value=.28
 peb=material('Damp roadside stones',(.065,.061,.052),.03,.55)
 tufts=[_tuft_data(i,rng,mats) for i in range(8)];stones=[_stone_data(i,rng,peb) for i in range(4)]
 roadseg=_segments(ROAD);gravel=_segments(GRAVEL);cum=[0.]
 for _,_,dx,dy in roadseg:cum.append(cum[-1]+math.hypot(dx,dy))
 # Random broad patches plus deliberate bare gaps, no periodic spacing pattern.
 clusters=[(rng.uniform(0,cum[-1]),rng.uniform(4,19),rng.choice([-1,1])) for _ in range(46)]
 placed={'grass':0,'pebbles':0};minroad=1e30;mingravel=1e30;attempts=0
 for kind,target,meshes in [('grass',grass_count,tufts),('pebbles',pebble_count,stones)]:
  count=0
  while count<target and attempts<(grass_count+pebble_count)*18:
   attempts+=1
   if kind=='grass':center,spread,side=rng.choice(clusters);distance=max(0,min(cum[-1]-.001,rng.gauss(center,spread)))
   else:distance=rng.uniform(0,cum[-1]);side=rng.choice([-1,1])
   seg=min(len(roadseg)-1,bisect.bisect_right(cum,distance)-1);ax,ay,dx,dy=roadseg[seg];length=math.hypot(dx,dy);q=(distance-cum[seg])/length
   offset=rng.uniform(4.60,7.0);x=ax+dx*q-dy/length*side*offset;y=ay+dy*q+dx/length*side*offset
   dr=_distance_sq(x,y,roadseg);dg=_distance_sq(x,y,gravel)
   if dr<4.48**2 or dg<4.12**2:continue
   # Occasional open patches prevent a landscaped uniform boundary.
   if kind=='grass' and math.sin(distance*.09+side)*math.sin(distance*.023+1)>.47 and rng.random()<.8:continue
   data=rng.choice(meshes);o=bpy.data.objects.new('Wet grass tuft' if kind=='grass' else 'Verge pebble',data);col.objects.link(o)
   if kind=='grass':
    scale=rng.uniform(.65,1.30);o.scale=(scale*rng.uniform(.8,1.25),scale*rng.uniform(.8,1.25),scale);z=.025
   else:
    scale=rng.uniform(.012,.045);o.scale=(scale*rng.uniform(.8,1.6),scale,scale*rng.uniform(.55,.9));z=.025+scale*.25
   o.location=(x,y,z);o.rotation_euler.z=rng.random()*math.tau
   minroad=min(minroad,math.sqrt(dr));mingravel=min(mingravel,math.sqrt(dg));count+=1
  placed[kind]=count
 col['seed']=seed;col['shared_meshes']=len(tufts)+len(stones);col['grass_count']=placed['grass'];col['pebble_count']=placed['pebbles'];col['minimum_road_center_distance']=minroad;col['minimum_gravel_center_distance']=mingravel
 return {'collection':col,'counts':placed,'shared_meshes':len(tufts)+len(stones),'minimum_road_center_distance':minroad,'minimum_gravel_center_distance':mingravel}

def build_gravel_verge(seed=9374,count=420):
 rng=random.Random(seed);col=bpy.data.collections['Roadside natural detail'];meshes=list({o.data for o in col.objects if o.name.startswith('Wet grass tuft')});road=_segments(ROAD);gravel=_segments(GRAVEL);placed=0
 for attempt in range(count*10):
  if placed>=count:break
  i=rng.randrange(4,len(GRAVEL)-5);p=GRAVEL[i];t=(GRAVEL[i+1]-GRAVEL[i-1]).normalized();side=rng.choice([-1,1]);offset=rng.uniform(4.4,9.0);x=p.x-t.y*side*offset+rng.uniform(-.8,.8);y=p.y+t.x*side*offset+rng.uniform(-.8,.8)
  if _distance_sq(x,y,road)<4.5**2 or _distance_sq(x,y,gravel)<4.1**2:continue
  if rng.random()>.65+.25*math.sin(x*.29):continue
  o=bpy.data.objects.new('Gravel verge tuft',rng.choice(meshes));col.objects.link(o);v=rng.uniform(.7,1.25);o.scale=(v,v,v);o.location=(x,y,.025);o.rotation_euler.z=rng.random()*math.tau;placed+=1
 return placed
