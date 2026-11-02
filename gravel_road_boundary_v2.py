"""Reconstructed analytic shoulder mask: no elevated sand ribbon across asphalt."""
import bpy
def constrain_gravel_to_shoulder():
 for mat in bpy.data.materials:
  if not any(t in mat.name.lower() for t in ('gravel','rut')) or not mat.use_nodes:continue
  nt=mat.node_tree;bs=next((n for n in nt.nodes if n.type=='BSDF_PRINCIPLED'),None)
  if not bs:continue
  def m(op,a=None,b=None):
   n=nt.nodes.new('ShaderNodeMath');n.operation=op
   for i,v in enumerate((a,b)):
    if v is None:continue
    if isinstance(v,(int,float)):n.inputs[i].default_value=v
    else:nt.links.new(v,n.inputs[i])
   return n.outputs[0]
  g=nt.nodes.new('ShaderNodeNewGeometry');sp=nt.nodes.new('ShaderNodeSeparateXYZ');nt.links.new(g.outputs['Position'],sp.inputs[0]);x=sp.outputs['X'];y=sp.outputs['Y']
  e=m('EXPONENT',m('MULTIPLY',m('MULTIPLY',m('DIVIDE',x,155),m('DIVIDE',x,155)),-1));cy=m('ADD',m('MULTIPLY',e,104),-44);slope=m('MULTIPLY',m('MULTIPLY',x,-208/24025),e)
  distance=m('DIVIDE',m('ABSOLUTE',m('SUBTRACT',y,cy)),m('SQRT',m('ADD',m('MULTIPLY',slope,slope),1)))
  edge=nt.nodes.new('ShaderNodeMapRange');edge.interpolation_type='SMOOTHERSTEP';edge.clamp=True;edge.inputs['From Min'].default_value=3.1;edge.inputs['From Max'].default_value=4.55;edge.inputs['To Min'].default_value=0;edge.inputs['To Max'].default_value=1;nt.links.new(distance,edge.inputs['Value'])
  old=bs.inputs['Alpha'].links[0].from_socket if bs.inputs['Alpha'].links else 1
  nt.links.new(m('MULTIPLY',old,edge.outputs['Result']),bs.inputs['Alpha'])
