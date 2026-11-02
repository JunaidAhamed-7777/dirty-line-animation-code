import bpy

def refine_lamp_glass():
 # Supplied covers are thin surface shells, not sealed solid glass volumes.
 for name in ['GT40_Headlight1','GT40_Headlight3']:
  m=bpy.data.materials.get(name)
  if not m:continue
  nt=m.node_tree;nt.nodes.clear();tr=nt.nodes.new('ShaderNodeBsdfTransparent');gl=nt.nodes.new('ShaderNodeBsdfGlossy');gl.inputs['Color'].default_value=(.95,.98,1,1);gl.inputs['Roughness'].default_value=.025;fr=nt.nodes.new('ShaderNodeFresnel');fr.inputs['IOR'].default_value=1.45;mix=nt.nodes.new('ShaderNodeMixShader');out=nt.nodes.new('ShaderNodeOutputMaterial');nt.links.new(fr.outputs[0],mix.inputs[0]);nt.links.new(tr.outputs[0],mix.inputs[1]);nt.links.new(gl.outputs[0],mix.inputs[2]);nt.links.new(mix.outputs[0],out.inputs['Surface'])
 for name in ['GT40_Headlight4','GT40_Headlight5']:
  m=bpy.data.materials.get(name)
  if m:
   p=next(n for n in m.node_tree.nodes if n.type=='BSDF_PRINCIPLED');p.inputs['Emission Strength'].default_value=4
