"""Recovered reconstruction, not byte-identical lost helper. World-meter CC0 maps."""
import bpy,math
from pathlib import Path
ROOT=Path(__file__).parent/'textures'
def material(name,asset,tile,tint,rough,bump):
 m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.use_nodes=True;n=m.node_tree.nodes;n.clear();l=m.node_tree.links
 def new(t,label):x=n.new(t);x.label=label;return x
 out=new('ShaderNodeOutputMaterial','output');p=new('ShaderNodeBsdfPrincipled','rough scanned surface');l.new(p.outputs[0],out.inputs[0]);p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.18 if asset=='sandy_gravel' else .25
 geo=new('ShaderNodeNewGeometry','real metric position');scale=new('ShaderNodeVectorMath','physical tile scale');scale.operation='SCALE';scale.inputs[3].default_value=1/tile;l.new(geo.outputs['Position'],scale.inputs[0])
 mapping=new('ShaderNodeMapping','secondary de-tiling');mapping.inputs['Rotation'].default_value[2]=.73;mapping.inputs['Location'].default_value=(.37,.83,0);l.new(scale.outputs[0],mapping.inputs[0])
 noise=new('ShaderNodeTexNoise','broad tile blending');noise.inputs['Scale'].default_value=.13;noise.inputs['Detail'].default_value=2;l.new(geo.outputs['Position'],noise.inputs['Vector'])
 scans={}
 for kind in ['diff','rough','disp']:
  im=bpy.data.images.load(str(ROOT/f'{asset}_{kind}_2k.jpg'),check_existing=True);im.colorspace_settings.name='sRGB' if kind=='diff' else 'Non-Color';im.pack()
  a=new('ShaderNodeTexImage',kind+' scan');a.image=im;b=new('ShaderNodeTexImage',kind+' secondary');b.image=im;l.new(scale.outputs[0],a.inputs[0]);l.new(mapping.outputs[0],b.inputs[0]);mix=new('ShaderNodeMixRGB',kind+' de-tile');l.new(noise.outputs['Fac'],mix.inputs[0]);l.new(a.outputs['Color'],mix.inputs[1]);l.new(b.outputs['Color'],mix.inputs[2]);scans[kind]=mix.outputs[0]
 color=new('ShaderNodeMixRGB','surface tint');color.blend_type='MULTIPLY';color.inputs[0].default_value=1;color.inputs[2].default_value=(*tint,1);l.new(scans['diff'],color.inputs[1]);l.new(color.outputs[0],p.inputs['Base Color'])
 rm=new('ShaderNodeMapRange','roughness range');rm.inputs['To Min'].default_value=rough[0];rm.inputs['To Max'].default_value=rough[1];l.new(scans['rough'],rm.inputs['Value']);l.new(rm.outputs[0],p.inputs['Roughness'])
 b=new('ShaderNodeBump','scanned fine grain');b.inputs['Strength'].default_value=.65;b.inputs['Distance'].default_value=bump;l.new(scans['disp'],b.inputs['Height']);l.new(b.outputs[0],p.inputs['Normal'])
 if asset=='sandy_gravel':
  cl=new('ShaderNodeTexNoise','loose sand clumps');cl.inputs['Scale'].default_value=2.2;cl.inputs['Detail'].default_value=3.5;cl.inputs['Roughness'].default_value=.7;l.new(geo.outputs['Position'],cl.inputs[0])
  ramp=new('ShaderNodeValToRGB','V2 loose-sand clump tint');ramp.color_ramp.elements[0].position=.2;ramp.color_ramp.elements[0].color=(.46,.39,.30,1);ramp.color_ramp.elements[1].position=.78;ramp.color_ramp.elements[1].color=(1.10,1.04,.91,1);l.new(cl.outputs['Fac'],ramp.inputs[0])
  cm=new('ShaderNodeMixRGB','warm irregular loose sand');cm.blend_type='MULTIPLY';cm.inputs[0].default_value=.72;l.new(color.outputs[0],cm.inputs[1]);l.new(ramp.outputs[0],cm.inputs[2]);l.new(cm.outputs[0],p.inputs['Base Color'])
  macro=new('ShaderNodeBump','shallow sand clumps');macro.inputs['Strength'].default_value=.45;macro.inputs['Distance'].default_value=.055;l.new(cl.outputs['Fac'],macro.inputs['Height']);l.new(b.outputs[0],macro.inputs['Normal']);l.new(macro.outputs[0],p.inputs['Normal'])
 return m

def feather(m,length,feather_m):
 n=m.node_tree.nodes;l=m.node_tree.links;out=next(x for x in n if x.type=='OUTPUT_MATERIAL');old=out.inputs[0].links[0].from_socket
 def mathnode(op,a,b):
  x=n.new('ShaderNodeMath');x.operation=op
  for i,v in enumerate((a,b)):
   if isinstance(v,(float,int)):x.inputs[i].default_value=v
   else:l.new(v,x.inputs[i])
  return x.outputs[0]
 uv=n.new('ShaderNodeTexCoord');sep=n.new('ShaderNodeSeparateXYZ');l.new(uv.outputs['UV'],sep.inputs[0])
 x=sep.outputs['X'];y=sep.outputs['Y'];edge=mathnode('MINIMUM',x,mathnode('SUBTRACT',1,x));side=mathnode('MULTIPLY',edge,12)
 ends=mathnode('MINIMUM',y,mathnode('SUBTRACT',1,y));end=mathnode('MULTIPLY',ends,length/max(feather_m,.01))
 geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=1.8;noise.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],noise.inputs[0])
 irregular=mathnode('ADD',mathnode('MULTIPLY',noise.outputs['Fac'],.45),-.12);a=mathnode('MINIMUM',side,mathnode('ADD',end,irregular));a=mathnode('MAXIMUM',0,a);a=mathnode('MINIMUM',1,a)
 trans=n.new('ShaderNodeBsdfTransparent');mix=n.new('ShaderNodeMixShader');l.new(a,mix.inputs[0]);l.new(trans.outputs[0],mix.inputs[1]);l.new(old,mix.inputs[2]);l.new(mix.outputs[0],out.inputs[0])
 if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'

def apply_v2_surface_materials(gravel_length_m=160.0,entrance_feather_m=9.0):
 road=material('Rain-black asphalt','asphalt_02',3,(.46,.48,.51),(.57,.81),.005)
 gravel=material('Compacted ochre gravel','sandy_gravel',2.1,(1,.64,.31),(.77,.96),.018)
 earth=material('Midnight wet earth','grass_path_3',1,(.62,.72,.49),(.82,.99),.025)
 ribbon=gravel.copy();ribbon.name='V2 sandy gravel — feathered ribbon';feather(ribbon,gravel_length_m,entrance_feather_m)
 for ob in bpy.data.objects:
  if ob.type=='MESH' and ob.name.startswith('Gravel shortcut'):
   if len(ob.data.materials):ob.data.materials[0]=ribbon
   else:ob.data.materials.append(ribbon)
  if ob.name.startswith(('Thin puddle','Irregular puddle','Standing water')) or (ob.type=='MESH' and any(m and m.name=='Thin standing water' for m in ob.data.materials)):ob.hide_render=True;ob.hide_viewport=True
 return {'road':road,'gravel':gravel,'earth':earth,'ribbon':ribbon}
# Call gravel_readability_patch.improve_sandy_gravel() after material creation
# if the recovered scene includes compressed tire-rut geometry.
