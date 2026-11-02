"""Recovered from retained authored settings. Camera-only real CC0 photographic sky."""
import bpy,math
from pathlib import Path
PREFIX='V2 Star Sky | '
def apply_star_sky(rotation_degrees=115.0,camera_strength=.45,keep_half_moon=True):
 w=bpy.context.scene.world
 if not w:w=bpy.data.worlds.new('DIRTY LINE night');bpy.context.scene.world=w
 w.use_nodes=True;n=w.node_tree.nodes;l=w.node_tree.links
 out=next((x for x in n if x.type=='OUTPUT_WORLD'),None) or n.new('ShaderNodeOutputWorld')
 orig=out.inputs['Surface'].links[0].from_socket if out.inputs['Surface'].is_linked else None
 old=n.get(PREFIX+'camera mix')
 if old and old.inputs[1].is_linked:orig=old.inputs[1].links[0].from_socket
 for x in list(n):
  if x.name.startswith(PREFIX):n.remove(x)
 if orig is None:
  b=n.new('ShaderNodeBackground');b.inputs['Color'].default_value=(.012,.018,.03,1);b.inputs['Strength'].default_value=.15;orig=b.outputs[0]
 def node(t,label):
  x=n.new(t);x.name=PREFIX+label;x.label=label;return x
 tc=node('ShaderNodeTexCoord','world direction');mp=node('ShaderNodeMapping','fixed celestial rotation');mp.inputs['Rotation'].default_value[2]=math.radians(rotation_degrees);l.new(tc.outputs['Generated'],mp.inputs['Vector'])
 norm=node('ShaderNodeVectorMath','normalize direction');norm.operation='NORMALIZE';l.new(mp.outputs[0],norm.inputs[0])
 sep=node('ShaderNodeSeparateXYZ','direction xyz');l.new(norm.outputs[0],sep.inputs[0])
 add=node('ShaderNodeMath','sky latitude offset');add.operation='ADD';add.inputs[1].default_value=.75;l.new(sep.outputs['Z'],add.inputs[0])
 floor=node('ShaderNodeMath','exclude photographic horizon');floor.operation='MAXIMUM';floor.inputs[1].default_value=.70;l.new(add.outputs[0],floor.inputs[0])
 combine=node('ShaderNodeCombineXYZ','sky-only direction');l.new(sep.outputs['X'],combine.inputs['X']);l.new(sep.outputs['Y'],combine.inputs['Y']);l.new(floor.outputs[0],combine.inputs['Z'])
 norm2=node('ShaderNodeVectorMath','normalize sky lookup');norm2.operation='NORMALIZE';l.new(combine.outputs[0],norm2.inputs[0])
 env=node('ShaderNodeTexEnvironment','Greg Zaal Satara photograph');env.image=bpy.data.images.load(str(Path(__file__).parent/'textures/satara_night_no_lamps.jpg'),check_existing=True);env.image.pack();l.new(norm2.outputs[0],env.inputs['Vector'])
 hsv=node('ShaderNodeHueSaturation','restrained star color');hsv.inputs['Saturation'].default_value=.55;l.new(env.outputs['Color'],hsv.inputs['Color'])
 tint=node('ShaderNodeMixRGB','cool sky tint');tint.blend_type='MULTIPLY';tint.inputs[0].default_value=1;tint.inputs[2].default_value=(.55,.67,1,1);l.new(hsv.outputs[0],tint.inputs[1])
 bg=node('ShaderNodeBackground','camera stars only');bg.inputs['Strength'].default_value=camera_strength;l.new(tint.outputs[0],bg.inputs['Color'])
 lp=node('ShaderNodeLightPath','camera visibility');mix=node('ShaderNodeMixShader','camera mix');l.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);l.new(orig,mix.inputs[1]);l.new(bg.outputs[0],mix.inputs[2]);l.new(mix.outputs[0],out.inputs['Surface'])
 for ob in bpy.data.objects:
  if ob.name.startswith('V2 Sky Grass | cloud') or (not keep_half_moon and ob.name.startswith('V2 Sky Grass | HALF MOON')):ob.hide_render=True;ob.hide_viewport=True
 w['star_source']='https://polyhaven.com/a/satara_night_no_lamps';w['star_license']='CC0 1.0 — Greg Zaal';w['sky_camera_only']=True
 return w
