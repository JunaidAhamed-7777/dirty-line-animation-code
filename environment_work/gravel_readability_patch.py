"""Recovered rut patch; warm grain/clump corrections already in surface helper."""
import bpy
def improve_sandy_gravel():
 for m in bpy.data.materials:
  if not m.name.startswith('Damp compressed tire ruts'):continue
  m.use_nodes=True;n=m.node_tree.nodes;l=m.node_tree.links;p=next((x for x in n if x.type=='BSDF_PRINCIPLED'),None)
  if not p:continue
  p.inputs['Roughness'].default_value=.91;p.inputs['Metallic'].default_value=0;p.inputs['Specular IOR Level'].default_value=.12
  tex=n.new('ShaderNodeTexCoord');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=5.5;l.new(tex.outputs['Object'],noise.inputs[0]);r=n.new('ShaderNodeValToRGB');r.color_ramp.elements[0].color=(.065,.033,.012,1);r.color_ramp.elements[1].color=(.23,.14,.065,1);l.new(noise.outputs['Fac'],r.inputs[0]);l.new(r.outputs[0],p.inputs['Base Color'])
  sep=n.new('ShaderNodeSeparateXYZ');l.new(tex.outputs['UV'],sep.inputs[0]);ramp=n.new('ShaderNodeValToRGB');ramp.color_ramp.elements[0].position=0;ramp.color_ramp.elements[0].color=(0,0,0,1);ramp.color_ramp.elements[1].position=.5;ramp.color_ramp.elements[1].color=(.7,.7,.7,1);e=ramp.color_ramp.elements.new(1);e.color=(0,0,0,1);l.new(sep.outputs['X'],ramp.inputs[0]);mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';l.new(ramp.outputs[0],mul.inputs[0]);l.new(noise.outputs['Fac'],mul.inputs[1]);l.new(mul.outputs[0],p.inputs['Alpha'])
  if hasattr(m,'surface_render_method'):m.surface_render_method='DITHERED'
 return True
if __name__=='__main__':improve_sandy_gravel()
