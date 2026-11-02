"""Reconstructed progressive lower-body dust. Not byte-identical recovery.
Only supplied Audi carpaint.089; no glass, roof material replacement or mesh edits.
"""
import bpy

def dust_car_materials_v2():
 m=bpy.data.materials.get('carpaint.089');body=bpy.data.objects.get('AUDI_BODY')
 if not m or not body:raise RuntimeError('Expected supplied Audi body/paint missing')
 n=m.node_tree.nodes;l=m.node_tree.links;p=next(x for x in n if x.type=='BSDF_PRINCIPLED')
 old=p.inputs['Base Color'].links[0].from_socket if p.inputs['Base Color'].links else None
 tc=n.new('ShaderNodeTexCoord');tc.object=body;sp=n.new('ShaderNodeSeparateXYZ');l.new(tc.outputs['Object'],sp.inputs[0])
 h=n.new('ShaderNodeMapRange');h.clamp=True;h.interpolation_type='SMOOTHERSTEP';h.inputs['From Min'].default_value=.4;h.inputs['From Max'].default_value=1.3;h.inputs['To Min'].default_value=1;h.inputs['To Max'].default_value=0;l.new(sp.outputs['Z'],h.inputs['Value'])
 noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=7;noise.inputs['Detail'].default_value=4;noise.inputs['Roughness'].default_value=.7;l.new(tc.outputs['Object'],noise.inputs[0])
 def math(op,a,b):
  x=n.new('ShaderNodeMath');x.operation=op
  for i,v in enumerate((a,b)):
   if isinstance(v,(float,int)):x.inputs[i].default_value=v
   else:l.new(v,x.inputs[i])
  return x.outputs[0]
 film=math('ADD',math('MULTIPLY',noise.outputs['Fac'],.48),.52)
 # Wheel-proximate dust enrichment is subtle; no hard circles or upper-panel mask.
 near=[]
 for axle in (-1.11,1.11):
  d=n.new('ShaderNodeMath');d.operation='SUBTRACT';l.new(sp.outputs['X'],d.inputs[0]);d.inputs[1].default_value=axle
  a=n.new('ShaderNodeMath');a.operation='ABSOLUTE';l.new(d.outputs[0],a.inputs[0]);near.append(a.outputs[0])
 nearest=math('MINIMUM',near[0],near[1]);wheel=n.new('ShaderNodeMapRange');wheel.clamp=True;wheel.inputs['From Min'].default_value=0;wheel.inputs['From Max'].default_value=.7;wheel.inputs['To Min'].default_value=1.3;wheel.inputs['To Max'].default_value=1;l.new(nearest,wheel.inputs['Value'])
 progress=n.new('ShaderNodeValue');progress.name='Progressive gravel dust accumulation'
 for fr,value in [(1,0),(85,0),(115,.22),(150,.53),(180,.69),(260,1),(536,1)]:progress.outputs[0].default_value=value;progress.outputs[0].keyframe_insert('default_value',frame=fr)
 mask=math('MULTIPLY',math('MULTIPLY',math('MULTIPLY',h.outputs['Result'],film),wheel.outputs['Result']),progress.outputs[0]);mask=math('MINIMUM',math('MULTIPLY',mask,.78),.86)
 mix=n.new('ShaderNodeMixRGB');mix.name='Settled sandy lower-body film';l.new(mask,mix.inputs[0]);mix.inputs[2].default_value=(.30,.205,.105,1)
 if old:l.new(old,mix.inputs[1])
 else:mix.inputs[1].default_value=p.inputs['Base Color'].default_value
 l.new(mix.outputs[0],p.inputs['Base Color']);rough=math('ADD',math('MULTIPLY',mask,.55),.21);l.new(rough,p.inputs['Roughness'])
 if m.node_tree.animation_data:
  for fc in m.node_tree.animation_data.action.fcurves:
   for k in fc.keyframe_points:k.interpolation='LINEAR'
 return {'material':m.name,'height_range_m':[.4,1.3],'full_dust_frame':260,'reconstructed':True}
