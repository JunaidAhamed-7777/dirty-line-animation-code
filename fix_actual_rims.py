"""Move the supplied Audi's actual painted rim geometry onto its wheel rig.
Uses disconnected mesh components and Blender's native Separate operation to
preserve UVs, material slots and custom mesh layers. Does not save any file.
The inner offset brake-caliper components deliberately remain stationary.
"""
import bpy,math
from mathutils import Vector

def _component_targets(ob,root,wheels):
 me=ob.data;parent=list(range(len(me.vertices)))
 def find(a):
  while parent[a]!=a:parent[a]=parent[parent[a]];a=parent[a]
  return a
 for edge in me.edges:
  a,b=map(find,edge.vertices)
  if a!=b:parent[b]=a
 comps={}
 for v in me.vertices:comps.setdefault(find(v.index),[]).append(v.index)
 T=root.matrix_world.inverted()@ob.matrix_world;labels={};details=[]
 isblack=any(m and m.name.startswith('black.') for m in me.materials)
 for comp,indices in comps.items():
  vs=[T@me.vertices[i].co for i in indices];center=sum(vs,Vector())/len(vs);pos=min(wheels,key=lambda p:(center-wheels[p]).length);w=wheels[pos]
  maxr=max(math.hypot(v.x-w.x,v.z-w.z) for v in vs);maxdy=max(abs(v.y-w.y) for v in vs)
  if maxr>=.28 or maxdy>=.16:continue
  outward=(center.y-w.y)*(1 if w.y>0 else -1);center_radius=math.hypot(center.x-w.x,center.z-w.z)
  # Offset caliper is inside the barrel, not on the rotating rim face.
  if isblack and outward<-.005 and center_radius>.05:
   details.append({'component':comp,'wheel':pos,'action':'retain stationary inner caliper','vertices':len(vs)});continue
  labels[comp]=pos
 return {p.index:labels.get(find(p.vertices[0])) for p in me.polygons},details

def fix_actual_rims():
 if bpy.data.objects.get('AUDI_RIM_DETAIL_FL_15'):
  return {'status':'already applied; no duplicate mutation'}
 s=bpy.context.scene;frame=s.frame_current;s.frame_set(1);bpy.context.view_layer.update()
 root=bpy.data.objects['AUDI_ROOT'];wheels={p:bpy.data.objects['AUDI_STEER_'+p].location.copy() for p in ('FL','FR','BL','BR')}
 report={'status':'applied','splits':[],'stationary_components':[],'gt40_rim_parents':{},'validation':[]}
 if bpy.context.object and bpy.context.object.mode!='OBJECT':bpy.ops.object.mode_set(mode='OBJECT')
 for name in ('AUDI_Object_15','AUDI_Object_4','AUDI_Object_21'):
  ob=bpy.data.objects.get(name)
  if not ob:continue
  targets,stationary=_component_targets(ob,root,wheels);report['stationary_components']+=stationary
  before=(len(ob.data.vertices),len(ob.data.polygons));uvnames=[uv.name for uv in ob.data.uv_layers]
  uvsum=[sum(d.uv[k] for uv in ob.data.uv_layers for d in uv.data) for k in (0,1)]
  attr=ob.data.attributes.new('_wheel_component_target','INT','FACE');codes={None:0,'FL':1,'FR':2,'BL':3,'BR':4}
  for p in ob.data.polygons:attr.data[p.index].value=codes[targets[p.index]]
  pieces=[]
  for pos in ('FL','FR','BL','BR'):
   data=ob.data;tag=data.attributes['_wheel_component_target'];selected=[p.index for p in data.polygons if tag.data[p.index].value==codes[pos]]
   if not selected:continue
   bpy.ops.object.select_all(action='DESELECT');ob.hide_set(False);ob.select_set(True);bpy.context.view_layer.objects.active=ob
   for v in data.vertices:v.select=False
   for e in data.edges:e.select=False
   for p in data.polygons:p.select=False
   for i in selected:data.polygons[i].select=True
   bpy.context.tool_settings.mesh_select_mode=(False,False,True)
   old=set(bpy.data.objects);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.separate(type='SELECTED');bpy.ops.object.mode_set(mode='OBJECT')
   new=list(set(bpy.data.objects)-old)
   if len(new)!=1:raise RuntimeError('Unexpected Separate output: '+str(len(new)))
   piece=new[0];piece.name='AUDI_RIM_DETAIL_'+pos+'_'+name.rsplit('_',1)[-1]
   world=piece.matrix_world.copy();piece.parent=bpy.data.objects['AUDI_WHEEL_'+pos];piece.matrix_world=world;bpy.context.view_layer.update()
   pieces.append(piece);report['splits'].append({'source':name,'object':piece.name,'wheel':pos,'polygons':len(piece.data.polygons),'materials':[m.name for m in piece.data.materials if m],'uv_layers':[uv.name for uv in piece.data.uv_layers]})
  allparts=[ob]+pieces;after=(sum(len(o.data.vertices) for o in allparts),sum(len(o.data.polygons) for o in allparts))
  afteruv=[sum(d.uv[k] for o in allparts for uv in o.data.uv_layers for d in uv.data) for k in (0,1)]
  assert before==after,(name,before,after)
  assert all([uv.name for uv in o.data.uv_layers]==uvnames for o in allparts)
  assert max(abs(a-b) for a,b in zip(uvsum,afteruv))<1e-4,(name,uvsum,afteruv)
  report['validation'].append({'source':name,'before_vertices_faces':before,'after_vertices_faces':after,'UV_sum_max_error':max(abs(a-b) for a,b in zip(uvsum,afteruv))})
  for o in allparts:
   tag=o.data.attributes.get('_wheel_component_target')
   if tag:o.data.attributes.remove(tag)
 for pos in ('FL','FR','BL','BR'):
  rim=bpy.data.objects.get('GT40_Rim'+pos);expected='GT40_WHEEL_'+pos
  report['gt40_rim_parents'][pos]=rim.parent.name if rim and rim.parent else None
  assert rim and rim.parent and rim.parent.name==expected,('GT40 unexpected rim parent',pos)
 s.frame_set(frame);bpy.context.view_layer.update();return report
