"""Break up the outer ribbon's feather without extending sand across asphalt."""
import bpy,os
R=os.path.dirname(os.path.abspath(__file__))
for mat in bpy.data.materials:
 if not mat.name.startswith('V2 sandy gravel'):continue
 n=mat.node_tree.nodes;l=mat.node_tree.links
 edge=next(x for x in n if x.type=='MATH' and x.operation=='MINIMUM' and x.inputs[0].links and x.inputs[0].links[0].from_node.type=='SEPXYZ')
 previous=list(edge.outputs[0].links)
 geo=n.new('ShaderNodeNewGeometry');noise=n.new('ShaderNodeTexNoise');noise.inputs['Scale'].default_value=3.5;noise.inputs['Detail'].default_value=3;l.new(geo.outputs['Position'],noise.inputs[0])
 mul=n.new('ShaderNodeMath');mul.operation='MULTIPLY';mul.inputs[1].default_value=.025;l.new(noise.outputs['Fac'],mul.inputs[0]);add=n.new('ShaderNodeMath');add.operation='ADD';add.inputs[1].default_value=.015;l.new(mul.outputs[0],add.inputs[0]);sub=n.new('ShaderNodeMath');sub.operation='SUBTRACT';l.new(edge.outputs[0],sub.inputs[0]);l.new(add.outputs[0],sub.inputs[1])
 for link in previous:l.new(sub.outputs[0],link.to_socket)
bpy.ops.file.pack_all();bpy.ops.wm.save_as_mainfile(filepath=R+'/DIRTY_LINE.blend',compress=True)
